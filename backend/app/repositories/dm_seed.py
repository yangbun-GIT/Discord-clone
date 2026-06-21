from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from app.schemas.auth import UserPublic


class IdGenerator(Protocol):
    def generate(self) -> int: ...


FindExistingDm = Callable[[list[int]], Awaitable[int | None]]

ADMIN_DEMO_USER_ID = 42
GUIDE_USER_ID = 700
GUIDE_DM_ID_OFFSET = 80_000_000_000_000
GUIDE_USERNAME = "Guide"
GUIDE_HANDLE = "discord.guide"
GUIDE_MESSAGE = (
    "Discord Clone에 오신 것을 환영합니다. 왼쪽 사이드바에서 친구와 서버를 이동하고, "
    "친구 추가, DM, 서버 초대, 텍스트 채팅, 음성 채널, 화면 공유를 확인해 보세요. "
    "하단 사용자 패널의 설정에서 언어와 음성 장치를 조정할 수 있습니다."
)

DEMO_DM_PROFILES = [
    (GUIDE_USER_ID, GUIDE_USERNAME, GUIDE_HANDLE, "online", "Clone guide"),
    (701, "Mina", "mina.study", "online", "Reading in voice"),
    (702, "Joon", "joon.dev", "online", "Working on layout"),
    (703, "Rina", "rina.notes", "idle", "Reviewing notes"),
    (704, "Haru", "haru.music", "offline", None),
    (705, "Nora", "nora.design", "offline", None),
    (706, "Tae", "tae.voice", "online", "In a voice channel"),
]

ADMIN_DEMO_RELATIONSHIPS = [
    (701, "friend"),
    (702, "friend"),
    (703, "friend"),
    (704, "friend"),
    (705, "pending_incoming"),
    (706, "friend"),
]

ADMIN_DEMO_DM_MESSAGES = [
    (701, "오늘 자료방 정리했어요."),
    (702, "작업 끝나면 음성 채널에서 다시 얘기하자."),
    (706, "마이크 들어오면 테두리로만 표시하면 좋겠어."),
]

DEMO_WORKSPACE_LOCK_OFFSET = 30_000_000_000_000


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
    lock_key = DEMO_WORKSPACE_LOCK_OFFSET + user_id
    await database.execute("SELECT pg_advisory_lock($1)", lock_key)
    try:
        await _ensure_postgres_dm_demo_workspace_locked(
            database=database,
            id_generator=id_generator,
            user_id=user_id,
            find_existing_dm=find_existing_dm,
        )
    finally:
        await database.execute("SELECT pg_advisory_unlock($1)", lock_key)


async def reset_postgres_development_workspace(
    *,
    database: Any,
    id_generator: IdGenerator,
    user_id: int,
    username: str,
    find_existing_dm: FindExistingDm,
) -> None:
    if user_id != ADMIN_DEMO_USER_ID:
        raise PermissionError(
            "development workspace reset is only available for the admin test account",
        )

    lock_key = DEMO_WORKSPACE_LOCK_OFFSET + user_id
    await database.execute("SELECT pg_advisory_lock($1)", lock_key)
    try:
        await _release_reserved_seed_usernames(database)
        await _reset_postgres_development_workspace_locked(
            database=database,
            user_id=user_id,
            username=username,
        )
        await _ensure_postgres_dm_demo_workspace_locked(
            database=database,
            id_generator=id_generator,
            user_id=user_id,
            find_existing_dm=find_existing_dm,
        )
    finally:
        await database.execute("SELECT pg_advisory_unlock($1)", lock_key)


async def _reset_postgres_development_workspace_locked(
    *,
    database: Any,
    user_id: int,
    username: str,
) -> None:
    dm_rows = await database.fetch(
        "SELECT dm_id FROM direct_message_members WHERE user_id = $1",
        user_id,
    )
    dm_ids = [int(row["dm_id"]) for row in dm_rows]
    if dm_ids:
        await database.execute(
            "DELETE FROM direct_message_channels WHERE id = ANY($1::bigint[])",
            dm_ids,
        )

    await database.execute(
        "DELETE FROM relationships WHERE user_id = $1 OR related_user_id = $1",
        user_id,
    )
    await database.execute(
        "DELETE FROM user_server_rail_layouts WHERE user_id = $1",
        user_id,
    )
    await database.execute(
        """
        INSERT INTO users (id, username, password_hash, status)
        VALUES ($1, $2, $3, 1)
        ON CONFLICT (id) DO UPDATE SET
            username = EXCLUDED.username,
            status = EXCLUDED.status
        """,
        user_id,
        username,
        "dev-session",
    )
    await database.execute(
        """
        INSERT INTO dm_profiles (user_id, handle, presence_status, activity)
        VALUES ($1, $2, 'online', NULL)
        ON CONFLICT (user_id) DO UPDATE SET
            handle = EXCLUDED.handle,
            presence_status = EXCLUDED.presence_status,
            activity = EXCLUDED.activity
        """,
        user_id,
        username.lower(),
    )


async def _ensure_postgres_dm_demo_workspace_locked(
    *,
    database: Any,
    id_generator: IdGenerator,
    user_id: int,
    find_existing_dm: FindExistingDm,
) -> None:
    await _release_reserved_seed_usernames(database)
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
        relationships = (
            ADMIN_DEMO_RELATIONSHIPS
            if user_id == ADMIN_DEMO_USER_ID
            else [(GUIDE_USER_ID, "friend")]
        )
        for related_user_id, relationship in relationships:
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

    dm_messages = (
        ADMIN_DEMO_DM_MESSAGES
        if user_id == ADMIN_DEMO_USER_ID
        else [(GUIDE_USER_ID, GUIDE_MESSAGE)]
    )
    for related_user_id, message in dm_messages:
        existing_dm_id = await find_existing_dm(sorted([user_id, related_user_id]))
        dm_id = existing_dm_id or (
            GUIDE_DM_ID_OFFSET + user_id
            if related_user_id == GUIDE_USER_ID
            else id_generator.generate()
        )
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


async def _release_reserved_seed_usernames(database: Any) -> None:
    reserved_users = [
        (ADMIN_DEMO_USER_ID, "admin"),
        (GUIDE_USER_ID, GUIDE_USERNAME),
    ]
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
