# Chamber Representation

Chambers are 25 columns x 15 rows. Each tile maps to one ASCII character.
Grids are rendered as compact 25-char rows with row-number labels on the left.

## Tile Legend

| Char  | Constant   | Value | Description                                  |
| ----- | ---------- | ----- | -------------------------------------------- |
| `.` | AIR        | 0     | Empty space                                  |
| `#` | WALL       | 1     | Solid wall (floor, ceiling, boundaries)      |
| `~` | PIT        | 2     | Death void — touching respawns player       |
| `^` | GOLEM_SPAWN | 3     | Player spawn marker (invisible, determines golem position) |
| `v` | DOOR_D     | 4     | Down-side exit door (glyph-locked). Test chamber uses `^` at row 2.           |
| `*` | GLYPH      | 5     | Collectible knowledge glyph                  |
| `X` | CRACKED    | 7     | Breakable wall (requires Glyph 4)            |
| `=` | PLATFORM   | 8     | One-way platform (passable from below)       |
| `@` | END_PORTAL | 9     | Final portal — triggers ending              |
| `M` | MAGICAL_W  | 10    | Destructible barrier (dash kills on contact) |
| `S` | PUSH_SPAWN | 11    | Spawn marker for free-moving push block      |

## Format

```
+-----------------------------+
| Ch.N [Name]                 |
+-----------------------------+
|00 ######################### |
|01 #.......................# |
|02 #.......................# |
|03 #.......................# |
|04 #.......................# |
|05 #.......................# |
|06 #.......................# |
|07 #.......................# |
|08 #.......................# |
|09 #.......................# |
|10 #.......................# |
|11 #.......................# |
|12 #.......................# |
|13 #.......................# |
|14 #.......................# |
+-----------------------------+
```

- **Header:** Chamber name in the top banner row.
- **Row labels:** `|00` through `|14` — the two digits are the row number (y-coordinate).
- **Grid cells:** Exactly 25 characters per row, no spaces between them. Each character
  is one tile. Column index increases left to right (0-24).
- **Border:** `+` corners, `-` horizontal lines, `|` vertical delimiters.

## Coordinate System

- Origin (0, 0) is top-left.
- Position is (column, row) — column first, matching the JS `g[row][col]` access.
- Row numbers are shown on the left. To find tile at (col=10, row=8), read row `|08`
  and count 10 characters from the left (after `|08 `).

## Chamber Flow System

Chambers are ordered by the `CHAMBER_FLOW` array (defined after
`CHAMBER_NAMES` in Section 1 of `golem.html`), **not** by position in the
`chambers[]` array. This decouples level ordering from file structure.

### How it works

1. Each main chamber has a `flowId` property: `'ch0'`, `'ch1'`, etc.
2. `CHAMBER_FLOW = ['ch0','ch1','ch2','ch3','ch4']` defines progression order.
3. `checkDoors()` finds the current chamber's position in `CHAMBER_FLOW` and
   transitions to the next flowId — the DOOR_D always leads to the next level
   in the flow.
4. Chambers **without** a `flowId` (e.g. the test chamber) are not part of the
   flow. They are identified by `!c.flowId`.
5. The test chamber's DOOR_D returns to the source chamber (`testChamberSrc`).

### Adding a new main chamber

1. Choose a `flowId` (e.g. `'ch5'`) and insert it into `CHAMBER_FLOW` at the
   desired position (e.g. between `'ch2'` and `'ch3'` to insert between
   Chambers 2 and 3).
2. Add a `CHAMBER_NAMES` entry at the matching index.
3. Create the chamber IIFE with `flowId` in the push object:
   ```js
   chambers.push({w,h,tiles:g,glyphs:[...],flowId:'ch5'});
   ```
4. The IIFE can be placed **anywhere** in Section 2 — the flow system handles ordering.

### Replacing an existing chamber

1. Keep the same `flowId` (e.g. `'ch2'`).
2. Replace the grid tiles in the IIFE.
3. Update `chamber-data.md` with the new ASCII grid.
4. No changes to `CHAMBER_FLOW` or `CHAMBER_NAMES`.

### Appending after the final chamber

1. Add a new flowId (e.g. `'ch5'`) to the end of `CHAMBER_FLOW`.
2. Add the chamber name to `CHAMBER_NAMES`.
3. The current last chamber's DOOR_D will now lead to the new chamber.
4. If the current last chamber has an END_PORTAL, change it to DOOR_D
   (or add a DOOR_D alongside the portal).

### Adding a special chamber (test, bonus, secret)

1. Do **NOT** add a `flowId` — omit it from the push object entirely.
2. The chamber is identified by absence of flowId (`!c.flowId`).
3. The test chamber has its own entry/exit logic (press T, tracked via
   `testChamberSrc`). Custom entry logic is needed for other special types.
4. Place the IIFE anywhere in Section 2.

### Important rules

- Every main chamber **MUST** have a unique `flowId` present in `CHAMBER_FLOW`.
- `CHAMBER_FLOW` length must match `CHAMBER_NAMES` length.
- The test chamber **MUST NOT** have a `flowId` — it is the discriminator.
- `collectedGlyphs` is sized to `chambers.length` at init, so it adapts
  automatically to any number of chambers.
- Numbers for main progression (Ch.0, Ch.1, ...). Letters for special
  chambers (Ch.T for test, Ch.A/B/C for bonus, etc.).

## Reading a Chamber

1. **Trace walkable space** — contiguous `.` cells are where the player moves.
2. **Find barriers** — `#` (WALL), `X` (CRACKED), `M` (MAGICAL_WALL) block movement.
3. **Locate platforms** — `=` (PLATFORM) are one-way: walkable from above, passable
   from below.
4. **Identify hazards** — `~` (PIT) tiles kill and respawn the player.
5. **Find spawn point** — `^` (GOLEM_SPAWN) marks where the golem enters the chamber.
   Each chamber has exactly one spawn tile.
6. **Find objectives** — `*` (GLYPH) to collect, `v` (DOOR_D) to exit,
   `S` (PUSH_SPAWN) for push blocks, `@` (END_PORTAL) for the finale.
7. **Note spawn coordinates** — listed in the annotation below each grid.

## Modifying a Chamber

1. Copy the blank template. Keep exactly 25 characters per row and 15 rows total.
2. Replace `.` with any tile character from the legend.
3. **Place spawn marker** — each chamber must have exactly one `^` (GOLEM_SPAWN) tile
   at the player spawn position.
4. After editing, verify:
   - Spawn area has walkable `.` tiles beneath it.
   - The `^` (GOLEM_SPAWN) tile has a solid floor tile (`#`) directly below it.
   - Each chamber has exactly one `^` tile.
   - Exit doors (`v`) are reachable from walkable space.
   - Pits (`~`) are surrounded by barriers so they act as hazards.
   - Push block spawns (`S`) have empty space ahead for movement.
   - The grid still has exactly 25 chars per row and 15 rows.
5. To convert back to JavaScript, replace each character with its tile constant value
   and assign via `g[row][col] = VALUE` or build row arrays.

## Extracting Chamber Data from golem.html

The game source builds each chamber inside an IIFE block. The process is:

### Step 1 — Locate the chamber block

Find the IIFE in the `SECTION 2: CHAMBER DATA` area. Each block looks like:

```js
(function(){
  const w=25,h=15,g=mkGrid(w,h);
  // ... tile assignments ...
  chambers.push({w,h,tiles:g,glyphs:[...]});
})();
```

### Step 2 — Parse the assignments

Each statement modifies the grid `g[row][col]`. There are three forms:

**A. Loop statements** — fill ranges with a constant value:

```js
for(let x=0;x<w;x++){ g[14][x]=WALL; g[13][x]=WALL; g[0][x]=WALL; }
```

This sets row 14, 13, and 0, all columns 0-24, to WALL.

**B. Range loops** — fill a horizontal span on one row:

```js
for(let y=4;y<13;y++) g[y][9]=WALL;
```

This sets rows 4 through 12, column 9, to WALL (note: `<13` means up to row 12).

**C. Direct assignments** — single tile:

```js
g[8][10]=GLYPH;
```

This sets row 8, column 10 to GLYPH.

### Step 3 — Reconstruct the grid

Apply all statements in order to a 25x15 grid initialized to AIR (0).
Later assignments overwrite earlier ones. The final state is the chamber.

**Note:** Place `^` (GOLEM_SPAWN) at the player spawn position. This tile is
invisible at runtime but determines where the golem spawns. Each chamber must
have exactly one `^` tile, and there must be a solid floor tile (`#`) directly
below it to support the golem on entry.

**Key parsing rules:**

- `g[y][x]` means `g[row][col]` — first index is row (y), second is column (x).
- `for(let i=a;i<b;i++)` covers indices a through b-1 (exclusive upper bound).
- `for(let i=a;i<=b;i++)` covers indices a through b inclusive.
- `w` is always 25, `h` is always 15.

### Verification

After extraction, verify the grid matches the game by checking:

- GOLEM_SPAWN (^) tile position matches the player spawn position.
- Glyph positions from the `glyphs` array.
- Special properties like `pushSpawn`, `pushSlot`.

## Converting ASCII Grid back to JavaScript

Two approaches: explicit per-tile assignments (simple, readable) or
compact loop-based code (matches the original style).

### Approach A — Per-tile assignments (direct, unambiguous)

For each non-AIR tile in the grid, emit a `g[row][col] = CONSTANT;` line:

```
Grid row |08 #.........*.............#
```

becomes:

```js
g[8][0]=WALL;
g[8][10]=GLYPH;
g[8][24]=WALL;
```

This is the safest method — every changed tile is visible.

### Approach B — Loop-based (compact, matches original style)

Group contiguous runs of the same tile into loop statements.

**Horizontal runs on the same row:**

```
|10 #...##########=========.#
```

becomes:

```js
g[10][0]=WALL;
for(let x=4;x<=13;x++) g[10][x]=WALL;
for(let x=14;x<=22;x++) g[10][x]=PLATFORM;
g[10][24]=WALL;
```

**Vertical runs (same column, consecutive rows):**

```js
for(let y=4;y<13;y++) g[y][9]=WALL;
```

covers rows 4 through 12 at column 9.

**Full-row fills:**

```js
for(let x=0;x<w;x++) g[0][x]=WALL;
```

### Conversion script (Python)

To convert an ASCII grid back to JS automatically, use this:

```python
CHAR_TO_CONST = {
    '.': 'AIR', '#': 'WALL', '~': 'PIT', '^': 'GOLEM_SPAWN',
    'v': 'DOOR_D', '*': 'GLYPH', 'X': 'CRACKED',
    '=': 'PLATFORM', '@': 'END_PORTAL', 'M': 'MAGICAL_WALL',
    'S': 'PUSH_SPAWN'
}

def ascii_grid_to_js(grid_lines, chamber_name):
    """Convert ASCII grid lines (|00 ...) to JavaScript tile assignments."""
    rows = []
    for line in grid_lines:
        # Strip |NN prefix and trailing |
        chars = line[4:29]  # chars 4..28 = 25 tiles
        rows.append(chars)

    # Emit IIFE wrapper
    lines = [f"// {chamber_name}", "(function(){{", "  const w=25,h=15,g=mkGrid(w,h);"]

    # Emit per-tile assignments for non-AIR tiles
    for y in range(15):
        for x in range(25):
            tile = rows[y][x]
            if tile != '.':
                const = CHAR_TO_CONST[tile]
                lines.append(f"  g[{y}][{x}]={const};")

    lines.append("  chambers.push({w,h,tiles:g,glyphs:[],flowId:'chN'});")
    lines.append("})();")
    return "\n".join(lines)
```

Replace `'chN'` with the actual flowId and adjust `glyphs` array for main
chambers. Omit `flowId` for special chambers (test, bonus, etc.).

### Where the JS goes in golem.html

Insert the new chamber IIFE in `SECTION 2: CHAMBER DATA`. The IIFE can be
placed anywhere in this section — the `CHAMBER_FLOW` array controls the
playable order, not the file position. The section is bounded by delimiter comments:

```
/* ══════════════════════════════════════════════════
   2. CHAMBER DATA (Level data)
   ══════════════════════════════════════════════════ */
```

Place your IIFE after the last existing chamber and before the closing of the
before `SECTION 3: ENTITIES`. Update `CHAMBER_FLOW` and `CHAMBER_NAMES`
in Section 1 to include the new chamber.

### golem.html Section Map (after refactor)

| Section | Contents |
|---------|----------|
| 1. SETUP & CONSTANTS | Canvas, context, dimensions, tile types, dash constants |
| 2. CHAMBER DATA | mkGrid(), chambers[], all chamber IIFEs |
| 3. ENTITIES | P (player), PB (push block), game state globals |
| 4. INPUT | Key listeners, fresh(), shiftHeld() |
| 5. TILE HELPERS & COLLISION | getTile, setTile, solid, platSolid, collides*, inPit, aabb, tileCollides |
| 6. PUSH BLOCK SYSTEM | resetPushBlock, resolvePushBlockCollision, updatePushBlock |
| 7. PARTICLE SYSTEM | shatterBlock, spawnParticles, updateParticles |
| 8. GAME FLOW | showMessage, _doTransition, transition, checkDoors, checkGlyphs, transitionEnding |
| 9. UPDATE | update() — main physics/input/game logic loop |
| 10. RENDER | COLORS, render() — all drawing |
| 11. INIT & GAME LOOP | Init code, loop(), requestAnimationFrame |

## Existing Chambers

See `chamber-data.md` for the full ASCII grids and annotations of all 5
existing chambers (Ch.0 Awakening through Ch.4 The Ibis Chamber).
