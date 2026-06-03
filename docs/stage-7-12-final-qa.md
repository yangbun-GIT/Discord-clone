# Stage 7.12 Final QA

Stage 7.12 closes the core Discord app parity slice documented in
`docs/discord-app-clone-implementation-plan.md`.

## Command Verification

Run from the repository root on 2026-06-03:

- `npm run test:backend`
  - Result: passed, 103 tests.
- `npm run lint:backend`
  - Result: passed.
- `npm run lint:frontend`
  - Result: passed.
- `npm --prefix frontend run build`
  - Result: passed.
- `docker compose exec -T backend pytest`
  - Result: passed, 103 tests.

## Docker Smoke

Docker Compose services were running with local PostgreSQL:

- `postgres`: healthy.
- `backend`: healthy.
- `frontend`: reachable.

Smoke endpoints:

- `http://localhost:8000/api/health`
  - Result: `database.configured=true`, `database.connected=true`.
- `http://localhost:5173/`
  - Result: reachable.
- Authenticated development session plus REST smoke:
  - `GET /api/users/me/relationships`: returned 5 demo relationships.
  - `GET /api/dms`: returned 3 demo DM threads.
  - `POST /api/dms/801/messages`: created a persisted DM message.

Note: on this Windows/Docker setup, `localhost:8000` was the reliable Docker health
target during smoke verification.

## Browser Smoke

Headless Chrome was driven through the Chrome DevTools Protocol against
`http://localhost:5173` with a local development session.

Passed workflow:

- Restore demo login and open `@me`.
- Switch Friends tabs: All, Pending, Blocked, Add Friend, Online.
- Open a DM and send a message.
- Open a server.
- Switch to a voice channel.
- Switch back to a text channel and verify chat visibility.
- Open and close user settings.
- Create a server.
- Create an invite.
- Exercise the join-server modal with that invite code.
- Log out and verify auth reset state.

Desktop viewport metrics during the final browser smoke:

- `scrollWidth`: 1440.
- `clientWidth`: 1440.
- Alerts: none.

## Residual External QA

- Real TURN-backed voice calls across separate networks still require an external
  TURN provider and at least two real browser sessions.
- Production HTTPS/WebSocket behavior still requires the chosen deployment target.
- Full Discord-depth settings, moderation, trust/safety, and mobile app parity remain
  outside the completed Stage 7.12 scope.
