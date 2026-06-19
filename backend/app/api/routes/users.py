from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.api.errors import raise_route_error
from app.realtime.publisher import publish_relationship_delete, publish_relationship_update
from app.schemas.auth import UserPublic
from app.schemas.dm import RelationshipDeleteRead, RelationshipRead, RelationshipRequestCreate
from app.services.dm_service import (
    accept_friend_request,
    block_user,
    cancel_friend_request,
    list_relationships,
    reject_friend_request,
    remove_friend,
    send_friend_request,
    unblock_user,
)

router = APIRouter()


@router.get("/me/relationships", response_model=list[RelationshipRead])
async def list_my_relationships(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> list[RelationshipRead]:
    return await list_relationships(current_user)


@router.post(
    "/me/relationships/requests",
    response_model=RelationshipRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_friend_request(
    payload: RelationshipRequestCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> RelationshipRead:
    try:
        actor_relationship, target_relationship = await send_friend_request(
            actor=current_user,
            target_username=payload.username,
        )
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="user not found",
            forbidden=str(exc),
            bad_request=str(exc),
        )
    await publish_relationship_update(
        user_id=current_user.id,
        relationship=actor_relationship,
    )
    await publish_relationship_update(
        user_id=actor_relationship.id,
        relationship=target_relationship,
    )
    return actor_relationship


@router.post("/me/relationships/{user_id}/accept", response_model=RelationshipRead)
async def accept_relationship_request(
    user_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> RelationshipRead:
    try:
        actor_relationship, target_relationship = await accept_friend_request(
            actor=current_user,
            target_user_id=user_id,
        )
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="relationship not found",
            forbidden=str(exc),
            bad_request=str(exc),
        )
    await publish_relationship_update(user_id=current_user.id, relationship=actor_relationship)
    await publish_relationship_update(
        user_id=actor_relationship.id,
        relationship=target_relationship,
    )
    return actor_relationship


@router.post("/me/relationships/{user_id}/reject", response_model=RelationshipDeleteRead)
async def reject_relationship_request(
    user_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> RelationshipDeleteRead:
    try:
        actor_delete, target_delete = await reject_friend_request(
            actor=current_user,
            target_user_id=user_id,
        )
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="relationship not found",
            forbidden=str(exc),
            bad_request=str(exc),
        )
    await publish_relationship_delete(user_id=current_user.id, relationship=actor_delete)
    await publish_relationship_delete(user_id=user_id, relationship=target_delete)
    return actor_delete


@router.post("/me/relationships/{user_id}/cancel", response_model=RelationshipDeleteRead)
async def cancel_relationship_request(
    user_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> RelationshipDeleteRead:
    try:
        actor_delete, target_delete = await cancel_friend_request(
            actor=current_user,
            target_user_id=user_id,
        )
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="relationship not found",
            forbidden=str(exc),
            bad_request=str(exc),
        )
    await publish_relationship_delete(user_id=current_user.id, relationship=actor_delete)
    await publish_relationship_delete(user_id=user_id, relationship=target_delete)
    return actor_delete


@router.delete("/me/relationships/{user_id}", response_model=RelationshipDeleteRead)
async def delete_relationship(
    user_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> RelationshipDeleteRead:
    try:
        actor_delete, target_delete = await remove_friend(
            actor=current_user,
            target_user_id=user_id,
        )
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="relationship not found",
            forbidden=str(exc),
            bad_request=str(exc),
        )
    await publish_relationship_delete(user_id=current_user.id, relationship=actor_delete)
    await publish_relationship_delete(user_id=user_id, relationship=target_delete)
    return actor_delete


@router.post("/me/relationships/{user_id}/block", response_model=RelationshipRead)
async def block_relationship_user(
    user_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> RelationshipRead:
    try:
        actor_relationship, target_delete = await block_user(
            actor=current_user,
            target_user_id=user_id,
        )
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="user not found",
            forbidden=str(exc),
            bad_request=str(exc),
        )
    await publish_relationship_update(user_id=current_user.id, relationship=actor_relationship)
    await publish_relationship_delete(user_id=user_id, relationship=target_delete)
    return actor_relationship


@router.delete("/me/relationships/{user_id}/block", response_model=RelationshipDeleteRead)
async def unblock_relationship_user(
    user_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> RelationshipDeleteRead:
    try:
        actor_delete, target_delete = await unblock_user(
            actor=current_user,
            target_user_id=user_id,
        )
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="relationship not found",
            forbidden=str(exc),
            bad_request=str(exc),
        )
    await publish_relationship_delete(user_id=current_user.id, relationship=actor_delete)
    await publish_relationship_delete(user_id=user_id, relationship=target_delete)
    return actor_delete
