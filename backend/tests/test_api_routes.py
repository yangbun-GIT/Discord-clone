from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app


def auth_headers(user_id: int = 42, username: str = "yangbun") -> dict[str, str]:
    token = create_access_token(subject=str(user_id), claims={"username": username})
    return {"Authorization": f"Bearer {token}"}


def auth_token(user_id: int = 42, username: str = "yangbun") -> str:
    return create_access_token(subject=str(user_id), claims={"username": username})


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


def test_get_guild_returns_current_membership_snapshot() -> None:
    client = TestClient(app)

    response = client.get("/api/guilds/1001", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["id"] == 1001
    assert any(member["username"] == "codex" for member in response.json()["members"])


def test_get_guild_requires_membership() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/guilds/1001",
        headers=auth_headers(user_id=999, username="outsider"),
    )

    assert response.status_code == 404


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


def test_create_role_and_assign_member_role() -> None:
    client = TestClient(app)

    role_response = client.post(
        "/api/guilds/1001/roles",
        json={"name": "Moderator", "permissions": 16},
        headers=auth_headers(),
    )

    assert role_response.status_code == 201
    role = role_response.json()["roles"][-1]
    assert role["name"] == "Moderator"

    assign_response = client.post(
        "/api/guilds/1001/members/43/roles",
        json={"role_id": role["id"]},
        headers=auth_headers(),
    )

    assert assign_response.status_code == 200
    member = next(item for item in assign_response.json()["members"] if item["id"] == 43)
    assert role["id"] in member["role_ids"]
    assert "Moderator" in member["role"]


def test_remove_member_role() -> None:
    client = TestClient(app)

    role_response = client.post(
        "/api/guilds/1001/roles",
        json={"name": "Temporary", "permissions": 0},
        headers=auth_headers(),
    )
    role = role_response.json()["roles"][-1]
    client.post(
        "/api/guilds/1001/members/43/roles",
        json={"role_id": role["id"]},
        headers=auth_headers(),
    )

    remove_response = client.delete(
        f"/api/guilds/1001/members/43/roles/{role['id']}",
        headers=auth_headers(),
    )

    assert remove_response.status_code == 200
    member = next(item for item in remove_response.json()["members"] if item["id"] == 43)
    assert role["id"] not in member["role_ids"]


def test_create_role_requires_administrator_permission() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/guilds/1001/roles",
        json={"name": "Blocked", "permissions": 0},
        headers=auth_headers(user_id=43, username="codex"),
    )

    assert response.status_code == 403


def test_remove_member() -> None:
    client = TestClient(app)

    invite_response = client.post("/api/guilds/1001/invites", headers=auth_headers())
    code = invite_response.json()["code"]
    client.post(
        f"/api/guilds/invites/{code}/join",
        headers=auth_headers(user_id=890, username="removable"),
    )

    response = client.delete(
        "/api/guilds/1001/members/890",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert all(member["id"] != 890 for member in response.json()["members"])


def test_remove_member_rejects_owner() -> None:
    client = TestClient(app)

    response = client.delete(
        "/api/guilds/1001/members/42",
        headers=auth_headers(),
    )

    assert response.status_code == 400


def test_remove_member_requires_administrator_permission() -> None:
    client = TestClient(app)

    response = client.delete(
        "/api/guilds/1001/members/44",
        headers=auth_headers(user_id=43, username="codex"),
    )

    assert response.status_code == 403


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


def test_update_message_returns_updated_payload() -> None:
    client = TestClient(app)
    create_response = client.post(
        "/api/channels/2001/messages",
        json={"channel_id": 2001, "content": "before edit"},
        headers=auth_headers(),
    )
    message_id = create_response.json()["id"]

    response = client.patch(
        f"/api/channels/2001/messages/{message_id}",
        json={"content": "after edit"},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["id"] == message_id
    assert response.json()["content"] == "after edit"


def test_update_message_requires_author_or_manager() -> None:
    client = TestClient(app)
    create_response = client.post(
        "/api/channels/2001/messages",
        json={"channel_id": 2001, "content": "owned by yangbun"},
        headers=auth_headers(),
    )
    message_id = create_response.json()["id"]

    response = client.patch(
        f"/api/channels/2001/messages/{message_id}",
        json={"content": "blocked edit"},
        headers=auth_headers(user_id=43, username="codex"),
    )

    assert response.status_code == 403


def test_delete_message_returns_deleted_payload() -> None:
    client = TestClient(app)
    create_response = client.post(
        "/api/channels/2001/messages",
        json={"channel_id": 2001, "content": "delete me"},
        headers=auth_headers(),
    )
    message_id = create_response.json()["id"]

    response = client.delete(
        f"/api/channels/2001/messages/{message_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {"id": message_id, "channel_id": 2001}


def test_delete_message_requires_author_or_manager() -> None:
    client = TestClient(app)
    create_response = client.post(
        "/api/channels/2001/messages",
        json={"channel_id": 2001, "content": "owned by yangbun"},
        headers=auth_headers(),
    )
    message_id = create_response.json()["id"]

    response = client.delete(
        f"/api/channels/2001/messages/{message_id}",
        headers=auth_headers(user_id=43, username="codex"),
    )

    assert response.status_code == 403


def test_gateway_identify_subscribes_user_channels() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/gateway") as websocket:
            hello = websocket.receive_json()
            assert hello["op"] == 10

            websocket.send_json({"op": 2, "d": {"token": auth_token()}})
            ready = websocket.receive_json()

    assert ready["t"] == "READY"
    assert 1001 in ready["d"]["session"]["subscribed_guild_ids"]
    assert 2001 in ready["d"]["session"]["subscribed_channel_ids"]


def test_message_create_fans_out_to_gateway_subscribers() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/gateway") as websocket:
            websocket.receive_json()
            websocket.send_json({"op": 2, "d": {"token": auth_token()}})
            websocket.receive_json()

            response = client.post(
                "/api/channels/2001/messages",
                json={"channel_id": 2001, "content": "gateway hello"},
                headers=auth_headers(),
            )
            event = websocket.receive_json()

    assert response.status_code == 201
    assert event["t"] == "MESSAGE_CREATE"
    assert event["d"]["content"] == "gateway hello"


def test_message_update_and_delete_fan_out_to_gateway_subscribers() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/gateway") as websocket:
            websocket.receive_json()
            websocket.send_json({"op": 2, "d": {"token": auth_token()}})
            websocket.receive_json()

            create_response = client.post(
                "/api/channels/2001/messages",
                json={"channel_id": 2001, "content": "gateway mutable"},
                headers=auth_headers(),
            )
            created_event = websocket.receive_json()
            message_id = create_response.json()["id"]

            update_response = client.patch(
                f"/api/channels/2001/messages/{message_id}",
                json={"content": "gateway edited"},
                headers=auth_headers(),
            )
            updated_event = websocket.receive_json()

            delete_response = client.delete(
                f"/api/channels/2001/messages/{message_id}",
                headers=auth_headers(),
            )
            deleted_event = websocket.receive_json()

    assert create_response.status_code == 201
    assert created_event["t"] == "MESSAGE_CREATE"
    assert update_response.status_code == 200
    assert updated_event["t"] == "MESSAGE_UPDATE"
    assert updated_event["d"]["content"] == "gateway edited"
    assert delete_response.status_code == 200
    assert deleted_event["t"] == "MESSAGE_DELETE"
    assert deleted_event["d"] == {"id": message_id, "channel_id": 2001}


def test_channel_create_fans_out_to_gateway_subscribers() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/gateway") as websocket:
            websocket.receive_json()
            websocket.send_json({"op": 2, "d": {"token": auth_token()}})
            websocket.receive_json()

            response = client.post(
                "/api/guilds/1001/channels",
                json={"name": "live-channel", "type": 0},
                headers=auth_headers(),
            )
            event = websocket.receive_json()

    assert response.status_code == 201
    assert event["t"] == "CHANNEL_CREATE"
    assert event["d"]["name"] == "live-channel"


def test_role_create_fans_out_guild_update() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/gateway") as websocket:
            websocket.receive_json()
            websocket.send_json({"op": 2, "d": {"token": auth_token()}})
            websocket.receive_json()

            response = client.post(
                "/api/guilds/1001/roles",
                json={"name": "Live Role", "permissions": 0},
                headers=auth_headers(),
            )
            event = websocket.receive_json()

    assert response.status_code == 201
    assert event["t"] == "GUILD_UPDATE"
    assert any(role["name"] == "Live Role" for role in event["d"]["roles"])


def test_voice_state_update_fans_out_to_channel_subscribers() -> None:
    with TestClient(app) as client:
        with (
            client.websocket_connect("/gateway") as sender,
            client.websocket_connect("/gateway") as receiver,
        ):
            sender.receive_json()
            sender.send_json({"op": 2, "d": {"token": auth_token()}})
            sender.receive_json()
            receiver.receive_json()
            receiver.send_json(
                {
                    "op": 2,
                    "d": {"token": auth_token(user_id=43, username="codex")},
                }
            )
            receiver.receive_json()

            sender.send_json(
                {
                    "op": 4,
                    "d": {"guild_id": 1001, "channel_id": 2003, "self_mute": False},
                }
            )
            sender_event = sender.receive_json()
            receiver_event = receiver.receive_json()

    assert sender_event["t"] == "VOICE_STATE_UPDATE"
    assert sender_event["d"]["channel_id"] == 2003
    assert sender_event["d"]["user_id"] == 42
    assert receiver_event == sender_event


def test_voice_signal_routes_to_target_voice_peer() -> None:
    with TestClient(app) as client:
        with (
            client.websocket_connect("/gateway") as sender,
            client.websocket_connect("/gateway") as receiver,
        ):
            sender.receive_json()
            sender.send_json({"op": 2, "d": {"token": auth_token()}})
            sender.receive_json()
            receiver.receive_json()
            receiver.send_json(
                {
                    "op": 2,
                    "d": {"token": auth_token(user_id=43, username="codex")},
                }
            )
            receiver.receive_json()

            sender.send_json({"op": 4, "d": {"guild_id": 1001, "channel_id": 2003}})
            sender.receive_json()
            receiver.receive_json()
            receiver.send_json({"op": 4, "d": {"guild_id": 1001, "channel_id": 2003}})
            sender.receive_json()
            receiver.receive_json()

            sender.send_json(
                {
                    "op": 5,
                    "d": {
                        "channel_id": 2003,
                        "target_user_id": 43,
                        "type": "offer",
                        "description": {"type": "offer", "sdp": "fake-sdp"},
                    },
                }
            )
            signal_event = receiver.receive_json()

    assert signal_event["t"] == "VOICE_SIGNAL"
    assert signal_event["d"]["channel_id"] == 2003
    assert signal_event["d"]["from_user_id"] == 42
    assert signal_event["d"]["target_user_id"] == 43
    assert signal_event["d"]["type"] == "offer"
    assert signal_event["d"]["description"] == {"type": "offer", "sdp": "fake-sdp"}


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
