# Discord Interaction Polish Plan

This document controls Stage 10 work. It is based on the user's latest side-by-side
screenshots where the left side is real Discord and the right side is the current
clone after Stage 9.

Future implementation must read this document before changing the app shell,
server rail, sidebars, Friends home, text channel, composer, member list, bottom
user controls, voice channel workspace, or screen-share flow.

Privacy rule: use user-provided screenshots only for layout, density, interaction
structure, state visibility, and hierarchy. Do not copy private Discord names,
messages, avatars, images, server names, or other personal content into seed data,
fixtures, UI copy, or documentation.

## Reference Material

- Discord Beginner's Guide:
  `https://support.discord.com/hc/en-us/articles/360045138571-Beginner-s-Guide-to-Discord`
- Go Live and Screen Share:
  `https://support.discord.com/hc/en-us/articles/360040816151-Go-Live-and-Screen-Share`
- Discord Voice, Video, and Streaming Guide:
  `https://support.discord.com/hc/en-us/articles/33030151293079-Discord-Voice-Video-Streaming-Guide`
- Group Chat and Calls:
  `https://support.discord.com/hc/en-us/articles/223657667-Group-Chat-and-Calls`
- Text Channels and Text Chat in Voice Channels:
  `https://support.discord.com/hc/en-us/articles/4412085582359-Text-Channels-Text-Chat-In-Voice-Channels`
- Discord UI refresh coverage:
  `https://www.theverge.com/news/635435/discord-ui-refresh-dark-mode-new-overlay`
- Discord UI component reference catalog:
  `https://nicelydone.club/apps/discord/components`

Use official Discord Support pages for interaction order and feature behavior. Use
third-party UI catalogs only as visual reference, not as an implementation authority.

## Stage 10 Target

Stage 10 is not a feature-count stage. It is a product-quality pass whose goal is to
make the existing clone feel cleaner, quieter, and more Discord-like.

The priority is:

1. Remove visual noise and development/test artifacts from primary screens.
2. Rebuild layout hierarchy so frequently used controls are easy to find.
3. Replace the current bottom bar with Discord-like user and voice control areas.
4. Improve text/button spacing, panel boundaries, message density, and component
   proportions.
5. Keep only useful high-frequency functionality visible by default.

## Current Problem Inventory

### Global UI

- The clone still reads like a demo dashboard rather than a chat application.
- Too many controls and status texts are visible at once.
- Development/test data such as `QA Smoke`, `stage8-*`, long generated IDs, and
  template messages appear in user-facing surfaces.
- Color choices and panel layering are inconsistent with Discord's muted dark shell.
- Some controls look like standalone cards instead of parts of one continuous app.
- Icon buttons, row heights, pills, and text sizes do not share one consistent rhythm.

### Text And Box Boundaries

- Text is too close to the edges of file cards, reaction pills, channel rows, and
  bottom control cards.
- Some buttons are visually heavy while adjacent text is too small or weak.
- Message rows, reaction buttons, and attachment cards do not align to one baseline.
- Several labels are truncated too aggressively because the containing row is too
  narrow or has unnecessary neighboring controls.

### Bottom User And Voice Area

- The current bottom bar is too large, too busy, and visually detached.
- Voice diagnostics such as STUN/TURN readiness are user-facing when they should be
  hidden in settings or diagnostics.
- The bottom bar can cover or visually compete with the main content.
- The current structure differs from Discord's pattern: compact user panel in the
  lower-left, voice state near the active voice context, and only essential call
  controls visible.

### Friends And Direct Messages

- Friends rows are cleaner than before, but the view still has more visible demo
  styling than Discord.
- Some friend metadata feels artificial and dense in the wrong place.
- The right activity panel is useful, but its hierarchy should be quieter and closer
  to Discord's "Active Now" style.
- Private sidebar direct messages need better scan quality with less visible
  generated/demo text.

### Server And Channel Sidebar

- Channel rows still show too many management affordances by default.
- Voice channel rows are clearer after Stage 9 but still show extra text and badges
  compared with Discord's compact connected-state presentation.
- Server/channel names created during QA remain visible and harm visual evaluation.

### Text Channel

- Timeline width and message grouping feel less natural than real Discord.
- Attachment cards and reaction pills are too visually loud and too similar to
  generic dashboard components.
- The composer is functional but not polished enough in spacing, icon alignment, and
  default button visibility.
- Some current messages are test artifacts rather than realistic conversation data.

### Voice And Screen Share

- The voice workspace now shows clear tiles, but it is still too card-heavy.
- Real Discord exposes voice connection, microphone, camera/screen share, leave, and
  chat affordances with fewer words.
- Speaking state should be shown by glow/ring and row state, not by adding verbose
  labels.
- Screen share should follow Discord's flow: join voice, use the screen-share control,
  choose a target, then show a compact stream/preview state.

## Implementation Rules For Stage 10

- Complete each stage with verification before moving on.
- If implementation or QA exposes a new UI issue, add a `Stage 10.x.y` corrective
  note under the relevant section before fixing it.
- Keep commits scoped and use Korean commit titles.
- Push completed work to `origin/main` unless explicitly told not to.
- Update `PROJECT_CONTEXT.md`, `docs/implementation-plan.md`, and `docs/README.md`
  when Stage 10 status changes.
- Do not copy private Discord data from screenshots.
- Do not add new large features unless they directly simplify a high-frequency
  Discord workflow.

## Stage 10.0: Baseline Lock

Status: completed. Baseline notes are recorded in `docs/stage-10-baseline.md`.

Goal: freeze the current visual baseline before implementation.

Tasks:

- Record current Friends, Add Friend, text channel, voice preview, connected voice,
  and screen-share screenshots.
- Record current browser width/height and zoom assumption: FHD or side-by-side Chrome
  at 100% zoom.
- Identify which visible data is persistent user data and which is test/demo data.

Verification:

- Browser screenshots exist or are documented in QA notes.
- No implementation changes are made in this stage.

## Stage 10.1: Demo And Test Data Cleanup

Status: completed. Fresh demo seed copy now uses natural safe sample users/messages,
and the frontend filters obvious smoke-test names/messages from default visual
surfaces without deleting persistent database rows.

Corrective Stage 10.1.1: implementation review found that hidden QA guilds could
leave the active guild/channel selection pointing at filtered data, and one DM
cleanup helper name collided with a local variable. Both issues were corrected before
moving to Stage 10.2.

Corrective Stage 10.1.2: backend verification found one test still expected the old
`SRS Lab` seed name, and the native demo-store fallback still used development-style
DM names/messages. The test expectation and native fallback seed data were updated
before moving to Stage 10.2.

Corrective Stage 10.1.3: repeat backend verification found DM API, demo-store, and
repository tests still using the old development-style DM fixture names. The fixture
data and expectations were updated to the same safe sample names used by runtime
seed data.

Corrective Stage 10.1.4: Stage 10.2 browser QA found that existing Docker
PostgreSQL volumes still retained old development-style DM usernames because user
rows were inserted with `ON CONFLICT DO NOTHING`. Seed/repository upserts now refresh
seeded demo usernames/statuses, and the frontend visual-noise filter also hides the
old fixture names while the existing session refreshes.

Goal: remove development artifacts from primary UI.

Tasks:

- Hide or rename `QA Smoke`, `stage8-*`, generated smoke-test channels, and obvious
  test messages from default visual QA surfaces.
- Keep the data in the database if needed for tests, but filter it from default
  presentation or move it behind a diagnostics/development mode.
- Replace seed messages with natural safe sample conversation, attachment, and
  reaction content.
- Ensure fresh Docker data starts with clean demo servers, channels, friends, and DMs.

Verification:

- Friends, server sidebar, text channel, and voice views no longer show test names by
  default.
- Backend tests still pass if seed/repository behavior changes.

## Stage 10.2: Design Token Reset

Status: completed. Global dark shell tokens, surface layers, selected/hover states,
focus ring, scrollbar colors, and high-use icon/composer/member/voice surfaces now
share a quieter Discord-like palette and sizing baseline.

Goal: make the visual language quieter and more Discord-like.

Tasks:

- Rework global dark palette, surface layers, selected row color, hover color,
  dividers, muted text, and focus color.
- Standardize row heights, icon button sizes, border radius, panel padding, and
  text sizes.
- Reduce saturated accent usage to active/positive/danger states only.
- Remove decorative gradients except where media/voice stage needs a deliberate
  visual surface.

Verification:

- FHD browser screenshot shows one coherent dark shell, not separate dashboard cards.
- Focus styles remain visible.
- Browser QA confirmed the live app shell uses the updated `#313338` app background
  and `#404249` selected surface tokens, has no horizontal body overflow at 1280 px,
  and no longer exposes old development-style DM names in the primary shell.

## Stage 10.3: Shell Layout Recomposition

Status: completed. The workspace now owns the main content height while the voice
panel is constrained to the active sidebar column, so bottom controls no longer take
space from chat, Friends, member, or voice workspace content.

Goal: fix the overall rail/sidebar/main/member/bottom rhythm.

Tasks:

- Revisit app shell grid columns and bottom row usage.
- Keep server rail and active sidebar stable.
- Keep main content from being visually covered by bottom controls.
- Make the member list feel like a side panel, not a separate page.
- Remove horizontal overflow sources.

Verification:

- No horizontal scrollbar in Friends, text channel, or voice channel.
- Main content remains readable at FHD side-by-side width.
- Browser QA passed for Friends, text channel, and voice channel surfaces: no body
  horizontal overflow, voice controls stay inside the sidebar column, the sidebar
  ends above the voice panel, and the workspace remains clear of the voice-control
  column.

## Stage 10.4: Server Rail Polish

Status: completed. Server rail active/unread markers now use a consistent left pill,
server buttons keep stable sizing and quiet hover states, mention badges are clamped
to compact labels, and add/discovery controls are visually secondary.

Goal: improve scan quality of the left icon rail.

Tasks:

- Normalize server icon shape, active marker, unread marker, mention badge, and
  separator spacing.
- Use safe visual avatars or initials consistently.
- Reduce decorative hover effects.
- Keep add/discovery controls visually secondary.

Verification:

- Active server is recognizable without reading text.
- Badges do not overlap avatars.
- Browser QA confirmed the active marker renders as a tall left pill, active buttons
  use the expected 16 px rounded state, the rail has no horizontal overflow, and
  add/discovery controls use secondary colors. The current demo state had no live
  mention badge, so badge overlap was verified from the clamped corner placement
  implementation.

## Stage 10.5: Private Sidebar Simplification

Status: completed. Private navigation is now limited to the primary Friends entry
and compact DM rows, while repeated inactive/fallback copy is hidden from the main
sidebar.

Goal: make the DM/Friends sidebar match Discord's practical density.

Tasks:

- Hide low-frequency or unimplemented rows from primary view.
- Keep Friends and DM rows compact and readable.
- Ensure DM names, activities, status dots, and unread counts align.
- Move development scope text into settings/docs, not primary navigation.

Verification:

- Sidebar rows do not wrap unexpectedly.
- DM list feels populated but not noisy.
- Browser QA confirmed the private sidebar renders at 300 px, DM rows stay compact
  at 46 px, title/activity lines stay single-line, no `no activity` fallback text is
  shown, and only the primary Friends navigation row is visible.

## Stage 10.6: Friends Home Rework

Status: completed. Friends rows now hide secondary actions until hover/focus/active,
fallback `no activity` copy is removed from the primary list, and the right panel is
a quieter activity card instead of a profile metadata table.

Goal: make Friends feel like a native Discord screen.

Tasks:

- Rework tabs, search field, friend row, hover actions, and selected states.
- Calm the right activity panel and reduce unnecessary metadata.
- Use clearer empty states only when data is genuinely empty.
- Avoid large unused center canvas.

Verification:

- Friends Online and Add Friend screenshots match the real Discord hierarchy more
  closely.
- Message/open actions are discoverable without permanent visual clutter.
- Browser QA confirmed Friends has no horizontal overflow, friend rows stay at or
  under 60 px, non-active row actions are hidden until interaction, no fallback
  `no activity` text appears, the right activity panel no longer renders a metadata
  table, and the Add Friend tab still opens with its input/button intact.

## Stage 10.7: Add Friend Workflow Polish

Goal: make Add Friend simple and less dashboard-like.

Tasks:

- Rebuild input row with strong field/button spacing.
- Show success/error states inline.
- Hide illustration/discovery copy if it creates clutter in narrow views.
- Keep the workflow one-step: type handle, submit, see result.

Verification:

- Input text and button text never touch borders.
- Disabled and success states are visible.

## Stage 10.8: Server Sidebar Polish

Goal: make channel navigation quiet and compact.

Tasks:

- Rework server header, Events row, category labels, text channels, voice channels,
  and channel action buttons.
- Show channel management actions primarily on hover/focus or when forms are open.
- Make active text and voice channels use consistent selected states.
- Compact connected voice members under the active voice channel.

Verification:

- Channel list does not look like an admin panel.
- Active channel and connected voice state are scannable.

## Stage 10.9: Header Action Reduction

Goal: show only useful controls in the top header.

Tasks:

- Hide or defer icons that do not perform high-frequency actions.
- Keep search, member list, pins/notifications where implemented or visibly useful.
- Move logout/development actions to settings.
- Ensure header title, location, and search do not crowd each other.

Verification:

- Header icons do not wrap or collide at side-by-side width.
- Each visible icon has a working action or clear local fallback.

## Stage 10.10: Text Timeline Rebuild

Goal: make chat content feel like Discord.

Tasks:

- Rework message groups, timestamps, author line, hover actions, and date dividers.
- Replace artificial reaction labels with compact reaction pills.
- Rework attachment cards with stable icon, filename, size, and spacing.
- Remove artificial repeated template messages from default visual data.
- Fix message column width and overflow.

Verification:

- No horizontal scroll in the message panel.
- Text and attachments align to one message column.

## Stage 10.11: Composer Rebuild

Goal: make message entry feel polished and low-friction.

Tasks:

- Rework plus/upload, input, emoji, and send affordances.
- Hide nonessential composer actions by default.
- Keep implemented local actions available without clutter.
- Ensure placeholder and typed text align vertically.

Verification:

- Composer is readable, stable, and not covered by voice controls.
- Keyboard send behavior remains unchanged.

## Stage 10.12: Member List Simplification

Goal: reduce admin noise in the right panel.

Tasks:

- Hide role-management controls by default.
- Keep role management accessible through a clear management toggle or settings
  surface.
- Show member avatar, name, role/status, and minimal actions.
- Reduce panel contrast so it supports the main chat rather than competing with it.

Verification:

- Normal users see a clean member list.
- Admin controls remain reachable for authorized users.

## Stage 10.13: Bottom User Panel Rebuild

Goal: replace the current full-width bottom bar with Discord-like controls.

Tasks:

- Keep user identity, status, mic, headphones, and settings in the lower-left panel.
- Move voice diagnostics out of the primary bottom bar.
- Show compact voice connection card only when connected or a voice channel is
  selected.
- Make disconnect, mute, deafen, and screen-share states clear through icon state,
  color, and tooltip.

Verification:

- Bottom controls do not obscure main content.
- Mic on/off and speaking state are understandable at a glance.

## Stage 10.14: Voice Channel Workspace Rebuild

Goal: make voice view cleaner and closer to Discord's call surface.

Tasks:

- Reduce card-heavy presentation.
- Use participant tiles only where they add clarity.
- Use speaking ring/row glow for input activity.
- Keep leave and screen-share buttons prominent but not oversized.
- Make "no other participants" a quiet secondary state.

Verification:

- Voice connected state is visible in sidebar and workspace.
- Speaking state is visible without extra explanatory text.

## Stage 10.15: Screen Share Flow Rework

Goal: follow Discord's screen-share flow and reduce clutter.

Tasks:

- Enable screen share only after voice connection.
- Keep the control in the voice status area.
- Show a compact preview tile or PiP only while sharing.
- Provide a clear stop-sharing affordance.
- Hide detailed stream diagnostics from the primary surface.

Verification:

- Screen share can be started/stopped from the expected voice controls.
- Preview does not cover composer or member list.

## Stage 10.16: Feature Visibility Policy

Goal: decide what should be visible by default.

Visible by default:

- Friends, direct messages, text channels, voice channels, message composer, member
  list toggle, user status/settings, mute/deafen, voice join/leave, screen share.

Hidden or deferred from primary UI:

- Nitro, Shop, Quests, external apps, full GIF search, commerce flows, debug gateway
  text, STUN/TURN diagnostics, smoke-test controls.

Available through settings/diagnostics:

- Gateway status, ICE/STUN/TURN detail, local demo scope, logout, developer notes.

Verification:

- Primary screen contains no obvious developer/debug text.
- Low-frequency features do not appear as broken buttons.

## Stage 10.17: Responsive And Accessibility QA

Goal: make the cleaner UI stable across practical layouts.

Tasks:

- Test FHD full-width, side-by-side desktop, tablet-like width, and mobile width.
- Check keyboard focus order for rail, sidebar, header, chat, composer, voice, and
  settings.
- Check visible focus states and accessible labels for icon-only controls.
- Check text truncation, wrapping, and overflow.

Verification:

- Browser screenshots and notes are recorded.
- No horizontal scroll remains in primary screens.

## Stage 10.18: Final QA, Documentation, Commit, Push

Goal: finish Stage 10 with repeatable evidence.

Tasks:

- Run frontend production build.
- Run backend tests if data or API behavior changed.
- Run Docker smoke if Docker remains the active local environment.
- Record browser QA for Friends, Add Friend, text channel, connected voice, and
  screen share.
- Update `PROJECT_CONTEXT.md`, `docs/implementation-plan.md`, and `docs/README.md`.
- Commit with a Korean title and push to `origin/main`.

Verification:

- Required commands pass or residual risks are explicitly documented.
- Working tree is clean after commit and push.
