# Action Error Remediation - 2026-06-21

## Scope

This pass audits button/action error surfaces across the Discord clone and hardens
the cases where recoverable browser or WebRTC errors were displayed as persistent
app errors.

## Problems

### E1. Internal API fallback messages exposed implementation paths

- Location: `frontend/src/services/api.ts`
- Current behavior: non-JSON failed API responses could show messages such as
  `POST /api/... failed with 500`.
- Expected behavior: users should see a concise app-owned message without
  internal method/path details.
- Resolution: generic HTTP fallbacks now map common status codes to user-facing
  Korean messages and hide internal API paths.
- Verification: message-send and other API call failures should no longer expose
  request method/path strings when the backend has no detailed error body.

### E2. Voice media errors could duplicate across global and voice-specific UI

- Location: `frontend/src/composables/useVoiceSessionController.ts`
- Current behavior: microphone/device connection failures could be displayed by
  both the voice media error surface and the workspace/global action error.
- Expected behavior: typed media failures should stay in the voice-specific error
  surface, while only non-media voice join failures use the general action error.
- Resolution: voice connect catch paths skip the general action error when
  `voiceRtc.error` or `voiceRtc.errorCode` already owns the failure.
- Verification: denied microphone or unavailable device should show one
  voice-specific error path, not multiple persistent alerts.

### E3. Recoverable WebRTC signaling races were shown as user-facing errors

- Location: `frontend/src/composables/useVoiceSessionController.ts`
- Current behavior: recoverable `RTCPeerConnection` races, such as answer/offer
  state mismatch or `m-lines` order errors during renegotiation, could appear as
  global action errors even when the peer registry can recover on the next offer.
- Expected behavior: transient WebRTC signaling state errors should be ignored at
  the user-facing layer; real unrecoverable signaling failures should still be
  surfaced.
- Resolution: participant-sync and signal-handling catch paths now suppress known
  recoverable WebRTC state messages and preserve the existing error path for
  other failures.
- Verification: duplicate refresh/rejoin/screen-share renegotiation should not
  show raw `RTCPeerConnection` exceptions, while real connection failures still
  use the voice error surface.

## Guardrails

- No browser-native `alert`, `confirm`, or `prompt` usage was introduced.
- No signaling, SDP, ICE, JWT, or media-device details are logged or documented.
- Existing P2P voice and screen-share transport behavior remains unchanged; this
  pass only changes error routing and API fallback copy.

## Verification Log

- Passed: `npm run lint:frontend`
- Passed: `npm run test:frontend`
- Passed: `npm --prefix frontend run build`
- Passed: `npm run smoke:realtime:browser:https`
  - Confirmed server text realtime, DM realtime, DM composer focus retention,
    voice reload rejoin, remote audio sinks after reload, remote screen video
    after receiver reload, and no browser errors in the smoke result.
- Passed: `git diff --check`
