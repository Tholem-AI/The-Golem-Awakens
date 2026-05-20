# Chamber Proposal Template

Copy this file for each new chamber proposal. Fill in all sections before
submitting for review.

---

## Chamber Overview

| Field | Value |
|-------|-------|
| FlowId | `chN` |
| Name | Chamber Name |
| Flow position | Nth in CHAMBER_FLOW (index N) |
| Grants | Ability/Glyph description, or N/A |
| Requires | Previous abilities needed to complete |
| Grid | 25x15 (standard) |

---

## Design

### Flow Description

Describe the intended player path from spawn to exit. Reference tile
coordinates and key decision points.

### Mechanics Used

Check which abilities/mechanics the chamber uses or teaches:

- [ ] Walking / Jumping
- [ ] Double Jump
- [ ] Dash (charge + release)
- [ ] Push Blocks
- [ ] Break Cracked
- [ ] One-way Platforms (drop-down with ArrowDown/KeyS)

### ASCII Grid

Follow the format in `chamber-template.md`. Exactly 25 columns x 15 rows.

```
+-----------------------------+
| Ch.N [Name]                 |
+-----------------------------+
|00 ######################### |
|01 #.......................# |
... (15 rows total) ...
|14 ######################### |
+-----------------------------+
```

### Key Coordinates

- Spawn (^): (x, y)
- Glyph (*): (x, y) — or N/A if no glyph
- Door (v): (x, y) — or N/A if END_PORTAL
- Push block (S): (x, y) — or N/A
- End portal (@): (x, y) — or N/A
- Platforms (=): row, col ranges
- Pits (~): row, col ranges

---

## Verification Checklist

- [ ] Grid is exactly 25 columns x 15 rows
- [ ] Exactly one GOLEM_SPAWN (^) tile
- [ ] Spawn has solid floor (#) directly beneath it
- [ ] Glyph is reachable with current abilities
- [ ] Exit door/portal is reachable after objectives
- [ ] Pits (~) bordered by solid tiles on all sides
- [ ] Push block spawns (S) have empty space ahead for movement
- [ ] flowId added to CHAMBER_FLOW at correct position
- [ ] CHAMBER_NAMES has entry at matching index
- [ ] Tested in browser with `_testMode = true`
- [ ] All DOOR_D tiles are reachable from walkable space

---

## Implementation Notes

### Adding to the game

1. Choose a `flowId` (e.g. `ch5`) and insert it into `CHAMBER_FLOW` at the
   desired position.
2. Add a `CHAMBER_NAMES` entry at the matching index.
3. Create the chamber IIFE in `golem.html` Section 2 with the flowId:
   ```js
   chambers.push({w,h,tiles:g,glyphs:[...],flowId:'ch5'});
   ```
4. The IIFE can be placed anywhere in Section 2 — the flow system handles ordering.

### Changes to existing chambers

List any changes to existing chambers required by this proposal.
If none, write "None — no existing chambers modified."

### Risk assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Example: Unreachable glyph | Low/Med/High | Add alternative path |

---

## References

- `chamber-template.md` — format spec and conversion guide
- `chamber-data.md` — existing chamber grids
- `golem.html` Section 2 — chamber IIFE examples
- `docs/Project-Constraints.md` — stack and design constraints
