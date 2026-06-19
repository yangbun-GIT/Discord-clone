# Deployment Notes

## Runtime Shape

- Build `backend/Dockerfile` with the `runtime` target for production.
- The runtime container starts Gunicorn with Uvicorn workers:
  `gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker`.
- Build `frontend/Dockerfile` with the `runtime` target to serve the Vite bundle
  through Nginx.
- Put the frontend and backend behind one HTTPS reverse proxy so `/api` and
  `/gateway` share the same origin.

## Required Environment

- `ENVIRONMENT=production`
- `JWT_SECRET`: long random secret, never committed.
- `CORS_ORIGINS`: production frontend origin.
- `DATABASE_URL`: Neon PostgreSQL or a managed PostgreSQL URL.
- `REDIS_URL`: Upstash Redis or another Redis endpoint for multi-instance fan-out.
- `WEBRTC_ICE_SERVERS_JSON`: JSON array of STUN/TURN servers.

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

## VM Checklist

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
