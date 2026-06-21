# Project Context

This file is the quick recovery map for future work on the submitted Discord
Clone project. Keep it focused on the current implementation, runtime shape,
important paths, and verification commands. Detailed planning, remediation,
stage, prompt, screenshot, and video files are local-only and ignored by Git.

## Required Reading Order

1. `DEVELOPMENT_PROMPT.md` for the project-specific engineering policy.
2. `AGENTS.md` for concise agent-facing rules.
3. `PROJECT_CONTEXT.md` for the current implementation map.
4. `README.md` for setup, execution, and verification commands.
5. `docs/README.md` for the submitted documentation index.
6. `docs/project-file-map.md` for quick path routing.
7. `docs/structure-map/reference-map.md` for cross-file dependency routing.

## Submission Scope

The project is a Discord-style clone with both frontend and backend
implementation:

- Frontend: Vue 3, Vite, TypeScript, Pinia.
- Backend: FastAPI ASGI service, async SQLAlchemy repositories, PostgreSQL.
- Realtime: Discord-style WebSocket gateway payloads with `op`, `d`, `s`, and
  `t` fields.
- Voice/screen share: browser WebRTC P2P transport with STUN by default and TURN
  readiness support for external NAT environments.
- Default submission path: local Docker Compose execution.
- Optional demo path: Cloudflare Quick Tunnel for temporary HTTPS access.

This is not a static-only app. GitHub Pages alone is not sufficient because the
clone needs backend APIs, WebSocket gateway, database state, and WebRTC signaling.

## Core Implemented Areas

- Authentication and local/development user flows.
- Friends, friend requests, DM list, unread indicators, and DM chat.
- Guild/server creation, invite join flow, leave/delete controls, simplified
  member role/permission handling.
- Server rail ordering, folders/groups, hover tooltips, selected/unread/voice
  indicators.
- Text and voice channels, bottom-up message timelines, message date dividers,
  message deletion for own messages, and realtime dispatch.
- Voice channel participation, DM voice calls, mute/deafen separation, screen
  sharing, participant grids, speaking feedback, reconnect/rejoin handling, and
  voice settings.
- User settings modal, account/settings sections, audio/video controls, language
  support, accessibility-oriented focus/labels, and responsive layout work.

## Key Runtime Files

- Backend application entry: `backend/app/main.py`.
- Backend settings: `backend/app/core/config.py`.
- Backend database models: `backend/app/models/`.
- Backend API routes: `backend/app/api/routes/`.
- Backend repositories/services: `backend/app/repositories/`,
  `backend/app/services/`.
- WebSocket gateway: `backend/app/gateway/router.py`,
  `backend/app/gateway/events.py`, `backend/app/gateway/voice_service.py`.
- Frontend entry: `frontend/src/main.ts`, `frontend/src/App.vue`.
- Frontend stores: `frontend/src/stores/`.
- Frontend API and realtime clients: `frontend/src/api/`,
  `frontend/src/composables/useGateway.ts`.
- Voice/WebRTC client logic: `frontend/src/composables/useVoiceRtc.ts`,
  `frontend/src/composables/voicePeerConnections.ts`,
  `frontend/src/composables/useVoiceSessionController.ts`,
  `frontend/src/composables/voiceMedia.ts`.
- Major UI components: `frontend/src/components/ServerRail.vue`,
  `frontend/src/components/ChannelSidebar.vue`,
  `frontend/src/components/FriendsHome.vue`,
  `frontend/src/components/DirectMessageView.vue`,
  `frontend/src/components/ChatView.vue`,
  `frontend/src/components/VoicePanel.vue`,
  `frontend/src/components/SettingsView.vue`.
- Shared frontend styling: `frontend/src/styles/base.css`.
- Internationalization: `frontend/src/i18n/index.ts`.

## Execution

Use README for the full Korean quick start. Common commands:

```powershell
npm install
npm run docker:up
npm run docker:up:https:detached
npm run docker:down
```

Default local addresses:

- HTTP frontend: `http://localhost:5173`
- HTTPS frontend: `https://localhost:5173`
- Backend health: `/api/health`
- Voice readiness: `/api/meta/voice/readiness`
- Gateway: `/gateway`

Cloudflare Quick Tunnel is an optional temporary demo route for external HTTPS
access. It is not a permanent production deployment and should not be documented
as a stable public URL.

## Verification

Use the following checks when relevant:

```powershell
npm run lint:frontend
npm run test:frontend
npm --prefix frontend run build
npm run test:backend
npm run lint:backend
npm run check:submission:local
npm run check:deployment:config
npm run check:deployment:readiness
npm run smoke:realtime:browser
npm run smoke:realtime:browser:https
npm run smoke:realtime:redis
git diff --check
```

Voice and screen-share quality still require manual browser-device QA because
fake-device smoke tests cannot judge microphone intelligibility, Bluetooth device
behavior, or real screen capture quality.

## Submitted Documentation

- `README.md`: Korean setup and execution guide.
- `docs/README.md`: submitted documentation index.
- `docs/assignment-submission-guide.md`: assignment/demo guide.
- `docs/deployment.md`: local Docker, LAN HTTPS, Cloudflare Tunnel, and
  deployment notes.
- `docs/external-deployment-decision.md`: external deployment decision record.
- `docs/external-deployment-runbook.md`: future external deployment runbook.
- `docs/voice-qa.md`: voice and screen-share QA notes.
- `docs/realtime-communication-qa.md`: realtime QA notes.
- `docs/voice-transport-architecture.md`: P2P transport and future SFU boundary.
- `docs/project-file-map.md`: current project path map.
- `docs/structure-map/reference-map.md`: cross-file reference map.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md`: Git workflow notes.

## Git Hygiene

The repository should not track personal media, local QA artifacts, prompt
experiments, stage work logs, remediation task documents, local certificates, or
source requirement binaries. These files remain available locally when needed but
are ignored by `.gitignore`.

Do not commit real secrets:

- `.env` files with actual values.
- JWT secrets.
- DB/Redis passwords.
- TURN credentials.
- Cloudflare tokens or tunnel credentials.
- Certificate private keys.
- Personal screenshots, videos, or original assignment documents.
