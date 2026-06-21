from __future__ import annotations

from typing import Protocol

from app.db.pool import database
from app.demo.store import demo_store
from app.repositories.dms import dm_repository
from app.schemas.auth import UserPublic
from app.schemas.dm import (
    DmCreate,
    DmDeleteRead,
    DmMessageCreate,
    DmMessageDeleteRead,
    DmMessageRead,
    DmRead,
    PresenceUpdateRead,
    RelationshipDeleteRead,
    RelationshipRead,
    UserPresenceStatus,
)


class DmStorage(Protocol):
    async def list_relationships(self, user: UserPublic) -> list[RelationshipRead]: ...

    async def update_presence(
        self,
        *,
        user: UserPublic,
        status: UserPresenceStatus,
        activity: str | None,
    ) -> tuple[PresenceUpdateRead, list[int]]: ...

    async def send_friend_request(
        self,
        *,
        actor: UserPublic,
        target_username: str,
    ) -> tuple[RelationshipRead, RelationshipRead]: ...

    async def accept_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipRead]: ...

    async def reject_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]: ...

    async def cancel_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]: ...

    async def remove_friend(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]: ...

    async def block_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipDeleteRead]: ...

    async def unblock_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]: ...

    async def list_dms(self, user: UserPublic) -> list[DmRead]: ...

    async def create_dm(self, payload: DmCreate, user: UserPublic) -> DmRead: ...

    async def close_dm(self, *, dm_id: int, actor: UserPublic) -> DmDeleteRead: ...

    async def create_dm_message(
        self,
        *,
        dm_id: int,
        payload: DmMessageCreate,
        author: UserPublic,
    ) -> DmMessageRead: ...

    async def delete_dm_message(
        self,
        *,
        dm_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> DmMessageDeleteRead: ...

    async def reset_development_workspace(self, user: UserPublic) -> None: ...


class PostgresDmStorage:
    async def list_relationships(self, user: UserPublic) -> list[RelationshipRead]:
        return await dm_repository.list_relationships(user.id)

    async def update_presence(
        self,
        *,
        user: UserPublic,
        status: UserPresenceStatus,
        activity: str | None,
    ) -> tuple[PresenceUpdateRead, list[int]]:
        return await dm_repository.update_presence(user=user, status=status, activity=activity)

    async def send_friend_request(
        self,
        *,
        actor: UserPublic,
        target_username: str,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        return await dm_repository.send_friend_request(actor=actor, target_username=target_username)

    async def accept_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        return await dm_repository.accept_friend_request(actor=actor, target_user_id=target_user_id)

    async def reject_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        return await dm_repository.reject_friend_request(actor=actor, target_user_id=target_user_id)

    async def cancel_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        return await dm_repository.cancel_friend_request(actor=actor, target_user_id=target_user_id)

    async def remove_friend(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        return await dm_repository.remove_friend(actor=actor, target_user_id=target_user_id)

    async def block_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipDeleteRead]:
        return await dm_repository.block_user(actor=actor, target_user_id=target_user_id)

    async def unblock_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        return await dm_repository.unblock_user(actor=actor, target_user_id=target_user_id)

    async def list_dms(self, user: UserPublic) -> list[DmRead]:
        return await dm_repository.list_dms(user)

    async def create_dm(self, payload: DmCreate, user: UserPublic) -> DmRead:
        return await dm_repository.create_dm(payload, user)

    async def close_dm(self, *, dm_id: int, actor: UserPublic) -> DmDeleteRead:
        return await dm_repository.close_dm(dm_id=dm_id, actor=actor)

    async def create_dm_message(
        self,
        *,
        dm_id: int,
        payload: DmMessageCreate,
        author: UserPublic,
    ) -> DmMessageRead:
        return await dm_repository.create_dm_message(dm_id=dm_id, payload=payload, author=author)

    async def delete_dm_message(
        self,
        *,
        dm_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> DmMessageDeleteRead:
        return await dm_repository.delete_dm_message(
            dm_id=dm_id,
            message_id=message_id,
            actor=actor,
        )

    async def reset_development_workspace(self, user: UserPublic) -> None:
        await dm_repository.reset_development_workspace(user)


class DemoDmStorage:
    async def list_relationships(self, user: UserPublic) -> list[RelationshipRead]:
        return demo_store.list_relationships(user.id)

    async def update_presence(
        self,
        *,
        user: UserPublic,
        status: UserPresenceStatus,
        activity: str | None,
    ) -> tuple[PresenceUpdateRead, list[int]]:
        return demo_store.update_presence(user=user, status=status, activity=activity)

    async def send_friend_request(
        self,
        *,
        actor: UserPublic,
        target_username: str,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        return demo_store.send_friend_request(actor=actor, target_username=target_username)

    async def accept_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        return demo_store.accept_friend_request(actor=actor, target_user_id=target_user_id)

    async def reject_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        return demo_store.reject_friend_request(actor=actor, target_user_id=target_user_id)

    async def cancel_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        return demo_store.cancel_friend_request(actor=actor, target_user_id=target_user_id)

    async def remove_friend(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        return demo_store.remove_friend(actor=actor, target_user_id=target_user_id)

    async def block_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipDeleteRead]:
        return demo_store.block_user(actor=actor, target_user_id=target_user_id)

    async def unblock_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        return demo_store.unblock_user(actor=actor, target_user_id=target_user_id)

    async def list_dms(self, user: UserPublic) -> list[DmRead]:
        return demo_store.list_dms(user)

    async def create_dm(self, payload: DmCreate, user: UserPublic) -> DmRead:
        return demo_store.create_dm(payload, user)

    async def close_dm(self, *, dm_id: int, actor: UserPublic) -> DmDeleteRead:
        return demo_store.close_dm(dm_id=dm_id, actor=actor)

    async def create_dm_message(
        self,
        *,
        dm_id: int,
        payload: DmMessageCreate,
        author: UserPublic,
    ) -> DmMessageRead:
        return demo_store.create_dm_message(dm_id=dm_id, payload=payload, author=author)

    async def delete_dm_message(
        self,
        *,
        dm_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> DmMessageDeleteRead:
        return demo_store.delete_dm_message(dm_id=dm_id, message_id=message_id, actor=actor)

    async def reset_development_workspace(self, user: UserPublic) -> None:
        demo_store.reset_development_workspace(user)


postgres_dm_storage = PostgresDmStorage()
demo_dm_storage = DemoDmStorage()


def get_dm_storage() -> DmStorage:
    return postgres_dm_storage if database.is_connected else demo_dm_storage
