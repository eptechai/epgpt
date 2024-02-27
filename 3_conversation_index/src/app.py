import asyncio
import glob
import logging
import os
import shutil
import threading

import grpc
import variables as vars
from conversation_index_proto import conversation_index_pb2, conversation_index_pb2_grpc
from deletion_task import delete_indices
from indexing_task import index_builder
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from logger import configure_logging, create_logger
from storage import Storage

_logger = create_logger("conversation_index:app")


class ConversationIndexService(conversation_index_pb2_grpc.ConversationIndexServicer):
    def __init__(self):
        """Load the vector database from cloud storage and start the server"""
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=os.path.join(
                os.path.dirname(__file__), "../gen_deps/embedding-model"
            ),
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    async def getCitations(
        self, request: conversation_index_pb2.getConvCitationsRequest, context
    ) -> conversation_index_pb2.getConvCitationsResponse:
        conversation_id = request.conversationId
        query = request.query
        k = request.k

        try:
            # Create a folder for downloading the index files for that conversation
            folder_path = os.path.join(vars.SEARCHABLE_INDICES_DIR, conversation_id)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            os.mkdir(folder_path)

            storage = Storage(vars.CONV_INDICES_BUCKET_NAME)
            storage.download_folder(f"{conversation_id}", folder_path)
            indices = glob.glob(f"{folder_path}/*.faiss")

            no_of_indices = len(indices)
            if no_of_indices == 0:
                _logger.warning(f"No indices found for conversation {conversation_id}")
                return conversation_index_pb2.getConvCitationsResponse(citations=[])

            _logger.info(
                f"Found {no_of_indices} indices for conversation {conversation_id}"
            )
            for index, filename in enumerate(indices):
                file_basename = os.path.basename(filename).rsplit(".", 1)[0]
                if index == 0:
                    faiss_index = FAISS.load_local(
                        folder_path, self.embedding_model, file_basename
                    )
                else:
                    faiss_index_i = FAISS.load_local(
                        folder_path, self.embedding_model, file_basename
                    )
                    faiss_index.merge_from(faiss_index_i)

            retriever = faiss_index.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k},
            )
            _logger.info(f"Retrieving citations for query: {query} | similarity: {k}")
            citations = retriever.get_relevant_documents(query)
            citations = [
                conversation_index_pb2.ConvCitation(
                    filename=citation.metadata["source"] or "",
                    pagenum=citation.metadata["page"],
                    text=citation.page_content,
                )
                for citation in citations
            ]
            _logger.info(f"Found {len(citations)} citations for given query: {query}")
            return conversation_index_pb2.getConvCitationsResponse(citations=citations)

        finally:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

    async def getIndex(
        self, request: conversation_index_pb2.getIndexRequest, context
    ) -> conversation_index_pb2.getIndexResponse:
        conversation_id = request.conversationId
        file_name = request.fileName
        extracted_filename = file_name.rsplit(".", 1)[0]

        try:
            storage = Storage(vars.CONV_INDICES_BUCKET_NAME)
            if storage.exists(f"{conversation_id}/{extracted_filename}.faiss"):
                return conversation_index_pb2.getIndexResponse(
                    conversationId=conversation_id, fileName=file_name, status="INDEXED"
                )
        except Exception:
            _logger.exception(f"Failed to get index for conversation {conversation_id}")

        return conversation_index_pb2.getIndexResponse(
            conversationId=conversation_id, fileName=file_name, status="NOT_FOUND"
        )

    async def deleteIndex(
        self, request: conversation_index_pb2.deleteIndexRequest, context
    ) -> conversation_index_pb2.deleteIndexResponse:
        conversation_id = request.conversationId
        file_name = request.fileName
        extracted_filename = file_name.rsplit(".", 1)[0]

        try:
            storage = Storage(vars.CONV_INDICES_BUCKET_NAME)
            if storage.exists(f"{conversation_id}/{extracted_filename}.faiss"):
                storage.delete_file(f"{conversation_id}/{extracted_filename}.faiss")
                storage.delete_file(f"{conversation_id}/{extracted_filename}.pkl")

                return conversation_index_pb2.deleteIndexResponse(
                    conversationId=conversation_id, fileName=file_name, status="DELETED"
                )

            return conversation_index_pb2.deleteIndexResponse(
                conversationId=conversation_id, fileName=file_name, status="NOT_FOUND"
            )
        except Exception:
            _logger.exception(
                f"Failed to delete index for conversation {conversation_id}"
            )
            return conversation_index_pb2.deleteIndexResponse(
                conversationId=conversation_id, fileName=file_name, status="FAILED"
            )


## BOILERPLATE
# Below is boilerplate code to start the server.
async def serve():
    """Start the server"""
    server = grpc.aio.server()
    conversation_index_pb2_grpc.add_ConversationIndexServicer_to_server(
        ConversationIndexService(), server
    )
    listen_addr = f"[::]:{vars.PORT}"
    server.add_insecure_port(listen_addr)
    await server.start()
    _logger.info(f"Started server on {listen_addr}")
    await server.wait_for_termination()
    _logger.info(f"Server terminated on {listen_addr}")


if __name__ == "__main__":
    configure_logging()

    _logger.debug("Creating directories on filesystem...")
    for directory in [
        vars.SEARCHABLE_INDICES_DIR,
        vars.TEMP_INDICES_DIR,
        vars.CREATED_INDICES_DIR,
    ]:
        if not os.path.exists(directory):
            os.mkdir(directory)

    asyncio.run(serve())
## END BOILERPLATE
