from typing import Any

from pydantic import BaseModel, Field, model_validator

GATEWAY_EVENTS_CHANNEL = "discord_clone:gateway_events"


class RealtimeGatewayEvent(BaseModel):
    channel_id: int | None = None
    guild_id: int | None = None
    dm_id: int | None = None
    event: str = Field(min_length=1)
    data: dict[str, Any]

    @model_validator(mode="after")
    def require_target(self) -> RealtimeGatewayEvent:
        if self.channel_id is None and self.guild_id is None and self.dm_id is None:
            raise ValueError("channel_id, guild_id, or dm_id is required")
        return self
