# Master Improvement Plan: The Golem Awakens

> **Status: COMPLETED** — All 8 slices implemented and validated (May 22, 2026).
> Results: 1727 -> 1716 lines (net -11 lines), 0 browser console errors, game loads and runs correctly.
> Source reports (code-review-report.md, optimization-opportunities-report.md, refactor-readiness-report.md, left-out-findings.md) removed after execution.
> This file kept as reference for the completed refactoring work.

## Executive Summary

Three independent review reports were produced for `golem.html` (1727 lines, ~64 KB): a code review (bugs and improvements), a refactor readiness report (grouping and organization), and an optimization opportunities report (dead code, duplication, performance). All three agree on the core assessment: the codebase is well-structured for a single-file game, with clean sectioning, well-tuned physics, and a sophisticated push-block system. No critical bugs that break core functionality were found.

The findings span five categories: (1) two latent correctness issues (prevKeys unbounded growth, return vs continue in push-block collision), (2) dead code and duplication (2 unused easing functions, _testMode always false, 5 dash reset sites, duplicated message queue logic), (3) UI/gameplay redundancies (duplicate "I awaken..." overlay, duplicate dash charge indicator, dead in-slot checking code), (4) structural clarity (unnumbered helper sections, scattered push-block code, separated message constants), and (5) future-proofing (data-driven glyph system, tile property map, particle color constants).

This plan consolidates all findings, deduplicates across reports, and splits the work into 8 independently testable slices ordered by risk (safest first). Total expected line savings from quick wins: ~62 lines (includes 3 UI/gameplay cleanup items). No slice modifies level design data or changes gameplay behavior. Each slice includes explicit validation gates so the game remains fully playable after every step.

---

## Synthesized Findings

All findings are deduplicated. Cross-report citations use these abbreviations:
- **CR** = code-review-report.md
- **REF** = refactor-readiness-report.md
- **OPT** = optimization-opportunities-report.md

### Critical Bugs

*No critical bugs found. All core systems (main loop, input, collision, state transitions, push-block physics) function correctly.* — CR, REF, OPT (all agree)

### Important Fixes

| # | Finding | Lines | Reports | Severity |
|---|---------|-------|---------|----------|
| F1 | **prevKeys dictionary can grow unbounded** — `for...in` copy + delete loop runs every frame in both `update()` and `updateAnim()`. Keys accumulate from any keypress and are only deleted when released. Over a long session this degrades per-frame performance. | 1156-1157, 1196-1197 | CR #1, OPT §Performance #1, OPT §Redundancy #2 | Low (latent) |
| F2 | **`return` instead of `continue` in push-block collision loop** — line 695 in `resolvePushBlockCollision()` exits the function when `isOnTop` is true on the first matching block, so remaining blocks are never checked. | 695 | CR #2 | Low (blocks don't overlap in current levels) |
| F3 | **`killAndRespawn` has unused `onGround` parameter** — parameter is never read in the function body; all callers pass `false`. | 105, 624, 1148 | CR #3 | None (misleading API) |
| F4 | **rAF never cancelled on game end** — when `gameState` becomes `'ending'`, the loop still requests new animation frames every cycle. `update()` returns early but `render()` still executes. | 1722, 1723 | CR #4 | Low (wastes CPU on credits screen) |


### UI / Gameplay Cleanups

| # | Finding | Lines | Reports | Type |
|---|---------|-------|---------|------|
| U1 | **Duplicate "I awaken..." message in Chamber 0** — `X.fillText('I awaken...', W/2, 60)` at line 1687 renders a persistent smaller-font overlay during the entire first chamber (condition: `ch===0 && glyphsCollected===0 && messageQueue.length===0`). The proper `showMessage('I awaken...', 150)` at line 1719 already handles this via the message queue with fade in/out. The X.fillText version is redundant. | 1685-1688 | New finding | Dead render code |
| U2 | **Duplicate dash charge indicator** — Two indicators exist: (a) ring indicator centered on golem (lines 1505-1560) and (b) HUD bar indicator in top-left corner (lines 1616-1631). The centered ring indicator is preferred; the HUD bar is redundant. | 1505-1560, 1616-1631 | New finding | Dead render code |
| U3 | **Push block "in slot" slot-checking code is dead** — Lines 726-736 in `updatePushBlock()` check `if(c.pushSlot)` and lock a block into place. No chamber in the current codebase defines `pushSlot`, so this code is never triggered. The `inSlot` property on push block objects (used in 7+ places as a guard: `activePushBlocks`, `checkPushBlockCrush`, `resolvePushBlockCollision`, render) should be preserved for future use, but the slot-checking logic in Phase D of `updatePushBlock` can be removed. | 726-736 | New finding | Dead game logic |


### Code Cleanup (Dead Code, Duplication)

| # | Finding | Lines | Reports | Savings |
|---|---------|-------|---------|---------|
| C1 | **`easeInOutCubic` is dead code** — defined but never called anywhere. | 101 | OPT §Dead Code #1 | 1 line |
| C2 | **`easeOutBack` is dead code** — defined but never called anywhere. | 102 | OPT §Dead Code #2 | 1 line |
| C3 | **`_testMode` is always false** — declared at line 408, checked at lines 841 and 908, never set to true in the file. Dead code paths in both `transition()` and `transitionEnding()`. | 408, 841, 908 | OPT §Dead Code #5 | ~6 lines |
| C4 | **Message queue advancement duplicated** — identical logic in `update()` (line 953) and `updateAnim()` (lines 1166-1175). | 953, 1166-1175 | OPT §Redundancy #1 | ~8 lines |
| C5 | **prevKeys copy duplicated** — identical 2-line pattern in `update()` and `updateAnim()`. (Combined with F1 fix.) | 1156-1157, 1196-1197 | OPT §Redundancy #2 | ~4 lines |
| C6 | **portalLockMsg decrement duplicated** — `if(portalLockMsg>0) portalLockMsg--;` in both `update()` and `updateAnim()`. | 954, 1177 | OPT §Redundancy #3 | ~2 lines |
| C7 | **Dash state reset scattered across 5 sites** with inconsistent fields: `endDash()` (line 91), `killAndRespawn` (line 107), `_doTransition` (line 834), pit death (line 1147), respawn->idle (line 1191). | 91, 107, 834, 1147, 1191 | OPT §Logic Simplification #2 | ~8 lines |
| C8 | **Player respawn reset duplicated** — identical line at `dying->respawning` (line 1183) and `respawning->idle` (line 1189). | 1183, 1189 | OPT §Logic Simplification #1 | ~5 lines |
| C9 | **setTile maintains solidTiles redundantly** — solidTiles is built once at init from the grid and the render loop reads from the actual grid. The maintenance code (lines 455-460) is safe to remove since the grid is the source of truth. | 455-460 | OPT §Dead Code #4 | ~6 lines |
| C10 | **Player center + grid conversion duplicated** — 3 places compute `px=P.x+P.w/2, py=P.y+P.h/2; gx=Math.floor(px/T), gy=Math.floor(py/T)`. | 516-517, 849-850, 887-888 | OPT §Redundancy #5 | ~3 lines |
| C11 | **X-collision resolution tail duplication** — `snapToTileX(gx1, gx2, prevX); P.vx=0;` appears in both the dash branch (line 1056) and the normal branch (line 1060). | 1049-1062 | OPT §Logic Simplification #5 | ~3 lines |

### Structural Improvements (Grouping, Organization)

| # | Finding | Lines | Reports | Effort |
|---|---------|-------|---------|--------|
| S1 | **Helper functions lack proper section header** — 7 utility functions (lines 78-110) sit inside Section 1's delimiter block with only a `═══` header. Should be a proper section (e.g., "1.5. UTILITIES"). | 78-110 | REF §Grouping #2 | None |
| S2 | **ANIM UPDATE lacks section header** — `updateAnim()` (lines 1160-1198) is unnumbered and sits between Sections 9 and 10. | 1160-1198 | REF §Grouping #3, §Naming #1 | None |
| S3 | **Message constants separated from message functions** — MSG_* constants at lines 61-68 (Section 1) while `calcDisplayDuration`/`showMessage` are at lines 810-825 (Section 8). | 61-68, 810-825 | REF §Grouping #4 | Low |
| S4 | **Push block physics scattered across Sections 5 and 6** — 9 push-block functions live in Section 5 (lines 534-637: `pushBlockHit`, `isRiding`, `resolveBlockX`, `moveBlockRiders`, `applyBlockVelocityX`, `resolveBlockY`, `activePushBlocks`, `checkPushBlockCrush`, `tileCollides`), while 3 orchestration functions live in Section 6 (lines 643-747: `resetPushBlock`, `resolvePushBlockCollision`, `updatePushBlock`). | 534-637, 639-747 | REF §Grouping #1 | Low |
| S5 | **Game state globals could be better grouped** — transition, message, and animation globals all mixed in Section 3. | 398-413 | REF §Grouping #5 | None |
| S6 | **Stale A-prefix comment prefixes** — internal revision markers (A3, A4, A5, A6, A7) in comments may be stale. | 82, 89, 94, 104, 433 | REF §Naming #3 | None |
| S7 | **Particle colors not extracted to constants** — inline strings like `'#8a7d6b'` (lines 1122, 1130, 1228), `'#d4a84b'` (line 1136), `'#f0d060'` (line 897) used in multiple locations. | Various | REF §Naming #5, OPT | Low |

### Optimization Opportunities

| # | Finding | Lines | Reports | Savings |
|---|---------|-------|---------|---------|
| O1 | **Jump logic could be factored** — 4 branches with repeated `P.jumpBuffer=0` and `Particles.spawn()`. | 1112-1143 | OPT §Logic Simplification #4 | ~12 lines |
| O2 | **Neighbor tile scan pattern** — `inPit()`, `checkDoors()`, `checkGlyphs()` all iterate a 3x3 neighborhood. | 519-525, 851-881, 889-902 | OPT §Redundancy #6 | Future |
| O3 | **Collision functions allocate options objects per frame** — `collides()` creates `{includePlatforms:true, prevY, curY}` every frame. | 495-497 | OPT §Performance #3 | Minor |
| O4 | **Dash charge ratio computed twice in render** — `P.dashCharge / DASH_CHARGE_MAX` in two places. | ~1508, ~1618 | OPT §Performance #4 | Trivial |

### Future-Proofing

| # | Finding | Lines | Reports | Effort |
|---|---------|-------|---------|--------|
| FP1 | **Data-driven glyph/ability system** — replace hardcoded if/else chain (lines 898-901) and sync with ABILITIES array (lines 71-74) using a single `GLYPH_EFFECTS` data structure. | 71-74, 898-901 | OPT §Future-Proofing #1, OPT §Redundancy #4, REF §Extraction #4 | Low |
| FP2 | **Tile property map** — replace `solid()` if/chain (line 471) with a `TILE_PROPS` lookup for extensibility. | 471 | OPT §Future-Proofing #3 | Low |
| FP3 | **Push block slot standardization** — normalize chambers to always use `pushSpawns`/`pushSlots` arrays. | 647, 726-737 | OPT §Future-Proofing #4 | Low |
| FP4 | **Chamber boundary helper** — extract `drawBorder(g, w, h, gaps)` to reduce boilerplate in chamber IIFEs. | Various chamber data | OPT §Future-Proofing #2 | Medium |

---

## Implementation Plan

### Slice 1: Remove Dead Code

- **Items included:**
  - C1: Remove `easeInOutCubic` (line 101) — [OPT]
  - C2: Remove `easeOutBack` (line 102) — [OPT]
  - C3: Remove `_testMode` variable (line 408) and dead branches in `transition()` (line 841) and `transitionEnding()` (line 908) — [OPT]
- **Risk level:** None — pure dead code removal, no behavioral impact
- **Expected line savings:** ~9 lines net (2 easing functions + 1 variable declaration + 2 dead branches + cleanup)
- **Files changed:** golem.html
- **Changes summary:** Delete lines 101-102 (unused easing functions). Remove `let _testMode = false;` at line 408. Remove `if(_testMode){_doTransition(toChamber); return;}` from `transition()` at line 841, inlining the non-test-mode path. Remove `if(_testMode){...}` branch from `transitionEnding()` at line 908, keeping only the normal path. Update comment on line 100 (easing functions header) to singular since only `easeOutCubic` remains.
- **Validation gate:** Game loads, all 5 chambers playable, transitions work normally, test chamber accessible via T key, game ending sequence works
- **Testing checklist:**
  - [ ] Game loads without console errors
  - [ ] Play through all 5 chambers (ch0-ch4)
  - [ ] Press T to enter test chamber, press T to return
  - [ ] Reach end portal — ending screen displays message correctly
  - [ ] Death/respawn animation uses easeOutCubic (should look identical)
  - [ ] No ReferenceError on `_testMode` anywhere

**Documentation impact:** None. Dead code was not documented in any external file.

---

### Slice 2: Section Headers and Comment Cleanup

- **Items included:**
  - S1: Give helper functions (lines 78-110) a proper numbered section header — [REF]
  - S2: Give ANIM UPDATE (lines 1160-1198) a proper numbered section header — [REF]
  - S6: Clean up stale A3/A4/A5/A6/A7 comment prefixes — [REF]
- **Risk level:** None — comments and section headers only
- **Expected line savings:** ~0 lines (adds 2 header blocks, removes 5 short prefixes)
- **Files changed:** golem.html
- **Changes summary:** Replace the existing `═══ HELPER FUNCTIONS ═══` block at line 78 with `═══ 1.5. UTILITIES (shared helper functions) ═══`. Replace the ANIM UPDATE header at line 1160 with `═══ 9.5. ANIMATION STATE MACHINE ═══`. Renumber subsequent sections 10->11, 11->12 for consistency. Remove A3, A4, A5, A6, A7, A1 prefixes from inline comments (lines 82, 89, 94, 104, 433, and any A1/A2 references) replacing with descriptive text or removing entirely.
- **Validation gate:** Game loads, no JS syntax errors from comment changes
- **Testing checklist:**
  - [ ] Game loads without errors
  - [ ] Browser console shows no errors
  - [ ] Visual inspection of file: section numbering reads 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 9.5, 10, 11

**Documentation impact:** docs/Project-Reference.md section map (line 14-25) should be updated to reflect new section numbers (1.5, 9.5, renumbered 10/11).

---

### Slice 3: Fix prevKeys and Extract Duplicated Timers

- **Items included:**
  - F1: Fix prevKeys unbounded growth — replace `for...in` copy+delete with `prevKeys = {...keys}` — [CR #1, OPT §Performance #1, OPT §Redundancy #2]
  - C4: Extract `advanceMessageQueue()` helper from duplicated logic — [OPT §Redundancy #1]
  - C6: Include `portalLockMsg--` in shared timer helper — [OPT §Redundancy #3]
- **Risk level:** Low — `prevKeys` fix changes copy semantics but `fresh()` only reads keys currently in `keys`, so spread copy is equivalent. Message queue extraction is pure refactoring.
- **Expected line savings:** ~14 lines net (2x4 lines of prevKeys -> 2x1 line = 6 saved; 1 line message queue in update() + 10 lines in updateAnim() -> 1 helper + 2 calls = ~8 saved)
- **Files changed:** golem.html
- **Changes summary:**
  1. Create `function syncPrevKeys() { prevKeys = {...keys}; }` in UTILITIES section.
  2. Replace lines 1156-1157 in `update()` with `syncPrevKeys();`.
  3. Replace lines 1196-1197 in `updateAnim()` with `syncPrevKeys();`.
  4. Create `function advanceTimers() { /* message queue advancement + portalLockMsg */ }` in UTILITIES section.
  5. Replace line 953 + line 954 in `update()` with `advanceTimers();`.
  6. Replace lines 1166-1177 in `updateAnim()` with `advanceTimers();`.
- **Validation gate:** Game loads, message display works in both normal and death/respawn states, portal lock message cooldown works, input still responsive
- **Testing checklist:**
  - [ ] Game loads without errors
  - [ ] "I awaken..." message displays and fades correctly
  - [ ] During death/respawn animation, "Clay reforms..." message displays
  - [ ] "The seal demands Knowledge..." lock message appears once then cools down
  - [ ] Movement and jumping work (input not broken by prevKeys change)
  - [ ] Dash charge indicator works
  - [ ] Play through chamber 1 (tests message display during normal gameplay)

**Documentation impact:** None. Internal function naming only.

---

### Slice 4: API Cleanup — killAndRespawn and rAF Cancel

- **Items included:**
  - F3: Remove unused `onGround` parameter from `killAndRespawn` — [CR #3]
  - F4: Cancel rAF when game ends — [CR #4]
- **Risk level:** Low — parameter removal is safe (never used); rAF cancel only affects ending state
- **Expected line savings:** ~2 lines (parameter removal) + ~1 line (rAF guard)
- **Files changed:** golem.html
- **Changes summary:**
  1. Change `function killAndRespawn(onGround, msg, duration)` (line 105) to `function killAndRespawn(msg, duration)`.
  2. Update caller at line 624: `killAndRespawn(false, ...)` -> `killAndRespawn(...)`.
  3. Update caller at line 1022: `killAndRespawn(true, ...)` -> `killAndRespawn(...)`.
  4. Update caller at line 1148: `killAndRespawn(false, ...)` -> `killAndRespawn(...)`.
  5. Wrap game loop with rAF cancellation: declare `let animFrameId;` at top, change `loop()` to check `gameState==='ending'` and stop requesting frames, render ending frame once.
- **Validation gate:** Game loads, all death types work (pit, crush, magical wall), ending screen displays
- **Testing checklist:**
  - [ ] Game loads without errors
  - [ ] Fall into pit — death message "The void claims clay..." displays, respawn works
  - [ ] Get crushed by push block — death message displays, respawn works
  - [ ] Dash into magical wall — death message displays, respawn works
  - [ ] Complete game — ending screen shows message, CPU usage drops (rAF stopped)
  - [ ] DevTools Performance tab: confirm no frames requested after ending

**Documentation impact:** None. API change is internal only.

---

### Slice 5: Consolidate Dash Reset and Player Reset Helpers

- **Items included:**
  - C7: Consolidate 5 dash reset sites into `fullDashReset()` and `cancelDash()` helpers — [OPT §Logic Simplification #2]
  - C8: Extract `resetPlayerToRespawn()` for duplicated respawn reset lines — [OPT §Logic Simplification #1]
- **Risk level:** Low — each call site is replaced with equivalent behavior wrapped in a named function
- **Expected line savings:** ~13 lines net (5 dash sites consolidated into 2 helpers + 2 respawn lines into 1 helper)
- **Files changed:** golem.html
- **Changes summary:**
  1. Add to UTILITIES section:
     ```js
     function fullDashReset() {
       P.dashing=false; P.dashTimer=0; P.dashCooldown=0; P.dashPhase=false; P.dashCharge=0;
     }
     function cancelDash() {
       P.dashing=false; P.dashTimer=0;
     }
     ```
  2. Replace line 91 (`endDash()`) body: `P.dashing=false; P.dashTimer=0; P.dashCooldown=DASH_COOLDOWN; P.dashPhase=false;` (note: endDash sets cooldown to DASH_COOLDOWN, not 0 — keep endDash as-is since it's the normal end, not a reset).
  3. Replace line 107 (`killAndRespawn`): `cancelDash();`
  4. Replace line 834 (`_doTransition`): `fullDashReset();`
  5. Replace line 1147 (pit death): `cancelDash();`
  6. Replace lines 1191 (respawn->idle): `fullDashReset();`
  7. Add to UTILITIES section:
     ```js
     function resetPlayerToRespawn() {
       P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0; P.jumps=0; P.dashCharge=0;
     }
     ```
  8. Replace lines 1183 and 1189 with `resetPlayerToRespawn();`.
- **Validation gate:** Dash works normally (charge, execute, cooldown), death resets state correctly, transitions reset state correctly
- **Testing checklist:**
  - [ ] Dash charges and executes correctly
  - [ ] Dash cooldown prevents immediate re-dash
  - [ ] Death resets dash state (cannot dash immediately after respawning)
  - [ ] Chamber transition resets dash state
  - [ ] Respawn animation restores player position and state
  - [ ] Push block crush death works (tests cancelDash in killAndRespawn)

**Documentation impact:** None. Internal function naming only.

---

### Slice 6: Push Block Defensive Fix and playerGridPos Helper

- **Items included:**
  - F2: Change `return` to `continue` in `resolvePushBlockCollision` (line 695) — [CR #2]
  - C10: Extract `playerGridPos()` helper from 3 duplicated sites — [OPT §Redundancy #5]
  - C11: Simplify X-collision resolution tail — [OPT §Logic Simplification #5]
- **Risk level:** Low — `return`->`continue` is defensive (no behavioral change in current levels); helper extraction is pure refactoring
- **Expected line savings:** ~6 lines net (playerGridPos: ~3 lines; X-collision simplification: ~3 lines)
- **Files changed:** golem.html
- **Changes summary:**
  1. Line 695: Change `if(isOnTop) return;` to `if(isOnTop) continue;` with updated comment.
  2. Add `playerGridPos()` to UTILITIES:
     ```js
     function playerGridPos() {
       return { gx: Math.floor((P.x+P.w/2)/T), gy: Math.floor((P.y+P.h/2)/T) };
     }
     ```
  3. Replace lines 516-517 in `inPit()`, lines 849-850 in `checkDoors()`, lines 887-888 in `checkGlyphs()` with `const {gx, gy} = playerGridPos();`.
  4. Simplify X-collision resolution (lines 1043-1064): extract `snapToTileX + P.vx=0` to a common path using a `crashed` flag.
- **Validation gate:** All collision and game flow checks work correctly
- **Testing checklist:**
  - [ ] Pit death triggers correctly (inPit uses playerGridPos)
  - [ ] Door detection works (checkDoors uses playerGridPos)
  - [ ] Glyph collection works (checkGlyphs uses playerGridPos)
  - [ ] Push block collision: player can walk past block without getting stuck (tests continue vs return)
  - [ ] X-collision: player snaps to tile wall correctly in normal movement
  - [ ] Dash X-collision: player breaks cracked tile or snaps to wall correctly

**Documentation impact:** None. Internal function naming only.

---

### Slice 7: Move Message Constants and Simplify setTile

- **Items included:**
  - S3: Move MSG_* constants from Section 1 to Section 8 — [REF §Grouping #4]
  - C9: Remove redundant solidTiles maintenance from setTile — [OPT §Dead Code #4]
- **Risk level:** None (constants are `const`, hoisted) / Low (setTile simplification)
- **Expected line savings:** ~6 lines (solidTiles maintenance removed from setTile)
- **Files changed:** golem.html
- **Changes summary:**
  1. Move lines 61-68 (MSG_* constants block) from Section 1 to the top of Section 8, before `calcDisplayDuration`.
  2. In `setTile()` (lines 450-462): remove the `if(old!==AIR && v===AIR){...} else if(old===AIR && v!==AIR){...}` block (lines 455-460). The function becomes:
     ```js
     function setTile(ch,x,y,v){
       const c=chambers[ch];
       if(x>=0&&x<c.w&&y>=0&&y<c.h){ c.tiles[y][x]=v; }
     }
     ```
     Rationale: `solidTiles` is built once at init from the grid. The render loop reads `c.tiles[y][x]` from the actual grid, so if a tile becomes AIR, the render simply draws nothing at that position. The `solidTiles` list is iterated but the tile value check (`if(t===WALL)`) prevents rendering AIR tiles even if they remain in the list.
- **Validation gate:** Messages display correctly, glyphs collect correctly (setTile removes glyph tile), cracked tiles break correctly (setTile removes cracked tile)
- **Testing checklist:**
  - [ ] Messages fade in/out with correct timing
  - [ ] Message queue respects MSG_MAX_QUEUE_DEPTH (5)
  - [ ] Collect all 4 glyphs — each glyph tile disappears from the grid
  - [ ] Dash through cracked tile — tile breaks and disappears
  - [ ] Render: no visual artifacts from stale solidTiles entries (render still checks tile value)

**Documentation impact:** docs/Project-Reference.md section map — message constants now in Section 8.

---

### Slice 8: Data-Driven Glyph Ability System

- **Items included:**
  - FP1: Replace hardcoded if/else chain in `checkGlyphs()` with `GLYPH_EFFECTS` data structure — [OPT §Future-Proofing #1, OPT §Redundancy #4, REF §Extraction #4]
  - S7: Extract recurring particle colors to a `PARTICLE_COLORS` object — [REF §Naming #5]
- **Risk level:** Low — replaces equivalent logic with data-driven lookup; color extraction is pure string replacement
- **Expected line savings:** ~0 lines net (slightly longer data structure, shorter logic)
- **Files changed:** golem.html
- **Changes summary:**
  1. Add to Section 1 (after ABILITIES array, line 74):
     ```js
     const GLYPH_EFFECTS = [
       { set: () => { P.maxJumps = 2; }, msg: "Knowledge lifts me." },
       { set: () => { P.canDash = true; }, msg: "Speed courses through me." },
       { set: () => { P.canPush = true; }, msg: "Strength returns." },
       { set: () => { P.canBreak = true; }, msg: "Clay becomes Wisdom." },
     ];
     ```
  2. Replace lines 898-901 in `checkGlyphs()`:
     ```js
     const gx = glyphsCollected - 1;
     if(gx >= 0 && gx < GLYPH_EFFECTS.length){
       GLYPH_EFFECTS[gx].set();
       showMessage(GLYPH_EFFECTS[gx].msg, 120);
     }
     ```
  3. Add particle color constants (extract from inline strings):
     ```js
     const PARTICLE_COLORS = {
       jump: '#8a7d6b',
       doubleJump: '#d4a84b',
       glyph: '#f0d060',
       dashBurst: 'rgba(220,120,255,0.6)',
       death: '#8a7d6b',
     };
     ```
  4. Replace inline strings: `'#8a7d6b'` -> `PARTICLE_COLORS.jump` (lines 1122, 1130, 1228), `'#d4a84b'` -> `PARTICLE_COLORS.doubleJump` (line 1136), `'#f0d060'` -> `PARTICLE_COLORS.glyph` (line 897), `'rgba(220,120,255,0.6)'` -> `PARTICLE_COLORS.dashBurst` (line 996).
- **Validation gate:** All 4 glyphs grant correct abilities, particle colors unchanged visually
- **Testing checklist:**
  - [ ] Collect glyph 1 — double jump ability unlocked, message correct
  - [ ] Collect glyph 2 — dash ability unlocked, message correct
  - [ ] Collect glyph 3 — push block ability unlocked, message correct
  - [ ] Collect glyph 4 — break cracked ability unlocked, message correct
  - [ ] Test chamber (all abilities pre-unlocked) — no ability granted on entry (glyphsCollected already 4)
  - [ ] Particle colors look identical to before (jump dust, double jump sparkle, glyph collection burst, dash burst)

**Documentation impact:** docs/Project-Reference.md — note that GLYPH_EFFECTS is now the single source of truth for glyph abilities.

---

### Slice 1.5: UI and Gameplay Cleanup


- **Items included:**
  - U1: Remove duplicate "I awaken..." X.fillText overlay (lines 1685-1688) — [New]
  - U2: Remove HUD dash charge indicator (lines 1616-1631) — [New]
  - U3: Remove dead push block slot-checking code from updatePushBlock (lines 726-736) — [New]
- **Risk level:** None — pure dead code / redundant render removal
- **Expected line savings:** ~20 lines net (4 lines render overlay + 16 lines HUD indicator + 11 lines slot code)
- **Files changed:** golem.html
- **Changes summary:**
  1. Remove lines 1685-1688 in render(): the `if(ch===0 && glyphsCollected===0 && messageQueue.length===0){ X.fillText(...) }` block. The `showMessage('I awaken...', 150)` at line 1719 already handles the initial message via the proper message queue with fade in/out.
  2. Remove lines 1616-1631 in render(): the HUD dash charge bar indicator (`if(P.dashCharge > 0){ ... bar render ... }`). The preferred ring indicator centered on the golem (lines 1505-1560) remains.
  3. Remove lines 726-736 in `updatePushBlock()` Phase D: the `if(c.pushSlot){ ... }` block. The `inSlot` property on push block objects is preserved (initialized as `false` at line 650, used as a guard in 7+ places). Since no chamber defines `pushSlot`, this code is never triggered. Future chambers can define `pushSlot` — the `inSlot` guard logic in `activePushBlocks()`, `checkPushBlockCrush()`, `resolvePushBlockCollision()`, and the render function already supports it.
- **Validation gate:** Game loads, Chamber 0 message works via showMessage (fade in/out), dash charge ring indicator visible on golem, push blocks work normally
- **Testing checklist:**
  - [ ] Game loads — only the showMessage "I awaken..." appears (fade in/out), no persistent small-font overlay
  - [ ] Chamber 0: no duplicate text at (W/2, 60)
  - [ ] Dash: ring indicator centered on golem during charge (grows from 8px to 40px, pulses at max)
  - [ ] Dash: no bar indicator in top-left HUD area
  - [ ] Chamber 3: push blocks push normally, no slot behavior (there was none before)
  - [ ] Push block crush still works (inSlot guard preserved)
  - [ ] Push block active filtering still works (inSlot guard preserved)

**Documentation impact:** docs/Project-Reference.md — note that inSlot is preserved as a future-ready guard but no chamber currently uses pushSlot.

---


---

## Validation Strategy

Each slice follows this validation sequence before proceeding to the next:

1. **Syntax check:** Open golem.html in browser DevTools — verify no JavaScript syntax errors or ReferenceErrors in console.
2. **Load test:** Page loads, canvas renders, "I awaken..." message appears, death/respawn animation plays.
3. **Full playthrough test:** Play through all 5 chambers (ch0-ch4) completing each chamber's objective.
4. **Ability verification:** Each ability (double jump, dash, push blocks, break cracked) works as expected.
5. **Test chamber test:** Press T to enter test chamber, verify all abilities work, press T to return.
6. **Edge case test:** Trigger all death types (pit fall, push block crush, magical wall contact), verify respawn works.
7. **Ending test:** Reach end portal, verify ending screen displays correctly.

If any test fails, revert the slice and investigate before proceeding. Each slice is committed separately (if using git) for easy rollback.

---

## Dependency Map

```
Slice 1 (Dead Code) ──────────────────────────────────────────┐
                                                               ├──> Slice 3 (prevKeys + Timers)
Slice 2 (Headers/Comments) ───────────────────────────────────┤
                                                               ├──> Slice 4 (API Cleanup + rAF)
Slice 2 (Headers/Comments) ── prerequisite for ───────────────┤
                                                               ├──> Slice 5 (Dash/Reset Helpers)
Slice 2 (Headers/Comments) ── prerequisite for ───────────────┤
                                                               ├──> Slice 6 (Push Fix + Helpers)
Slice 2 (Headers/Comments) ── prerequisite for ───────────────┤
                                                               ├──> Slice 7 (Constants Move + setTile)
                                                               └──> Slice 8 (Glyph Data-Driven)

Slice 1.5: independent of all others (pure dead code removal)
Slices 3-8: no interdependencies among them (all can run after Slice 2)
Slice 1: independent of all others
Slice 2: prerequisite for slices that add new UTILITIES functions (3, 5, 6, 8)
          because those helpers are placed in the newly-headered UTILITIES section
```

**Independent pairs (can be done in parallel):**
- Slice 1 is fully independent
- Slices 3, 4, 5, 6, 7, 8 have no inter-dependencies (all only depend on Slice 2)

**Recommended order (by risk, not dependency):**
1. Slice 1 (None) -> 1.5. Slice 1.5 (None) -> 2. Slice 2 (None) -> 3. Slice 3 (Low) -> 4. Slice 4 (Low) -> 5. Slice 5 (Low) -> 6. Slice 6 (Low) -> 7. Slice 7 (Low) -> 8. Slice 8 (Low)

---

## Risk Assessment

| Risk | Slice(s) | Likelihood | Mitigation |
|------|----------|------------|------------|
| **prevKeys spread copy changes timing** | Slice 3 | Very low | `fresh()` checks `keys[code] && !prevKeys[code]` — spread copy captures exactly the same state as the old loop at frame boundary. Verified: no timing-sensitive logic depends on prevKeys cleanup order. |
| **Message queue helper changes timing by 1 frame** | Slice 3 | None | Helper is a 1:1 extraction — same code, wrapped in a function call. Zero timing difference. |
| **_testMode removal breaks external test harness** | Slice 1 | Low | AGENTS.md line 70 references `_testMode = true` for instant transitions. This is a documented testing convention. Removal should be noted; test harness can re-add `_testMode` as a global override before the file. |
| **solidTiles removal causes render artifact** | Slice 7 | Very low | Render loop reads `c.tiles[y][x]` from the actual grid for every tile in solidTiles. If a tile is AIR, none of the `if(t===WALL)` etc. checks match, so nothing is drawn. Verified: no tile rendering depends on solidTiles being accurate. |
| **Dash reset helper misses a field** | Slice 5 | Low | Carefully mapped each of the 5 sites to ensure `fullDashReset()` covers all fields set by any site and `cancelDash()` covers the minimal set. Cross-referenced with P object definition (line 385-393). |
| **return->continue changes push block behavior** | Slice 6 | Very low | Current levels don't have overlapping push blocks, so no behavioral change. Change is purely defensive for future level design. |
| **Glyph data-driven system breaks ability unlock** | Slice 8 | Low | Array index `glyphsCollected - 1` maps 1->0, 2->1, 3->2, 4->3 — exactly matching the original if/else chain order. Guarded by bounds check. |

**General mitigations:**
- Function hoisting protects all call-order dependencies (all functions use `function` declarations).
- Single global scope means moving code between sections changes nothing about variable visibility.
- Test chamber (press T) provides a sandbox with all abilities unlocked for rapid verification.
- Browser DevTools console catches any ReferenceError immediately.

---

## Innovate Checkpoint

### Alternatives Considered

1. **Full IIFE module extraction** (REF §Extraction #1-#2): Wrap push-block system and tile system in IIFE modules matching the `Particles` pattern.
   - **Tradeoff:** High risk, many call-site changes, no behavioral improvement. Deferred to a future architectural pass.
2. **HiDPI canvas scaling** (CR §Suggestion #5): Scale canvas for devicePixelRatio.
   - **Tradeoff:** Medium risk (all drawing coordinates would need no change since we use X.scale, but testing on non-HiDPI screens is harder). Out of scope for this refinement pass.
3. **Particle compact-after-dead pattern** (OPT §Performance #2): Replace splice with compaction loop.
   - **Tradeoff:** Marginal gain (<50 particles at any time). Out of scope for quick-win pass.
4. **Collision object allocation elimination** (OPT §Performance #3): Pass parameters directly instead of through options objects.
   - **Tradeoff:** Changes API surface of tileCollidesRect/collides/collidesNoPlat/collidesDash. Higher risk than current pass justifies.
5. **Neighbor scan extraction** (OPT §Redundancy #6): Extract `scanNeighborTiles(callback)` pattern.
   - **Tradeoff:** Adds abstraction layer over simple loops. Risk outweighs benefit for 3 call sites of 3 lines each.

### Selected Approach

8 slices ordered by risk (None -> Low), each independently testable. Focus on:
- **Quick wins first:** Dead code removal (2 lines), comment cleanup (0 lines)
- **Defensive fixes:** prevKeys unbounded growth, return->continue
- **Duplication elimination:** Message queue, dash reset, player grid position
- **Structural clarity:** Section headers, constant co-location
- **Future-proofing:** Data-driven glyph system

### Confidence Assessment

- **Slices 1-2 (None risk):** 100% confidence — dead code removal and comment changes.
- **Slices 3-4 (Low risk):** 95% confidence — well-understood refactoring with clear validation gates.
- **Slices 5-6 (Low risk):** 90% confidence — helper extraction with 1:1 behavioral mapping.
- **Slices 7-8 (Low risk):** 85% confidence — solidTiles removal needs visual verification; glyph data-driven system needs full playthrough.

**Overall confidence: 90%** — all slices are well-scoped with explicit validation gates. The plan is a refinement pass, not a rewrite, and avoids the higher-risk architectural changes (module extraction, API changes) until a future pass.

### Estimated Total Effort

- **Slices 1-2 (incl 1.5):** 25 minutes (mechanical changes)
- **Slices 3-4:** 25 minutes (requires careful testing)
- **Slices 5-6:** 20 minutes (helper extraction, verification)
- **Slices 7-8:** 20 minutes (constant move, data-driven refactor)
- **Total:** ~80 minutes focused work

**Total line savings:** ~62 lines direct + ~0 lines structural = ~62 lines (~3.6% of 1727 lines)

---

## Summary

| Slice | Name | Risk | Lines Saved | Est. Time |
|-------|------|------|-------------|-----------|
| 1 | Remove Dead Code | None | ~9 | 5 min |
| 1.5 | UI and Gameplay Cleanup | None | ~20 | 5 min |
| 2 | Section Headers & Comments | None | ~0 | 5 min |
| 3 | Fix prevKeys + Extract Timers | Low | ~14 | 10 min |
| 4 | API Cleanup (killAndRespawn, rAF) | Low | ~3 | 5 min |
| 5 | Consolidate Dash/Reset Helpers | Low | ~13 | 10 min |
| 6 | Push Block Fix + playerGridPos | Low | ~6 | 5 min |
| 7 | Move Constants + Simplify setTile | Low | ~6 | 5 min |
| 8 | Data-Driven Glyph System | Low | ~0 | 10 min |
