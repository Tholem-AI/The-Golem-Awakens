# Chamber Flow System — Execution Plan

## Objective

Replace implicit array-index-based chamber progression with an explicit flow
system. Chambers are ordered by a `CHAMBER_FLOW` array and per-chamber `flowId`
property instead of relying on position in `chambers[]`. This enables inserting,
replacing, or reordering levels without rewriting game flow logic.

## Scope

Minimal implementation — only what's required to make the flow system work:
- Add `flowId` to each chamber object and `CHAMBER_FLOW` ordering array
- Rewrite door/transition logic to follow flow instead of index+1
- Rewrite test chamber detection to not depend on array position
- Update HUD ending condition
- Update Chamber T grid to the new design
- Update all documentation

**Out of scope:** New abilities, new tile types, new UI elements beyond HUD
chamber label change.

---

## Prerequisites (Research — Done)

| Finding | Source | Line(s) |
|---------|--------|---------|
| `checkDoors()` — DOOR_D → `transition(ch+1)` | golem.html | 606-633 |
| Test check in `checkDoors()` — `ch === chambers.length - 1` | golem.html | 614 |
| Test entry in `update()` — `ch === chambers.length - 1` | golem.html | 676-693 |
| HUD chamber name — `if(ch<4)` branch | golem.html | 1378-1384 |
| `CHAMBER_NAMES` — 5 entries (indices 0-4) | golem.html | 75 |
| 6 `chambers.push()` calls (indices 0-4 main, 5 test) | golem.html | 119-232 |
| Init — `collectedGlyphs = new Array(chambers.length)` | golem.html | 1431 |
| `collectedGlyphs` array sized at init, not constant | golem.html | 258, 1431 |

---

## Slices

### Slice 1 — Add `flowId` to Chambers + `CHAMBER_FLOW` Array

**Goal:** Introduce the flow identifiers without breaking anything. This is
purely additive — the game still works by array index after this slice.

**Changes in `golem.html`:**

1. After `CHAMBER_NAMES` (line 75), add the flow array:
   ```js
   const CHAMBER_FLOW = ['ch0','ch1','ch2','ch3','ch4'];
   ```

2. Add `flowId` to each `chambers.push()` call in Section 2 (Chamber Data):

   | Chamber | Current push | Updated push |
   |---------|-------------|--------------|
   | Ch.0 (line 131) | `{w,h,tiles:g,glyphs:[...]}` | `{w,h,tiles:g,glyphs:[...],flowId:'ch0'}` |
   | Ch.1 (line 148) | `{w,h,tiles:g,glyphs:[...]}` | `{w,h,tiles:g,glyphs:[...],flowId:'ch1'}` |
   | Ch.2 (line 164) | `{w,h,tiles:g,glyphs:[...]}` | `{w,h,tiles:g,glyphs:[...],flowId:'ch2'}` |
   | Ch.3 (line 188) | `{w,h,tiles:g,glyphs:[...],pushSpawn:...,pushSlot:...}` | `{w,h,tiles:g,glyphs:[...],pushSpawn:...,pushSlot:...,flowId:'ch3'}` |
   | Ch.4 (line 214) | `{w,h,tiles:g,glyphs:[]}` | `{w,h,tiles:g,glyphs:[],flowId:'ch4'}` |
   | Ch.T (line 230) | `{w,h,tiles:g,glyphs:[],pushSpawn:...}` | **No change** — test chamber has no flowId (undefined) |

**Impact:** Zero runtime behavior change. Test chamber intentionally has no
flowId — this is the discriminator used in later slices.

**Validation gate:**
- [ ] JS syntax check: `node -c golem.html` passes
- [ ] Game loads and plays Chambers 0-4 unchanged
- [ ] `chambers[i].flowId` matches expected for i=0..4; `chambers[5].flowId` is undefined

---

### Slice 2 — Rewrite `checkDoors()` to Follow Flow

**Goal:** Replace `transition(ch+1)` with flow-based progression.

**Changes in `golem.html` (Section 8, line 606-633):**

Replace the entire `checkDoors()` function:

```js
function checkDoors(){
  const ch=P.chamber, c=chambers[ch];
  const px=P.x+P.w/2, py=P.y+P.h/2;
  const gx=Math.floor(px/T), gy=Math.floor(py/T);
  for(let dy=-1;dy<=1;dy++) for(let dx=-1;dx<=1;dx++){
    const t=_getTile(gx+dx,gy+dy);
    if(t===DOOR_D){
      /* Return from test chamber (no flowId) */
      if(!c.flowId && testChamberSrc >= 0){
        transition(testChamberSrc);
        return;
      }
      /* Follow flow for main chambers */
      if(collectedGlyphs[ch]){
        const fi = CHAMBER_FLOW.indexOf(c.flowId);
        if(fi >= 0 && fi < CHAMBER_FLOW.length - 1){
          /* Find chamber index by flowId of next in flow */
          const nextFlow = CHAMBER_FLOW[fi+1];
          for(let i=0;i<chambers.length;i++){
            if(chambers[i].flowId === nextFlow){ transition(i); return; }
          }
        }
      } else {
        if(portalLockMsg<=0){
          showMessage("The seal demands Knowledge...", 70);
          portalLockMsg = 45;
        }
      }
      return;
    }
    if(t===END_PORTAL){
      transitionEnding();
      return;
    }
  }
}
```

**Key changes:**
- Test chamber exit: `!c.flowId` instead of `ch === chambers.length - 1`
- DOOR_D progression: find current chamber's position in `CHAMBER_FLOW`,
  advance to next flowId, look up its array index
- All other logic (glyph check, portal lock message) preserved unchanged

**Validation gate:**
- [ ] JS syntax check passes
- [ ] Chambers 0→1→2→3→4 progression works via DOOR_D
- [ ] Chamber 4 has no DOOR_D (uses END_PORTAL) — no regression
- [ ] Test chamber DOOR_D returns to source chamber
- [ ] Locked door message still shows when glyph not collected

---

### Slice 3 — Rewrite Test Chamber Entry/Exit

**Goal:** Replace fragile `chambers.length - 1` check with `!c.flowId`.

**Changes in `golem.html` (Section 9, line 676-693):**

Replace the T-key handler:

```js
  if(fresh('KeyT')){
    const c = chambers[P.chamber];
    if(!c.flowId && testChamberSrc >= 0){
      /* Return from test chamber */
      transition(testChamberSrc);
      showMessage("Back to chamber " + testChamberSrc + ".", 60);
    } else {
      /* Enter test chamber */
      testChamberSrc = P.chamber;
      glyphsCollected = 4;
      P.maxJumps = 2;
      P.canDash = true;
      P.canPush = true;
      P.canBreak = true;
      /* Find test chamber by absence of flowId */
      for(let i=0;i<chambers.length;i++){
        if(!chambers[i].flowId){ transition(i); break; }
      }
      showMessage("Test chamber — all abilities unlocked.", 90);
    }
    return;
  }
```

**Key changes:**
- Test detection: `!c.flowId` instead of `P.chamber === chambers.length - 1`
- Test entry: loop through chambers to find the one without flowId
- All ability-unlocking logic preserved unchanged

**Validation gate:**
- [ ] JS syntax check passes
- [ ] Pressing T from any main chamber enters test chamber
- [ ] Pressing T from test chamber returns to source
- [ ] All abilities unlocked in test chamber
- [ ] `testChamberSrc` correctly remembers source chamber

---

### Slice 4 — Update HUD Ending Condition

**Goal:** Show chamber name using flow position instead of array index.

**Changes in `golem.html` (Section 10, line 1377-1384):**

Replace the chamber name display logic:

```js
  X.fillStyle='#665a4a'; X.font='12px monospace'; X.textAlign='center';
  const c = chambers[ch];
  if(c.flowId){
    const fi = CHAMBER_FLOW.indexOf(c.flowId);
    if(fi >= 0 && fi < CHAMBER_FLOW.length - 1){
      /* Main chambers with portal (not last in flow) */
      const locked = !glyphCollected;
      const portalStatus = locked ? ' \u{1F512} Portal Sealed' : ' Portal Open \u2714';
      X.fillText(CHAMBER_NAMES[fi] + portalStatus, W/2, H-10);
    } else if(fi === CHAMBER_FLOW.length - 1){
      /* Last chamber in flow — The Ibis Chamber */
      X.fillText(CHAMBER_NAMES[fi] + ' \u2605 Path of Wisdom', W/2, H-10);
    }
  } else {
    /* Test chamber (no flowId) */
    X.fillText('Ch.T Test Chamber', W/2, H-10);
  }
```

**Key changes:**
- Main chamber check: `c.flowId` exists (not `ch < 4`)
- Portal status: based on flow position (`fi < CHAMBER_FLOW.length - 1`)
- Last chamber: `fi === CHAMBER_FLOW.length - 1` (not `ch === 4`)
- Test chamber: explicit label when no flowId

**Validation gate:**
- [ ] JS syntax check passes
- [ ] HUD shows "Awakening [Portal status]" through "The Ibis Chamber Path of Wisdom"
- [ ] HUD shows "Ch.T Test Chamber" in test mode
- [ ] Portal locked/open indicator correct per chamber

---

### Slice 5 — Update Chamber T Grid to New Design

**Goal:** Give the test chamber a more comprehensive layout that exercises
all abilities and tile types.

**Changes in `golem.html` (Section 2, test chamber IIFE at line 217-232):**

Replace the test chamber IIFE with:

```js
// Ch.T: Test chamber — full ability sandbox, entered by pressing KeyT
(function(){
  const w=25,h=15,g=mkGrid(w,h);
  for(let x=0;x<w;x++){g[0][x]=WALL;g[14][x]=WALL;}
  for(let y=0;y<h;y++){g[y][0]=WALL;g[y][w-1]=WALL;}
  /* Floor at row 12 */
  for(let x=1;x<w-1;x++) g[12][x]=WALL;
  /* Pit for death/respawn test (cols 4-6, row 13) */
  g[13][4]=PIT;g[13][5]=PIT;g[13][6]=PIT;
  g[12][4]=PIT;g[12][5]=PIT;g[12][6]=PIT;
  /* Wall section for push block test (col 20, rows 9-11) */
  for(let y=9;y<=11;y++) g[y][20]=WALL;
  /* CRACKED wall for break test (col 15, rows 8-11) */
  for(let y=8;y<=11;y++) g[y][15]=CRACKED;
  /* MAGICAL_WALL for dash test (col 7, rows 4-8) */
  for(let y=4;y<=8;y++) g[y][7]=MAGICAL_WALL;
  /* Platform for jump/dash test */
  for(let x=3;x<6;x++) g[9][x]=PLATFORM;
  for(let x=9;x<12;x++) g[7][x]=PLATFORM;
  /* Push block spawn */
  g[11][10]=PUSH_SPAWN;
  /* Spawn position */
  g[10][2]=GOLEM_SPAWN;
  /* Test exit door */
  g[1][12]=DOOR_D;
  chambers.push({w,h,tiles:g,glyphs:[],
    pushSpawn:{x:10,y:11}});
})();
```

**Key changes:**
- Wider pit at cols 4-6, rows 12-13 (2 rows deep)
- CRACKED wall section at col 15 for break testing
- MAGICAL_WALL at col 7 for dash-through testing
- Platform sequence for jump testing
- DOOR_D at top center for testing return exit
- Spawn moved to (2,10) for better entry positioning

**Validation gate:**
- [ ] JS syntax check passes
- [ ] Test chamber loads without errors
- [ ] All tile types present: WALL, PIT, CRACKED, MAGICAL_WALL, PLATFORM,
  GOLEM_SPAWN, PUSH_SPAWN, DOOR_D
- [ ] Push block spawns and is pushable
- [ ] DOOR_D at top returns to source chamber
- [ ] Pit causes death and respawn at spawn point

---

### Slice 6 — Update `chamber-template.md` with Flow System Documentation

**Goal:** Document the flow system in the chamber template for future
contributors.

**Changes in `chamber-template.md`:**

Add a new section after "## Tile Legend":

```markdown
## Chamber Flow System

Chambers are ordered by the `CHAMBER_FLOW` array (defined after
`CHAMBER_NAMES` in Section 1), not by position in the `chambers[]` array.

### How it works

1. Each main chamber has a `flowId` property: `'ch0'`, `'ch1'`, etc.
2. `CHAMBER_FLOW = ['ch0','ch1','ch2','ch3','ch4']` defines the progression order.
3. `checkDoors()` finds the current chamber's position in `CHAMBER_FLOW` and
   transitions to the next flowId.
4. Chambers without a `flowId` (e.g. the test chamber) are not part of the flow.
   They are identified by `!c.flowId`.

### Adding a new main chamber

1. Choose a `flowId` (e.g. `'ch5'`) and insert it into `CHAMBER_FLOW` at the
   desired position.
2. Add a `CHAMBER_NAMES` entry at the matching index.
3. Create the chamber IIFE with `flowId:'ch5'` in the push object:
   ```js
   chambers.push({w,h,tiles:g,glyphs:[...],flowId:'ch5'});
   ```
4. The chamber IIFE can be placed anywhere in Section 2 — the flow system
   handles ordering.

### Adding a special chamber (test, bonus, secret)

1. Do NOT add a `flowId` — leave it out of the push object entirely.
2. The chamber is identified by absence of flowId (`!c.flowId`).
3. Add an entry to `CHAMBER_NAMES` only if referenced by name in the HUD.
4. Place the IIFE anywhere in Section 2.

### Important rules

- Every main chamber MUST have a unique `flowId` present in `CHAMBER_FLOW`.
- `CHAMBER_FLOW` length must match `CHAMBER_NAMES` length.
- The test chamber MUST NOT have a `flowId` — it is used as the discriminator.
- `collectedGlyphs` is sized to `chambers.length` at init, so it works with
  any number of chambers.
```

Update the "Converting ASCII Grid back to JavaScript" section to show the
flowId in the push call:

```js
lines.append(f'  chambers.push({{w,h,tiles:g,glyphs:[...],flowId:\x27chN\x27}});')
```

**Validation gate:**
- [ ] Document reads clearly and covers all flow system concepts
- [ ] Examples match actual code patterns in golem.html
- [ ] Adding/removing chamber instructions are accurate

---

### Slice 7 — Replace `chamber-proposal.md` with Clean Template

**Goal:** Replace the chamber-specific improvement proposals with a reusable
template for future chamber proposals.

**Changes to `chamber-proposal.md`:**

Replace the entire file with:

```markdown
# Chamber Proposal Template

Copy this file for each new chamber proposal. Fill in all sections.

---

## Chamber Overview

| Field | Value |
|-------|-------|
| FlowId | `chN` |
| Name | Chamber Name |
| Flow position | Nth in CHAMBER_FLOW (index N) |
| Grants | Ability/Glyph description |
| Requires | Previous abilities needed |
| Grid | 25x15 (standard) |

---

## Design

### Flow Description

Describe the player path from spawn to exit. Reference tile coordinates.

### Mechanics Used

List which abilities/mechanics the chamber uses and teaches:
- [ ] Walking / Jumping
- [ ] Double Jump
- [ ] Dash
- [ ] Push Blocks
- [ ] Break Cracked
- [ ] One-way Platforms (down)

### ASCII Grid

```
+-----------------------------+
| Ch.N [Name]                 |
+-----------------------------+
|00 ######################### |
|01 #.......................# |
... (15 rows total) ...
+-----------------------------+
```

### Key Coordinates

- Spawn (^): (x, y)
- Glyph (*): (x, y) — or N/A if no glyph
- Door (v): (x, y) — or N/A if END_PORTAL
- Push block (S): (x, y) — or N/A
- End portal (@): (x, y) — or N/A

---

## Verification Checklist

- [ ] Grid is exactly 25 columns x 15 rows
- [ ] Exactly one GOLEM_SPAWN (^) tile
- [ ] Spawn has solid floor (#) directly beneath it
- [ ] Glyph is reachable with current abilities
- [ ] Exit door/portal is reachable after objectives
- [ ] Pits (~) bordered by solid tiles
- [ ] Push block spawns (S) have empty space ahead
- [ ] flowId added to CHAMBER_FLOW at correct position
- [ ] CHAMBER_NAMES has entry at matching index
- [ ] Tested in browser with _testMode = true

---

## Implementation Notes

### Changes to existing chambers

List any changes to existing chambers required by this proposal.
If none, write "None — no existing chambers modified."

### Risk assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Example: Unreachable glyph | Low/med/high | Add alternative path |

---

## References

- `chamber-template.md` — format spec and conversion guide
- `chamber-data.md` — existing chamber grids
- `golem.html` Section 2 — chamber IIFE examples
- `docs/Project-Constraints.md` — stack and design constraints
```

**Validation gate:**
- [ ] Template is clean, well-structured, and reusable
- [ ] Covers all fields needed for a complete chamber proposal
- [ ] Verification checklist is comprehensive
- [ ] References point to correct files

---

### Slice 8 — Update All Documentation

**Goal:** Update ROADMAP.md, File-Structure-Reference.md, Project-Constraints.md,
and README.md to reflect the flow system.

**8a. ROADMAP.md:**

Add new completed section after "Death & Respawn Animations":

```markdown
### Chamber Flow System (May 2026)
- [x] CHAMBER_FLOW array and flowId properties on chambers
- [x] checkDoors() rewritten to follow flow instead of array index+1
- [x] Test chamber entry/exit rewritten to use !c.flowId discriminator
- [x] HUD chamber name display updated to use flow position
- [x] Chamber T grid updated with comprehensive test layout
- [x] chamber-template.md updated with flow system documentation
- [x] chamber-proposal.md replaced with clean reusable template
- [x] All documentation updated (ROADMAP, File-Structure-Reference, Project-Constraints, README)
- [x] Validation: JS syntax OK, Chambers 0-4 progression works, test chamber works
```

Update status table: add row `| Chamber flow system | Complete | CHAMBER_FLOW in golem.html, all chambers have flowId |`

**8b. File-Structure-Reference.md:**

Update `chamber-proposal.md` description:
`# Improvement proposals` → `# Reusable template for new chamber proposals`

**8c. Project-Constraints.md:**

Update "Design Constraints" table:

| Constraint | Detail | Source |
|-----------|--------|-------|
| Chamber flow system | Chambers ordered by CHAMBER_FLOW array, not array index. flowId property on each chamber. Test chamber has no flowId. | golem.html Section 1 |
| 5 canonical chambers + 1 test | Progressive difficulty chain via flow. Test chamber accessible by pressing T. | golem.html Section 2 |

Remove the old "5 canonical chambers + 1 test" row since it's now superseded.

**8d. README.md:**

Add note under Chambers section:

```markdown
## Chambers

Chambers are ordered by a flow system (`CHAMBER_FLOW`), not array position.
This allows adding or reordering levels without changing game logic.

1. **Awakening** — Tutorial. Learn movement, collect Glyph 1.
2. **The Library** — Platforming with double jump. Collect Glyph 2.
3. **The Hall of Echoes** — Dash through magical walls. Collect Glyph 3.
4. **The Weight of Wisdom** — Push block puzzle. Collect Glyph 4.
5. **The Ibis Chamber** — Break cracked walls to reach the final portal.
```

Update file list to reflect `chamber-proposal.md` change:
`# Proposed chamber improvements` → `# Reusable template for chamber proposals`

**8e. chamber-data.md:**

Add `flowId: 'chN'` annotation to each chamber header:
- Ch.0: `Spawn: ^ at (3,11) | flowId: ch0 | Glyph 1 at (10,8)...`
- Ch.1: `Spawn: ^ at (3,11) | flowId: ch1 | Glyph 2 at (17,6)...`
- Ch.2: `Spawn: ^ at (3,11) | flowId: ch2 | ...`
- Ch.3: `Spawn: ^ at (3,10) | flowId: ch3 | ...`
- Ch.4: `Spawn: ^ at (2,11) | flowId: ch4 | ...`
- Ch.T: `Spawn: ^ at (12,10) | flowId: (none) | ...`

Update Chamber T grid to match new design from Slice 5.

**Validation gate:**
- [ ] All docs reference flow system consistently
- [ ] No contradictory information between docs
- [ ] ROADMAP status table updated
- [ ] File descriptions accurate
- [ ] chamber-data.md annotations match actual code

---

## Innovate Checkpoint (Before Execution)

**Review before implementing:**

1. **Completeness check:** Does every reference to `ch+1` or
   `chambers.length-1` get addressed?
   - `checkDoors()` DOOR_D transition → Slice 2 ✓
   - `checkDoors()` test check → Slice 2 ✓
   - `update()` T-key handler → Slice 3 ✓
   - HUD chamber display → Slice 4 ✓
   - No other references found.

2. **Backward compatibility:** The flow system is transparent to existing
   gameplay. Chambers 0-4 progress identically. Only the mechanism changes.

3. **Forward compatibility:** New chambers can be inserted at any flow
   position without touching game flow logic. Test chamber stays opt-out via
   absence of flowId.

4. **Minimalism check:** Only 4 files modified for code (golem.html for 4
   slices), 5 files for docs. No new functions added to the global scope
   beyond CHAMBER_FLOW constant.

---

## Execution Order

1. Slice 1 (additive, zero risk)
2. Slice 2 (core logic change, depends on Slice 1)
3. Slice 3 (test logic, depends on Slice 1)
4. Slice 4 (display only, depends on Slice 1)
5. Slice 5 (test chamber grid, independent)
6. Slice 6 (docs — chamber-template.md)
7. Slice 7 (docs — replace chamber-proposal.md)
8. Slice 8 (docs — ROADMAP, File-Structure-Reference, Project-Constraints,
   README, chamber-data.md)

Each slice has a validation gate that must pass before proceeding to the next.
If any gate fails, stop and fix before continuing.
