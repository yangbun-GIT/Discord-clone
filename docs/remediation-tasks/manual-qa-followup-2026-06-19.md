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
3. Refresh still leaves the active call.
   - Current WebRTC media session is not restored after page reload.
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
     processing presets. The default is speech-stability, which disables browser
     noise suppression and enables auto gain to reduce sustained-syllable chopping.
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
- Real sustained-vowel listening remains a manual gate because fake-device tests do
  not prove speech quality.

### Stage M2: Screen-Share Participant Composition

Owner files:

- `frontend/src/App.vue`
- `frontend/src/components/VoicePanel.vue`
- `frontend/src/components/VoiceVideoSink.vue`
- `frontend/src/styles/base.css`
- `scripts/realtime_browser_smoke.mjs`

Tasks:

1. Redesign receiver view so a remote user's screen share and participant state are
   one composition.
2. Keep sharer-side local preview available, but avoid duplicate remote user cards.
3. Define multi-share layout rules: one tile per sharing participant, with status
   overlay or side metadata.
4. Update browser smoke to assert that a remote sharing user does not produce both a
   separate screen tile and a separate duplicate participant card in the same stage.

Acceptance:

- Receiver sees one primary card per sharing participant.
- Four sharing users produce four share/participant compositions, not eight cards.
- Local preview and local participant state remain understandable for the sharer.

### Stage M3: Refresh Rejoin Recovery

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
2. On reload, do not silently claim the microphone. Show an app-owned "rejoin
   voice" recovery prompt.
3. If the user confirms, reacquire microphone permission and rejoin the channel.
4. If the user dismisses, send/confirm a leave state and clear stale local state.
5. Add automated coverage for reload state reconciliation where feasible.

Acceptance:

- Refresh does not leave stale connected UI.
- User can intentionally rejoin the previous voice channel after reload.
- The other participant sees a consistent leave/rejoin transition.

### Stage M4: LAN Secure-Context Development Path

Owner files:

- `README.md`
- `docs/voice-qa.md`
- `docs/deployment.md`
- `package.json`
- Vite/backend dev config if HTTPS scripts are added.

Tasks:

1. Document why `http://<LAN-IP>` blocks microphone/screen capture in modern
   browsers.
2. Add a local HTTPS LAN path, preferably using a documented dev certificate flow.
3. Ensure backend CORS and gateway URLs work from the LAN origin.
4. Add a LAN checklist for backend health, frontend load, gateway connection,
   text/DM, voice join, and screen share.

Acceptance:

- Another PC can open the clone over a secure origin and attempt microphone capture.
- The docs clearly separate localhost-only, HTTP LAN, and HTTPS LAN capabilities.

### Stage M5: TURN/NAT Readiness

Owner files:

- `README.md`
- `docs/voice-qa.md`
- `docs/deployment.md`
- `backend/app/api/routes/meta.py`
- `backend/app/core/config.py`

Tasks:

1. Keep TURN credentials environment-only.
2. Add a clear setup path for `WEBRTC_ICE_SERVERS_JSON`.
3. Expose safe readiness data only: ICE server count and `turn_configured`.
4. Add a manual internet test script using two different networks.

Acceptance:

- User can tell whether TURN is configured before starting an external test.
- No TURN credential, ICE candidate, token, or media label is logged or documented.

### Stage M6: Friends Pending And Presence Clarity

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
2. Add clear incoming/outgoing request grouping and copy.
3. Implement or document online/offline/idle/away realtime presence updates for
   friends.
4. Ensure Friends list status changes do not require refresh.

Acceptance:

- The user can distinguish friend request state from online state at a glance.
- Friend presence updates appear consistently in Friends and DM surfaces.

### Stage M7: DM Identity Consistency

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
2. Audit DM participant ordering and display-name selection.
3. Ensure one-to-one DMs display the other participant, while messages display the
   actual author.
4. Add regression coverage for A->B and B->A message receipt.

Acceptance:

- Receiving a DM never changes the sidebar row to the wrong account.
- Message author and DM row participant identity remain distinct and correct.

### Stage M8: Invite Modal Per-Recipient State And DM Invite Delivery

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
2. Keep plain code/link copy as a separate bottom action.
3. For a friend row, send a DM containing a clear invite link or invite code.
4. Confirm recipient can use the invite from the DM flow.
5. Keep all notices app-owned and localized.

Acceptance:

- Clicking one friend's invite button affects only that row.
- Friend-targeted invite results in a DM-visible invitation instead of only copying
  a code.

### Stage M9: Deafen Behavior

Owner files:

- `frontend/src/composables/useVoiceSessionController.ts`
- `frontend/src/composables/useVoiceRtc.ts`
- `frontend/src/components/VoiceAudioSink.vue`
- `frontend/src/App.vue`
- `frontend/src/i18n/index.ts`

Tasks:

1. Verify current deafen state updates local UI and gateway state.
2. Ensure remote audio elements are muted or paused locally while deafened.
3. Ensure undeafen restores remote audio without requiring rejoin.
4. Keep microphone mute semantics separate from deafen semantics.

Acceptance:

- With deafen enabled, user does not hear remote participants.
- Remote participants do not lose their connection because one user deafened.
- UI communicates deafen state clearly in bottom panel and voice workspace.

### Stage M10: Invite Permission Browser QA

Owner files:

- `frontend/src/App.vue`
- `frontend/src/components/ChannelSidebar.vue`
- `frontend/src/stores/guilds.ts`
- `backend/tests/test_api_routes.py`
- `scripts/realtime_browser_smoke.mjs` if extended.

Tasks:

1. Keep backend `403` permission enforcement.
2. Add browser-level owner/member permission verification.
3. Owner should see invite controls and create an invite.
4. Member without `CREATE_INSTANT_INVITE` should not see active invite controls; if
   any disabled control remains, it must explain the permission state in localized
   app copy.

Acceptance:

- No raw `create invite permission required` text reaches normal UI.
- Unauthorized member cannot create invites through UI or API.

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
