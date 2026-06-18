# Structure Map

This folder contains fast-navigation documents for project structure and code
ownership. Use it to reduce broad file exploration before implementation.

## Files

- `../project-file-map.md`
  - Main quick path map.
  - Lists important folders/files, common task routing, and efficient lookup
    commands.
- `reference-map.md`
  - Core reference and reverse-reference map.
  - Shows which important files call, import, render, or are consumed by other
    files.

## Required Use

Before broad code exploration:

1. Read the required startup documents.
2. Read `../project-file-map.md`.
3. For cross-file changes, read `reference-map.md`.
4. Search only the likely owner folders first.
5. Expand search only when the owner files do not explain the behavior.

## Update Rule

Update this folder when:

- A folder or important file is added, removed, or renamed.
- A file's main responsibility changes.
- A new cross-file dependency becomes important for future work.
- A refactor moves behavior between frontend stores, components, composables,
  backend routes, services, repositories, gateway modules, or realtime modules.

Keep entries factual and concise. Prefer concrete paths over broad summaries.
