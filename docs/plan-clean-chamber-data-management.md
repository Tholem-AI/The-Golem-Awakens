# Execution Plan: Clean Chamber Data Management

**Project:** GOLEM_GAME
**Date:** 2026-05-20
**Author:** Hermes Agent (planner-agent phase)
**Status:** Ready for execution
**Parent:** RIPER Plan Phase

---

## Objective

Eliminate ambiguity in chamber data management by:
1. Fixing all 25 genuine tile mismatches between `chamber-data.md` and `golem.html`
2. Removing all annotation lines from `chamber-data.md` (grid-only source of truth)
3. Establishing a consistent ordered construction convention for `golem.html` IIFEs
4. Fixing the critical handler ordering bug in `chamber_diff.py`
5. Enhancing `chamber_diff.py` with JS->ASCII export, strict validation, flowId checks
6. Updating `chamber-template.md` Tile Legend to match `golem.html` constants exactly
7. Establishing clear diff workflows for both production and proposal scenarios

---

## Current State Assessment

### Files Involved

| File | Lines | Role | Issues |
|------|-------|------|--------|
| `golem.html` | 1499 | Single-file game, Section 2 (L112-250) has 6 chamber IIFEs | Inconsistent construction order across IIFEs |
| `chamber-data.md` | 185 | ASCII grid reference for all 6 chambers | 25 genuine tile mismatches; annotation lines contradict grid/JS |
| `chamber-template.md` | 350 | Format spec + conversion guide | Tile Legend matches; no construction convention documented |
| `chamber-proposal.md` | 113 | Reusable template for new chambers | No issues — well structured |
| `tools/chamber_diff.py` | 817 | Diff/validation tool | Critical handler ordering bug causing ~50 false positives; missing JS->ASCII export |
| `docs/chamber-data-consistency-findings.md` | 380 | Research report | Source of truth for all findings |

### Confirmed Issues Summary

| Issue | Chambers Affected | Severity | Count |
|-------|-------------------|----------|-------|
| GOLEM_SPAWN (^) at wrong column (col 1 instead of 2-3) | Ch.0, Ch.1, Ch.2, Ch.3, Ch.4 | HIGH | 5 |
| Ch.3 slot opening: WALL instead of AIR at (11,12) and (11,13) | Ch.3 | HIGH | 2 |
| Ch.T grid completely wrong (17 tiles use wrong characters/positions) | Ch.T | CRITICAL | 17 |
| Annotation lines contradict grid and/or JS code | Ch.0-4, Ch.T | MEDIUM | 5 |
| chamber_diff.py handler ordering bug (multi_for after direct_pattern) | Tool | CRITICAL | 1 bug, ~50 false positives |
| golem.html IIFEs use 6 different construction orders | Ch.0-4, Ch.T | LOW | Style only |

---

## Innovate Checkpoint

Before executing, two alternative approaches are evaluated for each major decision:

### Decision 1: Approach to chamber-data.md Cleanup

**Alternative A — Regenerate from golem.html using enhanced chamber_diff.py (RECOMMENDED)**

- Fix chamber_diff.py handler ordering bug first
- Add `--export-ascii` mode: parses JS IIFEs, outputs correct ASCII grids
- Pipe output to produce a clean chamber-data.md
- Benefits: Guaranteed consistency with JS; automatable; no manual errors
- Risks: Requires getting the handler ordering right before export; one-step dependency

**Alternative B — Manual surgical fixes to existing chamber-data.md**

- Apply the 25 specific tile corrections from the research report
- Delete all annotation lines (lines 30-31, 57-60, 86-89, 115-118, 144-147, 173-185)
- Benefits: Direct, auditable changes; no tool dependency
- Risks: Manual effort prone to off-by-one errors; doesn't prevent future divergence

**Decision: Alternative A.** The tool-based approach is more robust and sets up the export
capability needed for the diff workflow. Alternative B is kept as a fallback for any
edge cases the parser doesn't handle.

### Decision 2: Construction Convention for golem.html IIFEs

**Alternative A — Ordered step comments with sequential construction (RECOMMENDED)**

- Document a 9-step convention in `chamber-template.md`
- Reorder existing IIFEs to follow the convention with `/* STEP N: ... */` comments
- Benefits: Readable, consistent, easy to diff; humans and tools can parse structure
- Risks: Requires reordering ~140 lines across 6 IIFEs; merge conflicts possible

**Alternative B — Declarative row-by-row data structure**

- Replace IIFE construction loops with a row-array literal or JSON-like structure:
  ```js
  const gridData = [
    "#########################",
    "#...........v...........#",
    // ... 15 rows ...
  ];
  const g = gridData.map(row => [...row].map(ch => CHAR_MAP[ch]));
  ```
- Benefits: Direct visual correspondence to ASCII grid; trivially diffable
- Risks: Changes the coding style significantly; may not fit single-file constraints cleanly;
  ~56KB file might grow; requires adding CHAR_MAP lookup; this is a larger refactor

**Decision: Alternative A.** Less invasive, preserves existing coding patterns, adds
convention discipline without architectural changes. Alternative B is a future option
if the codebase grows and readability becomes a priority.

---

## Execution Plan: Phases

### Phase 1: Fix and enhance chamber_diff.py (PREREQUISITE for all other phases)

**Files:** `tools/chamber_diff.py`
**Estimated effort:** 2-3 hours

#### Task 1.1: Fix handler ordering bug (CRITICAL)

**Current (BROKEN) order in `parse_js_chambers()`:**
```
1. direct_pattern (g[r][c]=CONST;)       # L294-300
2. for_loop_x (for x loop, single g[y][x]) # L304-328
3. for_loop_y (for y loop, single g[y][c]) # L330-355
4. multi_for (for x loop, {g[r1][x]=C;g[r2][x]=C;}) # L357-371
5. multi_for_y (for y loop, {g[y][c1]=C;g[y][c2]=C;}) # L373-393
6. special_door (g[h-3][w-1]=CONST;)    # L396-402
7. multi_for_y_h2 (for y<h-2 variant)   # L405-421
```

**Problem:** Steps 4-5 run AFTER step 1, so boundary loops (multi_for) OVERWRITE
direct assignments. Example: Ch.0 sets `g[14][12]=PIT` (direct), then multi_for
overwrites row 14 entirely with WALL.

**Fix:** Reorder to:
```
1. multi_for (boundary loops — fill first, lowest priority)
2. multi_for_y (boundary loops — fill first)
3. multi_for_y_h2 (boundary h-2 variant — fill first)
4. for_loop_x (range loops — fill second)
5. for_loop_y (range loops — fill second)
6. direct_pattern (specific overrides — last, highest priority)
7. special_door (edge case overrides — final)
```

**Implementation:** In `parse_js_chambers()` (L288-422), reorder the handler
blocks. The code for each handler stays the same — only the block order changes.

#### Task 1.2: Add `--export-ascii` mode (JS -> ASCII grid)

**New function:** `export_ascii_grid(js_chamber, chamber_key)`

- Takes the parsed JS grid (value matrix) and converts to ASCII using `grid_to_ascii()`
- Formats with proper border framing matching chamber-data.md format:
  ```
  +-----------------------------+
  | Ch.N [Name]                 |
  +-----------------------------+
  |00 ######################### |
  |01 #.......................# |
  ...
  |14 ######################### |
  +-----------------------------+
  ```
- Outputs full markdown section including H2 header

**New CLI flag:** `--export-ascii [OUTPUT.md]`
- Without argument: prints to stdout
- With argument: writes to file (overwrites existing)
- Auto-detects chamber names from `CHAMBER_NAMES` array in golem.html

**Implementation details:**
- Parse CHAMBER_NAMES from golem.html Section 1 (L75):
  `const CHAMBER_NAMES = ['Awakening','The Library',...];`
- Map chamber keys (Ch.0, Ch.1, etc.) to names
- Ch.T uses "[TEST CHAMBER]" as name (no CHAMBER_NAMES entry)

#### Task 1.3: Add `--strict` validation mode

**New CLI flag:** `--strict`

Enhances validation checks beyond basic structure:

1. **Spawn walkability:** Verify 3x3 area around spawn is AIR/GOLEM_SPAWN (no walls blocking entry)
2. **Spawn floor support:** Verify tile directly below spawn is WALL/PLATFORM (currently checks but only warns)
3. **Pit bordering:** Complete the stubbed pit validation — check left/right of pit tiles are WALL/PLATFORM/CRACKED/MAGICAL_WALL (not AIR)
4. **Property consistency:**
   - If `pushSpawn` property exists, verify grid has PUSH_SPAWN (S) at that coordinate
   - If `pushSlot` property exists, verify grid has AIR at that coordinate
   - If `glyphs` array has entries, verify grid has GLYPH (*) at those coordinates
5. **Door reachability:** DOOR_D tiles must have at least one adjacent AIR tile
6. **Unique tiles:** Verify exactly one GOLEM_SPAWN, exactly one DOOR_D or END_PORTAL

#### Task 1.4: Add flowId consistency check

**New function:** `check_flow_consistency(golem_path)`

- Parse `CHAMBER_FLOW` array from golem.html (L76): `['ch0','ch1','ch2','ch3','ch4']`
- Parse `CHAMBER_NAMES` array from golem.html (L75)
- Verify CHAMBER_FLOW length == CHAMBER_NAMES length
- For each chamber IIFE:
  - If it has a flowId, verify flowId is in CHAMBER_FLOW
  - If it lacks a flowId, report as "special chamber" (expected for test)
- Report any orphaned flowIds (in CHAMBER_FLOW but no matching chamber)
- Report any chambers without flowId that should have one

**CLI integration:** Add `--check-flow` flag that runs this check independently
or as part of the default diff mode.

#### Task 1.5: Add three-way diff capability

**Enhance `--diff-proposal` mode:**

Current: Compares proposal MD against data MD only.
Enhanced: Compares proposal against BOTH data MD AND golem.html JS.

```
python3 tools/chamber_diff.py --diff-proposal chamber-data.md proposal.md --against-js golem.html
```

- Shows proposal vs existing data (visual diff)
- Shows proposal vs JS code (validation that proposal matches code if already implemented)
- Reports chambers in proposal that don't exist in data or JS (new chambers)

#### Task 1.6: Verify fix with existing data

Run the fixed tool against current (unfixed) chamber-data.md:
```bash
python3 tools/chamber_diff.py --visual --strict
```
Expected: ~25 genuine mismatches (no false positives from handler bug).

---

### Phase 2: Clean chamber-data.md

**Files:** `chamber-data.md`
**Estimated effort:** 30-45 minutes
**Dependency:** Phase 1 complete (need working `--export-ascii`)

#### Task 2.1: Export clean ASCII grids from golem.html

```bash
python3 tools/chamber_diff.py --export-ascii chamber-data-clean.md
```

This generates a new file with:
- H2 headers for each chamber
- Properly framed ASCII grids (25x15, border format)
- NO annotation lines
- Grids guaranteed to match golem.html JS code exactly

#### Task 2.2: Replace chamber-data.md with clean version

Replace the content of `chamber-data.md` with the exported grids.
Keep the file header (lines 1-4: title, description, template reference).

**Before (current structure):**
```
## Chamber 0 — Awakening
[grid]
Spawn: ^ at (3,11) | Glyph 1 at (10,8) — Double Jump | ...
Diagonal staircase walls ascend from (12,12) up to (9,10). ...
```

**After (clean structure):**
```
## Chamber 0 — Awakening
[grid only]

## Chamber 1 — The Library
[grid only]
```

#### Task 2.3: Verify with diff

```bash
python3 tools/chamber_diff.py --strict
```
Expected: 0 mismatches, all validation passes.

---

### Phase 3: Establish ordered construction convention in golem.html

**Files:** `golem.html` (Section 2, lines 120-249), `chamber-template.md`
**Estimated effort:** 1-2 hours

#### Task 3.1: Document the 9-step convention in chamber-template.md

Add a new section to `chamber-template.md`:

```markdown
## Ordered Construction Convention (golem.html IIFEs)

Each chamber IIFE in `golem.html` Section 2 MUST follow this construction order:

| Step | Phase | Description | Comment prefix |
|------|-------|-------------|----------------|
| 1 | Boundaries | Ceiling (row 0), floor (rows 13-14), left wall (col 0) | `/* Step 1: Boundaries */` |
| 2 | Pits | Override floor tiles with PIT (~) where needed | `/* Step 2: Pits */` |
| 3 | Door/Portal | Place DOOR_D (v) or END_PORTAL (@) | `/* Step 3: Door/Portal */` |
| 4 | Interior walls | Solid interior barriers (#) and special walls (M) | `/* Step 4: Interior walls */` |
| 5 | Platforms | One-way platforms (=) | `/* Step 5: Platforms */` |
| 6 | Glyphs | Collectible knowledge glyphs (*) | `/* Step 6: Glyphs */` |
| 7 | Special tiles | PUSH_SPAWN (S), CRACKED (X), slot overrides (AIR) | `/* Step 7: Special tiles */` |
| 8 | Spawn | GOLEM_SPAWN (^) — always last tile assignment | `/* Step 8: Golem spawn */` |
| 9 | Push | chambers.push() with grid, glyphs, flowId, properties | (no comment needed) |

This order ensures:
- Boundaries are set first (lowest priority, can be overridden)
- Spawn is set last (highest priority, never accidentally overwritten)
- Each phase is visually separated by a comment for readability and diffability
```

#### Task 3.2: Reorder existing IIFEs in golem.html

Apply the convention to all 6 chambers. Current vs target order:

**Ch.0 (lines 121-133) — needs reordering:**
Current: boundaries -> pit direct -> staircase -> glyph -> spawn -> push
Target:
```js
// Chamber 0: Awakening — learn movement, get Glyph 1 (Double Jump)
(function(){
  const w=25,h=15,g=mkGrid(w,h);
  /* Step 1: Boundaries */
  for(let x=0;x<w;x++){g[14][x]=WALL;g[13][x]=WALL;g[0][x]=WALL;}
  for(let y=0;y<h;y++){g[y][0]=WALL;}
  for(let y=0;y<h-2;y++){g[y][w-1]=WALL;}
  /* Step 2: Pits */
  g[14][12]=PIT;g[14][13]=PIT;g[14][14]=PIT;
  g[13][12]=PIT;g[13][13]=PIT;g[13][14]=PIT;
  /* Step 3: Door/Portal */
  g[h-3][w-1]=DOOR_D;
  /* Step 4: Interior walls */
  g[12][6]=WALL;g[12][7]=WALL; g[11][7]=WALL;g[11][8]=WALL;
  g[10][8]=WALL;g[10][9]=WALL; g[9][9]=WALL;g[9][10]=WALL;
  /* Step 6: Glyphs */
  g[8][10]=GLYPH;
  /* Step 8: Golem spawn */
  g[11][3]=GOLEM_SPAWN;
  chambers.push({w,h,tiles:g,glyphs:[{x:10,y:8}],flowId:'ch0'});
})();
```

**Ch.1 (lines 136-150) — needs minor reordering:**
Current: boundaries -> door -> pits -> platforms -> glyph -> walls -> spawn -> push
Target: boundaries -> pits -> door -> walls -> platforms -> glyph -> spawn -> push

**Ch.2 (lines 153-166) — needs minor reordering:**
Current: boundaries -> door -> pits -> platforms -> magical wall -> top wall -> glyph -> spawn -> push
Target: boundaries -> pits -> door -> walls (magical + top) -> platforms -> glyph -> spawn -> push

**Ch.3 (lines 169-191) — needs significant reordering:**
Current: boundaries -> door -> floor override -> slot -> pushSpawn -> walls -> platforms -> glyph -> spawn -> push
Target: boundaries -> door -> walls -> slot (AIR) -> platforms -> glyph -> pushSpawn -> spawn -> push

**Ch.4 (lines 194-216) — needs reordering:**
Current: boundaries -> END_PORTAL -> CRACKED -> platforms -> spawn -> push
Target: boundaries -> END_PORTAL -> CRACKED (Step 7) -> platforms -> spawn -> push

**Ch.T (lines 219-249) — needs significant reordering:**
Current: boundaries (reversed: ceiling/floor before sides) -> door -> pushSpawn -> wall barrier -> platform column -> platform rows -> wall divider -> platform column (rows 10-12) -> floor row -> spawn -> push
Target: boundaries (standard order) -> door -> walls -> platforms -> pushSpawn -> spawn -> push

#### Task 3.3: Verify game still works

After reordering, the game behavior must be identical since we only rearrange
statements within the same IIFE scope. Verify by:
1. Running `python3 tools/chamber_diff.py --strict` — still 0 mismatches
2. Opening `golem.html` in browser — game loads, all chambers work

---

### Phase 4: Update chamber-template.md Tile Legend

**Files:** `chamber-template.md`
**Estimated effort:** 15-30 minutes

#### Task 4.1: Verify Tile Legend matches golem.html constants

Current legend in `chamber-template.md` (lines 6-20):

| Char | Constant | Value | Description |
|------|----------|-------|-------------|
| . | AIR | 0 | Empty space |
| # | WALL | 1 | Solid wall |
| ~ | PIT | 2 | Death void |
| ^ | GOLEM_SPAWN | 3 | Player spawn marker |
| v | DOOR_D | 4 | Down-side exit door |
| * | GLYPH | 5 | Collectible glyph |
| X | CRACKED | 7 | Breakable wall |
| = | PLATFORM | 8 | One-way platform |
| @ | END_PORTAL | 9 | Final portal |
| M | MAGICAL_WALL | 10 | Destructible barrier |
| S | PUSH_SPAWN | 11 | Push block spawn |

golem.html line 26: `const AIR=0, WALL=1, PIT=2, GOLEM_SPAWN=3, DOOR_D=4, GLYPH=5, CRACKED=7, PLATFORM=8, END_PORTAL=9, MAGICAL_WALL=10, PUSH_SPAWN=11;`

**Verification:** Values match exactly. The gap at value 6 is intentional (no tile type).

**Minor corrections needed:**
- DOOR_D description: "Down-side exit door (glyph-locked). Test chamber uses `^` at row 2." — the "Test chamber uses `^`" part is incorrect; the test chamber uses `v` (DOOR_D) at g[2][12]. Remove this misleading note.
- GOLEM_SPAWN description: "invisible, determines golem position" — correct, but should clarify it's the player spawn position (the golem IS the player character).

**Updated descriptions:**
```
| ^ | GOLEM_SPAWN | 3 | Player spawn position (invisible at runtime) |
| v | DOOR_D | 4 | Exit door — follows CHAMBER_FLOW to next chamber |
```

#### Task 4.2: Add construction convention section

Add the 9-step convention from Task 3.1 as a permanent reference in `chamber-template.md`.

#### Task 4.3: Update format spec to enforce no annotations

Add explicit rule to the format section:
```markdown
## Rules

- Grid-only data in `chamber-data.md` — no annotation lines after code blocks.
- All interpretive notes belong in `chamber-template.md` (format guide) or `docs/`.
- Each chamber section contains exactly: H2 header, blank line, fenced code block with grid.
```

---

### Phase 5: Establish clear diff workflows

**Files:** `chamber-template.md` (workflow documentation), `AGENTS.md` (governance)
**Estimated effort:** 30 minutes

#### Task 5.1: Document diff workflows in chamber-template.md

Add a "Diff Workflows" section:

```markdown
## Diff Workflows

### Workflow A: Verify chamber-data.md matches golem.html (production check)

Run after any changes to golem.html Section 2:

    python3 tools/chamber_diff.py --strict

Expected: 0 mismatches. If mismatches found, either:
  - Update chamber-data.md: `python3 tools/chamber_diff.py --export-ascii chamber-data.md`
  - Fix golem.html if the MD is correct

### Workflow B: Validate a new chamber proposal

Before implementing a proposal:

    python3 tools/chamber_diff.py --validate proposal.md --strict

Expected: No validation errors. This checks grid structure, spawn, pit borders, etc.

### Workflow C: Compare proposal against existing data

After creating a proposal, see what changed:

    python3 tools/chamber_diff.py --diff-proposal chamber-data.md proposal.md

This shows tile-by-tile differences between proposal and current data.

### Workflow D: Three-way check (proposal vs data vs code)

After implementing a proposal in golem.html:

    python3 tools/chamber_diff.py --diff-proposal chamber-data.md proposal.md --against-js golem.html
    python3 tools/chamber_diff.py --strict

Expected: Both show 0 mismatches. The proposal was implemented correctly.

### Workflow E: Regenerate chamber-data.md from golem.html

When golem.html changes and chamber-data.md needs updating:

    python3 tools/chamber_diff.py --export-ascii chamber-data.md
```

#### Task 5.2: Add chamber quality gates to AGENTS.md

Update AGENTS.md quality gates section to reference the diff tool:

```markdown
## Quality gates (updated)

6. For chamber changes: run `python3 tools/chamber_diff.py --strict` — must show 0 mismatches.
7. For new chambers: validate with `python3 tools/chamber_diff.py --validate proposal.md --strict`.
8. Chamber-data.md must never contain annotation lines — grids only.
```

---

## Detailed Task Dependencies

```
Phase 1 (Fix chamber_diff.py)
  ├── Task 1.1: Fix handler ordering (CRITICAL — all other tasks depend on this)
  ├── Task 1.2: Add --export-ascii
  ├── Task 1.3: Add --strict validation
  ├── Task 1.4: Add flowId consistency check
  ├── Task 1.5: Add three-way diff
  └── Task 1.6: Verify fix (run against current broken data, expect ~25 mismatches)

Phase 2 (Clean chamber-data.md)
  ├── Task 2.1: Export clean ASCII (depends on Task 1.2)
  ├── Task 2.2: Replace chamber-data.md
  └── Task 2.3: Verify with diff (depends on Tasks 1.1, 1.3)

Phase 3 (Ordered construction convention)
  ├── Task 3.1: Document convention in chamber-template.md
  ├── Task 3.2: Reorder all 6 IIFEs in golem.html
  └── Task 3.3: Verify (depends on Phase 1 tool)

Phase 4 (Update Tile Legend)
  ├── Task 4.1: Verify and fix Tile Legend descriptions
  ├── Task 4.2: Add construction convention section
  └── Task 4.3: Add no-annotations rule

Phase 5 (Diff workflows)
  ├── Task 5.1: Document workflows in chamber-template.md
  └── Task 5.2: Update AGENTS.md quality gates
```

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Handler reorder breaks parsing of some IIFE pattern | MEDIUM | Test against all 6 chambers after fix; compare with research report's known-good values |
| Reordering IIFEs in golem.html changes behavior | LOW | Only rearranging independent assignments; verify with diff tool + browser test |
| Export misses edge case (e.g., multi-line push statement in Ch.3/Ch.T) | MEDIUM | Manual review of exported output for Ch.3 and Ch.T |
| Strict validation false positives (e.g., pit with AIR neighbor by design) | LOW | Tune validation rules based on actual chamber layouts |
| CHAMBER_NAMES parsing edge case | LOW | Simple regex on single line; test with current data |

---

## Deliverables

Upon completion, the following will be true:

1. `chamber-data.md` — Clean grids only, 0 mismatches with `golem.html`, no annotations
2. `golem.html` Section 2 — All 6 IIFEs follow the 9-step ordered construction convention
3. `tools/chamber_diff.py` — Fixed handler ordering, plus `--export-ascii`, `--strict`, `--check-flow`
4. `chamber-template.md` — Updated Tile Legend, construction convention documented, diff workflows documented
5. `chamber-proposal.md` — No changes needed (already well-structured)
6. `AGENTS.md` — Updated quality gates referencing diff tool

---

## Acceptance Criteria

- [ ] `python3 tools/chamber_diff.py --strict` returns 0 mismatches and 0 errors
- [ ] `python3 tools/chamber_diff.py --export-ascii` produces grids matching golem.html exactly
- [ ] `python3 tools/chamber_diff.py --check-flow` reports all flowIds consistent
- [ ] chamber-data.md has no annotation lines (only H2 headers and fenced code blocks)
- [ ] All 6 golem.html IIFEs have `/* Step N: ... */` comment markers
- [ ] chamber-template.md Tile Legend matches golem.html constants exactly
- [ ] Game loads and runs in browser without errors after IIFE reordering
- [ ] Diff workflows documented and usable from chamber-template.md

---

## Estimated Total Effort

| Phase | Estimated Time |
|-------|---------------|
| Phase 1: Fix/enhance chamber_diff.py | 2-3 hours |
| Phase 2: Clean chamber-data.md | 30-45 minutes |
| Phase 3: Ordered construction convention | 1-2 hours |
| Phase 4: Update Tile Legend | 15-30 minutes |
| Phase 5: Diff workflows | 30 minutes |
| **Total** | **~4-6 hours** |

---

*Plan generated by Hermes Agent planner phase. Ready for executor-agent to begin Phase 1.*
