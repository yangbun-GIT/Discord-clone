# Discord Clone QA Test Prompt

Use this prompt when the user asks to audit, QA, test, or find missing/broken
behavior in the Discord clone before a later implementation pass.

## Mission

You are not implementing fixes in this pass unless the user explicitly asks for
fixes. Your mission is to test the current clone broadly and deeply, compare it
against the expected Discord-like behavior, and produce a structured defect and
improvement document that later implementation work can execute.

The audit must distinguish:

- Not implemented because it is intentionally out of scope.
- Missing implementation that should exist in the clone scope.
- Implemented incorrectly or inconsistently.
- Implemented but visually/design-wise below the expected Discord-like quality.
- Working now, but risky because of weak feedback, unclear state, missing edge
  handling, accessibility issues, or poor responsive behavior.

## Required Startup

Before testing, read:

1. `DEVELOPMENT_PROMPT.md`
2. `AGENTS.md`
3. `PROJECT_CONTEXT.md`
4. `docs/README.md`
5. `docs/project-file-map.md`
6. `docs/structure-map/reference-map.md`
7. `docs/discord-app-clone-implementation-plan.md`
8. `docs/discord-ui-remediation-plan.md`
9. `docs/discord-visual-parity-remediation-plan.md`
10. `docs/discord-interaction-polish-plan.md`
11. `docs/discord-stage-11-completion-plan.md`
12. `docs/reference-screenshots/README.md`, if visual screenshots are involved

Use the project file map to identify likely owner files for each defect, but do
not over-investigate code unless it is necessary to classify a finding.

## Roles

Run the audit with these five roles. Keep findings separated by role first, then
merge duplicates into a final prioritized list.

### 1. Horizontal Product QA

Test the whole app surface broadly. Move through Friends, Add Friend, DM list,
DM conversation, server rail, server creation/join, channel creation, text
channels, voice channels, member list, settings, context menus, modals, and
responsive widths.

Focus on:

- Missing entry points.
- Dead buttons or controls.
- Inconsistent active/selected states.
- Broken navigation loops.
- Features that appear usable but do nothing.
- State that does not persist or refresh correctly.
- Korean/English copy gaps.

### 2. Vertical Workflow QA

Pick critical workflows and test them deeply from start to finish:

- Register/login/demo session.
- Create server, create text channel, send/edit/delete message.
- Create or open DM, send messages, receive realtime updates if another session is
  available.
- Join voice, leave voice, switch server/channel, mute/deafen, screen share.
- Invite or relationship flows if exposed in UI.
- Settings changes such as locale/status.

For each workflow, record exact reproduction steps, expected result, actual
result, and whether the issue is frontend, backend, realtime, persistence, or
design/state-feedback related.

### 3. Discord Power User: Daily Chat And Server Use

This role must be familiar with real Discord behavior. Use the user's provided
Discord screenshots, `docs/reference-screenshots/`, and, when the user permits or
asks for live comparison, the logged-in Discord web app or current web sources.

Focus on:

- Server rail and sidebar hierarchy.
- Channel row behavior, hover tools, unread/connected/speaking states.
- DM sidebar density and selection behavior.
- Message timeline grouping, date dividers, reactions, attachments, and composer
  behavior.
- Context menus and outside-click dismissal.
- Whether the clone feels like a Discord app rather than a generic dashboard.

### 4. Discord Power User: Voice And Presence

This role must also be familiar with real Discord voice usage.

Focus on:

- Joining a voice channel by clicking the voice row.
- Where connected users appear in the voice sidebar.
- Speaking indicator behavior around avatars/icons.
- Mute/deafen/screen-share state feedback.
- Cross-server voice switching prompts.
- Bottom-left connected voice card and user status card behavior.
- Voice workspace density, empty participant states, and screen-share preview.

### 5. Visual Design, Accessibility, And Responsive QA

Inspect the app like a UI reviewer.

Focus on:

- Box proportions, spacing, typography, color contrast, borders, shadows, and layer
  hierarchy.
- Text overlap, clipped controls, cramped rows, and excessive empty space.
- Whether visual components share a coherent design language.
- Keyboard navigation, focus styles, labels, semantic button/link behavior, and
  reduced-motion/accessibility concerns.
- FHD 100 percent zoom, 1280 x 720, tablet width, and mobile/narrow layouts.

## Discord Reference Collection

When Discord comparison is needed:

- Prefer user-provided screenshots and `docs/reference-screenshots/` first.
- If the user explicitly asks for live Discord comparison and a logged-in browser
  is available, inspect `https://discord.com/channels/@me` and representative
  server/channel/voice screens.
- If current external information is needed, browse current primary or reputable
  references and record the source links in the QA document.
- Do not copy private Discord messages or personal identifiers into committed
  documents. Redact user-specific data.

## Test Method

1. Confirm the app can run. Use Docker or native dev mode based on current project
   state and the user's request.
2. Open the clone in a browser and test with FHD 100 percent zoom first.
3. Cover each role above.
4. For every defect, classify severity:
   - P0: blocks core app usage or causes data/security risk.
   - P1: core Discord-like workflow broken or misleading.
   - P2: visible quality, consistency, or medium workflow problem.
   - P3: polish, copy, or low-frequency issue.
5. Classify category:
   - Feature missing.
   - Feature out of scope but exposed.
   - Feature incorrect.
   - Design/visual parity.
   - UX/state feedback.
   - Realtime/persistence.
   - Accessibility/responsive.
   - Documentation/QA gap.
6. Record likely owner files using `docs/project-file-map.md`.

## Required Output Document

Create or update a QA document under `docs/qa-audits/`.

Recommended filename:

```text
docs/qa-audits/discord-clone-qa-YYYY-MM-DD.md
```

The document must include:

- Scope, date, browser/device/viewport, app URL, and run mode.
- Reference material used.
- Role-by-role raw observations.
- Deduplicated prioritized findings.
- Reproduction steps for each actionable issue.
- Expected vs actual behavior.
- Severity, category, affected surface, and likely owner files.
- Whether the issue appears global or screen-specific.
- Screenshots or artifact paths when available.
- A final implementation backlog grouped into logical stages.
- Explicit residual risks and manual checks not completed.

## Rules

- Do not treat "demo" or "local" as an excuse for dead UI if the control is visible
  and appears usable.
- Do not require full Discord parity for low-frequency paid/commercial features
  unless the clone exposes them as usable.
- Prefer finding root patterns over listing the same spacing/state bug repeatedly.
- If a bug appears in one screen, inspect other major screens for the same pattern.
- Do not make code changes unless the user asks to proceed from QA into
  implementation.
- If the QA creates or updates documents, update `PROJECT_CONTEXT.md`,
  `docs/README.md`, and `docs/project-file-map.md` when appropriate.

## Final Response

Report:

- The QA document path.
- Top 5 highest-risk findings.
- Verification or browser coverage completed.
- What was not tested and why.
- Recommended next implementation stage.
