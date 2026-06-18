from app.db.pool import database
from app.demo.data import create_initial_guilds

DM_PROFILES = [
    (42, "yangbun", "yangbun", "online", None),
    (701, "Mina", "mina.study", "online", "Reading in voice"),
    (702, "Joon", "joon.dev", "online", "Working on layout"),
    (703, "Rina", "rina.notes", "idle", "Reviewing notes"),
    (704, "Haru", "haru.music", "offline", None),
    (705, "Nora", "nora.design", "offline", None),
]

RELATIONSHIPS = [
    (42, 701, "friend"),
    (42, 702, "friend"),
    (42, 703, "friend"),
    (42, 704, "friend"),
    (42, 705, "pending_incoming"),
]

DM_SEEDS = [
    (
        801,
        [42, 701],
        2,
        [
            (8101, 701, "오늘 자료방 정리는 끝났어."),
            (8102, 42, "좋아. 채널 목록도 더 깔끔하게 맞춰볼게."),
        ],
    ),
    (
        802,
        [42, 702],
        0,
        [(8201, 702, "저녁에 음성 채널에서 다시 얘기하자.")],
    ),
    (
        803,
        [42, 701, 702, 703],
        1,
        [(8301, 703, "회의 전에 공유할 파일만 정리해둘게.")],
    ),
]


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

    await seed_dm_workspace()


async def seed_dm_workspace() -> None:
    for user_id, username, handle, presence_status, activity in DM_PROFILES:
        await database.execute(
            """
            INSERT INTO users (id, username, password_hash, status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO NOTHING
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
                unread_count if participant_id == 42 else 0,
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
