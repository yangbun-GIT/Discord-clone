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
            name="Study Hall",
            owner_id=42,
            permissions=permissions,
            channels=[
                ChannelRead(id=2001, guild_id=1001, name="general", type=0, position=0),
                ChannelRead(id=2002, guild_id=1001, name="resources", type=0, position=1),
                ChannelRead(id=2003, guild_id=1001, name="voice-room", type=1, position=2),
                ChannelRead(id=2004, guild_id=1001, name="study-room", type=1, position=3),
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
                    content="자료방에는 과제 파일과 회의 기록만 모아두자.",
                ),
                MessageRead(
                    id=3002,
                    channel_id=2001,
                    author_id=42,
                    author_name="admin",
                    content="좋아. 채팅 화면은 최대한 조용하고 읽기 쉽게 맞춰볼게.",
                ),
                MessageRead(
                    id=3003,
                    channel_id=2001,
                    author_id=45,
                    author_name="designer",
                    content="음성 채널은 말할 때 아바타 테두리만 자연스럽게 빛나면 충분해.",
                ),
                MessageRead(
                    id=3004,
                    channel_id=2001,
                    author_id=44,
                    author_name="reviewer",
                    content="채널 목록, 멤버 목록, 입력창 높이를 한 리듬으로 맞추면 훨씬 깔끔해져.",
                ),
                MessageRead(
                    id=3005,
                    channel_id=2002,
                    author_id=43,
                    author_name="codex",
                    content="자료 미리보기는 작은 카드로만 보여주면 될 것 같아.",
                ),
            ],
        )
    ]
