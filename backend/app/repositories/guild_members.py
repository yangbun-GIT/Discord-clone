from __future__ import annotations

from app.db.pool import database
from app.repositories.guild_common import get_manageable_guild_row, read_guild
from app.schemas.auth import UserPublic
from app.schemas.guild import GuildRead


class MemberRepository:
    async def remove_member(
        self,
        guild_id: int,
        member_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        guild_row = await get_manageable_guild_row(guild_id, actor)
        owner_id = int(guild_row["owner_id"])
        if member_id == owner_id:
            raise ValueError("owner cannot be removed")
        if member_id == actor.id:
            raise ValueError("self-removal is not supported")

        member_row = await database.fetchrow(
            """
            SELECT 1
            FROM guild_members
            WHERE guild_id = $1 AND user_id = $2
            """,
            guild_id,
            member_id,
        )
        if member_row is None:
            raise KeyError(member_id)

        await database.execute(
            """
            DELETE FROM guild_members
            WHERE guild_id = $1 AND user_id = $2
            """,
            guild_id,
            member_id,
        )
        return await read_guild(guild_row, actor.id)


member_repository = MemberRepository()
