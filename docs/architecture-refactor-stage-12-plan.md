# Stage 12 Architecture Refactor Plan

Stage 12 turns the latest architecture-principles audit into implementation
work. The goal is to reduce remaining SRP, DIP, DRY, encapsulation, and
testability gaps without changing user-facing Discord clone behavior.

## Process

Preserve the Stage 10 and Stage 11 process:

1. Work one stage at a time.
2. Read `DEVELOPMENT_PROMPT.md`, `AGENTS.md`, `PROJECT_CONTEXT.md`,
   `docs/implementation-plan.md`, `README.md`, `docs/README.md`,
   `docs/project-file-map.md`, `docs/structure-map/reference-map.md`, and this
   plan before implementation.
3. Identify the owning layer and target files before editing.
4. Keep each stage behavior-preserving unless the stage explicitly says
   otherwise.
5. Run verification for the touched surface before moving on.
6. Review the result for regressions, stale references, and missing docs.
7. If a new defect appears, add it as a current-stage subtask and fix it before
   advancing.
8. Update `PROJECT_CONTEXT.md`, `docs/architecture-principles-audit.md`,
   `docs/project-file-map.md`, and `docs/structure-map/reference-map.md` when
   responsibilities or dependencies change.
9. Run `git diff --check`.
10. Commit each completed stage with a short Korean commit title.
11. Push completed stages to `origin/main` unless the user explicitly says not to.

## Stage List

### Stage 12.0 Audit And Plan Lock

- Status: completed.
- Record the refreshed architecture audit and this implementation sequence.
- Add this plan to the documentation index and implementation roadmap.
- Verification: documentation diff review and `git diff --check`.

### Stage 12.1 App Voice Session Controller

- Status: completed.
- Move voice join, leave, cross-server switch confirmation, mute/deafen sync, and
  screen-share toggle orchestration out of `frontend/src/App.vue`.
- Add a focused `useVoiceSessionController.ts` facade that composes the existing
  guild store, gateway composable, RTC composable, and app notice/error callbacks.
- Keep the existing UI, modal, and gateway payload behavior unchanged.
- Verification: frontend lint and production build.

### Stage 12.2 Voice RTC Internal Modules

- Status: completed.
- Split `frontend/src/composables/useVoiceRtc.ts` internals into focused modules:
  media capture, local VAD, peer connection lifecycle, and screen-share helpers.
- Keep `useVoiceRtc.ts` as the public facade used by `App.vue` and Stage 12.1.
- Verification: frontend lint and production build.

### Stage 12.3 Guild Voice Presence Store Boundary

- Status: completed.
- Move connected voice guild/channel state and voice-state mutation helpers out of
  `frontend/src/stores/guilds.ts` into a focused voice-presence module or store.
- Keep existing component props and gateway event behavior stable.
- Verification: frontend lint and production build.

### Stage 12.4 DM Storage Provider Boundary

- Status: completed.
- Mirror the guild storage provider pattern for direct messages.
- Move PostgreSQL/demo branching out of `backend/app/services/dm_service.py`.
- Keep route contracts and demo fallback behavior unchanged.
- Verification: backend tests and backend lint.

### Stage 12.5 Guild Repository Query Movement

- Status: completed.
- Move channel, message, invite, role, and member SQL from
  `backend/app/repositories/guilds.py` into the existing domain-specific
  repository files.
- Keep compatibility imports and test behavior stable during the split.
- Verification: backend tests and backend lint.

### Stage 12.6 API Exception Mapping

- Introduce shared route exception helpers for `KeyError`, `PermissionError`, and
  `ValueError` mappings.
- Replace repeated mappings in guild, channel, and DM routes.
- Verification: backend tests and backend lint.

### Stage 12.7 Realtime Fan-Out DRY Pass

- Extract common Redis/local gateway subscription-sync behavior shared by
  `backend/app/realtime/publisher.py` and `backend/app/realtime/subscriber.py`.
- Keep `gateway_manager` facade behavior unchanged unless a later explicit stage
  replaces singleton access.
- Verification: backend tests and backend lint.

### Stage 12.8 Browser API Adapter Pass

- Wrap remaining scattered frontend browser APIs that affect testability, such as
  clipboard, localStorage voice-confirm preferences, and document-level listeners.
- Do not alter browser permission behavior for microphone or display capture in
  this stage.
- Verification: frontend lint and production build.

### Stage 12.9 CSS And I18n Split Plan

- Prepare the next visual-maintenance split by documenting concrete ownership for
  `frontend/src/styles/base.css` and `frontend/src/i18n/index.ts`.
- Only perform low-risk mechanical extraction when it does not threaten visual
  parity.
- Verification: frontend lint and production build if code moves; otherwise
  documentation verification.

### Stage 12.10 Final Architecture Regression

- Run frontend lint/build, backend tests/lint, `git diff --check`, and a final
  architecture-doc review.
- Record remaining external or intentionally deferred risks.
- Commit and push the final Stage 12 state.
