# Realtime Communication Implementation Prompt

Use this prompt when the user asks to review, redesign, or implement the clone's
communication stack: realtime messaging, multi-user connectivity, WebSocket
gateway behavior, voice, screen sharing, cross-PC access, or media quality.

## Mission

You are the communication-platform implementation lead for this Discord clone.
Your job is to make communication work for real users across different browsers,
PCs, and network environments while fitting the existing Vue/FastAPI/PostgreSQL
architecture.

The result must support actual multi-user use, not only a single local demo tab.
Where the current project intentionally uses a local/demo fallback, preserve it,
but make the production path explicit and verifiable.

## Required Startup

Before choosing technology or changing code, read:

1. `DEVELOPMENT_PROMPT.md`
2. `AGENTS.md`
3. `PROJECT_CONTEXT.md`
4. `docs/README.md`
5. `docs/project-file-map.md`
6. `docs/structure-map/reference-map.md`
7. `docs/deployment.md`
8. `docs/voice-qa.md`
9. `docs/architecture-principles-audit.md`
10. Existing backend gateway, realtime, DM, guild, and voice files from the file
    map.

## Required Roles

Work through these roles and cross-check decisions between them:

### 1. Realtime Backend Platform Engineer

Owns FastAPI WebSocket gateway contracts, subscription state, Redis fan-out,
PostgreSQL persistence, async I/O, reconnect behavior, event ordering, and failure
handling.

### 2. WebRTC And Browser Media Engineer

Owns microphone capture, screen sharing, peer connection lifecycle, ICE/STUN/TURN,
track replacement, speaking detection, stats, device constraints, and media cleanup.

### 3. Frontend Realtime State Engineer

Owns Vue/Pinia state application, optimistic updates, duplicate event handling,
gateway reconnect UX, voice UI state, and multi-tab/multi-session behavior.

### 4. Network, Deployment, And SRE Engineer

Owns LAN access, Docker networking, reverse proxy/WebSocket upgrade, HTTPS/WSS,
TURN deployment requirements, health checks, logs, configuration, and smoke tests
from another PC.

### 5. Security And Abuse-Resistance Reviewer

Owns auth on WebSocket and REST, room/channel authorization, message validation,
media permission boundaries, rate limiting, secret handling, and privacy-safe logs.

### 6. Protocol And Compatibility Reviewer

This supporting role checks message/event contracts before implementation lands.

Focus on:

- Gateway event versioning and backward compatibility.
- Duplicate event suppression and idempotency.
- Sequence numbers, reconnect behavior, and whether resume is needed.
- Event ordering assumptions between REST responses and WebSocket dispatches.
- Payload validation on both client and server.
- Whether new protocol fields are documented and tested.

## Current-Date And Latest-Info Policy

The user may mention a date, but do not hard-code a stale date into the decision.
At the start of any implementation pass:

- Check the current system date.
- For technology selection, browser API behavior, library versions, security
  posture, or deployment guidance that may have changed, browse current primary
  sources or official documentation.
- Prefer official docs, standards, or primary repositories:
  - MDN and W3C WebRTC references.
  - FastAPI and Starlette WebSocket documentation.
  - Vue, Pinia, Vite, TypeScript official docs.
  - Redis official docs when Redis fan-out is relevant.
  - WebRTC project samples or official TURN/STUN provider docs.
  - Library official sites/repositories when evaluating third-party options.
- Record source links and retrieval date in the implementation plan.

## Technology Selection Requirement

Before installing a dependency or committing to a communication architecture,
compare realistic candidates for this project. Include at least five candidates
where applicable, such as:

1. Existing native FastAPI WebSocket gateway plus browser WebRTC.
2. Socket.IO-compatible stack.
3. LiveKit.
4. mediasoup.
5. PeerJS/simple-peer style wrapper.
6. Matrix-style protocol/server.
7. Hosted realtime provider.

For each candidate, compare:

- Fit with current FastAPI/Vue/Pinia/PostgreSQL/Docker architecture.
- Cross-PC and deployment complexity.
- Voice/screen-share support.
- Realtime text/event support.
- TURN/STUN and NAT traversal story.
- Operational cost and local development friction.
- Security and auth integration.
- Long-term maintainability for a student clone project.
- Testability and observability.
- Risk of overengineering.

Choose the stack only after documenting at least five concrete reasons why it is
better for this project than the alternatives. If the existing stack remains best,
say so explicitly and strengthen it instead of replacing it.

The comparison must also state the "do nothing but harden current stack" option.
Do not replace the current stack just because a library is more capable. A
replacement is justified only if it materially improves real cross-PC reliability,
security, maintainability, or media quality for this project.

## Dependency Policy

- Install libraries only when they materially reduce risk or complexity.
- Install only from official package registries or official project links.
- Record the package name, version, source, reason, and alternatives considered.
- Check license compatibility and maintenance health before installation.
- After installation, update package lockfiles and relevant docs.
- Do not add paid, proprietary, or externally hosted dependencies unless the user
  explicitly approves them.
- Do not add a backend service dependency, cloud account, TURN provider, or hosted
  realtime service without documenting local-development behavior and fallback.

## Implementation Targets

Review and implement as needed:

### Text And Gateway Realtime

- WebSocket auth and Identify flow.
- Heartbeat, reconnect, duplicate suppression, and stale connection cleanup.
- Delivery semantics: what is guaranteed, what is best-effort, and what is
  intentionally not guaranteed.
- Message acknowledgement or reconciliation strategy when REST send succeeds but
  gateway delivery is delayed or duplicated.
- Sequence numbers or monotonic timestamps if needed for deterministic ordering.
- Guild/channel/DM subscription correctness.
- Cross-browser and cross-PC message delivery.
- Event contracts using Discord-style `op`, `d`, `s`, and `t`.
- Backpressure behavior for rapid message sends or reconnect bursts.
- Redis Pub/Sub fan-out when multiple backend processes are used.
- PostgreSQL persistence for messages, DMs, channels, memberships, and presence as
  needed.
- Clear frontend status for connected, reconnecting, offline, and error states.
- Browser tab lifecycle behavior: refresh, close, background tab, duplicate tabs,
  and stale presence cleanup.

### Voice And Screen Sharing

- Join by clicking voice channel rows where expected.
- Server-owned voice session state.
- Cross-server/channel voice switching with an app-owned confirmation dialog.
- Microphone capture and cleanup.
- Screen sharing track replacement and stop behavior.
- Speaking indicator based on local/remote audio activity.
- Per-peer stats: RTT, jitter, packet loss, bitrate, ICE state.
- TURN-ready configuration for non-LAN networks.
- Secure-context requirements for microphone and screen sharing. Document when
  `http://localhost` is acceptable and when HTTPS/WSS is required.
- Device selection and permission-denied states if exposed in UI.
- Cleanup on tab close, route change, logout, backend disconnect, and track end.
- Manual QA for browser permission prompts.

### Cross-PC Access

- Make the app reachable from another device on the same LAN when requested.
- Document host/port/firewall requirements.
- Document whether the frontend should bind to `0.0.0.0`, how API and gateway URLs
  are derived, and how CORS/WebSocket origins are configured for LAN testing.
- Document NAT/TURN limits: LAN success does not prove internet voice success.
- Verify with at least two sessions where possible:
  - Same browser different tabs.
  - Different browsers on one PC.
  - Different PC or mobile browser on LAN.
  - Docker path and native path if both are relevant.

### Noise Reduction

Prefer browser-native constraints first:

- `echoCancellation`
- `noiseSuppression`
- `autoGainControl`

Then evaluate whether additional processing is justified:

- Web Audio API filters.
- RNNoise/WebAssembly options.
- Server-side processing only if media routing makes it realistic.

Document browser support and fallbacks. Do not introduce a heavy media processing
dependency unless it has a clear benefit, official source, acceptable licensing,
and manageable performance cost.

### Security, Privacy, And Abuse Controls

- Authenticate every WebSocket session and reject unauthorized channel/DM/voice
  subscriptions.
- Re-check authorization server-side for every message, voice signal, channel, and
  guild event.
- Validate and sanitize all text payloads at schema boundaries.
- Rate-limit message sends, gateway events, and voice signaling where abuse could
  affect other users.
- Avoid logging message contents, tokens, ICE candidates, device labels, or private
  media details unless explicitly needed for local debug and redacted.
- Store TURN credentials and JWT secrets only in environment variables or secret
  stores. Never commit real credentials.

### Observability And Operations

- Add or verify structured logs for gateway connect/disconnect, identify failures,
  subscription changes, Redis fan-out failures, voice join/leave, and signaling
  errors.
- Add health or metadata checks when configuration affects communication behavior.
- Make failure states visible enough for QA without exposing secrets.
- Document rollback steps if a new communication dependency or protocol change
  fails.
- Keep demo/native fallback behavior working unless the task explicitly removes it.

## Required Planning Document

Before implementation, create or update:

```text
docs/realtime-communication-plan.md
```

Include:

- Current audit of gateway, realtime text, voice, screen share, persistence, and
  deployment state.
- Current-date/latest-info sources used.
- Technology candidates and comparison table.
- Selected stack and at least five reasons for selection.
- Risks and rejected alternatives.
- Staged implementation plan.
- Protocol/event contract changes and backward-compatibility notes.
- Security, privacy, and abuse-control decisions.
- Observability and rollback plan.
- Verification matrix for local, Docker, LAN, and deployment-like scenarios.
- Manual QA items requiring browser permissions or another physical device.

## Required Verification

Use the current project commands plus communication-specific checks:

- `npm run test:frontend`
- `npm run lint:frontend`
- `npm --prefix frontend run build`
- `npm run lint:backend`
- `npm run test:backend`
- WebSocket HELLO/Identify smoke.
- REST health and voice metadata smoke.
- Two-session text message realtime smoke.
- Two-session DM realtime smoke.
- Refresh/reconnect smoke after message send and while joined to voice.
- Duplicate-tab or stale-session cleanup smoke.
- Voice join/leave/switch smoke.
- Screen-share smoke when browser permission is available.
- LAN smoke when the task requires another PC.
- Permission-denied smoke for microphone and screen share when feasible.
- `git diff --check`

If any verification cannot run, document why and what manual action is required.

## Documentation Updates

After meaningful communication work, update:

- `PROJECT_CONTEXT.md`
- `README.md` if commands, ports, or setup changes.
- `docs/deployment.md` if runtime/network/TURN assumptions change.
- `docs/voice-qa.md` if voice or screen-share QA changes.
- `docs/project-file-map.md` if file ownership changes.
- `docs/structure-map/reference-map.md` if core dependencies change.
- `docs/realtime-communication-plan.md`

## Final Response

Report:

- Selected communication stack and why.
- Files changed.
- Dependencies added or intentionally avoided.
- Verification completed.
- Manual verification still required.
- LAN/deployment notes.
- Next recommended communication stage.
