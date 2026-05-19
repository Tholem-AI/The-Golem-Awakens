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

### Dash Rewrite (May 2026)
- [x] Hold-to-charge dash with linear distance scaling, ring indicator, HUD bar
- [x] Validation: 20/20 tests passed, zero JS errors

### Code Refactor & Optimization (May 2026)
- [x] 11-section reorganization with delimiter comments
- [x] Logic duplication elimination: killAndRespawn(), endDash(), land(), snapToTileX()
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

---

## Remaining Work

### Bug Fixes (Not Started)

#### Pushblock gap skip
- [ ] Fix: when pushing pushblock over a 1-tile gap at high speed, gravity check is skipped and block floats across. Pushblock should fall into 1-tile gap as intended. Likely needs per-frame gravity enforcement regardless of horizontal velocity.

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

- [ ] Add Web Audio API engine with oscillator-based sounds (no external files)
- [ ] Sounds for: jump, double jump, dash charge, dash release, glyph collect, pushblock push, cracked break, death
- [ ] Estimated ~50 lines for engine + call sites

### Chamber Redesign (Not Started)

Redesign each chamber for better experience using `chamber-proposal.md` as staging area.

- [ ] Chamber 0 — Awakening: Replace staircase with platform-based jump sequence, widen pit
- [ ] Chamber 4 — The Ibis Chamber: Add pits, reposition platforms, make outer cracked walls structurally meaningful
- [ ] Chambers 1, 2, 3: No changes (assessed as well-designed)
- [ ] See `chamber-proposal.md` for detailed proposals and verification criteria

### Visual and Story Overhaul (Not Started)

- [ ] Rework visual theme to match thome.ai website design/theming
- [ ] General visual polish: colors, particle effects, HUD aesthetics, golem sprite detail

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
| Pushblock standing fix | Complete | Review approved, browser verified |
| Pushblock mechanics overhaul | Complete | Smooth push, animation, gap gravity |
| Code refactor | Complete | 11-section reorganization, dead code removed |
| Code optimization | Complete | 6 slices implemented, JS syntax OK |
|| Golem spawn system | Complete | `GOLEM_SPAWN=3` in golem.html, all chambers updated |
||| Transition snap-back fix | Complete | Fade-driven _transitionTarget with guard, JS syntax OK |
||| Dash teleport collision fix | Complete | platSolid one-way + null prevY + PB landing, JS syntax OK, RIPER reviewed |
|| Bug fixes (gap skip) | Not Started | — |
|| Platform visual rework + drop-down | Complete | gy2 fix + platSolid tolerance + inputDown() + narrow ledge render |
|| Message display improvement | Complete | FIFO queue, 3s fade phases, auto-duration, text shadow, 10 browser tests |
| Pause toggle | Not Started | — |
| Responsive canvas scaling | Not Started | — |
| Sound effects | Not Started | — |
| Chamber redesign | Not Started | Proposals in `chamber-proposal.md` |
| Visual/story overhaul | Not Started | — |
|| Touch/mobile controls | Not Started | — |
|| Website integration prep | Not Started | — |
|| Open source release prep | Not Started | — |
