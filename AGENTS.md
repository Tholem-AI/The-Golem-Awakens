# The Golem Awakens — System Instructions

> **Note for contributors:** This file documents the internal AI-agent governance and development workflow used during the project's creation. It is kept here for transparency into the development process, not as a contribution guide. For contributing to the game, see [README.md](README.md) and the [docs/](docs/) directory.

This file defines always-on governance, execution lifecycle, safety, quality, and project-constraint policy for the GOLEM_GAME project.

## Governance (always-on)

1. Require explicit user approval before high-impact actions: architecture changes, structural moves/renames, stack changes, or git writes.
2. Escalate contradictions across runtime rules, roadmap, manifest, and migration runbook before continuing.
3. Keep runtime artifacts operational-only. Move tutorials, long examples, and narrative rationale to `docs/`.
4. Keep `ROADMAP.md` and relevant docs aligned with actual implementation state.
5. Do not reactivate deprecated workflow artifacts as active execution targets unless explicitly approved.

## Execution lifecycle (RIPER)

1. Follow RIPER sequencing for non-trivial work: Research -> Plan -> Execute -> Review.
2. Use `ROADMAP.md` as the canonical active lifecycle surface.
3. Use the `riper-orchestrator` skill to coordinate full RIPER phase handoffs.
4. Agents may move work to `Ready for Review` but must not mark final completion without explicit user confirmation and validation evidence.
5. Significant phase transitions require concise handoff summaries with: what changed, why, impact on next actions, and responsible owner.
6. Task and handoff updates must include concise evidence tied to actual repo changes.

## Safety constraints

1. Do not modify `golem.html` for architectural changes (splitting files, changing module system, refactoring game loop) without user approval. Normal feature work, bug fixes, and chamber edits are allowed.
2. Do not perform destructive or history-rewriting git operations unless explicitly requested.
3. Do not commit, merge, rebase, reset, or push without explicit user approval.
4. Do not move or rename files/directories without explicit user approval.
5. Preserve import/reference integrity when proposing structural changes.

## Quality gates

1. Run relevant quality checks before declaring work ready for review.
2. For chamber changes: run `python3 tools/chamber_diff.py --strict` — must show 0 mismatches.
3. For new chambers: validate with `python3 tools/chamber_diff.py --validate proposal.md --strict`.
4. For proposals: diff against existing data with `python3 tools/chamber_diff.py --diff-proposal chamber-data.md proposal.md`.
5. chamber-data.md must never contain annotation lines — grids only.
6. All golem.html IIFEs must follow the 9-step ordered construction convention (documented in `chamber-template.md`).
7. Verify flow consistency with `python3 tools/chamber_diff.py --check-flow`.
8. Verify the game loads and runs without console errors.
9. Do not mark work complete without corresponding validation evidence.
10. Keep implementation, `ROADMAP.md`, and key docs in sync, including `docs/File-Structure-Reference.md` and `docs/Project-Constraints.md`.

## Project constraints

1. Core stack: Vanilla JavaScript, HTML5 Canvas 2D. No frameworks unless approved via governance rule 1.
2. Current architecture: single-file (`golem.html`). Splitting into modules or adding external dependencies requires approval via governance rule 1.
3. Current canvas: 800x480 pixels, 32x32 tiles. Existing chambers use a 25x15 grid — new chambers or UI overlays may differ.
4. Current tile set: 12 types (AIR through PUSH_SPAWN). Adding new tile types requires approval via governance rule 1.
5. Chamber flow system: `CHAMBER_FLOW` array defines progression order. Each main chamber has a `flowId` property. DOOR_D follows flow. Test chamber has no flowId.
6. Existing progression: 4-glyph grant-then-use chain across chambers 0-4. New chambers or abilities should maintain or extend this pattern — do not break existing chambers.
7. See `docs/Project-Constraints.md` for full constraint documentation.

## Kit skills

The Tholem Hermes Kit provides these skills (in `skills.external_dirs`):

- `research-agent` — Read-only discovery and evidence capture.
- `planner-agent` — Execution-ready plan with innovate checkpoint.
- `executor-agent` — Implementation slices with validator-gated progression.
- `reviewer-agent` — Final quality, risk, and release-readiness review.
- `riper-orchestrator` — Coordinates full RIPER phase flow.
- `bootstrap-project` — Project initialization and governance setup.
- `roadmap-updater` — Maintains ROADMAP.md checkpoints.
- `documentation-maintainer` — Keeps runtime documentation aligned.

## Testing

- Browser testing: open `golem.html` in browser, use `golem-state-audit.md` Section 14 for update cycle verification.
- Test chamber: press `T` to enter sandbox with all abilities unlocked.
- Set `_testMode = true` for instant transitions during automated testing.
