# File Structure Reference

## GOLEM_GAME/

```
GOLEM_GAME/
  AGENTS.md                  # Project-scoped governance (Tholem Hermes Kit)
  golem.html                # Single-file HTML5 game (~2012 lines, 12 sections + ending animation, ~74 KB)
  README.md                 # Project overview, controls, abilities, chambers
  ROADMAP.md                # Active development checkpoints
  chamber-data.md           # Chamber grid exports extracted from golem.html (grid-only, no annotations)
  chamber-proposal.md       # Reusable template for new chamber proposals with diff-guided workflow
  chamber-template.md       # Tile legend, coordinate system, chamber flow, ordered construction convention, diff workflows (A-F), conversion spec
  master-improvement-plan.md  # Completed Master Improvement Plan (8 slices) — reference for past refactoring work
  tools/
    chamber_diff.py         # Diff/validation tool (6 modes: diff, validate, strict, export-ascii, diff-proposal, check-flow)
  docs/
    File-Structure-Reference.md   # This file
    Project-Constraints.md        # Inferred stack and constraints
    Project-Reference.md          # Architecture, physics tuning rationale, push-block design
    Visual-Story-Design.md        # Visual/narrative theming spec and implementation phases
```

## Key files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project governance: safety, quality, lifecycle, constraints |
||| `golem.html` | Complete game source. Single-file HTML5 platformer. ~2012 lines. 12-section structure (1, 1.5, 2-9, 9.5, 10, 11): Setup/Constants (Section 1 includes tile types, physics/dash constants, PARTICLE_COLORS, GLYPH_EFFECTS, FONT_*/COLORS, static UI arrays, ending state), Utilities (Section 1.5: snapToTileX, playerGridPos, endDash, land, easeOutCubic, syncPrevKeys, advanceTimers, fullDashReset, cancelDash, resetPlayerToRespawn, killAndRespawn), Chamber Data (Section 2, 9-step ordered construction with /* Step N: */ comments, CHAMBER_FLOW flow system), Entities (Section 3: P player, PB push block, game state globals), Input (Section 4), Tile Helpers/Collision (Section 5: getTile, setTile, solid, platSolid, tileCollidesRect, collides*, inPit, aabb, pushBlockHit, isRiding, resolveBlockX/Y, moveBlockRiders, applyBlockVelocityX, activePushBlocks, checkPushBlockCrush), Push Block System (Section 6: 3-phase orchestrator, block-vs-block AABB, rider collision, crush death), Particle System (Section 7, IIFE with shape param, reduced platforming particles), Game Flow (Section 8: MSG_* constants, showMessage, _doTransition, transition, checkDoors, checkGlyphs, transitionEnding), Update (Section 9: main physics/input loop), Animation State Machine (Section 9.5: idle->dying->respawning->idle), Render (Section 10: tholem.ai palette, background runes, themed tiles with geometry refinements (beveled walls, chamfered platforms, rounded push blocks, hex magical walls, X-crack walls, geometric door, compass rose dash, rounded golem, symmetric pit indicators, particle shapes), animated ending beats), Init/Game Loop (Section 11). |
| `README.md` | Project overview, controls, abilities, chambers |
| `ROADMAP.md` | Active development checkpoints |
| `chamber-data.md` | ASCII grid exports of all 6 chambers — grid-only, no annotations. Verified 0 mismatches against golem.html. |
| `chamber-proposal.md` | Reusable template for new chamber proposals; used with chamber_diff.py diff-proposal workflow |
| `chamber-template.md` | Tile legend, coordinate system, chamber flow system, ordered construction convention (9-step), diff workflows (A-F), conversion spec |
| `master-improvement-plan.md` | Completed 8-slice improvement plan with execution details, validation gates, and before/after state. Kept as reference for future refactoring. |
| `tools/chamber_diff.py` | Diff/validation CLI tool with 6 modes: --diff, --validate, --strict, --export-ascii, --diff-proposal, --check-flow |
| `docs/Project-Constraints.md` | Stack, runtime constraints, design constraints, assumptions. |
| `docs/Project-Reference.md` | Architecture overview, physics tuning rationale, push-block system design, tile system. |
|| `docs/Visual-Story-Design.md` | tholem.ai theming spec, narrative tables, palette/contrast guardrails, Phases 1-10b checklist, code map. Phases 1-5.5 (+4.5) implemented. |
