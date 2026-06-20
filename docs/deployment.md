# Deployment Notes

## Assignment Submission Scope

The default assignment submission path is local Docker Compose execution. A grader
can run the frontend, backend, PostgreSQL, WebSocket gateway, and voice metadata on
one machine with:

```powershell
npm run docker:up
```

Then open `http://127.0.0.1:5173`. This is the primary grading path because the
project requirement is frontend plus backend implementation, not a permanently
hosted public service.

Optional external access for a short demo can use Cloudflare Tunnel after the local
stack is running:

```powershell
npm run docker:up:cloudflare-tunnel
cloudflared tunnel --url http://localhost:5174
```

Cloudflare Tunnel creates a temporary public HTTPS URL to the local origin. It can
carry the frontend, REST API, and `/gateway` WebSocket traffic through the same
origin, but it is not a formal deployment and it does not replace WebRTC TURN
requirements. Different-network voice and screen sharing still need a real TURN
configuration and manual QA before they can be called complete.

The Cloudflare demo path uses `frontend-tunnel` on local port `5174` instead of
the Vite dev frontend on `5173`. `frontend-tunnel` serves the built frontend with
Nginx and avoids Vite HMR WebSocket errors on random Quick Tunnel hostnames.

The complete submission guide is `docs/assignment-submission-guide.md`.

## Runtime Shape

- Build `backend/Dockerfile` with the `runtime` target for production.
- The runtime container starts Gunicorn with Uvicorn workers:
  `gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker`.
- Build `frontend/Dockerfile` with the `runtime` target to serve the Vite bundle
  through Nginx.
- Put the frontend and backend behind one HTTPS reverse proxy so `/api` and
  `/gateway` share the same origin.

Recommended future always-on external-test topology for this project:

1. A small single VM or server running Docker Compose.
2. Caddy as the public HTTPS reverse proxy for the domain.
3. Frontend runtime container served through Nginx.
4. Backend runtime container on the internal Docker network.
5. PostgreSQL and Redis as managed services or Compose services.
6. TURN through either a managed TURN provider or a self-hosted coturn service.

The deployment decision record is `docs/external-deployment-decision.md`. It is now
classified as a future always-on public deployment option. It selects single VM
Docker Compose as the first future external-network QA path and keeps TURN/NAT
internet voice marked incomplete until a real HTTPS/WSS deployment, TURN
configuration, and two different networks are verified.

This is preferred over GitHub Pages or another static-only host because the clone
requires a stateful backend API, authenticated WebSocket gateway, PostgreSQL,
Redis-backed fan-out for multi-worker deployments, and WebRTC ICE/TURN
configuration. Static hosting can serve the Vue bundle only; it cannot run the
FastAPI `/api` service, upgrade `/gateway`, or provide TURN relay behavior.

Reference files for a first external test are:

- `compose.production.example.yaml`
- `deploy/Caddyfile.example`
- `deploy/production.env.example`
- `deploy/coturn/turnserver.conf.example`
- `scripts/deployment_readiness_check.mjs`
- `docs/external-deployment-runbook.md`

The example topology is intentionally conservative: production-oriented Compose
should avoid application-code bind mounts, set deployment-specific environment
variables, and use restart policies. Caddy is selected for HTTPS reverse proxying,
and coturn is selected as the self-hosted TURN candidate because it is the standard
open-source STUN/TURN server used for NAT traversal.

## Required Environment

- `ENVIRONMENT=production`
- `JWT_SECRET`: long random secret, never committed.
- `CORS_ORIGINS`: production frontend origin.
- `DATABASE_URL`: Neon PostgreSQL or a managed PostgreSQL URL.
- `REDIS_URL`: Upstash Redis or another Redis endpoint for multi-instance fan-out.
- `WEBRTC_ICE_SERVERS_JSON`: JSON array of STUN/TURN servers.
- `APP_DOMAIN`: public domain for the HTTPS reverse proxy when using the example
  Caddy topology.
- `ACME_EMAIL`: certificate notification email for Caddy/ACME.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: only when using the example
  Compose PostgreSQL service instead of a managed database.

Example ICE JSON:

```json
[
  { "urls": "stun:stun.l.google.com:19302" },
  {
    "urls": "turn:turn.example.com:3478",
    "username": "replace-me",
    "credential": "replace-me"
  }
]
```

Use a TURN provider such as Open Relay or Metered Video before testing voice across
NATs or deployed networks. STUN-only is acceptable for local development but is not a
reliable production voice path.

`GET /api/meta/voice/readiness` exposes only `ice_server_count`,
`stun_configured`, and `turn_configured` so deployment checks can confirm whether a
TURN server is active without printing ICE URLs or TURN credentials. The browser app
still uses `GET /api/meta/voice` to fetch the ICE server configuration required by
WebRTC.

## LAN Development Access

LAN testing is a separate gate from TURN/NAT internet testing. A same-LAN pass means
another device can reach the development host on the local network; it does not prove
that voice works across different NATs or the public internet.

Native LAN run commands:

```powershell
npm run dev:backend:lan
npm run dev:frontend:lan
```

Equivalent explicit commands:

```powershell
cd backend
..\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
npm --prefix frontend run dev -- --host 0.0.0.0
```

Find the host IPv4 address:

```powershell
ipconfig
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.254*' }
```

LAN checklist:

1. Pick the host IP, for example `192.168.0.25`.
2. Set `CORS_ORIGINS` to include `http://192.168.0.25:5173` when browser clients
   call the backend directly. The Vite dev server proxy keeps `/api` and `/gateway`
   same-origin for the browser, but explicit backend access still needs CORS.
3. Open the frontend from the second device:
   `http://192.168.0.25:5173`.
4. Confirm the frontend can reach:
   - `http://192.168.0.25:5173/api/health`
   - `ws://192.168.0.25:5173/gateway`
5. Allow Windows firewall prompts for ports `5173` and `8000`.
6. For Docker LAN, Compose already publishes `5173:5173` and `8000:8000`; access
   the same host IP and keep the frontend proxy target pointed at the backend
   container.
7. For microphone and screen capture from a non-localhost LAN origin, browser support
   may require HTTPS. If media capture is blocked on `http://<host-ip>`, use a local
   HTTPS reverse proxy or test media from localhost and reserve LAN for text/gateway
   reachability.

HTTPS LAN media path:

1. Create or obtain a locally trusted development certificate for the exact host
   name or IP that the second device will open. Do not use production certificates
   or commit private keys.
2. Trust the certificate authority or certificate on the second device.
3. Start the backend on all interfaces:

   ```powershell
   npm run dev:backend:lan
   ```

4. In a separate shell, point Vite at the certificate files and backend proxy:

   ```powershell
   $env:VITE_HTTPS_KEY_FILE="C:\path\to\host-ip-key.pem"
   $env:VITE_HTTPS_CERT_FILE="C:\path\to\host-ip-cert.pem"
   $env:VITE_BACKEND_PROXY_TARGET="http://127.0.0.1:8000"
   npm run dev:frontend:lan:https
   ```

5. Open `https://<host-ip>:5173` from the second device.
6. Confirm `https://<host-ip>:5173/api/health` works and the browser shows a
   secure origin before attempting microphone or screen sharing.
7. If the browser still reports an insecure context, fix certificate trust/SAN
   mismatch first. Do not mark LAN voice complete from `http://<host-ip>`.

Docker HTTPS LAN development:

1. Generate a local certificate for the exact LAN host used by the second device:

   ```powershell
   .\scripts\create_lan_https_cert.ps1 -HostName <host-ip>
   ```

2. Trust `certs/lan-dev-root-ca.cer` on the second device under
   `Trusted Root Certification Authorities`. Keep `certs/lan-dev.pfx` only on the
   development host. Compare the certificate warning thumbprint with the script's
   `Root CA thumbprint` before accepting.
3. Start the HTTPS Compose override:

   ```powershell
   npm run docker:up:https:detached
   ```

4. Open `https://<host-ip>:5173`. Vite terminates HTTPS and proxies `/api` plus
   `/gateway` to the backend container, so browser microphone and display-capture
   calls run from a secure origin while the internal backend remains HTTP.

TURN/NAT internet checklist:

1. Configure `WEBRTC_ICE_SERVERS_JSON` with at least one `turn:` or `turns:` URL.
2. Restart the backend and verify the safe readiness check reports
   `turn_configured: true`:

   ```powershell
   npm run check:voice:readiness
   ```

3. Test two users from different networks, such as home Wi-Fi and mobile hotspot.
4. Verify voice join, audio, mute/unmute, screen-share start/stop, and peer stats.
5. Mark internet voice incomplete if TURN credentials are unavailable or
   `/api/meta/voice/readiness` reports `turn_configured: false`.

For deployed hosts, prefer the combined deployment check:

```powershell
$env:DEPLOYMENT_ORIGIN = "https://<domain>"
$env:REQUIRE_TURN = "1"
npm run check:deployment:readiness
```

## Future VM Checklist

This section is not required for the default assignment submission. Use it only when
moving from the local Docker Compose + optional Cloudflare Tunnel path to an
always-on public deployment.

Follow `docs/external-deployment-decision.md` before provisioning external
resources. It separates user-prepared items from Codex-actionable work and records
which release gates must remain `Pending / Not Verified`.

1. Provision a small Oracle Cloud or GCP VM.
2. Install Docker Engine and the Compose plugin.
3. Point DNS at the VM and terminate HTTPS with Nginx, Caddy, or a managed load
   balancer.
4. Set production environment variables through the host secret mechanism or a
   non-committed `.env`.
5. Run the frontend and backend runtime images.
6. Verify:
   - `GET /api/health` returns `status: ok`.
   - `GET /api/meta/voice/readiness` returns `turn_configured: true` without
     credentials.
   - `/gateway` upgrades to WebSocket.
   - Two authenticated browser sessions can exchange text messages.
   - Two authenticated browser sessions can join the same voice channel and exchange
     WebRTC offer/answer/ICE signals.
   - The voice panel reports connected peers plus RTT, jitter, packet loss, and
     outbound bitrate from browser WebRTC stats.
   - Screen sharing renders a remote screen tile and shows connection state.

## Example Compose Deployment

Use this only as a starting point for an external QA host. Real secrets must come
from a non-committed `.env`, the host secret store, or managed provider settings.
The execution runbook is `docs/external-deployment-runbook.md`.

1. Copy `compose.production.example.yaml` to the deployment host.
2. Copy `deploy/production.env.example` to `deploy/production.env` on the host.
   The real `deploy/production.env` file is ignored by Git and must not be
   committed.
3. Set:
   - `APP_DOMAIN`
   - `ACME_EMAIL`
   - `JWT_SECRET`
   - `CORS_ORIGINS=https://<domain>`
   - PostgreSQL variables or managed `DATABASE_URL` equivalent.
   - `WEBRTC_ICE_SERVERS_JSON` with at least one `turn:` or `turns:` entry.
4. Render the Compose config before startup:

   ```powershell
   docker compose --env-file deploy/production.env -f compose.production.example.yaml config
   ```

   For a local placeholder-only rendering check, run:

   ```powershell
   npm run check:deployment:config
   ```

5. Open host firewall/security-group ports:
   - TCP `80` and `443` for HTTPS.
   - UDP/TCP `3478` and UDP relay range `49160-49200` if self-hosting coturn.
6. Start app services:

   ```powershell
   docker compose --env-file deploy/production.env -f compose.production.example.yaml up -d --build
   ```

7. If using the example self-hosted coturn service, copy
   `deploy/coturn/turnserver.conf.example` outside the repository, replace
   placeholders with secret values, and start with the `turn` profile only after
   firewall rules and DNS are ready:

   ```powershell
   docker compose --env-file deploy/production.env -f compose.production.example.yaml --profile turn up -d --build
   ```

8. Run the safe deployment readiness check:

   ```powershell
   $env:DEPLOYMENT_ORIGIN = "https://<domain>"
   $env:REQUIRE_TURN = "1"
   npm run check:deployment:readiness
   ```

The readiness check verifies HTTPS origin shape, `/api/health`,
`/api/meta/voice/readiness`, and `/gateway` HELLO over WSS. It prints only
non-secret readiness fields and does not identify, print tokens, print ICE URLs,
or expose TURN credentials.

For local self-signed HTTPS development only, add
`DEPLOYMENT_IGNORE_TLS_ERRORS=1`. Do not use that variable for a public deployment
or final external QA.

## Hardening

- Keep `CORS_ORIGINS` pinned to the production frontend URL.
- Require HTTPS for browser microphone access in production.
- Keep Redis configured when running more than one backend instance.
- Monitor backend stdout/stderr logs from Gunicorn and the reverse proxy access logs.
- Rotate `JWT_SECRET` only with a planned user logout window.

## Voice QA

Follow `docs/voice-qa.md` for the two-browser local smoke test, TURN/NAT test, and
deployment verification checklist.

## Stage C9 Communication Gate

The 2026-06-19 local communication gate passed with the Docker stack running
frontend, backend, backend-secondary, PostgreSQL, and Redis. Local health, frontend
HTTP, voice metadata, the full frontend/backend command suite, and
`npm run smoke:realtime:browser` passed. A post-C9 remediation pass added
abnormal voice-leave cleanup, Redis zero-subscriber fallback, Redis-backed
operation limit support, inactive-DM unread handling, `npm run smoke:realtime:redis`,
and stronger remote screen-share/voice-leave browser smoke assertions.

Deployment remains gated by environment-specific checks:

- Configure `JWT_SECRET`, `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`, and
  `WEBRTC_ICE_SERVERS_JSON` through host secrets, not committed files.
- Confirm `/api/meta/voice/readiness.turn_configured` is `true` before claiming
  internet voice support.
- Run different-PC LAN QA and different-network TURN/NAT QA separately from the
  same-PC fake-device browser smoke.
- Do not treat fake microphone or fake screen-share automation as real microphone
  quality or real screen-picker UX completion.
