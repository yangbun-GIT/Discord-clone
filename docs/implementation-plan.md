# Implementation Plan

## Stage 1: Foundation

- Create a FastAPI backend that boots without external infrastructure.
- Add async database and Redis boundaries for Neon and Upstash integration.
- Implement Snowflake ID generation, permission bitfields, JWT helpers, rate limiting,
  gateway opcodes, and WebSocket connection management.
- Create a Vue 3 + Vite frontend app shell that resembles the Discord workspace flow.
- Add local development scripts, environment examples, and tests.

## Stage 2: Persistence and Auth

- Add asyncpg repositories and migrations for users, guilds, channels, roles, members,
  and messages.
- Implement registration, login, JWT-protected REST APIs, and guild membership queries.
- Replace frontend demo data with API-backed state.

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

- Add Dockerfiles, Gunicorn/Uvicorn worker config, and environment documentation.
- Prepare Oracle Cloud / GCP VM deployment notes.
- Add production CORS, rate-limit, logging, and health-check guidance.

