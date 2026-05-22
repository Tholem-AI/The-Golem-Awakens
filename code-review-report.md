# Code Review: The Golem Awakens

## Overall Assessment

Well-structured single-file game with clean sectioning, well-tuned physics, and a thoughtful push-block system. The architecture is easy to follow: 11 logical sections, function hoisting, IIFE-encapsulated particle module, and sparse render lists for performance. The biggest opportunities are around input key-state cleanup and a few defensive checks in the collision layer. No critical bugs that break core functionality were found.

## Critical Issues

None. All core systems (main loop, input, collision, state transitions, push-block physics) function correctly.

## Important Improvements

### 1. `prevKeys` dictionary can grow unbounded (lines 420, 1156-1157, 1196-1197)

`prevKeys` is copied from `keys` each frame via `for...in`, and keys are only deleted when released. If a player never releases a key (e.g., modifier key pressed before loading), it persists indefinitely. Over a long session, this makes the per-frame key-copy loop slower.

**Fix:** Clear and copy atomically, or snapshot once per frame:

```javascript
// Replace lines 1156-1157 and 1196-1197 with:
prevKeys = {...keys};
```

This creates a fresh snapshot each frame, guaranteeing `prevKeys` never accumulates stale entries. The spread operator is standard and fast for small dictionaries.

### 2. Push-block `resolvePushBlockCollision` returns early on first `isOnTop` match (lines 656-699)

The `for` loop iterates all push blocks, but uses `return` (not `continue`) when `isOnTop` is true on line 695. If the player overlaps multiple blocks and is on top of the first one, remaining blocks are never checked.

**Risk:** Low in practice (blocks don't overlap each other), but `return` silently exits the function instead of `continue`ing to the next block. If future chamber design places blocks close together, the player could miss collision resolution with a second block.

**Fix:** Change `return` to `continue` on line 695:

```javascript
if(isOnTop) continue; // let Y landing check handle this
```

### 3. `killAndRespawn` has an unused `onGround` parameter (line 105)

```javascript
function killAndRespawn(onGround, msg, duration) {
```

The `onGround` parameter is never referenced in the function body (lines 106-110). All callers pass `false` anyway (lines 624, 1148). This is misleading API surface.

**Fix:** Remove the parameter:

```javascript
function killAndRespawn(msg, duration) {
```

Update callers on lines 624 and 1148 accordingly.

### 4. No `requestAnimationFrame` cancellation on game end (line 1722)

When `gameState` becomes `'ending'`, the loop function still runs every frame (it returns early in `update` but `render` still executes). This wastes CPU cycles on the ending screen.

**Fix:** Cancel the loop when the game ends:

```javascript
let animFrameId;
function loop(){
  if(gameState==='ending'){ render(); return; } // render once, stop
  update(); render();
  animFrameId = requestAnimationFrame(loop);
}
animFrameId = requestAnimationFrame(loop);
```

## Suggestions

### 5. Canvas not scaled for high-DPI displays (lines 22-23, CSS line 9)

The canvas is fixed at 800x480 with no device pixel ratio adjustment. On Retina/HiDPI screens the game will appear blurry.

```javascript
// Add after line 23:
const dpr = window.devicePixelRatio || 1;
C.style.width = W + 'px';
C.style.height = H + 'px';
C.width = W * dpr;
C.height = H * dpr;
X.scale(dpr, dpr);
```

### 6. Particle pool uses `splice` for removal (line 798)

`pool.splice(i, 1)` shifts all subsequent elements. Fine for typical particle counts (<100) but quadratic for large bursts. A swap-and-pop or filtered approach would be more robust if particle counts grow.

### 7. `for...in` on plain objects for key iteration (lines 1156, 1196)

`for...in` iterates enumerable properties including prototype chain entries. For a small game this is harmless, but `Object.keys()` is safer:

```javascript
for(const k of Object.keys(keys)) prevKeys[k] = keys[k];
```

(Combined with fix #1 above, this becomes moot.)

## Positive Observations

- **Physics constants are well-documented and mathematically justified.** The gravity/velocity relationship (line 46: `GRAVITY = 0.07`) is derived from the peak height formula, with clear rationale in the reference docs.
- **Push-block system is sophisticated for a single-file game.** The 4-phase orchestrator (horizontal velocity, rider coupling, gravity+Y resolution, friction/slots) with bottom-up processing order (line 606) handles stacking, sliding off edges, and crush deaths correctly.
- **Y-overlap guard in push collision** (lines 668-670) prevents horizontal knock when landing on top of a block — a subtle but important detail.
- **Coyote time + jump buffer + variable jump height** (lines 49-52, 1112-1143) give the platforming a forgiving, polished feel.
- **Sparse render list** (`solidTiles` array, lines 1706-1713) avoids iterating 25x15 tiles for AIR cells. Properly maintained through `setTile` (lines 450-461).
- **Death/respawn animation** (lines 1213-1354) is detailed with part-by-part materialization, clay pile dissipation, and glyph activation flash — excellent visual polish.
- **Section delimiter comments** make the 1727-line file navigable. Function hoisting means no ordering headaches.

## Recommended Next Steps

1. **Apply fix #1** (`prevKeys = {...keys}`) — one-line change, eliminates a latent performance concern and makes the intent clearer.
2. **Apply fix #2** (`return` to `continue` on line 695) — defensive fix that makes the push-block loop robust against future chamber layouts.
3. **Apply fix #3** (remove unused `onGround` parameter) — cleans up misleading API.
4. **Consider fix #4** (cancel rAF on ending) — small quality-of-life improvement that stops CPU churn on the credits screen.
