# Stage 8 Responsive And Accessibility QA

Stage 8.13 verifies the Stage 8 UI remediation work at desktop and mobile widths and
records keyboard/accessibility findings before final Stage 8 verification.

## Commands

```powershell
npm run lint:frontend
npm --prefix frontend run build
docker compose up --build -d frontend
```

All commands passed on 2026-06-04.

## Screenshot Artifacts

- Desktop, 1366 x 900: `docs/qa-artifacts/stage-8-13-desktop.png`
- Mobile, 390 x 844: `docs/qa-artifacts/stage-8-13-mobile.png`

## Overflow Metrics

| Viewport | Client | Scroll | Horizontal Overflow | Notes |
| --- | --- | --- | --- | --- |
| Desktop | 1366 x 900 | 1366 x 900 | No | Private sidebar visible; member list hidden on Friends home. |
| Mobile | 390 x 844 | 390 x 844 | No | Private/channel sidebars hidden by responsive rules. |

## Keyboard And Accessibility Notes

- The first Tab stops traverse the server rail, private sidebar search, Friends row,
  clone-scope row, DM creation, DM rows, and topbar logout without trapping focus.
- Visible focus styles are defined globally for buttons, inputs, and selects and
  locally for rail, sidebar, message, composer, settings, and modal controls in
  `frontend/src/styles/base.css`.
- `ServerRail.vue` was corrected during QA so `aria-current="page"` is only applied
  to the active server when the user is not on the Direct Messages/Friends home.
  The rail may still visually retain the last selected server, but screen-reader
  current-page state is unique.
- Major structural areas expose labels through `aria-label`, `aria-labelledby`, or
  visible text: server rail, private sidebar, Friends home tabs, DM view, chat view,
  composer, voice panel, settings, and add/discovery modals.

## Residual Manual Checks

- Browser automation in this environment can be inconsistent for synthesized mouse
  events after Docker rebuilds. The Stage 8.13 checks used CDP viewport, screenshot,
  DOM, and keyboard-event inspection. Full human keyboard passes through every modal
  and settings panel should be repeated if those surfaces change again.
- Real screen-reader output was not run; this QA verifies DOM labels and focus order,
  not spoken announcements.
