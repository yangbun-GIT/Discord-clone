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
                ChannelRead(id=2001, guild_id=1001, name="architecture", type=0, position=0),
                ChannelRead(id=2002, guild_id=1001, name="frontend", type=0, position=1),
                ChannelRead(id=2003, guild_id=1001, name="voice-room", type=1, position=2),
            ],
            members=[
                MemberRead(id=42, username="admin", status=1, role="Owner"),
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
                    content="architecture 채널에는 구현 구조와 통신 흐름을 정리해 두었습니다.",
                ),
                MessageRead(
                    id=3002,
                    channel_id=2001,
                    author_id=42,
                    author_name="admin",
                    content="서버 초대, 텍스트 채팅, 음성 채널, 화면 공유 흐름을 확인해 보세요.",
                ),
                MessageRead(
                    id=3003,
                    channel_id=2002,
                    author_id=45,
                    author_name="designer",
                    content=(
                        "frontend 채널에는 UI 사용성과 화면 구성 확인용 대화를 "
                        "남겨 두었습니다."
                    ),
                ),
                MessageRead(
                    id=3004,
                    channel_id=2002,
                    author_id=44,
                    author_name="reviewer",
                    content="DM과 서버 채팅은 최신 메시지가 하단 기준으로 보이도록 구성했습니다.",
                ),
                MessageRead(
                    id=3005,
                    channel_id=2002,
                    author_id=43,
                    author_name="codex",
                    content=(
                        "음성 채널에서 마이크, 소리 차단, 화면 공유를 함께 "
                        "테스트할 수 있습니다."
                    ),
                ),
            ],
        )
    ]
