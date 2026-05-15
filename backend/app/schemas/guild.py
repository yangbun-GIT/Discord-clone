from pydantic import BaseModel, Field


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


class MemberRead(BaseModel):
    id: int
    username: str
    status: int
    role: str


class MessageRead(BaseModel):
    id: int
    channel_id: int
    author_id: int
    author_name: str
    content: str


class GuildRead(BaseModel):
    id: int
    name: str
    owner_id: int
    permissions: int
    channels: list[ChannelRead]
    members: list[MemberRead]
    messages: list[MessageRead]
