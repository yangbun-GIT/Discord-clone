# Server Settings And Text Chat Remediation - 2026-06-21

## Scope

This pass targets the active server workspace after the server rail work. It is
limited to server heading actions, server settings/leave/delete flows, and server
text-channel message usability.

## Findings And Fixes

### S1. Server heading menu only opened

- Location: `frontend/src/components/ChannelSidebar.vue`
- Current behavior: clicking the server heading `...` repeatedly only refreshed
  the open menu.
- Expected behavior: the button toggles the menu open and closed.
- Fix: `toggleServerMenu()` now flips `serverMenuOpen`, and outside click/Escape
  still dismiss the menu. A follow-up bug where clicking the SVG icon inside the
  `...` button closed the menu on `mousedown` and immediately reopened it on
  `click` was fixed by treating SVG targets as generic `Element` nodes for
  `closest()` checks.
- Verification: frontend build, frontend lint, and manual code review.

### S2. Server heading lacked a direct invite action

- Location: `frontend/src/components/ChannelSidebar.vue`
- Current behavior: invite was only inside the heading menu.
- Expected behavior: a compact invite icon appears next to `...` when invite
  permission is available.
- Fix: added a permission-aware invite icon button to the heading action cluster.
- Verification: frontend build and lint.

### S3. Server text chat used top-biased timeline behavior

- Location: `frontend/src/components/ChatView.vue`
- Current behavior: server text messages accumulated from the top and did not
  match the DM bottom-start pattern.
- Expected behavior: server text channels start from the bottom, keep new
  messages visible, and expose the jump-to-latest behavior through the existing
  scroll logic.
- Fix: wrapped message rows in `guild-thread-stack` and reused bottom-anchored
  list behavior.
- Verification: frontend tests, build, and lint.

### S4. Server messages did not distinguish authors clearly

- Location: `frontend/src/components/ChatView.vue`,
  `frontend/src/styles/base.css`
- Current behavior: alternating authors looked visually similar in active server
  text channels.
- Expected behavior: different authors remain left-aligned but gain enough visual
  separation to identify who sent which message.
- Fix: server message rows now use author accent variables and current-user row
  styling without changing message ownership semantics.
- Verification: frontend build and lint.

### S5. Server message time/date did not use persisted message timestamps

- Location: backend guild message repositories and `ChatView.vue`
- Current behavior: server message display used synthetic/static timeline dates.
- Expected behavior: server text messages use the persisted `created_at`
  timestamp, with Snowflake fallback only for legacy/demo messages without a
  timestamp.
- Fix: `MessageRead` now carries `created_at`; PostgreSQL/demo message create and
  list paths return it; `ChatView.vue` renders real per-message time and per-day
  dividers.
- Verification: backend tests, frontend tests, frontend build, backend lint.

### S6. Server leave/delete actions were missing

- Location: backend guild API/service/storage/repository/demo store,
  `frontend/src/stores/guildAdmin.ts`, `frontend/src/stores/guilds.ts`,
  `frontend/src/App.vue`, `frontend/src/components/ChannelSidebar.vue`
- Current behavior: users could not leave a server, and owners could not delete a
  server from the app UI.
- Expected behavior: non-owners can leave; owners can delete; actions use
  app-owned confirmation UI and remove the server from the local rail/workspace.
- Fix: added `DELETE /api/guilds/{guild_id}/leave` and
  `DELETE /api/guilds/{guild_id}`; wired store actions and UI confirmations.
- Verification: backend tests, backend lint, frontend build/lint/tests.

### S7. Server settings surface was missing

- Location: `frontend/src/components/ServerSettingsDialog.vue`, `App.vue`,
  `ChannelSidebar.vue`
- Current behavior: menu item existed but did not open a real server settings
  surface.
- Expected behavior: server settings opens an app-owned dialog with server
  summary, invite action, leave/delete actions based on ownership, and safe
  confirmation flows.
- Fix: added `ServerSettingsDialog.vue` and connected it from the heading menu and
  rail context-menu settings action.
- Verification: frontend build, frontend lint, and frontend tests.

## Validation

- `npm run lint:frontend`: passed.
- `npm run test:frontend`: 46 tests passed.
- `npm --prefix frontend run build`: passed.
- `npm run lint:backend`: passed.
- `npm run test:backend`: 148 tests passed.
- `npm run smoke:realtime:browser:https`: passed with `browserErrors: 0`.
- `git diff --check`: passed.

## Remaining Notes

- Server delete is intentionally owner-only. Non-owner users see leave actions
  instead.
- This pass does not implement a full Discord-like multi-tab server settings
  dashboard. The added settings dialog is the first functional settings surface
  needed for invite, leave, and delete workflows.
