# File Structure Reference

Generated from observed repository structure.

## GOLEM_GAME/

```
GOLEM_GAME/
  AGENTS.md                # Project-scoped governance (Tholem Hermes Kit)
  golem.html              # Single-file HTML5 game (~1153 lines, 11 sections, ~42 KB)
  README.md               # Project overview, controls, abilities, chambers
  ROADMAP.md              # Active development checkpoints
  chamber-data.md          # Chamber layouts extracted from golem.html (5 chambers + test)
  chamber-proposal.md      # Improvement proposals for Chambers 0 and 4
  chamber-template.md      # Tile legend, format spec, conversion instructions
  code-review.md           # Code review: assessment, issues, recommendations
  golem-state-audit.md     # Comprehensive game state audit (~688 lines)
  docs/
    File-Structure-Reference.md  # This file
    Project-Constraints.md       # Inferred stack and constraints
    Physics-Research-Report.md   # Human reaction time alignment research
    Pushblock-Standing-Bug-Execution-Plan.md  # Standing bug fix plan
    push-block-mechanics-plan.md  # Smooth push mechanics overhaul plan
    review-push-block-overhaul.md  # Review report for push overhaul
    beyond-scope-simplifications.md  # Simplification opportunities beyond refactor scope
    refactor-execution-plan.md       # Code refactor execution plan and innovate checkpoint
    code-optimization-analysis.md    # Research findings: 6-slice code optimization analysis
    code-optimization-proposals.md   # Optimization proposals report (32 proposals, P0-P3)
```

## Key files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project governance: safety, quality, lifecycle, constraints |
| `golem.html` | Complete game source. Single-file HTML5 platformer. 11-section structure: Setup/Constants, Chamber Data, Entities, Input, Tile Helpers/Collision, Push Block System, Particle System, Game Flow, Update, Render, Init/Game Loop. |
| `README.md` | Project overview, controls, abilities, chambers |
| `ROADMAP.md` | Active development checkpoints |
| `chamber-data.md` | ASCII grid exports of all 6 chambers with annotations. |
| `chamber-proposal.md` | Proposed chamber restructures for Ch.0 and Ch.4. |
| `chamber-template.md` | Tile legend, coordinate system, extraction/conversion workflow. |
| `code-review.md` | Code quality review with prioritized improvements. |
| `golem-state-audit.md` | Full game architecture audit: physics, tiles, chambers, entities, rendering. |
