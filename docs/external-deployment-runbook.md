# External Deployment Runbook

Date: 2026-06-20

Status: future always-on public deployment option. This runbook is retained for a
later VM/VPS deployment and is not the default assignment submission path. The
default submission/demo flow is local Docker Compose plus optional Cloudflare
Tunnel, documented in `docs/assignment-submission-guide.md`.

This runbook is the execution guide for the first public HTTPS/WSS deployment of
the Discord clone. It assumes the selected topology from
`docs/external-deployment-decision.md`: one VM running Docker Compose, Caddy,
frontend, backend, PostgreSQL, Redis, and TURN through environment configuration.

This document does not claim external TURN/NAT voice success. That gate remains
pending until a real public host, real TURN configuration, and two different
networks pass manual QA.

## Required User Inputs

The following values must be prepared outside Git before deployment:

- VM/VPS public IP.
- Domain or temporary DNS hostname pointing to the VM.
- Email address for ACME certificate notices.
- Real `JWT_SECRET`.
- Real PostgreSQL password if using the Compose PostgreSQL service.
- Real TURN provider values, or self-hosted coturn secret and firewall plan.
- Firewall/security-group access for TCP `80` and `443`.
- If self-hosting TURN: UDP/TCP `3478` plus the selected UDP relay range.

Do not paste actual secrets into project documents, screenshots, logs, commits, or
chat messages.

## Deployment Files

Committed placeholders:

- `compose.production.example.yaml`
- `deploy/Caddyfile.example`
- `deploy/coturn/turnserver.conf.example`
- `deploy/production.env.example`
- `scripts/deployment_readiness_check.mjs`

Host-only files:

- `deploy/production.env`
- Any real coturn config containing `static-auth-secret` or long-term credentials.
- Any certificate private key if a custom certificate flow is used.

The repository `.gitignore` ignores `deploy/*.env` and keeps only
`deploy/*.env.example` trackable.

## VM Preparation

Run on the VM:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
```

Log out and back in after adding the user to the Docker group.

Clone the repository:

```bash
git clone https://github.com/yangbun-GIT/Discord-clone.git
cd Discord-clone
```

Create the host-only environment file:

```bash
cp deploy/production.env.example deploy/production.env
chmod 600 deploy/production.env
```

Edit `deploy/production.env` on the VM. Replace placeholders with real host values.
Keep `CORS_ORIGINS` exactly aligned with `https://<domain>`.

## Preflight Checks

Render the Compose config without starting services:

```bash
docker compose --env-file deploy/production.env -f compose.production.example.yaml config
```

Check the values before startup:

- `APP_DOMAIN` matches the browser URL.
- DNS `A` record points to the VM public IP.
- VM firewall allows TCP `80` and `443`.
- `WEBRTC_ICE_SERVERS_JSON` includes a real `turn:` or `turns:` entry before
  claiming external voice.
- Real secret values are stored only in `deploy/production.env` or the host secret
  store.

## Start The Stack

Application stack:

```bash
docker compose --env-file deploy/production.env -f compose.production.example.yaml up -d --build
```

If using self-hosted coturn after firewall ports are ready:

```bash
docker compose --env-file deploy/production.env -f compose.production.example.yaml --profile turn up -d --build
```

Inspect service status:

```bash
docker compose --env-file deploy/production.env -f compose.production.example.yaml ps
docker compose --env-file deploy/production.env -f compose.production.example.yaml logs --tail=100 caddy backend
```

Do not paste logs containing secrets into documentation or commits. Redact host-only
values if logs are shared for debugging.

## Automated Verification

Run from the operator machine after DNS and HTTPS are active:

```powershell
$env:DEPLOYMENT_ORIGIN = "https://<domain>"
$env:REQUIRE_TURN = "1"
npm run check:deployment:readiness
```

Pass criteria:

- `secure_origin` is `true`.
- `/api/health` returns a healthy service.
- `/api/meta/voice/readiness.turn_configured` is `true`.
- `/gateway` sends `HELLO` over WSS.

If using a local self-signed deployment only, `DEPLOYMENT_IGNORE_TLS_ERRORS=1` is
allowed for localhost checks. It is not allowed for public deployment QA.

## Manual External QA

Run only after automated verification passes:

1. Open `https://<domain>` from two different networks, such as home Wi-Fi and
   mobile hotspot.
2. Log in with two different accounts.
3. Send server text messages both directions.
4. Send DM messages both directions.
5. Send or use a server invite and confirm join routing.
6. Join the same voice channel.
7. Confirm both users see the same participant list.
8. Confirm audio works both directions.
9. Toggle mute and deafen independently.
10. Start screen sharing from one user and verify the receiver sees the screen.
11. Stop screen sharing and verify the remote tile clears.
12. Refresh one voice-connected browser and confirm app-owned rejoin recovery.

The external release gate is not complete if any of these fail, if
`turn_configured` is false, or if both clients are still on the same network.

## Rollback

Stop the stack:

```bash
docker compose --env-file deploy/production.env -f compose.production.example.yaml down
```

Preserve PostgreSQL data unless a reset is explicitly intended. To remove volumes:

```bash
docker compose --env-file deploy/production.env -f compose.production.example.yaml down -v
```

## Current Execution Status

As of 2026-06-20:

- Local and same-Wi-Fi LAN communication have been validated separately.
- Production config rendering can be checked locally with the placeholder example.
- No VM/VPS target, public DNS hostname, or real TURN credential is available in
  this workspace.
- Public external deployment and two-network TURN/NAT media QA remain pending.
