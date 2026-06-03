import pytest
from pydantic import ValidationError

from app.schemas.store import (
    StoreEquipCreate,
    StoreGiftCreate,
    StoreItemSummary,
    StoreItemType,
    StoreOwnershipState,
    StorePreviewStyle,
    StorePriceRead,
    StorePurchaseCreate,
)


def valid_item_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": 6001,
        "collection_id": 5001,
        "type": StoreItemType.AVATAR_DECORATION,
        "slug": "aurora-ring",
        "title": "Aurora Ring",
        "description": "A soft original profile frame for the demo Store.",
        "price": StorePriceRead(price_display="$2.99", orb_price=300),
        "ownership_state": StoreOwnershipState.NOT_OWNED,
        "tags": ["soft", "glow"],
        "colors": ["#77D9FF", "#D882FF"],
        "theme": "aurora",
        "preview": StorePreviewStyle(
            accent_color="#77D9FF",
            secondary_color="#D882FF",
            effect="halo",
            icon="sparkles",
        ),
        "featured": True,
        "limited": False,
        "giftable": True,
        "bundle_item_ids": [],
    }
    payload.update(overrides)
    return payload


def test_store_item_summary_accepts_supported_contract() -> None:
    item = StoreItemSummary(**valid_item_payload())

    assert item.type == StoreItemType.AVATAR_DECORATION
    assert item.price.orb_price == 300
    assert item.preview.accent_color == "#77D9FF"


def test_store_item_summary_rejects_invalid_color_token() -> None:
    with pytest.raises(ValidationError):
        StoreItemSummary(**valid_item_payload(colors=["blue"]))


def test_store_bundle_requires_child_items() -> None:
    with pytest.raises(ValidationError):
        StoreItemSummary(**valid_item_payload(type=StoreItemType.BUNDLE, bundle_item_ids=[]))


def test_store_non_bundle_rejects_bundle_child_items() -> None:
    with pytest.raises(ValidationError):
        StoreItemSummary(**valid_item_payload(bundle_item_ids=[6002]))


def test_store_purchase_create_restricts_currency() -> None:
    assert StorePurchaseCreate(item_id=6001, currency="orbs").currency == "orbs"

    with pytest.raises(ValidationError):
        StorePurchaseCreate(item_id=6001, currency="credits")


def test_store_gift_create_validates_recipient_and_note() -> None:
    gift = StoreGiftCreate(item_id=6001, recipient_id=43, note="Enjoy this.")

    assert gift.card_style == "classic"

    with pytest.raises(ValidationError):
        StoreGiftCreate(item_id=6001, recipient_id=0, note="x" * 121)


def test_store_equip_create_allows_clearing_a_slot() -> None:
    equip = StoreEquipCreate(item_id=None, slot="nameplate")

    assert equip.item_id is None
    assert equip.slot == "nameplate"
