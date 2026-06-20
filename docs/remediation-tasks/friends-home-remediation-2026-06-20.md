# Friends Home Remediation - 2026-06-20

## Document Status

- Status: partial implementation record plus remaining Friends-home feature backlog.
- Source: user-provided Friends home screenshot and current clone behavior on the
  private `@me` Friends surface.
- Purpose: keep the Friends home usability defects, implementation-worthy missing
  features, fixes, verification evidence, and remaining manual QA gates in one
  place so the next screen pass does not rediscover the same control-policy issues.
- Update rule: if a later Friends/DM/sidebar change changes a finding outcome,
  update this document before committing.

## Scope

Target surface: the private home Friends screen shown from `@me`.

This pass is not a decorative visual refresh. It focuses on errors, missing or
misleading behavior, inefficient flows, weak visibility, and usability gaps that
make the Friends screen harder to use.

In scope:

- Friends header tabs, search, list rows, row actions, context menu behavior,
  Add Friend feedback, selected-friend activity panel, blocked-user access, and
  narrow viewport action reachability.
- Shared control policy where the Friends screen exposed active-looking controls
  through `App.vue` global context menus.
- Implementation-worthy missing Friends/private-home features, including friend
  profile popout, friend/DM call entry, conversation mute, target-aware friend/DM
  context menu actions, and start-new-DM from the private sidebar/search popover.
- Documentation repair when broken setup text directly affects the required project
  handoff path.

Out of scope for this pass:

- Cosmetic Discord pixel parity unrelated to usability.
- New friend suggestions or contact import.
- Backend relationship lifecycle redesign; the current backend-backed friend
  request, accept/reject/cancel, remove, block, and unblock flow is reused.
- Final DM conversation polish. DM-specific defects should move to the next DM
  remediation document.

## Document Adequacy Review

- The original finding list covered the visible Friends home issues from the
  screenshot and the code-level inactive-control gap, but it was too aggressive in
  classifying appropriate Discord-like features as temporary non-scope.
- This review corrects that direction: if a visible friend/private-home control
  represents normal Discord behavior, the document must either include an
  implementation stage or explicitly justify why it belongs to another screen plan.
- The current implementation results are still valid as a temporary quality gate:
  active-looking controls should not remain wired to fake notices. However, the
  Friends surface should not be considered feature-complete until FH-010 through
  FH-014 are implemented or deliberately moved to a more specific DM/voice plan.
- Future work should not reopen this document for broad server design work; open a
  separate screen-specific remediation document instead.

## Implementation Scope Recheck - 2026-06-20

The Friends home pass was rechecked after the user clarified that Discord-like
private-home features should be implemented when they are appropriate, not removed
from the product scope just because they were missing.

Implementation-worthy items that must remain in the Friends/private-home backlog:

- `View Profile`: implement an app-owned friend profile popout before restoring the
  action.
- `Start Call`: implement a real friend/DM call entry before restoring the action.
- `Mute Conversation`: implement a DM mute preference that affects unread or
  notification emphasis before restoring the action.
- `Start New DM`: implement the private sidebar `+` and quick-switcher create flow
  as a real recipient picker and DM open/create action.
- Friend/DM context menus: restore target-aware right-click actions only after the
  menu receives a real friend or DM target ID.

Items not treated as missing for this Friends screen pass:

- `Message Friend`: already routes through `handleMessageFriend(...)` and
  `dms.createDm(...)`.
- Friend request lifecycle: send, accept, reject, cancel, remove, block, and
  unblock are already backend-backed and remain regression targets.
- New friend suggestions/contact import: useful at larger scope, but not necessary
  for the current clone completion pass.
- Nitro, Store, and public discovery surfaces: intentionally outside the private
  Friends home workflow.

This means F10-F14 are not optional polish. They are the feature-completion stages
needed before the Friends home surface can be considered complete.

## Findings

### FH-001 - Nonfunctional friend menu items appear as active controls

- Priority: P1
- Location: Friends list row `...` menu and global right-click menu for friends/DMs.
- Current behavior: `Start call`, `View profile`, and `Mute conversation` are shown
  as clickable actions, but they only close the menu or show a generic local-control
  notice.
- Expected behavior: visible active controls should either perform a real action or
  be hidden only temporarily until the matching Discord-like feature is implemented.
- User impact: users waste clicks on actions that appear complete but do nothing
  meaningful.
- Resolution direction: remove unsupported active actions from friend-specific menus
  and keep only wired actions for this pass; create a follow-up implementation
  backlog for profile popout, friend call, and conversation mute before re-exposing
  those controls.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/App.vue`, `frontend/src/i18n/index.ts`.
- Verification: inspect menus, run frontend lint/build, and confirm no friend menu
  item routes to a generic placeholder notice.

### FH-010 - Friend profile popout should be implemented before restoring View Profile

- Priority: P1
- Location: Friends row menu, activity panel, and future target-aware context menu.
- Current behavior: `View profile` was removed from active menus because it had no
  behavior.
- Expected behavior: selecting a friend profile should open an app-owned profile
  popout/modal with username, handle, presence, activity, relationship action, and
  message entry.
- User impact: users expect to inspect a friend before messaging/removing/blocking.
- Resolution direction: implement a lightweight app-owned profile popout first;
  then restore the menu item as a real action.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/App.vue`, `frontend/src/styles/base.css`,
  `frontend/src/i18n/index.ts`.
- Verification: profile opens/closes with outside-click/Escape, has no browser
  native UI, and exposes only real relationship actions.

### FH-011 - Friend call should be implemented as a real DM call flow before restoring Start Call

- Priority: P1
- Location: Friends row menu and activity panel.
- Current behavior: `Start call` was removed from active menus because the app only
  has guild voice-channel calling, not a friend/DM call flow.
- Expected behavior: starting a call from a friend should create/open a DM context
  and start a private voice session or clearly route to a call-capable DM workflow.
- User impact: a Discord clone is expected to support direct call initiation, not
  only server voice channels.
- Resolution direction: design and implement a DM voice-call transport on top of
  the existing voice transport boundary, or explicitly map friend call to a
  private call room with the same mute/deafen/screen-share controls. Do not restore
  the menu item until the call can actually connect.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/components/DirectMessageView.vue`,
  `frontend/src/composables/useVoiceSessionController.ts`,
  `frontend/src/composables/useVoiceRtc.ts`,
  `backend/app/gateway/voice_service.py`, and related gateway/API routing if a
  DM voice room is added.
- Verification: two users can start and receive a friend call, join, mute/deafen,
  leave, refresh/rejoin where supported, and the existing guild voice flow remains
  unchanged.

### FH-012 - Conversation mute should be implemented before restoring Mute Conversation

- Priority: P2
- Location: Friends row menu, DM row menu, and DM notification/unread behavior.
- Current behavior: `Mute conversation` was removed from active menus because there
  is no persisted or local preference affecting notifications/unread state.
- Expected behavior: muting a DM should suppress notification/unread emphasis for
  that conversation while still allowing messages to arrive.
- User impact: users expect to reduce noise from a specific conversation without
  blocking the friend.
- Resolution direction: add a local preference or persisted DM mute state, reflect
  it in the DM list and message-receive handling, then restore the menu action as a
  toggle.
- Target files: `frontend/src/stores/dms.ts`,
  `frontend/src/stores/preferences.ts` or backend DM preference storage if
  persisted, `frontend/src/components/PrivateChannelSidebar.vue`,
  `frontend/src/components/FriendsHome.vue`, and `frontend/src/i18n/index.ts`.
- Verification: muted DMs still receive messages but do not show normal unread
  emphasis; unmuting restores unread behavior.

### FH-013 - Private sidebar Start New DM control should open a real recipient picker

- Priority: P1
- Location: private sidebar `+` button and quick switcher `Start a new direct
  message` action.
- Current behavior: the `createDm` event routes to `handleOpenFriends`, so the
  control appears to start a new DM but effectively returns to the Friends home.
- Expected behavior: selecting the `+` button or quick-create action should open an
  app-owned recipient picker/search using accepted friends and valid users, then
  create/open the DM.
- User impact: users cannot start a new conversation from the sidebar where the UI
  suggests they can.
- Resolution direction: implement a `CreateDmDialog` or private-sidebar popover
  that searches accepted friends at minimum, creates/opens the DM through
  `dms.createDm(...)`, and shows app-owned validation/error feedback.
- Target files: `frontend/src/components/PrivateChannelSidebar.vue`,
  `frontend/src/App.vue`, `frontend/src/stores/dms.ts`,
  `frontend/src/i18n/index.ts`, `frontend/src/styles/base.css`.
- Verification: the sidebar `+` and quick switcher create action both open the
  picker, selected friend creates/opens a DM, duplicate one-to-one DMs reuse the
  existing thread, Escape/outside-click closes the picker, and no browser-native UI
  is used.

### FH-014 - Friend/DM global context menus should be target-aware before actions return

- Priority: P2
- Location: global right-click menu for friend rows and DM rows.
- Current behavior: global context menu items for friend/DM rows were removed
  because `App.vue` receives only a label/kind, not the target friend or DM ID.
- Expected behavior: right-clicking a friend or DM should open app-owned actions
  for the exact target once the target ID is available.
- User impact: users expect right-click actions to work consistently across friend
  rows, DM rows, and selected friend cards.
- Resolution direction: add `data-context-id` or a typed context payload so
  `App.vue` can route message, profile, call, mute, remove, block, and unblock to
  the correct target. Restore only actions implemented by FH-010 through FH-013.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/components/PrivateChannelSidebar.vue`,
  `frontend/src/App.vue`, `frontend/src/styles/base.css`,
  `frontend/src/i18n/index.ts`.
- Verification: right-click friend/DM menus perform the same real actions as the
  visible row menu and never fall back to generic local-control notices.

### FH-002 - Add Friend result feedback is not local to the Add Friend panel

- Priority: P1
- Location: Friends `Add Friend` tab.
- Current behavior: the panel sets a local "sending" message, while success/failure
  is only shown through the global workspace notice/error surface.
- Expected behavior: the Add Friend panel should show the current request result
  directly where the user submitted the request.
- User impact: users can miss whether the request succeeded, failed, or is still
  pending.
- Resolution direction: pass relationship mutation notice/error into
  `FriendsHome.vue` and render success/error feedback in the Add Friend panel.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/App.vue`, `frontend/src/styles/base.css`.
- Verification: submit disabled/empty states remain intact; success/error copy is
  visible in the Add Friend panel.

### FH-003 - Friend tab counts and request grouping are not visible enough

- Priority: P2
- Location: Friends top tabs and list heading.
- Current behavior: counts are only shown in the list heading, while tabs do not
  show whether there are online friends or pending requests.
- Expected behavior: high-value tab state should be visible before opening the tab.
- User impact: users must click tabs to discover if there are online friends or
  pending requests.
- Resolution direction: add compact counts to All, Online, and Friend Request tabs;
  keep incoming/outgoing request grouping inside the pending view.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/styles/base.css`.
- Verification: counts match the filtered relationships and remain readable on
  desktop/mobile.

### FH-004 - Search empty state does not distinguish no data from no result

- Priority: P2
- Location: Friends search and list empty state.
- Current behavior: search with no result uses the same generic empty copy as an
  empty relationship list.
- Expected behavior: search should state that no matching users were found.
- User impact: users cannot tell whether there are no friends or only no matching
  results.
- Resolution direction: add a query-aware empty message.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/i18n/index.ts`.
- Verification: empty unfiltered list and empty filtered search show different
  messages.

### FH-005 - Current activity panel overstates activity for offline/no-activity users

- Priority: P2
- Location: Right `현재 활동 중` panel.
- Current behavior: the selected profile card appears under "Active Now" even when
  the selected friend is offline or has no activity.
- Expected behavior: the panel should make it clear whether the selected friend is
  active, online without activity, or offline.
- User impact: the panel can imply activity that does not exist.
- Resolution direction: keep the selected-friend card, but render a clear
  activity/status line and no-activity copy.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/i18n/index.ts`.
- Verification: offline friends display offline/no-activity text instead of an
  ambiguous activity card.

### FH-006 - Mobile Friends rows hide the only overflow menu

- Priority: P1
- Location: Friends list at narrow viewport widths.
- Current behavior: the last row button is hidden under `max-width: 620px`; for
  normal friends that removes access to remove/block actions.
- Expected behavior: mobile users must still have access to row actions.
- User impact: accepted friends cannot be managed on small screens.
- Resolution direction: keep the overflow menu visible on mobile and adjust row grid
  sizing to prevent text/action overlap.
- Target files: `frontend/src/styles/base.css`.
- Verification: mobile CSS keeps at least the overflow action available.

### FH-007 - Friend row action visibility depends too heavily on hover

- Priority: P3
- Location: Friends list rows.
- Current behavior: row action buttons are invisible until hover/focus/selected.
- Expected behavior: selected row and keyboard focus should expose actions, while
  default rows still reveal available actions through a stable affordance on
  touch-oriented layouts.
- User impact: discoverability is weaker on touch or non-hover environments.
- Resolution direction: make overflow/action controls visible on selected rows and
  at narrow widths, with labels retained for assistive technology.
- Target files: `frontend/src/styles/base.css`.
- Verification: selected row and mobile row controls are visible and keyboard
  reachable.

### FH-008 - Blocked relationships exist but have no visible route back

- Priority: P1
- Location: Friends tab state.
- Current behavior: `blocked` is a supported relationship state and unblock is
  implemented, but the header does not expose a blocked view.
- Expected behavior: blocked users should be reachable when blocked rows exist so
  users can review or unblock them.
- User impact: users can block someone but cannot easily find the unblock route.
- Resolution direction: show a compact Blocked tab only when blocked relationships
  exist.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/i18n/index.ts`.
- Verification: blocked count appears only when there are blocked relationships and
  the unblock row action remains available.

### FH-009 - README Korean quick-start section is mojibake in repository text

- Priority: P2
- Location: `README.md`.
- Current behavior: the Korean quick-start section added in the previous pass is
  stored as mojibake text.
- Expected behavior: project startup instructions should be readable Korean because
  they are part of the required handoff path.
- User impact: future work and local execution handoff are slower and error-prone.
- Resolution direction: replace the corrupted Korean quick-start block with valid
  UTF-8 Korean text while preserving the existing English sections.
- Target files: `README.md`.
- Verification: read the top README section using UTF-8 and run `git diff --check`.

## Stage Plan

- F1: Friends tab/filter/search state.
- F2: Friend row and context menu actionable controls.
- F3: Add Friend request feedback and request visibility.
- F4: DM entry from friend rows/activity panel.
- F5: Current activity panel copy and state clarity.
- F6: Unsupported visible controls removal.
- F7: Presence/status display regression check.
- F8: Accessibility and keyboard/focus check.
- F9: Responsive/narrow viewport row action check.
- F10: Friend profile popout implementation and `View Profile` restoration.
- F11: Friend/DM call entry design and implementation.
- F12: Conversation mute preference and unread/notification behavior.
- F13: Private sidebar `Start New DM` recipient picker implementation.
- F14: Target-aware friend/DM global context menu restoration.

## Acceptance Criteria

- No Friends home visible control is left as an enabled placeholder action.
- Friend row actions perform wired behavior; if hidden temporarily, the matching
  implementation stage must remain in this document and block Friends final
  completion until implemented or explicitly reassigned.
- Add Friend displays request progress and success/error feedback in the Add Friend
  panel itself.
- All/Online/Pending counts are visible before opening the tab.
- Blocked users are reachable when blocked relationships exist.
- Search empty state clearly means "no matching result", not "no friends".
- The activity panel does not imply that an offline/no-activity user is active.
- Narrow viewport Friends rows still expose the management overflow menu.
- App-owned menus and notices remain in use; browser-native alert/confirm/prompt or
  default context menus are not introduced.
- Normal Discord-like private-home features are not treated as permanently
  out-of-scope merely because they were previously unimplemented.
- Existing realtime, DM, voice, and local submission smoke paths still pass.

## Stage Results

- F1 completed: Friends tabs now show All, Online, and pending request counts; the
  blocked view appears only when blocked users exist.
- F2 completed: friend row actions are grouped into a stable action cluster so
  pending rows with multiple actions do not overflow the grid.
- F3 completed: Add Friend request feedback now appears inside the Add Friend panel
  with sending, success, and error tones.
- F4 completed: DM entry remains wired from friend rows and the activity panel.
- F5 completed: the activity panel now shows a clear offline/no-activity message
  instead of implying activity for every selected friend.
- F6 completed: nonfunctional Start Call, View Profile, and Mute Conversation
  entries were removed from friend menus and global friend/DM context menus as a
  temporary inactive-control cleanup. They are now tracked as implementation-worthy
  follow-up features in FH-010 through FH-012 and should be restored only after
  they perform real clone-owned behavior.
- F7 completed: presence updates continue to flow through the existing
  relationship-only `PRESENCE_UPDATE` path; this pass did not reintroduce DM row
  presence repainting.
- F8 completed: actionable controls retain accessible labels, unsupported
  controls are no longer exposed as active menu items, and menu dismissal still uses
  app-owned outside-click/Escape behavior.
- F9 completed: narrow Friends rows keep the overflow action reachable instead of
  hiding the only management route.
- FH-009 completed: the README Korean quick-start block was restored as readable
  UTF-8 Korean.
- F10 pending: profile popout is implementation-worthy and must be built before
  `View Profile` returns.
- F11 pending: friend/DM call entry is implementation-worthy and must be designed
  against the current guild voice transport before `Start Call` returns.
- F12 pending: conversation mute is implementation-worthy and must affect DM
  unread/notification behavior before `Mute Conversation` returns.
- F13 pending: the private sidebar `+` and quick-create action must open a real
  start-DM picker instead of routing back to Friends.
- F14 pending: friend/DM global context menus need target IDs before real actions
  can be restored there.

## Verification Log

- `npm run lint:frontend` passed.
- `npm run test:frontend` passed: 7 files, 46 tests.
- `npm --prefix frontend run build` passed.
- `npm run check:submission:local` passed against `https://localhost:5173/`;
  TURN remained false, which is acceptable for local submission readiness.
- `npm run smoke:realtime:browser:https` passed with `browserErrors: 0`, one
  remote audio sink, DM/server realtime, invite-DM realtime, screen-share cleanup,
  and voice reload/rejoin recovery.
- `git diff --check` passed after final whitespace cleanup.

## Manual QA Checklist

Run this when visually checking the Friends screen after future changes:

1. Open Friends home at desktop width and confirm All/Online/Friend Requests counts
   match visible data.
2. Search for an existing friend and a non-existing friend; confirm the no-result
   copy is specific to search.
3. Send a valid friend request from Add Friend and confirm panel-local success
   feedback appears.
4. Try an invalid or duplicate friend request and confirm panel-local error feedback
   appears.
5. Right-click a friend row and confirm only implemented actions are shown.
6. Use the row `...` menu and confirm message/remove/block/unblock behavior is
   available according to relationship state.
7. Block a friend, confirm the Blocked tab appears, then unblock from that tab.
8. Select an offline friend and confirm the activity panel clearly says offline or
   no current activity.
9. Resize below `620px` and confirm the row overflow action remains visible and
   usable.
10. Press Escape/outside-click on open menus and confirm app-owned overlays close.

Feature-completion QA to run after F10-F14:

1. Open a friend profile from the row menu and activity panel; confirm the popout is
   target-correct and dismissible.
2. Start a friend/DM call from Friends; confirm the recipient can join and the guild
   voice flow is not broken.
3. Mute and unmute a DM conversation; confirm muted conversations still receive
   messages but do not show normal unread emphasis.
4. Use the private sidebar `+` and quick switcher create action to create/open a DM.
5. Right-click friend and DM rows; confirm each menu item acts on the correct
   target and no generic local-control notice appears.

## Residual Risks And Next Screen Handoff

- The Friends screen now removes inactive friend-call/profile/mute controls only as
  a temporary quality gate. They are appropriate Discord-clone features and should
  be implemented by F10-F12 before being re-exposed as active controls.
- The global context menu intentionally returns no items for friend and DM rows
  because it does not receive target IDs. This is not final behavior; F14 must add
  target-aware context metadata before friend/DM context actions return.
- DM-specific conversation polish remains outside this document: DM message
  timeline clarity and full conversation layout should be covered by the next DM
  screen remediation pass. However, start-new-DM, conversation mute, and friend/DM
  call entry are private-home/Friends-adjacent enough to remain tracked here.
- Final visual parity is not complete; this pass only fixes usability and
  inactive-control defects on the Friends surface while adding F10-F14 as the
  missing feature-completion backlog.
