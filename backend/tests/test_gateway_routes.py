from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.operation_limits import reset_operation_limits
from app.core.security import create_access_token
from app.main import app


def auth_token(user_id: int = 42, username: str = "yangbun") -> str:
    return create_access_token(subject=str(user_id), claims={"username": username})


def identify_payload(token: str) -> dict[str, object]:
    return {"op": 2, "d": {"token": token, "os": "test", "library": "pytest"}}


def receive_disconnect(websocket) -> WebSocketDisconnect:
    while True:
        try:
            websocket.receive_json()
        except WebSocketDisconnect as exc:
            return exc


def test_gateway_identify_rate_limit_closes_with_policy_code() -> None:
    reset_operation_limits()
    client = TestClient(app)
    token = auth_token()

    for _ in range(5):
        with client.websocket_connect("/gateway") as websocket:
            assert websocket.receive_json()["op"] == 10
            websocket.send_json(identify_payload(token))
            assert websocket.receive_json()["t"] == "READY"

    with client.websocket_connect("/gateway") as websocket:
        assert websocket.receive_json()["op"] == 10
        websocket.send_json(identify_payload(token))
        exc_info = receive_disconnect(websocket)

    assert exc_info.code == 4008
    reset_operation_limits()


def test_gateway_rejects_invalid_identify_token() -> None:
    reset_operation_limits()
    client = TestClient(app)

    with client.websocket_connect("/gateway") as websocket:
        assert websocket.receive_json()["op"] == 10
        websocket.send_json(identify_payload("not-a-token"))
        exc_info = receive_disconnect(websocket)

    assert exc_info.code == 4001
    reset_operation_limits()


def test_gateway_rejects_voice_state_for_unsubscribed_channel() -> None:
    reset_operation_limits()
    client = TestClient(app)

    with client.websocket_connect("/gateway") as websocket:
        assert websocket.receive_json()["op"] == 10
        websocket.send_json(identify_payload(auth_token()))
        assert websocket.receive_json()["t"] == "READY"
        websocket.send_json(
            {
                "op": 4,
                "d": {
                    "guild_id": 1001,
                    "channel_id": 999999,
                    "self_mute": False,
                    "self_deaf": False,
                },
            }
        )
        exc_info = receive_disconnect(websocket)

    assert exc_info.code == 4003
    reset_operation_limits()


def test_gateway_rejects_voice_signal_before_voice_join() -> None:
    reset_operation_limits()
    client = TestClient(app)

    with client.websocket_connect("/gateway") as websocket:
        assert websocket.receive_json()["op"] == 10
        websocket.send_json(identify_payload(auth_token()))
        assert websocket.receive_json()["t"] == "READY"
        websocket.send_json(
            {
                "op": 5,
                "d": {
                    "channel_id": 2003,
                    "target_user_id": 43,
                    "type": "offer",
                    "description": {"type": "offer", "sdp": "redacted-test"},
                    "candidate": None,
                },
            }
        )
        exc_info = receive_disconnect(websocket)

    assert exc_info.code == 4003
    reset_operation_limits()
