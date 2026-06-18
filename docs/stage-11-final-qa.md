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

## Stage 11.2: Friends Surface Finalization

Date: 2026-06-18

Changes verified:

- Friends header title now reads as a clear header item with an icon, while the
  tabs remain visually distinct buttons.
- Friends tab order is `All`, `Online`, `Pending`, and `Add Friend`; the low-value
  `Blocked` tab remains hidden from the default primary tab row.
- Friend rows use stronger card-like spacing, 78 px row height, larger avatar/action
  columns, clearer selected-row emphasis, and additional vertical separation for
  status/activity text.
- The right activity panel uses a clearer card hierarchy and primary message action.
- Add Friend removes demo wording from the primary user-facing copy and uses a
  raised panel with one focused input flow.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `docker compose up -d --build frontend` rebuilt and restarted the development
  frontend stack successfully.
- Browser QA on `http://localhost:5173/` measured horizontal overflow as `0`,
  confirmed visible tab labels are `모두`, `온라인`, `대기 중`, `친구 추가`, confirmed
  the `차단됨` tab is not visible, and measured the first three friend rows at
  78 px height.

Residual notes:

- The Friends local more/context menu behavior was not intentionally changed in
  this stage. The global menu/popover audit remains assigned to Stage 11.8.

## Stage 11.3: Direct Messages Surface Finalization

Date: 2026-06-18

Changes verified:

- DM sidebar rows now use 56 px height, larger avatar columns, explicit transparent
  borders for stable active/hover states, and clearer copy spacing.
- DM intro sections now have a larger avatar, stronger bottom separation, and more
  stable spacing before the timeline date divider.
- DM composer background was aligned with the raised composer surface used by other
  message views.
- Group DM copy no longer calls the conversation a demo conversation.
- The DM emoji picker set was normalized to common emoji choices.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `docker compose up -d --build frontend` rebuilt and restarted the development
  frontend stack successfully.
- Browser static QA on `http://localhost:5173/` measured horizontal overflow as
  `0` and the first visible DM sidebar rows at 56 px height.

Residual notes:

- The in-app browser execution context rejected standard synthetic click event
  creation during this run, so automatic DM-open/send interaction QA could not be
  completed. The affected code paths remain compile-verified and are scheduled for
  broader menu/composer verification in later Stage 11 QA.

## Stage 11.4: Server Sidebar And Channel Navigation

Date: 2026-06-18

Changes verified:

- Server rail now uses the shared rail surface color and a clearer non-active
  voice-connected background.
- Guild heading uses the sidebar surface with a subtle bottom shadow so it reads as
  part of the layered sidebar rather than a disconnected strip.
- Events and channel rows gained more stable padding and row height.
- Category create buttons remain discoverable at reduced opacity instead of being
  fully hidden until hover.
- Text/voice channel rows now reserve a transparent border for stable hover/active
  states, show active/connected actions without layout shift, and use cleaner
  voice-detail spacing.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `docker compose up -d --build frontend` rebuilt and restarted the development
  frontend stack successfully.
- Browser static QA on `http://localhost:5173/` confirmed horizontal overflow is
  `0`, the server rail is 72 px wide, and the visible rail slots remain 56 x 48 px.

Residual notes:

- Automated server-switch and channel-click QA was limited by the same in-app
  browser synthetic-event restriction observed in Stage 11.3. The server/channel
  interaction code path was not changed in this stage; visual and state styling
  changes are compile-verified and will be covered again in final manual/browser QA.

## Stage 11.5: Text Channel Timeline And Composer

Date: 2026-06-18

Changes verified:

- Removed fake PDF attachment cards from the primary text-channel timeline so
  messages no longer show unrelated demo files.
- Replaced `:ok:`/`:+1:` style composer emoji entries with common emoji choices.
- Date dividers now render only when the channel has messages.
- File selection labels use an ASCII separator for stable display.
- Composer helper panels no longer use "demo" wording and now use the neutral
  raised panel surface.
- Message row spacing and empty-channel spacing were tightened.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `docker compose up -d --build frontend` rebuilt and restarted the development
  frontend stack successfully.
- Browser static QA on `http://localhost:5173/` confirmed horizontal overflow is
  `0` and no visible `Team Project#1.pdf`, `Mid-fi prototyping`, `18.0_Evaluation`,
  `:ok:`, or `:+1:` text is present in the current DOM.

Residual notes:

- Direct server text-channel click/send automation remains limited by the in-app
  browser synthetic-event restriction noted in Stage 11.3 and 11.4. The text
  timeline and composer code paths are compile-verified.

## Stage 11.6: Bottom User And Voice Panel

Date: 2026-06-18

Changes verified:

- Disconnected and connected voice-panel padding now use the same spacing model.
- The lower-left user card uses a darker raised surface with steadier internal
  gaps, keeping the identity area and action cluster separated.
- Disabled user action buttons now render as disabled controls instead of looking
  active.
- Connected voice cards gained matching horizontal padding for consistent raised
  card composition.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `docker compose up -d --build frontend` rebuilt and restarted the development
  frontend stack successfully.
- Browser QA on `http://localhost:5173/` measured horizontal overflow as `0`, the
  disconnected voice panel at 68 px height, the lower-left user card at 48 px
  height, and one disabled user action button while disconnected.

Residual notes:

- Connected media-state QA still depends on a browser session with microphone
  permission granted. The connected panel styling is compile-verified and will be
  covered again in Stage 11.7 and final media QA.

## Stage 11.7: Voice Channel Workspace

Date: 2026-06-18

Changes verified:

- Voice workspace now uses a layered dark surface with a clearer header/status
  divider and a live-status dot on the channel icon.
- Participant tiles use tighter responsive columns, steadier card elevation, and
  less empty vertical space.
- Connected and speaking states now have stronger borders and a visible speaking
  ring around both the card and avatar.
- Screen-share preview cards use the same card family with clearer icon/text
  alignment.

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `docker compose up -d --build frontend` rebuilt and restarted the development
  frontend stack successfully.
- Browser static QA on `http://localhost:5173/` confirmed horizontal overflow is
  `0` and the bundled `.voice-workspace-grid` CSS is present after reload.

Residual notes:

- The active browser view was not already inside a voice workspace, so the
  workspace DOM was not visible during this static pass. Interactive voice entry
  and screen-share transitions still require the final media QA pass with browser
  microphone/screen-capture permission granted.
