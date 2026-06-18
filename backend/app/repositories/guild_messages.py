from __future__ import annotations

from app.repositories.guilds import guild_repository
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
        return await guild_repository.create_message(
            channel_id=channel_id,
            author=author,
            content=content,
        )

    async def update_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
        content: str,
    ) -> MessageRead:
        return await guild_repository.update_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=actor,
            content=content,
        )

    async def delete_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> MessageDeleteRead:
        return await guild_repository.delete_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=actor,
        )


message_repository = MessageRepository()
