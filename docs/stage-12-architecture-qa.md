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
