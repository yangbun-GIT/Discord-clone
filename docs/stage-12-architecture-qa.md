# Stage 12 Architecture QA

This file records verification for behavior-preserving architecture refactor
stages. It should be updated after each Stage 12 sub-stage before committing.

## Stage 12.0 Audit And Plan Lock

Status: completed.

Documentation updated:

- `docs/architecture-refactor-stage-12-plan.md`
- `docs/architecture-principles-audit.md`
- `docs/implementation-plan.md`
- `docs/README.md`
- `PROJECT_CONTEXT.md`

Verification:

- Documentation links and stage order reviewed during edit.

Residual risk:

- None for documentation-only planning.

## Stage 12.1 App Voice Session Controller

Status: completed.

Changed files:

- `frontend/src/composables/useVoiceSessionController.ts`
- `frontend/src/App.vue`

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.

Review:

- `App.vue` no longer contains the main voice join/leave/switch/mute/deafen/screen
  share orchestration or the voice participant/signal watches.
- The new controller preserves the existing gateway update, WebRTC facade, voice
  switch dialog state, and screen-share guard behavior.

Residual risk:

- Live microphone and screen-capture transitions remain permission-dependent manual
  QA, consistent with `docs/voice-qa.md`.

## Stage 12.2 Voice RTC Internal Modules

Status: completed.

Changed files:

- `frontend/src/composables/useVoiceRtc.ts`
- `frontend/src/composables/voiceMedia.ts`
- `frontend/src/composables/voiceVad.ts`
- `frontend/src/composables/voicePeerConnections.ts`

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.

Review:

- Browser microphone/display capture helpers moved to `voiceMedia.ts`.
- Local AudioContext/analyser/timer VAD behavior moved to `voiceVad.ts`.
- Peer connection registry, offer/answer/ICE handling, remote streams, participant
  sync, and peer renegotiation moved to `voicePeerConnections.ts`.
- `useVoiceRtc.ts` remains the public facade used by the app and voice session
  controller.

Residual risk:

- Live microphone, peer audio, and display-capture transitions remain
  permission-dependent manual QA, consistent with `docs/voice-qa.md`.

## Stage 12.3 Guild Voice Presence Store Boundary

Status: completed.

Changed files:

- `frontend/src/stores/guilds.ts`
- `frontend/src/stores/voicePresence.ts`

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.

Review:

- Connected voice guild/channel refs, voice-state collections, latest voice signal,
  voice-channel derived state, and voice-presence mutation helpers moved to
  `voicePresence.ts`.
- `guilds.ts` keeps the existing public Pinia API while delegating voice presence
  ownership to the focused module.
- Gateway dispatch behavior still calls the same voice-state and voice-signal
  callbacks through `guildGatewayHandlers.ts`.

Residual risk:

- Live cross-server voice switching and peer presence updates remain
  browser/gateway-dependent manual QA, consistent with `docs/voice-qa.md`.

## Stage 12.4 DM Storage Provider Boundary

Status: completed.

Changed files:

- `backend/app/services/dm_service.py`
- `backend/app/services/dm_storage.py`
- `backend/tests/test_dm_storage.py`

Verification:

- `npm run lint:backend` passed.
- `npm run test:backend -- tests/test_dm_api.py tests/test_dm_repository.py tests/test_dm_storage.py tests/test_demo_store.py` passed.

Review:

- `dm_service.py` no longer imports `database`, `demo_store`, or
  `dm_repository`.
- `dm_storage.py` mirrors the guild storage provider pattern with a `DmStorage`
  protocol plus PostgreSQL and demo implementations.
- New provider-selection tests cover connected and disconnected database modes.

Residual risk:

- None identified for route contracts; DM API and repository tests passed.

## Stage 12.5 Guild Repository Query Movement

Status: completed.

Changed files:

- `backend/app/repositories/guilds.py`
- `backend/app/repositories/guild_common.py`
- `backend/app/repositories/guild_channels.py`
- `backend/app/repositories/guild_invites.py`
- `backend/app/repositories/guild_members.py`
- `backend/app/repositories/guild_messages.py`
- `backend/app/repositories/guild_roles.py`
- `backend/tests/test_guild_repository.py`

Verification:

- `npm run lint:backend` passed.
- `npm run test:backend -- tests/test_guild_repository.py` passed.
- `npm run test:backend` passed with 107 tests.

Review:

- Channel, invite, member, message, and role SQL moved from `guilds.py` into the
  matching domain-specific repository files.
- `guilds.py` now owns guild aggregate list/read/create behavior and keeps
  compatibility wrapper methods for existing callers.
- Shared guild snapshot, permission, member/role, and ID helper logic moved to
  `guild_common.py` so domain repositories do not depend on the broad
  `GuildRepository` implementation.
- Guild repository tests now patch the domain modules that own each SQL path.

Residual risk:

- `guilds.py` intentionally retains compatibility wrapper methods until callers
  no longer need the historical broad repository API.

## Stage 12.6 API Exception Mapping

Status: completed.

Changed files:

- `backend/app/api/errors.py`
- `backend/app/api/routes/guilds.py`
- `backend/app/api/routes/channels.py`
- `backend/app/api/routes/dms.py`

Verification:

- `npm run lint:backend` passed.
- `npm run test:backend` passed with 107 tests.

Review:

- Shared route exception mapping now lives in `backend/app/api/errors.py`.
- Guild, channel, and DM routes preserve route-specific detail messages while
  delegating `KeyError`, `PermissionError`, and `ValueError` status-code mapping
  to `raise_route_error()`.
- Payload/path mismatch checks remain local to routes because they are explicit
  request-contract validation, not service-layer exception mapping.

Residual risk:

- None identified for REST contracts; full backend tests passed.

## Stage 12.7 Realtime Fan-Out DRY Pass

Status: completed.

Changed files:

- `backend/app/realtime/fanout.py`
- `backend/app/realtime/publisher.py`
- `backend/app/realtime/subscriber.py`
- `backend/tests/test_realtime_fanout.py`

Verification:

- `npm run lint:backend` passed.
- `npm run test:backend` passed with 110 tests.

Review:

- Local fallback publishing and Redis subscriber dispatch now share
  `fanout_gateway_event()`.
- DM create, channel create, and guild update subscription synchronization moved
  out of both publisher and subscriber modules into `fanout.py`.
- Focused tests cover DM subscriber sync, channel subscriber sync, guild member
  and channel sync, and the resulting broadcast target.

Residual risk:

- None identified for local/Redis dispatch contracts; full backend tests passed.

## Stage 12.8 Browser API Adapter Pass

Status: completed.

Changed files:

- `frontend/src/services/browserApi.ts`
- `frontend/src/App.vue`
- `frontend/src/components/ChannelSidebar.vue`
- `frontend/src/components/FriendsHome.vue`
- `frontend/src/components/PrivateChannelSidebar.vue`
- `frontend/src/composables/useGateway.ts`
- `frontend/src/composables/useVoiceSessionController.ts`
- `frontend/src/stores/guilds.ts`
- `frontend/src/stores/preferences.ts`
- `frontend/src/stores/session.ts`

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.

Review:

- Session, preference, and voice-switch confirmation storage now use
  `browserStorage`.
- Clipboard copy, viewport clamping, current URL reads, document key/pointer
  listener registration, gateway URL construction, navigator platform reads, and
  view transitions now go through `frontend/src/services/browserApi.ts`.
- WebRTC microphone/display-capture APIs remain in `voiceMedia.ts` as planned so
  browser permission behavior is unchanged.

Residual risk:

- Live browser permission prompts for microphone and display capture remain manual
  QA items, consistent with `docs/voice-qa.md`.

## Stage 12.9 CSS And I18n Split Plan

Status: completed.

Changed files:

- `docs/frontend-css-i18n-ownership.md`
- `docs/README.md`
- `docs/project-file-map.md`
- `docs/architecture-principles-audit.md`
- `docs/architecture-refactor-stage-12-plan.md`
- `docs/implementation-plan.md`

Verification:

- Documentation paths and update rules reviewed during edit.
- `git diff --check` must pass before commit.

Review:

- `docs/frontend-css-i18n-ownership.md` now defines the future extraction order
  for CSS tokens, layout, overlays, chat, voice, settings, Store, and domain i18n
  modules.
- The current decision is to keep `base.css` and `i18n/index.ts` intact during
  Stage 12 to avoid risking visual parity through broad mechanical movement.

Residual risk:

- `frontend/src/styles/base.css` and `frontend/src/i18n/index.ts` remain large
  files until a future focused split can be visually verified.

## Stage 12.10 Final Architecture Regression

Status: completed.

Changed files:

- `docs/architecture-principles-audit.md`
- `docs/architecture-refactor-stage-12-plan.md`
- `docs/implementation-plan.md`
- `docs/stage-12-architecture-qa.md`
- `PROJECT_CONTEXT.md`

Verification:

- `npm run lint:frontend` passed.
- `npm --prefix frontend run build` passed.
- `npm run lint:backend` passed.
- `npm run test:backend` passed with 110 tests.
- `git diff --check` must pass before commit.

Review:

- Stage 12.6 through 12.9 changes remain covered by the final regression suite.
- Architecture docs now distinguish completed Stage 12 scope from future deferred
  candidates.

Residual risk:

- `frontend/src/stores/dms.ts` still combines DM state, REST mutations, and
  gateway event application; split only when DM work expands.
- CSS/i18n physical splitting remains deferred to preserve current visual parity.
- Live microphone and screen-capture permission QA still requires browser
  permission/manual media verification.
