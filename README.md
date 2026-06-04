# The Golem Awakens

An Egyptian-inspired golem awakens in ancient chambers, collecting knowledge glyphs inscribed with Hebrew letters. Each glyph unlocks a new ability as the golem progresses deeper — building toward a final convergence where the four glyphs spell **EMET** (אמת) — "truth."

A single-file HTML5 platformer with puzzle elements, built entirely with local AI models.

## How to Play

Open [`golem.html`](golem.html) in any modern web browser. No build step, no installation, no dependencies. Press any key on the title screen to begin.

You can also play the live version at [tholem.ai](https://tholem.ai).

## Browser Requirements

- **Any modern browser** — Chrome, Firefox, Safari, Edge
- Canvas 2D support
- Web Audio API support

No plugins, frameworks, or internet connection required once the file is loaded.

## Controls

| Action | Keys |
|--------|------|
| Move | Arrow keys / WASD |
| Jump | Arrow Up / W / Space |
| Dash (charge) | Shift (hold to charge, release to fire) |
| Drop through platforms | Arrow Down / S (while above a platform) |
| Pause | P |
| Mute | M |
| Test chamber (developer) | T |

## Abilities Progression

Each chamber grants a knowledge glyph that unlocks a new ability for the next level:

| Glyph | Hebrew | Ability | Chamber |
|-------|--------|---------|---------|
| 1 | א (Aleph) | Double Jump | Awakening |
| 2 | מ (Mem) | Dash | The Library |
| 3 | ה (He) | Push Blocks | The Hall of Echoes |
| 4 | ת (Tav) | Break Cracked | The Weight of Wisdom |

**The Ibis Chamber** is the final test — use all four abilities to break through cracked walls and reach the end portal.

## Chambers

1. **Awakening** — Tutorial. Learn basic movement and collect your first glyph.
2. **The Library** — Platforming with double jump. Navigate gaps and reach Glyph 2.
3. **The Hall of Echoes** — Dash through magical walls to solve the path ahead.
4. **The Weight of Wisdom** — Push blocks into position to bridge gaps and reach Glyph 4.
5. **The Ibis Chamber** — The finale. Break cracked walls and combine all abilities to reach the end portal.

## Credits

Made by [Tholem Labs](https://tholem.ai). Fully open source — built entirely with local AI models on a single RTX 3090 Ti.

**Repository:** [github.com/Tholem-AI/The-Golem-Awakens](https://github.com/Tholem-AI/The-Golem-Awakens)

## For Contributors

- [Adding Chambers](docs/Adding-Chambers.md) — Guide for designing and implementing new levels
- [Tile System](docs/Tile-System.md) — Reference for all 12 tile types and their behaviors
- [chamber-template.md](chamber-template.md) — Tile legend, grid format, and construction conventions
- [chamber-proposal.md](chamber-proposal.md) — Reusable template for new chamber proposals
- [Visual Story Design](docs/Visual-Story-Design.md) — Art and animation design decisions
- [File Structure Reference](docs/File-Structure-Reference.md) — Repository layout overview
- [Project Constraints](docs/Project-Constraints.md) — Technical stack and design constraints
