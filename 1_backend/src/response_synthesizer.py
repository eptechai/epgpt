import pickle
from typing import List

import grpc
from fastapi import HTTPException
from grpc import FutureTimeoutError
import logging
from response_synthesizer_proto.response_synthesizer_pb2 import FinalEmpty, getFinalAnswerRequest
from response_synthesizer_proto.response_synthesizer_pb2_grpc import ResponseSynthesizerStub
from variables import RESPONSE_SYNTHESIZER_SERVICE_HOST, USE_INSECURE_CHANNEL

_logger = logging.getLogger("backend:query")


class ResponseSynthesizerService:
    """
    ResponseSynthesizerService is a class that handles the gRPC calls to the server which hosts the conversational indices.
    """

    def __init__(self, id: str) -> None:
        self.id = id

        try:
            if USE_INSECURE_CHANNEL:
                channel = grpc.insecure_channel(RESPONSE_SYNTHESIZER_SERVICE_HOST)
            else:
                channel = grpc.secure_channel(
                    RESPONSE_SYNTHESIZER_SERVICE_HOST,
                    grpc.ssl_channel_credentials(
                        root_certificates=open("/root/ca.crt", "rb").read(),
                        private_key=open("/root/client.key", "rb").read(),
                        certificate_chain=open("/root/client.crt", "rb").read(),
                    ),
                )
            grpc.channel_ready_future(channel).result(timeout=3)
            self.client = ResponseSynthesizerStub(channel)
        except FutureTimeoutError:
            _logger.exception(f"Model server is unavailable: {RESPONSE_SYNTHESIZER_SERVICE_HOST}")
            raise HTTPException(500, "INTERNAL SERVER ERROR: DOWNSTREAM CONNECTION ERROR")

    def get_final_answer(
        self,
        query: str,
        params: dict,
        qa_pairs: dict,
        sources: List[bytes],
    ):
        """
        Sends a prompt to the model server and returns the response
        :param prompt: Prompt string
        :return: Response string
        """
        request = getFinalAnswerRequest(
            query=query,
            params=params,
            qaPairs=qa_pairs,
            Sources=pickle.dumps([pickle.loads(node)["node"] for node in sources]),
        )
        response = self.client.summarizeResponse(request)

        for token in response:
            yield token.Answer

    def get_params(self):
        """
        Returns the current model parameters
        :return: Model parameters
        """
        request = FinalEmpty()
        response = self.client.getSynthesizerDefaultParams(request)
        return {k: getattr(response, k) for k in response.DESCRIPTOR.fields_by_name}
