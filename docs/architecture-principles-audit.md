# Architecture Principles Audit

This document records the current implementation-principle and design-pattern
audit. Use it before planning broad refactors so future work does not drift into
unrelated UI or feature changes.

## Scope

The audit covers the current FastAPI backend and Vue 3 frontend structure with a
focus on:

- Single Responsibility Principle.
- Separation of concerns.
- Open/Closed Principle.
- Dependency inversion and replaceability.
- Encapsulation.
- DRY and repeated workflow logic.
- Testability.
- Existing design-pattern fit.

## Overall Assessment

The project already uses a reasonable full-stack structure:

- Backend layers: `backend/app/api`, `backend/app/services`,
  `backend/app/repositories`, `backend/app/schemas`, `backend/app/domain`,
  `backend/app/gateway`, and `backend/app/realtime`.
- Frontend layers: `frontend/src/components`, `frontend/src/stores`,
  `frontend/src/composables`, `frontend/src/services`, `frontend/src/i18n`,
  and `frontend/src/styles`.
- Applied patterns: layered architecture, repository pattern, service layer,
  Pinia store pattern, API adapter, Vue composable pattern, app factory, gateway
  manager, and schema-boundary validation.

The structure is not broken, but some files have grown beyond their original
responsibility. Future feature work should avoid adding more behavior to these
files unless it is part of a planned split.

## Principle And Pattern Gaps

### 1. `frontend/src/App.vue`

Weak areas:

- Single Responsibility Principle.
- Encapsulation.
- Open/Closed Principle.
- Testability.

Current issue:

`App.vue` coordinates the whole app shell and also owns substantial feature logic:
session boot, navigation, guild/DM switching, global notices, context menus,
invite flow, server add/discovery flow, voice connection, screen share controls,
member-list visibility, settings routing, and workspace header panels.

Why it matters:

Any change to global UI, voice state, modal behavior, invite behavior, or
navigation can require editing the same file. This increases regression risk and
makes targeted tests difficult.

Recommended split:

- `AppShell.vue`: top-level layout composition only.
- `useWorkspaceController.ts`: active destination and workspace title/subtitle.
- `useGlobalNotice.ts`: notice state, timeout, dismiss behavior.
- `useContextMenuController.ts`: app-owned right-click and more-button menus.
- `useVoiceSessionController.ts`: voice join/leave/switch orchestration.
- `useInviteController.ts`: invite modal, copy, friend invite behavior.
- Keep component rendering in focused child components instead of expanding
  `App.vue`.

### 2. `frontend/src/stores/guilds.ts`

Weak areas:

- Single Responsibility Principle.
- Store boundary clarity.
- Open/Closed Principle.
- Testability.

Current issue:

The guild store owns guild lists, active guild/channel selection, channel
messages, member/role mutations, invites, voice state, gateway dispatch handling,
and message mutation API calls.

Why it matters:

The store is both a state container and a domain workflow coordinator. Gateway
event handling and API mutation code are tightly coupled to the same state object,
so adding a new realtime event or guild feature widens the store again.

Recommended split:

- `guilds.ts`: guild list, active guild, active channel selection.
- `channelMessages.ts`: channel message collection, send/edit/delete operations.
- `guildAdmin.ts`: roles, member removal, invite creation, channel creation.
- `voicePresence.ts`: connected voice guild/channel and voice-state updates.
- `gatewayEventHandlers.ts`: typed handler map for gateway events.

### 3. `frontend/src/composables/useVoiceRtc.ts`

Weak areas:

- Single Responsibility Principle inside the voice domain.
- Testability.
- Encapsulation of browser APIs.

Current issue:

The composable handles media capture, mute state, screen sharing, local voice
activity detection, peer connection lifecycle, signaling, remote streams, and RTC
quality statistics in one module.

Why it matters:

The file is cohesive around voice, but it is difficult to test individual parts
such as VAD thresholds, quality-stat aggregation, screen-share transitions, or
peer renegotiation without a browser media environment.

Recommended split:

- `voiceMedia.ts`: microphone and screen-capture lifecycle.
- `voiceVad.ts`: local input level and speaking detection.
- `voicePeerConnections.ts`: peer registry and offer/answer/ICE handling.
- `voiceStats.ts`: WebRTC stats collection and quality aggregation.
- `useVoiceRtc.ts`: small facade that composes the modules above.

### 4. `backend/app/repositories/guilds.py`

Weak areas:

- Single Responsibility Principle.
- Repository granularity.
- Domain rule placement.

Current issue:

`GuildRepository` handles guild reads/creation, member removal, role creation and
assignment, invite creation/joining, channel creation, message creation, message
editing, message deletion, and permission helper queries.

Why it matters:

The repository has become a persistence gateway for several domains. Message,
channel, invite, member, and role changes all compete in one file, which makes
database behavior harder to review and increases the chance of unrelated merge
conflicts.

Recommended split:

- `GuildRepository`: guild reads and guild creation.
- `ChannelRepository`: channel creation and channel-specific reads.
- `MessageRepository`: create/update/delete/list channel messages.
- `InviteRepository`: invite creation and invite join.
- `RoleRepository`: role creation, assignment, removal.
- `MemberRepository`: guild membership reads/removal.
- `PermissionService` or domain helpers: permission checks shared by repositories.

### 5. `backend/app/services/guild_service.py`

Weak areas:

- Dependency inversion.
- Replaceability.

Current issue:

The service functions directly choose between the PostgreSQL repository and
`demo_store` by checking `database.is_connected`.

Why it matters:

The current approach is pragmatic for local demo mode, but the service layer is
coupled to concrete storage implementations. This makes alternative persistence
or focused service tests harder than necessary.

Recommended split:

- Introduce a storage/provider boundary that returns the active implementation.
- Keep demo mode and PostgreSQL mode behind the same service-facing interface.
- Move `database.is_connected` branching out of individual service functions.

### 6. `backend/app/gateway/manager.py`

Weak areas:

- Single Responsibility Principle boundary.
- Future scalability.

Current issue:

The gateway manager owns client connection tracking, guild/channel/DM
subscriptions, voice state broadcasting, voice signaling, subscriber syncing, and
zombie connection cleanup behavior.

Why it matters:

The current size is manageable, but this file will become a bottleneck if gateway
features expand into presence, typing, thread events, notification fan-out, or
multi-worker coordination.

Recommended split:

- `ConnectionRegistry`: active websocket connections and heartbeat metadata.
- `SubscriptionRegistry`: guild, channel, and DM subscription maps.
- `GatewayBroadcaster`: channel/guild/DM dispatch helpers.
- `VoiceGatewayService`: voice state and voice signal routing.
- `GatewayReaper`: stale heartbeat cleanup.

## Cross-Cutting Refactor Rules

- Do not refactor all files in one large commit.
- Keep each refactor behavior-preserving unless a stage explicitly includes a
  behavior change.
- Add or update tests around moved behavior before or during the split.
- After each split, run at least the verification for the touched surface.
- Update `PROJECT_CONTEXT.md`, this document, and any stage plan that starts using
  the new boundary.
- Use Korean commit titles, matching the Stage 10 and Stage 11 process.

## Previous Stage Process To Preserve

Use this process when turning the gaps above into implementation stages:

1. Read startup context first:
   `DEVELOPMENT_PROMPT.md`, `AGENTS.md`, `PROJECT_CONTEXT.md`,
   `docs/implementation-plan.md`, `README.md`, `docs/README.md`, and the
   task-specific plan.
2. Work one stage at a time.
3. Before editing, identify the owning layer and target files.
4. Keep the stage scope narrow and behavior-preserving unless the plan says
   otherwise.
5. After implementation, run verification appropriate to the touched surface.
6. Review the result for regressions, missing states, visual issues, and stale docs.
7. If a new defect is found, add it as a subtask under the current stage and fix it
   before moving on.
8. Update `PROJECT_CONTEXT.md`, relevant docs, and QA notes.
9. Run `git diff --check`.
10. Commit the completed stage with a short Korean commit title.
11. Push the completed stage to `origin/main` unless the user explicitly says not
    to.
12. Report changed files, verification, residual risks, and the next recommended
    stage.

## Latest Whole-Project Re-Audit

The 2026-06-19 whole-project re-audit found that the first remediation pass
reduced several broad risks, but the project still has the following remaining
principle and pattern gaps:

1. `frontend/src/stores/dms.ts` still combines DM state, REST mutations, and
   gateway event application.
2. `backend/app/repositories/guilds.py` still contains the actual SQL for channel,
   message, invite, role, member, and permission-helper workflows; the
   domain-specific repository files currently provide only entry-point boundaries.
3. `backend/app/api/routes/guilds.py`, `channels.py`, and `dms.py` repeat
   exception-to-HTTP mappings.
4. `backend/app/realtime/publisher.py` and `subscriber.py` duplicate
   subscription-sync behavior around local gateway fan-out.
5. Browser APIs such as clipboard, localStorage, document listeners, mediaDevices,
   and view transitions remain scattered across a few frontend modules. Some are
   appropriate at the browser boundary, but high-use clone workflows should be
   wrapped where doing so improves testability.
6. `frontend/src/styles/base.css` and `frontend/src/i18n/index.ts` remain large
    single files. They are acceptable for current visual stability, but future
    changes should move toward token/layout/component and domain-copy ownership.

The active implementation plan for these gaps is
`docs/architecture-refactor-stage-12-plan.md`.

## Suggested Refactor Stage Order

These are planning candidates, not completed stages.

1. Architecture Stage A: create frontend controller/composable boundaries around
   `App.vue` without changing UI behavior.
2. Architecture Stage B: move global notices and context menus out of `App.vue`.
3. Architecture Stage C: move voice session orchestration out of `App.vue`.
4. Architecture Stage D: split `guilds.ts` gateway event handling into typed
   handler modules.
5. Architecture Stage E: split channel-message state and API mutations from
   `guilds.ts`.
6. Architecture Stage F: split guild admin mutations from `guilds.ts`.
7. Architecture Stage G: split `useVoiceRtc.ts` into media, VAD, peer, and stats
   modules.
8. Architecture Stage H: introduce backend repository provider abstraction for
   PostgreSQL/demo-store selection.
9. Architecture Stage I: split `GuildRepository` by guild, channel, message,
   invite, role, and member responsibilities.
10. Architecture Stage J: split gateway manager registries and broadcasters when
    gateway behavior next expands.

For active work, use the more current Stage 12 plan in
`docs/architecture-refactor-stage-12-plan.md`.

## Current Status

Partially applied.

- `frontend/src/App.vue`: global notice, app context-menu state, invite modal
  state, workspace title/subtitle calculation, and voice session orchestration
  were moved into focused composables. The remaining `App.vue` risk is now broad
  layout composition and event wiring rather than owning voice join/leave/switch
  behavior directly.
- `frontend/src/composables/useVoiceSessionController.ts`: owns voice config
  loading, voice join/leave/switch orchestration, mute/deafen gateway sync,
  screen-share toggle orchestration, voice participant synchronization, and
  incoming voice-signal handling.
- `frontend/src/stores/guilds.ts`: gateway event validation moved to
  `guildGatewayHandlers.ts`; server message REST mutations moved to
  `channelMessages.ts`; guild invite/channel/role/member REST mutations moved to
  `guildAdmin.ts`; connected voice presence moved to `voicePresence.ts`.
- `frontend/src/stores/voicePresence.ts`: owns connected voice guild/channel refs,
  voice-state collections, latest voice signal, derived voice channel state, and
  voice-presence mutation helpers used by `guilds.ts`.
- `frontend/src/composables/useVoiceRtc.ts`: now acts as the public WebRTC facade.
  Media capture helpers moved to `voiceMedia.ts`, local VAD moved to
  `voiceVad.ts`, peer lifecycle/signaling/remote-stream handling moved to
  `voicePeerConnections.ts`, and quality stats remain in `voiceStats.ts`.
- `backend/app/services/guild_service.py`: PostgreSQL/demo branching moved behind
  `guild_storage.py`.
- `backend/app/services/dm_service.py`: PostgreSQL/demo branching moved behind
  `dm_storage.py`.
- `backend/app/services/dm_storage.py`: owns the direct-message storage protocol
  and PostgreSQL/demo provider selection used by `dm_service.py`.
- `backend/app/repositories/guilds.py`: domain-specific repository entry points
  were added for channels, invites, members, messages, and roles. They currently
  delegate to the legacy implementation so query movement can proceed safely in
  smaller repository-focused commits.
- `backend/app/gateway/manager.py`: split into connection, subscription,
  broadcaster, voice service, and zombie reaper modules while preserving the
  manager facade used by routes, realtime, and tests.

Verification for this pass:

- `npm --prefix frontend run build`
- `npm --prefix frontend run lint`
- `npm run lint:backend`
- `npm run test:backend`
