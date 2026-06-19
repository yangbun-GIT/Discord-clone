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

Verification:

- Two-session voice join/leave.
- Mute/deafen toggles.
- Screen share start/stop.
- Peer disconnect/reconnect.

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
