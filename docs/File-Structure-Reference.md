# File Structure Reference

## GOLEM_GAME/

```
GOLEM_GAME/
  AGENTS.md                  # Project-scoped governance (Tholem Hermes Kit)
 golem.html                # Single-file HTML5 game (~1722 lines, 11 sections + animation system, ~64 KB)
  README.md                 # Project overview, controls, abilities, chambers
  ROADMAP.md                # Active development checkpoints
  chamber-data.md           # Chamber grid exports extracted from golem.html (grid-only, no annotations)
  chamber-proposal.md       # Reusable template for new chamber proposals with diff-guided workflow
  chamber-template.md       # Tile legend, coordinate system, chamber flow, ordered construction convention, diff workflows (A-F), conversion spec
 tools/
    chamber_diff.py         # Diff/validation tool (6 modes: diff, validate, strict, export-ascii, diff-proposal, check-flow)
 docs/
    File-Structure-Reference.md   # This file
    Project-Constraints.md        # Inferred stack and constraints
    Project-Reference.md          # Architecture, physics tuning rationale, push-block design
```

## Key files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project governance: safety, quality, lifecycle, constraints |
|| `golem.html` | Complete game source. Single-file HTML5 platformer. ~1722 lines. 11-section structure: Setup/Constants, Chamber Data (Section 2 uses 9-step ordered construction convention with /* Step N: */ comments, CHAMBER_FLOW flow system), Entities, Input, Tile Helpers/Collision (pushBlockHit, isRiding, resolveBlockX/Y, activePushBlocks, checkPushBlockCrush), Push Block System (3-phase orchestrator, block-vs-block AABB, rider collision, crush death), Particle System, Game Flow (flow-based DOOR_D), Update, Render, Init/Game Loop. Death/respawn animation system (state machine: idle->dying->respawning->idle). |
| `README.md` | Project overview, controls, abilities, chambers |
| `ROADMAP.md` | Active development checkpoints |
| `chamber-data.md` | ASCII grid exports of all 6 chambers — grid-only, no annotations. Verified 0 mismatches against golem.html. |
|| `chamber-proposal.md` | Reusable template for new chamber proposals; used with chamber_diff.py diff-proposal workflow |
|| `chamber-template.md` | Tile legend, coordinate system, chamber flow system, ordered construction convention (9-step), diff workflows (A-F), conversion spec |
|| `tools/chamber_diff.py` | Diff/validation CLI tool with 6 modes: --diff, --validate, --strict, --export-ascii, --diff-proposal, --check-flow |
|| `docs/Project-Constraints.md` | Stack, runtime constraints, design constraints, assumptions. |
| `docs/Project-Reference.md` | Architecture overview, physics tuning rationale, push-block system design, tile system. |
