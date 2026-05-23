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
|| File size | ~2035 lines, ~74 KB | Single-file constraint (Phases 1-5.5 theming added ~298 lines) |
|| Dash system | Hold-to-charge (max 180 frames/3s), linear distance 60-267px | Section 1 constants |
|| Color palette | tholem.ai brand tokens: Midnight bg (#12121F), Temple Stone walls, Champagne sacred accents, Seafoam interactive, Emerald completion | Section 10 COLORS |
|| Typography | System fonts: FONT_UI (system-ui), FONT_DISPLAY (italic Georgia), FONT_HEBREW (Segoe UI/Arial Hebrew) | Section 1 constants |
| Push block | PBlocks[] array — supports N push blocks per chamber via `pushSpawns` array. Backward-compatible with `pushSpawn` single-block. Velocity-based push at PUSH_SPEED (1.25 px/frame). 3-phase orchestrator: horizontal velocity -> rider coupling -> gravity/vertical. Block-vs-block AABB collision: solid walls horizontally, stacking vertically. Riders get individual wall collision via `resolveBlockX()`. Falling block crush death via `checkPushBlockCrush()` with 3 guards: golem-on-top skip, block-below skip, horizontal overlap >=10px. Runs after player Y resolution. Bottom-up processing via `activePushBlocks()`. | Sections 3, 5, 6 |
|| rAF lifecycle | Continues during `'ending'` state (animated ending sequence); update() skips, render() draws ending beats | Section 10/11 |
| Deployment | Single HTML file, no external dependencies | — |

## Code Organization

| Constraint | Detail | Source |
|-----------|--------|--------|
| 12 sections | 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 9.5, 10, 11 | `golem.html` delimiter comments |
| Section 1.5 | Shared utility functions (11 helpers) — between Setup/Constants and Chamber Data | Section 1.5 |
| Section 8 | Contains MSG_* message system constants + `showMessage()`, `calcDisplayDuration()` | Section 8 |
| Section 9.5 | Animation state machine (death/respawn) — between Update and Render | Section 9.5 |
| Function hoisting | All helpers use `function` declarations; call order within file does not matter | `golem.html` |
| IIFE encapsulation | Particle system is an IIFE module (`Particles.shatter`, `.spawn(x,y,color,count,shape)`, `.update`). Shape param: 'square' (default), 'circle', 'diamond', 'star'. Render selects shape via path. | Section 7 |
| Data structures | `PARTICLE_COLORS` object (Section 1), `GLYPH_EFFECTS` array (Section 1) | Section 1 |

## Design Constraints

| Constraint | Detail | Source |
|-----------|--------|--------|
| Single-file architecture | All game code in one HTML file | `golem.html` |
| 12 tile types | AIR through PUSH_SPAWN (values 0-11, with value 6 removed) | `golem.html` line 26 |
| 4 glyphs, sequential | Each grants one ability; must collect in order | Section 8 game flow |
| 5 canonical chambers + 1 test | Progressive difficulty chain via flow. Test chamber accessible by pressing T. | `chamber-data.md` |
| Chamber flow system | Chambers ordered by CHAMBER_FLOW array, not array index. Each main chamber has flowId property. DOOR_D follows flow. Test chamber has no flowId (identified by !c.flowId). | golem.html Section 1 |
| Grant-then-use ability chain | Chamber N grants ability for Chamber N+1 | `chamber-proposal.md` |
| Chamber proposals | chamber-proposal.md is a reusable template. Copy and fill for each new proposal. | `chamber-proposal.md` |
| API stability | `killAndRespawn(msg, duration)` — no `onGround` parameter (removed as unused) | Section 1.5 |
| setTile | Simplified — no longer maintains `solidTiles` cache | Section 5 |

## Assumptions (labeled)

1. **No build step or bundler** — the game runs directly in any modern browser. Adding a build tool would be an architectural change per governance rule 1.
2. **No external assets** — all visuals are currently procedurally drawn (Canvas 2D primitives, particle colors). Adding image/sprite assets would change the asset model.
3. **60 FPS target** — physics constants are tuned for 60 FPS. Changing frame rate requires re-tuning gravity, speed, and timing values.
4. **No audio** — the current implementation has no sound system. Adding audio requires architectural decisions (Web Audio API vs. library).
5. **rAF continues during ending** — the animation loop continues during the animated ending sequence (Phase 5). `update()` skips while `render()` draws the 6-beat ending animation. Play Again button reloads the page.
