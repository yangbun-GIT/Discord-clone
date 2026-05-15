from typing import Any

from pydantic import BaseModel, Field


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
    guild_id: int
    channel_id: int | None = None
    self_mute: bool = False
    self_deaf: bool = False


class VoiceSignalPayload(BaseModel):
    channel_id: int
    target_user_id: int
    type: str = Field(pattern="^(offer|answer|ice)$")
    description: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
