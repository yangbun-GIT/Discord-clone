# Stage 9 Final QA

Stage 9 focused on FHD 100% zoom visual parity against the user's real Discord
screenshots. Exact DevTools pixel extraction was not required; the implementation
uses conservative Discord-like proportions and hides low-value demo/developer text
from primary screens.

## Completed Scope

- Rebalanced global shell tokens, server rail shape, private/server sidebars,
  channel rows, top bar, member list, composer, and bottom voice panel.
- Added richer demo Friends/DM density so Friends and Add Friend screens no longer
  look empty during local QA.
- Added text-channel date dividers, attachment-style cards, reactions, and a clean
  empty-channel state.
- Hid low-frequency or admin-heavy controls by default, including visible clone-scope
  navigation and member role management controls.
- Improved voice channel rows, local voice members, bottom user avatar, and voice
  workspace tiles with speaking-state glow indicators.
- Added an in-workspace screen-share state tile and compacted the floating remote
  screen-share preview.
- Added dark scrollbar styling after browser QA found native light scrollbars in
  dense channel/message regions.

## Verification

- `npm --prefix frontend run build`: passed.
- `docker compose exec -T frontend npm run build`: passed.
- `docker compose exec -T backend pytest -q`: passed, 103 tests, 1 upstream
  `StarletteDeprecationWarning`.
- `git diff --check`: passed, with Windows CRLF normalization warnings only.
- Browser QA on `http://localhost:5173/`:
  - Demo login loaded successfully.
  - Friends Online view rendered with dense friend rows and profile panel.
  - Add Friend view rendered without text overlap.
  - Text channel view rendered header, message timeline, composer, and member list
    without overlap.
  - Voice channel preview rendered large participant tiles, clear join/share buttons,
    and bottom voice status controls.

## Residual Notes

- Existing local PostgreSQL volumes may contain older test-created channels. Those
  rows are valid functional data, but a fresh Docker volume will show the cleaner
  Stage 9 seed shape.
- Browser screenshots in the in-app browser occasionally showed a right-edge visual
  echo of the server rail. DOM inspection confirmed only one `.server-rail` exists
  and the app shell width matched the viewport, so this was treated as a capture
  artifact rather than an app layout defect.
