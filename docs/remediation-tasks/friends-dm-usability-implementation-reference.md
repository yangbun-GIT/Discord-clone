# Friends And DM Usability Implementation Reference

## Purpose

This is the Codex-facing implementation reference for the next Friends/DM usability
work. Use it together with:

- `DEVELOPMENT_PROMPT.md`
- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `docs/project-file-map.md`
- `docs/structure-map/reference-map.md`
- `docs/remediation-tasks/friends-home-remediation-2026-06-20.md`

The goal is not decorative pixel polish. The goal is to implement missing
Discord-like private-home behavior when it improves clarity, workflow efficiency,
feedback, or usability.

## Non-Negotiable Policy

- Do not classify a normal Friends/DM Discord-like control as excluded just because
  it is currently missing.
- If a visible control is useful and expected, implement it or keep it in a staged
  backlog with an owner, target files, and verification.
- If a visible control cannot be implemented in the current stage, do not leave it
  as an enabled placeholder.
- Keep all overlays, confirmations, and notices inside clone-owned UI. Do not use
  browser-native `alert`, `confirm`, `prompt`, or default context menus.
- Preserve current working local Docker, HTTPS LAN, Cloudflare quick-tunnel,
  realtime DM, and voice paths.

## Current Implementation Targets

### F10 - Friend Profile Popout

- Implement a lightweight app-owned profile popout/modal.
- Restore `View Profile` only after it opens the target friend profile.
- Include username, handle, presence, activity/no-activity state, relationship
  state, message entry, and relationship actions that already work.
- Target files:
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/App.vue`
  - `frontend/src/styles/base.css`
  - `frontend/src/i18n/index.ts`

### F11 - Friend/DM Call Entry

- Implement `Start Call` as a real friend/DM call entry.
- Reuse the existing voice transport boundary; do not break guild voice.
- Either add a private call-room mapping or a clear DM voice workflow.
- Target files:
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/components/DirectMessageView.vue`
  - `frontend/src/composables/useVoiceSessionController.ts`
  - `frontend/src/composables/useVoiceRtc.ts`
  - `backend/app/gateway/voice_service.py`
  - related gateway/API files if private voice rooms are added

### F12 - Conversation Mute

- Implement DM mute as a real preference.
- Muted DMs still receive messages but do not show normal unread or notification
  emphasis.
- Restore `Mute Conversation` only after the preference changes visible behavior.
- Target files:
  - `frontend/src/stores/dms.ts`
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/i18n/index.ts`
  - persistence files if a backend preference is added

### F13 - Start New DM Recipient Picker

- Replace the current `createDm -> handleOpenFriends` behavior.
- The private sidebar `+` and quick switcher create action should open a recipient
  picker/search.
- At minimum, list accepted friends; then create/open a one-to-one DM through
  `dms.createDm(...)`.
- Reuse an existing one-to-one DM if it already exists.
- Target files:
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/App.vue`
  - `frontend/src/stores/dms.ts`
  - `frontend/src/i18n/index.ts`
  - `frontend/src/styles/base.css`

### F14 - Target-Aware Friend/DM Context Menus

- Add target metadata for friend and DM rows.
- Restore right-click actions only when `App.vue` can route them to the exact
  friend or DM target.
- Actions should match implemented row-menu behavior.
- Target files:
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/App.vue`
  - `frontend/src/styles/base.css`
  - `frontend/src/i18n/index.ts`

### F15 - Incoming Friend Request Feedback

- Detect new incoming friend requests from `RELATIONSHIP_UPDATE`.
- Make request arrival visible without requiring manual refresh or hidden tab
  discovery.
- Prefer:
  - pending request badge on Friends/private-home surfaces
  - clone-owned notice/action that opens the pending request tab
  - stable unread-like indicator on `@me` when relevant
- Clear or update feedback after accept/reject/cancel/remove.
- Target files:
  - `frontend/src/stores/dms.ts`
  - `frontend/src/stores/dmGatewayHandlers.ts`
  - `frontend/src/App.vue`
  - `frontend/src/components/ServerRail.vue`
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/i18n/index.ts`
  - `frontend/src/styles/base.css`

### F16 - Bottom-Anchored DM And Server Message Timelines

- Make server chat and DM chat open at the latest message by default.
- Newly sent messages should remain visible at the bottom.
- Incoming messages should auto-scroll only when the user is already near the
  bottom.
- If the user is reading older messages, preserve scroll and show a compact
  "jump to latest" affordance.
- Keep chronological DOM order for accessibility unless a tested alternative is
  chosen.
- Target files:
  - `frontend/src/components/DirectMessageView.vue`
  - `frontend/src/components/ChatView.vue`
  - `frontend/src/stores/dms.ts`
  - `frontend/src/stores/guilds.ts`
  - `frontend/src/styles/base.css`
  - `frontend/src/i18n/index.ts`

### F17 - DM Header And Profile-Side Action Audit

- Audit DM-specific header/profile-side controls.
- Implement useful controls where they are expected:
  - profile view
  - DM call
  - message search
  - group/member information
- Hide or clearly scope anything not implemented in this pass.
- Target files:
  - `frontend/src/App.vue`
  - `frontend/src/components/DirectMessageView.vue`
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/i18n/index.ts`
  - `frontend/src/styles/base.css`

## Items Not Added To The Current Implementation Target

- Nitro, Store, Quests, public discovery, and payment-like features.
- New contact import or external account sync.
- Full large-scale search indexing beyond local visible-message search.
- Always-on public deployment. This remains separate from local/Cloudflare demo
  flow.

## 2026-06-20 Implementation Pass Status

- F10 Friend Profile Popout: implemented.
  - Added `frontend/src/components/FriendProfileDialog.vue`.
  - Friend rows, activity panel, and target-aware context menus can open an
    app-owned profile dialog with username, handle, presence, activity,
    relationship state, message entry, call entry, and mute toggle.
- F11 Friend/DM Call Entry: partially implemented, not complete as real private
  voice calling.
  - Friend/DM call controls now open the target DM and show clone-owned guidance.
  - The existing backend gateway still authorizes voice through guild voice
    channel subscriptions only. A true friend/DM call still needs a backend
    private-call room or DM voice mapping before it can be marked complete.
  - Do not report this as real friend/DM voice-call completion.
- F12 Conversation Mute: implemented as a local preference.
  - `frontend/src/stores/preferences.ts` persists muted DM IDs.
  - `frontend/src/stores/dms.ts` suppresses unread increments for muted inactive
    DMs while still receiving and rendering messages.
  - Friend, DM row, profile, and DM screen actions can toggle mute state.
- F13 Start New DM Recipient Picker: implemented.
  - Added `frontend/src/components/CreateDmDialog.vue`.
  - Private sidebar `+` and quick switcher create action open a friend recipient
    picker and create/open a DM through `dms.createDm(...)`.
- F14 Target-Aware Friend/DM Context Menus: implemented for the actions that can
  currently execute.
  - Friend and DM rows now provide `data-context-id`.
  - `App.vue` routes profile, message, mute, and call-entry actions to the exact
    friend/DM target.
  - The call action remains limited by F11.
- F15 Incoming Friend Request Feedback: partially implemented.
  - `RELATIONSHIP_UPDATE` increases for new `pending_incoming` relationships now
    show a clone-owned notice and focus the Friends pending view.
  - A dedicated `@me`/sidebar pending-request badge is still a follow-up if more
    persistent request attention is needed.
- F16 Bottom-Anchored DM And Server Message Timelines: implemented.
  - `DirectMessageView.vue` and `ChatView.vue` scroll to latest on DM/channel
    switch, keep latest visible while near bottom, preserve older scroll position,
    and show a jump-to-latest control.
  - DM messages remain left-aligned for both local and remote authors; current-user
    messages are distinguished by row styling and keep author-only deletion.
  - The DM composer restores input focus after Enter or send-button submission so
    repeated messages can be typed without clicking the input again.
- F17 DM Header And Profile-Side Action Audit: partially implemented.
  - DM screen now exposes profile, call-entry, and mute actions scoped to the
    selected DM.
  - The private sidebar exposes close conversation through the DM row context menu.
    The backend stores this as per-member hidden state, so the other participant's
    DM list and messages are not deleted. Recreating/opening the same DM unhides it.
  - Full DM search and richer group/member profile-side information remain
    follow-up items.
- Verification for this pass:
  - `npm run lint:frontend` passed.
  - `npm run test:frontend` passed with 7 files / 46 tests.
  - `npm --prefix frontend run build` passed.
  - `npm run smoke:realtime:browser:https` passed with server text realtime,
    DM realtime, invite-DM realtime, voice smoke, screen-share smoke, refresh
    recovery, and `browserErrors: 0`.
  - After `npm run docker:up:https:detached`, `npm run check:submission:local`
    passed for `https://localhost:5173/` with frontend, API health, database,
    STUN, and gateway HELLO available; TURN remained intentionally unconfigured.
  - After the Docker rebuild, `npm run smoke:realtime:browser:https` passed again
    with `browserErrors: 0`.
  - `git diff --check` passed with line-ending warnings only.

## Stage Process

For each stage:

1. Read the current target files and the Friends remediation document.
2. Confirm existing behavior before editing.
3. Implement the smallest complete behavior that removes the usability gap.
4. Update this document, the Friends remediation document, `PROJECT_CONTEXT.md`,
   and path maps if ownership changes.
5. Run relevant verification:
   - `npm run lint:frontend`
   - `npm run test:frontend`
   - `npm --prefix frontend run build`
   - `npm run smoke:realtime:browser:https` when realtime/DM/voice can be affected
   - `git diff --check`
6. If a new usability defect appears, add it to the current stage before moving on.
7. Commit and push with a Korean commit title.

## Manual QA Gates

- Two logged-in sessions can send/receive a friend request and the receiver sees
  realtime feedback.
- The private sidebar `+` opens a real DM picker and can create/open a DM.
- Friend profile opens from row menu, activity panel, and context menu when those
  controls are visible.
- Friend/DM call can be started and received, or the control is not shown.
- DM mute changes unread/notification emphasis.
- Long DM and server chats open at the latest message and do not force the user to
  scroll down after navigation.
- Right-click menus act on the correct target.
- No implemented path uses browser-native alert/confirm/prompt/context menu.
