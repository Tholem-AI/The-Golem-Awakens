# GOLEM GAME — State Audit

## 1. Overview

- **Title:** The Golem Awakens
- **File:** golem.html (single-file HTML5 game, ~958 lines, ~33 KB)
- **Runtime:** Vanilla JavaScript, Canvas 2D rendering, no frameworks
- **Canvas:** 800x480 pixels, pixelated rendering
- **Tile size:** 32x32 pixels
- **Genre:** 2D side-scrolling platformer with puzzle elements
- **Theme:** Egyptian-inspired golem collecting knowledge glyphs through chambers

---

## 2. Architecture

The game follows a single-file structure with three main sections:

1. **Data layer** — Tile constants, chamber definitions, player state object
2. **Update loop** — Physics, input processing, collision, game logic (update())
3. **Render loop** — Canvas 2D drawing for tiles, entities, particles, HUD (render())

The game loop is a standard `requestAnimationFrame` cycle calling `update()` then `render()` each frame. No scene graph, ECS, or entity component system — everything is imperative and global-state driven.

### Global State Variables

| Variable | Type | Purpose |
|---|---|---|
| `keys` | Object | Current frame key states |
| `prevKeys` | Object | Previous frame key states (for edge-detection) |
| `P` | Object | Player entity (position, velocity, abilities) |
| `PB` | Object | Push block entity (position, velocity, slot state) |
| `chambers` | Array | Level definitions (6 chambers: 5 canonical + 1 test) |
| `glyphsCollected` | Number | Total glyphs collected (0-4) |
| `collectedGlyphs` | Array | Per-chamber boolean collection tracking |
| `gameState` | String | 'playing' or 'ending' |
| `screenFade` | Number | Fade direction: 0=off, 1=fade-in, -1=fade-out |
| `screenAlpha` | Number | Current fade opacity (0-1) |
| `messageText` | String | Current HUD message text |
| `messageTimer` | Number | Message display countdown |
| `portalLockMsg` | Number | Cooldown timer for locked portal message |
| `particles` | Array | Active particle objects |
| `testChamberSrc` | Number | Source chamber index for test chamber return (-1 = none) |
| `_testMode` | Boolean | Instant transitions (no fade) for test harness |

---

## 3. Tile System

### Tile Constants (12 types)

| Constant | Value | Description |
|---|---|---|
| `AIR` | 0 | Empty space |
| `WALL` | 1 | Solid wall (floor, ceiling, boundaries) |
| `PIT` | 2 | Death void — touching respawns player |
| `DOOR_R` | 3 | Right-side exit door (glyph-locked) |
| `DOOR_D` | 4 | Down-side exit door (glyph-locked) |
| `GLYPH` | 5 | Collectible knowledge glyph |
| `BLOCK` | 6 | Pushable block (tile-based, old system) |
| `CRACKED` | 7 | Breakable wall (requires Glyph 4) |
| `PLATFORM` | 8 | One-way platform (passable from below) |
| `END_PORTAL` | 9 | Final portal — triggers ending |
| `MAGICAL_WALL` | 10 | Destructible barrier (dash kills on contact) |
| `PUSH_SPAWN` | 11 | Spawn marker for free-moving push block |

### Solidness Rules

The `solid()` function determines collision behavior:

- **Always solid:** WALL, BLOCK, CRACKED, DOOR_R, DOOR_D, END_PORTAL, MAGICAL_WALL
- **Conditional solid:** PLATFORM — solid only when player falls from above (`platSolid()`)
- **Never solid:** AIR, PIT, GLYPH, PUSH_SPAWN

### Collision Functions

Three specialized collision checkers exist:

1. **`collidesNoPlat()`** — Used for X-axis movement. Checks only solid tiles, ignores platforms entirely.
2. **`collides()`** — Used for Y-axis movement. Checks solid tiles + one-way platforms (player must be falling).
3. **`collidesDash()`** — Used during dash. Ignores MAGICAL_WALL, includes push block entity, checks solid + platforms.

All collision uses AABB tile-grid sampling: the entity bounding box is converted to tile coordinates and each covered tile is checked.

---

## 4. Chamber Definitions (5 Chambers)

All chambers are 25x15 grids (800x480 in pixels).

### Chamber 0: Awakening

- **Purpose:** Tutorial — learn basic movement, collect Glyph 1 (Double Jump)
- **Layout:** Left wall, right partial wall with DOOR_D at row 13. Staircase of walls ascending diagonally from bottom-left toward center.
- **Hazards:** 3x2 pit at tiles (12-14, 13-14).
- **Glyph:** Tile (10, 8) — sits atop the diagonal staircase.
- **Spawn:** (3*T, 11*T) — left side near bottom.
- **Exit:** DOOR_D at right wall, row 13.

### Chamber 1: The Library

- **Purpose:** Requires double jump to navigate. Collect Glyph 2 (Dash).
- **Layout:** Three ascending platforms at increasing heights. Two vertical wall segments block direct paths.
- **Platforms:** Row 11 (cols 4-6), Row 9 (cols 10-12), Row 7 (cols 16-18).
- **Hazards:** Wide pit at bottom (cols 8-16, rows 13-14).
- **Walls:** Vertical barriers at col 9 (rows 4-12) and col 14 (rows 6-12).
- **Glyph:** Tile (17, 6) — sits above the highest platform.
- **Exit:** DOOR_D at top center (12, 1).

### Chamber 2: The Hall of Echoes

- **Purpose:** Requires dash to cross the magical wall. Collect Glyph 3 (Push).
- **Layout:** Central magical wall barrier (col 10, rows 1-12). Wide pit at bottom.
- **Platforms:** Row 11 at cols 4-5 (left side) and 17-18 (right side).
- **Magical wall:** Full vertical column at col 10 spanning rows 1-12. The dash
  collision checker (`collidesDash()`) explicitly ignores MAGICAL_WALL
  (`if(t===MAGICAL_WALL) continue`), so the player passes through it. Death only
  fires if the player lands *inside* an M tile when the dash burst ends
  (`getTile(cx,cy)===MAGICAL_WALL`), which does not happen since the 320px dash
  travel far exceeds the 32px wall width.
- **Glyph:** Tile (17, 6) — right side, above the platform. Grants Push (`canPush = true`).
- **Exit:** DOOR_D at top center (12, 1).
- **Intended solution:** The player jumps near the left side of the magical wall to
  gain height, then dashes through the wall. During the dash burst, gravity is
  disabled (`vy = 0`), so the player carries their vertical position. After the dash
  ends, the player is past the wall and can use a double jump to clear the gap to the
  right-side platform at (17-18, 11). From there, a single jump reaches the glyph at
  (17, 6).

### Chamber 3: The Weight of Wisdom

- **Purpose:** Puzzle — push block into slot to create a bridge. Collect Glyph 4 (Break).
- **Layout:** Solid wall at row 10 (cols 4-13) blocks passage. Slot opening at (11, 12-13).
- **Push block:** Spawned at tile (10, 11) as a free-moving physics entity. Slot target at (11, 13).
- **Platforms:** Row 10 (cols 14-22) and row 9 (cols 16-17) on the right side.
- **Floor:** Solid wall at row 12 (cols 2-23) — no death void in this chamber.
- **Glyph:** Tile (17, 8) — right side, atop platforms. Grants Break (`canBreak = true`).
- **Mechanics:** The player enters with Push (from Ch.2). They collect the glyph on the
  right side first (unlocking Break), then push the block into the slot to create a bridge,
  cross to the right platforms, and reach the door.

### Chamber 4: The Ibis Chamber

- **Purpose:** Final chamber — break cracked walls to reach END_PORTAL.
- **Layout:** Central END_PORTAL at (12, 7) surrounded by cracked walls.
- **Inner 3x3 box:** CRACKED tiles forming a sealed box around the portal (rows 6-8, cols 11-13).
- **Outer diamond ring:** CRACKED tiles in a diamond pattern (rows 3-11, cols 8-16).
- **Platforms:** Row 12 at cols 4-7 and 17-21. Row 10 at cols 11-13.
- **No glyph needed:** This chamber has no GLYPH tile. Glyph 4 (Break) is collected in Chamber 3 before entering.
- **Mechanics:** Player must dash through cracked walls to break them (`P.canBreak` enabled), clearing a path to the END_PORTAL. Touching the portal triggers the ending sequence.

### Chamber 5: Test Chamber (Ch.T)

- **Purpose:** Debug/testing — empty sandbox with all abilities unlocked.
- **Layout:** Empty 25x15 box — border walls only (rows 0 and 14, cols 0 and 24). Interior is all AIR.
- **Hazards:** None.
- **Glyph:** None.
- **Spawn:** (12*T, 10*T) — center-top of the chamber, standing on row 10.
- **Entry:** Press `T` (KeyT) from any chamber. Saves current chamber to `testChamberSrc`,
  sets `glyphsCollected = 4`, unlocks all abilities (Double Jump, Dash, Push, Break).
- **Exit:** Press `T` again — transitions back to `testChamberSrc`. Also exits via
  DOOR_R/DOOR_D tiles if placed in the chamber (handled by `checkDoors()`).
- **Does not affect** original chambers 0-4 or normal game flow.

---

## 5. Player Entity (`P` object)

### Position and Dimensions

- **Hitbox:** 24x28 pixels (smaller than a single tile)
- **Position:** `x`, `y` in world coordinates
- **Velocity:** `vx`, `vy` in pixels per frame
- **Facing:** `facing` — 1 (right) or -1 (left)

### Movement Physics

| Property | Value | Context |
|---|---|---|
| Ground acceleration | 0.1 px/frame | Horizontal input on ground |
| Air acceleration | 0.4 px/frame | Horizontal input airborne |
| Max horizontal speed | 5 px/frame | Capped |
| Deceleration | 0.45 px/frame | No input |
| Gravity | 0.28 px/frame^2 | When airborne |
| Max fall speed | 5 px/frame | Capped |
| Jump velocity (first) | -10 px/frame | Ground or coyote jump |
| Jump velocity (second) | -13 px/frame | Double jump (stronger) |

### Jump System

Three-layer jump handling with coyote time and input buffering:

1. **Jump buffer** (8 frames): Press jump slightly before landing — executes on landing.
2. **Coyote time** (8 frames): Press jump shortly after leaving a ledge — still jumps.
3. **Variable height:** Releasing jump key early reduces vertical velocity (handled implicitly by per-frame input).
4. **Double jump:** Unlocked by Glyph 1. Second jump is stronger (-13 vs -10) and spawns gold particles.

### Dash System (Glyph 2)

Two-phase dash with charge-up and burst:

1. **Charge phase (20 frames):** Hold Shift. Player hovers (gravity reduced to 10% of normal, velocity dampened). Purple particles spawn.
2. **Burst phase (10 frames):** Player moves at 10 px/frame in facing direction. No gravity. Purple trail particles.
3. **Cooldown (20 frames):** Cannot dash again during cooldown.
4. **Magical wall interaction:** Landing inside a MAGICAL_WALL after a dash triggers death and respawn with message "The barrier consumes you..."

### Push Ability (Glyph 3)

The `resolvePushBlockCollision()` function handles pushing:

- Only works on ground, moving toward the block, and when not already pushing.
- Pushes the block one tile in the facing direction.
- Block must have an empty tile ahead to move.
- Player velocity is zeroed on push.
- Push spawns gold particles at the block position.

### Break Ability (Glyph 4)

- When dashing (`P.dashPhase`) and colliding with CRACKED tile, it is destroyed (`setTile` to AIR).
- Triggers `shatterBlock()` particle effect (chunky debris + dust + sparks).
- Dash ends immediately on breaking a wall.

### Respawn System

Death triggers on:
- Touching a PIT tile (checked at player center X and bottom Y)
- Falling below chamber height

On death:
- Player resets to `P.respawnX`, `P.respawnY`
- All velocity zeroed, jumps reset
- Dash state cleared
- Push block reset
- Coyote time granted (8 frames)
- Message: "The void claims clay..."

---

## 6. Push Block Entity (`PB` object)

A free-moving physics entity (not tile-locked) introduced in Chamber 3.

### Properties

| Property | Type | Purpose |
|---|---|---|
| `x`, `y` | Number | World position (floating-point) |
| `w`, `h` | Number | Dimensions (32x32 = one tile) |
| `vx`, `vy` | Number | Velocity with gravity and friction |
| `active` | Boolean | Whether block is in play |
| `inSlot` | Boolean | Whether block has settled into target slot |

### Physics

- **Gravity:** 0.3 px/frame^2 (slightly heavier than player)
- **Max fall speed:** 4 px/frame
- **Friction:** Velocity multiplied by 0.85 each frame; zeroed below 0.1
- **Collision:** Separated X then Y axis, snapped to tile boundaries
- **Slot detection:** When block center aligns with `pushSlot` coordinates, it freezes and locks in place
- **Reset on fall:** If block falls past chamber bottom, it respawns at `pushSpawn`
- **Player can stand on block:** Y collision allows player to land on top (with 4px tolerance)

### Rendering

- Drawn as a styled block similar to static BLOCK tiles
- When `inSlot`: darker colors, no hint glow
- When active and pushable: pulsing gold hint glow inside the block

---

## 7. Glyph System

Four glyphs, collected sequentially. Each grants a permanent ability.

| Glyph # | Chamber | Ability | Message |
|---|---|---|---|
| 1 | Chamber 0 | Double Jump (`maxJumps = 2`) | "Knowledge lifts me." |
| 2 | Chamber 1 | Dash (`canDash = true`) | "Speed courses through me." |
| 3 | Chamber 2 | Push Blocks (`canPush = true`) | "Strength returns." |
| 4 | Chamber 3 | Break Cracked (`canBreak = true`) | "Clay becomes Wisdom." |

### Collection Mechanics

- Glyphs are collected in sequence (`glyphsCollected` must equal chamber index).
- Player must be within 1 tile of the glyph center.
- On collection: tile set to AIR, particle burst (gold), HUD message displayed.
- `collectedGlyphs[chamber]` boolean prevents re-collection.
- Unlocked glyphs shown in green in the HUD; locked glyphs shown in dim gray.

### Visual Feedback

- Collected glyphs appear as horizontal lines on the golem's body (one per glyph).
- GLYPH tiles have a pulsing golden glow and bob animation.
- BLOCK tiles gain a subtle white highlight when push is unlocked.
- CRACKED tiles gain an orange tint when break is unlocked.

---

## 8. Door and Portal System

### Exit Doors (DOOR_R / DOOR_D)

- Locked until the current chamber's glyph is collected.
- Locked appearance: Pulsing red with lock emoji (U+1F512).
- Unlocked appearance: Green glow with arrow symbol (U+279C).
- Approaching a locked door shows message: "The seal demands Knowledge..." (45-frame cooldown).
- Approaching an unlocked door triggers `transition()` to the next chamber.

### End Portal (END_PORTAL)

- Located in Chamber 4 at tile (12, 7).
- Multi-layered pulsing glow animation (dark purple to white center).
- Star symbol (U+2605) rendered at center.
- Touching triggers `transitionEnding()` — fades to black, shows ending screen.

### Chamber Transition

1. `screenFade` set to 1, fade-in begins (0.06 alpha per frame).
2. After 300ms, `_doTransition()` executes:
   - Sets new chamber, resets player position and velocities.
   - Calculates spawn position from chamber data (2 tiles above floor at spawn X).
   - Resets dash state, push block.
3. `screenFade` set to -1, fade-out begins.
4. Game logic is paused during fade (`if(screenFade !== 0) return`).

---

## 9. Particle System

### Particle Properties

Each particle is an object with: `x`, `y`, `vx`, `vy`, `life`, `maxLife`, `color`, `size`.

- Gravity applied: `vy += 0.1` per frame.
- Lifetime countdown: removed when `life <= 0`.
- Rendered with alpha based on `life/maxLife` (fades below 70% life).

### Particle Types

| Trigger | Colors | Count | Size | Behavior |
|---|---|---|---|---|
| Jump (ground) | `#8a7d6b` (brown) | 5 | 2-5px | Upward burst |
| Jump (double) | `#d4a84b` (gold) | 8 | 2-5px | Upward burst |
| Landing (hard) | `#8a7d6b` (brown) | 4 | 2-5px | At feet |
| Dash charge | `rgba(180,80,255,0.5)` (purple) | 3 | 2-5px | Hover particles |
| Dash burst | `rgba(220,120,255,0.4)` (purple) | 2 | 2-5px | Trail particles |
| Push block | `#d4a84b` (gold) | 8 | 2-5px | At block position |
| Block in slot | `#d4a84b` (gold) | 12 | 2-5px | At slot position |
| Glyph collect | `#f0d060` (bright gold) | 15 | 2-5px | At glyph position |
| Block push (tile) | `#9a8d7d` (tan) | 6 | 2-5px | At block position |

### Shatter Effect (Block Breaking)

Three-layer particle burst:

1. **Chunky debris** (12 particles): Fast, heavy. Colors: `#c86040`, `#a04030`, `#d08060`, `#e0a070`. Size 3-7px.
2. **Dust cloud** (10 particles): Slow, diffuse. Color: `rgba(200,160,100,0.5)`. Size 2-4px.
3. **Spark flash** (6 particles): Rapid scatter. Color: `#ffe0a0`. Size 1-3px.

---

## 10. Rendering Details

### Color Palette

```
Background:      #0d0d1a (near-black with blue tint)
Wall:            #4a4035 (brown)
Wall top edge:   #6b5d4f (lighter brown)
Platform:        #5a4d3a (dark brown)
Pit:             #000000 (black)
Door (locked):   #1a1520 base, pulsing red overlay
Door (unlocked): rgba(42,90,58) pulsing green
Glyph:           #c8a84e (gold)
Glyph glow:      #f0d060 (bright gold)
Block:           #7a6d5d (tan)
Push block:      #a08868 (warm tan)
Push block top:  #b8a080 (light tan)
Cracked:         #8a5040 (reddish brown)
Magical wall:    rgba(60,20,80) with purple glyphs
Golem body:      #8a7d6b (warm gray-brown)
Golem dark:      #5a5040 (dark brown)
Golem eye:       #d4a84b (gold)
Text/HUD:        #d4a84b (gold)
```

### Visual Effects

- **Starfield:** 40 static dots per frame, offset by chamber index. Color: `#1a1a2e`.
- **Pit glow:** Animated red glow using `sin(Date.now()/600 + x)`. Red line at top, darker below, edge strips.
- **Door pulse:** Red (locked) or green (unlocked) pulsing using `sin(Date.now()/500)`.
- **Glyph bob:** `sin(Date.now()/400) * 3` vertical offset. Pulsing golden glow circle.
- **Magical wall:** Animated purple glyphs and floating spark particles using `Date.now()/200`.
- **Dash phase visual:** Magical walls become more transparent when dashing (`phaseAlpha = 0.2` vs `0.6`).
- **Player squash & stretch:**
  - Jumping upward: width -3px, height +4px, offset -4px
  - Moving on ground: width +3px, height -2px, offset +2px
  - Falling fast: width -2px, height +6px, offset -2px
- **Falling motion lines:** Three animated lines below the player when `vy > 3`.
- **Screen fade:** Black overlay from 0 to 1 alpha at 0.06/frame.

### Chamber Centering

Chambers are centered on the 800x480 canvas using offset calculations:
```
ox = floor((800 - chamber_width * 32) / 2)
oy = floor((480 - chamber_height * 32) / 2)
```

For 25x15 chambers: `ox = 20`, `oy = 12`. This creates 20px horizontal and 12px vertical margins.

---

## 11. HUD Elements

### Top-Left (Abilities Panel)

- **Glyphs counter:** "Glyphs: N/4" in gold, 14px monospace.
- **Ability list:** Four lines in 11px monospace, green if unlocked, dim gray if locked.
  - `[1] Double Jump`
  - `[2] Dash (Shift)`
  - `[3] Push Blocks`
  - `[4] Break Cracked`

### Bottom Center (Chamber Name)

- Chamber names with portal status, 12px monospace, color `#665a4a`.
- Chambers 0-3: Name + lock emoji (sealed) or checkmark (open).
- Chamber 4: Name + star emoji + "Path of Wisdom".

### Center (Messages)

- Bold 18px serif text in gold, alpha fades based on remaining timer.
- Position: center of screen, 60px above center.

### Tutorial Text

- Chamber 0, no glyphs collected, no active message: "I awaken..." at center, 60px from top.

---

## 12. Input System

### Controls

| Action | Keys |
|---|---|
| Move left | ArrowLeft, A |
| Move right | ArrowRight, D |
| Jump | ArrowUp, W, Space |
| Dash (charge) | ShiftLeft, ShiftRight (hold) |
| Test chamber | KeyT (press to enter/exit) |

### Input Processing

- **keydown:** Sets `keys[code] = true`. Prevents default for movement/jump/dash keys.
- **keyup:** Sets `keys[code] = false`.
- **`fresh(code)`:** Returns true only on the frame the key was first pressed (key is down now but was not down last frame).
- **prevKeys update:** At end of each `update()` call, `keys` is copied to `prevKeys`. Stale entries are cleaned.

### Prevented Default Keys

ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Space, KeyW, KeyA, KeyS, KeyD, ShiftLeft, ShiftRight.

Note: KeyS and KeyD are in the prevent-default list even though S is not used for any action (likely included for WASD symmetry).

---

## 13. Game States

### Playing (`gameState = 'playing'`)

- Normal update/render cycle.
- Physics, input, collisions, glyph collection, door transitions all active.

### Ending (`gameState = 'ending'`)

- Update loop returns immediately (no physics or input).
- Render shows:
  - Dark overlay (92% black).
  - Title: "Awakening of the Golem" in bold 28px serif gold.
  - Divider line.
  - "The Ibis speaks:" in italic 20px serif.
  - "'You were clay. Now you are Wisdom.'" in italic 22px serif.
  - "Refresh to play again" in 14px monospace gray.

### Test Mode (`_testMode = true`)

- Skips screen fade transitions (instant `_doTransition`).
- Ending triggers immediately without fade.
- Set externally by test harness for automated testing.

---

## 14. Update Cycle Order

The `update()` function executes in this fixed order:

1. Game state check — returns immediately if 'ending'
2. Test chamber entry/exit — fresh('KeyT') check, returns after transition
3. Screen fade handling (pauses everything during fade)
4. Message timer countdown
5. Portal lock message cooldown countdown
6. Horizontal input processing (acceleration + friction)
7. Dash charge phase (hover, particles, timer countdown)
8. Dash activation (Shift press detection)
9. Dash burst phase (high-speed movement, wall death check)
10. Dash cooldown countdown
11. Gravity application
12. Coyote time countdown
13. X-axis movement + tile collision resolution
14. Push block entity collision resolution
15. Y-axis movement + tile/platform collision resolution
16. Push block Y collision (standing on block)
17. Jump buffer countdown
18. Jump execution (buffered, coyote, or double jump)
19. Pit/death check + respawn
20. Push block physics update
21. Door proximity check
22. Glyph proximity check
23. Particle update
24. prevKeys synchronization

---

## 15. Tile Rendering Details

### WALL
- Brown fill with lighter top edge (3px).
- Cross-hatch lines: vertical line if `(x+y)` even, always horizontal line.
- Red tint overlay (`rgba(180,40,20,0.25)`) if adjacent to PIT tile (4-directional check).

### PLATFORM
- Drawn inset by 2px on all sides (T-4 dimensions).
- Dark top edge (2px) above the platform body.

### PIT
- Black fill.
- Animated red glow: top line (2px) and secondary line (4px) with sine-based alpha.
- Red edge strips (2px) on left and right sides.

### DOOR_R / DOOR_D
- **Locked:** Dark base, nested red rectangles with pulsing alpha, lock emoji centered.
- **Unlocked:** Green gradient (dark to light), arrow symbol centered.

### END_PORTAL
- Multi-layer pulsing: dark purple base, gold fill, bright gold inner, white center.
- Gold stroke border.
- Star emoji centered.
- Three different pulse frequencies for layered animation.

### GLYPH
- Pulsing golden circle glow (radius = tile size).
- Cross shape: vertical and horizontal gold rectangles.
- Bob animation: `sin(Date.now()/400) * 3` vertical offset.

### BLOCK (static tile)
- Tan fill with lighter top edge (3px) and darker bottom edge.
- White highlight overlay when `P.canPush` is true.

### CRACKED
- Reddish-brown fill with wall-style top edge.
- Crack lines: three strokes from top-left, top-right, and bottom-left toward center.
- Orange tint overlay when `P.canBreak` is true.

### MAGICAL_WALL
- Purple translucent fill (alpha varies during dash phase).
- Purple stroke border with pulsing alpha.
- Gold glyph symbol (cross shape).
- Three animated spark particles floating upward.

---

## 16. Player Rendering

### Body Structure (drawn back-to-front)

1. Dark torso inset (4px from edges, starts at y+6)
2. Main body fill (2px inset, starts at y+4)
3. Head (centered, 4px inset from edges, 10px tall)
4. Eye (4x3px gold rectangle, position depends on facing direction)
5. Feet (two dark rectangles at bottom, 7px wide each)
6. Arms (two gold rectangles at sides, 3x10px)

### Glyph Markings

- Horizontal gold lines on the body, one per collected glyph.
- Positioned at `y + 12 + (index * 4)`.
- Pulsing opacity: `0.3 + sin(Date.now()/500) * 0.15`.

### Squash and Stretch

Dynamic dimensions applied before rendering:
- **Airborne, moving up:** Narrower and taller (jumping stretch).
- **On ground, moving:** Wider and shorter (running squash).
- **Falling fast:** Very narrow and tall (falling stretch).

---

## 17. Messages and Timing

### Message System

- `showMessage(text, duration)` sets the message and timer.
- Duration is in frames (at 60fps, 120 frames = 2 seconds).
- Messages fade out: alpha = `min(1, timer / 30)`.

### Messages by Trigger

| Message | Trigger | Duration |
|---|---|---|
| "I awaken..." | Game start | 150 frames (2.5s) |
| "Knowledge lifts me." | Glyph 1 collected | 120 frames (2s) |
| "Speed courses through me." | Glyph 2 collected | 120 frames (2s) |
| "Strength returns." | Glyph 3 collected | 120 frames (2s) |
| "Clay becomes Wisdom." | Glyph 4 collected | 120 frames (2s) |
| "The seal demands Knowledge..." | Approach locked door | 70 frames (1.17s) |
| "The weight settles." | Block enters slot | 80 frames (1.33s) |
| "The void claims clay..." | Death (pit/fall) | 90 frames (1.5s) |
| "The barrier consumes you..." | Dash into magical wall | 90 frames (1.5s) |
| Ending quote | End portal reached | 99999 frames (persistent) |

---

## 18. Known Design Notes

### Chamber 2 Solution

The Hall of Echoes (Chamber 2) has a full-height magical wall at column 10. The
dash collision checker ignores MAGICAL_WALL tiles, so the player passes through
them. The intended approach:

- The player jumps near the left side of the wall to gain height.
- While airborne near the wall, the player presses Shift to dash through it.
- During the dash burst, gravity is disabled (`vy = 0`), so the player carries
  their vertical position through the wall.
- After the dash ends, the player is on the right side of the wall and can use
  a double jump to clear the gap to the right-side platform at (17-18, 11).
- From the right-side platform, a single jump reaches the glyph at (17, 6).
- The player does NOT die from dashing through the magical wall — death only
  triggers if the player lands *inside* an M tile when the dash ends, which does
  not happen since the 320px dash travel exceeds the 32px wall width.

### Chamber 3 Block Puzzle

The push block mechanic requires:
1. The player enters Chamber 3 with Push already unlocked (from Ch.2 glyph).
2. Collect Glyph 4 at (17, 8) on the right side — this grants Break for Ch.4.
3. Navigate back to the push block spawn at (10, 11).
4. Push the block one tile left into the slot at (11, 13).
5. The block settles, and the player can cross via the right-side platforms.

The current implementation checks `glyphsCollected !== ch` before allowing glyph
collection. In Chamber 3 (ch=3), the glyph is collected when `glyphsCollected === 3`,
which increments it to 4 and triggers `canBreak = true`. Push was already granted in
Chamber 2.

### Unused Features

- **KeyS** is in the prevent-default list but has no associated action.
- **ArrowDown** is prevented but has no function.
- **BLOCK tile type (value 6)** is defined and has a `pushBlock()` function, but Chamber 3 uses the free-moving `PUSH_SPAWN` system instead. The tile-based push function remains in code but is not called from the main update loop.
- **DOOR_R (value 3)** is defined but all chambers use `DOOR_D` (value 4). No right-side doors are placed in any chamber.

### Code Structure

- Chamber data uses IIFE (Immediately Invoked Function Expressions) for encapsulation.
- No classes or modules — all code is in global scope within a single script tag.
- The `pushBlock()` function (tile-based) is defined but never called. The active push system uses `resolvePushBlockCollision()` which works with the `PB` entity object.

---

## 19. File Summary

| Aspect | Value |
|---|---|
| Total lines | 958 |
| HTML structure | Lines 1-14 |
| JavaScript code | Lines 14-957 |
| CSS | Lines 6-9 (minimal, inline) |
| Canvas dimensions | 800x480 |
| Number of chambers | 5 |
| Number of glyphs | 4 |
| Tile types defined | 12 |
| Input keys used | 8 (Arrow keys, WASD, Space, Shift) |
| Particle types | ~9 distinct spawn scenarios |
| Color palette entries | ~24 named colors |
| External dependencies | None — fully self-contained |
