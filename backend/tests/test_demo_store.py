from app.demo.store import DemoStore
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

