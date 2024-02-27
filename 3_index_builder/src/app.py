import asyncio
import os
import shutil
import time

import grpc
import variables as vars
from index_builder_proto import index_builder_pb2, index_builder_pb2_grpc
from llama_index import (
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler,
    OpenInferenceCallbackHandler,
)
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import OpenAI
from logger import configure_logging, create_logger
from storage import Storage

_logger = create_logger("index_builder:app")

storage_context_dict = {}


def _init_service_context():
    # callback manager

    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_handler = OpenInferenceCallbackHandler()
    callback_manager = CallbackManager([llama_debug, callback_handler])
    # service context

    embed_model = HuggingFaceEmbedding(model_name=vars.EMBED_MODEL_NAME)
    llm_model = OpenAI(model=vars.LLM_MODEL_NAME, temperature=0)

    service_context = ServiceContext.from_defaults(
        embed_model=embed_model,
        llm=llm_model,
        callback_manager=callback_manager,
    )
    return service_context


index_service_context = _init_service_context()


class IndexBuilderService(index_builder_pb2_grpc.IndexBuilderServicer):
    def __init__(self):
        """Load  vector vector locations and start the server"""
        # global index storage dir
        self.global_index_dir = vars.GLOBAL_INDICES_DIR
        # attachments files dir
        self.conv_files_dir = vars.TEMP_INDICES_DIR
        # conv index storage dir
        self.conv_index_dir = vars.CREATED_INDICES_DIR
        # logger

    @staticmethod
    def _path_exist(path):
        return os.path.isdir(path)

    def getIndex(
        self, request: index_builder_pb2.getBuildIndexRequest, context
    ) -> index_builder_pb2.getBuildIndexResponse:
        conversation_id = request.conversationId
        file_name = request.fileName

        try:
            storage = Storage(vars.CONV_INDICES_BUCKET_NAME)

            if storage.exists(f"{vars.CREATED_INDICES_DIR}/{file_name}"):
                return index_builder_pb2.getBuildIndexResponse(
                    conversationId=conversation_id,
                    fileName=file_name,
                    status="INDEXED",
                )
        except Exception:
            _logger.exception(f"Failed to get index for conversation {conversation_id}")

        return index_builder_pb2.getIndexResponse(
            conversationId=conversation_id,
            fileNameList=file_name,
            status="NOT_FOUND",
        )

    def buildIndex(
        self, request: index_builder_pb2.buildIndexRequest, context
    ) -> index_builder_pb2.buildIndexResponse:
        conversation_id = request.conversationId
        index_attachments = request.indexAttachments
        tool_name = request.toolName
        subquestion_id = request.subQuestionId

        try:
            attachments_path = os.path.join(vars.CREATED_INDICES_DIR, conversation_id)
            merge_index_path = os.path.join(
                vars.TEMP_INDICES_DIR, f"{conversation_id}-{subquestion_id}"
            )
            if os.path.exists(attachments_path):
                shutil.rmtree(attachments_path)
            os.mkdir(attachments_path)
            storage_context = storage_context_dict[tool_name]
            index = load_index_from_storage(
                storage_context,
                service_context=index_service_context,
            )

            _logger.info(f"Global index  for {tool_name} loaded")
            storage = Storage(vars.CONV_INDICES_BUCKET_NAME)

            for file_name, attachment_id in index_attachments.items():
                storage.download_folder(
                    f"{conversation_id}/{file_name}",
                    f"{attachments_path}/{attachment_id}-{subquestion_id}",
                )
                attachment_storage_context = StorageContext.from_defaults(
                    persist_dir=f"{attachments_path}/{attachment_id}-{subquestion_id}"
                )
                attachment_index = load_index_from_storage(
                    attachment_storage_context,
                    service_context=index_service_context,
                )
                _logger.info(
                    f"Local index  for {attachment_id}-{subquestion_id} loaded"
                )
                attachment_nodes = [
                    values["node_ids"]
                    for key, values in attachment_index.docstore.to_dict()[
                        "docstore/ref_doc_info"
                    ].items()
                ]
                _logger.info(f"Loaded {attachment_id} nodes")
                for node in attachment_nodes:
                    index.insert_nodes(nodes=attachment_index.docstore.get_nodes(node))
                _logger.info(
                    f"Merged {attachment_id}-{subquestion_id} with {tool_name} global index"
                )

            index.storage_context.persist(persist_dir=merge_index_path)
            merged_storage = Storage(vars.MERGED_INDICES_BUCKET_NAME)
            merged_storage.upload_folder(
                merge_index_path, f"{conversation_id}/{subquestion_id}"
            )
            _logger.info(f"Sending to backend {conversation_id} merged index files")
            return index_builder_pb2.buildIndexResponse(
                conversationId=conversation_id,
                status="INDEXED",
            )
        except Exception as error:
            _logger.error(f"Could not build index {error}")
            return index_builder_pb2.buildIndexResponse(
                conversationId=conversation_id,
                status="NOT_FOUND",
            )

    def deleteIndex(
        self, request: index_builder_pb2.deleteBuildIndexRequest, context
    ) -> index_builder_pb2.deleteBuildIndexResponse:
        conversation_id = request.conversationId
        file_name = request.fileName
        extracted_filename = file_name.rsplit(".", 1)[0]

        try:
            storage = Storage(vars.CONV_INDICES_BUCKET_NAME)
            folder_path = f"{conversation_id}/{extracted_filename}"
            file_name_path = f"{folder_path}/{vars.VECTOR_INDEX_FILENAMES[0]}"
            if storage.exists(file_name_path):
                storage.delete_folder(f"{conversation_id}/{extracted_filename}")
                _logger.info(f"Folder for {folder_path} deleted")
                return index_builder_pb2.deleteBuildIndexResponse(
                    conversationId=conversation_id, fileName=file_name, status="DELETED"
                )
            _logger.info(f"Folder for {folder_path} not found")
            return index_builder_pb2.deleteBuildIndexResponse(
                conversationId=conversation_id, fileName=file_name, status="NOT_FOUND"
            )
        except Exception:
            _logger.exception(
                f"Failed to delete index for conversation {conversation_id}"
            )
            return index_builder_pb2.deleteBuildIndexResponse(
                conversationId=conversation_id, fileName=file_name, status="FAILED"
            )


def download_company_storage():
    """Start with company indices loaded"""
    storage = Storage(vars.GCS_INDEX_BUILDER_BUCKET)

    blobs = storage.bucket.list_blobs()
    companies = []
    for blob in blobs:
        if blob.name.split("/")[0] not in companies:
            company = blob.name.split("/")[0]
            storage.download_folder(
                f"{company}",
                f"{vars.GLOBAL_INDICES_DIR}/{company}",
            )
            companies.append(company)
            company_index_dir = os.path.join(vars.GLOBAL_INDICES_DIR, company)

            storage_context_dict.update(
                {company: StorageContext.from_defaults(persist_dir=company_index_dir)}
            )
            _logger.info(f"Company {company} downloaded to {vars.GLOBAL_INDICES_DIR}")
    _logger.info(f"Company indices downloaded to {vars.GLOBAL_INDICES_DIR}")


## BOILERPLATE
# Below is boilerplate code to start the server.
async def serve():
    """Start the server"""

    server = grpc.aio.server()
    index_builder_pb2_grpc.add_IndexBuilderServicer_to_server(
        IndexBuilderService(), server
    )
    listen_addr = f"[::]:{vars.PORT}"
    server.add_insecure_port(listen_addr)
    await server.start()
    _logger.info(f"Started server on {listen_addr}")
    await server.wait_for_termination()
    _logger.info(f"Server terminated on {listen_addr}")


if __name__ == "__main__":
    configure_logging()
    for directory in [
        vars.GLOBAL_INDICES_DIR,
        vars.TEMP_INDICES_DIR,
        vars.CREATED_INDICES_DIR,
    ]:
        if not os.path.exists(directory):
            os.mkdir(directory)
    download_company_storage()
    _logger.debug("Creating directories on filesystem...")

    asyncio.run(serve())
## END BOILERPLATE
