# File Structure Reference

## GOLEM_GAME/

```
GOLEM_GAME/
  AGENTS.md                  # Project-scoped governance (Tholem Hermes Kit)
  golem.html                # Single-file HTML5 game (~1462 lines, 11 sections + animation system, ~51 KB)
  README.md                 # Project overview, controls, abilities, chambers
  ROADMAP.md                # Active development checkpoints
  chamber-data.md           # Chamber layouts extracted from golem.html (5 chambers + test)
  chamber-proposal.md       # Improvement proposals for Chambers 0 and 4
  chamber-template.md       # Tile legend, format spec, conversion instructions
 docs/
    File-Structure-Reference.md   # This file
    Project-Constraints.md        # Inferred stack and constraints
    Project-Reference.md          # Architecture, physics tuning rationale, push-block design
```

## Key files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project governance: safety, quality, lifecycle, constraints |
| `golem.html` | Complete game source. Single-file HTML5 platformer. 11-section structure: Setup/Constants, Chamber Data, Entities, Input, Tile Helpers/Collision, Push Block System, Particle System, Game Flow, Update, Render, Init/Game Loop. Death/respawn animation system (state machine: idle->dying->respawning->idle, easing functions, renderDeathRespawnAnimation). |
| `README.md` | Project overview, controls, abilities, chambers |
| `ROADMAP.md` | Active development checkpoints |
| `chamber-data.md` | ASCII grid exports of all 6 chambers with annotations. |
| `chamber-proposal.md` | Proposed chamber restructures for Ch.0 and Ch.4. |
| `chamber-template.md` | Tile legend, coordinate system, extraction/conversion workflow. |
| `docs/Project-Constraints.md` | Stack, runtime constraints, design constraints, assumptions. |
| `docs/Project-Reference.md` | Architecture overview, physics tuning rationale, push-block system design, tile system. |
