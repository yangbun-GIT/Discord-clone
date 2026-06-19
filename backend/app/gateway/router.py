import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.operation_limits import (
    GATEWAY_HEARTBEAT_LIMIT,
    GATEWAY_IDENTIFY_LIMIT,
    VOICE_SIGNAL_LIMIT,
    VOICE_STATE_LIMIT,
    allow_operation,
)
from app.core.security import decode_access_token
from app.gateway.events import (
    GatewayEvent,
    IdentifyPayload,
    PresenceUpdatePayload,
    VoiceSignalPayload,
    VoiceStatePayload,
)
from app.gateway.manager import gateway_manager
from app.gateway.opcodes import Opcode
from app.realtime.publisher import publish_presence_update
from app.schemas.auth import UserPublic
from app.services.dm_service import list_dms, update_presence
from app.services.guild_service import list_guilds_for_user

gateway_router = APIRouter()
logger = logging.getLogger("app.gateway")


async def close_rate_limited(websocket: WebSocket, operation: str) -> None:
    logger.warning("gateway rate limit exceeded operation=%s", operation)
    await websocket.close(code=4008, reason="rate limited")


@gateway_router.websocket("/gateway")
async def gateway(websocket: WebSocket) -> None:
    settings = get_settings()
    client_host = websocket.client.host if websocket.client else "unknown"
    connection = await gateway_manager.connect(websocket)
    logger.info("gateway connect host=%s active=%s", client_host, gateway_manager.size)
    await connection.send(
        op=Opcode.HELLO,
        data={"heartbeat_interval": settings.gateway_heartbeat_interval_ms},
    )

    try:
        while True:
            raw_payload = await websocket.receive_json()
            event = GatewayEvent.model_validate(raw_payload)

            if event.op == Opcode.HEARTBEAT:
                if not await allow_operation(
                    f"gateway-heartbeat:{id(connection)}",
                    GATEWAY_HEARTBEAT_LIMIT,
                ):
                    await close_rate_limited(websocket, "heartbeat")
                    return
                gateway_manager.mark_heartbeat(connection)
                await connection.send(op=Opcode.HEARTBEAT_ACK)
                continue

            if event.op == Opcode.IDENTIFY:
                identify = IdentifyPayload.model_validate(event.d or {})
                try:
                    token_payload = decode_access_token(identify.token)
                except InvalidTokenError:
                    if not await allow_operation(
                        f"gateway-identify:{client_host}:invalid",
                        GATEWAY_IDENTIFY_LIMIT,
                    ):
                        await close_rate_limited(websocket, "identify")
                        return
                    logger.warning(
                        "gateway identify rejected reason=invalid-token host=%s",
                        client_host,
                    )
                    await websocket.close(code=4001, reason="invalid token")
                    return
                if not await allow_operation(
                    f"gateway-identify:{client_host}:{token_payload['sub']}",
                    GATEWAY_IDENTIFY_LIMIT,
                ):
                    await close_rate_limited(websocket, "identify")
                    return

                user = UserPublic(
                    id=int(token_payload["sub"]),
                    username=str(token_payload.get("username", "unknown")),
                    status=1,
                )
                guilds = await list_guilds_for_user(user)
                dms = await list_dms(user)
                subscribed_guild_ids = {guild.id for guild in guilds}
                subscribed_channel_ids = {
                    channel.id
                    for guild in guilds
                    for channel in guild.channels
                }
                subscribed_dm_ids = {dm.id for dm in dms}
                gateway_manager.mark_identified(
                    connection,
                    user_id=user.id,
                    username=user.username,
                    guild_ids=subscribed_guild_ids,
                    channel_ids=subscribed_channel_ids,
                    dm_ids=subscribed_dm_ids,
                )
                logger.info(
                    "gateway identify user_id=%s guilds=%s channels=%s dms=%s",
                    user.id,
                    len(subscribed_guild_ids),
                    len(subscribed_channel_ids),
                    len(subscribed_dm_ids),
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
                            "subscribed_dm_ids": sorted(subscribed_dm_ids),
                        },
                    },
                )
                await gateway_manager.send_voice_state_snapshot(
                    connection,
                    guild_ids=subscribed_guild_ids,
                )
                continue

            if event.op == Opcode.REQUEST_GUILD_MEMBERS:
                await connection.send(
                    op=Opcode.DISPATCH,
                    event="GUILD_MEMBERS_CHUNK",
                    data={"members": []},
                )
                continue

            if event.op == Opcode.UPDATE_PRESENCE:
                if not connection.identified or connection.user_id is None:
                    await websocket.close(code=4003, reason="identify required")
                    return

                presence_payload = PresenceUpdatePayload.model_validate(event.d or {})
                presence, friend_user_ids = await update_presence(
                    user=UserPublic(
                        id=connection.user_id,
                        username=connection.username or "unknown",
                        status=1,
                    ),
                    status=presence_payload.status,
                    activity=presence_payload.activity,
                )
                for friend_user_id in friend_user_ids:
                    await publish_presence_update(user_id=friend_user_id, presence=presence)
                logger.info(
                    "gateway presence update user_id=%s status=%s targets=%s",
                    connection.user_id,
                    presence.status,
                    len(friend_user_ids),
                )
                continue

            if event.op == Opcode.UPDATE_VOICE_STATE:
                if not connection.identified or connection.user_id is None:
                    await websocket.close(code=4003, reason="identify required")
                    return

                voice_state = VoiceStatePayload.model_validate(event.d or {})
                if not await allow_operation(
                    f"voice-state:{connection.user_id}:{voice_state.guild_id}",
                    VOICE_STATE_LIMIT,
                ):
                    await close_rate_limited(websocket, "voice-state")
                    return
                if voice_state.guild_id not in connection.guild_ids:
                    logger.warning(
                        "gateway voice state rejected "
                        "reason=guild-subscription user_id=%s guild_id=%s",
                        connection.user_id,
                        voice_state.guild_id,
                    )
                    await websocket.close(code=4003, reason="not subscribed to guild")
                    return
                if (
                    voice_state.channel_id is not None
                    and voice_state.channel_id not in connection.channel_ids
                ):
                    logger.warning(
                        "gateway voice state rejected "
                        "reason=channel-subscription user_id=%s channel_id=%s",
                        connection.user_id,
                        voice_state.channel_id,
                    )
                    await websocket.close(code=4003, reason="not subscribed to channel")
                    return

                previous_channel_id = connection.voice_channel_id
                previous_guild_id = connection.voice_guild_id
                gateway_manager.update_voice_channel(
                    connection,
                    guild_id=voice_state.guild_id,
                    channel_id=voice_state.channel_id,
                )
                if (
                    previous_channel_id is not None
                    and previous_channel_id != voice_state.channel_id
                ):
                    await gateway_manager.broadcast_voice_state(
                        previous_channel_id=previous_channel_id,
                        channel_id=None,
                        data={
                            "guild_id": previous_guild_id or voice_state.guild_id,
                            "channel_id": None,
                            "user_id": connection.user_id,
                            "username": connection.username,
                            "self_mute": False,
                            "self_deaf": False,
                        },
                    )
                if voice_state.channel_id is not None:
                    await gateway_manager.broadcast_voice_state(
                        previous_channel_id=None,
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
                    await gateway_manager.send_voice_state_snapshot(
                        connection,
                        guild_ids={voice_state.guild_id},
                        channel_id=voice_state.channel_id,
                    )
                logger.info(
                    "gateway voice state user_id=%s previous_channel_id=%s channel_id=%s",
                    connection.user_id,
                    previous_channel_id,
                    voice_state.channel_id,
                )
                continue

            if event.op == Opcode.VOICE_SIGNAL:
                if not connection.identified or connection.user_id is None:
                    await websocket.close(code=4003, reason="identify required")
                    return

                voice_signal = VoiceSignalPayload.model_validate(event.d or {})
                if not await allow_operation(
                    (
                        f"voice-signal:{connection.user_id}:"
                        f"{voice_signal.channel_id}:{voice_signal.target_user_id}"
                    ),
                    VOICE_SIGNAL_LIMIT,
                ):
                    await close_rate_limited(websocket, "voice-signal")
                    return
                if connection.voice_channel_id != voice_signal.channel_id:
                    logger.warning(
                        "gateway voice signal rejected "
                        "reason=voice-channel user_id=%s channel_id=%s",
                        connection.user_id,
                        voice_signal.channel_id,
                    )
                    await websocket.close(code=4003, reason="not connected to voice channel")
                    return

                sent = await gateway_manager.send_voice_signal(
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
                        "screen_sharing": voice_signal.screen_sharing,
                    },
                )
                logger.info(
                    "gateway voice signal "
                    "user_id=%s target_user_id=%s channel_id=%s type=%s sent=%s",
                    connection.user_id,
                    voice_signal.target_user_id,
                    voice_signal.channel_id,
                    voice_signal.type,
                    sent,
                )
                continue

            await websocket.close(code=4002, reason="unsupported opcode")
            return

    except (WebSocketDisconnect, ValidationError):
        pass
    finally:
        await gateway_manager.disconnect(connection)
        logger.info(
            "gateway disconnect user_id=%s active=%s",
            connection.user_id,
            gateway_manager.size,
        )
