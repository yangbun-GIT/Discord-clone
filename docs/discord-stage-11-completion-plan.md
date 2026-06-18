# Discord Stage 11 Completion Plan

Stage 11 is the post-Stage 10 completion pass for making the clone feel like a
coherent Discord-style app rather than a collection of individually corrected
screens.

## Operating Process

Use the same process that governed Stage 10:

1. Read `DEVELOPMENT_PROMPT.md`, `AGENTS.md`, `PROJECT_CONTEXT.md`,
   `docs/implementation-plan.md`, `README.md`, `docs/README.md`, and this plan
   before starting a Stage 11 task.
2. Work one stage at a time. Do not merge unrelated Stage 11 work into the same
   implementation step unless the current stage explicitly depends on it.
3. After each stage, run the verification appropriate to the touched surface.
4. If verification or visual review finds a new defect, add it as a subtask under
   the current stage and resolve it before advancing.
5. Update `PROJECT_CONTEXT.md`, `docs/implementation-plan.md`, this plan, and the
   relevant QA document before committing.
6. Commit each completed stage with a short Korean commit title and push to
   `origin/main`.

## Quality Bar

- Prefer Discord-like layered composition over flat wireframe panels.
- Visible buttons should either perform useful local behavior or be hidden.
- Avoid demo/debug/diagnostic text on primary app surfaces.
- Keep surfaces dense but readable at FHD 100% zoom.
- Prevent text overlap, double borders, accidental browser-native dialogs, and
  Chrome context menus inside clone-owned app regions.
- Validate Korean and English labels where layout can be affected.
- Keep media permissions and real microphone/screen-share limitations explicit in
  QA notes.

## Stage 11.0: Baseline And Scope Lock

Goal: create a fresh baseline after Stage 10.29 so further work does not drift into
unrelated redesign.

Tasks:

- Record the current completed state and remaining risk areas.
- Classify each upcoming item as implementation, visual polish, interaction polish,
  backend/API, media QA, or final verification.
- Define the expected verification for each stage.
- Create `docs/stage-11-baseline.md` as the Stage 11 recovery point.

Verification:

- Documentation diff check.
- Secret scan over updated docs.
- Confirm working tree contains only Stage 11 documentation changes before commit.

## Stage 11.1: Global Layer System

Goal: make server rail, sidebars, workspace headers, content panes, popovers, and
bottom panels use one consistent layer model.

Status: completed. The global CSS layer tokens now own inline menus, popovers,
backdrops, modals, sticky overlays, reusable borders, and floating shadows. Stage
11.1 QA is recorded in `docs/stage-11-final-qa.md`.

Tasks:

- Audit current z-index, border, background, and grid-row usage in
  `frontend/src/styles/base.css`.
- Introduce or consolidate layer tokens for base shell, rail, sidebar, header,
  content, popover, modal, and floating menus.
- Remove screen-specific border hacks that create duplicate lines.
- Verify Friends, DM, server text, server voice, settings, and modal surfaces.

Verification:

- Frontend lint and production build.
- Browser QA for Friends, DM, server text, and voice screens.
- Confirm no horizontal overflow and no visible duplicate top/bottom seams.

## Stage 11.2: Friends Surface Finalization

Goal: make Friends home, Add Friend, friend rows, and activity panel feel complete
and Discord-like.

Status: completed. Friends tabs, row density, selected-row emphasis, right-side
activity card hierarchy, Add Friend copy, and hidden low-frequency Blocked tab
behavior were verified in `docs/stage-11-final-qa.md`.

Tasks:

- Re-check tab order, active states, search placement, row density, and right panel
  hierarchy.
- Tighten friend row spacing so status/activity text does not crowd adjacent rows.
- Ensure Add Friend has one clear input flow and no decorative dead zones.
- Confirm right-click and more-button menus dismiss reliably.

Verification:

- Frontend lint and production build.
- Browser QA for Online, All, Pending, Add Friend, friend context menu, and profile
  side panel.

## Stage 11.3: Direct Messages Surface Finalization

Goal: make DM list, DM profile intro, timeline, and composer usable as a primary
communication surface.

Status: completed. DM row density, selected-state affordance, intro spacing,
date-divider spacing, composer surface color, and group-DM copy were tightened.
QA evidence and browser automation limitation notes are in
`docs/stage-11-final-qa.md`.

Tasks:

- Refine DM list selected/unread/group states.
- Review DM intro spacing, date dividers, message grouping, and empty states.
- Ensure "Find or start a conversation" can open existing DMs and create a local
  DM flow without confusing dead controls.
- Verify DM composer, attachment/menu buttons, and send behavior.

Verification:

- Frontend lint and production build.
- Browser QA for DM search, DM open, DM send, timeline separators, and composer
  focus.

## Stage 11.4: Server Sidebar And Channel Navigation

Goal: make server/channel navigation predictable and visually aligned with Discord.

Tasks:

- Refine server heading, events row, text/voice category headers, and channel rows.
- Normalize active, hover, unread, voice-connected, and settings/action states.
- Keep invite, channel creation, and channel settings discoverable without visual
  clutter.
- Verify server switching does not leak active or connected state into another
  server.

Verification:

- Frontend lint and production build.
- Browser QA for server switch, text channel select, voice channel select/join,
  channel create, invite modal, and context menus.

## Stage 11.5: Text Channel Timeline And Composer

Goal: make message reading and writing feel clean in server text channels.

Tasks:

- Review message grouping, hover actions, attachments, reactions, and date dividers.
- Remove any remaining demo-only pills or confusing placeholders from the primary
  timeline.
- Keep composer height, button alignment, and input text vertically stable.
- Verify send/edit/delete/right-click actions where implemented.

Verification:

- Frontend lint and production build.
- Backend tests if API behavior changes.
- Browser QA for message send, message context menu, attachment cards, and composer
  overflow.

## Stage 11.6: Bottom User And Voice Panel

Goal: make the lower-left user card and connected voice panel feel like raised
Discord controls instead of fixed wireframe blocks.

Tasks:

- Normalize disconnected and connected lower-left panel heights.
- Keep the user status card aligned with the message composer on text surfaces.
- Verify mute, deafen, settings, screen-share, activity, and leave controls have
  stable spacing and clear states.
- Ensure connected voice state is owned by the connected guild/channel, not the
  currently selected server.

Verification:

- Frontend lint and production build.
- Browser QA for disconnected user card, connected voice card, cross-server switch
  dialog, and bottom-panel overflow.

## Stage 11.7: Voice Channel Workspace

Goal: make voice preview, connected voice, participant cards, speaking indicators,
and screen-share states feel coherent.

Tasks:

- Refine idle voice preview cards and connected participant layout.
- Keep speaking indicator visible around the active participant avatar/card.
- Ensure joining a voice channel by clicking the channel remains direct.
- Verify screen-share state transitions and disabled states.

Verification:

- Frontend lint and production build.
- Browser QA for idle voice workspace and disconnected controls.
- Chrome manual QA with microphone/screen-capture permission for connected media.

## Stage 11.8: App-Owned Menus, Popovers, And Modals

Goal: remove remaining browser-native or inconsistent interaction surfaces.

Tasks:

- Re-audit `alert`, `confirm`, `prompt`, browser context menus, and hidden dead
  controls.
- Normalize outside-click, Escape, close button, and focus behavior for popovers.
- Ensure context menus are target-aware for user, friend, server, channel, message,
  voice, and blank workspace targets.
- Keep clipboard and local-only actions routed through app notices.

Verification:

- Frontend lint and production build.
- `rg` audit for native dialogs.
- Browser QA for menus, popovers, notices, and outside-click dismissal.

## Stage 11.9: Feature Exposure Policy

Goal: make primary navigation show only useful clone features.

Tasks:

- Hide or clearly defer Nitro, Shop, Quests, commerce, app launcher, and other
  non-core Discord surfaces.
- Keep common actions such as DM search, server invite, channel create, message
  send, voice join, and settings visible.
- Re-check Korean and English text for confusing demo wording.

Verification:

- Frontend lint and production build.
- Browser QA for Friends, DM, server, voice, and settings primary navigation.
- Text scan for forbidden debug/demo terms on primary surfaces.

## Stage 11.10: Backend/API Completion Pass

Goal: ensure user-facing flows exposed by the frontend have reliable backend or
demo-store support.

Tasks:

- Audit relationship, DM, guild, channel, invite, message, member, and voice
  endpoints against the visible UI.
- Add focused PostgreSQL and demo-store tests where visible workflows depend on
  persistence.
- Keep async I/O, safe Snowflake IDs, permission bitfields, and schema-boundary
  validation intact.

Verification:

- Backend tests and backend lint.
- Frontend lint/build if contracts or API calls change.
- Docker API smoke and `/api/health`.

## Stage 11.11: Responsive And Accessibility QA

Goal: ensure the polished UI holds up across common viewport widths and keyboard
navigation.

Tasks:

- Verify FHD 100%, 1280 x 720, 900 px, and mobile-width layouts.
- Check no horizontal overflow, text overlap, clipped buttons, or broken fixed
  panels.
- Check aria labels, focus-visible styles, and non-drag alternatives for important
  controls.
- Verify Korean/English text expansion.

Verification:

- Frontend lint and production build.
- Browser screenshots/metrics for each viewport.
- Record results in a Stage 11 QA document.

## Stage 11.12: Real Media QA

Goal: separate browser-permission limitations from actual WebRTC issues.

Tasks:

- Run Chrome microphone-permission voice join QA.
- Run same-server and cross-server voice switch QA.
- Run screen-share start/stop QA where permission is available.
- Record unverified media paths explicitly if permissions are blocked.

Verification:

- Chrome manual media QA.
- Backend health and gateway smoke.
- Update `docs/voice-qa.md` if the media QA procedure changes.

## Stage 11.13: Final Visual Pass

Goal: remove the remaining visual roughness after the functional passes.

Tasks:

- Review colors, borders, shadows, radius, icon sizing, typography, density, and
  hover/active states globally.
- Compare against stored Discord reference screenshots and new user screenshots.
- Remove one-off CSS where tokens can express the same design.
- Confirm surfaces no longer read as wireframes.

Verification:

- Frontend lint and production build.
- Browser QA across Friends, DM, server text, voice, settings, modal, and context
  menu surfaces.

## Stage 11.14: Final Regression And Handoff

Goal: close Stage 11 with a reproducible verification and handoff state.

Tasks:

- Run frontend lint/build, backend tests/lint, Docker rebuild, API health, frontend
  HTTP smoke, and browser workflow QA.
- Update `PROJECT_CONTEXT.md`, `docs/implementation-plan.md`, this plan, final QA
  docs, and relevant task docs.
- Summarize remaining external/manual media risks.
- Commit and push the final Stage 11 state.

Verification:

- Full command suite.
- Docker smoke.
- Browser QA across core workflows.
- Clean Git working tree after push.
