# Execution Plan: Pushblock Standing Bug Fix

**Date:** 2026-05-16
**Phase:** Plan (RIPER)
**Predecessor:** Research phase (research-agent findings)
**Next phase:** Execute (executor-agent)

---

## 1. Problem Statement

The golem cannot land on top of a pushblock and stand on it. Instead, when falling onto the pushblock, the player is snapped horizontally to the side and falls past. Walking on top and pushing horizontally from the side must both still work.

### Required behaviors after fix:
1. Golem falls onto pushblock from above -> lands on top, `onGround = true`
2. Golem walks on top of pushblock -> normal ground physics (gravity off, coyote time, jumps work)
3. Golem stands beside pushblock and pushes -> horizontal push still works as before

---

## 2. Root Cause (from research-agent)

In `golem.html`, the update cycle runs:

1. **Line 663:** `resolvePushBlockCollision()` — X-axis separation against pushblock
2. **Lines 689-698:** Y-axis landing check for pushblock

When player falls onto pushblock:
- Frame N: Player bottom enters pushblock top, AABB overlaps
- `resolvePushBlockCollision()` fires (line 663):
  - Sees overlap, `P.onGround` is false (falling), `movingToward` is false (no horizontal velocity)
  - Falls to `else` branch (lines 204-206): snaps `P.x` to side of pushblock
- Y landing check (lines 689-698) runs next:
  - AABB no longer overlaps (player kicked sideways)
  - Landing silently fails
  - Player falls through

### Key dimensions:
- Player: w=24, h=28
- Pushblock: w=32, h=32
- Tile size T=32

---

## 3. Chosen Approach: Option B — Y-Overlap Guard

**Preferred fix:** Add a guard in `resolvePushBlockCollision()` that detects when the player is falling on top of the pushblock and skips X-axis separation in that case.

### Rationale:
- **Minimal change:** Single function, one new conditional branch
- **No structural changes:** Doesn't reorder update loop (Option A)
- **No extra state:** Doesn't require passing prevY (Option C)
- **Localized risk:** Only affects `resolvePushBlockCollision()`, no ripple effects

### Why NOT Option A (reorder):
- Moves Y landing before X separation — changes the fundamental update order
- Could break other collision paths that depend on current ordering
- Higher risk surface, harder to verify

### Why NOT Option C (pass prevY):
- Requires threading prevY through function signature
- More plumbing, more places to audit
- No additional benefit over Option B's approach

---

## 4. Detailed Implementation Plan

### Step 1: Add Y-overlap guard to `resolvePushBlockCollision()`

**File:** `golem.html`
**Target:** `resolvePushBlockCollision()` function (lines 181-208)

**Logic to add (before the else branch at line 204):**

```javascript
function resolvePushBlockCollision(){
  if(!P.canPush || !PB.active || PB.inSlot) return;
  if(!aabb(P.x, P.y, P.w, P.h, PB.x, PB.y, PB.w, PB.h)) return;

  const centerP = P.x + P.w / 2;
  const centerB = PB.x + PB.w / 2;
  const dir = (centerP < centerB) ? 1 : -1;

  const movingToward = (P.vx * dir > 0.1);

  // ── NEW: Y-overlap guard — skip X separation when player is on top ──
  // Check if player bottom is near pushblock top (within small tolerance)
  // AND player is not already on ground (falling down onto it)
  const playerBottom = P.y + P.h;
  const pushTop = PB.y;
  const onTopTolerance = 8; // pixels — accounts for variable fall distance per frame
  const isOnTop = playerBottom >= pushTop - onTopTolerance
                 && playerBottom <= pushTop + P.h / 2
                 && P.y < pushTop; // player top is above pushblock top
  // ───────────────────────────────────────────────────────────────────

  if(P.onGround && movingToward){
    const tileStep = dir * T;
    if(!tileCollides(P.chamber, PB.x + tileStep, PB.y, PB.w, PB.h)){
      PB.x += tileStep;
      if(dir > 0) P.x = PB.x - P.w;
      else        P.x = PB.x + PB.w;
      P.vx = 0;
      spawnParticles(P.x + P.w/2, P.y + P.h - 4, '#d4a84b', 8);
    } else {
      if(dir > 0) P.x = PB.x - P.w;
      else        P.x = PB.x + PB.w;
      P.vx = 0;
    }
  } else {
    // ── NEW: Skip X separation if player is landing on top ──
    if(isOnTop) return; // let Y landing check handle this frame
    // ──────────────────────────────────────────────────────
    if(centerP < centerB) P.x = PB.x - P.w;
    else                  P.x = PB.x + PB.w;
  }
}
```

**Guard logic breakdown:**
| Condition | Purpose |
|-----------|---------|
| `playerBottom >= pushTop - onTopTolerance` | Player feet have reached or are near pushblock top |
| `playerBottom <= pushTop + P.h / 2` | Player hasn't sunk more than half their height into pushblock (not beside it) |
| `P.y < pushTop` | Player top is above pushblock top (not embedded from side) |
| `onTopTolerance = 8` | Accounts for gravity adding velocity — at 0.07 g/frame, a falling player might pass through 2-4px before the frame ends; 8px gives margin |

### Step 2: Verify the guard doesn't break horizontal pushing

**Horizontal push scenario** (player beside pushblock, walking toward it):
- `P.onGround` is true (standing on ground)
- `movingToward` is true (walking toward block)
- `isOnTop` check: `playerBottom >= pushTop - 8` is likely true (same ground level) BUT `P.y < pushTop` is false because player bottom is at ground level and pushblock is on ground level, so `P.y` (player top) is NOT above `PB.y` (pushblock top) — they're at the same Y level
- Wait — actually `P.y` is the player's top coordinate. If both are on the same ground, `P.y` would be above `PB.y` by some amount since the player is shorter (28px) than the pushblock (32px). Let me reconsider...

**Revised analysis for horizontal push:**
- Both on ground: player bottom at ground Y, pushblock bottom at ground Y
- Player height = 28, pushblock height = 32
- `P.y = groundY - 28`, `PB.y = groundY - 32`
- `isOnTop` check: `P.y < pushTop` => `groundY - 28 < groundY - 32` => `-28 < -32` => **false**
- Result: `isOnTop` is false, guard does NOT trigger, normal push path taken
- **Horizontal push preserved.** Good.

**Landing scenario:**
- Player falling, bottom near pushblock top
- `playerBottom = P.y + 28` approaching `PB.y` (pushblock top)
- When `P.y + 28 >= PB.y - 8` and `P.y + 28 <= PB.y + 14` and `P.y < PB.y`
- All three conditions true when player feet are just touching or slightly overlapping pushblock top
- `isOnTop` = true, guard triggers, X separation skipped
- Next frame Y landing check sets `P.y = PB.y - 28`, `P.onGround = true`
- **Landing works.** Good.

### Step 3: Verify walking on top

**Walking on top scenario:**
- Player standing on pushblock: `P.y = PB.y - 28`, `P.onGround = true`
- Player moves horizontally: AABB might briefly overlap pushblock corners
- `isOnTop` check: `P.y < PB.y` => `PB.y - 28 < PB.y` => **true**
- `playerBottom = PB.y - 28 + 28 = PB.y`, so `playerBottom >= PB.y - 8` => **true**
- `playerBottom <= PB.y + 14` => `PB.y <= PB.y + 14` => **true**
- `isOnTop` = true, X separation skipped even during corner grazing
- **Walking on top preserved.** Good.

But wait — if `isOnTop` is always true when on top, what about when the player is on top and the AABB overlaps significantly from a side movement? Let me think...

When standing on top:
- Player is centered or offset on the 32px-wide pushblock
- Player width is 24px, pushblock is 32px
- Max overhang = (24-32)/2 = -4px when centered, so player is fully within pushblock width when centered
- If player walks to the edge, player x ranges from `PB.x` to `PB.x + 32 - 24 = PB.x + 8`
- The AABB check `aabb(P.x, P.y, 24, 28, PB.x, PB.y, 32, 32)` would return true because player top (`P.y = PB.y - 28`) overlaps pushblock top (`PB.y`) vertically: `P.y < PB.y + 32` => `PB.y - 28 < PB.y + 32` => true
- But `isOnTop` would be true (all three conditions met), so X separation is skipped
- This is correct — we DON'T want X separation when on top

**Edge case: player walking off the edge of the pushblock**
- When player walks past the pushblock edge, the AABB might still overlap
- But the X collision from normal tile movement (lines 629-660) doesn't handle pushblock entity — it's only tile-based
- The `resolvePushBlockCollision()` is the only handler for pushblock entity collision
- If player walks past edge, AABB no longer overlaps (player x > PB.x + 32 or player x + 24 < PB.x), so function returns early at line 183
- **Edge walking handled correctly.**

---

## 5. Code Diff (Exact Changes)

```diff
 function resolvePushBlockCollision(){
   if(!P.canPush || !PB.active || PB.inSlot) return;
   if(!aabb(P.x, P.y, P.w, P.h, PB.x, PB.y, PB.w, PB.h)) return;

   const centerP = P.x + P.w / 2;
   const centerB = PB.x + PB.w / 2;
   const dir = (centerP < centerB) ? 1 : -1;

   const movingToward = (P.vx * dir > 0.1);

+  // Y-overlap guard: skip X separation when player is landing on top
+  const isOnTop = P.y < PB.y
+                 && P.y + P.h >= PB.y - 8
+                 && P.y + P.h <= PB.y + P.h / 2;

   if(P.onGround && movingToward){
     const tileStep = dir * T;
     if(!tileCollides(P.chamber, PB.x + tileStep, PB.y, PB.w, PB.h)){
       PB.x += tileStep;
       if(dir > 0) P.x = PB.x - P.w;
       else        P.x = PB.x + PB.w;
       P.vx = 0;
       spawnParticles(P.x + P.w/2, P.y + P.h - 4, '#d4a84b', 8);
     } else {
       if(dir > 0) P.x = PB.x - P.w;
       else        P.x = PB.x + PB.w;
       P.vx = 0;
     }
   } else {
+    if(isOnTop) return; // let Y landing check (lines 689-698) handle this
+
     if(centerP < centerB) P.x = PB.x - P.w;
     else                  P.x = PB.x + PB.w;
   }
 }
```

**Total lines changed:** +7 lines added, 0 lines removed, 0 lines modified in other locations.

---

## 6. Innovate Checkpoint

### Alternative considered: tighten Y landing tolerance
The Y landing check (lines 689-698) already has a tolerance of 4px (`prevY + P.h <= PB.y + 4`). The guard tolerance of 8px is intentionally wider than the landing check to ensure we catch the overlap frame, while the landing check itself uses a tighter tolerance for precision. This is correct — the guard is a "don't separate" signal, the landing check is a "place precisely" signal.

### Risk: player stuck inside pushblock from extreme angles
If the player somehow enters the pushblock from a steep diagonal, the `isOnTop` check might be true even when the player is more "beside" than "on top." The `P.y < PB.y` guard prevents this: if player top is below pushblock top, the player is not on top. Combined with `P.y + P.h <= PB.y + P.h / 2`, we ensure the player hasn't sunk deep into the block.

### Risk: pushblock moving under player while standing on it
When `updatePushBlock()` moves the pushblock, if the pushblock falls under the player, the player should still land on it. The guard doesn't depend on pushblock velocity — it's purely positional. This is fine.

### Recommendation: NO additional innovation needed. Option B is minimal and sufficient.

---

## 7. Verification Plan

### Automated verification (browser console frame trace)

**Test 1: Landing from above**
1. Open golem.html in browser, press `T` for test chamber
2. Position player above pushblock (use debug or jump from platform)
3. Open browser console, add frame trace before running:
   ```javascript
   // In console before testing:
   const origUpdate = update;
   let frame = 0;
   update = function(...args) {
     origUpdate.apply(this, args);
     if(PB.active && aabb(P.x, P.y, P.w, P.h, PB.x, PB.y, PB.w, PB.h) ||
        Math.abs(P.y + P.h - PB.y) < 20) {
       console.log(`Frame ${++frame}: onGround=${P.onGround}, P.y=${P.y.toFixed(1)}, P.vy=${P.vy.toFixed(2)}, PB.y=${PB.y}, overlap=${aabb(P.x,P.y,P.w,P.h,PB.x,PB.y,PB.w,PB.h)}`);
     }
   };
   ```
4. Expected: see `onGround=true` within 1-2 frames of player reaching pushblock top
5. Expected: `P.vy` drops to 0
6. Expected: no horizontal displacement (P.x should not change suddenly)

**Test 2: Walking on top**
1. After landing (Test 1), press left/right arrow keys
2. Expected: `onGround=true` maintained while player walks on pushblock
3. Expected: player can jump from pushblock (jumps reset to 0 on landing)

**Test 3: Horizontal push from side**
1. Position player beside pushblock on same ground level
2. Walk toward pushblock
3. Expected: pushblock moves one tile in direction of push
4. Expected: `resolvePushBlockCollision()` takes the `if(P.onGround && movingToward)` branch
5. Expected: `isOnTop` is false (verified by console: `P.y < PB.y` is false)

**Test 4: Pushing against wall**
1. Push pushblock until it hits a solid tile
2. Expected: pushblock stops, player is snapped to edge (existing behavior preserved)

**Test 5: Falling past pushblock (no landing)**
1. If player has significant vertical velocity and passes through pushblock area in one frame (extreme case)
2. Expected: guard doesn't prevent normal collision resolution in edge cases
3. Expected: Y landing check handles or player falls past (acceptable — gravity is 0.07, unlikely to skip)

### Manual verification checklist:
- [ ] Player lands on pushblock from above -> stands on it
- [ ] Player can walk left/right while on pushblock
- [ ] Player can jump from pushblock (first jump, double jump)
- [ ] Player can push pushblock horizontally from the side
- [ ] Pushing against wall still works
- [ ] Pushblock still falls into slot correctly
- [ ] No console errors
- [ ] Existing chambers (0-4) still playable

---

## 8. Execution Slices (for executor-agent)

### Slice 1: Implement the guard
- **File:** `golem.html`
- **Change:** Add 7 lines to `resolvePushBlockCollision()` (lines ~181-208)
- **Effort:** ~1 minute
- **Risk:** Low (single function, well-understood logic)
- **Validator:** Code loads without JS syntax errors

### Slice 2: Verify landing behavior
- **Test:** Browser console frame trace (Test 1 above)
- **Validator:** `onGround=true` within 2 frames, no horizontal displacement
- **Rollback:** If guard is too aggressive, widen/narrow tolerance (8px)

### Slice 3: Verify horizontal push still works
- **Test:** Browser manual test (Tests 2-5 above)
- **Validator:** All 5 tests pass
- **Rollback:** If push broken, `isOnTop` logic needs refinement

### Slice 4: Regression check
- **Test:** Play through chambers 0-4
- **Validator:** No new bugs introduced, existing mechanics intact
- **Rollback:** Full revert if regression found

---

## 9. Rollback Plan

If the fix introduces regressions:
1. Revert `resolvePushBlockCollision()` to original (remove 7 added lines)
2. File: `golem.html`, lines ~189-207
3. Original code is simple enough to restore manually if git isn't available

---

## 10. Success Criteria

The fix is complete when:
1. Player can fall onto pushblock and land on top (`onGround=true`)
2. Player can walk on top of pushblock without being kicked aside
3. Player can jump from pushblock
4. Player can still push pushblock horizontally from the side
5. Browser console frame trace confirms `onGround=true` when standing on pushblock
6. Zero JavaScript errors in console
7. Existing chambers (0-4) still function correctly

---

**Plan status:** Ready for execution
**Estimated effort:** < 5 minutes (code change + verification)
**Risk level:** Low (minimal, localized change)
