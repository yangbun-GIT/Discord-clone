from __future__ import annotations

from app.repositories.guilds import guild_repository
from app.schemas.auth import UserPublic
from app.schemas.guild import GuildRead


class MemberRepository:
    async def remove_member(
        self,
        guild_id: int,
        member_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        return await guild_repository.remove_member(guild_id, member_id, actor)


member_repository = MemberRepository()
