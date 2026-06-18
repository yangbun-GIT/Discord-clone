# Stage 10.0 Baseline Lock

This document freezes the Stage 10 baseline before implementation changes.

## Reference Context

- User comparison screenshots were captured at FHD Chrome 100% zoom.
- Left side in the screenshots is real Discord; right side is the current clone.
- Use the screenshots for layout, density, interaction structure, and hierarchy only.
- Do not copy private server names, messages, avatars, or user content into code,
  fixtures, or documentation.

## Captured Surfaces

The user-provided screenshots cover these primary surfaces:

- Friends home and Add Friend view.
- Server text channel with message timeline, file cards, reactions, composer, and
  member list.
- Voice channel preview and connected voice state.
- Screen-share state after joining voice.

## Baseline Problems

### Global Shell

- The clone still feels more like a demo dashboard than a continuous chat app.
- Several panels use heavy boxes and borders where real Discord uses quieter surface
  separation.
- The bottom controls occupy too much visual weight and compete with main content.
- Some development or test data appears in primary screens and distorts visual QA.

### Data And Copy

- Test-like guild names, channel names, generated IDs, and template messages are too
  visible.
- Friend and DM demo copy is useful for development but too explicit for a polished
  clone.
- Voice diagnostics such as STUN/TURN readiness are visible in the primary footer.

### Text Channel

- Message column density is inconsistent with Discord's grouped timeline.
- Attachment cards and reaction pills look too much like generic dashboard cards.
- Composer actions are visible enough to feel cluttered even when not high-frequency.
- Text and button boundaries need more consistent padding.

### Navigation

- Server rail, DM sidebar, and channel sidebar are functional but still too noisy.
- Channel management affordances should appear mainly on hover/focus or when editing.
- Active channel and connected voice state are visible, but the state presentation is
  still verbose.

### Voice And Screen Share

- Voice workspace tiles are clear but too card-heavy.
- Speaking state should rely on rings/glow and compact row state rather than
  explanatory labels.
- Screen share should be controlled from compact voice controls and avoid diagnostic
  text in the primary surface.

## Persistent Data Classification

- Persistent user data: registered local users, user-created guilds/channels/messages,
  relationships, and DMs stored in the Docker PostgreSQL volume.
- Demo seed data: default demo guild, default channels, sample members, sample DMs,
  and seeded relationship rows.
- Test artifacts to hide from primary UI: names or content matching smoke-test,
  `QA Smoke`, `stage8-*`, long generated QA labels, and repeated template messages.

## Verification

- This stage made no application implementation changes.
- The baseline is documented here and linked from the Stage 10 plan/index.
