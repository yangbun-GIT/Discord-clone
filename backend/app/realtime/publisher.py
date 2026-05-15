from app.gateway.manager import gateway_manager
from app.realtime.events import GATEWAY_EVENTS_CHANNEL, RealtimeGatewayEvent
from app.realtime.redis_bus import redis_bus
from app.schemas.guild import ChannelRead, GuildRead, MessageRead


async def publish_message_create(message: MessageRead) -> None:
    event = RealtimeGatewayEvent(
        channel_id=message.channel_id,
        event="MESSAGE_CREATE",
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


async def _publish_or_broadcast(event: RealtimeGatewayEvent) -> None:
    if redis_bus.is_connected:
        await redis_bus.publish_json(GATEWAY_EVENTS_CHANNEL, event.model_dump_json())
        return

    _sync_local_subscriptions(event)
    if event.channel_id is not None:
        await gateway_manager.broadcast_channel(event.channel_id, event.event, event.data)
    elif event.guild_id is not None:
        await gateway_manager.broadcast_guild(event.guild_id, event.event, event.data)


def _sync_local_subscriptions(event: RealtimeGatewayEvent) -> None:
    if event.event == "CHANNEL_CREATE" and event.guild_id is not None:
        channel_id = event.data.get("id")
        if isinstance(channel_id, int):
            gateway_manager.add_channel_to_guild_subscribers(event.guild_id, channel_id)
        return

    if event.event != "GUILD_UPDATE" or event.guild_id is None:
        return

    members = event.data.get("members")
    channels = event.data.get("channels")
    if not isinstance(members, list) or not isinstance(channels, list):
        return

    member_ids = {
        member.get("id")
        for member in members
        if isinstance(member, dict) and isinstance(member.get("id"), int)
    }
    channel_ids = {
        channel.get("id")
        for channel in channels
        if isinstance(channel, dict) and isinstance(channel.get("id"), int)
    }
    gateway_manager.sync_guild_subscribers(
        event.guild_id,
        member_ids=member_ids,
        channel_ids=channel_ids,
    )
