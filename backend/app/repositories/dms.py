from collections.abc import Iterable

from app.db.pool import database
from app.domain.snowflake import SnowflakeGenerator
from app.repositories.dm_seed import (
    ensure_dm_repository_user,
    ensure_postgres_dm_demo_workspace,
)
from app.schemas.auth import UserPublic
from app.schemas.dm import (
    DmCreate,
    DmMessageCreate,
    DmMessageDeleteRead,
    DmMessageRead,
    DmParticipantRead,
    DmRead,
    PresenceUpdateRead,
    RelationshipDeleteRead,
    RelationshipRead,
    RelationshipState,
    UserPresenceStatus,
)

id_generator = SnowflakeGenerator(worker_id=3)


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

    async def update_presence(
        self,
        *,
        user: UserPublic,
        status: UserPresenceStatus,
        activity: str | None,
    ) -> tuple[PresenceUpdateRead, list[int]]:
        await ensure_dm_repository_user(database, user)
        await database.execute(
            """
            INSERT INTO dm_profiles (user_id, handle, presence_status, activity)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE SET
                presence_status = EXCLUDED.presence_status,
                activity = EXCLUDED.activity
            """,
            user.id,
            user.username.lower(),
            status,
            activity,
        )
        relationships = await self.list_relationships(user.id)
        friend_user_ids = [
            relationship.id
            for relationship in relationships
            if relationship.relationship == "friend"
        ]
        return (
            PresenceUpdateRead(
                user_id=user.id,
                username=user.username,
                status=status,
                activity=activity,
            ),
            friend_user_ids,
        )

    async def send_friend_request(
        self,
        *,
        actor: UserPublic,
        target_username: str,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        await ensure_dm_repository_user(database, actor)
        target = await self._find_user_by_username(target_username)
        if target is None:
            raise KeyError("target user not found")
        target_id = int(target["id"])
        if target_id == actor.id:
            raise ValueError("cannot send a friend request to yourself")

        existing = await self._relationship(actor.id, target_id)
        reverse = await self._relationship(target_id, actor.id)
        if existing == "blocked" or reverse == "blocked":
            raise PermissionError("relationship is blocked")
        if existing == "friend" or reverse == "friend":
            await self._set_relationship(actor.id, target_id, "friend")
            await self._set_relationship(target_id, actor.id, "friend")
            return await self._relationship_pair(actor.id, target_id)
        if existing == "pending_incoming" and reverse == "pending_outgoing":
            return await self.accept_friend_request(actor=actor, target_user_id=target_id)

        await self._set_relationship(actor.id, target_id, "pending_outgoing")
        await self._set_relationship(target_id, actor.id, "pending_incoming")
        return await self._relationship_pair(actor.id, target_id)

    async def accept_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        await ensure_dm_repository_user(database, actor)
        existing = await self._relationship(actor.id, target_user_id)
        reverse = await self._relationship(target_user_id, actor.id)
        if existing == "friend" and reverse == "friend":
            return await self._relationship_pair(actor.id, target_user_id)
        if existing != "pending_incoming" or reverse != "pending_outgoing":
            raise ValueError("incoming friend request required")

        await self._set_relationship(actor.id, target_user_id, "friend")
        await self._set_relationship(target_user_id, actor.id, "friend")
        return await self._relationship_pair(actor.id, target_user_id)

    async def reject_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        await self._require_relationship(actor.id, target_user_id, "pending_incoming")
        await self._delete_relationship_pair(actor.id, target_user_id)
        return RelationshipDeleteRead(id=target_user_id), RelationshipDeleteRead(id=actor.id)

    async def cancel_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        await self._require_relationship(actor.id, target_user_id, "pending_outgoing")
        await self._delete_relationship_pair(actor.id, target_user_id)
        return RelationshipDeleteRead(id=target_user_id), RelationshipDeleteRead(id=actor.id)

    async def remove_friend(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        await self._require_relationship(actor.id, target_user_id, "friend")
        await self._delete_relationship_pair(actor.id, target_user_id)
        return RelationshipDeleteRead(id=target_user_id), RelationshipDeleteRead(id=actor.id)

    async def block_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipDeleteRead]:
        if target_user_id == actor.id:
            raise ValueError("cannot block yourself")
        await ensure_dm_repository_user(database, actor)
        target = await self._profile_by_user_id(target_user_id)
        if target is None:
            raise KeyError("target user not found")
        await self._set_relationship(actor.id, target_user_id, "blocked")
        await self._delete_relationship(target_user_id, actor.id)
        actor_relationship = await self._relationship_read(actor.id, target_user_id)
        return actor_relationship, RelationshipDeleteRead(id=actor.id)

    async def unblock_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        await self._require_relationship(actor.id, target_user_id, "blocked")
        await self._delete_relationship(actor.id, target_user_id)
        return RelationshipDeleteRead(id=target_user_id), RelationshipDeleteRead(id=actor.id)

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
        seen_recipient_sets: set[tuple[int, ...]] = set()
        for row in rows:
            dm = await self.get_dm_for_user(int(row["dm_id"]), user.id)
            if dm is not None:
                recipient_key = tuple(sorted(dm.recipient_ids))
                if recipient_key in seen_recipient_sets:
                    continue
                seen_recipient_sets.add(recipient_key)
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

        await ensure_dm_repository_user(database, user)
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

        await ensure_dm_repository_user(database, author)
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

    async def delete_dm_message(
        self,
        *,
        dm_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> DmMessageDeleteRead:
        membership = await database.fetchrow(
            """
            SELECT 1 AS exists
            FROM direct_message_members
            WHERE dm_id = $1 AND user_id = $2
            """,
            dm_id,
            actor.id,
        )
        if membership is None:
            channel = await database.fetchrow(
                "SELECT id FROM direct_message_channels WHERE id = $1",
                dm_id,
            )
            if channel is None:
                raise KeyError(dm_id)
            raise PermissionError("direct message membership required")

        row = await database.fetchrow(
            """
            SELECT id, dm_id, author_id
            FROM direct_messages
            WHERE id = $1 AND dm_id = $2
            """,
            message_id,
            dm_id,
        )
        if row is None:
            raise KeyError(message_id)
        if int(row["author_id"]) != actor.id:
            raise PermissionError("message author required")

        await database.execute(
            """
            DELETE FROM direct_messages
            WHERE id = $1 AND dm_id = $2
            """,
            message_id,
            dm_id,
        )
        return DmMessageDeleteRead(id=message_id, dm_id=dm_id)

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

    async def _find_user_by_username(self, username: str) -> object | None:
        return await database.fetchrow(
            """
            SELECT id, username, status
            FROM users
            WHERE lower(username) = lower($1)
            """,
            username,
        )

    async def _relationship(
        self,
        user_id: int,
        related_user_id: int,
    ) -> RelationshipState | None:
        row = await database.fetchrow(
            """
            SELECT relationship
            FROM relationships
            WHERE user_id = $1 AND related_user_id = $2
            """,
            user_id,
            related_user_id,
        )
        if row is None:
            return None
        return row["relationship"]  # type: ignore[return-value]

    async def _set_relationship(
        self,
        user_id: int,
        related_user_id: int,
        relationship: RelationshipState,
    ) -> None:
        await database.execute(
            """
            INSERT INTO relationships (user_id, related_user_id, relationship)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, related_user_id)
            DO UPDATE SET relationship = EXCLUDED.relationship
            """,
            user_id,
            related_user_id,
            relationship,
        )

    async def _delete_relationship(self, user_id: int, related_user_id: int) -> None:
        await database.execute(
            """
            DELETE FROM relationships
            WHERE user_id = $1 AND related_user_id = $2
            """,
            user_id,
            related_user_id,
        )

    async def _delete_relationship_pair(self, first_user_id: int, second_user_id: int) -> None:
        await self._delete_relationship(first_user_id, second_user_id)
        await self._delete_relationship(second_user_id, first_user_id)

    async def _require_relationship(
        self,
        user_id: int,
        related_user_id: int,
        relationship: RelationshipState,
    ) -> None:
        existing = await self._relationship(user_id, related_user_id)
        if existing != relationship:
            raise ValueError(f"{relationship} relationship required")

    async def _relationship_pair(
        self,
        actor_id: int,
        target_id: int,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        return (
            await self._relationship_read(actor_id, target_id),
            await self._relationship_read(target_id, actor_id),
        )

    async def _relationship_read(self, user_id: int, related_user_id: int) -> RelationshipRead:
        row = await self._profile_by_user_id(related_user_id, viewer_user_id=user_id)
        if row is None:
            raise KeyError("target user not found")
        return RelationshipRead(
            id=int(row["id"]),
            username=str(row["username"]),
            handle=str(row["handle"]),
            status=_status_from_row(row["presence_status"]),
            activity=row["activity"],
            relationship=row["relationship"],
        )

    async def _profile_by_user_id(
        self,
        user_id: int,
        *,
        viewer_user_id: int | None = None,
    ) -> object | None:
        if viewer_user_id is None:
            return await database.fetchrow(
                """
                SELECT
                    u.id,
                    u.username,
                    COALESCE(p.handle, u.username) AS handle,
                    COALESCE(p.presence_status, u.status::text) AS presence_status,
                    p.activity,
                    'friend' AS relationship
                FROM users u
                LEFT JOIN dm_profiles p ON p.user_id = u.id
                WHERE u.id = $1
                """,
                user_id,
            )
        return await database.fetchrow(
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
            WHERE r.user_id = $1 AND r.related_user_id = $2
            """,
            viewer_user_id,
            user_id,
        )

    async def _find_existing_dm(self, participant_ids: list[int]) -> int | None:
        rows = await database.fetch("SELECT dm_id, user_id FROM direct_message_members")
        grouped: dict[int, list[int]] = {}
        for row in rows:
            grouped.setdefault(int(row["dm_id"]), []).append(int(row["user_id"]))
        for dm_id, members in grouped.items():
            if sorted(members) == participant_ids:
                return dm_id
        return None

    async def ensure_demo_workspace(self, user: UserPublic) -> None:
        await ensure_dm_repository_user(database, user)
        await self.ensure_demo_workspace_for_user_id(user.id)

    async def ensure_demo_workspace_for_user_id(self, user_id: int) -> None:
        await ensure_postgres_dm_demo_workspace(
            database=database,
            id_generator=id_generator,
            user_id=user_id,
            find_existing_dm=self._find_existing_dm,
        )


dm_repository = DmRepository()
