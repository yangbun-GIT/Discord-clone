from app.services import dm_storage


class FakeDatabase:
    def __init__(self, *, is_connected: bool) -> None:
        self.is_connected = is_connected


def test_get_dm_storage_returns_postgres_provider_when_database_connected(
    monkeypatch,
) -> None:
    monkeypatch.setattr(dm_storage, "database", FakeDatabase(is_connected=True))

    storage = dm_storage.get_dm_storage()

    assert isinstance(storage, dm_storage.PostgresDmStorage)


def test_get_dm_storage_returns_demo_provider_when_database_disconnected(monkeypatch) -> None:
    monkeypatch.setattr(dm_storage, "database", FakeDatabase(is_connected=False))

    storage = dm_storage.get_dm_storage()

    assert isinstance(storage, dm_storage.DemoDmStorage)
