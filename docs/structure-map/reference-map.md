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
    - `backend/app/realtime/publisher.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/services/guild_service.py`
  - Referenced by:
    - `backend/app/api/router.py`

- `backend/app/api/routes/channels.py`
  - References:
    - `backend/app/api/dependencies.py`
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
    - `backend/app/realtime/publisher.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
    - `backend/app/services/dm_service.py`
  - Referenced by:
    - `backend/app/api/router.py`

- `backend/app/api/routes/users.py`
  - References:
    - `backend/app/api/dependencies.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
    - `backend/app/services/dm_service.py`
  - Referenced by:
    - `backend/app/api/router.py`

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
    - `backend/app/db/pool.py`
    - `backend/app/demo/store.py`
    - `backend/app/repositories/dms.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
  - Referenced by:
    - `backend/app/api/routes/dms.py`
    - `backend/app/api/routes/users.py`
    - `backend/app/gateway/router.py`

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
    - `backend/app/domain/snowflake.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/schemas/message.py`
  - Referenced by:
    - `backend/app/services/guild_storage.py`
    - `backend/app/repositories/guild_channels.py`
    - `backend/app/repositories/guild_invites.py`
    - `backend/app/repositories/guild_members.py`
    - `backend/app/repositories/guild_messages.py`
    - `backend/app/repositories/guild_roles.py`
    - `backend/tests/test_guild_repository.py`

- `backend/app/repositories/dms.py`
  - References:
    - `backend/app/db/pool.py`
    - `backend/app/domain/snowflake.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/schemas/dm.py`
  - Referenced by:
    - `backend/app/services/dm_service.py`
    - `backend/tests/test_dm_repository.py`

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
    - `backend/app/core/security.py`
    - `backend/app/gateway/events.py`
    - `backend/app/gateway/manager.py`
    - `backend/app/gateway/opcodes.py`
    - `backend/app/schemas/auth.py`
    - `backend/app/services/dm_service.py`
    - `backend/app/services/guild_service.py`
  - Referenced by:
    - `backend/app/main.py`

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
    - `backend/app/realtime/publisher.py`
    - `backend/app/realtime/subscriber.py`
    - `backend/tests/test_gateway_manager.py`

- `backend/app/gateway/connection.py`
  - References:
    - `backend/app/gateway/opcodes.py`
  - Referenced by:
    - `backend/app/gateway/manager.py`
    - `backend/app/gateway/broadcaster.py`
    - `backend/app/gateway/subscriptions.py`
    - `backend/app/gateway/voice_service.py`
    - `backend/app/gateway/zombie_reaper.py`

- `backend/app/gateway/broadcaster.py`, `subscriptions.py`, `voice_service.py`,
  `zombie_reaper.py`
  - Referenced by:
    - `backend/app/gateway/manager.py`

- `backend/app/realtime/publisher.py`
  - References:
    - `backend/app/gateway/manager.py`
    - `backend/app/realtime/events.py`
    - `backend/app/realtime/redis_bus.py`
    - `backend/app/schemas/dm.py`
    - `backend/app/schemas/guild.py`
    - `backend/app/schemas/message.py`
  - Referenced by:
    - `backend/app/api/routes/channels.py`
    - `backend/app/api/routes/dms.py`
    - `backend/app/api/routes/guilds.py`

- `backend/app/realtime/subscriber.py`
  - References:
    - `backend/app/gateway/manager.py`
    - `backend/app/realtime/events.py`
    - `backend/app/realtime/redis_bus.py`
  - Referenced by:
    - `backend/app/main.py`

## Frontend References

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
    - `frontend/src/stores/dms.ts`
    - `frontend/src/stores/guilds.ts`
    - `frontend/src/stores/navigation.ts`
    - `frontend/src/stores/preferences.ts`
    - `frontend/src/stores/session.ts`
    - `frontend/src/stores/store.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/main.ts`

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

- `frontend/src/stores/session.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/types.ts`
  - Referenced by:
    - `frontend/src/App.vue`

- `frontend/src/stores/guilds.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/stores/channelMessages.ts`
    - `frontend/src/stores/guildAdmin.ts`
    - `frontend/src/stores/guildGatewayHandlers.ts`
    - `frontend/src/types.ts`
    - `frontend/src/utils/visualNoise.ts`
  - Referenced by:
    - `frontend/src/App.vue`

- `frontend/src/stores/dms.ts`
  - References:
    - `frontend/src/services/api.ts`
    - `frontend/src/types.ts`
    - `frontend/src/utils/visualNoise.ts`
  - Referenced by:
    - `frontend/src/App.vue`

- `frontend/src/stores/navigation.ts`
  - Referenced by:
    - `frontend/src/App.vue`

- `frontend/src/stores/preferences.ts`
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
  - Referenced by:
    - `frontend/src/App.vue`
  - Talks to:
    - Backend `/gateway` WebSocket.

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
    - Browser `navigator.mediaDevices`, `RTCPeerConnection`, and WebRTC APIs.

- `frontend/src/composables/voiceMedia.ts`
  - Referenced by:
    - `frontend/src/composables/useVoiceRtc.ts`
    - `frontend/src/composables/voicePeerConnections.ts`
  - Talks to:
    - Browser `navigator.mediaDevices`.

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
    - Peer connection registry, remote stream mutation, offer/answer/ICE handling,
      screen-share track renegotiation, and participant synchronization.

- `frontend/src/composables/useVoiceSessionController.ts`
  - References:
    - `frontend/src/services/api.ts`
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
      gateway updates, screen-share toggle orchestration, voice participant sync,
      and incoming voice-signal handling.

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
  - Receives active guild, channels, voice state, and user/voice status from
    `frontend/src/App.vue`.
  - Emits channel, invite, voice, user, and menu actions to `frontend/src/App.vue`.
- `frontend/src/components/FriendsHome.vue`
  - Receives relationships/activity state from `frontend/src/App.vue`.
  - Emits message friend and local UI actions to `frontend/src/App.vue`.
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
    stats from `frontend/src/App.vue`.
  - Emits join/leave/mute/screen-share actions to `frontend/src/App.vue`.
- `frontend/src/components/VoiceAudioSink.vue`
  - Receives remote audio stream from `frontend/src/App.vue`/`useVoiceRtc`.
- `frontend/src/components/VoiceVideoSink.vue`
  - Receives remote screen/video stream from `frontend/src/App.vue`/`useVoiceRtc`.
- `frontend/src/components/SettingsView.vue`
  - Receives current user and status controls from `frontend/src/App.vue`.
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
