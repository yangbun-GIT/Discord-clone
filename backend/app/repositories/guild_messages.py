from __future__ import annotations

from typing import Any

from app.db.pool import database
from app.domain.permissions import Permission, has_permission
from app.repositories.guild_common import ensure_user, id_generator, permissions_for_member
from app.schemas.auth import UserPublic
from app.schemas.guild import MessageRead
from app.schemas.message import MessageDeleteRead


class MessageRepository:
    async def create_message(
        self,
        *,
        channel_id: int,
        author: UserPublic,
        content: str,
    ) -> MessageRead:
        channel_row = await database.fetchrow(
            """
            SELECT c.id, c.guild_id, c.type, g.owner_id
            FROM channels c
            JOIN guilds g ON g.id = c.guild_id
            WHERE c.id = $1
            """,
            channel_id,
        )
        if channel_row is None:
            raise KeyError(channel_id)
        if int(channel_row["type"]) != 0:
            raise ValueError("messages can only be created in text channels")
        permissions = await permissions_for_member(
            int(channel_row["guild_id"]),
            author.id,
            int(channel_row["owner_id"]),
        )
        if not has_permission(permissions, Permission.SEND_MESSAGES):
            raise PermissionError("send messages permission required")

        await ensure_user(author)

        message = MessageRead(
            id=id_generator.generate(),
            channel_id=channel_id,
            author_id=author.id,
            author_name=author.username,
            content=content,
        )
        await database.execute(
            """
            INSERT INTO messages (id, channel_id, author_id, content)
            VALUES ($1, $2, $3, $4)
            """,
            message.id,
            message.channel_id,
            message.author_id,
            message.content,
        )
        return message

    async def update_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
        content: str,
    ) -> MessageRead:
        row = await self._get_message_row(channel_id, message_id)
        await self._require_message_author_or_manager(row, actor)

        await database.execute(
            """
            UPDATE messages
            SET content = $1
            WHERE id = $2 AND channel_id = $3
            """,
            content,
            message_id,
            channel_id,
        )
        return MessageRead(
            id=int(row["id"]),
            channel_id=int(row["channel_id"]),
            author_id=int(row["author_id"]),
            author_name=str(row["author_name"]),
            content=content,
        )

    async def delete_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> MessageDeleteRead:
        row = await self._get_message_row(channel_id, message_id)
        await self._require_message_author_or_manager(row, actor)

        await database.execute(
            """
            DELETE FROM messages
            WHERE id = $1 AND channel_id = $2
            """,
            message_id,
            channel_id,
        )
        return MessageDeleteRead(id=message_id, channel_id=channel_id)

    async def _get_message_row(self, channel_id: int, message_id: int) -> Any:
        row = await database.fetchrow(
            """
            SELECT
                m.id,
                m.channel_id,
                m.author_id,
                u.username AS author_name,
                c.guild_id,
                c.type,
                g.owner_id
            FROM messages m
            JOIN channels c ON c.id = m.channel_id
            JOIN guilds g ON g.id = c.guild_id
            JOIN users u ON u.id = m.author_id
            WHERE m.id = $1 AND m.channel_id = $2
            """,
            message_id,
            channel_id,
        )
        if row is None:
            raise KeyError(message_id)
        if int(row["type"]) != 0:
            raise ValueError("messages can only be managed in text channels")
        return row

    async def _require_message_author_or_manager(self, row: Any, actor: UserPublic) -> None:
        permissions = await permissions_for_member(
            int(row["guild_id"]),
            actor.id,
            int(row["owner_id"]),
        )
        if actor.id == int(row["author_id"]):
            return
        if has_permission(permissions, Permission.MANAGE_MESSAGES):
            return
        raise PermissionError("message author or manage messages permission required")


message_repository = MessageRepository()
