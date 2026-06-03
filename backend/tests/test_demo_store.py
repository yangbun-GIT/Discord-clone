from app.demo.store import DemoStore
from app.schemas.auth import UserPublic
from app.schemas.dm import DmCreate, DmMessageCreate
from app.schemas.guild import ChannelCreate


def test_demo_store_creates_channel() -> None:
    store = DemoStore()

    channel = store.create_channel(1001, ChannelCreate(name="backend", type=0))
    guild = store.list_guilds()[0]

    assert channel.name == "backend"
    assert any(item.id == channel.id for item in guild.channels)


def test_demo_store_creates_message() -> None:
    store = DemoStore()

    message = store.create_message(
        channel_id=2001,
        author_id=42,
        author_name="yangbun",
        content="hello",
    )
    guild = store.list_guilds()[0]

    assert message.content == "hello"
    assert any(item.id == message.id for item in guild.messages)


def test_demo_store_creates_dm_message_for_member() -> None:
    store = DemoStore()

    message = store.create_dm_message(
        dm_id=801,
        payload=DmMessageCreate(dm_id=801, content="hello dm"),
        author=UserPublic(id=42, username="yangbun", status=1),
    )
    dms = store.list_dms(UserPublic(id=42, username="yangbun", status=1))

    assert message.content == "hello dm"
    assert any(item.id == message.id for item in dms[0].messages)


def test_demo_store_hides_dms_from_non_members() -> None:
    store = DemoStore()

    dms = store.list_dms(UserPublic(id=999, username="outsider", status=1))

    assert dms == []


def test_demo_store_creates_dm_for_known_recipient() -> None:
    store = DemoStore()

    dm = store.create_dm(
        DmCreate(recipient_ids=[704]),
        UserPublic(id=42, username="yangbun", status=1),
    )

    assert dm.display_name == "QA Reviewer"
    assert dm.recipient_ids == [704]
