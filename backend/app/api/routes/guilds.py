from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.schemas.auth import UserPublic
from app.schemas.guild import (
    ChannelCreate,
    ChannelRead,
    GuildCreate,
    GuildRead,
    InviteRead,
    MemberRoleUpdate,
    RoleCreate,
)
from app.services.guild_service import (
    assign_member_role,
    create_channel,
    create_guild,
    create_invite,
    create_role,
    join_invite,
    list_guilds_for_user,
    remove_member_role,
)

router = APIRouter()


@router.get("/me", response_model=list[GuildRead])
async def list_my_guilds(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> list[GuildRead]:
    return await list_guilds_for_user(current_user)


@router.post("", response_model=GuildRead, status_code=status.HTTP_201_CREATED)
async def create_user_guild(
    payload: GuildCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildRead:
    return await create_guild(payload, current_user)


@router.post(
    "/invites/{code}/join",
    response_model=GuildRead,
    status_code=status.HTTP_201_CREATED,
)
async def join_guild_invite(
    code: str,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildRead:
    try:
        return await join_invite(code, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="invite not found",
        ) from exc


@router.post(
    "/{guild_id}/invites",
    response_model=InviteRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_guild_invite(
    guild_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> InviteRead:
    try:
        return await create_invite(guild_id, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="guild not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="create invite permission required",
        ) from exc


@router.post(
    "/{guild_id}/roles",
    response_model=GuildRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_guild_role(
    guild_id: int,
    payload: RoleCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildRead:
    try:
        return await create_role(guild_id, payload, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="guild not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="administrator permission required",
        ) from exc


@router.post(
    "/{guild_id}/members/{member_id}/roles",
    response_model=GuildRead,
    status_code=status.HTTP_200_OK,
)
async def assign_guild_member_role(
    guild_id: int,
    member_id: int,
    payload: MemberRoleUpdate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildRead:
    try:
        return await assign_member_role(guild_id, member_id, payload, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="member or role not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="administrator permission required",
        ) from exc


@router.delete(
    "/{guild_id}/members/{member_id}/roles/{role_id}",
    response_model=GuildRead,
    status_code=status.HTTP_200_OK,
)
async def remove_guild_member_role(
    guild_id: int,
    member_id: int,
    role_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildRead:
    try:
        return await remove_member_role(guild_id, member_id, role_id, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="member or role not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="administrator permission required",
        ) from exc


@router.post(
    "/{guild_id}/channels",
    response_model=ChannelRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_guild_channel(
    guild_id: int,
    payload: ChannelCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> ChannelRead:
    try:
        return await create_channel(guild_id, payload, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="guild not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="manage channels permission required",
        ) from exc
