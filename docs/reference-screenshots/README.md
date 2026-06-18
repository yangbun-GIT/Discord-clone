# Discord Visual Reference Screenshots

Use this folder for screenshots that compare the real Discord web app with the
current clone implementation.

## Folders

- `real-discord/`: screenshots from the real Discord web app.
- `clone-current/`: screenshots from the local clone at `http://localhost:5173/`.

## Naming

Prefer stable, descriptive filenames:

- `friends-100-fhd.png`
- `add-friend-100-fhd.png`
- `text-channel-100-fhd.png`
- `voice-preview-100-fhd.png`
- `voice-connected-100-fhd.png`
- `screen-share-100-fhd.png`

When adding a pair, use the same filename in both folders so future comparison is
straightforward.

## Notes

- Keep browser zoom at 100% unless a test intentionally targets another zoom level.
- Include the viewport context in the filename when it matters, such as `fhd`,
  `side-by-side`, `tablet`, or `mobile`.
- Do not add screenshots containing private tokens, private messages, or sensitive
  account details.
- Screenshot files in `real-discord/` and `clone-current/` are local-only reference
  material and are ignored by Git. Only this README and `.gitkeep` placeholders
  should be committed.
