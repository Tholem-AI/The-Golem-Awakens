# ROADMAP

### Completed

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
- [x] Chamber 0 — Awakening (current)
- [x] Chamber 1 — The Library (current)
- [x] Chamber 2 — The Hall of Echoes (current)
- [x] Chamber 3 — The Weight of Wisdom (current)
- [x] Chamber 4 — The Ibis Chamber (current)
- [x] Chamber T — Test Chamber (debug)
- [x] Game state audit (`golem-state-audit.md`)
- [x] Chamber data extraction (`chamber-data.md`)
- [x] Chamber template spec (`chamber-template.md`)
- [x] Project bootstrap: governance docs, file structure reference, constraints
- [x] AGENTS.md — project-scoped governance (safety, quality, RIPER, constraints)

### Physics Tuning (May 2026)
- [x] Human reaction time alignment: horizontal speed halved (2.5 px/frame), gravity quartered (0.07)
- [x] Jump tuning: first jump -5 vy (same 179px peak, 2x float time), double jump -4.33 vy (134px, 75% of first)
- [x] Variable jump height: cut-on-release at -2 vy for short hops and mid-air control
- [x] Forgiveness mechanics: coyote time 12 frames (200ms), jump buffer 12 frames (200ms)
- [x] Dash charge gravity updated to 0.007 (1/10th of new 0.07 gravity)
- [x] Terminal velocity matched to horizontal speed (2.5 px/frame)
- [x] Research report: `docs/Physics-Research-Report.md`
- [x] Review: approved with zero critical/high findings

### Pushblock Standing Fix (May 2026)
- [x] Chamber T layout: walls on rows 0/14, cols 0/24, PUSH_SPAWN at (12,13), pushSpawn:{x:12,y:13}
- [x] Bug: golem knocked sideways when landing on pushblock from above (X separation before Y landing check)
- [x] Fix: Y-overlap guard in `resolvePushBlockCollision()` — skip X separation when player is on top of pushblock
- [x] Guard: `isOnTop = P.y < PB.y && P.y+P.h >= PB.y-8 && P.y+P.h <= PB.y+P.h/2`
- [x] Preserved: horizontal push (P.y < PB.y is false at same ground level), slot detection, Chamber 3 mechanics
- [x] Review: approved with zero critical/high findings

### Pushblock Mechanics Overhaul (May 2026)
- [x] Smooth velocity-based push: replaced instant 32px tile-step with PB.vx = dir * PUSH_SPEED (1.25 px/frame, half walk speed)
- [x] Push animation: P.pushing flag sets forward-leaning squash (w-3, h-1, 3px lean offset) + pulsing golden arm/shoulder lines
- [x] Gap gravity: smooth push allows existing gravity (PB.vy += 0.3) to act naturally when block moves over pit
- [x] Airborne guard: P.onGround required for push; airborne golem separates from block without pushing
- [x] Death respawn: resetPushBlock() called on pit/OOB death (preserved from existing code)
- [x] Wall blocking: tileCollides in updatePushBlock() stops block against solid; golem free to walk away
- [x] Test chamber enhanced: 3-tile pit at cols 4-6, wall at col 20 rows 9-12 for comprehensive testing
- [x] Review: approved READY FOR BROWSER TESTING, zero critical/high findings

### Dash Rewrite (May 2026)
- [x] Hold-to-charge dash: Shift held accumulates charge (1-180 frames, max 3s)
- [x] Release-to-fire: dash executes with distance proportional to charge time
- [x] Linear distance scaling: 60px (min) to 267px (max, ~1/3 chamber width)
- [x] Charge state: input blocked (X movement frozen, facing still aims), 1/10th gravity with velocity carryover
- [x] Visual feedback: ring indicator (radius 8-40px, pulsates at max), HUD charge bar with MAX indicator
- [x] Preserved: magical wall pass-through, CRACKED block breaking, cooldown, direction follows facing
- [x] Validation: 20/20 tests passed, zero JS errors

### Design Documentation
- [x] `docs/File-Structure-Reference.md` — repository structure
- [x] `docs/Project-Constraints.md` — inferred stack and constraints
- [x] `README.md` — project overview

---

## Remaining Work

### Chamber Improvements (from `chamber-proposal.md`)

#### Chamber 0 — Awakening (Restructure)
- [ ] Replace diagonal staircase with platform-based jump sequence
- [ ] Add platform at row 11 cols 2-3 and row 9 cols 8-9
- [ ] Widen pit from 3 to 6 tiles (cols 4-9)
- [ ] Verify: spawn walkable, glyph reachable, door reachable, row length 25
- [ ] Browser test: tutorial teaches jumping, pit is a real hazard

#### Chamber 4 — The Ibis Chamber (Restructure)
- [ ] Add left pit (cols 4-10, rows 13-14) and right pit (cols 17-23, rows 12-14)
- [ ] Reposition platforms: row 12 cols 3-4 (left), cols 15-16 (right)
- [ ] Add mid-height platforms: row 10 cols 5-6 and 13-14
- [ ] Remove center platform at row 10 cols 11-13
- [ ] Verify: cracked walls block approach paths, portal reachable via dash+break
- [ ] Browser test: outer diamond is structurally meaningful

### Code Quality (from `code-review.md`)

#### Resolved
- [x] Reduce dash charge time or switch to hold-to-charge — done: full hold-to-charge rewrite
- [x] Add dash charge HUD indicator — done: bar + MAX pulse indicator
- [x] Fix redundant ch2/c2 lookup in render loop — done: replaced with existing `c` variable
- [x] Remove dead `pushBlock()` function — done: confirmed never called, removed

#### Code Refactor (May 2026)
- [x] Reorganized golem.html into 11 logical sections with clear delimiter comments
- [x] Section structure: Setup/Constants, Chamber Data, Entities, Input, Tile Helpers/Collision, Push Block System, Particle System, Game Flow, Update, Render, Init/Game Loop
- [x] Removed dead pushBlock() function (old tile-based push, never called)
- [x] Fixed redundant ch2/c2 lookup in render loop (used existing `c` variable)
- [x] Updated chamber-template.md with new section map and extraction instructions
- [x] Beyond-scope simplifications report: `docs/beyond-scope-simplifications.md` (10 items, P0-P5)
- [x] Execution plan: `docs/refactor-execution-plan.md`
- [x] Review: passed, zero critical/high findings
- [x] Validation: JS syntax valid, all 29 functions present, all entities verified
- [ ] Browser testing: verify full playthrough end-to-end (requires browser)

#### High Priority
- [ ] Add responsive canvas scaling (CSS or JS viewport fit)
- [ ] Remove dead `pushBlock()` function (line 350) and unused `BLOCK` tile references

#### Medium Priority
- [ ] Equalize jump velocities (first: -5, second: -4.33 -> consider adjusting double jump feel)
- [ ] Add pause toggle (Escape key)
- [ ] Fix redundant chamber lookup in wall render loop (use `c` instead of `c2`)

---

## Status

|| Phase | Status | Evidence |
|-------|--------|----------|
| Core game | Complete | `golem.html` playable, state audit verified |
| Dash rewrite | Complete | 20/20 tests, zero JS errors, hold-to-charge + ring indicator + HUD bar |
| Physics tuning | Complete | All 5 milestones verified, review approved, docs updated |
| Governance docs | Complete | `docs/`, `README.md`, `ROADMAP.md` created |
| Pushblock standing | Complete | Review approved, zero critical/high findings, browser verified |
| Pushblock mechanics | Complete | Smooth push, animation, gap gravity — review approved, awaiting browser verification |
| Code refactor | Complete | 11-section reorganization, dead code removed, redundancy fixed — review passed, awaiting browser test |
| Chamber improvements | Pending | Awaiting approval from `chamber-proposal.md` |
| Code quality | In Progress | Dash charge items resolved; scaling, cleanup, pause remaining |
