import grpc
import pytest
from app import ModelService
from model_pb2 import LengthRequest, PromptRequest


## Boilerplate
# Sets up gRPC server that is ephemeral for testing purposes.
@pytest.fixture(scope="module")
def grpc_add_to_server():
    from model_pb2_grpc import add_ModelServicer_to_server

    return add_ModelServicer_to_server


@pytest.fixture(scope="module")
def grpc_channel():
    channel = grpc.insecure_channel("localhost:5001")
    yield channel
    channel.close()


@pytest.fixture(scope="module")
def grpc_stub(grpc_channel):
    return ModelService()


## End Boilerplate


# Test the server
@pytest.mark.asyncio
async def test_getDefaultParams(
    grpc_stub: ModelService,
):  # This must be named grpc_stub for pytest to work.
    response = await grpc_stub.getDefaultParams({}, None)
    assert response is not None
    assert response.k == 3


@pytest.mark.asyncio
async def test_getBatchTokenizedLength(
    grpc_stub: ModelService,
):  # This must be named grpc_stub for pytest to work.
    response = await grpc_stub.getBatchTokenizedLength(
        LengthRequest(text="Hello World"), None
    )
    assert response is not None
    assert response.length == 2


@pytest.mark.asyncio
async def test_getResponseStream(
    grpc_stub: ModelService,
):  # This must be named grpc_stub for pytest to work.
    response = grpc_stub.getResponseStream(PromptRequest(prompt="Hello World"), None)

    async for token in response:
        print(token)
        assert token.token is not None
