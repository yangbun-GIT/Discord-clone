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

    assert dm.display_name == "Haru"
    assert dm.recipient_ids == [704]


def test_demo_store_closes_dm_for_current_user_only() -> None:
    store = DemoStore()
    actor = UserPublic(id=42, username="yangbun", status=1)
    other = UserPublic(id=701, username="Mina", status=1)

    closed = store.close_dm(dm_id=801, actor=actor)

    assert closed.id == 801
    assert all(dm.id != 801 for dm in store.list_dms(actor))
    assert any(dm.id == 801 for dm in store.list_dms(other))


def test_demo_store_reopens_hidden_dm_when_recreated() -> None:
    store = DemoStore()
    actor = UserPublic(id=42, username="yangbun", status=1)

    store.close_dm(dm_id=801, actor=actor)
    dm = store.create_dm(DmCreate(recipient_ids=[701]), actor)

    assert dm.id == 801
    assert any(item.id == 801 for item in store.list_dms(actor))


def test_demo_store_friend_request_accept_and_remove() -> None:
    store = DemoStore()
    actor = UserPublic(id=42, username="yangbun", status=1)

    outgoing, incoming = store.send_friend_request(actor=actor, target_username="Haru")

    assert outgoing.relationship == "friend"
    assert incoming.relationship == "friend"

    actor_delete, target_delete = store.remove_friend(actor=actor, target_user_id=704)

    assert actor_delete.id == 704
    assert target_delete.id == 42
    assert all(item.id != 704 for item in store.list_relationships(42))


def test_demo_store_pending_request_lifecycle() -> None:
    store = DemoStore()
    actor = UserPublic(id=42, username="yangbun", status=1)

    outgoing, incoming = store.send_friend_request(actor=actor, target_username="Nora")

    assert outgoing.relationship == "pending_outgoing"
    assert incoming.relationship == "pending_incoming"

    canceled, target_delete = store.cancel_friend_request(actor=actor, target_user_id=705)

    assert canceled.id == 705
    assert target_delete.id == 42
    assert all(item.id != 705 for item in store.list_relationships(42))
    assert all(item.id != 42 for item in store.list_relationships(705))


def test_demo_store_accepts_incoming_request() -> None:
    store = DemoStore()
    nora = UserPublic(id=705, username="Nora", status=1)
    actor = UserPublic(id=42, username="yangbun", status=1)

    store.send_friend_request(actor=nora, target_username="yangbun")
    actor_relationship, target_relationship = store.accept_friend_request(
        actor=actor,
        target_user_id=705,
    )

    assert actor_relationship.relationship == "friend"
    assert target_relationship.relationship == "friend"


def test_demo_store_blocks_and_unblocks_user() -> None:
    store = DemoStore()
    actor = UserPublic(id=42, username="yangbun", status=1)

    blocked, target_delete = store.block_user(actor=actor, target_user_id=704)

    assert blocked.relationship == "blocked"
    assert target_delete.id == 42

    unblocked, _ = store.unblock_user(actor=actor, target_user_id=704)

    assert unblocked.id == 704
    assert all(item.id != 704 for item in store.list_relationships(42))
