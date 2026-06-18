# Discord Clone QA Remediation Development Plan - 2026-06-19

## Document Status

- Status: promoted from QA audit to implementation-ready remediation plan.
- Original purpose: record QA findings from `docs/prompts/discord-clone-qa-test-prompt.md`.
- Current purpose: drive concrete development work for each defect without
  rediscovering scope, owner files, or acceptance criteria.
- Execution rule: before fixing any item, read the finding, its development
  directives, its likely owner files, and the matching remediation stage. After a
  fix, update this document with fixed/residual status before moving to the next
  stage.
- Stage process: preserve the Stage 10/11 process. Work one remediation stage at a
  time, verify before advancing, add newly found sub-issues under the current
  finding or stage, and do not mark a finding fixed until regression checks pass.

## Scope

- QA prompt: `docs/prompts/discord-clone-qa-test-prompt.md`
- Real Discord reference:
  - `https://discord.com/channels/1517273681154412666/1517273681964040214`
  - User-provided real Discord screenshots from the current thread.
  - `https://discord.com/channels/@me` was opened in a new tab but redirected to
    Discord account re-login, so live `@me` checks were limited to user screenshots
    and the already logged-in Discord server tab.
- Clone URL: `http://localhost:5173/`
- Browser/runtime: Chrome, FHD-like desktop viewport, frontend dev server,
  backend API at `127.0.0.1:8000`, PostgreSQL connected.
- Safety: no real Discord settings, payment, leave, invite, or private-message send
  actions were performed. Clone messages were sent as local QA smoke data.
- Recheck note: a follow-up QA pass on the same date compared the open real Discord
  test-server tab with the clone Friends, server text, and settings surfaces. This
  pass confirmed several existing findings and added settings/accessibility/header
  ownership details below.

## Baseline Feature Matrix

| Surface | Expected clone scope | QA status |
| --- | --- | --- |
| Friends home | Friends tabs, search, friend list, Add Friend, activity panel | Partially working, visual hierarchy still weak |
| DM list and DM conversation | Open DMs and send local messages | Working smoke, layout and grouping need polish |
| Server rail | DM/server switching, selected/unread/voice indicators | Working, connected-state context remains ambiguous |
| Server sidebar | Text/voice channel list, create/settings/invite entry points | Working, too many always-visible tools |
| Text channel | Message send/edit/delete/reply affordances, composer | Send works, timeline and action visibility need redesign |
| Voice channel | Click row to join/switch, internal switch dialog, voice panel | Working smoke, cross-server state feedback needs fix |
| Context menus | App-owned menus instead of browser menu | Friend row works; full-surface coverage still required |
| Settings | Local settings shell, language/accessibility/voice sections | Present; some copy/policy decisions need tighter UI routing |
| Nitro/Shop/commercial | Deferred/hidden unless explicitly local-demo | Mostly hidden; exposed tool buttons still need classification |

## Follow-Up QA Recheck - 2026-06-19

- Real Discord reference used in recheck:
  - Open Chrome tab at
    `https://discord.com/channels/1517273681154412666/1517273681964040214`.
  - Observation was read-only. No real Discord messages, settings, invites, or voice
    actions were submitted.
- Clone surfaces rechecked:
  - Friends home.
  - Server text channel.
  - User settings.
- Additional confirmed gaps:
  - Friends uses a screen-specific `friends-header` while the shared `topbar`
    remains mounted at `0x0`; this indicates global header ownership is still
    inconsistent and should be fixed under QA-P1-03.
  - Server text channels still render persistent `message-actions` for many rows;
    this confirms QA-P1-01 is still active.
  - Hidden composer controls can remain in the DOM at `0x0` with accessible labels,
    such as local-template controls. This should be fixed under QA-P1-04 because
    hidden/deferred controls must not remain keyboard or screen-reader reachable.
  - The voice sidebar can display duplicated local participant text such as `나 나`
    while connected. This should be fixed under QA-P1-02 and QA-P2-09.
  - Settings pages still show clone-scope/developer-style explanatory cards in the
    primary UI and use wide document-like cards with large empty space. This needs a
    separate settings-surface remediation item, QA-P2-11.

## Development Execution Rules

1. Treat each QA item as a development work item, not only a design note.
2. Fix global component/style patterns at their shared owner first; avoid one-off
   screen patches unless the behavior is genuinely screen-specific.
3. Every visible control must end in one of four states: implemented, hidden,
   disabled with clear copy, or explicitly local-demo-only.
4. Browser-native `alert`, `confirm`, and default context menus must not be used for
   clone-owned workflows. Use app-owned modals, notices, popovers, and context menus.
5. For each fix, verify at least Friends, DM, server text, voice, and settings
   surfaces when the changed component or token is shared.
6. After any UI/layout fix, check Korean and English strings for overflow and
   confusing demo/debug copy.
7. After any realtime, voice, or persistence fix, test refresh behavior and, when
   possible, a second local session.

## Role Observations

### Horizontal Product QA

- Main flows are reachable: Friends, Add Friend, DM, server text channel, voice
  channel, settings.
- Several controls look fully usable before their behavior is clear: header
  notification/pin/member/search/invite tools, channel row invite/settings tools,
  composer expression controls, and server/member management tools.
- Clone-owned context menu exists for friend rows, but every major interactive
  surface still needs explicit right-click coverage.

### Vertical Workflow QA

- DM send smoke passed: local message appeared after pressing Enter.
- Server text-channel send smoke passed: local message appeared after pressing
  Enter.
- Voice row click opened the voice workspace. Switching to a voice channel in a
  different server displayed an internal confirmation dialog and Cancel dismissed it.
- After switching servers while connected elsewhere, the bottom voice card remained
  visible in the active server without enough guild/channel context.

### Discord Power User: Daily Chat And Server Use

- Real Discord uses a dense but layered shell: server rail, sidebar, header,
  content, member list, composer, and user panel each have distinct visual roles.
- The clone has the correct broad structure, but message action bars are visible
  too often, channel tools are too prominent, and the content surface feels more
  like an admin dashboard than a chat client in several places.

### Discord Power User: Voice And Presence

- Real Discord places voice participants directly under the active voice channel
  row and shows bottom-left connection state as a compact raised card.
- Clone shows voice participants and the cross-server switch dialog, but the voice
  state still follows the user across server navigation in a way that can be read as
  "connected in this active server."
- Speaking/mute/deafen/screen-share feedback needs a final pass against real
  Discord density and icon placement.

### Visual, Accessibility, Responsive QA

- Desktop 100% viewport was covered. Narrow/mobile and explicit keyboard-only
  passes were not completed in this run.
- Many controls have accessible names, which is positive.
- Visual issues are mostly shared component/style problems: persistent action
  buttons, heavy or uneven panel borders, large empty areas, and inconsistent row
  separation.

## Prioritized Findings

### QA-P1-01: Message timelines expose action bars as persistent UI

- Severity: P1
- Category: Design/visual parity, UX/state feedback
- Surface: server text channels and DMs
- Scope: global message timeline pattern
- Steps:
  1. Open a server text channel.
  2. Observe existing messages without hovering.
  3. Open a DM and observe message rows.
- Expected: Discord-like message rows show a clean timeline by default. Reply/edit/
  delete/more controls appear on hover/focus or in a contextual affordance.
- Actual: message action groups are visible on each message row, producing repeated
  controls and visual clutter.
- Evidence: clone DOM showed repeated `메시지 작업`, `답장`, `메시지 수정`,
  `메시지 삭제`, `메시지 작업 더보기` for each article.
- Likely owner files:
  - `frontend/src/components/ChatView.vue`
  - `frontend/src/components/DirectMessageView.vue`
  - `frontend/src/styles/base.css`
- Suggested fix direction:
  - Convert message action bars to hover/focus-revealed floating toolbars.
  - Keep keyboard-accessible alternatives via focus-within and message context menu.
  - Use one shared message-row/action styling pattern for DM and channel timelines.
- Development directives:
  1. Inspect `ChatView.vue` and `DirectMessageView.vue` for duplicated message-row
     markup and action rendering. Fix the shared visual contract before adding
     screen-specific overrides.
  2. Default rows may show only message content, author metadata, attachments,
     reactions, and edited/deleted state. Reply/edit/delete/more controls must be
     hidden until hover, keyboard focus, or context-menu activation.
  3. Keep keyboard-accessible actions through focus-visible controls or an app-owned
     message context menu.
  4. Render each date divider once per group. New messages must not create a second
     divider/border line above the row.
  5. Preserve existing send, edit, and delete REST behavior while changing visuals.
- Acceptance criteria:
  - Server and DM timelines share the same default/action visibility rules.
  - No message row displays repeated permanent action buttons.
  - Newly sent messages do not introduce duplicate dividers or double-line artifacts.
- Regression checks:
  - Message send/edit/delete still works.
  - Keyboard focus can reveal actions.
  - No duplicate date divider or double-line artifact appears above newly sent
    messages.

### QA-P1-02: Cross-server voice connection state is ambiguous

- Severity: P1
- Category: UX/state feedback, voice workflow
- Surface: server rail, channel sidebar, bottom user/voice panel
- Scope: global voice session behavior
- Steps:
  1. Join a voice channel in `SRS Lab`.
  2. Switch to `Study Hall`.
  3. Observe the bottom voice card and server rail.
  4. Click a voice channel in `Study Hall`.
- Expected: connected state remains tied to the original guild/channel, the bottom
  card clearly names that guild/channel, and switching voice channels requires an
  app-owned confirmation.
- Actual: confirmation dialog appears correctly, but while browsing another server
  the bottom card can read like the active server is already connected.
- Evidence: clone showed `voice-room 연결됨` in the bottom voice card after server
  switch, while the rail indicated another server had voice state.
- Likely owner files:
  - `frontend/src/composables/useVoiceSessionController.ts`
  - `frontend/src/stores/voicePresence.ts`
  - `frontend/src/components/ChannelSidebar.vue`
  - `frontend/src/components/VoicePanel.vue`
  - `frontend/src/styles/base.css`
- Suggested fix direction:
  - Always render connected guild + channel in the bottom voice card.
  - If active guild differs from connected guild, use a "connected elsewhere" state
    and provide a clear jump/leave action.
  - Preserve the internal switch dialog; do not use browser-native confirm.
- Development directives:
  1. Treat voice session ownership as `{ guildId, guildName, channelId,
     channelName, connectedUserIds, localState }`.
  2. Keep server rail voice indicators attached only to the guild that owns the
     active voice session.
  3. In `VoicePanel.vue`, always render connected guild and channel. If the active
     guild differs, show a compact "connected elsewhere" state with jump and leave
     actions.
  4. In `ChannelSidebar.vue`, show participants only under the owning voice channel.
     Do not mirror local participants into same-named channels in other servers.
  5. Cross-server voice switches must use the app-owned dialog, never browser-native
     confirm.
- Acceptance criteria:
  - Browsing another server while connected cannot be mistaken for being connected
    to that server.
  - Cancel keeps the existing voice session unchanged.
  - Confirm cleanly leaves the old channel and joins the new one.
- Regression checks:
  - Join, leave, switch server, switch voice channel.
  - Server rail voice indicator remains on the connected server only.
  - Bottom card never implies connection to the wrong active server.

### QA-P1-03: Header, sidebar, and content layers still lack real Discord layering

- Severity: P1
- Category: Design/visual parity
- Surface: global app shell, Friends, server, DM
- Scope: global layout pattern
- Steps:
  1. Compare real Discord server and Friends screenshots to clone.
  2. Inspect rail, private/server sidebar, header, tab row, content, and composer.
- Expected: Discord-like layered shell where the server rail and top title/header
  appear connected, while search/tab rows sit on a second surface layer.
- Actual: clone broadly matches columns, but several areas still read as one flat
  grid. Search rows, tab rows, header boundaries, and sidebar surfaces do not always
  sit on convincing stacked layers.
- Evidence: real Discord server showed rail 72px, sidebar about 303px, 48px channel
  header, and a separate composer layer. Clone DOM uses the right broad regions but
  visual density differs.
- Likely owner files:
  - `frontend/src/App.vue`
  - `frontend/src/components/ServerRail.vue`
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/components/ChannelSidebar.vue`
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/styles/base.css`
- Suggested fix direction:
  - Define explicit shell layers: app base, rail, sidebar slab, top bar, content
    panel, composer/user floating cards.
  - Apply shared top/header seam tokens globally rather than screen-specific fixes.
  - Recheck Friends, server text, DM, voice, and settings after one layer change.
- Development directives:
  1. Implement shared shell tokens/classes in `base.css` first: app base, rail base,
     sidebar slab, top header layer, tab/search layer, content layer, composer/user
     floating cards.
  2. The server rail and top title/header seam must read as one continuous shell
     layer. Search/start rows and Friends tabs should sit on a second layer below
     the title/header line.
  3. Avoid adding extra borders only to hide seams. Correct layer background,
     z-index, and spacing ownership instead.
  4. Recheck Friends, server text, DM, voice, and settings after token changes so
     screen-specific layer styles do not diverge.
  5. Keep fixed header and composer dimensions stable at FHD 100 percent and
     side-by-side widths.
  6. Remove screen-specific fake headers that leave the shared `topbar` mounted at
     `0x0`. Friends, DM, server text, voice, and settings must either use the shared
     header layer or intentionally opt out without leaving inaccessible remnants.
- Acceptance criteria:
  - The rail/header/sidebar top area reads as a Discord-like stacked shell.
  - No leftover seam line remains between the server rail and active header.
  - Search/tab rows sit below the main header layer without vertical jumps.
  - No primary header element has a `0x0` layout while a replacement header is doing
    its job elsewhere.
- Regression checks:
  - No old seam line remains between rail and active top header.
  - Search/start controls align with Discord-like tab row placement.
  - FHD 100% and side-by-side views keep the same hierarchy.

### QA-P1-04: Visible controls exceed confirmed behavior

- Severity: P1
- Category: Feature out of scope but exposed, feature incomplete
- Surface: header tools, channel tools, composer tools, member/server management
- Scope: global visible-control policy
- Steps:
  1. Open server text channel.
  2. Observe header and channel-row tools.
  3. Open composer expression/file controls.
  4. Open settings and compare scope copy.
- Expected: visible controls either work, are clearly disabled, or are hidden when
  outside current clone scope.
- Actual: many controls remain visible and active-looking before the user can know
  whether they are implemented locally, demo-only, or deferred.
- Evidence: clone exposed notification, pin, member toggle, search, invite, channel
  settings, message actions, upload, emoji, and member management entry points.
- Likely owner files:
  - `frontend/src/App.vue`
  - `frontend/src/components/ChatView.vue`
  - `frontend/src/components/ChannelSidebar.vue`
  - `frontend/src/components/MemberList.vue`
  - `frontend/src/components/ServerAddDialog.vue`
  - `frontend/src/i18n/index.ts`
- Suggested fix direction:
  - Create a visible-control decision matrix: implement, hide, disabled-with-copy,
    or local-demo-only.
  - Apply consistent disabled styling and copy for local-only features.
  - Prioritize implementing search/start conversation, invite preview, message
    operations, and channel/server CRUD before adding decorative controls.
- Development directives:
  1. Build a control inventory before code edits: header buttons, sidebar buttons,
     channel tools, member actions, composer controls, server rail actions, settings
     entries, and voice controls.
  2. For every control, choose exactly one outcome: implement now, hide, disable
     with copy, or keep as local-demo-only.
  3. Prioritize high-value Discord-like flows: search/start conversation, invite
     preview/join, message operations, channel create/delete where exposed, and
     safe server/member actions.
  4. Hide or demote low-value decorative/commercial controls from primary surfaces.
  5. Disabled controls must show concise app-owned feedback and must not look like
     successful primary actions.
  6. Hidden or deferred controls must also be removed from keyboard navigation and
     the accessibility tree. Do not leave `0x0` buttons with labels such as local
     templates, gifts, apps, or commercial controls.
- Acceptance criteria:
  - No primary visible control silently does nothing.
  - Exposed local/demo controls are visually secondary and clearly labeled.
  - Deferred commercial or destructive features are hidden unless explicitly scoped.
  - Hidden controls are not reachable by keyboard or exposed as active controls to
    assistive technology.
- Regression checks:
  - No visible control does nothing silently.
  - Deferred commercial features remain hidden or clearly non-primary.

### QA-P1-05: Friends and DM surfaces still feel less structured than Discord

- Severity: P1
- Category: Design/visual parity, UX/state feedback
- Surface: Friends home, Add Friend, DM sidebar, DM conversation
- Scope: shared private-channel surfaces
- Steps:
  1. Open Direct Messages.
  2. Switch Friends tabs.
  3. Open Add Friend.
  4. Open an individual DM and send a local smoke message.
- Expected: Friends tabs, list rows, activity cards, and DM conversation intro
  should have clear Discord-like hierarchy and spacing.
- Actual: functionality mostly works, but the activity panel is thin, friend rows
  and DM rows still rely heavily on text density, and the DM intro/timeline lacks
  the visual polish of real Discord.
- Evidence: Add Friend and All tabs rendered; DM send worked; visual hierarchy was
  weaker than the provided Discord Friends screenshots.
- Likely owner files:
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/components/DirectMessageView.vue`
  - `frontend/src/styles/base.css`
  - `frontend/src/i18n/index.ts`
- Suggested fix direction:
  - Rebuild Friends list rows around avatar, primary name, secondary status, and
    right-side compact actions.
  - Make the activity panel richer but not noisy.
  - Align DM intro and message grouping with Discord: large identity block only at
    conversation start, then compact message rows.
- Development directives:
  1. Treat Friends and DM as one private-channel product area. Align row heights,
     selected states, avatar/status placement, and compact right-side actions.
  2. Friends tabs must be clearly interactive and visually segmented. Keep default
     order as All, Online, Pending, Add Friend; keep Blocked secondary unless a
     dedicated route/menu is implemented.
  3. Friend rows need enough vertical rhythm that secondary status text does not
     collapse separation between users.
  4. DM intro should use a Discord-like identity block only at conversation start;
     ordinary messages should use compact grouped rows.
  5. Activity cards should show meaningful local data or be hidden when no useful
     activity exists.
- Acceptance criteria:
  - Friends rows, DM sidebar rows, and DM timeline rows feel related but not cramped.
  - Add Friend is visually distinct from passive tabs.
  - Korean and English labels fit without crowding or overlap.
- Regression checks:
  - Friends tab order remains `모두`, `온라인`, `대기 중`, `친구 추가`.
  - Add Friend form remains usable in Korean and English.
  - DM messages persist after refresh.

### QA-P2-06: Composer and bottom user panel dimensions are still inconsistent

- Severity: P2
- Category: Design/visual parity, responsive/accessibility
- Surface: global bottom area
- Scope: shared bottom layout
- Steps:
  1. Compare a server text channel composer with the sidebar user panel.
  2. Join voice and compare connected voice panel height.
- Expected: Discord-like bottom controls use compact raised cards with consistent
  vertical rhythm and enough padding above separators.
- Actual: current controls are functional, but composer/user/voice panel heights
  still differ visually and can make the bottom area feel heavier than Discord.
- Evidence: clone DOM showed message input region around 70px high and user/voice
  sections changing from 68px to 122px when connected.
- Likely owner files:
  - `frontend/src/components/ChannelSidebar.vue`
  - `frontend/src/components/ChatView.vue`
  - `frontend/src/components/DirectMessageView.vue`
  - `frontend/src/styles/base.css`
- Suggested fix direction:
  - Define shared bottom-card height and padding tokens.
  - Keep voice-connected card compact and context-rich.
  - Ensure text never touches card borders at FHD and side-by-side widths.
- Development directives:
  1. Define bottom-area tokens for card height, vertical padding, horizontal padding,
     icon button size, and gap. Apply them to the user panel, connected voice card,
     text composer, and DM composer.
  2. The disconnected user panel should be a raised card above the sidebar base, not
     just text placed on the sidebar background.
  3. The connected voice card should sit above the user panel using the same raised
     card language, stay compact, and never overlap or clip channel text.
  4. Composer and sidebar bottom cards should align vertically at the same optical
     center where layouts share a bottom baseline.
  5. Remove decorative arcs, clipped borders, or accidental half-shapes created by
     overlapping connected-state styles.
- Acceptance criteria:
  - Disconnected and connected bottom states look like intentional Discord-like
    floating cards.
  - Text has enough padding from borders in Korean and English.
  - Composer, user, and voice panels do not visually fight for the same bottom area.
- Regression checks:
  - Disconnected and connected states align with composer vertical center.
  - No overlap with Windows taskbar/browser chrome at FHD 100%.

### QA-P2-07: Text-channel empty/onboarding state is not Discord-like enough

- Severity: P2
- Category: Design/visual parity, UX
- Surface: newly created/empty server text channels
- Scope: server text channel
- Steps:
  1. Open real Discord test server with a fresh text channel.
  2. Open clone text channel with little or no content.
- Expected: empty server channels should show a concise channel intro or Discord-like
  welcome/onboarding state that fits the channel context.
- Actual: clone uses a generic `#general 메시지와 파일 미리보기가 이 채널에 표시됩니다.`
  style message or dense local data depending on the server, with less polished
  onboarding than Discord.
- Likely owner files:
  - `frontend/src/components/ChatView.vue`
  - `frontend/src/i18n/index.ts`
  - `frontend/src/styles/base.css`
- Suggested fix direction:
  - Add a reusable empty-channel intro component with channel name, one-line helper,
    and no excessive demo/debug copy.
  - Keep server welcome checklist only where it adds value.
- Development directives:
  1. Add a reusable empty-channel intro pattern owned by `ChatView.vue` or a small
     child component if reuse becomes necessary.
  2. Show the intro only when the channel has no real messages after load. It must
     disappear cleanly when the first message is sent.
  3. Copy must be concise and contextual: channel name, "this is the start" style
     text, and one optional action only if the action is implemented.
  4. Do not show file-preview, debug, or demo wording in empty channels.
  5. Do not render date dividers for empty channels.
- Acceptance criteria:
  - Empty text channels have a polished first-use state.
  - Existing channels keep normal timeline grouping.
  - First sent message replaces the empty state without duplicate separators.
- Regression checks:
  - Empty channel, existing channel, and newly sent first message all render without
    duplicate dividers.

### QA-P2-08: Context menu coverage is incomplete until proven global

- Severity: P2
- Category: Feature missing, UX/state feedback
- Surface: server rail, channels, members, messages, DM/friend rows
- Scope: global context menu policy
- Steps:
  1. Right-click a friend row.
  2. Repeat for server, channel, message, member, empty content, and composer.
- Expected: Discord-like app-owned menus where context is meaningful; browser menu
  should not appear on app surfaces.
- Actual: friend row showed an app-owned menu. Other major surfaces were not fully
  covered in this run and must not be assumed complete.
- Likely owner files:
  - `frontend/src/composables/useContextMenuController.ts`
  - `frontend/src/App.vue`
  - `frontend/src/components/ServerRail.vue`
  - `frontend/src/components/ChannelSidebar.vue`
  - `frontend/src/components/ChatView.vue`
  - `frontend/src/components/MemberList.vue`
- Suggested fix direction:
  - Build a context-menu matrix by surface.
  - Add app-owned menus for each meaningful surface.
  - Suppress browser context menu on the app shell only when the app can provide an
    appropriate fallback.
- Development directives:
  1. Create a surface matrix for right-click behavior: server rail item, server
     sidebar header, text channel row, voice channel row, member row, friend row, DM
     row, message row, composer, empty content, and app background.
  2. Use `useContextMenuController.ts` as the single owner for menu state and
     dismissal behavior.
  3. Provide app-owned menus only where meaningful actions exist. For surfaces with
     no meaningful action, suppress the browser menu only inside the clone app shell
     and show no menu.
  4. Menus must close on outside click, Escape, route/server/channel changes, and
     opening another menu.
  5. Destructive or not-yet-implemented menu items must be hidden or disabled with
     clear copy.
- Acceptance criteria:
  - Browser default context menu does not appear on major clone app surfaces.
  - Right-click behavior is consistent across Friends, DM, server, message, and
    member surfaces.
  - Context menus do not remain stuck after clicking elsewhere.
- Regression checks:
  - Menus close on outside click, Escape, route change, and opening another menu.

### QA-P2-09: Voice workspace has too much empty space and weak participant density

- Severity: P2
- Category: Design/visual parity, voice workflow
- Surface: voice channel workspace
- Scope: voice panel
- Steps:
  1. Click a voice channel.
  2. Observe participant tiles, empty participant state, and top actions.
- Expected: voice workspace should balance participant preview, empty states, and
  primary actions without excessive blank area.
- Actual: voice workspace works, but one-person state and empty participant card are
  larger and less information-dense than real Discord.
- Likely owner files:
  - `frontend/src/components/VoicePanel.vue`
  - `frontend/src/components/VoiceAudioSink.vue`
  - `frontend/src/components/VoiceVideoSink.vue`
  - `frontend/src/styles/base.css`
- Suggested fix direction:
  - Reduce one-person/empty card footprint.
  - Keep primary actions near the channel title and voice participant context.
  - Show speaking state around avatar/tile border in the Discord-like pattern.
- Development directives:
  1. Rework voice workspace density around participant count. One-person and empty
     states should not consume the same space as a large multi-participant call.
  2. Keep join, leave, and screen-share actions near the voice channel header and
     current session state.
  3. Speaking state should be visible around avatar/tile borders and in the channel
     sidebar participant row.
  4. Screen-share preview should scale into available space without forcing unrelated
     empty-state cards to dominate the view.
  5. Keep hidden audio/video sink lifecycle behavior intact while changing layout.
  6. De-duplicate local participant rendering. A connected user should appear once
     under the owning voice channel and once, at most, in the workspace participant
     grid.
- Acceptance criteria:
  - Voice workspace presents current participants and session state with less blank
    space.
  - Speaking, mute, and screen-share states are visible in both sidebar and
    workspace.
  - Single participant, empty, and screen-sharing layouts remain stable.
  - Participant labels are not duplicated, including local-user labels such as `나`.
- Regression checks:
  - Join, leave, mute, deafen, screen-share start/stop.
  - Single participant and multi-participant layouts remain stable.

### QA-P2-10: Responsive, keyboard, and multi-session coverage remain incomplete

- Severity: P2
- Category: Accessibility/responsive, realtime/persistence
- Surface: global
- Scope: QA coverage gap
- Steps:
  1. Repeat this audit at 1280x720, tablet, and mobile widths.
  2. Repeat keyboard-only navigation for Friends, DM, server text, and voice.
  3. Use a second session for realtime message/voice confirmation.
- Expected: clone should be usable across desktop/narrow widths and keyboard paths,
  and realtime should work across sessions.
- Actual: this run covered one desktop Chrome viewport and one local session.
- Likely owner files:
  - `frontend/src/styles/base.css`
  - `frontend/src/composables/useGateway.ts`
  - `frontend/src/stores/guilds.ts`
  - `frontend/src/stores/dms.ts`
  - `frontend/src/composables/useVoiceSessionController.ts`
- Suggested fix direction:
  - Add a dedicated post-fix QA pass for viewport and keyboard coverage.
  - Run two-session smoke for server text, DM, and voice state.
- Development directives:
  1. After R1-R7 fixes, run this as a final QA stage instead of treating it as a
     passive residual risk.
  2. Cover FHD 100 percent, 1280x720, one tablet/narrow width, and one mobile width.
  3. Run keyboard-only flows for Friends tabs, Add Friend, DM open/send, server text
     send/actions, voice join/leave, settings open/close, context menus, and dialogs.
  4. Run two-session local smoke for server text messages, DM messages, and voice
     state. If a second browser/device is unavailable, document the exact blocker.
  5. Record command verification and browser smoke results in this document or a
     linked QA artifact.
- Acceptance criteria:
  - Responsive and keyboard coverage is explicitly passed or has documented blockers.
  - Two-session realtime behavior is tested or clearly marked pending with reason.
  - No P1 item remains unresolved before new feature work resumes.
- Regression checks:
  - No horizontal overflow at 1280x720.
  - Tab order is logical.
  - Realtime updates appear without refresh.

### QA-P2-11: Settings surface is too document-like and exposes clone-scope copy

- Severity: P2
- Category: Design/visual parity, feature out of scope but exposed, UX/state feedback
- Surface: user settings
- Scope: settings shell and settings content panels
- Steps:
  1. Open user settings from the bottom user panel.
  2. Inspect `내 계정`, `음성 및 비디오`, `화면`, `접근성`, `단축키`, and
     `언어 및 시간`.
  3. Compare with real Discord settings screenshots and expected clone scope.
- Expected: settings should feel like a Discord-like settings panel with clear
  categories, compact setting rows, toggles, selects, sliders, and only user-facing
  scope explanations when needed.
- Actual: settings are functional but read partly like a project/status document.
  Cards such as support scope and clone-scope decisions expose implementation
  policy copy in the primary UI, while the main content uses large cards and leaves
  excessive empty space.
- Evidence: clone settings showed `지원 범위`, `클론 범위 결정`, local-session
  explanations, and wide document-like cards in the main account page.
- Likely owner files:
  - `frontend/src/components/UserSettings.vue`
  - `frontend/src/styles/base.css`
  - `frontend/src/i18n/index.ts`
- Suggested fix direction:
  - Convert settings pages from explanatory cards into Discord-like setting rows.
  - Keep clone-scope information in small disabled-state helper copy only where a
    user tries to access unsupported account/security/payment/external-link features.
  - Use controls that match the setting type: toggles, sliders, selects, radio
    groups, and compact buttons instead of large static cards.
- Development directives:
  1. Audit every settings page for project/internal wording. Remove or demote copy
     that explains implementation scope instead of user-facing behavior.
  2. Rebuild account/session panels as compact rows with labels, values, and clear
     disabled states. Avoid large static cards unless the section is a genuine
     preview.
  3. Keep settings navigation density consistent with Discord: left category list,
     content width constraint, strong section headings, and row-level controls.
  4. Unsupported real Discord account/security/payment/external-link features must
     be hidden or disabled with concise local-only copy, not described as engineering
     policy in the main flow.
  5. Verify settings close, Escape/outside behavior if supported, keyboard focus,
     and Korean/English text fit after layout changes.
- Acceptance criteria:
  - Settings no longer reads like a project documentation page.
  - Unsupported settings are user-facing and concise, not implementation-policy
    explanations.
  - Account, voice/video, display, accessibility, shortcuts, and language pages use
    consistent row-based layout and controls.
- Regression checks:
  - Settings open/close still works.
  - Locale and status changes still apply.
  - Voice/display/accessibility controls remain reachable and labeled.

## Implementation Process Backlog

## Remediation Execution Log

### R1 - Visible-control policy

- Status: completed.
- Goal: every visible control must be implemented, hidden, disabled with concise
  copy, or clearly local-demo-only. Hidden/deferred controls must not remain
  keyboard-reachable or exposed as active assistive-technology controls.
- Findings reviewed:
  - QA-P1-04 visible controls exceed confirmed behavior.
  - QA-P1-01 message actions are still too visible by default.
  - QA-P2-08 context menu coverage requires app-owned behavior rather than browser
    default context menus.
- Target files reviewed:
  - `frontend/src/App.vue`
  - `frontend/src/components/ChatView.vue`
  - `frontend/src/components/ChannelSidebar.vue`
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/components/MemberList.vue`
  - `frontend/src/components/ServerAddDialog.vue`
  - `frontend/src/styles/base.css`
  - `frontend/src/i18n/index.ts`
- Control inventory:
  - Header notification/pin/search controls: implemented as local panels.
  - Header member-list control: implemented as a real member-list toggle.
  - Header invite control: implemented through the invite flow.
  - Channel create controls: implemented through channel creation forms.
  - Channel invite controls: implemented through the invite flow.
  - Channel settings controls: app-owned local notice/settings routing; remains
    secondary and is not a silent no-op.
  - Composer upload/emoji/template controls: implemented as local composer panels;
    optional template control must stay out of the accessibility tree while hidden.
  - Friend message and more controls: implemented through DM open and app-owned
    menu; hidden row actions must stay out of the accessibility tree until row
    hover/focus/selection.
  - Member management controls: implemented behind the management toggle.
  - Server rail create/discovery controls: implemented through modal flows.
  - Voice controls: implemented or disabled with native disabled state when not
    connected.
- Implementation:
  - `frontend/src/styles/base.css` now applies `visibility: hidden` to hidden
    channel-row and friend-row action groups, then restores visibility on
    hover/focus/active/connected states. This prevents invisible secondary controls
    from remaining keyboard-reachable while preserving Discord-like hover density.
- Newly found R1 sub-issue:
  - R1.1: message row actions also need the same strict visibility/accessibility
    policy; this will be fixed in R3 because that stage owns the shared message
    timeline pattern and action toolbar behavior.
- Verification:
  - `frontend/node_modules/.bin/oxlint.cmd .` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vue-tsc.cmd -b` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vite.cmd build` passed with bundled Node on PATH.
  - Native `npm` commands could not run because `npm` is not available in the
    current PowerShell PATH; direct local binary execution was used for equivalent
    frontend lint/type/build verification.

### R2 - Shared shell/layer system

- Status: completed.
- Goal: make rail/sidebar/header/content ownership explicit and remove hidden
  replacement headers from active screens.
- Findings reviewed:
  - QA-P1-03 header, sidebar, and content layers still lack real Discord layering.
  - QA-P1-04 hidden controls and hidden header remnants must not stay reachable.
- Target files reviewed:
  - `frontend/src/App.vue`
  - `frontend/src/components/ServerRail.vue`
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/components/ChannelSidebar.vue`
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/styles/base.css`
- Existing state:
  - The global `.topbar` was always rendered and then hidden by
    `.app-shell.friends-mode .topbar { display: none; }` while `FriendsHome` owned
    the visible Friends tab/header layer.
  - Rail/sidebar/header colors were already close to Discord but used fewer
    explicit ownership tokens than the remediation plan required.
- Implementation:
  - `frontend/src/App.vue` now uses `showWorkspaceTopbar` so the shared topbar is
    not rendered at all on the Friends home surface. This removes the hidden
    replacement-header remnant instead of relying on CSS.
  - `frontend/src/styles/base.css` now defines `--surface-header` and
    `--surface-secondary-layer` and applies them to the topbar and sidebars.
  - The obsolete Friends-only topbar hiding rule was removed.
- Verification:
  - `frontend/node_modules/.bin/oxlint.cmd .` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vue-tsc.cmd -b` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vite.cmd build` passed with bundled Node on PATH.

### R3 - Message timeline redesign

- Status: completed.
- Goal: server and DM timelines must share a clean default message-row pattern,
  with message actions hidden until hover, keyboard focus, or an open app-owned
  menu. Date dividers must not stack with row borders.
- Findings reviewed:
  - QA-P1-01 message timelines expose action bars as persistent UI.
  - R1.1 message row actions need the strict hidden-control accessibility policy.
- Target files reviewed:
  - `frontend/src/components/ChatView.vue`
  - `frontend/src/components/DirectMessageView.vue`
  - `frontend/src/styles/base.css`
- Existing state:
  - Server message actions were visually hidden with opacity but could still behave
    like active controls before row hover/focus.
  - DM rows already used the same `.message-row` base visual pattern but did not
    expose a row focus target for keyboard context-menu workflows.
  - Date divider behavior already avoided first-row double borders by applying row
    borders only to adjacent message rows.
- Implementation:
  - Server message rows now receive an `options-open` class and `tabindex="0"` so
    keyboard focus can intentionally reveal the action toolbar.
  - DM message rows now also use `tabindex="0"` to share the same focusable row
    contract.
  - `frontend/src/styles/base.css` now gives focused message rows a visible focus
    outline and hides `.message-actions` with `visibility: hidden` until
    hover/focus/options-open state.
  - The R1.1 sub-issue is resolved by the shared message-action visibility policy.
- Verification:
  - `frontend/node_modules/.bin/oxlint.cmd .` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vue-tsc.cmd -b` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vite.cmd build` passed with bundled Node on PATH.

### R4 - Friends and DM parity pass

- Status: completed.
- Goal: make Friends and DM surfaces feel like one private-channel product area
  with clear tab order, roomier rows, and a less document-like DM intro.
- Findings reviewed:
  - QA-P1-05 Friends and DM surfaces still feel less structured than Discord.
- Target files reviewed:
  - `frontend/src/components/FriendsHome.vue`
  - `frontend/src/components/PrivateChannelSidebar.vue`
  - `frontend/src/components/DirectMessageView.vue`
  - `frontend/src/styles/base.css`
- Existing state:
  - Friends tabs were rendered in the right visual order, but the default tab was
    `online`, making the `All` tab less prominent than the remediation target.
  - Friend rows had action hiding and row separation, but the status/activity line
    still read cramped at a glance.
  - DM conversation intro exposed status, message count, and participants as a
    large metadata block, which made the chat surface feel more like a profile
    document.
- Implementation:
  - Friends now opens on the `All` tab while preserving the visual order of All,
    Online, Pending, and Add Friend.
  - Friend rows gained slightly more vertical rhythm and clearer spacing around
    secondary activity text.
  - DM intro removed the large metadata definition list and keeps only the identity
    start block plus compact participant chips.
- Verification:
  - `frontend/node_modules/.bin/oxlint.cmd .` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vue-tsc.cmd -b` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vite.cmd build` passed with bundled Node on PATH.

### R5 - Voice state and workspace pass

- Status: completed.
- Goal: make connected voice ownership explicit, prevent cross-server ambiguity,
  and reduce excessive one-person/empty voice workspace space.
- Findings reviewed:
  - QA-P1-02 cross-server voice connection state is ambiguous.
  - QA-P2-09 voice workspace has too much empty space and weak participant density.
- Target files reviewed:
  - `frontend/src/App.vue`
  - `frontend/src/components/ChannelSidebar.vue`
  - `frontend/src/components/VoicePanel.vue`
  - `frontend/src/composables/useVoiceSessionController.ts`
  - `frontend/src/stores/voicePresence.ts`
  - `frontend/src/styles/base.css`
  - `frontend/src/i18n/index.ts`
- Existing state:
  - Voice ownership was already tracked separately by connected guild/channel.
  - The bottom voice card showed the connected channel but did not always show the
    owning guild, so another server could still appear connected at a glance.
  - One-person and empty voice workspace tiles still used a large vertical
    footprint.
- Implementation:
  - `VoicePanel.vue` now receives `connectedGuildName` and `connectedElsewhere`.
  - `App.vue` computes whether the active guild differs from the connected guild and
    passes that state to the bottom voice card.
  - The bottom voice card now always renders `guild / channel` when connected and
    uses a distinct "connected elsewhere" state when browsing another server.
  - Voice workspace tile minimum heights and grid width were reduced for denser
    one-person and empty states.
- Verification:
  - `frontend/node_modules/.bin/oxlint.cmd .` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vue-tsc.cmd -b` passed with bundled Node on PATH.
  - `frontend/node_modules/.bin/vite.cmd build` passed with bundled Node on PATH.

### Remediation Stage R1: Visible-control policy

1. Inventory every visible button/control by surface.
2. Classify each as implement, hide, disabled-with-copy, or local-demo-only.
3. Apply the decision globally.
4. Verify no control silently does nothing.

### Remediation Stage R2: Shared shell/layer system

1. Define global shell layer tokens in `base.css`.
2. Rework rail/sidebar/header/content/composer seams in one pass.
3. Validate Friends, server text, DM, voice, and settings at FHD 100%.

### Remediation Stage R3: Message timeline redesign

1. Extract one shared message-row visual pattern for server and DM timelines.
2. Hide action bars until hover/focus/context-menu.
3. Fix date-divider/double-line behavior for first message, old messages, and new
   messages.
4. Verify send/edit/delete/reply behavior.

### Remediation Stage R4: Friends and DM parity pass

1. Tighten Friends tabs, rows, search, and activity panel.
2. Tighten DM sidebar row density and selected state.
3. Rework DM intro and compact message grouping.
4. Verify Korean/English copy.

### Remediation Stage R5: Voice state and workspace pass

1. Make connected guild/channel explicit in the bottom card.
2. Add "connected elsewhere" state when browsing another server.
3. Recheck voice row participant display and speaking indicators.
4. Reduce one-person voice workspace empty space.

### Remediation Stage R6: Context-menu and popover closure pass

1. Build a context menu coverage matrix for server, channel, member, message, DM,
   friend, and empty app surfaces.
2. Implement missing menus or intentional no-op suppression rules.
3. Verify outside click, Escape, and route-change dismissal.

### Remediation Stage R7: Empty/onboarding and invite/search flows

1. Replace generic empty-channel copy with a Discord-like reusable empty-state
   component.
2. Implement or hide incomplete invite and search/start conversation surfaces.
3. Verify new server/channel/DM first-use flows.

### Remediation Stage R8: Settings surface polish

1. Convert settings content from document-like cards to Discord-like setting rows.
2. Remove or demote clone-scope/project-policy copy from primary settings surfaces.
3. Normalize account, voice/video, display, accessibility, shortcuts, and language
   layouts.
4. Verify settings keyboard navigation, close behavior, locale/status behavior, and
   Korean/English text fit.

### Remediation Stage R9: Final responsive/accessibility/realtime QA

1. Test FHD 100%, 1280x720, tablet, and mobile/narrow widths.
2. Test keyboard-only operation for core flows.
3. Test two-session realtime text, DM, and voice state.
4. Update this document with fixed/residual status.

## Must Fix Before New Feature Work

1. QA-P1-01 message action clutter and message timeline parity.
2. QA-P1-02 cross-server voice state ambiguity.
3. QA-P1-03 shell layer/header/sidebar parity.
4. QA-P1-04 visible controls that exceed confirmed behavior.
5. QA-P1-05 Friends/DM hierarchy and density.

## Residual Risks

- Live `@me` inspection could not be completed because a new Discord tab required
  re-login. Use existing user screenshots or ask the user to keep an authenticated
  `@me` tab open if exact live observation is needed later.
- No real Discord screenshots or private identifiers were stored in this document.
- Browser screenshot capture for the clone timed out once in this run; DOM and
  manual visual observation were used as evidence instead.
- No code changes were made as part of this QA pass.
