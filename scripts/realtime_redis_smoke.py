from __future__ import annotations

import asyncio
import json
import os
from uuid import uuid4

import httpx
import websockets


REST_PRIMARY = os.getenv("REST_PRIMARY", "http://127.0.0.1:8000")
REST_SECONDARY = os.getenv("REST_SECONDARY", "http://127.0.0.1:8001")
WS_SECONDARY = os.getenv("WS_SECONDARY", "ws://127.0.0.1:8001/gateway")
CHANNEL_ID = int(os.getenv("SMOKE_CHANNEL_ID", "2001"))
DM_ID = int(os.getenv("SMOKE_DM_ID", "801"))


async def main() -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        await _assert_health(client, REST_PRIMARY)
        await _assert_health(client, REST_SECONDARY)
        user42_token = await _dev_token(client, REST_PRIMARY, "yangbun", 42)
        user701_token = await _dev_token(client, REST_PRIMARY, "Mina", 701)

        async with websockets.connect(WS_SECONDARY) as websocket:
            await _identify(websocket, user42_token)
            await _assert_server_dispatch(client, websocket, user42_token)
            await _assert_dm_dispatch(client, websocket, user701_token)

    print("realtime dispatch smoke passed")


async def _assert_health(client: httpx.AsyncClient, base_url: str) -> None:
    response = await client.get(f"{base_url}/api/health")
    response.raise_for_status()


async def _dev_token(
    client: httpx.AsyncClient,
    base_url: str,
    username: str,
    user_id: int,
) -> str:
    response = await client.post(
        f"{base_url}/api/dev/session",
        json={"username": username, "user_id": user_id},
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    if not isinstance(token, str):
        raise RuntimeError("dev session response did not include an access token")
    return token


async def _identify(websocket: websockets.ClientConnection, token: str) -> None:
    hello = json.loads(await asyncio.wait_for(websocket.recv(), timeout=5))
    if hello.get("op") != 10:
        raise RuntimeError("gateway did not send HELLO")

    await websocket.send(json.dumps({"op": 2, "d": {"token": token}}))
    ready = json.loads(await asyncio.wait_for(websocket.recv(), timeout=5))
    if ready.get("op") != 0 or ready.get("t") != "READY":
        raise RuntimeError("gateway did not send READY after IDENTIFY")


async def _assert_server_dispatch(
    client: httpx.AsyncClient,
    websocket: websockets.ClientConnection,
    token: str,
) -> None:
    content = f"redis-server-smoke-{uuid4()}"
    response = await client.post(
        f"{REST_PRIMARY}/api/channels/{CHANNEL_ID}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"channel_id": CHANNEL_ID, "content": content},
    )
    response.raise_for_status()
    created_id = response.json()["id"]

    event = await _wait_for_event(websocket, "MESSAGE_CREATE")
    data = event.get("d", {})
    if data.get("id") != created_id or data.get("channel_id") != CHANNEL_ID:
        raise RuntimeError("server message dispatch did not match created message")


async def _assert_dm_dispatch(
    client: httpx.AsyncClient,
    websocket: websockets.ClientConnection,
    token: str,
) -> None:
    content = f"redis-dm-smoke-{uuid4()}"
    response = await client.post(
        f"{REST_PRIMARY}/api/dms/{DM_ID}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"dm_id": DM_ID, "content": content},
    )
    response.raise_for_status()
    created_id = response.json()["id"]

    event = await _wait_for_event(websocket, "DM_MESSAGE_CREATE")
    data = event.get("d", {})
    if data.get("id") != created_id or data.get("dm_id") != DM_ID:
        raise RuntimeError("DM dispatch did not match created message")


async def _wait_for_event(
    websocket: websockets.ClientConnection,
    event_name: str,
) -> dict[str, object]:
    for _ in range(12):
        payload = json.loads(await asyncio.wait_for(websocket.recv(), timeout=5))
        if payload.get("op") == 0 and payload.get("t") == event_name:
            return payload
    raise RuntimeError(f"gateway did not receive {event_name}")


if __name__ == "__main__":
    asyncio.run(main())
