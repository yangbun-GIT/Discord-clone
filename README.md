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

Browser microphone and screen-capture APIs treat `localhost` as secure, but they
usually block `http://<host-ip>` LAN origins. For same-LAN media testing, use a
locally trusted development certificate and run the HTTPS LAN frontend:

```powershell
$env:VITE_HTTPS_KEY_FILE="C:\path\to\host-ip-key.pem"
$env:VITE_HTTPS_CERT_FILE="C:\path\to\host-ip-cert.pem"
$env:VITE_BACKEND_PROXY_TARGET="http://127.0.0.1:8000"
npm run dev:backend:lan
npm run dev:frontend:lan:https
```

Then open `https://<host-ip>:5173` from the second device. The certificate must be
trusted on that device, and the certificate subject/SAN must match the host name or
IP used in the browser. Do not commit local certificate keys.

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

For Docker LAN media testing from another PC, HTTP is not enough because browsers
block microphone and screen capture on non-localhost insecure origins. Generate a
local development certificate for the host IP, trust the exported root CA `.cer`
file on the second device, and run the HTTPS Compose override:

```powershell
.\scripts\create_lan_https_cert.ps1 -HostName <host-ip>
npm run docker:up:https:detached
```

Then open `https://<host-ip>:5173` from the notebook. The frontend remains
same-origin for `/api` and `/gateway`; Vite terminates HTTPS and proxies to the
backend container over the internal Docker network. Docker HTTPS uses
`certs/lan-dev.pfx`; generated files under `certs/` are ignored by Git and must
not be committed. When installing `certs/lan-dev-root-ca.cer` on the notebook,
compare the Windows warning thumbprint with the script's `Root CA thumbprint`
before accepting.

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
Voice controls support microphone mute, input/output device preferences, optional
free RNNoise client-side denoising, combined input-level/sensitivity feedback, and
screen sharing.
Screen sharing uses the browser display-capture permission prompt and works only while
connected to a voice channel.
The backend voice metadata also reports whether TURN is configured, and the voice
panel shows peer count, RTT, jitter, packet loss, and outbound bitrate while connected.
For a credential-safe readiness check before external testing, run:

```powershell
npm run check:voice:readiness
```

This calls `/api/meta/voice/readiness` and prints only ICE server count plus
STUN/TURN readiness. It does not print ICE URLs, TURN credentials, tokens, or media
device labels.

LAN success and TURN/NAT internet success are separate release gates. Do not mark
internet voice complete unless the readiness check reports `turn_configured: true`
and two users on different networks can complete a real voice/screen-share test.

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
npm run smoke:realtime:browser:https
npm run smoke:realtime:redis
docker compose exec -T backend pytest
```

`npm run smoke:realtime:browser` expects the backend at `http://127.0.0.1:8000`
and the frontend at `http://127.0.0.1:5173`. It is a same-PC fake-device smoke for
server text, DM, voice peer, remote screen-share rendering, and voice leave cleanup
code paths, not a LAN/TURN release gate. When the Docker HTTPS LAN stack is running,
use `npm run smoke:realtime:browser:https`; HTTP URLs on port `5173` will return an
empty response because Vite is serving HTTPS only. `npm run smoke:realtime:redis` expects the
primary backend at `http://127.0.0.1:8000` and a secondary backend at
`http://127.0.0.1:8001`.

As of the 2026-06-19 Stage C9 gate, the local command suite and Docker/local
communication smoke pass. Real microphone quality, real screen picker UX,
different-PC LAN, and TURN/NAT internet voice remain separate manual gates.
