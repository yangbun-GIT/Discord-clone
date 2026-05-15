from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.gateway.events import GatewayEvent, IdentifyPayload, VoiceSignalPayload, VoiceStatePayload
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
                subscribed_guild_ids = {guild.id for guild in guilds}
                subscribed_channel_ids = {
                    channel.id
                    for guild in guilds
                    for channel in guild.channels
                }
                gateway_manager.mark_identified(
                    connection,
                    user_id=user.id,
                    username=user.username,
                    guild_ids=subscribed_guild_ids,
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
                            "subscribed_guild_ids": sorted(subscribed_guild_ids),
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
                if not connection.identified or connection.user_id is None:
                    await websocket.close(code=4003, reason="identify required")
                    return

                voice_state = VoiceStatePayload.model_validate(event.d or {})
                if voice_state.guild_id not in connection.guild_ids:
                    await websocket.close(code=4003, reason="not subscribed to guild")
                    return
                if (
                    voice_state.channel_id is not None
                    and voice_state.channel_id not in connection.channel_ids
                ):
                    await websocket.close(code=4003, reason="not subscribed to channel")
                    return

                previous_channel_id = gateway_manager.update_voice_channel(
                    connection,
                    voice_state.channel_id,
                )
                await gateway_manager.broadcast_voice_state(
                    previous_channel_id=previous_channel_id,
                    channel_id=voice_state.channel_id,
                    data={
                        "guild_id": voice_state.guild_id,
                        "channel_id": voice_state.channel_id,
                        "user_id": connection.user_id,
                        "username": connection.username,
                        "self_mute": voice_state.self_mute,
                        "self_deaf": voice_state.self_deaf,
                    },
                )
                continue

            if event.op == Opcode.VOICE_SIGNAL:
                if not connection.identified or connection.user_id is None:
                    await websocket.close(code=4003, reason="identify required")
                    return

                voice_signal = VoiceSignalPayload.model_validate(event.d or {})
                if connection.voice_channel_id != voice_signal.channel_id:
                    await websocket.close(code=4003, reason="not connected to voice channel")
                    return

                await gateway_manager.send_voice_signal(
                    channel_id=voice_signal.channel_id,
                    target_user_id=voice_signal.target_user_id,
                    data={
                        "channel_id": voice_signal.channel_id,
                        "from_user_id": connection.user_id,
                        "from_username": connection.username,
                        "target_user_id": voice_signal.target_user_id,
                        "type": voice_signal.type,
                        "description": voice_signal.description,
                        "candidate": voice_signal.candidate,
                    },
                )
                continue

            await websocket.close(code=4002, reason="unsupported opcode")
            return

    except (WebSocketDisconnect, ValidationError):
        gateway_manager.disconnect(connection)
