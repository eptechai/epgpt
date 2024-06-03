import grpc
from fastapi import HTTPException
from grpc import FutureTimeoutError
import logging
from query_engine_proto.query_engine_pb2 import SubEmpty, SubLengthRequest, getAnswerCitationsRequest
from query_engine_proto.query_engine_pb2_grpc import QueryEngineStub
from variables import QUERY_ENGINE_SERVICE_HOST, USE_INSECURE_CHANNEL

_logger = logging.getLogger("backend:query")


class QueryEngineService:
    """
    ConversationIndexService is a class that handles the gRPC calls to the server which hosts the conversational indices.
    """

    def __init__(self, id: str) -> None:
        self.id = id

        try:
            if USE_INSECURE_CHANNEL:
                channel = grpc.insecure_channel(QUERY_ENGINE_SERVICE_HOST)
            else:
                channel = grpc.secure_channel(
                    QUERY_ENGINE_SERVICE_HOST,
                    grpc.ssl_channel_credentials(
                        root_certificates=open("/root/ca.crt", "rb").read(),
                        private_key=open("/root/client.key", "rb").read(),
                        certificate_chain=open("/root/client.crt", "rb").read(),
                    ),
                )
            grpc.channel_ready_future(channel).result(timeout=3)
            self.client = QueryEngineStub(channel)
        except FutureTimeoutError:
            _logger.exception(f"Query Engine server is unavailable: {QUERY_ENGINE_SERVICE_HOST}")
            raise HTTPException(500, "INTERNAL SERVER ERROR: DOWNSTREAM CONNECTION ERROR")

    def get_answer_citations(self, query: str, params: dict, tool_name: str, subquestion_id: str):
        """
        Sends a prompt to the model server and returns the response
        :param prompt: Prompt string
        :return: Response string
        """

        request = getAnswerCitationsRequest(
            conversationId=self.id,
            subQuestion=query,
            params=params,
            toolName=tool_name,
            subQuestionId=subquestion_id,
        )

        response = self.client.getAnswerCitations(request)
        return response.Answer, response.citations, response.status

    def get_params(self):
        """
        Returns the current model parameters
        :return: Model parameters
        """
        request = SubEmpty()
        response = self.client.getSubDefaultParams(request)
        return {k: getattr(response, k) for k in response.DESCRIPTOR.fields_by_name}

    def get_batch_tokenized_length(self, text: str):
        """
        Returns the tokenized length of a batch of text
        :param text: Text to be tokenized
        :return: Tokenized length
        """
        request = SubLengthRequest(text=text)
        response = self.client.getSubBatchTokenizedLength(request)
        return response.length

    def get_context_length(self):
        """
        Returns the context length of the model
        :return: Context length
        """
        request = SubEmpty()
        response = self.client.getSubContextLength(request)
        return response.contextLength
