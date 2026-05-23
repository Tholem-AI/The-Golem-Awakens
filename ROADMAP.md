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

### Pause Toggle (Not Started)

- [ ] Add `P` key handler that sets `gameState = 'paused'`
- [ ] Skip `update()` calls while paused, keep `render()` running
- [ ] Visual overlay: "PAUSED — Press P to resume" text

### Responsive Canvas Scaling (Not Started)

- [ ] Add CSS: `canvas { max-width: 100vw; max-height: 100vh; object-fit: contain; }`
- [ ] Preserves 800x480 internal resolution while fitting viewport

### Sound Effects (Not Started)

See `docs/Visual-Story-Design.md` §4.8 and Phase 10a/10b.

- [ ] Phase 10a: Web Audio API SFX engine with oscillator-based sounds (no external files)
- [ ] Sounds for: jump, double jump, dash charge, dash release, glyph collect, pushblock push, cracked break, death
- [ ] Phase 10b: Temple ambient drone + optional melodic loop (~60 lines additional)
- [ ] Estimated ~60 lines for 10a engine + call sites; ~120 lines total with 10b

### Chamber Redesign (Not Started)

Redesign each chamber for better experience using `chamber-proposal.md` as staging area.

- [x] Chamber 0 — Awakening: Replace staircase with platform-based jump sequence, widen pit, add scattered pits, platforms, interior walls. Door moved to (24,2), glyph at (12,5), spawn at (4,12). Validation: 0 tile mismatches, flow checks pass, JS syntax OK, browser verified.
- [x] Chamber 1 — The Library: Replaced placeholder with complex grid (150 walls, 15 pits, 11 platforms, 2 MAGICAL_WALLs, 1 GLYPH). Validation: 0 tile mismatches, flow OK, JS syntax OK, browser verified.
- [x] Chamber 2 — The Hall of Echoes: Replaced placeholder with complex grid (50+ walls, 9 pits, 3 platforms, 5 MAGICAL_WALLs, 1 GLYPH, 1 PUSH_SPAWN). Validation: 0 tile mismatches, flow OK, JS syntax OK, browser verified.
- [x] Chamber 3 — The Weight of Wisdom: Replaced placeholder with complex grid (30+ walls, 15 pits, 6 platforms, 13 MAGICAL_WALLs, 1 GLYPH, 3 PUSH_SPAWNs, 5 CRACKED). Extended push block system to PBlocks[] array supporting N blocks with backward-compatible pushSpawn wrapper. Validation: 0 tile mismatches, flow OK, JS syntax OK, browser verified.
- [x] Chamber 4 — The Ibis Chamber: Replaced placeholder with complex grid (134 walls, 22 pits, 8 platforms, 8 MAGICAL_WALLs, 8 CRACKED, 3 PUSH_SPAWN, 1 END_PORTAL). Spawn at (2,4), END_PORTAL at (1,1), row 13 AIR override. Validation: 0 tile mismatches, flow OK, JS syntax OK, browser verified, reviewer approved.
- [ ] See `chamber-proposal.md` for detailed proposals and verification criteria

### Visual and Story Overhaul (Phases 1–5 Complete)

See `docs/Visual-Story-Design.md` for phase breakdown (6–10 future).

- [x] Phase 1: tholem.ai palette (Midnight/Ink/Temple Stone), FONT_* constants, PARTICLE_COLORS, DASH colors, CHAMBER_NAMES themed, GLYPH_EFFECTS messages themed, death/respawn messages themed, awakening message, HUD fonts/colors, portal status text (em dash), message colors, starfield, body CSS, particle shatter colors, death/respawn colors (~38 lines)
- [x] Phase 2: Hebrew letter glyph tiles (diamond Champagne halo + Aleph/Mem/He/Tav), golem body Hebrew letters (~15 lines)
- [x] Phase 3: Background runes — 5–9% opacity geometric overlay (Champagne diamond, Seafoam arc, Muted Gold corner accents), progressive sanctity (~15 lines)
- [x] Phase 4: Tile geometry refinements — WALL bevel+capstone trim, PLATFORM chamfered, PIT obsidian+teal rim+champagne cracks, DOOR_D Midnight/Champagne locked & Seafoam open, END_PORTAL Emerald glow, CRACKED Champagne fractures, MAGICAL_WALL Seafoam/Teal, push block altar stone, dash charge Seafoam, player effort/falling colors (~45 lines)
- [x] Phase 4.5: Movement polish — idle head sway, land squish (8-12f), turn lean (6-8f), airborne clay trail, coyote dust puff, landing dust extended to ground (~25 lines)
- [x] Phase 5: Animated 6-beat ending — hero golem, Hebrew letter orbit, EMET convergence on forehead, Champagne flash, Ibis narration, stats (time+deaths), Play Again button with click handler (~90 lines)
- [ ] Phases 6–8: Title menu, pause menu, extended HUD bar (future — see ROADMAP pause/responsive items)
- [ ] Phases 10a–10b: Web Audio SFX and ambient drone (future — see Sound Effects below)

**Reviewer notes:** Contrast guardrails for WALL/PLATFORM vs BG inherent conflict in dark temple palette (spec-level, not implementation). Minor font/color consolidation opportunities (cosmetic, non-blocking).

### Touch/Mobile Controls (Not Started)

- [ ] Add on-screen virtual D-pad and action buttons for mobile
- [ ] Touch event handling for movement, jump, dash, and interaction
- [ ] Estimated ~100+ lines for UI + touch handling

### Website Integration Prep (Not Started)

- [ ] Prepare game for embedding/hosting within website
- [ ] Ensure iframe compatibility, event isolation, and clean embed API if needed

### Open Source Release Prep (Not Started)

Prepare the project for public repository sharing.

- [ ] Add LICENSE file (choose license — e.g., MIT or Apache 2.0)
- [ ] Rewrite `README.md` as a public-facing document: game description, controls, browser requirements, and how to play
- [ ] Add JSDoc comments to all 38 public functions (parameters, returns, purpose)
- [ ] Write `docs/Adding-Chambers.md`: guide for contributors on how to design new levels using `chamber-template.md` and `chamber-data.md` format
- [ ] Write `docs/Code-Architecture.md`: overview of the 11-section structure, physics model, collision system, and entity flow
- [ ] Write `docs/Tile-System.md`: reference for all tile types, constants, solid/one-way behavior, and rendering
- [ ] Sanitize project files: remove internal-only governance docs (`AGENTS.md`, Hermes kit scaffolding) or move to a hidden `.hermes/` directory
- [ ] Add `.gitignore` if not present
- [ ] Verify `golem.html` runs standalone in any modern browser with a single file open

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
||| Code optimization | Complete | 6 slices implemented, JS syntax OK |
||| Code refinement pass | Complete | Dead code removed, helpers consolidated, data-driven glyphs, section cleanup |
||| Golem spawn system | Complete | `GOLEM_SPAWN=3` in golem.html, all chambers updated |
||| Transition snap-back fix | Complete | Fade-driven _transitionTarget with guard, JS syntax OK |
||| Dash teleport collision fix | Complete | platSolid one-way + null prevY + PB landing, JS syntax OK, RIPER reviewed |
||| Death & respawn animations | Complete | 1.5s collapse/construct, state machine, easing, particles, RIPER reviewed |
||| Chamber flow system | Complete | CHAMBER_FLOW + flowId, DOOR_D follows flow, !c.flowId test detection, flow-based HUD |
||| Platform visual rework + drop-down | Complete | gy2 fix + platSolid tolerance + inputDown() + narrow ledge render |
||| Message display improvement | Complete | FIFO queue, 3s fade phases, auto-duration, text shadow, 10 browser tests |
||| Chamber data management | Complete | chamber_diff.py (6 modes), 0 mismatches, 0 strict errors, grids match exactly |
|| Pause toggle | Not Started | — |
| Responsive canvas scaling | Not Started | — |
| Sound effects | Not Started | — |
||||| Chamber 0 redesign | Complete | 0 tile mismatches, flow checks pass, JS syntax OK, browser verified |
||||| Chamber 1 redesign (The Library) | Complete | 0 tile mismatches, flow check pass, JS syntax OK, browser verified |
|||||| Chamber 2 redesign (The Hall of Echoes) | Complete | 0 tile mismatches, flow check OK, JS syntax OK, browser verified |
||||||| Chamber 3 redesign (The Weight of Wisdom) | Complete | 0 tile mismatches, flow OK, JS syntax OK, browser verified, multi-block push system |
||||||| Chamber 4 redesign (The Ibis Chamber) | Complete | 0 tile mismatches, flow OK, JS syntax OK, browser verified, END_PORTAL final chamber |
||||||| Chamber redesign | Complete | All 5 chambers (0-4) redesigned. Diff infrastructure ready (`chamber_diff.py`), proposals in `chamber-proposal.md` |
|||| Visual/story overhaul | Complete | Phases 1–5 implemented: palette, fonts, Hebrew glyphs, runes, geometry, movement polish, animated ending. RIPER reviewed. ~215 lines added.
|| Touch/mobile controls | Not Started | — |
|| Website integration prep | Not Started | — |
|| Open source release prep | Not Started | — |
