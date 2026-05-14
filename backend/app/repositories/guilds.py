from app.db.pool import database
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.auth import UserPublic
from app.schemas.guild import ChannelCreate, ChannelRead, GuildRead, MemberRead, MessageRead

id_generator = SnowflakeGenerator(worker_id=2)


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

        guilds: list[GuildRead] = []
        for guild_row in guild_rows:
            guild_id = int(guild_row["id"])
            channels = await self._list_channels(guild_id)
            members = await self._list_members(guild_id, int(guild_row["owner_id"]))
            messages = await self._list_messages(guild_id)
            guilds.append(
                GuildRead(
                    id=guild_id,
                    name=str(guild_row["name"]),
                    owner_id=int(guild_row["owner_id"]),
                    permissions=0,
                    channels=channels,
                    members=members,
                    messages=messages,
                )
            )
        return guilds

    async def create_channel(self, guild_id: int, payload: ChannelCreate) -> ChannelRead:
        guild_exists = await database.fetchrow("SELECT id FROM guilds WHERE id = $1", guild_id)
        if guild_exists is None:
            raise KeyError(guild_id)

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
        channel_exists = await database.fetchrow(
            "SELECT id FROM channels WHERE id = $1",
            channel_id,
        )
        if channel_exists is None:
            raise KeyError(channel_id)

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


guild_repository = GuildRepository()
