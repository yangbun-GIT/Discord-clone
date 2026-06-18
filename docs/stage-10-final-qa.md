# Stage 10.18 Final QA

Date: 2026-06-18

Scope: final Stage 10 command, Docker, API, and browser workflow verification.

## Command Verification

- `npm --prefix frontend run build`: passed.
- `npm --prefix frontend run lint`: passed with 0 warnings and 0 errors.
- `npm run test:backend`: passed, 103 tests.
- `npm run lint:backend`: passed.

## Docker Smoke

- `docker compose ps`: backend, frontend, and PostgreSQL running; backend and
  PostgreSQL healthy.
- `GET http://localhost:8000/api/health`: `status=ok`, local environment,
  database configured and connected, Redis not configured.
- `GET http://localhost:5173/`: HTTP 200.

## Browser QA

Viewport: default in-app browser size after Stage 10.17 viewport reset.

- Friends home: no horizontal overflow, tabs rendered, lower-left voice panel
  stayed compact, and visible icon-only controls had labels.
- Add Friend: tab opened the add-friend form, no horizontal overflow, and visible
  icon-only controls had labels.
- Text channel: `SRS Lab / #architecture` rendered chat, 48 px composer, member
  list, header, lower-left voice panel, no horizontal overflow, and no label gaps.
- Voice channel preview: `voice-room` rendered the Discord-like preview workspace,
  join and screen-share controls, local preview tile, quiet empty participant tile,
  no horizontal overflow, and no remote screen-share overlay.
- Screen-share state before voice connection: both workspace and lower-left
  screen-share buttons stayed disabled with accessible labels.

## Residual Manual QA

- Attempting to join voice in the in-app browser returned `Permission denied` from
  browser media permissions. Because voice did not connect, connected voice and
  real screen-share start/stop still require a browser session with microphone and
  screen-capture permissions granted.
- Real multi-browser WebRTC quality and TURN/NAT verification remains external QA
  per `docs/voice-qa.md`.

## Stage 10.19 Follow-Up QA

Date: 2026-06-18

Scope: user feedback polish for Friends, private sidebar quick search, server menu,
voice row click behavior, disconnected voice panel visibility, invite modal, and
stuck notices.

Command verification:

- `npm --prefix frontend run build`: passed.
- `npm run lint:frontend`: passed.
- `npm run test:backend`: passed, 103 tests.
- `npm run lint:backend`: passed.
- `docker compose up -d --build frontend`: passed and refreshed the running
  frontend at `http://localhost:5173/`.

Browser QA:

- Friends home rendered primary tabs in the order All, Online, Pending, Add Friend;
  Blocked is no longer in the default tab row.
- Disconnected lower-left voice panel no longer renders the `voice-room` idle card.
- Private sidebar quick switcher opens from "Find or start a conversation" and closes
  on outside click.
- Friend more menu opens and closes on outside click.
- Server menu opens from the guild heading and closes on outside click.
- Voice channel row click moved to the voice workspace and attempted voice connection
  directly. The browser returned `Permission denied` for microphone access, so full
  connected media verification remains manual with microphone permission granted.

## Stage 10.20 Feedback Cleanup QA

Date: 2026-06-18

Scope: second user-feedback pass for friend/message density, lower-left user/voice
panel quality, app context menus, topbar cleanup, and voice state placement.

Command verification:

- `npm run lint` in `frontend/`: passed with 0 warnings and 0 errors.
- `npm run build` in `frontend/`: passed.
- `npm run test:backend`: passed, 103 tests.
- `npm run lint:backend`: passed.
- `docker compose up -d --build frontend`: passed and refreshed the running Docker
  frontend/backend containers.

Browser QA:

- Friends home: friend rows render at 72 px with one compact status/activity line
  and stronger row separation.
- Text channel: `.message-reactions` count is `0`; server message rows render with
  a top border, 13 px padding, and no `OK`/`+1` pills.
- Direct-message-compatible message styling: server and DM message rows now share
  the same `.message-row` separation rules.
- Lower-left user panel: renders as a raised card with a visible shadow and 128 px
  panel height; disconnected voice-room idle text is not shown.
- App right-click: right-clicking a message shows the app context menu with reply,
  copy, edit, and pin actions, and the browser context menu is suppressed.
- Outside click: clicking outside the context menu closes it.
- Server/channel context targets: server rail, DM rows, friend rows, text channels,
  voice channels, messages, and the user panel expose `data-context-kind` targets
  for app context menus.
- Topbar/voice placement: the visible topbar no longer renders the voice-location
  chip; voice connection indication is implemented on the server rail.

Residual manual QA:

- Voice join in the in-app browser returned `Permission denied`, so connected voice
  participant chips, server-rail voice badge visibility during a successful media
  session, and live speaking rings require manual QA in a browser session with
  microphone permission granted.

## Stage 10.21 Voice Sidebar Participant Stack QA

Date: 2026-06-18

Scope: focused follow-up for the server sidebar's connected voice-channel layout.

Command verification:

- `npm run lint` in `frontend/`: passed with 0 warnings and 0 errors.
- `npm run build` in `frontend/`: passed.

Code/design verification:

- A connected voice channel now renders as a compact header row, with participant
  and invite details in a separate lower stack instead of crowding inside the row.
- The lower stack order matches the user's Discord reference: channel status
  shortcut, dashed mood prompt, connected participants, and invite-to-voice action.
- Connected/speaking emphasis is scoped to the channel header/member row so the
  expanded block no longer becomes one large green selected card.

Residual manual QA:

- Successful voice-join visual QA still requires microphone permission in Chrome or
  another browser session where media permissions are granted.
