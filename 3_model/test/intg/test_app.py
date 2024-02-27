import grpc
import pytest
from model_proto.model_pb2 import Empty, LengthRequest, PromptRequest
from model_proto.model_pb2_grpc import ModelStub


@pytest.fixture(scope="module")
def client():
    channel = grpc.insecure_channel(
        "localhost:5001"
    )  # TODO: Parameterize using secrets
    # channel = grpc.insecure_channel("102.221.177.106:30219")
    client = ModelStub(channel)
    return client


@pytest.mark.asyncio
async def test_getDefaultParams(
    client: ModelStub,
):
    response = client.getDefaultParams(Empty())
    assert response is not None
    assert response.k == 3


@pytest.mark.asyncio
async def test_getResponseStream(
    client: ModelStub,
):
    response = client.getResponseStream(PromptRequest(prompt="Hello World"))

    for token, actual in zip(response, "HELLO WORLD"):
        assert token.token is actual
