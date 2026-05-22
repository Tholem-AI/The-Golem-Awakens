# Left-Out Findings: The Golem Awakens

Items from the three review reports that were NOT included in the master improvement plan. These are organized by reason for exclusion.

Cross-report abbreviations:
- **CR** = code-review-report.md
- **REF** = refactor-readiness-report.md
- **OPT** = optimization-opportunities-report.md

---

## Deferred — Higher Risk or Future Architectural Pass

These items were explicitly considered in the plan's innovate checkpoint and deferred to a future pass due to higher risk, architectural scope, or marginal benefit.

### 1. Push block physics consolidation across Sections 5 and 6

- **Source:** REF §Grouping #1 (S4)
- **Lines:** 534-637 (Section 5), 639-747 (Section 6)
- **Description:** 9 push-block functions live in Section 5 mixed among tile collision helpers, while 3 orchestration functions live in Section 6. Consolidating them into one section would improve navigability.
- **Why deferred:** This is a large structural move (~104 lines across 9 functions). While function hoisting makes it safe, the change touches the heart of the game's physics system and carries disproportionate risk for a cosmetic improvement. Best done as a dedicated architectural pass.
- **Risk:** Low (function hoisting protects call order), but high surface area.

### 2. TileSystem namespace extraction

- **Source:** REF §Extraction #1
- **Lines:** All 12 tile functions in Section 5
- **Description:** Wrap `getTile`, `setTile`, `solid`, `platSolid`, `tileCollidesRect`, `collides*`, `inPit`, `tileCollides` into a `TileSystem` object or namespace.
- **Why deferred:** Every call site throughout UPDATE and RENDER would need changing (`getTile(...)` -> `Tiles.get(...)`). ~50+ call sites. High change surface for organizational benefit only.
- **Risk:** Medium — missed call site = ReferenceError.

### 3. PushBlocks IIFE module extraction

- **Source:** REF §Extraction #2
- **Lines:** All 11 push-block functions
- **Description:** Wrap push block system in IIFE matching the `Particles` pattern, making `PBlocks` internal.
- **Why deferred:** Multiple call sites in UPDATE, `_doTransition`, and `killAndRespawn` need updating. The `PBlocks` array is accessed directly in several places.
- **Risk:** Medium-High — the plan explicitly deferred this in the innovate checkpoint.

### 4. GameFlow object extraction

- **Source:** REF §Extraction #3
- **Lines:** Section 8, 7 functions
- **Description:** Group message, transition, door, and glyph functions into a GameFlow object.
- **Why deferred:** Call sites in UPDATE and other functions need updating. Organizational benefit only.
- **Risk:** Medium.

### 5. HiDPI canvas scaling

- **Source:** CR §Suggestion #5
- **Lines:** 22-23, CSS line 9
- **Description:** Scale canvas for devicePixelRatio so the game renders sharply on Retina displays.
- **Why deferred:** Medium risk (requires `X.scale(dpr, dpr)` and testing on both HiDPI and standard displays). Out of scope for a refinement pass.
- **Risk:** Medium.

### 6. Particle compact-after-dead pattern

- **Source:** OPT §Performance #2
- **Lines:** 798 (Particle.update)
- **Description:** Replace `splice` removal with compact-after-dead loop for better cache performance.
- **Why deferred:** Marginal gain — particle counts stay under 50 at any time. The current `splice` in reverse iteration is correct and fast enough.
- **Risk:** None, but zero practical benefit.

### 7. Collision object allocation elimination

- **Source:** OPT §Performance #3, OPT §Redundancy #3 (collidesNoPlat)
- **Lines:** 495-497
- **Description:** Pass parameters directly instead of allocating options objects per frame in `collides()` and `collidesNoPlat()`.
- **Why deferred:** Changes the API surface of `tileCollidesRect`, `collides`, `collidesNoPlat`, and `collidesDash`. Higher risk than the benefit (1 allocation per frame).
- **Risk:** Medium — API change across 4 functions with multiple call sites.

### 8. Neighbor tile scan extraction

- **Source:** OPT §Redundancy #6 (O2)
- **Lines:** 519-525, 851-881, 889-902
- **Description:** Extract `scanNeighborTiles(callback)` pattern from `inPit()`, `checkDoors()`, `checkGlyphs()`.
- **Why deferred:** Adds an abstraction layer over simple 3-line loops. Risk outweighs benefit for 3 call sites.
- **Risk:** Low, but the callback pattern adds cognitive overhead for what is currently clear.

---

## Deferred — Low Priority / Cosmetic

These items are valid observations but were deprioritized in favor of higher-impact changes.

### 9. Jump logic factoring

- **Source:** OPT §Logic Simplification #4 (O1)
- **Lines:** 1112-1143
- **Description:** Factor out common `P.jumpBuffer=0` and `Particles.spawn()` from 4 jump branches into a shared helper.
- **Why deferred:** ~12 line savings but the 4 branches have subtle differences (ground vs coyote vs air vs double jump). Extracting a helper adds parameters that may obscure intent.
- **Risk:** Low.

### 10. Particle color constants (PARTICLE_COLORS object)

- **Source:** REF §Naming #5 (S7), OPT
- **Lines:** Various inline strings
- **Description:** Extract recurring particle color strings (`'#8a7d6b'`, `'#d4a84b'`, etc.) to a `PARTICLE_COLORS` object.
- **Why deferred:** Originally planned for Slice 8 but deprioritized — the color strings are self-documenting and changing them requires touching the same line anyway. The GLYPH_EFFECTS data-driven system was chosen as the single future-proofing item.
- **Risk:** None.

### 11. Tile property map (TILE_PROPS)

- **Source:** OPT §Future-Proofing #3 (FP2)
- **Lines:** 471 (`solid()` function)
- **Description:** Replace `solid()` if/chain with a `TILE_PROPS` lookup map for extensibility.
- **Why deferred:** ~5 lines of net growth. Adding new tile types currently only requires modifying `solid()` and `platSolid()` — the cognitive cost of a map vs. reading a single if-chain is debatable for a 1700-line game.
- **Risk:** Low.

### 12. Chamber boundary helper (drawBorder)

- **Source:** OPT §Future-Proofing #2 (FP4)
- **Lines:** Various chamber IIFEs
- **Description:** Extract `drawBorder(g, w, h, {top, bottom, left, right})` helper to reduce boilerplate in chamber data.
- **Why deferred:** Many chambers have non-trivial right-side boundaries with gaps. A generic helper would need significant gap specification logic, negating the boilerplate savings.
- **Risk:** Medium — touches all 6 chamber IIFEs.

### 13. Push block slot standardization

- **Source:** OPT §Future-Proofing #4 (FP3)
- **Lines:** 647, 726-737
- **Description:** Normalize chambers to always use `pushSpawns` array (chamber 2 and test chamber use singular `pushSpawn`).
- **Why deferred:** User explicitly noted that the inSlot system should be preserved for future use. Standardizing the spawn format is a level design change (chamber data), which was excluded from the plan.
- **Risk:** None (chamber data only), but excluded by user constraint.

### 14. `collectedGlyphs` / `glyphsCollected` naming

- **Source:** REF §Naming #6
- **Lines:** 399-400
- **Description:** Rename `collectedGlyphs` (array) to `chamberGlyphCollected` and `glyphsCollected` (count) to `totalGlyphsCollected` for clarity.
- **Why deferred:** Cosmetic renaming. The current names are clear in context and renaming would touch every call site.
- **Risk:** Low.

### 15. `solidTiles` -> `renderTiles` terminology

- **Source:** REF §Naming #7
- **Lines:** 456, 1373, 1706-1713
- **Description:** Rename `solidTiles` since it includes all non-AIR tiles, not just solid ones.
- **Why deferred:** The plan already simplifies `setTile` by removing solidTiles maintenance (Slice 7). Renaming is a separate cosmetic change that adds no behavioral value.
- **Risk:** Low — but 3 call sites must be updated consistently.

### 16. `PBlocks` vs `PB_` naming inconsistency

- **Source:** REF §Naming #4
- **Lines:** 396 (PBlocks), 56-59 (PB_*)
- **Description:** Constants use `PB_` prefix while the entity array is named `PBlocks` (not `PBs`).
- **Why deferred:** Cosmetic naming. The current convention is internally consistent enough and renaming would touch every constant and call site.
- **Risk:** None.

### 17. Game state globals regrouping

- **Source:** REF §Grouping #5 (S5)
- **Lines:** 398-413
- **Description:** Group transition, message, and animation globals more tightly within Section 3.
- **Why deferred:** Current subsection markers (`/* Player state */`, `/* Push block entities */`, `/* Game state */`) are already clear. Tighter grouping is a minor cosmetic improvement.
- **Risk:** None.

---

## Superseded — Handled by Other Plan Items

These findings were addressed by other items in the plan and did not need separate entries.

### 18. `for...in` on plain objects (prototype chain safety)

- **Source:** CR §Suggestion #7
- **Lines:** 1156, 1196
- **Superseded by:** Slice 3 (F1) — the `prevKeys = {...keys}` fix replaces the `for...in` loop entirely, making the prototype chain concern moot.

### 19. Dash charge ratio computed twice in render

- **Source:** OPT §Performance #4 (O4)
- **Lines:** ~1508, ~1618
- **Superseded by:** Slice 1.5 (U2) — removing the HUD indicator eliminates one of the two computation sites. The remaining site (ring indicator at line 1508) has no duplicate.

---

## Not Actionable — Observations Only

These items from the reports are valid observations but have no recommended fix or are out of scope.

### 20. Tile type value 6 gap

- **Source:** REF §Naming #2, OPT §Dead Code #6
- **Description:** `CRACKED=7` creates a gap (BLOCK=6 was removed). Documented in Project-Reference.md.
- **Status:** Noted and intentional. No action needed — the gap preserves stability for existing chamber data.

### 21. Glyph collection chamber index as progress gate

- **Source:** OPT §Future-Proofing #5
- **Lines:** 893 (`if(glyphsCollected!==ch) continue;`)
- **Description:** Chamber `i` can only be collected if exactly `i` glyphs have been collected before. Reordering `CHAMBER_FLOW` would break this.
- **Status:** Valid concern for future chamber reordering. The data-driven glyph system (Slice 8) partially addresses this by decoupling ability definitions from the if/else chain, but the chamber-sequence gating logic in `checkGlyphs()` would need a separate change.

---

## Summary

| Category | Count | Total from reports |
|----------|-------|--------------------|
| Included in plan | 23 items | — |
| Deferred (higher risk/future pass) | 8 | Items 1-8 |
| Deferred (low priority/cosmetic) | 6 | Items 9-14 |
| Superseded (handled by other items) | 2 | Items 18-19 |
| Not actionable (observation only) | 2 | Items 20-21 |
| **Total unique findings across 3 reports** | **~41** | **~41** |

**Recommendation:** The 8 deferred higher-risk items (consolidation, extraction, HiDPI) make sense as a future "architectural refinement" pass once this refinement pass is complete and the codebase is stable.
