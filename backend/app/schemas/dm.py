from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.core.sanitize import sanitize_message_content
from app.domain.permissions import MAX_JS_SAFE_INTEGER

UserPresenceStatus = Literal["online", "idle", "dnd", "offline"]
RelationshipState = Literal["friend", "pending_incoming", "pending_outgoing", "blocked"]


class RelationshipRead(BaseModel):
    id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    username: str = Field(min_length=1, max_length=80)
    handle: str = Field(min_length=1, max_length=80)
    status: UserPresenceStatus
    activity: str | None = Field(default=None, max_length=120)
    relationship: RelationshipState


class RelationshipRequestCreate(BaseModel):
    username: str = Field(min_length=2, max_length=80)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("username cannot be empty")
        return normalized


class RelationshipDeleteRead(BaseModel):
    id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)


class DmParticipantRead(BaseModel):
    id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    username: str = Field(min_length=1, max_length=80)
    handle: str = Field(min_length=1, max_length=80)
    status: UserPresenceStatus
    activity: str | None = Field(default=None, max_length=120)


class DmMessageRead(BaseModel):
    id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    dm_id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    author_id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    author_name: str = Field(min_length=1, max_length=80)
    content: str


class DmRead(BaseModel):
    id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    recipient_ids: list[int] = Field(min_length=1, max_length=9)
    participants: list[DmParticipantRead] = Field(min_length=2, max_length=10)
    display_name: str = Field(min_length=1, max_length=120)
    status: UserPresenceStatus
    activity: str | None = Field(default=None, max_length=120)
    unread_count: int = Field(ge=0, le=999)
    is_group: bool
    member_count: int = Field(ge=2, le=10)
    messages: list[DmMessageRead] = Field(default_factory=list)


class DmCreate(BaseModel):
    recipient_ids: list[int] = Field(min_length=1, max_length=9)


class DmMessageCreate(BaseModel):
    dm_id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, value: str) -> str:
        sanitized = sanitize_message_content(value)
        if not sanitized:
            raise ValueError("message content cannot be empty")
        return sanitized
