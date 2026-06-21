# Realtime Communication QA

Use this checklist for Stage C8 and later communication regressions. It separates
automated code-path smoke from real-device and real-network release gates.

## Automated Browser Smoke

Prerequisites:

- Backend is available at `http://127.0.0.1:8000`.
- Frontend is available at `http://127.0.0.1:5173`.
- `npm --prefix frontend install` has installed the official `playwright`
  devDependency.
- On Windows, system Chrome is available at
  `C:\Program Files\Google\Chrome\Application\chrome.exe`, or set
  `CHROME_EXECUTABLE`.

Run:

```powershell
npm run smoke:realtime:browser
```

If the Docker HTTPS LAN stack is running, Vite serves HTTPS only on port `5173`.
Use the HTTPS smoke instead of the default HTTP smoke:

```powershell
npm run smoke:realtime:browser:https
```

For manual local browser checks in that mode, open `https://localhost:5173` or
`https://127.0.0.1:5173`. `http://localhost:5173` and `http://127.0.0.1:5173`
will disconnect with an empty response because the server is not speaking HTTP on
that port.

Optional endpoints:

```powershell
$env:APP_URL = "http://127.0.0.1:5173"
$env:REST_BASE = "http://127.0.0.1:8000"
$env:CHROME_EXECUTABLE = "C:/Program Files/Google/Chrome/Application/chrome.exe"
npm run smoke:realtime:browser
```

The script creates temporary local dev users, a temporary shared guild, an invite,
and a DM. It verifies:

- Server text message appears in a second browser context through gateway dispatch.
- DM message appears in a second browser context through gateway dispatch.
- Friend presence changes dispatch as `PRESENCE_UPDATE` so a second accepted-friend
  session can update Friends presence, and shared server sessions can update
  member-list presence, without a refresh. DM sidebar and DM intro surfaces
  intentionally do not repaint status/activity from lightweight presence updates.
- Two users join the same voice channel with fake microphone devices.
- Remote audio sink appears.
- Voice peer count appears in the voice panel.
- Mute/deafen controls toggle.
- Fake screen-share path becomes visible locally.
- Local screen-share preview appears in the sharing browser context.
- A remote screen-share video tile appears in the second browser context.
- Stopping screen share removes the remote screen-share tile from the second
  browser context.
- Leaving voice removes the remote audio sink from the other browser context.

Privacy rules:

- The script must not print JWTs, message bodies, ICE candidates, TURN credentials,
  media device labels, or DM contents.
- Fake-device success is not a real microphone quality pass.
- Fake screen-share success is not a real screen picker UX pass.

Latest C8 automated result:

- Date: 2026-06-19.
- Command: `npm run smoke:realtime:browser`.
- Result: passed for two-context server text realtime, DM realtime, voice remote
  audio sink, peer detail visibility, mute/deafen toggles, fake screen-share
  visibility, remote screen-video rendering, voice leave cleanup, and zero browser
  errors.
- Scope: same-PC automated fake-device code-path coverage only. It is not a LAN,
  TURN/NAT, real microphone quality, or real screen-picker release gate.

Stage C9 local gate result:

- Date: 2026-06-19.
- Full frontend/backend command suite passed.
- Docker/local health, voice metadata, frontend HTTP, and browser communication
  smoke passed.
- `/api/meta/voice` reported `turn_configured: false`, so TURN/NAT internet voice
  remains incomplete until real TURN credentials and a different-network test pass.

Post-C9 remediation result:

- Date: 2026-06-19.
- Added abnormal voice-disconnect cleanup coverage, Redis zero-subscriber fallback,
  Redis-backed operation limit support, inactive-DM unread handling, and stronger
  remote screen-share/voice-leave browser smoke checks.
- Fixed the remote screen-share stage render condition so a received live video
  track is visible from the selected voice workspace.
- A later screen-share cleanup pass added explicit `VOICE_SIGNAL` screen-state
  dispatch, local screen-share preview rendering, in-workspace screen-share
  placement, and automated stop-cleanup verification.
- Current automated command baseline is:
  - `npm run test:backend`
  - `npm run test:frontend`
  - `npm run lint:backend`
  - `npm run lint:frontend`
  - `npm --prefix frontend run build`
  - `npm run smoke:realtime:browser`
  - `npm run smoke:realtime:redis`

Call recording QA result:

- Date: 2026-06-19.
- Source: local ignored recording under `docs/reference-videos/voice-call/`.
- Privacy: recording and generated analysis frames are ignored by Git and must not
  be committed.
- Container facts: about 100 seconds, 1920x1080, 60 fps, three AAC stereo audio
  tracks at 48 kHz.
- Automatic audio signal result: all three audio tracks had `mean_volume` around
  -39.5 dB and `max_volume` around -11.1 dB, with repeated low-volume/silence
  sections. This supports the user's report that spoken language is not reliable;
  actual intelligibility still requires human listening on the user's machine.
- Visual result before the fix: after screen share stopped, remote screen-share
  tiles could remain visible; remote screen share appeared as a detached lower
  stage; the sharer did not get an actual local screen preview.
- Automated result after the fix: `npm run smoke:realtime:browser` passed with
  local screen preview video count, remote screen video count, remote screen cleanup,
  voice leave cleanup, and zero browser errors.
- Refresh recovery update: refreshing a connected tab still tears down the old
  WebRTC media tracks, but normal websocket disconnects now keep the backend voice
  state through a short grace window instead of immediately broadcasting leave.
  Heartbeat timeout and stale-send cleanup bypass that grace and leave immediately.
  The client stores only same-user voice channel recovery metadata and
  automatically rejoins the previous channel after the refreshed tab's gateway
  reaches `connected`. Browser smoke verifies the connected voice panel, absence
  of the fallback rejoin prompt, and remote audio recovery after automatic rejoin.
  Real browser permission-expiry/denial behavior remains a manual gate.

Manual QA follow-up result:

- Date: 2026-06-19.
- Real microphone capture starts, and short words can sound acceptable.
- Sustained single-syllable speech is not stable: a long "아" can be heard as
  repeated cut segments instead of one continuous sound.
- Real screen sharing starts and stops correctly, but the receiver layout separates
  a sharing user's screen tile from that user's participant state. The next layout
  pass should merge these into one composition per sharing participant.
- Refresh now keeps voice membership through the backend grace window and
  automatically rejoins the previous voice channel after gateway reconnect when
  microphone capture can be reacquired. If capture fails, the explicit app-owned
  Rejoin/Leave path remains visible. Real permission-prompt behavior remains a
  manual browser gate.
- Same-Wi-Fi LAN test failed at voice join because `http://<LAN-IP>` is not a
  secure context for microphone/screen capture.
- TURN/NAT test has not been run and is not ready to claim while
  `/api/meta/voice.turn_configured` is `false`.
- Deafen/소리 차단 does not currently satisfy user expectation; remote audio should
  be muted locally while deafen is active.
- Latest deafen control rule: deafen mutes only remote playback locally.
  Microphone mute remains a separate control and must keep working while deafened.
- API-level owner/member invite permission was checked: owner invite creation
  returned `201`; normal member invite creation returned `403`. Browser
  visibility/disabled-state QA remains pending.
- Detailed staged follow-up was handled in local-only remediation notes. Those
  work documents are intentionally ignored by Git and are not required for
  submitted project execution.

Voice input feedback and gate update:

- Date: 2026-06-20.
- User-visible issue: connected voice users did not get clear visual feedback when
  microphone input entered the clone, and long sustained sounds could still pulse
  because the input gate closed after the processed signal dipped.
- Fix: local speaking state now follows the current RMS input-level path with a
  short release hold instead of the older frequency-bin VAD path. The input meter
  samples before RNNoise/gate attenuation, the sensitivity gate holds open longer
  for sustained speech, and a closed gate softly attenuates rather than fully
  cutting audio. The voice workspace tile, sidebar voice-channel row, and lower
  user card now react visually to input. Remote received audio streams are analyzed
  locally so remote participant cards can show speaking feedback.
- Verification: frontend lint, frontend tests, production build, and
  `CHROME_EXECUTABLE="C:/Program Files/Google/Chrome/Application/chrome.exe"
  npm run smoke:realtime:browser` passed with `voiceRemoteAudioSinks: 1` and
  `browserErrors: 0`.
- Remaining manual gate: the user still needs to run a real sustained vowel and
  fan/wind-noise listening test because fake-device automation cannot judge speech
  intelligibility.

Sustained input stability and input-level privacy update:

- Date: 2026-06-20.
- Source: user-provided OBS recordings
  `C:/Users/yangbun/Videos/OBS/마이크_실제입력.mp4` and
  `C:/Users/yangbun/Videos/OBS/마이크_데스크탑 오디오.mp4`.
- Finding: ffmpeg `silencedetect` found the raw microphone recording stayed
  continuous except for start/end silence, while the desktop-audio capture had
  repeated short silent gaps throughout the spoken segment. This points to the
  clone/browser/app processing path, not the raw microphone, as the primary
  dropout source.
- Fix: the speech-stability preset now disables browser echo cancellation, noise
  suppression, and auto gain by default. RNNoise and the app input sensitivity
  gate default off, with a one-time migration for existing default local settings.
  This keeps the outgoing microphone path more continuous for long vowels and
  leaves noise reduction/gating as explicit user choices.
- Privacy: exact live input amount is visible only inside Voice & Video settings.
  Main voice workspace tiles, the server sidebar voice row, the lower user card,
  and remote participant cards expose only binary speaking feedback. The quick
  microphone popover displays configured sensitivity percent instead of live input
  level.
- Remaining manual gate: real listening is still required for sustained vowel,
  fan/wind noise, and echo behavior because automated fake-device tests cannot
  evaluate speech intelligibility.

Voice option behavior audit:

- Date: 2026-06-20.
- Default baseline: keep RNNoise and the input sensitivity gate off by default
  because this is the stable real-microphone path for sustained speech.
- Input volume: updates the Web Audio input gain during the active call.
- Input sensitivity: changes the speaking threshold and, when the input
  sensitivity gate is enabled, the actual transmit gate threshold.
- Input sensitivity gate: optional. When enabled, the selected sensitivity now
  strongly attenuates input below the threshold; higher sensitivity can block quiet
  speech/background sound, while lower sensitivity keeps more sound open.
- RNNoise: optional. It is created as an AudioWorklet during microphone processor
  setup, so changes apply on the next voice join.
- Echo cancellation, noise suppression, and auto gain: browser capture constraints;
  changes are stored immediately but apply on the next microphone capture.
- Settings copy must keep this distinction visible so users do not expect the
  stable default path to behave like a live noise gate.

Voice settings input-meter usability update:

- Date: 2026-06-20.
- Source reference: user-provided Discord input-sensitivity recording
  `C:/Users/yangbun/Videos/OBS/디스코드 입력감도.mp4`.
- Discord behavior observed: the input sensitivity threshold is shown on the same
  horizontal control as a live input/activity meter, so users can see ambient room
  noise and move the threshold above that baseline.
- Clone behavior: Voice & Video settings now use a clearer live input-level
  overlay on the sensitivity track and show `input / sensitivity` values in
  settings only. Workspace, sidebar, lower user card, and remote participant UI
  still expose only binary speaking feedback.
- Routing: voice input/output popover setting buttons open the Voice & Video
  settings panel directly instead of landing on My Account.
- Layout: lower-left input/output popovers align both left and right edges with
  the lower user status card.

Screen-share participant composition update:

- Date: 2026-06-19.
- Remote sharing users now render as one screen-share participant composition, not
  both a screen tile and a duplicate participant tile.
- `npm run smoke:realtime:browser` verifies `remoteSharingUserScreenTiles: 1` and
  `duplicateRemoteSharingParticipantCards: 0`.

Voice participant consistency update:

- Date: 2026-06-20.
- User-visible issue: after two accounts joined the same voice channel, one account
  could show both participants while the other showed only itself.
- Root cause fixed in the client join order: the browser previously started
  WebRTC peer sync from any locally known participants before the backend had
  accepted that user's `UPDATE_VOICE_STATE`. This could send offers before the
  backend considered the sender connected to the voice channel.
- Fix: `useVoiceSessionController.ts` now starts local media with an empty initial
  participant list. Peer creation waits for gateway `VOICE_STATE_UPDATE` and
  `VOICE_STATE_SNAPSHOT` reconciliation after the user's voice state is registered.
- Verification: `CHROME_EXECUTABLE="C:/Program Files/Google/Chrome/Application/chrome.exe"
  npm run smoke:realtime:browser` passed with `voiceRemoteAudioSinks: 1`,
  `voicePeerDetailVisible: true`, `voiceRejoinRecovered: true`, and
  `browserErrors: 0`. Backend logs for the post-fix window showed no new
  `voice signal rejected` entries.

WebRTC signaling collision update:

- Date: 2026-06-20.
- User-visible issue: the B account could show
  `Failed to execute 'createAnswer' on 'RTCPeerConnection'` when duplicate, stale,
  or glare-related voice offers reached a peer after its signaling state had moved
  past `have-remote-offer`.
- Fix: `frontend/src/composables/voicePeerConnections.ts` now queues incoming
  voice signals per peer, rechecks active channel/user state before each queued
  operation, ignores stale remote descriptions, creates answers only from
  answerable states, and applies answers only while a local offer is pending.
- Verification: frontend lint, frontend tests, production build, and
  `CHROME_EXECUTABLE="C:/Program Files/Google/Chrome/Application/chrome.exe"
  npm run smoke:realtime:browser` passed with `voiceRemoteAudioSinks: 1`,
  `voicePeerDetailVisible: true`, `voiceRejoinRecovered: true`, and
  `browserErrors: 0`.

WebRTC m-line order recovery update:

- Date: 2026-06-20.
- User-visible issue: the A account could show
  `Failed to execute 'setLocalDescription' ... The order of m-lines in subsequent
  offer doesn't match order from previous offer/answer` when joining voice after
  prior peer negotiation activity.
- Cause: outbound offer creation and renegotiation were not serialized with the
  existing per-peer incoming signal queue, so participant sync or screen-share
  renegotiation could race with inbound offer/answer processing on the same
  `RTCPeerConnection`.
- Fix: `voicePeerConnections.ts` now queues outbound offer creation and
  renegotiation per peer. If Chrome still rejects an offer because the peer's SDP
  m-line order is corrupted, the affected peer is closed and rebuilt before the
  lower user ID attempts a fresh offer.
- Verification: frontend lint, frontend tests, production build, and
  `CHROME_EXECUTABLE="C:/Program Files/Google/Chrome/Application/chrome.exe"
  npm run smoke:realtime:browser` passed with `browserErrors: 0`.

Manual two-account product-flow result:

- Date: 2026-06-19.
- Scope: same-PC Chrome tabs using user A at `localhost:5173` and user B at
  `127.0.0.1:5173`.
- Existing DM text exchange worked in both directions, including unread badge and
  stored message visibility.
- Valid invite-code join could add user B to user A's server, but success feedback
  and automatic routing into the server were insufficient.
- Stale or mismatched invite-code join did not expose a clear app-owned error.
- Server text became visible after user B joined and user A opened the channel.
- User B could select the shared voice channel, but stayed in selected/pre-join
  state without a clear Join action; user A did not see user B as a voice
  participant.
- Browser microphone permission that was not answered produced an app-owned voice
  problem notice, so real voice QA must explicitly include permission grant and
  denial branches.
- Related product-flow defects were handled in local-only remediation notes. The
  submitted repository keeps only the current implementation and QA summary.

Manual two-account voice/product recheck:

- Date: 2026-06-19.
- Scope: same-PC Chrome tabs using user A at `localhost:5173`, user B at
  `127.0.0.1:5173`, plus a controlled B tab where the user's second Chrome profile
  was not automatable.
- User-reported real microphone result: keyboard/tap sounds were transmitted, but
  spoken language sounded echoing, unstable, or intermittently cut. This remains a
  real-device audio-quality blocker and is not covered by fake-device smoke.
- Server text passed both directions after both accounts were in the server.
- Existing DM passed both directions; inactive-recipient unread and later message
  visibility worked.
- Voice participant synchronization failed the user-visible quality bar: B could
  show only itself in the voice workspace while A/B were both connected or while A
  could see B elsewhere in the voice UI.
- Code review found a likely root cause: gateway voice state is event-only and does
  not provide a current voice-state snapshot to late joiners or newly identified
  clients.
- A controlled B tab could select the voice channel but remain in preview/pre-join
  state without a prominent workspace Join action.
- Member invite controls exposed a raw English permission error
  `create invite permission required`; this should become localized app-owned UX and
  unauthorized invite controls should be hidden or disabled.
- Follow-up implementation stages were handled in local-only remediation notes.
  This submitted QA document records the resulting behavior and remaining manual
  verification boundaries.

Chrome profile control note:

- Date: 2026-06-19.
- The two visible clone accounts can live in separate Chrome profiles. In this case,
  the automation surface exposes separate extension browser instances.
- Known profile mapping for the current local QA setup:
  - `minruel`: A tab at `http://localhost:5173/`.
  - `jbnu.ac.kr`: B tab at `http://127.0.0.1:5173/`.
- If only one clone tab is listed, inspect available extension browser instances and
  choose the profile that owns the missing tab before concluding the tab is
  unavailable.
- If a real profile cannot be controlled, fall back to the project Playwright smoke
  or open a controlled second tab with the local QA account procedure. Do not inspect
  browser cookies, local storage, saved passwords, or session stores.

Voice architecture note:

- Current implementation correctly uses WebSocket for signaling and WebRTC for
  media transport.
- Raw WebSocket microphone transport is rejected for clone completion because it
  would bypass browser-native WebRTC media handling.
- WebRTC P2P remains acceptable for immediate local two-user remediation.
- SFU-backed WebRTC, preferably a managed/open-source stack such as LiveKit unless a
  lower-level mediasoup integration is specifically justified, is the best long-term
  path for Discord-like multi-user voice channels.

DM private voice boundary update:

- Date: 2026-06-20.
- Backend gateway voice payloads now distinguish `guild` and `dm` voice contexts.
  DM private calls route voice state snapshots and WebRTC offer/answer/ICE/screen
  signals through subscribed DM rooms instead of guild voice-channel subscribers.
- Frontend Friends and selected-DM call actions now open the one-to-one DM and
  join a DM-scoped private WebRTC room. The bottom voice panel remains the shared
  mute/deafen/screen-share/leave surface, and the DM view renders an active call
  stage.
- Automated verification: Docker backend gateway tests passed with DM-only signal
  routing and DM voice-state snapshot coverage; frontend lint, frontend tests, and
  production build passed.
- Manual QA still needed: two real accounts should start a DM call from Friends
  and from an open DM, confirm both sides hear each other, then verify guild voice
  channel calls still work after leaving the DM call.

## Manual Same-PC QA

1. Open two isolated browser profiles.
2. Sign in as two different users.
3. Create or join one shared server.
4. Send one server text message from user A and confirm user B sees it without
   refresh.
5. Open a DM between the two users.
6. Send one DM from user A and confirm user B sees it without refresh.
7. Start a DM call from the DM header and confirm the other session joins the same
   DM voice room, with remote audio and bottom voice controls visible.
8. Leave the DM call, then join the same server voice channel from both sessions.
9. Confirm each session shows the other participant.
10. Confirm peer count reaches one connected peer.
11. Toggle mute and deafen.
12. Start and stop real screen sharing.
13. Refresh one voice-connected session and confirm the same voice workspace stays
    open, the bottom voice panel returns to connected state, and the other session
    receives the rejoined participant/audio again.

## LAN QA

Follow `docs/voice-qa.md#lan-smoke-test`. Record:

- Host IP.
- Frontend URL.
- Backend health URL.
- Whether `/gateway` stays connected.
- Whether text, DM, and voice participant state work from another device.

LAN success is not TURN/NAT internet success.

## Cloudflare Tunnel QA

Follow `docs/assignment-submission-guide.md#optional-cloudflare-tunnel-demo` and
`docs/voice-qa.md#optional-cloudflare-tunnel-external-access` when a temporary
public HTTPS URL is needed for a submission demo.

Record:

- Local stack mode: normal Docker HTTP origin, Docker HTTPS LAN stack, or the
  HMR-free `frontend-tunnel` origin.
- Tunnel command used.
- Generated public origin domain only, not any Cloudflare token.
- Whether the app loads through HTTPS.
- Whether `/api/health` succeeds through the public origin.
- Whether `/gateway` connects over WSS.
- Whether server text and DM realtime pass in two sessions.
- Whether `/api/meta/voice/readiness.turn_configured` is `true` before attempting
  different-network voice.
- Whether voice, mute/deafen, and screen share pass from two different networks.

Cloudflare Tunnel success for page/API/WebSocket access is not the same as
TURN/NAT voice success. The tunnel carries HTTP and WebSocket signaling; WebRTC
media still needs valid STUN/TURN behavior between browsers.

2026-06-20 Cloudflare Quick Tunnel check:

- Local origin: `frontend-tunnel` from `compose.cloudflare-tunnel.yaml`, serving
  the built frontend through Nginx on `http://localhost:5174`.
- Tunnel command: `cloudflared tunnel --url http://localhost:5174`.
- Temporary public origin: a generated `https://*.trycloudflare.com` hostname.
  The exact hostname was not recorded as a stable deployment URL.
- Public frontend load: passed with the auth surface visible and zero browser
  console errors in a page-load probe.
- Public API: `/api/health` and `/api/meta/voice/readiness` passed.
- Public WSS gateway: `npm run check:deployment:readiness` passed with
  `gateway_hello: true`.
- Public automated realtime: `APP_URL` and `REST_BASE` pointed at the temporary
  Cloudflare origin; `npm run smoke:realtime:browser` passed with server text,
  DM, invite DM, gateway dispatch, fake-media voice, fake screen share, refresh
  recovery, cleanup, and `browserErrors: 0`.
- Limit: this does not complete real external voice/screen-share QA because
  `turn_configured` was `false` and no two-network real media test was performed.

2026-06-20 external-network manual QA status:

- Codex reran the automated public-origin checks against the active temporary
  Cloudflare URL. `/api/health`, `/api/meta/voice/readiness`, WSS `/gateway`
  HELLO, and the public-origin browser realtime smoke all passed with
  `browserErrors: 0`.
- Manual two-network checks remain pending because they require a second physical
  device on a different network. Use
  `docs/assignment-submission-guide.md#cloudflare-external-network-manual-qa-checklist`
  to run the human pass.
- Record any manual failures as one of: auth, server invite, friend request, DM,
  server text, gateway reconnect, voice permission, voice media, screen-share, or
  refresh recovery.
- Do not upgrade the media status beyond "Cloudflare signaling path verified,
  TURN/NAT media gate incomplete" while `turn_configured` remains `false`.

2026-06-20 hotspot manual QA result:

- Topology: local development PC on the home network, notebook on a phone hotspot,
  both using the active Cloudflare Quick Tunnel HTTPS URL.
- User-observed result: DM send/receive worked across the two networks.
- User-observed result: voice call speaking and listening worked across the two
  networks.
- Automated public-origin checks were rerun in the same pass and still passed:
  `/api/health`, `/api/meta/voice/readiness`, WSS `/gateway` HELLO, and
  public-origin `npm run smoke:realtime:browser` with `browserErrors: 0`.
- Status wording: "specific hotspot external-network STUN/P2P voice success."
  Do not call this universal external-network media completion because
  `turn_configured` remained `false`.
- Next work is not final submission packaging. Continue with unresolved design
  polish and feature-completion remediation before the final submission pass.

## TURN/NAT QA

Follow `docs/external-deployment-decision.md` and
`docs/voice-qa.md#turn--nat-test`. The selected first external QA topology is
single VM Docker Compose with Caddy HTTPS and TURN configured through environment
variables. Record:

- ICE server count.
- `turn_configured` value.
- Networks used.
- Browser media permission result.
- Voice peer stability.
- Screen-share result.

Do not mark internet voice complete unless TURN is configured and a real
different-network test passes.

Before the manual two-network call, run the safe external deployment check:

```powershell
$env:DEPLOYMENT_ORIGIN = "https://<domain>"
$env:REQUIRE_TURN = "1"
npm run check:deployment:readiness
```

Pass criteria for the readiness step:

- `secure_origin` is `true`.
- `/api/health` returns healthy service data.
- `/api/meta/voice/readiness.turn_configured` is `true`.
- `/gateway` sends HELLO over WSS.

This readiness step does not complete the media gate. It only proves the deployed
origin is ready for the manual different-network voice and screen-share test.

## 2026-06-21 Voice Refresh Regression

The HTTPS browser smoke now covers the specific receiver-refresh path:

1. Two browser sessions join the same voice channel.
2. Session A starts screen sharing.
3. Session B refreshes while A is still sharing.
4. B auto-rejoins voice.
5. B must receive A's active screen share and a remote audio sink.
6. A stops screen sharing, and B must clear the remote screen tile.

The fix adds a non-secret `session_id` to WebRTC voice signaling and voice-state
snapshots so a refreshed browser is treated as a new RTC media session instead
of reusing a stale peer.
Latest automated HTTPS result passed with
`remoteScreenVideosAfterReceiverReload: 1`,
`receiverAudioSinksAfterReload: 1`, `remoteScreenCleared: true`,
`voiceRejoinRecovered: true`, and `browserErrors: 0`.

## 2026-06-21 Screen-Share Refresh Repair Follow-Up

User testing still found a narrower real-browser case after the refresh recovery:
voice reconnects after B refreshes, but A's already-active shared screen can appear
black or missing on B. The frontend P2P path now adds a second repair layer:

- Screen-share video elements are muted and replayed when stream tracks or media
  metadata change.
- If a peer is marked as screen sharing but no active remote video track appears,
  the receiver schedules a bounded peer repair.
- Incoming offers recreate an already-used peer so the answerer can reattach the
  current screen track to a fresh `RTCPeerConnection`.
- A user who is already screen sharing proactively renegotiates with later or
  rejoined participants during voice participant sync.
- Participant sync resets an existing peer when the voice-state snapshot reports
  a different session id for the same remote user.
- If a refreshed receiver has a screen-share tile but no usable video track, it
  sends a `screen-repair` signal so the active screen sharer creates the next
  offer with the current display track attached.

Verification passed for `npm run lint:frontend`, `npm run test:frontend`,
`npm --prefix frontend run build`, `npm run lint:backend`,
`npm run test:backend`, `git diff --check`, and
`npm run smoke:realtime:browser:https`. The HTTPS smoke returned
`remoteScreenVideosAfterReceiverReload: 1`,
`receiverAudioSinksAfterReload: 1`, `remoteScreenCleared: true`,
`voiceRejoinRecovered: true`, and `browserErrors: 0`.

## 2026-06-21 Screen-Share Cancel Regression Check

The display-capture picker cancel/deny path is intentionally separated from voice
connection failure handling:

- `NotAllowedError` and `AbortError` from `getDisplayMedia` are normalized to a
  screen-share cancellation notice.
- The app should render exactly one app-owned notice with a retry action.
- The voice connection error card, top-right workspace error, and bottom workspace
  banner should not duplicate that same cancel event.
- This does not complete real screen sharing; it only verifies that cancelling the
  picker is a clean, non-fatal UX path.
