# Stage 11 Baseline

Date: 2026-06-18

Stage 11 starts after Stage 10.29, where the Friends surface was changed to an
overlay-style layer model and the extra private-sidebar header band was removed.

## Required Reading

Read these files before Stage 11 implementation:

1. `DEVELOPMENT_PROMPT.md`
2. `AGENTS.md`
3. `PROJECT_CONTEXT.md`
4. `docs/implementation-plan.md`
5. `README.md`
6. `docs/README.md`
7. `docs/discord-stage-11-completion-plan.md`
8. The QA document for the current stage, when one exists

## Current Completed State

- Stage 10.29 is the current implementation baseline.
- Friends mode hides the workspace `topbar` and lets `FriendsHome` own the top row.
- The private sidebar no longer renders a pseudo 48 px header band on the Friends
  surface.
- Server rail active state is scoped to the current destination.
- Message timeline double-line issues were corrected for server text channels and
  DMs.
- Browser-native `alert`, `confirm`, and `prompt` usage was removed from clone-owned
  workflows.
- Bottom user and voice panels were rebuilt into raised-card controls.
- Voice media verification still depends on Chrome microphone and screen-capture
  permission.

## Remaining Risk Areas

- Global layer consistency is still fragile because many surfaces define borders,
  backgrounds, and z-index locally in `frontend/src/styles/base.css`.
- Friends, DM, server text, server voice, and settings surfaces have been polished
  independently and need one final global pass for density and hierarchy.
- Popovers, context menus, notices, and modals need another whole-app pass to ensure
  outside-click and Escape dismissal are consistent.
- Some visible actions remain local-only or deferred; Stage 11 must either wire,
  hide, or clearly classify them.
- Real microphone and screen-share flows need Chrome manual QA because the in-app
  browser may deny media permissions.

## Stage Classification

| Stage | Type | Main Verification |
| --- | --- | --- |
| 11.0 | Documentation and scope lock | `git diff --check`, secret scan |
| 11.1 | Frontend architecture/visual layer | Frontend lint/build, browser QA |
| 11.2 | Friends UI polish | Frontend lint/build, browser QA |
| 11.3 | DM UI and interaction polish | Frontend lint/build, browser QA |
| 11.4 | Server sidebar/navigation polish | Frontend lint/build, browser QA |
| 11.5 | Text channel timeline/composer polish | Frontend lint/build, backend tests if API changes |
| 11.6 | Bottom user/voice panel polish | Frontend lint/build, browser QA |
| 11.7 | Voice workspace polish | Frontend lint/build, Chrome media QA where available |
| 11.8 | Menus/popovers/modals | Frontend lint/build, native-dialog audit, browser QA |
| 11.9 | Feature exposure policy | Frontend lint/build, text/visibility scan |
| 11.10 | Backend/API completion | Backend tests/lint, Docker API smoke |
| 11.11 | Responsive/accessibility QA | Frontend lint/build, viewport browser QA |
| 11.12 | Real media QA | Chrome microphone/screen-share manual QA |
| 11.13 | Final visual pass | Frontend lint/build, cross-surface browser QA |
| 11.14 | Final regression/handoff | Full command suite, Docker smoke, browser QA |

## Stage 11.0 QA

Command verification:

- `git diff --check`: passed with CRLF normalization warnings only.
- Secret-pattern scan across `DEVELOPMENT_PROMPT.md`, `AGENTS.md`,
  `PROJECT_CONTEXT.md`, `README.md`, and `docs/`: passed with no matches.

Residual manual QA:

- No code or runtime behavior changes are part of Stage 11.0.
- Real media QA remains deferred to Stage 11.12 unless a stage changes voice or
  screen-share behavior earlier.
