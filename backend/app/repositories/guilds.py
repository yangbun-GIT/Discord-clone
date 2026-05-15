import secrets
from typing import Any

from app.db.pool import database
from app.domain.permissions import ALL_PERMISSIONS, Permission, has_permission, merge_permissions
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.auth import UserPublic
from app.schemas.guild import (
    ChannelCreate,
    ChannelRead,
    GuildCreate,
    GuildRead,
    InviteRead,
    MemberRead,
    MessageRead,
)

id_generator = SnowflakeGenerator(worker_id=2)
BASE_MEMBER_PERMISSIONS = merge_permissions(
    [
        Permission.READ_MESSAGES,
        Permission.SEND_MESSAGES,
        Permission.CONNECT,
        Permission.SPEAK,
    ]
)


class GuildRepository:
    async def list_for_user(self, user_id: int) -> list[GuildRead]:
        guild_rows = await database.fetch(
            """
            SELECT g.id, g.name, g.owner_id
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            WHERE gm.user_id = $1
            ORDER BY g.created_at ASC, g.id ASC
            """,
            user_id,
        )

        return [await self._read_guild(guild_row, user_id) for guild_row in guild_rows]

    async def get_for_user(self, guild_id: int, user_id: int) -> GuildRead | None:
        guild_row = await database.fetchrow(
            """
            SELECT g.id, g.name, g.owner_id
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            WHERE g.id = $1 AND gm.user_id = $2
            """,
            guild_id,
            user_id,
        )
        if guild_row is None:
            return None
        return await self._read_guild(guild_row, user_id)

    async def create_guild(self, payload: GuildCreate, owner: UserPublic) -> GuildRead:
        guild_id = id_generator.generate()
        text_channel = ChannelRead(
            id=id_generator.generate(),
            guild_id=guild_id,
            name="general",
            type=0,
            position=0,
        )
        voice_channel = ChannelRead(
            id=id_generator.generate(),
            guild_id=guild_id,
            name="voice-room",
            type=1,
            position=1,
        )

        await database.execute(
            """
            INSERT INTO users (id, username, password_hash, status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE
            SET username = EXCLUDED.username,
                status = EXCLUDED.status
            """,
            owner.id,
            owner.username,
            "dev-session",
            owner.status,
        )
        await database.execute(
            """
            INSERT INTO guilds (id, name, owner_id)
            VALUES ($1, $2, $3)
            """,
            guild_id,
            payload.name,
            owner.id,
        )
        await database.execute(
            """
            INSERT INTO guild_members (guild_id, user_id)
            VALUES ($1, $2)
            """,
            guild_id,
            owner.id,
        )
        await database.execute(
            """
            INSERT INTO channels (id, guild_id, name, type, position)
            VALUES ($1, $2, $3, $4, $5), ($6, $7, $8, $9, $10)
            """,
            text_channel.id,
            text_channel.guild_id,
            text_channel.name,
            text_channel.type,
            text_channel.position,
            voice_channel.id,
            voice_channel.guild_id,
            voice_channel.name,
            voice_channel.type,
            voice_channel.position,
        )
        return GuildRead(
            id=guild_id,
            name=payload.name,
            owner_id=owner.id,
            permissions=ALL_PERMISSIONS,
            channels=[text_channel, voice_channel],
            members=[
                MemberRead(
                    id=owner.id,
                    username=owner.username,
                    status=owner.status,
                    role="Owner",
                )
            ],
            messages=[],
        )

    async def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead:
        guild_row = await database.fetchrow(
            "SELECT id, owner_id FROM guilds WHERE id = $1",
            guild_id,
        )
        if guild_row is None:
            raise KeyError(guild_id)

        permissions = await self._permissions_for_member(
            guild_id,
            actor.id,
            int(guild_row["owner_id"]),
        )
        if not has_permission(permissions, Permission.CREATE_INSTANT_INVITE):
            raise PermissionError("create invite permission required")

        for _ in range(5):
            code = secrets.token_urlsafe(8)
            result = await database.execute(
                """
                INSERT INTO invites (code, guild_id, creator_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (code) DO NOTHING
                """,
                code,
                guild_id,
                actor.id,
            )
            if result == "INSERT 0 1":
                return InviteRead(code=code, guild_id=guild_id, created_by=actor.id)
        raise RuntimeError("could not create unique invite code")

    async def join_invite(self, code: str, user: UserPublic) -> GuildRead:
        invite_row = await database.fetchrow(
            """
            SELECT guild_id
            FROM invites
            WHERE code = $1
            """,
            code,
        )
        if invite_row is None:
            raise KeyError(code)

        await database.execute(
            """
            INSERT INTO users (id, username, password_hash, status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE
            SET username = EXCLUDED.username,
                status = EXCLUDED.status
            """,
            user.id,
            user.username,
            "dev-session",
            user.status,
        )
        await database.execute(
            """
            INSERT INTO guild_members (guild_id, user_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id, user_id) DO NOTHING
            """,
            int(invite_row["guild_id"]),
            user.id,
        )
        guild = await self.get_for_user(int(invite_row["guild_id"]), user.id)
        if guild is None:
            raise KeyError(code)
        return guild

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
        permissions = await self._permissions_for_member(
            guild_id,
            actor.id,
            int(guild_row["owner_id"]),
        )
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
        position = int(position_row["next_position"]) if position_row else 0
        channel = ChannelRead(
            id=id_generator.generate(),
            guild_id=guild_id,
            name=payload.name,
            type=payload.type,
            position=position,
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
        permissions = await self._permissions_for_member(
            int(channel_row["guild_id"]),
            author.id,
            int(channel_row["owner_id"]),
        )
        if not has_permission(permissions, Permission.SEND_MESSAGES):
            raise PermissionError("send messages permission required")

        await database.execute(
            """
            INSERT INTO users (id, username, password_hash, status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE
            SET username = EXCLUDED.username,
                status = EXCLUDED.status
            """,
            author.id,
            author.username,
            "dev-session",
            author.status,
        )

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

    async def _list_channels(self, guild_id: int) -> list[ChannelRead]:
        rows = await database.fetch(
            """
            SELECT id, guild_id, name, type, position
            FROM channels
            WHERE guild_id = $1
            ORDER BY position ASC, id ASC
            """,
            guild_id,
        )
        return [
            ChannelRead(
                id=int(row["id"]),
                guild_id=int(row["guild_id"]),
                name=str(row["name"]),
                type=int(row["type"]),
                position=int(row["position"]),
            )
            for row in rows
        ]

    async def _read_guild(self, guild_row: Any, user_id: int) -> GuildRead:
        guild_id = int(guild_row["id"])
        owner_id = int(guild_row["owner_id"])
        return GuildRead(
            id=guild_id,
            name=str(guild_row["name"]),
            owner_id=owner_id,
            permissions=await self._permissions_for_member(guild_id, user_id, owner_id),
            channels=await self._list_channels(guild_id),
            members=await self._list_members(guild_id, owner_id),
            messages=await self._list_messages(guild_id),
        )

    async def _list_members(self, guild_id: int, owner_id: int) -> list[MemberRead]:
        rows = await database.fetch(
            """
            SELECT u.id, u.username, u.status
            FROM users u
            JOIN guild_members gm ON gm.user_id = u.id
            WHERE gm.guild_id = $1
            ORDER BY u.username ASC
            """,
            guild_id,
        )
        return [
            MemberRead(
                id=int(row["id"]),
                username=str(row["username"]),
                status=int(row["status"]),
                role="Owner" if int(row["id"]) == owner_id else "Member",
            )
            for row in rows
        ]

    async def _list_messages(self, guild_id: int) -> list[MessageRead]:
        rows = await database.fetch(
            """
            SELECT m.id, m.channel_id, m.author_id, u.username AS author_name, m.content
            FROM messages m
            JOIN channels c ON c.id = m.channel_id
            JOIN users u ON u.id = m.author_id
            WHERE c.guild_id = $1
            ORDER BY m.id ASC
            LIMIT 200
            """,
            guild_id,
        )
        return [
            MessageRead(
                id=int(row["id"]),
                channel_id=int(row["channel_id"]),
                author_id=int(row["author_id"]),
                author_name=str(row["author_name"]),
                content=str(row["content"]),
            )
            for row in rows
        ]

    async def _permissions_for_member(
        self,
        guild_id: int,
        user_id: int,
        owner_id: int,
    ) -> int:
        membership = await database.fetchrow(
            """
            SELECT 1
            FROM guild_members
            WHERE guild_id = $1 AND user_id = $2
            """,
            guild_id,
            user_id,
        )
        if membership is None:
            return 0
        if user_id == owner_id:
            return ALL_PERMISSIONS

        role_rows = await database.fetch(
            """
            SELECT r.permissions
            FROM roles r
            JOIN member_roles mr ON mr.role_id = r.id
            WHERE mr.guild_id = $1 AND mr.user_id = $2
            """,
            guild_id,
            user_id,
        )
        role_permissions = [int(row["permissions"]) for row in role_rows]
        return merge_permissions([BASE_MEMBER_PERMISSIONS, *role_permissions])


guild_repository = GuildRepository()
