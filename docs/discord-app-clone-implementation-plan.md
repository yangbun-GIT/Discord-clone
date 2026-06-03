# Discord App Clone Implementation Plan

This plan supersedes the Store-first direction. The product target is the core
Discord web app experience rooted at `https://discord.com/channels/@me`, with Store
work treated as deferred supporting scope unless the user asks to resume it.

Observed on 2026-06-03 through the Codex in-app browser:

- `https://discord.com/channels/@me` opened with the user's logged-in Discord session.
- The `@me` home uses a four-zone app shell:
  - server rail
  - private-channel sidebar
  - main Friends/DM content
  - bottom user status, mute, deafen, and settings controls
- The server view uses:
  - server rail with selected server, folders, add server, discovery, and app download
  - server/channel sidebar with categories, text channels, voice channels, invite actions
  - channel header with thread, notification, pinned messages, member-list toggle, search
  - message timeline and composer actions
  - bottom user controls shared with the DM shell
- Personal DM names, server names, and message contents are not copied into this
  repository. Only UI structure and interaction patterns should inform the clone.

## Product Target

Build the actual Discord-like app, not a landing page and not a Store-first product.
The first screen after login should behave like Discord's app shell:

- `@me` Friends and DM home.
- Server rail and server workspace.
- Text channels, voice channels, and direct messages.
- User panel, settings entry, mute/deafen controls, and status controls.
- Channel header controls, member list, messages, and composer.
- Server creation/join/discovery flows.

## Stage 7.1: App Destination Model

Goal: let the frontend represent Discord-like destinations before adding more views.

Tasks:

- Add an app-level destination state:
  - `friends`
  - `dm`
  - `server_channel`
  - `voice_channel`
  - `settings`
- Keep active server/channel state preserved when switching to `@me` and back.
- Add frontend route-like state helpers without replacing Vue Router yet.
- Keep current guild chat behavior working.

Deliverables:

- App destination state in `frontend/src/App.vue` or a small navigation store.
- Updated `PROJECT_CONTEXT.md`.

Verification:

- Frontend lint/build.
- Browser smoke test for switching between `@me` and a server channel.

## Stage 7.2: Private Channel Sidebar And Friends Home

Goal: clone the `channels/@me` structure.

Tasks:

- Add a DM/private-channel sidebar with:
  - search/start conversation button
  - Friends
  - Nitro placeholder
  - Shop/Quest placeholders as non-primary links
  - DM list from demo data
  - create DM button
- Add Friends home main panel with:
  - top Friends navigation
  - Online/All/Pending/Blocked/Add Friend tabs
  - search input
  - friend rows with status and message action
- Do not expose private real Discord names; use original demo users.

Deliverables:

- Private sidebar component.
- Friends home component.
- Demo DM/friend data model.

Verification:

- Frontend lint/build.
- Browser smoke test for tabs and DM selection.

## Stage 7.3: Direct Messages

Goal: make DMs a functional first-class workspace.

Tasks:

- Add backend schemas and demo store methods for DM channels.
- Add authenticated APIs:
  - `GET /api/users/me/relationships`
  - `GET /api/dms`
  - `POST /api/dms`
  - `POST /api/dms/{dm_id}/messages`
- Reuse message sanitization and realtime dispatch style where possible.
- Add frontend DM store state and message composer integration.

Deliverables:

- Backend DM schemas/routes/service.
- Frontend DM state and DM chat view integration.

Verification:

- Backend tests for auth, DM creation, message validation, and member visibility.
- Frontend lint/build.
- Browser smoke test for opening a DM and sending a demo message.

## Stage 7.4: Server Rail Parity

Goal: make the server rail closer to Discord's navigation.

Tasks:

- Add dedicated `@me` button.
- Add server unread/mention badges.
- Add muted indicator.
- Add folder visual grouping for demo folders.
- Add add-server and discovery buttons.
- Keep keyboard focus and titles accessible.

Deliverables:

- Updated `ServerRail.vue`.
- Demo metadata for unread/muted/folder states.

Verification:

- Frontend lint/build.
- Browser smoke test for `@me`, server selection, add server, and discovery entry.

## Stage 7.5: Server Sidebar And Header Controls

Goal: improve the server workspace to match Discord's server/channel surface.

Tasks:

- Add server header with activity/menu entry.
- Add Events entry.
- Add collapsible channel categories.
- Add text/voice channel action buttons:
  - invite
  - channel settings placeholder
  - create channel
- Add channel header buttons:
  - threads
  - notification settings
  - pinned messages
  - member list toggle
  - search placeholder
  - inbox/help placeholders

Deliverables:

- Updated channel sidebar and topbar components.
- Member list visibility toggle.

Verification:

- Frontend lint/build.
- Browser smoke test for category collapse, header buttons, and member toggle.

## Stage 7.6: Composer And Message Actions

Goal: make message composition feel Discord-like.

Tasks:

- Add composer action buttons:
  - upload placeholder
  - gift placeholder
  - emoji picker placeholder
  - app/action placeholder
- Add reply placeholder, edit/delete existing controls, and message options menu.
- Keep send/edit/delete backend behavior unchanged.
- Keep text overflow and mobile layout stable.

Deliverables:

- Updated `ChatView.vue`.
- Focused CSS updates.

Verification:

- Frontend lint/build.
- Browser smoke test for message send/edit/delete and composer controls.

## Stage 7.7: Voice Channel UX

Goal: align the voice entry, user panel, and channel sidebar with Discord patterns.

Tasks:

- Show active voice channel membership inside the server sidebar.
- Add channel join/leave affordances.
- Keep existing WebRTC voice, mute, screen share, and quality diagnostics.
- Add user panel status control and mute/deafen visual state.

Deliverables:

- Updated voice panel and sidebar voice channel rows.
- User status panel controls.

Verification:

- Frontend lint/build.
- Browser smoke test for voice join/leave and mute/deafen states.

## Stage 7.8: User Settings Shell

Goal: implement the settings destination opened from the bottom user panel.

Tasks:

- Add settings view with left settings navigation.
- Include safe demo panels:
  - My Account
  - Profiles
  - Privacy & Safety
  - Voice & Video
  - Appearance
  - Keybinds placeholder
  - Log out
- Reuse current session logout behavior.

Deliverables:

- Settings shell component.
- Settings navigation state.

Verification:

- Frontend lint/build.
- Browser smoke test for opening/closing settings and logout.

## Stage 7.9: Server Discovery And Add Server

Goal: complete Discord-like navigation branches without external network dependency.

Tasks:

- Improve create-server modal.
- Add join-server by invite flow to the `@me`/rail add path.
- Add local discovery placeholder with demo public servers.
- Keep existing guild create/join backend APIs.

Deliverables:

- Add/discovery views or modals.
- Updated rail actions.

Verification:

- Backend existing guild tests.
- Frontend lint/build.
- Browser smoke test for create, join, and discovery placeholder.

## Stage 7.10: Persistence And Realtime Expansion

Goal: persist new DM/friend state with PostgreSQL while preserving demo fallback.

Tasks:

- Extend `backend/app/db/schema.sql` with DM/relationship tables.
- Add repository methods and demo fallback equivalence.
- Add realtime dispatch for DM messages.
- Keep Snowflake IDs JavaScript-safe.

Deliverables:

- SQL schema updates.
- Repository/service tests.
- Realtime DM dispatch handling.

Verification:

- Backend tests.
- Docker Compose smoke test when Docker is available.

## Stage 7.11: Responsive And Accessibility QA

Goal: make the app usable across desktop and narrow layouts.

Tasks:

- Verify keyboard navigation across rail, sidebars, tabs, composer, modals, settings.
- Keep visible focus states.
- Add stable dimensions for rails, channel rows, buttons, composer, and user panel.
- Verify mobile layout does not overlap or hide key controls.

Deliverables:

- CSS/layout polish.
- QA notes if needed.

Verification:

- Frontend lint/build.
- Browser screenshots at desktop and mobile widths.

## Stage 7.12: Final Discord App QA And Documentation

Goal: close the Discord app parity slice.

Tasks:

- Update `PROJECT_CONTEXT.md` with all new app maps and integration flows.
- Update `docs/implementation-plan.md`.
- Run:
  - `npm run test:backend`
  - `npm run lint:backend`
  - `npm run lint:frontend`
  - `npm --prefix frontend run build`
- Browser smoke test:
  - login/demo session
  - open `@me`
  - switch friend tabs
  - open DM
  - send message
  - open server
  - switch text and voice channels
  - open settings
  - create/join server flow
  - logout/reset state

Deliverables:

- Completed Discord app shell and core workflows.
- Updated documentation.
- Commit and push to `origin/main`.

## Deferred

- Real Discord assets, names, or private content.
- Real payment flows.
- Production trust/safety systems.
- Full Discord settings depth.
- Full mobile app parity.
