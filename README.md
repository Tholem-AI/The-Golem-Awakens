# The Golem Awakens

A single-file HTML5 platformer with puzzle elements. An Egyptian-inspired golem collects knowledge glyphs through chambers, unlocking new abilities with each one.

## Play

Open `golem.html` in a browser. No build step required.

## Controls

| Action | Keys |
|--------|------|
| Move | Arrow keys / WASD |
| Jump | Arrow Up / W / Space |
| Dash (charge) | Shift (hold to charge, release to fire) |
| Test chamber | T |

## Abilities

Each chamber grants a glyph that unlocks the next chamber's core mechanic:

| Glyph | Ability | Chamber |
|-------|---------|---------|
| 1 | Double Jump | Awakening |
| 2 | Dash | The Library |
| 3 | Push Blocks | The Hall of Echoes |
| 4 | Break Cracked | The Weight of Wisdom |

## Chambers

1. **Awakening** — Tutorial. Learn movement, collect Glyph 1.
2. **The Library** — Platforming with double jump. Collect Glyph 2.
3. **The Hall of Echoes** — Dash through magical walls. Collect Glyph 3.
4. **The Weight of Wisdom** — Push block puzzle. Collect Glyph 4.
5. **The Ibis Chamber** — Break cracked walls to reach the final portal.

## Structure

| File | Purpose |
|------|---------|
| `golem.html` | Complete game (~1153 lines, single file, 11-section structure) |
| `chamber-data.md` | Chamber layouts (ASCII grids) |
| `chamber-proposal.md` | Proposed chamber improvements |
| `chamber-template.md` | Tile legend and conversion spec |
| `code-review.md` | Code review findings |
| `golem-state-audit.md` | Full game architecture audit |
| `ROADMAP.md` | Active development checkpoints |
| `docs/Project-Constraints.md` | Stack and constraints |
| `docs/File-Structure-Reference.md` | Repository structure |

## Tech

Vanilla JavaScript, HTML5 Canvas 2D, no frameworks, no dependencies. 800x480 canvas with 32x32 tiles on a 25x15 grid per chamber.
