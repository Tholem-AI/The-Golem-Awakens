# Refactor Execution Plan: golem.html

**Date:** 2026-05-16
**Author:** Planner Agent (Hermes)
**Scope:** Reorganize golem.html (1133 lines) into 11 logical sections; remove dead code; fix redundancy; update docs.
**Constraint:** Single HTML file, no behavior change, no signature/variable renames.

---

## Innovate Checkpoint

Before committing to a grouping strategy, two alternatives were considered:

### Alternative A: Topological Dependency Order
Group code strictly by call-graph dependencies. Constants first, then data, then utilities, then systems in dependency order (entities depend on nothing, input depends on nothing, tile helpers depend on chamber data, push block depends on tile helpers + entities, particles depends on nothing, game flow depends on entities+transition, update depends on everything, render depends on everything, init depends on everything).

**Pros:** Cleanest dependency flow; forward references eliminated; each section only uses things defined above it.
**Cons:** Would require significant reordering of the existing code (e.g., `aabb()` currently defined at line 233 but used by `resolvePushBlockCollision()` at line 188 — wait, that's backward. Actually `aabb` is at 233 but `resolvePushBlockCollision` at 188 calls it — this means `aabb` is called BEFORE it's defined, which works in JS due to function hoisting but is confusing). This alternative would move `aabb` before its first caller.

**Verdict:** Good for maintainability but involves more risk of accidental reordering errors. The current code already relies on JS hoisting, so we'd be changing that contract.

### Alternative B: Functional Grouping (CHOSEN)
Group by logical subsystems while preserving the existing top-to-bottom flow as much as possible. Each section is clearly labeled with delimiter comments. Sections follow a natural flow: setup -> data -> state -> input -> helpers -> systems -> game loop.

**Pros:** Minimal disruption to existing code; preserves JS hoisting behavior; each section is self-contained; easy for humans to navigate; low risk of introducing bugs.
**Cons:** Some forward references remain (e.g., `aabb` defined in Section 5 but called by `resolvePushBlockCollision` in Section 6 — this is fine because both use function declarations which are hoisted).

**Decision: Alternative B (Functional Grouping).** Low-risk, preserves existing hoisting behavior, clean section boundaries.

### Alternative C (briefly considered): IIFE Module Pattern
Wrap each section in an IIFE and pass dependencies explicitly.

**Rejected:** Would change the architecture significantly (violates governance rule: no architectural changes without approval). Would require changing all function references to use explicit parameters or module exports.

---

## Current Code Structure (Line Map)

```
Lines 1-14:      HTML/Canvas setup
Lines 15-31:     Constants (W, H, T, tiles, dash, push speed)
Lines 33-145:    Chamber data (mkGrid, 6 IIFEs)
Lines 147-168:   Entities (P object, globals, PB object)
Lines 176-184:   resetPushBlock()          -- currently between entities and input
Lines 186-230:   resolvePushBlockCollision() -- currently between entities and input
Lines 232-235:   aabb()                    -- currently between push block and tile helpers
Lines 237-245:   tileCollides()            -- currently between push block and tile helpers
Lines 247-301:   updatePushBlock()         -- currently between push block and tile helpers
Lines 303-316:   Input system
Lines 318-384:   Tile helpers (getTile, setTile, solid, platSolid, etc.)
Lines 386-398:   pushBlock()               -- DEAD CODE
Lines 400-443:   Particle system
Lines 445-534:   Game flow (showMessage, transition, checkDoors, checkGlyphs, transitionEnding)
Lines 536-780:   update()
Lines 782-1118:  RENDER (COLORS, render())
Lines 1120-1125: Init
Lines 1127-1129: Game loop
```

---

## Proposed Section Order (11 Sections)

| # | Section | Target Lines | Current Lines |
|---|---------|-------------|---------------|
| 1 | HTML Setup & Constants | `<script>` + constants | 1-31 |
| 2 | Chamber Data | mkGrid + 6 IIFEs | 33-145 |
| 3 | Entities | P object, globals, PB object | 147-174 |
| 4 | Input System | keys, listeners, fresh(), shiftHeld() | 303-316 |
| 5 | Tile Helpers & Collision | getTile, setTile, solid, platSolid, tileCollidesY, collides, collidesNoPlat, collidesDash, inPit, aabb, tileCollides | 232-245, 318-384 |
| 6 | Push Block System | resetPushBlock, resolvePushBlockCollision, updatePushBlock | 176-230, 247-301 |
| 7 | Particle System | shatterBlock, spawnParticles, updateParticles | 400-443 |
| 8 | Game Flow | showMessage, _doTransition, transition, checkDoors, checkGlyphs, transitionEnding | 445-534 |
| 9 | Update | update() | 536-780 |
| 10 | Render | COLORS, render() | 782-1118 |
| 11 | Init & Game Loop | init code, loop() | 1120-1129 |

---

## Ordered Atomic Tasks

Each task is independent and verifiable. Tasks must be executed in order due to line-number shifts.

### Task 1: Remove dead pushBlock() function
- **What:** Delete lines 386-398 (the `pushBlock()` function and its `/* Abilities */` comment)
- **Lines removed:** 386-398 (13 lines)
- **Risk:** NONE — function is never called anywhere in the codebase
- **Verification:** Search for `pushBlock` — should only find references in the NEW push block system (resetPushBlock, resolvePushBlockCollision, updatePushBlock), not the dead function

### Task 2: Remove BLOCK tile constant
- **What:** Remove `BLOCK=6` from the tile constants line (line 21)
- **Before:** `const AIR=0, WALL=1, PIT=2, DOOR_R=3, DOOR_D=4, GLYPH=5, BLOCK=6, CRACKED=7, PLATFORM=8, END_PORTAL=9, MAGICAL_WALL=10, PUSH_SPAWN=11;`
- **After:** `const AIR=0, WALL=1, PIT=2, DOOR_R=3, DOOR_D=4, GLYPH=5, CRACKED=7, PLATFORM=8, END_PORTAL=9, MAGICAL_WALL=10, PUSH_SPAWN=11;`
- **Risk:** LOW — BLOCK is used in `solid()` (line 330) and render (line 886) but NEVER appears in any chamber data. However, we must keep `BLOCK` referenced in `solid()` and render() because the code may encounter it from future chambers or the conversion script. Wait — the research says it's unused. Let me verify: search shows `BLOCK` appears in:
  - Line 21: constant definition
  - Line 330: `solid()` function checks `t===BLOCK`
  - Line 392: dead `pushBlock()` function (removed in Task 1)
  - Line 886: render() `t===BLOCK`
  - chamber-template.md: in the legend and conversion script
- **Decision:** Keep BLOCK constant. The research flagged it as "safe to remove" but it IS referenced in `solid()` and `render()`. Removing it would break those functions. The research likely meant "no chamber data uses it" — which is true, but the code still references it. **DEFERRING BLOCK removal** — it's dead data but not dead code. The render branch at line 886 and the solid() check at line 330 will never execute but removing them introduces risk. Document this as a beyond-scope cleanup.

### Task 3: Fix redundant ch2/c2 lookup in render loop
- **What:** Replace lines 817-822 that redundantly look up `ch2` and `c2` (which are identical to already-existing `ch` and `c`)
- **Before (lines 817-822):**
  ```js
  const ch2=P.chamber, c2=chambers[ch2];
  let adjPit=false;
  if(y+1<c.h && c2.tiles[y+1]&&c2.tiles[y+1][x]===PIT) adjPit=true;
  if(y-1>=0 && c2.tiles[y-1]&&c2.tiles[y-1][x]===PIT) adjPit=true;
  if(x-1>=0 && c2.tiles[y]&&c2.tiles[y][x-1]===PIT) adjPit=true;
  if(x+1<c.w && c2.tiles[y]&&c2.tiles[y][x+1]===PIT) adjPit=true;
  ```
- **After:**
  ```js
  let adjPit=false;
  if(y+1<c.h && c.tiles[y+1]&&c.tiles[y+1][x]===PIT) adjPit=true;
  if(y-1>=0 && c.tiles[y-1]&&c.tiles[y-1][x]===PIT) adjPit=true;
  if(x-1>=0 && c.tiles[y]&&c.tiles[y][x-1]===PIT) adjPit=true;
  if(x+1<c.w && c.tiles[y]&&c.tiles[y][x+1]===PIT) adjPit=true;
  ```
- **Risk:** NONE — `ch2` always equals `ch` and `c2` always equals `c` at this point (both read `P.chamber` which doesn't change inside render)
- **Verification:** Game renders identically; no console errors

### Task 4: Reorganize code into 11 sections (main refactor)
This is the core structural change. It involves cutting and pasting entire blocks. Execute in this order:

#### 4a: Move section boundaries and add delimiter comments
Add clear section delimiters matching the 11-section plan. Each section gets:
```
/* ══════════════════════════════════════════════════
   SECTION NAME
   ══════════════════════════════════════════════════ */
```

#### 4b: Move Input System (current lines ~303-316) to after Entities
- Cut: Input system block
- Paste: After line ~168 (after `let testChamberSrc = -1;`)

#### 4c: Move Tile Helpers & Collision to consolidated block
- Current scattered locations: lines 318-384 (main block) + lines 232-245 (aabb, tileCollides)
- Move `aabb()` and `tileCollides()` from between push block code to the consolidated tile helpers section
- Final location: After Input System section

#### 4d: Move Push Block System to consolidated block
- Current scattered locations: lines 176-230 (resetPushBlock, resolvePushBlockCollision) + lines 247-301 (updatePushBlock)
- Consolidate all three functions into one contiguous block
- Final location: After Tile Helpers section

#### 4e: Reorder remaining sections (already roughly in order)
- Particle System (400-443) — already in good position
- Game Flow (445-534) — already in good position
- Update (536-780) — already in good position
- Render (782-1118) — already in good position
- Init & Game Loop (1120-1129) — already in good position

**Risk:** MODERATE — moving function declarations around is safe in JS (they're hoisted), but moving code that references variables defined later could cause issues. Since all functions use `function` declarations (not `const` arrow functions), hoisting ensures they work regardless of order.

**Verification:** Open golem.html in browser, verify game loads and runs without errors

### Task 5: Update chamber-template.md
- **What:** Remove BLOCK tile entry from the Tile Legend table
- **Line 16:** Remove `| \`B\` | BLOCK      | 6     | Pushable block (static tile)                 |`
- **Line 212:** Remove `'B': 'BLOCK',` from the Python CHAR_TO_CONST dict
- **Line 3:** Update description: "Each tile maps to one ASCII character." (no change needed)
- **Risk:** NONE — BLOCK is not used in any chamber data

### Task 6: Create beyond-scope simplifications report
- **What:** Write `docs/beyond-scope-simplifications.md` documenting opportunities found during research
- **Content:** See Beyond-Scope Report section below

---

## Validation Gates

Each task has a gate that must pass before moving to the next:

| Task | Validation Gate | Method |
|------|----------------|--------|
| 1 (Remove pushBlock) | No JS errors in console; search confirms no references to old pushBlock | Open browser console, search codebase |
| 2 (BLOCK constant) | DEFERRED — documented as beyond-scope | N/A |
| 3 (Fix ch2/c2) | Render identical; no console errors | Open browser, visual check |
| 4 (Reorganize) | Game loads, all 5 chambers playable, all 4 glyphs collectible, ending triggers | Full playthrough or test chamber (press T) |
| 5 (chamber-template.md) | File parses correctly; no syntax errors in Python conversion script | Visual review |
| 6 (Beyond-scope report) | Report exists, is accurate, and references specific lines | Visual review |

---

## Testing Strategy

Since this is a browser-based game, testing is manual:

### Quick Smoke Test (after each task):
1. Open `golem.html` in browser (Chrome/Firefox)
2. Check browser console for JS errors (F12)
3. Verify the first chamber loads with the golem character visible
4. Verify movement (arrow keys/WASD) works
5. **If any of these fail: STOP and investigate before proceeding**

### Full Verification (after Task 4 - reorganization):
1. Play through Chamber 0: collect glyph 1 (double jump), exit through door
2. Play through Chamber 1: use double jump, collect glyph 2 (dash), exit
3. Play through Chamber 2: use dash through magical wall, collect glyph 3 (push blocks)
4. Play through Chamber 3: push block into slot, collect glyph 4 (break cracked)
5. Play through Chamber 4: break cracked walls, reach END_PORTAL, trigger ending
6. Test chamber: Press T in any chamber, verify all abilities unlocked, test push block physics

### Automated Assist:
- Set `_testMode = true` (line 449) before loading to skip fade transitions — speeds up testing significantly
- Or press T to enter test chamber which grants all abilities instantly

---

## Dependency Ordering

```
Task 1 (Remove dead code)  -->  Task 3 (Fix redundancy)  -->  Task 4 (Reorganize)
                                                                         |
Task 5 (Update template) <-- Task 4 (Reorganize)  -->  Task 6 (Beyond-scope report)
```

- Tasks 1 and 3 can be done before or during Task 4 (they're small surgical edits)
- Task 4 depends on Tasks 1 and 3 being done first (line numbers shift)
- Tasks 5 and 6 are independent of the code changes and can be done in parallel

**Recommended execution order:** 1 -> 3 -> 4 -> 5 -> 6

---

## Beyond-Scope Simplifications Report (to be written as separate .md)

The following improvements were identified during research but are OUT OF SCOPE for this refactor:

1. **Jump equalization** — First jump uses `-5` velocity, double jump uses `-4.33`. Consider equalizing for consistent feel.
2. **Pause toggle** — No pause functionality exists. Adding a simple pause (P key) would improve UX.
3. **Responsive canvas scaling** — Canvas is fixed at 800x480. Adding CSS `max-width: 100vw; max-height: 100vh` with `object-fit: contain` would make it responsive on different screen sizes.
4. **BLOCK constant cleanup** — The BLOCK tile type (value 6) is defined and referenced in `solid()` and `render()` but never used in any chamber data. Full removal would require also removing the render branch and solid() check.
5. **Input normalization** — Arrow keys and WASD are both supported but listed separately. Could unify into a single directional input abstraction.
6. **Message queue** — `showMessage()` replaces the current message immediately. A queue system would allow chained messages.
7. **Camera/viewport system** — Current code hardcodes centering. A proper camera system would support larger chambers.
8. **Sound effects** — No audio. Could add Web Audio API for jump, dash, glyph collect, push block sounds.

Each of these is a feature addition, not a refactor, and should be planned separately.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Accidental behavior change during reorganization | Medium | Use cut-and-paste (not rewrite); verify each function is identical after move |
| Line reference errors | Low | Use exact line numbers from current file; re-verify after each edit |
| Browser caching | Low | Hard refresh (Ctrl+Shift+R) after each edit |
| Push block physics break | Low | Test chamber (press T) has dedicated push block testing |
| Glyph collection break | Medium | Full playthrough test required |
| Render artifacts | Low | Visual inspection; no logic change in render |

**Overall Risk: LOW-MEDIUM.** The refactor is purely structural reorganization. No logic changes. Main risk is human error during copy-paste operations.

---

## File Change Summary

| File | Changes |
|------|---------|
| `golem.html` | Remove dead pushBlock() function; fix ch2/c2 redundancy; reorganize into 11 sections with delimiter comments |
| `chamber-template.md` | Remove BLOCK tile from legend and Python conversion dict |
| `docs/beyond-scope-simplifications.md` | NEW FILE — document out-of-scope improvements |
| `docs/refactor-execution-plan.md` | NEW FILE — this plan document |
