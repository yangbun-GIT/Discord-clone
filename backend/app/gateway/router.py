from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.gateway.events import GatewayEvent, IdentifyPayload
from app.gateway.manager import gateway_manager
from app.gateway.opcodes import Opcode
from app.schemas.auth import UserPublic
from app.services.guild_service import list_guilds_for_user

gateway_router = APIRouter()


@gateway_router.websocket("/gateway")
async def gateway(websocket: WebSocket) -> None:
    settings = get_settings()
    connection = await gateway_manager.connect(websocket)
    await connection.send(
        op=Opcode.HELLO,
        data={"heartbeat_interval": settings.gateway_heartbeat_interval_ms},
    )

    try:
        while True:
            raw_payload = await websocket.receive_json()
            event = GatewayEvent.model_validate(raw_payload)

            if event.op == Opcode.HEARTBEAT:
                gateway_manager.mark_heartbeat(connection)
                await connection.send(op=Opcode.HEARTBEAT_ACK)
                continue

            if event.op == Opcode.IDENTIFY:
                identify = IdentifyPayload.model_validate(event.d or {})
                try:
                    token_payload = decode_access_token(identify.token)
                except InvalidTokenError:
                    await websocket.close(code=4001, reason="invalid token")
                    return

                user = UserPublic(
                    id=int(token_payload["sub"]),
                    username=str(token_payload.get("username", "unknown")),
                    status=1,
                )
                guilds = await list_guilds_for_user(user)
                subscribed_channel_ids = {
                    channel.id
                    for guild in guilds
                    for channel in guild.channels
                }
                gateway_manager.mark_identified(
                    connection,
                    user_id=user.id,
                    username=user.username,
                    channel_ids=subscribed_channel_ids,
                )
                await connection.send(
                    op=Opcode.DISPATCH,
                    event="READY",
                    data={
                        "user": {
                            "id": connection.user_id,
                            "username": connection.username,
                        },
                        "session": {
                            "gateway_connections": gateway_manager.size,
                            "subscribed_channel_ids": sorted(subscribed_channel_ids),
                        },
                    },
                )
                continue

            if event.op == Opcode.REQUEST_GUILD_MEMBERS:
                await connection.send(
                    op=Opcode.DISPATCH,
                    event="GUILD_MEMBERS_CHUNK",
                    data={"members": []},
                )
                continue

            if event.op == Opcode.UPDATE_VOICE_STATE:
                await connection.send(
                    op=Opcode.DISPATCH,
                    event="VOICE_STATE_UPDATE",
                    data=event.d or {},
                )
                continue

            await websocket.close(code=4002, reason="unsupported opcode")
            return

    except (WebSocketDisconnect, ValidationError):
        gateway_manager.disconnect(connection)
