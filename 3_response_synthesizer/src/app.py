import asyncio
import pickle
import threading
from queue import Empty

import grpc
import variables as vars
from logger import configure_logging, create_logger
from response_synthesizer import Config, ResponseSynthesizer
from response_synthesizer_proto import (
    response_synthesizer_pb2,
    response_synthesizer_pb2_grpc,
)

_logger = create_logger("response_synthesizer:app")


class ResponseSynthesizerService(
    response_synthesizer_pb2_grpc.ResponseSynthesizerServicer
):
    def __init__(self):
        self.synthesizer = ResponseSynthesizer()

    def summarizeResponse(
        self, request: response_synthesizer_pb2.getFinalAnswerRequest, context
    ) -> response_synthesizer_pb2.getFinalAnswerResponse:
        message = ""
        query = request.query
        model_params = request.params
        qa_pairs = request.qaPairs
        source_nodes = pickle.loads(request.Sources)
        _logger.info(f"Synthesizing Response for question: {query} | {qa_pairs}")

        streamer = self.synthesizer.initialize_synthesizer(
            query, qa_pairs, source_nodes, model_params
        )

        try:
            generation_task = threading.Thread(target=self.synthesizer.synthesize)
            generation_task.start()
            _logger.info("Synthesizer: Background generation task submitted...")

            for token in streamer:
                token = token.replace("#", "")
                if token:
                    yield response_synthesizer_pb2.getFinalAnswerResponse(Answer=token)

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
                    yield response_synthesizer_pb2.getFinalAnswerResponse(
                        Answer=f"{token} "
                    )

                yield response_synthesizer_pb2.getFinalAnswerResponse(Answer=words[-1])

    def getSynthesizerDefaultParams(
        self, request: response_synthesizer_pb2.FinalEmpty, context
    ) -> response_synthesizer_pb2.FinalParams:
        return response_synthesizer_pb2.FinalParams(**Config().to_dict())


## BOILERPLATE
# Below is boilerplate code to start the server.
async def serve():
    """Start the server"""
    server = grpc.aio.server()
    response_synthesizer_pb2_grpc.add_ResponseSynthesizerServicer_to_server(
        ResponseSynthesizerService(), server
    )
    listen_addr = f"[::]:{vars.PORT}"
    server.add_insecure_port(listen_addr)
    await server.start()
    _logger.info(f"Started server on {listen_addr}")
    await server.wait_for_termination()
    _logger.info(f"Server terminated on {listen_addr}")


if __name__ == "__main__":
    configure_logging()

    asyncio.run(serve())
## END BOILERPLATE
