from __future__ import annotations

from app.repositories.guilds import guild_repository
from app.schemas.auth import UserPublic
from app.schemas.guild import ChannelCreate, ChannelRead


class ChannelRepository:
    async def create_channel(
        self,
        guild_id: int,
        payload: ChannelCreate,
        actor: UserPublic,
    ) -> ChannelRead:
        return await guild_repository.create_channel(guild_id, payload, actor)


channel_repository = ChannelRepository()
