from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from app.schemas.auth import UserPublic


class IdGenerator(Protocol):
    def generate(self) -> int: ...


FindExistingDm = Callable[[list[int]], Awaitable[int | None]]

DEMO_DM_PROFILES = [
    (701, "Mina", "mina.study", "online", "Reading in voice"),
    (702, "Joon", "joon.dev", "online", "Working on layout"),
    (703, "Rina", "rina.notes", "idle", "Reviewing notes"),
    (704, "Haru", "haru.music", "offline", None),
    (705, "Nora", "nora.design", "offline", None),
    (706, "Tae", "tae.voice", "online", "In a voice channel"),
]

DEMO_RELATIONSHIPS = [
    (701, "friend"),
    (702, "friend"),
    (703, "friend"),
    (704, "friend"),
    (705, "pending_incoming"),
    (706, "friend"),
]

DEMO_DM_MESSAGES = [
    (701, "오늘 자료방 정리했어요."),
    (702, "작업 끝나면 음성 채널에서 다시 얘기하자."),
    (706, "마이크 들어오면 테두리로만 표시하면 좋겠어."),
]


async def ensure_dm_repository_user(database: Any, user: UserPublic) -> None:
    await database.execute(
        """
        INSERT INTO users (id, username, password_hash, status)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (id) DO NOTHING
        """,
        user.id,
        user.username,
        "dev-session",
        user.status,
    )


async def ensure_postgres_dm_demo_workspace(
    *,
    database: Any,
    id_generator: IdGenerator,
    user_id: int,
    find_existing_dm: FindExistingDm,
) -> None:
    for profile_id, username, handle, status, activity in DEMO_DM_PROFILES:
        await database.execute(
            """
            INSERT INTO users (id, username, password_hash, status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                status = EXCLUDED.status
            """,
            profile_id,
            username,
            "dev-session",
            1 if status == "online" else 0,
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
            profile_id,
            handle,
            status,
            activity,
        )

    relationship_count = await database.fetchrow(
        "SELECT COUNT(*) AS count FROM relationships WHERE user_id = $1",
        user_id,
    )
    if relationship_count is not None and int(relationship_count["count"]) == 0:
        for related_user_id, relationship in DEMO_RELATIONSHIPS:
            if related_user_id == user_id:
                continue
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

    dm_count = await database.fetchrow(
        "SELECT COUNT(*) AS count FROM direct_message_members WHERE user_id = $1",
        user_id,
    )
    if dm_count is None or int(dm_count["count"]) > 0:
        return

    for related_user_id, message in DEMO_DM_MESSAGES:
        existing_dm_id = await find_existing_dm(sorted([user_id, related_user_id]))
        dm_id = existing_dm_id or id_generator.generate()
        if existing_dm_id is not None:
            continue
        await database.execute(
            """
            INSERT INTO direct_message_channels (id, is_group)
            VALUES ($1, false)
            """,
            dm_id,
        )
        for participant_id in (user_id, related_user_id):
            await database.execute(
                """
                INSERT INTO direct_message_members (dm_id, user_id, unread_count)
                VALUES ($1, $2, $3)
                ON CONFLICT (dm_id, user_id) DO NOTHING
                """,
                dm_id,
                participant_id,
                1 if participant_id == user_id else 0,
            )
        await database.execute(
            """
            INSERT INTO direct_messages (id, dm_id, author_id, content)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO NOTHING
            """,
            id_generator.generate(),
            dm_id,
            related_user_id,
            message,
        )
