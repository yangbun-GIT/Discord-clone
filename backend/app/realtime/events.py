from typing import Any

from pydantic import BaseModel, Field

GATEWAY_EVENTS_CHANNEL = "discord_clone:gateway_events"


class RealtimeGatewayEvent(BaseModel):
    channel_id: int
    event: str = Field(min_length=1)
    data: dict[str, Any]

