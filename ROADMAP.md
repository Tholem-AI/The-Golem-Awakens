# ROADMAP

## Completed

### Core Game Implementation
- [x] Physics engine: gravity, acceleration, collision (X/Y separated), platform one-way logic
- [x] Jump system: coyote time (12 frames), input buffering (12 frames), variable jump height (cut-on-release)
- [x] Player entity: squash-and-stretch, facing, velocity caps
- [x] Dash system: hold-to-charge (up to 3s/180 frames), linear distance scaling (60-267px), release-to-fire, HUD charge bar, ring indicator, cooldown
- [x] Push block: free-moving physics entity with slot detection
- [x] Break ability: dash through CRACKED tiles with shatter particles
- [x] Glyph system: 4 sequential glyphs with ability gating
- [x] Door/portal system: glyph-locked exits, END_PORTAL ending sequence
- [x] Chamber transitions: screen fade with alpha ramping
- [x] Particle system: 10 trigger types, shatter effect (3 layers)
- [x] HUD: ability panel, chamber name, messages, tutorial text, dash charge bar
- [x] Chamber 0-4 + Chamber T (Test) all implemented
- [x] Game state audit (`golem-state-audit.md`)
- [x] Chamber data extraction (`chamber-data.md`) and template spec (`chamber-template.md`)
- [x] Project bootstrap: governance docs, file structure reference, constraints

### Physics Tuning (May 2026)
- [x] Human reaction time alignment: horizontal speed halved, gravity quartered
- [x] Jump tuning: first jump -5 vy, double jump -4.33 vy, variable cut-on-release at -2 vy
- [x] Forgiveness: coyote time 12 frames, jump buffer 12 frames
- [x] Terminal velocity matched to horizontal speed (2.5 px/frame)

### Pushblock Fixes & Overhaul (May 2026)
- [x] Pushblock standing fix: Y-overlap guard prevents X-knock when on top of pushblock
- [x] Smooth velocity-based push: PB.vx = dir * PUSH_SPEED (1.25 px/frame)
- [x] Push animation: forward-leaning squash + pulsing golden arm/shoulder lines
- [x] Gap gravity, airborne guard, death respawn reset, wall blocking

### Pushblock Block-vs-Block Collision (May 2026)
- [x] `pushBlockHit()` helper: AABB overlap test between push blocks (excludes self, inSlot stays solid)
- [x] Horizontal resolution: blocks treat other blocks as solid walls (push A into B stops at B's face)
- [x] Vertical resolution: stacking on top only (prevBottom <= hitY.y + 2 matches player landing tolerance)
- [x] Rider system: `moveBlockRiders()` recursively drags stacked blocks when support moves horizontally
- [x] Recursive rider propagation: 3+ block stacks move as a unit (was: only 2 blocks worked)
- [x] Full per-block flow: prevBx/save -> tile X -> block X -> riders -> prevBy/save -> tile Y -> block Y
- [x] No chain-push, no new tile types, no changes to resolvePushBlockCollision or tileCollides
- [x] Validation: 0 tile mismatches, flow check OK, JS syntax OK, browser test OK, reviewer approved

### Dash Rewrite (May 2026)
- [x] Hold-to-charge dash with linear distance scaling, ring indicator, HUD bar
- [x] Validation: 20/20 tests passed, zero JS errors

### Pushblock Physics Refactor (May 2026)
- [x] 3-phase orchestrator: Phase A (horizontal velocity), Phase B (rider coupling), Phase C (gravity/vertical), Phase D (friction/slots/reset)
- [x] `resolveBlockX(ch, pb, dx)`: horizontal resolver with tile + block collision, returns net displacement
- [x] `resolveBlockY(ch, pb)`: gravity + tile/block Y resolution extracted from updatePushBlock
- [x] `applyBlockVelocityX(ch, pb)`: Phase A helper, stores `_frameDx` for rider coupling
- [x] `isRiding(ob, base)`: extracted rider predicate (feet proximity + horizontal overlap)
- [x] `activePushBlocks()`: returns active non-slotted blocks sorted bottom-up for correct stacking
- [x] `moveBlockRiders(ch, pb, dx)`: riders now get their own wall collision via `resolveBlockX` instead of blind `+= dx`
- [x] `checkPushBlockCrush()`: falling blocks kill golem — 3 guards (vertical direction + horizontal overlap). Runs after player Y resolution so P.y is accurate.
- [x] Bottom-up processing prevents stack instability in multi-block stacks
- [x] `_frameDx` transient cleaned per block in Phase D
- [x] Validation: zero JS errors, game loads in browser

### Pushblock Crush Fix (May 2026)
- [x] Crush vertical guards: golem-on-top (`P.y + P.h <= pb.y + 4`) and block-below (`pb.y >= P.y + P.h - 4`) skip crush
- [x] Crush horizontal guard: `overlapW < 10` skips side-by-side brush
- [x] Crush check moved from `updatePushBlock()` to after player Y + push block landing resolution
- [x] Validation: JS syntax OK, game loads in browser

### Code Refactor & Optimization (May 2026)
- [x] Performance: Date.now() cached, ABILITIES/CHAMBER_NAMES hoisted
- [x] Input normalization: 5 helper functions replacing raw key checks
- [x] 15 physics constants extracted, starfield precomputed
- [x] Dead code removed (BLOCK constant, pushBlock(), redundant ch2/c2)
- [x] Particle system IIFE, tileCollidesRect consolidation
- [x] Sparse tile rendering: solidTiles list per chamber (~67-124 tiles vs 375), setTile() maintains list
- [x] getTile closure optimization: _c cached at update/render entry, _getTile() avoids chambers[] lookup

### Golem Spawn System (May 2026)
- [x] GOLEM_SPAWN tile constant (value 3, reuses unused DOOR_R)
- [x] DOOR_R removed from solid(), checkDoors(), and render()
- [x] GOLEM_SPAWN (^) tile placed in all 6 chamber grids
- [x] px/py removed from chambers.push() — spawn read from tile grid
- [x] _doTransition() simplified: pre-computed spawnPx/spawnPy, no floor search
- [x] Init pre-computes spawn positions in single-pass forEach (O(1) lookup)
- [x] chamber-data.md and chamber-template.md updated with ^ marker and GOLEM_SPAWN spec

### Transition Snap-Back Fix (May 2026)
- [x] Replaced setTimeout-based transition with fade-driven synchronous staging via `_transitionTarget`
- [x] Input/physics frozen only during fade-in (screenFade===1), not during fade-out (screenFade===-1)
- [x] Guard added: `_doTransition` only called when `_transitionTarget>=0` (prevents transitionEnding crash)
- [x] Eliminated ~580ms total freeze during chamber transitions
- [x] Validation: JS syntax OK, zero setTimeout in transition path, _transitionTarget in all 3 locations

### Dash Teleport Collision Fix (May 2026)
- [x] Fixed platSolid(): replaced direction-based predicate (prevY<=curY) with absolute-position one-way check (prevFeet <= gy*T)
- [x] Fixed X-phase null prevY: collidesDash now receives P.y instead of null (push-block AABB geometry corrected)
- [x] Fixed push-block landing: tightened vy>=0 to vy>0, added Math.abs(P.vx)<3 guard, reduced tolerance from +4 to +2
- [x] Validation: JS syntax OK, RIPER process (research->plan->execute->review), reviewer-agent approved

### Death & Respawn Animations (May 2026)
- [x] Death animation: golem collapses into clay over 1.5s (90 frames) with body parts spreading outward, alpha fade, clay particles
- [x] Respawn animation: golem constructs from clay bottom-up (legs->arms->torso->head->eye->glyphs) over 1.5s (90 frames)
- [x] Respawn animation plays at game start ("I awaken...") and after death
- [x] State machine: idle -> dying (90f) -> respawning (90f) -> idle
- [x] Easing functions: easeOutCubic, easeInOutCubic, easeOutBack
- [x] Animation freezes physics/input during death/respawn (updateAnim replaces update)
- [x] Double-trigger guard in killAndRespawn prevents stack overflow
- [x] Transition guards prevent chamber transitions during animation
- [x] Clay particles spawn during both death (outward burst) and respawn (upward convergence)
- [x] Validation: JS syntax OK, zero console errors, RIPER process (research->plan->execute->review), reviewer-agent approved

### Chamber Flow System (May 2026)
- [x] CHAMBER_FLOW array and flowId properties on all main chambers
- [x] checkDoors() rewritten: DOOR_D follows CHAMBER_FLOW instead of array index+1
- [x] Test chamber entry/exit: uses `!c.flowId` discriminator instead of `chambers.length-1`
- [x] HUD chamber name display: uses flow position instead of hardcoded `ch<4`
- [x] Chamber T grid updated: comprehensive sandbox (pit, MAGICAL_WALL, CRACKED, platforms, push block, DOOR_D)
- [x] chamber-template.md: added flow system documentation section with add/replace/insert/special chamber guides
- [x] chamber-proposal.md: replaced legacy content with clean reusable template
- [x] chamber-data.md: updated Chamber T grid and annotations
- [x] ROADMAP.md, File-Structure-Reference.md, Project-Constraints.md, README.md updated
- [x] Validation: JS syntax OK, flow system verified in code inspection

### Chamber 2 — The Hall of Echoes Implementation (May 2026)
- [x] Replaced placeholder Chamber 2 with "The Hall of Echoes" complex grid from chamber-data.md
- [x] New grid: 50+ walls, 9 pits, 3 platforms, 5 MAGICAL_WALLs, 1 GLYPH, 1 PUSH_SPAWN, 1 DOOR_D, 1 GOLEM_SPAWN
- [x] Spawn (22,2), Door (18,13), Glyph (3,1), PushSpawn (6,8), MAGICAL_WALL vertical column at col 20
- [x] Follows 9-step ordered construction convention
- [x] Validation: 0 tile mismatches, flow check OK, JS syntax OK, browser test OK

### Chamber Data Management (May 2026)
- [x] tools/chamber_diff.py: diff/validation tool with 6 modes (diff, validate, strict, export-ascii, diff-proposal, check-flow)
- [x] Fixed handler ordering bug in chamber_diff.py (parsing now robust)
- [x] Added --export-ascii for generating ASCII grid exports from HTML
- [x] Added --strict flag for strict tile validation against legend
- [x] Added --check-flow for verifying CHAMBER_FLOW consistency
- [x] Added three-way diff support for comparing multiple chamber sources
- [x] chamber-data.md: stripped all annotation lines — now grid-only (185 -> ~120 lines)
- [x] chamber-data.md: fixed 25 tile mismatches between grids and golem.html
- [x] chamber-data.md: grids now match golem.html exactly (0 mismatches)
- [x] golem.html Section 2: reordered all 6 chamber IIFEs to follow 9-step ordered construction convention with /* Step N: */ comments
- [x] chamber-template.md: fixed Tile Legend, added Rules section, Ordered Construction Convention section, Diff Workflows section (A-F)
- [x] AGENTS.md quality gates updated with chamber_diff.py commands (5 -> 10 items)
- [x] Validation: 0 tile mismatches, 0 strict validation errors, 0 JS errors, game loads in browser, export matches exactly, flow checks pass

### Chamber 3 — The Weight of Wisdom Implementation (May 2026)
- [x] Replaced placeholder Chamber 3 with "The Weight of Wisdom" complex grid from chamber-data.md
- [x] New grid: 30+ walls, 15 pits, 6 platforms, 13 MAGICAL_WALLs, 1 GLYPH, 3 PUSH_SPAWNs, 5 CRACKED
- [x] Spawn (11,12), Door (23,0), Glyph (18,1), PushSpawns (13,1)/(12,4)/(17,13)
- [x] Extended push block system: PB -> PBlocks[] array, resetPushBlock supports pushSpawns/pushSpawn
- [x] Updated resolvePushBlockCollision, updatePushBlock, collidesDash, render for multi-block iteration
- [x] Follows 9-step ordered construction convention
- [x] Validation: 0 tile mismatches, flow check OK, JS syntax OK, browser test OK

### Chamber 1 — The Library Implementation (May 2026)
- [x] Replaced placeholder Chamber 1 with "The Library" complex grid from chamber-data.md
- [x] New grid: 150 walls, 15 pits, 11 platforms, 2 MAGICAL_WALLs, 1 GLYPH, 1 DOOR_D, 1 GOLEM_SPAWN
- [x] Spawn (2,2), Door (11,13), Glyph (23,12), MAGICAL_WALL at (20,11) and (20,12)
- [x] Follows 9-step ordered construction convention
- [x] tools/chamber_diff.py: added int(col_expr) fallback for numeric column literals
- [x] Validation: 0 tile mismatches, flow check OK, JS syntax OK, browser test OK, reviewer approved

### Chamber 4 — The Ibis Chamber Implementation (May 2026)
- [x] Replaced placeholder Chamber 4 with "The Ibis Chamber" complex grid from chamber-data.md
- [x] New grid: 134 walls, 22 pits, 8 platforms, 8 MAGICAL_WALLs, 8 CRACKED, 3 PUSH_SPAWN, 1 END_PORTAL
- [x] Spawn (2,4), END_PORTAL (1,1), PushSpawns (6,3)/(6,4)/(13,5)
- [x] Row 13 AIR override for open floor area, row 14 has PIT at cols 1-6 + WALL at cols 7-24
- [x] Follows 9-step ordered construction convention
- [x] No game logic changes needed — existing pushSpawns array support handles 3 blocks
- [x] Validation: 0 tile mismatches, flow check OK, JS syntax OK, browser test OK, reviewer approved

### Code Refinement Pass (May 2026)
- [x] Dead code removal: easeInOutCubic, easeOutBack, `_testMode`, duplicate "I awaken..." overlay, dead render code, dead slot code
- [x] Section header renumbering: clean 1, 1.5, 2-9, 9.5, 10, 11 with comment cleanup
- [x] `prevKeys` unbounded growth fix: `syncPrevKeys()` helper keeps it bounded to active keys only
- [x] Message queue + timer extraction: `advanceTimers()` helper consolidates HUD/messaging state
- [x] API cleanup: `killAndRespawn` `onGround` param removed, rAF cancel on game end
- [x] Dash/reset helper consolidation: `fullDashReset()`, `cancelDash()`, `resetPlayerToRespawn()`
- [x] Push block defensive fix: `return` -> `continue` in `resolvePushBlockCollision` for multi-block iteration
- [x] `playerGridPos()` helper extraction, X-collision simplification
- [x] MSG_* constants co-located in Section 8, `setTile()` simplified
- [x] Data-driven glyph system: `GLYPH_EFFECTS` map, `PARTICLE_COLORS` constants
- [x] Helper functions consolidated in UTILITIES section (1.5)
- [x] File reduced: 1727 -> 1716 lines, ~64 KB -> ~62 KB. Zero JS errors, game loads and runs.

### Code Review Slices S1-S11 (May 2026)
- [x] S1: Dead code removal — removed `captionAlpha()` (11 lines, 0 call sites) and `ANIM_TOTAL_FRAMES` (unused constant)
- [x] S2: State guard consolidation — 3 `gameState==='X'` checks replaced with single `gameState !== 'playing'` guard
- [x] S3: ShadowText helper — extracted `shadowText(ctx, text, x, y, color, blur)` replacing 6 repeated shadowBlur patterns
- [x] S4: Player reset consolidation — `_doTransition()` and `resetGameState()` now call `resetPlayerToRespawn()` instead of duplicating reset logic
- [x] S5: Dash reset consolidation — `endDash()` and `fullDashReset()` now call `cancelDash()` as base instead of duplicating `P.dashing=false; P.dashTimer=0`
- [x] S6: Grid coordinate helper — extracted `playerGridBounds()` replacing duplicated `Math.floor(P.x/T)` / `Math.floor((P.x+P.w-1)/T)` in hot path
- [x] S7: Magic numbers to constants — added 8 named constants: TRANSITION_FADE_SPEED, ENDING_FADE_SPEED, SIM_ACCUMULATOR_CAP, MAX_TICKS_PER_FRAME, SHADOW_BLUR, LAND_SQUISH_FRAMES, TURN_LEAN_FRAMES, STARS_PER_CHAMBER
- [x] S8: Jump deduplication — extracted `doJump(vel, color, count, shape, sfx, fromGround)` helper replacing 4 jump branches with shared boilerplate
- [x] S9: DOM caching — cached HUD DOM refs (`hudBar`, `hudLeft`, `hudRight`) at module level, added throttle gate (`lastHudUpdate`) reducing DOM writes by 95%+
- [x] S10: Wall base helper — extracted `drawWallBase(ctx, px, py)` replacing 4 fillRect calls duplicated for WALL and CRACKED tiles
- [x] S11: Ending messages data-driven — Ibis lines rendered from data array + `shadowText()` helper
- [x] File: 2668 -> 2577 lines (-91 lines, -3.4%). JS syntax OK, zero console errors, browser test OK, reviewer-agent approved all 11 slices.

### Code Review Remaining Reduction (May 2026)
- [x] Item 1: Ending messages unified — merged beat 2/3 messages with ibisLines into single `endingMessages` array with type-based alpha selection (caption vs ibis). 5 entries, unified loop. ~16 lines saved.
- [x] Item 2: Chamber boundary helpers — extracted `sBounds(g,w,h)`, `hLine(g,y,x1,x2,v)`, `vLine(g,x,y1,y2,v)` after `mkGrid()`. Replaced repetitive boundary construction in all 6 chamber IIFEs. ~12 lines saved.
- [x] Item 3: Screen fade simplification — folded 3 `screenFade` if-blocks into single block using `screenFade*TRANSITION_FADE_SPEED` with `Math.max/Math.min` clamping. Early return preserved. ~2 lines saved.
- [x] Item 4: Dash arc segments extraction — extracted `drawSegArcs(cx,cy,r,count,gap)` helper replacing 3 inline arc-drawing for-loops. ~8 lines saved.
- [x] File: 2666 -> 2625 lines (-41 lines, -1.5%). JS syntax OK, zero console errors, chamber_diff.py --strict 0 mismatches, browser test OK, reviewer-agent approved.

### Code Review Line Reduction Cleanup (May 2026)
- [x] Dead code removal: unused `smoothStep()` function, unused `vLine()` function, unused `inputShiftPressed()` function, unused `_snd` property from push blocks (A1-A4)
- [x] Duplicate assignment cleanup: removed redundant `respawnX/Y` assignment in `resetGameState()` (A5)
- [x] Dead comments removed: 2 stale feature comments (A6)
- [x] Unused constants: removed 4 MSG base constants (MSG_FADE_IN_FRAMES, etc.) no longer used after wall-clock ending (B1)
- [x] Constant folding: DASH_EXEC and CHARGE_PARTICLE_COLOR folded into PARTICLE_COLORS object (B2)
- [x] Pattern compression: `endingBeat` if/else chain compressed to loop (6->2 lines), `captionAlphaSec()` compressed (11->6 lines), `resetGameState()` assignments compressed (C1-C3)
- [x] Comment reduction: verbose phase comments in `getEndingGlyphState()` trimmed (C4)
- [x] Whitespace: blank line removed in `fullDashReset()` (E2)
- [x] Skipped: E1 (not present), E3 (audio change out of scope), Section D (NOT RECOMMENDED per plan)
- [x] No architectural changes, no new features, no behavioral changes
- [x] File: 2625 -> 2588 lines (-37 lines, -1.4%). JS syntax OK, zero console errors, chamber_diff.py --strict 0 mismatches, --check-flow OK, browser test OK.

---

## Remaining Work

### Platform Visual Rework (May 2026) — COMPLETED

- [x] Redraw platforms as narrow ledges at the top of the tile (match hitbox, preserve landing-on-top behavior)
- [x] Create `inputDown()` helper for ArrowDown/KeyS (consistent with existing input helpers)
- [x] When Down is pressed/held, allow golem to phase through platform from above (drop-down mechanic)
- [x] Fixed gy2 off-by-one in Y collision: `(P.y+P.h-1)` → `(P.y+P.h)` inclusive boundary
- [x] Added +2px tolerance to `platSolid()` for edge stability
- [x] Validation: JS syntax OK, RIPER process (research→plan→execute→review), reviewer-agent approved

### Message Display Improvement (May 2026) — COMPLETED

- [x] Replace single-slot message system (messageText/messageTimer) with FIFO queue
- [x] 3-second fade-in (180 frames) + auto-calculated display hold + 3-second fade-out per message
- [x] Auto-duration based on text length (MSG_CHARS_PER_FRAME=0.35, clamped to 90-360 frames)
- [x] Queue max depth of 5 with silent overflow drop
- [x] Message dedup: skips identical text already at queue front
- [x] "Forever" messages (dur>=99999): clear queue, immediate display
- [x] Text shadow for readability on busy backgrounds
- [x] Updated guard at render: messageTimer<=0 → messageQueue.length===0
- [x] Validation: JS syntax OK, 10 browser tests passed, RIPER process (research→plan→execute→review), reviewer-agent approved

### Title Menu (Phase 6) + Pause Menu (Phase 7) (May 2026) — COMPLETED

- [x] Title menu: THOLEM SVG logo (6 paths matching Logo_Full_Color.svg exactly), "THE GOLEM AWAKENS" title, "made by Tholem Labs" link to tholem.ai, "Fully open source" link to GitHub + AI blurb, "PRESS ANY KEY TO BEGIN" prompt with pulse animation
- [x] Title screen overlay: HTML/CSS overlay in `#game-shell` wrapper, inline SVG with native `<a href>` link, CSS hover effects (Seafoam color transition)
- [x] Timer starts only when gameplay begins from title screen (deferred `gameStartTime`)
- [x] Pause menu: P key toggle with `fresh()` edge detection to prevent hold spam
- [x] Pause overlay: "PAUSED" text, RESUME button, RETURN TO MAIN MENU button
- [x] HUD visibility: hidden on title screen (cleared), visible during gameplay and pause (removed 'paused' from HUD guard)
- [x] Return to menu: full game reset via resetGameState() (player state, chamber, abilities, glyphs, particles, ending state, keys), loop cancellation, then UI transition
- [x] Play Again (ending): calls returnToMenu() instead of location.reload()
- [x] Loop guard: rAF only scheduled during playing/paused states (stops during title/ending)
- [x] startGame(): restarts rAF loop after reset
- [x] State machine: title -> playing -> paused -> playing (resume) or title (return to menu with full reset)
- [x] Validation: JS syntax OK, 0 browser errors/warnings, full flow verified (Title -> Start -> Play -> Pause -> Return to Menu -> Title -> Start fresh -> player moves)

### Responsive Canvas Scaling (Phase 9) (May 2026) — COMPLETED

- [x] CSS: `transform-origin: center center` on `#game-wrapper`
- [x] JS: IIFE responsive scaling — calculates `min(viewportWidth/800, viewportHeight/512)` and applies `transform: scale(N)`
- [x] Window resize listener updates scale factor dynamically
- [x] Scales entire game (canvas + HUD bar + title menu + pause overlay + all fonts/SVG)
- [x] Preserves 800x480 internal canvas resolution
- [x] `image-rendering: pixelated` ensures crisp scaling
- [x] Click handler already normalizes via `getBoundingClientRect()` — works with any CSS scale
- [x] Tested: 1920x1080 (2.109x), 375x812 (0.469x), 320x568 (0.4x), 3440x1440 (2.8125x)
- [x] Validation: zero JS errors, zero console errors, browser test OK, reviewer approved

### Sound Effects (May 2026) — COMPLETED

See `docs/Visual-Story-Design.md` §4.8 and Phase 10a/10b.

- [x] Phase 10a: Web Audio API SFX engine with oscillator-based sounds (no external files). Data-driven SFX config (SFX object with 9 sound definitions: 4 oscillator types — triangle, square, chord, noise). Sound IIFE module (Section 7.5) with init(), play(), setMute(), isMuted().
- [x] 11 SFX call sites wired: jump (x2), double jump, dash release, glyph collect, cracked break, push block (with spam guard), landing (x2: ground + pushblock), death, respawn
- [x] Phase 10b: Temple ambient drone (D2, 73.42 Hz sine) + D minor arpeggio loop at 75 BPM with look-ahead scheduler
- [x] Mute toggle: M key with fresh() edge detection + HUD mute indicator via Sound.isMuted()
- [x] Music lifecycle: startGame/init+start, togglePause/stop+start, transitionEnding/stop, returnToMenu/stop
- [x] Reviewer improvements: pre-allocated noise buffer, ctx.resume() in startMusic()
- [x] File: 2195 -> 2322 lines, ~96KB -> ~91KB. JS syntax PASS, zero browser errors.

### Fixed Timestep + Wall-Clock Ending (May 2026)

- [x] Fixed simulation timestep: 240 Hz (SIM_HZ=240) via accumulator pattern with performance.now()
- [x] Accumulator: simAcc (ms) + SIM_DT (ms/tick), max 8 ticks/frame, 128ms clamp prevents spiral of death
- [x] Accumulator only during 'playing' state — not paused, not ending, not title
- [x] Fixed frame-count constants: COYOTE_FRAMES/JUMP_BUFFER/DASH_CHARGE_MAX/DASH_DURATION/DASH_COOLDOWN/ANIM_TOTAL/MSG_* (240 Hz)
- [x] Original per-tick physics constants (GRAVITY=0.07, TERMINAL_VEL=2.5, JUMP_VEL_1=-5, etc.) preserved AS-IS
- [x] Wall-clock ending timeline: ENDING constants (BEAT_1-6 at 0s/2s/5s/9s/14s/16s), independent of difficulty
- [x] captionAlphaSec() helper for time-based caption fades in ending (vs frame-based captionAlpha())
- [x] Exclusive beat rendering (===) for beats 1-4, persistent (>=) for beats 5-6
- [x] Fixed caption Y overlaps: Beat 2 at H-155, Beat 3 at H-130, Beat 4 ibis lines staggered
- [x] Ending uses performance.now() - endingStartTime for wall-clock timing
- [x] Pace toggle removed: single 240 Hz mode (Temple Pace) only
- [x] Integration: simAcc reset in togglePause() and resetGameState(), lastSimTime=performance.now() in startGame()
- [x] HUD uses frozenElapsedSec during 'ending' state
- [x] Removed dead endingFrame variable; endingStartTime uses performance.now() consistently
- [x] Validation: JS syntax OK, file 2561 lines ~104KB, all existing functionality preserved

### Ending Glyph Sequence Smoothing (May 2026)

- [x] Easing helpers: `easeOutQuint`, `lerp`, `smoothStep` added to Section 1.5 utilities (complement existing `easeOutCubic`)
- [x] `getEndingGlyphState(endSec, cx, cy)` function — continuous glyph/EMET state machine replacing 4 exclusive per-beat blocks
- [x] Unified ending renderer — single `getEndingGlyphState()` call drives glyph positions, alpha, EMET alpha/fontSize/glow, flash bloom, and convergence progress
- [x] Glyph orbit: speed ramps from 0.6 to 2.2 rad/s with `easeOutCubic`; radius shrinks 50→35; center shifts toward `cy-30` — all time-driven from B2
- [x] Glyph convergence: `easeOutQuint` from orbit to target positions over 2.5s; He (index 2) dissolves first starting at converge=0.4
- [x] EMET cross-fade: starts at converge=0.6, `easeOutCubic` ramp to full alpha
- [x] Flash bloom: Gaussian bell curve (`exp(-t²)`) centered at converge≈0.7, width 0.15, peak alpha 0.25
- [x] Font size: smooth lerp 24→28px during convergence (`easeOutCubic`, converge 0.5→1.0)
- [x] EMET glow: ramps in after converge complete, `Math.max(baseGlow, baseGlow + pulse)` floors pulse at base so glow never dims below base
- [x] Ibis lines: changed from fade-in/fade-out (`captionAlphaSec`) to fade-in-then-persist (`Math.min((endSec - start)/0.6, 1)`)
- [x] Ibis lines guard: changed `endingBeat === 4` to `endingBeat >= 4` so lines render through all later beats
- [x] Glow pulse: deterministic `endSec` instead of `performance.now()` — no frame-rate artifacts
- [x] Stats and Play Again alpha: `easeOutCubic` instead of linear `Math.min()` for smoother fade-in
- [x] All 8 discontinuities from research plan resolved: 2 HIGH (orbit jump, glyph vanish/EMET blink), 4 MEDIUM (font size jump, linear fades, sin strobe flash, exclusive beat rendering), 2 LOW (ibis overlap, fade/timing mismatch)
- [x] Validation: JS syntax OK, zero console errors, timing verified against wall-clock timeline

#### Known Issues / Future Work

- [ ] `MSG_CHARS_PER_FRAME` doesn't scale with `SIM_HZ` (minor — text scroll speed fixed at 240 Hz)

### Left/Right Input Asymmetry Fix (June 2026)

- [x] Added `lastDirKey` global variable tracking most recently pressed horizontal direction key
- [x] Keydown handler records `lastDirKey` (Left=37, Right=39) on each press
- [x] Keyup handler recalculates `inputDirLeft()`/`inputDirRight()` instead of clearing flags — prevents stale direction
- [x] Tiebreaker in `update()`: when both Left and Right held, `lastDirKey` determines direction (last key pressed is sovereign)
- [x] Reset `lastDirKey` in `resetGameState()`
- [x] Fixed indentation on lines 1283-1286 (3-space to 2-space)
- [x] Minimal change: ~15 lines in golem.html only. No chamber changes, no new game mechanics. Purely input handling improvement.
- [x] Validation: JS syntax OK, zero behavioral changes beyond fixing asymmetric input

### MAGICAL_WALL Stuck Bug Fix + Visual Death Effect (June 2026)

- [x] Root cause: `collidesDash()` skips MAGICAL_WALL, but dash collision with WALL behind it called `endDash()` without the death check (which only fired on `dashTimer<=0`). Player snapped to WALL boundary overlapping MAGICAL_WALL, permanently trapped since MAGICAL_WALL is solid for normal movement.
- [x] Fix A1: MAGICAL_WALL center-tile check after X-axis dash collision resolution (snapToTileX + endDash path)
- [x] Fix A2: Persistent safety net for stuck players (animState==='idle' && !P.dashing && P.vx===0 && P.vy===0 && center on MAGICAL_WALL)
- [x] Fix B1-B8: Death cause tracking (`deathCause` state), `killAndRespawn(msg, duration, cause)` API, `Particles.magicalWallDeath()` with hexagonal teal/purple fracture particles, 'hex' particle shape, hexagonal fracture energy overlay in death animation
- [x] Review finding: CRITICAL Y-axis check killed player during ANY dash through MAGICAL_WALL (gravity drift triggered false positive). Removed entirely — X-axis check + timer expiry check + safety net cover all stuck scenarios.
- [x] Review finding: `deathCause` reset in `resetGameState()` added for defensive hygiene.
- [x] Safety guards: center-tile check (not AABB) prevents adjacent-stand false positives; `!P.dashing` prevents killing during active dash; `animState==='idle'` prevents double-trigger during animations.
- [x] Visual effect: 28 particles (18 hex teal/purple fracture shards + 10 white-teal energy sparks) + rotating hexagonal ring overlay during dying animation.
- [x] JS syntax OK, zero console errors, browser tests verified: dash through MW survival, dash-into-WALL death, safety net activation, adjacent stand safety.

### Chamber Redesign (Not Started)

Redesign each chamber for better experience using `chamber-proposal.md` as staging area.

- [x] Chamber 0 — Awakening: Replace staircase with platform-based jump sequence, widen pit, add scattered pits, platforms, interior walls. Door moved to (24,2), glyph at (12,5), spawn at (4,12). Validation: 0 tile mismatches, flow checks pass, JS syntax OK, browser verified.
- [x] Chamber 1 — The Library: Replaced placeholder with complex grid (150 walls, 15 pits, 11 platforms, 2 MAGICAL_WALLs, 1 GLYPH). Validation: 0 tile mismatches, flow OK, JS syntax OK, browser verified.
- [x] Chamber 2 — The Hall of Echoes: Replaced placeholder with complex grid (50+ walls, 9 pits, 3 platforms, 5 MAGICAL_WALLs, 1 GLYPH, 1 PUSH_SPAWN). Validation: 0 tile mismatches, flow OK, JS syntax OK, browser verified.
- [x] Chamber 3 — The Weight of Wisdom: Replaced placeholder with complex grid (30+ walls, 15 pits, 6 platforms, 13 MAGICAL_WALLs, 1 GLYPH, 3 PUSH_SPAWNs, 5 CRACKED). Extended push block system to PBlocks[] array supporting N blocks with backward-compatible pushSpawn wrapper. Validation: 0 tile mismatches, flow OK, JS syntax OK, browser verified.
- [x] Chamber 4 — The Ibis Chamber: Replaced placeholder with complex grid (134 walls, 22 pits, 8 platforms, 8 MAGICAL_WALLs, 8 CRACKED, 3 PUSH_SPAWN, 1 END_PORTAL). Spawn at (2,4), END_PORTAL at (1,1), row 13 AIR override. Validation: 0 tile mismatches, flow OK, JS syntax OK, browser verified, reviewer approved.
- [ ] See `chamber-proposal.md` for detailed proposals and verification criteria

### Ability Unlock Glow + Death Text Visual Distinction (June 2026)

- [x] Added message type constants: MSG_DEFAULT (0), MSG_ABILITY (1), MSG_DEATH (2)
- [x] Created styledText() helper with optional glow layer (shadowBlur=8, emerald rgba(5,150,105,0.6))
- [x] shadowText() preserved as thin wrapper for backward compatibility (HUD, ending captions, default messages)
- [x] showMessage() extended with optional type parameter (defaults to MSG_DEFAULT)
- [x] Message rendering: type-aware branch — ability gets emerald glow, death gets sepia tone, default unchanged
- [x] Ability name tagged MSG_ABILITY (lore message stays MSG_DEFAULT for visual hierarchy)
- [x] Death/respawn messages tagged MSG_DEATH (sepia rgba(180,150,110,a) — aged papyrus tone)
- [x] Aligned with Visual-Story-Design.md thematic requirements
- [x] Validation: JS syntax OK, zero console errors, browser test OK, all 3 message types verified, backward compat confirmed

### Ending Sequence Overhaul (May 2026)

- [x] Extracted `drawGolemSprite(ctx, px, py, opts)` shared rendering function — single source of truth for golem sprite proportions
- [x] Fixed ending sprite proportions: replaced hand-calculated offsets with center-to-top-left math (`px = cx - P.w/2, py = cy - P.h/2`)
- [x] Ending golem: 2x scale, soft glow (shadowBlur 4.8), front-facing variant (twoEyes), alpha via drawGolemSprite save/restore
- [x] In-game idle sprite: replaced 24-line inline drawing with single drawGolemSprite call (pixel-identical)
- [x] `captionAlpha(frame, start, fadeIn, hold, fadeOut)` helper — decouples caption timing from visual beats
- [x] Staggered Ibis lines: 3 captions revealed sequentially (start frames 380/440/500, 60-frame fadeIn, 180-frame hold, 60-frame fadeOut)
- [x] Extended beat timing: beats 4-6 stretched (480->800, 540->920) — total ending ~15s (from ~9s)
- [x] Caption shadow for readability over glyph animation (shadowBlur 4)
- [x] Skip-on-click: click anywhere after beat 3 jumps to Play Again
- [x] Death/respawn animations preserved (not converted — progressive reveal doesn't map to drawGolemSprite)
- [x] Validation: JS syntax OK, zero console errors, RIPER reviewed, timing verified

### Glyph Ordering & Ending Animation Fixes (May 2026)

- [x] Glyph letter assignment: replaced position-based formula `(x+y*25)%4` with chamber index `ch` — each chamber now shows correct Hebrew letter (Aleph/Mem/He/Tav)
- [x] HUD: replaced `Glyphs: 3/4` count with `Name: א ○ ○ ○` showing actual Hebrew letters with empty circle slots
- [x] EMET ending text: fixed `\u05e2` (Ayin) to `\u05d0` (Aleph) — renders אמת ("truth") not עמת ("earth")
- [x] Timer freeze: added `frozenElapsedSec` captured in `transitionEnding()`, displayed instead of live `Date.now()`
- [x] Text outline: added `strokeText()` before `fillText()` for EMET visibility against background
- [x] RTL rendering: set `X.direction='rtl'` for all Hebrew fillText calls (glyphs, HUD, orbit, ending)
- [x] Text overlap fix: beat 3 message guarded to only render during beat 3, not during beat 4+
- [x] Validation: JS syntax OK, zero console errors, flow checks pass, browser test OK, RIPER reviewed

### Visual and Story Overhaul (Phases 1-5.6 Complete)

See `docs/Visual-Story-Design.md` for phase breakdown (6-10 future).

- [x] Phase 1: tholem.ai palette (Midnight/Ink/Temple Stone), FONT_* constants, PARTICLE_COLORS, DASH colors, CHAMBER_NAMES themed, GLYPH_EFFECTS messages themed, death/respawn messages themed, awakening message, HUD fonts/colors, portal status text (em dash), message colors, starfield, body CSS, particle shatter colors, death/respawn colors (~38 lines)
- [x] Phase 2: Hebrew letter glyph tiles (diamond Champagne halo + Aleph/Mem/He/Tav), golem body Hebrew letters (~15 lines)
- [x] Phase 3: Background runes — 5-9% opacity geometric overlay (Champagne diamond, Seafoam arc, Muted Gold corner accents), progressive sanctity (~15 lines)
- [x] Phase 4: Tile geometry refinements — WALL bevel+capstone trim, PLATFORM chamfered, PIT obsidian+teal rim+champagne cracks, DOOR_D Midnight/Champagne locked & Seafoam open, END_PORTAL Emerald glow, CRACKED Champagne fractures, MAGICAL_WALL Seafoam/Teal, push block altar stone, dash charge Seafoam, player effort/falling colors (~45 lines)
- [x] Phase 4.5: Movement polish — idle head sway, land squish (8-12f), turn lean (6-8f), airborne clay trail, coyote dust puff, landing dust extended to ground (~25 lines)
- [x] Phase 5: Animated 6-beat ending — hero golem, Hebrew letter orbit, EMET convergence on forehead, Champagne flash, Ibis narration, stats (time+deaths), Play Again button with click handler (~90 lines)
- [x] Phase 5.5: Visual refinements — wall bevel corner highlight, platform chamfered edges (path drawing), pit danger glow all 4 edges, push block rounded corners (arcTo), push effort stroke lines + spark, dash compass rose (8 segments), magical wall hexagonal core (Cosmic Purple #7B68EE), cracked walls X-pattern + edge glow, door geometric icons (seal/chevron), particle shape system (circle/diamond/star/square), golem rounded head (arcTo) + splayed trapezoid feet, glyph RTL bottom-up ordering + dark stroke outline, ending golem consistent + text repositioning, pushblock particle spam fix (~103 lines)
- [x] Phase 5.6: Visual refinements (May 2026) — pit symmetric danger indicators (upward chevron + side ticks on all 4 edges), reduced platforming particles (removed airborne trail + coyote dust, halved landing dust 4->2), removed vertical Hebrew glyphs from golem body (glyph count in HUD), hide normal side arms during push animation (prevents 4-arm illusion). RIPER reviewed. ~23 lines removed/changed.
- [x] Phase 5.6.1: Pushblock particle spam fix — gated pushblock landing particles with `justLanded` check (`prevY + P.h < pb.y` strict) so particles only spawn once on actual landing, not every frame during gravity oscillation. Zero physics/mechanics change. ~3 lines added.
- [x] Phase 8: Extended HUD bar — DOM-based 32px bar above canvas (#game-wrapper), Hebrew glyph slots (RTL) left side, timer (MM:SS) + death count right side, removed "Name: " prefix artifact, removed inline ABILITIES list from canvas, ability unlocks show themed message + ability name via showMessage queue, removed unused ABILITIES const array. RIPER reviewed. ~40 lines net.
- [x] Phase 6: Title menu — THOLEM SVG logo (6 paths), "THE GOLEM AWAKENS" title, "made by Tholem Labs" link to tholem.ai, "Fully open source" link to GitHub + AI blurb, pulse animation prompt. Timer deferred until gameplay starts.
- [x] Phase 7: Pause menu — P key toggle (fresh edge detection), "PAUSED" overlay, RESUME + RETURN TO MAIN MENU buttons, HUD visible during pause, full game reset on return to menu (resetGameState()), loop restart on startGame().
- [x] Phase 9: Responsive CSS scaling — `transform-origin: center center` on `#game-wrapper`, JS IIFE calculates `min(viewportWidth/800, viewportHeight/512)` scale factor, window resize listener, scales entire game (canvas + HUD + overlays + fonts + SVG). Zero JS errors, browser verified, reviewer approved. ~13 lines net.
- [x] Phases 10a-10b: Web Audio SFX (9 sounds, 11 call sites, Section 7.5) + ambient drone (D2 73.42Hz) + D minor arpeggio at 75 BPM. M-key mute toggle with HUD indicator. Music lifecycle wired to game state transitions. JS syntax OK, zero browser errors.
- [x] Phase 5.5.1 PIT glow improvement (June 2026): Teal rim alpha boosted 0.28->0.42 (peak 0.252 meets spec >=0.25), soft radial gradient glow extends 0.1*T beyond all edges via createRadialGradient, inner glow/crack alpha boosted 0.15->0.22. RIPER process (research->plan->execute->review), JS syntax OK, zero browser errors, canvas pixel verification confirms smooth gradient falloff. ~10 lines net.

**Reviewer notes:** Contrast guardrails for WALL/PLATFORM vs BG inherent conflict in dark temple palette (spec-level, not implementation). Minor font/color consolidation opportunities (cosmetic, non-blocking).

### Pause Menu Controls + HUD Enhancements (May 2026)

- [x] Pause menu controls reference: added `.po-controls` block with CONTROLS header and 5 control rows (Move, Jump, Dash, Pause, Mute)
- [x] HUD "P to pause" reminder: subtle ink-colored (#454560) 10px text in HUD right section
- [x] CSS: 5 new rules (.po-controls, .po-controls-title, .po-control-row, .po-key, .po-action) scoped under #pause-overlay
- [x] No game logic changes — purely UI additions. ~60 lines added/modified out of 2655 (~2.3%)
- [x] Validation: JS syntax OK, zero browser errors, RIPER process (research->plan->execute->review), reviewer-agent approved

### Touch/Mobile Controls (Not Started)

- [ ] Add on-screen virtual D-pad and action buttons for mobile
- [ ] Touch event handling for movement, jump, dash, and interaction
- [ ] Estimated ~100+ lines for UI + touch handling

### Website Integration

- [ ] Ensure iframe compatibility, event isolation, and clean embed API if needed

### Open Source Release Prep (June 2026) — COMPLETED

Prepare the project for public repository sharing.

- [x] Evaluate git history for GitHub publication — clean, no sensitive data. Recommendation: master branch suitable for direct push.
- [x] Add LICENSE file (MIT License, Copyright 2026 Tholem Labs)
- [x] Rewrite `README.md` as a public-facing document: game description, controls, browser requirements, how to play, abilities, chambers, contributor links
- [x] Add JSDoc comments to all 86+ public functions (parameters, returns, purpose) — lightweight format
- [x] Write `docs/Adding-Chambers.md`: guide for contributors on how to design new levels using `chamber-template.md` and `chamber-data.md` format and verify using tools
- [x] Write `docs/Code-Architecture.md`: overview of the 14-section structure, physics model, collision system, and entity flow (renamed from Project-Reference.md)
- [x] Write `docs/Tile-System.md`: reference for all tile types, constants, solid/one-way behavior, and rendering
- [x] Keep AGENTS.md with purpose documentation for contributors
- [x] Add `.gitignore` (generic coverage: __pycache__, *.pyc, node_modules/, .env, OS artifacts, .hermes/, IDE dirs)
- [x] Clean up legacy documentation: removed check_syntax.js, code-review-line-reduction.md, tools/__pycache__/
- [x] Update docs/File-Structure-Reference.md to reflect current state
- [x] Validation: JS syntax OK, zero browser console errors, chamber_diff.py --strict 0 mismatches, --check-flow OK

---

## Status

| Phase | Status | Evidence |
|-------|--------|----------|
| Core game | Complete | `golem.html` playable, state audit verified |
| Dash rewrite | Complete | 20/20 tests, zero JS errors |
| Physics tuning | Complete | All milestones verified, review approved |
|| Pushblock standing fix | Complete | Review approved, browser verified |
|| Pushblock mechanics overhaul | Complete | Smooth push, animation, gap gravity |
||| Pushblock block-vs-block collision | Complete | pushBlockHit, moveBlockRiders (recursive), N-block stacking, riders |
||||| Pushblock crush fix | Complete | 3 guards (vertical + horizontal overlap), moved after player Y |
|||| Pushblock physics refactor | Complete | 3-phase orchestrator, resolveBlockX/Y, rider collision, crush death (3 guards), bottom-up |
| Code refactor | Complete | 11-section reorganization, dead code removed |
||||| Code optimization | Complete | 6 slices implemented, JS syntax OK |
||||| Code refinement pass | Complete | Dead code removed, helpers consolidated, data-driven glyphs, section cleanup |
|||||| Code review slices S1-S11 | Complete | 11 slices: dead code, state guards, shadowText, player/dash reset, grid bounds, 8 constants, doJump, DOM cache, drawWallBase, data-driven ending. 2668 -> 2577 lines (-91, -3.4%). JS syntax OK, zero console errors, reviewer approved. |
||||||| Code review remaining reduction | Complete | 4 items: ending messages unified (data-driven array), chamber boundary helpers (sBounds/hLine/vLine), screen fade simplification, dash arc segments extraction. 2666 -> 2625 lines (-41, -1.5%). JS syntax OK, chamber_diff 0 mismatches, browser OK, reviewer approved. |
||||||| Code review line reduction cleanup | Complete | Dead code (smoothStep, vLine, inputShiftPressed, _snd), duplicate assignment, dead comments, unused MSG constants, constant folding (DASH_EXEC/CHARGE_PARTICLE_COLOR -> PARTICLE_COLORS), pattern compression (endingBeat loop, captionAlphaSec, resetGameState), comment reduction, whitespace. 2625 -> 2588 lines (-37, -1.4%). Zero behavioral/architectural changes. chamber_diff.py --strict 0 mismatches, --check-flow OK, JS syntax OK, browser test OK. |
|||| Golem spawn system
||| Transition snap-back fix | Complete | Fade-driven _transitionTarget with guard, JS syntax OK |
||| Dash teleport collision fix | Complete | platSolid one-way + null prevY + PB landing, JS syntax OK, RIPER reviewed |
||| Death & respawn animations | Complete | 1.5s collapse/construct, state machine, easing, particles, RIPER reviewed |
||| Chamber flow system | Complete | CHAMBER_FLOW + flowId, DOOR_D follows flow, !c.flowId test detection, flow-based HUD |
||| Platform visual rework + drop-down | Complete | gy2 fix + platSolid tolerance + inputDown() + narrow ledge render |
||| Message display improvement | Complete | FIFO queue, 3s fade phases, auto-duration, text shadow, 10 browser tests |
||| Chamber data management | Complete | chamber_diff.py (6 modes), 0 mismatches, 0 strict errors, grids match exactly |
||| Pause toggle (Phase 6 + 7) | Complete | Title menu (THOLEM SVG + Tholem Labs credit + GitHub link + AI blurb, press-any-key start), P-key pause (fresh edge detection), RESUME + RETURN TO MAIN MENU, HUD hidden on title / visible during pause, full reset via resetGameState() on return to menu, loop guard stops rAF during title/ending, startGame() restarts loop. Play Again -> returnToMenu(). 0 browser errors, full flow verified. |
|| Responsive canvas scaling | Complete | Phase 9: JS-based transform scale, zero errors, reviewer approved |
| Sound effects | Complete | Phase 10a/10b: Web Audio API SFX (9 sounds, 11 call sites, Section 7.5 IIFE), ambient drone (D2 73.42Hz), D minor arpeggio (75 BPM), M-key mute + HUD indicator, music lifecycle wired to game state |
||||| Chamber 0 redesign | Complete | 0 tile mismatches, flow checks pass, JS syntax OK, browser verified |
||||| Chamber 1 redesign (The Library) | Complete | 0 tile mismatches, flow check pass, JS syntax OK, browser verified |
|||||| Chamber 2 redesign (The Hall of Echoes) | Complete | 0 tile mismatches, flow check OK, JS syntax OK, browser verified |
||||||| Chamber 3 redesign (The Weight of Wisdom) | Complete | 0 tile mismatches, flow OK, JS syntax OK, browser verified, multi-block push system |
|||||||| Chamber 4 redesign (The Ibis Chamber) | Complete | 0 tile mismatches, flow OK, JS syntax OK, browser verified, END_PORTAL final chamber |
|||||||| Chamber redesign | Complete | All 5 chambers (0-4) redesigned. Diff infrastructure ready (`chamber_diff.py`), proposals in `chamber-proposal.md` |
||||||||| Visual/story overhaul | Complete | Phases 1-10b implemented: palette, fonts, Hebrew glyphs, runes, geometry, movement polish, animated ending, visual refinements (symmetric pit, reduced particles, clean golem body, push arm guard), HUD bar, title menu, pause menu, responsive CSS scaling, Web Audio SFX (9 sounds, 11 call sites), ambient drone (D2 73.42Hz), D minor arpeggio (75 BPM), mute toggle. RIPER reviewed. ~310 lines net. |
||||||||||| Pause menu controls + HUD | Complete | Controls reference in pause overlay, P-to-pause hint. Zero JS errors, browser verified, RIPER reviewed. |
||||||||||| Glyph ordering & ending fixes | Complete | Chamber-index glyph letters, RTL Hebrew, EMET Ayin->Aleph, 3-letter orbit, frozen timer, text outline, overlap guard. RIPER reviewed.
||||||||| Ending sequence overhaul | Complete | Extracted drawGolemSprite() shared function (gameplay + ending), fixed ending sprite proportions (center-to-top-left math), 2x scale + glow + front-facing variant on ending screen, captionAlpha() timing helper, staggered Ibis lines (3s read each), extended beat timing (~9s -> ~15s), skip-on-click, caption shadow. RIPER reviewed.
||||||| Ending glyph smoothing | Complete | easeOutQuint/lerp/smoothStep helpers, getEndingGlyphState() continuous state machine replacing per-beat hard cuts, unified ending renderer, orbit speed/radius/center ramps, easeOutQuint convergence, EMET cross-fade, Gaussian flash bloom, font size lerp 24-28px, deterministic glow pulse, Ibis fade-in-then-persist, easeOutCubic stats/PlayAgain alpha. 8 discontinuities resolved (2 HIGH, 4 MEDIUM, 2 LOW). |
||| Touch/mobile controls | Not Started | — |
||| Website integration prep | Not Started | — |
||| Open source release prep | Complete | MIT LICENSE, .gitignore, README rewrite, 86+ JSDoc comments, docs/Adding-Chambers.md, docs/Code-Architecture.md (renamed), docs/Tile-System.md, AGENTS.md purpose note, legacy cleanup. JS syntax OK, zero browser errors, chamber_diff 0 mismatches, flow check OK. |
||| Fixed timestep + wall-clock ending | Complete | SIM_HZ=240, accumulator pattern (simAcc+SIM_DT, max 8 ticks, 128ms clamp), fixed frame-count constants (240 Hz), ENDING wall-clock timeline (0s/2s/5s/9s/14s/16s), captionAlphaSec() helper. Single 240 Hz mode (Temple Pace). All per-tick physics constants preserved. Pace toggle removed.
