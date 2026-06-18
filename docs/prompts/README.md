# Project Prompt Library

This folder contains task-specific prompts that can be loaded before specialized
work begins.

## Available Prompts

- `discord-clone-qa-test-prompt.md`
  - Use for broad and deep QA of the Discord clone.
  - Produces a defect/improvement audit for later implementation.
- `realtime-communication-implementation-prompt.md`
  - Use for realtime text, gateway, WebRTC voice, screen sharing, cross-PC access,
    and communication-stack implementation decisions.

## Usage Rule

When the user asks to use one of these prompts, read the matching prompt after the
required startup documents and before changing code or running a broad audit.

Keep prompt outputs as project documentation, and update `PROJECT_CONTEXT.md`,
`docs/README.md`, and `docs/project-file-map.md` if the prompt creates durable
plans, QA reports, or changes project workflow.

## Prompt Review Rule

When changing these prompts, review them as if they are incomplete by default.
Check that each prompt defines role coverage, startup context, scope boundaries,
evidence requirements, output format, verification, documentation updates, and
explicit residual-risk handling.
