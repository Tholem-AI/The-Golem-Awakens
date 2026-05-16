# Project Constraints

Inferred from `golem.html` source code and design artifacts.

## Technology Stack

| Category | Technology | Source |
|----------|-----------|--------|
| Language | Vanilla JavaScript (ES6+) | `golem.html` |
| Rendering | HTML5 Canvas 2D | `golem.html` line 16-18 |
| Framework | None | No external dependencies |
| Build | None — single-file deployment | `golem.html` is self-contained |
| Package manager | None | No `package.json` |

## Runtime Constraints (Current State)

| Constraint | Value | Source |
|-----------|-------|--------|
| Canvas resolution | 800 x 480 pixels | `golem.html` line 17 |
| Tile size | 32 x 32 pixels | `golem.html` line 17 (T=32) |
| Grid dimensions | 25 columns x 15 rows (existing chambers) | Chamber IIFE blocks |
| Target FPS | 60 (requestAnimationFrame) | Game loop |
| Deployment | Single HTML file, served by any HTTP server or opened locally | No dependencies |

## Design Constraints

| Constraint | Detail | Source |
|-----------|--------|--------|
| Single-file architecture | All game code in one HTML file | `golem.html` |
| 12 tile types | AIR through PUSH_SPAWN (values 0-11) | `golem.html` line 21 |
| 4 glyphs, sequential | Each grants one ability; must collect in order | `golem.html` lines 468-488 |
| 5 canonical chambers + 1 test | Progressive difficulty chain | `chamber-data.md` |
| Grant-then-use ability chain | Chamber N grants ability for Chamber N+1 | `chamber-proposal.md` |
| Chamber proposals scope | Chamber-proposal.md guidelines apply to current chambers only — new chambers may use different layouts | `chamber-proposal.md` Guiding Principles |

## Assumptions (labeled)

1. **No build step or bundler** — the game runs directly in any modern browser. Adding a build tool would be an architectural change per governance rule 1.
2. **No external assets** — all visuals are currently procedurally drawn (Canvas 2D primitives, particle colors). Adding image/sprite assets would change the asset model.
3. **60 FPS target** — physics constants are tuned for 60 FPS. Changing frame rate requires re-tuning gravity, speed, and timing values.
4. **No audio** — the current implementation has no sound system. Adding audio requires architectural decisions (Web Audio API vs. library).
