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
  - Owns:
    - Authenticated DM list/create, DM message create, and current-author DM
      message delete endpoints. Message create/delete publish DM gateway events
      after REST persistence succeeds.

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
  - Owns:
    - Async service boundary for relationships, presence, DM list/create, DM
      message create, and author-only DM message delete.

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
      protocol, including author-only DM message deletion.

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
    - `backend/app/realtime/publisher.py`
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
    - Voice-state snapshot dispatch for READY and post-join synchronization across
      guild voice channels and DM private voice rooms.

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
      guild/channel or DM-room state used for disconnect cleanup.

- `backend/app/gateway/broadcaster.py`, `subscriptions.py`, `voice_service.py`,
  `zombie_reaper.py`
  - Referenced by:
    - `backend/app/gateway/manager.py`
  - `voice_service.py` owns the in-memory voice-state registry used to send
    authoritative `VOICE_STATE_SNAPSHOT` payloads to late-joining clients.
  - `voice_service.py` also owns pending voice leave scheduling and cancellation
    when the same user rejoins a guild or DM voice room during the
    normal-disconnect grace window.

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
    - `frontend/src/components/CreateDmDialog.vue`
    - `frontend/src/components/ChannelSidebar.vue`
    - `frontend/src/components/ChatView.vue`
    - `frontend/src/components/DirectMessageView.vue`
    - `frontend/src/components/FriendProfileDialog.vue`
    - `frontend/src/components/VoicePanel.vue`
  - Referenced by:
    - `docs/realtime-communication-qa.md`
    - `docs/remediation-tasks/realtime-communication-plan.md`
  - Owns:
    - C8 repeatable two-browser same-PC communication smoke for server text, DM,
      invite-DM delivery, owner/member invite permission UI/API behavior, voice
      peer visibility, remote audio sink, independent mute/deafen behavior, fake
      screen-share UI, local screen-preview rendering, remote screen-video
      rendering, screen-share stop cleanup,
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
    - `docs/external-deployment-decision.md`
    - `docs/voice-qa.md`
  - Owns:
    - Safe operator-facing STUN/TURN readiness output without ICE URLs, TURN
      credentials, candidates, tokens, message content, or media device labels.

- `scripts/deployment_readiness_check.mjs`
  - References:
    - `/api/health`
    - `/api/meta/voice/readiness`
    - `/gateway`
    - root `package.json` script `check:deployment:readiness`.
  - Referenced by:
    - `README.md`
    - `docs/deployment.md`
    - `docs/external-deployment-decision.md`
    - `docs/voice-qa.md`
    - `docs/realtime-communication-qa.md`
  - Owns:
    - Safe external deployment readiness verification for HTTPS origin shape,
      backend health, TURN readiness, and gateway WSS HELLO without credentials.

- `scripts/submission_readiness_check.mjs`
  - References:
    - `/`
    - `/api/health`
    - `/api/meta/voice/readiness`
    - `/gateway`
    - root `package.json` script `check:submission:local`.
  - Referenced by:
    - `README.md`
    - `docs/assignment-submission-guide.md`
    - `docs/project-file-map.md`
  - Owns:
    - Local assignment submission readiness verification.
    - Auto-detection for normal HTTP Docker origin and local HTTPS Docker origins.
    - Safe frontend/API/WebSocket/voice metadata checks without printing secrets.

- `docs/assignment-submission-guide.md`
  - References:
    - `README.md`
    - `compose.yaml`
    - `compose.https.yaml`
    - `compose.cloudflare-tunnel.yaml`
    - `scripts/create_lan_https_cert.ps1`
    - `scripts/deployment_readiness_check.mjs`
    - `scripts/realtime_browser_smoke.mjs`
    - `scripts/submission_readiness_check.mjs`
    - `docs/deployment.md`
    - `docs/voice-qa.md`
    - `docs/realtime-communication-qa.md`
    - `docs/external-deployment-decision.md`
    - `docs/external-deployment-runbook.md`
  - Referenced by:
    - `README.md`
    - `docs/README.md`
    - `docs/deployment.md`
    - `docs/project-file-map.md`
    - `docs/voice-qa.md`
    - `docs/realtime-communication-qa.md`
  - Owns:
    - Default assignment submission path: local Docker Compose execution.
    - Same-Wi-Fi HTTPS LAN demo routing.
    - Optional Cloudflare Tunnel temporary external access guidance.
    - Feature check order and explicit limits for non-permanent deployment.

- `compose.https.yaml`
  - References:
    - `compose.yaml`
    - `frontend/vite.config.ts`
    - ignored local `certs/lan-dev.pfx`
  - Referenced by:
    - root `package.json` scripts `docker:up:https` and
      `docker:up:https:detached`
    - `README.md`
    - `docs/deployment.md`
    - `docs/voice-qa.md`
  - Owns:
    - Docker HTTPS LAN media path for non-localhost microphone and screen-capture
      testing.

- `compose.cloudflare-tunnel.yaml`
  - References:
    - `compose.yaml`
    - `frontend/Dockerfile`
    - `frontend/nginx.conf`
    - backend service health from the base Compose stack.
  - Referenced by:
    - root `package.json` script `docker:up:cloudflare-tunnel`
    - `docs/assignment-submission-guide.md`
    - `docs/deployment.md`
    - `docs/voice-qa.md`
    - `docs/realtime-communication-qa.md`
    - `docs/project-file-map.md`
  - Owns:
    - HMR-free local `frontend-tunnel` runtime service on port `5174` for
      Cloudflare Quick Tunnel demos.

- `compose.production.example.yaml`
  - References:
    - `backend/Dockerfile`
    - `frontend/Dockerfile`
    - `deploy/Caddyfile.example`
    - `deploy/coturn/turnserver.conf.example`
    - `deploy/production.env.example` when rendered through `--env-file`
  - Referenced by:
    - `README.md`
    - `docs/deployment.md`
    - `docs/external-deployment-decision.md`
    - `docs/external-deployment-runbook.md`
    - `docs/remediation-tasks/realtime-communication-plan.md`
  - Owns:
    - Placeholder-only single-server external QA topology with Caddy HTTPS,
      runtime app containers, PostgreSQL, Redis, and optional coturn.

- `deploy/production.env.example`
  - Referenced by:
    - `README.md`
    - `docs/deployment.md`
    - `docs/external-deployment-decision.md`
    - `docs/external-deployment-runbook.md`
    - `docs/project-file-map.md`
  - Owns:
    - Placeholder-only production environment template. Real `deploy/*.env` files
      are ignored and must stay host-local.

- `deploy/Caddyfile.example`
  - Referenced by:
    - `compose.production.example.yaml`
    - `docs/deployment.md`
    - `docs/external-deployment-decision.md`
    - `docs/external-deployment-runbook.md`
  - Owns:
    - Public HTTPS reverse-proxy routing for `/api`, `/gateway`, and frontend app
      routes.

- `deploy/coturn/turnserver.conf.example`
  - Referenced by:
    - `compose.production.example.yaml`
    - `docs/deployment.md`
    - `docs/external-deployment-decision.md`
  - Owns:
    - Placeholder-only self-hosted coturn configuration template.

- `scripts/create_lan_https_cert.ps1`
  - References:
    - Windows PowerShell/.NET certificate APIs
    - ignored local `certs/` output folder
  - Referenced by:
    - `README.md`
    - `docs/deployment.md`
    - `docs/voice-qa.md`
  - Owns:
    - Local self-signed certificate generation for same-Wi-Fi HTTPS development.

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
    - `VITE_HTTPS_PFX_FILE`
    - `VITE_HTTPS_KEY_FILE`
    - `VITE_HTTPS_CERT_FILE`
  - Referenced by:
    - `frontend/package.json` script `dev:lan:https`.
  - Owns:
    - Early failure for missing local HTTPS LAN certificate configuration.

- `frontend/vite.config.ts`
  - References:
    - `VITE_BACKEND_PROXY_TARGET`
    - `VITE_HTTPS_PFX_FILE`
    - `VITE_HTTPS_PFX_PASSPHRASE`
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
    - Friends/DM call-entry orchestration that opens the selected DM and delegates
      to `useVoiceSessionController.ts` for DM-scoped voice join/leave.
    - Incoming DM private-call banner state derived from DM voice presence,
      including accept/decline actions that keep the call in the same DM-scoped
      WebRTC room.

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
  - Owns:
    - Guild aggregate state, gateway state application, and guild member
      presence-state updates from `PRESENCE_UPDATE` dispatches.

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
    - `frontend/src/stores/preferences.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/stores/gatewayIdempotency.test.ts`
  - Owns:
    - DM list/message state, active-DM unread clearing, inactive-DM unread
      incrementing for gateway message dispatch, muted-DM unread suppression,
      relationship identity sync into matching DM rows, and relationship-only
      lightweight presence update application.
    - Current-user DM identity normalization so sidebar rows display recipients
      while message rows preserve actual authors.
    - Local REST-backed DM message deletion and `DM_MESSAGE_DELETE` gateway
      removal for remote subscribers.

- `frontend/src/stores/dmApi.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/stores/dms.ts`
  - Owns:
    - Direct-message REST loaders and mutations, including DM message create and
      author-only DM message delete wrappers.

- `frontend/src/stores/dmGatewayHandlers.ts`
  - References:
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/stores/dms.ts`
    - `frontend/src/stores/dmGatewayHandlers.test.ts`
  - Owns:
    - Direct-message gateway payload validation and callback dispatch, including
      DM create/message create/message delete, relationship, and presence events.

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
    - `frontend/src/components/FriendsHome.vue`
    - `frontend/src/i18n/index.ts`
    - `frontend/src/stores/dms.ts`
  - Owns:
    - Locale preference, local muted-DM ID persistence, and local favorite-friend
      ID persistence.

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
      routing, presence updates, and reconnect-success callbacks used for REST
      reconciliation.

- `frontend/src/composables/useVoiceRtc.ts`
  - References:
    - `frontend/src/composables/voiceMedia.ts`
    - `frontend/src/composables/voicePeerConnections.ts`
    - `frontend/src/composables/voiceStats.ts`
    - `frontend/src/composables/voiceTransport.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`
    - `frontend/src/composables/useVoiceSessionController.ts`
  - Talks to:
    - Browser `navigator.mediaDevices`, page lifecycle events, `RTCPeerConnection`,
      and WebRTC APIs.
  - Owns:
    - Local microphone and screen capture lifecycle, Web Audio input processing
      lifecycle, voice device settings refresh/update state, reserved screen-share
      sender track replacement, screen-share state broadcast, explicit local
      microphone mute state/setter, and voice RTC cleanup.
    - Active-call microphone-chain rebuild for input device or RNNoise mode
      changes, with peer sender audio-track replacement instead of leaving the
      current call.
    - Current `p2p-webrtc` implementation of the shared `VoiceTransport` contract.

- `frontend/src/composables/voiceTransport.ts`
  - References:
    - Vue `Ref`/`ShallowRef` types.
    - `frontend/src/types.ts`
    - `frontend/src/composables/voiceMedia.ts` types.
  - Referenced by:
    - `frontend/src/composables/useVoiceRtc.ts`
    - `frontend/src/composables/voicePeerConnections.ts`
    - `docs/voice-transport-architecture.md`
  - Owns:
    - Voice transport kind, shared connect options, state shape, and operation
      signatures that allow the current P2P implementation to remain replaceable
      by a future SFU-backed transport.

- `frontend/src/composables/voiceMedia.ts`
  - Referenced by:
    - `frontend/src/App.vue` for media error translation keys.
    - `frontend/src/components/SettingsView.vue` for safe constraint-support display
      and voice-processing preference toggles plus the only exact live input-level
      meter.
    - `frontend/src/composables/useVoiceRtc.ts`
    - `frontend/src/composables/voicePeerConnections.ts`
    - `frontend/src/composables/voiceMedia.test.ts`
  - Talks to:
    - Browser `navigator.mediaDevices`, `localStorage`, `AudioContext`, and media
      stream tracks.
  - Owns:
    - Typed microphone/screen capture errors, local voice-processing preferences,
      local voice device preferences, browser-supported audio constraint detection,
      optional denoiser setup before WebRTC transmission: off baseline and RNNoise
      through `@sapphi-red/web-noise-suppressor`.
    - Microphone input volume, pre-gate RMS-based input-level sampling, optional
      soft sensitivity/noise-gate processing, sustained-input stable defaults,
      one-time default setting migration, and media-track cleanup.

- `frontend/src/composables/voiceVad.ts`
  - Referenced by:
    - `frontend/src/composables/useVoiceRtc.ts`
  - Talks to:
    - Browser `AudioContext`, analyser nodes, and interval timers.
  - Owns:
    - Diagnostic speaking-state sampling. Public input-level display is sourced from
      the `voiceMedia.ts` input processor in current voice sessions.

- `frontend/src/composables/voicePeerConnections.ts`
  - References:
    - `frontend/src/composables/voiceMedia.ts`
    - `frontend/src/composables/voiceTransport.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/composables/useVoiceRtc.ts`
  - Owns:
    - Channel-scoped peer connection registry, remote stream mutation,
      offer/answer/ICE handling, pending ICE candidate queueing, stale signal
      filtering, bounded failed-peer retry, reserved video transceivers for screen
      sharing, explicit screen-share state signal handling, remote screen-track
      state refresh, local audio-track replacement for microphone-chain reloads,
      remote received-audio speaking detection, and participant synchronization.

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
    - Voice config loading, guild voice join/leave/switch orchestration, DM private
      voice join/leave orchestration, mute/deafen gateway updates, safe reload
      rejoin recovery metadata for guild voice channels, automatic rejoin after
      gateway-ready refresh recovery, screen-share toggle orchestration, voice
      participant sync, incoming context-scoped voice-signal handling, and DM-only
      solo-call auto-leave timing.

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
  - Emits friends/DM/search/start-new-DM actions to `frontend/src/App.vue`; DM
    rows expose target IDs for app-owned context menus.
- `frontend/src/components/CreateDmDialog.vue`
  - Receives accepted-friend relationship state from `frontend/src/App.vue`.
  - Emits selected recipient IDs to `frontend/src/App.vue` for `dms.createDm(...)`.
- `frontend/src/components/ChannelSidebar.vue`
  - Receives active guild, channels, voice state, invite permission, and user/voice
    status from `frontend/src/App.vue`.
  - Emits channel, invite, voice, user, and menu actions to `frontend/src/App.vue`;
    hides the server invite menu action when invite permission is absent.
- `frontend/src/components/FriendsHome.vue`
  - Receives relationships/activity state from `frontend/src/App.vue`.
  - Receives a reset key from `frontend/src/App.vue` so sidebar Friends navigation
    returns the visible tab to All.
  - Groups All friends into optional local favorites plus a single remaining
    friend list with a compact ascending/descending sort; pending requests stay
    separated only when both incoming and outgoing groups are present.
  - Visually distinguishes favorited friends through row-level favorite styling
    while persisting the preference in `frontend/src/stores/preferences.ts`.
  - Emits message friend, profile, call-entry, mute, and relationship mutation
    actions to `frontend/src/App.vue`.
- `frontend/src/components/FriendProfileDialog.vue`
  - Receives the selected friend and mute state from `frontend/src/App.vue`.
  - Emits profile-dialog message, call-entry, mute, and close actions to
    `frontend/src/App.vue`.
- `frontend/src/components/DirectMessageView.vue`
  - Receives selected DM and user state from `frontend/src/App.vue`.
  - Receives shared voice device settings/device lists from `frontend/src/App.vue`.
  - Emits message-send, current-user message delete, selected-DM profile,
    call-entry, conversation mute, voice mute/deafen, voice-device refresh, and
    voice-device update actions to `frontend/src/App.vue`.
  - Owns DM bottom-start scroll behavior, local/remote message row distinction,
    one-to-one intro status display, active private-call stage display, and local
    emoji plus DM call input/output popover state with outside-click/Escape
    dismissal. Active DM call controls group mute, deafen, quick input/output
    settings, and hang-up in one toolbar, and ongoing remote DM calls can render
    as joinable stages.
- `frontend/src/components/ChatView.vue`
  - Receives active channel, messages, and current user from `frontend/src/App.vue`.
  - Emits send/edit/delete actions to `frontend/src/App.vue`.
  - Owns bottom-anchored server-message scroll behavior, local message options,
    and composer panel state with outside-click/Escape dismissal.
- `frontend/src/components/MemberList.vue`
  - Receives members, roles, and permission flags from `frontend/src/App.vue`.
  - Emits role/member actions to `frontend/src/App.vue`.
- `frontend/src/components/VoicePanel.vue`
  - Receives selected voice channel, current user, voice quality stats, typed
    media-error copy, binary local speaking state, and voice device settings from
    `frontend/src/App.vue`.
  - Emits join/leave/mute/screen-share/retry, distinct My Account and Voice &
    Video settings actions, and quick voice device update/refresh actions to
    `frontend/src/App.vue`.
  - Keeps screen sharing and manual microphone mute available while deafened so
    deafen only controls local playback of remote audio.
  - Shows configured quick voice settings but does not receive or display exact
    live input level.
  - Owns quick input/output popover state, toggle-open chevrons,
    outside-click/Escape dismissal, and the lower-left user-status/connected-session
    card ordering. Its popovers are anchored above the full lower panel with extra
    clearance to avoid covering connected voice status.
- `frontend/src/components/VoiceAudioSink.vue`
  - Receives current-channel remote audio stream from
    `frontend/src/App.vue`/`useVoiceRtc`.
  - Applies local deafen state, output volume, and supported output sink selection
    to the remote audio element.
- `frontend/src/components/VoiceVideoSink.vue`
  - Receives current-channel local or remote screen/video stream from
    `frontend/src/App.vue`/`useVoiceRtc`.
- `frontend/src/components/SettingsView.vue`
  - Receives current user, status controls, debug-safe voice constraint support,
    voice device setting state, and the exact live input level from
    `frontend/src/App.vue`.
  - Reads/writes local voice-processing preferences and emits voice device
    setting changes through
    `frontend/src/composables/voiceMedia.ts`.
  - Owns the only user-facing exact microphone input-level meter; other workspace
    surfaces use binary speaking state only.
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
