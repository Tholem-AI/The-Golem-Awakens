# Adding Chambers — Contributor Guide

This guide walks you through designing and implementing a new chamber for *The Golem Awakens*. Chambers are 25x15 tile grids that define the level layout, spawn points, objectives, and hazards.

## Prerequisites

Before adding a chamber, familiarize yourself with:

- **[chamber-template.md](../chamber-template.md)** — The complete reference for tile types, grid format, coordinate system, and the ordered construction convention used in `golem.html`.
- **[chamber-data.md](../chamber-data.md)** — The current ASCII grids for all existing chambers. Use these as examples of well-structured level layouts.
- **[chamber-proposal.md](../chamber-proposal.md)** — Reusable template for drafting new chamber designs before implementation.
- **golem.html Section 2** — Where chamber IIFE (Immediately Invoked Function Expression) blocks live. Each chamber is defined inside one.

## Step-by-Step Workflow

### Step 1: Copy the proposal template

```bash
cp chamber-proposal.md my-new-chamber.md
```

Fill in all sections of the template:
- Chamber overview (flowId, name, abilities, prerequisites)
- Flow description (intended player path)
- Mechanics checklist (which abilities are used/taught)
- ASCII grid (see format below)
- Key coordinates (spawn, glyph, door, platforms, pits)
- Verification checklist

### Step 2: Build the ASCII grid

Every chamber is exactly **25 columns x 15 rows**, using characters from the tile legend:

| Char | Tile | Description |
|------|------|-------------|
| `.` | AIR | Empty space |
| `#` | WALL | Solid wall |
| `~` | PIT | Death void |
| `^` | GOLEM_SPAWN | Player spawn (one per chamber) |
| `v` | DOOR_D | Exit door (links to next chamber via flow) |
| `*` | GLYPH | Collectible |
| `X` | CRACKED | Breakable wall |
| `=` | PLATFORM | One-way platform |
| `@` | END_PORTAL | Final portal |
| `M` | MAGICAL_WALL | Dash-passable barrier |
| `S` | PUSH_SPAWN | Push block spawn |

Grid format example:

```
+-----------------------------+
| Ch.5 [My Chamber]           |
+-----------------------------+
|00 ######################### |
|01 #.......................# |
... (15 rows total, rows 00-14)
|14 ######################### |
+-----------------------------+
```

**Rules:**
- Exactly 25 characters per row, no spaces between tiles.
- Exactly 15 rows per chamber (00 through 14).
- Exactly one `^` (GOLEM_SPAWN) per chamber.
- The `^` tile must have a solid `#` directly below it.
- Pit tiles (`~`) must be bordered by solid tiles on all sides.

### Step 3: Validate the proposal

Run the chamber diff tool to check your grid before implementation:

```bash
# Workflow B: Validate proposal structure
python3 tools/chamber_diff.py --validate my-new-chamber.md --strict
```

This checks:
- Grid dimensions (25x15)
- Exactly one spawn point
- Spawn has solid floor beneath
- Pit borders are solid
- All tile characters are from the legend
- Properties consistency

### Step 4: Implement in golem.html

Create a chamber IIFE block in `golem.html`, Section 2 (CHAMBER DATA). Follow the **9-step ordered construction convention**:

```js
// Chamber 5: [Name] — [brief description]
(function(){
  const w=25,h=15,g=mkGrid(w,h);

  /* Step 1: Boundaries */
  sBounds(g,w,h);  // Sets ceiling (row 0), floor (rows 13-14), left wall (col 0), right wall (col 24)

  /* Step 2: Pits */
  for(let x=8;x<=12;x++) g[14][x]=PIT;

  /* Step 3: Door/Portal */
  g[1][20]=DOOR_D;

  /* Step 4: Interior walls */
  for(let x=10;x<=15;x++) g[8][x]=WALL;
  for(let y=2;y<=6;y++) g[y][5]=WALL;

  /* Step 5: Platforms */
  g[6][10]=PLATFORM; g[6][11]=PLATFORM;

  /* Step 6: Glyphs */
  g[1][15]=GLYPH;

  /* Step 7: Special tiles */
  g[4][12]=CRACKED;
  g[3][8]=MAGICAL_WALL;
  g[2][20]=PUSH_SPAWN;

  /* Step 8: Golem spawn */
  g[12][5]=GOLEM_SPAWN;

  /* Step 9: Push */
  chambers.push({w,h,tiles:g,glyphs:[{x:15,y:1}],flowId:'ch5'});
})();
```

**Important:**
- The IIFE can be placed **anywhere** in Section 2 — the `CHAMBER_FLOW` array controls the playable order.
- Use the `/* Step N: ... */` comment prefix for each phase (required for consistency).
- Convert your ASCII grid to JavaScript assignments using the approach described in [chamber-template.md](../chamber-template.md) ("Converting ASCII Grid back to JavaScript").

### Step 5: Register in flow system

In `golem.html` Section 1 (SETUP & CONSTANTS), add your chamber to the flow:

```js
const CHAMBER_FLOW = ['ch0','ch1','ch2','ch3','ch4','ch5'];
const CHAMBER_NAMES = ['Awakening','The Library','The Hall of Echoes','The Weight of Wisdom','The Ibis Chamber','My Chamber'];
```

Insert the `flowId` at the desired position — this determines which chamber the exit door leads to/from.

### Step 6: Final validation

Run the full validation pipeline (Workflows D and A from [chamber-template.md](../chamber-template.md)):

```bash
# Workflow D: Three-way check (proposal vs data vs code)
python3 tools/chamber_diff.py --diff-proposal chamber-data.md my-new-chamber.md --against-js golem.html
python3 tools/chamber_diff.py --strict

# Workflow F: Check flow consistency
python3 tools/chamber_diff.py --check-flow
```

All three commands should report 0 mismatches / no errors.

### Step 7: Test in browser

Open `golem.html` in a browser and play through your new chamber:
- Press `T` at any time to enter the test chamber (all abilities unlocked) for focused testing.
- Set `_testMode = true` in the browser console for instant transitions between chambers.
- Verify that all objectives are reachable and the exit door/portal works.

## Validation Tool Reference

The `tools/chamber_diff.py` tool supports six workflows (documented in [chamber-template.md](../chamber-template.md)):

| Workflow | Command | Purpose |
|----------|---------|---------|
| A | `python3 tools/chamber_diff.py --strict` | Verify chamber-data.md matches golem.html |
| B | `python3 tools/chamber_diff.py --validate FILE.md --strict` | Validate a proposal's structure |
| C | `python3 tools/chamber_diff.py --diff-proposal chamber-data.md proposal.md` | Compare proposal against existing data |
| D | `python3 tools/chamber_diff.py --diff-proposal chamber-data.md proposal.md --against-js golem.html` + `--strict` | Three-way check after implementation |
| E | `python3 tools/chamber_diff.py --export-ascii chamber-data.md` | Regenerate chamber-data.md from golem.html |
| F | `python3 tools/chamber_diff.py --check-flow` | Verify CHAMBER_FLOW, CHAMBER_NAMES, and flowIds consistency |

## Example: Verifying with verify_ch4_walls.py

The `tools/verify_ch4_walls.py` script demonstrates a custom validation pattern. It:

1. Defines the expected grid as a Python list of strings.
2. Scans for interior wall positions (not on boundary rows/cols).
3. Groups walls into contiguous vertical and horizontal runs by column/row.

This pattern is useful for chambers with complex wall layouts — you can write a similar verification script for your chamber to ensure the JavaScript implementation matches your design intent.

```python
# Example pattern from verify_ch4_walls.py:
grid = [
    '#########################',  # row 00
    '#@X..MMMM....M......M...#',  # row 01
    # ... (15 rows)
]
# Then iterate to find contiguous runs of WALL (#) tiles
```

## Common Pitfalls

| Pitfall | How to Avoid |
|---------|-------------|
| Wrong grid dimensions | Always 25 cols x 15 rows. Run `--validate` to catch early. |
| Missing spawn tile | Each chamber needs exactly one `^`. The game uses it for player position. |
| Spawn without floor | The `^` tile must have `#` directly below it, or the golem falls on entry. |
| Unreachable glyph | Trace the walkable path from spawn to glyph. Use `--validate` and browser testing. |
| Pit without borders | Pits (`~`) must be surrounded by solid tiles. Otherwise they look like holes in walls. |
| Push block with no space | `S` (PUSH_SPAWN) needs empty space in the push direction, or the block spawns stuck. |
| Duplicate flowId | Every main chamber needs a unique `flowId`. Run `--check-flow` to verify. |
| Forgetting CHAMBER_NAMES | Adding a flowId without a matching name entry causes index mismatch. |
| Not following construction order | Use the 9-step convention. Steps that override earlier ones (e.g., Pits over Boundaries) depend on execution order. |
| Tile value 6 doesn't exist | The value 6 was removed. Tile values jump from 5 (GLYPH) to 7 (CRACKED). |

## Best Practices

1. **Design the ASCII grid first** — it's easier to reason about level layout in a visual grid than in JavaScript code.
2. **Use the proposal template** — it forces you to document intent and verify before coding.
3. **Follow the 9-step convention** — keeps code readable, diffable, and consistent with the validation tool's parsing order.
4. **Group contiguous tiles into loops** — e.g., `for(let x=10;x<=15;x++) g[8][x]=WALL;` is more compact than six separate assignments.
5. **Test with `_testMode = true`** — skip the fade transitions and verify chamber-to-chamber flow quickly.
6. **Use the test chamber (`T`)** — it has all abilities unlocked, making it easy to prototype mechanics in isolation.
7. **Run the full validation pipeline** before declaring work complete. No mismatches = confidence in correctness.
8. **Keep chambers self-contained** — each IIFE should define its own grid. Don't reference tiles from other chambers.
