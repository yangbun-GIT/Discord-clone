from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.permissions import MAX_JS_SAFE_INTEGER

HexColor = Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")]
StoreSlug = Annotated[str, Field(min_length=2, max_length=64, pattern=r"^[a-z0-9-]+$")]


class StoreItemType(StrEnum):
    AVATAR_DECORATION = "avatar_decoration"
    PROFILE_EFFECT = "profile_effect"
    NAMEPLATE = "nameplate"
    BUNDLE = "bundle"
    ORB_EXCLUSIVE = "orb_exclusive"


class StoreOwnershipState(StrEnum):
    NOT_OWNED = "not_owned"
    OWNED = "owned"
    PARTIALLY_OWNED = "partially_owned"
    NITRO_ONLY = "nitro_only"
    UNAVAILABLE = "unavailable"


class StoreSortMode(StrEnum):
    RECENTLY_ADDED = "recently_added"
    PRICE_LOW_TO_HIGH = "price_low_to_high"
    PRICE_HIGH_TO_LOW = "price_high_to_low"
    NAME = "name"
    OWNED_FIRST = "owned_first"


class StoreEquipSlot(StrEnum):
    AVATAR_DECORATION = "avatar_decoration"
    PROFILE_EFFECT = "profile_effect"
    NAMEPLATE = "nameplate"


class StorePriceRead(BaseModel):
    price_display: str = Field(min_length=1, max_length=40)
    orb_price: int | None = Field(default=None, ge=0)
    nitro_discount_percent: int | None = Field(default=None, ge=0, le=100)
    is_nitro_discounted: bool = False


class StorePreviewStyle(BaseModel):
    accent_color: HexColor
    secondary_color: HexColor | None = None
    effect: str | None = Field(default=None, max_length=40)
    icon: str | None = Field(default=None, max_length=40)


class StoreCollectionRead(BaseModel):
    id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    slug: StoreSlug
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=1, max_length=240)
    accent_color: HexColor
    item_count: int = Field(ge=0)
    featured: bool = False
    starts_at: str | None = Field(default=None, max_length=40)
    ends_at: str | None = Field(default=None, max_length=40)
    position: int = Field(default=0, ge=0)


class StoreItemSummary(BaseModel):
    id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    collection_id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    type: StoreItemType
    slug: StoreSlug
    title: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=1, max_length=280)
    price: StorePriceRead
    ownership_state: StoreOwnershipState = StoreOwnershipState.NOT_OWNED
    tags: list[str] = Field(default_factory=list, max_length=12)
    colors: list[HexColor] = Field(default_factory=list, max_length=6)
    theme: str = Field(min_length=2, max_length=40)
    preview: StorePreviewStyle
    featured: bool = False
    limited: bool = False
    giftable: bool = True
    bundle_item_ids: list[int] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def validate_bundle_contract(self) -> StoreItemSummary:
        if self.type == StoreItemType.BUNDLE and not self.bundle_item_ids:
            raise ValueError("bundle items must include at least one child item")
        if self.type != StoreItemType.BUNDLE and self.bundle_item_ids:
            raise ValueError("only bundle items can include bundle_item_ids")
        return self


class StoreFiltersRead(BaseModel):
    item_types: list[StoreItemType]
    colors: list[HexColor]
    themes: list[str]
    collections: list[StoreCollectionRead]
    sort_modes: list[StoreSortMode]


class StoreCatalogRead(BaseModel):
    collections: list[StoreCollectionRead]
    featured: list[StoreItemSummary]
    items: list[StoreItemSummary]
    categories: list[StoreItemType]
    filters: StoreFiltersRead
    orb_balance: int = Field(default=0, ge=0)
    is_nitro_member: bool = False


class StoreItemDetailRead(BaseModel):
    item: StoreItemSummary
    related_items: list[StoreItemSummary] = Field(default_factory=list, max_length=12)
    included_items: list[StoreItemSummary] = Field(default_factory=list, max_length=12)
    can_purchase: bool
    can_gift: bool
    can_equip: bool


class StoreEquippedCosmeticsRead(BaseModel):
    avatar_decoration_item_id: int | None = Field(default=None, ge=1, le=MAX_JS_SAFE_INTEGER)
    profile_effect_item_id: int | None = Field(default=None, ge=1, le=MAX_JS_SAFE_INTEGER)
    nameplate_item_id: int | None = Field(default=None, ge=1, le=MAX_JS_SAFE_INTEGER)


class StoreInventoryRead(BaseModel):
    items: list[StoreItemSummary]
    equipped: StoreEquippedCosmeticsRead
    orb_balance: int = Field(default=0, ge=0)
    is_nitro_member: bool = False


class StorePurchaseCreate(BaseModel):
    item_id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    currency: Literal["cash", "orbs"] = "cash"


class StoreGiftCreate(BaseModel):
    item_id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    recipient_id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)
    card_style: StoreSlug = "classic"
    note: str | None = Field(default=None, max_length=120)
    emoji_style: str | None = Field(default=None, max_length=40)


class StoreEquipCreate(BaseModel):
    item_id: int | None = Field(default=None, ge=1, le=MAX_JS_SAFE_INTEGER)
    slot: StoreEquipSlot


class StoreMutationRead(BaseModel):
    item: StoreItemSummary | None = None
    inventory: StoreInventoryRead
    message: str = Field(min_length=1, max_length=160)
