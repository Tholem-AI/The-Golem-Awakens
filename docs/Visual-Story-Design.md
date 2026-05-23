# Visual and Story Design -- The Golem Awakens

## Purpose

Reference document for the visual and narrative overhaul of `golem.html` (see
`docs/File-Structure-Reference.md`). All changes are polish and theming only — no
gameplay mechanics, chamber layouts, or tile behavior is modified. Line count additions
are scoped to be minimal, enhancing the existing framework.

**Revision note (May 2026):** Palette rewritten with warm/cool contrast principle
after initial Phase 1-4 implementation revealed a "flat" look where all derived colors
were cool purple tones blending into the Obsidian background. New palette uses warm
earth tones for structural elements, warm amber for danger (pits, cracked), and reserves
cool purple exclusively for magic. Geometry refinements expanded to cover all interactive
tile types (CRACKED, DOOR_D).

**Revision note (May 2026, consistency pass):** Added deployment/runtime constraints
(standalone `golem.html`, system-font typography, inline SVG logo). Fixed Aleph Hebrew
codepoint in Section 1.2. Aligned overlay markup with actual canvas id (`c`) and
800×480 resolution per `docs/Project-Constraints.md`.

**Revision note (May 2026, typography):** System fonts only — `FONT_UI`, `FONT_DISPLAY`,
and `FONT_HEBREW` constants (Section 2.2). No Google Fonts or CDN.

### Deployment and runtime model

All visual work targets the existing **single-file** architecture (`golem.html` only).
There is no build step, bundler, or `package.json`. This matches
`docs/Project-Constraints.md` and `docs/File-Structure-Reference.md`.

| Requirement | Policy |
|-------------|--------|
| Standalone play | Opening `golem.html` directly (`file://`) or serving it from any static host must load and run the game with **zero additional files**. |
| External assets | No `<img src="…">`, no sprite sheets, no separate `.svg` / `.woff2` files on disk. The Tholem logo is **inline SVG markup** in the HTML (see Section 3.4). |
| Typography | **System fonts only** — no Google Fonts, no CDN, no `@font-face` embeds (Section 2.2). |
| Canvas identity | The game canvas is `<canvas id="c">` at **800×480** internal pixels (`W=800`, `H=480`, `T=32`). Do not rename the id or resolution in design examples. |
| Overlay UI | Title menu, pause menu, and logo use **HTML/CSS overlays** beside or above `#c`. Wrap canvas in a `position: relative` shell so absolute overlays align correctly. |
| Audio (future) | Web Audio API only — no external audio files (Section 6). |

---

## 1. NARRATIVE DESIGN

### 1.1 Core Story

The Golem is clay given sentience through the four letters of **EMET** (\u05e2\u05de\u05ea -- "Truth"
in Hebrew). Tradition holds that when a golem is created, EMET is inscribed upon its forehead.
Remove the first letter (Aleph) and it becomes MET (\u05de\u05ea -- "Death"). The game traces the
golem's hermetic initiation: an unconscious journey through four trials, each granting a letter
of Truth. At the end, the golem discovers it was self-created -- Thoth inscribed the path, but
the golem walked it.

### 1.2 Glyph = Letter Mapping

The four glyphs correspond to the four letters of EMET, earned in order:

| Glyph # | Letter  | Hebrew | Meaning         | Current Message          | Themed Message                            |
|---------|---------|--------|-----------------|--------------------------|-------------------------------------------|
| 1       | Aleph   | \u05d0  | Ox / Breath     | "Knowledge lifts me."    | "The First breathes life."                |
| 2       | Mem     | \u05de  | Water / Mystery | "Speed courses through me." | "The Waters flow through form."       |
| 3       | He      | \u05d4  | Window / Spirit | "Strength returns."      | "The Window opens within."              |
| 4       | Tav     | \u05ea  | Mark / Seal     | "Clay becomes Wisdom."   | "The Seal completes the Name."          |

Each letter unlocks an ability that serves as the "body" for that aspect of Truth:
breath becomes movement (double jump), water becomes flow (dash), spirit becomes force
(push blocks), and seal becomes clarity (break cracked walls).

### 1.3 Chamber Narrative Arc

| Chamber | Current Name      | Themed Name           | Theme                                              |
|---------|-------------------|-----------------------|----------------------------------------------------|
| 0       | Awakening         | The First Breath      | Clay stirs. The First Letter enters -- potential.  |
| 1       | The Library       | The Flowing Deep      | Movement and current -- the golem learns to flow.  |
| 2       | The Hall of Echoes| The Spirit's Mirror   | Reflection and force -- the golem pushes back.     |
| 3       | Weight of Wisdom  | The Weight of Name    | Burden and structure -- the golem bears the Word.  |
| 4       | The Ibis Chamber  | The Seal of Thoth     | Completion -- the golem stands before the Ibis.   |

### 1.4 Death Messages

Current messages are functional. Themed versions tie death to the dissolution of clay:

| Current Message              | Themed Alternative                          |
|------------------------------|---------------------------------------------|
| "The void claims clay..."    | "Clay returns to dust."                     |
| "The barrier consumes you..."| "The boundary rejects the unfinished."      |
| "The weight crushes you..."  | "Unformed clay breaks."                     |
| "The seal demands Knowledge..."| "Truth must be earned."                   |
| "Clay reforms..."            | "Clay reforms..." (same)  |

### 1.5 Ending Revelation

**Current:** Single static message -- "The Ibis speaks: 'You were clay. Now you are
Wisdom.'"

**Themed:** Multi-phase ending sequence (see Section 5). The final text:

> Phase 1: "The four letters converge."
> Phase 2: "EMET -- Truth -- inscribes itself upon the forehead of clay."
> Phase 3: "The Ibis watches. What Thoth began, the clay completed itself."
> Phase 4: "You walked the path of initiation. You are the Golem of Truth."

### 1.6 Initial Awakening Message

| Current          | Themed                                 |
|------------------|----------------------------------------|
| "I awaken..."    | "The clay remembers it was shaped."    |

---

## 2. VISUAL SYSTEM

### 2.1 Color Palette (from tholem.ai, with contrast guidance)

All base colors are mapped from the tholem.ai brand palette. Derived game-specific colors
are computed with a **warm/cool contrast principle**: the Obsidian background is neutral-dark,
but derived elements use warm earth tones (walls, cracked, pits) rather than cool purple
tones. This prevents the "flat" look where everything blends into the background.

**Rule:** Structural elements (walls, platforms, push blocks) use warm stone. Danger
elements (pits) use warm amber/orange glow. Magic uses cool Cosmic Purple. Accents use
warm Champagne gold. Interactive states use cool Seafoam teal.

**Base palette (brand):**

| Role                     | Name            | Hex       | Usage                                          |
|--------------------------|-----------------|-----------|------------------------------------------------|
| Background (primary)     | Obsidian        | `#0A0A12` | Canvas background (body CSS)                   |
| Background (secondary)   | Midnight Indigo | `#12121F` | Chamber backdrop, HUD panel                    |
| Brand gold               | Champagne       | `#C5B391` | Glyph glow, golem eye, text, accent highlights |
| Brand teal               | Seafoam         | `#5CB3AF` | Door portals (open), learned ability indicators, ending accents |
| Text (primary)           | Soft White      | `#E8E8F0` | HUD text, messages, UI labels                  |
| Text (secondary)         | Muted Champ     | `#A18F75` | Subheadings, chamber names, secondary HUD text |

**Derived game-specific colors** (computed from palette with warm/cool contrast):

| Element            | Color                  | Rationale                                                     |
|--------------------|------------------------|---------------------------------------------------------------|
| Wall (base)        | `#352C22`              | Warm dark stone -- brown-undertone, NOT cool purple            |
| Wall (top)         | `#4A3E32`              | Subtle warm highlight on wall top edge                        |
| Platform           | `#4A3E32`              | Same as wall top -- warm stone ledge                          |
| Pit (base)         | `#060608`              | Near-black void                                               |
| Pit (danger glow)  | `rgba(200,120,30,0.25)`| Warm amber/orange top-edge glow -- clearly signals danger     |
| Pit (crack glow)   | `rgba(200,120,30,0.15)`| Amber diagonal cracks descending into void                    |
| Golem (body)       | `#8B7D6B`              | Warm clay -- kept close to current                            |
| Golem (shadow)     | `#5A5040`              | Darker clay shadow                                            |
| Golem (eye)        | `#C5B391`              | Champagne -- spark of Thoth's fire                            |
| Cracked wall       | `#7A5A3A`              | Warm earth tone -- ochre base, clearly distinct from walls    |
| Cracked (cracks)   | `#3A2010`              | Dark brown crack lines -- visible against ochre base          |
| Cracked (glow)     | `rgba(200,120,30,0.2)` | Warm amber breakable glow -- signals "can be broken"          |
| Magical wall       | `rgba(139,92,246,0.35)`| Cosmic Purple at low opacity -- cool contrast to warm tones   |
| Magical wall (core)| `rgba(139,92,246,0.7)` | Cosmic Purple -- visible magical glow                         |
| Push block         | `#5A4A3A`              | Warm stone, darker than platforms, lighter than walls         |
| Push block (top)   | `#6E5E4E`              | Warm stone highlight                                          |
| Glyph (base)       | `#C5B391`              | Champagne -- gold of Thoth                                    |
| Glyph (glow)       | `rgba(197,179,145,0.4)`| Champagne glow halo                                           |
| Door (locked bg)   | `#1A1520`              | Dark purple-brown -- distinct from walls                      |
| Door (locked seal) | `rgba(180,120,40,0.4)` | Warm amber seal -- gold-tinged, signals "blocked"             |
| Door (locked icon) | `#B08030`              | Warm gold lock icon                                           |
| Door (open bg)     | `rgba(92,179,175,0.4)` | Seafoam -- cool contrast, signals "passage open"              |
| Door (open arrow)  | `#5CB3AF`              | Seafoam arrow                                                 |

**Cosmic Purple -- the magic accent**

The palette introduces **Cosmic Purple** as a game-specific color outside the core
tholem.ai brand set. It serves the magical/mystical dimension of the golem's journey:

| Role                          | Name            | Hex        | Usage                                      |
|-------------------------------|-----------------|------------|--------------------------------------------|
| Magic accent (dash, barriers) | Cosmic Purple   | `#8B5CF6`  | Dash execution particles, dash charge ring, magical wall glow, magical wall core spark |

Cosmic Purple is a vivid violet -- distinct from the warm Champagne and cool Seafoam. It
signals "active magic" without clashing: the Obsidian background provides strong contrast,
and purple sits between Champagne (gold) and Seafoam (teal) on the color wheel, creating a
triadic accent structure. Its cool tone provides the only significant cool color among
structural elements, making magical barriers visually distinct from warm stone and amber
danger zones.

**Key principle:** Cosmic Purple replaces the current `rgba(220,120,255,0.4)` purple but
is more saturated and intentional (`#8B5CF6`). Dash particles become `rgba(139,92,246,0.5)`
for execution and `rgba(139,92,246,0.3)` for charge. Magical walls use `rgba(139,92,246,0.35)`
base fill and `rgba(139,92,246,0.7)` core glow.

**Contrast principle summary:**

- **Warm earth** (`#352C22`, `#4A3E32`, `#5A4A3A`): Walls, platforms, push blocks -- the "stone" of the temple
- **Warm amber** (`rgba(200,120,30,...)`): Pit danger glow, cracked breakable glow -- signals hazard and action
- **Warm gold** (`#C5B391`, `#B08030`): Glyphs, golem eye, door seals -- sacred and valuable
- **Cool purple** (`#8B5CF6`): Magic -- barriers and dash ability
- **Cool teal** (`#5CB3AF`): Open passages and unlocked abilities -- safe and inviting
- **Neutral dark** (`#0A0A12`, `#060608`): Background and void -- canvas for all others

### 2.2 Typography (system fonts only)

The canvas uses `X.fillText()` with font strings. **No web fonts, no CDN, no `@font-face`.**
System fonts ship with the OS and work on `file://`, static hosts, and offline play.

Define three **family** constants in Section 1 (sizes and weight applied at each call site):

```javascript
const FONT_UI = 'system-ui, sans-serif';
const FONT_DISPLAY = 'Georgia, "Times New Roman", serif';
const FONT_HEBREW = '"Segoe UI", Arial, sans-serif';
```

| Role | Family constant | Used for |
|------|-----------------|----------|
| UI | `FONT_UI` | HUD labels, ability list, stats, body CSS |
| Display | `FONT_DISPLAY` | Center messages, ending title/quote, chamber name |
| Hebrew | `FONT_HEBREW` | Glyph tiles, golem body letters, HUD glyph counter |

**Latin text** (English HUD and narrative):

| Element              | Font string example                          |
|----------------------|----------------------------------------------|
| HUD labels           | `'14px ' + FONT_UI`                          |
| HUD ability list     | `'11px ' + FONT_UI`                          |
| Chamber name (bottom)| `'italic 12px ' + FONT_DISPLAY`             |
| Messages (center)    | `'bold 18px ' + FONT_DISPLAY`               |
| Ending title         | `'bold 28px ' + FONT_DISPLAY`               |
| Ending quote         | `'italic 22px ' + FONT_DISPLAY`             |

**Hebrew letters** (glyph tiles, golem torso, `Glyphs: אמ / עמת` counter):

| Element              | Font string example                          |
|----------------------|----------------------------------------------|
| Glyph tile letter    | `'24px ' + FONT_HEBREW`                      |
| Golem body letters   | `'8px ' + FONT_HEBREW`                       |
| HUD glyph counter    | `'14px ' + FONT_HEBREW` (mixed with UI text) |

`FONT_HEBREW` uses `"Segoe UI"` and `Arial` because they include Hebrew glyphs on Windows,
macOS, and most Linux desktops without any download. Do **not** use `FONT_DISPLAY` (Georgia)
for Hebrew — serif stacks often lack Hebrew coverage.

**Body CSS** (overlay menus, Section 5):

```css
body { font-family: system-ui, sans-serif; }
```

**Current state:** `golem.html` uses generic `monospace` / `serif`. Phase 1 adds the three
constants and replaces all `X.font` assignments.

**Lines added:** ~3 constants + font string updates at existing call sites.

### 2.3 Glyph Visual Design

The current glyph is a simple cross/plus rendered with `fillRect`. It is replaced with a
Hebrew letter rendered via `X.fillText()` using the actual Hebrew character, drawn with a
Champagne glow:

| Glyph # | Letter | Unicode | Canvas render                              |
|---------|--------|---------|--------------------------------------------|
| 1       | Aleph  | `\u05d0` | `X.fillText('\u05d0', cx, cy, 24)`        |
| 2       | Mem    | `\u05de` | `X.fillText('\u05de', cx, cy, 24)`        |
| 3       | He     | `\u05d4` | `X.fillText('\u05d4', cx, cy, 24)`        |
| 4       | Tav    | `\u05ea` | `X.fillText('\u05ea', cx, cy, 24)`        |

Each glyph tile renders as:
1. A pulsating Champagne glow circle (halo) -- same bob animation as current
2. The Hebrew letter centered in white/Champagne
3. The glow pulse uses `sin(now/300)` for smooth oscillation

Set `X.font = '24px ' + FONT_HEBREW` before drawing each letter (Section 2.2).

**Lines added:** ~5 per glyph tile render block (replaces existing fillRect cross).

### 2.4 Golem Body Glyph Lines

Current implementation draws horizontal lines on the golem's body for each collected glyph.
These are replaced with the actual Hebrew letters, rendered vertically on the golem's torso:

```
X.fillStyle = 'rgba(197,179,145,' + alpha + ')';
X.font = '8px ' + FONT_HEBREW;
X.textAlign = 'center';
for (let i = 0; i < glyphsCollected; i++) {
  const letters = ['\u05d0','\u05de','\u05d4','\u05ea'];
  X.fillText(letters[i], px + pw/2, py + 14 + i * 6);
}
```

**Lines added:** ~5 (replaces existing for-loop with fillRect).

### 2.5 Rune Background Elements

Per tholem.ai design principles, extremely subtle geometric rune-like line work at 6-10%
opacity may be used as background decoration. Implementation:

- Rendered once per frame behind all tiles
- Thin lines forming abstract geometric patterns (crossing diagonals, subtle triangles)
- Opacity capped at 8%
- Champagne color at low alpha
- Uses the existing starfield render position (before tiles, after background clear)
- No new arrays -- derived from chamber dimensions using modular arithmetic

**Lines added:** ~15 in render() before tile loop.

### 2.6 Particle System Colors

Updated to match palette:

| Particle type     | Current Location             | Current Color              | New Color                      |
|-------------------|------------------------------|----------------------------|--------------------------------|
| Jump              | `PARTICLE_COLORS.jump`       | `#8a7d6b`                  | `#8B7D6B` (warm clay)          |
| Double Jump       | `PARTICLE_COLORS.doubleJump` | `#d4a84b`                  | `#C5B391` (Champagne)          |
| Glyph collect     | `PARTICLE_COLORS.glyph`      | `#f0d060`                  | `#C5B391` (Champagne)          |
| Dash execution    | `PARTICLE_COLORS.dashBurst`  | `rgba(220,120,255,0.6)`   | `rgba(139,92,246,0.5)` (Cosmic Purple) |
| Dash burst (IIFE) | `DASH_EXEC_PARTICLE_COLOR`   | `rgba(220,120,255,0.4)`   | `rgba(139,92,246,0.4)` (Cosmic Purple) |
| Dash charge       | `PARTICLE_COLORS` (spawn)    | `rgba(180,80,255,0.4)`    | `rgba(139,92,246,0.3)` (Cosmic Purple) |
| Dash charge (IIFE)| `DASH_CHARGE_PARTICLE_COLOR` | `rgba(180,80,255,0.4)`    | `rgba(139,92,246,0.3)` (Cosmic Purple) |
| Death             | `PARTICLE_COLORS.death`      | `#8a7d6b`                  | `#8B7D6B` (warm clay)          |

**Note:** `DASH_EXEC_PARTICLE_COLOR` and `DASH_CHARGE_PARTICLE_COLOR` are standalone
constants (lines 39-40) separate from the `PARTICLE_COLORS` object. Phase 1 must update
all four dash-related color sources. Consider consolidating into `PARTICLE_COLORS` in a
future refactor.

### 2.7 Background Starfield

Current starfield uses `#1a1a2e` dots. Updated to use Champagne at very low opacity:
`rgba(197,179,145,0.12)` for subtle warmth against Obsidian.

### 2.8 Asset Geometry Adjustments

The existing tile and entity rendering uses `fillRect` -- pure rectangles. The following
geometric refinements improve visual identity without adding structural complexity. All
changes are render-only and stay within the existing 32x32 tile grid.

**Walls -- beveled top edge:**
Current walls render as a solid `fillRect` with a thin 3px top highlight line. Refined
to add a subtle bevel: the top highlight becomes a 4px trapezoid (narrower at top)
using `beginPath/moveTo/lineTo` instead of `fillRect`. Adds a single line per wall tile
in the render loop. The bevel direction (left-to-right) implies light from upper-left,
consistent with the overall composition.

```
// Current: X.fillRect(px, py, T, 3);
// Refined:
X.beginPath();
X.moveTo(px, py + 3);
X.lineTo(px + T, py + 3);
X.lineTo(px + T - 2, py);
X.lineTo(px + 2, py);
X.closePath();
X.fill();
```

**Platforms -- chamfered edges:**
Current platforms are thin rectangles (`fillRect(px+2, py+2, T-4, 3)`). Refined to add
small chamfer cuts at each end (2px triangles), giving a carved stone appearance.

```
X.beginPath();
X.moveTo(px + 4, py + 1);
X.lineTo(px + T - 4, py + 1);
X.lineTo(px + T - 2, py + 4);
X.lineTo(px + 2, py + 4);
X.closePath();
X.fill();
```

**Pits -- angled void edges with danger glow:**
Current pits render as black rects with a thin glow line on top. Refined to add subtle
diagonal "crack" lines descending into the void, rendered with `strokeStyle` at warm amber.
Two diagonal lines per pit tile, angled toward the pit center, giving depth. The amber
color (`rgba(200,120,30,...)`) clearly signals danger -- the player should avoid these.
```
X.fillStyle=COLORS.pit; X.fillRect(px,py,T,T);
// Top edge danger glow
X.fillStyle='rgba(200,120,30,'+(glow*0.25)+')';
X.fillRect(px,py,T,2);
// Diagonal crack lines
X.strokeStyle='rgba(200,120,30,'+(glow*0.15)+')';
X.lineWidth=1; X.beginPath();
X.moveTo(px+T/3, py); X.lineTo(px+T/2, py+T/2);
X.moveTo(px+2*T/3, py); X.lineTo(px+T/2, py+T/2);
X.stroke();
```

**Golem -- rounded shoulders, defined feet:**
The golem body is currently drawn with `fillRect` for each body part. Two refinements:
1. Head/shoulders: replace the head `fillRect` with a `beginPath` arc for a subtle
   rounded top (radius 4px on the head corners), distinguishing living clay from
   inanimate blocks.
2. Feet: replace the flat bottom rects with slightly splayed trapezoids (wider at base),
   implying a planted stance. Each foot is a 4-line path instead of a rect.

**Push blocks -- distinct from walls:**
Push blocks currently look like smaller wall tiles. Refined to render with rounded
corners (4px radius via arc-based path) to clearly distinguish them from the sharp
wall geometry. The rounded treatment implies "movable" vs. "fixed."

**Push effort visual (golem body):**
When actively pushing, the golem renders pulsing arm/shoulder lines toward the push
direction. Themed with Champagne (`#C5B391`) at `rgba(197,179,145,0.3)` base pulse,
replacing the current `rgba(212,168,75,...)`. The arm lines extend from the golem's
side toward the block, creating a visual "press" effect.

**Glyph tiles -- diamond halo:**
The glyph glow halo is currently a circle (`arc`). Refined to a diamond shape (4-point
polygon) that echoes the geometric rune aesthetic. The Hebrew letter still sits centered
inside, but the diamond frame gives a more deliberate, inscribed quality.

**Dash charge ring -- angular segments:**
The dash charge indicator ring is currently a full circle. Refined to render as 8
angular segments (like a compass rose) using `arc` with start/end angles, creating a
faceted appearance that matches the geometric identity.

**Magical walls -- hexagonal core:**
Magical wall tiles currently render a rectangular glyph in the center. Refined to a
small hexagon (6-point polygon) drawn with `beginPath/lineTo`, pulsing in Cosmic Purple.
The hexagonal shape implies crystalline/magical structure.

**Cracked walls -- beveled edges with crack detail:**
Cracked wall tiles currently render as a simple fillRect with a thin top highlight and
a few crack lines. Refined to:
1. A beveled top edge (same trapezoid treatment as walls) -- implies carved stone that's
   degrading.
2. Two diagonal crack lines crossing in an X pattern, drawn with `strokeStyle` at
   `#3A2010` (dark brown), giving a "fractured" appearance.
3. A warm amber glow (`rgba(200,120,30,0.2)`) around the tile edges -- signals "breakable"
   and clearly distinguishes from solid walls.

```
// Bevel base
X.fillStyle=COLORS.cracked; X.fillRect(px,py,T,T);
X.fillStyle=COLORS.wallTop;
X.beginPath(); X.moveTo(px,py+3); X.lineTo(px+T,py+3);
X.lineTo(px+T-2,py); X.lineTo(px+2,py); X.closePath(); X.fill();
// Crack lines (X pattern)
X.strokeStyle='#3A2010'; X.lineWidth=2;
X.beginPath(); X.moveTo(px+6,py+6); X.lineTo(px+T-6,py+T-6);
X.moveTo(px+T-6,py+6); X.lineTo(px+6,py+T-6); X.stroke();
// Amber glow hint
X.strokeStyle='rgba(200,120,30,0.2)'; X.lineWidth=1;
X.strokeRect(px+1,py+1,T-2,T-2);
```

**Door (DOOR_D) -- geometric panel treatment:**
Door tiles currently render as a fillRect with a centered lock/cross icon. Refined to:
1. A recessed panel look -- inner rectangle slightly inset from tile edges, with a
   subtle border.
2. **Locked state:** The seal icon sits within the panel, surrounded by a warm gold
   border (`#B08030`) with amber glow (`rgba(180,120,40,0.4)`). The border is drawn as a
   rounded rectangle path, not a fillRect.
3. **Open state:** The panel glows Seafoam (`rgba(92,179,175,0.4)`) with a chevron
   arrow in Seafoam (`#5CB3AF`). The inner panel border uses Seafoam instead of gold.

```
// Locked door
const pad=4;
X.fillStyle='#1A1520'; X.fillRect(px+pad,py+pad,T-pad*2,T-pad*2);
X.strokeStyle='#B08030'; X.lineWidth=2;
X.strokeRect(px+pad,py+pad,T-pad*2,T-pad*2);
// Seal glow
X.fillStyle='rgba(180,120,40,'+pulse*0.4+')';
X.beginPath(); X.arc(px+T/2,py+T/2,6,0,Math.PI*2); X.fill();
// Lock icon
X.fillStyle='#B08030'; X.font='14px serif'; X.textAlign='center'; X.textBaseline='middle';
X.fillText('\u{1F512}', px+T/2, py+T/2);

// Open door
X.fillStyle='rgba(92,179,175,'+pulse*0.4+')';
X.fillRect(px+pad,py+pad,T-pad*2,T-pad*2);
X.strokeStyle='#5CB3AF'; X.lineWidth=2;
X.strokeRect(px+pad,py+pad,T-pad*2,T-pad*2);
X.fillStyle='#5CB3AF'; X.font='16px serif'; X.textAlign='center'; X.textBaseline='middle';
X.fillText('\u279C', px+T/2, py+T/2);
```

**Estimated lines added:** ~40-50 across render() for the geometry refinements.
Most tiles gain 3-8 additional path commands. No new data structures needed.

### 2.9 Death/Respawn Animation Theming

The death/respawn animation system (`golem.html` Section 9.5 — animation state machine)
renders the golem dissolving into clay particles and reforming bottom-up. Themed updates:

**Death animation (dying state):**
- Clay particles: use `PARTICLE_COLORS.death` (`#8B7D6B`) -- already references the constant
- Head/torso/arm/leg spread: no color changes (uses `COLORS.golem`, `COLORS.golemDark`, `COLORS.golemEye`)
- Alpha fade remains unchanged

**Respawn animation (respawning state):**
- Clay pile at feet: color `rgba(138,125,107,...)` becomes `rgba(139,125,107,...)` (matching warm clay)
- Reforming particles: hardcoded `#8a7d6b` (line 1286) becomes `#8B7D6B` (warm clay) or references `PARTICLE_COLORS.death`
- Final activation flash: `#f0d060` becomes `#C5B391` (Champagne) for consistency
- Glyph lines on body during respawn: use Hebrew letters (matching Section 2.4) instead of fillRect bars

**Lines added:** ~5 color replacements in `renderDeathRespawnAnimation()`.

### 2.10 Golem Movement Animations (lightweight)

The current golem has basic squash-and-stretch during movement (push, jump, fall, ground
run). The following lightweight refinements add character without new data structures or
state machines. All changes are render-only, applied within the existing golem draw block
in `render()`.

**Idle sway (subtle breathing):**
When `P.vx` is near zero and `P.onGround`, apply a 1px vertical offset to the head
using `sin(now/800) * 1`. This gives the golem a barely-perceptible "breathing" presence
when stationary -- alive clay rather than inert block.

**Land impact squish:**
After landing (detected via `P.onGround` becoming true with `P.vy` previously positive),
apply a brief vertical squash for 8-12 frames: increase height by 2px, decrease width
by 2px, offset Y upward by 1px. Decay over the landing frames. Uses a simple frame
counter on the existing `P.coyoteTime` -- no new state needed.

**Turn anticipation:**
When `P.facing` flips (detected via `P.facing !== prevFacing`), lean the body 2px
toward the new direction for 6-8 frames before committing to full movement. This
creates a subtle "weight shift" that communicates direction change.

**Airborne trail particles:**
During sustained airtime (`P.onGround` false for >30 frames), emit a single clay
particle every 10 frames from the golem's feet position, colored at `rgba(139,125,107,0.3)`.
Stops when landing. Uses the existing `Particles.spawn()` -- no new system.

**Coyote time visual hint:**
During coyote time (`P.coyoteTime > 0` after leaving ground), render a faint dust puff
at the edge the golem walked off. Single `fillRect` at `rgba(139,125,107,0.2)` fading
over 12 frames. Communicates the "just left ground" window without HUD text.

**Landing dust:**
On landing from >4px fall (`prevY + P.h < landingY - 4`), spawn 3-4 warm clay particles
(`PARTICLE_COLORS.jump`) at feet position. Already partially implemented for platform
landings (line 1111) -- extend to ground landings.

**Implementation notes:**
- No new game state variables. All detection uses existing flags (`P.onGround`,
  `P.coyoteTime`, `P.vx`, `P.facing`, `P.vy`).
- Frame counters for transient effects (land squish, turn lean) can use existing
  `animFrame` modulo or small local `let` variables in render scope.
- Particle effects reuse `Particles.spawn()` with existing color constants.
- Total: ~20-30 lines added to the golem render block inside `render()`.
- No performance impact -- all changes are conditional draws within the existing
  per-frame render loop.

---

## 3. UI DESIGN

### 3.1 Current HUD Layout (to preserve)

```
+--------------------------------------------------+
| Glyphs: X/4                                      |
| [1] Double Jump      (left-aligned, top-left)    |
| [2] Dash (Shift)     (stacked below)             |
| [3] Push Blocks                                            |
| [4] Break Cracked                                          |
|                          Chamber Name (center-bottom)      |
+--------------------------------------------------+
```

### 3.2 Themed HUD (immediate -- minimal changes)

The current HUD is functional. Themed version adds visual polish without restructuring:

- **Background panel:** Semi-transparent Midnight Indigo panel behind HUD text
  (`rgba(18,18,31,0.85)`)
- **Glyph counter:** Displays collected letters instead of numbers
  `Glyphs: \u05d0\u05de / \u05e2\u05de\u05ea` (Aleph-Mem collected out of EMET)
- **Ability text color:** Seafoam (`#5CB3AF`) for unlocked, Muted Champagne (`#A18F75`)
  for locked -- replaces current `#8f8` / `#444`
- **Chamber name:** `FONT_DISPLAY` italic, Muted Champagne color
- **Portal status icons:** Replaced with text -- "\u{1F512} Sealed" / "\u2714 Open"
  styled with Seafoam for open, Muted Champagne for sealed
- **Ability labels:** Current key-bind labels (`[1] Double Jump`, `[2] Dash (Shift)`, etc.)
  are unchanged. The `ABILITIES` array structure and text remain as-is; only the text
  colors change per the unlock state rules above.

**Lines added:** ~10 (panel fillRect, color changes, text format).

### 3.3 Extended HUD Bar (future feature)

When the dedicated UI bar above the game canvas is implemented:

```
+--------------------------------------------------+
| [\u05d0] [\u05de] [ ] [ ]             Timer: 02:34  |
| Dbl Jump  Dash  Push  Break    Deaths: 3        |
+--------------------------------------------------+
|                                                    |
|                    CANVAS                           |
|                                                    |
+--------------------------------------------------+
```

- **Bar height:** 48px (8px grid: 6 units)
- **Background:** Midnight Indigo (`#12121F`)
- **Divider line:** Champagne at 20% opacity, separates bar from canvas
- **Left side -- Glyphs & abilities:**
  - Row 1: Four 32x32 glyph slots. Collected = filled with Hebrew letter in
    Champagne. Uncollected = dim border (`rgba(197,179,145,0.2)`).
  - Row 2: Ability labels in `FONT_UI` 11px. Unlocked = Seafoam (`#5CB3AF`).
    Locked = Muted Champagne (`#A18F75`).
- **Right side -- Stats:**
  - Row 1: Timer in Soft White (`#E8E8F0`), monospace, 12px.
  - Row 2: Death count in Muted Champagne (`#A18F75`), 12px.
- **No persistent branding.** The Tholem Labs mark appears only on the Title Menu.

This feature requires HTML structure changes (a div above the canvas). Deferred.
Stays within single-file scope — markup lives in `golem.html`, not a separate template.

### 3.4 Tholem logo (inline SVG)

The Tholem Labs mark appears **only** on the title menu (Section 4.1), not in the in-game
HUD (Section 3.3). It must be embedded as **inline SVG** inside `golem.html` — no external
`.svg` file, no `<img src="…">`, no CDN fetch. This preserves offline standalone play per
`docs/Project-Constraints.md` ("no external assets").

#### Prepare the SVG

1. Open the logo `.svg` in a text editor, or export from Inkscape (**File → Save As →
   Optimized SVG**).
2. Minify with [SVGOMG](https://jakearchibald.github.io/svgomg/) to strip metadata and
   reduce inline size.
3. Set `fill="currentColor"` (or Champagne `#C5B391`) on paths if the mark should inherit
   overlay text color or stay on-brand.
4. Give the root element `id="tholem-logo"` for CSS/JS targeting.

#### HTML shell (required for overlays)

Wrap the existing canvas in a relatively positioned container. The game canvas remains
`<canvas id="c">` at 800×480 — do not change id or internal resolution.

```html
<body>
<div id="game-shell" style="position:relative;">
  <canvas id="c"></canvas>

  <!-- Hidden until title menu (Phase 6); also usable on pause menu -->
  <div id="logo-container" style="position:absolute; top:15px; left:15px; z-index:10; display:none;">
    <svg id="tholem-logo" width="180" height="50" viewBox="0 0 180 50" fill="none"
         xmlns="http://www.w3.org/2000/svg" aria-label="Tholem Labs">
      <!-- Paste optimized SVG paths here -->
    </svg>
  </div>

  <!-- Phase 6: #title-menu overlay; Phase 7: #pause-menu overlay — same shell -->
</div>
```

#### Option A — HTML overlay (recommended)

Use for **title menu and pause menu**. The logo sits above the canvas via CSS; the canvas
loop can stay paused while the menu is visible. Toggle `#logo-container` visibility with
the title/pause state (`display:block` on title, optional on pause).

#### Option B — Draw onto canvas (optional)

Use only if the mark must appear **during gameplay** on the canvas bitmap (not planned for
v1). Convert inline SVG to an image and draw after init:

```javascript
const logoEl = document.getElementById('tholem-logo');
const logo = new Image();
logo.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(logoEl.outerHTML)));
logo.onload = () => { X.drawImage(logo, 20, 20, 160, 45); };
```

Prefer Option A for title/pause; Option B adds encoding edge cases and is unnecessary for
current scope.

#### Quick tips

- Minify SVG before paste — large path data inflates `golem.html` size.
- Use `currentColor` in SVG for themeable marks; set `color:#C5B391` on `#logo-container`.
- Do not reference logo files by URL — breaks `file://` and single-file deployment.
- Parent `#game-shell` must have `position:relative` so absolute logo/menu layers align to
  the canvas, not the viewport.

**Lines added (Phase 6):** ~15–25 for shell wrapper + inline SVG + show/hide toggle (SVG
path data excluded from estimate).

---

## 4. SCREENS

### 4.1 Title Menu (future feature)

```
+--------------------------------------------------+
|                                                    |
|                                                    |
|              [Tholem Labs logo / mark]             |
|                                                    |
|           THE GOLEM AWAKENS                         |
|                                                    |
|      "What Thoth began, the clay completes."       |
|                                                    |
|                                                    |
|                  [Start Game]                       |
|                                                    |
|                  [Sound: ON/OFF]                    |
|                                                    |
|            Powered by Tholem Labs                   |
|                                                    |
+--------------------------------------------------+
```

**Visual treatment:**
- Background: Obsidian (`#0A0A12`)
- Subtle geometric rune overlay at 8% opacity (Champagne lines)
- Title: `FONT_DISPLAY` bold 48px, Champagne (`#C5B391`)
- Subtitle: `FONT_DISPLAY` italic 16px, Muted Champagne
- Start button: Seafoam outline, 1.75px stroke, 24px height, round caps
- Tholem Labs logo: inline SVG staff + ribbon mark in Champagne (Section 3.4) — centered
  above title, not fetched from an external file
- EMET letters (`\u05e2\u05de\u05ea`) subtly visible as background watermark at 6% opacity

**Implementation:** `#game-shell` wrapper with `#title-menu` overlay (Section 3.4). Show
`#logo-container` while menu visible; pause canvas update loop (`gameState = 'title'`).
~60 lines HTML + CSS + state toggle (excluding SVG path payload).

### 4.2 Pause Menu (future feature)

- Triggered by **`P` key** (aligns with `ROADMAP.md` pause toggle; not yet implemented)
- Semi-transparent Midnight Indigo overlay over canvas (`rgba(18,18,31,0.9)`)
- Centered panel with:
  - "PAUSED" title in `FONT_DISPLAY`, Champagne
  - "Resume" button (Seafoam outline) — same as pressing `P` again
  - "Return to Title" button (Muted Champagne outline) — resets game logic
  - "Sound: ON/OFF" toggle (when Phase 10 audio exists)
- Optional small Tholem mark: reuse `#logo-container` at reduced opacity (Section 3.4)

**Implementation:** Overlay div inside `#game-shell`, `P` key handler, `gameState = 'paused'`.
Skip `update()` while paused; keep `render()` for dimmed game view. ~40 lines.

### 4.3 Ending Screen (redesign)

**Current (runtime):** Static overlay in `render()` when `gameState === 'ending'`: title
"Awakening of the Golem", Ibis quote, "Refresh to play again". `transitionEnding()` fires
a single `showMessage()` — see Section 9 code map. Phase 5 replaces this with the themed
sequence below.

**Themed animated ending:**

1. **Phase 1 (0-2s):** Screen fades to Obsidian. The golem renders centered, all four
   Hebrew letters visible on its body, gently pulsing in Champagne.

2. **Phase 2 (2-4s):** The four letters detach and float upward from the golem's body,
   orbiting above its head in a slow rotation.

3. **Phase 3 (4-6s):** The letters converge onto the golem's forehead, forming EMET
   (`\u05e2\u05de\u05ea`) horizontally. A Champagne flash radiates outward.

4. **Phase 4 (6-8s):** The flash resolves. The golem stands still, EMET glowing on its
   forehead. The narrative text appears below in `FONT_DISPLAY` italic:

   > "What Thoth began, the clay completed itself."
   > "You are the Golem of Truth."

5. **Phase 5 (8s+):** Stats line appears below:
   Time: XX:XX | Deaths: X

6. **Phase 6:** "Play Again" button (Seafoam outline). Click resets game state.

**Implementation approach:**
- Reuse existing golem render function with a "hero" mode (larger, centered)
- Letter orbit animation: simple circular path using `sin/cos` with time parameter
- Convergence animation: lerp letter positions from orbit to forehead
- Text phases: use messageQueue with timed reveals
- Play Again: `location.reload()` or reset all game state

**Lines added:** ~80-100 for ending sequence (new render function + animation state machine).

---

## 5. RESPONSIVE CANVAS (future feature)

**Current:** Fixed 800x480 canvas, no scaling.

**Change:** Add CSS rule to scale canvas to fit viewport while maintaining internal resolution:

```css
canvas {
  max-width: 100vw;
  max-height: 100vh;
  object-fit: contain;
}
```

**Implementation:** Replace existing CSS block (lines 6-9) with expanded style. Wrap
`<canvas id="c">` in `#game-shell` when overlay UI lands (Phase 6+); Phase 9 CSS applies
to `#game-shell` / `#c` as below.

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: #0A0A12;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  overflow: hidden;
  font-family: system-ui, sans-serif;
}
#game-shell { position: relative; }
canvas {
  display: block;
  image-rendering: pixelated;
  max-width: 100vw;
  max-height: 100vh;
  object-fit: contain;
}
```

**Lines added:** ~8 CSS rules (including `#game-shell`). Body font matches `FONT_UI` (Section 2.2).

---

## 6. AUDIO (future feature)

### 6.1 Design Philosophy

All audio is generated in-code using the Web Audio API -- no external files, no `<audio>`
tags. Sounds are themed around the Temple of Thoth: clay, stone, sacred resonance, and
ancient mystery. The audio system uses three primitive sound types mapped to the game's
narrative dimensions:

| Primitive   | Waveform     | Narrative role                          | Examples                          |
|-------------|--------------|-----------------------------------------|-----------------------------------|
| Stone       | Triangle     | Structure, weight, the physical temple  | Push blocks, footstep, cracked break |
| Breath      | Square sweep | Movement, life entering clay            | Jump, double jump, dash           |
| Spirit      | Sine chord   | Magic, glyphs, Thoth's presence         | Glyph collect, door unlock, ending |
| Dust        | Filtered noise | Dissolution, impact, crumbling        | Death, hit walls, break cracked   |

**Volume discipline:** Sound effects peak at 0.06--0.10. Background music stays at 0.02--0.04.
The temple should feel vast and hollow -- sounds echo slightly but never compete.

### 6.2 Sound Engine Architecture

Single IIFE module with three layers: config data, primitives, and themed presets.
Data-driven approach keeps the module compact -- adding a sound is one config entry.

**Layer 1 -- Config data (sound definitions as data, not functions):**

```javascript
// Sound presets: {freq, dur, type, vol} for oscillator sounds
const SFX = {
  step:       { freq: 80,  dur: 0.06, type: 'triangle', vol: 0.04 },
  jump:       { freq: 180, dur: 0.12, type: 'square',   vol: 0.06 },
  doubleJump: { freq: 320, dur: 0.14, type: 'square',   vol: 0.06 },
  dash:       { freq: 200, dur: 0.08, type: 'sawtooth', vol: 0.04 },
  push:       { freq: 100, dur: 0.12, type: 'triangle', vol: 0.05 },
  breakWall:  { freq: 80,  dur: 0.2,  type: 'sawtooth', vol: 0.06 },
  glyph:      { freq: 0,   dur: 0,    type: 0,          vol: 0 },  // special: chord
  door:       { freq: 0,   dur: 0,    type: 0,          vol: 0 },  // special: sweep
  death:      { freq: 0,   dur: 0,    type: 0,          vol: 0 },  // special: descending chord
  hitWall:    { freq: 0,   dur: 0,    type: 0,          vol: 0 },  // special: noise burst
};
```

**Layer 2 -- Primitives (one oscillator, one sweep, one noise):**

```javascript
const Audio = (function(){
  let ctx, masterGain, noiseBuffer;
  let muted = false;

  // --- Init ---
  function init() {
    if (ctx) { ctx.resume(); return; }
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    masterGain = ctx.createGain();
    masterGain.gain.value = 1;
    masterGain.connect(ctx.destination);
    // Noise buffer created lazily on first use
  }

  function ensureNoise() {
    if (noiseBuffer) return;
    const size = ctx.sampleRate * 2;
    noiseBuffer = ctx.createBuffer(1, size, ctx.sampleRate);
    const d = noiseBuffer.getChannelData(0);
    for (let i = 0; i < size; i++) d[i] = Math.random() * 2 - 1;
  }

  // --- Primitives ---
  function tone(freq, dur, type, vol) {
    if (!ctx || muted) return;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = type;
    o.frequency.value = freq;
    const t = ctx.currentTime;
    g.gain.setValueAtTime(vol, t);
    g.gain.linearRampToValueAtTime(0.001, t + dur);
    o.connect(g); g.connect(masterGain);
    o.start(t); o.stop(t + dur);
  }

  function sweep(from, to, dur, type, vol) {
    if (!ctx || muted) return;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = type;
    const t = ctx.currentTime;
    o.frequency.setValueAtTime(from, t);
    o.frequency.linearRampToValueAtTime(to, t + dur);
    g.gain.setValueAtTime(vol, t);
    g.gain.linearRampToValueAtTime(0.001, t + dur);
    o.connect(g); g.connect(masterGain);
    o.start(t); o.stop(t + dur);
  }

  function noise(dur, vol, filterFreq) {
    if (!ctx || muted) return;
    ensureNoise();
    const s = ctx.createBufferSource();
    s.buffer = noiseBuffer;
    const f = ctx.createBiquadFilter();
    f.type = 'lowpass'; f.frequency.value = filterFreq || 1200;
    const g = ctx.createGain();
    const t = ctx.currentTime;
    g.gain.setValueAtTime(vol, t);
    g.gain.linearRampToValueAtTime(0.001, t + dur);
    s.connect(f); f.connect(g); g.connect(masterGain);
    s.start(t); s.stop(t + dur);
  }

  // --- Themed presets ---
  // Movement
  function step()         { tone(80,  0.06, 'triangle', 0.04); }
  function jump()         { sweep(180, 420, 0.12, 'square', 0.06); }
  function doubleJump()   { sweep(260, 580, 0.15, 'square', 0.06); }
  function dash()         { sweep(400, 120, 0.1,  'sawtooth', 0.04); }

  // Interaction
  function push()         { tone(100, 0.12, 'triangle', 0.05); }
  function breakWall()    { noise(0.18, 0.06, 600); tone(80, 0.15, 'sawtooth', 0.04); }
  function hitWall()      { noise(0.08, 0.04, 2000); }

  // Sacred -- glyphs use ascending two-note chords (E-Dorian pentatonic: E G# A B D)
  function glyph() {
    if (!ctx || muted) return;
    tone(330, 0.3, 'sine', 0.07);   // E4 -- base
    tone(494, 0.25, 'sine', 0.05);  // B4 -- fifth, slightly shorter
  }

  // Door unlock -- descending sweep with resonance
  function door() {
    if (!ctx || muted) return;
    sweep(600, 200, 0.3, 'sine', 0.05);
    tone(165, 0.4, 'sine', 0.03);   // E3 -- lingering fundamental
  }

  // Death -- descending chord, like clay collapsing
  function death() {
    if (!ctx || muted) return;
    tone(220, 0.5, 'sine', 0.06);   // A3
    tone(165, 0.6, 'sine', 0.04);   // E3 -- lower, longer
    noise(0.3, 0.04, 400);          // dust settling
  }

  // --- Public API ---
  return {
    init,
    mute: () => { muted = true; },
    unmute: () => { muted = false; },
    toggleMute: () => { muted = !muted; return muted; },
    step, jump, doubleJump, dash, push, breakWall, hitWall, glyph, door, death,
  };
})();
```

### 6.3 Sound Event Mapping

Each game event triggers exactly one sound call. No new event detection is needed --
calls are inserted at existing game logic points:

| Event             | Narrative role                        | Sound            | Waveform character              |
|-------------------|---------------------------------------|------------------|---------------------------------|
| Jump              | Clay finds lift -- breath entering    | `Audio.jump()`   | Square sweep up (180->420 Hz)   |
| Double jump       | Aleph power -- deeper breath          | `Audio.doubleJump()` | Square sweep up (260->580 Hz) |
| Dash execute      | Mem power -- water rushing through    | `Audio.dash()`   | Sawtooth sweep down (400->120)  |
| Push block        | He power -- spirit meets stone        | `Audio.push()`   | Triangle tone, 100 Hz           |
| Break cracked     | Tav power -- seal shatters clay       | `Audio.breakWall()` | Noise burst + low sawtooth   |
| Hit wall/obstacle | Clay strikes unyielding stone         | `Audio.hitWall()` | High noise burst (2000 Hz)     |
| Glyph collect     | Letter of Truth enters the golem      | `Audio.glyph()`  | Sine chord (E4 + B4)           |
| Door unlock       | Path opens -- Thoth permits passage   | `Audio.door()`   | Descending sine + fundamental   |
| Death             | Clay returns to dust                  | `Audio.death()`  | Descending chord + dust noise   |
| Footstep (optional)| Golem walks on temple stone          | `Audio.step()`   | Triangle tap, 80 Hz             |

### 6.4 Call Site Locations

Inserted at existing game event points (line numbers approximate, based on current
`golem.html` structure):

| Event             | Function / location                    | Insert call             |
|-------------------|----------------------------------------|-------------------------|
| Jump              | `update()` -- velocity flip            | `Audio.jump()`          |
| Double jump       | `update()` -- second jump branch      | `Audio.doubleJump()`    |
| Dash execute      | `update()` -- dash active frame        | `Audio.dash()` (once)   |
| Push block        | `resolvePushBlockCollision()`          | `Audio.push()`          |
| Break cracked     | `update()` -- cracked wall destroy     | `Audio.breakWall()`     |
| Hit wall          | Collision response (optional)          | `Audio.hitWall()`       |
| Glyph collect     | `checkGlyphs()` -- glyph removed       | `Audio.glyph()`         |
| Door transition   | Chamber transition via DOOR_D          | `Audio.door()`          |
| Death             | `killAndRespawn()`                     | `Audio.death()`         |

**Implementation note:** Dash sound should fire only once per dash activation, not every
frame. Use a flag (`_dashPlayed`) cleared on dash cooldown reset.

### 6.5 Audio Initialization

Browsers require a user gesture before AudioContext can produce sound. The init call
fires on the first keydown or click:

```javascript
document.addEventListener('keydown', () => Audio.init(), { once: true });
document.addEventListener('click', () => Audio.init(), { once: true });
```

This is called once at page load (before the game loop) and covers the browser autoplay
policy. If the user never interacts, no audio plays -- no error is thrown.

### 6.6 Background Ambient Sound

The temple should hum with presence. A layered ambient drone runs continuously during
gameplay, providing atmospheric depth without melody.

**Design: Temple drone**

Three layers create the impression of a vast, hollow chamber with distant resonance:

| Layer       | Frequency | Waveform | Volume | Character                    |
|-------------|-----------|----------|--------|------------------------------|
| Fundamental | 55 Hz     | Sine     | 0.025  | Sub-bass hum -- chamber body |
| Fifth       | 82.5 Hz   | Sine     | 0.015  | A2 -- harmonic support       |
| Shimmer     | 220 Hz    | Sine     | 0.008  | A3 -- barely audible presence|

All three notes are A-based (A1-A2-A3), creating a pure, static drone. No movement,
no rhythm -- just the feeling of standing inside something ancient.

**Chamber variation (optional, Phase 9b):** The fundamental can shift per chamber to
reflect narrative progression:

| Chamber | Fundamental | Fifth  | Shimmer | Mood                |
|---------|-------------|--------|---------|---------------------|
| 0-1     | 55 Hz (A1)  | 82.5   | 220     | Awakening -- stable |
| 2       | 65.4 Hz (C2)| 98     | 261.6   | Reflection -- rising|
| 3       | 49 Hz (G1)  | 73.4   | 196     | Burden -- lower     |
| 4       | 55 Hz (A1)  | 82.5   | 440     | Completion -- higher shimmer |

**Implementation:**

```javascript
let droneOscs = [];

function startDrone() {
  if (!ctx || muted) return;
  stopDrone();
  const notes = [55, 82.5, 220];
  const vols  = [0.025, 0.015, 0.008];
  notes.forEach((freq, i) => {
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine';
    o.frequency.value = freq;
    g.gain.value = vols[i];
    o.connect(g); g.connect(masterGain);
    o.start();
    droneOscs.push({ osc: o, gain: g });
  });
}

function stopDrone() {
  droneOscs.forEach(d => { d.osc.stop(); });
  droneOscs = [];
}
```

`startDrone()` is called on game start (after first user gesture). `stopDrone()` on
pause or game end. The drone oscillators are long-lived nodes -- created once, stopped
when no longer needed.

### 6.7 Optional: Simple Melodic Loop (Phase 9b)

A sparse, repeating melodic phrase adds character without complexity. Designed to
evoke ancient Egyptian modal music -- pentatonic, slow, meditative.

**Scale: E Dorian pentatonic** (E F# G# B C#) -- a modal flavor between minor and
mysterious, fitting for Thoth's temple.

**Phrase (4 notes, 2-second cycle):**

| Beat | Note | Freq | Type   | Vol  | Character          |
|------|------|------|--------|------|--------------------|
| 0.0  | G#4  | 415  | Sine   | 0.03 | Question -- where? |
| 0.5  | B4   | 494  | Sine   | 0.025| Rising -- ascent   |
| 1.0  | A4   | 440  | Sine   | 0.025| Resolution -- home |
| 1.5  | E4   | 330  | Sine   | 0.03 | Answer -- truth    |

Each note holds for 0.45s with a 0.05s gap between notes -- deliberate space between
sounds, like a voice in a large chamber.

**Implementation (scheduled, not setInterval -- avoids drift):**

```javascript
let musicPlaying = false;
let musicTimer = null;

const MELODY = [
  { freq: 415, time: 0.0 },
  { freq: 494, time: 0.5 },
  { freq: 440, time: 1.0 },
  { freq: 330, time: 1.5 },
];
const MELODY_CYCLE = 2.0; // seconds per loop

function startMusic() {
  if (musicPlaying || !ctx) return;
  musicPlaying = true;
  scheduleMusic();
}

function scheduleMusic() {
  if (!musicPlaying) return;
  const t = ctx.currentTime;
  MELODY.forEach(n => {
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine';
    o.frequency.value = n.freq;
    const start = t + n.time;
    g.gain.setValueAtTime(0, start);
    g.gain.linearRampToValueAtTime(0.025, start + 0.05); // fade in
    g.gain.setValueAtTime(0.025, start + 0.40);
    g.gain.linearRampToValueAtTime(0.001, start + 0.48); // fade out
    o.connect(g); g.connect(masterGain);
    o.start(start); o.stop(start + 0.5);
  });
  musicTimer = setTimeout(scheduleMusic, MELODY_CYCLE * 1000);
}

function stopMusic() {
  musicPlaying = false;
  if (musicTimer) { clearTimeout(musicTimer); musicTimer = null; }
}
```

**Integration:** `startMusic()` called alongside `startDrone()` on game start.
`stopMusic()` on pause/end. The melody plays over the drone -- together they create
the temple soundscape.

### 6.8 Mute and Toggle

Sound state is managed through three exposed methods:

- `Audio.toggleMute()` -- returns new muted state (true = muted)
- `Audio.mute()` / `Audio.unmute()` -- explicit set
- Stops both SFX and music (drone + melody)

Toggle binding (optional, for pause menu or hotkey):

```javascript
// 'M' key toggles sound
if (e.key.toLowerCase() === 'm') {
  const isMuted = Audio.toggleMute();
  if (isMuted) { stopDrone(); stopMusic(); }
  else { startDrone(); startMusic(); }
}
```

### 6.9 Estimated Lines

| Component              | Lines  |
|------------------------|--------|
| Audio IIFE (primitives + presets + drone) | ~80 |
| Music scheduler         | ~25    |
| Call site inserts        | ~10    |
| Init listener            | ~2     |
| Mute toggle handler      | ~5     |
| **Total**               | **~120** |

Phased approach: Phase 9a adds SFX only (~60 lines). Phase 9b adds drone + melody
(~60 lines additional).

---

## 7. IMPLEMENTATION ORDER

Priority-ordered, each scoped as a self-contained change:

### Phase 1: Color & Text Polish (immediate, ~38 lines)
0. Add `FONT_UI`, `FONT_DISPLAY`, `FONT_HEBREW` constants; update all `X.font` strings (Section 2.2)
1. Update `COLORS` object with palette values (including Cosmic Purple)
2. Update particle colors (dash -> Cosmic Purple)
3. Update `DASH_EXEC_PARTICLE_COLOR` and `DASH_CHARGE_PARTICLE_COLOR` constants
4. Update death/respawn messages
5. Update glyph collect messages
6. Update initial awakening message
7. Update chamber names in `CHAMBER_NAMES` array
8. Update HUD text colors and font strings
9. Update door/portal render colors
10. Update magical wall render colors (Cosmic Purple)
11. Update background starfield color
12. Update death/respawn animation colors (see Section 2.9)

### Phase 2: Glyph Visuals (~15 lines)
1. Replace glyph cross render with Hebrew letter + diamond halo
2. Replace golem body glyph lines with Hebrew letters
3. Update glyph collect particle color

### Phase 3: Background Runes (~15 lines)
1. Add subtle geometric rune overlay to render loop
2. Ensure 6-8% opacity maximum

### Phase 4: Asset Geometry (~45 lines)
1. Wall beveled top edge (trapezoid path)
2. Platform chamfered edges
3. Pit diagonal crack lines (warm amber glow)
4. Cracked wall beveled edges + X-pattern crack lines + amber breakable glow
5. Door (DOOR_D) geometric panel: recessed inner panel, gold border (locked), Seafoam border (open)
6. Golem rounded shoulders + defined feet
7. Push block rounded corners
8. Push effort visual (Champagne arm lines)
9. Glyph diamond halo
10. Dash charge angular segments
11. Magical wall hexagonal core

### Phase 4.5: Golem Movement Animations (~20-30 lines)
See Section 2.10 for details.

### Phase 5: Ending Screen (~80-100 lines)
1. Rewrite `transitionEnding()` to trigger animated sequence
2. New ending render function with golem center, letter orbit, convergence
3. Multi-phase text reveal
4. Play Again button (reload)

### Phase 6: Title Menu (~60 lines) -- future
1. Add `#game-shell` wrapper and `#title-menu` overlay (Section 3.4)
2. Embed inline Tholem SVG in `#logo-container`; minify with SVGOMG before paste
3. CSS styling with brand colors and system fonts (Section 2.2)
4. `gameState = 'title'` state; hide logo/menu when playing
5. Start Game button transitions to `gameState = 'playing'`
6. Sound toggle in menu (when Phase 10 audio exists)

### Phase 7: Pause Menu (~40 lines) -- future
1. **`P` key** handler (per `ROADMAP.md`)
2. Pause overlay div inside `#game-shell`
3. Resume / Return to Title buttons
4. Game state freeze: skip `update()`, keep `render()`

### Phase 8: Extended HUD Bar (~40 lines) -- future
1. HTML div above canvas
2. Timer counter in update loop
3. Death counter
4. Glyph slot display with letters

### Phase 9: Responsive Canvas (~6 lines) -- future
1. CSS update in style block (Section 5, include `#game-shell`)

### Phase 10a: Sound Effects (~60 lines) -- future
1. Audio IIFE module with primitives (tone, sweep, noise)
2. Themed sound presets (jump, doubleJump, dash, push, breakWall, glyph, door, death)
3. Call sites in update/checkGlyphs/killAndRespawn
4. Init listener on first keydown/click
5. Mute toggle support

### Phase 10b: Ambient Sound (~60 lines) -- future
1. Three-layer temple drone (fundamental + fifth + shimmer)
2. Optional chamber-specific drone variations
3. Simple melodic loop (E Dorian pentatonic, scheduled notes)
4. Mute toggle integration with drone/music start/stop
5. Sound toggle in title/pause menus

---

## 8. CONSTRAINTS & GUARDRAILS

1. **No gameplay changes:** Chamber grids, physics, collision, tile behavior, ability
   mechanics remain untouched.
2. **No architecture changes:** Single-file `golem.html` structure is preserved. New
   features added as IIFEs or appended code blocks following the existing numbered
   section convention.
3. **No tile type additions:** The 12 existing tile types are the only tiles. Visual
   changes are render-only.
4. **Chamber flow preserved:** `CHAMBER_FLOW` array and door/portal logic unchanged.
5. **Test chamber untouched:** Pressing T still enters test chamber with all abilities.
6. **Canvas resolution unchanged:** Internal 800x480 pixels, 32x32 tiles. CSS scaling
   only for display.
7. **Existing 9-step IIFE convention:** Any new modular code follows the established
   pattern (see `chamber-template.md`).
8. **Quality gates:** After implementation, verify with `python3 tools/chamber_diff.py`
   (if chambers were touched -- they should not be), browser console error check, and
   game load/run verification.
9. **Standalone deployment:** All deliverables remain in one `golem.html`. Verify load via
   `file://` (offline) and static HTTP host (online) with no console errors.
10. **Font policy:** System fonts only via `FONT_UI`, `FONT_DISPLAY`, `FONT_HEBREW` (Section 2.2).
    No CDN or `@font-face`.
11. **Logo policy:** Tholem mark is inline SVG only (Section 3.4). No external image or
    SVG file references.
12. **Scope boundary:** Phases marked "future" (menus, HUD bar, audio, responsive CSS) add
    HTML/CSS/JS inside `golem.html` only — not separate modules or asset folders unless
    governance approves an architecture change.

---

## 9. REFERENCE: CURRENT CODE MAP

For implementers -- key sections of `golem.html` and what they control.

**Note:** Line numbers below reflect `golem.html` at time of document creation. As phases
are implemented, line counts will shift. Use section header comments (e.g. `9. UPDATE`,
`10. RENDER`) as anchors rather than relying on exact line numbers.

| Lines    | Section                    | What to change for theming                     |
|----------|----------------------------|------------------------------------------------|
| 6-9      | CSS + `<canvas id="c">`    | Background color, `#game-shell`, responsive rules |
| 29-36    | Dash constants             | DASH_EXEC/CHARGE_PARTICLE_COLOR (Cosmic Purple) |
| 62-68    | PARTICLE_COLORS            | All particle colors                            |
| 71-76    | ABILITIES, CHAMBER_NAMES   | Chamber names (ability labels unchanged)       |
| 77-82    | GLYPH_EFFECTS              | Glyph collect messages                         |
| 935-942  | transitionEnding()         | Ending sequence trigger (Phase 5)              |
| ~1172    | killAndRespawn pit death   | Pit death message                              |
| ~1198    | showMessage('Clay reforms')| Death reform message                           |
| ~1214+   | COLORS object              | All visual colors                              |
| ~1224+   | renderDeathRespawnAnimation (Section 9.5) | Clay particles, activation flash (Section 2.9) |
| ~1383+   | render() tile rendering    | Tile colors, glyph visual, pit glow colors     |
| ~1415+   | DOOR_D render              | Door locked/open colors                        |
| ~1438+   | END_PORTAL render          | Portal colors                                  |
| ~1451+   | GLYPH render               | Glyph cross -> Hebrew letter                   |
| ~1472+   | MAGICAL_WALL render        | Purple -> Cosmic Purple colors                 |
| ~1516+   | Dash charge indicator      | Purple -> Cosmic Purple colors                 |
| ~1599+   | Golem body glyph lines     | fillRect -> Hebrew letter textFill             |
| ~1616+   | HUD rendering              | Colors, fonts (`FONT_*` constants), chamber name |
| ~1645+   | Message rendering          | Font, color                                    |
| ~1664+   | Ending screen render       | Complete rewrite for animated ending (Phase 5)   |
| ~1709    | Initial message            | Awakening message text                         |

---

## Appendix A: Hebrew Letters Reference

| Letter | Unicode | HTML Entity | Canvas String  |
|--------|---------|-------------|----------------|
| Aleph  | U+05D0  | `&#1488;`   | `'\u05d0'`     |
| Mem    | U+05DE  | `&#1502;`   | `'\u05de'`     |
| He     | U+05D4  | `&#1492;`   | `'\u05d4'`     |
| Tav    | U+05EA  | `&#1514;`   | `'\u05ea'`     |
| EMET   |         |             | `'\u05e2\u05de\u05ea'` |

Note: EMET uses Ayin (\u05e2), not Aleph (\u05d0), as its first letter. The first glyph
collected is Aleph (\u05d0) representing "breath" -- the first sound. This is intentional:
the golem starts with potential (Aleph/breath) and completes with the actual Word (EMET/Truth).
The journey transforms breath into truth.

## Appendix B: tholem.ai Design Principles Applied

- **Obsidian background:** Used for canvas body and all overlay backgrounds.
- **Champagne as primary accent:** Glyphs, golem eye, text, portal glow, particle highlights.
- **Seafoam as interactive accent:** Open doors, unlocked abilities, button outlines, ending accents.
- **Cosmic Purple for magic:** Dash particles, dash charge indicator, magical wall barriers.
  A game-specific color outside the core brand palette, justified by the mystical theme
  of the golem's hermetic initiation. Vivid violet (`#8B5CF6`) contrasts cleanly with
  Champagne and Seafoam on the dark Obsidian background.
- **Rune line work:** 6-8% opacity geometric background patterns, Champagne color.
- **Typography hierarchy:** `FONT_DISPLAY` for titles/quotes, `FONT_UI` for HUD, `FONT_HEBREW`
  for Hebrew letters (Section 2.2). System fonts only — no CDN.
- **Inline brand mark:** Tholem logo as embedded SVG in HTML, title/pause only (Section 3.4).
- **Standalone runtime:** Single `golem.html`; zero network dependencies for typography or assets.
- **Outline iconography:** Button strokes at ~1.75px, round caps, Seafoam tint.
- **8px grid:** HUD bar height (48px = 6x8), spacing multiples of 8.
- **Generous whitespace:** Title menu and ending screen use centered layout with wide margins.
- **Asset geometry:** Rectangular primitives refined with bevels, chamfers, rounded corners,
  and polygonal halos to establish a cohesive visual identity -- walls are sharp and fixed,
  push blocks are rounded and movable, glyphs are inscribed within diamonds, magical barriers
  pulse with hexagonal cores.
