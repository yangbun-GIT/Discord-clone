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

## Docker Setup

Docker is optional for day-to-day development, but useful for onboarding, reproducible
runtime checks, and future VM deployment.

Run the full stack with Compose:

```powershell
npm run docker:up
```

Stop containers:

```powershell
npm run docker:down
```

Docker exposes the same local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

## Environment

Copy `.env.example` to `.env` and fill values as external services become available.
Local development works without `DATABASE_URL` or `REDIS_URL`; the first stage uses
demo data while preserving the async connection-pool boundaries required by the SRS.

## Verification

```powershell
npm run test:backend
npm run lint:frontend
npm --prefix frontend run build
docker compose exec -T backend pytest
```
