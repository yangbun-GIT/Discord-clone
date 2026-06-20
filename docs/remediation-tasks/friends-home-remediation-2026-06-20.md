# Friends Home Remediation - 2026-06-20

## Scope

Target surface: the private home Friends screen shown from `@me`.

This pass is not a decorative visual refresh. It focuses on errors, missing or
misleading behavior, inefficient flows, weak visibility, and usability gaps that
make the Friends screen harder to use.

## Findings

### FH-001 - Nonfunctional friend menu items appear as active controls

- Priority: P1
- Location: Friends list row `...` menu and global right-click menu for friends/DMs.
- Current behavior: `Start call`, `View profile`, and `Mute conversation` are shown
  as clickable actions, but they only close the menu or show a generic local-control
  notice.
- Expected behavior: visible active controls should either perform a real action or
  be removed from the active menu surface until implemented.
- User impact: users waste clicks on actions that appear complete but do nothing
  meaningful.
- Resolution direction: remove unsupported active actions from friend-specific menus
  and keep only wired actions: message, remove friend, block, unblock.
- Target files: `frontend/src/components/FriendsHome.vue`,
  `frontend/src/App.vue`, `frontend/src/i18n/index.ts`.
- Verification: inspect menus, run frontend lint/build, and confirm no friend menu
  item routes to a generic placeholder notice.

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
  entries were removed from friend menus and global friend/DM context menus.
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
