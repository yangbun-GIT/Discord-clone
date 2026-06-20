# Voice Channel Visual Remediation - 2026-06-21

## Scope

The user compared the current clone voice-channel workspace with a real Discord
voice-channel screenshot and asked to improve the default voice screen layout,
composition, element sizing, and visual hierarchy based on Discord's stage-like
voice workspace.

This pass is intentionally visual and usability focused. It must preserve the
existing WebRTC, gateway signaling, mute/deafen, screen-share, invite, and bottom
voice-panel behavior.

## Problems

### VCV-1: Voice workspace looked like a small two-card preview

- Location: `frontend/src/App.vue`, `frontend/src/styles/base.css`
- Current behavior: local participant and empty participant tiles were rendered as
  compact cards near the top of a mostly empty black workspace.
- Expected behavior: voice channel should feel like a large Discord-style stage,
  with participant tiles centered in the available space and scaled for FHD
  desktop view.
- Fix: `App.vue` now wraps voice content in `voice-workspace-stage`; `base.css`
  uses large responsive tiles, centered stage padding, and darker stage framing.

### VCV-2: Primary voice controls were attached to the header

- Location: `frontend/src/App.vue`, `frontend/src/styles/base.css`
- Current behavior: Join/Leave and screen-share controls lived in the top-right
  header, which did not match Discord's voice workspace control pattern.
- Expected behavior: controls should sit in a compact floating control bar near
  the bottom center of the voice stage.
- Fix: Join, screen-share, and leave controls now render through
  `voice-stage-controls` inside the stage while reusing the existing handlers.

### VCV-3: Empty participant state lacked Discord-like structure

- Location: `frontend/src/App.vue`, `frontend/src/styles/base.css`,
  `frontend/src/i18n/index.ts`
- Current behavior: empty state was a small dashed card with only text.
- Expected behavior: empty state should occupy a comparable stage tile, provide a
  useful next action, and avoid active fake controls.
- Fix: empty state now renders as a large activity-style tile with a real invite
  action when the user can create invites, and a disabled activity selection action
  to avoid implying unsupported functionality is implemented.

## Verification Plan

- `npm run lint:frontend`
- `npm run test:frontend`
- `npm --prefix frontend run build`
- `git diff --check`
- Rebuild/restart the HTTPS Docker frontend so `https://localhost:5173/` reflects
  the updated voice workspace.

## Result

- Completed.
- `npm run lint:frontend` passed.
- `npm run test:frontend` passed with 7 files and 46 tests.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:browser:https` passed with `browserErrors: 0`, one
  remote audio sink, screen-share preview/remote rendering, reload recovery, and
  voice leave cleanup.
- `git diff --check` passed with line-ending warnings only.
