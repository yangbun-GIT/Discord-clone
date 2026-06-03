from app.demo.store_catalog import (
    build_store_filters,
    get_store_item,
    list_store_collections,
    list_store_items,
)
from app.schemas.auth import UserPublic
from app.schemas.store import (
    StoreCatalogRead,
    StoreItemDetailRead,
    StoreItemSummary,
    StoreItemType,
    StoreOwnershipState,
)

DEMO_ORB_BALANCE = 1200


async def get_store_catalog(user: UserPublic) -> StoreCatalogRead:
    items = [_with_user_state(item, user) for item in list_store_items()]
    return StoreCatalogRead(
        collections=list_store_collections(),
        featured=[item for item in items if item.featured],
        items=items,
        categories=list(StoreItemType),
        filters=build_store_filters(),
        orb_balance=DEMO_ORB_BALANCE,
        is_nitro_member=_is_demo_nitro_member(user),
    )


async def get_store_item_detail(item_id: int, user: UserPublic) -> StoreItemDetailRead:
    item = _with_user_state(get_store_item(item_id), user)
    all_items = [_with_user_state(candidate, user) for candidate in list_store_items()]
    items_by_id = {candidate.id: candidate for candidate in all_items}

    included_items = [
        items_by_id[child_id]
        for child_id in item.bundle_item_ids
        if child_id in items_by_id
    ]
    related_items = _related_items(item, all_items)

    return StoreItemDetailRead(
        item=item,
        related_items=related_items,
        included_items=included_items,
        can_purchase=item.ownership_state == StoreOwnershipState.NOT_OWNED,
        can_gift=item.giftable and item.ownership_state == StoreOwnershipState.NOT_OWNED,
        can_equip=False,
    )


def _with_user_state(item: StoreItemSummary, user: UserPublic) -> StoreItemSummary:
    item.ownership_state = StoreOwnershipState.NOT_OWNED
    if _is_demo_nitro_member(user) and item.price.nitro_discount_percent:
        item.price.is_nitro_discounted = True
    return item


def _is_demo_nitro_member(user: UserPublic) -> bool:
    return user.id == 42


def _related_items(
    item: StoreItemSummary,
    all_items: list[StoreItemSummary],
) -> list[StoreItemSummary]:
    if item.type == StoreItemType.BUNDLE:
        related = [
            candidate
            for candidate in all_items
            if candidate.collection_id == item.collection_id and candidate.id != item.id
        ]
    else:
        related = [
            candidate
            for candidate in all_items
            if item.id in candidate.bundle_item_ids or (
                candidate.collection_id == item.collection_id and candidate.id != item.id
            )
        ]
    return related[:6]
