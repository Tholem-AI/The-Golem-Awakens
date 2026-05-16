# ROADMAP

## Completed

### Core Game Implementation
- [x] Physics engine: gravity, acceleration, collision (X/Y separated), platform one-way logic
- [x] Jump system: coyote time (8 frames), input buffering (8 frames), variable height
- [x] Player entity: squash-and-stretch, facing, velocity caps
- [x] Dash system: charge phase (20 frames), burst phase (10 frames), cooldown
- [x] Push block: free-moving physics entity with slot detection
- [x] Break ability: dash through CRACKED tiles with shatter particles
- [x] Glyph system: 4 sequential glyphs with ability gating
- [x] Door/portal system: glyph-locked exits, END_PORTAL ending sequence
- [x] Chamber transitions: screen fade with alpha ramping
- [x] Particle system: 10 trigger types, shatter effect (3 layers)
- [x] HUD: ability panel, chamber name, messages, tutorial text
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

#### High Priority
- [ ] Reduce dash charge time (20 -> 8-10 frames) or switch to press-to-dash
- [ ] Add responsive canvas scaling (CSS or JS viewport fit)
- [ ] Remove dead `pushBlock()` function (line 350) and unused `BLOCK` tile references

#### Medium Priority
- [ ] Equalize jump velocities (first: -10, second: -13 -> make equal)
- [ ] Add pause toggle (Escape key)
- [ ] Add dash charge HUD indicator
- [ ] Fix redundant chamber lookup in wall render loop (use `c` instead of `c2`)

---

## Status

| Phase | Status | Evidence |
|-------|--------|----------|
| Core game | Complete | `golem.html` playable, state audit verified |
| Governance docs | Complete | `docs/`, `README.md`, `ROADMAP.md` created |
| Chamber improvements | Pending | Awaiting approval from `chamber-proposal.md` |
| Code quality | Pending | Awaiting prioritization from `code-review.md` |
