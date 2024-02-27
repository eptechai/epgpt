import pytest
import grpc
from vectordb_pb2 import getCitationsRequest
from vectordb_pb2_grpc import VectorDBStub
from app import VectorDBService

# import sys
# sys.path.append("/workspaces/i0523dsollms-chatapp/2_svc_vectordb/src/generated")
# sys.path.append("/workspaces/i0523dsollms-chatapp/2_svc_vectordb/src")

## Boilerplate
# Sets up gRPC server that is ephemeral for testing purposes.
@pytest.fixture(scope="module")
def grpc_add_to_server():
    from vectordb_pb2_grpc import add_VectorDBServicer_to_server

    return add_VectorDBServicer_to_server


@pytest.fixture(scope="module")
def grpc_servicer():
    from vectordb_pb2_grpc import VectorDBServicer

    return VectorDBServicer()


@pytest.fixture(scope="module")
def grpc_stub_cls(grpc_channel):
    from app import VectorDBService

    return (
        lambda _: VectorDBService()
    )  # Weimen says: I have no idea why a lambda here makes it work. Pytest is full of side effects.

#Defines whether to use an in-memory server or actually hit some endpoint.
@pytest.fixture(autouse=True, scope='module')
def stub(grpc_stub, endpoint):
    if endpoint == "":
        return grpc_stub
    else:
        # Connect to the real gRPC server
        channel = grpc.aio.insecure_channel(endpoint)
        return VectorDBStub(channel)

## End Boilerplate


# Test the server
@pytest.mark.asyncio
async def test_getCitations(
    stub: VectorDBService,
):  # This must be named grpc_stub for pytest to work.
    response = await stub.getCitations(
        getCitationsRequest(
            query="Tell me about the business model.", k=5, score_threshold=0.5
        )
    )
    assert response is not None
    assert len(response.citations) != 0
    for r in response.citations:
        assert r is not None
        assert r.text != ""
        assert r.text is not None
        assert r.pagenum is not None
        assert r.pagenum > -1
        assert r.filename is not None
        assert r.filename != ""
