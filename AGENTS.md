# Discord Clone Engineering Notes

## Project Shape

- `backend/` contains the FastAPI ASGI service.
- `frontend/` contains the Vue 3 + Vite client.
- `docs/` contains project planning and architecture notes derived from the SRS.

## Context Recovery Rules

- Before starting implementation, read `DEVELOPMENT_PROMPT.md`, `AGENTS.md`,
  `PROJECT_CONTEXT.md`, `docs/implementation-plan.md`, `README.md`, and
  `docs/README.md`, then use `docs/project-file-map.md` and
  `docs/structure-map/reference-map.md` for path and dependency routing.
- Treat `DEVELOPMENT_PROMPT.md` as the project-specific development prompt:
  operating role, verification policy, documentation policy, security policy, and
  collaboration policy.
- Treat `docs/README.md` as the document index for task-specific docs.
- Treat `docs/GITHUB_COLLABORATION_WORKFLOW.md` as the Git staging, commit, push,
  and final-report workflow.
- Treat `docs/PROMPT_COMPLIANCE.md` as the audit map for checking whether the
  repository structure still reflects `DEVELOPMENT_PROMPT.md`.
- Treat `PROJECT_CONTEXT.md` as the current implementation map: file ownership,
  integration points, commands, known decisions, and next work.
- Use `docs/project-file-map.md` as the quick path map for locating likely owner
  files before broad code exploration.
- For cross-file changes, read `docs/structure-map/reference-map.md` before broad
  recursive searches so dependencies and reverse references are checked first.
- After meaningful code or policy changes, update `PROJECT_CONTEXT.md` and any
  relevant files in `docs/` before committing.
- When folders or important source-file responsibilities change, update
  `docs/project-file-map.md` before committing.
- When core file dependencies change, update
  `docs/structure-map/reference-map.md` before committing.
- Keep documentation factual and concise. Prefer concrete file paths and live
  integration details over broad summaries.
- Continue committing and pushing completed stages to `origin/main` unless the user
  explicitly asks not to.

## Efficiency Rules

- Use `docs/project-file-map.md` and `docs/structure-map/reference-map.md` to narrow
  target files before broad exploration.
- Prefer `rg` scoped to likely owner folders over full-repository recursive scans.
- Parallelize independent file reads with `multi_tool_use.parallel`.
- Keep stage scope tied to the mapped owner files; if scope expands, document the
  new owner path before continuing.

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
