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

- Future work must start by reading `PROJECT_CONTEXT.md`, this plan, and `AGENTS.md`.
- Meaningful implementation changes must update `PROJECT_CONTEXT.md`.
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

- Status: main feature bridge completed; focused repository coverage remains.
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
- Remaining persistence work: add focused repository tests for PostgreSQL-backed
  guild/role/member mutations.

## Stage 3: Realtime Messaging

- Status: in progress.
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
- Remaining realtime support work: add focused repository tests for PostgreSQL-backed
  guild/role/member mutations.

## Stage 4: Voice Signaling

- Add WebRTC signaling events for offers, answers, ICE candidates, and voice state.
- Add Open Relay / Metered Video ICE server configuration.
- Add frontend voice channel join controls and VAD scaffolding.

## Stage 5: Deployment

- Dockerfile baseline is complete; add production Gunicorn/Uvicorn worker config and
  deployment hardening.
- Prepare Oracle Cloud / GCP VM deployment notes.
- Add production CORS, rate-limit, logging, and health-check guidance.
