# External Deployment Decision

Date: 2026-06-20

Status: future always-on public deployment option. This is not the default
assignment submission path. For the current submission/demo flow, use local Docker
Compose plus optional Cloudflare Tunnel as documented in
`docs/assignment-submission-guide.md`.

This document selects the first external-network deployment path for the Discord
clone before any real public internet voice test is claimed complete. It is a
preparation and decision record only. External voice, screen sharing, and TURN/NAT
success remain pending until a real HTTPS/WSS host, TURN configuration, and two
different networks are available.

The selected single-VM path remains useful when the project later needs an
always-on public endpoint. It should not be treated as a completed deployment or a
required grading step.

## Current Readiness Structure

The repository already contains the placeholder-only deployment structure needed
for a first external QA host:

- `compose.production.example.yaml`
  - Example single-server topology with Caddy, runtime frontend/backend
    containers, PostgreSQL, Redis, and optional coturn profile.
  - Must be copied or adapted for a real host. Real secrets must not be committed.
- `deploy/Caddyfile.example`
  - Public HTTPS reverse-proxy example.
  - Keeps `/api` and `/gateway` on the same origin as the frontend.
- `deploy/coturn/turnserver.conf.example`
  - Placeholder-only coturn template.
  - Copy outside the repository before adding real TURN secrets.
- `scripts/deployment_readiness_check.mjs`
  - Safe readiness check for HTTPS origin shape, `/api/health`,
    `/api/meta/voice/readiness`, and `/gateway` HELLO over WSS.
  - Does not print JWTs, message bodies, ICE URLs, TURN credentials, ICE
    candidates, or media device labels.
- `deploy/production.env.example`
  - Placeholder-only environment template for the selected single-VM path.
  - Copy to `deploy/production.env` on the VM and fill real values there only.
- `docs/external-deployment-runbook.md`
  - Step-by-step execution guide for VM setup, Compose startup, readiness checks,
    manual external QA, and rollback.

Reference assumptions checked against primary documentation:

- Docker documents Compose use on a single remote server and recommends
  production-specific Compose changes such as environment, ports, service shape,
  and restart policy.
- Caddy can act as the HTTPS reverse proxy and automatically serve HTTPS when a
  domain name points to the machine and ports `80`/`443` are reachable.
- coturn is a free open-source STUN/TURN server suitable for WebRTC NAT traversal.

## Candidate Comparison

| Option | Cost | Setup Difficulty | HTTPS/WSS | WebSocket Stability | TURN Support | PostgreSQL/Redis | Maintenance | Fit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Local PC port forwarding | Lowest direct cost, but depends on home network | High: router, ISP NAT, firewall, changing IP, local certificate/domain issues | Possible with domain/DDNS and Caddy, but fragile | Works only while the PC/network is stable | Poor for self-hosted TURN behind home NAT; still likely needs hosted TURN | Local only, uptime tied to the PC | Poor | Not selected. Use only as a temporary reachability experiment |
| Oracle Cloud/GCP/AWS VM | Low to medium depending on VM size, free tier, traffic, and region | Medium: VM, firewall/security group, Docker, DNS | Strong with Caddy and a domain | Strong for a small clone if ports and proxy are stable | Strong: managed TURN or self-hosted coturn can be attached | Compose services or managed DB/Redis | Good | Good |
| Render/Fly.io/Railway PaaS | Low to medium, provider pricing and sleep limits vary | Low for app deploy, medium for multi-service realtime | Usually supported by platform | Generally possible, but provider-specific timeouts and scaling rules matter | Weak as an all-in-one path; TURN usually needs a separate provider | Managed DB/Redis options exist but split across provider features | Medium, provider-specific | Not first choice for TURN/WebRTC validation |
| Static frontend + separate backend | Flexible | Medium-high: split origins, CORS, cookie/token, WSS URL, deployment coordination | Possible, but HTTPS/WSS and CORS must be configured twice | Possible, but more moving parts | Still separate; needs hosted TURN or a VM | Backend host still required | Medium-low for this project | Not selected now. Useful later if frontend-only CDN is needed |
| Single VM Docker Compose | Predictable low VM cost plus bandwidth/TURN cost | Medium: one host, Docker, DNS, firewall, env file | Strong with Caddy same-origin proxy | Strong for current one-host gateway/API design | Strong: managed TURN first, self-hosted coturn optional | Compose PostgreSQL/Redis or managed replacements | Best current balance | Selected |

## Selected Path

Use a single VM/VPS with Docker Compose, Caddy HTTPS, runtime frontend/backend
containers, PostgreSQL, Redis, and TURN configured through environment variables.

Recommended first TURN choice:

1. Managed TURN provider for the first public external QA pass.
2. Self-hosted coturn on the same VM only if the user is ready to open and verify
   UDP/TCP `3478` plus the configured UDP relay port range.

This keeps the current WebRTC P2P media path and WebSocket signaling path intact.
It does not require an SFU or a platform migration before the existing clone is
validated across NAT.

## Selection Rationale

1. It matches the repository's current deployment assets:
   `compose.production.example.yaml`, `deploy/Caddyfile.example`, and the safe
   readiness script already target a single-host Compose topology.
2. Same-origin routing for the frontend, `/api`, and `/gateway` avoids extra CORS
   and WSS split-origin failures while preserving the existing Vite/FastAPI
   integration model.
3. Caddy can handle public HTTPS for the domain and reverse proxy both normal HTTP
   requests and WebSocket upgrades to the backend.
4. PostgreSQL and Redis can be run inside Compose for external QA, then replaced by
   managed services later without changing frontend behavior.
5. TURN can be introduced without changing the app's signaling protocol:
   `WEBRTC_ICE_SERVERS_JSON` is already the boundary for STUN/TURN configuration.
6. The path is easier to debug than a split PaaS deployment because logs,
   containers, network rules, and restart behavior are controlled from one host.
7. It does not disturb the currently working same-PC and same-Wi-Fi HTTPS LAN
   flows.

## Required Preparation

### User-Prepared Items

- A VM/VPS or cloud VM account.
- A domain or temporary DNS hostname with an `A` record pointing to the VM public
  IP.
- VM firewall/security group access:
  - TCP `80` and `443` for Caddy/HTTPS.
  - If self-hosting coturn: UDP/TCP `3478` and the chosen UDP relay range, for
    example `49160-49200`.
- A decision between:
  - managed TURN provider credentials, or
  - self-hosted coturn with the required firewall ports.
- A non-committed place for real secrets, such as a VM-local `.env` file or host
  secret store.
- Two browser clients on different networks for the final manual TURN/NAT test.

### Codex-Actionable Items

- Adapt the example Compose/Caddy/coturn files to the chosen domain and deployment
  shape without committing real secrets.
- Add or update non-secret environment variable examples.
- Run `docker compose config` against placeholder values.
- Run the local readiness script when a deployment origin exists.
- Update documentation and QA checklists.
- After the user supplies non-secret host facts, guide exact deployment and
  verification commands.

## Required Environment Variables

These names may appear in docs and examples, but real values must not be committed:

- `APP_DOMAIN`
- `ACME_EMAIL`
- `ENVIRONMENT`
- `JWT_SECRET`
- `CORS_ORIGINS`
- `DATABASE_URL` or the Compose PostgreSQL variables
- `REDIS_URL`
- `WEBRTC_ICE_SERVERS_JSON`
- Optional self-hosted coturn variables such as realm, static auth secret, or
  user credential names

## Deployment Command Flow

Use this as the first external QA deployment sequence after the user prepares a VM
and domain:

1. Provision the VM/VPS.
2. Install Docker Engine and the Docker Compose plugin.
3. Point the domain `A` record to the VM public IP.
4. Open TCP `80` and `443`.
5. If self-hosting coturn, open UDP/TCP `3478` and the selected UDP relay range.
6. Clone the repository on the VM.
7. Copy `deploy/production.env.example` to `deploy/production.env` and fill the
   VM-local non-committed environment file with production values.
8. Confirm `CORS_ORIGINS` exactly matches `https://<domain>`.
9. Confirm `WEBRTC_ICE_SERVERS_JSON` includes at least one `turn:` or `turns:`
   entry before external voice is claimed.
10. Render the config before startup:

    ```powershell
    docker compose --env-file deploy/production.env -f compose.production.example.yaml config
    ```

11. Start the stack:

    ```powershell
    docker compose --env-file deploy/production.env -f compose.production.example.yaml up -d --build
    ```

12. If self-hosting coturn after firewall/DNS are ready, start the profile:

    ```powershell
    docker compose --env-file deploy/production.env -f compose.production.example.yaml --profile turn up -d --build
    ```

13. Run the safe readiness check from an operator machine:

    ```powershell
    $env:DEPLOYMENT_ORIGIN = "https://<domain>"
    $env:REQUIRE_TURN = "1"
    npm run check:deployment:readiness
    ```

13. Run the manual QA checklist from two different networks.

## Verification Checklist

Automated checks after deployment:

- `GET https://<domain>/api/health` returns healthy status.
- `GET https://<domain>/api/meta/voice/readiness` reports:
  - `stun_configured: true`
  - `turn_configured: true`
- `/gateway` upgrades over WSS and returns a gateway `HELLO`.
- `npm run check:deployment:readiness` passes with `REQUIRE_TURN=1`.

Manual external QA after automated readiness:

- Log in as two different accounts from two different networks.
- Send server text messages both directions.
- Send DM messages both directions.
- Send and accept a server invite.
- Join the same voice channel.
- Verify both users see the same participant list.
- Verify audio both directions.
- Verify mute and deafen remain independent.
- Start and stop screen sharing.
- Verify screen-share stop clears the remote screen tile.
- Refresh one browser during a voice session and confirm the app-owned rejoin
  behavior.

## Pending / Not Verified

The following items are intentionally not complete in this decision step:

- No VM/VPS has been provisioned for this step.
- No public domain or temporary DNS hostname has been connected.
- No real TURN credential has been configured.
- No external different-network WebRTC call has been completed.
- No TURN/NAT internet voice or screen-share success is claimed.

The next stage may begin once the user provides a VM/VPS target, domain or
temporary DNS name, and the preferred TURN option.
