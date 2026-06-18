from app.realtime.events import GATEWAY_EVENTS_CHANNEL, RealtimeGatewayEvent
from app.realtime.fanout import fanout_gateway_event
from app.realtime.redis_bus import redis_bus
from app.schemas.dm import DmMessageRead, DmRead
from app.schemas.guild import ChannelRead, GuildRead, MessageRead
from app.schemas.message import MessageDeleteRead


async def publish_message_create(message: MessageRead) -> None:
    event = RealtimeGatewayEvent(
        channel_id=message.channel_id,
        event="MESSAGE_CREATE",
        data=message.model_dump(),
    )
    await _publish_or_broadcast(event)


async def publish_message_update(message: MessageRead) -> None:
    event = RealtimeGatewayEvent(
        channel_id=message.channel_id,
        event="MESSAGE_UPDATE",
        data=message.model_dump(),
    )
    await _publish_or_broadcast(event)


async def publish_message_delete(message: MessageDeleteRead) -> None:
    event = RealtimeGatewayEvent(
        channel_id=message.channel_id,
        event="MESSAGE_DELETE",
        data=message.model_dump(),
    )
    await _publish_or_broadcast(event)


async def publish_channel_create(channel: ChannelRead) -> None:
    event = RealtimeGatewayEvent(
        guild_id=channel.guild_id,
        event="CHANNEL_CREATE",
        data=channel.model_dump(),
    )
    await _publish_or_broadcast(event)


async def publish_guild_update(guild: GuildRead) -> None:
    event = RealtimeGatewayEvent(
        guild_id=guild.id,
        event="GUILD_UPDATE",
        data=guild.model_dump(),
    )
    await _publish_or_broadcast(event)


async def publish_dm_create(dm: DmRead) -> None:
    event = RealtimeGatewayEvent(
        dm_id=dm.id,
        event="DM_CREATE",
        data=dm.model_dump(),
    )
    await _publish_or_broadcast(event)


async def publish_dm_message_create(message: DmMessageRead) -> None:
    event = RealtimeGatewayEvent(
        dm_id=message.dm_id,
        event="DM_MESSAGE_CREATE",
        data=message.model_dump(),
    )
    await _publish_or_broadcast(event)


async def _publish_or_broadcast(event: RealtimeGatewayEvent) -> None:
    if redis_bus.is_connected:
        await redis_bus.publish_json(GATEWAY_EVENTS_CHANNEL, event.model_dump_json())
        return

    await fanout_gateway_event(event)
