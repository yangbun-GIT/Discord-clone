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

## Current Milestone

Stage 4's implementation scope is complete. Stage 1, the Docker development baseline,
Stage 2's main persistence/auth/member-management bridge, Stage 3's main text-realtime
scope, focused PostgreSQL repository coverage for current guild/message mutations,
Stage 5 deployment notes/runtime hardening, Stage 6.1 Store data contracts, Stage 6.2
Store seed catalog, Stage 6.3 Store backend read APIs, and Stage 6.4 frontend Store
state are complete and pushed to GitHub. Store UI work is now deferred. Stage 7.1
app destination state, Stage 7.2 `@me` Friends/DM shell, Stage 7.3 first-class
demo-backed Direct Messages, Stage 7.4 server rail parity, Stage 7.5 server
sidebar/header controls, and Stage 7.6 composer/message actions are complete and
pushed to GitHub.

The app boots in two local modes:

- Docker Compose mode provisions local PostgreSQL and persists created text channels
  and messages in the `postgres_data` Docker volume.
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
- `backend/app/db/seed.py`
  - Seeds the initial SRS demo guild, channels, members, and messages into PostgreSQL.
  - Uses idempotent inserts and skips guilds that already exist.
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
- `backend/app/gateway/reaper.py`
  - Background loop that periodically calls `gateway_manager.reap_zombies()` using
    the configured heartbeat interval.
- `backend/app/gateway/router.py`
  - `/gateway` WebSocket endpoint.
  - Sends Hello, accepts Identify, validates JWT, sends Ready, handles Heartbeat ACK,
    Request Guild Members, and Update Voice State placeholders.
  - On Identify, loads the authenticated user's guilds and subscribes the connection
    to every channel in those guilds.
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
    and `GUILD_UPDATE` payloads to Redis when configured.
  - Falls back to local `gateway_manager.broadcast_channel()` when Redis is absent.
  - Updates local gateway subscriptions for channel creation and guild membership
    changes before fallback broadcasts.
- `backend/app/realtime/subscriber.py`
  - Consumes Redis gateway-event Pub/Sub messages and fans them out to local WebSocket
    subscribers.
  - Updates local gateway subscriptions for channel creation and guild membership
    changes before broadcasting Redis-sourced events.
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
- `backend/app/repositories/users.py`
  - PostgreSQL repository for creating users and fetching password hashes by username.
- `backend/app/services/guild_service.py`
  - Runtime switch between PostgreSQL repositories and the process-local demo store.
  - Keeps route handlers independent from the current persistence mode.
- `backend/app/services/dm_service.py`
  - Async service boundary for Stage 7.3 DM APIs.
  - Delegates to `demo_store` for relationships, DM list/create, and DM message
    creation until Stage 7.10 introduces repository-backed persistence.
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
  - Backend startup connects PostgreSQL, runs `schema.sql`, then seeds demo data.
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

- Continue Stage 7 from `docs/discord-app-clone-implementation-plan.md` with Stage
  7.7 Voice Channel UX: active voice membership inside the sidebar, channel join/leave
  affordances, and bottom user status/mute/deafen visual state.
- Run multi-browser manual voice QA with a real TURN provider configured.
- Tune WebRTC quality with real network stats after manual QA exposes bottlenecks.
- Continue production deployment execution when target VM/provider is chosen.

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

After each stage or meaningful feature:

- Update this file's implementation map and integration notes.
- Update `docs/implementation-plan.md` stage status.
- Update `docs/PROMPT_COMPLIANCE.md` when prompt alignment, document ownership, or
  verification policy changes.
- Run relevant verification commands.
- Commit and push to `origin/main` unless the user asks otherwise.
