# Project Context

This file is the first recovery point for future Codex/Cursor work. Read it before
editing code, then update it whenever a meaningful implementation change lands.

## Required Reading Order

1. `DEVELOPMENT_PROMPT.md` for the project-specific operating prompt, verification
   policy, documentation policy, security policy, and collaboration policy.
2. `AGENTS.md` for concise agent-facing engineering rules.
3. `PROJECT_CONTEXT.md` for the current implementation map and integration points.
4. `docs/implementation-plan.md` for the staged roadmap.
5. `README.md` for setup and verification commands.
6. `docs/README.md` for the document index and task-specific reading guide.
7. `docs/project-file-map.md` for quick path routing before broad exploration.
8. `docs/structure-map/reference-map.md` for cross-file dependency routing.

## Current Milestone

Stage 4's implementation scope is complete. Stage 1, the Docker development baseline,
Stage 2's main persistence/auth/member-management bridge, Stage 3's main text-realtime
scope, focused PostgreSQL repository coverage for current guild/message mutations,
Stage 5 deployment notes/runtime hardening, Stage 6.1 Store data contracts, Stage 6.2
Store seed catalog, Stage 6.3 Store backend read APIs, and Stage 6.4 frontend Store
state are complete and pushed to GitHub. Store UI work is now deferred. Stage 7.1
app destination state, Stage 7.2 `@me` Friends/DM shell, Stage 7.3 first-class
demo-backed Direct Messages, Stage 7.4 server rail parity, Stage 7.5 server
sidebar/header controls, Stage 7.6 composer/message actions, Stage 7.7 voice
channel UX, Stage 7.8 user settings shell, Stage 7.9 server add/discovery flows,
Stage 7.10 DM persistence/realtime expansion, Stage 7.11 responsive QA, and Stage
7.12 final QA/documentation are complete and pushed to GitHub.
Stage 8 Discord UI remediation is complete through Stage 8.14 final QA, including
layout tokens, sidebar overlap cleanup, Korean/English i18n, bottom voice controls,
current-location visibility, placeholder-button cleanup, channel-header panels,
composer panels, Friends/DM information density, settings reorganization, voice
workspace clarity, low-frequency feature scope cleanup, responsive/accessibility QA,
and final command/Docker verification.

Stage 9 Discord visual parity and density remediation is complete. The controlling
plan is `docs/discord-visual-parity-remediation-plan.md`; final QA evidence is in
`docs/stage-9-final-qa.md`. The completed work rebalances FHD 100% zoom layout
density, hides low-value demo/developer text from primary surfaces, improves Friends
and Add Friend density, adds message attachment/reaction visual structure, cleans up
member management visibility, and improves voice/screen-share state clarity with
Discord-like speaking indicators.

Stage 10 interaction polish is complete through Stage 10.29. The controlling plan is
`docs/discord-interaction-polish-plan.md`; the Stage 10.0 baseline lock is recorded
in `docs/stage-10-baseline.md`, and QA evidence is recorded in
`docs/stage-10-final-qa.md`. The completed work covers demo/test data cleanup,
visual-noise reduction, Discord-like shell hierarchy, text/button spacing, bottom
user panel reconstruction, message/composer polish, timeline divider cleanup,
voice/screen-share interaction cleanup, app-owned context menus/notices,
browser-native UI removal for clone workflows, voice-sidebar participant hierarchy,
server-owned voice session tracking, the in-app cross-server voice-switch dialog,
message timeline divider cleanup, server-rail/header seam cleanup, and layered
Friends-surface overlay alignment without the extra private-sidebar header band.
Remaining
voice media verification still depends on a browser session with
microphone and screen-capture permissions granted.

Stage 11 completion work has started. The controlling plan is
`docs/discord-stage-11-completion-plan.md`, and the Stage 11.0 baseline/scope lock
is `docs/stage-11-baseline.md`. Stage 11.1 global layer consolidation is complete:
`frontend/src/styles/base.css` now defines the shared layer, border, surface, and
shadow tokens used by popovers, menus, modals, notices, and sticky overlays. Stage
11.2 Friends finalization is complete: `frontend/src/components/FriendsHome.vue`,
`frontend/src/styles/base.css`, and `frontend/src/i18n/index.ts` now provide clearer
Friends tabs, friend-row separation, activity-card hierarchy, and less demo-oriented
Add Friend copy. Stage 11.3 DM finalization is complete: DM sidebar rows, DM intro
spacing, timeline divider spacing, composer surface color, group-DM copy, and emoji
choices were tightened in `frontend/src/components/DirectMessageView.vue`,
`frontend/src/styles/base.css`, and `frontend/src/i18n/index.ts`. Stage 11.4 server
sidebar and channel navigation polish is complete in `frontend/src/styles/base.css`,
covering rail contrast, voice-connected rail state, guild heading layering, category
create-button discoverability, channel-row height, stable active/connected borders,
and voice-detail spacing. Stage 11.5 text-channel timeline/composer polish is
complete in `frontend/src/components/ChatView.vue`, `frontend/src/styles/base.css`,
and `frontend/src/i18n/index.ts`, removing fake attachment cards, code-like emoji
options, empty-channel date dividers, and demo wording from composer helper panels.
Stage 11.6 bottom user/voice panel polish is complete in
`frontend/src/styles/base.css`, tightening disconnected/connected panel padding,
raised-card styling, disabled action states, and connected voice-card composition.
`docs/stage-11-final-qa.md` records the running Stage 11 QA evidence. Stage 11
preserves the Stage 10 process: each stage is documented, implemented separately,
verified before advancing, and then committed with a Korean commit title before
pushing to `origin/main`.

Stage 12 architecture-principle refactoring is complete. The controlling plan is
`docs/architecture-refactor-stage-12-plan.md`, and the refreshed audit is recorded
in `docs/architecture-principles-audit.md`. Stage 12 is behavior-preserving refactor
work that reduced SRP, DIP, DRY, encapsulation, and testability gaps: App
voice orchestration, WebRTC module boundaries, guild voice presence, DM storage
provider selection, guild repository query movement, API exception mapping,
realtime fan-out duplication, browser API adapters, and CSS/i18n ownership
planning. The remaining deferred candidates are splitting `frontend/src/stores/dms.ts`
if DM behavior expands and physically splitting `base.css`/`i18n/index.ts` using
`docs/frontend-css-i18n-ownership.md` when visual verification can be focused.

Stage 13 final architecture maintenance is complete. The controlling plan is
`docs/architecture-refactor-stage-13-plan.md`. This pass closed the remaining
maintenance-only gaps before feature work resumes: `frontend/src/stores/dms.ts`
now delegates DM REST behavior to `dmApi.ts`, gateway event validation to
`dmGatewayHandlers.ts`, and DM visibility filtering to `dmVisibility.ts`;
`frontend/src/stores/guilds.ts` delegates visual-test filtering to
`guildVisibility.ts`; focused Vitest coverage now exists for the extracted
frontend policy/handler modules; PostgreSQL DM demo bootstrap moved from
`backend/app/repositories/dms.py` to `backend/app/repositories/dm_seed.py`; and
`backend/app/services/guild_storage.py` now exposes smaller protocol groups behind
the existing compatibility provider. No maintenance-only principle or pattern
blocker remains before feature implementation. Physical `base.css` and
`i18n/index.ts` splitting remains intentionally deferred to a focused visual/copy
feature pass.

Server rail usability remediation is complete in
`docs/remediation-tasks/server-rail-remediation-2026-06-21.md`. The far-left rail
now supports user-controlled server ordering, server folders/groups, folder
collapse/expand, and app-owned hover/focus tooltips. The rail layout is stored per
user through `GET/PUT /api/users/me/server-rail`, backed by
`user_server_rail_layouts` in PostgreSQL and the demo store fallback. Frontend
ownership is split across `ServerRail.vue` for drag/folder/tooltip UI,
`stores/guilds.ts` for layout state and persistence, `services/api.ts` for REST
wrappers, and `App.vue` for save orchestration and failure notice handling.
Follow-up polish keeps drag feedback icon-sized, renders tooltips through a
body-level layer, shows aggregate active/unread/mention markers on collapsed
folders, and localizes `ServerDiscoveryDialog.vue` through `i18n/index.ts`.

Server workspace remediation is complete in
`docs/remediation-tasks/server-settings-chat-remediation-2026-06-21.md`. Server
heading actions now include a permission-aware invite icon, the `...` menu toggles
open/closed, and a functional `ServerSettingsDialog.vue` exposes invite,
leave-server, and owner-only delete-server flows through app-owned confirmation UI.
Backend support is provided by `DELETE /api/guilds/{guild_id}/leave` and
`DELETE /api/guilds/{guild_id}`, with PostgreSQL and demo-store implementations.
Server text channels now use bottom-anchored message behavior, persisted
`created_at` timestamps, per-day dividers, and clearer author row styling while
preserving existing message action flows.

Voice channel visual remediation is recorded in
`docs/remediation-tasks/voice-channel-visual-remediation-2026-06-21.md`. The server
voice workspace now uses a Discord-like stage composition in
`frontend/src/App.vue` and `frontend/src/styles/base.css`: large responsive
participant and empty-state tiles, darker stage framing, bottom-center voice
actions for join/screen-share/leave, stage-level microphone/output controls with
device popovers before screen share, and a real invite action in the empty tile when
the user has invite permission. Screen-share tiles and participant tiles now share
one adaptive stage grid capped at 9 visible tiles per voice workspace. The grid
now follows the requested count rules: 1-2 tiles stay in a horizontal row, 3-4
tiles use a stable 2x2 layout, and 5-9 tiles use a stable 3x3 layout with bounded
stage widths so simultaneous shares do not overlap or escape the stage. Refreshing
or leaving while screen sharing broadcasts `screen_sharing: false` before closing
peer connections, so remote participants clear the video quickly while the
existing voice reload recovery can rejoin audio without restoring screen sharing.
Remote screen-share state is retained by peer until the remote media track arrives,
and the current local screen-share state is resent during new offer/answer
negotiation, so a refreshed participant can rejoin voice and see another
participant's already-active screen share again. Screen-share tiles and contained
video now use black letterboxing instead of the blue participant surface.
Voice signaling and voice-state snapshots now carry a non-secret
per-voice-connection `session_id`. The gateway forwards this field in
`VOICE_SIGNAL`, `VOICE_STATE_UPDATE`, and `VOICE_STATE_SNAPSHOT` dispatches, and
the P2P registry closes/recreates a stale `RTCPeerConnection` when an incoming
offer or participant snapshot comes from a new remote session. This fixes the
manual path where B refreshed while A was already sharing, then rejoined the
voice UI without A's screen share or working audio.
If a refreshed receiver still has screen-share state but no video track, it sends
a `screen-repair` signal so the active screen sharer creates a fresh offer with
the current display track attached.
`scripts/realtime_browser_smoke.mjs` now verifies this path through
`remoteScreenVideosAfterReceiverReload` and `receiverAudioSinksAfterReload`.
The existing WebRTC, voice panel, screen-share, and gateway signaling flows are
preserved.

The global dark-theme surface tokens in `frontend/src/styles/base.css` were lowered
and separated by layer on 2026-06-21 so the app workspace remains darker while
rails, sidebars, panels, raised controls, inputs, hover, and selected states keep
clearer visual hierarchy across Friends, DM, server, and voice surfaces.

Realtime communication implementation has started from
`docs/remediation-tasks/realtime-communication-plan.md`. Stage C0 environment and
verification recovery is complete: `.venv` is a valid Python 3.14.3 environment
when run through approved execution, backend checks should use
`cd backend; ..\.venv\Scripts\python.exe -m pytest` and
`cd backend; ..\.venv\Scripts\python.exe -m ruff check app tests`, frontend checks
should use bundled Node plus `frontend/node_modules/.bin`; C8 also adds
project-local official Playwright for the repeatable browser smoke. Stage C1
communication baseline is complete:
backend/frontend command checks passed, API health and voice metadata passed,
gateway `HELLO`/`IDENTIFY`/`READY`/`HEARTBEAT_ACK` passed, two-session server text
and DM WebSocket dispatch passed, and fake-media browser voice join plus
app-owned cross-server voice switch dialog smoke passed. A C1 blocker where
PostgreSQL DM seed logic attempted to insert self-relationships for seeded profile
users was fixed in `backend/app/repositories/dm_seed.py` and covered by
`backend/tests/test_dm_seed.py`. Stage C2 gateway reconnect and reconciliation is
complete: `useGateway.ts` now has bounded reconnect, explicit reconnect/offline/error
states, heartbeat ACK timeout stale-socket detection, and reconnect-success
callbacks; `App.vue` reloads guilds, DMs, and voice metadata after reconnect;
`guilds.ts` preserves active guild/channel during REST reconciliation; and
`gatewayIdempotency.test.ts` covers server/DM duplicate dispatch races. Stage C3
gateway rate-limit and observability is complete: `operation_limits.py` provides
local operation buckets for gateway and message mutations, REST message create/edit/
delete and DM message create return 429 when limited, gateway identify/heartbeat/
voice state/voice signal paths enforce close-code rate limits, privacy-safe gateway
logs were added, and gateway route tests cover identify rate limiting plus
unauthorized voice signal rejection. Stage C4 Redis multi-instance fan-out
verification is complete through `compose.redis-smoke.yaml` and
`scripts/realtime_redis_smoke.py`. Stage C5 voice media permission handling is
complete with native audio constraints, typed media errors, app-owned recovery UI,
settings visibility, and media cleanup. Stage C6 WebRTC peer lifecycle hardening is
complete with channel-scoped peers, pending ICE queueing, stale-signal filtering,
bounded failed-peer retry, current-channel remote stream filtering, and peer detail
UI. Stage C7 LAN/TURN readiness is complete with native LAN scripts, CORS/firewall
notes, HTTPS secure-context caveats, and separate LAN versus TURN/NAT release gates.
Stage C8 two-session realtime QA is complete: `docs/realtime-communication-qa.md`,
`scripts/realtime_browser_smoke.mjs`, and root `npm run smoke:realtime:browser`
verify same-PC two-browser server text, DM, voice peer, remote audio sink,
mute/deafen, and fake screen-share paths while keeping payload output private.
`gatewayIdempotency.test.ts` now also covers voice-state and guild-update
idempotency, and `backend/tests/test_gateway_routes.py` covers invalid identify and
unsubscribed voice-channel rejection. Stage C9 final local communication release
gate is complete: frontend/backend lint, tests, build, Docker/local health, voice
metadata, frontend HTTP, and `npm run smoke:realtime:browser` passed. Real
microphone quality, real screen picker UX, different-PC LAN, and TURN/NAT internet
voice remain external manual gates because the current local `/api/meta/voice`
reports `turn_configured: false`.

The post-C9 communication audit/remediation pass closed local code gaps found after
the first gate. Gateway connections now track voice guild/channel state and
disconnect, zombie reap, stale-send cleanup, logout, and explicit channel moves
fan out `VOICE_STATE_UPDATE` leave events. Redis publish with zero subscribers now
falls back to local fan-out, Redis-backed operation limits are used when Redis is
connected with local fallback on limiter failure, inactive DM gateway messages now
increment unread badges, and `package.json` exposes `npm run smoke:realtime:redis`.
`scripts/realtime_browser_smoke.mjs` now verifies remote screen-video rendering and
voice leave cleanup in addition to the previous same-PC fake-device checks. The
voice workspace now opens from voice-channel selection/join paths, and the remote
screen-share stage renders from the selected voice workspace when a live unmuted
remote video track is present.

A 2026-06-19 manual two-account browser QA pass found product-flow blockers that
are now tracked in `docs/remediation-tasks/friend-relationship-implementation-plan.md`
and summarized in `docs/realtime-communication-qa.md`: Add Friend still shows a
local success message without creating an incoming request, server invite targets
are demo friends rather than real accepted friends, invite join lacks clear
success/error routing, and the second account can select but not clearly join the
shared voice channel.

A later 2026-06-19 two-account voice/product recheck added communication follow-up
stages C10-C13 to `docs/remediation-tasks/realtime-communication-plan.md`. New
blockers are real speech quality, missing voice-state snapshots for late joiners,
workspace/sidebar participant divergence, preview mode without a clear Join action,
and raw/unlocalized invite permission errors for member accounts. Server text and
existing DM delivery passed in both directions during this recheck.

A 2026-06-20 voice participant consistency fix changed the client join order so
`useVoiceSessionController.ts` no longer passes existing participants into
`voiceRtc.connect()` before the backend has accepted the user's
`UPDATE_VOICE_STATE`. Peer creation now waits for gateway
`VOICE_STATE_UPDATE`/`VOICE_STATE_SNAPSHOT` reconciliation, preventing one-sided
participant visibility and backend `voice signal rejected reason=voice-channel`
logs caused by offers sent before the sender was registered in the voice channel.
`npm run smoke:realtime:browser` passed after the change with one remote audio
sink, visible peer detail, voice rejoin recovery, and zero browser errors.

A follow-up 2026-06-20 WebRTC signaling hardening pass fixed a manual B-account
warning where duplicate or stale offers could call `RTCPeerConnection.createAnswer`
outside `have-remote-offer`/`have-local-pranswer`. `voicePeerConnections.ts` now
serializes incoming offer/answer/ICE handling per peer, rechecks the active
channel/user before processing queued signals, ignores stale descriptions that no
longer fit the current signaling state, and applies answers only while a local
offer is pending. Frontend lint, frontend tests, production build, and
`npm run smoke:realtime:browser` passed with `browserErrors: 0`.

A 2026-06-20 A-account voice rejoin warning showed Chrome rejecting
`setLocalDescription(offer)` with an SDP m-line order mismatch. The local fix keeps
outbound offer creation and renegotiation in the same per-peer signal queue used
for incoming offer/answer/ICE processing, preventing screen-share renegotiation or
participant sync from racing with inbound signaling. If Chrome still reports an
m-line-order error for a corrupted `RTCPeerConnection`, the affected peer is closed
and rebuilt before the lower user ID sends a fresh offer. Frontend lint, frontend
tests, production build, and browser realtime smoke passed with `browserErrors: 0`.

The same recheck also clarified browser QA setup and voice architecture direction.
The two user tabs may live in separate Chrome profiles; the current local mapping is
`minruel` for `localhost:5173` and `jbnu.ac.kr` for `127.0.0.1:5173`, so future
manual QA must select both Chrome extension browser instances before claiming tabs.
Voice transport should remain WebRTC media with WebSocket signaling for C10-C13.
Raw WebSocket audio is rejected, and SFU-backed WebRTC is the preferred future
architecture if the clone moves toward larger Discord-like voice rooms.

A 2026-06-19 call-recording QA pass used a local, ignored video under
`docs/reference-videos/voice-call/` to inspect screen-share and voice behavior
without committing private media. Automatic audio analysis found very low average
volume across the recording (`mean_volume` about -39.5 dB) and long low-volume
sections, so real speech clarity remains a manual blocker. The visual pass
confirmed that screen-share tiles could remain on the other participant after stop,
that remote share placement was too detached from the voice workspace, and that the
sharer could not see a local preview. The local implementation now sends a typed
gateway `VOICE_SIGNAL` with `type: "screen"` and `screen_sharing`, renders local
and remote screen tiles inside the selected voice workspace, clears remote screen
tiles after stop, and extends `npm run smoke:realtime:browser` to verify local
screen preview, remote screen rendering, screen-stop cleanup, and voice leave
cleanup. Browser refresh still tears down the underlying WebRTC media tracks, but
the backend now keeps voice state through a short normal-disconnect grace window
instead of immediately broadcasting leave, and the client uses same-user recovery
metadata to rejoin the previous voice channel automatically after the gateway
reconnects. Heartbeat timeout and stale-send cleanup still broadcast leave
immediately.

Friend relationship implementation is now backend-backed. The Friends Add Friend
surface no longer relies on a local-only success message or hardcoded fallback
friend rows for accounts with no relationships. Backend relationship reads and
mutations now cover request send, accept, reject, cancel, remove, block, and
unblock across PostgreSQL and demo fallback storage. User-targeted gateway dispatch
now publishes `RELATIONSHIP_UPDATE` and `RELATIONSHIP_DELETE` to the affected
sessions, and the frontend DM store/Friends UI applies those events idempotently.
Focused backend and frontend tests pass; the remaining follow-up is a two-profile
browser smoke that proves A's request appears in B's Pending tab without refresh.

Workspace location persistence now preserves the user's current page across
browser refresh. `frontend/src/stores/navigation.ts` stores a per-user restorable
destination plus DM/guild/channel IDs through the browser storage adapter, and
`frontend/src/App.vue` restores those IDs before workspace reload so DM, server
text, and voice-channel pages do not fall back to Friends. Logout clears the saved
location. `scripts/realtime_browser_smoke.mjs` now verifies server-channel reload
retention and voice-workspace reload retention before the voice rejoin flow.

The latest manual QA follow-up is tracked in
`docs/remediation-tasks/manual-qa-followup-2026-06-19.md`. It records real-device
issues not covered by fake-device smoke: sustained-syllable audio dropout,
screen-share receiver card duplication, refresh rejoin absence, HTTP LAN
secure-context failure, TURN readiness uncertainty, Friends Pending copy ambiguity,
friend presence not updating, DM identity mismatch on receipt, invite modal global
copy state, missing DM-based friend invite delivery, deafen behavior not muting
remote audio, and owner/member invite permission browser QA. An API permission
check on 2026-06-19 confirmed backend invite enforcement: owner invite creation
returns `201`, member invite creation returns `403`.

Manual QA follow-up Stage M1 is implemented in code. Voice settings now expose
speech-stability, balanced, and near-raw browser audio-processing presets. A
2026-06-20 OBS comparison found the raw microphone capture stayed continuous while
the clone's desktop-audio output had repeated short silent gaps, so the default
speech-stability preset now minimizes browser echo cancellation, noise suppression,
and auto gain instead of relying on browser auto-processing. A voice-quality pass
also added the
MIT-licensed `@sapphi-red/web-noise-suppressor` dependency and inserts its
RNNoise AudioWorklet/WASM processor before the local gain/gate chain when the
browser supports 48 kHz AudioWorklet processing. For the stable default path, app
RNNoise and the app input gate are off by default and existing default local
settings migrate once to that baseline. The input-level path still drives local
speaking feedback, but exact input amount is only visible inside Voice & Video
settings; the main workspace, sidebar, lower user card, and remote participant
cards expose only binary speaking feedback. Remote WebRTC audio streams are
analyzed locally in `voicePeerConnections.ts` only for binary `speaking` state.
Focused frontend voice media tests, frontend lint, production build, and browser
realtime smoke passed. Real sustained-vowel and fan/wind-noise listening remains a
manual gate.

Manual QA follow-up Stage M2 is implemented in code. Remote screen-sharing
participants now render as one screen-share participant composition, and their
separate normal remote participant cards are omitted while they are sharing. The
same-PC browser smoke now verifies exactly one remote sharing user's screen tile
and zero duplicate remote participant cards, while preserving local screen preview
and screen-stop cleanup.

Manual QA follow-up Stage M3 is implemented in code. The gateway now treats normal
voice websocket disconnects as recoverable for a short grace period, preserving the
voice-state snapshot unless the user fails to reconnect or explicitly leaves.
Heartbeat timeouts and stale gateway connections bypass the grace period and leave
immediately. The voice session controller stores safe same-user voice rejoin
metadata, automatically rejoins the previous voice channel after a refreshed tab
reconnects to the gateway, and keeps the app-owned rejoin notice with Rejoin/Leave
actions as a fallback if microphone recovery fails. Normal leave and notice
dismissal clear the recovery record. The browser realtime smoke reloads a connected
tab, verifies the voice panel returns to connected state, and confirms the other tab
receives remote audio again after automatic rejoin.

Manual QA follow-up Stage M4 is implemented in code/docs. `frontend/vite.config.ts`
can start Vite over HTTPS when `VITE_HTTPS_KEY_FILE` and
`VITE_HTTPS_CERT_FILE` point at trusted local development certificate files, and
`npm run dev:frontend:lan:https` validates those inputs before binding the frontend
to the LAN. `README.md`, `docs/deployment.md`, and `docs/voice-qa.md` now separate
HTTP LAN text/gateway reachability from HTTPS LAN media-capture testing. Real
same-LAN media capture still requires a manually trusted certificate on the second
device.

Manual QA follow-up Stage M5 is implemented in code/docs. The backend now exposes
`GET /api/meta/voice/readiness`, which returns only `ice_server_count`,
`stun_configured`, and `turn_configured`; browser-required ICE configuration remains
on `GET /api/meta/voice`. `npm run check:voice:readiness` calls the safe readiness
endpoint and prints no TURN credentials, ICE candidates, tokens, or media device
labels. The current local Docker backend reports `turn_configured: false`, so
different-network TURN/NAT voice remains a manual release gate until real TURN
credentials are supplied and tested.

Manual QA follow-up Stage M6 is implemented in code/docs. The Friends view now
labels the pending tab as friend requests, keeps Online/All scoped to actual
friends, and groups pending incoming/outgoing friend requests with separate counts.
Relationship updates now keep DM identity data stable without repainting DM
presence, and the dedicated gateway `PRESENCE_UPDATE` flow persists the current
user's `dm_profiles.presence_status` in PostgreSQL/demo storage, publishes
user-targeted updates to accepted friends, and publishes guild-targeted updates to
shared server members. Friends rows and server member rows show status through
small presence dots only; DM sidebar/DM intro/invite rows no longer use realtime
presence color or activity, and large avatars remain visually stable.

Manual QA follow-up Stage M7 is implemented in code/docs. `frontend/src/stores/dms.ts`
now tracks the current user ID and normalizes direct-message payloads from REST or
gateway dispatches so one-to-one DM rows always display the other participant while
message rows keep the actual author. Focused frontend regression coverage verifies
incoming `DM_CREATE` normalization, and browser realtime smoke still passes for
live DM receipt.

Manual QA follow-up Stage M8 is implemented in code/docs. The invite controller now
keeps bottom invite-code copy state separate from per-friend invite delivery state.
Friend-row invite actions create/open a DM and send a localized invite-code message,
while the browser realtime smoke now creates a friend relationship, sends an invite
from the modal, and verifies the recipient receives the invite code in DM realtime.

Manual QA follow-up Stage M9 is implemented in code/docs. `VoiceAudioSink` now binds
the local deafen state to remote audio element `muted`, so deafen blocks local
playback without disconnecting peers. Microphone mute remains a separate control:
it stays available while deafened and independently controls the local microphone
track. Browser realtime smoke verifies remote audio is muted while deafened, the
local microphone stays open until the microphone button is pressed, mute/unmute
works while deafened, and remote audio is restored after undeafen without rejoin.

The app boots in two local modes:

- Docker Compose mode provisions local PostgreSQL and persists created text channels,
  direct messages, relationships, and messages in the `postgres_data` Docker volume.
- Native mode without `DATABASE_URL` still falls back to the process-local demo store
  while preserving async infrastructure boundaries required by the SRS.

## Repository Layout

- `DEVELOPMENT_PROMPT.md`
  - Project-specific AI development prompt adapted from the adaptive prompt template.
  - Defines role, startup order, implementation policy, verification policy,
    documentation policy, security policy, and response policy.
- `package.json`
  - Root script entrypoint.
  - Runs backend tests/lint through `.venv`.
  - Runs frontend dev/lint/build through `frontend/package.json`.
  - Adds `dev:backend:lan` and `dev:frontend:lan` for same-LAN browser testing.
  - Adds `smoke:realtime:browser` for the C8 same-PC two-browser communication
    smoke and `smoke:realtime:redis` for the C4 Redis cross-worker dispatch smoke.
  - Runs Docker Compose through `docker:up`, `docker:down`, and `docker:logs`.
- `compose.yaml`
  - Docker Compose development stack for PostgreSQL, backend, and frontend.
  - Uses external `DATABASE_URL` when provided; otherwise supplies a local PostgreSQL
    URL pointing at the `postgres` service.
  - Uses external `REDIS_URL` when provided; Redis remains optional and empty by
    default.
- `compose.redis-smoke.yaml`
  - Optional C4 override that adds Redis and `backend-secondary` on port 8001.
  - Use only for Redis multi-worker realtime verification; normal local Docker
    remains Redis-free.
- `scripts/realtime_redis_smoke.py`
  - Repeatable C4 smoke: secondary backend WebSocket session receives server text and
    DM dispatches created through the primary backend.
  - Keeps tokens and message contents in memory only and prints no private payloads.
- `backend/`
  - FastAPI ASGI backend.
  - Python package is configured by `backend/pyproject.toml`.
- `frontend/`
  - Vue 3 + Vite client.
  - TypeScript, Pinia, Vue Router, Oxlint, and lucide icons are configured here.
- `docs/`
  - Long-lived project planning documents.
- `docs/README.md`
  - Documentation index and task-based reading guide.
  - Lists startup reading order, task-specific docs, update rules, and documentation
    verification commands.
- `docs/stage-7-11-responsive-qa.md`
  - Records Stage 7.11 desktop/mobile screenshot paths, viewport metrics, fixes, and
    residual manual QA notes.
- `docs/stage-7-12-final-qa.md`
  - Records Stage 7.12 command verification, Docker smoke, browser smoke workflow,
    and residual external QA notes.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md`
  - Branch, commit, push, staging, verification, and final-report workflow for the
    current `main`-based GitHub flow.
- `docs/PROMPT_COMPLIANCE.md`
  - Maps `DEVELOPMENT_PROMPT.md` policies to concrete repository files and documents.
  - Records prompt-alignment status plus external gaps that cannot be closed locally.
- `docs/prompts/`
  - Task-specific prompt library for future specialized work.
  - `discord-clone-qa-test-prompt.md` defines the multi-role QA audit process for
    finding missing, broken, inconsistent, and visually weak clone behavior.
  - `realtime-communication-implementation-prompt.md` defines the communication
    implementation process for WebSocket gateway, realtime text, WebRTC voice,
    screen sharing, cross-PC access, technology selection, and noise-reduction
    review.
- `docs/remediation-tasks/realtime-communication-plan.md`
  - Current communication implementation plan.
  - Selects the existing FastAPI WebSocket gateway plus browser WebRTC stack for
    hardening rather than replacement, and defines staged work for reconnect,
    duplicate suppression, Redis fan-out verification, native audio constraints,
    WebRTC lifecycle hardening, LAN/TURN readiness, and two-session QA.
- `docs/remediation-tasks/friend-relationship-implementation-plan.md`
  - Future Friends/Add Friend implementation plan.
  - Records that the current Add Friend form is UI-only and defines staged work for
    friend request send, incoming/outgoing pending state, accept/reject/cancel,
    remove friend, block/unblock, relationship realtime updates, persistence, and
    two-browser QA.
- `docs/realtime-communication-qa.md`
  - Stage C8 and later communication QA checklist.
  - Documents automated two-browser same-PC smoke, same-PC manual QA, LAN QA,
    TURN/NAT QA, privacy rules, and latest communication QA result notes.
- `docs/remediation-tasks/discord-clone-qa-remediation-2026-06-19.md`
  - QA-derived UI/workflow remediation development plan.
  - Promotes the QA findings into implementation-ready work items with development
    directives, likely owner files, acceptance criteria, regression checks, and
    staged remediation order for visible controls, shell layering, message
    timelines, Friends/DM structure, voice state, context menus, empty states, and
    final responsive/realtime QA. A 2026-06-19 follow-up QA pass added explicit
    settings-surface polish, hidden-control accessibility, topbar ownership, and
    voice participant de-duplication requirements.
- `docs/store-clone-implementation-plan.md`
  - Detailed staged plan for implementing a Discord Store-like in-app shop.
  - Covers Store catalog, browse/search/filter, item detail preview, demo purchase,
    inventory, apply, gifting, Orbs, Nitro-like discounts, persistence, and QA.
  - Deferred after Stage 6.4 because the target is the full Discord app, not a
    Store-first surface.
- `docs/discord-app-clone-implementation-plan.md`
  - Current primary staged plan for cloning the core Discord web app rooted at
    `https://discord.com/channels/@me`.
  - Covers Friends/DM home, private-channel sidebar, server rail, server/channel
    workspace, DM messaging, settings, voice UX, discovery/add server flows,
    persistence expansion, responsive QA, and documentation.
- `docs/discord-ui-remediation-plan.md`
  - Current controlling Stage 8 plan for Discord UI polish, layout overlap fixes,
  Korean/English i18n, voice/status clarity, placeholder-button reliability,
    responsive/accessibility QA, and final verification.
- `docs/discord-visual-parity-remediation-plan.md`
  - Current controlling Stage 9 plan for real Discord versus clone visual parity.
  - Records screenshot-based problem inventory, staged remediation process,
    verification rules, and additional user reference-data requests.
- `docs/stage-9-final-qa.md`
  - Records Stage 9 command verification, browser QA coverage, completed visual
    parity changes, and residual local-data/capture notes.
- `docs/discord-interaction-polish-plan.md`
  - Current controlling Stage 10 plan for Discord-like interaction polish.
  - Records latest screenshot-based issues, external Discord behavior references,
    stage-by-stage remediation, feature visibility policy, and verification rules.
- `docs/architecture-principles-audit.md`
  - Current architecture-principles and design-pattern audit.
  - Documents SRP, OCP, DIP, encapsulation, DRY, and testability gaps in
    `frontend/src/App.vue`, `frontend/src/stores/guilds.ts`,
    `frontend/src/composables/useVoiceRtc.ts`,
    `backend/app/repositories/guilds.py`, `backend/app/services/guild_service.py`,
    and `backend/app/gateway/manager.py`.
  - Lists the previous Stage 10/11 process to preserve for future refactor stages.
- `docs/project-file-map.md`
  - Quick project folder/file ownership map for faster path lookup before
    implementation.
  - Must be updated when a project folder or important source file is added,
    removed, renamed, or assigned a meaningfully different responsibility.
- `docs/frontend-css-i18n-ownership.md`
  - Stage 12.9 frontend CSS and i18n ownership plan.
  - Defines future split order and verification rules for `base.css` and
    `i18n/index.ts`.
- `docs/structure-map/`
  - Fast-navigation structure folder.
  - `README.md` defines usage and update rules.
  - `reference-map.md` records core file references and reverse references for
    high-impact backend/frontend files.
- `docs/stage-10-baseline.md`
  - Stage 10.0 baseline lock for FHD 100% comparison screenshots, problem inventory,
    and persistent/demo/test data classification.
- `.env.example`
  - Non-secret environment variable template.
  - Real `.env` files must stay untracked.
- `.dockerignore`, `backend/.dockerignore`, `frontend/.dockerignore`
  - Prevent local virtualenvs, dependencies, build output, secrets, and cache files
    from entering Docker build contexts.

## Backend Map

- `backend/app/main.py`
  - Defines `create_app()`.
  - Registers CORS, local token-bucket rate limiting, REST routes, and WebSocket routes.
  - Lifespan startup connects optional database and Redis pools.
  - Starts the Redis gateway-event subscriber task when Redis is configured and
    cancels it during shutdown.
  - Starts the gateway zombie-connection reaper task and cancels it during shutdown.
- `backend/app/core/config.py`
  - Pydantic settings.
  - Reads `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `CORS_ORIGINS`,
    `WEBRTC_ICE_SERVERS_JSON`, and runtime settings.
  - Validates ICE server entries by requiring non-empty `urls` and exposes TURN
    detection for voice deployment checks.
- `backend/app/core/security.py`
  - Password hashing helpers using bcrypt.
  - JWT creation and decoding using PyJWT.
- `backend/app/api/dependencies.py`
  - Bearer-token dependency for protected REST routes.
  - Decodes JWTs and returns the current user payload.
- `backend/app/api/errors.py`
  - Shared REST route exception mapping helper.
  - Converts service-layer `KeyError`, `PermissionError`, and `ValueError` into
    route-specific HTTP responses for guild, channel, and DM routes.
- `backend/app/api/routes/auth.py`
  - `POST /api/auth/register` creates a database-backed user with bcrypt password
    hashing and returns a JWT.
  - `POST /api/auth/login` verifies username/password credentials and returns a JWT.
  - `GET /api/auth/me` returns the current bearer-token user payload.
  - Registration/login return `503` when no database pool is configured.
- `backend/app/core/rate_limit.py`
  - In-memory token bucket middleware for local Stage 1 protection.
  - Intended to be replaced or backed by Redis during realtime/distributed stages.
- `backend/app/core/sanitize.py`
  - Sanitizes message payloads by removing script blocks, inline event handlers, and
    `javascript:` URLs, then escaping HTML.
- `backend/app/db/pool.py`
  - Optional asyncpg connection pool wrapper.
  - No pool is created when `DATABASE_URL` is empty, so local demo mode can boot.
  - Runs `backend/app/db/schema.sql` through `migrate()` when a database pool exists.
  - Tracks the applied schema version in `schema_migrations`.
- `backend/app/db/schema.sql`
  - Initial PostgreSQL schema for users, guilds, channels, messages, roles, guild
    members, invites, and member roles.
  - Stage 7.10 adds DM profiles, relationships, direct message channels, direct
    message members with unread counts, and direct messages.
- `backend/app/db/seed.py`
  - Seeds the initial SRS demo guild, channels, members, and messages into PostgreSQL.
  - Seeds safe demo relationship and direct message data into PostgreSQL.
  - Uses idempotent inserts and skips guilds/DM rows that already exist.
- `backend/app/domain/snowflake.py`
  - JavaScript-safe Snowflake ID generator.
  - Uses a custom 2026 epoch and 53-bit-safe layout.
- `backend/app/domain/permissions.py`
  - Discord-style bitfield permissions.
  - `merge_permissions()` ORs permission values.
  - `has_permission()` treats `ADMINISTRATOR` as all permissions.
- `backend/app/gateway/opcodes.py`
  - Gateway opcode enum: Dispatch, Heartbeat, Identify, Voice State, Guild Members,
    Voice Signal, Hello, and Heartbeat ACK.
- `backend/app/gateway/events.py`
  - Pydantic gateway event, identify, voice state, and voice signal payload schemas.
- `backend/app/gateway/manager.py`
  - In-memory WebSocket connection registry.
  - Tracks user identity, sequence, heartbeat timestamp, subscribed guild IDs, and
    subscribed channel IDs.
  - Contains zombie-connection reaping helper.
  - Broadcasts Discord-style dispatch payloads to connections subscribed to a channel.
  - Broadcasts guild-scoped dispatch payloads and keeps guild/channel subscriptions in
    sync when channel or guild membership snapshots change.
  - Tracks the active voice channel for each identified connection and can route
    `VOICE_SIGNAL` payloads to a target user in the same voice channel.
  - Tracks subscribed DM IDs and broadcasts `DM_CREATE`/`DM_MESSAGE_CREATE`
    dispatches to DM subscribers.
- `backend/app/gateway/reaper.py`
  - Background loop that periodically calls `gateway_manager.reap_zombies()` using
    the configured heartbeat interval.
- `backend/app/gateway/router.py`
  - `/gateway` WebSocket endpoint.
  - Sends Hello, accepts Identify, validates JWT, sends Ready, handles Heartbeat ACK,
    Request Guild Members, and Update Voice State placeholders.
  - On Identify, loads the authenticated user's guilds/DMs and subscribes the
    connection to every guild channel plus visible DM thread.
  - `UPDATE_VOICE_STATE` validates guild/channel subscriptions, updates the
    connection's active voice channel, and dispatches `VOICE_STATE_UPDATE` to voice
    channel subscribers.
  - `VOICE_SIGNAL` validates the sender is connected to the voice channel and routes
    offer/answer/ICE payloads to the target user.
- `backend/app/realtime/redis_bus.py`
  - Optional Redis asyncio client wrapper.
  - Connects only when `REDIS_URL` is configured; connection failure logs a
    privacy-safe error and leaves realtime on local fallback.
- `backend/app/realtime/events.py`
  - Defines the Redis gateway-event channel name and `RealtimeGatewayEvent` schema.
- `backend/app/realtime/publisher.py`
  - Publishes `MESSAGE_CREATE`, `MESSAGE_UPDATE`, `MESSAGE_DELETE`, `CHANNEL_CREATE`,
    `GUILD_UPDATE`, `DM_CREATE`, and `DM_MESSAGE_CREATE` payloads to Redis when
    configured.
  - Falls back to the shared local realtime fan-out helper when Redis is absent or a
    publish attempt fails.
- `backend/app/realtime/subscriber.py`
  - Consumes Redis gateway-event Pub/Sub messages and fans them out to local WebSocket
    subscribers through the shared realtime fan-out helper.
  - Logs subscriber start/stop/restart and invalid payload rejection without message
    contents.
- `backend/app/realtime/fanout.py`
  - Shared realtime gateway-event fan-out and local subscription synchronization.
  - Updates local gateway subscriptions for channel creation, guild membership
    changes, and `DM_CREATE` participants before broadcasting to channel, guild, or
    DM subscribers.
- `backend/app/api/routes/health.py`
  - `/api/health` reports service status and whether DB/Redis are configured/connected.
  - Empty `DATABASE_URL` and `REDIS_URL` values are reported as not configured.
- `backend/app/api/routes/dev.py`
  - `/api/dev/session` creates a local development JWT and user payload.
  - Only intended for local/dev/test environments.
- `backend/app/api/routes/guilds.py`
  - `/api/guilds/me` requires a bearer token and returns the authenticated user's
    PostgreSQL-backed guild memberships when connected, otherwise demo guild data for
    the frontend shell.
  - `GET /api/guilds/{guild_id}` refreshes a single guild snapshot for current members.
  - `POST /api/guilds` creates a guild owned by the authenticated user with default
    `general` text and `voice-room` voice channels.
  - `POST /api/guilds/{guild_id}/invites` creates an invite code for users with
    `CREATE_INSTANT_INVITE`.
  - `POST /api/guilds/invites/{code}/join` adds the authenticated user to the invited
    guild.
  - `POST /api/guilds/{guild_id}/roles` creates a role for administrators and returns
    the refreshed guild payload.
  - `POST /api/guilds/{guild_id}/members/{member_id}/roles` assigns a role to a member.
  - `DELETE /api/guilds/{guild_id}/members/{member_id}/roles/{role_id}` removes an
    assigned role from a member.
  - `DELETE /api/guilds/{guild_id}/members/{member_id}` removes a non-owner member
    from a guild for administrators.
  - `POST /api/guilds/{guild_id}/channels` creates text or voice channels through
    the guild service.
  - Channel creation returns `403` when the authenticated user lacks
    `MANAGE_CHANNELS`.
  - Channel creation publishes `CHANNEL_CREATE`; invite join, role mutations, and
    member removal publish `GUILD_UPDATE`.
- `backend/app/api/routes/channels.py`
  - `POST /api/channels/{channel_id}/messages` creates sanitized messages through
    the guild service.
  - `PATCH /api/channels/{channel_id}/messages/{message_id}` edits sanitized message
    content for the message author or users with `MANAGE_MESSAGES`.
  - `DELETE /api/channels/{channel_id}/messages/{message_id}` deletes messages for
    the message author or users with `MANAGE_MESSAGES`.
  - Message creation returns `403` when the authenticated user is not a guild member
    or lacks `SEND_MESSAGES`.
  - After persistence succeeds, publishes `MESSAGE_CREATE`, `MESSAGE_UPDATE`, or
    `MESSAGE_DELETE` through the realtime publisher.
- `backend/app/api/routes/users.py`
  - `GET /api/users/me/relationships` requires a bearer token and returns safe demo
    relationship rows for the current local user.
- `backend/app/api/routes/dms.py`
  - `GET /api/dms` requires a bearer token and returns only DM threads where the
    current user is a participant.
  - `POST /api/dms` creates or returns an existing one-to-one or group DM for known
    demo recipients.
  - `POST /api/dms/{dm_id}/messages` creates sanitized DM messages and rejects
    non-members or path/payload ID mismatches.
- `backend/app/api/routes/meta.py`
  - `/api/meta/permissions` exposes permission names and integer values.
  - `/api/meta/voice` exposes WebRTC ICE server config from
    `WEBRTC_ICE_SERVERS_JSON`, plus ICE server count and whether TURN is configured.
- `backend/app/api/routes/store.py`
  - `GET /api/store/catalog` requires a bearer token and returns the demo Store
    catalog, featured items, categories, filters, demo Orb balance, Nitro-like demo
    metadata, and default ownership states.
  - `GET /api/store/items/{item_id}` requires a bearer token and returns item detail,
    related items, included bundle items, gift eligibility, purchase eligibility, and
    current equip eligibility.
  - Unknown Store item IDs return `404`.
- `backend/app/demo/data.py`
  - Initial guild/channel/member/message seed data used before persistence is wired.
- `backend/app/demo/store_catalog.py`
  - Original demo Store catalog for Stage 6.
  - Defines five collections, 23 cosmetics, three bundles, four Orb exclusives, and
    limited-drop metadata without real Discord assets, item names, or prices.
  - Exposes copy-returning helpers for listing collections/items, fetching one item,
    and building filter metadata for future Store APIs.
- `backend/app/demo/store.py`
  - Process-local mutable demo store.
  - Creates guilds, invite codes, roles, member-role assignments, channels, messages,
    relationships, DM threads, and DM messages with Snowflake IDs.
  - Updates and deletes messages for the message author or guild owner.
  - Still used for guild/channel/message fallback when no database pool is configured.
  - DM and relationship state intentionally uses this demo store until Stage 7.10
    adds PostgreSQL persistence and realtime DM dispatch.
  - Filters guild reads by member and enforces owner-only channel creation plus
    owner-only role/member management plus member-only message creation.
- `backend/app/repositories/guilds.py`
  - PostgreSQL repository for guild creation, invite creation/join, role creation,
    member-role assignment/removal, member removal, guild membership reads, channel
    creation, message creation, message update, and message deletion.
  - Converts asyncpg rows into `GuildRead`, `ChannelRead`, `MemberRead`, and
    `RoleRead`/`MessageRead` schemas.
  - Computes effective permissions from ownership, base member permissions, and role
    permissions.
  - Requires `MANAGE_CHANNELS` for channel creation and `SEND_MESSAGES` for message
    creation.
  - Requires message author ownership or `MANAGE_MESSAGES` for message update/delete.
  - Requires `ADMINISTRATOR` for role creation and member-role mutations.
- `backend/app/repositories/dms.py`
  - PostgreSQL repository for relationship reads, DM membership reads, DM creation,
    DM message creation, membership checks, unread count updates, and `DmRead`
    assembly.
  - Uses JavaScript-safe Snowflake IDs and keeps DM participants scoped to current
    DM membership.
- `backend/app/repositories/users.py`
  - PostgreSQL repository for creating users and fetching password hashes by username.
- `backend/app/services/guild_service.py`
  - Runtime switch between PostgreSQL repositories and the process-local demo store.
  - Keeps route handlers independent from the current persistence mode.
- `backend/app/services/dm_service.py`
  - Async service boundary for Stage 7.3 DM APIs.
  - Uses `dm_repository` when PostgreSQL is connected and `demo_store` otherwise for
    relationships, DM list/create, and DM message creation.
- `backend/app/services/auth_service.py`
  - Coordinates registration/login with async repository calls and runs bcrypt
    hashing/verification off the event loop.
- `backend/app/services/store_service.py`
  - Builds authenticated Store catalog and item-detail responses from the safe demo
    catalog.
  - Applies the current user's demo metadata, including `not_owned` ownership state
    and a local demo Nitro-like flag for user ID `42`.
  - Keeps Stage 6 read APIs independent from future purchase/inventory persistence.
- `backend/app/schemas/`
  - Pydantic API schemas for auth, guilds, messages, Direct Messages, and Store
    contracts.
- `backend/app/schemas/dm.py`
  - Relationship, DM participant, DM thread, DM message, DM create, and DM message
    create contracts.
  - Sanitizes DM message content with the shared message sanitizer at the schema
    boundary.
- `backend/app/schemas/store.py`
  - Store item, collection, price, preview, catalog, detail, inventory, purchase,
    gift, equip, and mutation response schemas.
  - Defines supported item types, ownership states, sort modes, and equip slots for
    Stage 6 before Store routes are implemented.
  - Validates hex color tokens, JavaScript-safe IDs, bundle child-item boundaries, and
    Store mutation request payload limits.
- `backend/tests/`
  - Unit tests for permissions, Snowflake IDs, settings, demo store mutations, protected
    API routes, gateway connection management, message schema sanitization, Store
    schema validation, Store seed catalog integrity, Store read API contracts, and
    focused guild repository mutation behavior for guild creation/reads, channel
    creation, invites, roles, member removal, and message update/delete.

## Frontend Map

- `frontend/vite.config.ts`
  - Vite Vue config.
  - Proxies `/api` to `VITE_BACKEND_PROXY_TARGET`, defaulting to
    `http://127.0.0.1:8000`.
  - Proxies `/gateway` WebSocket traffic to the same target with `ws` protocol.
  - Compose sets `VITE_BACKEND_PROXY_TARGET=http://backend:8000`.
- `frontend/src/main.ts`
  - Creates Vue app, Pinia, and Vue Router.
- `frontend/src/App.vue`
  - Main Discord-like workspace screen.
  - Composes server rail, private-channel sidebar, Friends home, channel sidebar,
    DM chat view, server chat view, member list, and voice panel.
  - Restores saved sessions, shows auth UI when logged out, loads guild data after
    authentication, and connects the gateway.
  - Opens the `@me` Friends destination after login, preserves current guild/channel
    state, and switches back to the server workspace when a server is selected.
  - Renders Discord-like server channel header controls for threads, notification
    settings, pinned messages, member-list toggle, search, inbox, and help.
  - Owns member-list visibility state and local placeholder notices for app-shell
    controls that are intentionally not backend-backed yet.
- `frontend/src/components/AuthPanel.vue`
  - Login/register form plus an explicit Demo user button for local development.
  - Emits auth actions to `App.vue`; it does not own token storage.
- `frontend/src/services/api.ts`
  - Small fetch wrapper for GET and POST calls.
  - GET, POST, PATCH, and DELETE calls accept an optional bearer token.
  - Exposes relationship and Direct Message wrappers for
    `/api/users/me/relationships`, `/api/dms`, and `/api/dms/{dm_id}/messages`.
  - Exposes Store read wrappers for `/api/store/catalog` and
    `/api/store/items/{item_id}`.
- `frontend/src/services/browserApi.ts`
  - Browser API adapter boundary.
  - Owns localStorage, clipboard, document-level listener, viewport/location,
    gateway WebSocket URL, navigator platform, and document view-transition
    helpers for high-use clone workflows.
- `frontend/src/stores/session.ts`
  - Pinia session store.
  - Calls `/api/auth/login`, `/api/auth/register`, `/api/auth/me`, and
    `/api/dev/session`.
  - Stores JWT/current user through `browserStorage` and clears them on logout.
- `frontend/src/stores/guilds.ts`
  - Pinia guild store.
  - Uses `shallowRef` for guild data as required by the SRS performance guidance.
  - Loads `/api/guilds/me`.
  - Tracks loading, mutation, and API error state for guild/channel/message/invite
    operations.
  - Tracks active guild, active channel, and active messages.
  - Delegates voice channel, connected voice guild/channel, voice states, and the
    latest voice signal dispatch to `frontend/src/stores/voicePresence.ts`.
  - Calls the protected guild creation API and selects the new guild's first channel.
  - Calls invite creation and invite join APIs.
  - Calls role creation, role assignment, and role removal APIs.
  - Calls single-guild refresh and member removal APIs.
  - Calls the protected channel creation and message creation/update/delete APIs.
  - Applies gateway `MESSAGE_CREATE` dispatches with message ID deduplication so REST
    echoes and WebSocket events do not double-insert messages.
  - Applies gateway `MESSAGE_UPDATE` and `MESSAGE_DELETE` dispatches to update or
    remove local message state.
  - Applies gateway `CHANNEL_CREATE` dispatches with channel ID deduplication.
  - Applies gateway `GUILD_UPDATE` dispatches by replacing the local guild snapshot
    and preserving a valid active channel.
  - Uses the browser API adapter for optional document view transitions during
    channel switching.
- `frontend/src/stores/dms.ts`
  - Pinia DM store for Stage 7.3.
  - Uses `shallowRef` for relationship rows and DM thread snapshots.
  - Loads authenticated relationship and DM data, creates or opens DM threads from a
    friend row, sends sanitized DM messages through the backend, appends returned
    messages immutably, and resets on logout.
  - Applies `DM_CREATE` and `DM_MESSAGE_CREATE` gateway dispatches with idempotent
    upsert/append behavior.
  - Applies `PRESENCE_UPDATE` gateway dispatches only into matching relationship
    rows; DM sidebar rows and DM intro surfaces intentionally do not repaint
    presence/activity from lightweight status updates.
- `frontend/src/stores/navigation.ts`
  - Pinia app destination store for the Discord-like shell.
  - Tracks `friends`, `dm`, `server_channel`, `voice_channel`, and `settings`
    destinations plus active DM ID.
  - Keeps `@me` navigation independent from guild/channel state.
- `frontend/src/stores/store.ts`
  - Pinia Store state module for Stage 6.
  - Uses `shallowRef` for catalog, active item detail, and future inventory payloads.
  - Tracks catalog/detail/inventory loading, active tab, search query, selected item
    type/ownership/show-only/color/theme/collection filters, sort mode, mutation
    state, and API errors.
  - Provides computed featured, Orb-eligible, and filtered/sorted item result sets.
  - Resets Store state independently from guild/chat state on logout.
- `frontend/src/composables/useGateway.ts`
  - Browser WebSocket gateway client.
  - On Hello opcode 10, sends Identify opcode 2 and starts heartbeat opcode 1.
  - Shows connected state after Ready dispatch.
  - Accepts a dispatch callback and forwards non-READY gateway dispatch events to the
    app store.
  - Exposes `updateVoiceState()` for opcode 4, `sendVoiceSignal()` for opcode 5,
    and `updatePresence()` for opcode 6.
  - Builds gateway URL and navigator platform values through `browserApi`.
- `frontend/src/composables/useVoiceRtc.ts`
  - Public WebRTC voice facade used by the app and Stage 12.1 voice session
    controller.
  - Composes focused modules for media capture, VAD, peer connections, screen-share
    track management, WebRTC stats, mute state, and cleanup.
- `frontend/src/composables/voiceMedia.ts`
  - Browser microphone/display capture helpers plus media-track stop and mute
    helpers.
- `frontend/src/composables/voiceVad.ts`
  - Local AudioContext/analyser voice activity detection and input-level sampling.
- `frontend/src/composables/voicePeerConnections.ts`
  - Peer connection registry for offer/answer/ICE handling, remote stream tracking,
    participant sync, and peer renegotiation.
- `frontend/src/composables/useVoiceSessionController.ts`
  - Stage 12.1 voice session orchestration boundary.
  - Loads voice metadata, coordinates voice join/leave/switch confirmation, syncs
    mute/deafen state through gateway opcode 4, toggles screen sharing through
    `useVoiceRtc()`, synchronizes connected participants, and applies incoming
    voice signals while keeping `App.vue` focused on layout/event wiring.
- `frontend/src/stores/voicePresence.ts`
  - Stage 12.3 voice-presence store boundary used by `guilds.ts`.
  - Owns connected voice guild/channel refs, voice states, latest voice signal,
    active/connected voice-state derived lists, and voice-presence mutation helpers.
- `backend/app/services/dm_storage.py`
  - Stage 12.4 DM storage provider boundary used by `dm_service.py`.
  - Selects PostgreSQL or demo direct-message storage once and exposes a common
    async interface for relationships, DM lists, DM creation, and DM messages.
- `backend/app/repositories/guild_common.py`
  - Stage 12.5 shared guild repository helper boundary.
  - Owns guild aggregate reads, permission calculation, user upsert, member/role
    validation, role labels, and shared guild Snowflake ID generation.
- `frontend/src/components/ServerRail.vue`
  - Discord-like rail with `@me` Direct Messages button, server icons, separators,
    server unread/mention badges, muted indicator, demo folder grouping, create-server
    icon button, and discovery icon button.
  - Uses accessible labels that include unread, mention, and muted state.
- `frontend/src/components/PrivateChannelSidebar.vue`
  - `@me` sidebar with search/start conversation button, Friends/Nitro/Shop/Quests
    entries, API-backed DM list, unread badges, and create-DM action placeholder.
- `frontend/src/components/FriendsHome.vue`
  - Friends home surface with Online/All/Pending/Blocked/Add Friend tabs, search,
    API-backed safe demo relationship rows, message actions, and add-friend
    placeholder form.
  - Emits `messageFriend` so `App.vue` can create or open a DM through `dms.ts`.
  - Real friend request send/receive, accept/reject/cancel, remove friend,
    block/unblock, and realtime relationship updates are planned in
    `docs/remediation-tasks/friend-relationship-implementation-plan.md`.
- `frontend/src/components/DirectMessageView.vue`
  - Renders selected DM participant intro, message history, and a DM composer inside
    the `dm` destination.
  - Keeps server channel editing/deletion behavior isolated in `ChatView.vue`.
- `frontend/src/components/ChannelSidebar.vue`
  - Text and voice channel lists.
  - Provides a server menu entry, Events entry, collapsible text/voice categories,
    inline text and voice channel creation forms, invite actions, and channel settings
    placeholder actions.
- `frontend/src/components/ChatView.vue`
  - Message list and composer UI.
  - Emits submitted message content, message edits, and message deletions to the guild
    store.
  - Shows edit controls for the current user's own messages and delete controls for
    own messages or `MANAGE_MESSAGES`.
  - Provides local reply targeting, message options menu, and composer action buttons
    for upload, gift, apps/actions, and emoji while preserving the existing backend
    send/edit/delete behavior.
- `frontend/src/components/MemberList.vue`
  - Member presence list.
  - Shows role labels and exposes administrator-only controls for role creation,
    assignment, and removal.
  - Exposes member refresh and non-owner member removal controls.
- `frontend/src/components/VoicePanel.vue`
  - Voice connection toggle UI.
  - Shows voice participant count, gateway signaling readiness, local speaking state,
    microphone input level, mute control, screen-share control, TURN/STUN status, and
    WebRTC quality diagnostics.
- `frontend/src/components/VoiceAudioSink.vue`
  - Binds remote `MediaStream` instances to hidden autoplay audio elements.
- `frontend/src/components/VoiceVideoSink.vue`
  - Binds remote screen-share video streams to floating video preview tiles.
- `frontend/src/styles/base.css`
  - App layout, accessible focus styles, responsive behavior, and View Transitions rule.
- `frontend/src/types.ts`
  - Shared frontend types matching the current backend demo API shape.
  - Includes Store TypeScript contracts for item types, ownership states, catalog,
    filters, item detail, inventory, purchase, gift, equip, and mutation responses.
- `docs/deployment.md`
  - VM/runtime deployment checklist, production environment variables, HTTPS/gateway
    notes, native/Docker LAN commands, external Compose/Caddy/coturn reference
    files, ICE/TURN guidance, voice verification, and hardening notes.
- `docs/voice-qa.md`
  - Two-browser local smoke test, LAN smoke test, TURN/NAT test, and deployment
    verification checklist for voice, screen sharing, and browser WebRTC stats.
- `backend/Dockerfile`
  - `dev` target installs backend dev dependencies and runs Uvicorn with reload.
  - `runtime` target installs production dependencies and runs Gunicorn with Uvicorn
    workers.
- `frontend/Dockerfile`
  - `dev` target runs Vite on `0.0.0.0`.
  - `build` target produces the static bundle.
  - `runtime` target serves the bundle through Nginx.
- `frontend/nginx.conf`
  - Production static server config.
  - Proxies `/api/` and `/gateway` to `backend:8000` for containerized deployments.

## Current Integrations

- Frontend startup flow:
  - `App.vue` calls `session.restoreSession()`.
  - If no saved token exists, `AuthPanel.vue` is shown.
  - Login/register POST to `/api/auth/login` or `/api/auth/register`.
  - Demo user explicitly POSTs to `/api/dev/session`.
  - After authentication, `App.vue` calls `guilds.loadGuilds(session.token)` and
    `useGateway().connect(token)`.
  - Logout closes the gateway, clears Pinia guild state, and removes saved session
    data from localStorage.
- Auth API flow:
  - Clients POST `{ username, password }` to `/api/auth/register` or
    `/api/auth/login`.
  - Backend validates auth schema payloads, uses PostgreSQL users, bcrypt password
    hashes, and returns the same JWT response shape as the dev session endpoint.
  - `GET /api/auth/me` validates bearer tokens through `get_current_user`.
- Store read API flow:
  - Store read APIs require the same bearer-token dependency as guild/message APIs.
  - `GET /api/store/catalog` returns the Stage 6 demo catalog from
    `store_service.get_store_catalog()`.
  - `store_service` reads original catalog data from `backend/app/demo/store_catalog.py`,
    applies the current user's default `not_owned` state, and returns featured items,
    categories, filter metadata, demo Orb balance, and Nitro-like demo metadata.
  - `GET /api/store/items/{item_id}` returns item detail, included bundle children,
    related items, purchase/gift eligibility, and current equip eligibility.
- Store frontend state flow:
  - `frontend/src/services/api.ts` wraps Store catalog and item-detail fetches.
  - `frontend/src/stores/store.ts` loads Store catalog/detail data with the current
    bearer token and keeps Store filters/sort state independent from guild state.
  - `App.vue` calls `store.resetStoreState()` during logout so Store state cannot
    leak between sessions.
- Discord app destination flow:
  - `openWorkspace()` loads guilds and voice config, then opens the `friends`
    destination before connecting the gateway.
  - `openWorkspace()` also loads relationships and Direct Messages through
    `frontend/src/stores/dms.ts`.
  - `ServerRail.vue` emits `home` for the `@me` button and `select` for guild icons.
  - `App.vue` routes `friends` and `dm` destinations to
    `PrivateChannelSidebar.vue`; `friends` renders `FriendsHome.vue`, while `dm`
    renders `DirectMessageView.vue`.
  - Selecting a server switches the destination to `server_channel` and preserves the
    existing guild/channel chat behavior.
- Direct Message flow:
  - `GET /api/users/me/relationships` and `GET /api/dms` hydrate `dms.ts` after
    login/demo session restore.
  - `PrivateChannelSidebar.vue` renders loaded DM threads and opens a selected thread
    through `navigation.openDm()`.
  - `FriendsHome.vue` emits `messageFriend`; `App.vue` calls
    `dms.createDm(token, [friendId])`, then opens the returned thread.
  - `DirectMessageView.vue` emits submitted content; `dms.ts` POSTs to
    `/api/dms/{dm_id}/messages`, appends the returned sanitized message, and keeps
    `ChatView.vue` focused on server text channels.
- Guild creation flow:
  - `ServerRail.vue` and the empty workspace call `App.vue`'s create-server handler.
  - `App.vue` opens a focused server-name dialog.
  - `guilds.ts` POSTs to `/api/guilds` with the current bearer token.
  - Backend creates the guild, owner membership, `general`, and `voice-room`, then
    returns a complete `GuildRead`.
  - `guilds.ts` appends the guild, selects it, and selects its first channel.
- Invite flow:
  - Active workspace topbar exposes create-invite and join-server icon buttons.
  - `guilds.ts` POSTs to `/api/guilds/{guild_id}/invites` to receive an invite code.
  - Another authenticated user can submit that code through the join-server dialog.
  - `guilds.ts` POSTs to `/api/guilds/invites/{code}/join`, appends or replaces the
    joined guild in local state, then selects it.
- Role management flow:
  - `MemberList.vue` emits role creation, assignment, and removal actions when the
    active guild grants `ADMINISTRATOR`.
  - `guilds.ts` POSTs to `/api/guilds/{guild_id}/roles` to create a role, POSTs to
    `/api/guilds/{guild_id}/members/{member_id}/roles` to assign it, and DELETEs
    `/api/guilds/{guild_id}/members/{member_id}/roles/{role_id}` to remove it.
  - Backend validates JWTs, checks administrator permissions, writes to
    `roles/member_roles` in PostgreSQL or the demo store, and returns the refreshed
    `GuildRead` for local state replacement.
- Member management flow:
  - `MemberList.vue` emits refresh and remove-member actions.
  - `guilds.ts` GETs `/api/guilds/{guild_id}` to refresh the active guild and DELETEs
    `/api/guilds/{guild_id}/members/{member_id}` to remove a non-owner member.
  - Backend validates JWTs, checks administrator permissions for removal, rejects owner
    and self-removal, deletes the membership from PostgreSQL or the demo store, and
    returns the refreshed `GuildRead`.
- Message mutation flow:
  - `ChatView.vue` emits submitted content.
  - `guilds.ts` POSTs to `/api/channels/{channel_id}/messages` with bearer token.
  - Backend validates JWT, sanitizes content, checks guild membership and
    `SEND_MESSAGES`, persists through PostgreSQL when connected or appends to
    `demo_store` in native fallback mode, then returns the created message.
  - `guilds.ts` immutably appends the returned message to the active guild state.
  - `ChatView.vue` also emits edits and deletes for eligible message rows.
  - `guilds.ts` PATCHes or DELETEs
    `/api/channels/{channel_id}/messages/{message_id}` with bearer token.
  - Backend sanitizes edited content, checks the actor is the message author or has
    `MANAGE_MESSAGES`, updates/deletes through PostgreSQL or `demo_store`, and returns
    either the updated message or `{ id, channel_id }`.
  - `guilds.ts` updates or removes the local message after the REST response and also
    accepts matching realtime echoes.
- Channel creation flow:
  - `ChannelSidebar.vue` opens an inline channel-name form from the plus icon.
  - `guilds.ts` POSTs to `/api/guilds/{guild_id}/channels` with bearer token.
  - Backend validates JWT, checks `MANAGE_CHANNELS`, persists through PostgreSQL when
    connected or appends to `demo_store` in native fallback mode, then returns the
    created channel.
  - `guilds.ts` immutably appends the returned channel and selects it.
- Gateway flow:
  - Server accepts `/gateway`.
  - Server sends Hello: `{ op: 10, d: { heartbeat_interval } }`.
  - Client sends Identify: `{ op: 2, d: { token, os, library } }`.
  - Server validates JWT, subscribes the connection to the authenticated user's guild
    and channel IDs, and sends Ready dispatch: `{ op: 0, t: "READY" }`.
  - Client sends Heartbeat: `{ op: 1 }`.
  - Server replies Heartbeat ACK: `{ op: 11 }`.
  - The lifespan reaper closes connections that miss two heartbeat windows with code
    `4000` and removes them from the in-memory connection registry.
- Voice signaling flow:
  - `VoicePanel.vue` toggles local voice connection state through `App.vue`.
  - `App.vue` loads ICE config from `/api/meta/voice`, starts microphone capture
    through `useVoiceRtc()`, then calls `useGateway().updateVoiceState()` with opcode
    4, the active guild, and the first voice channel.
  - `/api/meta/voice` also returns `turn_configured`, which the voice panel displays
    as `TURN ready` or `STUN only`.
  - Backend validates the identified connection is subscribed to the guild/channel and
    broadcasts `VOICE_STATE_UPDATE` to voice-channel subscribers.
  - Gateway opcode 5 accepts `offer`, `answer`, or `ice` voice signal payloads and
    routes them to the target user only when the sender and target are in the same
    voice channel.
  - `guilds.ts` stores voice presence state and the latest received signal.
  - `useVoiceRtc()` opens one peer connection per remote voice participant, sends
    offers from the lower user ID to avoid glare, applies answers and ICE candidates,
    renders remote audio through `VoiceAudioSink`, and tears down tracks/connections on
    disconnect.
  - `voicePeerConnections.ts` keys peers by `channelId:userId`, ignores stale
    signals from previous voice channels, queues ICE candidates until remote
    descriptions exist, and performs one bounded failed-peer recreate attempt.
  - Mute toggles local audio track enabled state without leaving the voice channel.
  - Media capture now detects native browser audio constraint support, requests
    supported echo cancellation/noise suppression/auto gain constraints, stores only
    debug-safe support booleans, and normalizes permission/device/screen errors into
    clone UI messages.
  - Screen sharing uses `getDisplayMedia()`, adds/removes a video sender on each
    active peer connection, renegotiates offers, and renders remote screen streams
    through `VoiceVideoSink`.
  - Local VAD samples microphone frequency data and exposes both a speaking flag and
    input-level meter in `VoicePanel`.
  - While connected, `useVoiceRtc()` samples `RTCPeerConnection.getStats()` every two
    seconds and the voice panel displays connected peers, RTT, inbound audio jitter,
    inbound packet loss, outbound audio bitrate, and outbound screen-share bitrate.
  - `RemoteVoiceStream` includes `channelId`, so `App.vue` only mounts audio/video
    sinks for the current connected voice channel.
  - `VoicePanel.vue` owns retry/open-settings/leave actions for media permission
    failures, and `SettingsView.vue` displays supported native audio processing
    without exposing media device labels.
- Realtime message flow:
  - `POST /api/channels/{channel_id}/messages` persists the sanitized message first.
  - `publish_message_create()` emits a `MESSAGE_CREATE` realtime event.
  - `PATCH /api/channels/{channel_id}/messages/{message_id}` persists sanitized
    content first and `publish_message_update()` emits `MESSAGE_UPDATE`.
  - `DELETE /api/channels/{channel_id}/messages/{message_id}` deletes first and
    `publish_message_delete()` emits `MESSAGE_DELETE`.
  - With Redis configured, the payload is published to
    `discord_clone:gateway_events`, consumed by the lifespan subscriber, and broadcast
    to local WebSocket connections subscribed to the channel.
  - Without Redis, the publisher directly uses the local gateway manager so native
    development still receives live message events.
  - `useGateway()` forwards gateway dispatches into `guilds.handleGatewayDispatch()`,
    which appends unseen messages by ID, replaces edited messages, and removes
    deleted messages.
- Realtime DM flow:
  - Gateway Identify loads the authenticated user's DM threads and subscribes the
    connection to their DM IDs.
  - `POST /api/dms` persists or returns a DM thread, publishes `DM_CREATE`, and
    gateway managers add the new DM ID to connected participant subscriptions before
    broadcasting.
  - `POST /api/dms/{dm_id}/messages` persists sanitized DM messages and publishes
    `DM_MESSAGE_CREATE` to DM subscribers.
  - `frontend/src/App.vue` forwards gateway dispatches to both the guild and DM
    Pinia stores, and `frontend/src/stores/dms.ts` applies DM events idempotently.
- Realtime guild state flow:
  - Channel creation publishes `CHANNEL_CREATE` to guild subscribers and updates their
    server-side channel subscriptions so future messages in the new channel can fan
    out without reconnecting.
  - Invite join, role creation/assignment/removal, and member removal publish
    `GUILD_UPDATE`.
  - `GUILD_UPDATE` syncs local gateway guild/channel subscriptions from the incoming
    member and channel snapshot, then broadcasts the refreshed guild payload.
  - The frontend applies `CHANNEL_CREATE` by appending unseen channels and applies
    `GUILD_UPDATE` by replacing the guild snapshot.
- External services:
  - `DATABASE_URL` will point to Neon PostgreSQL.
  - Docker Compose sets `DATABASE_URL` to local PostgreSQL by default.
  - `REDIS_URL` will point to Upstash Redis.
  - Native local shell can leave both empty and use the demo-store fallback.
- Docker development flow:
  - `npm run docker:up` builds and starts `postgres`, `backend`, and `frontend`.
  - Backend startup connects PostgreSQL, runs `schema.sql`, then seeds guild and DM
    demo data.
  - Frontend container proxies API/WebSocket traffic to `backend:8000` inside the
    Compose network.
  - Host browser still uses `http://127.0.0.1:5173`.
  - `npm run docker:down` stops containers while preserving `postgres_data`.
  - Use `docker compose down -v` only when resetting local PostgreSQL data is intended.

## Verification Commands

Run these from the repository root unless noted otherwise:

```powershell
npm run test:backend
npm run lint:backend
npm run lint:frontend
npm --prefix frontend run build
docker compose exec -T backend pytest
```

Local servers:

```powershell
npm run dev:backend
npm run dev:frontend
```

Expected local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

Docker servers:

```powershell
npm run docker:up
npm run docker:down
```

## Known Decisions And Constraints

- `DEVELOPMENT_PROMPT.md` is the highest-level local prompt document for future
  AI-assisted development in this repository. Keep it focused on durable operating
  policy, not one-off implementation details.
- `docs/PROMPT_COMPLIANCE.md` is the audit surface for checking whether the repository
  structure still reflects `DEVELOPMENT_PROMPT.md`.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md` documents the current single-user
  `main`-based push workflow; switch it only when the user requests branch/PR-based
  collaboration.
- The SRS says Pydantic v3, but the current PyPI line is Pydantic v2. The backend
  pins Pydantic v2 and isolates schema code for a future upgrade.
- In Docker Compose mode, text channels and messages persist across backend restarts
  through local PostgreSQL. In native mode without `DATABASE_URL`, created
  messages/channels survive page reloads while the backend process is alive but reset
  when that process restarts.
- Channel creation currently accepts ASCII slug names only, matching Discord-style
  channel names and avoiding inconsistent Unicode slug handling.
- `node_modules/`, `.venv/`, `dist/`, `*.egg-info/`, and `*.tsbuildinfo` are ignored
  and must not be committed.
- Real secrets belong in `.env`, not in Git.
- UI should remain the actual app surface, not a landing page or feature explainer.
- Docker is additive, not a replacement for native local development. Use native
  scripts for quick iteration and Docker when environment reproducibility matters.
- Docker Desktop must be running before `npm run docker:up`.

## Next Work

Next implementation stage:

- Start communication implementation from
  `docs/remediation-tasks/realtime-communication-plan.md`.
- Begin with Stage C0 environment and verification recovery, because the prior QA
  pass found local runner blockers around `.venv/Scripts/python.exe`, `py`, and
  plain `npm` availability.
- Continue through C1 baseline lock before changing gateway, text/DM, Redis, or
  voice behavior.
- Treat two-session browser verification as mandatory for real communication
  claims; store-only tests are not enough.
- Run multi-browser manual voice QA with a real TURN provider configured before
  claiming internet voice support.
- Tune WebRTC quality with real network stats after manual QA exposes bottlenecks.
- Continue production deployment execution when target VM/provider is chosen.
- Resume deferred Store UI work only if the user explicitly returns to Store scope.

Discord app inspection observation:

- `https://discord.com/channels/@me` was inspected through the Codex in-app browser on
  2026-06-03 with the user's logged-in Discord session.
- The implementation target is the Discord app shell: server rail, private-channel
  sidebar, Friends/DM home, server/channel sidebar, channel header controls, message
  timeline/composer, voice channel rows, bottom user panel, and settings entry.
- Do not copy real Discord private names, messages, server content, or assets into
  repository fixtures or documentation.
- Stage 7.1 and 7.2 completed the first app-parity slice:
  - App destination state is in `frontend/src/stores/navigation.ts`.
  - `@me` private sidebar is in `frontend/src/components/PrivateChannelSidebar.vue`.
  - Friends home is in `frontend/src/components/FriendsHome.vue`.
- Stage 7.3 moved safe demo friend/DM data into the backend and completed functional
  DM messaging:
  - DM contracts are in `backend/app/schemas/dm.py`.
  - DM routes are in `backend/app/api/routes/users.py` and
    `backend/app/api/routes/dms.py`.
  - DM service/demo fallback logic is in `backend/app/services/dm_service.py` and
    `backend/app/demo/store.py`.
  - DM frontend state is in `frontend/src/stores/dms.ts`.
  - DM chat UI is in `frontend/src/components/DirectMessageView.vue`.
- Stage 7.4 completed server rail parity:
  - Rail UI is in `frontend/src/components/ServerRail.vue`.
  - Safe demo rail metadata is computed in `frontend/src/App.vue`.
  - The rail exposes `@me` unread count, server unread/mention state, muted state,
    folder grouping, create-server, and discovery entry points.
- Stage 7.5 completed server sidebar and header controls:
  - `frontend/src/components/ChannelSidebar.vue` owns collapsible channel categories,
    Events entry, channel create forms, and channel row actions.
  - `frontend/src/App.vue` owns channel header controls and member-list visibility.
- Stage 7.6 completed composer and message actions:
  - `frontend/src/components/ChatView.vue` owns reply target state, message options
    menu state, composer action buttons, and the expanded composer layout.
  - Existing backend send/edit/delete routes remain unchanged and covered by backend
    API tests.
- Stage 7.7 completed voice channel UX:
  - `frontend/src/stores/guilds.ts` now prefers the selected active voice channel
    when deriving the current voice target.
  - `frontend/src/components/ChannelSidebar.vue` owns voice-channel join/leave
    affordances and displays active voice membership under voice channel rows.
  - `frontend/src/components/VoicePanel.vue` owns the bottom user identity, local
    status cycle, mute/deafen controls, settings entry, and existing WebRTC
    screen-share/quality controls.
  - `frontend/src/App.vue` orchestrates voice join/leave by channel id and mirrors
    mute/deafen state into gateway voice-state updates.
- Stage 7.8 completed the user settings shell:
  - `frontend/src/components/SettingsView.vue` owns the settings navigation and safe
    demo panels for My Account, Profiles, Privacy & Safety, Voice & Video,
    Appearance, Keybinds, and Log Out.
  - `frontend/src/stores/navigation.ts` records the pre-settings destination and
    restores it when settings closes.
  - `frontend/src/App.vue` opens settings from the bottom user panel, hides the app
    sidebars while settings is active, and reuses the existing logout reset path.
- Stage 7.9 completed server add and discovery flows:
  - `frontend/src/components/ServerAddDialog.vue` owns the unified create/join server
    modal used by the rail add path, empty workspace actions, and topbar join action.
  - `frontend/src/components/ServerDiscoveryDialog.vue` owns local demo public server
    cards plus search and can start server creation from a discovery card.
  - `frontend/src/App.vue` still routes actual mutations through existing
    `guilds.createGuild()` and `guilds.joinInvite()` API wrappers.
- Stage 7.10 completed DM persistence and realtime expansion:
  - `backend/app/db/schema.sql` and `backend/app/db/seed.py` define and seed
    PostgreSQL-backed DM profiles, relationships, DM channels, DM members, and DM
    messages.
  - `backend/app/repositories/dms.py` and `backend/app/services/dm_service.py` now
    provide the PostgreSQL/demo fallback switch for relationship and DM APIs.
  - `backend/app/gateway/manager.py`, `backend/app/gateway/router.py`,
    `backend/app/realtime/publisher.py`, and `backend/app/realtime/subscriber.py`
    support DM subscriptions plus `DM_CREATE`/`DM_MESSAGE_CREATE` dispatch.
  - `frontend/src/stores/dms.ts` applies DM gateway events and `frontend/src/App.vue`
    forwards gateway dispatches to both guild and DM stores.
- Stage 7.11 completed responsive and accessibility QA:
  - `frontend/src/styles/base.css` now hides private/channel sidebars below 900px,
    constrains mobile app/workspace width, hides the gateway status pill below 620px,
    and reduces friend-row actions to avoid right-edge clipping.
  - Desktop and mobile screenshots are stored under `docs/qa-artifacts/`.
  - QA notes and residual manual browser checks are in
    `docs/stage-7-11-responsive-qa.md`.
- Stage 7.12 completed final Discord app QA and documentation:
  - Full command verification passed: backend tests, backend lint, frontend lint, and
    frontend production build.
  - Docker Compose PostgreSQL smoke passed with backend/frontend services reachable
    through `localhost`.
  - Headless Chrome smoke passed for demo login, Friends tabs, DM messaging, server
    text/voice channel switching, settings, create/join server, and logout reset.
  - Final QA notes and residual external verification items are in
    `docs/stage-7-12-final-qa.md`.
- Stage 8 started from the user's Discord reference screenshots:
  - The controlling plan is `docs/discord-ui-remediation-plan.md`.
  - Priorities are layout/text-overlap cleanup, app-shell sizing, Korean/English
    language support, current-location and voice-state clarity, and removal or
    conversion of misleading placeholder buttons.
  - Do not copy private Discord screenshot content into code, fixtures, or docs.
- Stage 8.1 completed layout tokens and app shell sizing:
  - `frontend/src/styles/base.css` defines stable tokens for app surfaces, server
    rail, sidebars, header, member list, composer, bottom voice panel, and icon
    controls.
  - The app shell is viewport-bound with hidden global overflow; sidebars and content
    regions own their own scrolling.
  - Friends home mobile sizing was corrected so tabs/search remain within the
    workspace viewport.
  - QA screenshots are `docs/qa-artifacts/stage-8-1-desktop.png` and
    `docs/qa-artifacts/stage-8-1-mobile.png`.
- Stage 8.2 completed sidebar text overlap and channel creation cleanup:
  - `frontend/src/components/ChannelSidebar.vue` now uses stable stacked create
    panels for text and voice channel creation.
  - `frontend/src/styles/base.css` keeps channel category headings, create forms,
    channel rows, row actions, and voice member rows inside the fixed sidebar width.
  - QA created text and voice channels through the UI and captured
    `docs/qa-artifacts/stage-8-2-sidebar.png`.
- Stage 8.3 completed the Korean/English i18n foundation:
  - `frontend/src/i18n/index.ts` owns flat Korean/English dictionaries and the
    `useI18n()` helper.
  - `frontend/src/stores/preferences.ts` persists `ko`/`en` language selection in
    localStorage.
  - Auth, app shell/header, private sidebar, channel sidebar, Friends home, chat
    composer/actions, DM view, VoicePanel, gateway status label, and Settings use
    i18n for high-visibility copy.
  - Settings has a Language panel with Korean and English choices.
  - QA screenshots are `docs/qa-artifacts/stage-8-3-ko-home.png`,
    `docs/qa-artifacts/stage-8-3-en-home.png`, and
    `docs/qa-artifacts/stage-8-3-en-settings.png`.
- Stage 8.4 completed the bottom user and voice panel redesign:
  - `frontend/src/components/VoicePanel.vue` separates user identity/actions, voice
    connection summary, presence/meter/status, and screen/call controls.
  - `frontend/src/styles/base.css` now styles connected/disconnected summaries,
    speaking state, active screen share, and connected disconnect controls with fixed
    bottom-panel sizing.
  - Browser QA used fake media capture to verify connect, mute, deafen, settings
    entry, disconnect, desktop layout, and mobile layout.
  - QA screenshots are `docs/qa-artifacts/stage-8-4-voice-disconnected.png`,
    `docs/qa-artifacts/stage-8-4-voice-connected.png`, and
    `docs/qa-artifacts/stage-8-4-mobile.png`.
- Stage 8.5 completed current location and state visibility:
  - `frontend/src/App.vue` renders a destination subtitle and connected voice
    location/status pill in the topbar.
  - `frontend/src/components/ServerRail.vue`,
    `frontend/src/components/PrivateChannelSidebar.vue`, and
    `frontend/src/components/ChannelSidebar.vue` expose active selections through
    `aria-current` plus stronger selected styles.
  - `frontend/src/components/ChannelSidebar.vue` shows the connected voice channel,
    self voice row, and muted/deafened/speaking labels.
  - `frontend/src/components/VoicePanel.vue` prioritizes muted/deafened labels in the
    bottom voice status area.
  - Browser QA verified Friends, DM, server text channel, fake-media voice join, and
    mute state visibility with no horizontal overflow.
  - QA screenshot is `docs/qa-artifacts/stage-8-5-voice-state.png`.
- Stage 8.6 completed placeholder button audit and cleanup:
  - `frontend/src/App.vue` owns the shared demo-disabled notice pattern.
  - `frontend/src/components/PrivateChannelSidebar.vue` wires DM search, Nitro, Shop,
    and Quests to scoped demo notices.
  - `frontend/src/components/ChannelSidebar.vue` wires server menu and Events to
    scoped demo notices while preserving real channel and invite flows.
  - `frontend/src/components/FriendsHome.vue` turns the friend More button into a
    local profile-summary menu with a message action.
  - `frontend/src/components/ChatView.vue` turns upload, gift, apps, and emoji
    composer buttons into local demo panels until Stage 8.8 expands composer actions.
  - `frontend/src/styles/base.css` keeps workspace notices compact so they do not
    consume the main content area.
  - QA screenshot is `docs/qa-artifacts/stage-8-6-button-panels.png`.
- Stage 8.7 completed channel-header panels:
  - `frontend/src/App.vue` owns local panel state for threads, notifications, pinned
    messages, and current-channel search.
  - Notification settings support all messages, mentions only, and mute notifications
    as local session state.
  - Current-channel search filters the active in-memory messages by content or author.
  - Threads and pinned messages now show useful empty states instead of generic
    placeholder notices.
  - `frontend/src/styles/base.css` positions header panels below the topbar without
    consuming workspace layout rows.
  - QA screenshot is `docs/qa-artifacts/stage-8-7-header-panels.png`.
- Stage 8.8 completed composer action panels:
  - `frontend/src/components/ChatView.vue` now inserts local emoji into drafts,
    exposes a bounded upload metadata panel, provides poll/todo apps action
    templates, and keeps gift as an explicit demo limitation.
  - `frontend/src/components/DirectMessageView.vue` adds DM composer emoji insertion
    while preserving button-based DM send.
  - `frontend/src/styles/base.css` keeps composer panels within the input area and
    fixes the DM composer grid for input, expression action, and send controls.
  - QA screenshots are `docs/qa-artifacts/stage-8-8-composer-panels.png` and
    `docs/qa-artifacts/stage-8-8-dm-composer.png`.
- Stage 8.9 completed Friends and DM information density:
  - `frontend/src/components/FriendsHome.vue` shows friend status, relationship,
    handle, activity, selected-row state, and a wide-screen profile/activity panel.
  - `frontend/src/components/PrivateChannelSidebar.vue` shows DM presence dots,
    status/activity detail, group member counts, unread badges, and stronger selected
    state.
  - `frontend/src/components/DirectMessageView.vue` shows DM status, message count,
    participants, and participant chips in the conversation intro.
  - `frontend/src/styles/base.css` bounds Friends/DM detail layouts and hides the
    Friends profile panel at narrower breakpoints.
  - QA screenshots are `docs/qa-artifacts/stage-8-9-friends-home.png` and
    `docs/qa-artifacts/stage-8-9-friends-dm.png`.
- Stage 8.10 completed Settings reorganization:
  - `frontend/src/components/SettingsView.vue` groups Settings into Account,
    Experience, and Session sections with account/privacy, voice/video, appearance,
    accessibility, keybinds, language/time, and logout panels.
  - Voice connection state, input level, ICE readiness, language choice, and
    time-format choice are represented as real local settings panels.
  - Demo-only scope is explicit for local-only controls.
  - `frontend/src/styles/base.css` tightens settings sidebar selection, card copy,
    radio rows, toggles, and keybind rows so labels do not clip.
  - QA screenshot is `docs/qa-artifacts/stage-8-10-settings.png`.
- Stage 8.11 completed voice and screen-share workspace clarity:
  - `frontend/src/App.vue` opens a dedicated voice workspace when a voice channel is
    selected, before the user joins the call.
  - The workspace exposes selected guild/channel context, preview versus connected
    state, local and remote participant tiles, join/leave actions, and screen-share
    availability.
  - `frontend/src/components/ChannelSidebar.vue` marks selected voice channels
    separately from connected voice channels.
  - `frontend/src/components/VoicePanel.vue` uses selected-channel copy in its idle
    state so users understand the next action.
  - `frontend/src/styles/base.css` bounds the voice workspace, action buttons,
    participant tiles, and mobile layout to avoid overlap and horizontal overflow.
  - Browser QA covered in-app permission failure plus fake-media select, join,
    mute, deafen, screen-share-enabled state, leave, and no-horizontal-overflow
    checks.
  - QA screenshots are `docs/qa-artifacts/stage-8-11-voice-workspace.png` and
    `docs/qa-artifacts/stage-8-11-voice-workspace-fake-media.png`.
- Stage 8.12 completed low-frequency feature scope cleanup:
  - Scope decisions are documented in `docs/stage-8-12-feature-scope.md`.
  - `frontend/src/components/PrivateChannelSidebar.vue` replaces separate Nitro,
    Shop, and Quests rows with a single clone-scope entry.
  - `frontend/src/components/ChatView.vue` removes the gift checkout button and
    reframes external-app-style composer actions as local templates.
  - `frontend/src/components/SettingsView.vue` adds a clone-scope decisions card for
    commerce, external apps/activities, GIF search, real file transfer, and
    production notifications.
  - `frontend/src/i18n/index.ts` contains Korean/English labels for the new scope
    and local-template copy.
  - QA screenshot is `docs/qa-artifacts/stage-8-12-feature-scope.png`.
- Stage 8.13 completed responsive and accessibility QA:
  - QA notes are in `docs/stage-8-responsive-accessibility-qa.md`.
  - Desktop and mobile screenshots are
    `docs/qa-artifacts/stage-8-13-desktop.png` and
    `docs/qa-artifacts/stage-8-13-mobile.png`.
  - CDP viewport checks found no horizontal overflow at 1366 x 900 or 390 x 844.
  - `frontend/src/components/ServerRail.vue` now prevents duplicate
    `aria-current="page"` when the Direct Messages/Friends home is active.
  - Residual manual QA gap: rerun full human keyboard/screen-reader passes if modal
    or settings focus behavior changes.
- Stage 8.14 completed final Stage 8 verification:
  - Final QA notes are in `docs/stage-8-final-qa.md`.
  - Backend tests, backend lint, frontend lint, and frontend production build passed.
  - Docker Compose services were running; container-internal backend health confirmed
    PostgreSQL configured and connected.
  - Host `127.0.0.1:8000` may show native fallback health if another local backend is
    bound to loopback; use container-internal health for Docker database verification
    unless local port ownership is cleared.
  - Stage 8 browser QA artifact paths are indexed in the final QA document.

Store planning observation:

- `https://discord.com/store` was inspected through the Codex in-app browser on
  2026-06-03. The route redirected to Discord login because the in-app browser did
  not share the user's existing Discord login session.
- Store feature scope was therefore derived from route behavior plus Discord's public
  Shop/Profile support documentation. The implementation plan avoids real Discord
  assets, item names, prices, and payment processing.
- Stage 6.1 completed the cross-stack Store data contract:
  - Backend contracts are in `backend/app/schemas/store.py`.
  - Frontend contracts are in `frontend/src/types.ts`.
  - Validation coverage is in `backend/tests/test_store_schema.py`.
- Stage 6.2 completed the safe original demo catalog:
  - Catalog data and helper functions are in `backend/app/demo/store_catalog.py`.
  - Catalog integrity coverage is in `backend/tests/test_store_catalog.py`.
- Stage 6.3 completed authenticated Store read APIs:
  - Route handlers are in `backend/app/api/routes/store.py`.
  - Response assembly is in `backend/app/services/store_service.py`.
  - API coverage is in `backend/tests/test_store_api.py`.
- Stage 6.4 completed frontend Store state:
  - Store state is in `frontend/src/stores/store.ts`.
  - Store read wrappers are in `frontend/src/services/api.ts`.
  - Logout reset integration is in `frontend/src/App.vue`.
- Store UI work is deferred. Resume only after Stage 7 core Discord app parity or if
  the user explicitly asks to resume Store.

Completed Stage 2 bridge work:

- Added bearer-token protected message creation API.
- Added bearer-token protected channel creation API.
- Connected frontend message composer to the backend.
- Connected frontend text-channel creation form to the backend.
- Added Docker PostgreSQL service with persistent `postgres_data` volume.
- Added startup schema migration and idempotent seed data loading.
- Added a guild service/repository layer that uses PostgreSQL when connected and
  falls back to `demo_store` otherwise.
- Made `/api/guilds/me` bearer-token protected and connected the frontend guild load
  to the dev session token.
- Added guild membership and permission checks to channel/message mutation routes.
- Added database-backed `/api/auth/register`, `/api/auth/login`, and `/api/auth/me`.
- Added frontend login/register UI, saved-session restore, logout, and explicit Demo
  user entry.
- Added authenticated guild creation with default text/voice channels and frontend
  create-server UI.
- Added invite code creation/join APIs and frontend invite dialogs.
- Added Pinia loading/mutation/error state handling for guild operations.
- Added `schema_migrations` tracking around startup schema application.
- Added role creation plus member-role assignment/removal across backend, demo store,
  Pinia state, and the member list UI.
- Added single-guild refresh and administrator-only non-owner member removal across
  backend, demo store, Pinia state, and the member list UI.
- Added `MESSAGE_CREATE` realtime fan-out through Redis Pub/Sub when configured and a
  local gateway-manager fallback for native development.
- Added gateway channel subscriptions during Identify and frontend dispatch handling
  with message deduplication.
- Added a gateway zombie-connection reaper background task and tests for heartbeat
  timeout cleanup plus channel broadcast behavior.
- Added `CHANNEL_CREATE` and `GUILD_UPDATE` realtime dispatch for channel creation,
  invite joins, role mutations, and member removal, including server-side subscription
  synchronization and frontend state application.
- Added message update/delete REST APIs, demo-store and PostgreSQL repository support,
  `MESSAGE_UPDATE`/`MESSAGE_DELETE` realtime dispatch, Pinia state handling, and chat
  row edit/delete controls.
- Added focused PostgreSQL repository tests for message update/delete permission and
  write behavior using an isolated fake async database.
- Added focused PostgreSQL repository tests for guild creation/reads, channel
  creation permission, invite creation/join, role creation/assignment/removal, and
  member removal using an isolated fake async database.
- Added Stage 4 voice signaling scaffolding: gateway opcode 5, voice state broadcast,
  targeted offer/answer/ICE relay, frontend gateway send helpers, voice presence
  state, and VoicePanel signaling status.
- Added browser WebRTC voice implementation: ICE config API, microphone capture,
  peer-connection lifecycle, offer/answer/ICE handling, remote audio sinks, cleanup,
  and local VAD scaffold.
- Added call quality and screen-share expansion: microphone mute, input-level meter,
  screen capture, peer renegotiation for screen video tracks, remote screen preview,
  and connection-state display on screen-share tiles.
- Added WebRTC quality diagnostics and TURN readiness reporting: `/api/meta/voice`
  now exposes ICE server count and TURN status, the frontend samples browser stats,
  and the voice panel shows peer count, RTT, jitter, packet loss, and outbound
  bitrate while connected.
- Added `docs/voice-qa.md` plus deployment checklist updates for local two-browser
  smoke testing, TURN/NAT testing, and HTTPS deployment verification.
- Added deployment notes and switched backend runtime Docker image to Gunicorn with
  Uvicorn workers.
- Added `DEVELOPMENT_PROMPT.md` as the project-specific development prompt and linked
  it from `AGENTS.md` plus the required reading order.
- Added `docs/README.md` as the document index and aligned prompt, agent, project
  context, and roadmap reading-order rules.
- Added `docs/GITHUB_COLLABORATION_WORKFLOW.md` for branch, commit, push, staging,
  and verification workflow.
- Added `docs/PROMPT_COMPLIANCE.md` to map prompt policies to concrete files and
  record remaining external-only gaps.
- Added `docs/store-clone-implementation-plan.md` as the detailed Stage 6 plan for a
  Discord Store-like in-app shop.
- Added Stage 6.1 Store contracts across backend Pydantic schemas, frontend
  TypeScript types, and backend validation tests.
- Added Stage 6.2 Store seed catalog with original demo collections, cosmetics,
  bundle metadata, Orb exclusives, limited drops, and catalog integrity tests.
- Added Stage 6.3 authenticated Store read APIs for catalog and item detail payloads.
- Added Stage 6.4 frontend Store Pinia state, read API wrappers, filtering/sorting
  state, and logout reset integration.
- Added `docs/discord-app-clone-implementation-plan.md` as the current primary plan
  for cloning the Discord web app rooted at `channels/@me`.
- Added Stage 7.3 Direct Messages: authenticated relationship and DM APIs, demo-store
  DM membership checks, sanitized DM message creation, frontend DM state, friend-row
  DM creation/opening, and a functional DM chat composer.
- Added Stage 7.4 Server Rail Parity: `@me` unread badge, server unread/mention
  indicators, muted server state, demo folder grouping, add-server/discovery rail
  buttons, and browser-verified rail interactions.
- Added Stage 7.5 Server Sidebar And Header Controls: server menu and Events entries,
  collapsible text/voice categories, text/voice channel create forms, channel row
  invite/settings actions, channel header controls, member-list toggle, and
  browser-verified sidebar/header interactions.
- Added Stage 7.6 Composer And Message Actions: composer upload/gift/apps/emoji
  buttons, local reply target banner, message row reply/options menu, preserved
  edit/delete controls, and browser/backend verification for the message surface.
- Added Stage 10.0 baseline documentation for the latest FHD Discord comparison,
  Stage 10.1 visual-noise cleanup for demo/test names and stale seeded DM users, and
  Stage 10.2 global dark-shell token reset across surfaces, selected/hover states,
  focus rings, scrollbars, composer, member, and voice-panel surfaces. Stage 10.2
  browser QA confirmed token application, no horizontal body overflow at 1280 px,
  and old development-style DM names hidden from the primary shell.
- Added Stage 10.3 shell layout recomposition: the main workspace now spans the full
  content height, the voice controls are constrained to the active sidebar column,
  and browser QA verified Friends, text channel, and voice channel layouts have no
  horizontal body overflow or bottom-control overlap with the main workspace.
- Added Stage 10.4 server rail polish: active/unread markers now use a consistent
  left pill, server button hover/active states are quieter, mention badge labels are
  clamped, and add/discovery buttons read as secondary controls. Browser QA verified
  the active marker, rail width, and secondary action styling.
- Added Stage 10.5 private sidebar simplification: DM rows are compact single-line
  entries, repeated inactive fallback text is hidden, unread badges are clamped, and
  browser QA verified the sidebar stays at 300 px with no row wrapping or scope/test
  text in primary navigation.
- Added Stage 10.6 Friends home rework: friend rows now hide secondary actions until
  hover/focus/active, noisy fallback activity copy is removed, and the right panel is
  a compact activity card instead of a profile table. Browser QA verified row
  density, action visibility, no horizontal overflow, and Add Friend tab integrity.
- Added Stage 10.7 Add Friend workflow polish: the add-friend tab is now a
  single-column one-step form without discovery/activity preview clutter, with
  verified input/button spacing, disabled state, success result, and no horizontal
  overflow.
- Added Stage 10.8 server sidebar polish: channel rows are compact, category create
  buttons and channel management actions are hidden until hover/focus, and browser
  QA verified no horizontal overflow plus active/text/voice channel scan quality.
- Added Stage 10.9 header action reduction: the server header now keeps only
  notifications, pins, member list, search, and invite creation while removing
  threads, inbox, help, join-server, and logout from the primary header. Browser QA
  verified no wrapping or horizontal overflow.
- Added Stage 10.10 text timeline rebuild: server and DM message metadata now use
  locale-aware demo time labels instead of raw IDs, date dividers are formatted,
  message hover actions are compact floating toolbars, reaction buttons are compact
  structured pills, and attachment cards have stable icon/content columns. Browser
  QA verified text/DM message lists for horizontal overflow and metadata cleanup.
- Added Stage 10.11 composer rebuild: `ChatView.vue`,
  `DirectMessageView.vue`, and `frontend/src/styles/base.css` now share compact
  composer sizing, a 36 px send button, 44 px vertically centered input text, and a
  hidden-by-default template action that appears only on composer hover/focus or
  active state. Browser QA verified no horizontal overflow, no voice-panel overlap,
  and the Stage 10.11 specificity fix that reduced the optional action's default
  width to `0px`.
- Added Stage 10.12 member list simplification: `MemberList.vue`,
  `frontend/src/i18n/index.ts`, and `frontend/src/styles/base.css` now render a
  quieter localized member panel by default, hide refresh/role/member management
  inside an explicit management mode, and keep the admin toggle visible at low
  contrast. Browser QA verified the default member panel has no role controls and
  the management toggle opens role creation, refresh, and per-member controls.
- Added Stage 10.13 bottom user panel rebuild: `VoicePanel.vue` and
  `frontend/src/styles/base.css` now use a 102 px lower-left panel with a full-width
  user identity row, 28 px voice/user action buttons, a compact selected/connected
  voice card, explicit aria labels for voice actions, and hidden visible
  diagnostics. Browser QA verified no overflow, no workspace overlap, and the
  corrective split between composer send-button sizing and voice-panel button
  sizing.
- Added Stage 10.14 voice workspace rebuild: `frontend/src/App.vue` tags remote
  voice participant tiles, and `frontend/src/styles/base.css` now uses a tighter
  voice workspace header, 34 px join/screen-share buttons, lower participant tiles,
  a dashed quiet empty state, compact speaking rings, and a full-width compact
  screen-share preview row. Browser QA verified the idle voice channel workspace
  layout without triggering microphone permission.
- Added Stage 10.15 screen-share flow rework: `frontend/src/App.vue` now guards
  screen-share toggling behind an active voice connection, limits remote
  screen-share preview cards to the `voice_channel` workspace, and labels voice
  action buttons; `VoiceVideoSink.vue` no longer displays raw connection state;
  `frontend/src/styles/base.css` shrinks the remote preview PiP. Browser QA verified
  disconnected screen-share controls are disabled and no remote preview layer covers
  text-channel composer or member-list surfaces.
- Added Stage 10.16 feature visibility policy cleanup: `frontend/src/App.vue`
  removes the primary header gateway-status block, `VoicePanel.vue` removes the
  hidden lower-left voice diagnostics DOM, and `frontend/src/styles/base.css`
  removes the now-dead session/voice diagnostic selectors. Settings remains the
  place for clone scope and ICE/STUN/TURN detail. Browser QA verified no horizontal
  overflow, no visible gateway/STUN/TURN/RTT/Jitter/Nitro/Shop/Quests/smoke/debug
  terms in the primary shell, only the Friends private-nav row, and no
  `.session-state` or `.voice-presence` nodes in the app shell.
- Added Stage 10.17 responsive/accessibility QA documentation:
  `docs/stage-10-17-responsive-qa.md` records FHD, side-by-side, tablet, and mobile
  viewport measurements plus screenshot artifacts under `docs/qa-artifacts/`.
  Browser QA verified no horizontal body overflow across those widths, text-channel
  sidebar/header/chat/composer/member dimensions at 1280 px, no visible icon-only
  controls missing labels, visible focus styling, and the in-app browser limitation
  for repeated `Tab` key traversal.
- Added Stage 10.18 final QA documentation: `docs/stage-10-final-qa.md` records
  frontend build/lint, backend tests/lint, Docker service smoke, `/api/health`,
  frontend HTTP smoke, and browser QA for Friends, Add Friend, text channel, voice
  preview, and screen-share disabled state. Browser media permission returned
  `Permission denied` on voice join, so connected voice and real screen-share
  start/stop remain manual checks with microphone/screen-capture permissions.
- Added Stage 10.19 user feedback interaction polish: `FriendsHome.vue` now uses the
  All/Online/Pending/Add Friend tab order, stronger friend-row separation, and
  fixed-position more/right-click menus with outside-click and Escape dismissal;
  `PrivateChannelSidebar.vue` replaces the demo-disabled search action with a quick
  conversation switcher; `ChannelSidebar.vue` adds a server context menu and makes
  voice-channel row click attempt direct voice join; `VoicePanel.vue` hides the
  disconnected voice-room card; `App.vue` removes the disconnected voice join button
  from the voice workspace, adds closable notices, and replaces the invite-code-only
  dialog with a searchable friend invite modal. CSS updates in
  `frontend/src/styles/base.css` cover rail contrast, selected server-add state,
  menu/popover/modal layering, friend row spacing, and tighter voice workspace
  layout. Verification passed frontend build/lint plus Docker frontend rebuild and
  browser QA for menu dismissal, tab order, hidden disconnected voice card, and voice
  row direct-join attempt; microphone permission denial remains the manual connected
  media QA blocker.
- Added Stage 10.20 Discord feedback cleanup: `FriendsHome.vue` now keeps friend
  status/activity on one compact status line with taller row spacing; `ChatView.vue`
  and `DirectMessageView.vue` removed the hardcoded `OK`/`+1` reaction pills and now
  share clearer message-row borders, padding, and hover separation; `VoicePanel.vue`
  rebuilds the lower-left user/voice surface as raised cards, moves voice actions
  out of absolute overlap, and renders connected participant chips when media
  permission allows voice connection. `App.vue`, `ChannelSidebar.vue`,
  `PrivateChannelSidebar.vue`, `ServerRail.vue`, `types.ts`, `i18n/index.ts`, and
  `base.css` add target-aware app context menus, outside-click/Escape dismissal for
  transient menus/notices, cleaner one-line topbar behavior, and server-rail voice
  connection badges instead of topbar voice-location chips. Verification passed
  frontend lint/build, backend tests/lint, Docker frontend rebuild, browser QA for
  friend row density, server/DM message separation, removal of hardcoded reaction
  pills, app-level right-click menu suppression of the browser menu, outside-click
  dismissal, and Docker service refresh. In-app browser microphone permission still returned
  `Permission denied`, so connected voice participant rendering and live speaking
  rings remain manual QA in a browser session with microphone permission granted.
- Added Stage 10.21 voice-sidebar participant stack: `ChannelSidebar.vue` now keeps
  connected voice channels as a compact channel row and renders the Discord-like
  lower stack beneath it: channel status shortcut, dashed mood prompt, connected
  participant rows, and invite-to-voice action. `frontend/src/styles/base.css`
  scopes connected/speaking emphasis to the row/member surfaces instead of coloring
  the full expanded block, and `frontend/src/i18n/index.ts` localizes the new Korean
  and English labels. Frontend lint/build passed; successful connected-state visual
  QA still requires microphone permission in the browser.
- Added Stage 10.22 bottom user status card density: `frontend/src/App.vue` now tags
  the shell with `voice-connected`, and `frontend/src/styles/base.css` uses a compact
  64 px lower row for the default self status card while reserving the 128 px lower
  panel only for active voice connections. The user card now has tighter Discord-like
  elevation, spacing, and separated mic/deafen/settings controls. Frontend lint/build
  passed.
- Added Stage 10.23 voice session ownership and bottom panel alignment:
  `frontend/src/stores/guilds.ts` now tracks `connectedVoiceGuildId` and
  `connectedVoiceChannelId` separately from the selected guild/channel, while
  `frontend/src/App.vue` uses those values for server rail voice badges, channel
  sidebar connected state, mute/deafen updates, participant sync, and cross-server
  voice switching confirmation. `VoicePanel.vue` now keeps the connected voice card
  above the self status card and removes lower-left participant chips to avoid the
  clipped self/"나" artifact; participant rows remain in `ChannelSidebar.vue`.
  `base.css` aligns the self card to the composer-height pattern, narrows panel
  padding, and keeps the surrounding lower panel background matched to the sidebar.
  Frontend lint/build passed.

- Added Stage 10.24 in-app voice switch dialog and bottom edge alignment:
  `frontend/src/App.vue` replaces the cross-server voice `window.confirm` with a
  Discord-like modal that supports outside-click, Escape, close, cancel, confirm,
  and "do not ask again" behavior. `frontend/src/i18n/index.ts` adds Korean/English
  labels for the dialog, and `frontend/src/styles/base.css` styles the modal while
  aligning the lower-left self status card to the message composer top/bottom frame
  with narrower sidebar padding. Frontend lint/build, Docker frontend rebuild, and
  browser layout QA passed; the in-app browser still denied microphone permission,
  so the successful connected voice switch remains manual media-permission QA.
- Added Stage 10.25 browser-native UI audit and status-card spacing:
  `frontend/src/App.vue` now routes clipboard copy success/failure through localized
  app notices instead of silent browser-API outcomes, `frontend/src/i18n/index.ts`
  adds Korean/English copy feedback, and `frontend/src/styles/base.css` gives the
  lower-left status panel more top breathing room while preserving composer-frame
  alignment. A project search found no clone UI `alert`, `confirm`, or `prompt`
  usage outside sanitizer test payload strings. Frontend lint/build, Docker frontend
  rebuild, and browser layout QA passed.
- Added Stage 10.26 message timeline divider cleanup:
  `frontend/src/components/DirectMessageView.vue` now renders a date divider before
  DM messages, and `frontend/src/styles/base.css` removes stacked borders by
  clearing the first message row's top border and applying the thin separator only
  between adjacent message rows. The DM intro no longer draws a bottom border that
  can collide with the timeline divider. Frontend lint/build, Docker frontend
  rebuild, and browser layout QA passed for server text and DM timelines.
- Added Stage 10.27 server rail state and header seam cleanup:
  `frontend/src/components/ServerRail.vue` now scopes active server state to server
  destinations so Friends/DM views only mark Direct Messages as active, while
  inactive unread and mention states keep smaller markers. `frontend/src/styles/base.css`
  keeps voice-connected servers visually distinct from active servers and aligns
  private/server sidebar top separators with the workspace header edge. Frontend
  lint/build, Docker frontend rebuild, and browser layout QA passed for Friends and
  server surfaces.
- Added Stage 11.7 voice workspace polish: `frontend/src/styles/base.css` tightens
  the voice workspace surface, header divider, participant grid, tile elevation,
  connected-state borders, speaking card/avatar rings, and screen-share preview
  composition. Frontend lint/build, Docker frontend rebuild, and browser static QA
  passed for CSS presence and zero horizontal overflow; live microphone and
  screen-capture transitions remain manual media QA in Stage 11.12.
- Added Stage 11.8 app-owned menu/modal polish: `frontend/src/App.vue` now routes
  deferred global context-menu actions through localized app notices, centralizes
  notice close/auto-dismiss behavior, and prevents nested browser context menus
  inside the app menu. A source audit found no clone UI `alert`, `confirm`, or
  `prompt` calls outside sanitizer test payloads; frontend lint/build, Docker
  frontend rebuild, and browser static QA passed.
- Added Stage 11.9 feature exposure cleanup: `frontend/src/i18n/index.ts`,
  `frontend/src/components/ServerAddDialog.vue`,
  `frontend/src/components/ServerDiscoveryDialog.vue`, and
  `frontend/src/components/SettingsView.vue` now remove user-visible demo wording
  from primary flows while keeping common DM/server/message/voice/settings actions
  visible. `frontend/package-lock.json` updates Vite to 8.0.16 via `npm audit fix`;
  frontend audit, lint/build, Docker rebuild, and browser primary-surface text QA
  passed.
- Added Stage 11.10 backend/API completion pass: `backend/tests/test_api_routes.py`
  now covers `/api/dev/session` for local development token creation, user payload
  shape, decoded access-token claims, and production-environment hiding. Backend
  tests/lint passed, Docker services were running, and `/api/health` plus
  `/api/meta/voice` smoke checks returned the expected local values.
- Added Stage 11.11 responsive/accessibility QA: browser metrics at 1920 x 936,
  1280 x 720, 900 x 720, and 390 x 844 showed zero horizontal overflow, zero
  clipped core controls, and zero visible unnamed buttons. Frontend lint/build
  passed; visual screenshot comparison remains part of Stage 11.13.
- Added Stage 11.12 real-media QA: backend health, voice metadata, and WebSocket
  gateway HELLO smoke checks passed. Browser DOM checks found visible voice
  controls and no native JS dialogs, but automated permission-state/capture
  execution remains blocked by browser runtime permission access; `docs/voice-qa.md`
  records the required manual microphone/screen-share pass and TURN/NAT scope.
- Added Stage 11.13 final visual pass: `frontend/src/styles/base.css` now keeps
  optional composer actions out of layout until hover/focus/open state, removing a
  hidden zero-width clipped control found during server text QA. Frontend
  lint/build, Docker frontend rebuild, and browser metrics for Friends, DM, server
  text, and settings all passed with zero horizontal overflow and zero clipped core
  controls.
- Added Stage 11.14 final regression: frontend lint/build, backend tests/lint,
  full Docker rebuild, frontend high-severity audit, API/frontend HTTP smoke,
  gateway HELLO smoke, and browser regression all passed. Running services are
  `backend`, `frontend`, and `postgres`; remaining external QA is limited to
  browser-permission microphone/screen-capture checks and TURN/NAT validation in
  `docs/voice-qa.md`.
- Added architecture-principles remediation pass from
  `docs/architecture-principles-audit.md`: backend gateway internals are now split
  into `connection.py`, `subscriptions.py`, `broadcaster.py`, `voice_service.py`,
  and `zombie_reaper.py` behind the existing `GatewayConnectionManager` facade;
  `guild_service.py` now delegates PostgreSQL/demo selection to
  `guild_storage.py`; guild domain repository entry points were added for channel,
  invite, member, message, and role operations. Frontend `App.vue` now delegates
  global notices, context-menu state, invite modal state, and workspace
  title/subtitle derivation to composables. `guilds.ts` now delegates gateway
  payload validation to `guildGatewayHandlers.ts`, message REST calls to
  `channelMessages.ts`, and admin REST calls to `guildAdmin.ts`. `useVoiceRtc.ts`
  now delegates WebRTC quality-stat aggregation to `voiceStats.ts`. Verification
  passed frontend build/lint, backend lint, and full backend tests.
- Added Stage 12 architecture refactor planning:
  `docs/architecture-refactor-stage-12-plan.md` now controls the remaining
  behavior-preserving principle work. `docs/architecture-principles-audit.md`,
  `docs/implementation-plan.md`, and `docs/README.md` link the refreshed
  whole-project audit and Stage 12 order.
- Completed Stage 12.1 App voice session controller:
  `frontend/src/composables/useVoiceSessionController.ts` now owns voice config
  loading, join/leave/switch orchestration, mute/deafen gateway synchronization,
  screen-share toggling, voice participant sync, and incoming voice signal
  handling. `frontend/src/App.vue` delegates those behaviors to the controller
  while keeping the existing template bindings and UI behavior stable. Frontend
  lint and production build passed; live microphone/screen-capture QA remains
  permission-dependent manual coverage.
- Completed Stage 12.2 Voice RTC internal modules:
  `frontend/src/composables/useVoiceRtc.ts` is now a public facade over focused
  voice modules. `voiceMedia.ts` owns browser media capture helpers,
  `voiceVad.ts` owns local input-level/speaking detection,
  `voicePeerConnections.ts` owns peer registry, offer/answer/ICE handling, remote
  stream tracking, participant sync, and renegotiation, and `voiceStats.ts`
  continues to own WebRTC quality aggregation. Frontend lint and production build
  passed; live microphone/screen-capture QA remains permission-dependent manual
  coverage.
- Completed Stage 12.3 Guild voice presence store boundary:
  `frontend/src/stores/voicePresence.ts` now owns connected voice guild/channel
  refs, voice states, latest voice signal, derived active/connected voice-state
  lists, and voice-presence mutation helpers. `frontend/src/stores/guilds.ts`
  keeps the public Pinia API stable while delegating those voice responsibilities.
  Frontend lint and production build passed.
- Completed Stage 12.4 DM storage provider boundary:
  `backend/app/services/dm_storage.py` now mirrors the guild storage provider
  pattern for direct messages. `backend/app/services/dm_service.py` delegates
  relationships, DM list/create, and DM message creation through the provider and
  no longer imports `database`, `demo_store`, or `dm_repository` directly.
  Backend lint and DM-focused tests passed.
- Completed Stage 12.5 Guild repository query movement:
  channel, invite, member, message, and role SQL moved out of
  `backend/app/repositories/guilds.py` into `guild_channels.py`,
  `guild_invites.py`, `guild_members.py`, `guild_messages.py`, and
  `guild_roles.py`. Shared guild read/permission/helper logic moved into
  `guild_common.py`. `guilds.py` now owns guild aggregate list/read/create SQL
  plus compatibility wrapper methods. Backend lint, guild repository tests, and
  the full backend suite passed.
- Completed Stage 12.6 API exception mapping:
  `backend/app/api/errors.py` now owns shared route exception-to-HTTP mapping for
  `KeyError`, `PermissionError`, and `ValueError`; guild, channel, and DM routes
  preserve route-specific messages while delegating status mapping to the helper.
  Backend lint and the full backend suite passed.
- Completed Stage 12.7 Realtime fan-out DRY pass:
  `backend/app/realtime/fanout.py` now owns shared local gateway fan-out and
  subscription synchronization used by both Redis subscriber dispatch and native
  publisher fallback. Focused realtime fan-out tests were added, and backend lint
  plus the full backend suite passed.
- Completed Stage 12.8 Browser API adapter pass:
  `frontend/src/services/browserApi.ts` now wraps high-use browser APIs for storage,
  clipboard, document listeners, viewport/location reads, gateway URL construction,
  navigator platform, and view transitions. Frontend lint and production build
  passed; WebRTC permission APIs intentionally remain in the voice media boundary.
- Completed Stage 12.9 CSS and i18n split plan:
  `docs/frontend-css-i18n-ownership.md` now defines safe future ownership for
  `frontend/src/styles/base.css` and `frontend/src/i18n/index.ts`. No CSS or
  translation code was moved in Stage 12.9 to preserve current visual parity.
- Completed Stage 12.10 final architecture regression:
  frontend lint/build, backend lint/tests, and `git diff --check` passed. Remaining
  deferred candidates are the future `dms.ts` split, future CSS/i18n physical
  extraction, and manual microphone/screen-capture permission QA.
- Completed Stage 13 final architecture maintenance:
  `docs/architecture-refactor-stage-13-plan.md` now records the final maintenance
  pass. DM store responsibilities were split into `dmApi.ts`,
  `dmGatewayHandlers.ts`, and `dmVisibility.ts`; guild visual filtering moved to
  `guildVisibility.ts`; frontend Vitest coverage was added for extracted logic;
  PostgreSQL DM seed/bootstrap support moved to `dm_seed.py`; and guild storage
  protocols were split into smaller role-focused protocol groups while preserving
  the existing provider facade. The remaining CSS/i18n physical split is
  documented as feature-driven, not a maintenance blocker.
- Completed Stage C4 Redis multi-instance fan-out verification path:
  `compose.redis-smoke.yaml` adds optional Redis plus `backend-secondary` on port
  8001, `scripts/realtime_redis_smoke.py` verifies primary REST to secondary
  WebSocket server/DM dispatch, Redis connect/subscriber/publish paths log
  privacy-safe operational events, Redis publish failure falls back to local
  fan-out, and configured Redis subscriber loops reconnect after Redis returns.
  Backend lint and focused realtime tests passed; Docker Redis smoke evidence is
  recorded in
  `docs/remediation-tasks/realtime-communication-plan.md`.
- Completed Stage C5 voice media constraints and permission states:
  `frontend/src/composables/voiceMedia.ts` applies supported native audio
  constraints, normalizes microphone/screen media errors, stores supported
  constraint visibility for settings, and cleans media tracks on leave/unload.
  `VoicePanel.vue`, `SettingsView.vue`, and `voiceMedia.test.ts` cover app-owned
  recovery UI and unit behavior.
- Completed Stage C6 WebRTC peer lifecycle hardening:
  `frontend/src/composables/voicePeerConnections.ts` now scopes peers by
  channel/user, queues ICE until remote description exists, filters stale channel
  signals, retries one bounded failed peer, and tears down remote streams by channel.
  `App.vue`, `VoicePanel.vue`, `VoiceAudioSink.vue`, `VoiceVideoSink.vue`, and
  `voiceStats.ts` only render/aggregate current-channel peer state.
- Completed Stage C7 LAN/TURN readiness:
  `package.json`, `frontend/package.json`, `.env.example`, `README.md`,
  `docs/deployment.md`, and `docs/voice-qa.md` document native LAN commands,
  Docker LAN access, CORS/firewall requirements, secure-context media caveats, and
  separate LAN/TURN release gates.
- Completed Stage C8 two-session realtime QA suite:
  `docs/realtime-communication-qa.md` and `scripts/realtime_browser_smoke.mjs`
  define a repeatable two-browser same-PC smoke for server text, DM, voice peer
  visibility, remote audio sink, mute/deafen, and fake screen-share paths.
  `frontend/package.json` includes official Playwright as a devDependency for that
  smoke; root `package.json` exposes `npm run smoke:realtime:browser`.
  `frontend/src/stores/gatewayIdempotency.test.ts` now covers voice-state and
  guild-update idempotency, and `backend/tests/test_gateway_routes.py` covers
  invalid identify and unsubscribed voice-channel rejection. Verification passed
  frontend lint/test/build, focused backend gateway/realtime tests, the browser
  smoke, and `git diff --check`.
- Completed Stage C9 final communication release gate:
  `docs/remediation-tasks/realtime-communication-plan.md`,
  `docs/realtime-communication-qa.md`, `docs/voice-qa.md`, `docs/deployment.md`,
  `README.md`, and `docs/implementation-plan.md` now record the final local gate.
  Verification passed `npm run lint:frontend`, `npm run test:frontend`,
  `npm --prefix frontend run build`, `npm run lint:backend`,
  `npm run test:backend`, Docker/local health, `/api/meta/voice`, frontend HTTP,
  and `npm run smoke:realtime:browser`. The remaining gates are real microphone
  quality, real screen picker UX, different-PC LAN, and TURN/NAT internet voice
  with real TURN credentials.
- Completed post-C9 communication remediation C10-C13:
  backend gateway voice state now keeps an authoritative in-memory snapshot and
  dispatches `VOICE_STATE_SNAPSHOT` on READY and post-join so late two-account
  sessions see existing voice occupants. Frontend guild voice presence applies
  channel/guild snapshots as replace operations. Voice workspace preview now has
  an explicit Join Voice action. `voiceMedia.ts` persists browser audio-processing
  preferences and `SettingsView.vue` exposes supported echo cancellation, noise
  suppression, and auto-gain toggles without logging raw media/device data.
  Invite controls are permission-aware through `guilds.canCreateInvite`, with
  unauthorized controls hidden and permission errors localized. Automated frontend
  and gateway tests cover snapshots and media constraints; real microphone speech,
  owner/member invite, LAN, and TURN gates remain manual QA items.
- Completed manual QA follow-up stages M1-M10:
  `voiceMedia.ts` now defaults to a speech-stability capture preset and exposes
  local processing controls; screen-share tiles deduplicate remote sharers and
  clear stopped remote video; same-user voice reloads show an app-owned rejoin
  prompt; LAN HTTPS and TURN readiness checks are documented and scriptable;
  friend-request tabs, DM display normalization, per-recipient invite DM delivery,
  Discord-like deafen behavior, and owner/member invite permission browser QA are
  covered by frontend tests and `scripts/realtime_browser_smoke.mjs`. The M9
  recheck fixed deafen playback, and a later follow-up split deafen from microphone
  mute: deafen now mutes remote playback locally, the microphone button remains
  available while deafened, mute/unmute independently controls the local microphone
  track, and screen sharing remains independent. Remaining release gates are real
  sustained-vowel microphone quality, real screen picker layout with multiple
  participants, different-PC HTTPS LAN media, and TURN/NAT internet voice with real
  credentials.
- Added post-M10 voice input/output settings pass:
  `voiceMedia.ts` now persists microphone/speaker device settings and builds a
  Web Audio input-processing stream with high-pass filtering, light compression,
  input volume, and adjustable sensitivity/noise gate before WebRTC peer tracks
  are created. `useVoiceRtc.ts` exposes device settings and refresh/update helpers,
  `SettingsView.vue` adds Voice & Video device/volume/sensitivity controls,
  `VoicePanel.vue` adds Discord-like quick input/output popovers, and
  `VoiceAudioSink.vue` applies output volume plus supported `setSinkId` output
  routing. Frontend lint, production build, and focused `voiceMedia` tests passed.
  Real sustained-vowel/fan-noise listening remains a manual QA gate because
  automated tests cannot judge speech intelligibility.
- Added post-M10 sustained-input stability and privacy pass:
  OBS comparison of `마이크_실제입력.mp4` and `마이크_데스크탑 오디오.mp4`
  showed continuous raw microphone input but repeated desktop-output gaps in the
  clone path. To avoid browser/app processing repeatedly closing on long vowels,
  the speech-stability preset now disables browser echo cancellation, noise
  suppression, and auto gain by default; the local RNNoise worklet and input
  sensitivity gate also default off and existing default settings migrate once to
  that safer baseline. Quick voice popovers show configured sensitivity percent,
  not live input level. Live input amount remains visible only in Voice & Video
  settings, while the main workspace, sidebar, lower user card, and remote
  participant cards show only binary speaking feedback. Frontend voice media tests,
  lint, build, and browser realtime smoke passed; real sustained-vowel listening
  remains a manual gate.
- Added voice-option behavior audit and optional gate correction:
  the stable default remains unchanged with RNNoise and the input sensitivity gate
  off. When a user explicitly enables the input sensitivity gate, the sensitivity
  slider now raises the actual transmit gate threshold and the closed gate strongly
  attenuates input, so high sensitivity can block quiet speech/background sound.
  Input volume and gate settings update during an active call; RNNoise and browser
  echo/noise/auto-gain constraints apply on the next voice join because those are
  part of the capture/AudioWorklet setup. Settings copy now states that the
  sensitivity slider affects audio only when the gate is enabled.
- Added voice settings usability pass:
  the Voice & Video input sensitivity row now shows a clearer Discord-like live
  input-level overlay against the selected threshold so users can see baseline
  room noise before choosing a gate value. The exact input meter remains confined
  to settings. Voice-panel input/output popover setting buttons now open the Voice
  & Video panel directly, and the lower-left popover width is aligned with the
  user status card. Settings copy explains RNNoise, echo cancellation, browser
  noise suppression, and auto gain behavior plus their next-join application
  boundary.
- Added post-M10 overlay dismissal and bottom voice-panel layout polish:
  `VoicePanel.vue` now closes input/output quick settings on outside click or
  Escape, and the connected voice-session card is ordered below the user status
  card so the quick settings popover opens directly above the controls instead of
  above the connected-session card. `ChatView.vue` and `DirectMessageView.vue` now
  apply the same outside-click/Escape dismissal policy to composer and message
  option panels. Frontend lint, tests, production build, and browser smoke for the
  voice quick-settings outside-click behavior passed.
- Added selectable RNNoise support without changing the default communication
  path. `voiceMedia.ts` now treats client-side denoising as an optional pre-WebRTC
  input processor with two modes: Off baseline and RNNoise. Existing
  `rnnoiseSuppression` preferences migrate to RNNoise, while new default and
  migrated stability settings remain Off so current stable microphone behavior is
  preserved. Denoiser mode changes apply on the next voice join to avoid replacing
  tracks or renegotiating active calls. A later manual fan-noise comparison removed
  the SpeexDSP and WorkAdventure DTLN/LiteRT candidates, removed the DTLN package
  and Vite plugin, and left RNNoise as the only optional denoiser exposed by
  `SettingsView.vue` and `VoicePanel.vue`. `docs/voice-qa.md` now defines manual
  Off-versus-RNNoise comparison steps for fan/wind noise, keyboard noise,
  sustained vowels, naturalness, CPU cost, and latency.
- Moved the user settings close control out of the scrollable settings panel and
  into the fixed workspace topbar in `App.vue`, so Settings can be closed from
  the right side of the `User Settings` header regardless of the current scroll
  position.
- Added a Docker HTTPS LAN media path for another PC on the same Wi-Fi.
  `compose.https.yaml` runs the frontend Vite dev server with local certificate
  PFX mounted from ignored `certs/`, `scripts/create_lan_https_cert.ps1` generates
  a host-IP certificate plus `lan-dev-root-ca.cer` trust file, and README/voice/
  deployment docs now route microphone and screen-capture LAN testing through
  `https://<host-ip>:5173` instead of blocked `http://<host-ip>:5173` media.
- Added HTTPS-mode local verification routing: while `npm run docker:up:https` or
  `npm run docker:up:https:detached` is active, Vite serves HTTPS only on port
  `5173`, so local tabs must use `https://localhost:5173` or
  `https://127.0.0.1:5173`. The browser smoke script now supports that mode
  through `npm run smoke:realtime:browser:https`; plain HTTP smoke remains for the
  normal non-HTTPS dev stack.
- A manual two-profile HTTPS local check connected
  `https://localhost:5173` and `https://127.0.0.1:5173` as separate QA accounts in
  `Voice Pair QA 905704 / voice-room`; both tabs showed one remote audio sink,
  one connected peer, and the opposite participant in the voice workspace. A
  repeated Vue warning from an unresolved `<Mic>` icon in `App.vue` was fixed by
  importing the lucide `Mic` component.
- A follow-up two-profile Friends/DM QA pass fixed duplicate private-surface
  rendering and initial presence sync. PostgreSQL demo DM seeding now takes a
  user-scoped advisory lock so parallel relationship/DM workspace loads cannot
  create duplicate demo one-to-one DMs; backend DM listing and frontend DM
  visibility also dedupe by recipient set. Friends now renders the total heading
  once outside pending request subgroups, and the app sends the current presence
  after the initial gateway connection so accepted friends show online without a
  manual status toggle. Manual browser reload on the A/B HTTPS tabs showed one
  Tae/Joon/Mina row each, one `친구 - 1` heading, and the opposite QA friend online
  on both sides.

- External deployment readiness was added after same-PC voice, same-Wi-Fi LAN
  voice, and friend/DM/server-invite flows were manually confirmed as acceptable.
  GitHub Pages/static-only hosting is documented as insufficient for the
  communication target because the clone requires FastAPI, `/gateway` WebSocket
  upgrades, PostgreSQL, Redis fan-out, and TURN. `compose.production.example.yaml`,
  `deploy/Caddyfile.example`, `deploy/coturn/turnserver.conf.example`, and
  `scripts/deployment_readiness_check.mjs` now provide a placeholder-only
  single-server external QA path using Docker Compose, Caddy HTTPS, runtime
  frontend/backend containers, PostgreSQL, Redis, and optional coturn. The root
  script `npm run check:deployment:readiness` verifies HTTPS origin shape,
  `/api/health`, `/api/meta/voice/readiness`, and `/gateway` HELLO over WSS
  without printing tokens, ICE URLs, TURN credentials, message content, or media
  device labels. Verification passed local self-signed HTTPS deployment readiness,
  production Compose rendering with placeholder values, voice readiness, and
  `npm run smoke:realtime:browser:https` with `browserErrors: 0`. This is
  readiness only; final internet communication still requires real TURN credentials
  and two different networks to pass text, DM, voice, mute/unmute, screen-share
  start/stop, and reconnect checks.
- External deployment decision preparation is complete in
  `docs/external-deployment-decision.md`. The selected first external QA path is a
  single VM Docker Compose deployment with Caddy HTTPS, runtime frontend/backend
  containers, PostgreSQL, Redis, and TURN configured through environment variables.
  Managed TURN is recommended for the first public external QA pass, with
  self-hosted coturn kept as an option when VM firewall ports can be verified.
  Local PC port forwarding, PaaS-first deployment, static frontend plus separate
  backend, and GitHub Pages-only deployment are not selected as the first route.
  This pass did not provision a VM, configure DNS, configure real TURN credentials,
  or run an external different-network media test; those items remain
  pending/unverified.
- Voice transport expansion preparation is complete in
  `docs/voice-transport-architecture.md`. The active implementation remains
  P2P WebRTC plus gateway signaling; no LiveKit, mediasoup, or SFU dependency was
  added. `frontend/src/composables/voiceTransport.ts` now defines the shared
  `VoiceTransport` contract and current `p2p-webrtc` transport kind,
  `useVoiceRtc.ts` explicitly returns that contract, and
  `voicePeerConnections.ts` reuses the shared transport connect/signal types while
  keeping P2P offer/answer/ICE behavior unchanged. Future SFU work should add a
  separate transport implementation behind this boundary, plus backend token
  issuing, room mapping, deployment service configuration, and QA gates. Screen
  share quality should be tuned in P2P first for 1:1/small-room problems; SFU
  evaluation becomes appropriate when multi-viewer or simultaneous screen sharing
  causes sender bandwidth/CPU collapse.
- External deployment execution preparation is complete for the selected single-VM
  Docker Compose path. `deploy/production.env.example` is the placeholder-only
  host environment template, real `deploy/*.env` files are ignored by Git, and
  `docs/external-deployment-runbook.md` now owns VM preparation, host-only env
  creation, production Compose startup, readiness checks, manual two-network QA,
  and rollback. `npm run check:deployment:config` renders the production example
  with placeholders before a real VM env exists. This is still not a public
  deployment completion: no VM/VPS, public DNS hostname, real TURN credential,
  public HTTPS/WSS host, or different-network TURN/NAT media QA is available in
  the current workspace.
- Assignment submission packaging is now separated from future public deployment.
  The default grading path is local Docker Compose execution (`npm run docker:up`)
  with the app at `http://127.0.0.1:5173`, documented in
  `docs/assignment-submission-guide.md` and summarized in `README.md`. Same-Wi-Fi
  two-PC media testing stays on the existing Docker HTTPS LAN certificate path.
  Cloudflare Tunnel is documented only as optional temporary external access to
  the locally running app; it is not a formal deployment and does not replace
  TURN/NAT media QA. The preferred Cloudflare path now starts
  `frontend-tunnel` from `compose.cloudflare-tunnel.yaml` and tunnels
  `http://localhost:5174`, so public demos use a built Nginx frontend without
  Vite HMR WebSocket noise. The VM/VPS + Caddy + production Compose documents
  remain future always-on extension references.
- Local submission readiness verification is now scriptable with
  `npm run check:submission:local`. The script auto-detects the normal HTTP Docker
  origin or local HTTPS Docker origins, verifies frontend HTML, same-origin
  `/api/health`, PostgreSQL-backed health metadata,
  `/api/meta/voice/readiness`, and `/gateway` HELLO, and fails if Docker
  PostgreSQL is not configured. The 2026-06-20 packaging pass verified the current
  local HTTPS Docker stack with this script, `npm run check:deployment:config`,
  local HTTPS deployment readiness, and `npm run smoke:realtime:browser:https`.
  TURN remained unconfigured, so external different-network voice/screen sharing
  remains manual and incomplete.
- Cloudflare Quick Tunnel was executed on 2026-06-20 using the HMR-free
  `frontend-tunnel` origin. `cloudflared` was installed to a user-local tools
  path, a temporary `https://*.trycloudflare.com` URL was generated, and public
  checks passed for frontend load, `/api/health`, `/api/meta/voice/readiness`,
  WSS `/gateway` HELLO, and `npm run smoke:realtime:browser` with
  `browserErrors: 0`. The exact temporary URL is not recorded as a stable
  deployment address. TURN remained unconfigured, so real different-network
  microphone and screen-share QA is still incomplete.
- The active Cloudflare Tunnel path was rechecked for external-network manual QA
  preparation on 2026-06-20. Docker services, `frontend-tunnel`, and the
  `cloudflared` process were running; the temporary public URL returned HTTP 200;
  `/api/health`, `/api/meta/voice/readiness`, WSS `/gateway` HELLO, and
  public-origin `npm run smoke:realtime:browser` passed again. A new checklist in
  `docs/assignment-submission-guide.md` separates user-run two-network manual QA
  from Codex-run automated public-origin checks. Because `turn_configured` stayed
  `false`, the correct status remains "Cloudflare signaling path verified,
  TURN/NAT media gate incomplete."
- A user-run hotspot external-network QA pass followed on 2026-06-20: PC A stayed
  on the home network, PC B used a phone hotspot, and both connected through the
  active Cloudflare Quick Tunnel URL. DM send/receive and voice call
  speaking/listening worked. Document this as a specific hotspot external-network
  STUN/P2P success, not as universal TURN-backed media support; `turn_configured`
  remained `false` and hotspot screen-share still needs separate manual QA. This
  is not the final submission pass. Continue with missing design and feature
  remediation before final packaging: Discord UI detail/density polish,
  Friends/DM/server invite UX completion, voice/screen-share UX polish,
  responsive checks, accessibility checks, and inactive-control cleanup.
- The first Friends home usability remediation pass is tracked in
  `docs/remediation-tasks/friends-home-remediation-2026-06-20.md`. The pass
  documents and fixes first-screen Friends issues: unsupported Start Call/View
  Profile/Mute Conversation entries were removed from active friend menus and
  global friend/DM context menus as a temporary inactive-control cleanup, but they
  are now explicitly tracked as appropriate Discord-clone follow-up features:
  app-owned friend profile popout, real friend/DM call flow, conversation mute
  behavior, a private-sidebar start-new-DM recipient picker, and target-aware
  friend/DM context menus. These are not excluded from the Discord clone scope;
  they are pending feature-completion stages F10-F17. Friends tabs now expose
  counts, blocked users get an on-demand blocked tab, Add Friend success/error
  feedback appears inside the Add Friend panel, search empty copy distinguishes
  no-result from no-data, selected-friend activity copy no longer implies activity
  for offline/no-activity friends, mobile rows keep management actions reachable,
  and the README Korean quick-start block was restored as readable UTF-8 Korean.
- Friends/DM usability scope was rechecked after the latest Discord DM screenshots.
  `docs/remediation-tasks/friends-dm-usability-implementation-reference.md` is the
  Codex-facing English implementation reference, and
  `docs/remediation-tasks/friends-dm-usability-checklist-ko.md` is the Korean
  user-facing checklist. Additional non-optional usability targets are now tracked:
  incoming friend request feedback, bottom-anchored DM/server message timelines
  with controlled auto-scroll and jump-to-latest behavior, and target-aware DM
  header/profile-side actions. These are feature-completion items, not decorative
  polish, and should be implemented before treating the private Friends/DM surface
  as complete.
- The 2026-06-20 Friends/DM usability implementation pass added:
  `frontend/src/components/CreateDmDialog.vue`,
  `frontend/src/components/FriendProfileDialog.vue`, local muted-DM persistence in
  `frontend/src/stores/preferences.ts`, muted-DM unread suppression in
  `frontend/src/stores/dms.ts`, target-aware friend/DM context routing in
  `frontend/src/App.vue`, bottom-anchored DM/server timelines in
  `DirectMessageView.vue` and `ChatView.vue`, and app-owned incoming friend request
  notice/focus behavior.
- The 2026-06-20 Friends home follow-up pass refined the visible Friends screen:
  `FriendsHome.vue` now hides redundant All/Online tab count badges, avoids
  duplicate pending request headings for a single visible request group, groups All
  friends into optional local favorites plus one compact sorted friend list without
  online/offline subsection splits, and renders every strictly-online friend in
  Active Now. Row shortcut actions were reduced to favorite plus the overflow menu
  because profile/message/call are already available inside `...`. `App.vue`
  passes a Friends reset key so the private sidebar Friends entry returns the tab
  to All. `preferences.ts` persists local favorite-friend IDs. `VoicePanel.vue`
  separates the lower user-settings gear to My Account from quick voice popover
  Voice & Video settings, and input/output chevrons toggle their popovers open and
  closed.
- The 2026-06-20 DM private voice boundary pass added real DM voice-room signaling
  without replacing the existing guild voice transport. Gateway voice payloads now
  carry an optional `context_type` of `guild` or `dm`; `backend/app/gateway/router.py`,
  `manager.py`, `subscriptions.py`, and `voice_service.py` route DM voice state,
  snapshots, and offer/answer/ICE/screen signals through subscribed DM rooms while
  preserving the existing guild channel payload shape. Frontend `useGateway.ts`,
  `voicePresence.ts`, `guildGatewayHandlers.ts`, and
  `useVoiceSessionController.ts` understand the same context boundary, so Friends
  and DM `Start Call` create/open the one-to-one DM and join a private WebRTC room.
  `DirectMessageView.vue` shows a Discord-like DM call stage with a leave action,
  and the bottom `VoicePanel` can disconnect, mute/deafen, and screen-share while
  connected to either a guild channel or a DM call. Backend gateway tests now cover
  DM voice state snapshots and DM-only signal routing. Frontend lint/tests/build,
  Docker backend gateway tests, local submission readiness, and HTTPS realtime
  browser smoke passed after rebuilding the Docker stack. Manual two-account real
  microphone QA for DM private calls remains recommended before final submission.
- A follow-up Friends/DM usability pass added receiver-side feedback for private
  DM calls and clearer favorite-friend distinction. `frontend/src/App.vue` now
  detects an incoming DM voice state from another user, shows an app-owned private
  call banner with accept/decline actions, and joins the same DM-scoped WebRTC
  room when accepted. `frontend/src/components/FriendsHome.vue` and
  `frontend/src/styles/base.css` now render favorited friends with a distinct row
  accent, badge, and persistent active star state instead of relying only on the
  group heading.
- A second DM call voice-control follow-up added input/output quick settings to
  the active DM call stage in `frontend/src/components/DirectMessageView.vue`.
  These controls reuse the same `useVoiceRtc.updateVoiceDeviceSettings(...)` and
  device refresh path as `VoicePanel.vue`, so guild voice and DM calls share one
  microphone, output, sensitivity, noise-gate, and RNNoise settings model.
  `frontend/src/composables/useVoiceRtc.ts` now keeps an active call connected
  while rebuilding the local microphone processor for input-device or RNNoise mode
  changes, then swaps the new processed audio track into each peer connection
  through `voicePeerConnections.replaceLocalAudioTrack(...)`. Volume, sensitivity,
  and input-gate changes remain live processor updates. The lower `VoicePanel`
  quick settings popover now opens above the entire status/voice panel instead of
  covering the connected status card.
- A third DM call follow-up tightened Discord-like active-call controls and call
  lifecycle behavior. `DirectMessageView.vue` now renders the microphone, output,
  Voice & Video settings, and hang-up controls in one horizontal call toolbar, and
  anchors the input/output popovers to that toolbar instead of pinning them to the
  far side of the call stage. If one user leaves while the other remains in the
  DM voice room, `App.vue` suppresses repeated incoming-call banners for that
  still-active call and exposes it as a joinable DM call stage when the DM is
  selected. `useVoiceSessionController.ts` schedules a DM-only solo-call cleanup:
  if the local user is alone in a DM call for 3 minutes, the client leaves the DM
  voice room. Guild voice channels are not affected.
- A fourth DM call toolbar follow-up scoped the active private-call controls to
  the requested Discord-like behavior: microphone and output buttons now toggle
  mute/deafen directly, their chevrons open and close the corresponding quick
  settings, the separate call-stage settings icon was removed, the hang-up control
  remains a distinct red button, and the DM call popover opens downward to avoid
  clipping at the top of the call stage. The lower `VoicePanel` quick popover was
  also raised farther above the lower status/voice panel so it does not cover the
  connected DM call card.
- A DM message usability follow-up added bottom-start DM layout behavior and
  current-user message deletion. `DirectMessageView.vue` now uses a DM-only flex
  spacer so short or empty DM conversations start near the composer while long
  threads still scroll to the latest message, shows one-to-one intro status
  instead of duplicating the recipient name, visually distinguishes local vs
  remote DM messages, and exposes a delete action only on current-user messages.
  `DELETE /api/dms/{dm_id}/messages/{message_id}` persists author-only deletion
  through PostgreSQL/demo storage and publishes `DM_MESSAGE_DELETE`; `dms.ts` and
  `dmGatewayHandlers.ts` remove the message for both the local sender and remote
  subscribers.
- A 2026-06-20 DM usability correction kept current-user and remote DM messages
  left-aligned for readability while preserving current-user row styling and
  author-only delete controls. `DirectMessageView.vue` restores composer focus
  after send for repeated typing. `PrivateChannelSidebar.vue`, `App.vue`,
  `dms.ts`, and `/api/dms/{dm_id}` now support `대화 닫기`: PostgreSQL stores this
  as `direct_message_members.is_hidden` per user, demo storage mirrors the same
  behavior, `DM_DELETE` removes the closed DM from the current user's sessions,
  and recreating the same DM unhides the conversation without deleting the other
  participant's history.

- A 2026-06-21 DM follow-up removed the visible sidebar X close button and moved
  `대화 닫기` to the app-owned DM row context menu. `DirectMessageView.vue` now
  preserves composer focus after Enter or send-button submission through the
  post-render update, so repeated DM entry stays inside the message input.
- The DM composer focus fix now explicitly waits for the temporary disabled
  mutation window to end before restoring focus, and
  `scripts/realtime_browser_smoke.mjs` verifies that the DM textbox remains the
  active element after a submitted DM message.
- A 2026-06-21 DM timeline display fix made DM message timestamps source from the
  persisted `created_at` field instead of synthetic index-based times. PostgreSQL
  DM message creation now returns the inserted row timestamp, demo-store DM
  message creation stamps the current UTC time, and `DirectMessageView.vue` uses
  that timestamp for both the date divider and per-message time. The same pass
  tightened the DM intro/date/message spacing so the intro actions do not overlap
  the first message, keeps only the date divider as the separator between the intro
  and message list, and centers current-user delete controls vertically inside the
  message row.
- The follow-up fix keeps the date divider inside the DM intro block so the
  profile/actions/date/message order cannot visually interleave during bottom-up
  scrolling. Realtime publisher payloads now use JSON-safe Pydantic dumps so
  `created_at` dispatch data is serialized as a string, preventing DM message POST
  500s during active gateway sessions. `frontend/nginx.conf` also sends `no-store`
  cache headers for the Cloudflare Tunnel demo frontend so rebuilt bundles appear
  without stale static-page caching.
- A 2026-06-21 DM layout follow-up now wraps the DM intro, intro-owned date
  divider, and DM message rows in one `dm-thread-stack`. The stack keeps short
  conversations bottom-started near the composer while forcing the intro and
  messages to move as one normal scroll-flow unit, so newly added messages cannot
  overlap the profile/actions intro block.
- A follow-up DM display correction keeps the active private-call toolbar inside
  the black DM call stage by giving that stage enough vertical room for avatars,
  status text, and controls. `DirectMessageView.vue` also inserts additional DM
  date dividers whenever adjacent persisted message timestamps cross a local
  calendar date boundary, matching Discord's per-day timeline grouping.
- A 2026-06-21 server-add follow-up localizes
  `frontend/src/components/ServerAddDialog.vue`, lets the add-server modal close
  from backdrop clicks, and removes the demo-only automatic `Project` rail folder
  assignment in `frontend/src/App.vue` so newly created servers appear as normal
  top-level rail icons instead of being grouped under `PR`.
- A 2026-06-21 Cloudflare demo refresh fix keeps the local HTTPS and tunnel
  origins in sync. The root `docker:up:https:detached` script now also includes
  `compose.cloudflare-tunnel.yaml`, so `frontend-tunnel` on port `5174` is rebuilt
  with local HTTPS changes. `docker:up:cloudflare-tunnel` force-recreates the
  tunnel frontend, and `frontend/nginx.conf` sends strict no-cache/no-store
  headers for Cloudflare Quick Tunnel demos.
- A 2026-06-21 voice presence sync fix closes the late server-join gap. When a
  user joins or refreshes into a guild after other users are already in a voice
  channel, `backend/app/realtime/fanout.py` now triggers
  `GatewayConnectionManager.send_guild_voice_state_snapshots(...)` after
  `GUILD_UPDATE` fan-out, so the new subscriber receives the current
  `VOICE_STATE_SNAPSHOT` without waiting for existing participants to mute,
  deafen, leave, or rejoin. Backend tests cover both manager-level snapshot
  delivery and the realtime fan-out trigger.
- A 2026-06-21 screen-share refresh follow-up targets the remaining black remote
  screen case after a refreshed participant rejoins voice. `VoiceVideoSink.vue`
  now mutes screen-share video elements and retries playback when tracks or media
  metadata change. `voicePeerConnections.ts` adds bounded repair when explicit
  remote screen state is true but no active screen track arrives, recreates
  already-used answer-side peers for incoming offers, and makes an active screen
  sharer proactively renegotiate with later/rejoined participants. Frontend lint,
  tests, production build, and `git diff --check` passed. The stricter HTTPS
  browser smoke still cannot complete the fake-screen frame assertion
  (`videoWidth: 0`, `videoHeight: 0`), so the real shared tab/window refresh path
  remains a manual QA gate.
- A 2026-06-21 settings presentation follow-up changed user settings from a full
  workspace destination into a Discord-like modal overlay. `navigation.ts` now
  tracks `settingsOpen` separately from the active workspace destination, so
  Friends, DM, server text, voice, and lower voice controls remain visible behind
  the dimmed settings layer. `SettingsView.vue` owns its in-modal close button,
  while `App.vue` renders the settings panel as an app-level overlay and keeps the
  current page state intact.

After each stage or meaningful feature:

- Update this file's implementation map and integration notes.
- Update `docs/implementation-plan.md` stage status.
- Update `docs/PROMPT_COMPLIANCE.md` when prompt alignment, document ownership, or
  verification policy changes.
- Run relevant verification commands.
- Commit and push to `origin/main` unless the user asks otherwise.
