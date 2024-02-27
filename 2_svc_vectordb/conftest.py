import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--endpoint",
        action="store",
        default="",
        help="Endpoint to hit for testing. Leave blank to spin up an in-memory gRPC server instead.",
    )

@pytest.fixture(scope="session")
def endpoint(pytestconfig):
    return pytestconfig.getoption("--endpoint")