# Project Reference

Condensed reference for `golem.html` architecture, physics tuning rationale, and push-block system design.

---

## Architecture

Single HTML file (1240 lines, ~45 KB) organized into 11 sections with delimiter comments.

### Section Map

| # | Section | Functions |
|---|---------|-----------|
| 1 | SETUP & CONSTANTS | Canvas, tile types, dash/physics constants, static UI arrays |
| 2 | CHAMBER DATA | `mkGrid()`, 6 chamber IIFEs (Ch.0-4 + Test) |
| 3 | ENTITIES | `P` (player), `PB` (push block), game state globals |
| 4 | INPUT | Key listeners, `fresh()`, `shiftHeld()`, 5 input helper functions |
| 5 | TILE HELPERS & COLLISION | `getTile`, `setTile`, `solid`, `platSolid`, `tileCollidesRect`, `collides*`, `inPit`, `aabb` |
| 6 | PUSH BLOCK SYSTEM | `resetPushBlock`, `resolvePushBlockCollision`, `updatePushBlock` |
| 7 | PARTICLE SYSTEM | IIFE: `Particles.shatter`, `.spawn`, `.update` |
| 8 | GAME FLOW | `showMessage`, `_doTransition`, `transition`, `checkDoors`, `checkGlyphs`, `transitionEnding` |
| 9 | UPDATE | Main physics/input/game logic loop |
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
4. Player Y movement + tile/platform collision
5. `updatePushBlock()` — X move with collision, Y gravity, friction, slot detection, fall reset

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

---

## Chamber Design

- Grid: 25 columns x 15 rows
- Tile size: 32x32 px (canvas 800x480)
- See `chamber-data.md` for ASCII grids and `chamber-template.md` for format spec
- Grant-then-use chain: Chamber N grants ability for Chamber N+1
