# Tile System Reference

The Golem Awakens uses 12 tile types, each identified by a unique integer value and an ASCII character for the grid format. Tiles are 32x32 pixels on an 800x480 canvas, forming a 25x15 grid per chamber.

## Tile Legend

| Char | Constant | Value | Description |
|------|----------|-------|-------------|
| `.` | `AIR` | 0 | Empty space |
| `#` | `WALL` | 1 | Solid wall (floor, ceiling, boundaries) |
| `~` | `PIT` | 2 | Death void — touching respawns player |
| `^` | `GOLEM_SPAWN` | 3 | Player spawn marker (invisible at runtime) |
| `v` | `DOOR_D` | 4 | Exit door — follows CHAMBER_FLOW to next chamber |
| `*` | `GLYPH` | 5 | Collectible knowledge glyph |
| `X` | `CRACKED` | 7 | Breakable wall (dash through to destroy) |
| `=` | `PLATFORM` | 8 | One-way platform (walkable from above) |
| `@` | `END_PORTAL` | 9 | Final portal — triggers ending sequence |
| `M` | `MAGICAL_WALL` | 10 | Destructible barrier (dash kills on contact) |
| `S` | `PUSH_SPAWN` | 11 | Spawn marker for free-moving push block |

**Note:** Tile values are defined in `golem.html` Section 1:

```js
const AIR=0, WALL=1, PIT=2, GOLEM_SPAWN=3, DOOR_D=4, GLYPH=5, CRACKED=7, PLATFORM=8, END_PORTAL=9, MAGICAL_WALL=10, PUSH_SPAWN=11;
```

**Value 6 is skipped** — it was removed during development. Tile values jump from 5 (GLYPH) to 7 (CRACKED). The gap is intentional and should not be used.

## Collision Behavior

### `solid(t)` — Solid tiles

Returns `true` for tiles that block normal movement (walking, jumping, landing):

```js
function solid(t){
  return t===WALL || t===CRACKED || t===DOOR_D || t===END_PORTAL || t===MAGICAL_WALL;
}
```

| Tile | `solid()` | Notes |
|------|-----------|-------|
| WALL | `true` | Standard solid barrier |
| CRACKED | `true` | Blocks until broken by dash |
| DOOR_D | `true` | Blocks until glyph collected, then triggers transition |
| END_PORTAL | `true` | Blocks until reached, triggers ending |
| MAGICAL_WALL | `true` | Blocks normal movement; dash passes through |
| PLATFORM | `false` | Not solid — uses `platSolid()` instead |
| PIT | `false` | Not solid — uses `inPit()` death check instead |
| GLYPH, GOLEM_SPAWN, PUSH_SPAWN | `false` | Passable / non-blocking |

### `platSolid(t, prevFeet, gy)` — Platform collision

Handles one-way PLATFORM tiles. Returns `true` only when:

1. The tile is `PLATFORM`.
2. The player is NOT pressing Down (ArrowDown/S) — pressing Down lets you drop through.
3. The player's previous feet position was at or above the platform's top edge (within a 2px tolerance).

```js
function platSolid(t, prevFeet, gy){
  if(t!==PLATFORM) return false;
  if(inputDown()) return false;
  return prevFeet <= gy * T + 2;
}
```

This means: you land on platforms from above, pass through from below, and can drop through by pressing Down.

### `collidesDash(gx1, gy1, gx2, gy2, ch, prevY, curY)` — Dash collision

The dash uses a specialized collision checker that:

1. **Skips MAGICAL_WALL tiles** (`skipTileType: MAGICAL_WALL`) — the dash passes through magical walls, destroying them.
2. **Includes platform collision** — dash still respects one-way platforms.
3. **Checks push block AABB** — dash collides with active push blocks as solid objects.

```js
function collidesDash(gx1,gy1,gx2,gy2,ch,prevY,curY){
  if(tileCollidesRect(ch, gx1, gy1, gx2, gy2,
    {skipTileType:MAGICAL_WALL, includePlatforms:true, prevY, curY})) return true;
  // Also checks push block AABB
  return false;
}
```

## Special Behaviors

### PIT — Death void

- **Not a solid tile** — `solid(PIT)` returns `false`. The player falls through.
- **Death check:** `inPit()` uses Manhattan distance from the player's center to nearby PIT tiles. If any PIT tile is within threshold (`1.1 * TILE_SIZE`), the player dies and respawns.
- **Implementation:** Scans the 3x3 grid area around the player's grid position. For each PIT tile found, calculates Manhattan distance between player center `(px, py)` and PIT tile center. If distance < threshold, triggers death animation.
- **Design rule:** PIT tiles must be surrounded by solid walls on all sides to function as hazards (gaps, chasms, bottomless pits).

### MAGICAL_WALL — Dash-passable barrier

- **Solid** for normal movement (`solid(MAGICAL_WALL)` = `true`).
- **Skipped** during dash collision (`collidesDash()` excludes it via `skipTileType`).
- **Destructed** on dash contact — the wall is replaced with AIR and a particle burst.
- **Kills the player** on non-dash contact — if the player touches a magical wall without dashing, it triggers death.
- **Dash phase bonus:** During dash charge, the magical wall rendering dims (alpha reduced from 0.6 to 0.2) to visually signal that dashing can destroy it.

### PLATFORM — One-way surface

- **Not solid** by default — `solid(PLATFORM)` returns `false`.
- **Becomes solid** when `platSolid()` returns `true` (player was above it and not pressing Down).
- **Used in collision:** `collides()` (Y-axis movement) includes platform checks via `includePlatforms: true`. `collidesNoPlat()` (X-axis movement) does not include platforms.
- **Drop through:** Pressing ArrowDown or S while standing on a platform lets the player fall through it.

### CRACKED — Breakable wall

- **Solid** (`solid(CRACKED)` = `true`) — blocks normal movement.
- **Breakable by dash:** When the player has `canBreak` ability and dashes through a CRACKED tile, it shatters into particles and becomes AIR.
- **Visual hint:** When `P.canBreak` is true, cracked walls show a subtle highlight overlay and border to indicate they are interactable.
- **Particle effect:** Breaking spawns diamond-shaped champagne-colored particles via `shatterBlock()`.

## Rendering Notes

All tiles are rendered in the `render()` function (Section 10). Only non-AIR tiles are drawn (sparse rendering via `c.solidTiles` list).

### WALL (`#`)
- Base: Dark stone fill (`COLORS.wall = #222233`).
- Capstone: Champagne horizontal line at top (`rgba(197,179,145,0.60)`).
- Cross-hatching: Subtle dark lines (`rgba(58,58,82,0.3)`) — checkerboard pattern based on `(x+y) % 2` for vertical line, every tile has a horizontal crossbar.
- Uses shared `drawWallBase()` helper function.

### PLATFORM (`=`)
- Trapezoidal shape — thin horizontal bar (3px height) with slightly wider base.
- Top highlight: `COLORS.wallTop` (#3A3A52).
- Body: `COLORS.platform` (#42425C).
- Renders as a 3D-like floating slab.

### PIT (`~`)
- Background: `COLORS.pit` (#060608) — near black.
- Teal radial glow extending slightly beyond tile edges (clipped to 120% of tile area).
- Sharp teal rim at tile boundaries with animated alpha (`glow * 0.42`, peak ~0.252).
- Inner teal depth layer on top 3px.
- Champagne hairline cracks — subtle geometric patterns suggesting a sealed void.

### DOOR_D (`v`)
- Locked state: Dark fill (#12121F) with champagne border and padlock icon.
- Unlocked state: Seafoam-tinted glow (`rgba(92,179,175)`) with arrow icon pointing right.
- Pulsing border alpha based on `sin(now/500)`.

### END_PORTAL (`@`)
- Layered green fill with decreasing opacity (outermost to innermost).
- Emerald green border (`rgba(5,150,105)`).
- Star symbol (✵, U+2605) centered.
- Two-phase pulsing animation.

### GLYPH (`*`)
- Diamond-shaped halo outline.
- Champagne diamond glow fill behind the letter.
- Hebrew letter rendering (Aleph א, Mem מ, He ה, Tav ת) based on chamber index.
- Right-to-left text direction for correct Hebrew rendering.
- Pulsing alpha with position-based phase offset.

### CRACKED (`X`)
- Base: `drawWallBase()` with `COLORS.cracked` (#2E2840) — slightly purple-tinted stone.
- Cross-shaped crack pattern (two diagonal lines crossing at center).
- When `P.canBreak` is true: champagne overlay (`rgba(197,179,145,0.15)`) and border highlight (`rgba(197,179,145,0.25)`).

### MAGICAL_WALL (`M`)
- Seafoam-tinted fill (`rgba(92,179,175,0.30)`) with animated border.
- Purple hexagram (six-pointed star) centered — filled and stroked in violet (`#7B68EE`).
- Falling teal spark particles (3 per tile, animated vertical position).
- During dash charge: alpha drops to 0.2 (from 0.6) — visually indicates vulnerability.

### GOLEM_SPAWN (`^`), PUSH_SPAWN (`S`), GOLEM_SPAWN
- **Not rendered** — these are metadata tiles. GOLEM_SPAWN sets the player position at chamber entry. PUSH_SPAWN initializes push block entities.
- GOLEM_SPAWN is invisible at runtime. The player appears at its location when the chamber loads.
- PUSH_SPAWN creates push block entities with full rendering (rounded rectangle with top/bottom highlights).

## Constants Summary

```js
// Tile values (golem.html Section 1)
const AIR=0, WALL=1, PIT=2, GOLEM_SPAWN=3, DOOR_D=4, GLYPH=5, CRACKED=7, PLATFORM=8, END_PORTAL=9, MAGICAL_WALL=10, PUSH_SPAWN=11;

// Grid dimensions
const W=800, H=480, T=32;  // canvas width, height, tile size
// Grid: 25 columns x 15 rows (25*32=800, 15*32=480)

// Player dimensions (pixels)
// Player: 24x28 pixels (smaller than tile for movement clearance)
```

## Helper Functions

| Function | Purpose |
|----------|---------|
| `getTile(ch, x, y)` | Get tile value at grid position in specified chamber |
| `setTile(ch, x, y, v)` | Set tile value at grid position |
| `_getTile(x, y)` | Fast tile access using pre-cached chamber reference |
| `solid(t)` | Check if tile blocks normal movement |
| `platSolid(t, prevFeet, gy)` | Check if platform is solid at current position |
| `tileCollidesRect(...)` | Unified AABB-vs-grid collision with options |
| `collides(...)` | Y-axis collision (includes platforms) |
| `collidesNoPlat(...)` | X-axis collision (solid tiles only) |
| `collidesDash(...)` | Dash collision (skips magical walls, checks push blocks) |
| `inPit()` | Check if player center is near PIT tiles |
