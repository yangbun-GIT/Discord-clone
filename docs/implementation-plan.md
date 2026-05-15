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

- Status: in progress.
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
- Next persistence work: add explicit migration versioning and expand repositories
  for users, roles, and member-role management.
- Implement registration, login, JWT-protected REST APIs, and guild membership queries.
- Add API/store error and empty states.

## Stage 3: Realtime Messaging

- Persist messages through the REST/gateway boundary.
- Publish channel events through Redis Pub/Sub.
- Fan out Redis events to local WebSocket connections.
- Add heartbeat zombie-connection reaping tests.

## Stage 4: Voice Signaling

- Add WebRTC signaling events for offers, answers, ICE candidates, and voice state.
- Add Open Relay / Metered Video ICE server configuration.
- Add frontend voice channel join controls and VAD scaffolding.

## Stage 5: Deployment

- Dockerfile baseline is complete; add production Gunicorn/Uvicorn worker config and
  deployment hardening.
- Prepare Oracle Cloud / GCP VM deployment notes.
- Add production CORS, rate-limit, logging, and health-check guidance.
