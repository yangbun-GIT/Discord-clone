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

3. Open `http://<host-ip>:5173` from the second device for text/gateway reachability
   only.
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

If microphone or screen sharing is blocked from `http://<host-ip>`, this is expected
for many browsers because LAN HTTP is not a secure context. Use the HTTPS LAN media
path below or run media-capture checks from localhost.

### HTTPS LAN Media Path

Use this path when the second device must test real microphone or screen capture.

1. Prepare a locally trusted development certificate for the host IP or DNS name
   that the second device will open. The certificate subject/SAN must match that
   address. Do not commit certificate private keys.
2. Trust the certificate on the second device.
3. Start the backend:

   ```powershell
   npm run dev:backend:lan
   ```

4. Start the HTTPS LAN frontend in another shell:

   ```powershell
   $env:VITE_HTTPS_KEY_FILE="C:\path\to\host-ip-key.pem"
   $env:VITE_HTTPS_CERT_FILE="C:\path\to\host-ip-cert.pem"
   $env:VITE_BACKEND_PROXY_TARGET="http://127.0.0.1:8000"
   npm run dev:frontend:lan:https
   ```

5. Open `https://<host-ip>:5173` from the second device.
6. Confirm the browser reports a secure origin, then test login, gateway,
   server/DM text, voice join, mute/unmute, deafen, and screen share.
7. If the browser still reports an insecure context, fix certificate trust or SAN
   mismatch before testing media again.

### Docker HTTPS LAN Media Path

Use this when the local stack is running through Docker Compose.

1. Generate a certificate for the exact host IP or DNS name opened by the notebook:

   ```powershell
   .\scripts\create_lan_https_cert.ps1 -HostName <host-ip>
   ```

   The script writes `certs/lan-dev.pfx` and `certs/lan-dev-root-ca.cer`, then
   prints the Root CA thumbprint and the server certificate thumbprint. The
   `certs/` folder is ignored by Git.

2. Copy `certs/lan-dev-root-ca.cer` to the notebook and trust it under
   `Trusted Root Certification Authorities` for browser/server authentication.
   Compare the OS warning thumbprint with the script's `Root CA thumbprint` before
   accepting. Keep `lan-dev.pfx` on the development host.

3. Start the HTTPS Docker stack:

   ```powershell
   npm run docker:up:https:detached
   ```

4. Open `https://localhost:5173` or `https://127.0.0.1:5173` on the development
   PC, and `https://<host-ip>:5173` from the notebook. Do not use `http://...` on
   port `5173` while this stack is running; the frontend is HTTPS-only in this
   mode and HTTP tabs will disconnect with an empty response.
5. Confirm `https://<host-ip>:5173/api/health` works and the browser shows a secure
   origin before testing microphone, voice join, mute/unmute, screen sharing, and
   gateway reconnect.
6. If media is still blocked, check certificate trust on the notebook and confirm
   the certificate SAN matches the URL host exactly.
7. For same-PC automated verification in this mode, run:

   ```powershell
   npm run smoke:realtime:browser:https
   ```

## TURN / NAT Test

Read `docs/external-deployment-decision.md` before running this section. The
selected first external QA path is a single VM Docker Compose deployment with
Caddy HTTPS and TURN configured through environment variables. Keep this section
pending until the VM/domain/TURN resources exist.

1. Set production-like ICE servers in `.env` or the host secret store:

   ```powershell
   WEBRTC_ICE_SERVERS_JSON=[{"urls":"stun:stun.l.google.com:19302"},{"urls":"turn:turn.example.com:3478","username":"replace-me","credential":"replace-me"}]
   ```

2. Restart the backend and run the safe readiness check:

   ```powershell
   npm run check:voice:readiness
   ```

3. Confirm `turn_configured` is `true`. The readiness check must not print TURN
   credentials, ICE candidates, tokens, or media device labels.
4. For deployed hosts, run the combined safe readiness check:

   ```powershell
   $env:DEPLOYMENT_ORIGIN = "https://<domain>"
   $env:REQUIRE_TURN = "1"
   npm run check:deployment:readiness
   ```

   This checks `/api/health`, `/api/meta/voice/readiness`, and `/gateway` over WSS
   without identifying a user or printing credentials.
   For local self-signed HTTPS development only, add
   `DEPLOYMENT_IGNORE_TLS_ERRORS=1`; do not use it for final external QA.
5. Repeat the two-session voice test across two different networks, such as home
   Wi-Fi and mobile hotspot.
6. Watch the voice quality line for persistent packet loss, high jitter, or
   unstable peer counts.

Release gate:

- LAN pass: same network, same development host, text/gateway/voice reachable.
- TURN/NAT pass: different networks, `/api/meta/voice/readiness.turn_configured` is `true`,
  and media works through a configured TURN-capable ICE list.
- Do not mark internet voice complete from fake-device or LAN-only tests.

## Deployment Verification

Run this after deploying behind HTTPS:

- `GET /api/health` returns `status: ok`.
- `/api/meta/voice/readiness` returns the expected ICE server count and
  `turn_configured: true` without credentials.
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

For screen-share quality triage and the P2P-versus-SFU decision tree, read
`docs/voice-transport-architecture.md`. In short: tune P2P capture constraints,
sender bitrate/framerate, and CSS rendering first when 1:1 screen share is poor;
consider SFU only when multi-viewer or simultaneous screen-share load breaks an
otherwise acceptable P2P baseline.

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
7. Toggle deafen on one side and confirm the independent control behavior:
   - The deafened user cannot hear remote participants.
   - The deafened user's microphone remains controlled only by the separate
     mute/unmute button.
   - While deafened, mute/unmute still toggles the local microphone track without
     changing the deafen state.
   - Screen sharing remains available while deafened.
8. Refresh one client while the other remains connected and confirm:
   - The refreshed client returns to the same voice workspace.
   - The backend does not immediately remove the refreshed user from the other
     client's participant list during the normal reconnect grace window.
   - The bottom voice panel returns to connected state without requiring a manual
     channel click when microphone permission can be reacquired.
   - The other client sees the refreshed user rejoin and receives remote audio.
   - If browser microphone capture is blocked, the app-owned rejoin notice remains
     available with Rejoin and Leave actions.
9. Record the result as pass/fail notes only. Do not record raw audio, media device
   labels, ICE candidates, TURN credentials, or user tokens.

Known 2026-06-19 real-device issue:

- Keyboard/tap sounds can transmit while spoken language sounds echoing, unstable,
  or intermittently cut.
- Short words can sound acceptable, but a sustained syllable such as "?? can be
  chopped into repeated audible segments.
- A 2026-06-20 remediation added app-level input/output device settings, input
  volume, output volume, input sensitivity, and a local Web Audio sensitivity gate
  before WebRTC peer tracks are created.
- A later 2026-06-20 remediation added optional client-side RNNoise denoising
  before WebRTC transmission. The stable default remains `Off`; RNNoise from
  `@sapphi-red/web-noise-suppressor` is the only retained denoiser after manual
  fan-noise comparison found it more useful than the removed SpeexDSP and DTLN
  candidates. Treat real voice completion as blocked until a manual speech-quality
  pass checks RNNoise against fan/wind pickup, keyboard noise, CPU cost, latency,
  and sustained-vowel chopping.

Stage M1 remediation note:

- The clone no longer relies on only individual browser audio-processing toggles.
  User settings now provide three microphone processing presets:
  - Speech stability: echo cancellation on, noise suppression off, auto gain on.
    Use this first when sustained vowels are chopped.
  - Balanced: echo cancellation on, noise suppression on, auto gain off.
  - Near raw: echo cancellation, noise suppression, and auto gain all off for
    isolating browser-processing artifacts.
- Changes apply the next time the user joins a voice channel.
- The app's local VAD is diagnostic-only for speaking state and does not own the
  public input-level meter, gate outgoing microphone audio, or disable outgoing
  microphone audio.
- The post-M10 voice settings pass adds a separate Web Audio processing path:
  optional RNNoise denoising when AudioWorklet/WASM is available, high-pass
  filtering, light compression, microphone input volume, and adjustable
  sensitivity/noise gate. RNNoise is controlled through User Settings -> Voice &
  Video or the bottom microphone quick popover.
- The input sensitivity control overlays the current input level and transmission
  threshold on the same track. If the level bar stays below the thumb, the gate
  will eventually close. If the level bar stays above the thumb during a sustained
  vowel, the gate should remain open.
- Lower sensitivity if long vowels are chopped; raise sensitivity if fan/wind noise
  opens the microphone too often. Keep denoising set to `Off` for the baseline
  test, then compare RNNoise after leaving and rejoining the voice channel.
- Output volume and supported output-device routing are applied to remote audio
  sinks through the bottom headphones quick popover or User Settings -> Voice &
  Video.

Current sustained-vowel QA:

1. Open User Settings -> Voice & Video.
2. Select Speech stability.
3. Set the denoiser engine to `Off`, keep Noise Gate off for the baseline, set
   Input Volume near 80%, and start Input Sensitivity around 30-40%.
4. Leave and rejoin the voice channel if the input device, denoiser engine, or
   audio-processing preset changed.
5. Say a single vowel continuously for at least 10 seconds.
6. Watch the combined input-level/sensitivity track. If the sustained sound is
   chopped while the level bar is above the thumb, record it as a gate bug. If the
   level bar drops below the thumb, lower Input Sensitivity by 5-10 points and
   repeat. If fan/wind noise opens the mic too often, raise Input Sensitivity by
   5-10 points and repeat.
7. Repeat with a normal Korean sentence and a short English sentence.
8. If sustained audio is still chopped after sensitivity tuning, test Balanced and
   Near raw, leaving and rejoining after each preset change.
9. Compare denoising in this order: Off baseline, then RNNoise. Leave and rejoin
   after changing the denoiser setting. Record whether fan/wind noise, keyboard
   noise, speech naturalness, sustained vowels, and perceived delay improve or
   degrade.
10. Record only pass/fail notes and visible quality stats. Do not record raw audio,
   device labels, ICE candidates, TURN credentials, or user tokens.

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
- Refreshing a page still replaces the underlying WebRTC media session, but normal
  websocket disconnects now get a short backend voice-state grace window and the
  app automatically rejoins the previous voice channel after the refreshed tab's
  gateway reconnects. Real browser permission-expiry and denial behavior must still
  be checked manually.
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

## Manual LAN Result 2026-06-20

The same-Wi-Fi notebook HTTPS path passed for real voice after the local root CA and
host-IP certificate flow was corrected. Treat this as a LAN pass only. It does not
prove public internet/NAT voice, because the current deployed TURN gate still
requires a TURN-configured HTTPS/WSS host and two different networks.
