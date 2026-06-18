from collections.abc import Iterable

from app.db.pool import database
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.auth import UserPublic
from app.schemas.dm import (
    DmCreate,
    DmMessageCreate,
    DmMessageRead,
    DmParticipantRead,
    DmRead,
    RelationshipRead,
    UserPresenceStatus,
)

id_generator = SnowflakeGenerator(worker_id=3)

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
    (701, "오늘 자료방 정리는 끝났어."),
    (702, "저녁에 음성 채널에서 다시 얘기하자."),
    (706, "마이크 들어오면 테두리로만 표시되면 좋겠어."),
]


def _status_from_row(value: object) -> UserPresenceStatus:
    if value in {"online", "idle", "dnd", "offline"}:
        return value  # type: ignore[return-value]
    if value == 1:
        return "online"
    if value == 2:
        return "idle"
    if value == 3:
        return "dnd"
    return "offline"


def _display_name(participants: list[DmParticipantRead], user_id: int) -> str:
    others = [participant.username for participant in participants if participant.id != user_id]
    if not others:
        return participants[0].username
    return ", ".join(others[:3])


def _dm_status(participants: list[DmParticipantRead], user_id: int) -> UserPresenceStatus:
    for participant in participants:
        if participant.id != user_id and participant.status != "offline":
            return participant.status
    return "offline"


def _dm_activity(participants: list[DmParticipantRead], user_id: int) -> str | None:
    for participant in participants:
        if participant.id != user_id and participant.activity:
            return participant.activity
    return None


class DmRepository:
    async def list_relationships(self, user_id: int) -> list[RelationshipRead]:
        await self.ensure_demo_workspace_for_user_id(user_id)
        rows = await database.fetch(
            """
            SELECT
                u.id,
                u.username,
                COALESCE(p.handle, u.username) AS handle,
                COALESCE(p.presence_status, u.status::text) AS presence_status,
                p.activity,
                r.relationship
            FROM relationships r
            JOIN users u ON u.id = r.related_user_id
            LEFT JOIN dm_profiles p ON p.user_id = u.id
            WHERE r.user_id = $1
            ORDER BY u.username
            """,
            user_id,
        )
        return [
            RelationshipRead(
                id=int(row["id"]),
                username=str(row["username"]),
                handle=str(row["handle"]),
                status=_status_from_row(row["presence_status"]),
                activity=row["activity"],
                relationship=row["relationship"],
            )
            for row in rows
        ]

    async def list_dms(self, user: UserPublic) -> list[DmRead]:
        await self.ensure_demo_workspace(user)
        rows = await database.fetch(
            """
            SELECT dm_id
            FROM direct_message_members
            WHERE user_id = $1
            ORDER BY joined_at DESC, dm_id DESC
            """,
            user.id,
        )
        dms: list[DmRead] = []
        for row in rows:
            dm = await self.get_dm_for_user(int(row["dm_id"]), user.id)
            if dm is not None:
                dms.append(dm)
        return dms

    async def get_dm_for_user(self, dm_id: int, user_id: int) -> DmRead | None:
        membership = await database.fetchrow(
            """
            SELECT unread_count
            FROM direct_message_members
            WHERE dm_id = $1 AND user_id = $2
            """,
            dm_id,
            user_id,
        )
        if membership is None:
            return None

        channel = await database.fetchrow(
            "SELECT id, is_group FROM direct_message_channels WHERE id = $1",
            dm_id,
        )
        if channel is None:
            return None

        participants = await self._participants(dm_id)
        messages = await self._messages(dm_id)
        return DmRead(
            id=int(channel["id"]),
            recipient_ids=[
                participant.id
                for participant in participants
                if participant.id != user_id
            ],
            participants=participants,
            display_name=_display_name(participants, user_id),
            status=_dm_status(participants, user_id),
            activity=_dm_activity(participants, user_id),
            unread_count=int(membership["unread_count"]),
            is_group=bool(channel["is_group"]),
            member_count=len(participants),
            messages=messages,
        )

    async def create_dm(self, payload: DmCreate, user: UserPublic) -> DmRead:
        recipient_ids = sorted(set(payload.recipient_ids))
        if user.id in recipient_ids:
            raise ValueError("direct message recipient cannot be the current user")

        await self._ensure_user(user)
        recipients = await self._profiles(recipient_ids)
        if len(recipients) != len(recipient_ids):
            raise KeyError("recipient not found")

        participant_ids = sorted([user.id, *recipient_ids])
        existing_dm_id = await self._find_existing_dm(participant_ids)
        if existing_dm_id is not None:
            dm = await self.get_dm_for_user(existing_dm_id, user.id)
            if dm is None:
                raise PermissionError("direct message membership required")
            return dm

        dm_id = id_generator.generate()
        await database.execute(
            """
            INSERT INTO direct_message_channels (id, is_group)
            VALUES ($1, $2)
            """,
            dm_id,
            len(participant_ids) > 2,
        )
        for participant_id in participant_ids:
            await database.execute(
                """
                INSERT INTO direct_message_members (dm_id, user_id)
                VALUES ($1, $2)
                """,
                dm_id,
                participant_id,
            )

        dm = await self.get_dm_for_user(dm_id, user.id)
        if dm is None:
            raise PermissionError("direct message membership required")
        return dm

    async def create_dm_message(
        self,
        *,
        dm_id: int,
        payload: DmMessageCreate,
        author: UserPublic,
    ) -> DmMessageRead:
        membership = await database.fetchrow(
            """
            SELECT 1 AS exists
            FROM direct_message_members
            WHERE dm_id = $1 AND user_id = $2
            """,
            dm_id,
            author.id,
        )
        if membership is None:
            channel = await database.fetchrow(
                "SELECT id FROM direct_message_channels WHERE id = $1",
                dm_id,
            )
            if channel is None:
                raise KeyError(dm_id)
            raise PermissionError("direct message membership required")

        await self._ensure_user(author)
        message_id = id_generator.generate()
        await database.execute(
            """
            INSERT INTO direct_messages (id, dm_id, author_id, content)
            VALUES ($1, $2, $3, $4)
            """,
            message_id,
            dm_id,
            author.id,
            payload.content,
        )
        await database.execute(
            """
            UPDATE direct_message_members
            SET unread_count = CASE WHEN user_id = $2 THEN 0 ELSE unread_count + 1 END
            WHERE dm_id = $1
            """,
            dm_id,
            author.id,
        )
        return DmMessageRead(
            id=message_id,
            dm_id=dm_id,
            author_id=author.id,
            author_name=author.username,
            content=payload.content,
        )

    async def _participants(self, dm_id: int) -> list[DmParticipantRead]:
        rows = await database.fetch(
            """
            SELECT
                u.id,
                u.username,
                COALESCE(p.handle, u.username) AS handle,
                COALESCE(p.presence_status, u.status::text) AS presence_status,
                p.activity
            FROM direct_message_members m
            JOIN users u ON u.id = m.user_id
            LEFT JOIN dm_profiles p ON p.user_id = u.id
            WHERE m.dm_id = $1
            ORDER BY u.username
            """,
            dm_id,
        )
        return [
            DmParticipantRead(
                id=int(row["id"]),
                username=str(row["username"]),
                handle=str(row["handle"]),
                status=_status_from_row(row["presence_status"]),
                activity=row["activity"],
            )
            for row in rows
        ]

    async def _messages(self, dm_id: int) -> list[DmMessageRead]:
        rows = await database.fetch(
            """
            SELECT m.id, m.dm_id, m.author_id, u.username AS author_name, m.content
            FROM direct_messages m
            JOIN users u ON u.id = m.author_id
            WHERE m.dm_id = $1
            ORDER BY m.id
            """,
            dm_id,
        )
        return [
            DmMessageRead(
                id=int(row["id"]),
                dm_id=int(row["dm_id"]),
                author_id=int(row["author_id"]),
                author_name=str(row["author_name"]),
                content=str(row["content"]),
            )
            for row in rows
        ]

    async def _profiles(self, user_ids: Iterable[int]) -> list[DmParticipantRead]:
        ids = list(user_ids)
        if not ids:
            return []
        rows = await database.fetch(
            """
            SELECT
                u.id,
                u.username,
                COALESCE(p.handle, u.username) AS handle,
                COALESCE(p.presence_status, u.status::text) AS presence_status,
                p.activity
            FROM users u
            LEFT JOIN dm_profiles p ON p.user_id = u.id
            WHERE u.id = ANY($1::bigint[])
            """,
            ids,
        )
        return [
            DmParticipantRead(
                id=int(row["id"]),
                username=str(row["username"]),
                handle=str(row["handle"]),
                status=_status_from_row(row["presence_status"]),
                activity=row["activity"],
            )
            for row in rows
        ]

    async def _find_existing_dm(self, participant_ids: list[int]) -> int | None:
        rows = await database.fetch("SELECT dm_id, user_id FROM direct_message_members")
        grouped: dict[int, list[int]] = {}
        for row in rows:
            grouped.setdefault(int(row["dm_id"]), []).append(int(row["user_id"]))
        for dm_id, members in grouped.items():
            if sorted(members) == participant_ids:
                return dm_id
        return None

    async def _ensure_user(self, user: UserPublic) -> None:
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

    async def ensure_demo_workspace(self, user: UserPublic) -> None:
        await self._ensure_user(user)
        await self.ensure_demo_workspace_for_user_id(user.id)

    async def ensure_demo_workspace_for_user_id(self, user_id: int) -> None:
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
            existing_dm_id = await self._find_existing_dm(sorted([user_id, related_user_id]))
            dm_id = existing_dm_id or id_generator.generate()
            if existing_dm_id is None:
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


dm_repository = DmRepository()
