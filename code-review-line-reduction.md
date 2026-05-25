# golem.html -- Code Review: Line Count Reduction Analysis

**File:** golem.html (2,625 lines, ~109 KB)
**Structure:** 87 lines HTML/CSS, 2,535 lines JavaScript, 2 trailing HTML

---

## Overall Assessment

The codebase is well-organized with clear IIFE modules, consistent naming, and a logical
section structure. No architectural bloat. The main line count savings come from: (1) dead
code removal -- three unused functions and one unused property, (2) redundant constant
declarations where raw base values shadowed by scaled _ACTUAL variants, (3) compressible
patterns in the ending sequence and game reset, and (4) dead feature comments left from
prior iterations.

**Realistic savings: ~35-45 lines (1.3-1.7%) with zero-risk changes.**
Aggressive comment pruning could push to ~60 lines, but readability loss is non-trivial.

---

## A. Dead Code Removal (zero risk, guaranteed savings)

### A1. Unused function: `smoothStep()` (L245)

```javascript
function smoothStep(t) { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); }
```

Defined but never called anywhere. `easeOutCubic` and `easeOutQuint` are used instead.

**Savings: 1 line | Risk: none**

### A2. Unused function: `vLine()` (L312)

```javascript
function vLine(g,x,y1,y2,v){for(let y=y1;y<=y2;y++)g[y][x]=v;}
```

Sibling of `hLine()` (which IS used in chamber 2-4). No chamber data uses `vLine()`.

**Savings: 1 line | Risk: none (but document it in case future chambers need it)**

### A3. Unused function: `inputShiftPressed()` (L670)

```javascript
function inputShiftPressed() { return fresh('ShiftLeft')||fresh('ShiftRight'); }
```

Shift is handled via `shiftHeld()` and `inputShiftPressed()` is never called.

**Savings: 1 line | Risk: none**

### A4. Unused property: `_snd` on push blocks (L873)

```javascript
PBlocks.push({x:sp.x*T,y:sp.y*T,w:T,h:T,vx:0,vy:0,active:true,inSlot:false,_snd:false});
```

`_snd` is set to `false` at construction but never read or modified. `_pushF` on the Player
object (L898-899) handles push sound rate-limiting instead.

**Savings: inline field removal (no line count, cleaner object literal) | Risk: none**

### A5. Duplicate respawnX/Y assignment in `resetGameState()` (L2425)

```
L2417: P.respawnX=chambers[0].spawnPx; P.respawnY=chambers[0].spawnPy;
L2418: resetPlayerToRespawn();   // uses P.respawnX/Y set above
...
L2425: P.respawnX=chambers[0].spawnPx; P.respawnY=chambers[0].spawnPy;  // DUPLICATE
```

L2425 sets the same values that L2417 already set. Nothing between them modifies
`P.respawnX`/`P.respawnY`.

**Savings: 1 line | Risk: none**

### A6. Dead feature comments (L1414, L2115)

```javascript
/* Airborne clay trail (Phase 4.5) -- removed to reduce visual clutter */
/* Hebrew letters on body -- removed (glyph count shown in HUD instead) */
```

These document removed features with no code to reference. They serve no purpose.

**Savings: 2 lines | Risk: none**

---

## B. Redundant Constants

### B1. Unused message timing base constants (L1160-1161, L1164-1165)

```javascript
const MSG_FADE_IN_FRAMES   = 180;   // unused -- MSG_FADE_IN_ACTUAL used instead
const MSG_FADE_OUT_FRAMES  = 180;   // unused -- MSG_FADE_OUT_ACTUAL used instead
const MSG_MIN_HOLD         = 90;    // unused -- MSG_MIN_HOLD_ACTUAL used instead
const MSG_MAX_HOLD         = 360;   // unused -- MSG_MAX_HOLD_ACTUAL used instead
```

The `_ACTUAL` variants (L143-146) are the ones actually used throughout the code.
`applyPaceAssists()` computes them from the raw values. The raw `const` declarations
serve no purpose -- they duplicate the literals already inside `applyPaceAssists()`.

**Savings: 4 lines | Risk: low (verify no hidden references)**

### B2. Dash particle colors could fold into PARTICLE_COLORS (L112-113)

```javascript
const DASH_EXEC_PARTICLE_COLOR = 'rgba(92,179,175,0.50)';
const DASH_CHARGE_PARTICLE_COLOR = 'rgba(71,158,153,0.35)';
```

`PARTICLE_COLORS.dashBurst` (L196) is a similar but different value. These two standalone
constants could be added to `PARTICLE_COLORS` object, saving 2 lines for 2 new properties.

**Savings: 2 lines | Risk: none | Tradeoff: minor -- adds entries to existing object**

---

## C. Pattern Compression (low-moderate risk)

### C1. `endingBeat` progression (L2299-2304) -- 6 lines to 2

Current:
```javascript
    if(endSec < ENDING.BEAT_2) endingBeat = 1;
    else if(endSec < ENDING.BEAT_3) endingBeat = 2;
    else if(endSec < ENDING.BEAT_4) endingBeat = 3;
    else if(endSec < ENDING.BEAT_5) endingBeat = 4;
    else if(endSec < ENDING.BEAT_6) endingBeat = 5;
    else endingBeat = 6;
```

Compressed:
```javascript
    endingBeat = 1;
    for (let b = 2; b <= 6; b++) if (endSec >= ENDING['BEAT_' + b]) endingBeat = b;
```

**Savings: ~4 lines | Risk: low (pure logic compression, identical behavior)**

### C2. `captionAlphaSec()` (L277-287) -- 11 lines to ~7

Current:
```javascript
function captionAlphaSec(t, start, fadeIn, hold, fadeOut) {
  if (t < start) return 0;
  let elapsed = t - start;
  if (fadeIn > 0 && elapsed < fadeIn) return elapsed / fadeIn;
  elapsed -= fadeIn;
  if (hold > 0 && elapsed < hold) return 1;
  elapsed -= hold;
  if (fadeOut > 0 && elapsed < fadeOut) return 1 - (elapsed / fadeOut);
  if (fadeOut === 0) return 1;
  return 0;
}
```

Compressed:
```javascript
function captionAlphaSec(t, start, fi, hold, fo) {
  let e = t - start; if (e < 0) return 0;
  if (fi && e < fi) return e / fi; e -= fi;
  if (hold && e < hold) return 1; e -= hold;
  if (fo && e < fo) return 1 - e / fo;
  return fo ? 0 : 1;
}
```

**Savings: ~4 lines | Risk: low (parameter names shorter but semantics identical)**

### C3. `resetGameState()` consolidation (L2419-2424)

Current:
```javascript
  P.onGround=false; P.jumps=0; P.maxJumps=1;
  P.canDash=false; P.dashing=false; P.dashTimer=0; P.dashDir=0; P.dashCooldown=0; P.dashPhase=false; P.dashCharge=0;
  P.canPush=false; P.canBreak=false;
  P.facing=1; P.chamber=0;
  P.coyoteTime=0; P.jumpBuffer=0; P.pushing=false;
  P.landSquish=0; P.turnLean=0; P.lastFacing=1;
```

Compressed -- merge booleans and zeroed values:
```javascript
  P.maxJumps=1; P.facing=1; P.chamber=0; P.lastFacing=1;
  P.onGround=P.canDash=P.canPush=P.canBreak=P.dashing=P.dashPhase=P.pushing=false;
  P.jumps=P.dashTimer=P.dashDir=P.dashCooldown=P.dashCharge=P.coyoteTime=P.jumpBuffer=
    P.landSquish=P.turnLean=0;
```

**Savings: ~3 lines | Risk: low (readability tradeoff -- chained assignment is standard JS)**

### C4. `getEndingGlyphState()` phase comments (L2189-2278, 89 lines)

The function has ~12 comment lines marking phases (A through D) with detailed explanations.
These could be reduced to minimal labels:

```javascript
/* Phase A: Orbit */     ->  /* orbit */
/* Phase B: Convergence */ ->  /* converge */
/* Phase C: Flash bloom */ ->  /* flash */
/* Phase D: Glow */     ->  /* glow */
```

Several multi-line comment explanations (e.g., L2228 RTL explanation, L2215 converge timing)
could be shortened or folded into code comments.

**Savings: ~10-15 lines | Risk: none (comment-only) | Tradeoff: reduced self-documentation**

---

## D. Structural Observations (limited line reduction potential)

### D1. Chamber data step comments

Each chamber IIFE has step-numbered comments (Steps 1-9). These are ~30 lines across 6
chambers. Removing them saves lines but the 9-step convention is documented in
`chamber-template.md` and aids maintainability.

**Potential: ~30 lines | Risk: moderate (loses construction documentation) | NOT recommended**

### D2. Section headers (69 lines total)

The `/* ═══ SECTION NAME ═══ */` headers add clarity to the 2,500+ line file. Removing
them would make navigation harder without IDE folding.

**Potential: ~69 lines | Risk: high (severely impacts readability) | NOT recommended**

### D3. Blank lines (271 total)

Many are structural separators between logical blocks. Some inside functions (e.g.,
`getEndingGlyphState` has 9 internal blanks) could be reduced, but this is cosmetic.

**Potential: ~50-80 lines if aggressively compressed | NOT recommended**

### D4. SVG logo (L51-58, 8 lines of dense path data)

The embedded SVG is minified path data. Could theoretically be further compressed with
shorter precision, but the paths are already tight. An external SVG would save lines but
add a file dependency.

**Potential: ~4-6 lines with path precision reduction | Risk: visual fidelity loss**

---

## E. Minor Cleanups (1-2 lines each)

### E1. `solid()` trailing `|| false` (L694)

```javascript
function solid(t){ return t===WALL||t===CRACKED||t===DOOR_D||t===END_PORTAL||t===MAGICAL_WALL || false; }
```

The `|| false` is a no-op -- the chained `===` already returns boolean.

**Savings: inline cleanup (no line count) | Risk: none**

### E2. Blank line inside `fullDashReset()` (L269-270)

```javascript
function fullDashReset() {
  cancelDash(); P.dashCooldown=0; P.dashPhase=false; P.dashCharge=0;

}
```

Unnecessary blank line before closing brace.

**Savings: 1 line | Risk: none**

### E3. `_dashSfx` flag pattern (L233, L1394)

The `_dashSfx` boolean on Player controls whoosh sound throttling. It's set `true` during
dash (L1394) and cleared in `endDash()` (L233). The logic works but could be replaced with
a simpler frame-based throttle (`P.dashTimer % 3`) without the flag.

**Savings: ~1 line (remove flag from Player object and endDash) | Risk: low**

---

## Summary Table

| Category | Item | Lines | Risk |
|----------|------|-------|------|
| Dead code | `smoothStep()` | 1 | none |
| Dead code | `vLine()` | 1 | none |
| Dead code | `inputShiftPressed()` | 1 | none |
| Dead code | `_snd` property | 0 (inline) | none |
| Dead code | Duplicate respawnX/Y | 1 | none |
| Dead code | Feature comments | 2 | none |
| Redundant | MSG base constants | 4 | low |
| Redundant | Dash particle colors | 2 | none |
| Compression | endingBeat progression | 4 | low |
| Compression | captionAlphaSec | 4 | low |
| Compression | resetGameState | 3 | low |
| Compression | getEndingGlyphState comments | 10-15 | none |
| Minor | solid() \|\| false | 0 (inline) | none |
| Minor | fullDashReset blank | 1 | none |
| Minor | _dashSfx flag | 1 | low |
| **SUBTOTAL** | **Recommended** | **~35-40** | |
| | Aggressive (comments/headers) | +20 | moderate |

---

## Recommended Priority Order

1. **A1-A6** (dead code, 6 lines) -- immediate, zero risk
2. **B1** (redundant MSG constants, 4 lines) -- verify then remove
3. **C1-C3** (pattern compression, ~11 lines) -- logic compression, low risk
4. **B2, E1-E3** (minor cleanups, ~4 lines) -- cosmetic
5. **C4** (ending function comments, ~10-15 lines) -- readability tradeoff

---

## Positive Observations

- **Sparse tile rendering** (L1854) -- iterates only non-AIR tiles via `c.solidTiles`,
  avoiding 375 tile draws per frame. Smart optimization.
- **Chamber cache `_c`** (L1299, L1534, L1813) -- avoids repeated `chambers[P.chamber]`
  lookups in hot paths.
- **HUD throttling** (L2136) -- only updates DOM when state actually changes, saving
  95%+ of DOM writes.
- **Fixed-timestep game loop** (L2586-2607) -- accumulator pattern with cap prevents
  spiral-of-death. Correct implementation.
- **IIFE encapsulation** -- Particles and Sound modules properly isolate internals.
- **9-step chamber convention** -- consistent, verifiable construction pattern.
- **Push block 3-phase system** -- clean separation of horizontal velocity, rider coupling,
  and gravity resolution.
