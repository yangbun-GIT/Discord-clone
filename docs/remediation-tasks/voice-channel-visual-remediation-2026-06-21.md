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

### VCV-4: Stage footer lacked input/output controls

- Location: `frontend/src/App.vue`, `frontend/src/styles/base.css`
- Current behavior: the voice-channel stage footer exposed screen share and leave
  actions only, so users had to move to the bottom-left user panel to change mute,
  deafen, input device, output device, volume, sensitivity, or RNNoise settings.
- Expected behavior: the active voice-channel stage should expose the same
  microphone and output controls directly in the bottom stage control bar, placed
  before screen share.
- Fix: the stage footer now renders microphone and output control clusters when
  connected. Each `^` trigger opens a clone-owned device popover that reuses the
  existing voice device settings state and closes on outside click or Escape.

### VCV-5: Screen-share layout did not adapt to tile count

- Location: `frontend/src/App.vue`, `frontend/src/styles/base.css`
- Current behavior: screen-share tiles and participant tiles were rendered as
  separate stacked grids, so a shared screen plus participants could create
  oversized rows, overlap-prone composition, and uneven panel sizing.
- Expected behavior: screen shares and voice participants should be measured as a
  single stage grid. The shared screen should become the primary tile while local
  and remote participants receive smaller but stable supporting tiles.
- Fix: `App.vue` now computes screen-share and participant tile counts and applies
  stage grid modifier classes. `base.css` uses those classes to switch between
  normal participant layout, screen-share primary layout, multi-participant
  supporting columns, and mobile single-column stacking.

### VCV-6: Multiple simultaneous screen shares could still overlap

- Location: `frontend/src/App.vue`, `frontend/src/styles/base.css`
- Current behavior: the first screen-share tile could span multiple rows, which
  worked for one share but broke when two users shared screens and a participant
  tile was also visible.
- Expected behavior: a voice workspace should render at most 9 visible stage
  tiles and choose a stable 1/2/3-column grid from the visible tile count so no
  tile overlaps or escapes the stage.
- Fix: `App.vue` now caps the voice workspace to 9 rendered tiles, prioritizing
  screen-share tiles and filling the remaining slots with local/remote
  participant tiles. `base.css` removes the screen-share row-span exception and
  applies explicit `voice-workspace-grid--count-1` through `--count-9` layouts.

### VCV-7: Stage grid count rules needed stricter Discord-like rows

- Location: `frontend/src/styles/base.css`, `frontend/src/composables/useVoiceRtc.ts`
- Current behavior: three visible tiles used a three-column row, and a browser
  refresh while screen sharing could close the peer connection before remote
  clients received a final screen-share-off signal.
- Expected behavior: one or two tiles should stay in a single horizontal row;
  three or four tiles should use a stable 2 by 2 grid; five through nine tiles
  should use a stable 3 by 3 grid. A refresh should stop local screen sharing,
  let voice auto-rejoin through existing reload recovery, and notify other
  participants that the shared screen ended as early as possible.
- Fix: `base.css` now defines explicit row and column rules for the requested
  1/2, 2x2, and 3x3 layouts, with narrower max widths to avoid stretched panels.
  `useVoiceRtc.disconnect()` broadcasts `screen_sharing: false` before closing
  peer connections so remote screens clear quickly when a sharing tab refreshes
  or leaves.

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
- Follow-up VCV-4 verification passed: `npm run lint:frontend`,
  `npm run test:frontend`, `npm --prefix frontend run build`,
  `npm run smoke:realtime:browser:https`, and `git diff --check` all passed.
- Follow-up VCV-5 verification passed: `npm run lint:frontend`,
  `npm run test:frontend`, `npm --prefix frontend run build`,
  `npm run smoke:realtime:browser:https`, and `git diff --check` passed. The
  smoke result kept one remote screen video, no duplicate remote sharing
  participant card, and zero browser errors.
- Follow-up VCV-6 verification passed: `npm run lint:frontend`,
  `npm run test:frontend`, `npm --prefix frontend run build`,
  `npm run smoke:realtime:browser:https`, and `git diff --check` passed. The
  browser smoke kept local and remote screen-share rendering healthy with no
  duplicate remote sharing participant card and zero browser errors. Docker HTTPS
  refresh should be run after this change so `https://localhost:5173/` and the
  Cloudflare tunnel origin receive the 9-tile grid update.
- Follow-up VCV-7 verification passed: `npm run lint:frontend`,
  `npm run test:frontend`, `npm --prefix frontend run build`,
  `npm run smoke:realtime:browser:https`, and `git diff --check` passed. The
  browser smoke reported `remoteScreenCleared: true`,
  `voiceAutoRejoinedAfterReload: true`, `voiceRejoinRecovered: true`, and
  `browserErrors: 0`, so refresh stops screen sharing while preserving voice
  recovery. Docker HTTPS refresh should be run after this change so
  `https://localhost:5173/` and the Cloudflare tunnel origin receive the exact
  1/2, 2x2, and 3x3 grid behavior.
