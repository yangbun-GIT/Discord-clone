from app.gateway.manager import gateway_manager
from app.realtime.events import GATEWAY_EVENTS_CHANNEL, RealtimeGatewayEvent
from app.realtime.redis_bus import redis_bus
from app.schemas.guild import MessageRead


async def publish_message_create(message: MessageRead) -> None:
    event = RealtimeGatewayEvent(
        channel_id=message.channel_id,
        event="MESSAGE_CREATE",
        data=message.model_dump(),
    )
    if redis_bus.is_connected:
        await redis_bus.publish_json(GATEWAY_EVENTS_CHANNEL, event.model_dump_json())
        return

    await gateway_manager.broadcast_channel(
        event.channel_id,
        event.event,
        event.data,
    )

