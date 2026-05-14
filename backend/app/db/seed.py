from app.db.pool import database
from app.demo.data import create_initial_guilds


async def seed_database() -> None:
    guilds = create_initial_guilds()
    for guild in guilds:
        existing_guild = await database.fetchrow(
            "SELECT id FROM guilds WHERE id = $1",
            guild.id,
        )
        if existing_guild is not None:
            continue

        for member in guild.members:
            await database.execute(
                """
                INSERT INTO users (id, username, password_hash, status)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO NOTHING
                """,
                member.id,
                member.username,
                "dev-session",
                member.status,
            )

        await database.execute(
            """
            INSERT INTO guilds (id, name, owner_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO NOTHING
            """,
            guild.id,
            guild.name,
            guild.owner_id,
        )

        for member in guild.members:
            await database.execute(
                """
                INSERT INTO guild_members (guild_id, user_id)
                VALUES ($1, $2)
                ON CONFLICT (guild_id, user_id) DO NOTHING
                """,
                guild.id,
                member.id,
            )

        for channel in guild.channels:
            await database.execute(
                """
                INSERT INTO channels (id, guild_id, name, type, position)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO NOTHING
                """,
                channel.id,
                channel.guild_id,
                channel.name,
                channel.type,
                channel.position,
            )

        for message in guild.messages:
            await database.execute(
                """
                INSERT INTO messages (id, channel_id, author_id, content)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO NOTHING
                """,
                message.id,
                message.channel_id,
                message.author_id,
                message.content,
            )
