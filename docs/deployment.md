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

`GET /api/meta/voice` exposes `ice_server_count` and `turn_configured` so the frontend
and deployment checks can confirm whether a TURN server is active without inspecting
host secrets.

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

TURN/NAT internet checklist:

1. Configure `WEBRTC_ICE_SERVERS_JSON` with at least one `turn:` or `turns:` URL.
2. Restart the backend and verify `/api/meta/voice` reports
   `turn_configured: true`.
3. Test two users from different networks, such as home Wi-Fi and mobile hotspot.
4. Verify voice join, audio, mute/unmute, screen-share start/stop, and peer stats.
5. Mark internet voice incomplete if TURN credentials are unavailable or
   `/api/meta/voice` reports `turn_configured: false`.

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
   - `GET /api/meta/voice` returns `turn_configured: true`.
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
