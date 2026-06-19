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

## LAN Smoke Test

Use this when another PC or mobile device must connect to the development host.

1. Start LAN-bound services:

   ```powershell
   npm run dev:backend:lan
   npm run dev:frontend:lan
   ```

2. Find the host IPv4 address:

   ```powershell
   ipconfig
   Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.254*' }
   ```

3. Open `http://<host-ip>:5173` from the second device.
4. If the browser calls the backend directly instead of through the Vite proxy, add
   `http://<host-ip>:5173` to `CORS_ORIGINS` and restart the backend.
5. Confirm:
   - `http://<host-ip>:5173/api/health` returns the backend health payload.
   - `/gateway` connects without repeated reconnects.
   - Two users can exchange text messages through the same server or DM.
   - Two users can join the same voice channel and see each other in the participant
     list.
6. Treat LAN success as a LAN-only result. It does not prove TURN/NAT internet
   voice.

If microphone or screen sharing is blocked from `http://<host-ip>`, use HTTPS for
the LAN origin or run media-capture checks from localhost. Browser media APIs require
a secure context except for localhost-class origins.

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

Release gate:

- LAN pass: same network, same development host, text/gateway/voice reachable.
- TURN/NAT pass: different networks, `/api/meta/voice.turn_configured` is `true`,
  and media works through a configured TURN-capable ICE list.
- Do not mark internet voice complete from fake-device or LAN-only tests.

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

## Real Speech Quality Checklist

Use this checklist for the next voice remediation pass. Fake-device smoke does not
cover these items.

1. Join the same voice channel with two real accounts and real microphones.
2. Verify both clients show the same participant list in the sidebar, workspace,
   bottom panel, and server rail before testing audio.
3. Speak a short phrase for at least 30 seconds from each side:
   - normal volume.
   - quiet speech.
   - louder speech without shouting.
   - short Korean sentence and short English sentence.
4. While speaking, type on the keyboard and confirm keyboard noise does not dominate
   speech.
5. Watch the voice quality line for connected peer count, RTT, jitter, packet loss,
   and outbound bitrate.
6. Toggle mute/unmute on each side and confirm audio state is reflected on the other
   side.
7. Refresh one client while the other remains connected and confirm the late joiner
   receives the current participant snapshot.
8. Record the result as pass/fail notes only. Do not record raw audio, media device
   labels, ICE candidates, TURN credentials, or user tokens.

Known 2026-06-19 real-device issue:

- Keyboard/tap sounds can transmit while spoken language sounds echoing, unstable,
  or intermittently cut.
- Short words can sound acceptable, but a sustained syllable such as "아" can be
  chopped into repeated audible segments.
- Treat this as a blocker for real voice completion until a manual speech-quality
  pass succeeds.

## Call Recording QA 2026-06-19

The user-provided call recording is stored only in the ignored local folder
`docs/reference-videos/voice-call/`; do not commit recordings or generated analysis
frames.

Automatic checks found:

- Recording length: about 100 seconds.
- Audio tracks: three AAC stereo tracks at 48 kHz.
- Volume: `mean_volume` around -39.5 dB and `max_volume` around -11.1 dB on each
  track.
- Low-volume detection: repeated low-volume/silence sections were present across
  the recording.

Visual checks found before remediation:

- Stopping screen share could leave the previously shared screen visible on the
  other participant.
- Remote screen share was positioned as a detached lower tile instead of being
  integrated into the selected voice workspace.
- The sharing user could not see a real local preview of the shared screen.

Implemented local fix:

- Screen sharing now sends an explicit gateway `VOICE_SIGNAL` screen-state payload.
- Local and remote screen-share video tiles render inside the selected voice
  workspace.
- Stopping screen share clears remote screen tiles.
- `npm run smoke:realtime:browser` now verifies local screen preview, remote screen
  rendering, and remote screen cleanup.

Remaining manual gate:

- The low average volume and long low-volume sections make speech quality suspect,
  but actual Korean/English speech intelligibility must still be judged by a
  human listener using two real accounts and real microphones.
- Refreshing a page still leaves the active call. A separate voice rejoin/recovery
  flow is needed if refresh persistence is required.
- Same-Wi-Fi LAN access over `http://<LAN-IP>` can fail media capture because the
  browser does not treat that origin as a secure context. Use localhost for local
  media tests or add a documented HTTPS LAN development path before claiming LAN
  voice support.

## Stage 11.12 QA Note

The 2026-06-18 Stage 11.12 pass verified backend health, `/api/meta/voice`, and the
gateway HELLO handshake in the local Docker stack. Browser DOM checks also confirmed
that the clone page exposes voice controls without native JavaScript dialogs.

Stage C5/C6 browser automation later verified fake-device microphone join,
two-user voice presence, remote audio sink creation, mute/deafen toggles, and a fake
screen-share path in system Chrome. This remains a code-path smoke only. Treat
real microphone quality, real screen picker UX, LAN media capture, and TURN/NAT
behavior as manual checks using the sections above until a real TURN server and
two physical networks are available.

## Stage C9 Release Gate Note

The 2026-06-19 Stage C9 local release gate passed for:

- Full frontend lint, unit tests, and production build.
- Full backend lint and 124-test backend suite.
- Docker/local health, frontend HTTP, and voice metadata smoke.
- `npm run smoke:realtime:browser`, covering same-PC two-browser server text, DM,
  voice remote audio sink, peer detail visibility, mute/deafen, fake screen-share
  visibility, remote screen-video rendering, and voice leave cleanup.

The post-C9 remediation pass also verifies that abnormal gateway disconnect cleanup
emits voice leave events in backend tests. This does not replace real microphone,
screen-picker, LAN, or TURN/NAT checks.

This is still not a real internet voice completion. The current local metadata
reports `turn_configured: false`, so real microphone quality, real screen picker
UX, different-PC LAN, and TURN/NAT internet voice remain manual release gates.
