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
6. `docs/project-file-map.md`
   - Quick path map for likely owner files and common task routing.
7. `docs/structure-map/reference-map.md`
   - Cross-file dependency and reverse-reference map for important files.

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
- `docs/discord-visual-parity-remediation-plan.md`
  - Current controlling Stage 9 plan from the user's real Discord versus clone
    screenshots.
  - Lists visual/design/functionality/usability gaps, staged remediation order,
    verification expectations, and user-provided measurement requests.
- `docs/stage-9-final-qa.md`
  - Stage 9 final command verification, browser QA coverage, completed visual parity
    changes, and residual notes.
- `docs/discord-interaction-polish-plan.md`
  - Current controlling Stage 10 plan for Discord-like interaction polish after the
    latest real Discord versus clone comparison.
  - Lists remaining visual-noise, spacing, bottom-panel, message/composer, voice,
    screen-share, data-cleanup, and feature-visibility work.
- `docs/discord-stage-11-completion-plan.md`
  - Current controlling Stage 11 plan for the completion pass after Stage 10.29.
  - Preserves the Stage 10 process: one stage at a time, verification before moving
    forward, documentation updates, Korean commit title, and push to `origin/main`.
- `docs/architecture-principles-audit.md`
  - Current implementation-principle and design-pattern audit.
  - Lists current SRP, OCP, DIP, encapsulation, DRY, and testability status,
    completed Stage 12/13 refactor boundaries, and deferred feature-driven
    candidates.
- `docs/architecture-refactor-stage-12-plan.md`
  - Current controlling Stage 12 plan for turning the architecture-principles audit
    into behavior-preserving refactor stages.
  - Covers App voice orchestration, voice RTC module boundaries, guild voice
    presence, DM storage provider, guild repository query movement, API exception
    mapping, realtime fan-out DRY cleanup, browser API adapters, and CSS/i18n
    split planning.
- `docs/stage-12-architecture-qa.md`
  - Running Stage 12 QA log.
  - Records command checks, review notes, changed files, and residual risks for
    each architecture refactor sub-stage.
- `docs/frontend-css-i18n-ownership.md`
  - Stage 12.9 ownership plan for future `base.css` and i18n module splits.
  - Defines safe extraction order, verification rules, and deferred risks.
- `docs/architecture-refactor-stage-13-plan.md`
  - Final architecture-maintenance plan before feature implementation resumes.
  - Covers DM store boundary splitting, guild/DM visibility policies, frontend
    unit tests, backend DM seed extraction, storage protocol review, and the final
    CSS/i18n boundary decision.
- `docs/prompts/`
  - Task-specific prompt library for future specialized work.
  - `discord-clone-qa-test-prompt.md` is the QA audit prompt for broad/deep clone
    testing and defect documentation.
  - `realtime-communication-implementation-prompt.md` is the communication-stack
    prompt for realtime text, WebSocket gateway, WebRTC voice, screen sharing,
    cross-PC access, and technology selection.
- `docs/remediation-tasks/realtime-communication-plan.md`
  - Current staged development plan for production-like realtime messaging,
    WebSocket gateway hardening, WebRTC voice/screen sharing, LAN/TURN access,
    security, observability, and communication QA.
- `docs/remediation-tasks/friend-relationship-implementation-plan.md`
  - Development plan for turning the current UI-only Add Friend form into real
    friend request, accept/reject/cancel, remove, block/unblock, realtime
    relationship updates, and browser QA workflows.
- `docs/remediation-tasks/friends-home-remediation-2026-06-20.md`
  - Friends home usability remediation plan and completion log.
  - Owns the first-screen Friends pass for tab/search visibility, actionable-only
    friend menus, Add Friend feedback, blocked-user access, activity-panel clarity,
    responsive row actions, and README Korean quick-start repair.
  - Also owns the remaining Friends/private-home feature-completion backlog for
    friend profile popout, friend/DM call entry, conversation mute, start-new-DM
    recipient picker, target-aware friend/DM context menus, incoming friend request
    feedback, bottom-anchored message timelines, and DM header/profile-side actions.
- `docs/remediation-tasks/friends-dm-usability-implementation-reference.md`
  - English Codex-facing implementation reference for the next Friends/DM usability
    pass.
  - Use it when implementing the remaining private-home feature-completion stages.
- `docs/remediation-tasks/friends-dm-usability-checklist-ko.md`
  - Korean user-facing checklist for the same Friends/DM usability backlog.
  - Use it to confirm which missing features are in scope and why.
- `docs/remediation-tasks/server-rail-remediation-2026-06-21.md`
  - Server rail usability remediation plan and completion log.
  - Owns per-user server ordering, server folders/groups, folder collapse/expand,
    and app-owned rail hover/focus tooltips.
- `docs/remediation-tasks/server-settings-chat-remediation-2026-06-21.md`
  - Server workspace remediation record.
  - Owns server heading invite/menu behavior, functional server settings,
    leave/delete server flows, and bottom-anchored server text message timestamp
    and author-separation behavior.
- `docs/remediation-tasks/voice-channel-visual-remediation-2026-06-21.md`
  - Voice channel visual remediation record.
  - Owns the Discord-like voice workspace stage, large participant/empty tiles,
    bottom-center voice action controls, and empty voice-room next-action clarity.
- `docs/remediation-tasks/action-error-remediation-2026-06-21.md`
  - Action error remediation record.
  - Owns sanitized API fallback copy, duplicate voice media error prevention, and
    recoverable WebRTC signaling race suppression.
- `docs/remediation-tasks/manual-qa-followup-2026-06-19.md`
  - Latest user-run manual QA follow-up plan.
  - Owns sustained speech dropout, screen-share participant composition, refresh
    rejoin, LAN secure-context, TURN readiness, Friends pending/presence, DM
    identity, invite delivery/copy state, deafen behavior, and invite permission
    browser QA follow-up stages.
- `docs/remediation-tasks/manual-qa-followup-2026-06-19-ko.md`
  - Korean summary of the completed manual QA follow-up fixes.
  - Lists M1-M10 changes, verification results, unresolved manual gates, and
    related commits for quick handoff.
- `docs/realtime-communication-qa.md`
  - Stage C8 and later communication QA checklist.
  - Documents the automated two-browser smoke, same-PC manual QA, LAN QA, TURN/NAT
    QA, privacy constraints, and the latest C8 automated result.
- `docs/assignment-submission-guide.md`
  - Default assignment submission and demo guide.
  - Defines local Docker Compose as the primary grading path, same-Wi-Fi HTTPS LAN
    testing as the local two-PC path, optional Cloudflare Tunnel as temporary
    external access, and VM/VPS deployment as a future extension.
  - References `npm run check:submission:local` for local grading-readiness
    verification.
- `docs/project-file-map.md`
  - Quick project folder/file ownership map for faster path lookup before
    implementation.
  - Lists root files, backend/frontend ownership, tests, common task routing, and
    efficient lookup commands.
- `docs/remediation-tasks/`
  - QA-driven defect and remediation backlogs.
  - Use the latest development plan in this folder before starting UI, workflow,
    Discord-parity, or communication fix stages.
  - `discord-clone-qa-remediation-2026-06-19.md` is promoted from QA audit to
    development plan and includes per-finding implementation directives,
    acceptance criteria, regression checks, staged remediation order, and a
    follow-up QA recheck for settings polish, hidden-control accessibility, header
    ownership, and voice participant duplication.
  - `friend-relationship-implementation-plan.md` owns the future Friends/Add
    Friend backend, frontend, realtime, and QA implementation stages.
- `docs/structure-map/`
  - Fast-navigation structure folder.
  - `README.md` defines usage and update rules; `reference-map.md` records core
    file references and reverse references.
- `docs/stage-11-baseline.md`
  - Stage 11.0 baseline and scope lock.
  - Records completed Stage 10.29 behavior, remaining risk areas, stage
    classification, and Stage 11 verification expectations.
- `docs/stage-11-final-qa.md`
  - Running Stage 11 QA log.
  - Records command checks, browser checks, fixes, and residual risks for each
    Stage 11 implementation stage before commit.
- `docs/stage-10-baseline.md`
  - Stage 10.0 baseline lock for the latest FHD 100% real Discord versus clone
    comparison screenshots and problem inventory.
- `docs/stage-10-17-responsive-qa.md`
  - Stage 10.17 FHD, side-by-side, tablet, and mobile responsive screenshots,
    layout measurements, accessibility-label checks, and keyboard QA limitation.
- `docs/stage-10-final-qa.md`
  - Stage 10.18 final frontend/backend command verification, Docker/API smoke,
    browser workflow QA, and residual media-permission notes.
- `docs/reference-screenshots/`
  - Real Discord and current clone screenshot folders for future visual parity
    review and implementation reference.
- `docs/reference-videos/`
  - Local ignored call/video QA reference folders.
  - Keep only `.gitkeep` tracked; do not commit real recordings or generated
    analysis frames.
- `docs/deployment.md`
  - Production runtime shape, environment variables, HTTPS/WebSocket notes, Redis,
    WebRTC TURN guidance, health checks, and deployment verification.
  - Current external-readiness reference files are
    `compose.production.example.yaml`, `deploy/Caddyfile.example`,
    `deploy/coturn/turnserver.conf.example`, and
    `scripts/deployment_readiness_check.mjs`.
- `docs/external-deployment-decision.md`
  - Current decision record for the first external-network QA deployment.
  - Compares local port forwarding, VM/IaaS, PaaS, static frontend plus separate
    backend, and single VM Docker Compose.
  - Selects single VM Docker Compose with Caddy and TURN configuration while
    keeping external TURN/NAT voice marked pending until real infrastructure and
    two-network QA are available.
- `docs/external-deployment-runbook.md`
  - Step-by-step execution guide for the selected single-VM deployment.
  - Defines VM preparation, host-only env handling, Compose startup, readiness
    checks, rollback, and the manual two-network external QA gate.
- `docs/voice-transport-architecture.md`
  - Voice transport boundary and future SFU migration plan.
  - Documents the current P2P WebRTC transport, the shared `VoiceTransport`
    contract, future LiveKit/mediasoup requirements, and screen-share quality
    decision criteria.
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
- `docs/stage-8-responsive-accessibility-qa.md`
  - Stage 8.13 desktop/mobile overflow, screenshot, focus-order, accessibility-label,
    and residual manual QA notes for the UI remediation stage.
- `docs/stage-8-final-qa.md`
  - Stage 8.14 final command verification, Docker smoke notes, browser QA artifact
    index, and residual post-Stage 8 gaps.

## Update Rules

- Update `PROJECT_CONTEXT.md` whenever implementation maps, integrations, commands,
  constraints, completed work, or next work change.
- Update `docs/implementation-plan.md` when stage status or roadmap scope changes.
- Update `docs/deployment.md` when runtime, deployment, environment, Redis, Docker,
  HTTPS, WebSocket, or TURN assumptions change.
- Update `docs/assignment-submission-guide.md` when the assignment submission
  path, local Docker startup, same-Wi-Fi LAN check, Cloudflare Tunnel demo flow,
  feature verification order, or grading limitations change.
- Update `docs/external-deployment-decision.md` when the external deployment
  provider, topology, TURN strategy, readiness command flow, or pending external
  gate changes.
- Update `docs/external-deployment-runbook.md` when the selected deployment command
  flow, VM preparation, host-only environment handling, verification checklist, or
  rollback procedure changes.
- Update `docs/voice-transport-architecture.md` when the voice transport boundary,
  P2P transport contract, SFU migration plan, media-token requirements, or
  screen-share quality decision criteria change.
- Update `docs/voice-qa.md` when voice, screen sharing, TURN, or WebRTC quality QA
  steps change.
- Update `docs/realtime-communication-qa.md` when automated communication smoke,
  same-PC manual QA, LAN QA, TURN/NAT QA, or communication privacy rules change.
- Update `docs/stage-7-11-responsive-qa.md` when responsive QA viewport coverage or
  screenshot artifacts change.
- Update `docs/stage-7-12-final-qa.md` when the final Discord app smoke suite,
  Docker smoke, or residual QA notes change.
- Update `docs/stage-8-12-feature-scope.md` when low-frequency feature scope,
  composer action classification, commerce/deferred UI decisions, or related
  verification notes change.
- Update `docs/stage-8-responsive-accessibility-qa.md` when Stage 8 responsive
  breakpoints, focus order, accessibility labeling, screenshot artifacts, or residual
  QA notes change.
- Update `docs/stage-8-final-qa.md` when final Stage 8 verification commands,
  Docker smoke behavior, artifact inventory, or post-Stage 8 residual gaps change.
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
- Update `docs/discord-visual-parity-remediation-plan.md` when Stage 9 screenshot
  observations, visual parity priorities, measurement targets, staged remediation
  steps, requested user reference data, or final QA notes change.
- Update `docs/stage-9-final-qa.md` when final Stage 9 verification commands,
  browser QA coverage, or residual visual parity notes change.
- Update `docs/discord-interaction-polish-plan.md` when Stage 10 interaction polish
  scope, reference observations, stage order, feature visibility decisions, or QA
  rules change.
- Update `docs/discord-stage-11-completion-plan.md` when Stage 11 scope, stage
  status, stage order, verification expectations, or final completion priorities
  change.
- Update `docs/architecture-principles-audit.md` when broad architecture
  boundaries, principle gaps, refactor stage order, or design-pattern decisions
  change.
- Update `docs/architecture-refactor-stage-12-plan.md` when Stage 12 scope, stage
  status, verification expectations, or active refactor order changes.
- Update `docs/stage-12-architecture-qa.md` after each Stage 12 implementation
  stage with command checks, review notes, and residual risks.
- Update `docs/frontend-css-i18n-ownership.md` when frontend style or translation
  ownership changes, especially if `base.css` or `i18n/index.ts` is split.
- Update `docs/architecture-refactor-stage-13-plan.md` if the final
  maintenance-pass scope or completion status is corrected after regression.
- Update `docs/prompts/` when task-specific prompt behavior, required roles,
  output format, or source/verification expectations change.
- Update `docs/project-file-map.md` when a project folder or important source file
  is added, removed, renamed, or assigned a meaningfully different responsibility.
- Update `docs/structure-map/README.md` and
  `docs/structure-map/reference-map.md` when the structure-map usage rules or core
  cross-file dependencies change.
- Update `docs/stage-11-baseline.md` when Stage 11 baseline assumptions, stage
  classification, or initial risk areas change.
- Update `docs/stage-11-final-qa.md` after each Stage 11 implementation stage with
  command checks, browser checks, fixes, and residual risks.
- Update `docs/stage-10-baseline.md` only when the Stage 10 baseline comparison set
  changes before implementation continues.
- Update `docs/stage-10-17-responsive-qa.md` when Stage 10 responsive viewport
  coverage, screenshot artifacts, focus order, accessibility labels, or residual QA
  notes change.
- Update `docs/stage-10-final-qa.md` when final Stage 10 command verification,
  Docker/API smoke, browser workflow coverage, or residual media-permission notes
  change.
- Update `docs/reference-screenshots/README.md` when screenshot folder structure,
  naming rules, or visual-reference handling changes.
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
