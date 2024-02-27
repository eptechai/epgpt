import grpc
from fastapi import HTTPException
from grpc import FutureTimeoutError
from logger import create_logger
from model_proto.model_pb2 import Empty, LengthRequest, PromptRequest
from model_proto.model_pb2_grpc import ModelStub
from variables import MODEL_SERVICE_HOST, USE_INSECURE_CHANNEL

_logger = create_logger("backend:model")


class ModelService:
    """
    ModelService is a class that handles the gRPC calls to the model server.
    """

    def __init__(self) -> None:
        try:
            if USE_INSECURE_CHANNEL:
                channel = grpc.insecure_channel(MODEL_SERVICE_HOST)
            else:
                channel = grpc.secure_channel(
                    MODEL_SERVICE_HOST,
                    grpc.ssl_channel_credentials(
                        root_certificates=open("/root/ca.crt", "rb").read(),
                        private_key=open("/root/client.key", "rb").read(),
                        certificate_chain=open("/root/client.crt", "rb").read(),
                    ),
                )
            grpc.channel_ready_future(channel).result(timeout=3)
            self.client = ModelStub(channel)
        except FutureTimeoutError:
            _logger.exception(f"Model server is unavailable: {MODEL_SERVICE_HOST}")
            raise HTTPException(500, "INTERNAL SERVER ERROR: DOWNSTREAM CONNECTION ERROR")

    def converse(self, id: str, prompt: str, params: dict):
        """
        Sends a prompt to the model server and returns the response
        :param prompt: Prompt string
        :return: Response string
        """
        request = PromptRequest(id=id, prompt=prompt, params=params)
        response = self.client.getResponseStream(request)

        for token in response:
            yield token.token

    def get_params(self):
        """
        Returns the current model parameters
        :return: Model parameters
        """
        request = Empty()
        response = self.client.getDefaultParams(request)
        return {k: getattr(response, k) for k in response.DESCRIPTOR.fields_by_name}

    async def get_batch_tokenized_length(self, text: str):
        """
        Returns the tokenized length of a batch of text
        :param text: Text to be tokenized
        :return: Tokenized length
        """
        request = LengthRequest(text=text)
        response = self.client.getBatchTokenizedLength(request)
        return response.length

    async def get_context_length(self):
        """
        Returns the context length of the model
        :return: Context length
        """
        request = Empty()
        response = self.client.getContextLength(request)
        return response.context_length
