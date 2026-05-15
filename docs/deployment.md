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
