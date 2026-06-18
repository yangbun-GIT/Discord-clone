# Voice QA Checklist

Use this checklist after configuring `WEBRTC_ICE_SERVERS_JSON` with at least one
TURN server. STUN-only is acceptable for native local smoke tests, but it is not a
complete production voice check.

## Local Smoke Test

1. Start the backend and frontend:

   ```powershell
   npm run dev:backend
   npm run dev:frontend
   ```

2. Open `http://127.0.0.1:5173` in two browser profiles or two browsers.
3. Sign in as two different users. Use invite codes if one user needs to join the
   same guild.
4. Join the same voice channel from both sessions.
5. Verify both sessions show:
   - Connected voice state.
   - `Peers 1/1` in the voice quality line after the WebRTC connection settles.
   - Non-empty RTT/jitter/bitrate values while audio is flowing.
   - Mute toggles the local microphone track without leaving the channel.
   - Screen share prompts for browser display capture and renders a remote screen
     tile in the other session.

## TURN / NAT Test

1. Set production-like ICE servers in `.env` or the host secret store:

   ```powershell
   WEBRTC_ICE_SERVERS_JSON=[{"urls":"stun:stun.l.google.com:19302"},{"urls":"turn:turn.example.com:3478","username":"replace-me","credential":"replace-me"}]
   ```

2. Restart the backend and load `/api/meta/voice`.
3. Confirm `turn_configured` is `true`.
4. Repeat the two-session voice test across two different networks, such as home
   Wi-Fi and mobile hotspot.
5. Watch the voice quality line for persistent packet loss, high jitter, or
   unstable peer counts.

## Deployment Verification

Run this after deploying behind HTTPS:

- `GET /api/health` returns `status: ok`.
- `/api/meta/voice` returns the expected ICE server count and `turn_configured: true`.
- `/gateway` upgrades successfully through the reverse proxy.
- Two users can exchange text messages.
- Two users can join voice, hear each other, mute/unmute, and share a screen.
- Browser console has no repeated WebSocket, media permission, ICE, or autoplay
  errors during the test.

## Current Quality Signals

The frontend samples `RTCPeerConnection.getStats()` every two seconds while connected
to voice. The voice panel shows:

- Connected peer count.
- Average round-trip time.
- Inbound audio jitter.
- Inbound audio packet loss.
- Outbound audio bitrate.
- Outbound screen-share bitrate.

Use these values as diagnostics, not strict pass/fail thresholds. Typical follow-up
work is to collect stats over longer sessions and adapt screen-share frame rate or
resolution when packet loss and jitter stay high.

## Stage 11.12 QA Note

The 2026-06-18 Stage 11.12 pass verified backend health, `/api/meta/voice`, and the
gateway HELLO handshake in the local Docker stack. Browser DOM checks also confirmed
that the clone page exposes voice controls without native JavaScript dialogs.

Direct automated microphone and screen-capture execution was not completed because
the browser automation runtime did not expose `navigator.mediaDevices` permission or
capture APIs. Treat microphone join, same-server/cross-server voice switching, and
screen-share start/stop as manual browser-permission checks using the checklist
above. TURN/NAT behavior remains unverified until a real TURN server is supplied.
