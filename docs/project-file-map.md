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
  - Setup, Docker, local/LAN development, TURN release-gate notes, and verification
    commands.
- `package.json`
  - Root npm scripts for backend lint/tests, frontend lint/build/tests, native LAN
    dev commands, HTTPS LAN frontend dev, Docker HTTP/HTTPS startup, the C8
    realtime browser smoke, the C4 Redis cross-worker realtime smoke, production
    Compose config rendering, Cloudflare tunnel frontend startup, and safe
    voice/deployment readiness checks.
- `compose.yaml`
  - Local Docker Compose stack for PostgreSQL, backend, and frontend.
- `compose.https.yaml`
  - Optional Docker Compose override for same-LAN HTTPS media testing.
  - Runs the frontend Vite dev server with `VITE_HTTPS_PFX_FILE` mounted from
    ignored local `certs/` files.
- `compose.cloudflare-tunnel.yaml`
  - Optional Cloudflare Quick Tunnel demo override.
  - Adds `frontend-tunnel`, a runtime Nginx frontend on local port `5174` that
    proxies `/api` and `/gateway` without Vite HMR.
- `compose.production.example.yaml`
  - Example single-server external QA topology.
  - Uses Caddy for public HTTPS, runtime frontend/backend containers,
    PostgreSQL, Redis, and an optional coturn profile.
  - Placeholder-only: real secrets must come from a non-committed deployment
    environment or host secret store.
- `compose.redis-smoke.yaml`
  - Optional Redis + secondary backend override for C4 multi-worker realtime smoke.
  - Normal local Docker startup remains Redis-free unless this override is included.
- `scripts/create_lan_https_cert.ps1`
  - Generates an ignored local PFX certificate plus a root-CA `.cer` trust file
    for HTTPS LAN testing from another PC.
  - Keep the PFX on the development host; copy only `lan-dev-root-ca.cer` to the
    notebook.
- `scripts/realtime_redis_smoke.py`
  - C4 two-worker smoke: connects WebSocket to the secondary backend and creates
    server/DM messages through the primary backend.
  - Does not print JWTs, message bodies, ICE candidates, TURN credentials, media
    device labels, or DM contents.
- `scripts/realtime_browser_smoke.mjs`
  - C8 two-browser smoke: creates temporary dev sessions, a shared guild/invite,
    friend relationship, and a DM, then verifies invite-DM delivery, server text,
    DM, owner/member invite permission UI, voice peer visibility, remote audio
    sink, independent mute/deafen behavior, fake screen-share paths, local
    screen-preview rendering, remote screen-video rendering, screen-share stop
    cleanup, server-channel reload retention,
    connected voice-workspace reload retention, connected-tab automatic voice
    rejoin recovery, and voice leave cleanup through the app UI.
  - Uses the official project-local Playwright devDependency from `frontend/`.
  - Does not print JWTs, message bodies, ICE candidates, TURN credentials, media
    device labels, or DM contents.
- `scripts/submission_readiness_check.mjs`
  - Local assignment submission readiness check.
  - Auto-detects the normal HTTP Docker origin or local HTTPS Docker origins and
    verifies frontend HTML, same-origin `/api/health`,
    `/api/meta/voice/readiness`, and `/gateway` HELLO.
  - Fails if Docker PostgreSQL health metadata is not configured; does not print
    tokens, credentials, message bodies, ICE candidates, or media device labels.
- `scripts/voice_readiness_check.mjs`
  - Safe operator check for `/api/meta/voice/readiness`.
  - Prints only endpoint, ICE server count, STUN readiness, and TURN readiness.
  - Does not print ICE URLs, TURN credentials, candidates, tokens, message content,
    or media device labels.
- `scripts/deployment_readiness_check.mjs`
  - Safe external deployment check.
  - Verifies HTTPS origin shape, `/api/health`, `/api/meta/voice/readiness`, and
    `/gateway` HELLO over WSS.
  - Fails when `REQUIRE_TURN=1` and TURN is not configured, without printing ICE
    URLs, TURN credentials, tokens, message content, or media device labels.
- `deploy/production.env.example`
  - Placeholder-only production environment template for the selected single-VM
    deployment.
  - Copy to `deploy/production.env` on the host, fill real values there, and keep
    that host-only file out of Git.
- `.env.example`
  - Non-secret environment variable template, including LAN CORS, HTTPS LAN
    certificate, production-domain placeholders, and STUN/TURN guidance.
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
- `docs/prompts/`
  - Task-specific prompt library.
  - Use `discord-clone-qa-test-prompt.md` for future broad/deep QA audits.
  - Use `realtime-communication-implementation-prompt.md` for future realtime,
    WebSocket, WebRTC, voice, screen-share, and cross-PC communication work.
- `docs/project-file-map.md`
  - This quick file/folder ownership map.
- `docs/architecture-principles-audit.md`
  - Current SRP/OCP/DIP/encapsulation/testability gap list and refactor candidates.
- `docs/architecture-refactor-stage-12-plan.md`
  - Stage 12 behavior-preserving architecture refactor plan and process.
- `docs/stage-12-architecture-qa.md`
  - Running Stage 12 architecture refactor verification log.
- `docs/architecture-refactor-stage-13-plan.md`
  - Stage 13 final architecture-maintenance plan and completion gate.
- `docs/frontend-css-i18n-ownership.md`
  - Future frontend CSS and i18n split ownership plan.
  - Defines safe extraction order and verification rules for `base.css` and
    `i18n/index.ts`.
- `docs/deployment.md`
  - Runtime, Docker, Redis, HTTPS/WebSocket, TURN, and deployment hardening.
- `docs/assignment-submission-guide.md`
  - Default assignment submission and demo guide.
  - Owns local Docker Compose grading flow, same-Wi-Fi HTTPS LAN checks,
    optional Cloudflare Tunnel temporary external access, feature check order,
    `npm run check:submission:local` verification, and submission limitations.
- `docs/external-deployment-decision.md`
  - Future always-on public deployment decision record.
  - Selects single VM Docker Compose with Caddy and managed TURN first, self-hosted
    coturn optional.
  - Separates user-prepared resources, Codex-actionable setup, deployment command
    flow, verification checklist, and pending external gates.
- `docs/external-deployment-runbook.md`
  - Future always-on public HTTPS/WSS deployment runbook.
  - Owns VM preparation, host-only `deploy/production.env` handling, Compose
    startup, readiness command flow, manual external QA, rollback, and current
    pending external status.
- `docs/voice-transport-architecture.md`
  - Current voice transport boundary and future SFU migration plan.
  - Defines the `VoiceTransport` contract, current P2P transport ownership,
    future LiveKit/mediasoup backend/deployment requirements, and screen-share
    quality decision criteria.
- `docs/voice-qa.md`
  - Voice, screen sharing, TURN, and WebRTC QA procedure.
- `docs/remediation-tasks/realtime-communication-plan.md`
  - Staged implementation plan for WebSocket gateway, realtime text/DM, WebRTC
    voice/screen sharing, Redis fan-out, LAN/TURN access, security, observability,
    and communication verification.
- `docs/remediation-tasks/friend-relationship-implementation-plan.md`
  - Future Friends/Add Friend development plan.
  - Documents the current UI-only add-friend gap and staged backend, frontend,
    realtime, persistence, and QA work for real friend requests, accept/reject,
    cancel, remove friend, block, and unblock.
- `docs/remediation-tasks/friends-home-remediation-2026-06-20.md`
  - Friends home usability remediation record.
  - Documents and verifies the first-screen Friends pass for actionable-only menu
    items, tab counts, Add Friend panel feedback, blocked-user access, activity
    status clarity, responsive row actions, and README Korean quick-start repair.
  - Tracks implementation-worthy Friends/private-home backlog that must not be
    treated as excluded scope: friend profile popout, friend/DM call entry,
    conversation mute, start-new-DM recipient picker, target-aware friend/DM
    context menus, incoming request feedback, bottom-anchored message timelines,
    and DM header/profile-side actions.
- `docs/remediation-tasks/friends-dm-usability-implementation-reference.md`
  - Codex-facing English implementation reference for the next Friends/DM usability
    pass.
  - Routes target files for profile popout, DM call, conversation mute,
    start-new-DM, context menus, incoming request feedback, message scroll
    anchoring, and DM header/profile actions.
  - Records the 2026-06-20 implementation pass status: profile popout, local DM
    mute, recipient picker, target-aware context routing, request notice, and
    bottom-anchored timelines are implemented; true private DM voice calling is
    still a backend follow-up.
- `docs/remediation-tasks/friends-dm-usability-checklist-ko.md`
  - Korean user-facing checklist for the Friends/DM usability backlog.
  - Explains which missing controls should be implemented and which broad features
    can remain outside the current pass.
- `docs/remediation-tasks/manual-qa-followup-2026-06-19.md`
  - Latest manual QA follow-up development plan.
  - Routes sustained speech dropout, screen-share participant composition, refresh
    rejoin, LAN secure-context, TURN readiness, Friends pending/presence, DM
    identity, invite delivery/copy state, deafen behavior, and invite permission
    browser QA work.
- `docs/remediation-tasks/manual-qa-followup-2026-06-19-ko.md`
  - Korean summary of completed M1-M10 manual QA follow-up fixes.
  - Use for quick Korean handoff of changed behavior, verification, remaining
    manual gates, and related commits.
- `docs/realtime-communication-qa.md`
  - C8 and later communication QA checklist.
  - Owns automated two-browser smoke instructions, same-PC manual QA, LAN QA,
    TURN/NAT QA, privacy guardrails, and latest communication QA result notes.
- `docs/reference-screenshots/`
  - Private local visual-reference screenshot folders.
  - Do not commit real screenshot content unless explicitly approved.
- `docs/reference-videos/`
  - Private local call/video QA reference folders.
  - `docs/reference-videos/voice-call/` keeps only `.gitkeep` in Git; recordings
    and generated analysis artifacts are ignored.
- `docs/qa-artifacts/`
  - Stage QA screenshots already used for verification evidence.
- `deploy/`
  - Deployment reference assets that are safe to commit because they contain only
    placeholders.
  - `deploy/production.env.example` is the placeholder-only environment template
    for the selected single-VM deployment. Real `deploy/*.env` files are ignored.
  - `deploy/Caddyfile.example` routes `/api` and `/gateway` to the backend and app
    routes to the frontend behind public HTTPS.
  - `deploy/coturn/turnserver.conf.example` is a placeholder-only coturn template.
    Copy it outside the repository before adding real TURN secrets.
- `docs/remediation-tasks/`
  - QA-driven defect and remediation backlogs for future implementation passes.
  - Current live QA-derived development plan:
    `discord-clone-qa-remediation-2026-06-19.md`.
  - Current Friends relationship development plan:
    `friend-relationship-implementation-plan.md`.

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

- `backend/app/api/errors.py`
  - Shared REST route exception-to-HTTP mapping helpers.
  - Used by guild, channel, and DM routes to keep route handlers focused on API
    flow and route-specific detail text.
- `backend/app/api/routes/auth.py`
  - Register, login, and `me` endpoints.
- `backend/app/api/routes/dev.py`
  - Local development session endpoint.
- `backend/app/api/routes/health.py`
  - Health check endpoint.
- `backend/app/api/routes/meta.py`
  - Runtime metadata endpoints such as voice config and safe voice readiness.
- `backend/app/api/routes/guilds.py`
  - Guild list/read/create, invite, roles, members, and channel creation routes.
- `backend/app/api/routes/channels.py`
  - Channel message create/update/delete routes.
- `backend/app/api/routes/dms.py`
  - Direct-message list/create/message routes.
- `backend/app/api/routes/users.py`
  - Relationship/friend-oriented user routes.
  - Owns relationship reads plus friend request, accept, reject, cancel, remove,
    block, and unblock endpoints.
- `backend/app/api/routes/store.py`
  - Demo Store catalog and item read routes.

## Backend: Services

- `backend/app/services/auth_service.py`
  - Authentication business flow and token issuing.
- `backend/app/services/guild_service.py`
  - Guild, invite, role, member, channel, and message service facade.
- `backend/app/services/guild_storage.py`
  - Service-facing storage provider boundary.
  - Selects PostgreSQL or demo guild storage once and exposes a common async
    interface to `guild_service.py`.
- `backend/app/services/dm_service.py`
  - Direct-message service facade.
  - Owns Friends/Add Friend relationship mutation service calls.
- `backend/app/services/dm_storage.py`
  - Service-facing DM storage provider boundary.
  - Selects PostgreSQL or demo DM storage once and exposes a common async
    interface to `dm_service.py`.
  - Provides the PostgreSQL/demo boundary for relationship mutation workflows.
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
  - Core guild aggregate list/read/create persistence and compatibility facade for
    historical broad repository calls.
- `backend/app/repositories/guild_common.py`
  - Shared guild repository helpers for aggregate reads, permission calculation,
    user upsert, role/member validation, and Snowflake IDs.
- `backend/app/repositories/guild_channels.py`,
  `guild_invites.py`, `guild_members.py`, `guild_messages.py`, `guild_roles.py`
  - Domain-specific repository entry points used by `guild_storage.py`.
  - Own channel, invite, member, message, and role SQL respectively.
- `backend/app/repositories/dms.py`
  - Direct-message persistence.
  - Owns PostgreSQL relationship reads and paired-row relationship mutation
    transitions for Add Friend, pending, friend, block, and unblock states.
- `backend/app/repositories/dm_seed.py`
  - PostgreSQL DM demo relationship/workspace seed support used by `dms.py`.

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
- `backend/app/core/operation_limits.py`
  - Local operation-level token buckets for gateway identify/heartbeat/voice and
    REST message mutation protection.
- `backend/app/demo/data.py`
  - Native fallback demo data.
- `backend/app/demo/store.py`
  - Native fallback demo store behavior.
- `backend/app/demo/store_catalog.py`
  - Demo Store catalog data.
- `backend/app/gateway/router.py`
  - WebSocket gateway endpoint and payload handling.
  - Handles presence update opcode 6 by persisting profile status and publishing
    user-targeted `PRESENCE_UPDATE` dispatches to accepted friends plus
    guild-targeted presence dispatches to shared server subscribers.
  - Relays offer/answer/ICE voice signals and screen-share state signals.
- `backend/app/gateway/manager.py`
  - Compatibility facade for gateway connection, subscription, broadcast, voice,
    and reaper operations.
  - Separates normal voice websocket disconnects, which use a short recoverable
    grace window, from heartbeat/stale disconnects, which broadcast leave
    immediately.
- `backend/app/gateway/connection.py`
  - `ClientConnection` and active WebSocket connection registry.
- `backend/app/gateway/subscriptions.py`
  - Guild/channel/DM subscription mutation helpers and voice-channel assignment.
- `backend/app/gateway/broadcaster.py`
  - Channel/guild/DM dispatch fan-out and stale connection pruning.
- `backend/app/gateway/voice_service.py`
  - Voice state broadcast, recoverable voice-disconnect grace scheduling, pending
    leave cancellation on same-user rejoin, and targeted voice signal routing.
- `backend/app/gateway/zombie_reaper.py`
  - Heartbeat timeout detection and stale websocket closure.
- `backend/app/gateway/events.py`
  - Gateway event naming/contracts, including voice signal payload validation for
    offer/answer/ICE, screen-share state messages, and presence status updates.
- `backend/app/gateway/opcodes.py`
  - Discord-style gateway opcodes.
- `backend/app/gateway/reaper.py`
  - Gateway zombie-connection reaper loop.
- `backend/app/realtime/publisher.py`
  - Redis-backed gateway event publishing with local fan-out fallback when Redis is
    absent or publish fails.
  - Publishes user-targeted relationship update/delete and presence update
    dispatches.
- `backend/app/realtime/subscriber.py`
  - Redis-backed gateway event consumption with privacy-safe startup, stop, invalid
    payload, and restart logs.
- `backend/app/realtime/fanout.py`
  - Shared realtime gateway-event fan-out and local subscription synchronization.
  - Used by publisher native fallback and Redis subscriber dispatch.
- `backend/app/realtime/redis_bus.py`
  - Optional Redis Pub/Sub wrapper.
- `backend/app/realtime/events.py`
  - Realtime event payload helpers.
  - Supports channel, guild, DM, and user-targeted gateway-event envelopes.

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
- `backend/tests/test_dm_seed.py`
  - PostgreSQL DM demo workspace seed safety, including self-relationship
    prevention for seeded profile users.
- `backend/tests/test_dm_storage.py`
  - DM storage provider selection behavior.
- `backend/tests/test_gateway_manager.py`
  - Gateway manager behavior.
- `backend/tests/test_gateway_routes.py`
  - Gateway WebSocket route close-code, authentication, authorization, rate-limit,
    voice-state, and voice-signal validation behavior.
- `backend/tests/test_realtime_fanout.py`
  - Shared realtime fan-out, local subscription synchronization, Redis publish
    fallback, and subscriber payload decoding behavior.
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
  - Top-level app shell and remaining global workflow orchestration.
  - Delegates global notices, app context menus, invite modal state, and workspace
    title/subtitle calculation to focused composables.
  - Restores the last per-user DM/server/voice workspace location during app
    bootstrap before guild and DM state reconciliation.
  - Triggers automatic voice rejoin when the refreshed gateway reaches connected
    state and keeps app-owned retry/leave recovery actions visible if media capture
    fails.
  - Owns the selected voice workspace's local/remote screen-share stage placement.
  - Routes voice-panel setting actions directly into the Voice & Video settings
    panel while keeping generic settings entry on My Account.
  - Filters global context-menu invite actions through `guilds.canCreateInvite`.
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
  - Emits start-new-DM actions to `App.vue`; DM rows carry target IDs for
    context-menu routing.
- `frontend/src/components/CreateDmDialog.vue`
  - App-owned accepted-friend recipient picker for starting 1:1 or group DMs.
- `frontend/src/components/ChannelSidebar.vue`
  - Server heading, events, categories, text/voice channel rows, lower user/voice
    panels, and permission-aware server invite menu entry.
- `frontend/src/components/FriendsHome.vue`
  - Friends tabs, friend list, grouped incoming/outgoing friend requests,
    add-friend flow, and activity panel.
  - Emits real Add Friend, pending accept/reject/cancel, remove, block, and unblock
    actions instead of local-only UI results.
  - Shows relationship tab counts, query-aware empty states, Add Friend panel
    feedback from workspace notice/error state, blocked-user access when needed,
    and a stable grouped friend-row action cluster.
- `frontend/src/components/FriendProfileDialog.vue`
  - App-owned friend profile popout for username, handle, presence, relationship,
    message, call-entry, and mute actions.
- `frontend/src/components/DirectMessageView.vue`
  - DM intro, bottom-anchored message timeline, selected-DM actions, composer,
    and local emoji panel dismissal.
- `frontend/src/components/ChatView.vue`
  - Server text-channel bottom-anchored timeline, message actions/options,
    attachments, reactions, composer panels, and outside-click/Escape dismissal
    for local overlays.
- `frontend/src/components/MemberList.vue`
  - Server member list and role/member controls.
- `frontend/src/components/VoicePanel.vue`
  - Voice-channel workspace, participant tiles, screen-share state, bottom user
    controls, and quick input/output device popovers.
  - Keeps manual microphone mute available while deafened so mute and deafen remain
    independent.
  - Quick microphone popovers show configured device/sensitivity settings only; do
    not expose exact live microphone input level outside the settings screen.
  - Its quick setting actions open the Voice & Video settings panel directly.
  - Closes quick input/output popovers on outside click or Escape and orders the
    connected voice-session card below the user status card.
- `frontend/src/components/VoiceAudioSink.vue`
  - Remote audio stream rendering, output volume, output device sink selection when
    supported, and local deafen-to-audio-muted binding.
- `frontend/src/components/VoiceVideoSink.vue`
  - Local and remote video/screen stream rendering.
- `frontend/src/components/SettingsView.vue`
  - User settings shell and settings sections, including Voice & Video device,
    volume, sensitivity, live input-level meter, and native audio-processing
    controls.
  - Accepts an initial panel from `App.vue` so voice controls can land directly on
    Voice & Video instead of My Account.
- `frontend/src/components/ServerAddDialog.vue`
  - Server create/join dialog.
- `frontend/src/components/ServerDiscoveryDialog.vue`
  - Demo server discovery dialog.

## Frontend: Stores

- `frontend/src/stores/session.ts`
  - Auth token, current user, login/register/demo/logout.
- `frontend/src/stores/navigation.ts`
  - Active destination: friends, DM, server, voice, and settings.
  - Persists the last per-user restorable workspace location through
    `browserStorage` so refresh returns to the previous DM/server/voice page.
- `frontend/src/stores/guilds.ts`
  - Guild list, active guild/channel, local message state, admin state reflection,
    guild member presence updates, and gateway state application.
- `frontend/src/stores/guildVisibility.ts`
  - Guild/channel/message visibility filtering for visual-test/demo noise.
- `frontend/src/stores/voicePresence.ts`
  - Connected voice guild/channel state, voice-state collections, latest voice
    signal, and voice-channel derived state used by `guilds.ts`.
- `frontend/src/stores/channelMessages.ts`
  - Server text-channel message REST mutations.
- `frontend/src/stores/guildAdmin.ts`
  - Guild invite, channel, role, and member REST mutations.
- `frontend/src/stores/guildGatewayHandlers.ts`
  - Typed gateway-event validation and event-to-store callback dispatch.
- `frontend/src/stores/dms.ts`
  - Public Direct Message Pinia facade and state.
  - Owns relationship mutation actions and idempotent relationship update/delete
    state application, relationship identity sync into matching DM rows, and
    current-user DM identity normalization for REST/gateway payloads.
  - Suppresses inactive unread increments for locally muted DMs while still
    applying realtime message delivery.
  - Applies lightweight `PRESENCE_UPDATE` gateway dispatches to relationship rows
    only; DM sidebar rows and DM intro surfaces do not repaint status/activity.
- `frontend/src/stores/dmApi.ts`
  - Direct-message REST loaders and mutations used by `dms.ts`.
  - Wraps relationship mutation REST calls for Add Friend, pending, friend, block,
    and unblock workflows.
- `frontend/src/stores/dmGatewayHandlers.ts`
  - Direct-message gateway event validation and state callback dispatch.
  - Handles relationship update/delete and presence update gateway events.
- `frontend/src/stores/dmVisibility.ts`
  - Direct-message relationship/participant/message visibility filtering.
- `frontend/src/stores/preferences.ts`
  - User preferences such as locale/theme-like settings and locally muted DM IDs.
- `frontend/src/stores/store.ts`
  - Deferred/demo Store state.

## Frontend: Services, Composables, Styling

- `frontend/src/services/api.ts`
  - Fetch wrapper helpers for GET/POST/PATCH/DELETE.
- `frontend/src/services/browserApi.ts`
  - Browser API adapter helpers for storage, clipboard, document listeners,
    viewport/location reads, gateway URL construction, navigator platform, and
    view transitions.
- `frontend/src/composables/useGateway.ts`
  - WebSocket gateway connection, Identify, heartbeat, dispatch handling, and voice
    signal plus presence send/update helpers.
- `frontend/src/composables/useVoiceRtc.ts`
  - Public WebRTC voice facade used by the app.
  - Composes media capture, input processing, VAD, peer registry, screen share,
    output device settings, and stats modules.
  - Exposes explicit local microphone mute state/setter plus voice device setting
    state/update/refresh helpers for voice controls.
- `frontend/src/composables/voiceTransport.ts`
  - Voice transport contract used to keep the current P2P implementation
    replaceable by a future SFU-backed implementation.
  - Exposes the current `p2p-webrtc` transport kind, shared connect options, state
    shape, and operation signatures for join media, mute, screen share,
    participant sync, signal handling, device refresh, and quality stats.
- `frontend/src/composables/voiceMedia.ts`
  - Browser microphone/display capture helpers, native audio constraint support
  detection/storage, voice device preference storage, typed media error
    normalization, Web Audio input processing, and media-track helpers.
  - Persists local voice-processing preferences and builds microphone constraints
    from browser support plus user-selected echo/noise/gain settings.
  - Defaults the speech-stability path to minimal browser auto-processing for
    sustained input stability, and migrates default RNNoise/gate settings off so
    noise reduction and sensitivity gating remain explicit user choices.
  - Owns optional denoiser loading before WebRTC peer tracks are created: off
    baseline and RNNoise through `@sapphi-red/web-noise-suppressor`.
  - Owns microphone input volume, RMS-based input-level sampling from the pre-gate
    microphone path, optional soft input sensitivity/noise gate behavior, and input
    device selection helpers used before WebRTC peer tracks are created.
- `frontend/src/composables/voiceMedia.test.ts`
  - Unit coverage for typed microphone/screen media error normalization and
    voice-processing/device-setting constraint generation plus RMS input-level
    helper behavior.
- `frontend/src/composables/voiceVad.ts`
  - Local AudioContext/analyser voice activity detection for speaking state.
  - Can update input-level refs for legacy callers, but `useVoiceRtc.ts` now uses
    the processed `voiceMedia.ts` RMS sampler for the public voice meter.
- `frontend/src/composables/voicePeerConnections.ts`
  - Channel-scoped peer connection registry, offer/answer/ICE handling, pending
    candidate queueing, stale-signal filtering, remote stream tracking,
    participant sync, remote received-audio speaking detection, screen-share state
    signaling, retry, and peer renegotiation.
- `frontend/src/composables/voiceStats.ts`
  - WebRTC stats collection and quality aggregation used by `useVoiceRtc.ts`;
    consumes channel-scoped peer registry entries.
- `frontend/src/composables/useGlobalNotice.ts`
  - App notice state, timeout, and dismissal behavior.
- `frontend/src/composables/useContextMenuController.ts`
  - App-owned context menu state.
- `frontend/src/composables/useInviteController.ts`
  - Invite modal state, search query, bottom copy state, per-friend delivery state,
    and filtered invite targets.
- `frontend/src/composables/useWorkspaceController.ts`
  - Workspace title/subtitle and voice-location derived state.
- `frontend/src/composables/useVoiceSessionController.ts`
  - Voice session orchestration facade.
  - Owns voice config loading, join/leave/switch flow, mute/deafen gateway sync,
    safe reload rejoin recovery metadata, gateway-ready automatic rejoin after
    refresh, screen-share toggling, and voice participant/signal synchronization
    while composing the guild store, gateway composable, and WebRTC facade.
- `frontend/src/i18n/index.ts`
  - Korean/English copy dictionary and translation helper.
  - Keep as the public i18n facade until the split plan in
    `docs/frontend-css-i18n-ownership.md` is implemented.
- `frontend/src/styles/base.css`
  - Global layout, Discord-like visual system, component surfaces, responsive rules.
  - Keep as the current visual baseline until the split plan in
    `docs/frontend-css-i18n-ownership.md` is implemented.
- `frontend/src/utils/visualNoise.ts`
  - Helpers for filtering visual-test/demo names and messages from primary surfaces.

## Frontend Runtime And Build

- `frontend/package.json`
  - Frontend lint, typecheck/build, unit test, localhost Vite dev, LAN-bound Vite
    dev scripts, HTTPS LAN dev script, and the official Playwright devDependency
    used by the root realtime browser smoke.
- `frontend/vite.config.ts`
  - Vite config, backend/gateway dev proxy config, and optional HTTPS LAN certificate loading through
    `VITE_HTTPS_KEY_FILE` and `VITE_HTTPS_CERT_FILE`.
- `frontend/scripts/ensureHttpsCertEnv.mjs`
  - Validates local HTTPS LAN certificate environment variables before running the
    Vite HTTPS LAN dev server.
- `frontend/index.html`
  - HTML entry.
- `frontend/Dockerfile`
  - Frontend Docker image.
- `frontend/nginx.conf`
  - Frontend Nginx runtime config.
- `frontend/tsconfig.json`, `frontend/tsconfig.node.json`
  - TypeScript configuration.

## Frontend Tests

- `frontend/src/stores/dmGatewayHandlers.test.ts`
  - Direct-message gateway payload validation and dispatch behavior.
- `frontend/src/stores/dmVisibility.test.ts`
  - Direct-message relationship, participant, DM, and message visibility policy.
- `frontend/src/stores/guildVisibility.test.ts`
  - Guild, channel, and server-message visibility policy.
- `frontend/src/stores/gatewayIdempotency.test.ts`
  - Server-message, DM-message, voice-state, voice-state snapshot, and guild-update
    gateway dispatch idempotency for REST/gateway reconciliation races.

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
    `backend/app/repositories/dms.py`, `backend/app/repositories/dm_seed.py`.
  - Frontend: `frontend/src/stores/dms.ts`,
    `frontend/src/stores/dmApi.ts`,
    `frontend/src/stores/dmGatewayHandlers.ts`,
    `frontend/src/stores/dmVisibility.ts`,
    `frontend/src/components/PrivateChannelSidebar.vue`,
    `frontend/src/components/CreateDmDialog.vue`,
    `frontend/src/components/FriendProfileDialog.vue`,
    `frontend/src/components/DirectMessageView.vue`.
- Realtime gateway:
  - Backend: `backend/app/gateway/*`, `backend/app/realtime/*`.
  - Frontend: `frontend/src/composables/useGateway.ts`,
    `frontend/src/stores/guilds.ts`, `frontend/src/stores/dms.ts`.
- Voice and screen sharing:
  - Backend: `backend/app/gateway/router.py`, `backend/app/gateway/manager.py`,
    `backend/app/gateway/voice_service.py`, `backend/app/api/routes/meta.py`,
    `backend/app/core/config.py`.
  - Frontend: `frontend/src/composables/useVoiceRtc.ts`,
    `frontend/src/composables/voiceMedia.ts`,
    `frontend/src/composables/voicePeerConnections.ts`,
    `frontend/src/stores/voicePresence.ts`,
    `frontend/src/components/VoicePanel.vue`,
    `frontend/src/components/SettingsView.vue`,
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
  - `compose.yaml`, `compose.https.yaml`, `compose.cloudflare-tunnel.yaml`,
    `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`,
    `compose.production.example.yaml`,
    `deploy/Caddyfile.example`, `deploy/coturn/turnserver.conf.example`,
    `scripts/deployment_readiness_check.mjs`,
    `scripts/submission_readiness_check.mjs`, `docs/deployment.md`,
    `docs/assignment-submission-guide.md`,
    `docs/external-deployment-decision.md`, `README.md`.
- Test updates:
  - Backend tests live in `backend/tests`.
  - Frontend unit tests live beside owner modules, for example
    `frontend/src/composables/voiceMedia.test.ts`, and run through
    `npm --prefix frontend run test`.

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
