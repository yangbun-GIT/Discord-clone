# Friend Relationship Implementation Plan

This document turns the current Add Friend gap into an implementation-ready
development plan. Read it before changing Friends, DM relationship, or user
relationship code.

## Current Status

Date: 2026-06-19.

The Friends surface currently has relationship reads and DM creation, but Add
Friend is not a real backend-backed workflow.

Implemented today:

- `GET /api/users/me/relationships` returns relationship rows for the current
  authenticated user.
- `frontend/src/stores/dms.ts` loads relationships and direct messages.
- `frontend/src/components/FriendsHome.vue` renders Friends tabs, pending rows,
  friend rows, and the Add Friend form.
- `FriendsHome.vue` emits `messageFriend`; `frontend/src/App.vue` creates or opens
  a DM through `dms.createDm(...)`.

Missing today:

- Sending a friend request to another user.
- Persisting outgoing and incoming pending relationships.
- Showing newly received pending requests to the target user without manual seed
  data.
- Accepting, rejecting, or cancelling friend requests.
- Blocking and unblocking users.
- Realtime relationship updates across two browser sessions.
- Tests proving user A sends a request and user B can accept or reject it.

Important current behavior:

- `FriendsHome.vue` currently sets `addFriendResult` locally and clears the input.
  It does not call a backend endpoint.
- `backend/app/api/routes/users.py` only exposes relationship reads.
- `backend/app/repositories/dms.py` owns PostgreSQL relationship reads, but not
  relationship mutations.
- `backend/app/demo/store.py` owns demo fallback relationship rows, but not real
  request lifecycle mutations.

## Product Scope

Goal: make the Friends page behave like a functional Discord-like relationship
workflow without adding low-value social-network features.

In scope:

- Add friend by exact username.
- Prevent self-friend requests.
- Prevent duplicate requests.
- Show outgoing and incoming pending requests.
- Accept incoming request.
- Reject incoming request.
- Cancel outgoing request.
- Remove friend.
- Block user.
- Unblock user from the Blocked tab.
- Realtime relationship refresh/update for both involved users.
- App-owned success/error notices, no browser-native alert/confirm/prompt.

Out of scope for the first pass:

- Username discriminator system.
- Friend suggestions.
- Contact import.
- Nitro, profile decoration, or social graph recommendations.
- Mobile push notifications.

## Data Model Plan

Use the existing directed `relationships` table as the first implementation path.
Keep one row per viewer-to-related-user state.

Recommended relationship row pairs:

| Action | Actor row | Target row |
| --- | --- | --- |
| Send request | `pending_outgoing` | `pending_incoming` |
| Accept request | `friend` | `friend` |
| Reject incoming | remove | remove |
| Cancel outgoing | remove | remove |
| Remove friend | remove | remove |
| Block user | `blocked` | remove or `blocked_by` if the schema is extended |
| Unblock user | remove | no-op |

First pass should avoid a schema migration if the current statuses are enough:
`friend`, `pending_incoming`, `pending_outgoing`, and `blocked`. Add `blocked_by`
only if the UI needs target-side visibility that cannot be represented safely with
the current union.

Repository invariants:

- Relationship rows are always symmetric where the product needs both users to see
  state.
- A user cannot create a relationship to self.
- Username lookup is case-insensitive but stores canonical username from the users
  table.
- Mutations are idempotent where practical:
  - Re-sending an existing outgoing request returns the existing outgoing state.
  - Accepting a request that is already a friend returns the friend state.
  - Cancelling or rejecting a missing request returns a clean not-found or no-op
    contract, selected deliberately and tested.
- DM creation remains separate. Accepting a friend request must not implicitly send
  a message.

## API Contract Plan

Add user relationship mutation endpoints under `backend/app/api/routes/users.py`.

Proposed endpoints:

- `GET /api/users/me/relationships`
  - Existing endpoint.
  - Keep response model `list[RelationshipRead]`.
- `POST /api/users/me/relationships/requests`
  - Body: `{ "username": "target-user" }`
  - Creates outgoing/incoming request pair.
  - Returns the actor's `RelationshipRead`.
- `POST /api/users/me/relationships/{user_id}/accept`
  - Accepts an incoming request.
  - Returns actor's `RelationshipRead` as `friend`.
- `POST /api/users/me/relationships/{user_id}/reject`
  - Rejects an incoming request.
  - Returns a small deletion/read result or `204`.
- `POST /api/users/me/relationships/{user_id}/cancel`
  - Cancels an outgoing request.
  - Returns a small deletion/read result or `204`.
- `DELETE /api/users/me/relationships/{user_id}`
  - Removes friend relationship.
  - Returns a small deletion/read result or `204`.
- `POST /api/users/me/relationships/{user_id}/block`
  - Blocks a user and removes incompatible friend/request rows.
  - Returns actor's `RelationshipRead` as `blocked`.
- `DELETE /api/users/me/relationships/{user_id}/block`
  - Unblocks a user.
  - Returns a small deletion/read result or `204`.

Response and error expectations:

- `401` when unauthenticated.
- `404` when target user is not found.
- `400` for self-request or invalid state transition.
- `409` for duplicate/incompatible state when a no-op return is not chosen.
- Never expose password hashes, tokens, or private DM contents.

## Backend Implementation Stages

### Stage F1: Schemas And Service Boundary

Owner files:

- `backend/app/schemas/dm.py`
- `backend/app/services/dm_service.py`
- `backend/app/services/dm_storage.py`
- `backend/app/api/routes/users.py`

Tasks:

1. Add request/response schemas for relationship mutations.
2. Add service functions:
   - send friend request.
   - accept request.
   - reject request.
   - cancel request.
   - remove friend.
   - block user.
   - unblock user.
3. Keep API route handlers thin and service-owned.
4. Keep async boundaries intact.

Acceptance:

- Route handlers perform auth, parse payload, call service, publish realtime
  notification, and return typed response.
- Business rules live in service/storage, not Vue components.

### Stage F2: PostgreSQL Repository Mutations

Owner files:

- `backend/app/repositories/dms.py`
- `backend/app/repositories/users.py`
- `backend/app/db/schema.sql` only if a schema change is necessary.
- `backend/tests/test_dm_repository.py`

Tasks:

1. Add case-insensitive username lookup or reuse `user_repository`.
2. Add relationship pair upsert/delete helpers.
3. Keep pair mutations transactional.
4. Add repository tests for send, accept, reject, cancel, remove, block, and
   unblock.

Acceptance:

- Request state is visible from both users' relationship lists.
- Invalid state transitions are deterministic and tested.
- Duplicate requests cannot create duplicate rows.

### Stage F3: Demo Store Fallback Mutations

Owner files:

- `backend/app/demo/store.py`
- `backend/app/services/dm_storage.py`
- `backend/tests/test_demo_store.py`

Tasks:

1. Mirror PostgreSQL relationship mutation behavior in the demo store.
2. Preserve seeded demo relationships.
3. Add fallback tests for the same state transitions.

Acceptance:

- Native no-database mode and Docker PostgreSQL mode behave consistently for
  relationship workflows.

### Stage F4: Relationship Realtime Fan-Out

Owner files:

- `backend/app/realtime/events.py`
- `backend/app/realtime/fanout.py`
- `backend/app/realtime/publisher.py`
- `backend/app/gateway/manager.py`
- `backend/app/gateway/broadcaster.py`
- `backend/tests/test_realtime_fanout.py`
- `backend/tests/test_gateway_manager.py`

Tasks:

1. Add a user-targeted gateway dispatch path or a relationship-specific fan-out
   contract.
2. Dispatch relationship updates to both actor and target users.
3. Proposed events:
   - `RELATIONSHIP_CREATE`
   - `RELATIONSHIP_UPDATE`
   - `RELATIONSHIP_DELETE`
4. Keep payloads limited to `RelationshipRead` or deletion identifiers.
5. Ensure Redis multi-worker fan-out can route relationship updates.

Acceptance:

- Two active sessions see pending/accepted/rejected/blocked changes without
  refresh.
- Redis cross-worker smoke can be extended to cover one relationship event.

### Stage F5: REST And Gateway Tests

Owner files:

- `backend/tests/test_api_routes.py`
- `backend/tests/test_dm_api.py` if DM route coverage is the better fit.
- `backend/tests/test_realtime_fanout.py`
- `scripts/realtime_browser_smoke.mjs` only after frontend support exists.

Tasks:

1. Test unauthenticated relationship mutation rejection.
2. Test send request by username.
3. Test target sees incoming request.
4. Test accept turns both rows into `friend`.
5. Test reject/cancel removes both pending rows.
6. Test block removes friend/request state.
7. Test blocked user cannot immediately create incompatible duplicate request.

Acceptance:

- Backend tests cover both success and invalid state transitions.
- Tests do not log passwords, tokens, or private DM contents.

## Frontend Implementation Stages

### Stage F6: API Client And Store

Owner files:

- `frontend/src/services/api.ts`
- `frontend/src/stores/dms.ts`
- `frontend/src/stores/dmGatewayHandlers.ts`
- `frontend/src/stores/gatewayIdempotency.test.ts`

Tasks:

1. Add API wrappers for all relationship mutation endpoints.
2. Add store actions for send, accept, reject, cancel, remove, block, and unblock.
3. Add relationship upsert/delete handling for gateway events.
4. Keep active DM and unread behavior unchanged.

Acceptance:

- Relationship store state updates from both REST responses and gateway events.
- Duplicate gateway events remain idempotent.

### Stage F7: Friends UI Wiring

Owner files:

- `frontend/src/components/FriendsHome.vue`
- `frontend/src/App.vue`
- `frontend/src/i18n/index.ts`
- `frontend/src/styles/base.css`

Tasks:

1. Replace local-only Add Friend result with a real submit event.
2. Show loading, success, and error states from store/API results.
3. Pending tab:
   - incoming rows show Accept and Reject.
   - outgoing rows show Cancel.
4. Friend rows:
   - show Remove Friend in local menu.
   - keep Message action only when relationship is `friend`.
5. Blocked tab:
   - show Unblock.
6. Keep controls accessible and app-owned.
7. Remove misleading local/demo wording.

Acceptance:

- Sending from account A immediately shows outgoing pending for A and incoming
  pending for B.
- Accepting on B turns both sides into friends.
- Reject/cancel removes pending rows from both sides.
- Block/unblock changes are visible and reversible.

### Stage F8: Browser QA And Real User Workflow

Owner files:

- `docs/realtime-communication-qa.md`
- `scripts/realtime_browser_smoke.mjs`
- `docs/remediation-tasks/friend-relationship-implementation-plan.md`

Tasks:

1. Extend browser smoke or add a separate relationship smoke:
   - create two temp dev sessions.
   - user A sends request to B.
   - user B sees incoming request.
   - user B accepts.
   - both users see friend state.
   - user A opens DM from the new friend row.
2. Add manual QA checklist for:
   - request send.
   - accept.
   - reject.
   - cancel.
   - remove friend.
   - block/unblock.
   - refresh/reconnect.

Acceptance:

- Same-PC two-browser smoke proves the full request-to-friend path.
- Manual QA does not require seeded demo-only relationships.

## Verification Checklist

Minimum command suite before marking the feature complete:

```powershell
npm run lint:backend
npm run test:backend
npm run lint:frontend
npm run test:frontend
npm --prefix frontend run build
npm run smoke:realtime:browser
npm run smoke:realtime:redis
git diff --check
```

Additional browser checks:

1. Login as two different users.
2. User A sends a friend request to user B by username.
3. User B sees the incoming request without refresh.
4. User B accepts.
5. Both users see each other in All/Online friends.
6. User A starts a DM from the friend row.
7. User B receives the DM message in realtime.
8. Repeat with reject, cancel, block, and unblock.

## Documentation Update Requirements

When implementing this plan, update:

- `PROJECT_CONTEXT.md`
- `docs/project-file-map.md`
- `docs/structure-map/reference-map.md`
- `docs/README.md`
- `docs/realtime-communication-qa.md` if smoke/manual QA changes.
- This document's stage status and verification notes.

## Current Open Decision

The main implementation decision is whether to keep the existing directed
`relationships` table with paired rows or introduce a canonical relationship table
with two user IDs and one status. Prefer the paired-row approach for the first pass
because it matches existing reads and avoids a migration unless duplicate-state
risks become difficult to control.
