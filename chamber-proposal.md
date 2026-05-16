# Chamber Improvement Proposal

## Correct Glyph Progression

| Chamber | Grants | Used in |
|---------|--------|---------|
| Ch.0 Awakening | Glyph 1 -- Double Jump | Ch.1 |
| Ch.1 The Library | Glyph 2 -- Dash | Ch.2 |
| Ch.2 Hall of Echoes | Glyph 3 -- Push | Ch.3 |
| Ch.3 Weight of Wisdom | Glyph 4 -- Break | Ch.4 |
| Ch.4 The Ibis Chamber | (none) -- END_PORTAL | (finale) |

Each chamber grants an ability for the *next* chamber. This pattern is correct
in the code and should be preserved.

---

## Guiding Principles

1. **Grant-then-use chain is correct.** Each chamber's glyph unlocks the next
   chamber's core mechanic. Do not break this.
2. **Minimal changes.** Only restructure chambers that genuinely need improvement.
3. **The solution must be discoverable.** Layout hints at the path.
4. **Hazards should create meaningful tension.** Pits force decisions.
5. **Keep the existing tile set.** No new tile types.

---

## Chamber-by-Chamber Assessment

### Chamber 0 -- Awakening

**Current state:** Diagonal staircase ascending from (12,12) to (9,9). Glyph at
(10,8) sits on top. A 3x2 pit at (12-14, 13-14) exists below. The player walks
up the stairs, collects the glyph, drops to the door.

**Problem:** This is the tutorial chamber. It should teach the player that jumping
exists and that platforms can be hazards to avoid. Currently it is a walk-up.

**Goal:** Replace the staircase with a simple platform sequence that requires basic
jump timing, while keeping the layout trivial enough for a first chamber.

### Proposed layout

```
+-----------------------------+
| Ch.0 Awakening (Revised)    |
+-----------------------------+
|00 ######################### |
|01 #.......................# |
|02 #.......................# |
|03 #.......................# |
|04 #.......................# |
|05 #.......................# |
|06 #.......................# |
|07 #.......................# |
|08 #.........*.............# |
|09 #........==.............# |
|10 #.......##..............# |
|11 #..==..##...............# |
|12 #.....##................v |
|13 ####~~~~~~############### |
|14 ####~~~~~~############### |
+-----------------------------+
```

Spawn: (3,11) | Glyph 1 at (10,8) -- Double Jump | DOOR_D at (24,12)
Pit widened to cols 4-9, rows 13-14 (6 tiles).
Platforms: row 11 cols 2-3 (first step), row 9 cols 8-9 (glyph platform).

**Flow:**
- Spawn at (3,11). Walk to platform at (2-3,11).
- Jump from (2-3,11) to wall step at (6-7,10).
- Jump from (6-7,10) to platform at (8-9,9). Collect glyph at (10,8).
- Drop down, walk right past the widened pit to DOOR_D at (24,12).

**Changes from current:**
- Removed the diagonal staircase walls.
- Added platform at row 11 cols 2-3 and platform at row 9 cols 8-9.
- Widened pit from 3 to 6 tiles (cols 4-9 instead of 12-14).

**Why:** Teaches basic jump timing before the player has double jump. The widened
pit adds stakes -- falling is a real consequence of mistimed jumps.

---

### Chamber 1 -- The Library

**Current state:** Three ascending platforms at rows 11, 9, 7. Two vertical walls
at cols 9 and 14 create a zigzag. Pit spans cols 8-16. Glyph at (17,6). Door at
(12,1).

**Assessment:** Well designed. Double jump is needed to reach the upper platforms
and the glyph. The zigzag between walls forces vertical movement.

**No changes proposed.**

---

### Chamber 2 -- The Hall of Echoes

**Current state:** Magical wall at col 10 spanning rows 1-12. Platforms at left
(4-5, 11) and right (17-18, 11). Glyph at (17,6). Door at (12,1). Pit at cols
7-17. Walls block the upper-left area (row 1, cols 1-9).

**How it works:** The `collidesDash()` function explicitly skips MAGICAL_WALL
(`if(t===MAGICAL_WALL) continue`), so the dash passes through the wall. Death
only fires if the player lands *inside* an M tile when the burst ends, which does
not happen since the 320px dash travel exceeds the 32px wall width.

**Intended solution:** The player jumps near the left side of the wall to gain
height, then dashes through it. During the dash burst, gravity is disabled
(`vy = 0`), so the player carries their vertical position through the wall. After
the dash ends, the player is past the wall and can use a double jump to clear the
gap to the right-side platform at (17-18, 11). From there, a single jump reaches
the glyph at (17, 6).

**Assessment:** Works as designed. The chamber teaches the player to combine jump
+ dash as a single action. The upper-left wall section ensures the player must
cross to the right via dash first.

**No changes proposed.**

---

### Chamber 3 -- The Weight of Wisdom

**Current state:** Solid floor at row 12 (no pit). Wall at row 10 cols 4-13
blocks passage. Push block spawns at (10,11). Slot opening at (11,13) in the
floor. Platforms at row 10 cols 14-22 and row 9 cols 16-17 on the right side.
Glyph at (17,8). Door at (12,1).

**How it works:** The player enters with Push already unlocked (from Ch.2 glyph).
They collect the glyph on the right side (granting Break for Ch.4), push the block
into the slot, the block settles forming a bridge, then cross to the right and
navigate up to the door.

**Assessment:** The puzzle is clear and functional. Collect glyph, push block,
cross, exit. The grant-then-use chain is preserved.

**No changes proposed.**

---

### Chamber 4 -- The Ibis Chamber

**Current state:** END_PORTAL at (12,7). Inner 3x3 CRACKED box seals the portal.
Outer diamond ring of CRACKED tiles. Platforms at row 12 cols 4-7 (left), row 12
cols 17-21 (right), row 10 cols 11-13 (center). Spawn at (2,11).

**Current weakness:** The outer cracked walls are purely decorative. The player
can dash through the inner box from any direction and reach the portal. The
platform at row 10 cols 11-13 sits directly above the portal, making it too easy
to approach from above. There is no consequence for taking a particular route.

**Goal:** Make the outer cracked walls structurally meaningful -- they should
block approach paths so the player must break through them in a specific order.

### Proposed layout

```
+-----------------------------+
| Ch.4 The Ibis Chamber (Revised)|
+-----------------------------+
|00 ######################### |
|01 #.......................# |
|02 #.......................# |
|03 #...........X...........# |
|04 #.........X....X........# |
|05 #........X.....X........# |
|06 #.......X..X@X..X.......# |
|07 #........X.....X........# |
|08 #.........X....X........# |
|09 #...........X...........# |
|10 #.....=......=..........# |
|11 #.......................# |
|12 #...==.........==....~~~# |
|13 ####~~~~~~~~~####~~~~~~~# |
|14 ####~~~~~~~~~####~~~~~~~# |
+-----------------------------+
```

Spawn: (2,11) | END_PORTAL at (12,7)
Inner 3x3 CRACKED box at rows 6-8, cols 11-13 (preserved from current).
Outer diamond ring of CRACKED tiles (preserved from current).
Platforms: row 12 cols 3-4 (left approach), row 12 cols 15-16 (right approach).
Row 10 cols 5-6 and 13-14: mid-height platforms for repositioning.
Left pit: cols 4-10, rows 13-14. Wall barrier at cols 11-14, row 13.
Right pit: cols 17-23, rows 12-14.

**Flow:**
- Spawn at (2,11). The left pit (cols 4-10, rows 13-14) blocks walking around
  the bottom.
- Jump onto platform at (3-4, 12), then to (5-6, 10).
- Dash from the mid-height platform to break the left side of the outer diamond
  (X at col 8 or 9).
- Double-jump to reposition, dash to break the top of the diamond (X at 12, 3).
- Drop down through the broken opening toward the inner box.
- Dash through the inner CRACKED box to reach the END_PORTAL at (12,7).
- The right pit (cols 17-23) prevents walking around the right side.

**Changes from current:**
- Added pits on rows 13-14 that funnel the player toward the cracked walls.
- Removed the wide right-side platform (was row 12 cols 17-21, now cols 15-16).
- Removed the center platform at row 10 cols 11-13 (was directly above the
  portal, making it too easy to approach from above).
- Added mid-height platforms at row 10 cols 5-6 and 13-14 for repositioning
  between dashes.

**Why:** The pits create a funnel. The player cannot walk around the cracked
walls -- they must break through them. The outer diamond is no longer cosmetic;
it blocks the approach paths and must be partially destroyed to reach the inner
box. This turns a "smash the center" into a "break the right walls in the right
order" challenge.

---

## Changes Summary

| Chamber | Change | Reason |
|---------|--------|--------|
| Ch.0 | Replace staircase with platform jumps, widen pit | Tutorial should teach jumping |
| Ch.1 | No change | Well designed |
| Ch.2 | No change | Dash through magical wall works as designed |
| Ch.3 | No change | Push block puzzle works as designed |
| Ch.4 | Add pits, reposition platforms | Make outer cracked walls meaningful |

Only Chambers 0 and 4 are restructured. Chambers 1, 2, and 3 are preserved as-is.

---

## Implementation Notes

### Chambers requiring changes

**Chamber 0:** Replace the IIFE block (lines 29-40 in golem.html). Remove the
diagonal staircase wall assignments. Add platform tiles. Widen the pit range.

**Chamber 4:** Replace the IIFE block (lines 98-119). Add pit tiles in rows 13-14.
Adjust platform positions. The CRACKED wall pattern (inner box + outer diamond)
is preserved.

### What does NOT change

- Player physics, collision, or input handling.
- Glyph collection mechanics or ability unlocking.
- Door/portal transition logic.
- Particle system or rendering code.
- HUD layout.
- Test chamber (Chamber T / index 5).
- Chambers 1, 2, and 3.

### Verification steps

For each proposed chamber:
1. Convert the ASCII grid to JavaScript using the template in `chamber-template.md`.
2. Verify spawn position has walkable AIR tiles beneath it.
3. Verify the glyph/portal is reachable using the documented flow.
4. Verify the exit door is reachable after objectives are completed.
5. Verify pits are bordered by solid tiles.
6. Verify each grid row is exactly 25 characters.
7. Test with `_testMode = true` for instant transitions.
