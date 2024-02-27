import asyncio
import json
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, wait
from contextlib import asynccontextmanager
from tempfile import SpooledTemporaryFile
from typing import Annotated

import variables as vars
from attachment_proto.attachment_pb2 import Attachment, AttachmentDeletionMessage
from db.client.client import Prisma
from db.client.errors import RecordNotFoundError
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from index_builder import IndexBuilderService
from query_engine import QueryEngineService
from rabbitmq import RabbitMQ
from request_spec import (
    CompanyRequest,
    MessageFeedback,
    MessageRequest,
    ParamsUpdateRequest,
    SubsectorRequest,
)
from response_spec import (
    AttachmentListResponse,
    AttachmentStatus,
    CitationListResponse,
    CompanyListResponse,
    CompanyResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageListResponse,
    ParamsResponse,
    SubquestionListResponse,
    SubsectorListResponse,
    SubsectorResponse,
)
from response_synthesizer import ResponseSynthesizerService
from starlette.background import BackgroundTask

from sub_question_generator import SubQuestionGenerator
from utils import User, extract_user
import logging
_logger = logging.getLogger("backend:app")



# Below context creates global objects that are shared across requests
# It automatically picks up the datasource configured in schema.prisma
prisma = Prisma()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.info("Hello")
    await prisma.connect()
    yield
    await prisma.disconnect()


app = FastAPI(lifespan=lifespan, debug=True)

# This allows all endpoints to live under /api instead of /
router = APIRouter(prefix="/api")


async def validate_request(request: Request, id: str, user: Annotated[User, Depends(extract_user)]):
    """
    Validates if the parameters (Chat ID, Dialogue ID) are valid

    :param chat_id: Conversation ID
    :param dialogue_id: Dialogue ID within the conversation
    """
    try:
        await prisma.conversationpermission.find_first_or_raise(
            where={"conversationId": id, "userId": user.sub},
            include={"conversation": True},
        )
    except RecordNotFoundError:
        _logger.exception(f"Conversation: {id}|{user.username} Record Not Found")
        raise HTTPException(status_code=403, detail="Conversation Not Found/Not Authorized")

    return user


@router.get("/openapi.json")
async def get_open_api_endpoint():
    return JSONResponse(content=get_openapi(title="Open API JSON", version="1.0.0", routes=app.routes))


@router.get("/health")
def healthcheck():
    return {"status": 200}


@router.post(
    "/conversation",
    response_model=ConversationResponse,
    status_code=202,
    tags=["conversation"],
)
async def create_conversation(request: Request, user: Annotated[User, Depends(extract_user)]):
    """
    Cretes a new conversation
    :returns: Conversation UUID
    """
    conversation_id = uuid.uuid4()
    await prisma.conversationpermission.create(
        {
            "userId": user.sub,
            "role": "OWNER",
            "conversation": {
                "create": {
                    "id": str(conversation_id),
                    "parameters": json.dumps(
                        {
                            **QueryEngineService(id=conversation_id).get_params(),
                            **ResponseSynthesizerService(id=conversation_id).get_params(),
                        }
                    ),
                    "status": "IDLE",
                }
            },
        }
    )
    _logger.debug(f"Created conversation {conversation_id} for user {user.username}")
    return {"conversation_id": conversation_id}


@router.get(
    "/conversation/list",
    response_model=ConversationListResponse,
    status_code=200,
    tags=["conversation"],
)
async def get_conversation_history(
    request: Request,
    user: Annotated[User, Depends(extract_user)],
    limit: int = None,
    next_cursor: int = None,
):
    """
    Gets all conversations that the user has access to
    :returns Returns a list of conversations
    """
    conversation_permissions = await prisma.conversationpermission.find_many(
        take=limit,
        include={"conversation": True},
        where={
            "userId": user.sub,
            "conversation": {"createdAt": {"lt": next_cursor if next_cursor else int(time.time())}},
        },
        order={"conversation": {"createdAt": "desc"}},
    )

    return {
        "conversations": [
            {
                "id": conversation_permission.conversationId,
                "title": conversation_permission.conversation.title,
            }
            for conversation_permission in conversation_permissions
        ],
        "next_cursor": conversation_permissions[-1].conversation.createdAt
        if conversation_permissions and len(conversation_permissions) == limit
        else 1,
    }


@router.get(
    "/conversation/{id}",
    response_model=ConversationResponse,
    status_code=200,
    tags=["conversation"],
)
async def get_conversation(id: str, user: Annotated[User, Depends(validate_request)]):
    """
    Checks for the existence of a given conversation
    :returns Conversation ID with 200 status code if it exists, else 403
    """
    return {"conversation_id": id}


@router.delete("/conversation/{id}", status_code=200, tags=["conversation"])
async def delete_conversation(request: Request, id: str, user: Annotated[User, Depends(validate_request)]):
    """
    Deletes the conversation from the User's History
    """
    rabbitmq = RabbitMQ(queue_name=vars.INDEX_DELETION_QUEUE)
    attachments = await prisma.attachment.find_many(where={"document": {"conversationId": id}})
    for attachment in attachments:
        attachment_deletion_message = AttachmentDeletionMessage(
            id=attachment.id,
            conversationId=attachment.conversationId,
            fileName=attachment.document.name,
        )
        rabbitmq.send(attachment_deletion_message.SerializeToString())
    _logger.debug(f"Notified through RabbitMQ for conversation:{id} deletion")

    # Remove all attachments from GCS for this conversation
    storage = Storage(vars.USER_FILES_BUCKET)
    storage.delete_folder(remote_path=f"{id}/")
    _logger.debug(f"Deleted all attachments for conversation:{id}")

    # OnDelete: Cascade is the default behaviour
    await prisma.conversation.delete(where={"id": id})
    _logger.debug(f"Deleted conversation:{id}")

    return {"status": "OK"}


@router.post(
    "/conversation/{id}/params",
    response_model=ParamsResponse,
    status_code=200,
    tags=["conversation"],
)
async def configure_params(
    request: Request,
    id: str,
    params: ParamsUpdateRequest,
    user: Annotated[User, Depends(validate_request)],
):
    default_params = {
        **QueryEngineService(id=id).get_params(),
        **ResponseSynthesizerService(id=id).get_params(),
    }
    default_params.update(params.__dict__)

    conversation = await prisma.conversation.update(
        where={"id": id}, data={"parameters": json.dumps(default_params)}
    )
    return conversation.parameters


@router.get(
    "/conversation/{id}/params",
    response_model=ParamsResponse,
    status_code=200,
    tags=["conversation"],
)
async def get_params(request: Request, id: str, user: Annotated[User, Depends(validate_request)]):
    conversation = await prisma.conversation.find_unique(where={"id": id})
    return conversation.parameters


@router.get(
    "/conversation/{id}/message/list",
    response_model=MessageListResponse,
    tags=["message"],
)
async def get_messages(
    id: str,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
    limit: int = None,
    next_cursor: int = None,
):
    messages = await prisma.message.find_many(
        take=limit,
        where={
            "conversationId": id,
            "createdAt": {"lt": next_cursor if next_cursor else int(time.time())},
        },
        include={"citations": True},
        order={"createdAt": "desc"},
    )
    return {
        "messages": messages[::-1],
        "next_cursor": messages[-1].createdAt if messages and len(messages) == limit else 1,
    }


@router.get(
    "/conversation/{id}/message/{message_id}/citations",
    tags=["message"],
    response_model=CitationListResponse,
)
async def get_citations(
    id: str,
    message_id: str,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
):
    citations = await prisma.citation.find_many(where={"messageId": message_id})
    return {"citations": citations}


@router.post("/conversation/{id}/message/{message_id}/feedback", tags=["message"], status_code=200)
async def save_user_feedback(
    id: str,
    message_id: str,
    message_feedback: MessageFeedback,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
):
    try:
        message = await prisma.message.update(
            where={"id": message_id}, data={"isFeedbackPositive": message_feedback.is_feedback_positive}
        )
    except Exception as e:
        _logger.exception(f"{e}")
        raise HTTPException(500, f"Internal server error: {e}")
    return {"status": "OK"}


# Function will only be used for streaming APIs because if the stream gets cancelled, the connection will be closed
# If the global prisma object is used, it will be disconnected and the subsequent requests will fail
async def get_prisma():
    try:
        prisma = Prisma()
        if not prisma.is_connected():
            await prisma.connect()

        yield prisma
    finally:
        await prisma.disconnect()


@router.post("/conversation/{id}/message", tags=["message"])
async def post_message(
    id: str,
    request: Request,
    message: MessageRequest,
    upto: int = None,
):
    # TODO: Implement support for query parameters (upto and docs)

    user = User(
            username="Krishna",
            email="krishnaveni.rokala@teragonia.com",
            sub="Krishna",
        )

    await prisma.conversationpermission.create(
        {
            "userId": user.sub,
            "role": "OWNER",
            "conversation": {
                "create": {
                    "id": str(id),
                    "parameters": json.dumps(
                        {
                           "params": "test",
                        }
                    ),
                    "status": "IDLE",
                }
            },
        }
    )

    async def model_response_wrapper(model_response):
        tokens = []
        try:
            _logger.debug(f"Streaming response for conversation {id}...")
            # This is the message ID of the user's message
            # Will be used for cancelling the streaming or retrying
            yield message_db_record.id
            yield ";"

            # This is the message ID of the bot's message
            # Will be used to extract the citations attached to the message
            yield bot_message.id
            yield "<|endofid|>"

            for token in model_response:
                tokens.append(token)
                yield token
            yield "<|endoftext|>"
        finally:
            if not tokens:
                tokens = ["Connection", "closed", "by", "client"]

            await prisma.message.update(where={"id": bot_message.id}, data={"text": "".join(tokens)})
            _logger.info(f"Updated message {bot_message.id} with response from LLM: {''.join(tokens)}")

    def handle_subquestion(sub_question, tool_name, record_id, attachments):
        attachment_ids = {
            attachment.id: attachment.document.name.rsplit(".", 1)[0] for attachment in attachments
        }
        index_builder.build_index(attachment_ids, tool_name, record_id)
        answer, _citations, status = query_engine.get_answer_citations(
            query=sub_question, params=qe_params, tool_name=tool_name, subquestion_id=record_id
        )

        if status == "SUCCESS":
            source_nodes.extend([citation.node for citation in citations])
            citations.extend(_citations)
        else:
            answer = "DISCARDED"

        qa_pairs[sub_question] = answer
        subquestion_responses[record_id] = answer
        _logger.info(f"Sub-Question: {sub_question} ({status}) \nResponse: {answer}")

    # conversation = await prisma.conversation.find_unique(where={"id": id}, include={"messages": True})
    # if conversation.status == "BUSY":
    #     _logger.exception(f"Conversation: {id}|{user.username} is busy")
    #     raise HTTPException(400, "Bad Request: Chatbot is busy")

    # if not conversation.messages:
    #     await prisma.conversation.update(where={"id": id}, data={"title": message.prompt})

    # message_db_record = await prisma.message.create(
    #     data={
    #         "author": "USER",
    #         # TODO: Add the constructed prompt as well to the DB
    #         "text": message.prompt,
    #         "conversationId": id,
    #     }
    # )
    _logger.debug(f"Created message abc for conversation {id}")

    bot_message = await prisma.message.create(
        data={
            "author": "BOT",
            # TODO: Add the constructed prompt as well to the DB
            "text": "Pending...",
            "conversationId": id,
            "createdAt": 11,
        }
    )
    await prisma.conversation.update(where={"id": id}, data={"status": "BUSY"})
    _logger.debug(f"Updated conversation {id} status to BUSY")

    conversation = await prisma.conversation.find_unique(where={"id": id})

    try:
        # Initialize services
        response_synthesizer = ResponseSynthesizerService(id=id)
        # qe_params = {k: v for k, v in conversation.parameters.items() if k.startswith("qe_")}
        # rs_params = {k: v for k, v in conversation.parameters.items() if k.startswith("rs_")}

        # Fetch companies from DB: To build metadata
        companies_list = await prisma.company.find_many(include={"subSector": True})
        companies = {company.name: company.subSector.name for company in companies_list}
        _logger.info(f"companies from db: {companies}")

        # Generate sub-questions
        subq_generator = SubQuestionGenerator(companies=companies)
        sub_questions = subq_generator.generate_subquestions(query=message.prompt)
        qa_pairs = {}
        citations = []
        source_nodes = []
        subquestion_responses = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = []
            for question, tool_name, record_id in sub_questions:
                await prisma.subquestion.create(
                    {
                        "id": record_id,
                        "text": question,
                        "response": "",
                        "toolName": tool_name,
                        "messageId": bot_message.id,
                    }
                )
                attachments = await prisma.attachment.find_many(
                    where={"document": {"conversationId": id}, "company": {"toolName": tool_name}},
                    include={"document": True, "company": True},
                )
                results.append(
                    executor.submit(handle_subquestion, question, tool_name, record_id, attachments)
                )

            wait(results)
            try:
                for record_id, answer in subquestion_responses.items():
                    await prisma.subquestion.update(where={"id": record_id}, data={"response": answer})

                citations_length = await prisma.citation.create_many(
                    [
                        {
                            "content": citation.text.replace("\x00", ""),
                            "pageNumber": citation.pagenum,
                            "fileName": citation.filename,
                            "messageId": bot_message.id,
                            "documentId": citation.document_id,
                        }
                        for citation in citations
                    ]
                )
                _logger.info(f"Created {citations_length} citations for message {bot_message.id}")
            except Exception as exc:
                _logger.exception(f"Failed to store citations in the DB: {str(exc)}")

        final_answer = response_synthesizer.get_final_answer(
            query=message.prompt,
            params=rs_params,
            qa_pairs=qa_pairs,
            sources=source_nodes,
        )
        _logger.info("Streaming response from synthesizer...")
        return StreamingResponse(model_response_wrapper(final_answer))

    except HTTPException as exc:
        await prisma.message.update(where={"id": bot_message.id}, data={"text": f"Error: {exc}"})
        raise exc

    except Exception as exc:
        _logger.exception(f"Exception occurred: {exc}")
        data = {"text": "Sorry, I am unable to respond"}
        await prisma.message.update(where={"id": bot_message.id}, data=data)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await prisma.conversation.update(where={"id": id}, data={"status": "IDLE"})


@router.post("/conversation/{id}/message/{message_id}/cancel", status_code=202, tags=["message"])
async def cancel_streaming(
    id: str,
    message_id: str,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
):
    latest_message_id = await prisma.message.find_first(
        where={"conversationId": id, "author": "BOT"}, order={"createdAt": "desc"}
    )

    if latest_message_id.id != message_id:
        _logger.warning(f"Request failed: Message {message_id} is not the latest message")
        raise HTTPException(status_code=400, detail="Bad Request: Message is not latest")

    await prisma.conversation.update(where={"id": id}, data={"status": "IDLE"})
    return {"status": "OK"}


@router.post(
    "/conversation/{id}/attachment",
    tags=["attachment"],
    response_model=AttachmentStatus,
)
async def upload_attachment(
    id: str,
    file: UploadFile,
    company_id: Annotated[str, Form()],
    sub_sector_id: Annotated[str, Form()],
    year: Annotated[int, Form()],
    request: Request,
    user: Annotated[User, Depends(validate_request)],
    background_tasks: BackgroundTasks,
):
    async def submit_attachment():
        rabbitmq = RabbitMQ(queue_name=vars.NEW_ATTACHMENT_QUEUE)
        message = Attachment(
            id=attachment.id,
            conversationId=id,
            fileName=file.filename,
            fileContents=file_as_bytes,
        )

        rabbitmq.send(message.SerializeToString())
        _logger.debug(f"Notified through RabbitMQ for file {file.filename}")

    if not await prisma.company.find_unique(where={"id": company_id}):
        raise HTTPException(400, "Specified company does not exist")

    if not await prisma.subsector.find_unique(where={"id": sub_sector_id}):
        raise HTTPException(400, "Specified subsector does not exist")

    # Upload the file to the cloud storage
    storage = Storage(vars.USER_FILES_BUCKET)
    file_as_bytes: SpooledTemporaryFile[bytes] = file.file.read()
    remote_file_path = f"{id}/{file.filename}"

    if not storage.exists(remote_path=remote_file_path):
        # Add the file to the DB
        document = await prisma.document.create(
            {
                "id": str(uuid.uuid4()),
                "name": file.filename,
                "source": "USER_UPLOADED",
                "link": f"gs://{vars.USER_FILES_BUCKET}/{remote_file_path}",
                "credentials": "CLOUD_STORAGE_CREDENTIALS",
                "conversationId": id,
            }
        )
        attachment = await prisma.attachment.create(
            {
                "documentId": document.id,
                "companyId": company_id,
                "subSectorId": sub_sector_id,
                "year": year,
            },
            include={"document": True},
        )
    else:
        attachment = await prisma.attachment.find_first(
            where={"document": {"name": file.filename, "conversationId": id}},
            include={"document": True},
        )

    storage.upload_file_from_memory(data=file_as_bytes, remote_path=remote_file_path)
    _logger.info(f"Uploaded attachment: {file.filename}|{attachment.id} successfully")
    await prisma.attachment.update(where={"id": attachment.id}, data={"status": "UPLOADED"})

    # Delete the index from the Conversation Index so that files can stay in sync between GCS and the index

    index_builder = IndexBuilderService(id=id)
    await index_builder.delete_index(attachment.name)
    background_tasks.add_task(submit_attachment)

    return {"id": attachment.id, "name": attachment.document.name, "status": "UPLOADED"}


@router.get(
    "/conversation/{id}/attachment/{attachment_id}/status",
    tags=["attachment"],
    response_model=AttachmentStatus,
)
async def get_attachment_status(
    id: str,
    attachment_id: str,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
):
    try:
        attachment = await prisma.attachment.find_unique_or_raise(
            where={"id": attachment_id}, include={"document": True}
        )
        if attachment.conversationId != id:
            raise RecordNotFoundError
    except RecordNotFoundError:
        _logger.exception(f"Attachment: {attachment_id}|{user.username} Record Not Found")
        raise HTTPException(404, "Not Found: Attachment does not exist")

    if attachment.status in ["INDEXED", "ERRORED"]:
        return {
            "id": attachment.id,
            "name": attachment.document.name,
            "status": attachment.status,
        }

    index_builder = IndexBuilderService(id=id)
    index_status = await index_builder.get_index_status(attachment.name)

    if index_status == "INDEXED":
        await prisma.attachment.update(where={"id": attachment.id}, data={"status": index_status})
        _logger.info(f"Updated attachment: {attachment.id} status to {index_status}")
        return {
            "id": attachment.id,
            "name": attachment.name,
            "status": index_status,
        }
    return {"id": attachment.id, "name": attachment.document.name, "status": attachment.status}


@router.get(
    "/conversation/{id}/attachment/list",
    response_model=AttachmentListResponse,
    tags=["attachment"],
)
async def list_attachments(
    id: str,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
):
    attachments = await prisma.attachment.find_many(
        where={"document": {"conversationId": id}}, include={"document": True}
    )
    return {
        "attachments": [
            {"id": attachment.id, "name": attachment.document.name, "status": attachment.status}
            for attachment in attachments
        ]
    }


@router.get("/conversation/{id}/attachment/{attachment_id}", tags=["attachment"])
async def download_attachment(
    id: str,
    attachment_id: str,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
):
    def delete_file(file_path, folder_path):
        os.remove(file_path)
        os.rmdir(folder_path)

    try:
        attachment = await prisma.attachment.find_unique_or_raise(
            where={"id": attachment_id}, include={"document": True}
        )
    except RecordNotFoundError:
        _logger.exception(f"Attachment: {attachment_id}|{user.username} Record Not Found")
        raise HTTPException(404, "Not Found: Attachment does not exist")

    storage = Storage(vars.USER_FILES_BUCKET)
    download_folder = os.path.join(vars.ATTACHMENT_DOWNLOAD_PATH, id)
    download_path = os.path.join(download_folder, attachment.document.name)
    os.mkdir(download_folder)
    storage.download_file(remote_path=attachment.path, local_path=download_path)
    return FileResponse(
        path=download_path,
        filename=attachment.document.name,
        background=BackgroundTask(delete_file, download_path, download_folder),
    )


@router.delete("/conversation/{id}/attachment/{attachment_id}", tags=["attachment"])
async def delete_attachment(
    id: str,
    attachment_id: str,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
):
    """
    Deletes the attachment
    """
    # TODO: How to deal with previous citations which refer this attachment?

    # Verify if the attachment belongs to this conversation
    try:
        attachment = await prisma.attachment.find_unique_or_raise(
            where={"id": attachment_id}, include={"document": True}
        )
    except RecordNotFoundError:
        _logger.exception(f"Attachment: {attachment_id}|{user.username} Record Not Found")
        raise HTTPException(404, "Not Found: Attachment does not exist")

    if attachment.conversationId != id:
        raise HTTPException(400, "Bad Request: Attachment does not belong to this chat")

    # Delete from the conversation index

    index_builder = IndexBuilderService(id=id)
    index_status = index_builder.delete_index(attachment.name)
    if index_status in ["DELETED", "NOT_FOUND"]:
        # Delete from GCS
        storage = Storage(vars.USER_FILES_BUCKET)
        storage.delete_file(remote_path=attachment.path)
        _logger.info(f"Deleted attachment: {attachment.id} from GCS")

        await prisma.attachment.delete(where={"id": attachment_id})
        _logger.info(f"Deleted attachment: {attachment.id} successfully")
        return {"status": "OK"}

    raise HTTPException(500, "Internal Server Error: Unable to delete attachment")


@router.get(
    "/company/list",
    response_model=CompanyListResponse,
    status_code=200,
    tags=["company"],
)
async def get_companies(
    request: Request,
    user: Annotated[User, Depends(extract_user)],
):
    """
    Gets all companies
    :returns Returns a list of companies
    """
    try:
        companies = await prisma.company.find_many(
            where={"OR": [{"owner": "USER", "userId": user.sub}, {"owner": "GLOBAL"}]},
            include={"subSector": True},
            order={"createdAt": "desc"},
        )
    except Exception as e:
        _logger.exception(f"{e}")
        raise HTTPException(500, f"Internal server error: {e}")

    if not companies:
        raise HTTPException(204, "No companies found")

    return {
        "companies": [
            {
                "id": company.id,
                "name": company.name,
                "sub_sector_id": company.subSector.id,
            }
            for company in companies
        ],
    }


@router.post(
    "/company",
    response_model=CompanyResponse,
    status_code=201,
    tags=["company"],
)
async def create_company(
    request: Request,
    user: Annotated[User, Depends(extract_user)],
    company_payload: CompanyRequest,
):
    """
    Cretes a new conversation
    :returns: Company UUID
    """
    if bool(company_payload.sub_sector_id) and bool(company_payload.sub_sector):
        raise HTTPException(400, "Bad request, either subsector or subsector_id should be specified")

    if company_payload.sub_sector_id and company_payload.sub_sector:
        raise HTTPException(
            400, "Bad request, both subsector and subsector_id cannot be used at the same time"
        )

    common_fields = {
        "name": company_payload.name,
        "toolName": company_payload.name,
        "owner": "USER",
        "userId": user.sub,
    }

    company_data = (
        {**common_fields, "subSectorId": company_payload.sub_sector_id}
        if company_payload.sub_sector_id
        else {
            **common_fields,
            "subSector": {
                "create": {
                    "name": company_payload.sub_sector,
                }
            },
        }
    )

    company = await prisma.company.create(company_data)
    _logger.debug(f"Created company {company.id} for user {user.username}")
    return {
        "id": company.id,
        "name": company.name,
        "sub_sector_id": company.subSectorId,
    }


@router.get("/conversation/{id}/documents/{document_id}/", tags=["documents"])
async def download_document(
    id: str,
    document_id: str,
    request: Request,
    user: Annotated[User, Depends(validate_request)],
):
    def delete_file(file_path):
        os.remove(file_path)

    try:
        document = await prisma.document.find_unique_or_raise(where={"id": document_id})
        if document.source == "USER_UPLOADED":
            document = await prisma.document.find_unique_or_raise(
                where={
                    "id": document_id,
                    "conversationId": id,
                }
            )
    except RecordNotFoundError:
        _logger.exception(f"Document: {document_id}|{user.username} Record Not Found")
        raise HTTPException(404, "Not Found: Document does not exist")

    # TODO: Use conversation ID to create a folder structure, so that two users can download the same filename
    # link = gs://bucket_name/any/any/any.pdf
    file_path = document.link.replace("gs://", "")
    bucket = file_path.split("/")[0]
    storage = Storage(bucket)
    download_path = os.path.join(vars.DOCUMENTS_DOWNLOAD_PATH, document.name)
    storage.download_file(remote_path=file_path.split("/", 1)[1], local_path=download_path)
    return FileResponse(
        path=download_path,
        filename=document.name,
        background=BackgroundTask(delete_file, download_path),
    )


@router.get(
    "/conversation/{id}/sub-question/list",
    response_model=SubquestionListResponse,
    status_code=200,
    tags=["message"],
)
async def get_subquestions(
    id: str,
    request: Request,
    user: Annotated[User, Depends(extract_user)],
):
    """
    Gets subquestions generated for the currently active message
    :returns Returns a list of subquestions
    """
    try:
        message = await prisma.message.find_first(
            where={"conversationId": id, "author": "BOT"}, order={"createdAt": "desc"}
        )
        subquestions = await prisma.subquestion.find_many(
            where={
                "messageId": message.id,
                "message": {
                    "conversationId": id,
                },
            }
        )
    except Exception as e:
        _logger.exception(f"{e}")
        raise HTTPException(500, f"Internal server error: {e}")

    if not subquestions:
        raise HTTPException(204, "No subquestions found")

    return {
        "subquestions": [
            {
                "id": subquestion.id,
                "text": subquestion.text,
                "response": subquestion.response,
                "tool_name": subquestion.toolName,
            }
            for subquestion in subquestions
        ],
    }


@router.get(
    "/sub-sector/list",
    response_model=SubsectorListResponse,
    status_code=200,
    tags=["sub-sector"],
)
async def get_subsectors(
    request: Request,
    user: Annotated[User, Depends(extract_user)],
):
    """
    Gets all subsectors
    :returns Returns a list of subsectors
    """
    subsectors = await prisma.subsector.find_many(
        where={"OR": [{"owner": "USER", "userId": user.sub}, {"owner": "GLOBAL"}]},
        include={"companies": True},
    )

    if not subsectors:
        raise HTTPException(204, "No subsectors found")

    return {
        "subsectors": [
            {
                "id": subsector.id,
                "name": subsector.name,
                "companies": [
                    {
                        "id": company.id,
                        "name": company.name,
                        "sub_sector_id": company.subSectorId,
                    }
                    for company in subsector.companies
                ],
            }
            for subsector in subsectors
        ],
    }


@router.post(
    "/sub-sector",
    response_model=SubsectorResponse,
    status_code=201,
    tags=["sub-sector"],
)
async def create_subsector(
    request: Request,
    user: Annotated[User, Depends(extract_user)],
    subsector_payload: SubsectorRequest,
):
    """
    Cretes a new subsector
    :returns: Subsector UUID
    """
    subsector = await prisma.subsector.create(
        data={
            "name": subsector_payload.name,
            "owner": "USER",
            "userId": user.sub,
        },
        include={"companies": True},
    )
    _logger.debug(f"Created subsector {subsector.id} for user {user.username}")
    return subsector


app.include_router(router)

# Below is a reminder that when running with uvicorn, it is not __main__.
if __name__ == "__main__":
    _logger.debug("Hi, I'm main inside Uvicorn!")
else:
    _logger.debug("Hi, I'm not main inside Uvicorn!")
