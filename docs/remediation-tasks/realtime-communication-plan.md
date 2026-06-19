# Realtime Communication Implementation Plan

## Purpose

This document is the implementation plan for making the Discord clone's
communication stack reliable for real multi-user use across browsers, PCs, and
network environments.

It is controlled by `docs/prompts/realtime-communication-implementation-prompt.md`.
Before implementation, read this document with:

1. `DEVELOPMENT_PROMPT.md`
2. `AGENTS.md`
3. `PROJECT_CONTEXT.md`
4. `docs/project-file-map.md`
5. `docs/structure-map/reference-map.md`
6. `docs/deployment.md`
7. `docs/voice-qa.md`

## Date And Source Check

- Plan date: 2026-06-19
- Current implementation stack checked locally against repository files.
- Current external references checked from official or primary sources:
  - MDN `getUserMedia()` secure-context and permission behavior:
    https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
  - MDN media constraints:
    https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints
  - MDN `RTCPeerConnection`:
    https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection
  - FastAPI WebSocket docs:
    https://fastapi.tiangolo.com/advanced/websockets/
  - Redis Pub/Sub docs:
    https://redis.io/docs/latest/develop/pubsub/
  - Socket.IO docs:
    https://socket.io/docs/v4/
  - LiveKit docs:
    https://docs.livekit.io/intro/overview/
  - mediasoup docs:
    https://mediasoup.org/documentation/overview/
  - PeerJS docs:
    https://peerjs.com/client/getting-started
  - coturn TURN server repository:
    https://github.com/coturn/coturn

## Current Communication Audit

### Preflight Blockers To Resolve First

These items must be handled before Stage C1 is allowed to claim a clean baseline:

- Backend virtual environment:
  - R9 QA found that `.venv/Scripts/python.exe` exists but failed to create a
    process in the current PowerShell shell.
  - The system `py` launcher and plain `npm` command were not available in PATH.
  - Stage C0 must either repair `.venv`, recreate it, or document and use an
    equivalent backend test runner before C1 command verification is considered
    complete.
- Browser automation:
  - Playwright package is available, but the bundled Chromium browser was missing.
  - The installed Chrome channel worked for headless smoke tests. Use Chrome
    channel first unless Playwright browsers are installed explicitly.
- Existing local services:
  - `http://127.0.0.1:5173/` and `http://127.0.0.1:8000/api/health` were reachable
    during the R9 pass.
  - Treat that as a starting observation only; C1 must re-run health and gateway
    checks after any environment repair.
- Git tracking:
  - This plan may be untracked in a resumed workspace. Before implementation
    commits, ensure `docs/remediation-tasks/realtime-communication-plan.md` is
    staged and committed with the communication work.

### Backend Gateway

Current owner files:

- `backend/app/gateway/router.py`
- `backend/app/gateway/manager.py`
- `backend/app/gateway/connection.py`
- `backend/app/gateway/subscriptions.py`
- `backend/app/gateway/broadcaster.py`
- `backend/app/gateway/voice_service.py`
- `backend/app/gateway/zombie_reaper.py`
- `backend/app/gateway/opcodes.py`
- `backend/app/gateway/events.py`

Current state:

- WebSocket endpoint is `/gateway`.
- Server sends Discord-style `HELLO`.
- Client sends `IDENTIFY` with JWT.
- Gateway validates token and subscribes the connection to guild, channel, and DM
  IDs loaded from current services.
- Gateway supports heartbeat, member chunk placeholder, voice state update, and
  voice signaling.
- `ClientConnection.send()` increments a per-connection sequence number for
  dispatch events.
- Gateway rejects unauthenticated or unauthorized voice state/signal attempts with
  close codes.

Current gaps:

- Frontend reconnect is not complete enough for real network interruptions.
- Dispatch sequence is per connection and not a cross-process replay/resume
  contract.
- No client-side duplicate suppression contract is documented for REST response
  plus gateway dispatch races.
- Backpressure/rate limiting for gateway messages and voice signaling needs a
  focused pass.
- Structured communication logs are limited.

### Redis Fan-Out

Current owner files:

- `backend/app/realtime/redis_bus.py`
- `backend/app/realtime/publisher.py`
- `backend/app/realtime/subscriber.py`
- `backend/app/realtime/fanout.py`
- `backend/app/main.py`

Current state:

- Redis is optional.
- When `REDIS_URL` is absent, local single-process development still works.
- `RedisBus` can connect, publish JSON, expose client, and disconnect.

Current gaps:

- Multi-instance Redis Pub/Sub behavior needs a repeatable Docker/deployment smoke.
- Delivery semantics need to state that Redis Pub/Sub is live fan-out, not durable
  message storage.
- Redis subscriber failure logging and restart behavior need verification.

### Text And DM Realtime

Current owner files:

- `backend/app/api/routes/channels.py`
- `backend/app/api/routes/dms.py`
- `backend/app/realtime/publisher.py`
- `frontend/src/composables/useGateway.ts`
- `frontend/src/stores/guilds.ts`
- `frontend/src/stores/channelMessages.ts`
- `frontend/src/stores/dms.ts`
- `frontend/src/stores/dmGatewayHandlers.ts`
- `frontend/src/stores/guildGatewayHandlers.ts`

Current state:

- Messages persist through REST.
- Backend publishes realtime events after create/update/delete mutations.
- Frontend applies gateway events to guild and DM stores.

Current gaps:

- Two-session text/DM realtime must be verified after every communication stage.
- Optimistic update, REST response reconciliation, duplicate gateway dispatch, and
  refresh ordering need one documented policy.
- Reconnect after a message send needs a reconciliation path from REST state.

### Voice And Screen Sharing

Current owner files:

- `backend/app/api/routes/meta.py`
- `backend/app/gateway/router.py`
- `backend/app/gateway/voice_service.py`
- `frontend/src/composables/useVoiceSessionController.ts`
- `frontend/src/composables/useVoiceRtc.ts`
- `frontend/src/composables/voiceMedia.ts`
- `frontend/src/composables/voicePeerConnections.ts`
- `frontend/src/composables/voiceStats.ts`
- `frontend/src/composables/voiceVad.ts`
- `frontend/src/stores/voicePresence.ts`
- `frontend/src/components/VoicePanel.vue`
- `frontend/src/components/VoiceAudioSink.vue`
- `frontend/src/components/VoiceVideoSink.vue`

Current state:

- Voice join/leave/switch is driven by gateway voice state.
- Browser microphone capture and screen-share track handling are split into
  composables.
- Voice signaling uses WebRTC offer/answer/ICE over the gateway.
- Frontend collects WebRTC quality stats and local speaking/input level.
- `/api/meta/voice` exposes ICE server count and TURN readiness.

Current gaps:

- Real microphone and screen-capture permission QA remains manual.
- TURN is configuration-ready but not verified with a real TURN server.
- Noise suppression should first use browser-native media constraints and only then
  consider heavier processing.
- Voice stale-session cleanup and disconnect on tab close/reload need explicit
  browser lifecycle verification.

### LAN And Deployment

Current owner files:

- `compose.yaml`
- `backend/app/core/config.py`
- `frontend/src/services/browserApi.ts`
- `docs/deployment.md`
- `docs/voice-qa.md`

Current state:

- Docker and native local modes exist.
- Production notes require a single HTTPS reverse proxy for `/api` and `/gateway`.
- `WEBRTC_ICE_SERVERS_JSON` supports STUN/TURN configuration.

Current gaps:

- Cross-PC LAN access needs explicit frontend host binding, API URL, gateway URL,
  firewall, CORS, and WebSocket origin verification.
- Internet voice must not be claimed complete until a TURN server is configured and
  tested across NAT.

## Technology Candidate Comparison

| Candidate | Fit | Text realtime | Voice/screen | Cross-PC/NAT | Cost/friction | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Harden current FastAPI WebSocket + browser WebRTC | Excellent: already integrated with FastAPI, Vue, Pinia, PostgreSQL, Docker | Already implemented; needs reconnect/ack/reconciliation | Already implemented P2P; needs TURN QA and media polish | LAN works with config; internet requires TURN | Low dependency churn | Select |
| Socket.IO stack | Medium: Python server exists, but protocol differs from plain WebSocket | Strong reconnect/ack/broadcast features | Does not solve media transport by itself | Still needs TURN/WebRTC for voice | Adds protocol migration and client/server dependency | Reject for now |
| LiveKit | Medium: strong realtime media platform, but app needs service integration | Can support data/events, but text app already works | Strong SFU voice/video/screen | Stronger NAT/media story with server infra | Adds service, auth integration, deployment complexity | Defer |
| mediasoup | Low-medium: powerful SFU toolkit, but requires custom media server design | Not a text gateway replacement | Excellent for custom SFU media | Good if deployed correctly | High implementation and ops complexity | Reject for student clone scope |
| PeerJS/simple-peer wrapper | Medium: simplifies P2P setup | Not a full text gateway | Simplifies peer calls but does not remove signaling/NAT concerns | Still needs PeerServer/TURN | Adds abstraction over current explicit WebRTC code | Reject unless current WebRTC becomes unmanageable |
| Matrix-style protocol/server | Low: much broader federation/message protocol than needed | Strong durable chat model | Voice requires additional stack | Heavy deployment and product mismatch | Severe overengineering | Reject |
| Hosted realtime/media provider | Medium technically, low project-control fit | Strong if provider supports it | Strong if provider supports it | Provider handles ops | Paid/proprietary risk and account dependency | Reject unless user explicitly approves |
| Do nothing | High short-term convenience | Current local demo remains | Current local demo remains | Real multi-user remains under-verified | No work, but high hidden risk | Reject |

## Selected Stack

Selected approach: keep the existing native FastAPI WebSocket gateway plus browser
WebRTC stack, harden it, and add TURN-ready deployment verification.

Reasons:

1. It fits the current architecture without rewriting FastAPI, Vue, Pinia,
   PostgreSQL, and Docker boundaries.
2. The current stack already implements the SRS-style Discord gateway shape:
   `op`, `d`, `s`, `t`, `HELLO`, `IDENTIFY`, heartbeat, dispatch, voice state, and
   voice signal operations.
3. Text/DM messages are already persisted through REST, so realtime can remain
   event delivery rather than becoming durable queue infrastructure.
4. Browser WebRTC is the correct primitive for microphone and screen sharing; the
   missing piece is TURN and verification, not a full SFU rewrite.
5. Student clone scope benefits from low operational cost and direct debuggability.
   LiveKit/mediasoup are technically stronger for production-scale voice, but they
   add infrastructure that is disproportionate for the current project.
6. The existing optional Redis boundary can support multi-instance fan-out without
   making local development require Redis.
7. Keeping dependencies stable reduces security, licensing, and maintenance risk.

## Implementation Guardrails

These rules apply to every communication stage:

- Do not call a feature "real communication complete" unless at least two distinct
  sessions exchange data through the backend gateway without a page refresh.
- Do not replace two-session browser verification with isolated Pinia/store tests.
  Store tests are useful regression coverage, but they cannot prove end-to-end
  communication.
- Do not use browser-native `alert`, `confirm`, `prompt`, or the browser context
  menu for clone behavior. Voice switching, reconnect failure, permission failure,
  and destructive actions must use app-owned UI.
- Do not log JWTs, message content, ICE candidates, TURN credentials, media device
  labels, or private DM contents during debugging.
- Do not persist TURN credentials, test account passwords, or generated tokens in
  documentation, screenshots, test fixtures, or committed environment files.
- Do not claim internet voice support from LAN-only tests. LAN success and
  TURN/NAT success are separate release gates.
- Do not claim microphone quality improvement from fake-device tests. Fake-device
  smoke only proves code paths and signaling.
- Keep REST persistence as the source of truth for text and DM history. Gateway and
  Redis dispatches are realtime notification paths.
- Keep communication changes backward-compatible with single-process local
  development without Redis.
- If a command cannot run because the local toolchain is missing or broken, record
  the exact blocker in this document and resolve it in Stage C0 before editing
  communication behavior.

## Stage Completion Rules

Each stage is complete only when all of these are true:

1. The stage's implementation tasks are complete or a residual risk is explicitly
   recorded with a reason.
2. The stage's verification commands have run through the C0-selected command
   paths.
3. Two-session realtime smoke has been rerun for any stage that touches gateway,
   message, DM, Redis, voice presence, reconnect, or frontend session state.
4. `PROJECT_CONTEXT.md` and any affected docs are updated with new owner files,
   run commands, environment variables, and residual risks.
5. Newly discovered defects are added as sub-items under the active stage before
   moving forward.
6. No browser-native dialog or native context-menu dependency is introduced.
7. `git diff --check` passes.

## Protocol And Event Contract Plan

### Existing Gateway Opcodes

- `0 DISPATCH`
- `1 HEARTBEAT`
- `2 IDENTIFY`
- `4 UPDATE_VOICE_STATE`
- `5 VOICE_SIGNAL`
- `8 REQUEST_GUILD_MEMBERS`
- `10 HELLO`
- `11 HEARTBEAT_ACK`

### Required Contract Additions

1. Document every dispatch event in one table:
   - `READY`
   - message create/update/delete
   - DM message create/update/delete
   - guild/channel/member changes
   - `VOICE_STATE_UPDATE`
   - `VOICE_SIGNAL`
2. Add client-side `lastSequence` tracking.
3. Define reconnect behavior:
   - v1: reconnect and re-identify.
   - no durable resume claim.
   - after reconnect, reload guild/DM state through REST.
4. Define idempotency:
   - message events are keyed by message ID.
   - DM events are keyed by message ID and DM ID.
   - voice state is keyed by `guild_id:user_id`.
   - voice signals are best-effort and not replayed.
5. Define delivery semantics:
   - REST persistence is source of truth for text/DM.
   - WebSocket dispatch is low-latency notification.
   - Redis Pub/Sub fan-out is live best-effort across backend workers.
   - WebRTC media is peer-to-peer best-effort.

## Security, Privacy, And Abuse Controls

Required implementation rules:

- Authenticate WebSocket sessions with JWT before accepting subscriptions or voice
  operations.
- Re-check server-side authorization for every guild, channel, DM, voice state, and
  voice signal.
- Reject voice signaling if the sender is not connected to that voice channel.
- Validate payloads with Pydantic schemas on backend and typed guards on frontend.
- Sanitize text payloads at schema/service boundaries.
- Rate-limit:
  - REST message send/edit/delete.
  - gateway identify attempts.
  - heartbeat abuse.
  - voice state updates.
  - voice signals per peer/channel.
- Do not log:
  - JWTs.
  - message content except local debug with explicit redaction.
  - ICE candidates.
  - media device labels.
  - private DM contents.
- Keep TURN credentials in environment variables only.

### Initial Rate-Limit Baseline

Use these conservative local defaults unless implementation evidence requires
adjustment:

| Surface | Limit | Window | Key | Failure behavior |
| --- | --- | --- | --- | --- |
| Gateway `IDENTIFY` | 5 attempts | 60 seconds | client IP + connection user token subject when available | close with policy/try-later code |
| Gateway heartbeat | 2x expected heartbeat rate plus burst 3 | rolling heartbeat interval | connection ID | ignore extra frames, close on repeated abuse |
| Voice state update | 12 updates | 60 seconds | user ID + guild ID | reject frame with app-owned error dispatch or close on abuse |
| Voice signal | 60 frames | 60 seconds | sender user ID + voice channel ID + target user ID | drop or reject with redacted log |
| REST message create | 10 messages | 10 seconds | user ID + channel/DM ID | HTTP 429 |
| REST message edit/delete | 20 mutations | 60 seconds | user ID + channel/DM ID | HTTP 429 |

Implementation notes:

- Prefer the existing local token-bucket style for single-process local mode.
- Use Redis-backed counters only when Redis is configured and the project needs
  multi-instance consistency.
- Do not rate-limit heartbeat ACKs so aggressively that normal browser timer
  throttling causes false disconnects.
- Log only operation names, user IDs, channel IDs, and redacted reason codes. Do
  not log message content, JWTs, ICE candidates, or device labels.
- Record actual observed false positives/negatives in this document during C3.

## Noise Reduction Plan

Stage order:

1. Use browser-native constraints first:
   - `echoCancellation: true`
   - `noiseSuppression: true`
   - `autoGainControl: true`
2. Detect support through `navigator.mediaDevices.getSupportedConstraints()`.
3. Display current constraint support in a debug-safe local voice settings section.
4. Keep Web Audio VAD/input-level logic for speaking indicators.
5. Defer RNNoise/WebAssembly until after native constraints and TURN QA prove
   insufficient.

Do not add a heavy noise-reduction dependency until it has:

- Official source.
- Acceptable license.
- Stable browser performance.
- Clear measurable benefit over native constraints.
- A rollback path.

## Real Communication Test Strategy

Implementation must prove actual communication paths, not only isolated store or
component behavior. Use these test layers in order.

### Automated Two-Session Browser Smoke

Use Playwright with the installed Chrome channel when Playwright-managed browsers
are unavailable.

Required shape:

1. Open two isolated browser contexts.
2. Create two local dev sessions with different `user_id` values through
   `POST /api/dev/session`.
3. Identify both sessions against `/gateway`.
4. Use REST to create or load a shared guild/channel or DM.
5. Send a server text message from session A.
6. Assert session B receives the matching `MESSAGE_CREATE` dispatch without
   refresh.
7. Send a DM message from session B.
8. Assert session A receives the matching `DM_MESSAGE_CREATE` dispatch without
   refresh.
9. Refresh one session, reconnect, and assert REST reconciliation does not duplicate
   already received messages.

Pass condition:

- Events are observed through WebSocket dispatches in the other session.
- Message IDs are unique and duplicate suppression keeps one visible message.
- Browser native dialogs are not required for text/DM verification.

### Direct Gateway Protocol Smoke

For backend-focused stages, a browser page or Node-compatible WebSocket client may
connect directly to `/gateway`:

1. Wait for `HELLO`.
2. Send `IDENTIFY` with a valid token.
3. Assert `READY`.
4. Send heartbeat and assert `HEARTBEAT_ACK`.
5. Attempt invalid token and unauthorized voice signal cases.

This smoke verifies protocol behavior but does not replace the two-session browser
smoke for UI/store correctness.

### Automated Media Smoke With Fake Devices

When interactive microphone permission is unavailable, run a limited media smoke
with Chrome flags:

- `--use-fake-device-for-media-stream`
- `--use-fake-ui-for-media-stream`

This can verify:

- microphone capture code path.
- voice join state.
- local audio track lifecycle.
- peer signaling between two browser contexts on the same machine.
- mute/deafen track state.

It cannot verify:

- real microphone quality.
- real acoustic echo/noise behavior.
- user-facing permission prompt copy.
- real screen-capture picker behavior.

Do not claim production voice completion from fake-device smoke alone.

### Manual Real-Device Smoke

Manual QA remains required for:

- real microphone grant and denial.
- screen-share grant, denial, and browser track-ended behavior.
- two browsers on the same PC with real devices.
- another PC or mobile browser on the same LAN.
- TURN/NAT across different networks.

Record manual blockers explicitly instead of replacing them with fake-device
automation.

## Detailed Call Implementation Design

This section expands the call-specific work so implementation does not stop at a
high-level "make voice work" instruction. Use it as the controlling checklist for
voice and screen-share stages.

### Call Architecture Target

Keep the current peer-to-peer WebRTC model:

```text
Browser A media capture
  -> RTCPeerConnection
  -> offer/answer/ICE over /gateway
  -> Browser B RTCPeerConnection

Gateway
  -> authenticates user
  -> verifies guild/channel membership
  -> tracks voice state
  -> relays targeted voice signals
  -> broadcasts voice state updates
```

Do not introduce an SFU until P2P plus TURN fails the cross-PC goals.

### Call State Model

Required frontend states:

- `idle`: no selected or connected voice channel.
- `preview`: voice channel selected, not connected.
- `connecting`: microphone capture or signaling setup in progress.
- `connected`: local user joined and peer sync is active.
- `switching`: connected elsewhere and waiting for user confirmation.
- `screenSharing`: connected and publishing a display track.
- `reconnecting`: gateway or peer connection is recovering.
- `permissionDenied`: microphone or screen capture was rejected.
- `failed`: unrecoverable media, gateway, or ICE failure.

Required persisted/runtime identifiers:

- connected guild ID.
- connected channel ID.
- local user ID.
- per-peer user ID.
- local media stream ID.
- screen media stream ID.
- last voice signal timestamp per peer.

Likely owner files:

- `frontend/src/composables/useVoiceSessionController.ts`
- `frontend/src/composables/useVoiceRtc.ts`
- `frontend/src/composables/voiceMedia.ts`
- `frontend/src/composables/voicePeerConnections.ts`
- `frontend/src/composables/voiceStats.ts`
- `frontend/src/stores/voicePresence.ts`
- `frontend/src/components/VoicePanel.vue`
- `frontend/src/components/ChannelSidebar.vue`
- `backend/app/gateway/router.py`
- `backend/app/gateway/voice_service.py`

### Call Join Flow

1. User clicks a voice channel row.
2. If already connected to the same channel:
   - open the voice workspace only.
3. If already connected to a different channel:
   - show the app-owned voice switch dialog.
   - if cancelled, preserve current connection.
   - if confirmed, leave current channel then join target channel.
4. Load ICE config from `/api/meta/voice` if not already fresh.
5. Capture microphone with native constraints:
   - `echoCancellation: true`
   - `noiseSuppression: true`
   - `autoGainControl: true`
6. Send `UPDATE_VOICE_STATE` over gateway.
7. Sync current voice participants.
8. Create peer connections for remote participants.
9. Attach local audio track to each peer.
10. Send targeted offer/answer/ICE through `VOICE_SIGNAL`.
11. Render connected state in:
    - channel row participant stack.
    - bottom voice card.
    - voice workspace.
    - server rail voice badge.

### Call Leave Flow

1. User clicks leave from workspace, sidebar, or bottom voice card.
2. Stop screen share first if active.
3. Stop local microphone tracks.
4. Close all peer connections.
5. Clear remote streams.
6. Send `UPDATE_VOICE_STATE` with `channel_id: null`.
7. Remove local user from connected voice state.
8. Reset call UI to selected-channel preview or server text view, depending on
   current navigation.
9. Ensure no stale speaking indicator remains.

### Participant Sync Flow

1. Gateway broadcasts `VOICE_STATE_UPDATE`.
2. `guildGatewayHandlers.ts` validates the payload.
3. `voicePresence.ts` updates voice state by `guild_id:user_id`.
4. `useVoiceSessionController.ts` compares connected participant IDs.
5. `useVoiceRtc.ts`:
   - creates peers for new participants.
   - closes peers for departed participants.
   - preserves existing peers for unchanged participants.
6. UI updates participant rows and tiles without remounting the whole workspace.

### Screen Share Flow

1. Screen share button is enabled only when connected to voice.
2. User clicks screen share.
3. Browser display capture prompt opens.
4. If permission denied:
   - keep voice connected.
   - show local app notice.
5. If granted:
   - attach display video track.
   - replace or add screen track in each peer connection.
   - renegotiate where required.
   - show local preview tile.
   - show remote screen tile in other sessions.
6. If browser track ends:
   - stop sharing automatically.
   - remove screen track.
   - renegotiate or update sender state.
   - preserve voice connection.

### Speaking Indicator Flow

1. Local speaking:
   - use `voiceVad.ts` analyser.
   - mark local tile/avatar/channel participant row as speaking.
2. Remote speaking:
   - derive from inbound audio level where feasible.
   - if browser support is insufficient, use remote track activity plus stats as a
     coarse signal.
3. Mute/deafen:
   - mute disables local audio track.
   - deafen affects local playback and reflected state.
   - speaking indicator must not show for muted local audio.

### Call Error Handling

Handle each error with clone-owned UI, not browser-native dialogs:

- microphone permission denied.
- no microphone device.
- insecure context outside localhost.
- gateway disconnected before join.
- voice signal rejected by backend authorization.
- ICE failed or disconnected.
- screen capture denied.
- screen capture ended by user.
- TURN configured incorrectly.

Each error must include:

- visible user-facing state.
- safe retry action.
- leave/disconnect action if already joined.
- redacted log context for debugging.

### Call Verification Checklist

Minimum pass criteria before calling voice complete:

- one-session preview opens without microphone capture.
- one-session join captures microphone and shows connected state.
- two sessions in the same channel establish peer connection.
- local mute stops audio track and updates voice state.
- deafen updates UI and local playback state.
- speaking indicator appears only while input level crosses threshold.
- screen share starts, renders remotely, and stops cleanly.
- switching voice channels uses app-owned confirmation.
- moving to another server shows connected-elsewhere context.
- tab refresh removes stale voice presence after timeout.
- backend restart moves frontend to reconnecting/offline state.
- TURN-enabled metadata reports `turn_configured: true`.
- LAN cross-PC test succeeds for text and voice.

## Staged Implementation Plan

## Stage Progress Log

### Stage C0 Result: Completed 2026-06-19

Environment recovery found that the backend virtual environment was not corrupted.
The failure was caused by sandboxed execution of the Python 3.14 runtime outside the
workspace. The approved command path for backend verification is:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
..\.venv\Scripts\python.exe -m ruff check app tests
```

Backend tool versions verified:

- Python: `Python 3.14.3`
- pytest: `pytest 9.0.3`
- ruff: `ruff 0.14.14`

The system `py` launcher and plain `npm` remain unavailable in PATH. Use the bundled
Node runtime plus frontend local binaries for frontend verification:

```powershell
$env:PATH='C:\Users\yangbun\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;'+(Resolve-Path ..\frontend\node_modules\.bin).Path+';'+$env:PATH
..\frontend\node_modules\.bin\oxlint.cmd .
..\frontend\node_modules\.bin\vue-tsc.cmd -b
..\frontend\node_modules\.bin\vite.cmd build
..\frontend\node_modules\.bin\vitest.cmd run
```

Frontend tool versions verified:

- Node: `v24.14.0`
- oxlint: `1.64.0`
- TypeScript/vue-tsc: `5.9.3`
- Vite: `8.0.16`
- Vitest: `4.1.9`

Browser automation path:

- Direct shell `require('playwright')` from the bundled package path failed because
  `playwright-core` was not resolved in that shell context.
- The Codex Node REPL Playwright environment launched installed Chrome successfully
  with `chromium.launch({ channel: 'chrome', headless: true })`.
- Use Node REPL Playwright for C1 browser automation unless a project-local
  Playwright dependency is added deliberately.

Stage C0 verification:

- Backend Python `--version`: passed with approved `.venv` execution.
- Backend `pytest --version`: passed.
- Backend `ruff --version`: passed.
- Frontend `oxlint`, `vue-tsc`, `vite`, and `vitest` path/version checks: passed.
- Playwright installed Chrome launch smoke through Node REPL: passed.
- `git diff --check`: passed.

### Stage C1 Result: Completed 2026-06-19

Baseline checks were run against the local services at `127.0.0.1:8000` and
`127.0.0.1:5173`.

Command verification:

- Backend lint: `cd backend; ..\.venv\Scripts\python.exe -m ruff check app tests`
  passed.
- Backend tests: `cd backend; ..\.venv\Scripts\python.exe -m pytest` passed before
  the C1 fix with 110 tests. After the C1 fix, focused DM tests and the full
  backend suite passed with the added DM seed test.
- Frontend lint: bundled Node plus `frontend/node_modules/.bin/oxlint.cmd .`
  passed.
- Frontend unit tests: bundled Node plus `vitest.cmd run` passed with 3 files and
  11 tests.
- Frontend build: bundled Node plus `vue-tsc.cmd -b` and `vite.cmd build` passed
  from `frontend/`.

API and gateway smoke:

- `GET /api/health` returned `status: ok`, database configured/connected, Redis not
  configured.
- `GET /api/meta/voice` returned one STUN ICE server and `turn_configured: false`.
- Direct gateway smoke observed `HELLO`, `IDENTIFY`, `READY`, and `HEARTBEAT_ACK`.

Two-session realtime baseline:

- Server text realtime passed with user `42` sending to channel `2001` in guild
  `1001`; user `43` received the matching `MESSAGE_CREATE` dispatch over WebSocket.
- Direct-message realtime passed with user `701` sending in DM `803`; user `42`
  received the matching `DM_MESSAGE_CREATE` dispatch over WebSocket.

C1.1 discovered issue and fix:

- Issue: PostgreSQL DM demo seeding attempted to create a self-relationship when a
  seeded DM profile user such as `701` opened `/api/dms`. The database rejected
  `(701, 701)` through the `relationships_check` constraint, causing `/api/dms` and
  gateway `IDENTIFY` for that user to fail with a server error.
- Fix: `backend/app/repositories/dm_seed.py` now skips self-relationships while
  seeding demo relationships for any current user.
- Regression: `backend/tests/test_dm_seed.py` verifies that demo workspace seeding
  never inserts self-relationships.

Voice baseline:

- Fake-media browser smoke through Node REPL Playwright Chrome opened the app,
  selected the Study Hall server, clicked `voice-room`, and observed the connected
  lower voice card.
- Cross-server voice switch baseline passed: while connected to Study Hall
  `voice-room`, selecting the SRS Lab `voice-room` showed the app-owned switch
  dialog and did not show browser-native dialog text.
- Direct gateway voice state smoke passed for user `42`: `UPDATE_VOICE_STATE`
  joined channel `2003` and then left with `channel_id: null`, both observed as
  `VOICE_STATE_UPDATE` dispatches.

Residual C1 notes:

- Browser fake-device smoke proves only the join/state UI and permission path, not
  real microphone quality.
- `/api/meta/voice` is STUN-only. TURN/NAT remains a C7/C9 release gate.
- Redis is not configured in the current local stack; multi-worker fan-out remains
  a C4 target.

### Stage C2 Result: Completed 2026-06-19

Implementation:

- `frontend/src/composables/useGateway.ts` now tracks `connected`,
  `reconnecting`, `offline`, and `error` states and preserves the existing
  Discord-style `HELLO` -> `IDENTIFY` -> `READY` flow.
- Gateway reconnect uses bounded exponential backoff with a 10 second maximum delay.
- Client heartbeat now waits for `HEARTBEAT_ACK`; if the stale socket stays open
  after backend restart and no ACK arrives, the client closes the socket and enters
  reconnect flow.
- `frontend/src/App.vue` now passes an `onReconnect` callback that reloads guilds,
  DMs, and voice metadata through REST after successful re-identification.
- `frontend/src/stores/guilds.ts` preserves the active guild/channel when
  reconciliation reloads guild state.
- `frontend/src/stores/gatewayIdempotency.test.ts` covers duplicate server-message
  and DM-message gateway dispatches so REST response plus gateway dispatch races
  leave one visible message.
- `frontend/src/App.vue` exposes a non-visible `data-gateway-status` attribute on
  the app shell for QA automation. It does not add user-facing debug text.

Verification:

- Frontend lint passed.
- Frontend unit tests passed: 4 files, 13 tests.
- Frontend typecheck and production build passed.
- Docker frontend was restarted so the local dev server served the updated source.
- Backend restart reconnect smoke passed: a user `43` browser page stayed open on
  SRS Lab, Docker backend was restarted, user `42` sent a new message to channel
  `2001`, and the existing page displayed the message without refresh after
  gateway reconnect/reconciliation.
- Two-session server text dispatch passed again after C2.
- Two-session DM dispatch passed again after C2.

Residual C2 notes:

- Browser recovery from backend restart depends on heartbeat timeout when the stale
  WebSocket is not closed immediately by the dev proxy.
- Durable gateway resume is still intentionally not claimed; REST reload remains
  the reconciliation source of truth.

### Stage C3 Result: Completed 2026-06-19

Implementation:

- `backend/app/core/operation_limits.py` defines local operation-level token buckets
  for gateway identify, heartbeat abuse, voice state, voice signal, REST message
  create, and REST message edit/delete.
- `backend/app/api/routes/channels.py` rate-limits server message create, edit, and
  delete by user and channel.
- `backend/app/api/routes/dms.py` rate-limits DM message create by user and DM.
- `backend/app/gateway/router.py` rate-limits identify by client host plus token
  subject, invalid-token identify attempts by host, heartbeat abuse by connection,
  voice state by user/guild, and voice signal by sender/channel/target.
- Gateway logs now record privacy-safe connect, identify reject, identify success,
  voice state, voice signal reject/send, rate-limit, and disconnect events. Logs do
  not include JWTs, message content, ICE candidates, TURN credentials, device
  labels, or private DM contents.
- Gateway connections are now cleaned up in a `finally` path so rate-limit and
  close-code returns cannot leave stale connections in the registry.

Verification:

- Backend lint passed.
- Backend full test suite passed: 114 tests.
- `backend/tests/test_api_routes.py` covers REST message create rate limiting with
  HTTP 429.
- `backend/tests/test_gateway_routes.py` covers gateway identify rate limiting with
  close code `4008` and unauthorized voice signal with close code `4003`.
- Runtime smoke passed:
  - invalid gateway token closed with `4001`.
  - unauthorized voice signal closed with `4003`.
  - 11 rapid REST server-message creates returned 10 `201` responses and then
    `429`.
- Two-session server text dispatch passed after C3.
- Two-session DM dispatch passed after C3.

Tuning notes:

- Identify rate limiting was adjusted during C3 from client-host-only to
  client-host plus token subject for valid tokens. Host-only limiting was too broad
  for same-PC multi-user QA and could block legitimate local two-session tests.
- Runtime Redis is still not configured, so these operation buckets are
  single-process local protection. Distributed counters remain a future production
  hardening option if multi-instance abuse consistency becomes necessary.

### Stage C0: Environment And Verification Recovery

Goal: remove local tooling blockers before changing communication behavior.

Tasks:

1. Verify `.venv/Scripts/python.exe` can run `--version`.
2. If the executable cannot create a process, recreate the backend virtual
   environment using the documented Python version or the closest available project
   runtime.
3. Install backend dev dependencies from `backend[dev]`.
4. Verify frontend commands through either `npm` or direct local binaries with
   bundled Node on PATH.
5. Verify Playwright can launch either installed Chrome channel or a managed browser.
6. Record the exact command path selected for C1-C9 verification.

Verification:

- backend Python `--version`.
- backend `pytest --version`.
- backend `ruff --version`.
- frontend `oxlint`, `vue-tsc`, `vite build`, and `vitest` path check.
- `git diff --check`.

### Stage C1: Communication Baseline Lock

Goal: capture current behavior before changing code.

Tasks:

1. Run backend health and `/api/meta/voice`.
2. Run gateway HELLO/IDENTIFY/HEARTBEAT smoke.
3. Run two-session browser server message smoke.
4. Run two-session browser DM message smoke.
5. Run one-session voice preview/join/leave/switch smoke with fake media if real
   permission is unavailable.
6. Run current connected-elsewhere UI smoke.
7. Record current gaps in this document before changing protocol code.

Verification:

- backend lint/test through the C0-selected command path.
- frontend lint/test/build through the C0-selected command path.
- API health and voice metadata smoke.
- gateway HELLO/IDENTIFY/READY/HEARTBEAT_ACK smoke.
- two-session text and DM realtime smoke.
- `git diff --check`

### Stage C2: Gateway Reconnect And Reconciliation

Goal: make text/DM usable after refresh, disconnect, and reconnect.

Tasks:

1. Add frontend gateway reconnect with bounded exponential backoff.
2. Track gateway status: connected, reconnecting, offline, error.
3. On reconnect, re-identify and reload guild/DM state through REST.
4. Add duplicate dispatch suppression by resource ID.
5. Add tests for event handler idempotency.

Verification:

- Kill/restart backend while frontend is open.
- Send message before/after reconnect.
- Refresh after message send.
- Verify no duplicate messages.

### Stage C3: Gateway Rate Limit And Observability

Goal: protect gateway and make failures diagnosable.

Tasks:

1. Add rate limiting for identify, heartbeat abuse, voice state, voice signal, and
   REST message mutation operations using the initial rate-limit baseline above.
2. Add structured logs for connect, identify failure, disconnect, voice join/leave,
   signal reject, and Redis publish/subscriber errors.
3. Keep logs privacy-safe.
4. Add test coverage for authorization, rate-limit, and close-code behavior.
5. Add a short tuning note in this document if any default limit causes false
   positives during smoke.

Verification:

- Invalid token gateway smoke.
- Unauthorized voice channel signal smoke.
- Repeated signal/send abuse smoke.

### Stage C4: Redis Multi-Instance Fan-Out Verification

Goal: verify real multi-worker behavior.

Redis fan-out semantics:

- Redis Pub/Sub is a best-effort live notification path between backend workers.
- PostgreSQL REST writes remain the source of truth for server text and DM content.
- Redis events must not be treated as durable storage, replay history, or guaranteed
  offline delivery.
- When Redis is absent, local single-worker fan-out must remain usable for local
  development.
- When Redis publish fails after startup, the publishing worker may use local
  fan-out fallback so the REST write is not rejected only because notification
  fan-out degraded.

Tasks:

1. Document Redis fan-out semantics as best-effort live notification.
2. Add or verify subscriber startup/restart logs.
3. Add a repeatable local multi-worker test path. Acceptable options:
   - Docker Compose override with two backend services and one frontend proxy.
   - Two native backend processes on different ports plus a simple reverse proxy.
   - A documented manual fallback if no load-balancer is available.
4. Run two backend workers with Redis configured.
5. Open two sessions routed to different workers if possible.
6. Verify server text and DM realtime across workers.
7. Stop Redis and verify single-process no-Redis local fallback still works.

Verification:

- `REDIS_URL` configured Docker smoke.
- Redis unavailable fallback smoke.
- Two-session message delivery.
- Logs show subscriber startup and no message-content leakage.

Stage C4 Result: Completed 2026-06-19.

Implementation:

- Added `compose.redis-smoke.yaml` with optional Redis and `backend-secondary`
  service on port 8001. The normal `compose.yaml` path remains Redis-free unless
  the override is explicitly included.
- Added `scripts/realtime_redis_smoke.py` to verify cross-worker realtime dispatch:
  a gateway session connects to the secondary backend while server text and DM
  messages are created through the primary backend.
- Added privacy-safe Redis connection, subscriber start/stop/restart, invalid
  payload, publish success, and publish failure logs. Logs include event names and
  subscriber counts where useful, but not JWTs, message contents, ICE candidates,
  TURN credentials, media labels, or DM body text.
- Redis connection failure no longer prevents local app startup; realtime falls back
  to local fan-out.
- When `REDIS_URL` is configured but Redis is down during startup, the subscriber
  loop keeps retrying and attaches after Redis returns without restarting the
  backend.
- Redis publish failure falls back to local fan-out after the REST source-of-truth
  write has succeeded.
- Added unit coverage for Redis publish failure fallback and subscriber payload
  decoding behavior.

Verification:

- `cd backend; ..\.venv\Scripts\python.exe -m ruff check app tests` passed.
- `cd backend; ..\.venv\Scripts\python.exe -m pytest` passed with 116 tests.
- `.\.venv\Scripts\python.exe -m py_compile scripts\realtime_redis_smoke.py`
  passed.
- C4 Docker Redis smoke command path is:
  `docker compose -f compose.yaml -f compose.redis-smoke.yaml up -d --build redis backend backend-secondary`
  followed by
  `.\.venv\Scripts\python.exe scripts\realtime_redis_smoke.py`.
  This passed for server text and DM dispatch from primary REST on port 8000 to
  secondary WebSocket on port 8001.
- The same cross-worker smoke also passed with explicit worker routing:
  `.\.venv\Scripts\python.exe -c "import os, runpy; os.environ['REST_SECONDARY']='http://127.0.0.1:8001'; os.environ['WS_SECONDARY']='ws://127.0.0.1:8001/gateway'; runpy.run_path('scripts/realtime_redis_smoke.py', run_name='__main__')"`
- Redis unavailable fallback command path is:
  `docker compose -f compose.yaml -f compose.redis-smoke.yaml stop redis`
  followed by
  `.\.venv\Scripts\python.exe -c "import os, runpy; os.environ['REST_SECONDARY']='http://127.0.0.1:8000'; os.environ['WS_SECONDARY']='ws://127.0.0.1:8000/gateway'; runpy.run_path('scripts/realtime_redis_smoke.py', run_name='__main__')"`
  to route the gateway and REST traffic to a single worker. This passed for server
  text and DM dispatch after Redis was stopped.
- After Redis was stopped, both backends were restarted with `REDIS_URL` still set,
  the single-worker fallback smoke passed, Redis was started again, and the explicit
  port-8001 cross-worker smoke passed without restarting either backend. `/api/health`
  reported Redis configured and connected on ports 8000 and 8001.

### Stage C5: Voice Media Constraints And Permission States

Goal: improve microphone behavior and user feedback.

Tasks:

1. Add native audio constraints in `voiceMedia.ts`.
2. Detect supported constraints.
3. Add UI feedback for permission denied, no device, insecure context, and ignored
   permission prompt.
4. Ensure media tracks stop on leave, logout, tab close, and capture error.
5. Normalize media errors into typed frontend error codes.
6. Add app-owned notices for retry, open settings, and leave voice.
7. Keep microphone capture behind the explicit join action; selecting a voice row for
   preview must not open a browser permission prompt.
8. Record current constraint support in settings or debug-safe local state without
   exposing device labels.

Verification:

- Permission granted microphone smoke.
- Permission denied smoke.
- No microphone device smoke if feasible.
- Local speaking indicator smoke.

Result 2026-06-19:

- Implemented browser-native microphone constraints, supported-constraint detection,
  debug-safe constraint support storage, and typed media error normalization in
  `frontend/src/composables/voiceMedia.ts`.
- `useVoiceRtc()` now records constraint support before explicit voice join,
  exposes typed media error codes, stops media on page hide/unmount/disconnect, and
  keeps retry/leave behavior inside clone-owned UI.
- `VoicePanel.vue` now renders app-owned voice error actions for retry, opening
  voice settings, and leaving voice; `SettingsView.vue` displays supported native
  audio processing without exposing device labels.
- Added `frontend/src/composables/voiceMedia.test.ts` for permission/device/screen
  error mapping.
- Verification passed:
  - `npm --prefix frontend run lint`
  - `npm --prefix frontend run test`
  - `npm --prefix frontend run build`
  - Playwright with system Chrome, fake microphone, and explicit click path from
    development login to `Study Hall / voice-room` voice join.
- Permission-denied/no-device real browser UI checks remain manual because the
  automated smoke uses fake media devices and must not be claimed as real audio
  quality or real hardware coverage.

### Stage C6: WebRTC Peer Lifecycle Hardening

Goal: make voice stable across joins, leaves, screen share, and participant changes.

Tasks:

1. Audit peer registry cleanup for participant leave and stale remote streams.
2. Ensure screen-share track replacement renegotiates cleanly.
3. Add ICE state and connection state UI.
4. Add retry/recreate behavior for failed peer connections.
5. Preserve voice signaling as best-effort, not durable.
6. Key peer connections by remote user ID and connected voice channel ID.
7. Ignore stale voice signals from a previous channel/session.
8. Add per-peer teardown on participant leave before removing UI state.
9. Add screen-share sender replacement tests or manual smoke steps.
10. Keep remote audio/video sinks mounted only while streams are live.

Discovered C6 sub-items:

- C6-a: Media error codes were cleared by `disconnect()` when microphone capture
  failed. Fixed by preserving typed media error state after cleanup.
- C6-b: Two-session voice QA cannot use two default dev sessions because
  `/api/dev/session` defaults to the same user ID. Fixed the verification path by
  creating distinct dev user IDs, creating a temporary guild, and joining the second
  user through an invite before voice smoke.

Verification:

- Two-session voice join/leave.
- Mute/deafen toggles.
- Screen share start/stop.
- Peer disconnect/reconnect.

Result 2026-06-19:

- `voicePeerConnections.ts` now keys peers by `channelId:userId`, ignores stale
  voice signals from previous channels, queues ICE candidates until a remote
  description exists, and tears down remote streams by channel scope.
- Failed peer connections schedule one bounded recreate attempt; intentional
  participant removal and disconnect paths close peer connections and remove remote
  streams without retry.
- `RemoteVoiceStream` now carries `channelId`, and `App.vue` renders audio/video
  sinks only for the currently connected voice channel.
- `VoicePanel.vue` now uses the already collected WebRTC quality stats to display
  signaling/STUN/TURN and peer connection status instead of passing those props
  unused.
- Verification passed:
  - `npm --prefix frontend run lint`
  - `npm --prefix frontend run test`
  - `npm --prefix frontend run build`
  - Playwright/system Chrome two-user smoke with distinct dev user IDs, temporary
    shared guild/invite, fake microphone, voice join for both users, remote audio
    sink count 1, peer detail visible, mute/deafen toggles, and fake screen-share
    path visible.
- Real-device audio quality and real screen picker behavior remain manual by design;
  fake-device smoke only proves code path and signaling.

### Stage C7: TURN And LAN Deployment Readiness

Goal: make cross-PC testing repeatable.

Tasks:

1. Document native and Docker LAN commands:
   - Backend native:
     `cd backend; ..\\.venv\\Scripts\\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Frontend native:
     `npm --prefix frontend run dev -- --host 0.0.0.0`
   - Host IP discovery:
     `ipconfig` or
     `Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike '169.254*'}`
2. Ensure frontend can bind to `0.0.0.0`.
3. Ensure API and gateway URLs derive from the browser origin or documented env.
   If the frontend is opened from `http://<host-ip>:5173`, backend API and gateway
   calls must target the same host IP or a documented proxy route.
4. Confirm CORS/WebSocket origins for LAN. Current Compose defaults only include
   `localhost` and `127.0.0.1`; LAN testing must set `CORS_ORIGINS` to include
   `http://<host-ip>:5173`.
5. Configure `WEBRTC_ICE_SERVERS_JSON` with STUN and TURN.
6. Verify `/api/meta/voice` reports `turn_configured: true`.
7. Document Windows firewall prompts and allowed ports.
8. Document HTTPS/WSS requirements for non-localhost microphone/screen capture.
9. Add a LAN checklist with host IP, frontend URL, backend URL, and browser origin.
10. Add a TURN/NAT checklist that explicitly distinguishes LAN success from internet
    voice success.

Verification:

- Same-PC two-browser smoke.
- Different PC/mobile on same LAN smoke.
- Different network TURN smoke.
- Explicitly mark internet voice incomplete if TURN credentials are unavailable.

Result 2026-06-19:

- Added native LAN scripts:
  - `npm run dev:backend:lan`
  - `npm run dev:frontend:lan`
  - `npm --prefix frontend run dev:lan`
- `README.md`, `.env.example`, `docs/deployment.md`, and `docs/voice-qa.md` now
  document host IP discovery, LAN URLs, CORS origin additions, Windows firewall
  ports, Docker LAN access, and the HTTPS secure-context caveat for microphone and
  screen capture from non-localhost origins.
- LAN and TURN/NAT release gates are explicitly separated. LAN reachability is not
  enough to mark internet voice complete; TURN/NAT completion requires
  `turn_configured: true` and a real different-network voice/screen-share pass.
- Verification passed:
  - `npm --prefix frontend run lint`
  - `npm --prefix frontend run test`
  - `npm --prefix frontend run build`
  - `GET http://127.0.0.1:8000/api/meta/voice` returned voice metadata in the
    current Docker stack.
- Different-PC LAN and different-network TURN/NAT tests remain manual external
  release gates because this local environment only provides one host/network and no
  real TURN credentials.

### Stage C8: Two-Session Realtime QA Suite

Goal: make communication regressions easier to catch.

Tasks:

1. Add a manual QA script under docs.
2. Add lightweight automated gateway smoke where feasible.
3. Add Playwright two-context realtime smoke for server text and DM.
4. Add fake-device browser voice smoke where feasible.
5. Add frontend store tests for duplicate suppression and reconnect state.
6. Add backend tests for gateway auth/authorization/rate-limit/voice signal
   validation.

Verification:

- Server text realtime.
- DM realtime.
- Refresh/reconnect.
- Duplicate tab cleanup.
- Voice join/leave/switch.
- Screen share with permission.
- Fake-device voice smoke result is labeled separately from real-device manual QA.

Implementation and verification result:

- Added `docs/realtime-communication-qa.md` as the repeatable manual and automated
  communication QA checklist.
- Added root script `npm run smoke:realtime:browser`, backed by
  `scripts/realtime_browser_smoke.mjs`, using official project-local Playwright.
- The browser smoke creates temporary local dev sessions, a shared guild/invite, and
  a DM, then verifies server text, DM, voice peer visibility, remote audio sink,
  mute/deafen controls, and fake screen-share visibility across two isolated browser
  contexts.
- The smoke output is payload-safe: it does not print JWTs, message bodies, ICE
  candidates, TURN credentials, media device labels, or DM contents, and it masks
  synthetic smoke message identifiers on failure.
- Added frontend store coverage in `frontend/src/stores/gatewayIdempotency.test.ts`
  for voice-state replacement/removal and gateway guild-update replacement without
  duplicate guilds or active-channel loss.
- Added backend gateway route coverage for invalid identify token close code and
  unsubscribed voice-channel close code in `backend/tests/test_gateway_routes.py`.
- Verification passed:
  - `npm run smoke:realtime:browser`
  - `npm --prefix frontend run lint`
  - `npm --prefix frontend run test`
  - `npm --prefix frontend run build`
  - `cd backend; ..\\.venv\\Scripts\\python.exe -m pytest tests/test_gateway_routes.py tests/test_gateway_manager.py tests/test_realtime_fanout.py`
  - `git diff --check`
- `git diff --check` emitted Windows CRLF conversion warnings only.
- Same-PC fake-device voice remains code-path/signaling coverage, not real
  microphone quality completion. Different-PC LAN and TURN/NAT internet voice remain
  separate external release gates.

### Stage C9: Final Communication Release Gate

Goal: declare what is production-ready and what remains manual.

Tasks:

1. Update `docs/voice-qa.md`.
2. Update `docs/deployment.md`.
3. Update `README.md` with LAN/TURN run commands if changed.
4. Update `PROJECT_CONTEXT.md`.
5. Record verification results and residual risks.

Verification:

- Full command suite.
- Docker smoke.
- LAN smoke.
- TURN/NAT smoke if credentials are available.

Final result:

- Completed local release gate on 2026-06-19.
- Command suite passed:
  - `npm run lint:frontend`
  - `npm run test:frontend` (5 files, 19 tests)
  - `npm --prefix frontend run build`
  - `npm run lint:backend`
  - `npm run test:backend` (119 tests)
  - `npm run smoke:realtime:browser`
- Docker/local service smoke passed:
  - `docker compose ps` showed frontend, backend, backend-secondary, PostgreSQL,
    and Redis running; backend and PostgreSQL were healthy.
  - `GET http://127.0.0.1:8000/api/health` returned healthy database and Redis
    state.
  - `GET http://127.0.0.1:8000/api/meta/voice` returned one STUN ICE server and
    `turn_configured: false`.
  - `GET http://127.0.0.1:5173/` returned HTTP 200.
- Automated same-PC browser communication smoke passed:
  - server text realtime: passed.
  - DM realtime: passed.
  - voice remote audio sink: passed with fake microphone devices.
  - peer detail visibility: passed.
  - mute/deafen toggles: passed.
  - fake screen-share visible path: passed.
  - browser errors: zero.
- Release gate classification:
  - Local same-PC text, DM, gateway dispatch, Redis-backed local stack, fake-device
    voice signaling, and fake screen-share code paths are complete.
  - Real microphone quality, real screen picker UX, different-PC LAN, and
    TURN/NAT internet voice remain external manual gates.
- Internet voice must not be marked complete until real TURN credentials are
  configured, `/api/meta/voice.turn_configured` is `true`, and a different-network
  two-user voice/screen-share test passes.

## Post-C9 Communication Audit And Remediation

Date: 2026-06-19.

Audit findings added after the first C9 gate:

1. Voice participants could remain stale after abnormal WebSocket disconnect,
   heartbeat zombie reap, stale-send cleanup, or logout because the gateway removed
   the connection without broadcasting a `VOICE_STATE_UPDATE` leave event.
2. Client logout used local media cleanup instead of the app's normal voice leave
   path.
3. Redis publish success with zero Pub/Sub subscribers was treated as complete even
   though no backend subscriber consumed the event.
4. Gateway and message mutation rate limits were process-local only, which is weak
   for multi-worker Docker or production deployments.
5. The browser smoke verified a local "Screen sharing" label but did not require a
   remote screen-share tile in the second browser context or a post-leave voice
   cleanup assertion.
6. `scripts/realtime_redis_smoke.py` existed, but no root npm script exposed it as
   a repeatable command.
7. DM gateway messages always reset `unread_count` to zero, so inactive DMs could
   miss unread badges.
8. TURN/NAT internet voice remained correctly gated by external credentials and
   real different-network QA.
9. The remote screen-share media track was received, but the screen-share stage
   render condition was narrower than the voice workspace condition, so the remote
   video tile could be hidden from the current voice workspace.

Remediation completed in this pass:

- `backend/app/gateway/connection.py`, `subscriptions.py`, `voice_service.py`,
  `manager.py`, `zombie_reaper.py`, and `router.py` now track voice guild/channel
  state and route normal disconnects, zombie reaps, stale send failures, and
  explicit voice moves through a single leave-event cleanup path.
- `frontend/src/App.vue` now logs out through `disconnectVoice()` before closing the
  gateway, so normal logout sends the same app-owned leave event as the visible
  disconnect control.
- `backend/app/realtime/publisher.py` falls back to local fan-out when Redis publish
  reports zero subscribers.
- `backend/app/core/operation_limits.py` uses Redis-backed fixed-window operation
  buckets when Redis is connected, with a privacy-safe local fallback if Redis
  limiting fails.
- `scripts/realtime_browser_smoke.mjs` now asserts remote screen-video rendering in
  the second browser context and verifies that leaving voice removes remote audio
  sinks.
- `frontend/src/composables/voicePeerConnections.ts`, `useVoiceRtc.ts`,
  `voiceMedia.ts`, and `frontend/src/App.vue` reserve a video transceiver for
  screen sharing, refresh remote screen flags from live unmuted video tracks, and
  render the screen-share stage whenever a selected voice channel has a remote
  screen stream.
- `package.json` exposes `npm run smoke:realtime:redis`.
- `frontend/src/stores/dms.ts` tracks the active DM, clears unread on open, keeps
  REST-sent messages read, and increments unread for inactive DM gateway messages.

Verification recorded for this remediation:

- `npm run test:backend` passed with 124 tests.
- `npm run test:frontend -- --run` passed with 21 tests.
- `npm run lint:backend` passed.
- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:redis` passed.
- `npm run smoke:realtime:browser` passed with remote screen-video rendering and
  voice leave cleanup after restarting the frontend dev container to load the
  latest Vite transform.

Remaining external gates:

- Real microphone quality.
- Real browser screen picker UX.
- Different-PC LAN text, DM, voice, and screen-share QA.
- TURN/NAT internet voice and screen-share QA with
  `/api/meta/voice.turn_configured: true`.

## Post-C9 Manual Voice/Product QA Findings

Date: 2026-06-19.

Scenario:

- User A was connected at `http://localhost:5173`.
- User B was connected at `http://127.0.0.1:5173` in a second profile, with a
  controlled same-origin B tab opened for repeatable interaction checks.
- Both users belonged to the same `test` server.
- This pass intentionally avoided printing passwords, tokens, invite codes, message
  bodies beyond synthetic QA markers, ICE candidates, media device labels, and TURN
  credentials.

Confirmed working behavior:

- Server text messages delivered in both directions after both users were in the
  same server and channel.
- Existing DM messages delivered in both directions; when user A was outside the DM,
  user B's DM created an unread badge and the message appeared after opening the DM.
- No browser console errors were observed during text/DM checks.

New defects:

1. Real microphone quality is not acceptable yet.
   - User-observed behavior: keyboard/tap noise is transmitted, but spoken language
     sounds echoing, unstable, or intermittently cut.
   - Existing code enables supported browser constraints such as echo cancellation,
     noise suppression, auto gain control, mono channel count, 48 kHz sample rate,
     16-bit sample size, and low latency, but there is no user-facing device,
     processing, input-sensitivity, or diagnostics workflow that can isolate the
     failure.
   - Required fix: add a real-device audio-quality stage that records WebRTC stats
     over a timed call, surfaces local track settings and processing support, offers
     device/processing toggles where browser support allows, tunes local speaking
     threshold separately from transmitted audio, and documents pass/fail speech
     test phrases for manual QA.
2. Late joiners can miss existing voice participants.
   - User-observed behavior: A can see B in the voice sidebar, but B's voice
     workspace can show only B and an "no other participants" empty state.
   - Code review confirms the gateway broadcasts `VOICE_STATE_UPDATE` events when a
     user changes voice state, but does not send a current voice-state snapshot to a
     newly identified client or a newly joined voice client.
   - Required fix: add an authoritative in-memory voice-state registry in the
     gateway manager, include current channel voice states in READY or send a
     channel-scoped snapshot immediately after `UPDATE_VOICE_STATE`, and reconcile
     frontend voice-state arrays from that snapshot.
3. Voice workspace and sidebar can disagree.
   - The sidebar and workspace derive from selected/connected voice state in
     different UI paths. When the local selected channel is not synchronized with
     the connected channel, a user can see connected indicators but an incomplete
     participant grid.
   - Required fix: normalize participant derivation so sidebar, workspace, bottom
     panel, and server rail all render from the same connected-channel snapshot when
     the user is connected, while still allowing a clear preview mode for a different
     selected channel.
4. Controlled B voice join can remain in preview.
   - In a controlled B tab, selecting `voice-room` produced `선택됨 / 참여 전`,
     disabled screen share, and no obvious main-workspace Join action.
   - Required fix: if voice channel click is intended to join immediately, media
     capture errors must show an app-owned recovery state. If preview mode is
     intended, the voice workspace must show a prominent Join Voice action.
5. Permission errors are raw and poorly localized.
   - A member pressing invite controls can receive `create invite permission
     required` as an English raw backend message.
   - Required fix: map permission errors to localized app-owned notices and hide or
     disable invite actions when the current user cannot create invites.
6. Member invite controls do not match permission state.
   - The B member account still sees invite affordances in voice/server surfaces but
     cannot create invites.
   - Required fix: expose permission-aware UI metadata or use existing role/member
     data to suppress unauthorized controls, with a localized disabled explanation
     when the control remains visible.

Additional implementation stages required before claiming real voice completion:

- Stage C10: Authoritative voice-state snapshot.
  - Backend stores current voice states by guild/channel/user in the gateway manager.
  - READY or post-voice-join dispatch sends existing voice occupants to the joining
    client.
  - Leave, disconnect, zombie reap, stale-send cleanup, and logout remove the stored
    state and broadcast a delete/null update.
  - Frontend treats the snapshot as a replace operation and keeps incremental
    `VOICE_STATE_UPDATE` idempotent.
- Stage C11: Voice workspace/sidebar unification.
  - Workspace, sidebar, bottom voice panel, and server rail use one connected-channel
    participant source.
  - Preview mode has a visible Join action and cannot masquerade as connected.
  - Regression test verifies A-joins-first/B-joins-later and B-joins-first/A-joins-
    later both show two participants on both sides.
- Stage C12: Real microphone quality remediation.
  - Add device/processing visibility and user controls for supported browser audio
    constraints.
  - Add a timed manual speech QA checklist covering echo, clipping, dropouts,
    keyboard-noise handling, mute/unmute, and reconnect.
  - Store no raw audio and print no media device labels in logs or documentation.
- Stage C13: Permission-aware voice/invite UX.
  - Hide or disable unauthorized invite controls.
  - Localize permission errors.
  - Add browser QA for member and owner invite behavior.

Implementation update, 2026-06-19:

- Stage C10 completed in code.
  - `backend/app/gateway/voice_service.py` now keeps an in-memory voice-state
    registry keyed by guild and user.
  - `backend/app/gateway/router.py` sends `VOICE_STATE_SNAPSHOT` after READY and
    immediately after a successful voice join so late joiners receive current
    occupants.
  - `frontend/src/stores/voicePresence.ts` applies guild-wide and channel-scoped
    snapshots as replace operations while preserving incremental
    `VOICE_STATE_UPDATE` handling.
  - Automated coverage: `backend/tests/test_gateway_manager.py` and
    `frontend/src/stores/gatewayIdempotency.test.ts`.
- Stage C11 completed in code for preview/join clarity.
  - `frontend/src/App.vue` now shows an explicit Join Voice action in the voice
    workspace when the selected voice channel is only being previewed.
  - Sidebar, workspace, and bottom voice state continue to use the shared guild
    voice presence source.
- Stage C12 completed in code for browser-supported processing controls.
  - `frontend/src/composables/voiceMedia.ts` persists local audio-processing
    preferences and builds microphone constraints from browser support plus user
    settings.
  - `frontend/src/components/SettingsView.vue` exposes echo cancellation, noise
    suppression, and auto gain controls only when the browser reports support.
  - No raw audio, device labels, ICE candidates, or credentials are written to
    docs or logs.
- Stage C13 completed in code for invite permissions.
  - `frontend/src/stores/guilds.ts` exposes `canCreateInvite`.
  - `frontend/src/App.vue` and `frontend/src/components/ChannelSidebar.vue` hide
    unauthorized invite controls and translate server-side invite permission
    denials into clone UI copy.

Remaining manual QA before claiming real voice completion:

- Two Chrome profiles with account A and B must verify that A-joins-first and
  B-joins-first both show both occupants in sidebar and workspace without refresh.
- A timed speech test must verify spoken Korean/English intelligibility, echo,
  clipping, dropout, keyboard-noise handling, mute/unmute, reconnect, and screen
  share start/stop on real microphones. Fake-device tests are not enough for this
  gate.
- Owner/member invite behavior must be checked in-browser: owner sees invite
  controls and member without `CREATE_INSTANT_INVITE` does not.

Manual QA follow-up, 2026-06-19:

- Sustained syllable speech can be chopped even though short words sound acceptable.
- Receiver-side screen share should merge the shared screen and participant state
  into one composition per sharing user.
- Refresh still requires an explicit rejoin/recovery flow.
- Same-Wi-Fi LAN voice join failed because HTTP LAN origins are not secure contexts
  for microphone/screen capture.
- TURN/NAT remains untested and cannot be claimed while `turn_configured` is false.
- Deafen/소리 차단 does not yet mute remote audio as expected.
- Full staged follow-up lives in
  `docs/remediation-tasks/manual-qa-followup-2026-06-19.md`.

## Voice Architecture Decision Update

Date: 2026-06-19.

Current implementation:

- Use WebSocket only for gateway state, voice-state updates, and WebRTC signaling
  payloads such as offer, answer, and ICE.
- Use browser WebRTC peer connections for actual microphone audio and screen-share
  media.
- Current topology is P2P mesh between browser clients.

Decision:

- Keep the current WebRTC P2P plus WebSocket signaling approach for the immediate
  C10-C13 remediation work.
- Do not move microphone audio transport to raw WebSocket. Raw WebSocket audio would
  require custom codec, jitter buffering, packet-loss handling, echo cancellation,
  media permissions, and device handling that browsers already provide through
  WebRTC.
- Treat SFU-backed WebRTC as the best long-term architecture for a Discord-like
  voice channel experience when the target moves beyond small-room local clone QA.

Architecture comparison:

| Option | Fit | Strength | Risk / limitation | Decision |
| --- | --- | --- | --- | --- |
| Raw WebSocket audio | Poor | Simple conceptual transport | Reimplements browser media stack, weak latency/jitter handling, poor echo/noise support | Reject |
| WebRTC P2P mesh + WebSocket signaling | Good now | Browser-native media, low infrastructure cost, fits 2-user/local QA | Mesh upload/CPU grows with participants; late-join snapshot still needs app logic | Keep for C10-C13 |
| WebRTC SFU, LiveKit-style | Best long-term | Scales multi-user rooms, centralizes track forwarding, SDK/ops support | Adds server dependency, auth/token integration, deployment and TURN work | Evaluate after C10-C13 |
| WebRTC SFU, mediasoup-style | Strong but low-level | Maximum media-layer control | More custom room/signaling/server work than LiveKit | Defer unless LiveKit is insufficient |
| Managed realtime/media provider | Possible | Fastest hosted path | Cost, vendor lock-in, project budget constraints | Defer |

Evidence used for this decision:

- MDN WebRTC API documents WebRTC as the browser-native API for real-time audio,
  video, and data.
- MDN WebRTC signaling guidance separates signaling/discovery from media exchange.
- Discord's public engineering write-up describes its voice stack as WebRTC-based.
- LiveKit documents an SFU as a low-latency media-forwarding server optimized for
  multi-party WebRTC.
- mediasoup is also an SFU option but is lower-level and requires more application
  integration work.

Implementation implication:

- C10-C13 must fix correctness and quality gaps in the current P2P stack first:
  voice-state snapshot, participant-source consistency, preview/join UX, real speech
  quality diagnostics, and permission-aware controls.
- A later SFU evaluation stage should be created only after the current stack passes
  real same-PC speech QA and the project needs larger voice rooms or cross-network
  reliability beyond TURN-backed P2P.

## Chrome Profile QA Note

Date: 2026-06-19.

Two local clone accounts were opened in different Chrome profiles:

- Profile `minruel`: `http://localhost:5173/`
- Profile `jbnu.ac.kr`: `http://127.0.0.1:5173/`

The Codex Chrome extension can see both profiles, but browser automation initially
defaulted to the last-used `minruel` profile and therefore only listed the A tab.
Future manual two-account QA should explicitly select both extension browser
instances before claiming tabs.

Required future QA setup:

1. List available extension browsers and identify the intended Chrome profile names.
2. Select the A profile and claim the `localhost:5173` tab.
3. Select the B profile and claim the `127.0.0.1:5173` tab.
4. Keep both user tabs as handoff tabs when the QA turn ends.
5. If one profile still does not appear, use the automated Playwright smoke with two
   isolated browser contexts, or create a controlled second tab and log in with the
   non-secret local QA account procedure.

## Verification Matrix

| Scenario | Text | DM | Gateway reconnect | Voice | Screen share | Required |
| --- | --- | --- | --- | --- | --- | --- |
| One browser, local native | yes | yes | yes | yes | permission-dependent | yes |
| Two tabs, local native | yes | yes | yes | partial voice | permission-dependent | yes |
| Two browsers, same PC | yes | yes | yes | yes | permission-dependent | yes |
| Docker single backend | yes | yes | yes | yes | permission-dependent | yes |
| Docker + Redis/multi-worker | yes | yes | yes | signaling fan-out | permission-dependent | yes before production claim |
| Different PC on LAN | yes | yes | yes | yes | permission-dependent | required for "real users" claim |
| Different networks with TURN | yes | yes | yes | yes | permission-dependent | required for internet voice claim |
| Permission denied | n/a | n/a | n/a | graceful error | graceful error | yes |

## Observability And Rollback

Add logs for:

- gateway connect/disconnect.
- identify success/failure.
- subscription counts.
- Redis connect/publish/subscriber failures.
- message event publish failures.
- voice join/leave.
- voice signal rejected/sent.
- ICE/peer connection failures on frontend as redacted UI/debug state.

Rollback policy:

- Keep demo/local no-Redis behavior working.
- Keep REST persistence as source of truth for text and DM.
- Feature-flag any new reconnect/resume behavior if it risks duplicated messages.
- Do not remove current P2P WebRTC until an alternative has passed LAN and TURN QA.

## Manual QA Items

Manual checks that require browser/device permission or another device:

- Microphone permission grant.
- Microphone permission denial.
- Browser ignored permission prompt.
- Screen share permission grant and stop.
- Screen share denied.
- LAN access from another PC or mobile device.
- TURN/NAT test across two networks.

## External Deployment Readiness Pass

Date: 2026-06-20.

Scope:

- Preserve the current local and same-Wi-Fi LAN voice behavior.
- Add an external deployment/verification structure so the next gate can be tested
  on a real HTTPS/WSS host with TURN configured.
- Keep UI/design follow-up out of this pass until external communication is stable.

Decision:

- GitHub Pages or any static-only host is not sufficient for the communication
  target. Static hosting can serve the Vue bundle, but it cannot run FastAPI,
  PostgreSQL, Redis fan-out, `/gateway` WebSocket upgrades, or a TURN relay.
- Recommended first external QA path is a single VM/server with Docker Compose,
  Caddy HTTPS reverse proxy, backend runtime container, frontend runtime container,
  PostgreSQL, Redis, and either managed TURN or self-hosted coturn.
- This keeps the current FastAPI WebSocket plus browser WebRTC architecture intact
  and avoids a premature SFU migration.

Files added:

- `compose.production.example.yaml`
  - Example production-like topology with Caddy, frontend, backend, PostgreSQL,
    Redis, and optional coturn profile.
- `deploy/Caddyfile.example`
  - Public HTTPS proxy routing `/api` and `/gateway` to backend and app routes to
    frontend.
- `deploy/coturn/turnserver.conf.example`
  - Placeholder-only coturn configuration. Real secrets must stay outside Git.
- `scripts/deployment_readiness_check.mjs`
  - Safe checker for HTTPS origin shape, `/api/health`,
    `/api/meta/voice/readiness`, and `/gateway` HELLO over WSS.

Acceptance criteria:

- `npm run check:deployment:readiness` exists.
- The readiness check does not identify, print JWTs, print ICE URLs, print TURN
  credentials, print media device labels, or print message content.
- With `REQUIRE_TURN=1`, readiness fails if `turn_configured` is false.
- Docs clearly state that readiness success is not the same as a completed
  different-network media test.

Verification:

- `npm run check:deployment:readiness` passed against
  `https://localhost:5173` with local TLS verification intentionally ignored for
  the self-signed development certificate. It reported health `ok`, WSS gateway
  HELLO, one STUN ICE server, and `turn_configured: false`.
- `docker compose -f compose.production.example.yaml config` passed with
  placeholder environment values, proving the example topology renders without
  committing secrets.
- `npm run check:voice:readiness` passed and still reported STUN-only local
  configuration.
- `npm run smoke:realtime:browser:https` passed with server text, DM, invite-DM,
  voice remote audio sink, mute/deafen, screen-share preview/remote/stop cleanup,
  reload rejoin recovery, voice leave cleanup, and `browserErrors: 0`.
- `git diff --check` passed.

Remaining external gate:

- A real TURN credential and HTTPS/WSS deployment are still required.
- The final internet communication claim requires two different networks to pass
  text, DM, voice, mute/unmute, screen-share start/stop, and reconnect checks.

## External Deployment Decision Pass

Date: 2026-06-20.

Scope:

- Decide the first external-network deployment approach before provisioning
  external infrastructure.
- Do not claim external TURN/NAT voice, screen sharing, or reconnect success.
- Keep the current same-PC and same-Wi-Fi HTTPS LAN behavior as a regression gate.

Decision record:

- `docs/external-deployment-decision.md` is now the source document for the first
  external deployment choice.
- The selected path is single VM Docker Compose with Caddy HTTPS, runtime
  frontend/backend containers, PostgreSQL, Redis, and TURN supplied through
  environment configuration.
- Managed TURN is recommended for the first public external QA pass. Self-hosted
  coturn remains available when the user is ready to open and verify the required
  UDP/TCP firewall ports.

Candidate comparison result:

- Local PC port forwarding is rejected as the primary route because residential
  NAT, changing IPs, certificate trust, uptime, and TURN hosting are fragile.
- VM/IaaS is viable and becomes the selected shape when paired with the existing
  Docker Compose assets.
- PaaS is not first choice because app deployment is easier, but TURN, persistent
  Redis/PostgreSQL, WebSocket timeouts, and provider-specific networking split the
  realtime stack.
- Static frontend plus separate backend is deferred because it adds CORS/WSS
  split-origin risk while still requiring a backend and TURN host.
- Single VM Docker Compose best matches the current repository, same-origin
  gateway/API design, and operator debugging needs.

Pending / not verified:

- No external VM/VPS has been provisioned in this pass.
- No public DNS hostname has been configured in this pass.
- No real TURN credential has been configured in this pass.
- No different-network voice or screen-share QA has been run in this pass.

## Dependency Decision

No new dependency is selected at the planning stage.

Potential future dependencies:

- A TURN server or hosted TURN provider, configured only through environment
  variables.
- coturn for self-hosted TURN when deployment requires it.

Rejected for immediate implementation:

- Socket.IO migration.
- LiveKit migration.
- mediasoup SFU.
- PeerJS wrapper.
- Hosted realtime provider.
- RNNoise/WebAssembly noise suppression.

These can be reopened only if Stage C1-C8 prove that the current stack cannot meet
cross-PC reliability or media-quality goals within acceptable complexity.
