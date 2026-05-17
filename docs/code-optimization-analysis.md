# Code Optimization Analysis: golem.html

**Date:** 2026-05-16
**File:** golem.html (1152 lines, 44KB, 11 sections)
**Scope:** Six-slice comprehensive optimization research

---

## Slice A — Code Duplication & Redundancy

### A1. Jump Particle Spawn (3 identical patterns, lines 758, 766, 772)

Three jump branches all call `spawnParticles(P.x+P.w/2, P.y+P.h, ...)` with different color/count:
- Line 758: buffer-jump, color `'#8a7d6b'`, count 5
- Line 766: coyote-jump, color `'#8a7d6b'`, count 5
- Line 772: double-jump, color `'#d4a84b'`, count 8

**Waste:** Coordinate expression `P.x+P.w/2` and `P.y+P.h` each computed 3x per jump event.
**Fix:** Precompute once at jump block entry.

### A2. Dash Particle Spawn (2 identical calls, lines 633, 647)

```
spawnParticles(P.x+P.w/2, P.y+P.h/2, 'rgba(220,120,255,0.4)', 2)
```
Identical call on line 633 (charge particles) and line 647 (dash execution particles).
**Fix:** Extract to `DASH_PARTICLE_COLOR = 'rgba(220,120,255,0.4)'` constant.

### A3. Player Death/Respawn Reset (2 identical blocks, lines 652-654 and 783-785)

Pattern `P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0; P.jumps=0; P.dashing=false; P.dashCharge=0; P.onGround=...; P.coyoteTime=12;` appears in:
- Line 652-654: magical wall death
- Line 783-785: pit/out-of-bounds death

Both blocks differ only in the `P.onGround` value (true vs false).
**Fix:** Extract to `function killAndRespawn(){ ... }` called from both sites.

### A4. X Collision Response (2 near-identical blocks, lines 688-692 and 694-698)

```js
if(P.vx>0){ P.x=gx2*T-P.w; }
else if(P.vx<0){ P.x=(gx1+1)*T; }
else { P.x=prevX; }
P.vx=0;
```
This appears inside the dash-phase collision handler AND the non-dash handler. Same 4 lines, copy-pasted.
**Fix:** Extract to `function resolveXCollision(){ ... }` or `function snapToTile(){ ... }`.

### A5. Dash End Pattern (3 copies, lines 649, 653, 685)

```js
P.dashing=false; P.dashCooldown=DASH_COOLDOWN; P.dashPhase=false;
```
Appears in three contexts: dash timer expiry, magical wall death, CRACKED break.
**Fix:** `function endDash(){ P.dashing=false; P.dashCooldown=DASH_COOLDOWN; P.dashPhase=false; }`

### A6. Ground Landing Reset (2 copies, lines 719-721 and 737-739)

```js
P.onGround=true; P.jumps=0; P.coyoteTime=12;
```
One for tile landing (719-721), one for push-block landing (737-739).
**Fix:** `function land(){ P.onGround=true; P.jumps=0; P.coyoteTime=12; }`

### A7. Input Key Check Duplicates (5 call sites for horizontal, 2 for vertical)

Horizontal movement checks:
- Line 591: `keys['ArrowLeft']||keys['KeyA']`
- Line 592: `keys['ArrowRight']||keys['KeyD']`

Jump checks:
- Line 749: `fresh('ArrowUp')||fresh('KeyW')||fresh('Space')`
- Line 750: `keys['ArrowUp']||keys['KeyW']||keys['Space']`

Dash trigger:
- Line 637: `fresh('ShiftLeft')||fresh('ShiftRight')` (while `shiftHeld()` at line 206 exists but only used for one check)

**Fix:** Create `inputLeft()`, `inputRight()`, `inputJumpPressed()`, `inputJumpHeld()` abstractions. (This overlaps with beyond-scope item #5.)

### A8. Redundant Variable Lookup: `collectedGlyphs[ch]` (lines 504, 507, 856, 1093)

The chamber's glyph collection status is looked up 4x in render and update. In render(), the same value is computed in two separate branches (door rendering at line 856, chamber name at line 1093) without caching.
**Fix:** Compute `const glyphCollected = collectedGlyphs[ch];` once at render entry.

### A9. Redundant `P.chamber` lookup in `getTile()` (called ~375x/frame in tile loop)

Every tile iteration calls `getTile(ch, gx, gy)` which does `const c=chambers[ch]` — but `c` is already available in the outer render scope. The tile helpers cannot access the outer `c` variable.
**Fix:** Pass the chamber object directly instead of the index, or use a closure-scoped `currentChamber` variable.

---

## Summary Table: Slice A

| Pattern | Copies | Lines | Suggested Fix | Effort |
|---------|--------|-------|---------------|--------|
| Jump particles (coord expr) | 3 | 758,766,772 | Precompute coords | Trivial |
| Dash particles (identical call) | 2 | 633, 647 | Color constant | Trivial |
| Death/respawn reset | 2 | 652-654, 783-785 | `killAndRespawn()` | ~5 lines |
| X collision response | 2 | 688-692, 694-698 | `resolveXCollision()` | ~5 lines |
| Dash end pattern | 3 | 649, 653, 685 | `endDash()` | ~3 lines |
| Ground landing reset | 2 | 719-721, 737-739 | `land()` | ~3 lines |
| Input key checks | 5+ | 591-592, 749-750, 637 | Abstraction funcs | ~10 lines |
| `collectedGlyphs[ch]` | 4 | 504,856,1093 | Local var | Trivial |
| `chambers[ch]` per getTile | 375x/frame | 212-216 | Closure var | Moderate |

**Total duplicated patterns found: 9 categories**
**Lines of copy-pasted code: ~25 lines total**
**Potential savings via extraction: ~10-15 lines of code**

---

## Slice B — Per-Frame Performance

### B1. Date.now() Calls: 15 per Frame

All 15 occur in `render()` (Section 10):

| Line | Context | Per-Tile or Per-Frame | Calls per Frame (typical) |
|------|---------|----------------------|---------------------------|
| 849 | PIT glow `Math.sin(Date.now()/600+x)` | Per PIT tile | ~6-12 |
| 858 | Door locked pulse | Per door tile | 0-1 |
| 868 | Door unlocked pulse | Per door tile | 0-1 |
| 879 | END_PORTAL pulse 1 | Per portal tile | 0-1 |
| 880 | END_PORTAL pulse 2 | Per portal tile | 0-1 |
| 892 | GLYPH bob | Per glyph tile | 0-1 |
| 893 | GLYPH pulse | Per glyph tile | 0-1 |
| 919 | MAGICAL_WALL pulse | Per MW tile | 0-11 |
| 927 | MAGICAL_WALL spark Y | Per MW tile | 0-11 |
| 945 | Push block hint | Per frame | 0-1 |
| 972 | Dash max charge pulse | Per frame | 0-1 |
| 1033 | Push effort pulse | Per frame | 0-1 |
| 1042 | Glyph body lines | Per frame | 1 |
| 1050 | Falling motion lines | Per frame | 0-1 |
| 1082 | Dash HUD MAX pulse | Per frame | 0-1 |

**Worst case:** ~50+ Date.now() calls per frame if all animated tiles are on screen (Chamber 4 has ~12 CRACKED tiles, Chamber 2 has 12 MAGICAL_WALL tiles).

**Fix:** Cache `const now = Date.now()` once at render entry. All 15 calls become `now` lookups. Zero behavior change. ~1 line added, 15 calls optimized.

### B2. Math.sin() Calls: 13 per Frame

13 of the 15 Date.now() lines also call Math.sin(). Lines 927 and 1050 use Date.now() without Math.sin (integer division + modulo for animation offsets).

**Worst case:** ~30+ Math.sin() calls per frame when all animated tiles present.

### B3. Per-Frame Allocations That Could Be Precomputed

1. **Starfield positions** (line 817):
   ```js
   for(let i=0;i<40;i++) X.fillRect((i*137+ch*50)%W,(i*97+ch*30)%H,1,1);
   ```
   Only depends on `ch` (chamber index). 5 chambers means 5 possible starfields. Currently recomputed every frame (40 modulo ops + 40 fillRect).
   **Fix:** Precompute per chamber into a small offscreen canvas or a cached array of [x,y] pairs.

2. **Abilities array** (lines 1061-1064):
   ```js
   const abilities = [['[1] Double Jump',1],...];
   ```
   Completely static. Created every frame.
   **Fix:** Move to module scope as `const ABILITIES = ...`.

3. **Chamber names array** (line 1090):
   ```js
   const names=['Awakening','The Library',...];
   ```
   Completely static. Created every frame.
   **Fix:** Move to module scope as `const CHAMBER_NAMES = ...`.

### B4. Tile Render Loop Efficiency

The main tile loop iterates all 25*15=375 tiles every frame:
```js
for(let y=0;y<c.h;y++) for(let x=0;x<c.w;x++){
```
Most tiles are AIR (0) and the if/else chain immediately skips them. Typical non-AIR tile count: 50-100.
**Fix:** Maintain a sparse list of non-AIR tiles per chamber. Reduces iterations from 375 to ~50-100 per frame (3-7x reduction). Trade-off: need to maintain the sparse list when tiles change (setTile calls).

### B5. Particle System: splice() During Iteration

Line 454: `particles.splice(i,1)` in backward iteration. Works correctly but reallocates the array on every removal. At current scale (typically <50 particles, max ~100 during shatter), this is negligible. No fix needed at current scale.

### B6. Previous Keys Cleanup (lines 794-795)

```js
for(const k in keys) prevKeys[k]=keys[k];
for(const k in prevKeys) { if(!keys[k] && k in prevKeys) delete prevKeys[k]; }
```
The second loop iterates ALL keys in prevKeys to clean up stale entries. Since `keys` typically has 3-5 entries and `prevKeys` mirrors it, this is minimal overhead. No fix needed.

---

## Summary Table: Slice B

| Issue | Impact | Current Cost | Fix | Effort |
|-------|--------|-------------|-----|--------|
| 15 Date.now() calls | Moderate | ~50 calls/frame worst case | Cache to `now` var | 1 line |
| 13 Math.sin() calls | Low | ~30 calls/frame worst case | Cache `now` reduces arg calc | Included above |
| Starfield recomputed | Low | 40 mod ops + 40 fillRect | Precompute per chamber | ~5 lines |
| Abilities array alloc | Negligible | 1 array/frame | Move to module scope | 2 lines |
| Names array alloc | Negligible | 1 array/frame | Move to module scope | 2 lines |
| Tile loop 375 iterations | Low-Moderate | 375 iters vs ~50 needed | Sparse tile list | ~20 lines |
| Particle splice | Negligible | O(n) removals | N/A at current scale | N/A |

---

## Slice C — Structural Modularity

### C1. Global State Coupling Analysis

Every function in the codebase accesses at least one global variable. Coupling levels:

| Function | Globals Used | Coupling Level |
|----------|-------------|----------------|
| `mkGrid()` | `AIR` (constant) | LOW — self-contained |
| `getTile(ch,x,y)` | `chambers`, `WALL` | LOW — takes chamber index |
| `setTile(ch,x,y,v)` | `chambers` | LOW |
| `solid(t)` | tile constants | LOW — pure function |
| `platSolid(t,prevY,curY)` | `P.h`, `PLATFORM` | MEDIUM — needs P.h |
| `tileCollidesY(...)` | `T`, `getTile`, `solid`, `platSolid` | LOW |
| `collides()` | `T`, `P.h`, `tileCollidesY` | MEDIUM — needs P.h |
| `collidesNoPlat()` | `solid`, `getTile` | LOW |
| `collidesDash()` | `T`, `MAGICAL_WALL`, `PB`, `aabb`, `P` | HIGH — needs PB, P |
| `inPit(px,py)` | `P.chamber`, `getTile`, `T`, `PIT` | HIGH — needs P |
| `aabb(...)` | none | LOW — pure function |
| `tileCollides()` | `T`, `solid`, `getTile` | LOW |
| `resetPushBlock()` | `P.chamber`, `chambers`, `PB` | HIGH |
| `resolvePushBlockCollision()` | `P`, `PB`, `aabb`, `PUSH_SPEED`, `spawnParticles` | HIGH |
| `updatePushBlock()` | `P`, `PB`, `chambers`, `T`, `spawnParticles`, `showMessage` | HIGH |
| `shatterBlock()` | `particles` | MEDIUM — needs particles array |
| `spawnParticles()` | `particles` | MEDIUM |
| `updateParticles()` | `particles` | MEDIUM |
| `showMessage()` | `messageText`, `messageTimer` | HIGH |
| `_doTransition()` | `P`, `chambers`, `resetPushBlock` | HIGH |
| `checkDoors()` | `P`, `chambers`, `collectedGlyphs`, `portalLockMsg`, `transition` | HIGH |
| `checkGlyphs()` | `P`, `chambers`, `collectedGlyphs`, `glyphsCollected`, `GLYPH` | HIGH |
| `update()` | EVERYTHING | CRITICAL |
| `render()` | EVERYTHING | CRITICAL |
| `loop()` | `update`, `render` | LOW |

### C2. Dependency Graph (Sections)

```
Section 1 (Constants) --> ALL sections
Section 2 (Chamber Data) --> Section 1
Section 3 (Entities) --> NONE (declarations only)
Section 4 (Input) --> Section 3 (keys, prevKeys)
Section 5 (Tile Helpers) --> Sections 1, 2, 3
Section 6 (Push Block) --> Sections 1, 2, 3, 5, 7
Section 7 (Particles) --> Section 3 (particles array)
Section 8 (Game Flow) --> Sections 1, 2, 3, 7
Section 9 (Update) --> ALL (Sections 1-8)
Section 10 (Render) --> ALL (Sections 1-8)
Section 11 (Init) --> Sections 2, 3
```

### C3. What Would Need to Change for Module Extraction

**Chamber data extraction (easiest):**
- Move chamber IIFEs to a separate file
- Export `chambers` array
- Import in main file
- Requires: module system (ESM or CommonJS) — but single-file constraint blocks this
- Without modules: could use a `<script src="chambers.js">` before the main script

**Particle system extraction (easy):**
- `shatterBlock`, `spawnParticles`, `updateParticles` only need `particles` array
- Could be an IIFE that returns `{spawn, shatter, update}` methods
- Would require passing `particles` array or using an internal one with `.get()` accessor

**Render extraction (hard):**
- `render()` is the most tightly coupled function
- Needs access to: P, PB, particles, COLORS, chambers, collectedGlyphs, glyphsCollected, gameState, screenAlpha, messageText, messageTimer
- Would need a `RenderContext` object passed in

**Major blocker:** The `P` object is the central hub. Almost every system reads or modifies P directly. Extracting anything cleanly would require either:
1. Creating a `GameContext` object that bundles P, PB, particles, keys, chambers, etc.
2. Using an event/message system (overkill for this scale)
3. Passing explicit parameters to functions that need them

### C4. Forward Reference Issues (Hoisting Dependency)

The code relies on JavaScript function hoisting:
- `aabb()` defined in Section 5 but called by `resolvePushBlockCollision()` in Section 6
- `spawnParticles()` defined in Section 7 but called by `resolvePushBlockCollision()` in Section 6
- `collidesNoPlat()` defined in Section 5 but called by `update()` in Section 9

All use `function` declarations (hoisted), so order doesn't matter for execution. But for extraction into modules, dependencies would need to be explicit.

---

## Summary Table: Slice C

| System | Extractability | Blockers | Effort |
|--------|---------------|----------|--------|
| Constants | Trivial | None — already self-contained | N/A |
| Chamber Data | Easy | Need script tag or module | ~5 lines |
| Input | Easy | Only needs keys object | ~10 lines |
| Tile Helpers | Moderate | `platSolid` needs P.h | ~15 lines |
| Push Block | Hard | Needs P, PB, particles, game flow | ~30 lines |
| Particles | Easy | Only needs particles array | ~10 lines |
| Game Flow | Hard | Needs P, chambers, glyphs | ~25 lines |
| Update | Critical | Needs everything | ~50+ lines |
| Render | Critical | Needs everything + COLORS | ~50+ lines |

**Recommendation:** For true modular extraction, create a `GameContext` object. This is a significant architectural change requiring governance approval per AGENTS.md Rule 1.

---

## Slice D — File Size Reduction

### D1. Current File Size Breakdown

| Component | Approx Size | Percentage |
|-----------|------------|------------|
| HTML/CSS boilerplate | ~500 bytes | 1.1% |
| Section delimiter comments | ~800 bytes | 1.8% |
| Code comments (inline) | ~1,500 bytes | 3.3% |
| Chamber data (6 IIFEs) | ~3,500 bytes | 7.7% |
| Code logic (all functions) | ~28,000 bytes | 61.1% |
| Render code (visuals) | ~8,500 bytes | 18.6% |
| Whitespace/indentation | ~2,000 bytes | 4.4% |

### D2. Minification-Friendly Patterns

1. **Dead code paths** (BLOCK=6, ~200 bytes):
   - Line 26: `BLOCK=6` in constants
   - Line 223: `t===BLOCK` in `solid()`
   - Lines 901-905: `else if(t===BLOCK)` render branch
   These are never executed (no chamber uses BLOCK tiles) but add ~200 bytes.

2. **Repeated string literals** (estimated ~300 bytes savings):
   - `'rgba(220,120,255,0.4)'` appears 2x (dash particles)
   - `'rgba(220,120,255,0.6)'` appears 1x (dash fire)
   - `'#d4a84b'` appears 4x (multiple particle spawns)
   - `'#8a7d6b'` appears 4x (jump particles + golem body)
   - `'rgba(0,0,0,'` appears 2x (screen fade overlay)
   Using constants for these saves ~300 bytes after minification.

3. **Long variable names** (estimated ~500 bytes):
   - `resolvePushBlockCollision` (24 chars) x 3 references = 72 chars
   - `PUSH_SPEED` (10 chars) x 4 references = 40 chars
   - `DASH_CHARGE_MAX` (15 chars) x 4 references = 60 chars
   - `DASH_DISTANCE_MIN` (17 chars) x 3 references = 51 chars
   - `DASH_CHARGE_RING_MIN` (20 chars) x 1 reference = 20 chars
   These are already reasonable for readability. Minification would handle this automatically.

4. **Per-frame array allocations** (no file size impact, but runtime):
   - `const abilities = [...]` (line 1061)
   - `const names=[...]` (line 1090)
   Moving these out of render() saves ~200 bytes of repeated allocation.

### D3. Estimated File Size Savings

| Optimization | Bytes Saved | Method |
|-------------|------------|--------|
| Remove BLOCK dead code | ~200 | Delete constant, solid() check, render branch |
| Color constant extraction | ~100 | Replace repeated string literals |
| Move abilities/names out of render | ~0 file size | Runtime only |
| Minification (if applied) | ~6,000-8,000 | Standard minifier |
| Whitespace reduction (manual) | ~1,500 | Tighten formatting |

**Total potential savings without minification: ~300-500 bytes (~1%)**
**Total with minification: ~6,000-8,500 bytes (~15-20%)**

Note: The file is already 44KB, well within reasonable limits for a single HTML file. File size optimization is low priority.

---

## Slice E — Overlap Analysis with beyond-scope-simplifications.md

### E1. Item-by-Item Status

| # | Item | Status | Addressed by Refactor? | Optimization Can Help? | Merge into Optimization? |
|---|------|--------|----------------------|----------------------|------------------------|
| 1 | Jump Velocity Equalization | Still present (lines 753, 769) | No | Constant extraction makes change trivial | Yes — group with magic number cleanup |
| 2 | Pause Toggle | Not implemented | No | Adding `gameState='paused'` early-return in `update()` is trivial | No — distinct feature |
| 3 | Responsive Canvas | Still fixed 800x480 | No | 1-line CSS change, no code interaction | No — pure CSS |
| 4 | BLOCK Cleanup | Still present (line 26, 223, 901-905) | No (deferred) | Dead code removal identified in Slice D | Yes — merge into dead code cleanup |
| 5 | Input Normalization | Still duplicated (lines 591-592, 749-750, 637) | No | Abstraction functions identified in Slice A7 | Yes — already covered in Slice A |
| 6 | Message Queue | Still immediate replacement | No | Would benefit from Slice C (GameContext) | No — feature addition |
| 7 | Camera System | Still hardcoded ox/oy (lines 820-821) | No | Camera object would benefit from Slice C extraction | No — architectural |
| 8 | Sound Effects | Not implemented | No | Independent system | No — feature addition |
| 9 | Touch Controls | Not implemented | No | Independent UI system | No — feature addition |
| 10 | Code Comments | Section delimiters added, JSDoc still missing | Partially | Section reorg improved navigation | No — documentation |

### E2. Recommendations

**Merge into optimization proposal:**
- Item #4 (BLOCK Cleanup) + Slice D1 (dead code paths) = unified dead code removal task
- Item #5 (Input Normalization) + Slice A7 = unified input abstraction task
- Item #1 (Jump Equalization) + new magic number cleanup = unified constants task

**Keep separate:**
- Items #2, #3, #6, #7, #8, #9 are feature additions, not optimizations
- Item #10 is documentation

---

## Slice F — New Optimization Opportunities NOT Yet Documented

### F1. Magic Number Extraction (HIGH value)

Physics constants scattered throughout `update()`:

| Magic Number | Line(s) | Meaning | Proposed Constant |
|-------------|---------|---------|-------------------|
| 0.05 | 597 | Ground horizontal acceleration | `H_ACCEL_GROUND` |
| 0.2 | 597 | Air horizontal acceleration | `H_ACCEL_AIR` |
| 0.225 | 600-601 | Horizontal friction | `H_FRICTION` |
| 0.07 | 662 | Gravity | `GRAVITY` |
| 2.5 | 598, 664 | Terminal velocity (both X and Y) | `TERMINAL_VEL` |
| -5 | 753, 761 | First jump velocity | `JUMP_VEL_1` |
| -4.33 | 769 | Double jump velocity | `JUMP_VEL_2` |
| -2 | 779 | Variable jump cut velocity | `JUMP_CUT_VEL` |
| 0.85 | 608 | Charge state friction | `CHARGE_FRICTION` |
| 0.3 | 375 | Push block gravity | `PB_GRAVITY` |
| 4 | 376 | Push block terminal velocity | `PB_TERMINAL_VEL` |
| 0.85 | 386 | Push block friction | `PB_FRICTION` |
| 0.1 | 387 | Push block velocity threshold | `PB_STOP_THRESH` |
| 12 | 721, 739, 785, 653 | Coyote time frames | `COYOTE_FRAMES` |
| 12 | 757, 765, 775 | Jump buffer frames | `JUMP_BUFFER_FRAMES` |

**Effort:** ~15 constant definitions, ~25 line edits. Would make future physics tuning trivial.

### F2. Player State Reset Function (Slice A3 + A6 combined)

The death/respawn pattern is repeated 2x (lines 652-654, 783-785) and the ground landing pattern 2x (lines 719-721, 737-739). Combining with dash end pattern (3 copies) gives a `PlayerState` utility:

```js
function resetOnDeath(){
  P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0;
  P.jumps=0; P.dashing=false; P.dashTimer=0; P.dashCharge=0;
  P.onGround=false; P.coyoteTime=COYOTE_FRAMES;
  resetPushBlock();
}
```
This appears at lines 652-654 (with slight variation) and 783-786.

**Effort:** ~8 lines added, ~20 lines saved.

### F3. Sparse Tile Rendering (NEW)

Current: iterates 375 tiles every frame, most are AIR.
Proposed: maintain a `nonAirTiles` array per chamber, iterate only ~50-100 tiles.

```js
// In each chamber IIFE, collect non-AIR tiles:
chambers.push({w, h, tiles: g, px, py, glyphs,
  solidTiles: g.reduce((acc, row, y) => {
    row.forEach((t, x) => { if(t) acc.push({x,y,t}); });
    return acc;
  }, [])
});
```

Then in render:
```js
for(const {x,y,t} of c.solidTiles){
  const px=ox+x*T, py=oy+y*T;
  // ... same if/else chain
}
```

**Trade-off:** `setTile` must maintain the sparse list when CRACKED tiles are destroyed. Adds ~5 lines to `setTile()`.

**Effort:** ~20 lines. **Impact:** 3-7x reduction in tile loop iterations.

### F4. Precompute Starfield (NEW)

The starfield (line 817) only varies by chamber index. With 6 chambers, precomputing is trivial:

```js
const STARFIELDS = chambers.map(ch =>
  Array.from({length:40}, (_,i) =>
    [{x:(i*137+ch.w*50)%W, y:(i*97+ch.w*30)%H}]
  )
);
// Or simply cache as arrays:
chambers.forEach((c,i) => {
  c.stars = [];
  for(let j=0;j<40;j++) c.stars.push([(j*137+i*50)%W, (j*97+i*30)%H]);
});
```

Then in render:
```js
X.fillStyle='#1a1a2e';
for(const [sx,sy] of c.stars) X.fillRect(sx,sy,1,1);
```

**Effort:** ~5 lines. **Impact:** Eliminates 40 modulo operations per frame.

### F5. Collides Function Simplification (NEW)

`collides()` at line 245 is a thin wrapper that just converts grid coords to pixel coords and calls `tileCollidesY`:

```js
function collides(gx1,gy1,gx2,gy2, ch, prevY, curY){
  return tileCollidesY(ch, gx1*T, curY, (gx2-gx1+1)*T, P.h, prevY, curY);
}
```

And `collidesDash()` (lines 259-272) is nearly identical to `tileCollidesY` with just one extra `continue` for MAGICAL_WALL.

**Observation:** These could share a common implementation with a `skipType` parameter.

**Effort:** ~10 lines. **Impact:** Code clarity, minor size reduction.

### F6. `prevKeys` Cleanup Optimization (NEW)

Lines 794-795:
```js
for(const k in keys) prevKeys[k]=keys[k];
for(const k in prevKeys) { if(!keys[k] && k in prevKeys) delete prevKeys[k]; }
```

The `k in prevKeys` check in the second loop is redundant — iterating `for(const k in prevKeys)` already guarantees `k` is in prevKeys. Can simplify:
```js
for(const k in keys) prevKeys[k]=keys[k];
for(const k in prevKeys) if(!keys[k]) delete prevKeys[k];
```

Or use Object.assign for the first line:
```js
Object.assign(prevKeys, keys);
```

**Effort:** 2 lines. **Impact:** Negligible but cleaner.

### F7. Tile Render Switch Statement (NEW)

Lines 827-931 use an 8-branch if/else chain for tile rendering. A switch statement would be slightly cleaner:
```js
switch(t){
  case WALL: ... break;
  case PLATFORM: ... break;
  // ... etc
}
```

**Impact:** No performance change (V8 optimizes both equally). Readability improvement for 8 branches.

### F8. Particle Color Pre-computation (NEW)

In the particle render loop (lines 952-958), `p.color` is used directly as fillStyle. For particles with alpha-based colors like `'rgba(200,160,100,0.5)'` (from shatterBlock dust), the alpha is baked into the string. The render loop then conditionally appends alpha:

```js
X.fillStyle=p.color+(a>0.7?'':'');
if(a<0.7) X.globalAlpha=a;
```

This works but `globalAlpha` affects all subsequent draws. The `X.globalAlpha=1` reset at line 957 is correct but adds an extra canvas state change per fading particle.

**Observation:** No fix needed at current scale. If particle count grows significantly, consider precomputing the faded color.

---

## Summary Table: Slice F

| Opportunity | Priority | Effort | Impact | Already Documented? |
|------------|----------|--------|--------|---------------------|
| Magic number extraction | HIGH | ~40 lines | Physics tuning clarity | No |
| Player state reset function | HIGH | ~8 lines | Remove ~20 lines duplication | Partially (Slice A3) |
| Sparse tile rendering | MEDIUM | ~20 lines | 3-7x tile loop reduction | No |
| Precompute starfield | LOW | ~5 lines | Eliminates 40 mod/frame | No |
| Collides function simplification | LOW | ~10 lines | Code clarity | No |
| prevKeys cleanup optimization | LOW | 2 lines | Cleanliness | No |
| Tile render switch statement | LOW | ~30 lines | Readability only | No |
| Particle color optimization | LOW | N/A | Negligible at current scale | No |

---

## Cross-Cutting Summary

### Highest Impact, Lowest Effort (Quick Wins)

1. **Cache Date.now() once per frame** — 1 line change, eliminates 14 redundant calls
2. **Move abilities/names arrays to module scope** — 4 lines moved, eliminates 2 per-frame allocations
3. **Extract endDash() / land() / killAndRespawn()** — ~20 lines of new code, removes ~25 lines of duplication
4. **Remove BLOCK dead code** — ~200 bytes saved, cleans up solid() and render()
5. **Input normalization abstractions** — ~10 lines, replaces 5+ duplicated key checks

### Medium Effort, Medium Impact

6. **Magic number extraction** — ~40 lines of new constants, makes all physics values tunable
7. **Sparse tile rendering** — ~20 lines, 3-7x reduction in render loop iterations
8. **Merge BLOCK cleanup + dead code + magic numbers into one optimization task**

### Low Priority (Nice to Have)

9. **Precompute starfield** — ~5 lines, eliminates 40 mod operations per frame
10. **Tile render switch statement** — readability only
11. **prevKeys cleanup optimization** — 2 lines, cleanliness only

### NOT Optimization (Feature Work)

- Pause toggle, responsive canvas, message queue, camera system, sound effects, touch controls, code comments — these are all documented in beyond-scope-simplifications.md and remain as separate feature items.

---

## Line Reference Index

All line numbers refer to golem.html (post-refactor, 11-section version):

| Line(s) | Section | Description |
|---------|---------|-------------|
| 26 | 1 | Tile constants (BLOCK=6 dead code) |
| 223 | 5 | solid() BLOCK check |
| 245 | 5 | collides() thin wrapper |
| 259-272 | 5 | collidesDash() duplicate logic |
| 339 | 6 | Push particle spawn |
| 375-376 | 6 | Push block gravity/terminal velocity magic numbers |
| 386-387 | 6 | Push block friction/stop threshold magic numbers |
| 399 | 6 | Slot particle spawn |
| 454 | 7 | Particle splice() removal |
| 534 | 8 | Glyph collect particle spawn |
| 591-592 | 9 | Horizontal input key checks |
| 597 | 9 | Acceleration/friction magic numbers |
| 608 | 9 | Charge friction magic number |
| 626-633 | 9 | Dash particle spawns |
| 637 | 9 | Dash trigger key check |
| 647 | 9 | Dash execution particle spawn |
| 649 | 9 | Dash end pattern (copy 1) |
| 652-654 | 9 | Death reset pattern (copy 1) |
| 662 | 9 | Gravity magic number |
| 685 | 9 | Dash end pattern (copy 2) |
| 688-692 | 9 | X collision response (copy 1) |
| 694-698 | 9 | X collision response (copy 2) |
| 719-721 | 9 | Landing reset pattern (copy 1) |
| 723 | 9 | Landing particle spawn |
| 737-739 | 9 | Landing reset pattern (copy 2) |
| 749-750 | 9 | Jump input key checks |
| 753 | 9 | First jump velocity magic number |
| 758 | 9 | Jump particle spawn (copy 1) |
| 761 | 9 | First jump velocity (duplicate) |
| 766 | 9 | Jump particle spawn (copy 2) |
| 769 | 9 | Double jump velocity magic number |
| 772 | 9 | Jump particle spawn (copy 3) |
| 779 | 9 | Jump cut velocity magic number |
| 783-785 | 9 | Death reset pattern (copy 2) |
| 794-795 | 9 | prevKeys cleanup |
| 811 | 10 | P.chamber lookup in render |
| 817 | 10 | Starfield computation (per-frame) |
| 820-821 | 10 | Hardcoded ox/oy centering |
| 824-931 | 10 | Tile render loop (375 iterations) |
| 849 | 10 | PIT Date.now() + Math.sin() |
| 858 | 10 | Door locked Date.now() + Math.sin() |
| 868 | 10 | Door unlocked Date.now() + Math.sin() |
| 879-880 | 10 | END_PORTAL 2x Date.now() + Math.sin() |
| 892-893 | 10 | GLYPH 2x Date.now() + Math.sin() |
| 901-905 | 10 | BLOCK render branch (dead code) |
| 919 | 10 | MAGICAL_WALL Date.now() + Math.sin() |
| 927 | 10 | MAGICAL_WALL spark Date.now() |
| 945 | 10 | Push block hint Date.now() + Math.sin() |
| 952-958 | 10 | Particle render loop |
| 972 | 10 | Dash max charge Date.now() + Math.sin() |
| 1033 | 10 | Push effort Date.now() + Math.sin() |
| 1042 | 10 | Glyph body lines Date.now() + Math.sin() |
| 1050 | 10 | Falling motion Date.now() |
| 1061-1064 | 10 | Abilities array (per-frame allocation) |
| 1082 | 10 | Dash HUD MAX Date.now() + Math.sin() |
| 1090 | 10 | Chamber names array (per-frame allocation) |

---

*End of Code Optimization Analysis*
