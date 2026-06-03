# File Structure Reference

## GOLEM_GAME/

```
GOLEM_GAME/
  AGENTS.md                  # Project-scoped governance (Tholem Hermes Kit)
  golem.html                # Single-file HTML5 game (~2513 lines, 13 sections + sound engine, ~104 KB)
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
    Project-Reference.md          # Architecture, physics tuning rationale, push-block design, sim timing system
    Visual-Story-Design.md        # Visual/narrative theming spec and implementation phases
```

## Key files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project governance: safety, quality, lifecycle, constraints |
|| `golem.html` | Complete game source. Single-file HTML5 platformer. ~2513 lines. 13-section structure (1, 1.5, 2-9, 9.5, 10, 11, with 7.5 Sound Engine between 7 and 8): Setup/Constants (Section 1 includes tile types, physics/dash constants, SIM_HZ timing system, fixed frame constants, ENDING wall-clock timeline, PARTICLE_COLORS, GLYPH_EFFECTS, FONT_*/COLORS, static UI arrays, ending state, SFX sound definitions, 8 named constants from code review S7: TRANSITION_FADE_SPEED, ENDING_FADE_SPEED, SIM_ACCUMULATOR_CAP, MAX_TICKS_PER_FRAME, SHADOW_BLUR, LAND_SQUISH_FRAMES, TURN_LEAN_FRAMES, STARS_PER_CHAMBER), Utilities (Section 1.5: snapToTileX, playerGridPos, endDash, land, easeOutCubic, easeOutQuint, lerp, smoothStep, syncPrevKeys, advanceTimers, fullDashReset, cancelDash, resetPlayerToRespawn, killAndRespawn, captionAlphaSec, startGame, returnToMenu, getEndingGlyphState, shadowText, playerGridBounds, doJump, drawWallBase), Chamber Data (Section 2, 9-step ordered construction with /* Step N: */ comments, CHAMBER_FLOW flow system), Entities (Section 3: P player, PB push block, game state globals), Input (Section 4), Tile Helpers/Collision (Section 5: getTile, setTile, solid, platSolid, tileCollidesRect, collides*, inPit, aabb, pushBlockHit, isRiding, resolveBlockX/Y, moveBlockRiders, applyBlockVelocityX, activePushBlocks, checkPushBlockCrush), Push Block System (Section 6: 3-phase orchestrator, block-vs-block AABB, rider collision, crush death), Particle System (Section 7, IIFE with shape param, reduced platforming particles), Sound Engine (Section 7.5, IIFE: init, play, setMute, isMuted, startMusic, stopMusic, duckMusic; Web Audio API with 9 SFX, ambient drone D2 73.42Hz, D minor arpeggio 75 BPM), Game Flow (Section 8: MSG_* constants, showMessage, _doTransition, transition, checkDoors, checkGlyphs, transitionEnding), Update (Section 9: main physics/input loop with title/pause state guards, single gameState guard), Animation State Machine (Section 9.5: idle->dying->respawning->idle), Render (Section 10: tholem.ai palette, background runes, themed tiles with geometry refinements (beveled walls, chamfered platforms, rounded push blocks, hex magical walls, X-crack walls, geometric door, compass rose dash, r... [truncated]
| `README.md` | Project overview, controls, abilities, chambers |
| `ROADMAP.md` | Active development checkpoints |
| `chamber-data.md` | ASCII grid exports of all 6 chambers — grid-only, no annotations. Verified 0 mismatches against golem.html. |
| `chamber-proposal.md` | Reusable template for new chamber proposals; used with chamber_diff.py diff-proposal workflow |
| `chamber-template.md` | Tile legend, coordinate system, chamber flow system, ordered construction convention (9-step), diff workflows (A-F), conversion spec |
| `master-improvement-plan.md` | Completed 8-slice improvement plan with execution details, validation gates, and before/after state. Kept as reference for future refactoring. |
| `tools/chamber_diff.py` | Diff/validation CLI tool with 6 modes: --diff, --validate, --strict, --export-ascii, --diff-proposal, --check-flow |
|| `docs/Project-Constraints.md` | Stack, runtime constraints (sim timing, wall-clock ending), design constraints, assumptions. |
| `docs/Project-Reference.md` | Architecture overview, simulation timing system, physics tuning rationale, push-block system design, tile system, ending timeline. |
| | `docs/Visual-Story-Design.md` | tholem.ai theming spec, narrative tables, palette/contrast guardrails, Phases 1-10b checklist, code map. Phases 1-10b implemented (palette, Hebrew glyphs, runes, geometry, movement polish, ending, HUD, title menu, pause menu, responsive scaling, Web Audio SFX + ambient music). Glyph ordering and ending animation bugs fixed. |
