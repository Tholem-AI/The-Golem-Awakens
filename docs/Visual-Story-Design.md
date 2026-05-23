# Visual and Story Design -- The Golem Awakens

## Purpose

Reference document for the visual and narrative overhaul of `golem.html`. All changes are
polish and theming only -- no gameplay mechanics, chamber layouts, or tile behavior is
modified. Line count additions are scoped to be minimal, enhancing the existing framework.

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
| 1       | Aleph   | \u05e0  | Ox / Breath     | "Knowledge lifts me."    | "The First breathes life."                |
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

### 2.1 Color Palette (Locked -- from tholem.ai)

All colors are mapped from the tholem.ai brand palette. Existing game colors are replaced
to achieve cohesive theming.

| Role                     | Name            | Hex       | Current Usage Mapping                                    |
|--------------------------|-----------------|-----------|----------------------------------------------------------|
| Background (primary)     | Obsidian        | `#0A0A12` | Canvas background (body CSS, currently `#0a0a0a`)        |
| Background (secondary)   | Midnight Indigo | `#12121F` | Chamber backdrop, HUD panel, message box background      |
| Brand gold               | Champagne       | `#C5B391` | Glyph glow, golem eye, text, accent highlights, portals  |
| Brand teal               | Seafoam         | `#5CB3AF` | Door portals (open state), learned ability indicators    |
| Track Differentiator     | Emerald         | `#059669` | END_PORTAL glow, ending sequence accents                 |
| Text (primary)           | Soft White      | `#E8E8F0` | HUD text, messages, UI labels                            |
| Text (secondary)         | Muted Champ     | `#A18F75` | Subheadings, chamber names, secondary HUD text           |

**Derived game-specific colors** (computed from palette):

| Element        | Color           | Rationale                                        |
|----------------|-----------------|--------------------------------------------------|
| Wall (base)    | `#1E1E30`       | Midnight Indigo brightened slightly for depth     |
| Wall (top)     | `#2A2A40`       | Subtle highlight on wall top edge                 |
| Platform       | `#2E2E42`       | Wall tone, slightly lighter for distinction       |
| Pit            | `#060608`       | Near-black, deeper than Obsidian                  |
| Pit (glow)     | `rgba(197,179,145,0.15)` | Champagne at low opacity -- void whispers gold |
| Golem (body)   | `#8B7D6B`       | Warm clay -- kept close to current                |
| Golem (shadow) | `#5A5040`       | Darker clay shadow -- kept close to current       |
| Golem (eye)    | `#C5B391`       | Champagne -- the spark of Thoth's fire            |
| Cracked wall   | `#6B4A3A`       | Warm earth tone, darker than current              |
| Magical wall   | `rgba(139,92,246,0.35)` | Cosmic Purple at low opacity |
| Magical wall (core) | `rgba(139,92,246,0.7)` | Cosmic Purple -- visible magical glow              |
| Push block     | `#3E3E52`       | Wall-derived, distinct from static walls          |
| Glyph (base)   | `#C5B391`       | Champagne -- the gold of Thoth                    |
| Glyph (glow)   | `rgba(197,179,145,0.4)` | Champagne glow halo                          |
| Door (locked)  | `rgba(161,143,117,0.4)` | Muted Champagne -- dim seal                  |
| Door (open)    | `rgba(92,179,175,0.6)`  | Seafoam -- passage opens                    |

**Cosmic Purple -- the magic accent**

The palette introduces **Cosmic Purple** as a game-specific color outside the core
tholem.ai brand set. It serves the magical/mystical dimension of the golem's journey:

| Role                          | Name            | Hex        | Usage                                      |
|-------------------------------|-----------------|------------|--------------------------------------------|
| Magic accent (dash, barriers) | Cosmic Purple   | `#8B5CF6`  | Dash execution particles, dash charge ring, magical wall glow, magical wall core spark |

Cosmic Purple is a vivid violet -- distinct from the brand Seafoam and Champagne. It
signals "active magic" without clashing: the palette's dark Obsidian/Midnight Indigo
background provides strong contrast, and purple sits between Champagne (gold) and
Seafoam (teal) on the color wheel, creating a triadic accent structure.

**Key principle:** Cosmic Purple replaces the current `rgba(220,120,255,0.4)` purple but
is more saturated and intentional (`#8B5CF6`). Dash particles become `rgba(139,92,246,0.5)`
for execution and `rgba(139,92,246,0.3)` for charge. Magical walls use `rgba(139,92,246,0.35)`
base fill and `rgba(139,92,246,0.7)` core glow.

### 2.2 Typography (Canvas rendering)

The canvas uses `X.fillText()` with font strings. Two font families are referenced:

| Element              | Font String                     | Weight/Style       |
|----------------------|---------------------------------|--------------------|
| HUD labels           | `14px 'Inter', monospace`       | Regular            |
| HUD ability list     | `11px 'Inter', monospace`       | Regular            |
| Chamber name (bottom)| `12px 'Inter', monospace`       | Medium             |
| Messages (center)    | `bold 18px 'Cormorant Garamond', serif` | SemiBold      |
| Ending title         | `bold 28px 'Cormorant Garamond', serif` | Bold (700)   |
| Ending quote         | `italic 22px 'Cormorant Garamond', serif` | Italic (500) |

**Implementation note:** Google Fonts can be loaded via a `<link>` tag in the HTML head
for Cormorant Garamond and Inter. This adds one `<link>` element. Fallback to system
serif/monospace is automatic.

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

**Lines added:** ~5 per glyph tile render block (replaces existing fillRect cross).

### 2.4 Golem Body Glyph Lines

Current implementation draws horizontal lines on the golem's body for each collected glyph.
These are replaced with the actual Hebrew letters, rendered vertically on the golem's torso:

```
X.fillStyle = 'rgba(197,179,145,' + alpha + ')';
X.font = '8px serif';
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

| Particle type     | Current Color              | New Color                      |
|-------------------|----------------------------|--------------------------------|
| Jump              | `#8a7d6b`                  | `#8B7D6B` (warm clay)          |
| Double Jump       | `#d4a84b`                  | `#C5B391` (Champagne)          |
| Glyph collect     | `#f0d060`                  | `#C5B391` (Champagne)          |
| Dash execution    | `rgba(220,120,255,0.6)`   | `rgba(139,92,246,0.5)` (Cosmic Purple) |
| Dash charge       | `rgba(180,80,255,0.4)`    | `rgba(139,92,246,0.3)` (Cosmic Purple) |
| Death             | `#8a7d6b`                  | `#8B7D6B` (warm clay)          |

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

**Pits -- angled void edges:**
Current pits render as black rects with a thin glow line on top. Refined to add subtle
diagonal "crack" lines descending into the void, rendered with `strokeStyle` at low
opacity Champagne. Two diagonal lines per pit tile, angled toward the pit center,
giving depth.

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

**Estimated lines added:** ~25-35 across render() for the geometry refinements.
Most tiles gain 3-6 additional path commands. No new data structures needed.

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
- **Chamber name:** Rendered in Cormorant Garamond italic with Muted Champagne color
- **Portal status icons:** Replaced with text -- "\u{1F512} Sealed" / "\u2714 Open"
  styled with Seafoam for open, Muted Champagne for sealed

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
  - Row 2: Ability labels in Inter 11px. Unlocked = Seafoam (`#5CB3AF`).
    Locked = Muted Champagne (`#A18F75`).
- **Right side -- Stats:**
  - Row 1: Timer in Soft White (`#E8E8F0`), monospace, 12px.
  - Row 2: Death count in Muted Champagne (`#A18F75`), 12px.
- **No persistent branding.** The Tholem Labs mark appears only on the Title Menu.

This feature requires HTML structure changes (a div above the canvas). Deferred.

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
- Title: Cormorant Garamond 700, 48px, Champagne (`#C5B391`)
- Subtitle: Cormorant Garamond italic 500, 16px, Muted Champagne
- Start button: Seafoam outline, 1.75px stroke, 24px height, round caps
- Tholem Labs logo: SVG staff + ribbon mark, Champagne
- EMET letters (`\u05e2\u05de\u05ea`) subtly visible as background watermark at 6% opacity

**Implementation:** Overlay div with absolute positioning over canvas. Canvas paused
while menu is visible. ~60 lines HTML + CSS + state toggle.

### 4.2 Pause Menu (future feature)

- Triggered by Escape key
- Semi-transparent Midnight Indigo overlay over canvas (`rgba(18,18,31,0.9)`)
- Centered panel with:
  - "PAUSED" title in Cormorant Garamond, Champagne
  - "Resume" button (Seafoam outline)
  - "Return to Title" button (Muted Champagne outline) -- resets game logic
  - "Sound: ON/OFF" toggle

**Implementation:** Overlay div, Escape key handler, `gameState = 'paused'`. ~40 lines.

### 4.3 Ending Screen (redesign)

**Current:** Static black overlay with text.

**Themed animated ending:**

1. **Phase 1 (0-2s):** Screen fades to Obsidian. The golem renders centered, all four
   Hebrew letters visible on its body, gently pulsing in Champagne.

2. **Phase 2 (2-4s):** The four letters detach and float upward from the golem's body,
   orbiting above its head in a slow rotation.

3. **Phase 3 (4-6s):** The letters converge onto the golem's forehead, forming EMET
   (`\u05e2\u05de\u05ea`) horizontally. A Champagne flash radiates outward.

4. **Phase 4 (6-8s):** The flash resolves. The golem stands still, EMET glowing on its
   forehead. The narrative text appears below in Cormorant Garamond italic:

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

**Implementation:** Replace existing CSS block (lines 6-9) with expanded style:

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: #0A0A12;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}
canvas {
  display: block;
  image-rendering: pixelated;
  max-width: 100vw;
  max-height: 100vh;
  object-fit: contain;
}
```

**Lines added:** ~6 CSS rules.

---

## 6. AUDIO (future feature)

### 6.1 Sound Engine

Web Audio API with oscillator-based sounds (no external files). Single IIFE module:

```javascript
const Audio = (function(){
  let ctx = null;
  let muted = false;

  function init() {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
  }

  function tone(freq, duration, type, volume) {
    if (!ctx || muted) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type || 'sine';
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(volume || 0.1, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + duration);
  }

  // Preset sounds
  function jump()      { tone(440, 0.1, 'square', 0.05); }
  function doubleJump(){ tone(660, 0.12, 'square', 0.05); }
  function glyph()     { tone(880, 0.3, 'sine', 0.08); tone(1100, 0.2, 'sine', 0.06); }
  function dash()      { tone(220, 0.08, 'sawtooth', 0.03); }
  function push()      { tone(150, 0.1, 'triangle', 0.05); }
  function break_()    { tone(100, 0.2, 'sawtooth', 0.06); }
  function death()     { tone(200, 0.4, 'sine', 0.08); tone(150, 0.5, 'sine', 0.06); }

  return { init, toggleMute: () => { muted = !muted; }, jump, doubleJump, glyph,
           dash, push, break: break_, death };
})();
```

### 6.2 Call Sites

Added at existing game event points (no new event detection needed):

| Event           | Current location                    | Audio call            |
|-----------------|--------------------------------------|-----------------------|
| Jump            | `update()` line ~1143/1150/1158     | `Audio.jump()`        |
| Double jump     | `update()` line ~1158               | `Audio.doubleJump()`  |
| Glyph collect   | `checkGlyphs()` line ~925           | `Audio.glyph()`       |
| Dash execute    | `update()` line ~1023               | `Audio.dash()`        |
| Push block      | `resolvePushBlockCollision()`        | `Audio.push()`        |
| Break cracked   | `update()` line ~1078               | `Audio.break()`       |
| Death           | `killAndRespawn()` line ~152        | `Audio.death()`       |

**Lines added:** ~50 for Audio IIFE + ~8 for call site inserts.

### 6.3 Ambient Music (optional)

A very low ambient drone during gameplay:
- 55 Hz sine wave at 0.02 volume (sub-bass hum, like a temple chamber)
- Starts on first user interaction (AudioContext requirement)
- Toggled with sound mute setting

---

## 7. IMPLEMENTATION ORDER

Priority-ordered, each scoped as a self-contained change:

### Phase 1: Color & Text Polish (immediate, ~30 lines)
1. Update `COLORS` object with palette values (including Cosmic Purple)
2. Update particle colors (dash -> Cosmic Purple)
3. Update death/respawn messages
4. Update glyph collect messages
5. Update initial awakening message
6. Update chamber names in `CHAMBER_NAMES` array
7. Update HUD text colors and font strings
8. Update door/portal render colors
9. Update magical wall render colors (Cosmic Purple)
10. Update background starfield color

### Phase 2: Glyph Visuals (~15 lines)
1. Replace glyph cross render with Hebrew letter + diamond halo
2. Replace golem body glyph lines with Hebrew letters
3. Update glyph collect particle color

### Phase 3: Background Runes (~15 lines)
1. Add subtle geometric rune overlay to render loop
2. Ensure 6-8% opacity maximum

### Phase 3.5: Asset Geometry (~25-35 lines)
1. Wall beveled top edge (trapezoid path)
2. Platform chamfered edges
3. Pit diagonal crack lines
4. Golem rounded shoulders + defined feet
5. Push block rounded corners
6. Glyph diamond halo
7. Dash charge angular segments
8. Magical wall hexagonal core

### Phase 4: Ending Screen (~80-100 lines)
1. Rewrite `transitionEnding()` to trigger animated sequence
2. New ending render function with golem center, letter orbit, convergence
3. Multi-phase text reveal
4. Play Again button (reload)

### Phase 5: Title Menu (~60 lines) -- future
1. HTML overlay div with menu elements
2. CSS styling with brand fonts and colors
3. `gameState = 'title'` state
4. Start Game button transitions to `gameState = 'playing'`
5. Sound toggle in menu

### Phase 6: Pause Menu (~40 lines) -- future
1. Escape key handler
2. Pause overlay div
3. Resume / Return to Title buttons
4. Game state freeze/unfreeze

### Phase 7: Extended HUD Bar (~40 lines) -- future
1. HTML div above canvas
2. Timer counter in update loop
3. Death counter
4. Glyph slot display with letters

### Phase 8: Responsive Canvas (~6 lines) -- future
1. CSS update in style block

### Phase 9: Audio (~60 lines) -- future
1. Audio IIFE module
2. Call sites in update/checkGlyphs/killAndRespawn
3. Mute toggle in title/pause menus

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

---

## 9. REFERENCE: CURRENT CODE MAP

For implementers -- key sections of `golem.html` and what they control:

| Lines    | Section                    | What to change for theming                     |
|----------|----------------------------|------------------------------------------------|
| 6-9      | CSS style                  | Background color, add responsive rules         |
| 62-68    | PARTICLE_COLORS            | All particle colors                            |
| 71-76    | ABILITIES, CHAMBER_NAMES   | Chamber names, ability text                    |
| 77-82    | GLYPH_EFFECTS              | Glyph collect messages                         |
| 939-941  | transitionEnding()         | Ending message text                            |
| 1198     | showMessage('Clay reforms')| Death reform message                           |
| 1174     | killAndRespawn pit death   | Pit death message                              |
| 1214-1221| COLORS object              | All visual colors                              |
| 1367-1486| render() tile rendering    | Tile colors, glyph visual, pit glow colors     |
| 1415-1436| DOOR_D render              | Door locked/open colors                        |
| 1438-1449| END_PORTAL render          | Portal colors                                  |
| 1451-1459| GLYPH render               | Glyph cross -> Hebrew letter                   |
| 1472-1484| MAGICAL_WALL render        | Purple -> Seafoam colors                       |
| 1516-1557| Dash charge indicator      | Purple -> Seafoam colors                       |
| 1600-1603| Golem body glyph lines     | fillRect -> Hebrew letter textFill             |
| 1617-1643| HUD rendering              | Colors, fonts, chamber name format             |
| 1645-1656| Message rendering          | Font, color                                    |
| 1664-1678| Ending screen render       | Complete rewrite for animated ending           |
| 1709     | Initial message            | Awakening message text                         |

---

## Appendix A: Hebrew Letters Reference

| Letter | Unicode | HTML Entity | Canvas String  |
|--------|---------|-------------|----------------|
| Aleph  | U+05D0  | &hebrew;    | `'\u05d0'`     |
| Mem    | U+05DE  |             | `'\u05de'`     |
| He     | U+05D4  |             | `'\u05d4'`     |
| Tav    | U+05EA  |             | `'\u05ea'`     |
| EMET   |         |             | `'\u05e2\u05de\u05ea'` |

Note: EMET uses Ayin (\u05e2), not Aleph (\u05d0), as its first letter. The first glyph
collected is Aleph (\u05d0) representing "breath" -- the first sound. This is intentional:
the golem starts with potential (Aleph/breath) and completes with the actual Word (EMET/Truth).
The journey transforms breath into truth.

## Appendix B: tholem.ai Design Principles Applied

- **Obsidian background:** Used for canvas body and all overlay backgrounds.
- **Champagne as primary accent:** Glyphs, golem eye, text, portal glow, particle highlights.
- **Seafoam as interactive accent:** Open doors, unlocked abilities, button outlines.
- **Emerald for creative elements:** END_PORTAL and ending sequence convergence flash.
- **Cosmic Purple for magic:** Dash particles, dash charge indicator, magical wall barriers.
  A game-specific color outside the core brand palette, justified by the mystical theme
  of the golem's hermetic initiation. Vivid violet (`#8B5CF6`) contrasts cleanly with
  Champagne and Seafoam on the dark Obsidian background.
- **Rune line work:** 6-8% opacity geometric background patterns, Champagne color.
- **Typography hierarchy:** Cormorant Garamond for titles/quotes, Inter for UI/HUD.
- **Outline iconography:** Button strokes at ~1.75px, round caps, Seafoam tint.
- **8px grid:** HUD bar height (48px = 6x8), spacing multiples of 8.
- **Generous whitespace:** Title menu and ending screen use centered layout with wide margins.
- **Asset geometry:** Rectangular primitives refined with bevels, chamfers, rounded corners,
  and polygonal halos to establish a cohesive visual identity -- walls are sharp and fixed,
  push blocks are rounded and movable, glyphs are inscribed within diamonds, magical barriers
  pulse with hexagonal cores.
