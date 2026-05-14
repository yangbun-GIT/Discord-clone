from app.domain.permissions import Permission, merge_permissions
from app.schemas.guild import ChannelRead, GuildRead, MemberRead, MessageRead


def demo_guilds() -> list[GuildRead]:
    permissions = merge_permissions(
        [
            Permission.READ_MESSAGES,
            Permission.SEND_MESSAGES,
            Permission.CONNECT,
            Permission.SPEAK,
        ]
    )
    return [
        GuildRead(
            id=1001,
            name="SRS Lab",
            owner_id=42,
            permissions=permissions,
            channels=[
                ChannelRead(id=2001, guild_id=1001, name="architecture", type=0, position=0),
                ChannelRead(id=2002, guild_id=1001, name="frontend", type=0, position=1),
                ChannelRead(id=2003, guild_id=1001, name="voice-room", type=1, position=2),
            ],
            members=[
                MemberRead(id=42, username="yangbun", status=1, role="Owner"),
                MemberRead(id=43, username="codex", status=1, role="Engineer"),
                MemberRead(id=44, username="reviewer", status=0, role="Advisor"),
            ],
            messages=[
                MessageRead(
                    id=3001,
                    channel_id=2001,
                    author_id=43,
                    author_name="codex",
                    content=(
                        "Stage 1 focuses on the app shell, gateway protocol, "
                        "and async boundaries."
                    ),
                ),
                MessageRead(
                    id=3002,
                    channel_id=2001,
                    author_id=42,
                    author_name="yangbun",
                    content="Keep every external service optional for local development.",
                ),
            ],
        )
    ]
