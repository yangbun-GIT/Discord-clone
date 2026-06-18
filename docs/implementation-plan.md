# Implementation Plan

## Stage 1: Foundation

- Status: completed.
- Create a FastAPI backend that boots without external infrastructure.
- Add async database and Redis boundaries for Neon and Upstash integration.
- Implement Snowflake ID generation, permission bitfields, JWT helpers, rate limiting,
  gateway opcodes, and WebSocket connection management.
- Create a Vue 3 + Vite frontend app shell that resembles the Discord workspace flow.
- Add local development scripts, environment examples, and tests.

## Documentation Maintenance

- Future work must start by reading `DEVELOPMENT_PROMPT.md`, `AGENTS.md`,
  `PROJECT_CONTEXT.md`, this plan, `README.md`, and `docs/README.md`.
- Meaningful implementation changes must update `PROJECT_CONTEXT.md`.
- Prompt alignment, document ownership, or verification policy changes must update
  `docs/PROMPT_COMPLIANCE.md`.
- Stage progress changes must update this file.
- Completed stages should be committed and pushed to `origin/main`.

## Stage 1.5: Docker Development Baseline

- Status: completed.
- Add backend and frontend Dockerfiles with development and runtime targets.
- Add Compose stack for local backend/frontend orchestration.
- Keep Docker optional so native `.venv` and `npm` workflows remain available.
- Configure Vite proxy target through `VITE_BACKEND_PROXY_TARGET` for container
  networking.

## Stage 2: Persistence and Auth

- Status: completed for the current SRS scope.
- Bridge completed: protected message creation and channel creation APIs are wired to
  the frontend through the process-local demo store.
- Persistence bridge completed: Docker Compose provisions local PostgreSQL, backend
  startup runs the initial schema, and demo guild data is seeded idempotently.
- Guild membership reads, channel creation, and message creation now use an asyncpg
  repository when a database is connected, with demo-store fallback for native local
  runs without `DATABASE_URL`.
- `/api/guilds/me` is bearer-token protected, and the frontend guild load uses the
  dev session token.
- Channel/message mutation routes now check guild membership and permission bitfields
  before writing.
- Database-backed `/api/auth/register`, `/api/auth/login`, and `/api/auth/me` are
  implemented with bcrypt password hashing and JWT responses.
- The frontend now shows login/register UI when logged out, restores saved sessions,
  supports logout, and keeps Demo user as an explicit local-development action.
- Authenticated guild creation is implemented with default `general` and `voice-room`
  channels, including frontend create-server UI.
- Invite code creation and invite join flows are implemented across backend and
  frontend so users can join each other's guilds.
- Guild Pinia state now tracks loading, mutation, and API error state for real API
  calls.
- Startup schema application now records `schema_migrations`.
- Role creation and member-role assignment/removal now use the PostgreSQL repository
  when connected, the demo store otherwise, and the frontend member list exposes
  administrator-only controls.
- Single-guild refresh and administrator-only non-owner member removal are implemented
  across the backend, demo store, Pinia state, and member list UI.
- Focused repository tests now cover PostgreSQL-backed guild creation/reads, channel
  creation permission, invite creation/join, role creation/assignment/removal, member
  removal, and message update/delete behavior through an isolated fake async database.

## Stage 3: Realtime Messaging

- Status: main text-realtime scope completed.
- Persist messages through the REST/gateway boundary.
- First slice completed: persisted REST message creation now publishes
  `MESSAGE_CREATE` to Redis Pub/Sub when configured, or directly to the local gateway
  manager in native fallback mode.
- First slice completed: gateway Identify subscribes the connection to the
  authenticated user's channels, and frontend gateway dispatches append unseen
  messages by ID.
- Heartbeat zombie-connection reaping now runs from lifespan startup and is covered by
  gateway manager tests.
- Channel creation now dispatches `CHANNEL_CREATE` and updates gateway channel
  subscriptions for guild subscribers.
- Invite join, role mutations, and member removal now dispatch `GUILD_UPDATE`, sync
  server-side gateway subscriptions, and replace frontend guild snapshots.
- Message update/delete APIs now validate sanitized content and author or
  `MANAGE_MESSAGES` permission, persist through PostgreSQL or demo-store fallback,
  dispatch `MESSAGE_UPDATE`/`MESSAGE_DELETE`, and update the frontend chat state.
- Focused repository tests now cover PostgreSQL-backed message update/delete
  permission and write behavior through an isolated fake async database.
- Focused repository tests now cover PostgreSQL-backed guild/role/member mutations.

## Stage 4: Voice Signaling

- Status: implementation and local QA support completed; external TURN-backed
  multi-network manual QA remains.
- Add WebRTC signaling events for offers, answers, ICE candidates, and voice state.
- First slice completed: gateway opcode 4 now broadcasts validated
  `VOICE_STATE_UPDATE` events to voice-channel subscribers.
- First slice completed: gateway opcode 5 now routes `offer`, `answer`, and `ice`
  payloads to the target user when both peers are in the same voice channel.
- First slice completed: frontend VoicePanel sends voice state updates, shows gateway
  signaling readiness, and tracks voice presence/signaling state in Pinia.
- WebRTC implementation completed: frontend obtains microphone audio through
  `getUserMedia`, creates `RTCPeerConnection` instances per remote voice participant,
  exchanges offer/answer/ICE through gateway opcode 5, renders remote audio through
  hidden audio sinks, and cleans up tracks/connections on disconnect.
- ICE server config is exposed by `/api/meta/voice` from `WEBRTC_ICE_SERVERS_JSON`.
- VAD scaffold completed: local microphone frequency sampling feeds a speaking flag
  in the voice panel.
- Call quality controls completed: microphone mute toggles local audio tracks and the
  voice panel shows an input-level meter.
- Screen sharing completed: frontend captures display video with `getDisplayMedia`,
  adds/removes screen video senders on active peers, renegotiates offers, and renders
  remote screen-share video tiles with connection state.
- Quality diagnostics completed: frontend samples `RTCPeerConnection.getStats()` and
  displays connected peer count, RTT, inbound audio jitter, packet loss, outbound
  audio bitrate, and outbound screen-share bitrate in the voice panel.
- TURN readiness completed: `/api/meta/voice` returns ICE server count plus
  `turn_configured`, and the frontend displays whether the current setup is TURN
  ready or STUN only.
- Voice QA documentation completed in `docs/voice-qa.md`.
- Remaining external manual QA: configure a real TURN provider such as Open Relay or
  Metered Video and verify two browsers across deployed/NAT networks.

## Stage 5: Deployment

- Status: implementation notes and verification checklist completed; actual VM rollout
  remains external.
- Dockerfile baseline is complete.
- Backend runtime image now starts Gunicorn with Uvicorn workers.
- `docs/deployment.md` documents Oracle Cloud / GCP VM deployment flow, production
  environment variables, HTTPS/WebSocket requirements, CORS, logging, health checks,
  Redis, WebRTC TURN guidance, and voice verification using browser WebRTC stats.

## Stage 6: Discord Store-Like Shop

- Status: deferred after early infrastructure work. Store scope/data contracts, seed
  catalog, backend read APIs, and frontend Store state are complete, but Store is no
  longer the primary product direction.
- Plan document: `docs/store-clone-implementation-plan.md`.
- Target: add an in-app Store tab inspired by Discord's Store, using original demo
  cosmetics and no real payment processing.
- Store contracts completed: backend Pydantic schemas in `backend/app/schemas/store.py`
  and frontend TypeScript types in `frontend/src/types.ts` define item types,
  ownership states, price metadata, catalog/detail/inventory responses, and
  purchase/gift/equip request-response shapes.
- Seed catalog completed: `backend/app/demo/store_catalog.py` defines original demo
  collections and cosmetics with safe visual metadata, minimum item counts for each
  planned Store category, bundles, Orb exclusives, and limited drops.
- Backend read APIs completed: authenticated `GET /api/store/catalog` and
  `GET /api/store/items/{item_id}` return catalog metadata, default ownership states,
  featured items, filter metadata, item details, bundle contents, and related items.
- Frontend Store state completed: `frontend/src/stores/store.ts` isolates Store
  catalog/detail/inventory references, loading state, active tab, search, filters,
  sort state, and logout reset behavior from guild/chat state.
- Current decision: the project target is the core Discord web app experience rooted
  at `https://discord.com/channels/@me`; continue with Stage 7 before resuming Store
  UI work.
- Scope includes Store entry, catalog, featured collections, Browse tab, search,
  sort, filters, item cards, item detail preview, demo purchase, inventory, apply,
  bundles, gifting, Orbs exclusives, Nitro-like discounts, profile integration,
  PostgreSQL persistence, accessibility, responsive QA, and final documentation.
- Current observation: `https://discord.com/store` is login-gated. Codex's in-app
  browser did not share the user's Discord login session and was redirected to
  `https://discord.com/login?redirect_to=%2Fstore`; public Discord Shop/Profile docs
  were used for feature structure.

## Stage 7: Discord App Parity

- Status: completed through Stage 7.12 final QA; app destination model, `@me`
  private sidebar, Friends home, first-class demo-backed Direct Messages, server rail
  parity, server sidebar/header controls, composer/message actions, voice channel UX,
  user settings shell, server add/discovery flows, DM persistence/realtime expansion,
  responsive/accessibility QA, and final documentation are complete.
- Plan document: `docs/discord-app-clone-implementation-plan.md`.
- Target: clone the actual Discord web app rooted at `https://discord.com/channels/@me`,
  not a Store-first surface.
- Observed scope includes `@me` Friends/DM home, private-channel sidebar, server rail,
  server/channel sidebar, text and voice channels, channel header controls, message
  composer actions, user status/settings panel, add/join/discovery flows, settings,
  realtime DM expansion, persistence, responsive QA, and documentation.
- Privacy note: real Discord personal names, message contents, and private server
  content observed during browser inspection must not be copied into repository data.
- Completed first slice:
  - `frontend/src/stores/navigation.ts` tracks app destinations.
  - `frontend/src/components/PrivateChannelSidebar.vue` renders the `@me` sidebar.
  - `frontend/src/components/FriendsHome.vue` renders the Friends home tabs and demo
    friend rows.
  - `frontend/src/App.vue` opens Friends by default after login and preserves current
    server/channel behavior when selecting a server.
- Completed Stage 7.3 Direct Messages:
  - Authenticated `/api/users/me/relationships`, `/api/dms`, and DM message APIs are
    implemented with demo-store fallback data.
  - `frontend/src/stores/dms.ts` loads relationships/DMs, creates DM threads, and
    sends DM messages.
  - `frontend/src/components/DirectMessageView.vue` renders DM history and composer
    inside the `dm` destination.
- Completed Stage 7.4 Server Rail Parity:
  - `frontend/src/components/ServerRail.vue` now shows `@me` unread count, server
    unread/mention indicators, muted state, a demo folder grouping, and distinct add
    server/discovery buttons with accessible labels.
  - `frontend/src/App.vue` computes safe demo rail metadata and opens a wired
    discovery entry placeholder ahead of Stage 7.9.
- Completed Stage 7.5 Server Sidebar And Header Controls:
  - `frontend/src/components/ChannelSidebar.vue` now includes a server menu entry,
    Events entry, collapsible text/voice categories, text and voice channel create
    forms, invite actions, and settings placeholders.
  - `frontend/src/App.vue` now renders channel header controls for threads,
    notifications, pinned messages, member list toggle, search, inbox, and help.
  - Member list visibility can be toggled without leaving the active channel.
- Completed Stage 7.6 Composer And Message Actions:
  - `frontend/src/components/ChatView.vue` now exposes upload, gift, apps/actions,
    emoji, reply, and message options controls around the existing send/edit/delete
    REST behavior.
  - The composer supports a local reply target banner, and message rows expose a
    compact options menu with reply/edit/delete actions.
- Completed Stage 7.7 Voice Channel UX:
  - `frontend/src/components/ChannelSidebar.vue` now shows voice channel membership
    rows and join/leave affordances for voice channels.
  - `frontend/src/components/VoicePanel.vue` now includes the bottom user identity,
    status cycle, mute/deafen controls, settings entry, and existing WebRTC
    screen-share/quality controls.
  - `frontend/src/App.vue` connects voice join/leave by channel id and keeps mute and
    deafen state reflected through gateway voice-state updates.
- Completed Stage 7.8 User Settings Shell:
  - `frontend/src/components/SettingsView.vue` renders account, profile, privacy,
    voice, appearance, keybind, and logout settings panels.
  - `frontend/src/stores/navigation.ts` records the previous app destination before
    opening settings and restores it on close.
  - `frontend/src/App.vue` opens settings from the bottom user panel and reuses the
    existing logout path from the settings logout panel.
- Completed Stage 7.9 Server Discovery And Add Server:
  - `frontend/src/components/ServerAddDialog.vue` provides a unified create/join
    server path from the rail, empty workspace, and topbar join action.
  - `frontend/src/components/ServerDiscoveryDialog.vue` provides local demo public
    server cards and search without external network dependency.
  - Existing backend guild create and invite join APIs remain the mutation boundary.
- Completed Stage 7.10 Persistence And Realtime Expansion:
  - `backend/app/db/schema.sql` and `backend/app/db/seed.py` now include
    PostgreSQL-backed DM profiles, relationships, DM channels, DM members, and DM
    messages.
  - `backend/app/repositories/dms.py` provides PostgreSQL relationship/DM reads, DM
    creation, DM message creation, membership checks, and unread count updates while
    `backend/app/services/dm_service.py` preserves the demo fallback switch.
  - Gateway/realtime publishing now supports `DM_CREATE` and `DM_MESSAGE_CREATE`
    dispatches to DM subscribers.
  - `frontend/src/stores/dms.ts` applies DM gateway dispatches alongside the existing
    REST send/create paths.
- Completed Stage 7.11 Responsive And Accessibility QA:
  - Mobile CSS now hides sidebars, constrains app/workspace width, hides the gateway
    pill, and reduces friend-row actions to avoid clipping below 620px.
  - Desktop/mobile screenshots and DOM overflow metrics are recorded in
    `docs/stage-7-11-responsive-qa.md`.
- Completed Stage 7.12 Final Discord App QA And Documentation:
  - Full backend test, backend lint, frontend lint, and frontend build verification
    passed.
  - Docker Compose PostgreSQL smoke and headless Chrome app workflow smoke passed.
  - Final QA notes are recorded in `docs/stage-7-12-final-qa.md`.

## Stage 8: Discord UI Remediation And Interaction Polish

- Status: completed through Stage 8.14 final QA.
- Plan document: `docs/discord-ui-remediation-plan.md`.
- Target: fix the post-Stage 7 UI quality gaps identified from the user's Discord
  reference screenshots: bottom controls, text overlap, sizing, Korean/English
  support, location/status clarity, and visible buttons that do not work.
- Privacy note: reference screenshots may contain private Discord names, messages,
  avatars, and server content. Use only layout and interaction structure; do not copy
  private content into repository data or documentation.
- Stage execution rule: complete each Stage 8 sub-stage with verification, fix any
  discovered sub-issues before moving on, update docs, commit, and push to
  `origin/main`.
- Completed Stage 8.0: `docs/discord-ui-remediation-plan.md` is the controlling
  Stage 8 plan and is linked from project docs.
- Completed Stage 8.1: `frontend/src/styles/base.css` defines stable app-shell
  sizing tokens and viewport-bound layout rules; desktop/mobile screenshots are in
  `docs/qa-artifacts/stage-8-1-desktop.png` and
  `docs/qa-artifacts/stage-8-1-mobile.png`.
- Completed Stage 8.2: `frontend/src/components/ChannelSidebar.vue` renders channel
  creation as stable stacked panels, and sidebar CSS keeps category labels, generated
  channel rows, row actions, and voice members within the fixed sidebar width.
- Completed Stage 8.3: `frontend/src/i18n/index.ts` and
  `frontend/src/stores/preferences.ts` provide Korean/English UI language switching
  with localStorage persistence; key app shell, sidebar, friends, chat, voice, and
  settings copy is wired to the i18n helper.
- Completed Stage 8.4: `frontend/src/components/VoicePanel.vue` and
  `frontend/src/styles/base.css` separate bottom user identity controls from voice
  connection status, speaking/meter detail, and screen/call actions, with verified
  connected/disconnected and mobile layouts.
- Completed Stage 8.5: `frontend/src/App.vue`, `ServerRail.vue`,
  `PrivateChannelSidebar.vue`, `ChannelSidebar.vue`, `VoicePanel.vue`, and
  `frontend/src/styles/base.css` make current destination, active rail/sidebar rows,
  connected voice channel, self voice row, and muted/deafened/speaking state visible.
- Completed Stage 8.6: visible placeholder actions in the private sidebar, server
  sidebar, Friends rows, and chat composer now open scoped demo notices or local
  panels instead of doing nothing.
- Completed Stage 8.7: channel header threads, notifications, pinned messages, and
  current-channel search open local panels with useful empty states, local
  notification selection, and active-message filtering.
- Completed Stage 8.8: server and DM composers support useful local emoji
  insertion; the server composer also provides bounded upload metadata, apps/action
  drafting templates, and an explicit gift demo limitation without breaking message
  send/edit/delete behavior.
- Completed Stage 8.9: Friends rows, the private DM sidebar, and DM conversation
  intros now expose scan-friendly status, activity, handle, participant, unread, and
  selected-state information, with a wide-screen Friends profile panel and responsive
  fallback rules for narrower layouts.
- Completed Stage 8.10: `SettingsView.vue` is reorganized into Account,
  Experience, and Session groups with account/privacy, voice/video, appearance,
  accessibility, keybind, language/time, and logout panels. Useful voice, language,
  and time controls are real local panels, and demo-only scope is explicit.
- Completed Stage 8.11: selecting a voice channel now opens a dedicated voice
  workspace before joining. The workspace distinguishes preview, connected,
  screen-share availability, local/remote participant tiles, and join/leave state;
  sidebar and bottom voice-panel copy now make selected versus connected channels
  clearer.
- Completed Stage 8.12: low-frequency and deferred features are classified in
  `docs/stage-8-12-feature-scope.md`. Separate Nitro, Shop, Quests, and gift
  controls were removed from the active UI, composer app actions were reframed as
  local templates, and Settings now documents commerce, external app, real file
  transfer, GIF search, and production-notification scope.
- Completed Stage 8.13: responsive/accessibility QA is documented in
  `docs/stage-8-responsive-accessibility-qa.md` with desktop/mobile screenshots,
  overflow metrics, focus-order notes, residual manual checks, and a rail
  `aria-current` correction in `ServerRail.vue`.
- Completed Stage 8.14: final Stage 8 verification is documented in
  `docs/stage-8-final-qa.md`. Backend tests, backend lint, frontend lint, frontend
  production build, Docker service status, container-internal backend health, and the
  Stage 8 browser QA artifact index were recorded.

## Stage 9: Discord Visual Parity And Density Remediation

- Status: completed through Stage 9.13 final QA.
- Plan document: `docs/discord-visual-parity-remediation-plan.md`.
- Final QA document: `docs/stage-9-final-qa.md`.
- Target: make the existing functional clone read visually and ergonomically like the
  real Discord web app across Friends, Add Friend, server text channels, voice
  preview, voice connected state, and screen sharing.
- Privacy note: reference screenshots may contain private Discord names, messages,
  avatars, images, and server content. Use only layout, density, proportions,
  hierarchy, and interaction behavior; do not copy private content into repository
  data or documentation.
- Stage execution rule: complete each Stage 9 sub-stage with verification,
  documentation updates, commit, and push to `origin/main`. If verification finds
  overlap, broken behavior, or unacceptable visual drift, add a corrective sub-stage
  before continuing.
- Completed Stage 9.0: baseline measurement and screenshot matrix for real comparison
  widths and core Discord surface metrics.
- Completed Stage 9.1: safe demo data/content density so Friends, DM, text channel,
  member list, activity, and voice views can be judged without private Discord data.
- Completed Stage 9.2: global shell density, design tokens, typography, color layers,
  and primary panel proportions.
- Completed Stage 9.3: server rail parity for active markers, unread/mention badges,
  folders, generated safe avatars, and action buttons.
- Completed Stage 9.4: private sidebar and DM density parity.
- Completed Stage 9.5: Friends home and Add Friend parity, including right activity
  panel and complete Add Friend form states.
- Completed Stage 9.6: server sidebar and channel list parity.
- Completed Stage 9.7: text channel timeline and composer parity.
- Completed Stage 9.8: channel header panels and right sidebar parity.
- Completed Stage 9.9: bottom user and voice control parity.
- Completed Stage 9.10: voice stage and screen-share parity.
- Completed Stage 9.11: i18n, copy, and demo-scope cleanup across dense surfaces.
- Completed Stage 9.12: responsive and accessibility regression, including dark
  scrollbar correction recorded as Stage 9.12.1.
- Completed Stage 9.13: final visual parity QA, docs, commit, and push.

## Stage 10: Discord Interaction Polish And Noise Reduction

- Status: in progress; Stage 10.0 through Stage 10.10 are complete and implementation
  continues at Stage 10.11.
- Plan document: `docs/discord-interaction-polish-plan.md`.
- Target: make the existing clone feel cleaner, quieter, and more Discord-like by
  removing visual noise, development/test artifacts, oversized bottom controls, and
  dashboard-like component styling from high-frequency screens.
- Privacy note: reference screenshots may contain private Discord names, messages,
  avatars, images, and server content. Use only layout, density, proportions,
  hierarchy, and interaction behavior; do not copy private content into repository
  data or documentation.
- Stage execution rule: complete each Stage 10 sub-stage with verification,
  documentation updates, Korean commit titles, and push to `origin/main`. If
  verification finds overlap, broken behavior, or unacceptable visual drift, add a
  corrective `Stage 10.x.y` note before continuing.
- Completed Stage 10.0: baseline lock for current Friends, Add Friend, text channel,
  voice, and screen-share views in `docs/stage-10-baseline.md`.
- Completed Stage 10.1: demo and test data cleanup so smoke-test names, generated QA
  labels, old development-style DM users, and template messages do not dominate
  primary UI.
- Completed Stage 10.2: design token reset for quieter Discord-like colors, surface
  layers, hover/selected states, focus styles, scrollbars, and high-use shell
  controls; browser QA confirmed token application, no horizontal overflow, and old
  development-style names hidden.
- Completed Stage 10.3: shell layout recomposition moved the bottom voice controls
  into the active sidebar column, let the workspace keep the full main height, and
  verified Friends, text channel, and voice channel surfaces for horizontal overflow
  and column separation.
- Completed Stage 10.4: server rail polish normalized active/unread markers,
  quieter hover states, mention badge labels, secondary add/discovery actions, and
  browser-verified active marker/rail overflow behavior.
- Completed Stage 10.5: private sidebar simplification hid repeated inactive
  fallback copy, tightened DM rows to compact single-line layouts, clamped unread
  badges, and browser-verified sidebar density/noise.
- Completed Stage 10.6: Friends home rework tightened friend rows, hid secondary
  actions until interaction, removed noisy fallback activity copy, converted the
  right panel into a quieter activity card, and browser-verified Friends/Add Friend
  shell behavior.
- Completed Stage 10.7: Add Friend workflow polish removed secondary discovery and
  activity preview panels, rebuilt the form as a one-step input/submit flow, and
  browser-verified spacing plus disabled/success states.
- Completed Stage 10.8: server sidebar polish tightened channel row density,
  reduced category and channel action visibility to hover/focus, and browser-verified
  compact active/text/voice channel navigation.
- Completed Stage 10.9: header action reduction removed low-frequency/crowding
  buttons from the primary header and browser-verified remaining search/member/pin/
  notification/invite controls do not wrap.
- Completed Stage 10.10: text timeline rebuild replaced raw message IDs with
  locale-aware demo time labels, cleaned the date divider, converted reactions into
  compact pills, stabilized attachment card columns, and browser-verified text/DM
  message panels for horizontal overflow.
- Completed Stage 10.11: composer rebuild tightened server and DM message entry
  controls with fixed compact action columns, a 36 px send button, vertically
  centered 44 px input text, and a deferred template action. Browser QA verified no
  horizontal overflow, no voice-panel overlap, and a corrective fix for optional
  action width specificity.
- Completed Stage 10.12: member list simplification moved refresh, role creation,
  role assignment/removal, and member removal behind an explicit low-contrast
  management toggle, added localized member-list labels, and browser-verified the
  default panel remains clean while admin controls remain reachable.
- Completed Stage 10.13: bottom user panel rebuild shortened the lower-left panel,
  split user identity/actions from the selected/connected voice card, moved visible
  diagnostics out of the primary surface, added explicit aria labels for voice
  action buttons, and browser-verified compact sizing plus the corrected user
  identity width.
- Planned Stage 10.14: voice channel workspace rebuild.
- Planned Stage 10.15: screen-share flow rework.
- Planned Stage 10.16: feature visibility policy.
- Planned Stage 10.17: responsive and accessibility QA.
- Planned Stage 10.18: final QA, documentation, commit, and push.
