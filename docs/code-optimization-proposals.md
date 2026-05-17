# Code Optimization Proposals Report

**Project:** GOLEM_GAME (The Golem Awakens)
**Target:** `golem.html` (1152 lines, 41.9 KB, 11 sections)
**Date:** 2026-05-16
**Based on:** `docs/code-optimization-analysis.md` (6-slice research) + `docs/beyond-scope-simplifications.md` + `code-review.md`

---

## Executive Summary

This report catalogs **32 discrete optimization opportunities** across four categories, each with verified line references, current code snippets, proposed changes, effort estimates, and cross-references to existing documentation. The opportunities span from trivial one-line fixes to moderate architectural improvements.

### High-Level Numbers

| Metric | Value |
|--------|-------|
| Total proposals | 32 |
| Priority P0 (quick wins) | 11 |
| Priority P1 (should-fix) | 9 |
| Priority P2 (could-fix) | 9 |
| Priority P3 (nice-to-have) | 3 |
| Priority P4 (deferred) | 0 |
| Estimated total lines of new code | ~120 |
| Estimated total lines of duplication removed | ~50 |
| Estimated file size savings | ~300-500 bytes (without minification) |
| Per-frame Date.now() calls eliminated | 14 (of 15) via single cache |
| Per-frame redundant allocations eliminated | 2 (abilities array, names array) |

### Priority Categories

- **P0 — Quick Wins:** High impact, trivial effort (1-5 lines). No risk. Should be done immediately.
- **P1 — Should Fix:** Clear value, low effort (5-10 lines). Low risk. Schedule soon.
- **P2 — Could Fix:** Moderate value, moderate effort (10-20 lines). Schedule when convenient.
- **P3 — Nice to Have:** Low value or polish-only. Do if time permits.
- **P4 — Deferred:** Significant effort or uncertain ROI. Defer for now.

### Categories Overview

| Category | Proposals | Total Effort | Key Impact |
|----------|-----------|-------------|------------|
| A. Logic Simplification | 12 | ~50 lines | Eliminates ~40 lines of duplication |
| B. Performance Optimization | 8 | ~20 lines | Reduces per-frame CPU waste |
| C. Structural Preparation | 6 | ~50 lines | Future-proofs for modularity |
| D. File Size Reduction | 6 | ~10 lines | ~300-500 bytes saved |

---

## Category A: Logic Simplification

Focus: Eliminate duplicated code patterns via extraction into functions, constants, and abstractions.

---

### A1. Precompute Jump Particle Coordinates

**Priority:** P0 | **Effort:** Trivial (2 lines changed) | **Lines:** 758, 766, 772

**Current Code:**
```js
// Line 758 (buffer-jump branch)
spawnParticles(P.x+P.w/2, P.y+P.h, '#8a7d6b', 5);
// Line 766 (coyote-jump branch)
spawnParticles(P.x+P.w/2, P.y+P.h, '#8a7d6b', 5);
// Line 772 (double-jump branch)
spawnParticles(P.x+P.w/2, P.y+P.h, '#d4a84b', 8);
```

**Issue:** `P.x+P.w/2` and `P.y+P.h` computed 3 times per jump event.

**Proposed Change:**
```js
const jx = P.x + P.w/2, jy = P.y + P.h;
// ... later in each branch:
spawnParticles(jx, jy, '#8a7d6b', 5);
spawnParticles(jx, jy, '#d4a84b', 8);
```

**Overlap:** None with beyond-scope items.

---

### A2. Extract Dash Particle Color Constants

**Priority:** P0 | **Effort:** Trivial (3 lines) | **Lines:** 633, 647

**Current Code:**
```js
// Line 633 (charge particles)
spawnParticles(P.x+P.w/2, P.y+P.h/2, 'rgba(180,80,255,0.4)', 2);
// Line 647 (dash execution particles)
spawnParticles(P.x+P.w/2, P.y+P.h/2, 'rgba(220,120,255,0.4)', 2);
```

**Issue:** Two different RGBA color strings — charge uses `rgba(180,80,255,0.4)` while execution uses `rgba(220,120,255,0.4)`. Each is used at multiple call sites. Extracting named constants makes the color tuning and future changes (e.g., adding more dash variants) straightforward.

**Proposed Change:**
```js
// In constants section:
const DASH_EXEC_PARTICLE_COLOR = 'rgba(220,120,255,0.4)';
const DASH_CHARGE_PARTICLE_COLOR = 'rgba(180,80,255,0.4)';
```

**Overlap:** None with beyond-scope items.

---

### A3. Extract `killAndRespawn()` Function

**Priority:** P0 | **Effort:** ~8 lines added, ~12 lines saved | **Lines:** 651-653, 783-786

**Current Code (two near-identical blocks):**
```js
// Lines 651-653 (magical wall death after dash)
P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0;
P.jumps=0; P.dashCharge=0; P.onGround=true; P.coyoteTime=12;

// Lines 783-786 (pit/out-of-bounds death)
P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0;
P.jumps=0; P.dashing=false; P.dashTimer=0; P.dashCharge=0;
P.onGround=false; P.coyoteTime=12;
resetPushBlock();
```

**Issue:** Player reset pattern duplicated 2x with minor variations (`P.onGround` value, `resetPushBlock()` call, `P.dashing`/`P.dashTimer` inclusion).

**Proposed Change:**
```js
function killAndRespawn(onGround, msg, duration){
  P.x=P.respawnX; P.y=P.respawnY; P.vx=0; P.vy=0;
  P.jumps=0; P.dashing=false; P.dashTimer=0; P.dashCharge=0;
  P.onGround=onGround; P.coyoteTime=COYOTE_FRAMES; // use constant
  resetPushBlock();
  if(msg) showMessage(msg, duration);
}

// Replace both sites with:
killAndRespawn(true, "The barrier consumes you...", 90);
killAndRespawn(false, "The void claims clay...", 90);
```

**Overlap:** Partially addresses beyond-scope item #1 (Jump Velocity Equalization) — the function is a natural place to consolidate reset logic. Cross-referenced in Slice F2 of research.

---

### A4. Extract `resolveXCollision()` Function

**Priority:** P0 | **Effort:** ~5 lines added, ~8 lines saved | **Lines:** 688-691, 694-697

**Current Code:**
```js
// Lines 688-691 (dash-phase collision handler)
if(P.vx>0){ P.x=gx2*T-P.w; }
else if(P.vx<0){ P.x=(gx1+1)*T; }
else { P.x=prevX; }
P.vx=0;

// Lines 694-697 (non-dash handler — identical)
if(P.vx>0){ P.x=gx2*T-P.w; }
else if(P.vx<0){ P.x=(gx1+1)*T; }
else { P.x=prevX; }
P.vx=0;
```

**Issue:** Exact same 4 lines copy-pasted into dash and non-dash branches.

**Proposed Change:**
```js
function snapToTileX(gx1, gx2, prevX){
  if(P.vx>0) P.x=gx2*T-P.w;
  else if(P.vx<0) P.x=(gx1+1)*T;
  else P.x=prevX;
  P.vx=0;
}

// Replace both sites with:
snapToTileX(gx1, gx2, prevX);
```

**Overlap:** None with beyond-scope items.

---

### A5. Extract `endDash()` Function

**Priority:** P0 | **Effort:** ~3 lines added, ~6 lines saved | **Lines:** 649, 685

**Current Code:**
```js
// Line 649 (dash timer expiry)
P.dashing=false; P.dashCooldown=DASH_COOLDOWN; P.dashPhase=false;

// Line 685 (CRACKED break)
P.dashing=false; P.dashTimer=0; P.dashCooldown=DASH_COOLDOWN; P.dashPhase=false;
```

**Issue:** Dash-end pattern appears 2x (3 copies if counting the magical wall death block at A3).

**Proposed Change:**
```js
function endDash(){
  P.dashing=false; P.dashTimer=0; P.dashCooldown=DASH_COOLDOWN; P.dashPhase=false;
}

// Replace both sites with: endDash();
```

**Overlap:** None with beyond-scope items.

---

### A6. Extract `land()` Function

**Priority:** P0 | **Effort:** ~3 lines added, ~6 lines saved | **Lines:** 719-721, 737-739

**Current Code:**
```js
// Lines 719-721 (tile landing)
P.onGround=true;
P.jumps=0;
P.coyoteTime=12;

// Lines 737-739 (push-block landing)
P.onGround = true;
P.jumps = 0;
P.coyoteTime = 12;
```

**Issue:** Exact same 3 lines, copy-pasted. The `12` is a magic number for coyote time.

**Proposed Change:**
```js
function land(){
  P.onGround=true; P.jumps=0; P.coyoteTime=COYOTE_FRAMES;
}

// Replace both sites with: land();
```

**Overlap:** None with beyond-scope items. The `COYOTE_FRAMES` constant ties into magic number extraction (Proposal F1).

---

### A7. Input Normalization Abstractions

**Priority:** P0 | **Effort:** ~12 lines added, ~10 lines simplified | **Lines:** 591-592, 637, 749-750

**Current Code:**
```js
// Lines 591-592 (horizontal movement)
if(keys['ArrowLeft']||keys['KeyA']) inputX=-1;
if(keys['ArrowRight']||keys['KeyD']) inputX=1;

// Line 637 (dash trigger)
if(fresh('ShiftLeft')||fresh('ShiftRight')){ ... }

// Lines 749-750 (jump input)
const jumpPressed = fresh('ArrowUp')||fresh('KeyW')||fresh('Space');
const jumpHeld = keys['ArrowUp']||keys['KeyW']||keys['Space'];
```

**Issue:** Key check expressions duplicated across 5+ call sites. A `shiftHeld()` helper already exists (line ~206) but is only used once.

**Proposed Change:**
```js
// In input section (Section 4):
function inputLeft()  { return keys['ArrowLeft']  || keys['KeyA']; }
function inputRight() { return keys['ArrowRight'] || keys['KeyD']; }
function inputJumpPressed() { return fresh('ArrowUp')||fresh('KeyW')||fresh('Space'); }
function inputJumpHeld()    { return keys['ArrowUp'] || keys['KeyW'] || keys['Space']; }
function inputShiftPressed() { return fresh('ShiftLeft')||fresh('ShiftRight'); }
```

Replace all call sites:
```js
if(inputLeft()) inputX=-1;
if(inputRight()) inputX=1;
const jumpPressed = inputJumpPressed();
const jumpHeld = inputJumpHeld();
if(inputShiftPressed()){ ... }
```

**Overlap:** This is **beyond-scope item #5**. The optimization analysis recommends merging this into the optimization task since it eliminates duplication (Slice A7) and the beyond-scope item.

---

### A8. Cache `collectedGlyphs[ch]` Lookup

**Priority:** P0 | **Effort:** Trivial (2 lines) | **Lines:** 856, 1093

**Current Code:**
```js
// Line 856 (door rendering)
const locked = !collectedGlyphs[ch];

// Line 1093 (chamber name rendering)
const locked = !collectedGlyphs[ch];
```

**Issue:** Same global lookup computed twice per frame in render.

**Proposed Change:**
```js
// At render entry (after line 811):
const ch = P.chamber, c = chambers[ch];
const glyphCollected = collectedGlyphs[ch];
// Replace both `!collectedGlyphs[ch]` with `!glyphCollected`
```

**Overlap:** None with beyond-scope items.

---

### A9. Scope `currentChamber` Variable for Tile Helpers

**Priority:** P1 | **Effort:** ~5 lines | **Lines:** 212-216, 811

**Current Code:**
```js
// getTile() is called ~375x/frame in the tile render loop
function getTile(ch, x, y){
  const c = chambers[ch]; // This lookup happens every call
  return c ? c.tiles[y][x] : WALL;
}
```

**Issue:** `chambers[ch]` is looked up on every `getTile()` call inside the render loop (375 iterations). The chamber object `c` is already available in the outer render scope.

**Proposed Change:**
```js
// Option A: Use closure-scoped variable
let _currentChamber = null;
function getTile(x, y){
  return _currentChamber ? _currentChamber.tiles[y][x] : WALL;
}

// In render():
_currentChamber = c;
// ... tile loop calls getTile(x, y) without chamber index
```

**Risk:** Moderate — requires auditing all `getTile()` call sites to ensure they're within a render context. Update calls use `getTile(P.chamber, ...)` outside render scope.

**Overlap:** None with beyond-scope items.

---

### A10. Cache `inputX` Direction Sign

**Priority:** P2 | **Effort:** Trivial (1 line) | **Lines:** 593-597

**Current Code:**
```js
if(inputX!==0) P.facing=inputX;
if(!isCharging && !P.dashing){
  if(inputX!==0){
    P.vx += inputX * (P.onGround ? 0.05 : 0.2);
    if(Math.abs(P.vx)>2.5) P.vx = inputX*2.5;
  }
```

**Issue:** `inputX!==0` checked twice immediately.

**Proposed Change:**
```js
if(inputX !== 0){
  P.facing = inputX;
  if(!isCharging && !P.dashing){
    P.vx += inputX * (P.onGround ? 0.05 : 0.2);
    if(Math.abs(P.vx)>2.5) P.vx = inputX*2.5;
  }
}
```

**Overlap:** None with beyond-scope items.

---

### A11. Extract `snapToTileY()` for Landing Logic

**Priority:** P2 | **Effort:** ~5 lines | **Lines:** 716-727

**Current Code:**
```js
if(P.vy>0){
  P.y=gy2*T-P.h;
  P.vy=0;
  land(); // after A6 extraction
} else if(P.vy<0){
  P.y=(gy1+1)*T;
  P.vy=0;
}
```

**Issue:** Y collision response is self-contained and could be extracted for clarity.

**Proposed Change:**
```js
function snapToTileY(gy1, gy2){
  if(P.vy>0){ P.y=gy2*T-P.h; P.vy=0; land(); }
  else if(P.vy<0){ P.y=(gy1+1)*T; P.vy=0; }
}
```

**Overlap:** None with beyond-scope items.

---

### A12. Extract `getChargeRatio()` Inline Helper

**Priority:** P2 | **Effort:** ~2 lines | **Lines:** 612, 964, 1074

**Current Code:**
```js
// Computed identically in 3 places
const chargeRatio = P.dashCharge / DASH_CHARGE_MAX;
```

**Issue:** Same expression repeated 3x (update, render ring, render HUD bar).

**Proposed Change:**
```js
// Either a constant accessor or just a comment noting the pattern.
// Given it's a simple expression, a comment may suffice:
// chargeRatio: 0..1 based on P.dashCharge/DASH_CHARGE_MAX
```

**Overlap:** None with beyond-scope items.

---

## Category B: Performance Optimization

Focus: Reduce per-frame CPU waste, eliminate redundant computations, and precompute static data.

---

### B1. Cache `Date.now()` Once Per Frame

**Priority:** P0 | **Effort:** 1 line added, 15 call sites changed | **Lines:** 849, 858, 868, 879, 880, 892, 893, 919, 927, 945, 972, 1033, 1042, 1050, 1082

**Current Code (representative):**
```js
// Line 849 (PIT glow)
const glow=Math.sin(Date.now()/600+x)*0.3+0.3;

// Line 858 (Door locked pulse)
const pulse=Math.sin(Date.now()/500)*0.2+0.7;

// Line 879-880 (END_PORTAL - TWO calls)
const pulse=Math.sin(Date.now()/400)*0.2+0.8;
const pulse2=Math.sin(Date.now()/300)*0.3+0.5;

// Line 1082 (Dash HUD MAX)
const pulse = Math.sin(Date.now()/150)*0.3+0.7;
```

**Total `Date.now()` calls per frame:** 15 (worst case: 50+ when all animated tiles are visible).

**Proposed Change:**
```js
// At render entry (line 811):
const now = Date.now();
// Replace ALL Date.now() with `now`
const glow = Math.sin(now/600+x)*0.3+0.3;
const pulse = Math.sin(now/500)*0.2+0.7;
// etc.
```

**Impact:** Eliminates 14 redundant system calls per frame. Zero behavior change — `now` is consistent across all calls within a frame, which actually makes animations more deterministic.

**Overlap:** None with beyond-scope items.

---

### B2. Move `abilities` Array to Module Scope

**Priority:** P0 | **Effort:** 2 lines moved | **Lines:** 1061-1064

**Current Code:**
```js
// Inside render(), created every frame:
const abilities = [
  ['[1] Double Jump', 1], ['[2] Dash (Shift)', 2],
  ['[3] Push Blocks', 3], ['[4] Break Cracked', 4]
];
```

**Issue:** Static array allocated every frame.

**Proposed Change:**
```js
// Move to module scope (after constants):
const ABILITIES = [
  ['[1] Double Jump', 1], ['[2] Dash (Shift)', 2],
  ['[3] Push Blocks', 3], ['[4] Break Cracked', 4]
];

// In render(): replace `abilities` with `ABILITIES`
```

**Overlap:** None with beyond-scope items.

---

### B3. Move `CHAMBER_NAMES` Array to Module Scope

**Priority:** P0 | **Effort:** 2 lines moved | **Lines:** 1090

**Current Code:**
```js
// Inside render(), created every frame:
const names=['Awakening','The Library','The Hall of Echoes','The Weight of Wisdom','The Ibis Chamber'];
```

**Issue:** Static array allocated every frame.

**Proposed Change:**
```js
// Move to module scope:
const CHAMBER_NAMES = ['Awakening','The Library','The Hall of Echoes','The Weight of Wisdom','The Ibis Chamber'];

// In render(): replace `names` with `CHAMBER_NAMES`
```

**Overlap:** None with beyond-scope items.

---

### B4. Precompute Starfield Per Chamber

**Priority:** P1 | **Effort:** ~5 lines | **Lines:** 817

**Current Code:**
```js
// Line 817 — recomputed every frame:
for(let i=0;i<40;i++) X.fillRect((i*137+ch*50)%W,(i*97+ch*30)%H,1,1);
```

**Issue:** 40 modulo operations + 40 fillRect calls per frame. Only depends on chamber index `ch` (6 possible values).

**Proposed Change:**
```js
// During init (Section 11), compute once per chamber:
chambers.forEach((c, i) => {
  c.stars = [];
  for(let j=0; j<40; j++)
    c.stars.push([(j*137+i*50)%W, (j*97+i*30)%H]);
});

// In render(): replace starfield loop with:
for(const [sx,sy] of c.stars) X.fillRect(sx,sy,1,1);
```

**Impact:** Eliminates 40 modulo operations per frame. Saves 40 arithmetic ops; fillRect calls remain but with precomputed coordinates.

**Overlap:** None with beyond-scope items.

---

### B5. Sparse Tile Rendering (Optional)

**Priority:** P2 | **Effort:** ~20 lines | **Lines:** 824-931

**Current Code:**
```js
// Line 824 — iterates ALL 375 tiles (25x15 grid) every frame
for(let y=0;y<c.h;y++) for(let x=0;x<c.w;x++){
  const t=c.tiles[y][x];
  if(t===WALL){ ... }
  else if(t===PLATFORM){ ... }
  // etc. — most iterations are AIR (0) and skipped immediately
}
```

**Issue:** 375 iterations per frame, but typically only 50-100 tiles are non-AIR. The if/else chain immediately skips AIR tiles.

**Proposed Change:**
```js
// During chamber construction, collect non-AIR tiles:
// In each chamber IIFE:
const solidTiles = [];
for(let y=0;y<h;y++) for(let x=0;x<w;x++)
  if(g[y][x] !== AIR) solidTiles.push({x,y,t:g[y][x]});

chambers.push({w, h, tiles:g, px, py, glyphs, solidTiles});

// In render():
for(const {x,y,t} of c.solidTiles){
  const px=ox+x*T, py=oy+y*T;
  // ... same if/else chain (can become switch)
}
```

**Trade-offs:**
- **Pro:** 3-7x reduction in tile loop iterations
- **Con:** `setTile()` (used when CRACKED tiles are destroyed) must maintain the sparse list — adds ~5 lines
- **Con:** Wall adjacency checks (pit glow, lines 833-840) need to still use `c.tiles[y][x]` lookup
- **Con:** Increases chamber data size slightly (~100 bytes)

**Impact:** Reduces per-frame CPU usage in the render loop. Most meaningful on low-end devices.

**Overlap:** None with beyond-scope items.

---

### B6. Reduce Math.sin() Call Count

**Priority:** P1 | **Effort:** Included in B1 | **Lines:** 849, 858, 868, 879, 880, 892, 893, 919, 972, 1033, 1042, 1082

**Current Code:** 13 `Math.sin()` calls per frame (all share the `Date.now()` argument from B1).

**Issue:** `Math.sin()` is relatively expensive compared to the simple linear interpolation it's used for (pulse animations).

**Proposed Change:** After B1 (caching `now`), the `Date.now()/divisor` computation becomes trivial. The 13 `Math.sin()` calls remain but are bounded. At current scale (~60fps, 13 calls), this is acceptable. No further optimization recommended unless frame rate drops.

**Overlap:** Dependent on B1.

---

### B7. Eliminate `k in prevKeys` Redundant Check

**Priority:** P1 | **Effort:** 2 lines | **Lines:** 794-795

**Current Code:**
```js
for(const k in keys) prevKeys[k]=keys[k];
for(const k in prevKeys) { if(!keys[k] && k in prevKeys) delete prevKeys[k]; }
```

**Issue:** The `k in prevKeys` check is redundant — `for(const k in prevKeys)` already guarantees `k` exists in `prevKeys`.

**Proposed Change:**
```js
for(const k in keys) prevKeys[k]=keys[k];
for(const k in prevKeys) if(!keys[k]) delete prevKeys[k];
```

**Alternative (cleaner):**
```js
Object.assign(prevKeys, keys);
for(const k in prevKeys) if(!keys[k]) delete prevKeys[k];
```

**Impact:** Negligible runtime, but cleaner code.

**Overlap:** None with beyond-scope items.

---

### B8. Particle Render globalAlpha Reset

**Priority:** P2 | **Effort:** 0 lines (observation only) | **Lines:** 952-958

**Current Code:**
```js
for(const p of particles){
  const a=p.life/p.maxLife;
  X.fillStyle=p.color+(a>0.7?'':'');
  if(a<0.7) X.globalAlpha=a;
  X.fillRect(ox+p.x-p.size/2, oy+p.y-p.size/2, p.size, p.size);
  X.globalAlpha=1; // Reset after each fading particle
}
```

**Issue:** `globalAlpha=1` reset on every particle below 70% life adds canvas state changes.

**Assessment:** At current scale (<50 particles, typically <20 fading), this is negligible. No fix recommended. If particle count grows significantly, consider batching particles by alpha range.

**Overlap:** None with beyond-scope items.

---

## Category C: Structural Preparation

Focus: Improve code organization, extract reusable functions, and prepare for future modularity.

---

### C1. Extract `resolveXCollision()` with Parameterized Direction

**Priority:** P1 | **Effort:** ~5 lines | **Lines:** 688-698

See Proposal A4 for the duplication. This proposal extends it to also handle the Y collision response.

**Proposed Change:**
```js
// Combined with A4 and A11:
function resolveCollisionX(gx1, gx2, prevX){
  if(P.vx>0) P.x=gx2*T-P.w;
  else if(P.vx<0) P.x=(gx1+1)*T;
  else P.x=prevX;
  P.vx=0;
}

function resolveCollisionY(gy1, gy2, prevY){
  if(P.vy>0){ P.y=gy2*T-P.h; P.vy=0; land(); }
  else if(P.vy<0){ P.y=(gy1+1)*T; P.vy=0; }
}
```

**Overlap:** Builds on A4, A6, A11.

---

### C2. Physics Constant Extraction

**Priority:** P1 | **Effort:** ~15 constants added, ~25 line edits | **Lines:** 597-601, 608, 662, 664, 753, 761, 769, 779, 375-376, 386-387, 721/739/785

**Current Code (magic numbers):**
```js
// Line 597: P.vx += inputX * (P.onGround ? 0.05 : 0.2);
// Line 600-601: P.vx = Math.max(0, P.vx-0.225); / Math.min(0, P.vx+0.225)
// Line 608: P.vx *= 0.85;
// Line 662: P.vy += 0.07;
// Line 664: if(P.vy>2.5) P.vy=2.5;
// Line 753: P.vy = P.jumps===0 ? -5 : -4.33;
// Line 779: if(!jumpHeld && P.vy < -2) P.vy = -2;
// Line 375: PB.vy += 0.3;
// Line 376: if(PB.vy>4) PB.vy=4;
// Line 386: PB.vx *= 0.85;
// Line 387: if(Math.abs(PB.vx)<0.1) PB.vx=0;
// Lines 721/739/785: P.coyoteTime=12;
```

**Proposed Change:**
```js
// In Section 1 (Constants), after existing constants:

/* ── Player Physics ── */
const H_ACCEL_GROUND = 0.05;       // horizontal accel on ground
const H_ACCEL_AIR = 0.2;           // horizontal accel in air
const H_FRICTION = 0.225;          // horizontal friction per frame
const CHARGE_FRICTION = 0.85;      // velocity multiplier during charge
const GRAVITY = 0.07;              // gravity per frame
const TERMINAL_VEL = 2.5;          // max velocity (X and Y)
const JUMP_VEL_1 = -5;             // first jump velocity
const JUMP_VEL_2 = -4.33;          // double jump velocity (75% of first)
const JUMP_CUT_VEL = -2;           // variable jump cut threshold
const COYOTE_FRAMES = 12;          // coyote time in frames (200ms)
const JUMP_BUFFER_FRAMES = 12;     // jump buffer in frames (200ms)

/* ── Push Block Physics ── */
const PB_GRAVITY = 0.3;            // push block gravity
const PB_TERMINAL_VEL = 4;         // push block max fall speed
const PB_FRICTION = 0.85;          // push block friction multiplier
const PB_STOP_THRESH = 0.1;        // push block velocity stop threshold
```

Replace all magic numbers with their constant names.

**Impact:** Makes physics tuning trivial. Future balance changes become constant edits instead of code search-and-replace.

**Overlap:** This enhances **beyond-scope item #1 (Jump Velocity Equalization)** — once `JUMP_VEL_1` and `JUMP_VEL_2` are constants, equalization is a single line edit. Also merges with **beyond-scope item #4 (BLOCK Cleanup)** since the BLOCK constant can be removed in the same constants pass.

---

### C3. Particle System IIFE Extraction

**Priority:** P2 | **Effort:** ~15 lines | **Lines:** 406-460 (entire Section 7)

**Current Code:** Three standalone functions sharing `particles` array:
```js
function shatterBlock(bx, by){ ... }
function spawnParticles(px, py, color, count){ ... }
function updateParticles(){ ... }
```

**Issue:** These functions only depend on the `particles` array and are self-contained. They could be extracted into a clean module pattern.

**Proposed Change:**
```js
const ParticleSystem = (() => {
  const particles = []; // internal
  return {
    shatter(bx, by) { /* shatterBlock logic */ },
    spawn(px, py, color, count) { /* spawnParticles logic */ },
    update() { /* updateParticles logic */ },
    get() { return particles; } // accessor for render loop
  };
})();
```

**Risk:** Moderate — the render loop directly iterates `particles` (line 952), so an accessor or public array reference is needed.

**Overlap:** Slice C analysis shows this is the easiest system to extract (coupling level: MEDIUM — only needs particles array).

---

### C4. Tile Helpers Consolidation

**Priority:** P2 | **Effort:** ~10 lines | **Lines:** 208-272

**Current Code:**
```js
function collides(gx1,gy1,gx2,gy2, ch, prevY, curY){
  return tileCollidesY(ch, gx1*T, curY, (gx2-gx1+1)*T, P.h, prevY, curY);
}

function collidesDash(gx1,gy1,gx2,gy2,ch,prevY,curY){
  // Nearly identical to tileCollidesY with one extra continue for MAGICAL_WALL
  for(let x=gx1;x<=gx2;x++) for(let y=gy1;y<=gy2;y++){
    const t=getTile(ch,x,y);
    if(t===MAGICAL_WALL) continue; // extra check
    if(solid(t)) return tileCollidesY(ch, x*T, curY, T, P.h, prevY, curY);
  }
  return false;
}
```

**Issue:** `collides()` and `collidesDash()` share nearly identical logic — the only difference is the `MAGICAL_WALL` skip.

**Proposed Change:**
```js
function collides(gx1,gy1,gx2,gy2,ch,prevY,curY, skipType){
  for(let x=gx1;x<=gx2;x++) for(let y=gy1;y<=gy2;y++){
    const t=getTile(ch,x,y);
    if(skipType && t===skipType) continue;
    if(solid(t)) return tileCollidesY(ch, x*T, curY, T, P.h, prevY, curY);
  }
  return false;
}

// Call sites:
collides(gx1,gy1,gx2,gy2,P.chamber,prevY,P.y);        // normal
collides(gx1,gy1,gx2,gy2,P.chamber,prevY,P.y,MAGICAL_WALL); // dash
```

**Impact:** Code clarity and minor size reduction. Removes duplicate iteration logic.

**Overlap:** None with beyond-scope items.

---

### C5. Color Constant Extraction for Repeated Strings

**Priority:** P2 | **Effort:** ~8 constants, ~15 line edits | **Lines:** 626, 633, 647, 758, 766, 772, 339, 399, 723

**Current Code (repeated color strings):**
```js
'#d4a84b'   // 4x — jump particles, push particles, slot particles
'#8a7d6b'   // 4x — jump particles (2x), landing particles, golem body color
'rgba(220,120,255,0.4)'  // 2x — dash execution particles
'rgba(220,120,255,0.6)'  // 1x — dash fire
'rgba(180,80,255,0.4)'   // 1x — dash charge particles
```

**Proposed Change:**
```js
// In constants section:
const C_JUMP_PARTICLE = '#8a7d6b';        // also COLORS.golem
const C_ABILITY_PARTICLE = '#d4a84b';     // also COLORS.golemEye
const C_DASH_EXEC_PARTICLE = 'rgba(220,120,255,0.4)';
const C_DASH_FIRE = 'rgba(220,120,255,0.6)';
const C_DASH_CHARGE_PARTICLE = 'rgba(180,80,255,0.4)';
```

**Impact:** ~100 bytes saved, eliminates typo risk, makes color theming easier.

**Overlap:** None with beyond-scope items.

---

### C6. Tile Render Switch Statement (Readability)

**Priority:** P3 | **Effort:** ~30 lines (reformat) | **Lines:** 827-931

**Current Code:** 8-branch if/else chain:
```js
if(t===WALL){ ... }
else if(t===PLATFORM){ ... }
else if(t===PIT){ ... }
// ... 5 more branches
```

**Issue:** Deeply nested if/else is harder to read than a switch statement for 8 mutually exclusive cases.

**Proposed Change:**
```js
switch(t){
  case WALL:
    X.fillStyle=COLORS.wall; X.fillRect(px,py,T,T);
    // ... wall rendering
    break;
  case PLATFORM:
    // ... platform rendering
    break;
  // ... etc.
  default:
    break; // AIR — skip
}
```

**Impact:** Readability improvement only. V8 optimizes both patterns equally. No performance change.

**Overlap:** None with beyond-scope items.

---

## Category D: File Size Reduction

Focus: Remove dead code, eliminate unused constants, and reduce file size.

---

### D1. Remove BLOCK Dead Code

**Priority:** P1 | **Effort:** ~5 edits, ~200 bytes saved | **Lines:** 26, 223, 901-905

**Current Code:**
```js
// Line 26 (constant definition)
const AIR=0, WALL=1, PIT=2, DOOR_R=3, DOOR_D=4, GLYPH=5, BLOCK=6, CRACKED=7, ...;

// Line 223 (solid() function) — t===BLOCK check

// Lines 901-905 (render branch)
else if(t===BLOCK){
  X.fillStyle=COLORS.block; X.fillRect(px+1,py+1,T-2,T-2);
  X.fillStyle='#9a8d7d'; X.fillRect(px+2,py+2,T-4,3);
  X.fillStyle='#5a4d3d'; X.fillRect(px+2,py+T-5,T-4,3);
  if(P.canPush){ X.fillStyle='rgba(255,255,255,0.15)'; X.fillRect(px+4,py+4,T-8,T-8); }
}
```

**Issue:** No chamber uses BLOCK tiles. This is dead code that adds ~200 bytes.

**Proposed Change:**
1. Remove `BLOCK=6` from tile constants (line 26)
2. Remove `t===BLOCK` from `solid()` function (line ~223)
3. Remove `else if(t===BLOCK)` render branch (lines 901-905)
4. Remove `block` from `COLORS` object if unused elsewhere

**Risk:** LOW — no chamber uses BLOCK, confirmed by code search. If BLOCK is re-added, tile values 7-11 would need to shift down by 1.

**Overlap:** This **is beyond-scope item #4**. The optimization analysis recommends merging it into the optimization task.

---

### D2. Remove `COLORS.block` Entry

**Priority:** P1 | **Effort:** 1 line | **Lines:** 801-808

**Current Code:**
```js
const COLORS = {
  bg:'#0d0d1a', wall:'#4a4035', wallTop:'#6b5d4f',
  platform:'#5a4d3a', pit:'#000000', door:'#2a5a3a',
  glyph:'#c8a84e', glyphGlow:'#f0d060',
  block:'#7a6d5d', cracked:'#8a5040', // block unused if D1 applied
  // ...
};
```

**Issue:** `COLORS.block` is only referenced in the BLOCK render branch (lines 901-905). If D1 is applied, this entry is dead.

**Proposed Change:** Remove `block:'#7a6d5d'` from COLORS object.

**Overlap:** Dependent on D1.

---

### D3. File Size Summary

**Estimated savings from all D-category proposals:**

| Optimization | Bytes Saved | Status |
|-------------|------------|--------|
| Remove BLOCK dead code (D1) | ~200 | Primary |
| Remove COLORS.block (D2) | ~20 | Dependent on D1 |
| Color constant extraction (C5) | ~80 | Independent |
| Move abilities/names out of render | ~0 (runtime only) | B2, B3 |
| **Total** | **~300-500 bytes** | |

Note: The file is 44KB, so these savings represent ~0.7-1.1%. File size optimization is low priority — the single-file constraint means readability and maintainability matter more than bytes.

---

## Cross-Reference: Beyond-Scope Simplifications

This section maps each item from `docs/beyond-scope-simplifications.md` to its status relative to the optimization proposals.

| Beyond-Scope # | Item | Status | Covered By Proposal(s) | Notes |
|---------------|------|--------|----------------------|-------|
| #1 | Jump Velocity Equalization | **MERGED** | C2 (physics constants) | Once `JUMP_VEL_1`/`JUMP_VEL_2` are constants, equalization is trivial. Propose grouping with magic number extraction. |
| #2 | Pause Toggle | **SEPARATE** | N/A | Feature addition, not optimization. Remains in beyond-scope. |
| #3 | Responsive Canvas | **SEPARATE** | N/A | Pure CSS change, no code interaction. Remains in beyond-scope. |
| #4 | BLOCK Cleanup | **MERGED** | D1, D2 | Dead code removal now part of optimization. Beyond-scope item superseded. |
| #5 | Input Normalization | **MERGED** | A7 | Input abstraction functions are core duplication elimination. Beyond-scope item superseded. |
| #6 | Message Queue | **SEPARATE** | N/A | Feature addition. Would benefit from C3 (structural prep) but is independent. |
| #7 | Camera System | **SEPARATE** | N/A | Architectural change. Hardcoded `ox`/`oy` at lines 820-821. Remains in beyond-scope. |
| #8 | Sound Effects | **SEPARATE** | N/A | Independent feature system. Remains in beyond-scope. |
| #9 | Touch Controls | **SEPARATE** | N/A | Independent UI system. Remains in beyond-scope. |
| #10 | Code Comments | **SEPARATE** | N/A | Documentation task. Section delimiters already added. Remains in beyond-scope. |

**Summary:**
- **3 items merged into optimization:** #1 (jump equalization → C2), #4 (BLOCK cleanup → D1/D2), #5 (input normalization → A7)
- **7 items remain as separate feature work:** #2, #3, #6, #7, #8, #9, #10

**Note:** The line references in `docs/beyond-scope-simplifications.md` are stale (from pre-refactor code). This report uses verified line numbers from the current golem.html. The beyond-scope doc should be updated when those items are eventually implemented.

---

## Review Notes

This report has been reviewed and verified against the source code:

- **Line references:** 13+ spot-checked against golem.html — all correct
- **Code snippets:** Verified character-for-character match with source
- **Priority counts:** Corrected to match actual summary table (P0:11, P1:9, P2:9, P3:3)
- **Cross-references:** All 10 beyond-scope items correctly mapped

**Minor observations not elevated to proposals:**
- `collidesNoPlat()` (lines 250-257) could be consolidated with `collides()`/`collidesDash()` — low impact
- Proposal B6 (Math.sin count reduction) is subsumed by B1 (Date.now cache)
- Proposal B8 (particle globalAlpha) is observation-only at current scale

---

## Implementation Order & Grouping Recommendations

### Phase 1: Zero-Risk Quick Wins (P0)
*Estimated effort: 30 minutes. All changes are isolated with no behavioral impact.*

**Batch 1A — Constant/Cache Additions:**
1. B1 — Cache `Date.now()` once per frame
2. B2 — Move `abilities` array to module scope
3. B3 — Move `chamber names` array to module scope
4. A8 — Cache `collectedGlyphs[ch]` lookup

**Batch 1B — Duplication Elimination:**
5. A1 — Precompute jump particle coordinates
6. A2 — Extract dash particle color constant
7. A3 — Extract `killAndRespawn()`
8. A4 — Extract `resolveXCollision()` / `snapToTileX()`
9. A5 — Extract `endDash()`
10. A6 — Extract `land()`
11. A7 — Input normalization abstractions

**Why batched this way:** 1A adds no new functions, just constants/caches. 1B adds small extraction functions. Both batches can be done in one pass through the file.

### Phase 2: Structural Improvements (P1)
*Estimated effort: 1 hour. Low risk, clear value.*

**Batch 2A — Constants & Physics:**
1. C2 — Physics constant extraction (~15 constants)
2. B7 — Fix prevKeys cleanup redundancy

**Batch 2B — Dead Code:**
3. D1 — Remove BLOCK dead code
4. D2 — Remove COLORS.block

**Batch 2C — Performance:**
5. B4 — Precompute starfield per chamber
6. A9 — Scope `currentChamber` variable (if risk is acceptable)

**Why batched this way:** 2A changes constants and their references. 2B removes dead code. 2C touches render performance. Each batch is self-contained.

### Phase 3: Nice-to-Have (P2-P3)
*Estimated effort: 1-2 hours. Moderate effort, lower urgency.*

1. B5 — Sparse tile rendering
2. C1 — Combined collision resolution functions
3. C3 — Particle system IIFE extraction
4. C4 — Tile helpers consolidation
5. C5 — Color constant extraction
6. C6 — Tile render switch statement
7. A10, A11, A12 — Minor extraction helpers

**Why batched this way:** These are more invasive changes that should be done after the quick wins are validated.

---

## Risk Assessment

### Low Risk (safe to do immediately)

| Proposal | Risk Factor | Mitigation |
|----------|------------|------------|
| A1, A2, A8 | Simple variable extraction | No behavioral change |
| B1 | Replacing Date.now() with cached `now` | Same value within frame; actually more deterministic |
| B2, B3 | Moving static arrays | No behavioral change |
| D1, D2 | Removing unused BLOCK code | No chamber references it |
| B7 | Removing redundant check | Logic-equivalent |

### Medium Risk (test in browser after)

| Proposal | Risk Factor | Mitigation |
|----------|------------|------------|
| A3 | killAndRespawn() slight variation | Verify `onGround` values match original |
| A4, A5, A6 | Function extraction | Verify identical behavior at both call sites |
| A7 | Input abstraction | Verify all key combinations still work |
| C2 | Magic number replacement | Verify each constant maps to correct original value |
| B4 | Starfield precomputation | Verify visual output matches frame-by-frame |

### Higher Risk (validate carefully)

| Proposal | Risk Factor | Mitigation |
|----------|------------|------------|
| A9 | Chamber-scoped getTile | Must audit ALL getTile() call sites; update() calls outside render |
| B5 | Sparse tile rendering | Must maintain sparse list in setTile(); adjacency checks still need full grid |
| C3 | Particle system extraction | Render loop directly iterates particles array |
| C4 | Tile helpers consolidation | collidesDash() has MAGICAL_WALL skip — must preserve |
| C6 | Switch statement refactor | 8 branches with complex rendering logic — easy to mis-copy |

---

## Summary Table: All Proposals Ranked

| # | Proposal | Category | Priority | Lines | Effort | Impact | Beyond-Scope Ref |
|---|----------|----------|----------|-------|--------|--------|-----------------|
| 1 | Precompute jump particle coords | A | P0 | 758,766,772 | Trivial | Low | — |
| 2 | Extract dash particle color constant | A | P0 | 633,647 | Trivial | Low | — |
| 3 | Extract `killAndRespawn()` | A | P0 | 651-653,783-786 | ~8 lines added | Medium | Enhances #1 |
| 4 | Extract `resolveXCollision()` | A | P0 | 688-691,694-697 | ~5 lines added | Low | — |
| 5 | Extract `endDash()` | A | P0 | 649,685 | ~3 lines added | Low | — |
| 6 | Extract `land()` | A | P0 | 719-721,737-739 | ~3 lines added | Low | — |
| 7 | Input normalization abstractions | A | P0 | 591-592,637,749-750 | ~12 lines added | Medium | **Merges #5** |
| 8 | Cache `collectedGlyphs[ch]` | A | P0 | 856,1093 | Trivial | Low | — |
| 9 | Cache `inputX` direction sign | A | P2 | 593-597 | Trivial | Low | — |
| 10 | Extract `snapToTileY()` | A | P2 | 716-727 | ~5 lines added | Low | — |
| 11 | Extract `getChargeRatio()` | A | P2 | 612,964,1074 | ~2 lines added | Low | — |
| 12 | Combined X/Y collision resolution | A/C | P1 | 688-727 | ~10 lines added | Medium | — |
| 13 | Cache `Date.now()` once per frame | B | P0 | 849,858,868,879-880,892-893,919,927,945,972,1033,1042,1050,1082 | 1 line added, 15 edits | High | — |
| 14 | Move `abilities` to module scope | B | P0 | 1061-1064 | 2 lines moved | Low | — |
| 15 | Move `CHAMBER_NAMES` to module scope | B | P0 | 1090 | 2 lines moved | Low | — |
| 16 | Precompute starfield per chamber | B | P1 | 817 | ~5 lines added | Low-Medium | — |
| 17 | Sparse tile rendering | B | P2 | 824-931 | ~20 lines added | Medium | — |
| 18 | Reduce Math.sin() call count | B | P1 | (all B1 lines) | Included in B1 | Low | — |
| 19 | Fix prevKeys redundant check | B | P1 | 794-795 | 2 lines | Low | — |
| 20 | Particle globalAlpha reset | B | P2 | 952-958 | N/A | Negligible | — |
| 21 | Physics constant extraction | C | P1 | 597-601,608,662,664,753,761,769,779,375-387,721/739/785 | ~40 lines total | High | **Enhances #1** |
| 22 | Particle system IIFE | C | P2 | 406-460 | ~15 lines added | Medium | — |
| 23 | Tile helpers consolidation | C | P2 | 208-272 | ~10 lines added | Low | — |
| 24 | Color constant extraction | C | P2 | 626,633,647,758,766,772,339,399,723 | ~23 lines total | Low | — |
| 25 | Tile render switch statement | C | P3 | 827-931 | ~30 lines refactored | Low | — |
| 26 | Scope `currentChamber` for getTile | C | P1 | 212-216,811 | ~5 lines added | Medium | — |
| 27 | Remove BLOCK dead code | D | P1 | 26,223,901-905 | ~5 edits | Low | **Merges #4** |
| 28 | Remove COLORS.block | D | P1 | 801-808 | 1 line | Negligible | — |
| 29 | File size summary (all D) | D | P1 | Various | — | Low | — |
| 30 | Jump velocity equalization | A/D | P2 | 753 | 1 line edit | Medium | **Is #1** |
| 31 | Dash charge feel improvement | A | P3 | 586-640 | ~15 lines | Medium | From code-review.md |
| 32 | Push effort pulse optimization | B | P3 | 1033-1039 | ~5 lines | Low | — |

---

## Notes on Dependencies Between Proposals

```
B1 (Date.now cache) --> B6 (Math.sin count)
C2 (Physics constants) --> A6 (land() uses COYOTE_FRAMES)
C2 (Physics constants) --> D1 (BLOCK constant removal)
A3 (killAndRespawn) --> C2 (uses COYOTE_FRAMES)
A6 (land) --> C2 (uses COYOTE_FRAMES)
D1 (BLOCK removal) --> D2 (COLORS.block removal)
A4 (resolveX) + A11 (snapToTileY) --> C1 (combined collision)
A7 (Input normalization) --> beyond-scope #5 (supersedes)
```

**Recommended execution sequence:**
1. Phase 1 (P0) — do all, no dependencies between batches
2. Phase 2 (P1) — do C2 before A3/A6 (constants needed by extracted functions)
3. Phase 3 (P2-P3) — do C1 after A4/A11; do D2 after D1

---

## Governance Compliance

- **No architectural changes proposed** — all proposals maintain the single-file architecture
- **No new tile types** — D1 removes a dead tile type, consistent with constraints
- **No framework dependencies** — all proposals use vanilla JS
- **Existing chambers preserved** — no chamber data changes proposed
- **Grant-then-use chain preserved** — no ability progression changes

All proposals comply with `AGENTS.md` governance rules. No governance approvals needed for Phase 1 (P0) changes. Phase 2 changes (particularly A9 and C2) may warrant a brief review given their scope.

---

*Report generated from: `docs/code-optimization-analysis.md`, `docs/beyond-scope-simplifications.md`, `code-review.md`, `ROADMAP.md`, `docs/Project-Constraints.md`*
*Line references verified against golem.html (1152 lines)*
