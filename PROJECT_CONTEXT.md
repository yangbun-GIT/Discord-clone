# Project Context

This file is the first recovery point for future Codex/Cursor work. Read it before
editing code, then update it whenever a meaningful implementation change lands.

## Required Reading Order

1. `DEVELOPMENT_PROMPT.md` for the project-specific operating prompt, verification
   policy, documentation policy, security policy, and collaboration policy.
2. `AGENTS.md` for concise agent-facing engineering rules.
3. `PROJECT_CONTEXT.md` for the current implementation map and integration points.
4. `docs/implementation-plan.md` for the staged roadmap.
5. `README.md` for setup and verification commands.
6. `docs/README.md` for the document index and task-specific reading guide.
7. `docs/project-file-map.md` for quick path routing before broad exploration.
8. `docs/structure-map/reference-map.md` for cross-file dependency routing.

## Current Milestone

Stage 4's implementation scope is complete. Stage 1, the Docker development baseline,
Stage 2's main persistence/auth/member-management bridge, Stage 3's main text-realtime
scope, focused PostgreSQL repository coverage for current guild/message mutations,
Stage 5 deployment notes/runtime hardening, Stage 6.1 Store data contracts, Stage 6.2
Store seed catalog, Stage 6.3 Store backend read APIs, and Stage 6.4 frontend Store
state are complete and pushed to GitHub. Store UI work is now deferred. Stage 7.1
app destination state, Stage 7.2 `@me` Friends/DM shell, Stage 7.3 first-class
demo-backed Direct Messages, Stage 7.4 server rail parity, Stage 7.5 server
sidebar/header controls, Stage 7.6 composer/message actions, Stage 7.7 voice
channel UX, Stage 7.8 user settings shell, Stage 7.9 server add/discovery flows,
Stage 7.10 DM persistence/realtime expansion, Stage 7.11 responsive QA, and Stage
7.12 final QA/documentation are complete and pushed to GitHub.
Stage 8 Discord UI remediation is complete through Stage 8.14 final QA, including
layout tokens, sidebar overlap cleanup, Korean/English i18n, bottom voice controls,
current-location visibility, placeholder-button cleanup, channel-header panels,
composer panels, Friends/DM information density, settings reorganization, voice
workspace clarity, low-frequency feature scope cleanup, responsive/accessibility QA,
and final command/Docker verification.

Stage 9 Discord visual parity and density remediation is complete. The controlling
plan is `docs/discord-visual-parity-remediation-plan.md`; final QA evidence is in
`docs/stage-9-final-qa.md`. The completed work rebalances FHD 100% zoom layout
density, hides low-value demo/developer text from primary surfaces, improves Friends
and Add Friend density, adds message attachment/reaction visual structure, cleans up
member management visibility, and improves voice/screen-share state clarity with
Discord-like speaking indicators.

Stage 10 interaction polish is complete through Stage 10.29. The controlling plan is
`docs/discord-interaction-polish-plan.md`; the Stage 10.0 baseline lock is recorded
in `docs/stage-10-baseline.md`, and QA evidence is recorded in
`docs/stage-10-final-qa.md`. The completed work covers demo/test data cleanup,
visual-noise reduction, Discord-like shell hierarchy, text/button spacing, bottom
user panel reconstruction, message/composer polish, timeline divider cleanup,
voice/screen-share interaction cleanup, app-owned context menus/notices,
browser-native UI removal for clone workflows, voice-sidebar participant hierarchy,
server-owned voice session tracking, the in-app cross-server voice-switch dialog,
message timeline divider cleanup, server-rail/header seam cleanup, and layered
Friends-surface overlay alignment without the extra private-sidebar header band.
Remaining
voice media verification still depends on a browser session with
microphone and screen-capture permissions granted.

Stage 11 completion work has started. The controlling plan is
`docs/discord-stage-11-completion-plan.md`, and the Stage 11.0 baseline/scope lock
is `docs/stage-11-baseline.md`. Stage 11.1 global layer consolidation is complete:
`frontend/src/styles/base.css` now defines the shared layer, border, surface, and
shadow tokens used by popovers, menus, modals, notices, and sticky overlays. Stage
11.2 Friends finalization is complete: `frontend/src/components/FriendsHome.vue`,
`frontend/src/styles/base.css`, and `frontend/src/i18n/index.ts` now provide clearer
Friends tabs, friend-row separation, activity-card hierarchy, and less demo-oriented
Add Friend copy. Stage 11.3 DM finalization is complete: DM sidebar rows, DM intro
spacing, timeline divider spacing, composer surface color, group-DM copy, and emoji
choices were tightened in `frontend/src/components/DirectMessageView.vue`,
`frontend/src/styles/base.css`, and `frontend/src/i18n/index.ts`. Stage 11.4 server
sidebar and channel navigation polish is complete in `frontend/src/styles/base.css`,
covering rail contrast, voice-connected rail state, guild heading layering, category
create-button discoverability, channel-row height, stable active/connected borders,
and voice-detail spacing. Stage 11.5 text-channel timeline/composer polish is
complete in `frontend/src/components/ChatView.vue`, `frontend/src/styles/base.css`,
and `frontend/src/i18n/index.ts`, removing fake attachment cards, code-like emoji
options, empty-channel date dividers, and demo wording from composer helper panels.
Stage 11.6 bottom user/voice panel polish is complete in
`frontend/src/styles/base.css`, tightening disconnected/connected panel padding,
raised-card styling, disabled action states, and connected voice-card composition.
`docs/stage-11-final-qa.md` records the running Stage 11 QA evidence. Stage 11
preserves the Stage 10 process: each stage is documented, implemented separately,
verified before advancing, and then committed with a Korean commit title before
pushing to `origin/main`.

The app boots in two local modes:

- Docker Compose mode provisions local PostgreSQL and persists created text channels,
  direct messages, relationships, and messages in the `postgres_data` Docker volume.
- Native mode without `DATABASE_URL` still falls back to the process-local demo store
  while preserving async infrastructure boundaries required by the SRS.

## Repository Layout

- `DEVELOPMENT_PROMPT.md`
  - Project-specific AI development prompt adapted from the adaptive prompt template.
  - Defines role, startup order, implementation policy, verification policy,
    documentation policy, security policy, and response policy.
- `package.json`
  - Root script entrypoint.
  - Runs backend tests/lint through `.venv`.
  - Runs frontend dev/lint/build through `frontend/package.json`.
  - Runs Docker Compose through `docker:up`, `docker:down`, and `docker:logs`.
- `compose.yaml`
  - Docker Compose development stack for PostgreSQL, backend, and frontend.
  - Uses external `DATABASE_URL` when provided; otherwise supplies a local PostgreSQL
    URL pointing at the `postgres` service.
  - Uses external `REDIS_URL` when provided; Redis remains optional and empty by
    default.
- `backend/`
  - FastAPI ASGI backend.
  - Python package is configured by `backend/pyproject.toml`.
- `frontend/`
  - Vue 3 + Vite client.
  - TypeScript, Pinia, Vue Router, Oxlint, and lucide icons are configured here.
- `docs/`
  - Long-lived project planning documents.
- `docs/README.md`
  - Documentation index and task-based reading guide.
  - Lists startup reading order, task-specific docs, update rules, and documentation
    verification commands.
- `docs/stage-7-11-responsive-qa.md`
  - Records Stage 7.11 desktop/mobile screenshot paths, viewport metrics, fixes, and
    residual manual QA notes.
- `docs/stage-7-12-final-qa.md`
  - Records Stage 7.12 command verification, Docker smoke, browser smoke workflow,
    and residual external QA notes.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md`
  - Branch, commit, push, staging, verification, and final-report workflow for the
    current `main`-based GitHub flow.
- `docs/PROMPT_COMPLIANCE.md`
  - Maps `DEVELOPMENT_PROMPT.md` policies to concrete repository files and documents.
  - Records prompt-alignment status plus external gaps that cannot be closed locally.
- `docs/store-clone-implementation-plan.md`
  - Detailed staged plan for implementing a Discord Store-like in-app shop.
  - Covers Store catalog, browse/search/filter, item detail preview, demo purchase,
    inventory, apply, gifting, Orbs, Nitro-like discounts, persistence, and QA.
  - Deferred after Stage 6.4 because the target is the full Discord app, not a
    Store-first surface.
- `docs/discord-app-clone-implementation-plan.md`
  - Current primary staged plan for cloning the core Discord web app rooted at
    `https://discord.com/channels/@me`.
  - Covers Friends/DM home, private-channel sidebar, server rail, server/channel
    workspace, DM messaging, settings, voice UX, discovery/add server flows,
    persistence expansion, responsive QA, and documentation.
- `docs/discord-ui-remediation-plan.md`
  - Current controlling Stage 8 plan for Discord UI polish, layout overlap fixes,
  Korean/English i18n, voice/status clarity, placeholder-button reliability,
    responsive/accessibility QA, and final verification.
- `docs/discord-visual-parity-remediation-plan.md`
  - Current controlling Stage 9 plan for real Discord versus clone visual parity.
  - Records screenshot-based problem inventory, staged remediation process,
    verification rules, and additional user reference-data requests.
- `docs/stage-9-final-qa.md`
  - Records Stage 9 command verification, browser QA coverage, completed visual
    parity changes, and residual local-data/capture notes.
- `docs/discord-interaction-polish-plan.md`
  - Current controlling Stage 10 plan for Discord-like interaction polish.
  - Records latest screenshot-based issues, external Discord behavior references,
    stage-by-stage remediation, feature visibility policy, and verification rules.
- `docs/architecture-principles-audit.md`
  - Current architecture-principles and design-pattern audit.
  - Documents SRP, OCP, DIP, encapsulation, DRY, and testability gaps in
    `frontend/src/App.vue`, `frontend/src/stores/guilds.ts`,
    `frontend/src/composables/useVoiceRtc.ts`,
    `backend/app/repositories/guilds.py`, `backend/app/services/guild_service.py`,
    and `backend/app/gateway/manager.py`.
  - Lists the previous Stage 10/11 process to preserve for future refactor stages.
- `docs/project-file-map.md`
  - Quick project folder/file ownership map for faster path lookup before
    implementation.
  - Must be updated when a project folder or important source file is added,
    removed, renamed, or assigned a meaningfully different responsibility.
- `docs/structure-map/`
  - Fast-navigation structure folder.
  - `README.md` defines usage and update rules.
  - `reference-map.md` records core file references and reverse references for
    high-impact backend/frontend files.
- `docs/stage-10-baseline.md`
  - Stage 10.0 baseline lock for FHD 100% comparison screenshots, problem inventory,
    and persistent/demo/test data classification.
- `.env.example`
  - Non-secret environment variable template.
  - Real `.env` files must stay untracked.
- `.dockerignore`, `backend/.dockerignore`, `frontend/.dockerignore`
  - Prevent local virtualenvs, dependencies, build output, secrets, and cache files
    from entering Docker build contexts.

## Backend Map

- `backend/app/main.py`
  - Defines `create_app()`.
  - Registers CORS, local token-bucket rate limiting, REST routes, and WebSocket routes.
  - Lifespan startup connects optional database and Redis pools.
  - Starts the Redis gateway-event subscriber task when Redis is configured and
    cancels it during shutdown.
  - Starts the gateway zombie-connection reaper task and cancels it during shutdown.
- `backend/app/core/config.py`
  - Pydantic settings.
  - Reads `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `CORS_ORIGINS`,
    `WEBRTC_ICE_SERVERS_JSON`, and runtime settings.
  - Validates ICE server entries by requiring non-empty `urls` and exposes TURN
    detection for voice deployment checks.
- `backend/app/core/security.py`
  - Password hashing helpers using bcrypt.
  - JWT creation and decoding using PyJWT.
- `backend/app/api/dependencies.py`
  - Bearer-token dependency for protected REST routes.
  - Decodes JWTs and returns the current user payload.
- `backend/app/api/routes/auth.py`
  - `POST /api/auth/register` creates a database-backed user with bcrypt password
    hashing and returns a JWT.
  - `POST /api/auth/login` verifies username/password credentials and returns a JWT.
  - `GET /api/auth/me` returns the current bearer-token user payload.
  - Registration/login return `503` when no database pool is configured.
- `backend/app/core/rate_limit.py`
  - In-memory token bucket middleware for local Stage 1 protection.
  - Intended to be replaced or backed by Redis during realtime/distributed stages.
- `backend/app/core/sanitize.py`
  - Sanitizes message payloads by removing script blocks, inline event handlers, and
    `javascript:` URLs, then escaping HTML.
- `backend/app/db/pool.py`
  - Optional asyncpg connection pool wrapper.
  - No pool is created when `DATABASE_URL` is empty, so local demo mode can boot.
  - Runs `backend/app/db/schema.sql` through `migrate()` when a database pool exists.
  - Tracks the applied schema version in `schema_migrations`.
- `backend/app/db/schema.sql`
  - Initial PostgreSQL schema for users, guilds, channels, messages, roles, guild
    members, invites, and member roles.
  - Stage 7.10 adds DM profiles, relationships, direct message channels, direct
    message members with unread counts, and direct messages.
- `backend/app/db/seed.py`
  - Seeds the initial SRS demo guild, channels, members, and messages into PostgreSQL.
  - Seeds safe demo relationship and direct message data into PostgreSQL.
  - Uses idempotent inserts and skips guilds/DM rows that already exist.
- `backend/app/domain/snowflake.py`
  - JavaScript-safe Snowflake ID generator.
  - Uses a custom 2026 epoch and 53-bit-safe layout.
- `backend/app/domain/permissions.py`
  - Discord-style bitfield permissions.
  - `merge_permissions()` ORs permission values.
  - `has_permission()` treats `ADMINISTRATOR` as all permissions.
- `backend/app/gateway/opcodes.py`
  - Gateway opcode enum: Dispatch, Heartbeat, Identify, Voice State, Guild Members,
    Voice Signal, Hello, and Heartbeat ACK.
- `backend/app/gateway/events.py`
  - Pydantic gateway event, identify, voice state, and voice signal payload schemas.
- `backend/app/gateway/manager.py`
  - In-memory WebSocket connection registry.
  - Tracks user identity, sequence, heartbeat timestamp, subscribed guild IDs, and
    subscribed channel IDs.
  - Contains zombie-connection reaping helper.
  - Broadcasts Discord-style dispatch payloads to connections subscribed to a channel.
  - Broadcasts guild-scoped dispatch payloads and keeps guild/channel subscriptions in
    sync when channel or guild membership snapshots change.
  - Tracks the active voice channel for each identified connection and can route
    `VOICE_SIGNAL` payloads to a target user in the same voice channel.
  - Tracks subscribed DM IDs and broadcasts `DM_CREATE`/`DM_MESSAGE_CREATE`
    dispatches to DM subscribers.
- `backend/app/gateway/reaper.py`
  - Background loop that periodically calls `gateway_manager.reap_zombies()` using
    the configured heartbeat interval.
- `backend/app/gateway/router.py`
  - `/gateway` WebSocket endpoint.
  - Sends Hello, accepts Identify, validates JWT, sends Ready, handles Heartbeat ACK,
    Request Guild Members, and Update Voice State placeholders.
  - On Identify, loads the authenticated user's guilds/DMs and subscribes the
    connection to every guild channel plus visible DM thread.
  - `UPDATE_VOICE_STATE` validates guild/channel subscriptions, updates the
    connection's active voice channel, and dispatches `VOICE_STATE_UPDATE` to voice
    channel subscribers.
  - `VOICE_SIGNAL` validates the sender is connected to the voice channel and routes
    offer/answer/ICE payloads to the target user.
- `backend/app/realtime/redis_bus.py`
  - Optional Redis asyncio client wrapper.
  - Connects only when `REDIS_URL` is configured.
- `backend/app/realtime/events.py`
  - Defines the Redis gateway-event channel name and `RealtimeGatewayEvent` schema.
- `backend/app/realtime/publisher.py`
  - Publishes `MESSAGE_CREATE`, `MESSAGE_UPDATE`, `MESSAGE_DELETE`, `CHANNEL_CREATE`,
    `GUILD_UPDATE`, `DM_CREATE`, and `DM_MESSAGE_CREATE` payloads to Redis when
    configured.
  - Falls back to local `gateway_manager.broadcast_channel()` when Redis is absent.
  - Updates local gateway subscriptions for channel creation and guild membership
    changes before fallback broadcasts.
  - Updates local DM subscriptions from `DM_CREATE` participants before broadcasting
    new DM events.
- `backend/app/realtime/subscriber.py`
  - Consumes Redis gateway-event Pub/Sub messages and fans them out to local WebSocket
    subscribers.
  - Updates local gateway subscriptions for channel creation and guild membership
    changes before broadcasting Redis-sourced events.
  - Updates local DM subscriptions for Redis-sourced `DM_CREATE` events and broadcasts
    DM events by `dm_id`.
- `backend/app/api/routes/health.py`
  - `/api/health` reports service status and whether DB/Redis are configured/connected.
  - Empty `DATABASE_URL` and `REDIS_URL` values are reported as not configured.
- `backend/app/api/routes/dev.py`
  - `/api/dev/session` creates a local development JWT and user payload.
  - Only intended for local/dev/test environments.
- `backend/app/api/routes/guilds.py`
  - `/api/guilds/me` requires a bearer token and returns the authenticated user's
    PostgreSQL-backed guild memberships when connected, otherwise demo guild data for
    the frontend shell.
  - `GET /api/guilds/{guild_id}` refreshes a single guild snapshot for current members.
  - `POST /api/guilds` creates a guild owned by the authenticated user with default
    `general` text and `voice-room` voice channels.
  - `POST /api/guilds/{guild_id}/invites` creates an invite code for users with
    `CREATE_INSTANT_INVITE`.
  - `POST /api/guilds/invites/{code}/join` adds the authenticated user to the invited
    guild.
  - `POST /api/guilds/{guild_id}/roles` creates a role for administrators and returns
    the refreshed guild payload.
  - `POST /api/guilds/{guild_id}/members/{member_id}/roles` assigns a role to a member.
  - `DELETE /api/guilds/{guild_id}/members/{member_id}/roles/{role_id}` removes an
    assigned role from a member.
  - `DELETE /api/guilds/{guild_id}/members/{member_id}` removes a non-owner member
    from a guild for administrators.
  - `POST /api/guilds/{guild_id}/channels` creates text or voice channels through
    the guild service.
  - Channel creation returns `403` when the authenticated user lacks
    `MANAGE_CHANNELS`.
  - Channel creation publishes `CHANNEL_CREATE`; invite join, role mutations, and
    member removal publish `GUILD_UPDATE`.
- `backend/app/api/routes/channels.py`
  - `POST /api/channels/{channel_id}/messages` creates sanitized messages through
    the guild service.
  - `PATCH /api/channels/{channel_id}/messages/{message_id}` edits sanitized message
    content for the message author or users with `MANAGE_MESSAGES`.
  - `DELETE /api/channels/{channel_id}/messages/{message_id}` deletes messages for
    the message author or users with `MANAGE_MESSAGES`.
  - Message creation returns `403` when the authenticated user is not a guild member
    or lacks `SEND_MESSAGES`.
  - After persistence succeeds, publishes `MESSAGE_CREATE`, `MESSAGE_UPDATE`, or
    `MESSAGE_DELETE` through the realtime publisher.
- `backend/app/api/routes/users.py`
  - `GET /api/users/me/relationships` requires a bearer token and returns safe demo
    relationship rows for the current local user.
- `backend/app/api/routes/dms.py`
  - `GET /api/dms` requires a bearer token and returns only DM threads where the
    current user is a participant.
  - `POST /api/dms` creates or returns an existing one-to-one or group DM for known
    demo recipients.
  - `POST /api/dms/{dm_id}/messages` creates sanitized DM messages and rejects
    non-members or path/payload ID mismatches.
- `backend/app/api/routes/meta.py`
  - `/api/meta/permissions` exposes permission names and integer values.
  - `/api/meta/voice` exposes WebRTC ICE server config from
    `WEBRTC_ICE_SERVERS_JSON`, plus ICE server count and whether TURN is configured.
- `backend/app/api/routes/store.py`
  - `GET /api/store/catalog` requires a bearer token and returns the demo Store
    catalog, featured items, categories, filters, demo Orb balance, Nitro-like demo
    metadata, and default ownership states.
  - `GET /api/store/items/{item_id}` requires a bearer token and returns item detail,
    related items, included bundle items, gift eligibility, purchase eligibility, and
    current equip eligibility.
  - Unknown Store item IDs return `404`.
- `backend/app/demo/data.py`
  - Initial guild/channel/member/message seed data used before persistence is wired.
- `backend/app/demo/store_catalog.py`
  - Original demo Store catalog for Stage 6.
  - Defines five collections, 23 cosmetics, three bundles, four Orb exclusives, and
    limited-drop metadata without real Discord assets, item names, or prices.
  - Exposes copy-returning helpers for listing collections/items, fetching one item,
    and building filter metadata for future Store APIs.
- `backend/app/demo/store.py`
  - Process-local mutable demo store.
  - Creates guilds, invite codes, roles, member-role assignments, channels, messages,
    relationships, DM threads, and DM messages with Snowflake IDs.
  - Updates and deletes messages for the message author or guild owner.
  - Still used for guild/channel/message fallback when no database pool is configured.
  - DM and relationship state intentionally uses this demo store until Stage 7.10
    adds PostgreSQL persistence and realtime DM dispatch.
  - Filters guild reads by member and enforces owner-only channel creation plus
    owner-only role/member management plus member-only message creation.
- `backend/app/repositories/guilds.py`
  - PostgreSQL repository for guild creation, invite creation/join, role creation,
    member-role assignment/removal, member removal, guild membership reads, channel
    creation, message creation, message update, and message deletion.
  - Converts asyncpg rows into `GuildRead`, `ChannelRead`, `MemberRead`, and
    `RoleRead`/`MessageRead` schemas.
  - Computes effective permissions from ownership, base member permissions, and role
    permissions.
  - Requires `MANAGE_CHANNELS` for channel creation and `SEND_MESSAGES` for message
    creation.
  - Requires message author ownership or `MANAGE_MESSAGES` for message update/delete.
  - Requires `ADMINISTRATOR` for role creation and member-role mutations.
- `backend/app/repositories/dms.py`
  - PostgreSQL repository for relationship reads, DM membership reads, DM creation,
    DM message creation, membership checks, unread count updates, and `DmRead`
    assembly.
  - Uses JavaScript-safe Snowflake IDs and keeps DM participants scoped to current
    DM membership.
- `backend/app/repositories/users.py`
  - PostgreSQL repository for creating users and fetching password hashes by username.
- `backend/app/services/guild_service.py`
  - Runtime switch between PostgreSQL repositories and the process-local demo store.
  - Keeps route handlers independent from the current persistence mode.
- `backend/app/services/dm_service.py`
  - Async service boundary for Stage 7.3 DM APIs.
  - Uses `dm_repository` when PostgreSQL is connected and `demo_store` otherwise for
    relationships, DM list/create, and DM message creation.
- `backend/app/services/auth_service.py`
  - Coordinates registration/login with async repository calls and runs bcrypt
    hashing/verification off the event loop.
- `backend/app/services/store_service.py`
  - Builds authenticated Store catalog and item-detail responses from the safe demo
    catalog.
  - Applies the current user's demo metadata, including `not_owned` ownership state
    and a local demo Nitro-like flag for user ID `42`.
  - Keeps Stage 6 read APIs independent from future purchase/inventory persistence.
- `backend/app/schemas/`
  - Pydantic API schemas for auth, guilds, messages, Direct Messages, and Store
    contracts.
- `backend/app/schemas/dm.py`
  - Relationship, DM participant, DM thread, DM message, DM create, and DM message
    create contracts.
  - Sanitizes DM message content with the shared message sanitizer at the schema
    boundary.
- `backend/app/schemas/store.py`
  - Store item, collection, price, preview, catalog, detail, inventory, purchase,
    gift, equip, and mutation response schemas.
  - Defines supported item types, ownership states, sort modes, and equip slots for
    Stage 6 before Store routes are implemented.
  - Validates hex color tokens, JavaScript-safe IDs, bundle child-item boundaries, and
    Store mutation request payload limits.
- `backend/tests/`
  - Unit tests for permissions, Snowflake IDs, settings, demo store mutations, protected
    API routes, gateway connection management, message schema sanitization, Store
    schema validation, Store seed catalog integrity, Store read API contracts, and
    focused guild repository mutation behavior for guild creation/reads, channel
    creation, invites, roles, member removal, and message update/delete.

## Frontend Map

- `frontend/vite.config.ts`
  - Vite Vue config.
  - Proxies `/api` to `VITE_BACKEND_PROXY_TARGET`, defaulting to
    `http://127.0.0.1:8000`.
  - Proxies `/gateway` WebSocket traffic to the same target with `ws` protocol.
  - Compose sets `VITE_BACKEND_PROXY_TARGET=http://backend:8000`.
- `frontend/src/main.ts`
  - Creates Vue app, Pinia, and Vue Router.
- `frontend/src/App.vue`
  - Main Discord-like workspace screen.
  - Composes server rail, private-channel sidebar, Friends home, channel sidebar,
    DM chat view, server chat view, member list, and voice panel.
  - Restores saved sessions, shows auth UI when logged out, loads guild data after
    authentication, and connects the gateway.
  - Opens the `@me` Friends destination after login, preserves current guild/channel
    state, and switches back to the server workspace when a server is selected.
  - Renders Discord-like server channel header controls for threads, notification
    settings, pinned messages, member-list toggle, search, inbox, and help.
  - Owns member-list visibility state and local placeholder notices for app-shell
    controls that are intentionally not backend-backed yet.
- `frontend/src/components/AuthPanel.vue`
  - Login/register form plus an explicit Demo user button for local development.
  - Emits auth actions to `App.vue`; it does not own token storage.
- `frontend/src/services/api.ts`
  - Small fetch wrapper for GET and POST calls.
  - GET, POST, PATCH, and DELETE calls accept an optional bearer token.
  - Exposes relationship and Direct Message wrappers for
    `/api/users/me/relationships`, `/api/dms`, and `/api/dms/{dm_id}/messages`.
  - Exposes Store read wrappers for `/api/store/catalog` and
    `/api/store/items/{item_id}`.
- `frontend/src/stores/session.ts`
  - Pinia session store.
  - Calls `/api/auth/login`, `/api/auth/register`, `/api/auth/me`, and
    `/api/dev/session`.
  - Stores JWT/current user in localStorage and clears them on logout.
- `frontend/src/stores/guilds.ts`
  - Pinia guild store.
  - Uses `shallowRef` for guild data as required by the SRS performance guidance.
  - Loads `/api/guilds/me`.
  - Tracks loading, mutation, and API error state for guild/channel/message/invite
    operations.
  - Tracks active guild, active channel, active messages, voice channel, and voice
    connection UI state.
  - Tracks voice states and the latest voice signal dispatch received from the gateway.
  - Calls the protected guild creation API and selects the new guild's first channel.
  - Calls invite creation and invite join APIs.
  - Calls role creation, role assignment, and role removal APIs.
  - Calls single-guild refresh and member removal APIs.
  - Calls the protected channel creation and message creation/update/delete APIs.
  - Applies gateway `MESSAGE_CREATE` dispatches with message ID deduplication so REST
    echoes and WebSocket events do not double-insert messages.
  - Applies gateway `MESSAGE_UPDATE` and `MESSAGE_DELETE` dispatches to update or
    remove local message state.
  - Applies gateway `CHANNEL_CREATE` dispatches with channel ID deduplication.
  - Applies gateway `GUILD_UPDATE` dispatches by replacing the local guild snapshot
    and preserving a valid active channel.
  - Uses `document.startViewTransition()` when available for channel switching.
- `frontend/src/stores/dms.ts`
  - Pinia DM store for Stage 7.3.
  - Uses `shallowRef` for relationship rows and DM thread snapshots.
  - Loads authenticated relationship and DM data, creates or opens DM threads from a
    friend row, sends sanitized DM messages through the backend, appends returned
    messages immutably, and resets on logout.
  - Applies `DM_CREATE` and `DM_MESSAGE_CREATE` gateway dispatches with idempotent
    upsert/append behavior.
- `frontend/src/stores/navigation.ts`
  - Pinia app destination store for the Discord-like shell.
  - Tracks `friends`, `dm`, `server_channel`, `voice_channel`, and `settings`
    destinations plus active DM ID.
  - Keeps `@me` navigation independent from guild/channel state.
- `frontend/src/stores/store.ts`
  - Pinia Store state module for Stage 6.
  - Uses `shallowRef` for catalog, active item detail, and future inventory payloads.
  - Tracks catalog/detail/inventory loading, active tab, search query, selected item
    type/ownership/show-only/color/theme/collection filters, sort mode, mutation
    state, and API errors.
  - Provides computed featured, Orb-eligible, and filtered/sorted item result sets.
  - Resets Store state independently from guild/chat state on logout.
- `frontend/src/composables/useGateway.ts`
  - Browser WebSocket gateway client.
  - On Hello opcode 10, sends Identify opcode 2 and starts heartbeat opcode 1.
  - Shows connected state after Ready dispatch.
  - Accepts a dispatch callback and forwards non-READY gateway dispatch events to the
    app store.
  - Exposes `updateVoiceState()` for opcode 4 and `sendVoiceSignal()` for opcode 5.
- `frontend/src/composables/useVoiceRtc.ts`
  - Owns browser microphone capture, screen capture, `RTCPeerConnection` lifecycle,
  local VAD/input-level sampling, mute state, offer/answer/ICE handling, remote
    stream tracking, screen-share renegotiation, WebRTC `getStats()` quality
    sampling, and cleanup.
- `frontend/src/components/ServerRail.vue`
  - Discord-like rail with `@me` Direct Messages button, server icons, separators,
    server unread/mention badges, muted indicator, demo folder grouping, create-server
    icon button, and discovery icon button.
  - Uses accessible labels that include unread, mention, and muted state.
- `frontend/src/components/PrivateChannelSidebar.vue`
  - `@me` sidebar with search/start conversation button, Friends/Nitro/Shop/Quests
    entries, API-backed DM list, unread badges, and create-DM action placeholder.
- `frontend/src/components/FriendsHome.vue`
  - Friends home surface with Online/All/Pending/Blocked/Add Friend tabs, search,
    API-backed safe demo relationship rows, message actions, and add-friend
    placeholder form.
  - Emits `messageFriend` so `App.vue` can create or open a DM through `dms.ts`.
- `frontend/src/components/DirectMessageView.vue`
  - Renders selected DM participant intro, message history, and a DM composer inside
    the `dm` destination.
  - Keeps server channel editing/deletion behavior isolated in `ChatView.vue`.
- `frontend/src/components/ChannelSidebar.vue`
  - Text and voice channel lists.
  - Provides a server menu entry, Events entry, collapsible text/voice categories,
    inline text and voice channel creation forms, invite actions, and channel settings
    placeholder actions.
- `frontend/src/components/ChatView.vue`
  - Message list and composer UI.
  - Emits submitted message content, message edits, and message deletions to the guild
    store.
  - Shows edit controls for the current user's own messages and delete controls for
    own messages or `MANAGE_MESSAGES`.
  - Provides local reply targeting, message options menu, and composer action buttons
    for upload, gift, apps/actions, and emoji while preserving the existing backend
    send/edit/delete behavior.
- `frontend/src/components/MemberList.vue`
  - Member presence list.
  - Shows role labels and exposes administrator-only controls for role creation,
    assignment, and removal.
  - Exposes member refresh and non-owner member removal controls.
- `frontend/src/components/VoicePanel.vue`
  - Voice connection toggle UI.
  - Shows voice participant count, gateway signaling readiness, local speaking state,
    microphone input level, mute control, screen-share control, TURN/STUN status, and
    WebRTC quality diagnostics.
- `frontend/src/components/VoiceAudioSink.vue`
  - Binds remote `MediaStream` instances to hidden autoplay audio elements.
- `frontend/src/components/VoiceVideoSink.vue`
  - Binds remote screen-share video streams to floating video preview tiles.
- `frontend/src/styles/base.css`
  - App layout, accessible focus styles, responsive behavior, and View Transitions rule.
- `frontend/src/types.ts`
  - Shared frontend types matching the current backend demo API shape.
  - Includes Store TypeScript contracts for item types, ownership states, catalog,
    filters, item detail, inventory, purchase, gift, equip, and mutation responses.
- `docs/deployment.md`
  - VM/runtime deployment checklist, production environment variables, HTTPS/gateway
    notes, ICE/TURN guidance, voice verification, and hardening notes.
- `docs/voice-qa.md`
  - Two-browser local smoke test, TURN/NAT test, and deployment verification checklist
    for voice, screen sharing, and browser WebRTC stats.
- `backend/Dockerfile`
  - `dev` target installs backend dev dependencies and runs Uvicorn with reload.
  - `runtime` target installs production dependencies and runs Gunicorn with Uvicorn
    workers.
- `frontend/Dockerfile`
  - `dev` target runs Vite on `0.0.0.0`.
  - `build` target produces the static bundle.
  - `runtime` target serves the bundle through Nginx.
- `frontend/nginx.conf`
  - Production static server config.
  - Proxies `/api/` and `/gateway` to `backend:8000` for containerized deployments.

## Current Integrations

- Frontend startup flow:
  - `App.vue` calls `session.restoreSession()`.
  - If no saved token exists, `AuthPanel.vue` is shown.
  - Login/register POST to `/api/auth/login` or `/api/auth/register`.
  - Demo user explicitly POSTs to `/api/dev/session`.
  - After authentication, `App.vue` calls `guilds.loadGuilds(session.token)` and
    `useGateway().connect(token)`.
  - Logout closes the gateway, clears Pinia guild state, and removes saved session
    data from localStorage.
- Auth API flow:
  - Clients POST `{ username, password }` to `/api/auth/register` or
    `/api/auth/login`.
  - Backend validates auth schema payloads, uses PostgreSQL users, bcrypt password
    hashes, and returns the same JWT response shape as the dev session endpoint.
  - `GET /api/auth/me` validates bearer tokens through `get_current_user`.
- Store read API flow:
  - Store read APIs require the same bearer-token dependency as guild/message APIs.
  - `GET /api/store/catalog` returns the Stage 6 demo catalog from
    `store_service.get_store_catalog()`.
  - `store_service` reads original catalog data from `backend/app/demo/store_catalog.py`,
    applies the current user's default `not_owned` state, and returns featured items,
    categories, filter metadata, demo Orb balance, and Nitro-like demo metadata.
  - `GET /api/store/items/{item_id}` returns item detail, included bundle children,
    related items, purchase/gift eligibility, and current equip eligibility.
- Store frontend state flow:
  - `frontend/src/services/api.ts` wraps Store catalog and item-detail fetches.
  - `frontend/src/stores/store.ts` loads Store catalog/detail data with the current
    bearer token and keeps Store filters/sort state independent from guild state.
  - `App.vue` calls `store.resetStoreState()` during logout so Store state cannot
    leak between sessions.
- Discord app destination flow:
  - `openWorkspace()` loads guilds and voice config, then opens the `friends`
    destination before connecting the gateway.
  - `openWorkspace()` also loads relationships and Direct Messages through
    `frontend/src/stores/dms.ts`.
  - `ServerRail.vue` emits `home` for the `@me` button and `select` for guild icons.
  - `App.vue` routes `friends` and `dm` destinations to
    `PrivateChannelSidebar.vue`; `friends` renders `FriendsHome.vue`, while `dm`
    renders `DirectMessageView.vue`.
  - Selecting a server switches the destination to `server_channel` and preserves the
    existing guild/channel chat behavior.
- Direct Message flow:
  - `GET /api/users/me/relationships` and `GET /api/dms` hydrate `dms.ts` after
    login/demo session restore.
  - `PrivateChannelSidebar.vue` renders loaded DM threads and opens a selected thread
    through `navigation.openDm()`.
  - `FriendsHome.vue` emits `messageFriend`; `App.vue` calls
    `dms.createDm(token, [friendId])`, then opens the returned thread.
  - `DirectMessageView.vue` emits submitted content; `dms.ts` POSTs to
    `/api/dms/{dm_id}/messages`, appends the returned sanitized message, and keeps
    `ChatView.vue` focused on server text channels.
- Guild creation flow:
  - `ServerRail.vue` and the empty workspace call `App.vue`'s create-server handler.
  - `App.vue` opens a focused server-name dialog.
  - `guilds.ts` POSTs to `/api/guilds` with the current bearer token.
  - Backend creates the guild, owner membership, `general`, and `voice-room`, then
    returns a complete `GuildRead`.
  - `guilds.ts` appends the guild, selects it, and selects its first channel.
- Invite flow:
  - Active workspace topbar exposes create-invite and join-server icon buttons.
  - `guilds.ts` POSTs to `/api/guilds/{guild_id}/invites` to receive an invite code.
  - Another authenticated user can submit that code through the join-server dialog.
  - `guilds.ts` POSTs to `/api/guilds/invites/{code}/join`, appends or replaces the
    joined guild in local state, then selects it.
- Role management flow:
  - `MemberList.vue` emits role creation, assignment, and removal actions when the
    active guild grants `ADMINISTRATOR`.
  - `guilds.ts` POSTs to `/api/guilds/{guild_id}/roles` to create a role, POSTs to
    `/api/guilds/{guild_id}/members/{member_id}/roles` to assign it, and DELETEs
    `/api/guilds/{guild_id}/members/{member_id}/roles/{role_id}` to remove it.
  - Backend validates JWTs, checks administrator permissions, writes to
    `roles/member_roles` in PostgreSQL or the demo store, and returns the refreshed
    `GuildRead` for local state replacement.
- Member management flow:
  - `MemberList.vue` emits refresh and remove-member actions.
  - `guilds.ts` GETs `/api/guilds/{guild_id}` to refresh the active guild and DELETEs
    `/api/guilds/{guild_id}/members/{member_id}` to remove a non-owner member.
  - Backend validates JWTs, checks administrator permissions for removal, rejects owner
    and self-removal, deletes the membership from PostgreSQL or the demo store, and
    returns the refreshed `GuildRead`.
- Message mutation flow:
  - `ChatView.vue` emits submitted content.
  - `guilds.ts` POSTs to `/api/channels/{channel_id}/messages` with bearer token.
  - Backend validates JWT, sanitizes content, checks guild membership and
    `SEND_MESSAGES`, persists through PostgreSQL when connected or appends to
    `demo_store` in native fallback mode, then returns the created message.
  - `guilds.ts` immutably appends the returned message to the active guild state.
  - `ChatView.vue` also emits edits and deletes for eligible message rows.
  - `guilds.ts` PATCHes or DELETEs
    `/api/channels/{channel_id}/messages/{message_id}` with bearer token.
  - Backend sanitizes edited content, checks the actor is the message author or has
    `MANAGE_MESSAGES`, updates/deletes through PostgreSQL or `demo_store`, and returns
    either the updated message or `{ id, channel_id }`.
  - `guilds.ts` updates or removes the local message after the REST response and also
    accepts matching realtime echoes.
- Channel creation flow:
  - `ChannelSidebar.vue` opens an inline channel-name form from the plus icon.
  - `guilds.ts` POSTs to `/api/guilds/{guild_id}/channels` with bearer token.
  - Backend validates JWT, checks `MANAGE_CHANNELS`, persists through PostgreSQL when
    connected or appends to `demo_store` in native fallback mode, then returns the
    created channel.
  - `guilds.ts` immutably appends the returned channel and selects it.
- Gateway flow:
  - Server accepts `/gateway`.
  - Server sends Hello: `{ op: 10, d: { heartbeat_interval } }`.
  - Client sends Identify: `{ op: 2, d: { token, os, library } }`.
  - Server validates JWT, subscribes the connection to the authenticated user's guild
    and channel IDs, and sends Ready dispatch: `{ op: 0, t: "READY" }`.
  - Client sends Heartbeat: `{ op: 1 }`.
  - Server replies Heartbeat ACK: `{ op: 11 }`.
  - The lifespan reaper closes connections that miss two heartbeat windows with code
    `4000` and removes them from the in-memory connection registry.
- Voice signaling flow:
  - `VoicePanel.vue` toggles local voice connection state through `App.vue`.
  - `App.vue` loads ICE config from `/api/meta/voice`, starts microphone capture
    through `useVoiceRtc()`, then calls `useGateway().updateVoiceState()` with opcode
    4, the active guild, and the first voice channel.
  - `/api/meta/voice` also returns `turn_configured`, which the voice panel displays
    as `TURN ready` or `STUN only`.
  - Backend validates the identified connection is subscribed to the guild/channel and
    broadcasts `VOICE_STATE_UPDATE` to voice-channel subscribers.
  - Gateway opcode 5 accepts `offer`, `answer`, or `ice` voice signal payloads and
    routes them to the target user only when the sender and target are in the same
    voice channel.
  - `guilds.ts` stores voice presence state and the latest received signal.
  - `useVoiceRtc()` opens one peer connection per remote voice participant, sends
    offers from the lower user ID to avoid glare, applies answers and ICE candidates,
    renders remote audio through `VoiceAudioSink`, and tears down tracks/connections on
    disconnect.
  - Mute toggles local audio track enabled state without leaving the voice channel.
  - Screen sharing uses `getDisplayMedia()`, adds/removes a video sender on each
    active peer connection, renegotiates offers, and renders remote screen streams
    through `VoiceVideoSink`.
  - Local VAD samples microphone frequency data and exposes both a speaking flag and
    input-level meter in `VoicePanel`.
  - While connected, `useVoiceRtc()` samples `RTCPeerConnection.getStats()` every two
    seconds and the voice panel displays connected peers, RTT, inbound audio jitter,
    inbound packet loss, outbound audio bitrate, and outbound screen-share bitrate.
- Realtime message flow:
  - `POST /api/channels/{channel_id}/messages` persists the sanitized message first.
  - `publish_message_create()` emits a `MESSAGE_CREATE` realtime event.
  - `PATCH /api/channels/{channel_id}/messages/{message_id}` persists sanitized
    content first and `publish_message_update()` emits `MESSAGE_UPDATE`.
  - `DELETE /api/channels/{channel_id}/messages/{message_id}` deletes first and
    `publish_message_delete()` emits `MESSAGE_DELETE`.
  - With Redis configured, the payload is published to
    `discord_clone:gateway_events`, consumed by the lifespan subscriber, and broadcast
    to local WebSocket connections subscribed to the channel.
  - Without Redis, the publisher directly uses the local gateway manager so native
    development still receives live message events.
  - `useGateway()` forwards gateway dispatches into `guilds.handleGatewayDispatch()`,
    which appends unseen messages by ID, replaces edited messages, and removes
    deleted messages.
- Realtime DM flow:
  - Gateway Identify loads the authenticated user's DM threads and subscribes the
    connection to their DM IDs.
  - `POST /api/dms` persists or returns a DM thread, publishes `DM_CREATE`, and
    gateway managers add the new DM ID to connected participant subscriptions before
    broadcasting.
  - `POST /api/dms/{dm_id}/messages` persists sanitized DM messages and publishes
    `DM_MESSAGE_CREATE` to DM subscribers.
  - `frontend/src/App.vue` forwards gateway dispatches to both the guild and DM
    Pinia stores, and `frontend/src/stores/dms.ts` applies DM events idempotently.
- Realtime guild state flow:
  - Channel creation publishes `CHANNEL_CREATE` to guild subscribers and updates their
    server-side channel subscriptions so future messages in the new channel can fan
    out without reconnecting.
  - Invite join, role creation/assignment/removal, and member removal publish
    `GUILD_UPDATE`.
  - `GUILD_UPDATE` syncs local gateway guild/channel subscriptions from the incoming
    member and channel snapshot, then broadcasts the refreshed guild payload.
  - The frontend applies `CHANNEL_CREATE` by appending unseen channels and applies
    `GUILD_UPDATE` by replacing the guild snapshot.
- External services:
  - `DATABASE_URL` will point to Neon PostgreSQL.
  - Docker Compose sets `DATABASE_URL` to local PostgreSQL by default.
  - `REDIS_URL` will point to Upstash Redis.
  - Native local shell can leave both empty and use the demo-store fallback.
- Docker development flow:
  - `npm run docker:up` builds and starts `postgres`, `backend`, and `frontend`.
  - Backend startup connects PostgreSQL, runs `schema.sql`, then seeds guild and DM
    demo data.
  - Frontend container proxies API/WebSocket traffic to `backend:8000` inside the
    Compose network.
  - Host browser still uses `http://127.0.0.1:5173`.
  - `npm run docker:down` stops containers while preserving `postgres_data`.
  - Use `docker compose down -v` only when resetting local PostgreSQL data is intended.

## Verification Commands

Run these from the repository root unless noted otherwise:

```powershell
npm run test:backend
npm run lint:backend
npm run lint:frontend
npm --prefix frontend run build
docker compose exec -T backend pytest
```

Local servers:

```powershell
npm run dev:backend
npm run dev:frontend
```

Expected local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

Docker servers:

```powershell
npm run docker:up
npm run docker:down
```

## Known Decisions And Constraints

- `DEVELOPMENT_PROMPT.md` is the highest-level local prompt document for future
  AI-assisted development in this repository. Keep it focused on durable operating
  policy, not one-off implementation details.
- `docs/PROMPT_COMPLIANCE.md` is the audit surface for checking whether the repository
  structure still reflects `DEVELOPMENT_PROMPT.md`.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md` documents the current single-user
  `main`-based push workflow; switch it only when the user requests branch/PR-based
  collaboration.
- The SRS says Pydantic v3, but the current PyPI line is Pydantic v2. The backend
  pins Pydantic v2 and isolates schema code for a future upgrade.
- In Docker Compose mode, text channels and messages persist across backend restarts
  through local PostgreSQL. In native mode without `DATABASE_URL`, created
  messages/channels survive page reloads while the backend process is alive but reset
  when that process restarts.
- Channel creation currently accepts ASCII slug names only, matching Discord-style
  channel names and avoiding inconsistent Unicode slug handling.
- `node_modules/`, `.venv/`, `dist/`, `*.egg-info/`, and `*.tsbuildinfo` are ignored
  and must not be committed.
- Real secrets belong in `.env`, not in Git.
- UI should remain the actual app surface, not a landing page or feature explainer.
- Docker is additive, not a replacement for native local development. Use native
  scripts for quick iteration and Docker when environment reproducibility matters.
- Docker Desktop must be running before `npm run docker:up`.

## Next Work

Next implementation stage:

- Start Stage 9 from `docs/discord-visual-parity-remediation-plan.md`.
- Stage 8.0 through Stage 8.14 are complete. The next user-directed priority is
  Discord visual parity and density remediation based on the side-by-side comparison
  screenshots.
- Stage 9 should begin with baseline measurement, screenshot matrix capture, safe
  demo content density, and global shell design-token tuning before individual
  Friends, channel, composer, and voice surfaces are polished.
- Run multi-browser manual voice QA with a real TURN provider configured.
- Tune WebRTC quality with real network stats after manual QA exposes bottlenecks.
- Continue production deployment execution when target VM/provider is chosen.
- Resume deferred Store UI work only if the user explicitly returns to Store scope.

Discord app inspection observation:

- `https://discord.com/channels/@me` was inspected through the Codex in-app browser on
  2026-06-03 with the user's logged-in Discord session.
- The implementation target is the Discord app shell: server rail, private-channel
  sidebar, Friends/DM home, server/channel sidebar, channel header controls, message
  timeline/composer, voice channel rows, bottom user panel, and settings entry.
- Do not copy real Discord private names, messages, server content, or assets into
  repository fixtures or documentation.
- Stage 7.1 and 7.2 completed the first app-parity slice:
  - App destination state is in `frontend/src/stores/navigation.ts`.
  - `@me` private sidebar is in `frontend/src/components/PrivateChannelSidebar.vue`.
  - Friends home is in `frontend/src/components/FriendsHome.vue`.
- Stage 7.3 moved safe demo friend/DM data into the backend and completed functional
  DM messaging:
  - DM contracts are in `backend/app/schemas/dm.py`.
  - DM routes are in `backend/app/api/routes/users.py` and
    `backend/app/api/routes/dms.py`.
  - DM service/demo fallback logic is in `backend/app/services/dm_service.py` and
    `backend/app/demo/store.py`.
  - DM frontend state is in `frontend/src/stores/dms.ts`.
  - DM chat UI is in `frontend/src/components/DirectMessageView.vue`.
- Stage 7.4 completed server rail parity:
  - Rail UI is in `frontend/src/components/ServerRail.vue`.
  - Safe demo rail metadata is computed in `frontend/src/App.vue`.
  - The rail exposes `@me` unread count, server unread/mention state, muted state,
    folder grouping, create-server, and discovery entry points.
- Stage 7.5 completed server sidebar and header controls:
  - `frontend/src/components/ChannelSidebar.vue` owns collapsible channel categories,
    Events entry, channel create forms, and channel row actions.
  - `frontend/src/App.vue` owns channel header controls and member-list visibility.
- Stage 7.6 completed composer and message actions:
  - `frontend/src/components/ChatView.vue` owns reply target state, message options
    menu state, composer action buttons, and the expanded composer layout.
  - Existing backend send/edit/delete routes remain unchanged and covered by backend
    API tests.
- Stage 7.7 completed voice channel UX:
  - `frontend/src/stores/guilds.ts` now prefers the selected active voice channel
    when deriving the current voice target.
  - `frontend/src/components/ChannelSidebar.vue` owns voice-channel join/leave
    affordances and displays active voice membership under voice channel rows.
  - `frontend/src/components/VoicePanel.vue` owns the bottom user identity, local
    status cycle, mute/deafen controls, settings entry, and existing WebRTC
    screen-share/quality controls.
  - `frontend/src/App.vue` orchestrates voice join/leave by channel id and mirrors
    mute/deafen state into gateway voice-state updates.
- Stage 7.8 completed the user settings shell:
  - `frontend/src/components/SettingsView.vue` owns the settings navigation and safe
    demo panels for My Account, Profiles, Privacy & Safety, Voice & Video,
    Appearance, Keybinds, and Log Out.
  - `frontend/src/stores/navigation.ts` records the pre-settings destination and
    restores it when settings closes.
  - `frontend/src/App.vue` opens settings from the bottom user panel, hides the app
    sidebars while settings is active, and reuses the existing logout reset path.
- Stage 7.9 completed server add and discovery flows:
  - `frontend/src/components/ServerAddDialog.vue` owns the unified create/join server
    modal used by the rail add path, empty workspace actions, and topbar join action.
  - `frontend/src/components/ServerDiscoveryDialog.vue` owns local demo public server
    cards plus search and can start server creation from a discovery card.
  - `frontend/src/App.vue` still routes actual mutations through existing
    `guilds.createGuild()` and `guilds.joinInvite()` API wrappers.
- Stage 7.10 completed DM persistence and realtime expansion:
  - `backend/app/db/schema.sql` and `backend/app/db/seed.py` define and seed
    PostgreSQL-backed DM profiles, relationships, DM channels, DM members, and DM
    messages.
  - `backend/app/repositories/dms.py` and `backend/app/services/dm_service.py` now
    provide the PostgreSQL/demo fallback switch for relationship and DM APIs.
  - `backend/app/gateway/manager.py`, `backend/app/gateway/router.py`,
    `backend/app/realtime/publisher.py`, and `backend/app/realtime/subscriber.py`
    support DM subscriptions plus `DM_CREATE`/`DM_MESSAGE_CREATE` dispatch.
  - `frontend/src/stores/dms.ts` applies DM gateway events and `frontend/src/App.vue`
    forwards gateway dispatches to both guild and DM stores.
- Stage 7.11 completed responsive and accessibility QA:
  - `frontend/src/styles/base.css` now hides private/channel sidebars below 900px,
    constrains mobile app/workspace width, hides the gateway status pill below 620px,
    and reduces friend-row actions to avoid right-edge clipping.
  - Desktop and mobile screenshots are stored under `docs/qa-artifacts/`.
  - QA notes and residual manual browser checks are in
    `docs/stage-7-11-responsive-qa.md`.
- Stage 7.12 completed final Discord app QA and documentation:
  - Full command verification passed: backend tests, backend lint, frontend lint, and
    frontend production build.
  - Docker Compose PostgreSQL smoke passed with backend/frontend services reachable
    through `localhost`.
  - Headless Chrome smoke passed for demo login, Friends tabs, DM messaging, server
    text/voice channel switching, settings, create/join server, and logout reset.
  - Final QA notes and residual external verification items are in
    `docs/stage-7-12-final-qa.md`.
- Stage 8 started from the user's Discord reference screenshots:
  - The controlling plan is `docs/discord-ui-remediation-plan.md`.
  - Priorities are layout/text-overlap cleanup, app-shell sizing, Korean/English
    language support, current-location and voice-state clarity, and removal or
    conversion of misleading placeholder buttons.
  - Do not copy private Discord screenshot content into code, fixtures, or docs.
- Stage 8.1 completed layout tokens and app shell sizing:
  - `frontend/src/styles/base.css` defines stable tokens for app surfaces, server
    rail, sidebars, header, member list, composer, bottom voice panel, and icon
    controls.
  - The app shell is viewport-bound with hidden global overflow; sidebars and content
    regions own their own scrolling.
  - Friends home mobile sizing was corrected so tabs/search remain within the
    workspace viewport.
  - QA screenshots are `docs/qa-artifacts/stage-8-1-desktop.png` and
    `docs/qa-artifacts/stage-8-1-mobile.png`.
- Stage 8.2 completed sidebar text overlap and channel creation cleanup:
  - `frontend/src/components/ChannelSidebar.vue` now uses stable stacked create
    panels for text and voice channel creation.
  - `frontend/src/styles/base.css` keeps channel category headings, create forms,
    channel rows, row actions, and voice member rows inside the fixed sidebar width.
  - QA created text and voice channels through the UI and captured
    `docs/qa-artifacts/stage-8-2-sidebar.png`.
- Stage 8.3 completed the Korean/English i18n foundation:
  - `frontend/src/i18n/index.ts` owns flat Korean/English dictionaries and the
    `useI18n()` helper.
  - `frontend/src/stores/preferences.ts` persists `ko`/`en` language selection in
    localStorage.
  - Auth, app shell/header, private sidebar, channel sidebar, Friends home, chat
    composer/actions, DM view, VoicePanel, gateway status label, and Settings use
    i18n for high-visibility copy.
  - Settings has a Language panel with Korean and English choices.
  - QA screenshots are `docs/qa-artifacts/stage-8-3-ko-home.png`,
    `docs/qa-artifacts/stage-8-3-en-home.png`, and
    `docs/qa-artifacts/stage-8-3-en-settings.png`.
- Stage 8.4 completed the bottom user and voice panel redesign:
  - `frontend/src/components/VoicePanel.vue` separates user identity/actions, voice
    connection summary, presence/meter/status, and screen/call controls.
  - `frontend/src/styles/base.css` now styles connected/disconnected summaries,
    speaking state, active screen share, and connected disconnect controls with fixed
    bottom-panel sizing.
  - Browser QA used fake media capture to verify connect, mute, deafen, settings
    entry, disconnect, desktop layout, and mobile layout.
  - QA screenshots are `docs/qa-artifacts/stage-8-4-voice-disconnected.png`,
    `docs/qa-artifacts/stage-8-4-voice-connected.png`, and
    `docs/qa-artifacts/stage-8-4-mobile.png`.
- Stage 8.5 completed current location and state visibility:
  - `frontend/src/App.vue` renders a destination subtitle and connected voice
    location/status pill in the topbar.
  - `frontend/src/components/ServerRail.vue`,
    `frontend/src/components/PrivateChannelSidebar.vue`, and
    `frontend/src/components/ChannelSidebar.vue` expose active selections through
    `aria-current` plus stronger selected styles.
  - `frontend/src/components/ChannelSidebar.vue` shows the connected voice channel,
    self voice row, and muted/deafened/speaking labels.
  - `frontend/src/components/VoicePanel.vue` prioritizes muted/deafened labels in the
    bottom voice status area.
  - Browser QA verified Friends, DM, server text channel, fake-media voice join, and
    mute state visibility with no horizontal overflow.
  - QA screenshot is `docs/qa-artifacts/stage-8-5-voice-state.png`.
- Stage 8.6 completed placeholder button audit and cleanup:
  - `frontend/src/App.vue` owns the shared demo-disabled notice pattern.
  - `frontend/src/components/PrivateChannelSidebar.vue` wires DM search, Nitro, Shop,
    and Quests to scoped demo notices.
  - `frontend/src/components/ChannelSidebar.vue` wires server menu and Events to
    scoped demo notices while preserving real channel and invite flows.
  - `frontend/src/components/FriendsHome.vue` turns the friend More button into a
    local profile-summary menu with a message action.
  - `frontend/src/components/ChatView.vue` turns upload, gift, apps, and emoji
    composer buttons into local demo panels until Stage 8.8 expands composer actions.
  - `frontend/src/styles/base.css` keeps workspace notices compact so they do not
    consume the main content area.
  - QA screenshot is `docs/qa-artifacts/stage-8-6-button-panels.png`.
- Stage 8.7 completed channel-header panels:
  - `frontend/src/App.vue` owns local panel state for threads, notifications, pinned
    messages, and current-channel search.
  - Notification settings support all messages, mentions only, and mute notifications
    as local session state.
  - Current-channel search filters the active in-memory messages by content or author.
  - Threads and pinned messages now show useful empty states instead of generic
    placeholder notices.
  - `frontend/src/styles/base.css` positions header panels below the topbar without
    consuming workspace layout rows.
  - QA screenshot is `docs/qa-artifacts/stage-8-7-header-panels.png`.
- Stage 8.8 completed composer action panels:
  - `frontend/src/components/ChatView.vue` now inserts local emoji into drafts,
    exposes a bounded upload metadata panel, provides poll/todo apps action
    templates, and keeps gift as an explicit demo limitation.
  - `frontend/src/components/DirectMessageView.vue` adds DM composer emoji insertion
    while preserving button-based DM send.
  - `frontend/src/styles/base.css` keeps composer panels within the input area and
    fixes the DM composer grid for input, expression action, and send controls.
  - QA screenshots are `docs/qa-artifacts/stage-8-8-composer-panels.png` and
    `docs/qa-artifacts/stage-8-8-dm-composer.png`.
- Stage 8.9 completed Friends and DM information density:
  - `frontend/src/components/FriendsHome.vue` shows friend status, relationship,
    handle, activity, selected-row state, and a wide-screen profile/activity panel.
  - `frontend/src/components/PrivateChannelSidebar.vue` shows DM presence dots,
    status/activity detail, group member counts, unread badges, and stronger selected
    state.
  - `frontend/src/components/DirectMessageView.vue` shows DM status, message count,
    participants, and participant chips in the conversation intro.
  - `frontend/src/styles/base.css` bounds Friends/DM detail layouts and hides the
    Friends profile panel at narrower breakpoints.
  - QA screenshots are `docs/qa-artifacts/stage-8-9-friends-home.png` and
    `docs/qa-artifacts/stage-8-9-friends-dm.png`.
- Stage 8.10 completed Settings reorganization:
  - `frontend/src/components/SettingsView.vue` groups Settings into Account,
    Experience, and Session sections with account/privacy, voice/video, appearance,
    accessibility, keybinds, language/time, and logout panels.
  - Voice connection state, input level, ICE readiness, language choice, and
    time-format choice are represented as real local settings panels.
  - Demo-only scope is explicit for local-only controls.
  - `frontend/src/styles/base.css` tightens settings sidebar selection, card copy,
    radio rows, toggles, and keybind rows so labels do not clip.
  - QA screenshot is `docs/qa-artifacts/stage-8-10-settings.png`.
- Stage 8.11 completed voice and screen-share workspace clarity:
  - `frontend/src/App.vue` opens a dedicated voice workspace when a voice channel is
    selected, before the user joins the call.
  - The workspace exposes selected guild/channel context, preview versus connected
    state, local and remote participant tiles, join/leave actions, and screen-share
    availability.
  - `frontend/src/components/ChannelSidebar.vue` marks selected voice channels
    separately from connected voice channels.
  - `frontend/src/components/VoicePanel.vue` uses selected-channel copy in its idle
    state so users understand the next action.
  - `frontend/src/styles/base.css` bounds the voice workspace, action buttons,
    participant tiles, and mobile layout to avoid overlap and horizontal overflow.
  - Browser QA covered in-app permission failure plus fake-media select, join,
    mute, deafen, screen-share-enabled state, leave, and no-horizontal-overflow
    checks.
  - QA screenshots are `docs/qa-artifacts/stage-8-11-voice-workspace.png` and
    `docs/qa-artifacts/stage-8-11-voice-workspace-fake-media.png`.
- Stage 8.12 completed low-frequency feature scope cleanup:
  - Scope decisions are documented in `docs/stage-8-12-feature-scope.md`.
  - `frontend/src/components/PrivateChannelSidebar.vue` replaces separate Nitro,
    Shop, and Quests rows with a single clone-scope entry.
  - `frontend/src/components/ChatView.vue` removes the gift checkout button and
    reframes external-app-style composer actions as local templates.
  - `frontend/src/components/SettingsView.vue` adds a clone-scope decisions card for
    commerce, external apps/activities, GIF search, real file transfer, and
    production notifications.
  - `frontend/src/i18n/index.ts` contains Korean/English labels for the new scope
    and local-template copy.
  - QA screenshot is `docs/qa-artifacts/stage-8-12-feature-scope.png`.
- Stage 8.13 completed responsive and accessibility QA:
  - QA notes are in `docs/stage-8-responsive-accessibility-qa.md`.
  - Desktop and mobile screenshots are
    `docs/qa-artifacts/stage-8-13-desktop.png` and
    `docs/qa-artifacts/stage-8-13-mobile.png`.
  - CDP viewport checks found no horizontal overflow at 1366 x 900 or 390 x 844.
  - `frontend/src/components/ServerRail.vue` now prevents duplicate
    `aria-current="page"` when the Direct Messages/Friends home is active.
  - Residual manual QA gap: rerun full human keyboard/screen-reader passes if modal
    or settings focus behavior changes.
- Stage 8.14 completed final Stage 8 verification:
  - Final QA notes are in `docs/stage-8-final-qa.md`.
  - Backend tests, backend lint, frontend lint, and frontend production build passed.
  - Docker Compose services were running; container-internal backend health confirmed
    PostgreSQL configured and connected.
  - Host `127.0.0.1:8000` may show native fallback health if another local backend is
    bound to loopback; use container-internal health for Docker database verification
    unless local port ownership is cleared.
  - Stage 8 browser QA artifact paths are indexed in the final QA document.

Store planning observation:

- `https://discord.com/store` was inspected through the Codex in-app browser on
  2026-06-03. The route redirected to Discord login because the in-app browser did
  not share the user's existing Discord login session.
- Store feature scope was therefore derived from route behavior plus Discord's public
  Shop/Profile support documentation. The implementation plan avoids real Discord
  assets, item names, prices, and payment processing.
- Stage 6.1 completed the cross-stack Store data contract:
  - Backend contracts are in `backend/app/schemas/store.py`.
  - Frontend contracts are in `frontend/src/types.ts`.
  - Validation coverage is in `backend/tests/test_store_schema.py`.
- Stage 6.2 completed the safe original demo catalog:
  - Catalog data and helper functions are in `backend/app/demo/store_catalog.py`.
  - Catalog integrity coverage is in `backend/tests/test_store_catalog.py`.
- Stage 6.3 completed authenticated Store read APIs:
  - Route handlers are in `backend/app/api/routes/store.py`.
  - Response assembly is in `backend/app/services/store_service.py`.
  - API coverage is in `backend/tests/test_store_api.py`.
- Stage 6.4 completed frontend Store state:
  - Store state is in `frontend/src/stores/store.ts`.
  - Store read wrappers are in `frontend/src/services/api.ts`.
  - Logout reset integration is in `frontend/src/App.vue`.
- Store UI work is deferred. Resume only after Stage 7 core Discord app parity or if
  the user explicitly asks to resume Store.

Completed Stage 2 bridge work:

- Added bearer-token protected message creation API.
- Added bearer-token protected channel creation API.
- Connected frontend message composer to the backend.
- Connected frontend text-channel creation form to the backend.
- Added Docker PostgreSQL service with persistent `postgres_data` volume.
- Added startup schema migration and idempotent seed data loading.
- Added a guild service/repository layer that uses PostgreSQL when connected and
  falls back to `demo_store` otherwise.
- Made `/api/guilds/me` bearer-token protected and connected the frontend guild load
  to the dev session token.
- Added guild membership and permission checks to channel/message mutation routes.
- Added database-backed `/api/auth/register`, `/api/auth/login`, and `/api/auth/me`.
- Added frontend login/register UI, saved-session restore, logout, and explicit Demo
  user entry.
- Added authenticated guild creation with default text/voice channels and frontend
  create-server UI.
- Added invite code creation/join APIs and frontend invite dialogs.
- Added Pinia loading/mutation/error state handling for guild operations.
- Added `schema_migrations` tracking around startup schema application.
- Added role creation plus member-role assignment/removal across backend, demo store,
  Pinia state, and the member list UI.
- Added single-guild refresh and administrator-only non-owner member removal across
  backend, demo store, Pinia state, and the member list UI.
- Added `MESSAGE_CREATE` realtime fan-out through Redis Pub/Sub when configured and a
  local gateway-manager fallback for native development.
- Added gateway channel subscriptions during Identify and frontend dispatch handling
  with message deduplication.
- Added a gateway zombie-connection reaper background task and tests for heartbeat
  timeout cleanup plus channel broadcast behavior.
- Added `CHANNEL_CREATE` and `GUILD_UPDATE` realtime dispatch for channel creation,
  invite joins, role mutations, and member removal, including server-side subscription
  synchronization and frontend state application.
- Added message update/delete REST APIs, demo-store and PostgreSQL repository support,
  `MESSAGE_UPDATE`/`MESSAGE_DELETE` realtime dispatch, Pinia state handling, and chat
  row edit/delete controls.
- Added focused PostgreSQL repository tests for message update/delete permission and
  write behavior using an isolated fake async database.
- Added focused PostgreSQL repository tests for guild creation/reads, channel
  creation permission, invite creation/join, role creation/assignment/removal, and
  member removal using an isolated fake async database.
- Added Stage 4 voice signaling scaffolding: gateway opcode 5, voice state broadcast,
  targeted offer/answer/ICE relay, frontend gateway send helpers, voice presence
  state, and VoicePanel signaling status.
- Added browser WebRTC voice implementation: ICE config API, microphone capture,
  peer-connection lifecycle, offer/answer/ICE handling, remote audio sinks, cleanup,
  and local VAD scaffold.
- Added call quality and screen-share expansion: microphone mute, input-level meter,
  screen capture, peer renegotiation for screen video tracks, remote screen preview,
  and connection-state display on screen-share tiles.
- Added WebRTC quality diagnostics and TURN readiness reporting: `/api/meta/voice`
  now exposes ICE server count and TURN status, the frontend samples browser stats,
  and the voice panel shows peer count, RTT, jitter, packet loss, and outbound
  bitrate while connected.
- Added `docs/voice-qa.md` plus deployment checklist updates for local two-browser
  smoke testing, TURN/NAT testing, and HTTPS deployment verification.
- Added deployment notes and switched backend runtime Docker image to Gunicorn with
  Uvicorn workers.
- Added `DEVELOPMENT_PROMPT.md` as the project-specific development prompt and linked
  it from `AGENTS.md` plus the required reading order.
- Added `docs/README.md` as the document index and aligned prompt, agent, project
  context, and roadmap reading-order rules.
- Added `docs/GITHUB_COLLABORATION_WORKFLOW.md` for branch, commit, push, staging,
  and verification workflow.
- Added `docs/PROMPT_COMPLIANCE.md` to map prompt policies to concrete files and
  record remaining external-only gaps.
- Added `docs/store-clone-implementation-plan.md` as the detailed Stage 6 plan for a
  Discord Store-like in-app shop.
- Added Stage 6.1 Store contracts across backend Pydantic schemas, frontend
  TypeScript types, and backend validation tests.
- Added Stage 6.2 Store seed catalog with original demo collections, cosmetics,
  bundle metadata, Orb exclusives, limited drops, and catalog integrity tests.
- Added Stage 6.3 authenticated Store read APIs for catalog and item detail payloads.
- Added Stage 6.4 frontend Store Pinia state, read API wrappers, filtering/sorting
  state, and logout reset integration.
- Added `docs/discord-app-clone-implementation-plan.md` as the current primary plan
  for cloning the Discord web app rooted at `channels/@me`.
- Added Stage 7.3 Direct Messages: authenticated relationship and DM APIs, demo-store
  DM membership checks, sanitized DM message creation, frontend DM state, friend-row
  DM creation/opening, and a functional DM chat composer.
- Added Stage 7.4 Server Rail Parity: `@me` unread badge, server unread/mention
  indicators, muted server state, demo folder grouping, add-server/discovery rail
  buttons, and browser-verified rail interactions.
- Added Stage 7.5 Server Sidebar And Header Controls: server menu and Events entries,
  collapsible text/voice categories, text/voice channel create forms, channel row
  invite/settings actions, channel header controls, member-list toggle, and
  browser-verified sidebar/header interactions.
- Added Stage 7.6 Composer And Message Actions: composer upload/gift/apps/emoji
  buttons, local reply target banner, message row reply/options menu, preserved
  edit/delete controls, and browser/backend verification for the message surface.
- Added Stage 10.0 baseline documentation for the latest FHD Discord comparison,
  Stage 10.1 visual-noise cleanup for demo/test names and stale seeded DM users, and
  Stage 10.2 global dark-shell token reset across surfaces, selected/hover states,
  focus rings, scrollbars, composer, member, and voice-panel surfaces. Stage 10.2
  browser QA confirmed token application, no horizontal body overflow at 1280 px,
  and old development-style DM names hidden from the primary shell.
- Added Stage 10.3 shell layout recomposition: the main workspace now spans the full
  content height, the voice controls are constrained to the active sidebar column,
  and browser QA verified Friends, text channel, and voice channel layouts have no
  horizontal body overflow or bottom-control overlap with the main workspace.
- Added Stage 10.4 server rail polish: active/unread markers now use a consistent
  left pill, server button hover/active states are quieter, mention badge labels are
  clamped, and add/discovery buttons read as secondary controls. Browser QA verified
  the active marker, rail width, and secondary action styling.
- Added Stage 10.5 private sidebar simplification: DM rows are compact single-line
  entries, repeated inactive fallback text is hidden, unread badges are clamped, and
  browser QA verified the sidebar stays at 300 px with no row wrapping or scope/test
  text in primary navigation.
- Added Stage 10.6 Friends home rework: friend rows now hide secondary actions until
  hover/focus/active, noisy fallback activity copy is removed, and the right panel is
  a compact activity card instead of a profile table. Browser QA verified row
  density, action visibility, no horizontal overflow, and Add Friend tab integrity.
- Added Stage 10.7 Add Friend workflow polish: the add-friend tab is now a
  single-column one-step form without discovery/activity preview clutter, with
  verified input/button spacing, disabled state, success result, and no horizontal
  overflow.
- Added Stage 10.8 server sidebar polish: channel rows are compact, category create
  buttons and channel management actions are hidden until hover/focus, and browser
  QA verified no horizontal overflow plus active/text/voice channel scan quality.
- Added Stage 10.9 header action reduction: the server header now keeps only
  notifications, pins, member list, search, and invite creation while removing
  threads, inbox, help, join-server, and logout from the primary header. Browser QA
  verified no wrapping or horizontal overflow.
- Added Stage 10.10 text timeline rebuild: server and DM message metadata now use
  locale-aware demo time labels instead of raw IDs, date dividers are formatted,
  message hover actions are compact floating toolbars, reaction buttons are compact
  structured pills, and attachment cards have stable icon/content columns. Browser
  QA verified text/DM message lists for horizontal overflow and metadata cleanup.
- Added Stage 10.11 composer rebuild: `ChatView.vue`,
  `DirectMessageView.vue`, and `frontend/src/styles/base.css` now share compact
  composer sizing, a 36 px send button, 44 px vertically centered input text, and a
  hidden-by-default template action that appears only on composer hover/focus or
  active state. Browser QA verified no horizontal overflow, no voice-panel overlap,
  and the Stage 10.11 specificity fix that reduced the optional action's default
  width to `0px`.
- Added Stage 10.12 member list simplification: `MemberList.vue`,
  `frontend/src/i18n/index.ts`, and `frontend/src/styles/base.css` now render a
  quieter localized member panel by default, hide refresh/role/member management
  inside an explicit management mode, and keep the admin toggle visible at low
  contrast. Browser QA verified the default member panel has no role controls and
  the management toggle opens role creation, refresh, and per-member controls.
- Added Stage 10.13 bottom user panel rebuild: `VoicePanel.vue` and
  `frontend/src/styles/base.css` now use a 102 px lower-left panel with a full-width
  user identity row, 28 px voice/user action buttons, a compact selected/connected
  voice card, explicit aria labels for voice actions, and hidden visible
  diagnostics. Browser QA verified no overflow, no workspace overlap, and the
  corrective split between composer send-button sizing and voice-panel button
  sizing.
- Added Stage 10.14 voice workspace rebuild: `frontend/src/App.vue` tags remote
  voice participant tiles, and `frontend/src/styles/base.css` now uses a tighter
  voice workspace header, 34 px join/screen-share buttons, lower participant tiles,
  a dashed quiet empty state, compact speaking rings, and a full-width compact
  screen-share preview row. Browser QA verified the idle voice channel workspace
  layout without triggering microphone permission.
- Added Stage 10.15 screen-share flow rework: `frontend/src/App.vue` now guards
  screen-share toggling behind an active voice connection, limits remote
  screen-share preview cards to the `voice_channel` workspace, and labels voice
  action buttons; `VoiceVideoSink.vue` no longer displays raw connection state;
  `frontend/src/styles/base.css` shrinks the remote preview PiP. Browser QA verified
  disconnected screen-share controls are disabled and no remote preview layer covers
  text-channel composer or member-list surfaces.
- Added Stage 10.16 feature visibility policy cleanup: `frontend/src/App.vue`
  removes the primary header gateway-status block, `VoicePanel.vue` removes the
  hidden lower-left voice diagnostics DOM, and `frontend/src/styles/base.css`
  removes the now-dead session/voice diagnostic selectors. Settings remains the
  place for clone scope and ICE/STUN/TURN detail. Browser QA verified no horizontal
  overflow, no visible gateway/STUN/TURN/RTT/Jitter/Nitro/Shop/Quests/smoke/debug
  terms in the primary shell, only the Friends private-nav row, and no
  `.session-state` or `.voice-presence` nodes in the app shell.
- Added Stage 10.17 responsive/accessibility QA documentation:
  `docs/stage-10-17-responsive-qa.md` records FHD, side-by-side, tablet, and mobile
  viewport measurements plus screenshot artifacts under `docs/qa-artifacts/`.
  Browser QA verified no horizontal body overflow across those widths, text-channel
  sidebar/header/chat/composer/member dimensions at 1280 px, no visible icon-only
  controls missing labels, visible focus styling, and the in-app browser limitation
  for repeated `Tab` key traversal.
- Added Stage 10.18 final QA documentation: `docs/stage-10-final-qa.md` records
  frontend build/lint, backend tests/lint, Docker service smoke, `/api/health`,
  frontend HTTP smoke, and browser QA for Friends, Add Friend, text channel, voice
  preview, and screen-share disabled state. Browser media permission returned
  `Permission denied` on voice join, so connected voice and real screen-share
  start/stop remain manual checks with microphone/screen-capture permissions.
- Added Stage 10.19 user feedback interaction polish: `FriendsHome.vue` now uses the
  All/Online/Pending/Add Friend tab order, stronger friend-row separation, and
  fixed-position more/right-click menus with outside-click and Escape dismissal;
  `PrivateChannelSidebar.vue` replaces the demo-disabled search action with a quick
  conversation switcher; `ChannelSidebar.vue` adds a server context menu and makes
  voice-channel row click attempt direct voice join; `VoicePanel.vue` hides the
  disconnected voice-room card; `App.vue` removes the disconnected voice join button
  from the voice workspace, adds closable notices, and replaces the invite-code-only
  dialog with a searchable friend invite modal. CSS updates in
  `frontend/src/styles/base.css` cover rail contrast, selected server-add state,
  menu/popover/modal layering, friend row spacing, and tighter voice workspace
  layout. Verification passed frontend build/lint plus Docker frontend rebuild and
  browser QA for menu dismissal, tab order, hidden disconnected voice card, and voice
  row direct-join attempt; microphone permission denial remains the manual connected
  media QA blocker.
- Added Stage 10.20 Discord feedback cleanup: `FriendsHome.vue` now keeps friend
  status/activity on one compact status line with taller row spacing; `ChatView.vue`
  and `DirectMessageView.vue` removed the hardcoded `OK`/`+1` reaction pills and now
  share clearer message-row borders, padding, and hover separation; `VoicePanel.vue`
  rebuilds the lower-left user/voice surface as raised cards, moves voice actions
  out of absolute overlap, and renders connected participant chips when media
  permission allows voice connection. `App.vue`, `ChannelSidebar.vue`,
  `PrivateChannelSidebar.vue`, `ServerRail.vue`, `types.ts`, `i18n/index.ts`, and
  `base.css` add target-aware app context menus, outside-click/Escape dismissal for
  transient menus/notices, cleaner one-line topbar behavior, and server-rail voice
  connection badges instead of topbar voice-location chips. Verification passed
  frontend lint/build, backend tests/lint, Docker frontend rebuild, browser QA for
  friend row density, server/DM message separation, removal of hardcoded reaction
  pills, app-level right-click menu suppression of the browser menu, outside-click
  dismissal, and Docker service refresh. In-app browser microphone permission still returned
  `Permission denied`, so connected voice participant rendering and live speaking
  rings remain manual QA in a browser session with microphone permission granted.
- Added Stage 10.21 voice-sidebar participant stack: `ChannelSidebar.vue` now keeps
  connected voice channels as a compact channel row and renders the Discord-like
  lower stack beneath it: channel status shortcut, dashed mood prompt, connected
  participant rows, and invite-to-voice action. `frontend/src/styles/base.css`
  scopes connected/speaking emphasis to the row/member surfaces instead of coloring
  the full expanded block, and `frontend/src/i18n/index.ts` localizes the new Korean
  and English labels. Frontend lint/build passed; successful connected-state visual
  QA still requires microphone permission in the browser.
- Added Stage 10.22 bottom user status card density: `frontend/src/App.vue` now tags
  the shell with `voice-connected`, and `frontend/src/styles/base.css` uses a compact
  64 px lower row for the default self status card while reserving the 128 px lower
  panel only for active voice connections. The user card now has tighter Discord-like
  elevation, spacing, and separated mic/deafen/settings controls. Frontend lint/build
  passed.
- Added Stage 10.23 voice session ownership and bottom panel alignment:
  `frontend/src/stores/guilds.ts` now tracks `connectedVoiceGuildId` and
  `connectedVoiceChannelId` separately from the selected guild/channel, while
  `frontend/src/App.vue` uses those values for server rail voice badges, channel
  sidebar connected state, mute/deafen updates, participant sync, and cross-server
  voice switching confirmation. `VoicePanel.vue` now keeps the connected voice card
  above the self status card and removes lower-left participant chips to avoid the
  clipped self/"나" artifact; participant rows remain in `ChannelSidebar.vue`.
  `base.css` aligns the self card to the composer-height pattern, narrows panel
  padding, and keeps the surrounding lower panel background matched to the sidebar.
  Frontend lint/build passed.

- Added Stage 10.24 in-app voice switch dialog and bottom edge alignment:
  `frontend/src/App.vue` replaces the cross-server voice `window.confirm` with a
  Discord-like modal that supports outside-click, Escape, close, cancel, confirm,
  and "do not ask again" behavior. `frontend/src/i18n/index.ts` adds Korean/English
  labels for the dialog, and `frontend/src/styles/base.css` styles the modal while
  aligning the lower-left self status card to the message composer top/bottom frame
  with narrower sidebar padding. Frontend lint/build, Docker frontend rebuild, and
  browser layout QA passed; the in-app browser still denied microphone permission,
  so the successful connected voice switch remains manual media-permission QA.
- Added Stage 10.25 browser-native UI audit and status-card spacing:
  `frontend/src/App.vue` now routes clipboard copy success/failure through localized
  app notices instead of silent browser-API outcomes, `frontend/src/i18n/index.ts`
  adds Korean/English copy feedback, and `frontend/src/styles/base.css` gives the
  lower-left status panel more top breathing room while preserving composer-frame
  alignment. A project search found no clone UI `alert`, `confirm`, or `prompt`
  usage outside sanitizer test payload strings. Frontend lint/build, Docker frontend
  rebuild, and browser layout QA passed.
- Added Stage 10.26 message timeline divider cleanup:
  `frontend/src/components/DirectMessageView.vue` now renders a date divider before
  DM messages, and `frontend/src/styles/base.css` removes stacked borders by
  clearing the first message row's top border and applying the thin separator only
  between adjacent message rows. The DM intro no longer draws a bottom border that
  can collide with the timeline divider. Frontend lint/build, Docker frontend
  rebuild, and browser layout QA passed for server text and DM timelines.
- Added Stage 10.27 server rail state and header seam cleanup:
  `frontend/src/components/ServerRail.vue` now scopes active server state to server
  destinations so Friends/DM views only mark Direct Messages as active, while
  inactive unread and mention states keep smaller markers. `frontend/src/styles/base.css`
  keeps voice-connected servers visually distinct from active servers and aligns
  private/server sidebar top separators with the workspace header edge. Frontend
  lint/build, Docker frontend rebuild, and browser layout QA passed for Friends and
  server surfaces.
- Added Stage 11.7 voice workspace polish: `frontend/src/styles/base.css` tightens
  the voice workspace surface, header divider, participant grid, tile elevation,
  connected-state borders, speaking card/avatar rings, and screen-share preview
  composition. Frontend lint/build, Docker frontend rebuild, and browser static QA
  passed for CSS presence and zero horizontal overflow; live microphone and
  screen-capture transitions remain manual media QA in Stage 11.12.
- Added Stage 11.8 app-owned menu/modal polish: `frontend/src/App.vue` now routes
  deferred global context-menu actions through localized app notices, centralizes
  notice close/auto-dismiss behavior, and prevents nested browser context menus
  inside the app menu. A source audit found no clone UI `alert`, `confirm`, or
  `prompt` calls outside sanitizer test payloads; frontend lint/build, Docker
  frontend rebuild, and browser static QA passed.
- Added Stage 11.9 feature exposure cleanup: `frontend/src/i18n/index.ts`,
  `frontend/src/components/ServerAddDialog.vue`,
  `frontend/src/components/ServerDiscoveryDialog.vue`, and
  `frontend/src/components/SettingsView.vue` now remove user-visible demo wording
  from primary flows while keeping common DM/server/message/voice/settings actions
  visible. `frontend/package-lock.json` updates Vite to 8.0.16 via `npm audit fix`;
  frontend audit, lint/build, Docker rebuild, and browser primary-surface text QA
  passed.
- Added Stage 11.10 backend/API completion pass: `backend/tests/test_api_routes.py`
  now covers `/api/dev/session` for local development token creation, user payload
  shape, decoded access-token claims, and production-environment hiding. Backend
  tests/lint passed, Docker services were running, and `/api/health` plus
  `/api/meta/voice` smoke checks returned the expected local values.
- Added Stage 11.11 responsive/accessibility QA: browser metrics at 1920 x 936,
  1280 x 720, 900 x 720, and 390 x 844 showed zero horizontal overflow, zero
  clipped core controls, and zero visible unnamed buttons. Frontend lint/build
  passed; visual screenshot comparison remains part of Stage 11.13.
- Added Stage 11.12 real-media QA: backend health, voice metadata, and WebSocket
  gateway HELLO smoke checks passed. Browser DOM checks found visible voice
  controls and no native JS dialogs, but automated permission-state/capture
  execution remains blocked by browser runtime permission access; `docs/voice-qa.md`
  records the required manual microphone/screen-share pass and TURN/NAT scope.
- Added Stage 11.13 final visual pass: `frontend/src/styles/base.css` now keeps
  optional composer actions out of layout until hover/focus/open state, removing a
  hidden zero-width clipped control found during server text QA. Frontend
  lint/build, Docker frontend rebuild, and browser metrics for Friends, DM, server
  text, and settings all passed with zero horizontal overflow and zero clipped core
  controls.
- Added Stage 11.14 final regression: frontend lint/build, backend tests/lint,
  full Docker rebuild, frontend high-severity audit, API/frontend HTTP smoke,
  gateway HELLO smoke, and browser regression all passed. Running services are
  `backend`, `frontend`, and `postgres`; remaining external QA is limited to
  browser-permission microphone/screen-capture checks and TURN/NAT validation in
  `docs/voice-qa.md`.
- Added architecture-principles remediation pass from
  `docs/architecture-principles-audit.md`: backend gateway internals are now split
  into `connection.py`, `subscriptions.py`, `broadcaster.py`, `voice_service.py`,
  and `zombie_reaper.py` behind the existing `GatewayConnectionManager` facade;
  `guild_service.py` now delegates PostgreSQL/demo selection to
  `guild_storage.py`; guild domain repository entry points were added for channel,
  invite, member, message, and role operations. Frontend `App.vue` now delegates
  global notices, context-menu state, invite modal state, and workspace
  title/subtitle derivation to composables. `guilds.ts` now delegates gateway
  payload validation to `guildGatewayHandlers.ts`, message REST calls to
  `channelMessages.ts`, and admin REST calls to `guildAdmin.ts`. `useVoiceRtc.ts`
  now delegates WebRTC quality-stat aggregation to `voiceStats.ts`. Verification
  passed frontend build/lint, backend lint, and full backend tests.

After each stage or meaningful feature:

- Update this file's implementation map and integration notes.
- Update `docs/implementation-plan.md` stage status.
- Update `docs/PROMPT_COMPLIANCE.md` when prompt alignment, document ownership, or
  verification policy changes.
- Run relevant verification commands.
- Commit and push to `origin/main` unless the user asks otherwise.
