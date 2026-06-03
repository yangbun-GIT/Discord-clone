from collections import Counter

from app.demo.store_catalog import (
    STORE_COLLECTIONS,
    STORE_ITEMS,
    build_store_filters,
    get_store_item,
    list_store_collections,
    list_store_items,
)
from app.schemas.store import StoreItemType


def test_store_catalog_has_required_demo_item_counts() -> None:
    counts = Counter(item.type for item in STORE_ITEMS)

    assert counts[StoreItemType.AVATAR_DECORATION] >= 6
    assert counts[StoreItemType.PROFILE_EFFECT] >= 6
    assert counts[StoreItemType.NAMEPLATE] >= 4
    assert counts[StoreItemType.BUNDLE] >= 3
    assert counts[StoreItemType.ORB_EXCLUSIVE] >= 4
    assert sum(item.limited for item in STORE_ITEMS) >= 2


def test_store_catalog_ids_and_slugs_are_unique() -> None:
    collection_ids = [collection.id for collection in STORE_COLLECTIONS]
    collection_slugs = [collection.slug for collection in STORE_COLLECTIONS]
    item_ids = [item.id for item in STORE_ITEMS]
    item_slugs = [item.slug for item in STORE_ITEMS]

    assert len(collection_ids) == len(set(collection_ids))
    assert len(collection_slugs) == len(set(collection_slugs))
    assert len(item_ids) == len(set(item_ids))
    assert len(item_slugs) == len(set(item_slugs))


def test_store_catalog_collection_counts_match_items() -> None:
    counts = Counter(item.collection_id for item in STORE_ITEMS)

    for collection in STORE_COLLECTIONS:
        assert collection.item_count == counts[collection.id]


def test_store_catalog_bundles_reference_existing_non_bundle_items() -> None:
    items_by_id = {item.id: item for item in STORE_ITEMS}

    for item in STORE_ITEMS:
        if item.type != StoreItemType.BUNDLE:
            continue
        assert item.bundle_item_ids
        assert all(child_id in items_by_id for child_id in item.bundle_item_ids)
        assert all(
            items_by_id[child_id].type != StoreItemType.BUNDLE
            for child_id in item.bundle_item_ids
        )


def test_store_catalog_copy_helpers_do_not_expose_mutable_globals() -> None:
    copied_items = list_store_items()
    copied_collections = list_store_collections()
    copied_items[0].title = "Changed locally"
    copied_collections[0].name = "Changed locally"

    assert STORE_ITEMS[0].title != "Changed locally"
    assert STORE_COLLECTIONS[0].name != "Changed locally"


def test_get_store_item_returns_copy_or_raises_key_error() -> None:
    item = get_store_item(STORE_ITEMS[0].id)
    item.title = "Changed locally"

    assert STORE_ITEMS[0].title != "Changed locally"

    try:
        get_store_item(999999)
    except KeyError as exc:
        assert exc.args == (999999,)
    else:
        raise AssertionError("expected unknown Store item to raise KeyError")


def test_store_filters_include_catalog_metadata() -> None:
    filters = build_store_filters()

    assert StoreItemType.AVATAR_DECORATION in filters.item_types
    assert "#77D9FF" in filters.colors
    assert "aurora" in filters.themes
    assert {collection.id for collection in filters.collections} == {
        collection.id for collection in STORE_COLLECTIONS
    }
