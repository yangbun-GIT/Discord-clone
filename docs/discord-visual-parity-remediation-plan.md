# Discord Visual Parity Remediation Plan

This document is the controlling plan for the next Discord clone quality pass after
Stage 8. It is based on the user's side-by-side screenshots where the left side is
the real Discord web app and the right side is the current clone.

Future implementation must read this document before changing the app shell,
Friends home, channel sidebar, message timeline, composer, member list, bottom
controls, voice workspace, or screen-share workspace.

Privacy rule: use the screenshots only for layout, density, interaction structure,
state visibility, and component hierarchy. Do not copy private Discord names,
messages, server names, avatars, images, or real assets into seed data, fixtures,
documentation, or UI copy.

## Stage 9 Execution Update

The user confirmed the earlier comparison was affected by browser zoom and 4K display
scaling. Stage 9 should use the later FHD Chrome 100% screenshots as the visual
reference. Exact DevTools pixel measurements are not required; choose conservative
Discord-like proportions from the screenshots and verify by browser QA.

The user also clarified the target:

- Prioritize clean Discord-like box composition, spacing, and visual hierarchy.
- Hide unnecessary development text and low-value controls from the primary surface.
- Keep useful high-frequency controls visible and reliable.
- Voice channel rows should use a compact Discord-like input indicator: when the
  user is connected, the row is clear; when microphone input is detected, the icon or
  row edge should glow rather than adding verbose text.

During Stage 9, if implementation or verification exposes an additional issue, add a
`Stage 9.x.y` corrective note under the relevant stage, fix that issue before moving
on, then continue the main sequence.

Commit titles for Stage 9 should be Korean so the user can scan Git history quickly.

## First-Pass Assessment

The clone is functional, but it does not yet match Discord's visual density,
proportions, or information hierarchy. The most important gap is not one missing
feature; it is that the app shell, content density, empty states, and voice/call
surfaces still read as a custom dashboard rather than Discord's compact workspace.

The next implementation pass should prioritize shell proportions, content density,
navigation clarity, and high-frequency surfaces before adding new feature count.

## Problem Inventory

### Global Shell And Density

- The clone has too much unused dark space in Friends, Add Friend, text channel, and
  voice views.
- Primary content is often vertically and horizontally under-positioned compared with
  Discord's compact top-aligned layout.
- The app uses broad dark gradients where Discord relies more on layered flat panels
  and subtle separators.
- Text, icon, and row sizing are generally smaller and lighter than the real Discord
  reference, reducing readability.
- Header, sidebar, content, member list, and bottom panel proportions differ from
  Discord's stable rail/sidebar/main/right-panel rhythm.
- Several UI areas look like independent cards rather than parts of one continuous
  application shell.
- Selected states and hover states are present but not consistently strong enough to
  scan quickly.
- The clone exposes dev/status information such as gateway readiness too prominently
  compared with Discord's user-facing shell.

### Server Rail

- Server icons and active indicators are less dense and less Discord-like.
- Text-based server initials are overused where the real rail relies on stronger
  avatar/folder visual distinction.
- Rail grouping, unread badges, mention badges, and current-server affordances need
  more consistent spacing and contrast.
- The rail consumes attention in the clone but does not yet provide the same scan
  quality as Discord's icon stack.

### Private Sidebar And Direct Messages

- The clone's private sidebar has fewer useful rows and less content density than
  the real DM sidebar.
- The real Discord DM list shows many conversations with avatars, status dots,
  activity snippets, unread badges, and group counts; the clone often appears empty
  or sparse.
- The `Clone scope` row is useful for development but makes the app feel less like
  Discord's primary user surface.
- Sidebar labels and metadata are too small in some screenshots.
- Bottom user controls in the private sidebar are split awkwardly from voice status
  and are less compact than Discord's bottom user panel.

### Friends Home

- The real Friends view keeps the header tabs, search, friend list, empty message,
  and right activity panel in a balanced desktop layout.
- The clone Friends Online view shows a huge empty main field and no rich right
  activity panel in the provided comparison.
- The clone's empty state is too small, too sparse, and placed too far into the open
  canvas.
- Friend tab spacing and selected-tab styling do not yet match Discord's compact
  rhythm.
- The search box is overly wide for an empty list and does not anchor the page as
  clearly as Discord's search field.
- The clone needs better demo relationship data so visual QA does not happen against
  an empty Friends state.

### Add Friend View

- Discord shows a title, explanatory text, large input row, send button, illustration,
  discovery CTA, and activity column.
- The clone's Add Friend content appears too low and isolated inside the main field.
- The add input and submit affordance are too small and not visually equivalent to
  Discord's form.
- The illustration and "find friends elsewhere" section are missing.
- Validation and disabled/success/error states are not prominent enough for a
  high-frequency Friends workflow.

### Server Sidebar

- Real Discord's server sidebar has clearer hierarchy: server header, Events/Boost,
  categories, active channels, channel row actions, and voice participant rows.
- The clone's category labels, row spacing, and active channel affordances are still
  too sparse or small.
- Channel creation and management actions are functional, but the visual treatment
  still reads more like an admin panel than Discord's channel list.
- Member/role management controls appear directly in the main member list in some
  views and feel developer-facing rather than Discord-like.

### Text Channel Timeline

- The real channel timeline contains dense message groups, date dividers, attachments,
  reactions, hover actions, and a readable message column.
- The clone text channel often has very few messages at the top and a large blank
  center, making the surface feel unfinished.
- Attachment/media preview parity is weak; the reference has image cards and hover
  toolbars while the clone mainly shows text/demo rows.
- Message grouping, timestamps, date dividers, reactions, and hover toolbars need a
  stronger Discord-like rhythm.
- The message composer is too low, thin, and detached from the timeline in some
  screenshots.
- Composer action icons are present, but their size, grouping, and baseline alignment
  need polish.

### Channel Header And Right Panels

- Header icon sizing and spacing are not close enough to Discord's compact toolbar.
- The clone's header subtitles and status pills can add noise compared with Discord's
  simpler channel header.
- The Friends activity panel and server member list need clearer Discord-like width,
  typography, and content density.
- The member list in the clone can look like a configuration surface when role
  controls are visible.
- Search and utility panels need stronger visual separation without feeling like
  unrelated cards.

### Bottom User And Voice Controls

- Real Discord's bottom area is compact: identity, mute, deafen, settings, and voice
  connection state are grouped with predictable icon sizing.
- The clone's bottom controls are spread across the footer, a voice-room strip, and a
  right status cluster, which weakens scanability.
- Voice connection state is visible, but "selected voice channel", "connected voice
  channel", "muted", "deafened", "speaking", and "screen sharing" should be clearer
  at a glance.
- The current bottom voice panel takes too much width and still does not match the
  real call-control emphasis.

### Voice Workspace And Screen Share

- Real Discord's voice view behaves like a call stage with large tiles and centered
  bottom controls.
- The clone voice workspace still looks like a channel dashboard with small cards
  near the top and too much empty canvas.
- The browser permission/demo notice banner is intrusive and should be reduced or
  moved to a secondary help/status area.
- The local participant tile and remote/empty participant tile proportions are too
  small and too card-like.
- Screen-share mode should emphasize the shared surface first, then participant
  tiles and call controls.
- When screen sharing is active, the clone should show live/share badges, quality
  metadata, participant labels, and a more Discord-like full-stage layout.
- If the browser cannot expose a real preview, the fallback should still occupy the
  correct visual hierarchy and clearly explain the limitation.

### Functionality And Interaction Reliability

- Several useful controls now open panels or notices, but the clone still needs a
  stricter distinction between real actions, local demo panels, and hidden deferred
  features.
- Friend add, friend row actions, right activity cards, pinned/threads/search panels,
  message reactions, attachment previews, channel notification menus, and voice
  workspace actions should be prioritized by frequency.
- Low-frequency commerce or external app features should stay hidden or explicitly
  scoped, not compete with the core Discord workspace.

### I18n And Copy

- Korean and English support exists, but visible UI still mixes English admin labels,
  backend-like terms, and Korean labels in places.
- Some copy is development-oriented instead of user-facing Discord-like copy.
- Language switching should be verified against dense real surfaces, not only
  settings and simple empty states.

### Responsiveness And Accessibility

- The side-by-side browser comparison effectively tests a constrained desktop width;
  the clone needs to be checked at half-window desktop widths, not only full-width.
- Current large empty areas hide potential responsive problems because there is not
  enough seeded content.
- Focus order, accessible labels, keyboard operation, and reduced-motion behavior
  must be rechecked after visual density changes.

## Sequential Remediation Process

Each stage must finish with verification, documentation updates, and a Git commit
pushed to `origin/main`. If verification finds layout overlap, broken behavior, or
unacceptable visual drift, add a sub-stage to fix it before moving on.

### Stage 9.0: Baseline Measurement And Screenshot Matrix

Goal: turn the comparison into measurable UI targets.

Tasks:

- Capture current clone screenshots for Friends Online, Add Friend, text channel,
  voice preview, voice connected, and screen-share states when practical.
- Use the user's FHD Chrome 100% screenshots as the baseline reference.
- Define target ratios without requiring DevTools measurements:
  - rail: compact Discord-like icon column
  - sidebar: dense channel/DM list width
  - header: single compact toolbar row
  - composer: stable bottom input with small icon controls
  - bottom user/voice panel: compact identity and call state, no duplicated status
    noise
  - voice stage: large centered tiles, compact call controls, speaking glow
- Record deviations and corrective sub-stages in this document.

Verification:

- `git diff --check`.
- FHD 100% baseline assumptions are documented.
- Any newly discovered implementation issue is recorded as a corrective sub-stage
  before later stages depend on it.

### Stage 9.1: Demo Data And Visual QA Content Density

Goal: make every major surface judgeable without relying on private Discord data.

Tasks:

- Seed enough safe original friends, DM rows, activities, server members, messages,
  reactions, date dividers, and attachments to test density.
- Add text channel fixture content that demonstrates grouped messages, image/file
  attachment cards, reactions, and hover/action states.
- Add voice fixture state for preview, connected, remote participant, and
  screen-share-like fallback visuals.
- Keep all names, handles, avatars, images, and message content original and safe.

Verification:

- Backend tests for seed/demo data integrity if backend data changes.
- Browser smoke that Friends, Add Friend, text channel, and voice states are not
  empty in demo mode.

### Stage 9.2: Global Shell Density And Design Tokens

Goal: align base proportions before polishing individual components.

Tasks:

- Tune global CSS tokens for rail, sidebars, headers, right panels, composer, and
  bottom panels.
- Reduce large unused empty areas and remove broad dashboard-like gradients from core
  Discord surfaces.
- Normalize typography, icon sizes, row heights, hover states, selected states, and
  separators.
- Hide or de-emphasize development indicators from the primary shell.

Verification:

- Frontend lint/build.
- Browser screenshots at full desktop, side-by-side desktop, and mobile widths.
- DOM overflow checks for document and primary scroll containers.

### Stage 9.3: Server Rail Parity

Goal: make the left rail scan like Discord.

Tasks:

- Improve icon density, active rail marker, unread badges, mention badges, folders,
  and add/discovery buttons.
- Replace weak text-initial treatment with stronger generated safe avatar treatments
  where real images are unavailable.
- Verify rail focus, hover, current-state, and tooltip behavior.

Verification:

- Browser smoke for `@me`, server switching, add server, discovery, and keyboard
  navigation.

### Stage 9.4: Private Sidebar And DM Density

Goal: make `@me` sidebar match the information density of Discord's DM list.

Tasks:

- Add enough safe DM rows with avatars, status dots, activities, unread/mention
  badges, and group member counts.
- Rework private sidebar row heights, typography, search input, selected state, and
  bottom user panel proportions.
- Move clone-scope/development information out of the main private navigation or
  make it dev-only.

Verification:

- Browser smoke for Friends, DM selection, DM send, unread display, language switch,
  and half-window width.

### Stage 9.5: Friends Home And Add Friend Parity

Goal: make Friends Online and Add Friend look like complete Discord surfaces.

Tasks:

- Restore desktop right activity panel with meaningful safe activity cards.
- Reposition Friends empty/list content to match Discord's top-aligned structure.
- Rebuild Add Friend with title, explanation, input/button row, illustration-like
  safe asset, validation states, and discovery CTA.
- Keep Online, All, Pending, Blocked, and Add Friend tabs useful.

Verification:

- Browser smoke for tab switching, add-friend validation, add-friend success/demo
  result, and right activity panel responsive behavior.

### Stage 9.6: Server Sidebar And Channel List Parity

Goal: make server navigation feel like Discord rather than an admin list.

Tasks:

- Tighten server header, Events/Boost rows, category labels, channel rows, row action
  icons, and voice participant rows.
- Move role/member management controls away from the always-visible member list into
  a management panel or contextual action path.
- Improve channel create state so it feels native while remaining functional.

Verification:

- Browser smoke for text/voice channel create, server invite, channel selection,
  voice selection, and long channel names.

### Stage 9.7: Text Channel Timeline And Composer Parity

Goal: make message browsing and sending look like Discord's primary chat surface.

Tasks:

- Add message groups, date dividers, attachment cards, reaction rows, and hover
  action toolbar parity.
- Tune message column width, avatar spacing, timestamp alignment, and author colors.
- Rework composer size, action icon alignment, input placeholder, focus ring, and
  bottom anchoring.
- Preserve send, edit, delete, reply, emoji insertion, upload metadata, and local
  templates.

Verification:

- Frontend lint/build.
- Browser smoke for send, reply, edit, delete, emoji insertion, upload metadata,
  hover actions, and no overlap at dense content.

### Stage 9.8: Header Panels And Right Sidebar Parity

Goal: make toolbar panels and right sidebars compact and useful.

Tasks:

- Tune header icon button size, search input width, tooltip behavior, and selected
  utility panel states.
- Rework threads, pinned, notifications, search, and inbox/help demo panels to feel
  like Discord overlays.
- Improve server member list and Friends activity panel density and responsive
  visibility.

Verification:

- Browser smoke for every visible header button and search flow.
- Keyboard focus order through each panel.

### Stage 9.9: Bottom User And Voice Control Parity

Goal: make the bottom identity and voice control area scan like Discord.

Tasks:

- Recompose the bottom user panel around identity, status, mute, deafen, and settings.
- Recompose connected voice state into a compact call summary with clear channel,
  mute/deafen/speaking/screen-share states.
- Reduce duplicated status clusters and remove low-value diagnostic noise from the
  primary footer.

Verification:

- Browser smoke for status cycle, mute, deafen, settings, voice join/leave, and
  half-window layout.

### Stage 9.10: Voice Stage And Screen Share Parity

Goal: make voice and screen sharing behave visually like a call stage.

Tasks:

- Convert voice workspace from top cards into a centered stage with large
  participant tiles and bottom call controls.
- Make selected, joining, connected, muted, deafened, speaking, screen sharing, and
  remote participant states obvious.
- Prioritize shared screen preview when screen sharing is active.
- Add live/share badges, participant labels, quality metadata, and fullscreen-style
  controls where useful.
- Keep browser permission failure and unsupported states concise and secondary.

Verification:

- Browser smoke with fake media for join, mute, deafen, screen-share start/stop, and
  leave.
- Screenshot comparison against the user's voice reference states.

### Stage 9.11: I18n, Copy, And Demo Scope Cleanup

Goal: keep the polished UI consistent in Korean and English.

Tasks:

- Audit all visible labels for Korean/English coverage.
- Replace development-oriented copy with user-facing Discord-like copy.
- Keep deferred features hidden or clearly scoped through concise local panels.
- Verify long English labels and Korean labels in sidebars, headers, settings, and
  composer panels.

Verification:

- Frontend lint/build.
- Browser smoke for Korean and English across Friends, Add Friend, text channel,
  voice stage, settings, and modal/panel surfaces.

### Stage 9.12: Responsive And Accessibility Regression

Goal: verify the denser UI is stable across realistic sizes and input methods.

Tasks:

- Check full desktop, side-by-side desktop, tablet-like, and mobile widths.
- Check keyboard operation for rail, sidebars, header panels, composer, settings,
  add-server, add-friend, channel create, and voice controls.
- Check visible focus, accessible names, `aria-current`, dialog labeling, and reduced
  motion behavior.
- Record screenshots and residual manual QA gaps.

#### Stage 9.12.1: Scrollbar Contrast Correction

Browser QA on the FHD baseline showed native light scrollbars inside dense channel
and message regions. Style scrollbars with dark track/thumb colors before final QA
so long lists remain visually integrated with the Discord-like shell.

Verification:

- Frontend lint/build.
- Browser screenshot artifacts and overflow metrics.
- Focus-order notes recorded in docs.

### Stage 9.13: Final Visual Parity QA

Goal: close the pass with repeatable evidence.

Tasks:

- Run backend tests if data contracts changed.
- Run backend lint if backend code changed.
- Always run frontend lint and production build.
- Run Docker smoke if Docker remains the active local environment.
- Capture final comparison screenshots for Friends Online, Add Friend, text channel,
  voice preview, and screen sharing.
- Update `PROJECT_CONTEXT.md`, `docs/README.md`, and `docs/implementation-plan.md`.

Verification:

- Required commands pass.
- Browser smoke for high-frequency workflows passes.
- Commit and push final Stage 9 status to `origin/main`.

## Information To Request From The User

The current screenshots are enough to start Stage 9.0 and Stage 9.1, but the
following information would make visual parity work more precise:

- Browser zoom level used for the comparison. Prefer 100%.
- Exact viewport or browser window sizes for the real Discord and clone captures.
- Real Discord screenshots, with private content blurred if needed, for:
  - Friends Online with non-empty friends.
  - Add Friend.
  - DM conversation.
  - Server text channel with dense messages and attachments.
  - Server voice channel before joining.
  - Voice connected.
  - Screen sharing active.
  - User Settings: Voice & Video, Appearance, Accessibility, Keybinds, Language.
- Chrome DevTools computed measurements from the real Discord page:
  - server rail width
  - private/sidebar width
  - channel sidebar width
  - member or activity panel width
  - header height
  - composer height
  - bottom user panel height
  - icon button size
  - channel/DM row height
  - friend row height
  - message row avatar size
  - common border radius
  - body, sidebar, and header font sizes/line heights
- Computed color values for key real Discord surfaces:
  - app background
  - sidebar background
  - active row background
  - hover row background
  - header border
  - composer background
  - input background
  - primary button
  - danger button
- If DevTools is difficult, screenshots with ruler overlays or a simple list of pixel
  measurements are enough.
- Do not provide cookies, localStorage, Discord tokens, auth headers, HAR files with
  credentials, or any private account secrets.

## First Confirmation Result

1차 확인 결과: the clone is not ready for another feature-count expansion. The next
best work is Stage 9 visual parity and density remediation.

Implementation should start with measurement, safe demo content density, and global
shell tokens. Only after those are corrected should the work continue into Friends,
server channels, composer, and voice stage polishing.
