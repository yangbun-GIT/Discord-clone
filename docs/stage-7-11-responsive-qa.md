# Stage 7.11 Responsive QA

Date: 2026-06-03

## Scope

- Authenticated `@me` Friends shell through the Docker Compose frontend/backend.
- Desktop viewport: 1440 x 900.
- Mobile viewport: 390 x 844.
- Chrome headless screenshots captured through CDP after injecting a local dev
  session into `localStorage`.

## Results

- Desktop screenshot: `docs/qa-artifacts/stage-7-11-desktop.png`
  - `scrollWidth` 1440, `clientWidth` 1440.
  - No rendered alert nodes.
- Mobile screenshot: `docs/qa-artifacts/stage-7-11-mobile.png`
  - `scrollWidth` 390, `clientWidth` 390.
  - No rendered alert nodes.

## Fixes Applied

- Hide private and server channel sidebars below 900px so the workspace owns the
  second grid column.
- Constrain mobile app shell and workspace width to the viewport minus the server
  rail.
- Hide the gateway status pill below 620px.
- Collapse friend rows to one action button below 620px to avoid right-edge clipping.
- Keep Friends tabs horizontally scrollable on narrow widths.

## Residual Manual QA

- Full keyboard traversal across every modal and settings panel still benefits from a
  human pass in a visible browser.
- Real mobile browser testing remains external to this local desktop run.
