# Visual and Story Design — The Golem Awakens

Context spec for the visual and narrative overhaul of [`golem.html`](../golem.html). All changes are polish and theming only — no gameplay mechanics, chamber layouts, or tile behavior.

**Document status (May 2026):** Runtime baseline verified against `golem.html`. Theming Phases 1–5 (+ 4.5) **implemented and reviewed**. Future Phases 6–10 **not started**. Palette spec reflects tholem.ai brand tokens — code uses implemented palette.

---

## 1. Purpose and runtime model

| Requirement | Policy |
|-------------|--------|
| Standalone play | `golem.html` loads via `file://` or static host with zero additional files |
| External assets | No `<img>`, sprite sheets, or separate `.svg`/`.woff2` on disk; Tholem logo = inline SVG in HTML |
| Typography | System fonts only — `FONT_UI`, `FONT_DISPLAY`, `FONT_HEBREW` (Phase 1); no CDN or `@font-face` |
| Canvas | `<canvas id="c">` at **800×480** internal pixels (`W=800`, `H=480`, `T=32`) |
| Overlay UI | Title/pause menus use HTML/CSS overlays in a `position:relative` `#game-shell` wrapper |
| Audio (future) | Web Audio API only — no external audio files (Phase 10a/10b) |

See also [`docs/Project-Constraints.md`](Project-Constraints.md) and [`docs/File-Structure-Reference.md`](File-Structure-Reference.md).

---

## 2. Runtime baseline (implemented today)

Systems already in code that theming must respect or hook into:

| Feature | Section anchor | Notes for theming |
|---------|----------------|-------------------|
| FIFO message queue | 8. GAME FLOW — `MSG_*`, `messageQueue`, `showMessage()` | Fade in/out (180f each); auto hold by text length; max depth 5; render uses gold `rgba(212,168,75,α)` + text shadow |
| Timer advance | 1.5 UTILITIES — `advanceTimers()` | Drives message phases each frame |
| Data-driven glyphs | 1. SETUP — `GLYPH_EFFECTS[]` | `{ set, msg }` per glyph; Phase 1 updates `msg` fields |
| Death/respawn animation | 9.5 ANIMATION — `idle→dying→respawning→idle` | 90f each; clay particles; hardcoded flash `#f0d060` at respawn end |
| Sparse tile render | 11. INIT builds `c.solidTiles`; 10. RENDER iterates it | List built **once at init**; `setTile()` does **not** update the list; render re-reads `c.tiles[y][x]` so AIR after glyph/break is safe |
| Platform drop-down | 5. COLLISION — `inputDown()`, `platSolid()` | Down/S phases through platform from above; geometry pass must preserve behavior |
| Push block visuals | 6. PUSH BLOCK + 10. RENDER | Golden arm/shoulder lines, forward lean squash when pushing |
| Chamber flow HUD | 8. GAME FLOW — `CHAMBER_FLOW`, `flowId` | Bottom-center name from `CHAMBER_NAMES[fi]`; final chamber shows `★ Path of Wisdom` |
| Static ending | 10. RENDER — `gameState==='ending'` | Dark overlay, serif quote, "Refresh to play again"; rAF cancelled |

**Current palette** (`COLORS` in Section 10): `bg #0d0d1a`, brown walls `#4a4035`/`#6b5d4f`, clay golem `#8a7d6b`, gold text `#d4a84b`, magenta dash particles `rgba(220,120,255,…)`.

**Current fonts:** `14px monospace` HUD, `bold 18px serif` messages, `bold/italic serif` ending.

**Current chamber names** (`CHAMBER_NAMES`): Awakening, The Library, The Hall of Echoes, The Weight of Wisdom, The Ibis Chamber.

---

## 3. Narrative design

### 3.1 Core story

The Golem is clay given sentience through **EMET** (עמת — "Truth"). Remove Aleph and it becomes MET (מת — "Death"). Four trials grant letters of Truth; at the end the golem discovers it was self-created — Thoth inscribed the path, but the golem walked it.

### 3.2 Glyph = letter mapping

| Glyph | Letter | Hebrew | Meaning | Current message | Themed message |
|-------|--------|--------|---------|-----------------|----------------|
| 1 | Aleph | א | Ox / Breath | "Knowledge lifts me." | "The First breathes life." |
| 2 | Mem | מ | Water / Mystery | "Speed courses through me." | "The Waters flow through form." |
| 3 | He | ה | Window / Spirit | "Strength returns." | "The Window opens within." |
| 4 | Tav | ת | Mark / Seal | "Clay becomes Wisdom." | "The Seal completes the Name." |

Abilities: breath → double jump; water → dash; spirit → push; seal → break cracked walls.

### 3.3 Chamber narrative arc

| Chamber | Current name | Themed name | Theme |
|---------|--------------|-------------|-------|
| 0 | Awakening | The First Breath | Clay stirs; first letter — potential |
| 1 | The Library | The Flowing Deep | Movement and current |
| 2 | The Hall of Echoes | The Spirit's Mirror | Reflection and force |
| 3 | The Weight of Wisdom | The Weight of Name | Burden and structure |
| 4 | The Ibis Chamber | The Seal of Thoth | Completion before the Ibis |

### 3.4 Message tables (current → themed)

| Context | Current | Themed |
|---------|---------|--------|
| Awakening | "I awaken..." | "The clay remembers it was shaped." |
| Pit death | "The void claims clay..." | "Clay returns to dust." |
| Magical wall | "The barrier consumes you..." | "The boundary rejects the unfinished." |
| Crush | "The weight crushes you..." | "Unformed clay breaks." |
| Locked door | "The seal demands Knowledge..." | "Truth must be earned." |
| Respawn | "Clay reforms..." | (same) |
| Ending quote | "The Ibis speaks: 'You were clay. Now you are Wisdom.'" | See §5 Ending |

### 3.5 Temple visual identity

Chambers are **inscribed initiation halls**, not generic dungeons:

- **Material hierarchy:** Obsidian = void (pits); Midnight = temple air via **`COLORS.bg`** full-canvas clear through non-rendered AIR; Temple Stone = WALL tiles. No floor tile type.
- **Light:** Single upper-left torch — bevels and capstones align. Golem's Champagne eye = only warm living light early on.
- **Progressive sanctity:** Gold/teal intensify toward Chamber 4; Emerald end portal before the Ibis.

| Chamber | Temple read | Accent emphasis |
|---------|-------------|-----------------|
| 0 First Breath | Antechamber — clay stirs | Champagne runes, soft capstones |
| 1 Flowing Deep | Aqueduct hall | Seafoam pit rims |
| 2 Spirit's Mirror | Reflective gallery | Altar push blocks, symmetry |
| 3 Weight of Name | Burden vault | Strong bevels, dense capstones |
| 4 Seal of Thoth | Sanctum — EMET convergence | Emerald portal, brightest gold |

---

## 4. Visual system

### 4.1 Rendering model

**Do not render AIR tiles.** Sparse pipeline in Section 10:

1. `fillRect(0,0,W,H)` with `COLORS.bg`
2. Starfield dots
3. Iterate `c.solidTiles` only — each entry re-reads `c.tiles[y][x]`
4. AIR = negative space showing `COLORS.bg`

No floor tiles. Enclosure = WALL; ledges = thin PLATFORM; void = PIT; push blocks = entities at PUSH_SPAWN.

**Theming rule:** Set `COLORS.bg` to Midnight `#12121F` for interior air. Do **not** add an AIR render branch.

### 4.2 Color palette (tholem.ai target)

Brand tokens only — Obsidian/Midnight/Ink structure, Champagne sacred accents, Seafoam magic, Emerald completion. No brown walls, orange hazard glows, or off-brand violet.

**Ink-layer architecture:**

```
Obsidian #0A0A12     — body CSS, pit fill
  └── Midnight #12121F  — COLORS.bg (canvas clear; visible through AIR)
        └── Temple Stone #222233  — WALL masonry
              └── Ink Bright #3A3A52  — bevels, PLATFORM ledges
                    └── Capstone Gold rgba(197,179,145,0.60)  — 1px WALL trim
```

| Role | Name | Hex | Usage |
|------|------|-----|-------|
| Background | Obsidian | `#0A0A12` | Body CSS; pit base |
| Interior | Midnight | `#12121F` | **`COLORS.bg`** — canvas clear |
| Structure | Ink | `#1F1F2E` | Borders, dividers |
| Sacred | Champagne | `#C5B391` | Glyphs, golem eye, locked doors, capstones |
| Sacred dim | Muted Gold | `#A18F75` | Chamber names, locked HUD |
| Interactive | Seafoam | `#5CB3AF` | Open doors, dash, magical walls, unlocked HUD |
| Magic deep | Teal Deep | `#479E99` | Dash core, magical wall hex |
| Completion | Emerald | `#059669` | END_PORTAL |
| Text | Soft White | `#E8E8F0` | HUD, messages |
| Wall base | Temple Stone | `#222233` | WALL tiles |
| Wall bevel | Ink Bright | `#3A3A52` | WALL top, PLATFORM |
| Platform | — | `#42425C` | PLATFORM ledge |
| Pit base | — | `#060608` | Deeper than bg |
| Pit rim | — | `rgba(92,179,175,0.28)` min | Teal hazard cue |
| Golem body | Lit clay | `#A89B8E` | ≥4.5:1 vs Midnight bg |
| Golem shadow | — | `#4A4858` | Feet shadow |
| Cracked | — | `#2E2840` + Champagne fracture lines | Breakable read |
| Magical wall | — | `rgba(92,179,175,0.30)` / core `rgba(71,158,153,0.75)` | Replaces legacy purple |
| Push block | — | `#2E2E44` / top `#454560` | Altar stone |
| Door locked | — | Midnight panel + Champagne border/seal | Replaces red pulse |
| Door open | — | Seafoam panel + chevron | Replaces green rects |
| End portal | — | Emerald glow/core | Replaces gold portal |

**Dash particles (Section 1 constants):** execution `rgba(92,179,175,0.50)`, charge `rgba(71,158,153,0.35)` — replaces `rgba(220,120,255,…)`.

**Phase 1 `COLORS` merge target:**

```javascript
const COLORS = {
  bg: '#12121F', wall: '#222233', wallTop: '#3A3A52',
  wallCapstone: 'rgba(197,179,145,0.60)',
  platform: '#42425C', pit: '#060608',
  glyph: '#C5B391', glyphGlow: 'rgba(197,179,145,0.45)',
  cracked: '#2E2840',
  golem: '#A89B8E', golemDark: '#4A4858', golemEye: '#C5B391',
  text: '#E8E8F0', pushBlock: '#2E2E44', pushBlockTop: '#454560'
};
```

### 4.3 Contrast guardrails (verify at 800×480 before Phase 1 sign-off)

| Pair | Min ratio | Fix if fail |
|------|-----------|-------------|
| Golem body vs `COLORS.bg` | 4.5:1 | Lighten golem or darken bg one step |
| WALL vs `COLORS.bg` | 3:1 | Use Temple Stone `#222233` |
| PLATFORM vs `COLORS.bg` | 3:1 | Lighten to `#4A4A64` |
| HUD text vs bg | 4.5:1 | Use Soft White |
| PIT rim vs bg | Visible at glance | Teal alpha ≥ 0.25 at pulse peak |
| Glyph vs bg | 3:1 | Boost halo opacity |

**Anti-patterns:** brown `#4a4035` walls; red/orange pit glow; Cosmic Purple `#8B5CF6`; rendering AIR as a tile; floor tile type.

### 4.4 Typography (Phase 1)

```javascript
const FONT_UI      = '11px system-ui, -apple-system, "Segoe UI", sans-serif';
const FONT_DISPLAY = 'italic 16px Georgia, "Times New Roman", serif';
const FONT_HEBREW  = '18px "Segoe UI", "Arial Hebrew", "David", serif';
```

Replace all `monospace`/`serif` strings in HUD, messages, ending.

### 4.5 Particles and effects

| Event | Current | Target |
|-------|---------|--------|
| Jump / land | `#8a7d6b` | `#A89B8E` |
| Double jump | `#d4a84b` | Champagne tint |
| Glyph collect | `#f0d060` | `#C5B391` |
| Dash burst | magenta rgba | Seafoam rgba |
| Death | `#8a7d6b` | `#A89B8E` |
| Starfield | `#1a1a2e` | `#151525` or Midnight tint |

Death/respawn (Section 9.5): update respawn clay pile and activation flash to Champagne `#C5B391`; glyph lines on body → Hebrew letters (Phase 2).

### 4.6 Glyph and rune visuals (Phases 2–3)

- **Glyph tiles:** Replace fillRect cross with Hebrew letter in diamond Champagne halo (§Appendix).
- **Golem body:** Replace horizontal bars with collected Hebrew letters via `FONT_HEBREW`.
- **Background runes:** 6–8% opacity geometric overlay (Champagne + Seafoam + Muted Gold strokes) before or after bg clear — never obscure tiles.

### 4.7 Geometry checklist (Phase 4)

Per-tile render goals in Section 10 — no new data structures:

| Tile/entity | Refinement |
|-------------|------------|
| WALL | Beveled top + 1px capstone trim |
| PLATFORM | Chamfered narrow ledge (preserve hitbox) |
| PIT | Obsidian fill + teal rim + champagne hairline cracks |
| CRACKED | Bevel + X-pattern fractures + gold breakable glow |
| DOOR_D | Recessed panel; gold border locked / Seafoam open |
| MAGICAL_WALL | Seafoam veil + Teal Deep hex pulse |
| END_PORTAL | Emerald layered glow |
| Golem | Rounded shoulders, defined feet |
| Push block | Rounded corners; keep golden effort lines |
| Dash charge | Angular Seafoam segments |

**Phase 4.5 movement polish (~20–30 lines, render-only):** idle head sway; land squish 8–12f; turn lean 6–8f; airborne clay trail; coyote dust puff; extend landing dust to ground landings.

### 4.8 Audio stub (Phase 10 — future)

Web Audio API only; no external files. SFX peak 0.06–0.10; ambient 0.02–0.04.

| Primitive | Waveform | Examples |
|-----------|----------|----------|
| Stone | Triangle | Push, break, footstep |
| Breath | Square sweep | Jump, double jump, dash |
| Spirit | Sine chord | Glyph, door, ending |
| Dust | Filtered noise | Death, wall hit |

| Event | Phase | Est. lines |
|-------|-------|------------|
| SFX engine + call sites | 10a | ~60 |
| Temple drone + optional E Dorian loop | 10b | ~60 |

Init on first keydown/click; mute toggle in title/pause when Phase 6–7 exist. See [`ROADMAP.md`](../ROADMAP.md) Sound Effects.

---

## 5. UI and screens

### 5.1 HUD (preserve layout)

```
Glyphs: X/4                          (top-left)
[1] Double Jump                        (stacked ability list)
[2] Dash (Shift)
[3] Push Blocks
[4] Break Cracked
              Chamber Name ★ status    (bottom-center)
```

**Phase 1 themed delta (~10 lines):** Midnight panel behind HUD; glyph counter shows Hebrew letters collected; unlocked abilities Seafoam `#5CB3AF`, locked Muted Gold `#A18F75`; chamber name in `FONT_DISPLAY`; portal status text "Sealed" / "Open" (replaces emoji lock). `ABILITIES` label strings unchanged.

**Phases 6–8 (future):** Title menu, pause overlay (`P` key), extended 48px HUD bar — see [`ROADMAP.md`](../ROADMAP.md).

### 5.2 Logo and shell (Phase 6)

Inline SVG only in `#logo-container` inside `#game-shell`. Minify with SVGOMG; `fill="currentColor"` or Champagne; no external URLs.

```html
<div id="game-shell" style="position:relative;">
  <canvas id="c"></canvas>
  <div id="logo-container" style="position:absolute;top:15px;left:15px;display:none;">
    <svg id="tholem-logo" … aria-label="Tholem Labs"><!-- paths --></svg>
  </div>
</div>
```

Logo on title menu only — not persistent in-game HUD.

### 5.3 Ending screen (Phase 5 — canonical sequence)

**Current:** Static overlay — title "Awakening of the Golem", Ibis quote, "Refresh to play again".

**Themed animated sequence** (replaces Section 10 ending block + extends `transitionEnding()`):

| Beat | Time | Visual | Text |
|------|------|--------|------|
| 1 | 0–2s | Fade Obsidian; golem centered, four Hebrew letters pulsing Champagne | — |
| 2 | 2–4s | Letters detach, orbit above head | "The four letters converge." |
| 3 | 4–6s | Letters converge on forehead as EMET (עמת); Champagne flash | "EMET — Truth — inscribes itself upon the forehead of clay." |
| 4 | 6–8s | Flash resolves; EMET glows | "The Ibis watches. What Thoth began, the clay completed itself." / "You walked the path of initiation. You are the Golem of Truth." |
| 5 | 8s+ | Stats line | Time \| Deaths |
| 6 | — | "Play Again" button | Seafoam outline; reload or full state reset |

Implementation: hero golem render; orbit via sin/cos; lerp convergence; `messageQueue` timed reveals; ~80–100 lines.

### 5.4 Responsive canvas (Phase 9)

CSS only — preserve 800×480 internal resolution:

```css
canvas { max-width: 100vw; max-height: 100vh; object-fit: contain; }
```

Apply when `#game-shell` exists (Phase 6+).

---

## 6. Implementation phases

Priority-ordered; each phase is a self-contained change. Details in §3–5 above — do not duplicate palette tables here.

| Phase | Scope | Status | Est. |
|-------|-------|--------|------|
| **1** Color & text | `FONT_*`, `COLORS`, particles, dash constants, all messages, `CHAMBER_NAMES`, HUD colors, door/portal/magical wall colors, starfield, death/respawn colors; contrast QA §4.3 | **Complete** | ~38 |
| **2** Glyph visuals | Hebrew letter tiles + golem body letters | **Complete** | ~15 |
| **3** Background runes | 6–8% geometric overlay | **Complete** | ~15 |
| **4** Geometry | §4.7 checklist | **Complete** | ~45 |
| **4.5** Movement polish | §4.7 last bullet | **Complete** | ~25 |
| **5** Ending | §5.3 animated sequence | **Complete** | ~90 |
| **6** Title menu | `#game-shell`, inline SVG, `gameState='title'` | Future | ~60 |
| **7** Pause menu | `P` key, skip update, overlay | Future | ~40 |
| **8** Extended HUD | Bar above canvas, timer, deaths, glyph slots | Future | ~40 |
| **9** Responsive CSS | §5.4 | Future | ~6 |
| **10a** SFX | Web Audio primitives + call sites | Future | ~60 |
| **10b** Ambient | Drone + optional melody loop | Future | ~60 |

---

## 7. Constraints and guardrails

1. **No gameplay changes** — grids, physics, collision, abilities untouched.
2. **No architecture changes** — single-file `golem.html`; new code as IIFEs or appended blocks per section convention.
3. **No new tile types** — 12 types only; visual changes are render-only.
4. **Chamber flow preserved** — `CHAMBER_FLOW`, `flowId`, DOOR_D logic unchanged.
5. **Test chamber untouched** — `T` key sandbox with all abilities.
6. **Canvas resolution** — internal 800×480; CSS scaling display-only (Phase 9).
7. **9-step IIFE convention** for chamber blocks (`chamber-template.md`).
8. **Quality gates:** `python3 tools/chamber_diff.py --strict` (0 mismatches if chambers touched — they should not be); browser console clean; contrast pairs §4.3 at 800×480 after Phase 1.
9. **Standalone deployment** — verify `file://` and static host.
10. **Fonts:** system only via `FONT_*`; no CDN.
11. **Logo:** inline SVG only; no external image references.
12. **Scope:** Future phases add HTML/CSS/JS inside `golem.html` only unless governance approves architecture change.

---

## 8. Code map (section anchors)

Use **section header comments** in `golem.html`, not line numbers (counts shift with edits).

| Section | What to change for theming |
|---------|---------------------------|
| 1. SETUP — `PARTICLE_COLORS`, dash particle constants | Particle and dash colors |
| 1. SETUP — `ABILITIES`, `CHAMBER_NAMES` | Chamber names (ability labels unchanged) |
| 1. SETUP — `GLYPH_EFFECTS` | Glyph collect messages |
| 1.5 — `advanceTimers()` | Message phase timing (usually unchanged) |
| 8. GAME FLOW — `showMessage`, death strings in `killAndRespawn` | Death/portal messages |
| 8. GAME FLOW — `transitionEnding()` | Ending trigger (Phase 5) |
| 9.5 — `renderDeathRespawnAnimation()` | Clay/flash colors; Hebrew glyphs (Phase 2) |
| 10. RENDER — `COLORS` | All visual colors incl. **`bg`** |
| 10. RENDER — canvas clear + starfield | Interior air color |
| 10. RENDER — sparse tile loop | WALL/PLATFORM/PIT/DOOR/GLYPH/CRACKED/MAGICAL_WALL/END_PORTAL |
| 10. RENDER — push block + golem + dash indicator | Entity geometry and colors |
| 10. RENDER — HUD block | Fonts, colors, chamber name |
| 10. RENDER — `messageQueue` draw | Message font/color |
| 10. RENDER — ending overlay | Phase 5 rewrite |
| 11. INIT — `showMessage('I awaken...')` | Awakening message |
| CSS (head) + `<canvas id="c">` | Body bg, `#game-shell`, responsive rules |

---

## Appendix: Hebrew letters

| Letter | Unicode | Canvas string |
|--------|---------|---------------|
| Aleph | U+05D0 | `'\u05d0'` |
| Mem | U+05DE | `'\u05de'` |
| He | U+05D4 | `'\u05d4'` |
| Tav | U+05EA | `'\u05ea'` |
| EMET | — | `'\u05e2\u05de\u05ea'` (Ayin, not Aleph — intentional) |

First collected glyph is Aleph (breath/potential); journey completes with the Word EMET (Truth).
