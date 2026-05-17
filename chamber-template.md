# Chamber Representation

Chambers are 25 columns x 15 rows. Each tile maps to one ASCII character.
Grids are rendered as compact 25-char rows with row-number labels on the left.

## Tile Legend

| Char  | Constant   | Value | Description                                  |
| ----- | ---------- | ----- | -------------------------------------------- |
| `.` | AIR        | 0     | Empty space                                  |
| `#` | WALL       | 1     | Solid wall (floor, ceiling, boundaries)      |
| `~` | PIT        | 2     | Death void — touching respawns player       |
| `>` | DOOR_R     | 3     | Right-side exit door (glyph-locked)          |
| `v` | DOOR_D     | 4     | Down-side exit door (glyph-locked)           |
| `*` | GLYPH      | 5     | Collectible knowledge glyph                  |
| `B` | BLOCK      | 6     | Pushable block (static tile)                 |
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

## Reading a Chamber

1. **Trace walkable space** — contiguous `.` cells are where the player moves.
2. **Find barriers** — `#` (WALL), `X` (CRACKED), `M` (MAGICAL_WALL) block movement.
3. **Locate platforms** — `=` (PLATFORM) are one-way: walkable from above, passable
   from below.
4. **Identify hazards** — `~` (PIT) tiles kill and respawn the player.
5. **Find objectives** — `*` (GLYPH) to collect, `v` or `>` (DOOR) to exit,
   `S` (PUSH_SPAWN) for push blocks, `@` (END_PORTAL) for the finale.
6. **Note spawn point** — listed in the annotation below each grid.

## Modifying a Chamber

1. Copy the blank template. Keep exactly 25 characters per row and 15 rows total.
2. Replace `.` with any tile character from the legend.
3. After editing, verify:
   - Spawn area has walkable `.` tiles beneath it.
   - Exit doors (`v`, `>`) are reachable from walkable space.
   - Pits (`~`) are surrounded by barriers so they act as hazards.
   - Push block spawns (`S`) have empty space ahead for movement.
   - The grid still has exactly 25 chars per row and 15 rows.
4. To convert back to JavaScript, replace each character with its tile constant value
   and assign via `g[row][col] = VALUE` or build row arrays.

## Extracting Chamber Data from golem.html

The game source builds each chamber inside an IIFE block. The process is:

### Step 1 — Locate the chamber block

Find the IIFE in the `SECTION 2: CHAMBER DATA` area. Each block looks like:

```js
(function(){
  const w=25,h=15,g=mkGrid(w,h);
  // ... tile assignments ...
  chambers.push({w,h,tiles:g,px:3*T,py:11*T,glyphs:[...]});
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

**Key parsing rules:**

- `g[y][x]` means `g[row][col]` — first index is row (y), second is column (x).
- `for(let i=a;i<b;i++)` covers indices a through b-1 (exclusive upper bound).
- `for(let i=a;i<=b;i++)` covers indices a through b inclusive.
- `w` is always 25, `h` is always 15.

### Verification

After extraction, verify the grid matches the game by checking:

- Spawn position from the `chambers.push()` call (`px`, `py` divided by T=32 gives tile coords).
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
    '.': 'AIR', '#': 'WALL', '~': 'PIT', '>': 'DOOR_R',
    'v': 'DOOR_D', '*': 'GLYPH', 'B': 'BLOCK', 'X': 'CRACKED',
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

    lines.append("  chambers.push({w,h,tiles:g,px:3*T,py:11*T,glyphs:[]});")
    lines.append("})();")
    return "\n".join(lines)
```

### Where the JS goes in golem.html

Insert the new chamber IIFE in `SECTION 2: CHAMBER DATA`, in numerical order
(Ch.N) with the existing chambers. The section is bounded by delimiter comments:

```
/* ══════════════════════════════════════════════════
   2. CHAMBER DATA (Level data)
   ══════════════════════════════════════════════════ */
```

Place your IIFE after the last existing chamber and before the closing of the
section (before `SECTION 3: ENTITIES`). Then increment any code that references
the chamber count if applicable.

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
