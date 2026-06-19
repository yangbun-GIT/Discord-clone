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
- Detailed staged follow-up is tracked in
  `docs/remediation-tasks/manual-qa-followup-2026-06-19.md`.

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
- Related product-flow defects and implementation requirements are tracked in
  `docs/remediation-tasks/friend-relationship-implementation-plan.md`.

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
- Follow-up implementation stages C10-C13 are tracked in
  `docs/remediation-tasks/realtime-communication-plan.md`.

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

## Manual Same-PC QA

1. Open two isolated browser profiles.
2. Sign in as two different users.
3. Create or join one shared server.
4. Send one server text message from user A and confirm user B sees it without
   refresh.
5. Open a DM between the two users.
6. Send one DM from user A and confirm user B sees it without refresh.
7. Join the same voice channel from both sessions.
8. Confirm each session shows the other participant.
9. Confirm peer count reaches one connected peer.
10. Toggle mute and deafen.
11. Start and stop real screen sharing.
12. Refresh one voice-connected session and confirm the same voice workspace stays
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

## TURN/NAT QA

Follow `docs/voice-qa.md#turn--nat-test`. Record:

- ICE server count.
- `turn_configured` value.
- Networks used.
- Browser media permission result.
- Voice peer stability.
- Screen-share result.

Do not mark internet voice complete unless TURN is configured and a real
different-network test passes.
