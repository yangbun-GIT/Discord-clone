# Manual QA Follow-Up Remediation Plan - 2026-06-19

## Status

- Source: user-run manual QA with three local accounts and real microphone/screen
  share checks.
- Purpose: turn the latest manual findings into implementation-ready stages.
- Execution rule: process one stage at a time. For each stage, inspect owner files,
  implement, update this document, verify with automated tests when possible, then
  run the matching manual check before marking the stage complete.

## Confirmed Working

- Real microphone permission and capture can start.
- Short spoken words are transmitted with acceptable quality in the current local
  same-PC test.
- Real screen picker opens and screen sharing starts successfully.
- Screen-share stop removes the remote share.
- Friend request send/receive/accept flow works in manual testing.
- Server invite creation and invite-code join work for authorized users.
- Backend invite permission check works: an owner can create an invite, while a
  normal member receives `403`.

## Confirmed Gaps

1. Sustained vowel/syllable audio is chopped.
   - Example: a long "아" is heard as repeated cut segments.
   - Short words can sound acceptable, so the problem is not total capture failure.
2. Screen-share receiver layout duplicates surfaces.
   - The sharer can reasonably see local preview plus own participant state.
   - The receiver should see one participant/share composition per user, not a
     separate screen card plus a separate participant card.
   - If four users share, the current model can create eight visible cards.
3. Refresh must not leave the user visibly out of the active voice channel.
   - Browser reload still tears down the old WebRTC media tracks, but the clone
     should automatically rejoin the same voice channel once the refreshed tab's
     gateway connection is ready.
4. LAN voice join fails from another PC on the same Wi-Fi.
   - Browser reports HTTPS/localhost secure-context errors.
   - Current LAN path is not ready for real microphone/screen capture.
5. TURN/NAT external test is not yet possible for the user.
   - `/api/meta/voice` reports `turn_configured: false`.
   - The project needs explicit setup and readiness checks before internet voice
     can be claimed.
6. Friends Pending tab copy is ambiguous.
   - "대기 중" can read as user presence state instead of friend-request state.
7. Friend online/offline/idle/away presence does not update in the Friends list.
8. DM receive identity can mismatch the direct-message list entry.
   - Receiving side can see a sender identity that does not align with the DM row.
9. Invite modal copy state is global.
   - Copying/sending invite for one friend changes all invite rows to copied.
10. Friend invite action should send an invite through DM or a direct join link.
    - Plain code copy remains useful, but friend-targeted invite should create a
      clearer message/link flow.
11. Deafen/소리 차단 does not behave as expected.
    - Remote audio should be muted locally while deafen is active, and the UI should
      make this state clear.

## Remediation Stages

### Stage M1: Real Speech Dropout Diagnostics And Fix

Status: implemented, pending real-microphone sustained-vowel manual QA.

Owner files:

- `frontend/src/composables/voiceMedia.ts`
- `frontend/src/composables/useVoiceRtc.ts`
- `frontend/src/composables/voiceStats.ts`
- `frontend/src/components/SettingsView.vue`
- `frontend/src/i18n/index.ts`
- `docs/voice-qa.md`

Tasks:

1. Inspect current audio constraints, track enabled state, and VAD interaction.
   - Completed: VAD only drives input meter/speaking state and does not disable or
     gate outgoing microphone tracks.
2. Confirm no app code gates outgoing microphone audio based on VAD/speaking state.
   - Completed.
3. Add or tune visible audio-processing options for echo cancellation, noise
   suppression, auto gain, and optionally default processing presets.
   - Completed: settings now expose speech-stability, balanced, and near-raw
     processing presets.
   - 2026-06-20 follow-up: OBS comparison showed the raw microphone recording
     stayed continuous while the clone desktop-audio capture had repeated short
     silent gaps. The default speech-stability preset now minimizes browser echo
     cancellation, noise suppression, and auto gain instead of relying on browser
     auto-processing for long vowels.
4. Add a manual sustained-vowel QA script with expected pass criteria.
   - Completed in `docs/voice-qa.md`.
5. Record selected processing values in local preferences without logging device
   labels or raw audio.
   - Completed.

Acceptance:

- A sustained Korean vowel spoken for 10 seconds should not be repeatedly chopped
  under at least one documented local processing preset.
- Short words and normal sentences remain intelligible.
- Mute/unmute still works and is reflected remotely.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run test -- --run src/composables/voiceMedia.test.ts`
  passed.
- `npm --prefix frontend run build` passed.
- 2026-06-20 follow-up: the input-level meter now samples before RNNoise/gate
  attenuation, local speaking feedback is driven directly from that RMS input
  level, the sensitivity gate uses a longer hold plus soft attenuation instead of
  hard cutting, and remote received-audio streams update remote speaking feedback.
  Frontend lint, frontend tests, production build, and
  `npm run smoke:realtime:browser` passed.
- 2026-06-20 sustained-input follow-up: the app now defaults RNNoise and the local
  input sensitivity gate off, migrates existing default device settings once to
  that stable baseline, and keeps live input amount private to Voice & Video
  settings. Workspace/sidebar/user-card/remote-card UI shows binary speaking
  feedback only, and the quick microphone popover shows configured sensitivity
  percent instead of live input level.
- 2026-06-20 option audit follow-up: the default stable path remains unchanged,
  but the optional input sensitivity gate now makes the sensitivity slider affect
  the actual transmit threshold. The gate strongly attenuates below-threshold input
  when enabled, while RNNoise and native browser echo/noise/auto-gain options still
  apply on the next voice join because they are capture/AudioWorklet setup options.
- Real sustained-vowel listening remains a manual gate because fake-device tests do
  not prove speech quality.

### Stage M2: Screen-Share Participant Composition

Status: implemented, pending manual multi-user real screen-share layout QA.

Owner files:

- `frontend/src/App.vue`
- `frontend/src/components/VoicePanel.vue`
- `frontend/src/components/VoiceVideoSink.vue`
- `frontend/src/styles/base.css`
- `scripts/realtime_browser_smoke.mjs`

Tasks:

1. Redesign receiver view so a remote user's screen share and participant state are
   one composition.
   - Completed: remote sharing users render as screen-share participant
     compositions instead of a separate screen tile plus a duplicate participant
     tile.
2. Keep sharer-side local preview available, but avoid duplicate remote user cards.
   - Completed.
3. Define multi-share layout rules: one tile per sharing participant, with status
   overlay or side metadata.
   - Completed for current layout: one `screen-share-tile` per remote sharing user
     with user label and connection state.
4. Update browser smoke to assert that a remote sharing user does not produce both a
   separate screen tile and a separate duplicate participant card in the same stage.
   - Completed.

Acceptance:

- Receiver sees one primary card per sharing participant.
- Four sharing users produce four share/participant compositions, not eight cards.
- Local preview and local participant state remain understandable for the sharer.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:browser` passed with
  `remoteSharingUserScreenTiles: 1` and
  `duplicateRemoteSharingParticipantCards: 0`.

### Stage M3: Refresh Rejoin Recovery

Status: implemented, pending real-browser permission regression QA.

Owner files:

- `frontend/src/composables/useVoiceSessionController.ts`
- `frontend/src/composables/useVoiceRtc.ts`
- `frontend/src/stores/guilds.ts`
- `frontend/src/stores/voicePresence.ts`
- `frontend/src/App.vue`
- `backend/app/gateway/voice_service.py`
- `docs/realtime-communication-qa.md`

Tasks:

1. Persist the last connected voice guild/channel in a safe local client state.
   - Completed: client storage records only user/guild/channel IDs for the last
     joined voice channel.
2. On reload, restore the same voice-channel membership after the refreshed tab is
   connected to the gateway.
   - Completed: normal backend websocket disconnects keep the current voice state
     through a short grace window instead of immediately broadcasting leave.
   - Completed: heartbeat timeout and stale-send cleanup bypass the grace window
     and still leave immediately.
   - Completed: the client stores only same-user channel metadata, then
     automatically reacquires microphone access and rejoins the previous channel
     after gateway `READY`.
3. Keep an app-owned recovery prompt as the fallback when automatic capture fails.
   - Completed: failed automatic recovery leaves the previous-channel notice
     available so the user can retry or leave from the recovery state.
4. If the user dismisses, send/confirm a leave state and clear stale local state.
   - Completed: dismissal clears the local recovery record. Normal voice leave also
     clears the recovery record.
5. Add automated coverage for reload state reconciliation where feasible.
   - Completed: browser smoke reloads a connected tab, verifies the voice panel is
     connected again without a visible rejoin prompt, and confirms the other tab
     receives a remote audio sink again.
6. Preserve the user's current workspace page after refresh.
   - Completed: navigation now stores a same-user restorable destination and
     DM/guild/channel IDs, then restores them before workspace state reload.
   - Completed: browser smoke verifies that a server text channel and selected
     voice workspace remain open after reload instead of falling back to Friends.

Acceptance:

- Refresh does not leave stale connected UI.
- User returns to the previous voice channel automatically after reload when the
  browser can reacquire microphone capture.
- If automatic recovery fails, the user can intentionally rejoin the previous voice
  channel from the app-owned notice.
- The other participant sees a consistent leave/rejoin transition.
- Refresh returns to the same DM/server/voice page instead of the initial Friends
  page when the saved destination is still accessible.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:browser` passed after the Docker frontend refresh with
  `voiceAutoRejoinedAfterReload: true`, `voiceRejoinPromptVisible: false`, and
  `voiceRejoinRecovered: true`.
- `cd backend; ..\.venv\Scripts\python.exe -m pytest tests/test_gateway_manager.py
  tests/test_gateway_routes.py -q` passed, including normal-disconnect grace,
  same-user rejoin cancellation, and timeout leave coverage.
- Additional regression target: `scripts/realtime_browser_smoke.mjs` records
  `serverWorkspacePreservedAfterReload` and
  `voiceWorkspacePreservedAfterReload`.
- Real browser permission prompt behavior remains a manual gate because automated
  fake-device media cannot prove the user's actual microphone permission flow.

### Stage M4: LAN Secure-Context Development Path

Status: implemented, pending real same-LAN HTTPS device QA.

Owner files:

- `README.md`
- `docs/voice-qa.md`
- `docs/deployment.md`
- `package.json`
- Vite/backend dev config if HTTPS scripts are added.

Tasks:

1. Document why `http://<LAN-IP>` blocks microphone/screen capture in modern
   browsers.
   - Completed in `README.md`, `docs/deployment.md`, and `docs/voice-qa.md`.
2. Add a local HTTPS LAN path, preferably using a documented dev certificate flow.
   - Completed: `npm run dev:frontend:lan:https` validates local certificate env
     vars and Vite reads `VITE_HTTPS_KEY_FILE`/`VITE_HTTPS_CERT_FILE`.
3. Ensure backend CORS and gateway URLs work from the LAN origin.
   - Completed for the Vite-proxy path: `/api` and `/gateway` stay same-origin
     behind the HTTPS frontend, and `VITE_BACKEND_PROXY_TARGET` documents the
     backend target.
4. Add a LAN checklist for backend health, frontend load, gateway connection,
   text/DM, voice join, and screen share.
   - Completed in `docs/voice-qa.md`.

Acceptance:

- Another PC can open the clone over a secure origin and attempt microphone capture.
- The docs clearly separate localhost-only, HTTP LAN, and HTTPS LAN capabilities.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- Same-LAN HTTPS media capture remains a manual gate because it requires a trusted
  certificate installed on the second device.

### Stage M5: TURN/NAT Readiness

Status: implemented, pending real TURN credentials and different-network QA.

Owner files:

- `README.md`
- `docs/voice-qa.md`
- `docs/deployment.md`
- `backend/app/api/routes/meta.py`
- `backend/app/core/config.py`

Tasks:

1. Keep TURN credentials environment-only.
   - Completed: `.env.example` keeps placeholders only, and the readiness check
     prints no ICE URLs, TURN credentials, tokens, candidates, or device labels.
2. Add a clear setup path for `WEBRTC_ICE_SERVERS_JSON`.
   - Completed in `README.md`, `docs/deployment.md`, and `docs/voice-qa.md`.
3. Expose safe readiness data only: ICE server count and `turn_configured`.
   - Completed with `GET /api/meta/voice/readiness`, which returns only
     `ice_server_count`, `stun_configured`, and `turn_configured`.
4. Add a manual internet test script using two different networks.
   - Completed with `npm run check:voice:readiness` plus the different-network
     manual QA checklist in `docs/voice-qa.md`.

Acceptance:

- User can tell whether TURN is configured before starting an external test.
- No TURN credential, ICE candidate, token, or media label is logged or documented.

Verification:

- `npm run test:backend -- -q tests/test_api_routes.py::test_voice_readiness_omits_ice_server_credentials`
  passed.
- `npm run lint:backend` passed.
- `npm run test:backend` passed.
- `npm run check:voice:readiness` passed against the local Docker backend and
  reported `turn_configured: false` without credentials.
- Real TURN/NAT completion remains blocked until valid TURN credentials are supplied
  and two users on different networks pass voice and screen-share QA.

### Stage M6: Friends Pending And Presence Clarity

Status: implemented, pending real two-account presence-change QA if a dedicated
presence update endpoint/event is added later.

Owner files:

- `frontend/src/components/FriendsHome.vue`
- `frontend/src/stores/dms.ts`
- `frontend/src/stores/session.ts`
- `frontend/src/composables/useGateway.ts`
- `backend/app/gateway/router.py`
- `backend/app/gateway/manager.py`
- `frontend/src/i18n/index.ts`

Tasks:

1. Rename or visually clarify the Pending tab as friend-request pending, not
   presence waiting.
   - Completed: the tab is now labeled as friend requests instead of generic
     waiting/pending copy.
2. Add clear incoming/outgoing request grouping and copy.
   - Completed: the Friends list groups pending incoming and outgoing friend
     requests separately with counts.
3. Implement or document online/offline/idle/away realtime presence updates for
   friends.
   - Completed for existing relationship gateway updates: relationship status
     updates now sync into existing DM rows and participants. A standalone presence
     endpoint/event remains outside current backend scope and is not claimed as
     complete.
4. Ensure Friends list status changes do not require refresh.
   - Completed for `RELATIONSHIP_UPDATE` dispatches; focused frontend regression
     coverage verifies same-user DM row presence updates without reload.

Acceptance:

- The user can distinguish friend request state from online state at a glance.
- Friend presence updates appear consistently in Friends and DM surfaces.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run test -- --run src/stores/gatewayIdempotency.test.ts`
  passed.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:browser` passed after the Docker frontend refresh.

### Stage M7: DM Identity Consistency

Status: implemented.

Owner files:

- `frontend/src/stores/dms.ts`
- `frontend/src/stores/dmGatewayHandlers.ts`
- `frontend/src/stores/dmVisibility.ts`
- `frontend/src/components/PrivateChannelSidebar.vue`
- `frontend/src/components/DirectMessageView.vue`
- `backend/app/services/dm_service.py`
- `backend/app/repositories/dms.py`

Tasks:

1. Reproduce the receive-side mismatch between incoming message author and DM list
   row.
   - Completed: the likely mismatch path is `DM_CREATE` gateway payloads that can
     arrive in another user's display perspective.
2. Audit DM participant ordering and display-name selection.
   - Completed: backend REST/demo views already compute display name from the
     requesting user perspective; frontend now defensively normalizes gateway
     payloads by current user ID.
3. Ensure one-to-one DMs display the other participant, while messages display the
   actual author.
   - Completed: DM rows recompute `recipient_ids`, `display_name`, status, and
     activity from participants excluding the current user. Messages keep their
     original `author_id` and `author_name`.
4. Add regression coverage for A->B and B->A message receipt.
   - Completed: focused store regression covers current-user normalization for
     incoming `DM_CREATE`, and browser smoke covers live DM receipt.

Acceptance:

- Receiving a DM never changes the sidebar row to the wrong account.
- Message author and DM row participant identity remain distinct and correct.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run test -- --run src/stores/gatewayIdempotency.test.ts`
  passed.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:browser` passed after the Docker frontend refresh.

### Stage M8: Invite Modal Per-Recipient State And DM Invite Delivery

Status: implemented.

Owner files:

- `frontend/src/composables/useInviteController.ts`
- `frontend/src/App.vue`
- `frontend/src/stores/dms.ts`
- `frontend/src/components/DirectMessageView.vue`
- `frontend/src/i18n/index.ts`
- `backend/app/api/routes/dms.py`
- `backend/app/services/dm_service.py`

Tasks:

1. Replace the single global `inviteCopied` state with per-recipient state.
   - Completed: friend-row invite delivery state is tracked per friend ID, and
     bottom invite-code copy state is separate.
2. Keep plain code/link copy as a separate bottom action.
   - Completed: the bottom copy button only updates invite-code copy state.
3. For a friend row, send a DM containing a clear invite link or invite code.
   - Completed: friend-row invite sends a DM containing the invite code.
4. Confirm recipient can use the invite from the DM flow.
   - Completed for receipt: browser smoke confirms the recipient sees the invite
     code in DM realtime. Actual join-from-DM remains code-entry based.
5. Keep all notices app-owned and localized.
   - Completed: invite send success uses the existing app-owned notice layer and
     localized copy.

Acceptance:

- Clicking one friend's invite button affects only that row.
- Friend-targeted invite results in a DM-visible invitation instead of only copying
  a code.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run test -- --run src/composables/useInviteController.test.ts`
  passed.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:browser` passed after the Docker frontend refresh with
  `inviteDmRealtime: true`.

### Stage M9: Deafen Behavior

Status: implemented.

Owner files:

- `frontend/src/composables/useVoiceSessionController.ts`
- `frontend/src/composables/useVoiceRtc.ts`
- `frontend/src/components/VoiceAudioSink.vue`
- `frontend/src/App.vue`
- `frontend/src/i18n/index.ts`

Tasks:

1. Verify current deafen state updates local UI and gateway state.
   - Completed: existing deafen UI/gateway state remains intact.
2. Ensure remote audio elements are muted or paused locally while deafened.
   - Completed: `VoiceAudioSink` receives the deafen state and applies it to the
     remote audio element `muted` property.
3. Ensure undeafen restores remote audio without requiring rejoin.
   - Completed: browser smoke toggles undeafen and verifies remote audio elements
     become unmuted without reconnecting.
4. Keep microphone mute semantics separate from deafen semantics.
   - Corrected after user recheck: deafen now only mutes local playback of remote
     audio. The manual microphone mute button remains enabled while deafened and
     independently controls the local microphone track.
5. Keep screen sharing independent from deafen.
   - Completed after recheck: deafen no longer disables the screen-share button.

Acceptance:

- With deafen enabled, user does not hear remote participants.
- With deafen enabled, the local microphone continues to follow the separate
  microphone mute state instead of being implicitly disabled.
- While deafened, the microphone button can still mute and unmute the local
  microphone track.
- Remote participants do not lose their connection because one user deafened.
- UI communicates deafen state clearly in bottom panel and voice workspace.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:browser` passed after the Docker frontend refresh with
  `remoteAudioMutedWhileDeafened: true` and
  `remoteAudioUnmutedAfterUndeafen: true`.
- Recheck verification was updated after the independent-control fix to require
  `localMicrophoneOpenWhileDeafened: true`,
  `localMicrophoneMutedByMuteWhileDeafened: true`,
  `localMicrophoneUnmutedWhileStillDeafened: true`,
  `localMicrophoneRestoredAfterUndeafen: true`, and
  `muteButtonEnabledWhileDeafened: true`.

### Stage M10: Invite Permission Browser QA

Status: implemented.

Owner files:

- `frontend/src/App.vue`
- `frontend/src/components/ChannelSidebar.vue`
- `frontend/src/stores/guilds.ts`
- `backend/tests/test_api_routes.py`
- `scripts/realtime_browser_smoke.mjs` if extended.

Tasks:

1. Keep backend `403` permission enforcement.
   - Completed: existing backend invite permission behavior remains enforced and
     the browser smoke verifies a non-owner member receives `403`.
2. Add browser-level owner/member permission verification.
   - Completed: `scripts/realtime_browser_smoke.mjs` now records owner invite
     control visibility, member invite control hiding, member context-menu invite
     hiding, member API `403`, and raw permission-text absence.
3. Owner should see invite controls and create an invite.
   - Completed: the browser smoke requires the owner Create invite control to be
     visible and then uses it to deliver an invite code by DM.
4. Member without `CREATE_INSTANT_INVITE` should not see active invite controls; if
   any disabled control remains, it must explain the permission state in localized
   app copy.
   - Completed: `App.vue` global context-menu invite actions are now filtered by
     `guilds.canCreateInvite`; `ChannelSidebar` and the header already hide invite
     controls when the permission is absent.

Acceptance:

- No raw `create invite permission required` text reaches normal UI.
- Unauthorized member cannot create invites through UI or API.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `docker compose up -d --build frontend` refreshed the browser-test frontend.
- `npm run smoke:realtime:browser` passed with
  `ownerInviteControlVisible: true`, `memberInviteControlHidden: true`,
  `memberContextInviteHidden: true`, `memberInviteApiForbidden: true`, and
  `memberRawInvitePermissionHidden: true`.

## Verification Commands

Run after implementation stages where relevant:

```powershell
npm run lint:frontend
npm run test:frontend -- --run
npm --prefix frontend run build
npm run lint:backend
npm run test:backend
npm run smoke:realtime:browser
npm run smoke:realtime:redis
```

Manual gates still required:

- Real microphone sustained-vowel speech test.
- Real screen picker layout test with at least two participants.
- Same-LAN HTTPS test from another PC.
- TURN/NAT test after real TURN configuration.
