# Project Constraints

Inferred from `golem.html` source code and design artifacts.

## Technology Stack

| Category | Technology | Source |
|----------|-----------|--------|
| Language | Vanilla JavaScript (ES6+) | `golem.html` |
| Rendering | HTML5 Canvas 2D | `golem.html` line 21-23 |
| Framework | None | No external dependencies |
| Build | None — single-file deployment | `golem.html` is self-contained |
| Package manager | None | No `package.json` |

## Runtime Constraints (Current State)

| Constraint | Value | Source |
|-----------|-------|--------|
| Canvas resolution | 800 x 480 pixels | `golem.html` line 22 |
| Tile size | 32 x 32 pixels | `golem.html` line 22 (T=32) |
| Grid dimensions | 25 columns x 15 rows (existing chambers) | Chamber IIFE blocks |
| Target FPS | 60 (requestAnimationFrame) | Game loop |
||| File size | ~1665 lines, ~60 KB | Single-file constraint |
| Dash system | Hold-to-charge (max 180 frames/3s), linear distance 60-267px | Section 1 constants |
|| Push block | PBlocks[] array — supports N push blocks per chamber via `pushSpawns` array. Backward-compatible with `pushSpawn` single-block. Velocity-based push at PUSH_SPEED (1.25 px/frame). Block-vs-block AABB collision: solid walls horizontally, stacking vertically (top face only). Rider system drags stacked blocks when support moves. | Sections 3, 5, 6 |
| Deployment | Single HTML file, no external dependencies | — |

## Design Constraints

| Constraint | Detail | Source |
|-----------|--------|--------|
| Single-file architecture | All game code in one HTML file | `golem.html` |
| 12 tile types | AIR through PUSH_SPAWN (values 0-11) | `golem.html` line 26 |
| 4 glyphs, sequential | Each grants one ability; must collect in order | Section 8 game flow |
| 5 canonical chambers + 1 test | Progressive difficulty chain via flow. Test chamber accessible by pressing T. | `chamber-data.md` |
| Chamber flow system | Chambers ordered by CHAMBER_FLOW array, not array index. Each main chamber has flowId property. DOOR_D follows flow. Test chamber has no flowId (identified by !c.flowId). | golem.html Section 1 |
| Grant-then-use ability chain | Chamber N grants ability for Chamber N+1 | `chamber-proposal.md` |
| Chamber proposals | chamber-proposal.md is a reusable template. Copy and fill for each new proposal. | `chamber-proposal.md` |

## Assumptions (labeled)

1. **No build step or bundler** — the game runs directly in any modern browser. Adding a build tool would be an architectural change per governance rule 1.
2. **No external assets** — all visuals are currently procedurally drawn (Canvas 2D primitives, particle colors). Adding image/sprite assets would change the asset model.
3. **60 FPS target** — physics constants are tuned for 60 FPS. Changing frame rate requires re-tuning gravity, speed, and timing values.
4. **No audio** — the current implementation has no sound system. Adding audio requires architectural decisions (Web Audio API vs. library).
