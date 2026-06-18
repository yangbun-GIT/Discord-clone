# Stage 10.17 Responsive And Accessibility QA

Date: 2026-06-18

Scope: responsive layout and accessibility checks for the Stage 10 cleaned Discord
clone shell.

## Viewport Checks

Artifacts:

- `docs/qa-artifacts/stage-10-17-fhd.png`
- `docs/qa-artifacts/stage-10-17-side-by-side.png`
- `docs/qa-artifacts/stage-10-17-tablet.png`
- `docs/qa-artifacts/stage-10-17-mobile.png`

Results:

| Viewport | Size | Result |
| --- | ---: | --- |
| FHD desktop | 1920 x 1080 | No horizontal body overflow. Rail 72 px, sidebar 300 px, workspace 1548 px, lower-left voice panel 300 x 102 px. |
| Side-by-side desktop | 1280 x 720 | No horizontal body overflow. Rail 72 px, sidebar 300 px, workspace 908 px, lower-left voice panel 300 x 102 px. |
| Tablet-like | 900 x 720 | No horizontal body overflow. Sidebar is hidden by responsive CSS, workspace/voice panel use remaining 836 px. |
| Mobile | 390 x 844 | No horizontal body overflow. Rail compacts to 56 px, sidebar remains hidden, workspace/voice panel use remaining 334 px. |

## Text Channel Check

- Server text channel layout at 1280 x 720 had no horizontal body overflow.
- Channel sidebar stayed 300 px wide.
- Header stayed 48 px high.
- Chat view measured 644 px wide with a 48 px composer.
- Member list stayed 264 px wide.
- Visible icon-only buttons with no text/aria/title labels: `0`.

## Focus And Labels

- Static focusable DOM order follows the expected shell hierarchy: server rail,
  channel/private sidebar, workspace controls, then lower-left voice controls.
- The first keyboard-focused rail button showed a visible 2 px solid focus outline.
- Visible icon-only buttons had either `aria-label` or `title`.

## Limitation

The in-app browser keypress bridge kept repeated `Tab` presses on the first rail
button during this run, so dynamic keyboard traversal was not treated as reliable
evidence. Static focusable order, focus styling, and accessible labels were checked
instead.
