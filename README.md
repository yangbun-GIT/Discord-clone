# Discord Clone

Zero-budget Discord clone based on the SRS provided for the project.

## Stack

- Backend: Python 3.14, FastAPI, asyncpg, Redis asyncio client, Pydantic v2
- Frontend: Vue 3, Vite, Pinia, Vue Router, Oxlint
- Realtime: Discord-style gateway opcodes over WebSocket
- Data model: PostgreSQL schema with JavaScript-safe Snowflake IDs and bitfield permissions

## Local Setup

Install frontend dependencies:

```powershell
npm --prefix frontend install
```

Install backend dependencies:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python -m pip install -e .\backend[dev]
```

Run the backend:

```powershell
npm run dev:backend
```

Run the frontend in another terminal:

```powershell
npm run dev:frontend
```

Open `http://127.0.0.1:5173`.

For same-LAN testing from another PC or mobile device, bind both dev servers to all
interfaces:

```powershell
npm run dev:backend:lan
npm run dev:frontend:lan
```

Find the host IPv4 address with `ipconfig`, then open
`http://<host-ip>:5173` from the second device. If you bypass the Vite proxy and call
the backend directly from the browser, add `http://<host-ip>:5173` to
`CORS_ORIGINS`. Windows firewall must allow ports `5173` and `8000`.

The frontend starts at the login/register screen when no saved session exists. Use
the Demo user button for the seeded local workspace.

## Docker Setup

Docker is optional for day-to-day development, but useful for onboarding, reproducible
runtime checks, and future VM deployment. The Compose stack includes local PostgreSQL
for persistence.

Run the full stack with Compose:

```powershell
npm run docker:up
```

Stop containers:

```powershell
npm run docker:down
```

`npm run docker:down` preserves the PostgreSQL volume. To reset local Docker data,
run `docker compose down -v`.

Docker exposes the same local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

For Docker LAN access, open `http://<host-ip>:5173`; Compose already publishes
ports `5173` and `8000` on the host.

Useful backend auth endpoints:

- `POST http://127.0.0.1:8000/api/auth/register`
- `POST http://127.0.0.1:8000/api/auth/login`
- `GET http://127.0.0.1:8000/api/auth/me`
- `GET http://127.0.0.1:8000/api/users/me/relationships`
- `GET http://127.0.0.1:8000/api/dms`
- `GET http://127.0.0.1:8000/api/store/catalog`
- `GET http://127.0.0.1:8000/api/store/items/6401`

Authenticated users can create a server from the `Create server` button. New servers
start with `general` and `voice-room` channels.

Server owners can create invite codes from the top bar. Other authenticated users can
join with those codes from `Join server`.

## Environment

Copy `.env.example` to `.env` and fill values as external services become available.
Native local development works without `DATABASE_URL` or `REDIS_URL`; it uses an
in-memory demo store while preserving the async connection-pool boundaries required
by the SRS. Docker Compose supplies its own local PostgreSQL URL automatically.

Messages, channels, relationships, and direct messages created in Docker mode persist
in the local PostgreSQL volume. Messages, channels, and direct messages created in
native demo mode are kept in the running backend process and reset when that process
restarts.

WebRTC voice uses `WEBRTC_ICE_SERVERS_JSON` from the backend environment. The default
STUN server is enough for local development; deployed voice should use a TURN provider
such as Open Relay or Metered Video.
Voice controls support microphone mute, input-level feedback, and screen sharing.
Screen sharing uses the browser display-capture permission prompt and works only while
connected to a voice channel.
The backend voice metadata also reports whether TURN is configured, and the voice
panel shows peer count, RTT, jitter, packet loss, and outbound bitrate while connected.

LAN success and TURN/NAT internet success are separate release gates. Do not mark
internet voice complete unless `/api/meta/voice` reports `turn_configured: true` and
two users on different networks can complete a real voice/screen-share test.

Deployment notes are maintained in `docs/deployment.md`. Voice QA steps are maintained
in `docs/voice-qa.md`, and communication QA steps are maintained in
`docs/realtime-communication-qa.md`. The documentation index is maintained in
`docs/README.md`.
Git workflow notes are maintained in `docs/GITHUB_COLLABORATION_WORKFLOW.md`, and
prompt-alignment status is maintained in `docs/PROMPT_COMPLIANCE.md`.
The current Discord app clone roadmap is maintained in
`docs/discord-app-clone-implementation-plan.md`. The deferred Store-like shop roadmap
is maintained in `docs/store-clone-implementation-plan.md`.

## Verification

```powershell
npm run test:frontend
npm run test:backend
npm run lint:backend
npm run lint:frontend
npm --prefix frontend run build
npm run smoke:realtime:browser
npm run smoke:realtime:redis
docker compose exec -T backend pytest
```

`npm run smoke:realtime:browser` expects the backend at `http://127.0.0.1:8000`
and the frontend at `http://127.0.0.1:5173`. It is a same-PC fake-device smoke for
server text, DM, voice peer, remote screen-share rendering, and voice leave cleanup
code paths, not a LAN/TURN release gate. `npm run smoke:realtime:redis` expects the
primary backend at `http://127.0.0.1:8000` and a secondary backend at
`http://127.0.0.1:8001`.

As of the 2026-06-19 Stage C9 gate, the local command suite and Docker/local
communication smoke pass. Real microphone quality, real screen picker UX,
different-PC LAN, and TURN/NAT internet voice remain separate manual gates.
