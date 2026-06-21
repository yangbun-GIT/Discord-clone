# Documentation Index

This folder keeps only documentation that is useful for understanding, running,
verifying, or presenting the submitted Discord clone project.

Local planning notes, remediation task files, stage logs, prompts, screenshots,
videos, and generated QA artifacts are intentionally excluded from Git. They can
exist in the working tree for development, but they are not part of the GitHub
submission.

## Submitted Documents

- `docs/project-file-map.md`
  - Quick map of important project files and their responsibilities.
- `docs/structure-map/reference-map.md`
  - High-value dependency and reference map for core frontend/backend files.
- `docs/assignment-submission-guide.md`
  - Korean assignment/demo guide for local Docker Compose execution and optional
    Cloudflare Tunnel demonstration.
- `docs/deployment.md`
  - Runtime, Docker, HTTPS/WSS, Cloudflare Tunnel, and deployment notes.
- `docs/external-deployment-decision.md`
  - Future always-on deployment decision record.
- `docs/external-deployment-runbook.md`
  - Future always-on deployment runbook.
- `docs/voice-qa.md`
  - Voice, screen-share, LAN, and TURN-related QA guide.
- `docs/realtime-communication-qa.md`
  - Realtime text, DM, gateway, and WebSocket QA guide.
- `docs/voice-transport-architecture.md`
  - Current P2P voice transport boundary and future SFU migration notes.
- `docs/GITHUB_COLLABORATION_WORKFLOW.md`
  - Local development Git workflow used by Codex during the project.

## Local-Only Documentation

The following categories are ignored by Git because they are development-process
artifacts rather than submitted project information:

- `docs/remediation-tasks/`
- `docs/prompts/`
- `docs/qa-artifacts/`
- `docs/reference-screenshots/`
- `docs/reference-videos/`
- `docs/stage-*.md`
- `docs/*-plan.md`
- `docs/*remediation*.md`
- `docs/*baseline*.md`
- `docs/*final-qa.md`
- architecture audit/refactor planning files

## Update Rules

- Update `PROJECT_CONTEXT.md` when implementation status, operating assumptions,
  verification status, or submission notes change.
- Update `docs/project-file-map.md` when important source-file or folder
  responsibilities change.
- Update `docs/structure-map/reference-map.md` when core dependencies or
  cross-file references change.
- Update `docs/assignment-submission-guide.md` and `README.md` when the grading
  or local demo flow changes.
- Keep local-only work notes out of Git unless they become durable project
  documentation needed by someone running or reviewing the submitted project.
