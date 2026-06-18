# Stage 11 QA Log

This file records Stage 11 verification evidence. Each Stage 11 implementation
stage must append its command checks, browser checks, fixes, and residual risks
before the stage commit.

## Stage 11.1: Global Layer System

Date: 2026-06-18

Changes verified:

- Added global layer tokens in `frontend/src/styles/base.css` for inline menus,
  backdrops, sticky surfaces, popovers, menus, and modals.
- Added reusable app-surface, border, and floating-shadow tokens.
- Replaced remaining numeric `z-index` declarations in `base.css` with layer
  tokens.
- Normalized menu, popover, notice, modal, and screen-share floating surfaces to
  use the shared tokens.

Verification:

- `rg -n "z-index: [0-9]|--surface-app" frontend\src\styles\base.css`
  confirmed there are no remaining numeric `z-index` values and that
  `--surface-app` is defined before use.
- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `docker compose up -d --build frontend` rebuilt and restarted the development
  frontend stack successfully.
- Browser QA opened `http://localhost:5173/` and measured the Friends surface:
  horizontal overflow was `0`, the server rail and private sidebar remained
  full-height, and the runtime layer variables resolved to `45`, `60`, and `90`
  for popover, menu, and modal layers.

Residual notes:

- Stage 11.1 intentionally did not redesign screen composition. Friends, DM,
  server text, and voice surface finishing continues in later Stage 11 tasks.
