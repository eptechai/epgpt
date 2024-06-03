# /bin/python3
# Generate OpenAPI spec from FastAPI app

import os

from app import app
from fastapi.testclient import TestClient

if __name__ == "__main__":
    # Make the gen_dist directory if it doesn't exist.
    parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    output_dir = os.path.join(parent_dir, "gen_dist")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    client = TestClient(app)
    response = client.get("/api/openapi.json")

    with open(os.path.join(output_dir, "openapi.json"), "w") as f:
        f.write(response.text)
