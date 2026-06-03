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
