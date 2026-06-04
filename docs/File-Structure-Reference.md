# File Structure Reference

## GOLEM_GAME/

```
GOLEM_GAME/
  AGENTS.md                  # Project-scoped governance (Tholem Hermes Kit)
  golem.html                # Single-file HTML5 game (~3049 lines, 14 sections + JSDoc, ~125 KB)
  LICENSE                   # MIT License for open-source release
  .gitignore                # Git ignore rules (tools/__pycache__, etc.)
  README.md                 # Project overview, controls, abilities, chambers
  ROADMAP.md                # Active development checkpoints
  chamber-data.md           # Chamber grid exports extracted from golem.html (grid-only, no annotations)
  chamber-proposal.md       # Reusable template for new chamber proposals with diff-guided workflow
  chamber-template.md       # Tile legend, coordinate system, chamber flow, ordered construction convention, diff workflows (A-F), conversion spec
  tools/
    chamber_diff.py         # Diff/validation tool (6 modes: diff, validate, strict, export-ascii, diff-proposal, check-flow)
    verify_ch4_walls.py     # Chamber 4 wall verification example (demonstrates chamber_diff.py usage)
  docs/
    File-Structure-Reference.md   # This file
    Code-Architecture.md          # Architecture overview, simulation timing system, physics tuning rationale, push-block system design, tile system, ending timeline
    Project-Constraints.md        # Inferred stack and constraints
    Adding-Chambers.md            # Step-by-step guide for adding new chambers to the game
    Tile-System.md                # Tile types, collision behavior, and tile-based movement mechanics
    Visual-Story-Design.md        # Visual/narrative theming spec and implementation phases
```

## Key files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project governance: safety, quality, lifecycle, constraints |
| `golem.html` | Complete game source. Single-file HTML5 platformer. ~3049 lines. 14-section structure (1, 1.5, 2-9, 9.5, 10, 11, with 7.5 Sound Engine between 7 and 8). All 86+ public functions have JSDoc comments. |
| `LICENSE` | MIT License for open-source release. |
| `.gitignore` | Git ignore rules (tools/__pycache__, OS artifacts, .hermes/). |
| `README.md` | Public-facing project overview, controls, abilities, chambers |
| `ROADMAP.md` | Active development checkpoints |
| `chamber-data.md` | ASCII grid exports of all 6 chambers — grid-only, no annotations. Verified 0 mismatches against golem.html. |
| `chamber-proposal.md` | Reusable template for new chamber proposals; used with chamber_diff.py diff-proposal workflow |
| `chamber-template.md` | Tile legend, coordinate system, chamber flow system, ordered construction convention (9-step), diff workflows (A-F), conversion spec |
| `tools/chamber_diff.py` | Diff/validation CLI tool with 6 modes: --diff, --validate, --strict, --export-ascii, --diff-proposal, --check-flow |
| `tools/verify_ch4_walls.py` | Chamber 4 wall verification example — demonstrates chamber_diff.py usage for contributors. |
| `docs/File-Structure-Reference.md` | This file — current project file layout and descriptions. |
| `docs/Code-Architecture.md` | Architecture overview, simulation timing system, physics tuning rationale, push-block system design, tile system, ending timeline. |
| `docs/Project-Constraints.md` | Stack, runtime constraints (sim timing, wall-clock ending), design constraints, assumptions. |
| `docs/Adding-Chambers.md` | Step-by-step guide for adding new chambers to the game. |
| `docs/Tile-System.md` | Tile types, collision behavior, and tile-based movement mechanics. |
| `docs/Visual-Story-Design.md` | Visual/narrative theming spec, narrative tables, palette/contrast guardrails, Phases 1-10b checklist, code map. Phases 1-10b implemented (palette, Hebrew glyphs, runes, geometry, movement polish, ending, HUD, title menu, pause menu, responsive scaling, Web Audio SFX + ambient music). Glyph ordering and ending animation bugs fixed. |
