from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.api.errors import raise_route_error
from app.realtime.publisher import publish_channel_create, publish_guild_update
from app.schemas.auth import UserPublic
from app.schemas.guild import (
    ChannelCreate,
    ChannelRead,
    GuildActionRead,
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
    delete_guild,
    get_guild_for_user,
    join_invite,
    leave_guild,
    list_guilds_for_user,
    remove_member,
    remove_member_role,
)

router = APIRouter()


@router.get("/me", response_model=list[GuildRead])
async def list_my_guilds(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> list[GuildRead]:
    return await list_guilds_for_user(current_user)


@router.get("/{guild_id}", response_model=GuildRead)
async def get_guild(
    guild_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildRead:
    try:
        return await get_guild_for_user(guild_id, current_user)
    except KeyError as exc:
        raise_route_error(exc, not_found="guild not found")


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
        guild = await join_invite(code, current_user)
        await publish_guild_update(guild)
        return guild
    except KeyError as exc:
        raise_route_error(exc, not_found="invite not found")


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
    except (KeyError, PermissionError) as exc:
        raise_route_error(
            exc,
            not_found="guild not found",
            forbidden="create invite permission required",
        )


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
        guild = await create_role(guild_id, payload, current_user)
        await publish_guild_update(guild)
        return guild
    except (KeyError, PermissionError) as exc:
        raise_route_error(
            exc,
            not_found="guild not found",
            forbidden="administrator permission required",
        )


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
        guild = await assign_member_role(guild_id, member_id, payload, current_user)
        await publish_guild_update(guild)
        return guild
    except (KeyError, PermissionError) as exc:
        raise_route_error(
            exc,
            not_found="member or role not found",
            forbidden="administrator permission required",
        )


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
        guild = await remove_member_role(guild_id, member_id, role_id, current_user)
        await publish_guild_update(guild)
        return guild
    except (KeyError, PermissionError) as exc:
        raise_route_error(
            exc,
            not_found="member or role not found",
            forbidden="administrator permission required",
        )


@router.delete(
    "/{guild_id}/members/{member_id}",
    response_model=GuildRead,
    status_code=status.HTTP_200_OK,
)
async def remove_guild_member(
    guild_id: int,
    member_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildRead:
    try:
        guild = await remove_member(guild_id, member_id, current_user)
        await publish_guild_update(guild)
        return guild
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="member not found",
            forbidden="administrator permission required",
            bad_request=str(exc),
        )


@router.delete(
    "/{guild_id}/leave",
    response_model=GuildActionRead,
    status_code=status.HTTP_200_OK,
)
async def leave_user_guild(
    guild_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildActionRead:
    try:
        guild = await leave_guild(guild_id, current_user)
        await publish_guild_update(guild)
        return GuildActionRead(ok=True)
    except (KeyError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="guild not found",
            bad_request=str(exc),
        )


@router.delete(
    "/{guild_id}",
    response_model=GuildActionRead,
    status_code=status.HTTP_200_OK,
)
async def delete_user_guild(
    guild_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildActionRead:
    try:
        await delete_guild(guild_id, current_user)
        return GuildActionRead(ok=True)
    except (KeyError, PermissionError) as exc:
        raise_route_error(
            exc,
            not_found="guild not found",
            forbidden="server owner permission required",
        )


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
        channel = await create_channel(guild_id, payload, current_user)
        await publish_channel_create(channel)
        return channel
    except (KeyError, PermissionError) as exc:
        raise_route_error(
            exc,
            not_found="guild not found",
            forbidden="manage channels permission required",
        )
