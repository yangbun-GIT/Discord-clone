from app.db.pool import database
from app.demo.data import create_initial_guilds
from app.repositories.dm_seed import (
    ADMIN_DEMO_USER_ID,
    GUIDE_DM_ID_OFFSET,
    GUIDE_HANDLE,
    GUIDE_MESSAGE,
    GUIDE_USER_ID,
    GUIDE_USERNAME,
)

DM_PROFILES = [
    (ADMIN_DEMO_USER_ID, "admin", "admin", "online", None),
    (GUIDE_USER_ID, GUIDE_USERNAME, GUIDE_HANDLE, "online", "Clone guide"),
]

RELATIONSHIPS = [
    (ADMIN_DEMO_USER_ID, GUIDE_USER_ID, "friend"),
]

DM_SEEDS = [
    (
        GUIDE_DM_ID_OFFSET + ADMIN_DEMO_USER_ID,
        [ADMIN_DEMO_USER_ID, GUIDE_USER_ID],
        1,
        [(GUIDE_DM_ID_OFFSET + ADMIN_DEMO_USER_ID + 1, GUIDE_USER_ID, GUIDE_MESSAGE)],
    ),
]


async def seed_database() -> None:
    await release_reserved_seed_usernames()
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
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    status = EXCLUDED.status
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

    await seed_dm_workspace()


async def release_reserved_seed_usernames() -> None:
    reserved_users = [(ADMIN_DEMO_USER_ID, "admin"), (GUIDE_USER_ID, GUIDE_USERNAME)]
    for reserved_id, username in reserved_users:
        await database.execute(
            """
            UPDATE users
            SET username = username || '_legacy_' || id::text
            WHERE username = $1 AND id <> $2
            """,
            username,
            reserved_id,
        )


async def seed_dm_workspace() -> None:
    for user_id, username, handle, presence_status, activity in DM_PROFILES:
        await database.execute(
            """
            INSERT INTO users (id, username, password_hash, status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                status = EXCLUDED.status
            """,
            user_id,
            username,
            "dev-session",
            1 if presence_status == "online" else 0,
        )
        await database.execute(
            """
            INSERT INTO dm_profiles (user_id, handle, presence_status, activity)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE SET
                handle = EXCLUDED.handle,
                presence_status = EXCLUDED.presence_status,
                activity = EXCLUDED.activity
            """,
            user_id,
            handle,
            presence_status,
            activity,
        )

    for user_id, related_user_id, relationship in RELATIONSHIPS:
        await database.execute(
            """
            INSERT INTO relationships (user_id, related_user_id, relationship)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, related_user_id) DO NOTHING
            """,
            user_id,
            related_user_id,
            relationship,
        )

    for dm_id, participant_ids, unread_count, messages in DM_SEEDS:
        await database.execute(
            """
            INSERT INTO direct_message_channels (id, is_group)
            VALUES ($1, $2)
            ON CONFLICT (id) DO NOTHING
            """,
            dm_id,
            len(participant_ids) > 2,
        )
        for participant_id in participant_ids:
            await database.execute(
                """
                INSERT INTO direct_message_members (dm_id, user_id, unread_count)
                VALUES ($1, $2, $3)
                ON CONFLICT (dm_id, user_id) DO NOTHING
                """,
                dm_id,
                participant_id,
                unread_count if participant_id == ADMIN_DEMO_USER_ID else 0,
            )
        for message_id, author_id, content in messages:
            await database.execute(
                """
                INSERT INTO direct_messages (id, dm_id, author_id, content)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO NOTHING
                """,
                message_id,
                dm_id,
                author_id,
                content,
            )
