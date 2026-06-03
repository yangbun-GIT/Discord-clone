# Discord Store Clone Implementation Plan

This plan targets a Discord-like Store experience inside the existing clone. It is
based on direct route inspection plus Discord's public Shop/Profile documentation.

Observed on 2026-06-03:

- `https://discord.com/store` is login-gated. The Codex in-app browser did not share
  the user's Discord login session and was redirected to
  `https://discord.com/login?redirect_to=%2Fstore`.
- Discord's public Shop FAQ describes the Store surface as a place to preview and
  purchase profile cosmetics such as Avatar Decorations, Profile Effects, Nameplates,
  bundles, Nitro member discounts, Orbs exclusives, sort/filter/search, and gifting.
- This project should not copy Discord's paid assets, item names, artwork, pricing, or
  checkout flow. Use original placeholder assets and a demo purchase ledger.

Reference docs:

- Discord Shop FAQ:
  `https://support.discord.com/hc/en-us/articles/17162747936663-Shop-FAQ`
- Discord Avatar Decorations FAQ:
  `https://support.discord.com/hc/en-us/articles/13410113109911-Avatar-Decorations-FAQ`
- Discord Custom Profiles:
  `https://support.discord.com/hc/en-us/articles/4403147417623-Custom-Profiles`

## Product Target

Build a Store tab that feels native to the current Discord clone workspace:

- Entry from the app shell near the existing server rail / direct-message area.
- Store landing with featured collections, drops, category tabs, and item cards.
- Browse mode with search, sort, and filters.
- Item detail preview with profile-card preview.
- Demo purchase, gift, inventory, and apply flows.
- No real payment processing in this educational clone.

## Stage 6.1: Store Scope And Data Contract

Status: completed.

Goal: define exactly what the Store supports before UI work starts.

Tasks:

- Define supported item types:
  - `avatar_decoration`
  - `profile_effect`
  - `nameplate`
  - `bundle`
  - `orb_exclusive`
- Define item ownership states:
  - not owned
  - owned
  - partially owned bundle
  - Nitro-only preview
  - unavailable / expired drop
- Define pricing model:
  - virtual local price string for display
  - optional Orb cost
  - optional Nitro member discount
  - no real payment provider
- Define Store routes:
  - `/store`
  - `/store/browse`
  - `/store/items/:itemId`
  - `/store/inventory`
- Define API contracts before implementation:
  - `GET /api/store/catalog`
  - `GET /api/store/items/{item_id}`
  - `GET /api/store/inventory`
  - `POST /api/store/purchases`
  - `POST /api/store/gifts`
  - `POST /api/store/equip`

Deliverables:

- Backend schema design notes in `PROJECT_CONTEXT.md`.
- TypeScript Store types in `frontend/src/types.ts`.
- Pydantic Store schemas in `backend/app/schemas/store.py`.

Verification:

- Backend schema unit tests for validation boundaries: `npm run test:backend --
  tests/test_store_schema.py`.
- Frontend type check through `npm --prefix frontend run build`.

## Stage 6.2: Store Seed Catalog

Status: completed.

Goal: create a safe demo catalog with original placeholder items.

Tasks:

- Add backend demo Store data with original names and generated visual metadata.
- Use CSS gradients, icons, and simple local placeholder art instead of Discord assets.
- Include at least:
  - 6 avatar decorations
  - 6 profile effects
  - 4 nameplates
  - 3 bundles
  - 4 Orb exclusives
  - 2 limited-time drops
- Add collection metadata:
  - collection name
  - accent color
  - item count
  - availability window
  - featured order
- Add item metadata:
  - item type
  - title
  - short description
  - preview style token
  - price display
  - Orb price
  - Nitro discount flag
  - tags
  - colors
  - theme

Deliverables:

- `backend/app/demo/store_catalog.py`.
- Optional PostgreSQL seed extensions for catalog tables if persistence is included
  in the same slice.

Verification:

- Unit tests confirm catalog IDs are unique, item counts match required minimums,
  collection counts match item metadata, bundle references are valid, and helper
  functions return copies.

## Stage 6.3: Store Backend Read APIs

Status: completed.

Goal: expose catalog and item detail data through authenticated APIs.

Tasks:

- Add `backend/app/api/routes/store.py`.
- Register routes in `backend/app/api/router.py`.
- Implement `GET /api/store/catalog` with:
  - featured collections
  - item summaries
  - categories
  - filters metadata
  - current user's ownership state
- Implement `GET /api/store/items/{item_id}` with:
  - full item detail
  - related bundle data
  - owned/applicable state
  - gift eligibility
- Keep native fallback mode working without PostgreSQL.
- Add database repository interfaces only if persistence is implemented in this stage.

Deliverables:

- Store route module: `backend/app/api/routes/store.py`.
- Store service module: `backend/app/services/store_service.py`.
- Store schemas: `backend/app/schemas/store.py`.

Verification:

- `npm run test:backend`
- `npm run lint:backend`
- API route tests for auth required, catalog response shape, item not found, bundle
  detail data, and default ownership state.

## Stage 6.4: Store Frontend State

Goal: isolate Store state from guild/chat state.

Tasks:

- Add `frontend/src/stores/store.ts`.
- Use `shallowRef` for catalog result sets.
- Track:
  - catalog loading
  - detail loading
  - inventory loading
  - active tab
  - search query
  - selected filters
  - sort mode
  - active item detail
  - mutation error
- Add service calls to `frontend/src/services/api.ts` if needed.
- Keep Store state reset behavior on logout.

Deliverables:

- Pinia Store store.
- Store API wrapper functions.

Verification:

- `npm run lint:frontend`
- `npm --prefix frontend run build`

## Stage 6.5: Store Entry In App Shell

Goal: make Store accessible from the app without disrupting current guild workflows.

Tasks:

- Add Store entry button near the server rail/direct-message area.
- Add app-level mode or route state to switch between:
  - guild workspace
  - Store
  - Store inventory
- Preserve current active guild/channel when entering and leaving Store.
- Add keyboard/focus behavior for the Store entry button.
- Use lucide icon if available; avoid custom SVG unless necessary.

Deliverables:

- Store navigation entry in `ServerRail.vue` or a small adjacent component.
- App-level Store route/view composition in `App.vue`.

Verification:

- Browser smoke test:
  - enter Store
  - return to guild
  - active channel preserved
  - logout clears Store state

## Stage 6.6: Store Landing Page

Goal: build the main Store page surface.

Tasks:

- Add `frontend/src/components/store/StoreView.vue`.
- Add layout regions:
  - top navigation
  - featured hero collection
  - category tabs
  - featured item rows
  - limited drops row
  - Orbs exclusives entry
  - inventory shortcut
- Avoid marketing-page composition. This is an in-app Store surface, not a public
  landing page.
- Ensure page works in the existing dark Discord-like palette without becoming a
  one-color theme.
- Keep cards at 8px radius or less unless current app styling requires otherwise.

Deliverables:

- Store view component.
- Store layout CSS in `frontend/src/styles/base.css` or scoped component styles
  following existing project patterns.

Verification:

- Frontend lint/build.
- Browser screenshot at desktop width.

## Stage 6.7: Item Card Grid

Goal: implement reusable Store item cards.

Tasks:

- Add `StoreItemCard.vue`.
- Card content:
  - preview visual
  - item type badge
  - title
  - collection
  - price / Orb price
  - owned/partial/Nitro discount state
  - gift icon action
- Keep card dimensions stable so badges and long names do not shift layout.
- Use skeleton/loading states for catalog loading.
- Add empty state for no matching items.

Deliverables:

- Reusable card component.
- Item preview subcomponent if needed.

Verification:

- Browser smoke test with long item names.
- Responsive check for narrow viewport.

## Stage 6.8: Browse Tab, Search, Sort, And Filters

Goal: implement Store browsing behavior described by the official Shop FAQ.

Tasks:

- Add Browse tab.
- Add search bar in the upper area of Store content.
- Add Sort By control:
  - recently added
  - price low to high
  - price high to low
  - name
  - owned first
- Add filter sidebar:
  - show only: owned, unowned, discounted, Orb eligible
  - item type
  - color
  - theme
  - collection
- Add Clear all filters.
- Keep filtering client-side for seeded catalog; document when server-side filtering
  becomes necessary.

Deliverables:

- Browse component.
- Filter state in Pinia.
- Filter/sort helpers with focused unit tests if extracted.

Verification:

- Frontend build.
- Browser smoke test:
  - search
  - sort
  - apply multiple filters
  - clear filters
  - empty state

## Stage 6.9: Item Detail And Preview

Goal: let users inspect an item before buying or applying it.

Tasks:

- Add item detail panel or route.
- Include:
  - large item preview
  - profile-card preview
  - title/type/collection
  - description
  - price and discount state
  - bundle relationship
  - owned state
  - buy/apply/gift actions
- Preview item types:
  - avatar decoration: frame around avatar
  - profile effect: animated background/effect layer
  - nameplate: profile/header strip
- Keep animation lightweight and CSS-based.
- Respect reduced-motion preferences.

Deliverables:

- `StoreItemDetail.vue`.
- `ProfileCosmeticPreview.vue`.

Verification:

- Browser smoke test for all item types.
- Reduced motion CSS check.

## Stage 6.10: Demo Purchase Flow

Goal: simulate purchase without collecting payment.

Tasks:

- Add `POST /api/store/purchases`.
- Validate:
  - authenticated user
  - item exists
  - item is purchasable
  - bundle ownership rules
  - enough demo Orbs for Orb purchase
- Record ownership in demo store.
- If PostgreSQL persistence is included:
  - add `store_items`
  - add `user_store_inventory`
  - add `store_purchase_ledger`
- Return updated inventory and item ownership state.
- UI flow:
  - click Buy
  - confirmation modal
  - success state
  - item becomes owned/applyable

Deliverables:

- Purchase route/service.
- Demo store ownership mutation.
- Purchase confirmation UI.

Verification:

- Backend tests for buy success, duplicate purchase, invalid item, partial bundle, and
  Orb balance failure.
- Frontend browser smoke test for demo purchase.

## Stage 6.11: Inventory And Apply Flow

Goal: let users manage owned cosmetics.

Tasks:

- Add `GET /api/store/inventory`.
- Add `POST /api/store/equip`.
- Track equipped cosmetics:
  - avatar decoration
  - profile effect
  - nameplate
- Add inventory tab:
  - owned items grouped by type
  - currently equipped marker
  - apply/remove controls
- Connect equipped cosmetics to profile/member display where practical:
  - member list avatar preview
  - profile preview
  - chat author popover if added later

Deliverables:

- Inventory API.
- Inventory view.
- Equipped cosmetic state in user/session or profile shape.

Verification:

- Backend tests for equip permissions and item ownership.
- Frontend smoke test for apply/remove.

## Stage 6.12: Bundle Rules

Goal: match the Store behavior where bundles are discounted sets but ownership affects
availability.

Tasks:

- Add bundle item model:
  - bundle ID
  - included item IDs
  - bundle price
  - discount display
- Mark bundle states:
  - available
  - partially owned
  - fully owned
  - unavailable
- If one included item is owned, prevent discounted bundle purchase and show partial
  ownership state.
- Show included items inside detail view.

Deliverables:

- Bundle schema/service logic.
- Bundle UI state.

Verification:

- Backend tests for bundle purchase rules.
- UI smoke test for available/partial/owned bundle states.

## Stage 6.13: Gifting Flow

Goal: create a safe demo gift flow inspired by Discord's gifting surface.

Tasks:

- Add gift icon on item card and item detail.
- Add gift modal:
  - recipient search from current guild members
  - card design selection
  - short note
  - optional emoji confetti style
- Add `POST /api/store/gifts`.
- Validate:
  - authenticated sender
  - recipient exists
  - item is giftable
  - sender is not sending to self unless allowed by demo rules
- Record gift in demo ledger/inventory.
- Do not implement real payment.

Deliverables:

- Gift schema/route/service.
- Gift modal UI.
- Gift success state.

Verification:

- Backend tests for gift validation.
- Frontend browser smoke test for gift modal cancel and success.

## Stage 6.14: Orbs Exclusives

Goal: add a virtual reward-currency Store lane.

Tasks:

- Add demo Orb balance to session/user profile.
- Add Orbs Exclusives tab.
- Show items with Orb pricing first when user has enough Orbs.
- Show both virtual cash and Orb price on item detail when eligible.
- Block Orb purchase for excluded types:
  - gifts
  - recurring Nitro-like subscriptions
  - partner-branded items if demo partner items are added later
- Add simple balance update after Orb purchase.

Deliverables:

- Orb balance field in demo user/session response or Store metadata.
- Orbs tab UI.
- Orb purchase branch.

Verification:

- Backend tests for enough/insufficient Orbs.
- UI smoke test for price priority and balance update.

## Stage 6.15: Nitro-Like Discount Simulation

Goal: represent member pricing without implementing real Nitro billing.

Tasks:

- Add demo `is_nitro_member` flag to dev users or Store metadata.
- Display member pricing on eligible items.
- Add explanatory UI that this is demo-only.
- Keep regular users on standard price.
- Avoid subscription billing.

Deliverables:

- Store metadata flag.
- Price presentation component.

Verification:

- Backend tests for discount metadata.
- UI smoke test with Nitro and non-Nitro demo states if both are available.

## Stage 6.16: Profile Integration

Goal: make purchases visible in the rest of the app.

Tasks:

- Extend user/member read shapes with equipped cosmetic IDs.
- Render equipped nameplate/decoration in:
  - member list
  - profile preview
  - optional chat author hover/popover when implemented
- Keep existing member list layout stable.
- Provide fallback when item metadata is unavailable.

Deliverables:

- Schema updates.
- Member list/profile preview integration.

Verification:

- Backend schema tests.
- Frontend build and visual smoke test.

## Stage 6.17: Persistence Path

Goal: persist Store inventory in PostgreSQL while preserving native fallback.

Tasks:

- Extend `backend/app/db/schema.sql` with Store tables:
  - `store_items`
  - `store_collections`
  - `store_bundles`
  - `user_store_inventory`
  - `user_equipped_cosmetics`
  - `store_purchase_ledger`
  - `store_gift_ledger`
- Add idempotent seed data.
- Add PostgreSQL repository methods.
- Keep demo store fallback behavior equivalent.
- Update migration version handling if schema changes.

Deliverables:

- SQL schema changes.
- Seed updates.
- Repository/service switch.

Verification:

- Focused repository tests with fake async database.
- Docker Compose smoke test when Docker is available.

## Stage 6.18: Accessibility And Responsive QA

Goal: make Store usable and stable across screen sizes.

Tasks:

- Keyboard navigation for:
  - Store entry
  - tabs
  - item cards
  - filters
  - modals
- Visible focus states.
- Modal focus trap and escape/close behavior.
- Text overflow handling for long item names.
- Mobile/narrow layout:
  - filter sidebar becomes drawer
  - item grid adapts
  - detail panel becomes full-screen panel

Deliverables:

- Accessibility polish.
- Responsive CSS.

Verification:

- Browser smoke tests at desktop and mobile widths.
- Build/lint.

## Stage 6.19: Store Error States And Loading States

Goal: handle degraded states cleanly.

Tasks:

- Add loading skeletons for catalog/detail/inventory.
- Add retry UI for failed catalog fetch.
- Add permission/auth expired handling.
- Add empty collection and empty search states.
- Add purchase/gift failure messages.
- Keep errors out of console-only state.

Deliverables:

- Store error state UI.
- Pinia mutation state.

Verification:

- Mock/fallback smoke tests where practical.

## Stage 6.20: Final Store QA And Documentation

Goal: close the Store feature as a coherent product slice.

Tasks:

- Update `PROJECT_CONTEXT.md` with Store maps and integration flows.
- Update `docs/implementation-plan.md` Stage 6 status.
- Add Store QA notes if they become large enough for a separate document.
- Run:
  - `npm run test:backend`
  - `npm run lint:backend`
  - `npm run lint:frontend`
  - `npm --prefix frontend run build`
- Browser smoke test:
  - enter Store
  - browse/search/filter/sort
  - open detail
  - demo purchase
  - apply item
  - gift item
  - return to guild
  - logout/login state reset

Deliverables:

- Completed Store implementation.
- Updated documentation.
- Commit and push to `origin/main`.

## External / Deferred Items

Do not implement in the initial Store clone:

- Real payment processing.
- Real Discord artwork or product assets.
- Real Discord item names/prices.
- Refunds tied to payment providers.
- Production commerce compliance.
- Cross-account gift delivery outside the local demo user model.

These require legal, payment, security, and product decisions outside the current
educational clone scope.
