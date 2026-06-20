# Assignment Submission And Demo Guide

Date: 2026-06-20

This guide is the default submission path for the clone-coding assignment. It is
not an always-on public deployment plan. The expected grading path is:

1. Run the full frontend and backend locally with Docker Compose.
2. Verify the Discord clone in a browser on the grading machine.
3. Optionally expose the local app with Cloudflare Tunnel for temporary HTTPS
   access from another network.

The VM/VPS + Caddy + production Compose documents remain available as a future
extension path, but they are not required for the basic assignment submission.

## Project Structure For Grading

- Frontend: `frontend/`
  - Vue 3 + Vite app.
  - Discord-like app shell, Friends, DM, server text channels, voice channel UI,
    settings, and screen-share surfaces.
- Backend: `backend/`
  - FastAPI ASGI service.
  - Auth, guild/channel/message APIs, DM/friend APIs, metadata APIs, and
    Discord-style WebSocket gateway.
- Persistence:
  - Docker Compose runs local PostgreSQL.
  - Local Docker data persists until the Docker volume is removed.
- Realtime:
  - Text/DM events use REST as the source of truth plus WebSocket dispatch for
    live updates.
  - Voice and screen sharing use WebRTC P2P media with the backend WebSocket
    gateway for signaling and voice metadata.

## Default Submission Quick Start

Prerequisites:

- Docker Desktop or Docker Engine with the Compose plugin.
- Node.js/npm for root verification scripts.

Start the local full stack:

```powershell
npm run docker:up
```

Open:

- App: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

Run the local submission readiness check:

```powershell
npm run check:submission:local
```

This command automatically tries the normal HTTP Docker origin and the local HTTPS
Docker origins. It verifies:

- Frontend app HTML.
- Same-origin `/api/health`.
- PostgreSQL-backed health metadata.
- `/api/meta/voice/readiness`.
- `/gateway` HELLO over WebSocket or WSS.

Stop the local stack:

```powershell
npm run docker:down
```

`npm run docker:down` preserves the local PostgreSQL volume. Reset local Docker
data only when intended:

```powershell
docker compose down -v
```

## Test Accounts

No real password or fixed secret is committed for grading. Use the browser
Register screen to create two local accounts, then use those accounts for
Friends, DM, server, and voice checks.

For quick local exploration, the Demo user button opens a seeded local workspace.
For two-user communication checks, create two separate accounts in two browser
profiles or two browsers.

## Recommended Feature Check Order

1. Register or log in.
2. Create a server.
3. Create or select the `general` text channel.
4. Send a server text message.
5. Open a second browser profile, register a second account, and join the server
   through an invite.
6. Verify server text messages update in both sessions.
7. Add the second account as a friend and accept the request.
8. Open a Direct Message and send messages both directions.
9. Join the same voice channel from both sessions.
10. Verify participant lists, mute, deafen, and voice status indicators.
11. Test screen share from one session and confirm the other session sees the
    shared screen.
12. Open User Settings -> Voice & Video and confirm device, volume, sensitivity,
    RNNoise, and browser audio-processing controls are visible.

## Same-Wi-Fi Two-PC Test

Use this when the grader has two devices on the same network and wants to verify
real microphone or screen capture from the second device.

1. Find the host PC IPv4 address, for example `192.168.0.25`.
2. Generate a local HTTPS certificate for that exact address:

   ```powershell
   .\scripts\create_lan_https_cert.ps1 -HostName <host-ip>
   ```

3. Copy only `certs/lan-dev-root-ca.cer` to the second device and install it under
   Trusted Root Certification Authorities. Do not copy `certs/lan-dev.pfx`.
4. Start the HTTPS Docker stack:

   ```powershell
   npm run docker:up:https:detached
   ```

5. Open:

   - Host PC: `https://localhost:5173` or `https://127.0.0.1:5173`
   - Second device: `https://<host-ip>:5173`

6. Confirm `https://<host-ip>:5173/api/health` works and the browser reports a
   secure origin before testing microphone or screen sharing.

Same-Wi-Fi success is a LAN result only. It does not prove public internet TURN/NAT
voice.

## Optional Cloudflare Tunnel Demo

Cloudflare Tunnel is an optional temporary external-access path for demos. It is
not a formal always-on deployment. The local PC must stay on, Docker must keep
running, and the generated URL is temporary when using Quick Tunnel.

Official Cloudflare references:

- Cloudflare Tunnel:
  `https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/`
- TryCloudflare Quick Tunnel:
  `https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/`
- Cloudflare WebSockets:
  `https://developers.cloudflare.com/network/websockets/`

Recommended simple path:

1. Start the local Docker stack and the HMR-free tunnel frontend:

   ```powershell
   npm run docker:up:https:detached
   npm run docker:up:cloudflare-tunnel
   ```

2. Install `cloudflared` from Cloudflare's official documentation for the current
   OS. On Windows, the tested local path is a user-local executable such as
   `%USERPROFILE%\.local\bin\cloudflared.exe`.
3. Start a temporary tunnel to the HMR-free local frontend origin:

   ```powershell
   cloudflared tunnel --url http://localhost:5174
   ```

4. Open the printed `https://*.trycloudflare.com` URL from another browser or
   network.
5. Confirm:

   - The page loads over HTTPS.
   - `/api/health` works through the same public origin.
   - The WebSocket gateway connects over WSS.
   - Text and DM updates work in two sessions.

`frontend-tunnel` serves the built frontend through Nginx on local port `5174`
and proxies `/api` plus `/gateway` to the backend. Use this for Cloudflare
Tunnel demos instead of the Vite dev server on `5173`; the dev server injects HMR
WebSocket clients that are useful during development but create avoidable console
errors on a random public Quick Tunnel hostname.

Cloudflare provides the public HTTPS endpoint and proxies requests to the local
origin. The browser sees a secure context at the Cloudflare URL, which is required
for microphone and screen-capture APIs.

Important WebRTC limitation:

- Cloudflare Tunnel carries the frontend, REST API, and WebSocket signaling.
- WebRTC media still uses STUN/TURN candidate paths between browsers.
- For reliable voice and screen sharing across different networks, configure a
  TURN server in `WEBRTC_ICE_SERVERS_JSON` and verify
  `/api/meta/voice/readiness.turn_configured` is `true`.
- Do not mark external voice complete until two different networks pass a real
  microphone and screen-share test.

## Verification Commands

Submission readiness:

```powershell
npm run check:submission:local
```

Local Docker/HTTPS regression checks:

```powershell
npm run check:deployment:config
```

When the HTTPS Docker stack is running:

```powershell
$env:DEPLOYMENT_ORIGIN = "https://localhost:5173"
$env:DEPLOYMENT_IGNORE_TLS_ERRORS = "1"
npm run check:deployment:readiness
npm run smoke:realtime:browser:https
```

For the normal HTTP Docker stack:

```powershell
npm run smoke:realtime:browser
```

Documentation safety checks:

```powershell
git diff --check
rg -n -i "api[_-]?key|jwt_secret\s*=|password\s*=|credential\s*=|secret\s*=|token\s*=" DEVELOPMENT_PROMPT.md AGENTS.md PROJECT_CONTEXT.md README.md docs
```

The secret-pattern search is a guardrail. It may report environment variable
names or safe placeholder text; never add real secret values to docs or Git.

## Verification Result 2026-06-20

Local package checks run for this packaging pass:

- `npm run check:submission:local`: passed against the running local HTTPS Docker
  origin. PostgreSQL health metadata was configured, gateway HELLO succeeded, STUN
  was configured, and TURN was not configured.
- `npm run check:deployment:config`: passed with placeholder-only production
  values.
- `DEPLOYMENT_ORIGIN=https://localhost:5173` plus
  `DEPLOYMENT_IGNORE_TLS_ERRORS=1 npm run check:deployment:readiness`: passed for
  local HTTPS readiness with `turn_configured: false`.
- `npm run smoke:realtime:browser:https`: passed for same-PC HTTPS realtime smoke.
- `git diff --check`: passed.

Manual or environment-dependent items still not verified in this pass:

- Real different-network voice and screen sharing.
- TURN/NAT success with real TURN credentials.

## Cloudflare Tunnel Verification Result 2026-06-20

Cloudflare Quick Tunnel was verified with the HMR-free `frontend-tunnel` origin.
The exact `trycloudflare.com` hostname was temporary and is not recorded as a
stable deployment URL.

Commands and checks:

- Installed `cloudflared` from the official Cloudflare release path into a
  user-local tools directory. No login, token, account ID, or fixed tunnel
  credential was used.
- `docker compose -f compose.yaml -f compose.cloudflare-tunnel.yaml up -d --build frontend-tunnel`:
  passed and exposed the built frontend on `http://localhost:5174`.
- `cloudflared tunnel --url http://localhost:5174`: passed and generated a
  temporary `https://*.trycloudflare.com` URL.
- Public URL frontend load: passed with the login/register surface visible and no
  browser console errors in a page-load probe.
- Public URL `/api/health`: passed with database connectivity configured and
  connected.
- Public URL `/api/meta/voice/readiness`: passed with STUN configured and
  `turn_configured: false`.
- Public URL `npm run check:deployment:readiness`: passed with secure origin,
  healthy API, and `/gateway` HELLO over WSS.
- Public URL `npm run smoke:realtime:browser`: passed for server text, DM,
  gateway dispatch, voice fake-media peer creation, mute/deafen behavior,
  fake screen-share rendering/cleanup, voice refresh recovery, and
  `browserErrors: 0`.
- Local regression after the tunnel pass:
  `npm run check:submission:local` and `npm run smoke:realtime:browser:https`
  both passed.

Remaining manual gates:

- Real external-network microphone and screen-share QA are still not complete.
- TURN/NAT internet voice remains incomplete until `turn_configured: true` and
  two different networks pass real media QA.

## Not Part Of The Default Submission

- GitHub Pages-only deployment is not sufficient for this project because the app
  requires FastAPI, PostgreSQL, WebSocket gateway, and WebRTC ICE/TURN metadata.
- VM/VPS + Caddy + production Compose remains a future always-on deployment
  option, documented in `docs/external-deployment-decision.md` and
  `docs/external-deployment-runbook.md`.
- TURN/NAT external voice and screen sharing remain manual QA until a real TURN
  configuration and two different networks pass the test.

## Current Status

- Local Docker Compose is the default submission path.
- Same-Wi-Fi HTTPS LAN testing is documented and previously passed manually.
- Cloudflare Tunnel is documented as an optional temporary external access path.
- No permanent public VM/VPS deployment is claimed complete.
