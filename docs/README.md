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
  - Lists SRP, OCP, DIP, encapsulation, DRY, and testability gaps plus the
    previous Stage 10/11 process that should govern future refactor stages.
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
- `docs/project-file-map.md`
  - Quick project folder/file ownership map for faster path lookup before
    implementation.
  - Lists root files, backend/frontend ownership, tests, common task routing, and
    efficient lookup commands.
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
- Update `docs/voice-qa.md` when voice, screen sharing, TURN, or WebRTC quality QA
  steps change.
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
