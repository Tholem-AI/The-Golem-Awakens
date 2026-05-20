# Chamber Data Consistency Investigation — Findings

Generated: 2026-05-20
Scope: chamber-data.md vs golem.html Section 2, chamber-template.md spec, chamber_diff.py tool

================================================================================
1. FILE FORMAT ANALYSIS
================================================================================

## chamber-data.md (185 lines, 6 chambers)

Structure per chamber:
  Line N:  `## Chamber N — Name`                    (H2 header)
  Line N+1: (blank)
  Line N+2: ```` (fence open)
  Line N+3: `+-----------------------------+`        (border top)
  Line N+4: `| Ch.N Name                   |`        (title row)
  Line N+5: `+-----------------------------+`        (border mid)
  Lines N+6..N+20: `|00 ######################### |`  (15 data rows, 25 tiles each)
  Line N+21: `+-----------------------------+`        (border bottom)
  Line N+22: ```` (fence close)
  Line N+23: (blank)
  Line N+24+: ANNOTATION LINES (1-5 lines of prose describing spawn, glyphs, etc.)

ANNOTATION LINES — the problematic element. These appear AFTER every code block
and contain human-readable summaries of key coordinates and features.

## golem.html Section 2 (lines 112-250)

6 chamber IIFEs, each following this structure:
  1. `// Chamber N: ...` or `// Ch.T: ...` comment
  2. `(function(){`
  3. `const w=25,h=15,g=mkGrid(w,h);`
  4. Boundary assignments (loops + direct)
  5. Interior features (walls, platforms, glyphs, etc.)
  6. `chambers.push({...});`
  7. `})();`

## chamber-template.md (350 lines)

Tile Legend table (12 types):
  . = AIR(0), # = WALL(1), ~ = PIT(2), ^ = GOLEM_SPAWN(3),
  v = DOOR_D(4), * = GLYPH(5), X = CRACKED(7), = = PLATFORM(8),
  @ = END_PORTAL(9), M = MAGICAL_WALL(10), S = PUSH_SPAWN(11)

Note: value 6 is skipped (no tile type mapped to it).

Format spec: 25 cols x 15 rows, row labels |00 through |14, border framing.

================================================================================
2. TILE-BY-TILE COMPARISON (chamber-data.md vs golem.html)
================================================================================

Ran: python3 tools/chamber_diff.py --visual
Raw output: 76 mismatches across 6 chambers.

HOWEVER — chamber_diff.py has a handler ordering bug (see Section 4) that
causes FALSE POSITIVES. The actual genuine mismatches are documented below.

## Ch.0 — Awakening: 2 GENUINE mismatches (9 reported, 7 are false positives)

  MISMATCH 1: GOLEM_SPAWN position
    MD grid col 1: `#^.....`  (caret at col 1, ADJACENT TO LEFT WALL)
    JS code:       g[11][3]=GOLEM_SPAWN  (col 3, 2 cells from wall)
    VERDICT: MD grid is WRONG. Spawn should be at col 3.

  MISMATCH 2: DOOR_D at (24,12)
    MD grid col 24: `v` (DOOR_D)
    JS code: g[h-3][w-1]=DOOR_D resolves to g[12][24]=DOOR_D
    VERDICT: This IS a genuine mismatch in the MD grid. The MD places v at col 24,
             row 12. The JS also places it at (24,12). But the diff tool reports it
             as WALL due to its handler ordering bug. The MD annotation says
             "DOOR_D at (24,12)" which matches JS. The grid itself has `v` at the
             right position — so the MD grid is actually correct here, and the tool
             is wrong.

  FALSE POSITIVES (7): All pit tiles at rows 13-14 cols 12-14.
    MD grid shows `~` (PIT). JS code has:
      g[14][12]=PIT;g[14][13]=PIT;g[14][14]=PIT;
      g[13][12]=PIT;g[13][13]=PIT;g[13][14]=PIT;
    These are genuine direct assignments that SHOULD produce PIT. The tool
    reports them as WALL because multi_for handler overwrites them.
    VERDICT: Tool bug, NOT a real mismatch. MD grid matches JS code.

## Ch.1 — The Library: 2 GENUINE mismatches (20 reported, 18 are false positives)

  MISMATCH 1: GOLEM_SPAWN position
    MD grid col 1: `#^..===..` (caret at col 1)
    JS code: g[11][3]=GOLEM_SPAWN (col 3)
    VERDICT: MD grid is WRONG.

  FALSE POSITIVES (18): Pit tiles at rows 13-14 cols 8-16.
    JS code: for(let x=8;x<17;x++){g[14][x]=PIT;g[13][x]=PIT;}
    These are direct assignments inside a for-loop body. The tool's multi_for
    handler processes them, then the boundary loop handler overwrites with WALL.
    VERDICT: Tool bug. MD grid matches JS code.

## Ch.2 — The Hall of Echoes: 2 GENUINE mismatches (24 reported, 22 false positives)

  MISMATCH 1: GOLEM_SPAWN position
    MD grid col 1: `#^..==....` (caret at col 1)
    JS code: g[11][3]=GOLEM_SPAWN (col 3)
    VERDICT: MD grid is WRONG.

  FALSE POSITIVES (22): Pit tiles at rows 13-14 cols 7-17.
    JS code: for(let x=7;x<18;x++){g[14][x]=PIT;g[13][x]=PIT;}
    Same tool bug as above.

## Ch.3 — The Weight of Wisdom: 4 GENUINE mismatches (4 reported, 0 false positives)

  MISMATCH 1: GOLEM_SPAWN position
    MD grid col 1: `#^..##########` (caret at col 1)
    JS code: g[10][3]=GOLEM_SPAWN (col 3)
    VERDICT: MD grid is WRONG.

  MISMATCH 2: Slot opening at (11,12)
    MD grid: `#  .  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  .  #`
             col 11 shows `#` (WALL) in the MD grid row 12
    JS code: g[12][11]=AIR (explicit slot opening)
    VERDICT: MD grid is WRONG. Shows WALL where JS has AIR.

  MISMATCH 3: Slot extension at (11,13)
    MD grid: row 13 shows `#` at col 11
    JS code: g[13][11]=AIR (slot extension for push block drop)
    VERDICT: MD grid is WRONG.

  MISMATCH 4: The annotation says "Floor at row 12 cols 2-22 (slot opening at col 11)"
    which correctly describes the JS code. The grid, however, has WALL at col 11.
    This is a self-contradiction within the MD file: annotation says one thing,
    grid shows another.

## Ch.4 — The Ibis Chamber: 2 GENUINE mismatches (2 reported, 0 false positives)

  MISMATCH 1: GOLEM_SPAWN position
    MD grid col 1: `#^..........` (caret at col 1)
    JS code: g[11][2]=GOLEM_SPAWN (col 2)
    VERDICT: MD grid is WRONG.

  MISMATCH 2: Annotation says "Platforms row 12 cols 4-7 and 17-22"
    JS code: for(let x=17;x<22;x++) g[12][x]=PLATFORM; (cols 17-21, not 17-22)
    The MD grid shows 6 equals signs starting at col 17, which extends to col 22.
    The JS only sets cols 17-21. This is a genuine mismatch between annotation
    description and JS code.

    VERDICT: The annotation text claims cols 17-22. The MD grid also shows
    cols 17-22. But JS code produces cols 17-21. Either the MD/annotation is
    wrong (col 22 shouldn't be a platform), or the JS is wrong (should include 22).

## Ch.T — Test Chamber: 17 GENUINE mismatches (17 reported)

This is the most problematic chamber. The MD grid appears to have been constructed
from a different version of the code or was manually typed with significant errors.

Key mismatches:
  - R2C12: MD has ^ (GOLEM_SPAWN), JS has v (DOOR_D)
  - R4C11: MD has . (AIR), JS has S (PUSH_SPAWN) — positions swapped
  - R4C12: MD has S (PUSH_SPAWN), JS has . (AIR)
  - R6C12: MD has X (CRACKED), JS has = (PLATFORM)
  - R7C12: MD has X (CRACKED), JS has = (PLATFORM)
  - R8C13: MD has = (PLATFORM), JS has . (AIR)
  - R8C15: MD has . (AIR), JS has = (PLATFORM)
  - R10C11: MD has . (AIR), JS has = (PLATFORM)
  - R10C12: MD has M (MAGICAL_WALL), JS has # (WALL)
  - R11C11: MD has . (AIR), JS has = (PLATFORM)
  - R11C12: MD has M (MAGICAL_WALL), JS has # (WALL)
  - R12C11: MD has . (AIR), JS has = (PLATFORM)
  - R12C12: MD has M (MAGICAL_WALL), JS has # (WALL)
  - R12C22: MD has . (AIR), JS has ^ (GOLEM_SPAWN)
  - R13C22: MD has # (WALL), JS has . (AIR)

  The Ch.T MD grid uses the wrong tile characters entirely:
  - Shows CRACKED(X) where JS has PLATFORM(=) for the platform column
  - Shows MAGICAL_WALL(M) where JS has WALL(#) for the wall divider
  - Missing GOLEM_SPAWN(^) at (22,12) — the spawn is at the floor gap
  - S and . are swapped at (11,4)/(12,4)

================================================================================
3. SYSTEMATIC ISSUES FOUND
================================================================================

## Issue A: GOLEM_SPAWN (^) consistently wrong in chamber-data.md

ALL 6 chambers have the spawn marker at the wrong column in the ASCII grid:

  Chamber | MD col | JS col | Offset
  --------|--------|--------|-------
  Ch.0    |   1    |   3    |  +2
  Ch.1    |   1    |   3    |  +2
  Ch.2    |   1    |   3    |  +2
  Ch.3    |   1    |   3    |  +2
  Ch.4    |   1    |   2    |  +1
  Ch.T    |   2    |  22    |  +20 (different entirely)

The pattern: in chambers 0-3, the MD grid places ^ at col 1 (immediately
after the left wall #). The JS code consistently places it at col 3.
In Ch.4, JS has col 2 (the annotation correctly says "(2,11)").

The MD grid is systematically wrong. The ^ should be moved to match JS code
positions.

## Issue B: Annotation lines introduce confusion

Every chamber in chamber-data.md has 1-5 annotation lines after the code block.
These annotations:

  1. Duplicate information that is already visible in the grid (spawn position,
     glyph position, door position).
  2. Sometimes CONTRADICT the grid itself (Ch.3: annotation says "slot opening
     at col 11" but grid shows WALL at col 11).
  3. Sometimes CONTRADICT the JS code (Ch.4: annotation says "platforms
     cols 17-22" but JS code only sets 17-21).
  4. Add interpretive descriptions ("Diagonal staircase walls ascend from (12,12)
     up to (9,10)") that are not directly encoded in the grid and are hard to
     verify from the grid alone.
  5. For Ch.T, the annotations are 6 lines of prose including game mechanics
     explanation ("Press T from any main chamber..."), which belongs in docs/
     not in the chamber data file.

The user's requirement is clear: chamber-data.md should have NO annotation lines
under grids. The grid should be self-contained and unambiguous.

## Issue C: Inconsistent construction order in golem.html

Each chamber IIFE builds the grid in a different sequence:

  Ch.0: boundaries (floor/ceiling/left wall, right wall with door exception)
         -> pits -> diagonal staircase -> glyph -> spawn -> push

  Ch.1: boundaries (floor/ceiling/sides)
         -> door -> pits -> platforms -> glyph -> walls -> spawn -> push

  Ch.2: boundaries (floor/ceiling/sides)
         -> door -> pits -> platforms -> magical wall -> top wall -> glyph -> spawn -> push

  Ch.3: boundaries (floor/ceiling/sides)
         -> door -> solid floor override -> slot opening -> push spawn
         -> wall blocks -> platforms -> glyph -> spawn -> push

  Ch.4: boundaries (floor/ceiling/sides)
         -> END_PORTAL -> CRACKED tiles (inner + outer) -> platforms -> spawn -> push

  Ch.T: boundaries (ceiling/floor/sides)
         -> door -> push spawn -> wall barrier -> platform column
         -> platform rows -> wall divider -> M column (actually =)
         -> floor row -> golem spawn -> push

Inconsistencies:
  1. Ch.0 sets boundaries differently (splits right wall from others)
  2. Ch.T sets ceiling and floor before sides (reversed from others)
  3. Ch.T is the only chamber that doesn't set row 13 as part of floor
  4. Pit placement timing varies: Ch.0 places pits after boundaries,
     Ch.1-4 place pits as part of boundary or immediately after
  5. Special properties (pushSpawn, pushSlot) are placed at different
     points in the construction order

A consistent convention would be:
  STEP 1: Boundaries (ceiling row 0, floor rows 13-14, sides cols 0 and 24)
  STEP 2: Pit overrides (where floor rows 13-14 should be ~ instead of #)
  STEP 3: Door / END_PORTAL
  STEP 4: Interior walls and barriers
  STEP 5: Platforms
  STEP 6: Glyphs and objectives
  STEP 7: Special tiles (pushSpawn, pushSlot)
  STEP 8: Golem spawn
  STEP 9: chambers.push()

## Issue D: Ch.T MD grid uses wrong tile characters

The Ch.T grid in chamber-data.md uses X (CRACKED) and M (MAGICAL_WALL) where
the JS code uses = (PLATFORM) and # (WALL) respectively. This is a fundamental
misunderstanding of the test chamber layout. The entire grid needs to be
re-generated from the JS code.

================================================================================
4. chamber_diff.py ANALYSIS
================================================================================

Current capabilities:
  - Parses ASCII grids from markdown code blocks (extract_chambers_from_markdown)
  - Parses JS chamber IIFEs by simulating execution (parse_js_chambers)
  - Compares grids tile-by-tile (compare_grids)
  - Validates grid structure (validate_grid): dimensions, valid chars, spawn count
  - Structural checks: spawn floor support, pit bordering (incomplete)
  - Visual side-by-side comparison with mismatch highlighting
  - Three modes: default diff, --validate, --diff-proposal
  - JSON output support
  - Per-chamber filtering (--chamber)

CRITICAL BUG: Handler ordering causes false positives

  The tool processes tile assignments in this order:
    1. direct_pattern (g[r][c]=CONST;)
    2. for_loop_x (for x loop with g[r][x]=CONST;)
    3. for_loop_y (for y loop with g[y][c]=CONST;)
    4. multi_for (for x loop with {g[r][x]=C;g[r2][x]=C;})
    5. multi_for_y (for y loop with {g[y][c]=C;g[y][c2]=C;})
    6. special_door (g[h-3][w-1]=CONST;)

  Problem: handlers 4-5 (multi_for/multi_for_y) run AFTER handler 1 (direct).
  They overwrite direct assignments that were already applied.

  Example: Ch.0
    - multi_for processes `for(let x=0;x<w;x++){g[14][x]=WALL;g[13][x]=WALL;...}`
      -> sets rows 14 and 13 to WALL
    - Then the code that should set g[14][12]=PIT, g[13][12]=PIT, etc.
      was already processed by direct_pattern BEFORE multi_for
    - Result: PIT is overwritten by WALL

  Fix: multi_for and multi_for_y handlers should run FIRST, then direct_pattern
  should run LAST (so it acts as an override). The special_door handler should
  run after everything else.

  Correct order should be:
    1. multi_for (boundary loops — fill first)
    2. multi_for_y (boundary loops — fill first)
    3. for_loop_x (range loops — fill second)
    4. for_loop_y (range loops — fill second)
    5. direct_pattern (specific overrides — last, takes priority)
    6. special_door (edge case overrides — final)

Missing functionality:
  1. No grid export from JS -> ASCII (can't generate MD from code)
  2. No annotation validation (doesn't check if annotations match grid)
  3. Incomplete pit validation (pit border check is stubbed, always passes)
  4. No reachability analysis (can't verify glyph/door is reachable)
  5. No spawn walkability check (doesn't verify spawn has walkable area)
  6. No property validation (doesn't check pushSpawn/pushSlot coordinates
     match grid tiles)
  7. No flowId consistency check (doesn't verify CHAMBER_FLOW matches
     chamber list)
  8. No cross-chamber diff (can't compare chamber-proposal.md against
     chamber-data.md AND golem.html simultaneously)
  9. No automated MD grid regeneration from golem.html
  10. No construction order analysis for golem.html IIFEs

================================================================================
5. RECOMMENDATIONS
================================================================================

## Immediate fixes for chamber-data.md:

  1. Fix GOLEM_SPAWN position in all chambers (move ^ from col 1 to correct col)
  2. Fix Ch.3 slot opening at (11,12) and (11,13) — change # to .
  3. Fix Ch.4 platform range — verify col 22 is or isn't a platform
  4. Regenerate Ch.T grid entirely from golem.html JS code
  5. Remove ALL annotation lines after grids (per user requirement)
  6. Remove Ch.T game mechanics explanation from chamber-data.md
     (move to docs/ or keep in code comments)

## Fix for chamber_diff.py:

  1. Reorder handlers: multi_for/multi_for_y FIRST, direct LAST
  2. Add grid export function (JS -> ASCII)
  3. Add annotation validation mode
  4. Complete pit border validation
  5. Add property consistency checks (pushSpawn matches S tile, etc.)

## Convention for golem.html:

  1. Document the ordered construction convention (Steps 1-9 above)
  2. Reorder existing IIFEs to follow convention
  3. Add comments marking each step within each IIFE

================================================================================
6. SUMMARY OF ALL MISMATCHES (genuine, excluding tool bugs)
================================================================================

Chamber | Count | Details
--------|-------|------------------------------------------
Ch.0    |  1    | ^ at col 1 (should be 3)
Ch.1    |  1    | ^ at col 1 (should be 3)
Ch.2    |  1    | ^ at col 1 (should be 3)
Ch.3    |  3    | ^ at col 1 (should be 3), slot # instead of . at (11,12) and (11,13)
Ch.4    |  2    | ^ at col 1 (should be 2), platform annotation wrong
Ch.T    | 17    | Major grid reconstruction needed (wrong tiles, wrong positions)
--------|-------|------------------------------------------
Total   | 25    | Genuine tile mismatches between MD grid and JS code

Plus: 5 annotation contradictions (Ch.0 spawn coords, Ch.3 slot description,
      Ch.4 platform range, Ch.T game mechanics prose, Ch.1/Ch.2 wall descriptions)
