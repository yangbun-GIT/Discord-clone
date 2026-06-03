# Stage 8 Final QA

Stage 8.14 closes the Discord UI remediation slice covering layout polish, i18n,
state visibility, placeholder-button cleanup, voice workspace clarity, low-frequency
feature scope, and responsive/accessibility QA.

## Command Verification

Executed on 2026-06-04:

```powershell
npm run test:backend
npm run lint:backend
npm run lint:frontend
npm --prefix frontend run build
```

Results:

- Backend tests: 103 passed.
- Backend lint: passed.
- Frontend lint: 0 warnings, 0 errors.
- Frontend production build: passed.

## Docker Smoke

Docker Compose status:

- `discord-clone-postgres-1`: running, healthy.
- `discord-clone-backend-1`: running, healthy.
- `discord-clone-frontend-1`: running.

Container-internal backend health:

```json
{"status":"ok","environment":"local","database":{"configured":true,"connected":true},"redis":{"configured":false,"connected":false}}
```

Frontend host smoke:

- `http://127.0.0.1:5173/` returned HTTP 200 and the app title.

Host port note:

- `127.0.0.1:8000` returned a native/fallback health response with
  `database.configured=false`.
- `netstat` showed multiple listeners on port 8000, including Docker's
  `com.docker.backend.exe` and WSL relay. For Docker database verification, use
  container-internal health or make sure no native backend is also bound to
  loopback before relying on host `127.0.0.1:8000`.

## Browser QA Evidence

Stage-specific browser artifacts:

- Stage 8.1 desktop/mobile layout:
  - `docs/qa-artifacts/stage-8-1-desktop.png`
  - `docs/qa-artifacts/stage-8-1-mobile.png`
- Stage 8.2 sidebar/channel creation:
  - `docs/qa-artifacts/stage-8-2-sidebar.png`
- Stage 8.3 Korean/English i18n:
  - `docs/qa-artifacts/stage-8-3-ko-home.png`
  - `docs/qa-artifacts/stage-8-3-en-home.png`
  - `docs/qa-artifacts/stage-8-3-en-settings.png`
- Stage 8.4 bottom voice panel:
  - `docs/qa-artifacts/stage-8-4-voice-disconnected.png`
  - `docs/qa-artifacts/stage-8-4-voice-connected.png`
  - `docs/qa-artifacts/stage-8-4-mobile.png`
- Stage 8.5 current location and voice state:
  - `docs/qa-artifacts/stage-8-5-voice-state.png`
- Stage 8.6 placeholder-button panels:
  - `docs/qa-artifacts/stage-8-6-button-panels.png`
- Stage 8.7 channel header panels:
  - `docs/qa-artifacts/stage-8-7-header-panels.png`
- Stage 8.8 composer panels:
  - `docs/qa-artifacts/stage-8-8-composer-panels.png`
  - `docs/qa-artifacts/stage-8-8-dm-composer.png`
- Stage 8.9 Friends/DM information density:
  - `docs/qa-artifacts/stage-8-9-friends-home.png`
  - `docs/qa-artifacts/stage-8-9-friends-dm.png`
- Stage 8.10 Settings reorganization:
  - `docs/qa-artifacts/stage-8-10-settings.png`
- Stage 8.11 voice workspace:
  - `docs/qa-artifacts/stage-8-11-voice-workspace.png`
  - `docs/qa-artifacts/stage-8-11-voice-workspace-fake-media.png`
- Stage 8.12 feature-scope cleanup:
  - `docs/qa-artifacts/stage-8-12-feature-scope.png`
- Stage 8.13 responsive/accessibility QA:
  - `docs/qa-artifacts/stage-8-13-desktop.png`
  - `docs/qa-artifacts/stage-8-13-mobile.png`

## Residual Gaps

- Full screen-reader announcements were not run. Stage 8.13 verified DOM labeling and
  keyboard focus order, not spoken output.
- Full human keyboard passes through every modal should be repeated when modal or
  settings focus behavior changes.
- Real multi-browser WebRTC QA with TURN configured remains outside Stage 8's UI
  remediation scope and should use `docs/voice-qa.md`.
