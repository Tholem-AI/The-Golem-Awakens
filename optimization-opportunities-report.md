# Optimization Opportunities: The Golem Awakens

## Size Analysis

| Metric | Value |
|--------|-------|
| Total lines | 1,727 |
| File size | ~64 KB |
| HTML/JS code | ~1,713 lines (excluding HTML boilerplate) |

### Lines Per Section

| # | Section | Lines | % of Total |
|---|---------|-------|------------|
| 1 | SETUP & CONSTANTS + Helpers | 16–111 | ~6% |
| 2 | CHAMBER DATA | 113–378 | ~15% |
| 3 | ENTITIES | 381–413 | ~2% |
| 4 | INPUT | 416–439 | ~1% |
| 5 | TILE HELPERS & COLLISION | 442–637 | ~11% |
| 6 | PUSH BLOCK SYSTEM | 640–747 | ~6% |
| 7 | PARTICLE SYSTEM | 750–803 | ~3% |
| 8 | GAME FLOW | 806–914 | ~6% |
| 9 | UPDATE + ANIM UPDATE | 917–1198 | ~16% |
| 10 | RENDER | 1201–1689 | ~28% |
| 11 | INIT & GAME LOOP | 1692–1727 | ~2% |

### Largest Functions

| Function | Lines | Location |
|----------|-------|----------|
| `render()` | ~350 | 1356–1689 |
| `renderDeathRespawnAnimation()` | ~140 | 1213–1354 |
| `update()` | ~240 | 919–1158 |
| `checkDoors()` | ~35 | 847–882 |
| `resolvePushBlockCollision()` | ~44 | 656–700 |

---

## Logic Simplification Opportunities

### 1. Merge Duplicate Respawning State Lines (Lines 1183, 1189)

**Current:** Two near-identical lines reset player state during anim transitions:

```js
// Line 1183: dying -> respawning
P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0; P.jumps=0; P.dashCharge=0;

// Line 1189: respawning -> idle
P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0; P.jumps=0; P.dashCharge=0;
```

**Simplified:** Extract a helper:

```js
function resetPlayerToRespawn() {
  P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0; P.jumps=0; P.dashCharge=0;
}
```

Call it twice. **Saves ~15 chars per call** (minor) but more importantly, adds a single place to update if respawn reset logic ever needs a field added.

### 2. Consolidate Dash State Reset Pattern (5 sites)

**Current:** Dash state is reset in 5 locations with slight variations:

```js
// Line 91 (endDash helper):
P.dashing=false; P.dashTimer=0; P.dashCooldown=DASH_COOLDOWN; P.dashPhase=false;

// Line 107 (killAndRespawn):
P.dashing=false; P.dashTimer=0;

// Line 834 (_doTransition):
P.dashing=false; P.dashTimer=0; P.dashCooldown=0; P.dashPhase=false; P.dashCharge=0;

// Line 1147 (pit death):
P.dashing=false; P.dashTimer=0;

// Line 1191 (respawn -> idle):
P.dashing=false; P.dashTimer=0; P.dashCooldown=0; P.dashPhase=false;
```

**Simplified:** Create a full dash reset and a minimal dash cancel:

```js
function fullDashReset() {
  P.dashing=false; P.dashTimer=0; P.dashCooldown=0; P.dashPhase=false; P.dashCharge=0;
}
function cancelDash() {
  P.dashing=false; P.dashTimer=0;
}
```

Replace all 5 sites. **Saves ~20 lines total**, eliminates risk of inconsistent dash state.

### 3. Extract `_doTransition` Player Reset Logic (Lines 833–837)

**Current:** Player state reset during transition:

```js
P.vx=0; P.vy=0; P.jumps=0;
P.dashing=false; P.dashTimer=0; P.dashCooldown=0; P.dashPhase=false; P.dashCharge=0;
P.onGround=false; P.coyoteTime=0;
P.pushing=false;
```

**Simplified:** A `resetPlayerState()` function called from both `_doTransition` and `updateAnim`. This overlaps with the dash reset pattern above — a single comprehensive helper covering all player fields would serve both.

**Estimated savings: ~8 lines** (once extracted, called from 2 places).

### 4. Simplify Jump Logic (Lines 1112–1140)

**Current:** Four `if/else if` branches with repeated `Particles.spawn(jx, jy, ...)` and `P.jumpBuffer=0`:

```js
if(P.onGround && P.jumpBuffer>0 && P.jumps<P.maxJumps){
  P.vy = P.jumps===0 ? JUMP_VEL_1 : JUMP_VEL_2;
  P.jumps++; P.onGround=false; P.coyoteTime=0; P.jumpBuffer=0;
  Particles.spawn(jx, jy, '#8a7d6b', 5);
}
else if(jumpPressed && P.jumps===0 && P.coyoteTime>0){
  P.vy = JUMP_VEL_1;
  P.jumps++; P.onGround=false; P.coyoteTime=0; P.jumpBuffer=0;
  Particles.spawn(jx, jy, '#8a7d6b', 5);
}
// ... etc
```

**Simplified:** Factor out common `P.jumpBuffer=0` to an outer scope (it's set in 3 of 4 branches). The first two branches share nearly identical post-jump state:

```js
function applyJump(vel, color, count) {
  P.vy = vel; P.jumps++; P.onGround=false; P.coyoteTime=0; P.jumpBuffer=0;
  Particles.spawn(jx, jy, color, count);
}
```

**Estimated savings: ~12 lines.**

### 5. Consolidate X-Collision Resolution (Lines 1043–1064)

**Current:** Two branches (dash vs normal) that both end with `snapToTileX(gx1, gx2, prevX); P.vx=0;`:

```js
if(P.dashPhase){
  // ... check cracked tile ...
  } else {
    snapToTileX(gx1, gx2, prevX); P.vx=0;
  }
} else {
  snapToTileX(gx1, gx2, prevX); P.vx=0;
}
```

**Simplified:** Move `snapToTileX + P.vx=0` to the default path:

```js
let crashed = false;
if(P.dashPhase && _getTile(fcx,fcy)===CRACKED && P.canBreak){
  setTile(P.chamber,fcx,fcy,AIR); Particles.shatter(...); endDash(); P.vx=0;
  crashed = true;
}
if(!crashed){ snapToTileX(gx1, gx2, prevX); P.vx=0; }
```

**Estimated savings: ~3 lines.**

---

## Redundancy Elimination

### 1. Message Queue Advancement Duplicated in `update()` and `updateAnim()` (Lines 953, 1166–1175)

**Current:** Exact same message queue logic appears in two functions:

```js
// In update() line 953:
if(messageQueue.length>0){const m=messageQueue[0];m.elapsed++;if(m.phase==='fadeIn'&&m.elapsed>=MSG_FADE_IN_FRAMES){m.phase='display';m.elapsed=0;}else if(m.phase==='display'&&m.elapsed>=m.hold){m.phase='fadeOut';m.elapsed=0;}else if(m.phase==='fadeOut'&&m.elapsed>=MSG_FADE_OUT_FRAMES){messageQueue.shift();}}

// In updateAnim() lines 1166-1175:
if(messageQueue.length>0){
  const m=messageQueue[0]; m.elapsed++;
  if(m.phase==='fadeIn' && m.elapsed>=MSG_FADE_IN_FRAMES){ m.phase='display'; m.elapsed=0; }
  else if(m.phase==='display' && m.elapsed>=m.hold){ m.phase='fadeOut'; m.elapsed=0; }
  else if(m.phase==='fadeOut' && m.elapsed>=MSG_FADE_OUT_FRAMES){ messageQueue.shift(); }
}
```

**Consolidate:** Extract to `advanceMessageQueue()` and call from both. **Saves ~8 lines.**

### 2. prevKeys Copy Duplicated in `update()` and `updateAnim()` (Lines 1156–1157, 1196–1197)

**Current:**

```js
// In update() line 1156-1157:
for(const k in keys) prevKeys[k]=keys[k];
for(const k in prevKeys) if(!keys[k]) delete prevKeys[k];

// In updateAnim() line 1196-1197:
for(const k in keys) prevKeys[k]=keys[k];
for(const k in prevKeys) if(!keys[k]) delete prevKeys[k];
```

**Consolidate:** Extract to `syncPrevKeys()` and call from both. **Saves ~4 lines.**

### 3. Portal Lock Message Decrement Duplicated (Lines 954, 1177)

**Current:** `if(portalLockMsg>0) portalLockMsg--;` appears in both `update()` and `updateAnim()`.

**Consolidate:** Add to the shared `advanceMessageQueue()` or a general `advanceTimers()` helper. **Saves ~2 lines.**

### 4. Glyph Ability Unlock Uses Hardcoded If-Else Chain (Lines 898–901)

**Current:**

```js
if(glyphsCollected===1){ P.maxJumps=2; showMessage("Knowledge lifts me.",120); }
else if(glyphsCollected===2){ P.canDash=true; showMessage("Speed courses through me.",120); }
else if(glyphsCollected===3){ P.canPush=true; showMessage("Strength returns.",120); }
else if(glyphsCollected===4){ P.canBreak=true; showMessage("Clay becomes Wisdom.",120); }
```

**Consolidate:** Data-driven lookup:

```js
const GLYPH_EFFECTS = [
  { set: () => { P.maxJumps=2; }, msg: "Knowledge lifts me." },
  { set: () => { P.canDash=true; }, msg: "Speed courses through me." },
  { set: () => { P.canPush=true; }, msg: "Strength returns." },
  { set: () => { P.canBreak=true; }, msg: "Clay becomes Wisdom." },
];
// ...
const gx = glyphsCollected - 1;
if(gx >= 0 && gx < GLYPH_EFFECTS.length){
  GLYPH_EFFECTS[gx].set();
  showMessage(GLYPH_EFFECTS[gx].msg, 120);
}
```

**No line savings** (slightly longer), but makes adding glyphs zero-risk and removes the hardcoded chain entirely.

### 5. Player Center + Grid Conversion Pattern (Lines 516–517, 849–850, 887–888)

**Current:** Three places compute player center to grid coordinates:

```js
// inPit(): line 516-517
const px=P.x+P.w/2, py=P.y+P.h/2;
const gx=Math.floor(px/T), gy=Math.floor(py/T);

// checkDoors(): line 849-850
const px=P.x+P.w/2, py=P.y+P.h/2;
const gx=Math.floor(px/T), gy=Math.floor(py/T);

// checkGlyphs(): line 887-888
const px=P.x+P.w/2, py=P.y+P.h/2;
const gx=Math.floor(px/T), gy=Math.floor(py/T);
```

**Consolidate:** Extract `playerGridPos()` helper:

```js
function playerGridPos() {
  return { gx: Math.floor((P.x+P.w/2)/T), gy: Math.floor((P.y+P.h/2)/T) };
}
```

**Saves ~3 lines** (6 lines -> 1 helper + 3 call sites).

### 6. Neighbor Tile Scan Pattern (Lines 519–525, 851–881, 889–902)

**Current:** Three functions (`inPit`, `checkDoors`, `checkGlyphs`) all iterate a 3x3 neighborhood around the player center. The loop structure is identical:

```js
for(let dy=-1;dy<=1;dy++) for(let dx=-1;dx<=1;dx++){
  // ... check tile at (gx+dx, gy+dy)
}
```

**Consolidate:** Extract `scanNeighborTiles(callback)` that yields each neighbor's grid coordinates and tile value. Each caller provides only its check logic. This is a **bigger refactor** with more risk but eliminates the repeated iteration pattern.

---

## Performance Hotspots

### 1. prevKeys Cleanup Iterates All Keys Per Frame (Lines 1156–1157, 1196–1197)

**Current:** `for(const k in prevKeys) if(!keys[k]) delete prevKeys[k];` runs every frame in both `update()` and `updateAnim()`. As keys are added (any keydown), `prevKeys` accumulates all ever-pressed keys.

**Cost:** O(n) iteration + property deletion on every frame, where n = total distinct keys ever pressed.

**Optimized:** Replace with a single-frame snapshot approach:

```js
// At start of update: prevKeys = { ...keys };  (spread copy, O(active keys only))
```

Or simpler: use `prevKeys = Object.assign({}, keys)` which avoids deletions entirely. The `fresh()` function only checks keys that were just pressed, so stale entries don't affect correctness — but deletions still happen in `prevKeys`.

**Alternative (minimal change):** Only delete on keyup events instead of iterating per frame:

```js
document.addEventListener('keyup', function(e){
  keys[e.code] = false;
  delete prevKeys[e.code];  // remove stale entry immediately
});
```

Then the per-frame cleanup becomes just `for(const k in keys) prevKeys[k]=keys[k];` (no delete loop).

### 2. Particle Removal Uses `splice` on Active Array (Line 798)

**Current:** `pool.splice(i,1)` inside a reverse-iterating loop. While reverse iteration avoids index shifting issues, `splice` still does memory operations.

**Cost:** Each frame during particle-heavy moments, multiple splice calls.

**Optimized:** Use a compact-after-dead pattern:

```js
let w = 0;
for(let r = 0; r < pool.length; r++){
  const p = pool[r];
  p.x += p.vx; p.y += p.vy; p.vy += 0.1; p.life--;
  if(p.life > 0) pool[w++] = p;
}
pool.length = w;
```

No splice, single pass, cache-friendly. **Marginal gain** given particle counts are small (<50 at any time).

### 3. Collision Functions Allocate Options Objects (Lines 495–497)

**Current:** `collides()` creates a new object every frame:

```js
function collides(gx1,gy1,gx2,gy2,ch,prevY,curY) {
  return tileCollidesRect(ch, gx1, gy1, gx2, gy2, {includePlatforms:true, prevY, curY});
}
```

**Cost:** One object allocation per Y-collision check (called every frame during player Y movement).

**Optimized:** Pass parameters directly instead of through an object:

```js
function tileCollidesRect(ch, gx1, gy1, gx2, gy2, skipTileType, includePlatforms, prevFeet) {
  for(let gy=gy1;gy<=gy2;gy++)
    for(let gx=gx1;gx<=gx2;gx++){
      const t = getTile(ch,gx,gy);
      if(skipTileType && t === skipTileType) continue;
      if(solid(t)) return true;
      if(includePlatforms && platSolid(t, prevFeet, gy)) return true;
    }
  return false;
}
```

**Saves ~1 allocation per frame.** Minor but adds up over a 60fps run.

### 4. Dash Charge Indicator Repeated Math (Lines 1508, 1618)

**Current:** `P.dashCharge / DASH_CHARGE_MAX` computed in both the in-world indicator (line 1508) and HUD bar (line 1618).

**Optimized:** Compute once in render at the top:

```js
const dashChargeRatio = P.dashCharge ? P.dashCharge / DASH_CHARGE_MAX : 0;
```

**Saves 1 division per frame when charging.** Trivial.

---

## Dead Code and Unused Features

### 1. `easeInOutCubic` (Line 101) — **DEAD**

```js
function easeInOutCubic(t) { return t < 0.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2; }
```

Defined but **never called** anywhere in the file. Only `easeOutCubic` is used (lines 1222, 1279).

**Savings: 1 line removed.**

### 2. `easeOutBack` (Line 102) — **DEAD**

```js
function easeOutBack(t) { const c1=1.70158; const c3=c1+1; return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2); }
```

Defined but **never called** anywhere in the file.

**Savings: 1 line removed.**

### 3. `collidesNoPlat` Signature (Lines 500–502) — **PARTIALLY REDUNDANT**

```js
function collidesNoPlat(gx1,gy1,gx2,gy2,ch) {
  return tileCollidesRect(ch, gx1, gy1, gx2, gy2, {});
}
```

This passes an empty options object `{}` to `tileCollidesRect`. While it IS called (line 1046), the empty object allocation is wasteful. The function itself is needed since `collidesDash` and `collides` have different behaviors. **No removal, but could optimize** (see Performance #3).

### 4. `solidTiles` Maintenance in `setTile` (Lines 456–460) — **POTENTIALLY UNUSED**

```js
if(old!==AIR && v===AIR){
  const idx=c.solidTiles.findIndex(t=>t.x===x&&t.y===y);
  if(idx>=0) c.solidTiles.splice(idx,1);
} else if(old===AIR && v!==AIR){
  c.solidTiles.push({x,y});
}
```

`setTile` is called only twice: glyph collection (line 894) and cracked tile breaking (line 1051). Both set a tile to `AIR`. The `solidTiles` array is built once at init (line 1710) and used during rendering (line 1373). If a tile is removed via `setTile`, the `solidTiles` list gets stale — the next frame would try to render a tile at a position that's now `AIR`.

**However:** The render loop reads `c.tiles[y][x]` from the actual grid and checks against tile constants. If the tile at that position is `AIR`, the render loop still iterates the `solidTiles` entry but the `if(t===WALL)` and subsequent checks won't match `AIR`. So the render still works, but draws nothing — meaning the `solidTiles` maintenance code **is redundant** since the actual grid is the source of truth during render.

**Savings: ~6 lines removed from `setTile`, simplifying it to just `c.tiles[y][x]=v;`.**

### 5. `_testMode` Global (Line 408) — **DEAD (UNUSED)**

```js
let _testMode = false;             // set by test harness for instant transitions
```

This is never set to `true` anywhere in the file. It's referenced in `transition()` (line 841) and `transitionEnding()` (line 908) as a guard, but since it's always `false`, those branches are dead code paths.

**Savings: ~6 lines** (the variable + two if-checks + their immediate returns).

### 6. Tile Type Value 6 Gap — **NOT DEAD BUT NOTEWORTHY**

The comment in the reference says value 6 (BLOCK) was removed. The constants skip from GLYPH=5 to CRACKED=7. This is intentional and fine — no action needed, but documented here for awareness.

---

## Future-Proofing Opportunities

### 1. Glyph/Ability Data-Driven System

**Current:** Abilities are hardcoded in `checkGlyphs()` (lines 898–901) and the `ABILITIES` array (line 71) is manually synced.

**Recommendation:** Single source of truth:

```js
const GLYPH_DEFS = [
  { name: 'Double Jump', key: '[1] Double Jump', effect: () => { P.maxJumps=2; }, msg: "Knowledge lifts me." },
  { name: 'Dash', key: '[2] Dash (Shift)', effect: () => { P.canDash=true; }, msg: "Speed courses through me." },
  { name: 'Push Blocks', key: '[3] Push Blocks', effect: () => { P.canPush=true; }, msg: "Strength returns." },
  { name: 'Break Cracked', key: '[4] Break Cracked', effect: () => { P.canBreak=true; }, msg: "Clay becomes Wisdom." },
];
```

Generate `ABILITIES` and `checkGlyphs` logic from this. Adding a 5th ability requires only adding one entry to the array.

**Impact: Zero behavioral change, ~10 lines net.**

### 2. Chamber Boundary Helper

**Current:** Each chamber manually draws boundaries with loops (e.g., lines 124–128):

```js
for(let x=0;x<w;x++){g[14][x]=WALL;g[0][x]=WALL;}
for(let y=0;y<h;y++){g[y][0]=WALL;}
for(let y=0;y<2;y++){g[y][w-1]=WALL;}
// ... custom right-side gaps
```

**Recommendation:** A `drawBorder(g, w, h, gaps)` helper that fills all edges except specified gap ranges:

```js
function drawBorder(g, w, h, {top=[], bottom=[], left=[], right=[]}) {
  for(let x=0;x<w;x++){
    if(!bottom.includes(x)) g[h-1][x]=WALL;
    if(!top.includes(x)) g[0][x]=WALL;
  }
  for(let y=0;y<h;y++){
    if(!left.includes(y)) g[y][0]=WALL;
    if(!right.includes(y)) g[y][w-1]=WALL;
  }
}
```

This is a **bigger refactor** — many chambers have non-trivial right-side boundaries. Best left as a future improvement rather than a quick optimization.

### 3. Tile Collision Configuration Object

**Current:** `solid()` function (line 471) hardcodes which tiles are solid:

```js
function solid(t){ return t===WALL||t===CRACKED||t===DOOR_D||t===END_PORTAL||t===MAGICAL_WALL; }
```

**Recommendation:** A `TILE_PROPS` map:

```js
const TILE_PROPS = {
  [WALL]: { solid: true, passDash: false },
  [CRACKED]: { solid: true, breakable: true },
  [DOOR_D]: { solid: true },
  [END_PORTAL]: { solid: true },
  [MAGICAL_WALL]: { solid: true, passDash: true },
  [PLATFORM]: { solid: false, oneWay: true },
};
function solid(t){ return TILE_PROPS[t]?.solid ?? false; }
```

Adding new tile types (e.g., `ICE`, `TRAMPOLINE`) requires only adding one entry to the map.

**Impact: ~5 lines net growth, but makes adding tile types trivial.**

### 4. Push Block Slot System Hardcoded

**Current:** The pushSlot check (lines 726–737) assumes a single `c.pushSlot` per chamber. Only chamber 3 uses it. The `resetPushBlock` function handles `pushSpawns` (array) vs `pushSpawn` (single) inconsistently:

```js
const spawns=c.pushSpawns||(c.pushSpawn?[c.pushSpawn]:null);
```

**Recommendation:** Standardize chambers to always use `pushSpawns` array and `pushSlots` array (empty if none). Chamber 2 currently uses `pushSpawn` (singular) — should be `pushSpawns: [{x:6,y:8}]`.

**Impact: Makes chamber data structure uniform.**

### 5. Glyph Collection Uses Chamber Index as Progress Gate

**Current:** `checkGlyphs()` (line 893) enforces sequential collection:

```js
if(glyphsCollected!==ch) continue;
```

This means chamber `i` can only be collected if exactly `i` glyphs have been collected before. If chambers are reordered via `CHAMBER_FLOW`, this breaks.

**Recommendation:** Use `glyphsCollected !== CHAMBER_FLOW.indexOf(c.flowId)` or a chamber-specific `glyphId` field. This ensures the gate follows the flow order, not array index.

---

## Estimated Impact Summary

| Optimization | Lines Saved | Complexity Reduction | Risk Level | Category |
|-------------|-------------|----------------------|------------|----------|
| Remove `easeInOutCubic`, `easeOutBack` | 2 | None | None | Quick Win |
| Extract message queue advancement | 8 | Moderate | Low | Quick Win |
| Extract prevKeys sync | 4 | Low | None | Quick Win |
| Remove `_testMode` dead code | ~6 | Low | None | Quick Win |
| Simplify `setTile` (remove solidTiles maintenance) | 6 | Moderate | Low | Quick Win |
| Consolidate dash state reset helper | ~8 | Moderate | Low | Quick Win |
| Merge respawn reset lines (1183, 1189) | ~5 | Low | None | Quick Win |
| Extract playerGridPos helper | ~3 | Low | None | Quick Win |
| Fix prevKeys delete-on-keyup approach | 2 | Moderate | Low | Performance |
| Glyph/ability data-driven system | ~0 (net) | High | Low | Future-Proofing |
| Tile collision config map | ~5 (net growth) | High | Low | Future-Proofing |
| Simplify jump logic | ~12 | Moderate | Low | Medium |
| Simplify X-collision resolution | ~3 | Low | None | Quick Win |
| Remove options object allocation in collisions | 0 | Low | Low | Performance |

**Total direct line savings (quick wins): ~46 lines**
**Total with medium-effort optimizations: ~60 lines**

---

## Recommended Priority Order

### Priority 1: Remove Dead Code (easeInOutCubic, easeOutBack, _testMode)
- **Why:** Zero risk, immediate savings, cleans up confusion
- **Effort:** 5 minutes
- **Impact:** 8 lines saved, removes unused API surface

### Priority 2: Extract Duplicated Helpers (messageQueue, prevKeys, portalLockMsg)
- **Why:** These three are copy-pasted between `update()` and `updateAnim()` — fixing them eliminates the duplication entirely
- **Effort:** 15 minutes
- **Impact:** ~14 lines saved, reduces risk of future desync between the two update paths

### Priority 3: Consolidate Dash Reset + Player Reset Patterns
- **Why:** 5 sites of dash state reset with inconsistent fields is a maintenance hazard; a helper ensures consistency
- **Effort:** 20 minutes
- **Impact:** ~15 lines saved, eliminates risk of missing a dash field on reset

### Priority 4 (Future): Glyph/Ability Data-Driven System
- **Why:** Every new ability currently requires touching 3+ places (ABILITIES array, checkGlyphs chain, potentially HUD). Making this data-driven turns ability addition into a one-line change.
- **Effort:** 30 minutes
- **Impact:** Zero line savings, but transforms extensibility from O(n) file edits to O(1) data entry
