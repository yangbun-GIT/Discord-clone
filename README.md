# Discord Clone

Zero-budget Discord clone based on the SRS provided for the project.

## Stack

- Backend: Python 3.14, FastAPI, asyncpg, Redis asyncio client, Pydantic v2
- Frontend: Vue 3, Vite, Pinia, Vue Router, Oxlint
- Realtime: Discord-style gateway opcodes over WebSocket
- Data model: PostgreSQL schema with JavaScript-safe Snowflake IDs and bitfield permissions

## Local Setup

Install frontend dependencies:

```powershell
npm --prefix frontend install
```

Install backend dependencies:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python -m pip install -e .\backend[dev]
```

Run the backend:

```powershell
npm run dev:backend
```

Run the frontend in another terminal:

```powershell
npm run dev:frontend
```

Open `http://127.0.0.1:5173`.

The frontend starts at the login/register screen when no saved session exists. Use
the Demo user button for the seeded local workspace.

## Docker Setup

Docker is optional for day-to-day development, but useful for onboarding, reproducible
runtime checks, and future VM deployment. The Compose stack includes local PostgreSQL
for persistence.

Run the full stack with Compose:

```powershell
npm run docker:up
```

Stop containers:

```powershell
npm run docker:down
```

`npm run docker:down` preserves the PostgreSQL volume. To reset local Docker data,
run `docker compose down -v`.

Docker exposes the same local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

Useful backend auth endpoints:

- `POST http://127.0.0.1:8000/api/auth/register`
- `POST http://127.0.0.1:8000/api/auth/login`
- `GET http://127.0.0.1:8000/api/auth/me`

Authenticated users can create a server from the `Create server` button. New servers
start with `general` and `voice-room` channels.

## Environment

Copy `.env.example` to `.env` and fill values as external services become available.
Native local development works without `DATABASE_URL` or `REDIS_URL`; it uses an
in-memory demo store while preserving the async connection-pool boundaries required
by the SRS. Docker Compose supplies its own local PostgreSQL URL automatically.

Messages and channels created in Docker mode persist in the local PostgreSQL volume.
Messages and channels created in native demo mode are kept in the running backend
process and reset when that process restarts.

## Verification

```powershell
npm run test:backend
npm run lint:backend
npm run lint:frontend
npm --prefix frontend run build
docker compose exec -T backend pytest
```
