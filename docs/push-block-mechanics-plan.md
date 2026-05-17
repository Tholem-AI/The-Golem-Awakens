# Execution Plan: Push Block Mechanics Overhaul

## Project: The Golem Awakens (`golem.html`)
## Date: 2026-05-16
## Plan Type: Planner-Agent (RIPER — Plan Phase)
## Checkpoint: INNOVATE (non-trivial change spanning physics, collision, and rendering)

---

## INNOVATE CHECKPOINT

### Scope Assessment
This change touches three interdependent systems:
- **Physics**: Replace instant tile-step with velocity-based PB movement (Req 1, 2)
- **Collision**: Rewrite `resolvePushBlockCollision()` logic for smooth, continuous push (Req 2, 7)
- **Rendering**: Add forward-leaning squash/stretch push animation (Req 3)

### Risk Analysis
| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking existing chamber 4 puzzle (push block + slot) | HIGH | Test chamber 4 specifically after each task |
| Golem gets stuck inside block during push | HIGH | Strict AABB overlap guard + separation logic |
| Push velocity conflicts with normal walking input | MEDIUM | Gate push physics behind `P.pushing` state flag |
| Block falls through floor during gap push | MEDIUM | PB already has gravity; verify after smooth push enables gravity to act |
| Dash interacts badly with push blocks | LOW | `collidesDash` already treats PB as solid — no change needed |

### Design Decisions (Locked)
1. **Push speed**: `PUSH_SPEED = 1.25 px/frame` (half of `P.walkSpeed = 2.5`)
2. **During push**: Golem and block both move at `PUSH_SPEED` — golem's horizontal velocity is clamped
3. **Push state**: Set `P.pushing = true` in `resolvePushBlockCollision()` when active push conditions met
4. **Gap detection**: No explicit gap check needed — smooth push lets `updatePushBlock()` gravity (lines 252-259) act naturally on the block over a gap
5. **Wall blocking**: Existing `tileCollides` check in `updatePushBlock()` (line 245) already stops PB against walls — fixing the snap (Req 2) means golem can walk away naturally
6. **Animation**: Forward-leaning squash during push — narrower (w-3), slightly compressed (h-1), offset toward push direction

### Dependencies
- No external dependencies
- Internal: relies on existing `P.pushing` flag (line 148), existing `PB` physics (lines 232-283), existing squash/stretch rendering pattern (lines 972-976)
- Requirements 5 (no push airborne) and 6 (respawn on death) already work — no changes needed

---

## ORDERED EXECUTION TASKS

### TASK 1: Define Push Constants and Refactor `resolvePushBlockCollision()`
**Requirements addressed**: 1 (half-speed), 2 (smooth push), 7 (wall blocking)
**Impact scope**: Lines 181-214 (entire `resolvePushBlockCollision` function)

#### Changes:

**1a. Add push speed constant** (new line after line 31, before Level data):
```javascript
const PUSH_SPEED = 1.25;  // px/frame — half of walk speed 2.5
```

**1b. Replace `resolvePushBlockCollision()` (lines 181-214) entirely:**

REPLACE lines 179-214 with:
```javascript
/* Push block: resolve AFTER normal X movement + tile collision.
   Detect push overlap and apply velocity-based movement (not instant teleport). */
function resolvePushBlockCollision(){
  if(!P.canPush || !PB.active || PB.inSlot) return;
  if(!aabb(P.x, P.y, P.w, P.h, PB.x, PB.y, PB.w, PB.h)) return;

  const centerP = P.x + P.w / 2;
  const centerB = PB.x + PB.w / 2;
  const dir = (centerP < centerB) ? 1 : -1;

  const movingToward = (P.vx * dir > 0.1);

  // Y-overlap guard: skip X separation when player is landing on top
  const isOnTop = P.y < PB.y
                 && P.y + P.h >= PB.y - 8
                 && P.y + P.h <= PB.y + P.h / 2;

  if(P.onGround && movingToward){
    // ── Active push: velocity-based ──
    P.pushing = true;

    // Apply push velocity to the block (half walk speed)
    PB.vx = dir * PUSH_SPEED;

    // Clamp golem to same push speed (don't zero, just limit)
    if(Math.abs(P.vx) > PUSH_SPEED) P.vx = dir * PUSH_SPEED;

    // Keep golem glued to block side (smooth, no snap)
    if(dir > 0) P.x = Math.min(P.x, PB.x - P.w + 1);
    else        P.x = Math.max(P.x, PB.x + PB.w - 1);

    spawnParticles(P.x + P.w/2, P.y + P.h - 4, '#d4a84b', 2);

  } else if(movingToward && !P.onGround){
    // Requirement 5: no push while airborne — separate
    if(dir > 0) P.x = PB.x - P.w;
    else        P.x = PB.x + PB.w;

  } else {
    // Not pushing — static separation (walking past, standing against)
    if(isOnTop) return; // let Y landing check (lines 689-704) handle this
    if(centerP < centerB) P.x = PB.x - P.w;
    else                  P.x = PB.x + PB.w;
  }
}
```

#### Key differences from current code:
- **No `tileStep = dir * T`** — replaced with `PB.vx = dir * PUSH_SPEED`
- **No `P.x = PB.x - P.w` snap** — replaced with `Math.min`/`Math.max` soft clamp
- **No `P.vx = 0`** — golem keeps velocity (clamped to push speed)
- **`P.pushing = true`** is now actually set during active push
- Added `+1`/`-1` pixel offset to prevent re-triggering overlap every frame

#### Validation Gate 1:
- [ ] Game loads without JS errors
- [ ] Walking into block from left pushes it right smoothly (not instant snap)
- [ ] Walking into block from right pushes it left smoothly
- [ ] Holding left/right after pushing keeps block moving at ~1.25 px/frame
- [ ] Releasing keys stops pushing — block slows via existing friction (line 262)
- [ ] Jumping while touching block does NOT push it (Req 5 — airborne guard)

---

### TASK 2: Ensure `P.pushing` Resets Correctly
**Requirements addressed**: 3 (push animation flag)
**Impact scope**: Line 636, lines 196-210 (push detection in Task 1 already sets it)

#### Changes:

**2a. Verify reset logic** (line 636 — already correct):
```javascript
P.pushing = false;  // Reset every frame before movement
```
This line already exists and is in the right position (before X movement and push collision). Task 1 sets it to `true` only when an active push is detected, so it naturally resets each frame when no push occurs.

#### Validation Gate 2:
- [ ] `P.pushing` is `true` only during active push frames
- [ ] `P.pushing` is `false` when standing still against block
- [ ] `P.pushing` is `false` when walking away from block

---

### TASK 3: Add Push Animation to Golem Rendering
**Requirements addressed**: 3 (visual push animation)
**Impact scope**: Lines 972-1005 (player squash/stretch rendering)

#### Changes:

**3a. Add push animation state to the squash/stretch block (after line 976, before line 978):**

REPLACE lines 972-977 with:
```javascript
 /* ── Player (squash & stretch) ── */
  let pw=P.w, ph=P.h, poffX=0, poffY=0;
  const fallingFast = P.vy > 3;
  if(P.pushing){
    // Push animation: forward-leaning squash (narrower, slightly compressed)
    pw = P.w - 3;
    ph = P.h - 1;
    poffX = P.facing * 3;  // lean toward push direction
    poffY = 1;
  }
  else if(!P.onGround && P.vy<0){ pw=P.w-3; ph=P.h+4; poffY=-4; }
  else if(P.onGround && Math.abs(P.vx)>1){ pw=P.w+3; ph=P.h-2; poffY=2; }
  else if(fallingFast){ pw=P.w-2; ph=P.h+6; poffY=-2; }
```

**3b. Update the rendering x offset to include `poffX` (line 978):**

REPLACE line 978 with:
```javascript
  const px=ox+P.x+(P.w-pw)/2+poffX, py=oy+P.y+poffY;
```

**3c. Add push effort visual: arms press forward (after line 989, before glyph lines at 991):**

INSERT after line 989:
```javascript
  /* Push effort: arms press into block */
  if(P.pushing){
    const effortPulse = Math.sin(Date.now()/150)*0.15+0.3;
    X.fillStyle='rgba(212,168,75,'+effortPulse+')';
    // Arm/shoulder lines toward push direction
    const armX = P.facing > 0 ? px+pw-2 : px-3;
    X.fillRect(armX, py+8, 5, 3);
    X.fillRect(armX+(P.facing>0?2:-2), py+12, 5, 3);
  }
```

#### Validation Gate 3:
- [ ] Golem narrows and compresses slightly while pushing
- [ ] Golem leans forward (3px shift) in the direction of push
- [ ] Glowing arm/shoulder lines appear on the push-facing side
- [ ] Animation stops immediately when push ends
- [ ] Push animation does NOT conflict with jump/fall animations (push takes priority since P.onGround is required for pushing)

---

### TASK 4: Verify Gap Gravity Behavior (Req 4)
**Requirements addressed**: 4 (block falls when pushed over gap)
**Impact scope**: No code changes expected — verify behavior with new smooth push

#### Analysis:
- Current `updatePushBlock()` already applies gravity at lines 252-259 (`PB.vy += 0.3`)
- The instant 32px tile-step in old code teleported block over gaps before gravity could act
- With smooth 1.25 px/frame movement (Task 1), block will enter the gap tile area and gravity will pull it down naturally
- The tile collision check at line 245-249 handles X collision with solid tiles
- The tile collision check at line 255-259 handles Y collision (landing on ground below gap)

#### Changes: None (behavioral fix emerges from Tasks 1+2)

#### Validation Gate 4:
- [ ] Pushing block over the test chamber pit causes block to fall
- [ ] Block falls at natural gravity rate (0.3 acceleration, 4 max, per lines 252-253)
- [ ] Block resets when it falls past bottom (line 279-282 existing logic)
- [ ] Chamber 4 puzzle still works — block can still be pushed into the slot (lines 266-276)

---

### TASK 5: Verify Wall Blocking Behavior (Req 7)
**Requirements addressed**: 7 (solid block blocking)
**Impact scope**: No code changes expected — verify behavior with new smooth push

#### Analysis:
- `updatePushBlock()` line 245-249 already checks `tileCollides` for PB X movement
- If PB hits a wall, `PB.vx = 0` (line 248), block stops
- With smooth push, golem is clamped to block side (Task 1: `Math.min`/`Math.max`)
- Golem can walk away from block in other directions (velocity not zeroed, just clamped)

#### Changes: None (behavioral fix emerges from Task 1)

#### Validation Gate 5:
- [ ] Pushing block into a wall stops the block (not golem)
- [ ] Golem can walk UP/DOWN past a wall-blocked block
- [ ] Golem can walk away from block in opposite direction
- [ ] No sticking or jitter when block is against wall

---

## TESTING STRATEGY

### Automated/Manual Test Checklist

#### Test Chamber (press T — all abilities unlocked)
1. **Basic push**: Walk into block from left, verify smooth rightward movement
2. **Reverse push**: Walk into block from right, verify smooth leftward movement
3. **Half-speed**: Visually compare push speed vs walk speed — push should be ~half
4. **Release stop**: Release direction key while pushing — block should decelerate via friction (0.85 multiplier, line 262)
5. **Airborne no-push**: Jump while touching block — block should NOT move
6. **Gap fall**: Push block over a pit tile — block should fall via gravity
7. **Wall block**: Push block against wall — block stops, golem can walk past
8. **Animation check**: While pushing, golem should be narrower, compressed, leaning forward with glow lines
9. **Walk past**: Walk alongside block without pushing (not moving toward it) — block stays still

#### Chamber 4 (The Ibis Chamber) — Regression Test
1. **Puzzle solvable**: Block can still be pushed into the pushSlot (lines 266-276)
2. **Slot detection**: Block snaps to slot grid position and triggers "The weight settles" message
3. **Portal opens**: After block in slot, door/portal behavior works as expected
4. **No regression**: No new bugs introduced in existing chamber mechanics

#### All Chambers — Smoke Test
1. Chambers 0-3 load and are playable
2. No console errors
3. No visual glitches in player rendering

### Browser Test Procedure
1. Open `golem.html` in Chrome/Firefox
2. Press `T` to enter test chamber
3. Work through the Test Chamber checklist above
4. Exit test chamber (press `T` again)
5. Play through chambers 0-4, specifically chamber 4 puzzle
6. Check browser DevTools Console for JS errors

---

## TASK DEPENDENCY GRAPH

```
Task 1 (resolvePushBlockCollision rewrite)
    ├──→ Task 2 (P.pushing flag verification) — can run parallel, no code change
    ├──→ Task 4 (gap gravity verification) — no code change, depends on Task 1 behavior
    └──→ Task 5 (wall blocking verification) — no code change, depends on Task 1 behavior
    └──→ Task 3 (push animation rendering) — depends on P.pushing being set correctly
```

### Recommended Execution Order:
1. **Task 1** — Core physics/collision rewrite (most impactful)
2. **Task 2** — Verify flag behavior (quick check, no change)
3. **Task 4** — Verify gap gravity (quick check, no change)
4. **Task 5** — Verify wall blocking (quick check, no change)
5. **Task 3** — Push animation rendering (cosmetic, isolated change)
6. **Full regression test** — Chamber 4 puzzle + all chambers smoke test

---

## ROLLBACK PLAN
- Each task modifies distinct code regions, making partial rollback easy
- Task 1 is the highest-risk — keep a backup of lines 179-214 before modifying
- If Task 1 causes issues, revert to original `resolvePushBlockCollision()` and iterate
- Task 3 (rendering) is fully isolated — can be added/removed without affecting physics

---

## ESTIMATED EFFORT
- Task 1: ~15 lines changed (rewrite of resolvePushBlockCollision + 1 constant)
- Task 2: 0 lines changed (verification only)
- Task 3: ~15 lines added (push animation in render)
- Task 4: 0 lines changed (verification only)
- Task 5: 0 lines changed (verification only)
- **Total**: ~30 lines of code across 2 functions
