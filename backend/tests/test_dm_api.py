from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app


def auth_headers(user_id: int = 42, username: str = "yangbun") -> dict[str, str]:
    token = create_access_token(subject=str(user_id), claims={"username": username})
    return {"Authorization": f"Bearer {token}"}


def test_relationships_require_auth() -> None:
    client = TestClient(app)

    response = client.get("/api/users/me/relationships")

    assert response.status_code == 401


def test_relationships_return_current_user_demo_friends() -> None:
    client = TestClient(app)

    response = client.get("/api/users/me/relationships", headers=auth_headers())

    assert response.status_code == 200
    payload = response.json()
    assert {friend["id"] for friend in payload} >= {701, 702, 703, 704}
    assert any(friend["relationship"] == "pending_incoming" for friend in payload)


def test_dms_require_auth() -> None:
    client = TestClient(app)

    response = client.get("/api/dms")

    assert response.status_code == 401


def test_dms_return_only_member_visible_threads() -> None:
    client = TestClient(app)

    owner_response = client.get("/api/dms", headers=auth_headers())
    outsider_response = client.get(
        "/api/dms",
        headers=auth_headers(user_id=999, username="outsider"),
    )

    assert owner_response.status_code == 200
    assert len(owner_response.json()) >= 3
    assert all(42 not in dm["recipient_ids"] for dm in owner_response.json())
    assert outsider_response.status_code == 200
    assert outsider_response.json() == []


def test_create_dm_returns_existing_or_new_thread() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/dms",
        json={"recipient_ids": [704]},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["recipient_ids"] == [704]
    assert payload["display_name"] == "Haru"
    assert payload["member_count"] == 2


def test_create_dm_rejects_self_recipient() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/dms",
        json={"recipient_ids": [42]},
        headers=auth_headers(),
    )

    assert response.status_code == 400


def test_create_dm_rejects_unknown_recipient() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/dms",
        json={"recipient_ids": [987654]},
        headers=auth_headers(),
    )

    assert response.status_code == 404


def test_create_dm_message_sanitizes_content() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/dms/801/messages",
        json={"dm_id": 801, "content": "hello <script>alert(1)</script><b>team</b>"},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["dm_id"] == 801
    assert payload["author_name"] == "yangbun"
    assert payload["content"] == "hello &lt;b&gt;team&lt;/b&gt;"


def test_create_dm_message_requires_thread_membership() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/dms/801/messages",
        json={"dm_id": 801, "content": "blocked"},
        headers=auth_headers(user_id=999, username="outsider"),
    )

    assert response.status_code == 403


def test_create_dm_message_rejects_payload_mismatch() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/dms/801/messages",
        json={"dm_id": 802, "content": "wrong target"},
        headers=auth_headers(),
    )

    assert response.status_code == 400


def test_friend_request_endpoint_creates_pending_state() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/users/me/relationships/requests",
        json={"username": "Nora"},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == 705
    assert payload["relationship"] == "pending_outgoing"


def test_friend_request_accept_endpoint_turns_rows_into_friends() -> None:
    client = TestClient(app)

    client.post(
        "/api/users/me/relationships/requests",
        json={"username": "yangbun"},
        headers=auth_headers(user_id=705, username="Nora"),
    )
    response = client.post(
        "/api/users/me/relationships/705/accept",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["relationship"] == "friend"


def test_block_and_unblock_relationship_endpoints() -> None:
    client = TestClient(app)

    block_response = client.post(
        "/api/users/me/relationships/704/block",
        headers=auth_headers(),
    )
    unblock_response = client.delete(
        "/api/users/me/relationships/704/block",
        headers=auth_headers(),
    )

    assert block_response.status_code == 200
    assert block_response.json()["relationship"] == "blocked"
    assert unblock_response.status_code == 200
    assert unblock_response.json()["id"] == 704
