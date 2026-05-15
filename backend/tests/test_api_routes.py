from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app


def auth_headers(user_id: int = 42, username: str = "yangbun") -> dict[str, str]:
    token = create_access_token(subject=str(user_id), claims={"username": username})
    return {"Authorization": f"Bearer {token}"}


def test_create_message_requires_auth() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/channels/2001/messages",
        json={"channel_id": 2001, "content": "hello"},
    )

    assert response.status_code == 401


def test_list_my_guilds_requires_auth() -> None:
    client = TestClient(app)

    response = client.get("/api/guilds/me")

    assert response.status_code == 401


def test_auth_me_returns_current_user() -> None:
    client = TestClient(app)

    response = client.get("/api/auth/me", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["username"] == "yangbun"


def test_register_requires_database() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/auth/register",
        json={"username": "new-user", "password": "password123"},
    )

    assert response.status_code == 503


def test_login_requires_database() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={"username": "yangbun", "password": "password123"},
    )

    assert response.status_code == 503


def test_list_my_guilds_returns_authenticated_user_memberships() -> None:
    client = TestClient(app)

    response = client.get("/api/guilds/me", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()[0]["name"] == "SRS Lab"


def test_list_my_guilds_filters_non_members() -> None:
    client = TestClient(app)

    response = client.get("/api/guilds/me", headers=auth_headers(user_id=999, username="outsider"))

    assert response.status_code == 200
    assert response.json() == []


def test_create_guild_returns_owned_workspace() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/guilds",
        json={"name": "Project Room"},
        headers=auth_headers(user_id=777, username="builder"),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Project Room"
    assert payload["owner_id"] == 777
    assert payload["members"][0]["role"] == "Owner"
    assert [channel["name"] for channel in payload["channels"]] == ["general", "voice-room"]


def test_create_invite_and_join_guild() -> None:
    client = TestClient(app)

    invite_response = client.post("/api/guilds/1001/invites", headers=auth_headers())

    assert invite_response.status_code == 201
    code = invite_response.json()["code"]

    join_response = client.post(
        f"/api/guilds/invites/{code}/join",
        headers=auth_headers(user_id=888, username="joiner"),
    )

    assert join_response.status_code == 201
    assert join_response.json()["id"] == 1001
    assert any(member["username"] == "joiner" for member in join_response.json()["members"])


def test_create_invite_requires_permission() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/guilds/1001/invites",
        headers=auth_headers(user_id=43, username="codex"),
    )

    assert response.status_code == 403


def test_join_invite_rejects_unknown_code() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/guilds/invites/missing-code/join",
        headers=auth_headers(user_id=889, username="missing"),
    )

    assert response.status_code == 404


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


def test_create_message_requires_guild_membership() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/channels/2001/messages",
        json={"channel_id": 2001, "content": "hello"},
        headers=auth_headers(user_id=999, username="outsider"),
    )

    assert response.status_code == 403


def test_create_channel_returns_created_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/guilds/1001/channels",
        json={"name": "qa-room", "type": 0},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "qa-room"


def test_create_channel_requires_manage_channels_permission() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/guilds/1001/channels",
        json={"name": "blocked-room", "type": 0},
        headers=auth_headers(user_id=43, username="codex"),
    )

    assert response.status_code == 403
