from __future__ import annotations

from app.db.pool import database
from app.domain.permissions import Permission, has_permission
from app.repositories.guild_common import id_generator, permissions_for_member
from app.schemas.auth import UserPublic
from app.schemas.guild import ChannelCreate, ChannelRead


class ChannelRepository:
    async def create_channel(
        self,
        guild_id: int,
        payload: ChannelCreate,
        actor: UserPublic,
    ) -> ChannelRead:
        guild_row = await database.fetchrow(
            "SELECT id, owner_id FROM guilds WHERE id = $1",
            guild_id,
        )
        if guild_row is None:
            raise KeyError(guild_id)
        permissions = await permissions_for_member(guild_id, actor.id, int(guild_row["owner_id"]))
        if not has_permission(permissions, Permission.MANAGE_CHANNELS):
            raise PermissionError("manage channels permission required")

        position_row = await database.fetchrow(
            """
            SELECT COALESCE(MAX(position), -1) + 1 AS next_position
            FROM channels
            WHERE guild_id = $1
            """,
            guild_id,
        )
        channel = ChannelRead(
            id=id_generator.generate(),
            guild_id=guild_id,
            name=payload.name,
            type=payload.type,
            position=int(position_row["next_position"]) if position_row else 0,
        )
        await database.execute(
            """
            INSERT INTO channels (id, guild_id, name, type, position)
            VALUES ($1, $2, $3, $4, $5)
            """,
            channel.id,
            channel.guild_id,
            channel.name,
            channel.type,
            channel.position,
        )
        return channel


channel_repository = ChannelRepository()
