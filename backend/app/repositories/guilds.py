from app.db.pool import database
from app.domain.permissions import ALL_PERMISSIONS
from app.repositories.guild_common import ensure_user, id_generator, read_guild
from app.schemas.auth import UserPublic
from app.schemas.guild import (
    ChannelCreate,
    ChannelRead,
    GuildCreate,
    GuildRead,
    InviteRead,
    MemberRead,
    MemberRoleUpdate,
    MessageRead,
    RoleCreate,
)
from app.schemas.message import MessageDeleteRead


class GuildRepository:
    async def list_for_user(self, user_id: int) -> list[GuildRead]:
        guild_rows = await database.fetch(
            """
            SELECT g.id, g.name, g.owner_id
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            WHERE gm.user_id = $1
            ORDER BY g.created_at ASC, g.id ASC
            """,
            user_id,
        )

        return [await read_guild(guild_row, user_id) for guild_row in guild_rows]

    async def get_for_user(self, guild_id: int, user_id: int) -> GuildRead | None:
        guild_row = await database.fetchrow(
            """
            SELECT g.id, g.name, g.owner_id
            FROM guilds g
            JOIN guild_members gm ON gm.guild_id = g.id
            WHERE g.id = $1 AND gm.user_id = $2
            """,
            guild_id,
            user_id,
        )
        if guild_row is None:
            return None
        return await read_guild(guild_row, user_id)

    async def create_guild(self, payload: GuildCreate, owner: UserPublic) -> GuildRead:
        guild_id = id_generator.generate()
        text_channel = ChannelRead(
            id=id_generator.generate(),
            guild_id=guild_id,
            name="general",
            type=0,
            position=0,
        )
        voice_channel = ChannelRead(
            id=id_generator.generate(),
            guild_id=guild_id,
            name="voice-room",
            type=1,
            position=1,
        )

        await ensure_user(owner)
        await database.execute(
            """
            INSERT INTO guilds (id, name, owner_id)
            VALUES ($1, $2, $3)
            """,
            guild_id,
            payload.name,
            owner.id,
        )
        await database.execute(
            """
            INSERT INTO guild_members (guild_id, user_id)
            VALUES ($1, $2)
            """,
            guild_id,
            owner.id,
        )
        await database.execute(
            """
            INSERT INTO channels (id, guild_id, name, type, position)
            VALUES ($1, $2, $3, $4, $5), ($6, $7, $8, $9, $10)
            """,
            text_channel.id,
            text_channel.guild_id,
            text_channel.name,
            text_channel.type,
            text_channel.position,
            voice_channel.id,
            voice_channel.guild_id,
            voice_channel.name,
            voice_channel.type,
            voice_channel.position,
        )
        return GuildRead(
            id=guild_id,
            name=payload.name,
            owner_id=owner.id,
            permissions=ALL_PERMISSIONS,
            channels=[text_channel, voice_channel],
            members=[
                MemberRead(
                    id=owner.id,
                    username=owner.username,
                    status=owner.status,
                    role="Owner",
                )
            ],
            messages=[],
        )

    async def remove_member(
        self,
        guild_id: int,
        member_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        from app.repositories.guild_members import member_repository

        return await member_repository.remove_member(guild_id, member_id, actor)

    async def create_role(
        self,
        guild_id: int,
        payload: RoleCreate,
        actor: UserPublic,
    ) -> GuildRead:
        from app.repositories.guild_roles import role_repository

        return await role_repository.create_role(guild_id, payload, actor)

    async def assign_member_role(
        self,
        guild_id: int,
        member_id: int,
        payload: MemberRoleUpdate,
        actor: UserPublic,
    ) -> GuildRead:
        from app.repositories.guild_roles import role_repository

        return await role_repository.assign_member_role(guild_id, member_id, payload, actor)

    async def remove_member_role(
        self,
        guild_id: int,
        member_id: int,
        role_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        from app.repositories.guild_roles import role_repository

        return await role_repository.remove_member_role(guild_id, member_id, role_id, actor)

    async def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead:
        from app.repositories.guild_invites import invite_repository

        return await invite_repository.create_invite(guild_id, actor)

    async def join_invite(self, code: str, user: UserPublic) -> GuildRead:
        from app.repositories.guild_invites import invite_repository

        return await invite_repository.join_invite(code, user)

    async def create_channel(
        self,
        guild_id: int,
        payload: ChannelCreate,
        actor: UserPublic,
    ) -> ChannelRead:
        from app.repositories.guild_channels import channel_repository

        return await channel_repository.create_channel(guild_id, payload, actor)

    async def create_message(
        self,
        *,
        channel_id: int,
        author: UserPublic,
        content: str,
    ) -> MessageRead:
        from app.repositories.guild_messages import message_repository

        return await message_repository.create_message(
            channel_id=channel_id,
            author=author,
            content=content,
        )

    async def update_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
        content: str,
    ) -> MessageRead:
        from app.repositories.guild_messages import message_repository

        return await message_repository.update_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=actor,
            content=content,
        )

    async def delete_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> MessageDeleteRead:
        from app.repositories.guild_messages import message_repository

        return await message_repository.delete_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=actor,
        )


guild_repository = GuildRepository()
