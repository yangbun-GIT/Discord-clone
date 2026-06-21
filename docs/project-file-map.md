# Project File Map

Use this document as a quick routing map before broad code exploration. It is
kept in Git because it explains the submitted project structure, not because it
records transient work plans.

## Root

- `README.md`
  - Korean-first quick start, Docker execution, HTTPS/LAN notes, optional
    Cloudflare Tunnel demo, verification commands, and GitHub submission hygiene.
- `AGENTS.md`
  - Repository-specific Codex engineering rules.
- `DEVELOPMENT_PROMPT.md`
  - Project development policy used during implementation.
- `PROJECT_CONTEXT.md`
  - Current implementation summary, active assumptions, important verification
    notes, and residual risks.
- `.gitignore`
  - Excludes secrets, generated certificates, build outputs, local screenshots,
    local videos, local planning docs, prompts, stage logs, and generated QA
    artifacts from GitHub submission.
- `.env.example`
  - Non-secret local environment template.
- `compose.yaml`
  - Default local Docker Compose stack for frontend, backend, PostgreSQL, and
    supporting services.
- `compose.https.yaml`
  - Optional HTTPS local/LAN override for microphone and screen-share testing.
- `compose.cloudflare-tunnel.yaml`
  - Optional Cloudflare Quick Tunnel demo frontend.
- `compose.production.example.yaml`
  - Future always-on public deployment example. It contains placeholders only.
- `package.json`
  - Root scripts for Docker startup, checks, smoke tests, and readiness checks.

## Backend

- `backend/app/main.py`
  - FastAPI application assembly and lifespan wiring.
- `backend/app/core/`
  - Configuration, security, auth token helpers, and rate-limit support.
- `backend/app/api/`
  - REST API routing and request dependencies.
- `backend/app/api/routes/`
  - Auth, dev sessions, users, guilds, channels, DMs, store, meta, and health
    endpoints.
- `backend/app/gateway/`
  - Discord-style WebSocket gateway, voice signaling, heartbeat, and dispatch
    flow.
- `backend/app/services/`
  - Domain logic for auth, guilds, channels, DMs, users, store, voice, and
    persistence coordination.
- `backend/app/repositories/`
  - PostgreSQL repository implementations.
- `backend/app/db/`
  - Async database pool, schema, and seed data.
- `backend/app/realtime/`
  - Realtime event publishing and optional Redis fan-out.
- `backend/app/schemas/`
  - Pydantic schemas for API and gateway boundaries.
- `backend/tests/`
  - Backend unit/API/gateway/repository tests.

## Frontend

- `frontend/src/main.ts`
  - Vue app entrypoint.
- `frontend/src/App.vue`
  - Main Discord clone shell, destination routing, panels, voice workspace, and
    top-level UI state.
- `frontend/src/components/`
  - UI surfaces such as server rail, sidebars, friends, DMs, chat, voice panel,
    settings, store, and shared widgets.
- `frontend/src/stores/`
  - Pinia stores for session, guilds, DMs, private channels, voice, settings,
    and realtime handlers.
- `frontend/src/composables/`
  - Reusable Vue/WebRTC/gateway/media logic.
- `frontend/src/services/api.ts`
  - REST client helpers.
- `frontend/src/i18n/index.ts`
  - Korean/English UI copy.
- `frontend/src/styles/base.css`
  - Global layout and Discord-like visual styling.
- `frontend/tests/`
  - Frontend tests.

## Scripts

- `scripts/create_lan_https_cert.ps1`
  - Generates local HTTPS LAN certificate files under ignored `certs/`.
- `scripts/submission_readiness_check.mjs`
  - Checks the local submission/demo stack.
- `scripts/deployment_readiness_check.mjs`
  - Checks an HTTPS/WSS deployment origin without printing secrets.
- `scripts/voice_readiness_check.mjs`
  - Checks voice readiness metadata without printing ICE/TURN details.
- `scripts/realtime_browser_smoke.mjs`
  - Browser smoke test for realtime text, DM, voice, and screen-share flows.
- `scripts/realtime_redis_smoke.py`
  - Optional multi-worker Redis realtime smoke test.

## Submitted Docs

- `docs/README.md`
  - Documentation index and local-only documentation policy.
- `docs/structure-map/reference-map.md`
  - Selective dependency and reverse-reference map.
- `docs/assignment-submission-guide.md`
  - Assignment/demo guide.
- `docs/deployment.md`
  - Runtime and deployment notes.
- `docs/external-deployment-decision.md`
  - Future public deployment decision record.
- `docs/external-deployment-runbook.md`
  - Future public deployment runbook.
- `docs/voice-qa.md`
  - Voice and screen-share QA guide.
- `docs/realtime-communication-qa.md`
  - Realtime communication QA guide.
- `docs/voice-transport-architecture.md`
  - Voice transport and future SFU architecture notes.

## Local-Only Paths

These paths are intentionally ignored and should not be committed for submission:

- `certs/` generated HTTPS certificates.
- `docs/qa-artifacts/` generated QA screenshots.
- `docs/reference-screenshots/` real Discord/clone comparison screenshots.
- `docs/reference-videos/` voice/screen-share recordings and analysis frames.
- `docs/remediation-tasks/` task-specific work documents.
- `docs/prompts/` local prompt library.
- `docs/stage-*.md`, `docs/*-plan.md`, `docs/*remediation*.md`,
  `docs/*baseline*.md`, and `docs/*final-qa.md`.
