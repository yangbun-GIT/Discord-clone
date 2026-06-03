# Stage 8.12 Feature Scope Decisions

Stage 8.12 removes misleading low-frequency controls from the active Discord clone
surface while keeping useful local interactions available.

## Classification

| Feature | Decision | Current Surface |
| --- | --- | --- |
| Emoji insertion | Keep | Server and DM composers insert local emoji into drafts. |
| Poll/to-do actions | Keep as local templates | Server composer uses `Local templates` instead of external apps. |
| Channel notification mode | Keep as local state | Header notification panel stores the current session filter only. |
| File upload | Defer real transfer | Server composer previews local file metadata only. |
| Nitro | Hide from active navigation | Covered by `Clone scope` in the private sidebar and Settings. |
| Shop/Store commerce | Hide from active navigation | Store backend contracts remain deferred; no checkout UI is exposed. |
| Quests | Hide from active navigation | Covered by `Clone scope`; no game-platform integration. |
| Gifts | Hide from composer | Gift checkout is commerce scope and is not shown as a dead action. |
| Activities/external app launcher | Replace | Composer offers local templates, not external app launch. |
| Full GIF search | Defer | Emoji insertion remains; no fake GIF search panel is exposed. |
| Production notifications | Defer | Notification UI is clearly a local channel filter. |

## Implementation Map

- `frontend/src/components/PrivateChannelSidebar.vue`
  - Replaces separate Nitro, Shop, and Quests buttons with one `Clone scope` entry.
- `frontend/src/components/ChatView.vue`
  - Removes the visible gift action.
  - Renames external-app style actions to `Local templates`.
  - Keeps upload metadata preview, local templates, emoji insertion, and send.
- `frontend/src/components/SettingsView.vue`
  - Adds a `Clone scope decisions` card in the account panel.
- `frontend/src/i18n/index.ts`
  - Adds Korean/English labels for scope and local-template copy.
- `frontend/src/styles/base.css`
  - Adds bounded styles for the sidebar scope row and Settings scope list.

## Verification Notes

- Run frontend lint and production build after changes.
- Browser smoke should confirm:
  - the private sidebar no longer exposes separate Nitro, Shop, or Quests buttons;
  - the composer no longer exposes a gift button;
  - local template insertion still writes to the message draft;
  - upload metadata preview and emoji insertion still work;
  - Settings shows the scope decision card without text overlap.
