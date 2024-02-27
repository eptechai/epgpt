import asyncio
import os
import threading
from queue import Empty

import grpc
import numpy as np
from google.protobuf.json_format import MessageToDict
from logger import configure_logging, create_logger
from model_proto import model_pb2, model_pb2_grpc
from storage import Storage

import variables
from model import Config

if os.environ.get("PRODUCTION", False):
    from message import Message
    from model import GPT
else:
    from mocked_message import MockedMessage as Message
    from mocked_model import MockedGPT as GPT


storage = Storage(variables.ADAPTER_BUCKET)
storage.download_folder(f"{variables.QLORA_ADAPTER_FOLDER}", variables.LOCAL_QLORA_ADAPTER_FOLDER)
model = GPT()
_logger = create_logger("model:app")


class ModelService(model_pb2_grpc.ModelServicer):
    def __init__(self):
        pass

    def getContextLength(self, request: model_pb2.Empty, context) -> model_pb2.ModelContextLengthResponse:
        return model_pb2.ModelContextLengthResponse(context_length=model.context_length)

    async def getResponseStream(self, request: model_pb2.PromptRequest, context) -> model_pb2.ResponseStream:
        message = ""
        query = request.prompt
        params = request.params
        config = Config.from_proto(MessageToDict(params))

        dialogue = Message(request.id, query, config, model)
        generation_task = threading.Thread(target=dialogue.converse)
        generation_task.start()
        _logger.info(f"Background task submitted: {query} | {params} | {config}")

        try:
            for token in dialogue.streamer:
                token = token.replace("#", "")
                if token:
                    yield model_pb2.ResponseStream(token=token)

        except Empty:
            _logger.warning("Streamer did not yield any tokens on time")
            message = "Sorry, I am taking too long to respond. Please try later"
        except Exception as exc:
            _logger.exception(f"Streamer failed with exception: {exc}")
            message = "Unable to generate response. Please try again later"
        finally:
            if message:
                words = message.split()
                for token in words[:-1]:
                    yield model_pb2.ResponseStream(token=f"{token} ")

                yield model_pb2.ResponseStream(token=words[-1])

    async def getDefaultParams(self, request: model_pb2.Empty, context) -> model_pb2.Params:
        return model_pb2.Params(**Config().to_dict())

    async def getBatchTokenizedLength(
        self, request: model_pb2.LengthRequest, context
    ) -> model_pb2.LengthResponse:
        model.tokenizer.add_special_tokens({"pad_token": "[PAD]"})
        tokenized_inputs = model.tokenizer(request.text, return_tensors="np", padding=True, truncation=False)
        lengths = np.sum(
            np.not_equal(tokenized_inputs.input_ids, model.tokenizer.pad_token_id),
            axis=1,
        )

        return model_pb2.LengthResponse(length=lengths[0])


## BOILERPLATE
# Below is boilerplate code to start the server.
async def serve():
    """Start the server"""
    server = grpc.aio.server()
    model_pb2_grpc.add_ModelServicer_to_server(ModelService(), server)
    listen_addr = f"[::]:{variables.PORT}"
    if variables.USE_INSECURE_CHANNEL:
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
