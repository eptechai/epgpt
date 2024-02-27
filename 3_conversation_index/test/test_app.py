import grpc
import pytest
from app import ConversationIndexService
from conversation_index_pb2 import getConvCitationsRequest


## Boilerplate
# Sets up gRPC server that is ephemeral for testing purposes.
@pytest.fixture(scope="module")
def grpc_add_to_server():
    from conversation_index_pb2_grpc import add_ConversationIndexServicer_to_server

    return add_ConversationIndexServicer_to_server


@pytest.fixture(scope="module")
def grpc_channel():
    channel = grpc.insecure_channel("localhost:5003")
    yield channel
    channel.close()


@pytest.fixture(scope="module")
def grpc_stub(grpc_channel):
    return ConversationIndexService()


## End Boilerplate


# Test the server
@pytest.mark.asyncio
async def test_getCitations(
    grpc_stub: ConversationIndexService,
):  # This must be named grpc_stub for pytest to work.
    response = await grpc_stub.getCitations(
        getConvCitationsRequest(id="1234", query="Hello World", k=3), {}
    )
    assert len(response.citations) == 0


@pytest.mark.asyncio
async def test_getCitations_2(
    grpc_stub: ConversationIndexService,
):  # This must be named grpc_stub for pytest to work.
    response = await grpc_stub.getCitations(
        getConvCitationsRequest(
            id="b7cd0855-a3d2-45d3-bc78-ecc11ff6aa87", query="Who is the CEO?", k=3
        ),
        {},
    )
    assert len(response.citations) == 3
