import os
import time

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

## Core below.


# Ensure core health functionality works.
def test_read_health():
    response = client.get("/api/health")
    assert response.status_code == 200


# Ensure that /health is mounted on /api and not /
def test_root():
    response = client.get("/health")
    assert response.status_code == 404


# Define behavior that api root should return 404.
def test_api_root():
    response = client.get("/api")
    assert response.status_code == 404


def test_openapi():
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    # TODO: Have a reference of what the contents should contain.
    # assert response.json() ==


def test_crd_ops_on_conversation():
    # Lifecycle context.
    with TestClient(app) as _client:
        response = _client.post("/api/conversation")
        conversation_id = response.json()["conversation_id"]
        assert response.status_code == 202

        response = _client.get(f"/api/conversation/{conversation_id}")
        assert response.status_code == 200
        assert response.json()["conversation_id"] == conversation_id

        response = _client.delete(f"/api/conversation/{conversation_id}")
        assert response.status_code == 200

        response = _client.get(f"/api/conversation/{conversation_id}")
        assert response.status_code == 403


def test_get_conversation():
    # Lifecycle context.
    with TestClient(app) as _client:
        response = _client.get("/api/conversation/list")
        assert response.status_code == 200
        assert "next_cursor" in response.json()
        assert isinstance(response.json()["next_cursor"], int)
        assert "conversations" in response.json()
        assert len(response.json()["conversations"]) >= 1
        assert "id" in response.json()["conversations"][0]
        assert isinstance((response.json()["conversations"][0]["id"]), str)


def test_post_and_get_params():
    with TestClient(app) as _client:
        conversations = _client.get("/api/conversation/list").json()["conversations"]
        conversation_id = conversations[-1]["id"]
        response = _client.post(f"/api/conversation/{conversation_id}/params", json={"max_new_tokens": 75})
        assert response.status_code == 200
        assert response.json()["max_new_tokens"] == 75

        response = _client.get(f"/api/conversation/{conversation_id}/params")
        assert response.status_code == 200
        assert response.json()["k"] == 3
        assert response.json()["top_k"] == 5
        assert response.json()["temperature"] == 0.25
        assert response.json()["max_new_tokens"] == 75
        assert response.json()["score_threshold"] == 0.8


def test_message_list():
    with TestClient(app) as _client:
        conversations = _client.get("/api/conversation/list").json()["conversations"]
        conversation_id = conversations[-1]["id"]
        response = _client.get(f"/api/conversation/{conversation_id}/message/list")
        assert response.status_code == 200
        assert len(response.json()["messages"]) >= 1
        assert response.json()["messages"][0]["text"] == "dummy_text"


def test_post_and_get_message():
    with TestClient(app) as _client:
        conversations = _client.get("/api/conversation/list").json()["conversations"]
        conversation_id = conversations[-1]["id"]
        response = _client.post(
            f"/api/conversation/{conversation_id}/message",
            json={"prompt": "dummy_text_2"},
        )
        assert response.status_code == 200
        assert response.content.decode() is not None

        response = _client.get(f"/api/conversation/{conversation_id}/message/list")
        assert response.status_code == 200
        assert len(response.json()["messages"]) >= 2
        assert response.json()["messages"][-2]["text"] == "dummy_text_2"

        # Changes if we use actual model
        # assert response.json()["messages"][-1]["text"] == "HELLO WORLD"


def test_post_and_get_attachment():
    test_file = "test.pdf"
    with TestClient(app) as _client:
        conversations = _client.get("/api/conversation/list").json()["conversations"]
        conversation_id = conversations[-1]["id"]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        response = _client.post(
            f"/api/conversation/{conversation_id}/attachment",
            files={"file": open(os.path.join(base_dir, test_file), "rb")},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "UPLOADED"

        response = _client.get(f"/api/conversation/{conversation_id}/attachment/list")
        assert response.status_code == 200
        assert len(response.json()["attachments"]) >= 1
        assert response.json()["attachments"][-1]["name"] == test_file

        attachment_id = response.json()["attachments"][-1]["id"]
        response = _client.get(f"/api/conversation/{conversation_id}/attachment/{attachment_id}")

        assert response.status_code == 200

        time.sleep(5)
        response = _client.get(f"/api/conversation/{conversation_id}/attachment/{attachment_id}/status")
        assert response.json()["status"] == "INDEXED"

        response = _client.delete(f"/api/conversation/{conversation_id}/attachment/{attachment_id}")
        assert response.status_code == 200

        response = _client.get(f"/api/conversation/{conversation_id}/attachment/{attachment_id}")
        assert response.status_code == 404
