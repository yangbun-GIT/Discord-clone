# GitHub Collaboration Workflow

This project currently works directly on `main` because the user requested completed
stages to be committed and pushed to `origin/main`. Use this workflow unless the user
asks for a feature branch or pull request flow.

## Before Work

1. Read the required startup documents:
   - `DEVELOPMENT_PROMPT.md`
   - `AGENTS.md`
   - `PROJECT_CONTEXT.md`
   - `docs/implementation-plan.md`
   - `README.md`
   - `docs/README.md`
2. Check the working tree:

   ```powershell
   git status --short --branch
   ```

3. Do not revert, delete, or overwrite unrelated user changes.
4. If unrelated changes exist, work around them and stage only task-relevant files.

## Branch Policy

- Default: continue on `main` and push completed stages to `origin/main`.
- Use a feature branch only when the user asks for one or when the task is explicitly
  PR-oriented.
- If creating a branch through Codex desktop, use the `codex/` prefix by default.

## Commit Policy

- Commit only after the task is complete enough to verify.
- Stage only files relevant to the task.
- Use short imperative commit messages, for example:
  - `Add WebRTC quality diagnostics`
  - `Align docs with development prompt`
  - `Document deployment checklist`
- Do not include generated dependency folders, build output, local caches, `.env`
  files, secrets, or private local data.

## Push Policy

- Push completed stages to `origin/main` unless the user explicitly asks not to.
- After pushing, confirm the local branch is clean and tracking the remote:

  ```powershell
  git status --short --branch
  ```

## Verification Before Commit

Select checks based on the change:

- Documentation-only:

  ```powershell
  git diff --check
  rg -n -i "api[_-]?key|jwt_secret\s*=|password\s*=|credential\s*=|secret\s*=|token\s*=" DEVELOPMENT_PROMPT.md AGENTS.md PROJECT_CONTEXT.md README.md docs
  ```

- Backend/API:

  ```powershell
  npm run test:backend
  npm run lint:backend
  ```

- Frontend:

  ```powershell
  npm run lint:frontend
  npm --prefix frontend run build
  ```

- Cross-stack:

  ```powershell
  npm run test:backend
  npm run lint:backend
  npm run lint:frontend
  npm --prefix frontend run build
  ```

When Docker, deployed infrastructure, real TURN, or multi-network browser testing is
required but unavailable, report it as unverified instead of treating it as complete.

## Final Report

Final responses should include:

- What changed.
- What was verified.
- What was not verified.
- Documentation updated.
- Commit hash and push status.
- Recommended next intelligence level: `중간` for routine implementation, local QA,
  and docs; `높음` for architecture changes, WebRTC quality tuning, deployment
  incidents, security-sensitive changes, or broad cross-stack refactors.
