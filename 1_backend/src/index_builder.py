from typing import Dict

import grpc
from fastapi import HTTPException
from index_builder_proto.index_builder_pb2 import (
    buildIndexRequest,
    deleteBuildIndexRequest,
    deleteBuildIndexResponse,
    getBuildIndexRequest,
    getBuildIndexResponse,
)
from index_builder_proto.index_builder_pb2_grpc import IndexBuilderStub

from variables import INDEX_BUILDER_SERVICE_HOST

import logging


_logger = logging.getLogger("backend:index")


class IndexBuilderService:
    """
    ConversationIndexService is a class that handles the gRPC calls to the server which hosts the conversational indices.
    """

    def __init__(self, id: str) -> None:
        self.id = id

        try:
            channel = grpc.insecure_channel(INDEX_BUILDER_SERVICE_HOST)
            grpc.channel_ready_future(channel).result(timeout=3)
            self.client = IndexBuilderStub(channel)
        except grpc.FutureTimeoutError:
            _logger.exception(f"Index Builder service is unavailable: {INDEX_BUILDER_SERVICE_HOST}")
            raise HTTPException(500, "INTERNAL SERVER ERROR: DOWNSTREAM CONNECTION ERROR")

    def build_index(self, index_attachments: Dict, toolname: str, subquestion_id: str):
        """
        Sends a prompt to the index server and returns the response
        :param id: ID of the conversation
        :param prompt: Prompt string
        :param k:
        :return: Response files
        """
        request = buildIndexRequest(
            conversationId=self.id,
            indexAttachments=index_attachments,
            toolName=toolname,
            subQuestionId=subquestion_id,
        )
        response = self.client.buildIndex(request)

        return {
            "default_vector_store": response.defaultVectorStore,
            "doc_store": response.docStore,
            "graph_store": response.graphStore,
            "index_store": response.indexStore,
        }

    def get_index_status(self, filename, toolname):
        request = getBuildIndexRequest(conversationId=self.id, fileName=filename, toolName=toolname)
        response = self.client.getIndex(request)
        return getBuildIndexResponse.IndexStatus.Name(response.status)

    def delete_index(self, filename):
        request = deleteBuildIndexRequest(conversationId=self.id, fileName=filename)
        response = self.client.deleteIndex(request)
        return deleteBuildIndexResponse.DeletionStatus.Name(response.status)
