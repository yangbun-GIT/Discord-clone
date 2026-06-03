# Discord UI Remediation Plan

This is the controlling plan for the post-Stage 7 Discord app polish work. Future
implementation should read this document before editing UI, interaction, i18n,
settings, voice, or placeholder-button behavior.

The reference material is the user's Discord screenshots and the structural routes:

- `https://discord.com/channels`
- `https://discord.com/channels/@me`
- `https://discord.com/channels/@me/{dm_id}`
- `https://discord.com/channels/{guild_id}/{text_channel_id}`
- `https://discord.com/channels/{guild_id}/{voice_channel_id}`

Do not copy personal names, messages, server names, avatars, or private content from
reference screenshots into fixtures, seed data, documentation, or UI copy. Use only
layout structure, navigation patterns, status affordances, and interaction behavior.

## Product Direction

Stage 8 is not a feature-count expansion. It is a reliability and fidelity pass for
the already-functional Discord-like app surface:

- The UI should feel clean and stable at the first screen.
- Text must not overlap in sidebars, headers, forms, empty states, settings, or
  composer controls.
- Buttons that are visible must either work, open a useful local panel, or clearly
  identify a demo-only unavailable feature.
- The user should always be able to tell where they are: `@me`, a DM, a server text
  channel, a server voice channel, or settings.
- Voice state should be obvious: disconnected, connecting, connected, muted,
  deafened, speaking, and screen sharing.
- Korean and English should be supported through a real frontend i18n layer.

## Priority Rules

- P0: Fix layout, text overlap, status visibility, broken affordances, and state
  ambiguity before adding lower-value features.
- P1: Implement frequently used Discord workflows with local/demo behavior when no
  external service is required.
- P2: Keep low-frequency or external-service-heavy features as explicit demo-only
  panels or hide them until they can be made useful.

## Button Reliability Policy

Every visible action must fall into one of these categories:

- `implemented`: performs the real local action.
- `local-panel`: opens a useful local popover/modal/sheet with real state or an empty
  state.
- `demo-disabled`: remains visible only when its value is clear, and shows a concise
  demo limitation.
- `hidden`: removed from the main surface because it is misleading for the current
  implementation.

Avoid adding decorative controls that do nothing.

## Stage 8.0: UI Audit And Guardrail Documentation

Status: completed.

Goal: create this controlling document and connect it from the project documentation
so future work does not drift into unrelated Store or feature-count work.

Tasks:

- Record the UI remediation goals and privacy constraints.
- Define priority and button reliability rules.
- List Stage 8.1 through Stage 8.14 with deliverables and verification.
- Link this plan from `PROJECT_CONTEXT.md`, `docs/README.md`, and
  `docs/implementation-plan.md`.

Deliverables:

- `docs/discord-ui-remediation-plan.md`.
- Updated project context and documentation index.

Verification:

- `git diff --check`.
- Documentation secret-pattern guard.
- Commit and push to `origin/main`.

## Stage 8.1: Layout Tokens And App Shell Sizing

Status: completed.

Goal: make the base app shell match Discord-like proportions and prevent UI drift.

Tasks:

- Add stable CSS tokens for server rail, private sidebar, channel sidebar, header,
  member list, composer, and bottom panels.
- Rework `base.css` grid/flex sizing so the app does not depend on incidental content
  height.
- Normalize icon button dimensions, gaps, hover states, and selected states.
- Keep mobile breakpoints compatible with Stage 7.11 responsive behavior.

Deliverables:

- Updated `frontend/src/styles/base.css`.
- Small component class adjustments only where needed.

Verification:

- `npm run lint:frontend`.
- `npm --prefix frontend run build`.
- Browser screenshots at desktop and narrow widths with no horizontal overflow.
- Commit and push.

Completion notes:

- `frontend/src/styles/base.css` now owns app-shell sizing tokens for the server
  rail, channel/private sidebar width, header height, bottom voice panel height,
  composer height, icon buttons, and shared surface colors.
- The app shell now has fixed viewport bounds with hidden global overflow and
  scrollable inner sidebars/content regions.
- Stage 8.1 browser QA screenshots:
  - `docs/qa-artifacts/stage-8-1-desktop.png`
  - `docs/qa-artifacts/stage-8-1-mobile.png`
- Verified no document-level horizontal overflow at `1440x900` and `390x844`.

## Stage 8.2: Sidebar Text Overlap And Channel Creation UI

Status: completed.

Goal: remove overlapping category labels and make channel creation clean.

Tasks:

- Fix text/voice category label spacing in `ChannelSidebar.vue` and CSS.
- Replace cramped inline channel creation controls with a stable compact row or
  modal-like panel.
- Ensure long English names, Korean labels, and generated channel names truncate or
  wrap safely.
- Keep create text and create voice flows working through existing APIs.

Deliverables:

- Updated `frontend/src/components/ChannelSidebar.vue`.
- Focused CSS for category headers, channel rows, and channel create form.

Verification:

- Frontend lint/build.
- Browser smoke for creating text and voice channels.
- Visual check for default and newly created channels.
- Commit and push.

Completion notes:

- `frontend/src/components/ChannelSidebar.vue` now renders text and voice channel
  creation as compact stacked panels instead of cramped three-column inline forms.
- `frontend/src/styles/base.css` now keeps category labels, create panels, channel
  rows, row icons, action buttons, and voice-member rows inside the fixed sidebar
  width with truncation instead of overlap.
- Browser smoke created one text channel and one voice channel through the UI, then
  verified category labels, generated rows, and form bounds.
- Stage 8.2 browser QA screenshot:
  - `docs/qa-artifacts/stage-8-2-sidebar.png`

## Stage 8.3: Korean And English I18n Foundation

Status: completed.

Goal: support Korean and English through a reusable frontend i18n layer.

Tasks:

- Add `frontend/src/i18n/` with Korean and English dictionaries.
- Add a Pinia preferences store for language persistence.
- Add a `t()` helper or composable that works inside `<script setup>`.
- Convert high-visibility UI copy first: auth, navigation, friends, DM, channel
  sidebar, chat composer, voice panel, settings, and common dialogs.
- Add language selection in Settings.

Deliverables:

- `frontend/src/i18n/index.ts`.
- `frontend/src/stores/preferences.ts`.
- Updated components for key UI copy.

Verification:

- Frontend lint/build.
- Browser smoke for language switching and reload persistence.
- Check Korean and English labels do not overflow core surfaces.
- Commit and push.

Completion notes:

- `frontend/src/i18n/index.ts` defines Korean/English dictionaries and the `useI18n()`
  helper with parameter interpolation.
- `frontend/src/stores/preferences.ts` persists the selected language in localStorage.
- High-visibility UI copy is wired in the auth panel, app shell/header, private
  sidebar, channel sidebar, Friends home, server chat composer/actions, DM view,
  voice panel, gateway status label, and user settings.
- Settings now includes a `Language` panel with Korean/English radio choices.
- Browser QA verified Korean default copy, English switching, reload persistence,
  gateway/voice status labels, and no horizontal overflow.
- Stage 8.3 browser QA screenshots:
  - `docs/qa-artifacts/stage-8-3-ko-home.png`
  - `docs/qa-artifacts/stage-8-3-en-home.png`
  - `docs/qa-artifacts/stage-8-3-en-settings.png`

## Stage 8.4: Bottom User And Voice Panel Redesign

Status: completed.

Goal: make the bottom area clean, compact, and informative.

Tasks:

- Separate user identity controls from voice connection controls.
- Show voice connection card only when connected or connecting.
- Standardize microphone, deafen, settings, disconnect, and screen share controls.
- Show input meter and speaking state without crowding the panel.
- Keep existing WebRTC mute/deafen/screen-share behavior.

Deliverables:

- Updated `frontend/src/components/VoicePanel.vue`.
- Updated voice-panel CSS.

Verification:

- Frontend lint/build.
- Browser smoke for mute, deafen, settings, join/leave, and connected/disconnected
  layout.
- Commit and push.

Completion notes:

- `frontend/src/components/VoicePanel.vue` now separates user identity/actions,
  voice connection summary, presence/meter/status, and screen/call controls.
- `frontend/src/styles/base.css` styles connected and disconnected voice states as
  distinct compact summaries, with a green connected card, explicit speaking state,
  and a red disconnect button while connected.
- Narrow layouts hide secondary connection/presence detail and keep the user/actions
  row within the bottom panel.
- Browser QA used fake media capture and verified connect, mute, deafen, settings
  entry, disconnect, desktop overflow, and mobile overflow.
- Stage 8.4 browser QA screenshots:
  - `docs/qa-artifacts/stage-8-4-voice-disconnected.png`
  - `docs/qa-artifacts/stage-8-4-voice-connected.png`
  - `docs/qa-artifacts/stage-8-4-mobile.png`

## Stage 8.5: Current Location And State Visibility

Status: completed.

Goal: make the current destination and voice state obvious.

Tasks:

- Strengthen selected states for server rail, DM rows, text channels, and voice
  channels.
- Add a compact location/status summary near the channel header or main view.
- Show voice membership, self-connected state, muted/deafened state, and speaking
  state in the sidebar and bottom panel.
- Avoid duplicating noisy diagnostics in primary view; keep detailed stats secondary.

Deliverables:

- Updates to `App.vue`, `ChannelSidebar.vue`, `PrivateChannelSidebar.vue`,
  `ServerRail.vue`, `VoicePanel.vue`, and CSS as needed.

Verification:

- Frontend lint/build.
- Browser smoke for `@me`, DM, text channel, voice channel, mute, and speaking-state
  visual indicators.
- Commit and push.

Completion notes:

- `frontend/src/App.vue` now renders a compact destination subtitle in the header and
  a voice-location status pill while connected.
- `frontend/src/components/ServerRail.vue`,
  `frontend/src/components/PrivateChannelSidebar.vue`, and
  `frontend/src/components/ChannelSidebar.vue` expose current selection through
  `aria-current` and stronger active styling.
- `frontend/src/components/ChannelSidebar.vue` shows the locally connected voice
  channel, current user's voice row, and muted/deafened/speaking state labels.
- `frontend/src/components/VoicePanel.vue` prioritizes muted/deafened state in the
  bottom voice status area.
- Browser QA verified Friends, DM, server text channel, voice join, and mute state
  visibility with no horizontal overflow.
- Stage 8.5 browser QA screenshot:
  - `docs/qa-artifacts/stage-8-5-voice-state.png`

## Stage 8.6: Placeholder Button Audit And Cleanup

Status: completed.

Goal: remove or convert misleading buttons.

Tasks:

- Inventory visible placeholder buttons from `App.vue`, `ChatView.vue`,
  `PrivateChannelSidebar.vue`, `ChannelSidebar.vue`, `FriendsHome.vue`, and
  `SettingsView.vue`.
- Convert useful buttons to local panels.
- Hide low-value buttons from the primary path.
- Add a shared demo-disabled notice pattern for features outside local scope.

Deliverables:

- Updated visible button behavior and copy.
- Documentation note in `PROJECT_CONTEXT.md` describing the policy.

Verification:

- Frontend lint/build.
- Browser smoke clicks for every header/composer/sidebar action visible in the main
  surfaces.
- Commit and push.

Completion notes:

- `frontend/src/App.vue` now exposes a shared demo-disabled notice pattern for
  visible actions that remain outside the local clone scope.
- `frontend/src/components/PrivateChannelSidebar.vue` wires DM search, Nitro, Shop,
  and Quests to the demo notice instead of leaving them inert.
- `frontend/src/components/ChannelSidebar.vue` wires server menu and Events to the
  demo notice while preserving real create/invite/channel flows.
- `frontend/src/components/FriendsHome.vue` turns the friend-row More button into a
  local profile-summary menu with a message action.
- `frontend/src/components/ChatView.vue` turns upload, gift, apps, and emoji composer
  buttons into a local scoped demo panel until Stage 8.8 expands useful composer
  actions.
- The workspace notice row was fixed so demo notices stay compact and do not consume
  the main content area.
- Browser QA clicked the representative private-sidebar, server-sidebar,
  friend-row, and composer controls and verified no horizontal overflow.
- Stage 8.6 browser QA screenshot:
  - `docs/qa-artifacts/stage-8-6-button-panels.png`

## Stage 8.7: Channel Header Panels

Status: completed.

Goal: turn common channel-header buttons into useful local panels.

Tasks:

- Implement notification settings panel: all messages, mentions only, none.
- Implement pinned messages panel with empty state.
- Implement threads panel with empty state.
- Implement channel search for current message list.
- Keep member list toggle functional.

Deliverables:

- Header panel state in `App.vue` or a small component if it reduces complexity.
- Focused CSS for anchored panels.

Verification:

- Frontend lint/build.
- Browser smoke for each header icon and search result behavior.
- Commit and push.

Completion notes:

- `frontend/src/App.vue` now owns local channel-header panel state for threads,
  notifications, pinned messages, and current-channel search.
- Threads and pinned messages open useful empty-state panels instead of generic
  notices.
- Notification settings support all messages, mentions only, and mute notifications
  as local session state.
- Channel search filters the active channel's in-memory messages by author or
  content and shows empty/no-result states.
- `frontend/src/styles/base.css` positions the panel below the topbar without
  affecting the workspace grid.
- Browser QA verified threads, notifications, pinned messages, search, radio option
  selection, and no horizontal overflow.
- Stage 8.7 browser QA screenshot:
  - `docs/qa-artifacts/stage-8-7-header-panels.png`

## Stage 8.8: Composer Action Panels

Status: completed.

Goal: make composer actions useful without external services.

Tasks:

- Implement local emoji insertion.
- Implement file attach preview or explicit demo limitation.
- Implement local apps/actions panel with useful demo entries.
- Move gift/Nitro-related functionality out of the main composer if it is not useful.
- Preserve send/edit/delete behavior.

Deliverables:

- Updated `ChatView.vue` and DM composer parity where appropriate.
- CSS for composer popovers.

Verification:

- Frontend lint/build.
- Browser smoke for emoji insertion, file/demo panel, message send, edit, delete.
- Commit and push.

Completion notes:

- `frontend/src/components/ChatView.vue` now supports local emoji insertion, a
  hidden file picker with selected-file metadata, useful apps/action templates for
  poll and todo drafting, and an explicit gift demo limitation.
- `frontend/src/components/DirectMessageView.vue` has DM composer parity for local
  emoji insertion while preserving the existing DM message send flow.
- `frontend/src/styles/base.css` keeps composer panels bounded under the input and
  fixes the DM composer grid so the input, expression action, and send button align.
- Browser QA verified server composer emoji insertion, apps template insertion,
  upload demo metadata, DM composer emoji insertion, and DM button-based send.
- Stage 8.8 browser QA screenshots:
  - `docs/qa-artifacts/stage-8-8-composer-panels.png`
  - `docs/qa-artifacts/stage-8-8-dm-composer.png`

## Stage 8.9: Friends And DM Information Density

Status: completed.

Goal: make `@me` and DM screens easier to scan.

Tasks:

- Improve friend rows with status, activity, and message action clarity.
- Add optional activity/profile summary panel when width allows.
- Improve DM selected state and conversation intro.
- Keep demo friend/relationship data safe and original.

Deliverables:

- Updated `FriendsHome.vue`, `DirectMessageView.vue`, `PrivateChannelSidebar.vue`,
  and CSS.

Verification:

- Frontend lint/build.
- Browser smoke for Friends tabs, DM open, DM send, narrow layout.
- Commit and push.

Completion notes:

- `frontend/src/components/FriendsHome.vue` now shows status, relationship, handle,
  activity, selected-row state, and a wide-screen profile/activity summary panel.
- `frontend/src/components/PrivateChannelSidebar.vue` now shows DM presence dots,
  status/activity details, group member counts, unread badges, and stronger selected
  state in the private sidebar.
- `frontend/src/components/DirectMessageView.vue` now shows a richer DM intro with
  status, message count, participant names, and participant chips.
- `frontend/src/styles/base.css` adds bounded Friends/DM detail layouts and hides
  the Friends profile panel under the narrow breakpoint so the list remains primary.
- Browser QA verified Friends rows/summary panel, DM selected state, DM intro
  metadata, DM send, and no horizontal overflow in the available desktop viewport.
  The in-app Browser surface does not expose viewport resizing, so the narrow layout
  was verified by the 1180/900/620px responsive CSS rules plus frontend build.
- Stage 8.9 browser QA screenshots:
  - `docs/qa-artifacts/stage-8-9-friends-home.png`
  - `docs/qa-artifacts/stage-8-9-friends-dm.png`

## Stage 8.10: Settings Reorganization

Status: completed.

Goal: make Settings closer to the Discord structure while remaining locally useful.

Tasks:

- Reorganize settings groups: account, voice/video, appearance, accessibility,
  keybinds, language/time, and logout.
- Move useful voice state and language controls into real settings panels.
- Keep demo-only settings explicit.
- Ensure settings scroll and sidebar selection do not clip text.

Deliverables:

- Updated `SettingsView.vue`.
- CSS for denser settings sections.

Verification:

- Frontend lint/build.
- Browser smoke for settings navigation, language switching, voice panel visibility,
  logout, and narrow viewport.
- Commit and push.

Completion notes:

- `frontend/src/components/SettingsView.vue` now groups settings into Account,
  Experience, and Session navigation sections.
- Settings panels now cover account/privacy, voice and video, appearance,
  accessibility, keybinds, language/time, and logout with explicit local-demo scope.
- Useful voice state, input level, ICE readiness, language selection, and time-format
  controls are real local panels instead of loose placeholders.
- `frontend/src/styles/base.css` adds denser settings selection, card copy, radio,
  toggle, and keybind text handling so long labels do not clip.
- Browser QA verified settings navigation, voice panel visibility, accessibility
  controls, Korean/English switching, language/time controls, logout, and relogin.
  The in-app Browser surface does not expose viewport resizing, so narrow viewport
  coverage remains build-verified through the existing responsive CSS rules.
- Stage 8.10 browser QA screenshot:
  - `docs/qa-artifacts/stage-8-10-settings.png`

## Stage 8.11: Voice And Screen Share Workspace UX

Status: completed.

Goal: make voice channel entry and voice workspace less ambiguous.

Tasks:

- Separate selecting a voice channel from joining voice when needed.
- Improve voice workspace empty/connected/screen-share states.
- Surface local user tile, remote participants, and screen-share state cleanly.
- Keep browser permission prompts and errors understandable.

Deliverables:

- Updates to `App.vue`, `ChannelSidebar.vue`, `VoicePanel.vue`, and voice video
  surface CSS.

Verification:

- Frontend lint/build.
- Browser smoke for voice select, join, leave, mute, deafen, and screen-share toggle
  where browser permissions allow.
- Commit and push.

Completion notes:

- `App.vue` now opens a dedicated voice workspace when a voice channel is selected,
  separating channel preview from joining the call.
- The workspace shows the active guild/channel, local connected/preview state,
  remote/empty participant tiles, join/leave actions, and an explicitly disabled
  screen-share action until the user is connected.
- `ChannelSidebar.vue` marks selected-but-not-connected voice channels separately
  from connected channels, and `VoicePanel.vue` uses clearer selected-channel copy.
- Browser QA covered the in-app permission-denied path plus a fake-media Chrome path
  for select, join, mute, deafen, screen-share enabled state, leave, and horizontal
  overflow checks.
- Stage 8.11 browser QA screenshots:
  - `docs/qa-artifacts/stage-8-11-voice-workspace.png`
  - `docs/qa-artifacts/stage-8-11-voice-workspace-fake-media.png`

## Stage 8.12: Low-Frequency Feature Scope Decisions

Status: pending.

Goal: prevent misleading UI for features not worth implementing in this clone slice.

Tasks:

- Classify Nitro, Shop, Quests, Gifts, Activities, full GIF search, external app
  launcher, production notifications, and real file upload.
- Hide, defer, or convert each to a demo-disabled panel based on utility.
- Document deferred decisions.

Deliverables:

- Updated navigation/composer/settings surfaces.
- Updated `PROJECT_CONTEXT.md` scope notes.

Verification:

- Frontend lint/build.
- Browser smoke that no visible low-frequency button appears dead.
- Commit and push.

## Stage 8.13: Responsive And Accessibility QA

Status: pending.

Goal: verify Stage 8 changes across sizes and keyboard/screen-reader basics.

Tasks:

- Check focus order for rail, sidebars, header panels, composer, settings, and modals.
- Verify visible focus states.
- Capture desktop and mobile screenshots.
- Record overflow metrics and any residual manual QA gaps.

Deliverables:

- `docs/stage-8-responsive-accessibility-qa.md`.
- Screenshot artifacts under `docs/qa-artifacts/` if new screenshots are captured.

Verification:

- Frontend lint/build.
- Browser screenshots at desktop and mobile widths.
- DOM overflow metric check.
- Commit and push.

## Stage 8.14: Final Stage 8 Verification And Documentation

Status: pending.

Goal: close the UI remediation slice.

Tasks:

- Update `PROJECT_CONTEXT.md`, `docs/README.md`, and `docs/implementation-plan.md`.
- Run full verification:
  - `npm run test:backend`
  - `npm run lint:backend`
  - `npm run lint:frontend`
  - `npm --prefix frontend run build`
  - Docker Compose smoke when Docker is available.
- Run browser smoke:
  - login/demo session
  - language switch
  - `@me` and Friends tabs
  - DM open and send
  - text channel create/send
  - voice channel select/join/mute/deafen/leave
  - header panels
  - composer panels
  - settings navigation/logout

Deliverables:

- Final Stage 8 QA notes.
- Final docs and pushed commit.

Verification:

- Full command and browser smoke pass before the goal is complete.
