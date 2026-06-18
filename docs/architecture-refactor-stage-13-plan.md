# Stage 13 Architecture Maintenance Completion Plan

Stage 13 is the final maintenance-focused architecture pass before returning to
feature implementation. The scope is behavior-preserving unless a listed subtask
explicitly says otherwise.

## Goal

Close the remaining principle and pattern gaps found in the 2026-06-19
whole-project re-audit, then leave the project ready for feature work without
reopening broad maintenance.

## Process

Use the Stage 10 through Stage 12 process:

1. Work one stage at a time.
2. Read startup context and this plan before editing.
3. Keep each stage focused on one ownership boundary.
4. After each stage, run verification appropriate to the touched surface.
5. If a defect is found, add it under the current stage and fix it before moving
   on.
6. Update `PROJECT_CONTEXT.md`, `docs/project-file-map.md`,
   `docs/structure-map/reference-map.md`, and this plan when ownership changes.
7. Run `git diff --check`.
8. Commit completed work with a short Korean commit title and push to
   `origin/main`.

## Stage 13.0: Scope Lock And Final Re-Audit

- Status: completed.
- Record the final maintenance scope in this document.
- Refresh `docs/architecture-principles-audit.md` with the latest re-audit.
- Confirm no browser-native alert/confirm/prompt flows remain in clone code.
- Include new maintainability candidates found during the final check:
  frontend visual-noise filtering inside stores, missing frontend logic tests, and
  PostgreSQL DM demo seed logic inside the DM repository.

Verification:

- `rg -n "confirm\\(|alert\\(|window\\.prompt" frontend/src backend/app`
- `git diff --check`

## Stage 13.1: DM Store Boundary Split

- Status: completed.
- Keep `frontend/src/stores/dms.ts` as the public Pinia facade.
- Move DM API mutations/loaders into a focused module.
- Move DM gateway event validation/application into a focused module.
- Move DM visual filtering out of the store into a focused visibility policy
  module.
- Preserve existing public store methods and state names so components do not need
  feature changes.

Verification:

- `npm run lint:frontend`
- `npm --prefix frontend run build`

## Stage 13.2: Guild Store Visual Policy Split

- Status: completed.
- Move guild visual-test filtering out of `frontend/src/stores/guilds.ts`.
- Keep store behavior unchanged while making the filtering policy reusable and
  testable.

Verification:

- `npm run lint:frontend`
- `npm --prefix frontend run build`

## Stage 13.3: Frontend Unit Test Harness

- Status: completed.
- Add a minimal Vitest setup for frontend logic tests.
- Add focused tests for data visibility and DM gateway handling.
- Avoid browser media tests in this pass; WebRTC permission flows still require
  manual browser QA.

Verification:

- `npm --prefix frontend run test`
- `npm run lint:frontend`
- `npm --prefix frontend run build`

## Stage 13.4: Backend DM Seed Boundary

- Status: completed.
- Move PostgreSQL DM demo seed/bootstrap helpers out of
  `backend/app/repositories/dms.py` into a dedicated repository support module.
- Keep repository public behavior unchanged.

Verification:

- `npm run lint:backend`
- `npm run test:backend`

## Stage 13.5: Storage Interface Segregation Review

- Status: completed.
- Review `backend/app/services/guild_storage.py`.
- If low-risk, split the broad protocol into smaller protocol groups while keeping
  `get_guild_storage()` as the service-facing compatibility provider.
- If not low-risk, document why it should remain deferred to feature-driven work.

Verification:

- `npm run lint:backend`
- `npm run test:backend`

## Stage 13.6: CSS And I18n Boundary Decision

- Status: completed.
- Keep visual parity stable.
- Do not mechanically split thousands of CSS/i18n lines if the change cannot be
  visually verified in a focused way.
- Ensure the ownership plan and file maps are current so feature work can split
  styles/copy by screen when needed.
- Decision: physical CSS/i18n splitting remains deferred because this pass has no
  focused visual or copy feature that can constrain browser QA. The ownership plan
  remains the source of truth for future feature-driven splits.

Verification:

- `npm run lint:frontend`
- `npm --prefix frontend run build`

## Stage 13.7: Final Maintenance Gate

- Status: completed.
- Run full command verification.
- Update `PROJECT_CONTEXT.md`, `docs/README.md`, `docs/project-file-map.md`,
  `docs/structure-map/reference-map.md`, and
  `docs/architecture-principles-audit.md`.
- Confirm remaining risks are feature-driven rather than maintenance blockers.

Verification:

- `npm --prefix frontend run test`
- `npm run lint:frontend`
- `npm --prefix frontend run build`
- `npm run lint:backend`
- `npm run test:backend`
- `git diff --check`

## Completion Criteria

Stage 13 is complete when:

- DM store responsibilities are split.
- Guild/DM visual filtering is outside the stores.
- Frontend logic has focused automated tests.
- Backend DM seed/bootstrap behavior is outside the DM repository.
- CSS/i18n ownership docs are current and intentionally deferred until a visual or
  copy feature pass needs them.
- Full verification passes.
- The final architecture audit states that no maintenance-only blocker remains
  before feature implementation.
