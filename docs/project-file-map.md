# Project File Map

Use this document as the quick path map before broad implementation work. It is
not a replacement for `PROJECT_CONTEXT.md`; it is a faster routing table for
finding the right files without repeatedly rediscovering the folder structure.

## Update Rule

Update this document whenever a change adds, removes, renames, or meaningfully
changes the responsibility of a project folder or important source file.

For ordinary implementation work:

1. Read the required startup documents.
2. Use this map to jump to the likely owner files.
3. Confirm ownership by reading the current code.
4. Update this map before committing if file ownership changed.

## Root Files

- `AGENTS.md`
  - Concise agent-facing rules.
  - Read for repository-specific engineering constraints.
- `DEVELOPMENT_PROMPT.md`
  - Project-specific development prompt.
  - Read for role, verification, documentation, security, and collaboration policy.
- `PROJECT_CONTEXT.md`
  - Current implementation map and recovery point.
  - Read before implementation to understand completed stages, integrations, and
    known residual risks.
- `README.md`
  - Setup, Docker, local development, and verification commands.
- `package.json`
  - Root npm scripts for backend lint/tests, frontend lint/build, and Docker.
- `compose.yaml`
  - Local Docker Compose stack for PostgreSQL, backend, and frontend.
- `.env.example`
  - Non-secret environment variable template.
- `.dockerignore`, `backend/.dockerignore`, `frontend/.dockerignore`
  - Docker build-context exclusions.

## Documentation

- `docs/README.md`
  - Documentation index and update rules.
- `docs/structure-map/README.md`
  - Structure-map folder index and update rules.
- `docs/structure-map/reference-map.md`
  - Core file reference and reverse-reference map.
- `docs/implementation-plan.md`
  - Long-running roadmap and stage status.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md`
  - Git staging, commit, push, and final-report workflow.
- `docs/PROMPT_COMPLIANCE.md`
  - Prompt-to-repository compliance map.
- `docs/project-file-map.md`
  - This quick file/folder ownership map.
- `docs/architecture-principles-audit.md`
  - Current SRP/OCP/DIP/encapsulation/testability gap list and refactor candidates.
- `docs/deployment.md`
  - Runtime, Docker, Redis, HTTPS/WebSocket, TURN, and deployment hardening.
- `docs/voice-qa.md`
  - Voice, screen sharing, TURN, and WebRTC QA procedure.
- `docs/reference-screenshots/`
  - Private local visual-reference screenshot folders.
  - Do not commit real screenshot content unless explicitly approved.
- `docs/qa-artifacts/`
  - Stage QA screenshots already used for verification evidence.

## Stage And Planning Documents

- `docs/discord-app-clone-implementation-plan.md`
  - Core Discord app clone roadmap.
- `docs/discord-ui-remediation-plan.md`
  - Stage 8 UI cleanup plan.
- `docs/discord-visual-parity-remediation-plan.md`
  - Stage 9 screenshot-based visual parity plan.
- `docs/discord-interaction-polish-plan.md`
  - Stage 10 interaction polish plan.
- `docs/discord-stage-11-completion-plan.md`
  - Stage 11 completion pass plan.
- `docs/stage-*-*.md`
  - Stage-specific QA, baseline, feature scope, and final verification notes.
- `docs/store-clone-implementation-plan.md`
  - Deferred Store-like shop plan.

## Backend: Entry And App Assembly

- `backend/app/main.py`
  - FastAPI app factory, lifespan startup/shutdown, CORS, rate limit middleware,
    REST router registration, WebSocket router registration.
- `backend/app/api/router.py`
  - Aggregates REST route modules under the API prefix.
- `backend/app/api/dependencies.py`
  - Bearer-token dependency and current-user extraction.

## Backend: REST Routes

- `backend/app/api/routes/auth.py`
  - Register, login, and `me` endpoints.
- `backend/app/api/routes/dev.py`
  - Local development session endpoint.
- `backend/app/api/routes/health.py`
  - Health check endpoint.
- `backend/app/api/routes/meta.py`
  - Runtime metadata endpoints such as voice config.
- `backend/app/api/routes/guilds.py`
  - Guild list/read/create, invite, roles, members, and channel creation routes.
- `backend/app/api/routes/channels.py`
  - Channel message create/update/delete routes.
- `backend/app/api/routes/dms.py`
  - Direct-message list/create/message routes.
- `backend/app/api/routes/users.py`
  - Relationship/friend-oriented user routes.
- `backend/app/api/routes/store.py`
  - Demo Store catalog and item read routes.

## Backend: Services

- `backend/app/services/auth_service.py`
  - Authentication business flow and token issuing.
- `backend/app/services/guild_service.py`
  - Guild, invite, role, member, channel, and message service facade.
  - Current refactor candidate: storage-provider branching should be extracted.
- `backend/app/services/dm_service.py`
  - Direct-message service facade.
- `backend/app/services/store_service.py`
  - Demo Store service facade.

## Backend: Repositories And Persistence

- `backend/app/db/pool.py`
  - Async PostgreSQL pool wrapper and migration runner.
- `backend/app/db/schema.sql`
  - PostgreSQL schema.
- `backend/app/db/seed.py`
  - Idempotent PostgreSQL seed data.
- `backend/app/repositories/users.py`
  - User persistence and password-hash lookup.
- `backend/app/repositories/guilds.py`
  - Guild persistence plus current channel/message/invite/role/member operations.
  - Current refactor candidate: split by domain responsibility.
- `backend/app/repositories/dms.py`
  - Direct-message persistence.

## Backend: Domain, Demo, Gateway, Realtime

- `backend/app/domain/snowflake.py`
  - JavaScript-safe Snowflake ID generator.
- `backend/app/domain/permissions.py`
  - Permission bitfields and permission checks.
- `backend/app/core/config.py`
  - Runtime settings and environment-variable parsing.
- `backend/app/core/security.py`
  - Password hashing and JWT helpers.
- `backend/app/core/sanitize.py`
  - Message-content sanitization.
- `backend/app/core/rate_limit.py`
  - Local in-memory token-bucket rate limit middleware.
- `backend/app/demo/data.py`
  - Native fallback demo data.
- `backend/app/demo/store.py`
  - Native fallback demo store behavior.
- `backend/app/demo/store_catalog.py`
  - Demo Store catalog data.
- `backend/app/gateway/router.py`
  - WebSocket gateway endpoint and payload handling.
- `backend/app/gateway/manager.py`
  - Connection registry, subscriptions, broadcast, voice state, and voice signal
    routing.
  - Current refactor candidate: split registry/broadcaster/voice/reaper concerns.
- `backend/app/gateway/events.py`
  - Gateway event naming/contracts.
- `backend/app/gateway/opcodes.py`
  - Discord-style gateway opcodes.
- `backend/app/gateway/reaper.py`
  - Gateway zombie-connection reaper loop.
- `backend/app/realtime/publisher.py`
  - Redis-backed gateway event publishing.
- `backend/app/realtime/subscriber.py`
  - Redis-backed gateway event consumption.
- `backend/app/realtime/redis_bus.py`
  - Optional Redis Pub/Sub wrapper.
- `backend/app/realtime/events.py`
  - Realtime event payload helpers.

## Backend Tests

- `backend/tests/test_api_routes.py`
  - General route behavior.
- `backend/tests/test_config.py`
  - Runtime configuration parsing.
- `backend/tests/test_demo_store.py`
  - Native demo-store fallback behavior.
- `backend/tests/test_dm_api.py`
  - DM API behavior.
- `backend/tests/test_dm_repository.py`
  - PostgreSQL DM repository behavior.
- `backend/tests/test_gateway_manager.py`
  - Gateway manager behavior.
- `backend/tests/test_guild_repository.py`
  - PostgreSQL guild/message/channel/role/member repository behavior.
- `backend/tests/test_message_schema.py`
  - Message schema validation.
- `backend/tests/test_permissions.py`
  - Permission bitfield behavior.
- `backend/tests/test_snowflake.py`
  - Snowflake ID behavior.
- `backend/tests/test_store_api.py`, `test_store_catalog.py`, `test_store_schema.py`
  - Demo Store API, catalog, and schema behavior.

## Frontend: Entry And App Shell

- `frontend/src/main.ts`
  - Vue app bootstrap, Pinia, and root component mount.
- `frontend/src/App.vue`
  - Top-level app shell and current global workflow orchestration.
  - Current refactor candidate: split workspace, notice, context-menu, voice, and
    invite controllers.
- `frontend/src/types.ts`
  - Shared frontend DTO and state types.
- `frontend/src/env.d.ts`
  - Vite TypeScript environment declarations.

## Frontend: Components

- `frontend/src/components/AuthPanel.vue`
  - Login, register, and demo-session entry.
- `frontend/src/components/ServerRail.vue`
  - Far-left server rail and server switching.
- `frontend/src/components/PrivateChannelSidebar.vue`
  - Friends/DM sidebar.
- `frontend/src/components/ChannelSidebar.vue`
  - Server heading, events, categories, text/voice channel rows, lower user/voice
    panels.
- `frontend/src/components/FriendsHome.vue`
  - Friends tabs, friend list, add-friend flow, and activity panel.
- `frontend/src/components/DirectMessageView.vue`
  - DM intro, message timeline, and composer.
- `frontend/src/components/ChatView.vue`
  - Server text-channel timeline, message actions, attachments, reactions, and
    composer.
- `frontend/src/components/MemberList.vue`
  - Server member list and role/member controls.
- `frontend/src/components/VoicePanel.vue`
  - Voice-channel workspace, participant tiles, screen-share state, and controls.
- `frontend/src/components/VoiceAudioSink.vue`
  - Remote audio stream rendering.
- `frontend/src/components/VoiceVideoSink.vue`
  - Remote video/screen stream rendering.
- `frontend/src/components/SettingsView.vue`
  - User settings shell and settings sections.
- `frontend/src/components/ServerAddDialog.vue`
  - Server create/join dialog.
- `frontend/src/components/ServerDiscoveryDialog.vue`
  - Demo server discovery dialog.

## Frontend: Stores

- `frontend/src/stores/session.ts`
  - Auth token, current user, login/register/demo/logout.
- `frontend/src/stores/navigation.ts`
  - Active destination: friends, DM, server, settings, store.
- `frontend/src/stores/guilds.ts`
  - Guild list, active guild/channel, messages, admin mutations, voice state, and
    gateway event handling.
  - Current refactor candidate: split message, admin, voice, and gateway handlers.
- `frontend/src/stores/dms.ts`
  - Direct-message state and mutations.
- `frontend/src/stores/preferences.ts`
  - User preferences such as locale/theme-like settings.
- `frontend/src/stores/store.ts`
  - Deferred/demo Store state.

## Frontend: Services, Composables, Styling

- `frontend/src/services/api.ts`
  - Fetch wrapper helpers for GET/POST/PATCH/DELETE.
- `frontend/src/composables/useGateway.ts`
  - WebSocket gateway connection, Identify, heartbeat, dispatch handling, and voice
    signal send/update helpers.
- `frontend/src/composables/useVoiceRtc.ts`
  - Browser WebRTC media capture, peer connections, VAD, screen share, and quality
    stats.
  - Current refactor candidate: split media, VAD, peers, and stats modules.
- `frontend/src/i18n/index.ts`
  - Korean/English copy dictionary and translation helper.
- `frontend/src/styles/base.css`
  - Global layout, Discord-like visual system, component surfaces, responsive rules.
- `frontend/src/utils/visualNoise.ts`
  - Helpers for filtering visual-test/demo names and messages from primary surfaces.

## Frontend Runtime And Build

- `frontend/package.json`
  - Frontend lint, typecheck/build, and Vite scripts.
- `frontend/vite.config.ts`
  - Vite config.
- `frontend/index.html`
  - HTML entry.
- `frontend/Dockerfile`
  - Frontend Docker image.
- `frontend/nginx.conf`
  - Frontend Nginx runtime config.
- `frontend/tsconfig.json`, `frontend/tsconfig.node.json`
  - TypeScript configuration.

## Common Task Routing

- Authentication or session bug:
  - Backend: `backend/app/api/routes/auth.py`, `backend/app/services/auth_service.py`,
    `backend/app/repositories/users.py`, `backend/app/core/security.py`.
  - Frontend: `frontend/src/stores/session.ts`, `frontend/src/components/AuthPanel.vue`.
- Guild/server/channel behavior:
  - Backend: `backend/app/api/routes/guilds.py`,
    `backend/app/services/guild_service.py`, `backend/app/repositories/guilds.py`.
  - Frontend: `frontend/src/stores/guilds.ts`,
    `frontend/src/components/ServerRail.vue`,
    `frontend/src/components/ChannelSidebar.vue`.
- Server text-channel messages:
  - Backend: `backend/app/api/routes/channels.py`,
    `backend/app/services/guild_service.py`, `backend/app/repositories/guilds.py`.
  - Frontend: `frontend/src/components/ChatView.vue`,
    `frontend/src/stores/guilds.ts`.
- Direct messages:
  - Backend: `backend/app/api/routes/dms.py`, `backend/app/services/dm_service.py`,
    `backend/app/repositories/dms.py`.
  - Frontend: `frontend/src/stores/dms.ts`,
    `frontend/src/components/PrivateChannelSidebar.vue`,
    `frontend/src/components/DirectMessageView.vue`.
- Realtime gateway:
  - Backend: `backend/app/gateway/*`, `backend/app/realtime/*`.
  - Frontend: `frontend/src/composables/useGateway.ts`,
    `frontend/src/stores/guilds.ts`, `frontend/src/stores/dms.ts`.
- Voice and screen sharing:
  - Backend: `backend/app/gateway/router.py`, `backend/app/gateway/manager.py`,
    `backend/app/api/routes/meta.py`, `backend/app/core/config.py`.
  - Frontend: `frontend/src/composables/useVoiceRtc.ts`,
    `frontend/src/components/VoicePanel.vue`,
    `frontend/src/components/VoiceAudioSink.vue`,
    `frontend/src/components/VoiceVideoSink.vue`,
    `frontend/src/components/ChannelSidebar.vue`.
- Visual/UI polish:
  - Primary: `frontend/src/styles/base.css`.
  - Components: `frontend/src/components/*`.
  - Copy: `frontend/src/i18n/index.ts`.
  - Reference docs: `docs/reference-screenshots/`,
    `docs/discord-interaction-polish-plan.md`, `docs/stage-11-final-qa.md`.
- Architecture or refactor planning:
  - `docs/architecture-principles-audit.md`, `PROJECT_CONTEXT.md`, this file.
- Deployment or Docker:
  - `compose.yaml`, `backend/Dockerfile`, `frontend/Dockerfile`,
    `frontend/nginx.conf`, `docs/deployment.md`, `README.md`.
- Test updates:
  - Backend tests live in `backend/tests`.
  - Frontend currently relies on lint/build and browser smoke unless a future test
    framework is added.

## Efficient Lookup Commands

Use these before broad manual browsing:

```powershell
rg --files -g '!frontend/node_modules/**' -g '!.venv/**' -g '!**/__pycache__/**'
rg -n "function_name|class_name|event_name|api_path" backend frontend docs
rg -n "Stage 11|voice|gateway|composer|invite" PROJECT_CONTEXT.md docs
```

Prefer `rg` over recursive `Get-ChildItem` or `Select-String` for code lookup.

For cross-file changes, read `docs/structure-map/reference-map.md` before expanding
search beyond the likely owner files.
