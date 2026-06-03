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
| Sim timing | Fixed timestep: 240 Hz (SIM_HZ=240) via accumulator pattern with performance.now() | Section 1 constants (SIM_HZ) |
| Sim accumulator | simAcc (ms) + SIM_DT (ms/tick), max 8 ticks/frame, 128ms clamp prevents spiral of death. Only accumulates during 'playing' state (not paused/ending/title). | Section 11 loop() |
| Fixed frame constants | COYOTE_FRAMES, JUMP_BUFFER, DASH_CHARGE_MAX, DASH_DURATION, DASH_COOLDOWN, ANIM_TOTAL, MSG_FADE_IN/OUT, MSG_MIN/MAX_HOLD — fixed at 240 Hz | Section 1 constants |
| Ending timeline | Wall-clock (performance.now()), independent of sim Hz: beats at 0s, 2s, 5s, 9s, 14s, 16s. captionAlphaSec() for time-based fades. | Section 3, ENDING object |
| File size | ~2520 lines, ~101 KB | Single-file constraint |
| Dash system | Hold-to-charge (max 180 frames @ 240Hz / 3s), linear distance 60-267px. Uses DASH_CHARGE_MAX (180 frames). | Section 1 constants |
| Color palette | tholem.ai brand tokens: Midnight bg (#12121F), Temple Stone walls, Champagne sacred accents, Seafoam interactive, Emerald completion | Section 10 COLORS |
| Typography | System fonts: FONT_UI (system-ui), FONT_DISPLAY (italic Georgia), FONT_HEBREW (Segoe UI/Arial Hebrew) | Section 1 constants |
| Push block | PBlocks[] array — supports N push blocks per chamber via `pushSpawns` array. Backward-compatible with `pushSpawn` single-block. Velocity-based push at PUSH_SPEED (1.25 px/frame). 3-phase orchestrator: horizontal velocity -> rider coupling -> gravity/vertical. Block-vs-block AABB collision: solid walls horizontally, stacking vertically. Riders get individual wall collision via `resolveBlockX()`. Falling block crush death via `checkPushBlockCrush()` with 3 guards: golem-on-top skip, block-below skip, horizontal overlap >=10px. Runs after player Y resolution. Bottom-up processing via `activePushBlocks()`. | Sections 3, 5, 6 |
| rAF lifecycle | Continues during `'ending'` state (animated ending sequence); update() skips, render() draws ending beats | Section 10/11 |
| Deployment | Single HTML file, no external dependencies | — |

## Code Organization

| Constraint | Detail | Source |
|-----------|--------|--------|
| 13 sections | 1, 1.5, 2, 3, 4, 5, 6, 7, 7.5, 8, 9, 9.5, 10, 11 | `golem.html` delimiter comments |
| Section 1.5 | Shared utility functions (22 helpers) — between Setup/Constants and Chamber Data. Added easeOutQuint, lerp, getEndingGlyphState for ending sequence smoothing. Added shadowText, playerGridBounds, doJump, drawWallBase from code review S3-S4-S6-S8-S11. | Section 1.5 |
| Section 1 | Named constants from code review S7: TRANSITION_FADE_SPEED (0.06), ENDING_FADE_SPEED (0.03), SIM_ACCUMULATOR_CAP (128), MAX_TICKS_PER_FRAME (8), SHADOW_BLUR (4), LAND_SQUISH_FRAMES (10), TURN_LEAN_FRAMES (8), STARS_PER_CHAMBER (40) | Section 1 |
| Section 7.5 | Sound engine (IIFE: init, play, setMute, isMuted, startMusic, stopMusic) — between Particles and Game Flow | Section 7.5 |
| Section 8 | Contains MSG_* message system constants + `showMessage()`, `calcDisplayDuration()` | Section 8 |
| Section 9.5 | Animation state machine (death/respawn) — between Update and Render | Section 9.5 |
| Function hoisting | All helpers use `function` declarations; call order within file does not matter | `golem.html` |
|| IIFE encapsulation | Particle system is an IIFE module (`Particles.shatter`, `.spawn(x,y,color,count,shape)`, `.update`, `.magicalWallDeath(x,y)`). Shape param: 'square' (default), 'circle', 'diamond', 'star', 'hex'. Render selects shape via path. | Section 7 |
| Data structures | `PARTICLE_COLORS` object (Section 1), `GLYPH_EFFECTS` array (Section 1), `ENDING` object (Section 3) | Section 1, 3 |

## Design Constraints

| Constraint | Detail | Source |
|-----------|--------|--------|
| Single-file architecture | All game code in one HTML file | `golem.html` |
| 12 tile types | AIR through PUSH_SPAWN (values 0-11, with value 6 removed) | `golem.html` line 26 |
| 4 glyphs, sequential | Each grants one ability; must collect in order | Section 8 game flow |
|| 5 canonical chambers + 1 test | Progressive difficulty chain via flow. Test chamber accessible by pressing T. | `chamber-data.md` |
|| MAGICAL_WALL mechanics | Solid for normal movement, passable during dash. Death triggered when dash ends (collision or timer expiry) with player center inside MAGICAL_WALL tile. Persistent safety net kills stuck player (idle + zero velocity + center overlap). Visual death effect: hexagonal teal/purple particle burst + fracture overlay. | Sections 1.5, 4, 9 |
| Chamber flow system | Chambers ordered by CHAMBER_FLOW array, not array index. Each main chamber has flowId property. DOOR_D follows flow. Test chamber has no flowId (identified by !c.flowId). | golem.html Section 1 |
| Grant-then-use ability chain | Chamber N grants ability for Chamber N+1 | `chamber-proposal.md` |
| Chamber proposals | chamber-proposal.md is a reusable template. Copy and fill for each new proposal. | `chamber-proposal.md` |
|| API stability | `killAndRespawn(msg, duration, cause)` — `cause` is optional (null|'magicalWall'), defaults to null. Visual death effect varies by cause. | Section 1.5 |
| setTile | Simplified — no longer maintains `solidTiles` cache | Section 5 |
| Sim timing preserves per-tick constants | All per-tick physics constants (GRAVITY=0.07, TERMINAL_VEL=2.5, JUMP_VEL_1=-5, etc.) are preserved AS-IS. They define behavior per sim tick, not per rAF frame. Changing sim Hz changes the rate of ticks, not the physics per tick. | Section 1 constants |
| Ending independence | Ending sequence uses wall-clock time (performance.now() - endingStartTime) in seconds. Timeline beats (0s, 2s, 5s, 9s, 14s, 16s) fixed at single 240 Hz mode. | Section 3, ENDING object |
| Frozen timer during ending | HUD displays frozenElapsedSec (captured in transitionEnding()) during 'ending' state instead of live Date.now() timer. | Section 10 render |

## Assumptions (labeled)

1. **No build step or bundler** — the game runs directly in any modern browser. Adding a build tool would be an architectural change per governance rule 1.
2. **No external assets** — all visuals are currently procedurally drawn (Canvas 2D primitives, particle colors). Adding image/sprite assets would change the asset model.
3. **Per-tick physics constants** — physics constants (GRAVITY=0.07, TERMINAL_VEL=2.5, etc.) are tuned per simulation tick. At 240 Hz, each tick is ~4.17ms. The per-tick physics values define behavior per tick, and all frame-count constants (COYOTE_FRAMES, JUMP_BUFFER, DASH_CHARGE_MAX, etc.) are fixed at 240 Hz.
4. **Audio** — Web Audio API sound system (Section 7.5 IIFE): 9 SFX definitions (4 oscillator types: triangle, square, chord, noise), 11 call sites, ambient drone (D2 73.42 Hz) + D minor arpeggio loop at 75 BPM with look-ahead scheduler. M-key mute toggle with HUD indicator. Lazy-init on first user gesture (browser autoplay policy). No external audio files — all synthesized.
5. **rAF continues during ending** — the animation loop continues during the animated ending sequence (Phase 5). `update()` skips while `render()` draws the 6-beat ending animation. Wall-clock timing (performance.now()) makes ending duration independent of sim Hz. Play Again button returns to title menu via returnToMenu().
6. **Accumulator only during playing** — simAcc accumulates only when gameState==='playing'. It is reset to 0 (along with lastSimTime) in togglePause(), resetGameState(). lastSimTime is set to performance.now() in startGame(). This prevents phantom ticks during pauses, transitions, and the title screen.
