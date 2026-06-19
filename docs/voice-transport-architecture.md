# Voice Transport Architecture

Date: 2026-06-20

This document defines the voice/screen-share transport boundary for the Discord
clone. The current implementation remains WebRTC P2P plus gateway signaling. This
stage does not add LiveKit, mediasoup, or any SFU dependency. It only creates a
stable boundary so a future SFU transport can be evaluated without rewriting the
voice UI first.

## Current Ownership

Frontend:

- `frontend/src/composables/useVoiceSessionController.ts`
  - Owns user workflow: join, leave, switch, reload rejoin, mute/deafen publishing,
    screen-share command routing, and incoming gateway signal routing.
- `frontend/src/composables/useVoiceRtc.ts`
  - Current P2P transport implementation.
  - Owns microphone capture, input processing, local screen capture, mute, screen
    share, participant synchronization, signal handling, remote streams, and quality
    stats exposure.
- `frontend/src/composables/voicePeerConnections.ts`
  - Owns P2P-specific `RTCPeerConnection` lifecycle, offer/answer/ICE handling,
    screen sender renegotiation, remote stream mutation, and remote speaking
    detection.
- `frontend/src/composables/voiceMedia.ts`
  - Owns browser media capture, device settings, browser audio constraints,
    optional RNNoise, input-level sampling, and media cleanup.
- `frontend/src/components/VoicePanel.vue`
  - Renders transport state but should not know whether the media transport is P2P
    or SFU.

Backend:

- `backend/app/gateway/router.py`
  - Owns Discord-style gateway opcode handling.
  - Relays current P2P voice signals through `VOICE_SIGNAL`.
- `backend/app/gateway/events.py`
  - Owns gateway payload validation for voice state and P2P signal payloads.
- `backend/app/gateway/voice_service.py`
  - Owns authoritative voice-state snapshots, leave cleanup, and targeted signal
    delivery.

## Current Coupling Map

| Concern | Current owner | Coupling risk |
| --- | --- | --- |
| P2P offer/answer/ICE | `voicePeerConnections.ts` | Must remain inside P2P transport only |
| Participant list | backend voice snapshot + `guilds.connectedVoiceStates` | UI and transport both need consistent participant IDs |
| Mute/deafen | `useVoiceSessionController.ts` + `useVoiceRtc.ts` | Mute affects local outgoing microphone; deafen affects local playback |
| Screen-share start/stop | `useVoiceRtc.ts` + `voicePeerConnections.ts` | P2P requires sender replacement and renegotiation |
| Speaking state | `voiceMedia.ts`, `voicePeerConnections.ts`, `VoicePanel.vue` | Exact input level must stay local/settings-only; public UI gets binary speaking |
| Quality stats | `voiceStats.ts` over P2P peer registry | Future SFU stats need the same public shape |
| Reconnect/rejoin | `useVoiceSessionController.ts` | Should stay transport-neutral where possible |

## VoiceTransport Boundary

The public transport contract lives in:

- `frontend/src/composables/voiceTransport.ts`

The current default transport is:

- `kind: "p2p-webrtc"`
- implemented by `frontend/src/composables/useVoiceRtc.ts`

Required transport operations:

- `connect(options)`
- `disconnect()`
- `setMuted(muted)`
- `toggleMute()`
- `toggleScreenShare()`
- `syncParticipants(participants)`
- `handleSignal(signal)`
- `refreshVoiceDevices()`
- `updateVoiceDeviceSettings(settings)`

Required transport state:

- local microphone stream
- local screen stream
- remote streams
- connected/capturing state
- local mute state
- screen-share state
- binary local speaking state
- settings-only input level
- media error code/message
- safe media constraint support
- device settings/device lists
- quality stats

This keeps `VoicePanel.vue` and `useVoiceSessionController.ts` stable while a future
SFU implementation is developed.

## P2PTransport

Current P2P transport behavior:

1. `useVoiceSessionController.ts` loads ICE config from `/api/meta/voice`.
2. The user joins a voice channel through gateway `UPDATE_VOICE_STATE`.
3. `useVoiceRtc.ts` captures microphone and starts local media processing.
4. `voicePeerConnections.ts` creates P2P `RTCPeerConnection` objects after
   participant snapshots or updates arrive.
5. Offer/answer/ICE/screen state are sent through gateway `VOICE_SIGNAL`.
6. Remote streams and stats are exposed to the app shell and voice workspace.

This path remains the only active implementation.

## Future SFUTransport Shape

A future SFU transport should implement the same `VoiceTransport` interface but
must not reuse P2P offer/answer/ICE gateway messages as-is.

Likely additions:

- Backend REST API to issue short-lived media room tokens.
- Backend room mapping from guild/channel IDs to SFU room IDs.
- Backend permission checks before issuing a room token.
- Gateway dispatch or REST metadata for SFU room state if the SFU does not provide
  enough app-level participant metadata.
- Deployment service for LiveKit or mediasoup.
- TURN/TLS and UDP port handling for the media server.
- A migration flag such as `VOICE_TRANSPORT_KIND=p2p-webrtc|sfu-webrtc` only after
  the SFU path is implemented and verified.

### LiveKit Candidate

LiveKit is the preferred first SFU candidate if the project needs larger rooms,
because it provides an open-source SFU server, client SDKs, and a managed cloud
path. It still requires token issuing, room mapping, deployment, and QA work.

### mediasoup Candidate

mediasoup is a powerful lower-level SFU toolkit. It is better suited when the
project needs custom media-server behavior and can absorb more Node/server-side
integration complexity. It is not the first SFU candidate for this clone unless
LiveKit is insufficient.

## Backend Changes Needed For SFU

Do not add these until the SFU stage starts:

1. `POST /api/voice/rooms/{channel_id}/token`
   - Authenticates user.
   - Verifies guild/channel membership.
   - Verifies the channel is a voice channel.
   - Issues a short-lived SFU token without logging it.
2. Optional `GET /api/voice/rooms/{channel_id}/metadata`
   - Returns safe, non-secret room metadata.
3. Gateway compatibility layer:
   - Keep `VOICE_STATE_UPDATE` and `VOICE_STATE_SNAPSHOT` for app UI state.
   - Deprecate P2P-only offer/answer/ICE for SFU rooms.
   - Add SFU transport status dispatch only if required by the selected provider.
4. Deployment:
   - Add LiveKit or mediasoup service config outside the current production example
     until a concrete provider is selected.
   - Keep secrets and media tokens outside Git.

## Screen-Share Quality Decision Tree

Tune P2P first when:

- 1:1 screen share is blurry or low frame rate.
- Same-LAN quality is poor.
- The received stream is clear but the UI looks blurry due to CSS sizing or
  `object-fit`.
- `getDisplayMedia` constraints or sender parameters are too conservative.

Investigate P2P settings before SFU:

- Display capture width/height/frame-rate constraints.
- `RTCRtpSender.setParameters()` for screen-share sender bitrate and frame rate.
- CSS rendering size, aspect ratio, and scaling.
- WebRTC stats: outbound bitrate, packet loss, RTT, and frame dimensions.

Consider SFU when:

- 1:1 quality is acceptable but quality collapses with four or more viewers.
- Multiple simultaneous screen shares make sender upload/CPU unstable.
- Long-running rooms with many participants need server-side track forwarding.
- Different-network tests pass through TURN but multi-viewer screen share remains
  unstable due to sender bandwidth.

## Verification Policy

For this boundary stage:

- Do not add LiveKit/mediasoup dependencies.
- Do not remove P2P gateway signaling.
- Run frontend lint, frontend tests, frontend build, and browser realtime smoke
  when local services are available.
- Do not mark external TURN/NAT success complete.
- Do not log or document JWTs, TURN credentials, ICE candidates, media device
  labels, or message bodies.

2026-06-20 verification result:

- `npm run lint:frontend` passed.
- `npm run test:frontend` passed.
- `npm --prefix frontend run build` passed.
- `npm run smoke:realtime:browser:https` passed with server text realtime,
  DM realtime, invite realtime, voice remote audio, mute/deafen independence,
  screen-share start/stop, workspace refresh preservation, and voice auto-rejoin
  checks all green.
- Backend health responded on local HTTP. The frontend responded on local HTTPS.
- External TURN/NAT success remains not verified in this boundary stage.

For a future SFU stage:

- Keep P2P as a fallback until SFU passes local, LAN, and TURN/NAT QA.
- Add token-issuing tests before browser QA.
- Verify mute, deafen, speaking state, participant state, screen-share start/stop,
  reconnect, and refresh behavior against the same QA matrix as P2P.
