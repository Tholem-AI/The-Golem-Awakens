# Project Reference

Condensed reference for `golem.html` architecture, physics tuning rationale, and push-block system design.

---

## Architecture

Single HTML file (~1716 lines, ~62 KB) organized into 12 sections with delimiter comments.

### Section Map

| # | Section | Functions |
|---|---------|-----------|
| 1 | SETUP & CONSTANTS | Canvas, tile types, dash/physics constants, PARTICLE_COLORS, GLYPH_EFFECTS, static UI arrays |
| 1.5 | UTILITIES | `snapToTileX`, `playerGridPos`, `endDash`, `land`, `easeOutCubic`, `syncPrevKeys`, `advanceTimers`, `fullDashReset`, `cancelDash`, `resetPlayerToRespawn`, `killAndRespawn` |
| 2 | CHAMBER DATA | `mkGrid()`, 6 chamber IIFEs (Ch.0-4 + Test) |
| 3 | ENTITIES | `P` (player), `PB` (push block), game state globals |
| 4 | INPUT | Key listeners, `fresh()`, `shiftHeld()`, 5 input helper functions |
| 5 | TILE HELPERS & COLLISION | `getTile`, `setTile`, `solid`, `platSolid`, `tileCollidesRect`, `collides*`, `inPit`, `aabb`, `pushBlockHit`, `isRiding`, `resolveBlockX`, `moveBlockRiders`, `applyBlockVelocityX`, `resolveBlockY`, `activePushBlocks`, `checkPushBlockCrush` |
| 6 | PUSH BLOCK SYSTEM | `resetPushBlock`, `resolvePushBlockCollision`, `updatePushBlock` (3-phase orchestrator + crush) |
| 7 | PARTICLE SYSTEM | IIFE: `Particles.shatter`, `.spawn`, `.update` |
| 8 | GAME FLOW | `MSG_*` constants, `showMessage`, `calcDisplayDuration`, `_doTransition`, `transition`, `checkDoors`, `checkGlyphs`, `transitionEnding` |
| 9 | UPDATE | Main physics/input/game logic loop |
| 9.5 | ANIMATION STATE MACHINE | Death/respawn animations (idle -> dying -> respawning -> idle) |
| 10 | RENDER | `COLORS`, `render()` — all drawing |
| 11 | INIT & GAME LOOP | Init code, `loop()`, `requestAnimationFrame` |

### Key Design Decisions

- **Single file** — no build step, no modules, no external assets. All visuals drawn procedurally with Canvas 2D primitives.
- **Function hoisting** — all helpers use `function` declarations (not `const` arrow functions), so order within file does not matter.
- **60 FPS target** — all physics constants are tuned for 60 FPS. Changing frame rate requires re-tuning.

### Dependency Flow

```
Constants --> Chamber Data --> Entities --> Input --> Tile Helpers
                                                    |
Push Block --> Particles --> Game Flow --> Update / Render (both depend on all above)
```

---

## New Data Structures (added in refactoring)

### PARTICLE_COLORS (Section 1)

Named color constants extracted from particle spawn call sites to centralize color configuration:

```javascript
const PARTICLE_COLORS = {
  jump: '#8a7d6b',
  doubleJump: '#d4a84b',
  glyph: '#f0d060',
  dashBurst: 'rgba(220,120,255,0.6)',
  death: '#8a7d6b',
};
```

### GLYPH_EFFECTS (Section 1)

Data-driven glyph ability system — each entry maps a glyph index to its setter function and activation message:

```javascript
const GLYPH_EFFECTS = [
  { set: () => { P.maxJumps = 2; }, msg: "Knowledge lifts me." },
  { set: () => { P.canDash = true; }, msg: "Speed courses through me." },
  { set: () => { P.canPush = true; }, msg: "Strength returns." },
  { set: () => { P.canBreak = true; }, msg: "Clay becomes Wisdom." },
];
```

### MSG_* Constants (Section 8)

Message system constants moved from Section 1 to Section 8 (GAME FLOW) for co-location with `showMessage()`:

| Constant | Value | Purpose |
|----------|-------|---------|
| `MSG_FADE_IN_FRAMES` | 180 | Fade-in duration (frames) |
| `MSG_FADE_OUT_FRAMES` | 180 | Fade-out duration (frames) |
| `MSG_MAX_QUEUE_DEPTH` | 5 | Maximum queued messages |
| `MSG_CHARS_PER_FRAME` | 0.35 | Typewriter scroll rate |
| `MSG_MIN_HOLD` | 90 | Minimum display time (frames) |
| `MSG_MAX_HOLD` | 360 | Maximum display time (frames) |
| `MSG_FOREVER_THRESHOLD` | 99999 | Duration value for permanent messages |

---

## Utility Functions (Section 1.5)

All shared helper functions consolidated in a dedicated section between Setup/Constants and Chamber Data.

| Function | Purpose |
|----------|---------|
| `snapToTileX(gx1, gx2, prevX)` | Snap player X to tile boundary after collision |
| `playerGridPos()` | Return player center as grid coordinates `{gx, gy}` |
| `endDash()` | End dash state cleanly; sets cooldown to `DASH_COOLDOWN` |
| `land()` | Land on ground — reset jumps and coyote timer |
| `easeOutCubic(t)` | Easing function for death/respawn animations |
| `syncPrevKeys()` | Snapshot `prevKeys = { ...keys }` (replaces unbounded `for...in` copy) |
| `advanceTimers()` | Advance message queue phases + decrement portal lock timer |
| `fullDashReset()` | Reset all dash state — used on death/transition (clears charge too) |
| `cancelDash()` | Cancel active dash without resetting cooldown — used on immediate death |
| `resetPlayerToRespawn()` | Restore player position and velocity to respawn point |
| `killAndRespawn(msg, duration)` | Kill and respawn player; triggers death animation (no `onGround` param) |

### API Change Notes

- `killAndRespawn()` no longer takes an `onGround` parameter (was unused in all callers)
- `setTile()` simplified — no longer maintains `solidTiles` set (removed for clarity; `solidTiles` is optional cache)

---

## Physics Tuning Rationale

Current physics constants were tuned to align with human reaction time (~250ms).

### Tuning Goals

1. **Horizontal speed halved** (from 5.0 to 2.5 px/frame) — gives deliberate, readable pacing
2. **First jump same peak height** (179 px / ~5.6 tiles) — vertical reach unchanged from original
3. **Double jump smaller arc** (~75% of first jump = 134 px / ~4.2 tiles) — prevents double jump from dominating
4. **Floatier feel** — reduced gravity (0.28 -> 0.07) doubles airtime, giving more decision time mid-air

### Math

```
Peak height = vy^2 / (2 * g)
Same height with half vy -> g_new = g_old * (vy_new^2 / vy_old^2)
                            = 0.28 * (5^2 / 10^2) = 0.07

Double jump target: ~75% of first jump height = 134 px
vy_2 = -sqrt(2 * g_new * target_height) = -sqrt(2 * 0.07 * 134) = -4.33
```

### Current Constants (see golem.html section 1)

| Constant | Value | Purpose |
|----------|-------|---------|
| `H_ACCEL_GROUND` | 0.05 | Horizontal acceleration on ground |
| `H_ACCEL_AIR` | 0.2 | Horizontal acceleration airborne |
| `H_FRICTION` | 0.225 | Horizontal deceleration |
| `GRAVITY` | 0.07 | Gravity per frame |
| `TERMINAL_VEL` | 2.5 | Max velocity (X and Y) |
| `JUMP_VEL_1` | -5 | First jump velocity |
| `JUMP_VEL_2` | -4.33 | Double jump velocity |
| `JUMP_CUT_VEL` | -2 | Variable jump cutoff |
| `COYOTE_FRAMES` | 12 | Coyote time (200ms) |
| `JUMP_BUFFER_FRAMES` | 12 | Jump buffer (200ms) |
| `CHARGE_FRICTION` | 0.85 | Dash charge state friction |

### Derived Metrics

| Metric | Value |
|--------|-------|
| First jump peak | 179 px (~5.6 tiles) |
| First jump airtime | ~161 frames (~2.7s) |
| Double jump peak | 134 px (~4.2 tiles) |
| Double jump airtime | ~133 frames (~2.2s) |
| Horizontal tiles/sec | ~4.7 |
| Time to max speed (ground) | ~50 frames (~833ms) |
| Stopping distance from max | ~28 px (~0.9 tiles) |

### Dash Gravity

Dash charge state uses 1/10th gravity (`P.vy * 0.1 + 0.007`) for near-weightless feel during aiming.

### Forgiveness Mechanics

- **Coyote time** (12 frames / 200ms) — allows jumping slightly after walking off edge
- **Jump buffer** (12 frames / 200ms) — registers jump input pressed slightly before landing
- **Variable jump** — release early for short hops (minimum ~29 px)

---

## Push Block System Design

### Rationale

Replaced instant tile-step push with velocity-based movement for smooth, predictable behavior.

### Key Mechanics

1. **Half-speed push** — `PUSH_SPEED = 1.25 px/frame` (half of walk speed 2.5)
2. **Velocity-based** — `PB.vx = dir * PUSH_SPEED` instead of `PB.x += dir * T`
3. **Smooth clamp** — golem velocity clamped (not zeroed) during active push
4. **Gap gravity** — smooth movement lets existing `PB.vy += PB_GRAVITY` act naturally over gaps
5. **Airborne guard** — `P.onGround` required; airborne golem separates without pushing
6. **Y-overlap guard** — prevents X separation when player is landing on top of push block

### Y-Overlap Guard

In `resolvePushBlockCollision()`, the `isOnTop` guard prevents horizontal knock when the player is falling onto the push block:

```
isOnTop = P.y < PB.y                    // player top above push block
        && P.y + P.h >= PB.y - 8        // player feet near push block top (8px tolerance)
        && P.y + P.h <= PB.y + P.h/2    // player not sunk deeper than half height
```

**Why 8px tolerance:** Accounts for variable fall distance per frame. Gravity at 0.07 px/frame^2 means a falling player may overshoot the push block top by 2-4px before the frame ends. 8px provides margin.

### Push Animation

- `P.pushing` flag set only during active push frames
- Forward-leaning squash: `w-3`, `h-1`, 3px lean offset toward push direction
- Pulsing golden arm/shoulder lines (sin-based, ~150ms period)
- Takes priority in squash/stretch if/else chain (checked first)

### Push Block Physics

| Constant | Value |
|----------|-------|
| `PB_GRAVITY` | 0.3 |
| `PB_TERMINAL_VEL` | 4 |
| `PB_FRICTION` | 0.85 |
| `PB_STOP_THRESH` | 0.1 |

### Update Order

1. `P.pushing = false` (per-frame reset before movement)
2. Player X movement + tile collision
3. `resolvePushBlockCollision()` — detects overlap, applies push or separation
4. `updatePushBlock()` — 3-phase orchestrator (block physics only):
   - Phase A: `applyBlockVelocityX()` — each block moves horizontally by its vx, records `_frameDx`
   - Phase B: `moveBlockRiders()` — riders get the same `_frameDx` with their own wall collision
   - Phase C: `resolveBlockY()` — gravity + tile/block Y resolution
   - Phase D: friction, slot detection, fall reset, `_frameDx` cleanup
5. Player Y movement + tile/platform collision
6. Push block landing on golem (line ~1092)
7. `checkPushBlockCrush()` — after player Y resolved, so P.y is accurate:
   - Guard 1: `P.y + P.h <= pb.y + 4` — golem on top of block, skip
   - Guard 2: `pb.y >= P.y + P.h - 4` — block below golem feet, skip
   - Guard 3: `overlapW < 10` — side brush, skip
   - All 3 passed → crush death

All phases process blocks bottom-up (`activePushBlocks()` sorts by descending y).

### Block-vs-Block Collision

Push blocks collide with each other via AABB overlap (`pushBlockHit()` helper in Section 5).

**Horizontal:** blocks treat other blocks as solid walls. Pushing block A into block B stops A at B's face. No chain-push — A does not transfer momentum to B.

**Vertical:** blocks stack on top only. `prevBottom <= hitY.y + 2` tolerance matches the player landing check, so a falling block only lands when it was above the other block's top face the previous frame. Side overlap is ignored (X resolution handles it). Blocks also resolve upward collision (`pb.vy < 0`) when pushed from below.

**Riders:** `moveBlockRiders(ch, pb, dx)` drags blocks sitting on top of a moving block. A rider is detected by `isRiding()` — feet proximity (`|feet - base.y| <= 2`) and horizontal overlap (with 2px margin). Each rider calls `resolveBlockX(ch, ob, dx)` so it has its own wall and block-vs-block collision — it does not blindly offset by dx. If the support block falls off an edge, gravity pulls the rider down the next frame — no artificial binding.

**Crush death:** `checkPushBlockCrush()` runs after player Y + landing resolution, so P.y reflects the resolved position. Requires all 3 guards to pass before triggering:

1. Vertical guard 1: `P.y + P.h <= pb.y + 4` — skip if golem is on top of block (landing/riding)
2. Vertical guard 2: `pb.y >= P.y + P.h - 4` — skip if block is below golem feet (support, not crusher)
3. Horizontal guard: `overlapW < 10` — skip if horizontal overlap is <10px (side brush, not landing on golem)

All 3 pass → block is genuinely falling onto the golem → `killAndRespawn()` with "The weight crushes you..." message. Guarded by `animState !== 'idle'` so death/respawn animations are immune.

**Processing order:** `activePushBlocks()` filters to active, non-slotted blocks and sorts by descending y (bottom-up). All four phases use this order, so gravity and stacking resolve correctly — lower blocks move before blocks resting on them.

**Transient state:** `pb._frameDx` records Phase A net displacement for Phase B rider coupling. Cleared in Phase D.

**Design decisions:**
- `pushBlockHit()` skips self and inactive blocks but keeps `inSlot` blocks solid (locked-in blocks are immovable anchors)
- No chain-push or domino mechanics — solid contact only
- Separate from `tileCollides()` to keep grid and entity logic independent
- Separate from `resolvePushBlockCollision()` (player-to-block) to keep concerns isolated
- Crush check before player Y prevents the golem from jumping away in the same frame a block falls on it

**Bugfix note:** `resolvePushBlockCollision()` originally used `return` instead of `continue` when skipping an `isOnTop` block, which caused remaining blocks in the loop to never be checked. Fixed to `continue` so all active blocks are evaluated.

---

## Tile System

| Constant | Value | Description |
|----------|-------|-------------|
| `AIR` | 0 | Empty space |
| `WALL` | 1 | Solid wall |
| `PIT` | 2 | Death void |
| `GOLEM_SPAWN` | 3 | Player spawn marker (invisible, determines golem position) |
| `DOOR_D` | 4 | Down-side exit (glyph-locked) |
| `GLYPH` | 5 | Collectible |
| `CRACKED` | 7 | Breakable (dash + Glyph 4) |
| `PLATFORM` | 8 | One-way (solid from top only) |
| `END_PORTAL` | 9 | Final portal |
| `MAGICAL_WALL` | 10 | Dash-passable, kills on non-dash contact |
| `PUSH_SPAWN` | 11 | Push block spawn marker |

Note: `BLOCK` (value 6) was removed during optimization. Value gap is preserved to avoid renumbering.

### Solidity Rules

- `solid(t)` — WALL, CRACKED, DOOR_D, END_PORTAL, MAGICAL_WALL
- `platSolid(t, prevY, curY)` — PLATFORM is solid ONLY when landing from above
- `GOLEM_SPAWN` (3) is NOT solid — invisible pass-through tile
- Push block entity (`PB`) has its own collision via `resolvePushBlockCollision()`

### setTile Simplification

The `setTile()` function was simplified: it no longer maintains the optional `solidTiles` cache set. The `solid()` function checks tile type values directly, making the cache redundant. The `solidTiles` Set still exists as an optional cache but is not updated by `setTile()`.

---

## Chamber Design

- Grid: 25 columns x 15 rows
- Tile size: 32x32 px (canvas 800x480)
- See `chamber-data.md` for ASCII grids and `chamber-template.md` for format spec
- Grant-then-use chain: Chamber N grants ability for Chamber N+1

---

## Dead Code Removed (refactoring)

The following was identified as dead/unused and removed during the Master Improvement Plan:

| Item | Reason |
|------|--------|
| `easeInOutCubic()` | Defined but never called |
| `easeOutBack()` | Defined but never called |
| `_testMode` | Always false; dead code paths in `transition()` and `transitionEnding()` |
| Duplicate "I awaken..." overlay | `X.fillText` in render was redundant with `showMessage()` queue |
| HUD dash bar indicator | Redundant with centered ring indicator |
| Push slot `pushSlot` code | No chamber defines `pushSlot`; dead game logic (preserved `inSlot` property for future use) |
| `pushSpawns` fallback | Dead reference in `resetPushBlock()` |
