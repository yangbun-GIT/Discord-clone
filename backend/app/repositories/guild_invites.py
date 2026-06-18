from __future__ import annotations

from app.repositories.guilds import guild_repository
from app.schemas.auth import UserPublic
from app.schemas.guild import GuildRead, InviteRead


class InviteRepository:
    async def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead:
        return await guild_repository.create_invite(guild_id, actor)

    async def join_invite(self, code: str, user: UserPublic) -> GuildRead:
        return await guild_repository.join_invite(code, user)


invite_repository = InviteRepository()
