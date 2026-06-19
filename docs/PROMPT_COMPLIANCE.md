# Prompt Compliance Map

This document maps `DEVELOPMENT_PROMPT.md` policies to the concrete repository
structure. Use it when checking whether future project changes still reflect the
prompt.

## Startup Protocol

Implemented by:

- `DEVELOPMENT_PROMPT.md`: full project-specific prompt.
- `AGENTS.md`: concise agent-facing rules.
- `PROJECT_CONTEXT.md`: current implementation map.
- `docs/implementation-plan.md`: staged roadmap.
- `README.md`: setup and verification commands.
- `docs/README.md`: document index.

Current status: satisfied.

## Implementation Policy

Implemented by:

- Backend service boundaries in `backend/app/api`, `backend/app/services`,
  `backend/app/repositories`, `backend/app/gateway`, and `backend/app/realtime`.
- Frontend service boundaries in `frontend/src/components`,
  `frontend/src/composables`, `frontend/src/stores`, and `frontend/src/services`.
- Integration maps in `PROJECT_CONTEXT.md`.

Current status: satisfied for the current implementation. Future behavior changes
must update `PROJECT_CONTEXT.md` and the relevant task document.

## Backend Rules

Implemented by:

- Async FastAPI lifecycle and connection pools in `backend/app/main.py` and
  `backend/app/db/pool.py`.
- Async repository/service split in `backend/app/repositories` and
  `backend/app/services`.
- JavaScript-safe Snowflake IDs in `backend/app/domain/snowflake.py`.
- Permission bitfields in `backend/app/domain/permissions.py`.
- Payload validation in `backend/app/schemas` and route handlers.
- Discord-style gateway contracts in `backend/app/gateway`.

Current status: satisfied. PostgreSQL repository tests cover the current mutation
surface through fake async database fixtures.

## Frontend Rules

Implemented by:

- Vue 3 `<script setup>` components in `frontend/src/components`.
- Pinia global state in `frontend/src/stores`.
- `shallowRef` usage for guild/message state in `frontend/src/stores/guilds.ts`.
- Usable app-first shell in `frontend/src/App.vue`.
- Accessible controls and stable layout rules in `frontend/src/styles/base.css`.

Current status: satisfied for the current UI surface. Any significant UI change still
requires build/lint plus browser smoke verification.

## Documentation Policy

Implemented by:

- `DEVELOPMENT_PROMPT.md`: durable operating policy.
- `AGENTS.md`: concise agent rules.
- `PROJECT_CONTEXT.md`: implementation map.
- `docs/README.md`: document index and update rules.
- `docs/implementation-plan.md`: roadmap.
- `docs/deployment.md`: runtime/deployment.
- `docs/voice-qa.md`: voice QA.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md`: Git/GitHub workflow.
- `docs/PROMPT_COMPLIANCE.md`: this prompt-to-structure map.

Current status: satisfied.

## Verification Policy

Implemented by:

- Root npm scripts in `package.json`.
- Backend tests in `backend/tests`.
- Frontend lint/build scripts in `frontend/package.json`.
- Verification command lists in `README.md`, `PROJECT_CONTEXT.md`, and
  `docs/GITHUB_COLLABORATION_WORKFLOW.md`.

Current status: satisfied. External readiness now has placeholder-only Compose,
Caddy, coturn, and safe WSS/readiness-check files. Actual production VM rollout,
real TURN credentials, and multi-network browser QA still remain external.

## Security And Data Policy

Implemented by:

- `.gitignore` excludes `.env`, `.env.*`, dependency folders, caches, logs, and build
  output while allowing `.env.example`.
- `.env.example` uses placeholder values only.
- `PROJECT_CONTEXT.md` and `docs/deployment.md` document environment variable names
  and setup expectations instead of real secret values.

Current status: satisfied. Continue checking docs and staged changes for real secrets
before every commit.

## Collaboration Policy

Implemented by:

- `DEVELOPMENT_PROMPT.md` collaboration rules.
- `AGENTS.md` push-to-`origin/main` rule.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md` branch, commit, push, and verification
  workflow.

Current status: satisfied for the current single-user `main` workflow.

## Known External Gaps

These are not repository-structure gaps. They require external resources:

- Real TURN provider credentials.
- Multi-browser or multi-device voice QA across separate networks.
- Actual production VM rollout and HTTPS reverse proxy verification. The repository
  now includes safe reference files and `npm run check:deployment:readiness`, but
  the external host still has to be provisioned and tested.

Track these as next work in `PROJECT_CONTEXT.md` and relevant task docs until the
external environment exists.
