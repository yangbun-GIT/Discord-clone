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
