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

