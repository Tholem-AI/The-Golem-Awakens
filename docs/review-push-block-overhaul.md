# Review Report: Push Block Mechanics Overhaul

**Date:** 2026-05-16
**Reviewer:** Reviewer-Agent (sub-agent)
**File:** golem.html
**Plan:** docs/push-block-mechanics-plan.md

---

## Requirements Verification: ALL 7 PASS

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Block pushed at half walk speed | PASS | PUSH_SPEED=1.25, walkSpeed=2.5 (line 31, 582) |
| 2 | Pushing is smooth (velocity-based) | PASS | PB.vx=dir*PUSH_SPEED, Math.min/max soft clamp (lines 210, 216-217) |
| 3 | Push animation visible | PASS | P.pushing flag + squash/lean/effort lines (lines 992-1024) |
| 4 | Block falls over gaps | PASS | Gravity PB.vy+=0.3 in updatePushBlock (line 270), smooth push lets gravity act |
| 5 | No push when airborne | PASS | P.onGround gate at line 205, separate-only fallback at 221-224 |
| 6 | Block respawns on death | PASS | resetPushBlock() at line 767 on pit/OOB death |
| 7 | Solid block blocking | PASS | tileCollides check at line 263, PB.vx=0 at wall (line 266) |

## Code Structure Verification

### resolvePushBlockCollision() (lines 188-232)
- Guard: canPush, PB.active, !PB.inSlot, AABB overlap
- Direction detection via center comparison
- movingToward threshold: P.vx * dir > 0.1
- isOnTop guard prevents X separation during Y landing
- Three branches: active push (ground+moving), airborne separate, static separation
- Particle spawn reduced from 8 to 2 per push frame

### Push animation rendering (lines 989-1024)
- Push squash: pw=w-3, ph=h-1, poffX=facing*3, poffY=1
- Takes priority in if/else-if chain (checked first)
- No conflict: push requires P.onGround, so mutually exclusive with jump/fall animations
- Effort visual: pulsing golden arm/shoulder lines (sin-based pulse, period ~150ms)

### P.pushing flag lifecycle
- Reset: line 654 (per-frame before X movement), line 466 (chamber transition)
- Set: line 207 (only during active push)
- Correctly scoped to active push frames only

### updatePushBlock() (lines 250-301)
- X move with tile collision (line 262-267)
- Y gravity: PB.vy += 0.3, max 4 (lines 270-271)
- Friction: PB.vx *= 0.85, threshold 0.1 (lines 280-281)
- Slot detection (lines 283-294)
- Fall reset (lines 297-300)

### Game update loop order (verified correct)
1. Line 654: P.pushing = false
2. Line 656: P.x += P.vx
3. Lines 659-684: tile collision
4. Line 687: resolvePushBlockCollision()
5. Lines 690+: Y movement
6. Line 772: updatePushBlock()

### Test chamber (lines 131-147)
- 3-tile pit at columns 4-6, row 13 (gap testing)
- Wall at column 20, rows 9-12 (wall blocking testing)
- Push spawn at (12, 13)

## Issues Found

### Minor: Push speed clamp UX friction
During active push, P.vx is clamped to PUSH_SPEED (line 213). If push block is against a wall and player tries to move UP/DOWN to reposition, lateral velocity remains limited. Self-resolves when player stops pressing into the block. LOW impact.

### Minor: Plan doc chamber reference
Plan refers to "Chamber 4 (The Ibis Chamber)" for push puzzle regression, but puzzle is in Chamber 3 ("Weight of Wisdom"). Not a code issue.

## Regression Risk Assessment

| Area | Risk | Notes |
|------|------|-------|
| Chamber 3 (Weight of Wisdom) push puzzle | LOW-MEDIUM | Needs manual browser testing. Slot logic unchanged. |
| Chamber 4 (Ibis Chamber) | NONE | No push block in this chamber. |
| Player rendering | LOW | Push animation isolated, no conflict with other animations. |
| Dash + push block | NONE | Separate collision systems. |
| Platforms + push block | LOW | PLATFORM excluded from solid(), consistent with player. |

## Recommendation: READY FOR MANUAL BROWSER TESTING

All 7 requirements met. Code is clean, well-structured, and matches the plan. Manual browser testing needed for:
1. Chamber 3 push puzzle still solvable
2. Push animation renders cleanly
3. No console errors
4. Test chamber pit/wall test cases
