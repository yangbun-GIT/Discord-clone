# Discord Clone Engineering Notes

## Project Shape

- `backend/` contains the FastAPI ASGI service.
- `frontend/` contains the Vue 3 + Vite client.
- `docs/` contains project planning and architecture notes derived from the SRS.

## Backend Rules

- Keep all I/O async. Database, Redis, and external HTTP calls must be awaited.
- Reuse process-level connection pools created during FastAPI lifespan startup.
- Keep Snowflake IDs inside JavaScript's safe integer range.
- Represent permissions as integer bitfields and check them with bitwise operations.
- Validate and sanitize all client payloads at the schema boundary.
- WebSocket gateway payloads use Discord-style `op`, `d`, `s`, and `t` fields.

## Frontend Rules

- Use Vue 3 Composition API and `<script setup>` for all components.
- Use Pinia for global session and guild state.
- Use `shallowRef` for large message collections or immutable API result sets.
- Build the usable app screen first; do not add marketing or landing pages.
- Keep controls accessible, with visible focus styles and non-drag alternatives.

## Dependency Notes

- The SRS asks for Pydantic v3, but the current PyPI release line is Pydantic v2.
  The backend pins to Pydantic v2 while keeping schema code isolated for a future
  upgrade.

