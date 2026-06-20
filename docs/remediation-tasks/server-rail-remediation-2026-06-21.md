# Server Rail Remediation - 2026-06-21

## Scope

This pass implements Discord-like server rail usability:

- User-controlled server order.
- User-controlled server folders/groups.
- App-owned hover/focus tooltips for rail buttons.

The work must preserve existing server selection, Home navigation, Create Server,
Server Discovery, unread/mention badges, muted state, and voice-connected state.

## Current State

- `frontend/src/components/ServerRail.vue` renders Home, server buttons, optional
  folder groups, Create Server, and Discovery.
- `frontend/src/App.vue` provides `ServerRailGuildMeta`.
- The current folder path is display-only and depends on `folder_name` metadata.
  Newly created servers are intentionally top-level after the latest server-add
  fix.
- There is no user-driven drag/drop ordering, no persistent user rail layout, and
  no custom tooltip UI.

## Target Data Model

The rail layout is user-specific and stored separately from guild membership.

```ts
type ServerRailLayout = {
  items: Array<
    | { type: 'guild'; guild_id: number }
    | { type: 'folder'; folder_id: string }
  >
  folders: Array<{
    id: string
    name: string
    color: string | null
    collapsed: boolean
    guild_ids: number[]
  }>
}
```

Reasoning:

- `items` preserves top-level order, including mixed folder and guild positions.
- `folders[].guild_ids` preserves server order inside a folder.
- New guilds append as top-level items if they are missing from the saved layout.
- Unknown guild IDs are ignored when rendering.

## Problems And Acceptance Criteria

### SR-01: Server Order Cannot Be Changed

- Location: far-left server rail.
- Current behavior: server order follows loaded guild order.
- Expected behavior: user can drag a server to another rail position and the
  order survives refresh.
- Target files:
  - `frontend/src/components/ServerRail.vue`
  - `frontend/src/stores/guilds.ts`
  - `backend/app/api/routes/users.py`
  - `backend/app/services/user_settings_service.py`
  - `backend/app/repositories/user_settings.py`
  - `backend/app/db/schema.sql`
- Verification:
  - Drag server A below server B.
  - Refresh.
  - Confirm order is preserved for the same user.

### SR-02: Server Grouping Is Display-Only

- Location: far-left server rail.
- Current behavior: folders can be rendered only from supplied metadata; users
  cannot create or edit them.
- Expected behavior:
  - Dragging one server onto another creates a folder.
  - Dragging a server onto a folder adds it to that folder.
  - Dragging a server out to the rail removes it from the folder.
  - Folder contents keep their own order.
  - Folders can be collapsed and expanded.
- Verification:
  - Create a folder by dropping one server onto another.
  - Add another server to the folder.
  - Reorder inside the folder.
  - Drag a server out of the folder.
  - Refresh and confirm the layout remains.

### SR-03: Rail Uses Browser Tooltips

- Location: Home, server, folder, create, and discovery rail buttons.
- Current behavior: many controls rely on native `title` tooltip behavior.
- Expected behavior:
  - Custom app-owned tooltip appears to the right of the rail on hover/focus.
  - Tooltip closes on pointer leave/blur.
  - Tooltip does not break keyboard focus or accessible labels.
- Verification:
  - Hover/focus Home, a server, a folder, Create Server, and Discovery.
  - Confirm tooltip is visible, positioned right of the rail, and not clipped.

## Stage Plan

### Stage SR1 - Persistent Layout API

1. Add backend schemas and route for `GET/PUT /api/users/me/server-rail`.
2. Add PostgreSQL table and repository.
3. Add demo-store fallback.
4. Add frontend API wrappers and guild store state/actions.

### Stage SR2 - ServerRail Layout Rendering

1. Replace display-only `folder_name` grouping with normalized
   `ServerRailLayout`.
2. Preserve missing/new guilds as top-level items.
3. Preserve existing badges and voice indicators.

### Stage SR3 - Drag/Drop Order And Grouping

1. Add drag source state.
2. Add guild-to-guild folder creation.
3. Add guild-to-folder insertion.
4. Add drag-out-to-rail behavior.
5. Persist layout after each successful operation.

### Stage SR4 - Folder Collapse And Tooltip

1. Add folder collapse/expand.
2. Add custom rail tooltip.
3. Keep keyboard focus labels and aria state.

### Stage SR5 - Verification And Docs

1. Run frontend lint/test/build where possible.
2. Run backend tests where possible.
3. Run `git diff --check`.
4. Update `PROJECT_CONTEXT.md`, `docs/project-file-map.md`, and
   `docs/structure-map/reference-map.md`.

## Completion Log

- Implemented persistent user-specific rail layout storage through
  `GET/PUT /api/users/me/server-rail`.
- Added PostgreSQL persistence in `user_server_rail_layouts` plus demo-store
  fallback so local/demo mode keeps the same API contract.
- Reworked `frontend/src/components/ServerRail.vue` to render normalized mixed
  guild/folder layout data, preserve unread/mention/voice indicators, support
  server drag reorder, guild-to-guild folder creation, guild-to-folder insertion,
  drag-out-to-rail behavior, and folder collapse/expand.
- Added app-owned hover/focus rail tooltips for Home, guilds, folders, Create
  Server, and Discovery.
- Added API/store wiring in `frontend/src/services/api.ts`,
  `frontend/src/stores/guilds.ts`, and `frontend/src/App.vue`.
- Added backend API regression coverage in `backend/tests/test_api_routes.py`.
- Verification:
  - `npm run lint:frontend` passed.
  - `npm run test:frontend` passed.
  - `npm --prefix frontend run build` passed.
  - `npm run test:backend` passed.
  - `npm run smoke:realtime:browser:https` passed.
  - `git diff --check` passed.

## Follow-Up Polish - 2026-06-21

- Fixed the drag preview so server/folder dragging shows an icon-sized preview
  instead of visually grabbing the whole rail slot.
- Replaced folder text initials with an icon-only folder affordance to avoid
  misaligned group text.
- Moved rail tooltips to a body-level teleport so Home, server, folder, add, and
  discovery tooltip UI is not clipped by the rail/sidebar stacking context.
- Added collapsed-folder aggregate active/unread/mention markers so the left rail
  marker behavior stays consistent after servers are moved into or out of groups.
- Localized `ServerDiscoveryDialog.vue` through `i18n/index.ts` so the public
  server exploration dialog follows the current Korean/English preference.
- Verification:
  - `npm run lint:frontend` passed.
  - `npm run test:frontend` passed.
  - `npm --prefix frontend run build` passed.
  - `npm run smoke:realtime:browser:https` passed.
  - `git diff --check` passed.
  - `npm run docker:up:https:detached` rebuilt and restarted the local HTTPS
    stack.
  - `curl.exe -k https://localhost:5173/api/health` returned healthy backend/DB
    status.
  - `curl.exe -k https://localhost:5173/api/meta/voice/readiness` returned STUN
    configured and TURN not configured, matching current local demo state.

## Residual Notes

- Drag-and-drop is the primary edit path. Keyboard/focus users receive accessible
  labels and tooltips, but a full non-drag reorder command menu remains a future
  accessibility enhancement if server-folder editing expands further.
