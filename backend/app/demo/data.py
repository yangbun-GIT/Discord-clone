from app.domain.permissions import Permission, merge_permissions
from app.schemas.guild import ChannelRead, GuildRead, MemberRead, MessageRead


def create_initial_guilds() -> list[GuildRead]:
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
                ChannelRead(id=2001, guild_id=1001, name="general", type=0, position=0),
                ChannelRead(id=2002, guild_id=1001, name="resources", type=0, position=1),
                ChannelRead(id=2003, guild_id=1001, name="voice-room", type=1, position=2),
                ChannelRead(id=2004, guild_id=1001, name="study-room", type=1, position=3),
            ],
            members=[
                MemberRead(id=42, username="yangbun", status=1, role="Owner"),
                MemberRead(id=43, username="codex", status=1, role="Engineer"),
                MemberRead(id=44, username="reviewer", status=0, role="Advisor"),
                MemberRead(id=45, username="designer", status=1, role="Member"),
                MemberRead(id=46, username="voice-tester", status=1, role="Member"),
            ],
            messages=[
                MessageRead(
                    id=3001,
                    channel_id=2001,
                    author_id=43,
                    author_name="codex",
                    content=(
                        "The app shell needs to stay compact before we add more features."
                    ),
                ),
                MessageRead(
                    id=3002,
                    channel_id=2001,
                    author_id=42,
                    author_name="yangbun",
                    content="Focus on clean Discord-like spacing and hide development-only text.",
                ),
                MessageRead(
                    id=3003,
                    channel_id=2001,
                    author_id=45,
                    author_name="designer",
                    content="The voice channel should show a subtle glow when microphone input is active.",
                ),
                MessageRead(
                    id=3004,
                    channel_id=2001,
                    author_id=44,
                    author_name="reviewer",
                    content="Composer icons, member list, and channel rows should align to one compact rhythm.",
                ),
                MessageRead(
                    id=3005,
                    channel_id=2002,
                    author_id=43,
                    author_name="codex",
                    content="Safe demo attachments are rendered locally for visual QA.",
                ),
            ],
        )
    ]
