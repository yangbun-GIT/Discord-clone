# Remediation Task Documents

This folder stores QA-driven defect and remediation backlogs that are meant to be
used before implementation stages. Some QA reports are promoted into development
plans when each finding has implementation directives, owner files, acceptance
criteria, and regression checks.

## Usage

- Read the latest remediation document before starting a UI or workflow fix.
- Keep each finding tied to a reproducible surface, expected behavior, likely owner
  files, and regression checks.
- When a QA report is promoted to a development plan, execute one remediation stage
  at a time and update the same document with fixed/residual status before moving
  on.
- Update the relevant remediation document when a newly discovered issue changes
  scope or priority.
- Do not store real Discord screenshots or private account data here.

## Current Development Plans

- `discord-clone-qa-remediation-2026-06-19.md`
  - QA-derived UI/workflow remediation development plan.
  - Use for message timeline cleanup, voice state clarity, shell layering,
    visible-control policy, Friends/DM structure, bottom-card consistency, empty
    states, context menus, voice workspace density, settings surface polish, and
    final responsive/realtime QA.
- `realtime-communication-plan.md`
  - Communication implementation plan for WebSocket, realtime text/DM, WebRTC
    voice/screen sharing, LAN/TURN readiness, and communication QA.
