import asyncio
import json
import logging
import os
import zipfile

import grpc
import variables
from google.cloud import storage
from google.cloud.storage import Blob
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from logger import configure_logging, create_logger
from svc_vectordb_proto import vectordb_pb2, vectordb_pb2_grpc

_logger = create_logger("svc_vectordb:app")


class VectorDBService(vectordb_pb2_grpc.VectorDBServicer):
    def __init__(self):
        """Load the vector database from cloud storage and start the server"""
        ## Download or loads from cache the embedding model. TODO: Build into the image.
        embedding_model = HuggingFaceEmbeddings(
            model_name=os.path.join(os.path.dirname(__file__), "../gen_deps/embedding-model"),
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        ## Loads FAISS index from GCP. #TODO: Load from local file to enable unit tests in addition to integration test.
        if not os.path.exists(variables.FAISS_INDEX_PATH):
            os.makedirs(variables.FAISS_INDEX_PATH)
        storage_client = storage.Client.from_service_account_info(json.loads(variables.GCP_SVC_APP_KEY))
        bucket = storage_client.bucket(variables.GCS_VECTORDB_INDEX_GLOBAL_BUCKET)
        blob = Blob("index/faiss_index.zip", bucket)
        blob.download_to_filename("/tmp/faiss_index.zip", client=storage_client)
        with zipfile.ZipFile("/tmp/faiss_index.zip", "r") as zip_ref:
            zip_ref.extractall(variables.FAISS_INDEX_PATH)
        self.db = FAISS.load_local(variables.FAISS_INDEX_PATH, embeddings=embedding_model)
        _logger.info(f"Successfully loaded the vector database: {variables.FAISS_INDEX_PATH}")

    async def getCitations(
        self, request: vectordb_pb2.getCitationsRequest, context={}
    ) -> vectordb_pb2.getCitationsResponse:
        query = request.query
        k = request.k
        score_threshold = request.score_threshold
        retriever = self.db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": k, "score_threshold": score_threshold},
        )
        _logger.info(
            f"Retrieving citations for query: {query} | similarity_score_threshold (k={k}, score_threshold={score_threshold})"
        )
        citations = retriever.get_relevant_documents(query)
        citations = [
            vectordb_pb2.Citation(
                filename=citation.metadata["source"] or "",
                pagenum=citation.metadata["page"],
                text=citation.page_content,
            )
            for citation in citations
        ]
        _logger.info(f"Retrieved {len(citations)} citations for query: {query}")
        return vectordb_pb2.getCitationsResponse(citations=citations)


## BOILERPLATE
# Below is boilerplate code to start the server.
async def serve():
    """Start the server"""
    server = grpc.aio.server()
    vectordb_pb2_grpc.add_VectorDBServicer_to_server(VectorDBService(), server)
    listen_addr = f"[::]:{variables.PORT}"
    server.add_insecure_port(listen_addr)
    _logger.info(f"Starting server on {listen_addr}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    configure_logging()
    asyncio.run(serve())
## END BOILERPLATE
