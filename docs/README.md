# Documentation Index

This index points future development work to the right project documents. Start with
the project prompt and context files before changing code.

## Required Startup Reading

1. `DEVELOPMENT_PROMPT.md`
   - Project-specific AI development prompt.
   - Defines role, implementation policy, verification policy, documentation policy,
     security policy, and response policy.
2. `AGENTS.md`
   - Concise repository rules for coding agents.
   - Mirrors the key backend, frontend, context recovery, and Git rules.
3. `PROJECT_CONTEXT.md`
   - Current implementation map.
   - File ownership, integration flows, commands, constraints, completed work, and
     next work.
4. `docs/implementation-plan.md`
   - Stage roadmap and current stage status.
5. `README.md`
   - Local setup, Docker setup, environment notes, and verification commands.

## Task-Specific Documents

- `docs/GITHUB_COLLABORATION_WORKFLOW.md`
  - Branch, commit, push, staging, verification, and final-report workflow for the
    current single-user `main` flow.
- `docs/PROMPT_COMPLIANCE.md`
  - Maps `DEVELOPMENT_PROMPT.md` policies to concrete files and documents.
  - Use it when auditing whether the project structure still reflects the prompt.
- `docs/store-clone-implementation-plan.md`
  - Detailed staged plan for implementing a Discord Store-like in-app shop with
    original demo cosmetics, browse/search/filter, item detail preview, demo purchase,
    inventory, apply, gifting, and persistence.
- `docs/discord-app-clone-implementation-plan.md`
  - Current primary staged plan for cloning the core Discord web app rooted at
    `https://discord.com/channels/@me`, including Friends/DM home, server rail,
    server/channel workspace, DM messaging, settings, voice UX, and responsive QA.
- `docs/discord-ui-remediation-plan.md`
  - Current controlling Stage 8 plan for fixing Discord UI polish, layout overlap,
    i18n, voice/status visibility, placeholder-button behavior, and final QA.
- `docs/deployment.md`
  - Production runtime shape, environment variables, HTTPS/WebSocket notes, Redis,
    WebRTC TURN guidance, health checks, and deployment verification.
- `docs/voice-qa.md`
  - Local two-browser voice smoke test, TURN/NAT test, deployment voice checklist,
    and WebRTC quality signal interpretation.
- `docs/stage-7-11-responsive-qa.md`
  - Desktop/mobile responsive QA notes and screenshot artifact paths for Stage 7.11.
- `docs/stage-7-12-final-qa.md`
  - Final Stage 7.12 command, Docker, and browser smoke verification notes.
- `docs/stage-8-12-feature-scope.md`
  - Stage 8.12 classification for low-frequency, deferred, or local-template
    feature surfaces such as Nitro, Shop, Quests, gifts, upload, notifications,
    external apps, and GIF search.

## Update Rules

- Update `PROJECT_CONTEXT.md` whenever implementation maps, integrations, commands,
  constraints, completed work, or next work change.
- Update `docs/implementation-plan.md` when stage status or roadmap scope changes.
- Update `docs/deployment.md` when runtime, deployment, environment, Redis, Docker,
  HTTPS, WebSocket, or TURN assumptions change.
- Update `docs/voice-qa.md` when voice, screen sharing, TURN, or WebRTC quality QA
  steps change.
- Update `docs/stage-7-11-responsive-qa.md` when responsive QA viewport coverage or
  screenshot artifacts change.
- Update `docs/stage-7-12-final-qa.md` when the final Discord app smoke suite,
  Docker smoke, or residual QA notes change.
- Update `docs/stage-8-12-feature-scope.md` when low-frequency feature scope,
  composer action classification, commerce/deferred UI decisions, or related
  verification notes change.
- Update `docs/GITHUB_COLLABORATION_WORKFLOW.md` when branch, PR, commit, staging,
  push, or final-report rules change.
- Update `docs/PROMPT_COMPLIANCE.md` after broad policy, structure, documentation, or
  verification changes that affect prompt alignment.
- Update `docs/store-clone-implementation-plan.md` when Store scope, stage order,
  API contracts, data model, or QA plan changes.
- Update `docs/discord-app-clone-implementation-plan.md` when the primary Discord
  app clone scope, stage order, UI observations, API contracts, or QA plan changes.
- Update `docs/discord-ui-remediation-plan.md` when Stage 8 scope, stage status,
  Discord UI remediation priorities, or button reliability policy changes.
- Update `DEVELOPMENT_PROMPT.md` only for durable policy changes, not one-off code
  changes.

## Verification For Documentation Changes

For documentation-only changes:

```powershell
git diff --check
rg -n -i "api[_-]?key|jwt_secret\s*=|password\s*=|credential\s*=|secret\s*=|token\s*=" DEVELOPMENT_PROMPT.md AGENTS.md PROJECT_CONTEXT.md README.md docs
```

The secret-pattern search is a guardrail. It may need adjustment if future docs add
safe placeholder examples that intentionally mention environment variable names.
