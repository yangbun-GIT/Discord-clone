from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.permissions import MAX_JS_SAFE_INTEGER


class ChannelRead(BaseModel):
    id: int
    guild_id: int
    name: str
    type: int = Field(ge=0, le=1)
    position: int


class ChannelCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$",
    )
    type: int = Field(default=0, ge=0, le=1)


class GuildCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class InviteRead(BaseModel):
    code: str
    guild_id: int
    created_by: int


class RoleRead(BaseModel):
    id: int
    guild_id: int
    name: str
    permissions: int
    position: int


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    permissions: int = Field(default=0, ge=0, le=MAX_JS_SAFE_INTEGER)


class MemberRoleUpdate(BaseModel):
    role_id: int


class MemberRead(BaseModel):
    id: int
    username: str
    status: int
    role: str
    role_ids: list[int] = Field(default_factory=list)


class MessageRead(BaseModel):
    id: int
    channel_id: int
    author_id: int
    author_name: str
    content: str
    created_at: datetime | None = None


class GuildActionRead(BaseModel):
    ok: bool


class GuildRead(BaseModel):
    id: int
    name: str
    owner_id: int
    permissions: int
    channels: list[ChannelRead]
    roles: list[RoleRead] = Field(default_factory=list)
    members: list[MemberRead]
    messages: list[MessageRead]
