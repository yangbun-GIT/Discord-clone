from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.dm import UserPresenceStatus


class GatewayEvent(BaseModel):
    op: int
    d: dict[str, Any] | None = None
    s: int | None = None
    t: str | None = None


class IdentifyPayload(BaseModel):
    token: str = Field(min_length=1)
    os: str | None = None
    library: str | None = None


class VoiceStatePayload(BaseModel):
    context_type: Literal["guild", "dm"] = "guild"
    guild_id: int | None = None
    channel_id: int | None = None
    dm_id: int | None = None
    self_mute: bool = False
    self_deaf: bool = False


class VoiceSignalPayload(BaseModel):
    context_type: Literal["guild", "dm"] = "guild"
    channel_id: int
    dm_id: int | None = None
    target_user_id: int
    type: str = Field(pattern="^(offer|answer|ice|screen)$")
    description: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    screen_sharing: bool | None = None


class PresenceUpdatePayload(BaseModel):
    status: UserPresenceStatus
    activity: str | None = Field(default=None, max_length=120)
