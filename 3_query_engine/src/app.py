import asyncio
import os
import pickle
import shutil

import grpc
import numpy as np
import variables as vars
from llama_index import (
    StorageContext,
    load_index_from_storage,
)
from logger import configure_logging, create_logger
from query_engine import Config
from query_engine_proto import query_engine_pb2, query_engine_pb2_grpc
from storage import Storage

_logger = create_logger("query_engine:app")


if vars.USE_GPU:
    from query_engine import QueryEngine

    storage = Storage(vars.PEFT_MODEL_BUCKET)
    storage.download_folder(f"{vars.PEFT_MODEL_FOLDER}", vars.PEFT_MODEL)
else:
    from query_engine_mock import QueryEngineMock as QueryEngine


class QueryEngineService(query_engine_pb2_grpc.QueryEngineServicer):
    def __init__(self):
        self.query_engine = QueryEngine()

    def getSubContextLength(
        self, request: query_engine_pb2.SubEmpty, context
    ) -> query_engine_pb2.SubModelContextLengthResponse:
        return query_engine_pb2.SubModelContextLengthResponse(
            contextLength=self.query_engine.context_length
        )

    def getAnswerCitations(
        self, request: query_engine_pb2.getAnswerCitationsRequest, context
    ) -> query_engine_pb2.getAnswerCitationsResponse:
        conversation_id = request.conversationId
        query = request.subQuestion
        params = request.params
        tool_name = request.toolName
        subquestion_id = request.subQuestionId
        _logger.info(f"Request Params: {query} | {params} | {tool_name}")

        try:
            # Create a folder for downloading the index files for that conversation
            conversation_index_path = (
                f"{vars.TEMP_DIR}/{conversation_id}-{subquestion_id}"
            )
            # download files from bucket
            merged_storage = Storage(vars.MERGED_INDICES_BUCKET)
            merged_storage.download_folder(
                f"{conversation_id}/{subquestion_id}", conversation_index_path
            )

            # Load the index from the downloaded files
            conversation_index = load_index_from_storage(
                StorageContext.from_defaults(persist_dir=conversation_index_path),
                service_context=self.query_engine.index_service_context,
            )
            _logger.info(f"Merged index loaded from GCS: {conversation_index_path}")

            response = self.query_engine.generate(
                query,
                tool_name,
                conversation_index,
                params,
            )
            citations = [
                query_engine_pb2.SubConvCitation(
                    filename=source["filename"] or "",
                    pagenum=int(source["page"]),
                    document_id=source["document_id"],
                    text=source["text"],
                    node=pickle.dumps(source),
                )
                for source in response["citations"]
            ]
            _logger.info(f"Found {len(citations)} citations for given query: {query}")
            return query_engine_pb2.getAnswerCitationsResponse(
                Answer=response["qa_pair"].answer,
                citations=citations,
                status="SUCCESS",
            )
        except Exception as exc:
            _logger.exception(f"Exception occurred: {exc}")
            return query_engine_pb2.getAnswerCitationsResponse(
                Answer="",
                citations=[],
                status="FAIL",
            )
        finally:
            if os.path.exists(f"{conversation_id}"):
                shutil.rmtree(f"{conversation_id}")

    def getSubDefaultParams(
        self, request: query_engine_pb2.SubEmpty, context
    ) -> query_engine_pb2.SubParams:
        return query_engine_pb2.SubParams(**Config().to_dict())

    def getSubBatchTokenizedLength(
        self, request: query_engine_pb2.SubLengthRequest, context
    ) -> query_engine_pb2.SubLengthResponse:
        self.query_engine.tokenizer.add_special_tokens({"pad_token": "[PAD]"})
        tokenized_inputs = self.query_engine.tokenizer(
            request.text, return_tensors="np", padding=True, truncation=False
        )
        lengths = np.sum(
            np.not_equal(
                tokenized_inputs.input_ids,
                self.query_engine.tokenizer.pad_token_id,
            ),
            axis=1,
        )
        return query_engine_pb2.SubLengthResponse(length=lengths[0])


## BOILERPLATE
# Below is boilerplate code to start the server.
async def serve():
    """Start the server"""
    server = grpc.aio.server()
    query_engine_pb2_grpc.add_QueryEngineServicer_to_server(
        QueryEngineService(), server
    )
    listen_addr = f"[::]:{vars.PORT}"
    if vars.USE_INSECURE_CHANNEL:
        server.add_insecure_port(listen_addr)
    else:
        server.add_secure_port(
            listen_addr,
            grpc.ssl_server_credentials(
                private_key_certificate_chain_pairs=[
                    (
                        open("/root/server.key", "rb").read(),
                        open("/root/server.crt", "rb").read(),
                    )
                ],
                root_certificates=open("/root/ca.crt", "rb").read(),
                require_client_auth=True,
            ),
        )
    await server.start()
    _logger.info(f"Started server on {listen_addr}")
    await server.wait_for_termination()


if __name__ == "__main__":
    configure_logging()
    asyncio.run(serve())
## END BOILERPLATE
