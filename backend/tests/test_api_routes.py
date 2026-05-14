from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app


def auth_headers() -> dict[str, str]:
    token = create_access_token(subject="42", claims={"username": "yangbun"})
    return {"Authorization": f"Bearer {token}"}


def test_create_message_requires_auth() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/channels/2001/messages",
        json={"channel_id": 2001, "content": "hello"},
    )

    assert response.status_code == 401


def test_create_message_returns_created_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/channels/2001/messages",
        json={"channel_id": 2001, "content": "hello"},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json()["content"] == "hello"
    assert response.json()["author_name"] == "yangbun"


def test_create_channel_returns_created_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/guilds/1001/channels",
        json={"name": "qa-room", "type": 0},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "qa-room"
