from pydantic import BaseModel, Field


class ChannelRead(BaseModel):
    id: int
    guild_id: int
    name: str
    type: int = Field(ge=0, le=1)
    position: int


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

