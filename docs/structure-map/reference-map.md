# Core Reference Map

This map records high-value file relationships. It is intentionally selective:
it focuses on files most likely to be touched during implementation, debugging,
or refactoring.

## Full-Stack Flow

```text
Browser UI
  -> frontend/src/main.ts
  -> frontend/src/App.vue
  -> frontend/src/components/*
  -> frontend/src/stores/*
  -> frontend/src/services/api.ts
  -> /api/* REST routes or /gateway WebSocket
  -> backend/app/api/router.py or backend/app/gateway/router.py
  -> backend/app/services/*
  -> backend/app/repositories/* or backend/app/demo/store.py
  -> backend/app/db/pool.py, backend/app/db/schema.sql, backend/app/db/seed.py
```

## Backend References

### App Assembly

- `backend/app/main.py`
  - References:
    - `backend/app/api/router.py`
    - `backend/app/core/config.py`
    - `backend/app/core/rate_limit.py`
    - `backend/app/db/pool.py`
    - `backend/app/db/seed.py`
    - `backend/app/gateway/router.py`
    - `backend/app/gateway/reaper.py`
    - `backend/app/realtime/redis_bus.py`
    - `backend/app/realtime/subscriber.py`
  - Referenced by:
    - ASGI runtime through `app = create_app()`.

- `backend/app/api/router.py`
  - References:
    - `backend/app/api/routes/auth.py`
    - `backend/app/api/routes/channels.py`
    - `backend/app/api/routes/dev.py`
    - `backend/app/api/routes/dms.py`
    - `backend/app/api/routes/guilds.py`
    - `backend/app/api/routes/health.py`
    - `backend/app/api/routes/meta.py`
    - `backend/app/api/routes/store.py`
    - `backend/app/api/routes/users.py`
  - Referenced by:
    - `backend/app/main.py`

### REST Route To Service Flow

- `backend/app/api/errors.py`
  - References:
    - FastAPI `HTTPException` and status codes.
  - Referenced by:
    - `backend/app/api/routes/guilds.py`
    - `backend/app/api/routes/channels.py`
    - `backend/app/api/routes/dms.py`
  - Owns:
    - Shared REST route mapping for `KeyError`, `PermissionError`, and
      `ValueError` into HTTP responses.

- `backend/app/api/routes/auth.py`
  - References:
    - `backend/app/api/dependencies.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/services/auth_service.py`
  - Referenced by:
    - `backend/app/api/router.py`

- `backend/app/api/routes/guilds.py`
  - References:
    - `backend/app/api/dependencies.py`
    - `backend/app/api/errors.py`
    - `backend/app/realtime/publisher.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/services/guild_service.py`
  - Referenced by:
    - `backend/app/api/router.py`

- `backend/app/api/routes/channels.py`
  - References:
    - `backend/app/api/dependencies.py`
    - `backend/app/api/errors.py`
    - `backend/app/core/operation_limits.py`
    - `backend/app/realtime/publisher.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/schemas/message.py`
    - `backend/app/services/guild_service.py`
  - Referenced by:
    - `backend/app/api/router.py`

- `backend/app/api/routes/dms.py`
  - References:
    - `backend/app/api/dependencies.py`
    - `backend/app/api/errors.py`
    - `backend/app/core/operation_limits.py`
    - `backend/app/realtime/publisher.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
    - `backend/app/services/dm_service.py`
  - Referenced by:
    - `backend/app/api/router.py`

- `backend/app/api/routes/users.py`
  - References:
    - `backend/app/api/dependencies.py`
    - `backend/app/api/errors.py`
    - `backend/app/realtime/publisher.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
    - `backend/app/services/dm_service.py`
  - Referenced by:
    - `backend/app/api/router.py`
  - Owns:
    - Relationship reads plus Add Friend request, accept, reject, cancel, remove,
      block, and unblock REST endpoints.

- `backend/app/api/routes/meta.py`
  - References:
    - `backend/app/core/config.py`
    - `backend/app/domain/permissions.py`
  - Referenced by:
    - `backend/app/api/router.py`
    - `scripts/voice_readiness_check.mjs`
    - `frontend/src/composables/useVoiceSessionController.ts`
  - Owns:
    - Permission metadata, browser-required voice ICE configuration, and safe
      STUN/TURN readiness metadata.

- `backend/app/api/routes/store.py`
  - References:
    - `backend/app/api/dependencies.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/store.py`
    - `backend/app/services/store_service.py`
  - Referenced by:
    - `backend/app/api/router.py`

### Service To Repository Or Demo Flow

- `backend/app/services/auth_service.py`
  - References:
    - `backend/app/core/security.py`
    - `backend/app/db/pool.py`
    - `backend/app/repositories/users.py`
    - `backend/app/schemas/auth.py`
  - Referenced by:
    - `backend/app/api/routes/auth.py`

- `backend/app/services/guild_service.py`
  - References:
    - `backend/app/services/guild_storage.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/schemas/message.py`
  - Referenced by:
    - `backend/app/api/routes/guilds.py`
    - `backend/app/api/routes/channels.py`
    - `backend/app/gateway/router.py`

- `backend/app/services/guild_storage.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/demo/store.py`
    - `backend/app/repositories/guilds.py`
    - `backend/app/repositories/guild_channels.py`
    - `backend/app/repositories/guild_invites.py`
    - `backend/app/repositories/guild_members.py`
    - `backend/app/repositories/guild_messages.py`
    - `backend/app/repositories/guild_roles.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/schemas/message.py`
  - Referenced by:
    - `backend/app/services/guild_service.py`

- `backend/app/services/dm_service.py`
  - References:
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
    - `backend/app/services/dm_storage.py`
  - Referenced by:
    - `backend/app/api/routes/dms.py`
    - `backend/app/api/routes/users.py`
    - `backend/app/gateway/router.py`

- `backend/app/services/dm_storage.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/demo/store.py`
    - `backend/app/repositories/dms.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
  - Referenced by:
    - `backend/app/services/dm_service.py`
    - `backend/tests/test_dm_storage.py`
  - Owns:
    - DM PostgreSQL/demo storage provider selection and common async DM storage
      protocol.

- `backend/app/services/store_service.py`
  - References:
    - `backend/app/demo/store_catalog.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/store.py`
  - Referenced by:
    - `backend/app/api/routes/store.py`

### Persistence And Domain

- `backend/app/repositories/guilds.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/domain/permissions.py`
    - `backend/app/repositories/guild_common.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/schemas/message.py`
  - Referenced by:
    - `backend/app/services/guild_storage.py`
    - `backend/app/repositories/guild_invites.py`
    - `backend/tests/test_guild_repository.py`
  - Owns:
    - Guild aggregate list/read/create SQL and compatibility wrapper methods.

- `backend/app/repositories/guild_common.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/domain/permissions.py`
    - `backend/app/domain/snowflake.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
  - Referenced by:
    - `backend/app/repositories/guilds.py`
    - `backend/app/repositories/guild_channels.py`
    - `backend/app/repositories/guild_invites.py`
    - `backend/app/repositories/guild_members.py`
    - `backend/app/repositories/guild_messages.py`
    - `backend/app/repositories/guild_roles.py`
  - Owns:
    - Guild snapshot reads, permission calculation, user upsert, member/role
      validation, role labels, and shared guild ID generation.

- `backend/app/repositories/guild_channels.py`,
  `guild_invites.py`, `guild_members.py`, `guild_messages.py`, `guild_roles.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/repositories/guild_common.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
  - Referenced by:
    - `backend/app/services/guild_storage.py`
    - compatibility wrapper methods in `backend/app/repositories/guilds.py`
    - `backend/tests/test_guild_repository.py`
  - Own:
    - Channel, invite, member, message, and role SQL respectively.

- `backend/app/repositories/dms.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/domain/snowflake.py`
    - `backend/app/repositories/dm_seed.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
  - Referenced by:
    - `backend/app/services/dm_storage.py`
    - `backend/tests/test_dm_repository.py`
  - Owns:
    - Direct-message persistence and PostgreSQL paired-row relationship mutation
      transitions.

- `backend/app/repositories/dm_seed.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/domain/snowflake.py`
    - `backend/app/schemas/auth.py`
  - Referenced by:
    - `backend/app/repositories/dms.py`
    - `backend/tests/test_dm_seed.py`
  - Owns:
    - PostgreSQL DM demo user, relationship, direct-message, and message bootstrap
      support.

- `backend/app/repositories/users.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/domain/snowflake.py`
    - `backend/app/schemas/auth.py`
  - Referenced by:
    - `backend/app/services/auth_service.py`

- `backend/app/domain/permissions.py`
  - Referenced by:
    - `backend/app/demo/data.py`
    - `backend/app/demo/store.py`
    - `backend/app/api/routes/meta.py`
    - `backend/app/repositories/guilds.py`
    - `backend/app/schemas/dm.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/schemas/store.py`
    - `backend/tests/test_permissions.py`

- `backend/app/domain/snowflake.py`
  - Referenced by:
    - `backend/app/demo/store.py`
    - `backend/app/repositories/dms.py`
    - `backend/app/repositories/guilds.py`
    - `backend/app/repositories/users.py`
    - `backend/tests/test_snowflake.py`

### Gateway And Realtime

- `backend/app/gateway/router.py`
  - References:
    - `backend/app/core/config.py`
    - `backend/app/core/operation_limits.py`
    - `backend/app/core/security.py`
    - `backend/app/gateway/events.py`
    - `backend/app/gateway/manager.py`
    - `backend/app/gateway/opcodes.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/services/dm_service.py`
    - `backend/app/services/guild_service.py`
  - Referenced by:
    - `backend/app/main.py`
    - `backend/tests/test_gateway_routes.py`

- `backend/app/gateway/manager.py`
  - References:
    - `backend/app/gateway/broadcaster.py`
    - `backend/app/gateway/connection.py`
    - `backend/app/gateway/subscriptions.py`
    - `backend/app/gateway/voice_service.py`
    - `backend/app/gateway/zombie_reaper.py`
  - Referenced by:
    - `backend/app/gateway/router.py`
    - `backend/app/gateway/reaper.py`
    - `backend/app/realtime/fanout.py`
    - `backend/tests/test_gateway_manager.py`
  - Owns:
    - Gateway connection lifecycle cleanup, including recoverable voice-disconnect
      grace for normal websocket closes and immediate voice leave fan-out when a
      connection is reaped as a zombie or removed after a stale send failure.
    - Voice-state snapshot dispatch for READY and post-join synchronization.

- `backend/app/gateway/connection.py`
  - References:
    - `backend/app/gateway/opcodes.py`
  - Referenced by:
    - `backend/app/gateway/manager.py`
    - `backend/app/gateway/broadcaster.py`
    - `backend/app/gateway/subscriptions.py`
    - `backend/app/gateway/voice_service.py`
    - `backend/app/gateway/zombie_reaper.py`
  - Owns:
    - Per-WebSocket subscription state, heartbeat state, and active voice
      guild/channel state used for disconnect cleanup.

- `backend/app/gateway/broadcaster.py`, `subscriptions.py`, `voice_service.py`,
  `zombie_reaper.py`
  - Referenced by:
    - `backend/app/gateway/manager.py`
  - `voice_service.py` owns the in-memory voice-state registry used to send
    authoritative `VOICE_STATE_SNAPSHOT` payloads to late-joining clients.
  - `voice_service.py` also owns pending voice leave scheduling and cancellation
    when the same guild user rejoins during the normal-disconnect grace window.

- `backend/app/realtime/publisher.py`
  - References:
    - `backend/app/realtime/events.py`
    - `backend/app/realtime/fanout.py`
    - `backend/app/realtime/redis_bus.py`
    - `backend/app/schemas/dm.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/schemas/message.py`
  - Referenced by:
    - `backend/app/api/routes/channels.py`
    - `backend/app/api/routes/dms.py`
    - `backend/app/api/routes/guilds.py`
    - `scripts/realtime_redis_smoke.py` indirectly through REST message creation.

- `backend/app/realtime/subscriber.py`
  - References:
    - `backend/app/realtime/events.py`
    - `backend/app/realtime/fanout.py`
    - `backend/app/realtime/redis_bus.py`
  - Referenced by:
    - `backend/app/main.py`
    - `compose.redis-smoke.yaml` runtime backend services when `REDIS_URL` is set.

- `backend/app/realtime/fanout.py`
  - References:
    - `backend/app/gateway/manager.py`
    - `backend/app/realtime/events.py`
  - Referenced by:
    - `backend/app/realtime/publisher.py`
    - `backend/app/realtime/subscriber.py`
    - `backend/tests/test_realtime_fanout.py`
  - Owns:
    - Gateway-event fan-out to channel/guild/DM/user subscribers.
    - Local subscription synchronization for DM create, channel create, and guild
      update events.

- `compose.redis-smoke.yaml`
  - References:
    - `compose.yaml`
    - `backend/Dockerfile`
    - `backend/app/main.py`
    - `backend/app/realtime/redis_bus.py`
    - `backend/app/realtime/subscriber.py`
  - Referenced by:
    - `docs/remediation-tasks/realtime-communication-plan.md`
    - `scripts/realtime_redis_smoke.py` runtime prerequisites.
  - Owns:
    - Optional Redis and secondary backend topology used to verify cross-worker
      realtime fan-out.

- `scripts/realtime_redis_smoke.py`
  - References:
    - `/api/health`
    - `/api/dev/session`
    - `/api/channels/{channel_id}/messages`
    - `/api/dms/{dm_id}/messages`
    - `/gateway`
  - Referenced by:
    - `docs/remediation-tasks/realtime-communication-plan.md`
    - root `package.json` script `smoke:realtime:redis`.
  - Owns:
    - C4 repeatable primary-worker REST to secondary-worker WebSocket dispatch
      verification for server text and DM events.

- `scripts/realtime_browser_smoke.mjs`
  - References:
    - root `package.json` script `smoke:realtime:browser`.
    - `frontend/package.json` for the official Playwright devDependency.
    - `/api/dev/session`
    - `/api/guilds`
    - `/api/guilds/{guild_id}/invites`
    - `/api/guilds/invites/{code}/join`
    - `/api/dms`
    - `frontend/src/App.vue`
    - `frontend/src/components/ServerRail.vue`
    - `frontend/src/components/PrivateChannelSidebar.vue`
    - `frontend/src/components/ChannelSidebar.vue`
    - `frontend/src/components/ChatView.vue`
    - `frontend/src/components/DirectMessageView.vue`
    - `frontend/src/components/VoicePanel.vue`
  - Referenced by:
    - `docs/realtime-communication-qa.md`
    - `docs/remediation-tasks/realtime-communication-plan.md`
  - Owns:
    - C8 repeatable two-browser same-PC communication smoke for server text, DM,
      invite-DM delivery, owner/member invite permission UI/API behavior, voice
      peer visibility, remote audio sink, mute/deafen including local microphone
      track suppression while deafened, fake screen-share UI, local screen-preview
      rendering, remote screen-video rendering, screen-share stop cleanup,
      connected-tab reload rejoin recovery, and voice leave cleanup paths.
    - Payload-safe result output that omits JWTs, message bodies, ICE candidates,
      TURN credentials, media device labels, and DM contents.

- `scripts/voice_readiness_check.mjs`
  - References:
    - `/api/meta/voice/readiness`
    - root `package.json` script `check:voice:readiness`.
  - Referenced by:
    - `README.md`
    - `docs/deployment.md`
    - `docs/voice-qa.md`
  - Owns:
    - Safe operator-facing STUN/TURN readiness output without ICE URLs, TURN
      credentials, candidates, tokens, message content, or media device labels.

## Frontend References

### Runtime Config

- `frontend/package.json`
  - References:
    - `frontend/scripts/ensureHttpsCertEnv.mjs`
    - Vite CLI.
  - Referenced by:
    - root `package.json` frontend scripts.
  - Owns:
    - Frontend dev/build/test/lint commands, including HTTPS LAN dev startup.

- `frontend/scripts/ensureHttpsCertEnv.mjs`
  - References:
    - `VITE_HTTPS_KEY_FILE`
    - `VITE_HTTPS_CERT_FILE`
  - Referenced by:
    - `frontend/package.json` script `dev:lan:https`.
  - Owns:
    - Early failure for missing local HTTPS LAN certificate configuration.

- `frontend/vite.config.ts`
  - References:
    - `VITE_BACKEND_PROXY_TARGET`
    - `VITE_HTTPS_KEY_FILE`
    - `VITE_HTTPS_CERT_FILE`
  - Referenced by:
    - Vite dev/build commands.
  - Owns:
    - Vue plugin setup, `/api` and `/gateway` proxy targets, and optional HTTPS
      LAN certificate loading.

### App Entry

- `frontend/src/main.ts`
  - References:
    - `frontend/src/App.vue`
    - `frontend/src/styles/base.css`
  - Referenced by:
    - Vite entry through `frontend/index.html`.

- `frontend/src/App.vue`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/components/AuthPanel.vue`
    - `frontend/src/components/ChannelSidebar.vue`
    - `frontend/src/components/ChatView.vue`
    - `frontend/src/components/DirectMessageView.vue`
    - `frontend/src/components/FriendsHome.vue`
    - `frontend/src/components/MemberList.vue`
    - `frontend/src/components/PrivateChannelSidebar.vue`
    - `frontend/src/components/ServerAddDialog.vue`
    - `frontend/src/components/ServerDiscoveryDialog.vue`
    - `frontend/src/components/ServerRail.vue`
    - `frontend/src/components/SettingsView.vue`
    - `frontend/src/components/VoiceAudioSink.vue`
    - `frontend/src/components/VoicePanel.vue`
    - `frontend/src/components/VoiceVideoSink.vue`
    - `frontend/src/composables/useContextMenuController.ts`
    - `frontend/src/composables/useGateway.ts`
    - `frontend/src/composables/useGlobalNotice.ts`
    - `frontend/src/composables/useInviteController.ts`
    - `frontend/src/composables/useVoiceRtc.ts`
    - `frontend/src/composables/useVoiceSessionController.ts`
    - `frontend/src/composables/useWorkspaceController.ts`
    - `frontend/src/i18n/index.ts`
    - `frontend/src/services/browserApi.ts`
    - `frontend/src/stores/dms.ts`
    - `frontend/src/stores/guilds.ts`
    - `frontend/src/stores/navigation.ts`
    - `frontend/src/stores/preferences.ts`
    - `frontend/src/stores/session.ts`
    - `frontend/src/stores/store.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/main.ts`
  - Owns:
    - App shell composition, global workflow wiring, gateway reconnect
      reconciliation callback, voice workspace selection, local/remote
      screen-share stage placement, remote screen-share render conditions,
      permission-aware global context-menu invite filtering, and QA-only
      `data-gateway-status` state attribute.

### Stores And API

- `frontend/src/services/api.ts`
  - References:
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/stores/dms.ts`
    - `frontend/src/stores/guilds.ts`
    - `frontend/src/stores/session.ts`
    - `frontend/src/stores/store.ts`

- `frontend/src/services/browserApi.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/components/ChannelSidebar.vue`
    - `frontend/src/components/FriendsHome.vue`
    - `frontend/src/components/PrivateChannelSidebar.vue`
    - `frontend/src/composables/useGateway.ts`
    - `frontend/src/composables/useVoiceSessionController.ts`
    - `frontend/src/stores/guilds.ts`
    - `frontend/src/stores/preferences.ts`
    - `frontend/src/stores/session.ts`
  - Owns:
    - High-use browser API adapters for storage, clipboard, document listeners,
      viewport/location reads, WebSocket URL construction, navigator platform
      reads, and document view transitions.

- `frontend/src/stores/session.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/services/browserApi.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`

- `frontend/src/stores/guilds.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/services/browserApi.ts`
    - `frontend/src/stores/channelMessages.ts`
    - `frontend/src/stores/guildAdmin.ts`
    - `frontend/src/stores/guildGatewayHandlers.ts`
    - `frontend/src/stores/guildVisibility.ts`
    - `frontend/src/stores/voicePresence.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/stores/gatewayIdempotency.test.ts`

- `frontend/src/stores/voicePresence.ts`
  - References:
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/stores/guilds.ts`
  - Owns:
    - Connected voice guild/channel refs, voice states, latest voice signal,
      voice-channel derived state, and voice-presence mutation helpers.

- `frontend/src/stores/dms.ts`
  - References:
    - `frontend/src/stores/dmApi.ts`
    - `frontend/src/stores/dmGatewayHandlers.ts`
    - `frontend/src/stores/dmVisibility.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/stores/gatewayIdempotency.test.ts`
  - Owns:
    - DM list/message state, active-DM unread clearing, inactive-DM unread
      incrementing for gateway message dispatch, and relationship presence sync
      into matching DM rows.
    - Current-user DM identity normalization so sidebar rows display recipients
      while message rows preserve actual authors.

- `frontend/src/stores/dmApi.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/stores/dms.ts`
  - Owns:
    - Direct-message REST loaders and mutations.

- `frontend/src/stores/dmGatewayHandlers.ts`
  - References:
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/stores/dms.ts`
    - `frontend/src/stores/dmGatewayHandlers.test.ts`
  - Owns:
    - Direct-message gateway payload validation and callback dispatch.

- `frontend/src/stores/dmVisibility.ts`
  - References:
    - `frontend/src/types.ts`
    - `frontend/src/utils/visualNoise.ts`
  - Referenced by:
    - `frontend/src/stores/dms.ts`
    - `frontend/src/stores/dmVisibility.test.ts`
  - Owns:
    - Relationship, participant, DM, and DM-message visibility filtering.

- `frontend/src/stores/guildVisibility.ts`
  - References:
    - `frontend/src/types.ts`
    - `frontend/src/utils/visualNoise.ts`
  - Referenced by:
    - `frontend/src/stores/guilds.ts`
    - `frontend/src/stores/guildVisibility.test.ts`
  - Owns:
    - Guild, channel, and server-message visibility filtering.

- `frontend/src/stores/navigation.ts`
  - References:
    - `frontend/src/services/browserApi.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/stores/navigation.test.ts`
  - Owns:
    - Active app destination state and per-user refresh-safe workspace location
      persistence for Friends, DM, server text, and voice-channel destinations.

- `frontend/src/stores/preferences.ts`
  - References:
    - `frontend/src/services/browserApi.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/i18n/index.ts`

- `frontend/src/stores/store.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`

### Composables

- `frontend/src/composables/useGateway.ts`
  - References:
    - `frontend/src/i18n/index.ts`
    - `frontend/src/services/browserApi.ts`
  - Referenced by:
    - `frontend/src/App.vue`
  - Talks to:
    - Backend `/gateway` WebSocket.
  - Owns:
    - Gateway identify, heartbeat, ACK timeout, bounded reconnect, dispatch
      routing, and reconnect-success callbacks used for REST reconciliation.

- `frontend/src/composables/useVoiceRtc.ts`
  - References:
    - `frontend/src/composables/voiceMedia.ts`
    - `frontend/src/composables/voicePeerConnections.ts`
    - `frontend/src/composables/voiceStats.ts`
    - `frontend/src/composables/voiceVad.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/composables/useVoiceSessionController.ts`
  - Talks to:
    - Browser `navigator.mediaDevices`, page lifecycle events, `RTCPeerConnection`,
      and WebRTC APIs.
  - Owns:
    - Local microphone and screen capture lifecycle, reserved screen-share sender
      track replacement, screen-share state broadcast, explicit local microphone
      mute state/setter, and voice RTC cleanup.

- `frontend/src/composables/voiceMedia.ts`
  - Referenced by:
    - `frontend/src/App.vue` for media error translation keys.
    - `frontend/src/components/SettingsView.vue` for safe constraint-support display
      and voice-processing preference toggles.
    - `frontend/src/composables/useVoiceRtc.ts`
    - `frontend/src/composables/voicePeerConnections.ts`
    - `frontend/src/composables/voiceMedia.test.ts`
  - Talks to:
    - Browser `navigator.mediaDevices`, `localStorage`, and media stream tracks.
  - Owns:
    - Typed microphone/screen capture errors, local voice-processing preferences,
      browser-supported audio constraint detection, and media-track cleanup.

- `frontend/src/composables/voiceVad.ts`
  - Referenced by:
    - `frontend/src/composables/useVoiceRtc.ts`
  - Talks to:
    - Browser `AudioContext`, analyser nodes, and interval timers.

- `frontend/src/composables/voicePeerConnections.ts`
  - References:
    - `frontend/src/composables/voiceMedia.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/composables/useVoiceRtc.ts`
  - Owns:
    - Channel-scoped peer connection registry, remote stream mutation,
      offer/answer/ICE handling, pending ICE candidate queueing, stale signal
      filtering, bounded failed-peer retry, reserved video transceivers for screen
      sharing, explicit screen-share state signal handling, remote screen-track
      state refresh, and participant synchronization.

- `frontend/src/composables/useVoiceSessionController.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/services/browserApi.ts`
    - `frontend/src/composables/useGateway.ts`
    - `frontend/src/composables/useVoiceRtc.ts`
    - `frontend/src/stores/guilds.ts`
    - `frontend/src/stores/session.ts`
    - `frontend/src/i18n/index.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`
  - Owns:
    - Voice config loading, voice join/leave/switch orchestration, mute/deafen
      gateway updates, safe reload rejoin recovery metadata, automatic rejoin after
      gateway-ready refresh recovery, screen-share toggle orchestration, voice
      participant sync, and incoming voice-signal handling.

- `frontend/src/i18n/index.ts`
  - References:
    - `frontend/src/stores/preferences.ts`
  - Referenced by:
    - Most user-facing components and `frontend/src/App.vue`.

### Component Inputs

- `frontend/src/components/AuthPanel.vue`
  - Emits auth events consumed by `frontend/src/App.vue`.
- `frontend/src/components/ServerRail.vue`
  - Receives guild list and rail metadata from `frontend/src/App.vue`.
  - Emits server navigation and add/discovery actions to `frontend/src/App.vue`.
- `frontend/src/components/PrivateChannelSidebar.vue`
  - Receives relationship/DM state from `frontend/src/App.vue`.
  - Emits friends/DM/search/menu actions to `frontend/src/App.vue`.
- `frontend/src/components/ChannelSidebar.vue`
  - Receives active guild, channels, voice state, invite permission, and user/voice
    status from `frontend/src/App.vue`.
  - Emits channel, invite, voice, user, and menu actions to `frontend/src/App.vue`;
    hides the server invite menu action when invite permission is absent.
- `frontend/src/components/FriendsHome.vue`
  - Receives relationships/activity state from `frontend/src/App.vue`.
  - Groups incoming/outgoing friend requests separately from online presence.
  - Emits message friend and relationship mutation actions to
    `frontend/src/App.vue`.
- `frontend/src/components/DirectMessageView.vue`
  - Receives selected DM and user state from `frontend/src/App.vue`.
  - Emits message-send actions to `frontend/src/App.vue`.
- `frontend/src/components/ChatView.vue`
  - Receives active channel, messages, and current user from `frontend/src/App.vue`.
  - Emits send/edit/delete actions to `frontend/src/App.vue`.
- `frontend/src/components/MemberList.vue`
  - Receives members, roles, and permission flags from `frontend/src/App.vue`.
  - Emits role/member actions to `frontend/src/App.vue`.
- `frontend/src/components/VoicePanel.vue`
  - Receives selected voice channel, participants, current user, and voice quality
    stats plus typed media-error copy from `frontend/src/App.vue`.
  - Emits join/leave/mute/screen-share/retry/settings actions to
    `frontend/src/App.vue`.
  - Keeps screen sharing available while deafened and disables the manual mute
    control while deafen owns local microphone suppression.
- `frontend/src/components/VoiceAudioSink.vue`
  - Receives current-channel remote audio stream from
    `frontend/src/App.vue`/`useVoiceRtc`.
  - Applies local deafen state to the remote audio element `muted` property.
- `frontend/src/components/VoiceVideoSink.vue`
  - Receives current-channel local or remote screen/video stream from
    `frontend/src/App.vue`/`useVoiceRtc`.
- `frontend/src/components/SettingsView.vue`
  - Receives current user, status controls, and debug-safe voice constraint support
    from `frontend/src/App.vue`.
  - Reads/writes local voice-processing preferences through
    `frontend/src/composables/voiceMedia.ts`.
  - Emits locale/status/settings actions to `frontend/src/App.vue`.

## High-Risk Dependency Clusters

- `frontend/src/App.vue`
  - Most frontend components, stores, gateway, voice, and dialogs currently pass
    through this file.
  - Refactor with small behavior-preserving stages.
- `frontend/src/stores/guilds.ts`
  - Coupled to API calls, gateway dispatch handling, messages, voice state, and
    guild admin workflows.
- `frontend/src/composables/useVoiceRtc.ts`
  - Coupled to browser media APIs, WebRTC peer state, VAD, screen share, and stats.
- `backend/app/repositories/guilds.py`
  - Coupled to guild, channel, invite, role, member, and message persistence.
- `backend/app/gateway/manager.py`
  - Coupled to connection registry, subscriptions, broadcasting, voice state, and
    stale connection cleanup.

Update this section whenever these clusters are split or a new central dependency
appears.
