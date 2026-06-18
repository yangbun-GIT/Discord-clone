# Frontend CSS And I18n Ownership Plan

This document defines the next safe split points for
`frontend/src/styles/base.css` and `frontend/src/i18n/index.ts`. Stage 12.9 is a
planning stage, not a visual rewrite. Do not move large CSS or copy blocks unless
the target screen can be visually verified immediately after the move.

## Current Decision

- Keep `frontend/src/styles/base.css` and `frontend/src/i18n/index.ts` intact for
  the current Stage 12 completion pass.
- Treat both files as stable visual/copy baselines until the next UI feature or
  visual-parity pass creates a focused reason to split them.
- When splitting, move one ownership group at a time, run frontend lint/build, and
  perform browser visual smoke for the affected screen before continuing.

## CSS Ownership Targets

Future CSS extraction should use this ownership order:

1. `frontend/src/styles/tokens.css`
   - CSS custom properties for color, spacing, radius, borders, shadows, z-index,
     typography, and motion.
   - No component selectors.
2. `frontend/src/styles/layout.css`
   - Root app grid, server rail/sidebar/workspace columns, channel/content/member
     layout, responsive breakpoints, and shell-level overflow rules.
   - No component-specific button, row, card, or modal styling.
3. `frontend/src/styles/overlays.css`
   - App-owned menus, popovers, notices, modals, context menus, and layered panels.
   - Shared close-on-outside-click surfaces should live here.
4. `frontend/src/styles/chat.css`
   - Server text-channel and DM timelines, message rows, date dividers, composer,
     attachments, reactions, and message action affordances.
5. `frontend/src/styles/voice.css`
   - Voice sidebar rows, connected voice card, voice workspace, participant tiles,
     media state, speaking indicators, mute/deafen/screen-share controls, and voice
     diagnostics.
6. `frontend/src/styles/settings.css`
   - User settings shell, settings navigation, controls, sliders, switches, and
     accessibility preview surfaces.
7. `frontend/src/styles/store.css`
   - Deferred Store-like shop surfaces only if Store work resumes.

## I18n Ownership Targets

Future i18n extraction should use this ownership order:

1. `frontend/src/i18n/common.ts`
   - Shared labels, statuses, actions, empty states, errors, and accessibility text.
2. `frontend/src/i18n/shell.ts`
   - Server rail, sidebars, top bars, context menus, notices, and navigation copy.
3. `frontend/src/i18n/friends.ts`
   - Friends home, add friend, friend filters, friend rows, and activity panel copy.
4. `frontend/src/i18n/dms.ts`
   - DM sidebar, DM intro, DM timeline, and DM composer copy.
5. `frontend/src/i18n/guilds.ts`
   - Guild/channel sidebar, channel headers, text-channel timeline, member list,
     invites, roles, and admin copy.
6. `frontend/src/i18n/voice.ts`
   - Voice channels, connected voice card, voice workspace, media controls,
     voice-switch dialog, and WebRTC diagnostics copy.
7. `frontend/src/i18n/settings.ts`
   - Settings categories, panels, controls, accessibility sections, and logout copy.
8. `frontend/src/i18n/store.ts`
   - Deferred Store-like shop copy only if Store work resumes.

Each module should export a typed `Record<AppLanguage, ...>` or a flat key map
that can be composed by `frontend/src/i18n/index.ts`. Keep `index.ts` as the
public `useI18n()` facade until all call sites are migrated.

## Split Rules

- Move only one screen/domain group per commit.
- Do not rename translation keys during a mechanical move.
- Do not change CSS specificity and file order in the same commit unless the visual
  bug being fixed requires it.
- After a CSS move, compare the affected screen at desktop and mobile widths.
- After an i18n move, run a quick Korean/English toggle smoke for the affected
  screen.
- Update `PROJECT_CONTEXT.md`, `docs/project-file-map.md`, and
  `docs/structure-map/reference-map.md` whenever a real split lands.

## Deferred Risks

- `base.css` remains large and requires care when editing global selectors.
- `i18n/index.ts` remains large and can still grow if new features add copy without
  a domain module.
- Visual parity should take priority over mechanical file splitting.
