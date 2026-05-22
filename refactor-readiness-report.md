# Refactor Readiness Review: The Golem Awakens

## Current Architecture Summary

The codebase is a single HTML file (1727 lines, ~64 KB) organized into 11 numbered sections with delimiter comments. All JavaScript uses `function` declarations (function hoisting), so call order within the file does not matter.

| # | Section | Lines | Contents |
|---|---------|-------|----------|
| 1 | SETUP & CONSTANTS | 16-77 | Canvas init, tile type enums, all physics/timing/constants, static UI arrays, **plus helper functions** |
| -- | HELPER FUNCTIONS (unnumbered, inside Sec 1) | 78-110 | snapToTileX, endDash, land, easing functions, killAndRespawn |
| 2 | CHAMBER DATA | 112-378 | mkGrid(), 6 chamber IIFEs (Ch.0-4 + Test) |
| 3 | ENTITIES | 380-413 | P (player), PBlocks array, game state globals |
| 4 | INPUT | 415-439 | Key listeners, fresh(), shiftHeld(), 5 input abstraction functions |
| 5 | TILE HELPERS & COLLISION | 441-637 | Tile access, solidity checks, collision functions, **plus push-block physics helpers** |
| 6 | PUSH BLOCK SYSTEM | 639-747 | resetPushBlock, resolvePushBlockCollision, updatePushBlock |
| 7 | PARTICLE SYSTEM | 749-803 | IIFE: Particles object with spawn, shatter, update |
| 8 | GAME FLOW | 805-914 | Message queue, transitions, door/glyph checks, ending |
| 9 | UPDATE | 916-1158 | Main game loop function |
| -- | ANIM UPDATE (unnumbered, between 9 and 10) | 1160-1198 | Death/respawn animation state machine |
| 10 | RENDER | 1200-1689 | COLORS object, renderDeathRespawnAnimation, main render function |
| 11 | INIT & GAME LOOP | 1691-1727 | Initialization code, loop function, requestAnimationFrame |

**Key observation:** The 11-section structure is clean in principle, but several systems are split across sections, and the unnumbered helper functions and ANIM UPDATE lack section identity.

---

## Grouping Opportunities

### 1. Push Block Physics Scattered Across Two Sections

**What is scattered:** Push block physics/collision functions (`pushBlockHit`, `isRiding`, `resolveBlockX`, `moveBlockRiders`, `applyBlockVelocityX`, `resolveBlockY`, `activePushBlocks`, `checkPushBlockCrush`, `tileCollides`) live in Section 5 (TILE HELPERS & COLLISION, lines 534-637), while the push block orchestrator functions (`resetPushBlock`, `resolvePushBlockCollision`, `updatePushBlock`) live in Section 6 (lines 643-747).

**Where it lives now:**
- Section 5 (lines 534-637): 9 push-block-related functions mixed among tile collision helpers
- Section 6 (lines 643-747): 3 push-block orchestration functions

**Where it should go:** All push-block code should live together in a single section. Two options:
- (A) Move the Section 5 push-block helpers down into Section 6 (preferred)
- (B) Move Section 6 up into Section 5

**Why it matters:** Adding new push block behaviors (chain-push, different block types, slot mechanics) requires understanding code in two separate sections. Currently a developer adding a new block interaction would miss the physics helpers in Section 5. The separation also dilutes Section 5 — it's titled "TILE HELPERS & COLLISION" but nearly half its functions (lines 534-637, ~104 lines out of ~200) are entity-level push block physics, not tile collision.

**Impact:** Move 9 functions (~104 lines). No dependencies break since all functions are hoisted.

### 2. Helper Functions Buried Inside Section 1 (Constants)

**What is scattered:** Seven utility functions (snapToTileX, endDash, land, easeOutCubic, easeInOutCubic, easeOutBack, killAndRespawn) live at lines 78-110 inside the SETUP & CONSTANTS section, immediately after the constants but before the section delimiter ends.

**Where it lives now:** Section 1, lines 78-110 (marked as "HELPER FUNCTIONS")

**Where it should go:** A dedicated unnumbered section between SETUP & CONSTANTS and CHAMBER DATA, labeled `UTILITIES` or `SHARED HELPERS`

**Why it matters:** The current placement is misleading — a reader scanning Section 1 for constants will encounter function definitions. These are cross-cutting utilities used by multiple systems (collision, dash, animation, death). Giving them a visible section boundary makes the code more scannable and makes it clear these are shared abstractions, not part of setup.

**Impact:** Relabel with a proper section header. No code moves, just structural clarity.

### 3. Animation Code Split Between Three Locations

**What is scattered:** Easing functions (lines 99-102, in Section 1 helpers), `renderDeathRespawnAnimation` (lines 1213-1354, in Section 10 RENDER), and `updateAnim` (lines 1163-1198, between Sections 9 and 10).

**Where it lives now:**
- Section 1 helpers (lines 99-102): Easing functions
- Between Sections 9-10 (lines 1163-1198): `updateAnim` — death/respawn state machine
- Section 10 RENDER (lines 1213-1354): `renderDeathRespawnAnimation`

**Where it should go:** Group `updateAnim` with its section header (currently unnumbered) as "ANIMATION SYSTEM" between Sections 9 and 10. Keep `renderDeathRespawnAnimation` in RENDER since it's a drawing function. Keep easing functions in UTILITIES (see #3 above).

**Why it matters:** The `updateAnim` function currently has no section number/header, making it easy to miss. Adding a proper section header (e.g., "ANIMATION STATE MACHINE") clarifies that this is a distinct system parallel to the main update loop.

**Impact:** Add one section header. No code movement needed.

### 4. Message System Constants Separated from Message Functions

**What is scattered:** Message system constants (MSG_FADE_IN_FRAMES, MSG_FADE_OUT_FRAMES, MSG_MAX_QUEUE_DEPTH, MSG_CHARS_PER_FRAME, MSG_MIN_HOLD, MSG_MAX_HOLD, MSG_FOREVER_THRESHOLD) at lines 61-68, while message functions (calcDisplayDuration, showMessage) are in Section 8 at lines 810-825.

**Where it lives now:**
- Section 1 (lines 61-68): Constants
- Section 8 (lines 810-825): Functions

**Where it should go:** Move message constants to the top of Section 8, right before the message functions.

**Why it matters:** All other subsystem constants are co-located with their functions (dash constants near dash code, push block constants near push block code, particle colors near particle code). The message constants are the only exception. Keeping them together makes it easier to tune message behavior.

**Impact:** Move 8 constant declarations (~8 lines) from Section 1 to Section 8.

### 5. Game State Globals Mixed with Entity Definitions

**What is scattered:** Player state (`P`), push block entities (`PBlocks`), and general game state globals (`glyphsCollected`, `collectedGlyphs`, `gameState`, `screenFade`, `screenAlpha`, `messageQueue`, `portalLockMsg`, `particles`, `testChamberSrc`, `_testMode`, `_c`, `_transitionTarget`, `animState`, `animFrame`, `ANIM_TOTAL_FRAMES`) are all in Section 3.

**Where it lives now:** Section 3, lines 384-413

**Where it should go:** Split into subsections within Section 3:
- "Player state" (P) — already has this subsection marker
- "Push block entities" (PBlocks) — already has this subsection marker
- "Game state" (everything else) — has a marker but could be clearer

**Why it matters:** The current grouping is actually reasonable. The subsection markers (`/* ── Player state ── */`, etc.) are present and clear. Minor improvement: group related globals together more tightly — e.g., put `messageQueue` with message-related globals, `screenFade`/`screenAlpha` with transition-related globals, `particles` near the particle system.

**Impact:** Low. Mostly a cosmetic reordering within Section 3.

---

## Section Reordering Suggestions

The current section order roughly follows a dependency graph (constants -> data -> entities -> input -> collision -> systems -> game flow -> update -> render -> init). This is sound. However, the following reorderings would improve logical flow:

### Proposed: Move Push Block System (Section 6) Immediately After Tile Helpers (Section 5)

Currently Section 5 contains some push block code (lines 534-637) and Section 6 contains the rest. Once the grouping fix (#1) is applied, all push block code will be in one place. The section order should be:

1. SETUP & CONSTANTS
2. UTILITIES (extracted from Section 1 helpers)
3. CHAMBER DATA
4. ENTITIES
5. INPUT
6. TILE SYSTEM (renamed from "TILE HELPERS & COLLISION")
7. PUSH BLOCK SYSTEM (consolidated)
8. PARTICLE SYSTEM
9. GAME FLOW
10. ANIMATION STATE MACHINE (currently unnumbered, between 9-10)
11. UPDATE
12. RENDER
13. INIT & GAME LOOP

The key change is making ANIM UPDATE a numbered section and ensuring Push Block is a clean, self-contained section.

### Proposed: Move Message Constants from Section 1 to Section 8

This doesn't change section order but improves within-section coherence. Section 8 would then contain all message-related code: constants, `calcDisplayDuration`, `showMessage`, and the message queue processing in `update` and `updateAnim`.

---

## Extraction Candidates

### 1. `TileSystem` Object (IIFE or namespace)

**Pattern:** `{name}` containing related functions/properties, currently spread across Section 5

**Functions to group:**
- `getTile(ch, x, y)` — line 445
- `setTile(ch, x, y, v)` — line 450
- `_getTile(x, y)` — line 465 (fast access)
- `solid(t)` — line 471
- `platSolid(t, prevFeet, gy)` — line 475
- `tileCollidesRect(ch, gx1, gy1, gx2, gy2, opts)` — line 483
- `collides(gx1, gy1, gx2, gy2, ch, prevY, curY)` — line 495
- `collidesNoPlat(gx1, gy1, gx2, gy2, ch)` — line 499
- `collidesDash(gx1, gy1, gx2, gy2, ch, prevY, curY)` — line 504
- `inPit()` — line 515
- `aabb(ax, ay, aw, ah, bx, by, bw, bh)` — line 530
- `tileCollides(ch, x, y, w, h)` — line 630

**Why:** The tile system has 12 functions handling different aspects of tile interaction (access, solidity, collision, pit detection, AABB). Grouping them under a `TileSystem` namespace (or IIFE returning an object, similar to `Particles`) would make it clear which functions are tile-related. The `aabb` function is a general utility and could stay in UTILITIES.

**Effort:** Medium. Requires updating all call sites (used extensively throughout UPDATE and RENDER).

### 2. `PushBlocks` Object (IIFE — matching the `Particles` pattern)

**Pattern:** Object containing all push-block functions, currently spread across Sections 5 and 6

**Functions to group:**
- `resetPushBlock()` — line 643
- `resolvePushBlockCollision()` — line 656
- `updatePushBlock()` — line 703
- `pushBlockHit(x, y, w, h, skip)` — line 535
- `isRiding(ob, base)` — line 543
- `resolveBlockX(ch, pb, dx)` — line 549
- `moveBlockRiders(ch, pb, dx)` — line 565
- `applyBlockVelocityX(ch, pb)` — line 575
- `resolveBlockY(ch, pb)` — line 583
- `activePushBlocks()` — line 606
- `checkPushBlockCrush()` — line 612

**Why:** The `Particles` system already uses the IIFE pattern (`const Particles = (function(){ ... })()`). Push blocks are equally complex (11 functions) and would benefit from the same encapsulation. This would also consolidate the scattered code from Sections 5 and 6. The `PBlocks` global array would become internal to the module.

**Effort:** Medium-High. Requires updating call sites in UPDATE (lines 1067, 1070, 1094, 1106) and `_doTransition` (line 837) and `killAndRespawn` (line 1149).

### 3. `GameFlow` Object (optional — future possibility)

**Pattern:** Object containing game flow functions, currently in Section 8

**Functions to group:**
- `calcDisplayDuration(text, providedDur)` — line 810
- `showMessage(txt, dur)` — line 815
- `_doTransition(toChamber)` — line 828
- `transition(toChamber)` — line 839
- `checkDoors()` — line 847
- `checkGlyphs()` — line 884
- `transitionEnding()` — line 906

**Why:** These functions handle all progression logic (doors, glyphs, transitions, messages). Grouping them makes it clear which code manages game flow vs. physics vs. rendering. This would also provide a natural home for the message constants.

**Effort:** Medium. These functions are called from UPDATE (lines 1152-1153) and other places.

### 4. `GlyphAbilities` Object

**Pattern:** Object mapping glyph numbers to ability unlocks and messages

**Current state:** Scattered in `checkGlyphs()` at lines 898-901 as an if/else chain:
```javascript
if(glyphsCollected===1){ P.maxJumps=2; showMessage("Knowledge lifts me.",120); }
else if(glyphsCollected===2){ P.canDash=true; showMessage("Speed courses through me.",120); }
else if(glyphsCollected===3){ P.canPush=true; showMessage("Strength returns.",120); }
else if(glyphsCollected===4){ P.canBreak=true; showMessage("Clay becomes Wisdom.",120); }
```

**Why:** Adding a new ability requires modifying inline code in the game flow function. Extracting to a data-driven structure (array of `{glyph, ability, message}` objects) would make adding abilities as simple as appending to an array. This pairs with the `ABILITIES` UI array at line 71.

**Effort:** Low. Small, self-contained change in one function.

---

## Naming and Convention Consistency

### 1. Section Numbering vs. Unnumbered Sections

**Issue:** Three code blocks lack section numbers: HELPER FUNCTIONS (lines 78-110), ANIM UPDATE (lines 1160-1198), and the `COLORS` object placement within Section 10.

**Fix:** Assign section numbers to make the architecture fully 13-section (or renumber to integrate).

### 2. Tile Type Value Gap

**Issue:** `CRACKED=7` creates a gap (BLOCK=6 was removed). Noted in Project-Reference.md. This is fine for stability but worth documenting if new tile types are added.

**Recommendation:** When adding new tiles, document the next available value (6 if reusing, or 12+).

### 3. Inconsistent Comment Prefixes

**Issue:** Helper functions use `/* A3: ... */`, `/* A4: ... */`, etc. (letter-number), while sections use `/* ═══ 1. ... ═══ */`. The A-prefix comments appear to be internal revision markers from a previous refactoring pass and may be stale.

**Fix:** Replace with descriptive comments matching the section style, or remove the A-prefixed tags.

### 4. Mixed Naming for Push Block Constants

**Issue:** Constants use `PB_` prefix (PB_GRAVITY, PB_TERMINAL_VEL, PB_FRICTION, PB_STOP_THRESH) while the entity array is named `PBlocks` (not `PBs` or `P_Blocks`). The player object is `P` (consistent with PB abbreviation) but `PBlocks` breaks the pattern.

**Recommendation:** Either rename to `PBs` for consistency or rename constants to `PUSH_BLOCK_` for clarity.

### 5. Inline vs. Constant Particle Colors

**Issue:** Two particle colors are extracted to constants (DASH_EXEC_PARTICLE_COLOR, DASH_CHARGE_PARTICLE_COLOR at lines 38-40), while other particle colors are inline strings (e.g., `'#8a7d6b'`, `'#d4a84b'`, `'#f0d060'`, `'rgba(220,120,255,0.6)'` throughout UPDATE and RENDER).

**Recommendation:** Extract recurring color strings to a `PARTICLE_COLORS` object or similar, especially those used in multiple locations:
- `'rgba(220,120,255,0.6)'` — dash execution burst (line 996)
- `'#8a7d6b'` — jump particles (lines 1122, 1130, 1228, 1275)
- `'#d4a84b'` — double jump particles (line 1136)
- `'#f0d060'` — glyph collection particles (line 897)
- `'#c8a84e'` — glyph color (COLORS.glyph)

### 6. `collectedGlyphs` Dual Meaning

**Issue:** `collectedGlyphs` (line 400) is a per-chamber boolean array, while `glyphsCollected` (line 399) is a total count. The naming is close enough to cause confusion.

**Recommendation:** Rename to `chamberGlyphCollected` (array) and `totalGlyphsCollected` (count) for clarity.

### 7. `solidTiles` Terminology

**Issue:** `c.solidTiles` (built at line 1706-1713) includes ALL non-AIR tiles (including GLYPH, PIT, DOOR_D, etc.), not just solid tiles. The name suggests only solid tiles are included.

**Recommendation:** Rename to `c.renderTiles` or `c.nonAirTiles` since it's used for the sparse render loop.

---

## Recommended Refactoring Plan

### Phase 1: Structural Clarification (No behavioral changes)

**Step 1.1:** Give HELPER FUNCTIONS (lines 78-110) a proper section header.
- Add `/* ══════════════════════════════════════════════════ / 1.5. UTILITIES (shared helper functions) / ══════════════════════════════════════════════════ */`
- Remove stale A3/A4/A5/A6/A7 prefixes from comments.
- **Risk:** None. Pure structural change.

**Step 1.2:** Give ANIM UPDATE (lines 1160-1198) a proper section header.
- Add section header between Sections 9 and 10: `/* ═══ 9.5. ANIMATION STATE MACHINE ═══ */`
- **Risk:** None. Pure structural change.

**Step 1.3:** Move message constants (lines 61-68) from Section 1 to the top of Section 8.
- **Risk:** None. Constants are hoisted; no dependency changes.

**Step 1.4:** Add subsection headers in Section 3 to clarify game state grouping.
- Group transition-related globals (`screenFade`, `screenAlpha`, `_transitionTarget`) together.
- Group message-related globals (`messageQueue`, `portalLockMsg`) together.
- Group animation globals (`animState`, `animFrame`, `ANIM_TOTAL_FRAMES`) together.
- **Risk:** None. Pure reordering of variable declarations.

### Phase 2: Code Consolidation (Group related code)

**Step 2.1:** Move push-block physics functions from Section 5 into Section 6.
- Move lines 534-637 (pushBlockHit through checkPushBlockCrush) to Section 6.
- Update section title to "PUSH BLOCK SYSTEM (physics + orchestration)".
- Remove `tileCollides(ch, x, y, w, h)` from this move (it's a general tile collision function, not push-block specific).
- **Risk:** Low. Functions are hoisted. No call-site changes needed.

**Step 2.2:** Rename Section 5 to "TILE SYSTEM" and update internal comments.
- After removing push-block code, Section 5 contains pure tile/collision logic.
- Rename `solidTiles` -> `renderTiles` in lines 1706-1713 and all call sites (line 1373, line 456).
- **Risk:** Medium. `solidTiles` is referenced in 3 places (lines 456, 1373, 1706-1711). All must be updated.

### Phase 3: Data-Driven Refinements (Improve extensibility)

**Step 3.1:** Extract glyph ability definitions into a data structure.
- Create `const GLYPH_ABILITIES = [{num:1, set:()=>{P.maxJumps=2}, msg:"Knowledge lifts me."}, ...]`
- Replace the if/else chain in `checkGlyphs()` (lines 898-901) with a lookup.
- **Risk:** Low. Self-contained change in one function. Makes adding Glyph 5+ trivial.

**Step 3.2:** Extract recurring particle colors to constants.
- Add `PARTICLE_COLORS = { jump:'#8a7d6b', doubleJump:'#d4a84b', glyph:'#f0d06b', dashBurst:'rgba(220,120,255,0.6)', death:'#8a7d6b', reform:'#8a7d6b' }`
- Replace inline strings with references.
- **Risk:** Low. String replacement, no logic change.

### Phase 4: Module Extraction (Optional — higher impact)

**Step 4.1:** Wrap push block system in an IIFE (matching the `Particles` pattern).
- `const PushBlocks = (function(){ const blocks = []; ... return { reset, update, resolveCollision, checkCrush }; })()`
- **Risk:** Medium-High. Multiple call sites need updating (UPDATE lines 1067/1070/1094/1106, `_doTransition` line 837, `killAndRespawn` line 1149). The `PBlocks` array is accessed directly in several places.

**Step 4.2:** Wrap tile system in a namespace object.
- `const Tiles = { get(ch,x,y){...}, set(ch,x,y,v){...}, solid(t){...}, collidesRect(...){...}, ... }`
- **Risk:** Medium. Tile functions are called throughout UPDATE and RENDER. Every call site changes from `getTile(...)` to `Tiles.get(...)`.

---

## Risks

### High-Risk Items

1. **Module extraction (Phase 4):** Changing from `function` declarations to IIFE-returning objects requires updating all call sites. If even one call site is missed, the game breaks silently (ReferenceError at runtime). Recommendation: Use search-and-replace systematically, then run the game through a full playthrough.

2. **Renaming `solidTiles` to `renderTiles`:** This property is set in INIT (line 1706) and read in `setTile` (line 456) and `render` (line 1373). A missed reference causes silent rendering failures.

3. **Push block physics movement (Step 2.1):** While function hoisting protects against call order issues, the functions reference `PBlocks` and `P` which must remain global (or be passed in). Ensure no implicit dependencies on execution order are broken.

### Medium-Risk Items

4. **Glyph ability data extraction (Step 3.1):** The `checkGlyphs` function also checks `if(glyphsCollected!==ch) continue;` — ensure the data-driven version preserves the chamber-sequence gating logic.

5. **Constant relocation (Step 1.3):** Message constants are referenced in `updateAnim` (lines 1169-1174) via the `MSG_*` names. Moving them is safe since they are `const` declarations (hoisted), but verify no runtime scope issues.

### Low-Risk Items

6. **Section header additions (Steps 1.1, 1.2):** Purely cosmetic. Zero behavioral change.

7. **Game state variable reordering (Step 1.4):** All are `let` declarations at module scope. Reordering has no effect on behavior.

8. **Comment prefix cleanup (Step 1.1):** Only affects comments.

### General Mitigations

- **Function hoisting protects call order:** All functions use `function` declarations, so they are hoisted to module scope. Reordering sections does not break call dependencies.
- **Single global scope:** Everything shares the same scope. Moving code between sections changes nothing about variable visibility.
- **Test chamber coverage:** The test chamber (Ch.T, accessed via `T`) unlocks all abilities. After any refactoring, play through the test chamber to verify all mechanics work.
- **Git version control:** Each phase should be a separate commit so it can be rolled back independently.
- **Browser console:** Run with DevTools open to catch any ReferenceError immediately.
