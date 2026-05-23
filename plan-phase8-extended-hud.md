# Phase 8: Extended HUD — Execution Plan

> **Status: DRAFT — Awaiting Approval**
> **Target:** golem.html (single-file, vanilla JS + Canvas 2D)
> **Estimated effort:** ~40 lines net change, 5 slices, ~30 min focused work
> **Risk level:** Low-Medium (UI restructuring; no gameplay or state changes)

---

## Requirements

1. Add a 32px-high HUD bar above the canvas (800px wide)
2. Remove the "Name: " prefix artifact next to Hebrew glyphs
3. Move ability unlock text from inline HUD list to themed message popups (no overwriting narrative messages)
4. Add timer + death count to the HUD bar (top-right)
5. Keep Hebrew glyphs clean in the bar
6. Integrate without breaking canvas, state tracking, or level boundaries

---

## Current State (Evidence)

| Element | Location | Current Behavior |
|---------|----------|-----------------|
| HTML/CSS | Lines 1-14 | No wrapper div, canvas direct in body, flexbox centered |
| Canvas | Line 13 | `<canvas id="c">` at 800x480 |
| HUD render | Lines 1755-1798 | Canvas `fillText` overlays on the game canvas |
| "Name: " prefix | Line 1760 | `X.fillText('Name: '+collectedStr, 10, 20)` — the artifact |
| Hebrew glyphs | Lines 1757-1760 | Aleph/Mem/He/Tav with circles for uncollected |
| ABILITIES list | Lines 1762-1767 | `[1] Double Jump` etc. rendered inline in HUD |
| Ability unlock | Line 945 | `showMessage(GLYPH_EFFECTS[gi].msg, 120)` — already themed |
| Timer | Line 471, 959 | `gameStartTime = Date.now()`, frozen for ending |
| Deaths | Line 157, 472 | `totalDeaths++` on death, shown only in ending screen (line 1957) |
| Chamber name | Lines 1769-1785 | Bottom center, `H-10` |
| Message overlay | Lines 1787-1798 | Center, `H/2-60`, fade in/out |
| FONT_UI | Line 71 | `11px system-ui, ...` |
| FONT_DISPLAY | Line 72 | `italic 16px Georgia, ...` |
| FONT_HEBREW | Line 73 | `18px "Segoe UI", ...` |

---

## Task Order (Safest First)

### TASK 1: Remove "Name: " Prefix (Risk: None)

**Why first:** Pure text removal, zero structural change. Immediate win.

**Changes:**
- **Line 1760:** Change `X.fillText('Name: '+collectedStr, 10, 20);` to `X.fillText(collectedStr, 10, 20);`
- That's it. One character substitution (`'Name: '` -> `''`).

**Validation gate:**
- [ ] Game loads, no console errors
- [ ] Top-left HUD shows `א_mem_ה_ת` (Hebrew glyphs with circles) without "Name: " prefix
- [ ] Glyphs fill in as collected (circles become letters)
- [ ] No visual regression elsewhere

---

### TASK 2: Remove Inline ABILITIES List from HUD (Risk: None)

**Why second:** Pure removal. The ability unlock messages already route through `showMessage()` (line 945 calls `showMessage(GLYPH_EFFECTS[gi].msg, 120)`). The inline HUD list is redundant visual noise.

**Changes:**
- **Lines 1762-1767:** Remove the ABILITIES loop entirely:
  ```
  // DELETE these lines:
  X.font=FONT_UI;
  let ay=36;
  for(const [name,req] of ABILITIES){
    X.fillStyle=glyphsCollected>=req?'#5CB3AF':'#A18F75';
    X.fillText(name, 10, ay); ay+=14;
  }
  ```
- **Line 76-79:** The `ABILITIES` const array can remain (may be referenced elsewhere or removed in a cleanup pass) — leave it for now.

**Validation gate:**
- [ ] Game loads, no console errors
- [ ] No `[1] Double Jump` etc. text in the HUD
- [ ] Glyph collection still triggers themed messages ("The First breathes life." etc.) via showMessage
- [ ] No ability unlock messages overwritten by each other (messageQueue depth=5 protects this)

---

### TASK 3: Add HUD Bar Wrapper + CSS (Risk: Low)

**Why third:** Structural change but isolated — adds HTML wrapper and CSS, doesn't modify game logic.

**Changes:**

**HTML (lines 12-13):** Wrap canvas in a div:
```html
<!-- BEFORE -->
<body>
<canvas id="c"></canvas>

<!-- AFTER -->
<body>
<div id="game-wrapper">
  <div id="hud-bar"></div>
  <canvas id="c"></canvas>
</div>
```

**CSS (lines 6-10):** Update body + add wrapper/hud styles:
```css
/* BEFORE */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0A0A12; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
canvas { display: block; image-rendering: pixelated; }

/* AFTER */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0A0A12; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
#game-wrapper { display: flex; flex-direction: column; align-items: center; }
#hud-bar {
  width: 800px; height: 32px;
  background: rgba(10, 10, 18, 0.85);
  border: 1px solid rgba(197, 179, 145, 0.2);
  border-bottom: 1px solid rgba(197, 179, 145, 0.15);
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 12px;
  font: 11px system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #E8E8F0;
  user-select: none;
}
#hud-bar .hud-left, #hud-bar .hud-right {
  display: flex; align-items: center; gap: 12px;
}
canvas { display: block; image-rendering: pixelated; }
```

**JS — move HUD render from canvas to DOM:**
- Remove the old HUD canvas rendering (lines 1756-1767) since it will now be DOM-based.
- After the HUD bar is created, populate it via `innerHTML` or `textContent` in the render loop.

**Specifically, replace the old HUD canvas code (lines 1755-1767) with a DOM update:**
```javascript
/* ── HUD (DOM-based bar above canvas) ── */
const hudBar = document.getElementById('hud-bar');
const hudLeft = hudBar.querySelector('.hud-left');
const hudRight = hudBar.querySelector('.hud-right');

// Glyph slots (left side)
const hebrewHUD = ['\u05d0','\u05de','\u05d4','\u05ea'];
const glyphSlots = hebrewHUD.map((l,i) =>
  collectedGlyphs[i]
    ? `<span style="color:#C5B391;font-family:'Segoe UI','Arial Hebrew','David',serif;font-size:16px;">${l}</span>`
    : `<span style="color:#454560;font-size:16px;">\u25cb</span>`
).join(' &nbsp; ');
hudLeft.innerHTML = `<span style="font-family:'Segoe UI','Arial Hebrew','David',serif;font-size:16px;">${glyphSlots}</span>`;

// Timer + deaths (right side)
const elapsed = Math.floor((Date.now() - gameStartTime) / 1000);
const mins = Math.floor(elapsed / 60);
const secs = elapsed % 60;
const timeStr = mins + ':' + String(secs).padStart(2, '0');
hudRight.innerHTML = `<span style="color:#A18F75;">${timeStr}</span>` +
  `<span style="color:#8a6060;">Deaths: ${totalDeaths}</span>`;
```

**Validation gate:**
- [ ] Game loads, 32px bar visible above canvas
- [ ] Bar is 800px wide, matches canvas width
- [ ] Hebrew glyph slots displayed on left side of bar
- [ ] Timer counts up on right side
- [ ] Death count shown next to timer
- [ ] Canvas rendering area unchanged (still 800x480)
- [ ] Game is vertically centered (wrapper + bar + canvas)
- [ ] No console errors
- [ ] Play through all 5 chambers — no visual regression

---

### TASK 4: Clean Up Canvas HUD Artifacts (Risk: Low)

**Why fourth:** Now that HUD is DOM-based, remove all old canvas HUD rendering. Also remove the chamber name from canvas bottom and move it to the HUD bar.

**Changes:**

**Remove from render() function:**
- Lines 1755-1767: Old HUD (already handled by TASK 3 replacement)
- Lines 1769-1785: Chamber name at bottom — decide whether to keep on canvas or move to bar
  - Recommendation: Keep chamber name on canvas (bottom center) — it's contextual to the chamber, not a persistent HUD element. It already works well.
  - If moving to bar: add chamber name as a center element in the HUD bar.

**Also remove:** The `X.direction='rtl'` setting at line 1759 is no longer needed since Hebrew renders in the DOM bar.

**Validation gate:**
- [ ] No text rendered on canvas where HUD used to be (top-left corner clean)
- [ ] Chamber name still visible at bottom of canvas
- [ ] Message overlays still appear at center
- [ ] Screen fade overlay still works
- [ ] Ending screen still renders correctly (no HUD interference)

---

### TASK 5: Ability Unlock Message Queue Protection (Risk: Low)

**Why last:** This is the subtlest change — ensuring ability unlock messages don't overwrite narrative messages.

**Current state:**
- `showMessage()` at line 862 already has queue protection: max depth 5, skips duplicate text
- Glyph unlock calls `showMessage(GLYPH_EFFECTS[gi].msg, 120)` at line 945
- Narrative messages (death, portal lock, etc.) also use `showMessage()`
- The queue system naturally prevents overwriting — messages queue up and display sequentially

**What to verify/adjust:**
- The 120-frame duration for glyph messages should be sufficient. Check `calcDisplayDuration()` at line 857:
  - `"The First breathes life."` = 26 chars / 0.35 = 74 frames auto, min 90 -> 90 frames
  - Provided dur 120 -> `Math.min(360, Math.max(120, 74))` = 120 frames = 2 seconds
  - This is adequate — no change needed
- Confirm that collecting a glyph during a death message doesn't drop the glyph message:
  - `MSG_MAX_QUEUE_DEPTH = 5` — enough buffer
  - `killAndRespawn` calls `showMessage(msg, duration)` — adds to queue
  - Glyph collection adds to queue after respawn completes (animState='idle')
  - **Conclusion:** No change needed — the system already works correctly

**Optional enhancement:** Add a subtle visual indicator in the HUD bar when a new ability is unlocked (e.g., the glyph slot flashes champagne gold for 1 second).

**Validation gate:**
- [ ] Collect all 4 glyphs in sequence — each themed message displays
- [ ] Die and collect a glyph on respawn — both messages appear (death then glyph)
- [ ] No message is dropped or cut short
- [ ] Message fade in/out still smooth

---

## Summary of Changes by File

| File | Lines Added | Lines Removed | Net | Risk |
|------|-------------|---------------|-----|------|
| golem.html | ~35 (CSS + DOM HUD) | ~15 (canvas HUD) | +20 | Low |

**Total estimated change:** ~35 lines added, ~15 removed = net +20 lines (within "~40 lines" budget from spec)

---

## Innovate Checkpoint

### Alternatives Considered

1. **Canvas-drawn HUD bar** — Draw the bar as a filled rect on the canvas with text overlays.
   - **Tradeoff:** Requires adjusting canvas height to 512 (480+32) or offsetting all game rendering down by 32px. All existing tile coordinates, camera offsets, and chamber rendering would shift. Too risky for a single-file game.
   - **Rejected.** DOM-based bar is cleaner.

2. **Overlay div on canvas** — Position a div absolutely over the top of the canvas.
   - **Tradeoff:** Would obscure the top 32px of the game canvas, potentially covering tiles. Chamber data uses the full 480px height.
   - **Rejected.** Wrapper div above canvas preserves game area.

3. **Move chamber name to HUD bar** — Replace bottom-of-screen chamber name with a bar element.
   - **Tradeoff:** Chamber name is contextual (player reads it while in the chamber). Bottom center placement matches the atmospheric design. Moving to bar makes it a "stat" rather than narrative context.
   - **Decision:** Keep chamber name on canvas bottom-center. It's not part of the HUD requirements.

4. **Timer format** — Show minutes:seconds vs. seconds-only.
   - **Decision:** `MM:SS` format is standard for games. The game takes ~2-3 minutes, so `0:00` to `3:00` range. Clean and readable.

5. **DOM vs. requestAnimationFrame for HUD update** — Should the HUD bar update every frame or less frequently?
   - **Decision:** Timer updates every frame is fine for a single `innerHTML` assignment — negligible DOM cost. Deaths don't change every frame. The overhead is trivial.

### Confidence Assessment

| Task | Confidence | Rationale |
|------|-----------|-----------|
| TASK 1 (Remove "Name:") | 100% | One string literal change, zero behavioral impact |
| TASK 2 (Remove ABILITIES list) | 100% | Pure removal, messages already work via showMessage |
| TASK 3 (Add HUD bar) | 90% | CSS + DOM addition; well-isolated from game logic. Risk is CSS positioning on different screens. |
| TASK 4 (Clean up canvas) | 95% | Removing old code that's replaced by DOM HUD |
| TASK 5 (Message queue) | 95% | System already works; verification only |

**Overall confidence: 93%** — The primary risk is CSS positioning (TASK 3) but the flexbox wrapper approach is robust.

### Risk Mitigations

- **CSS positioning:** The `#game-wrapper` flexbox column centers the entire game area (bar + canvas) vertically. Body flexbox centers the wrapper. This is standard layout.
- **Game area integrity:** Canvas dimensions unchanged (800x480). Chamber rendering uses `ox`/`oy` offsets calculated from `W`/`H`/`c.w`/`c.h` — no change needed.
- **State tracking:** No game state variables modified. HUD is purely presentational.
- **Level boundaries:** No chamber data modified. No tile coordinates changed.

---

## Dependency Map

```
TASK 1 (Remove "Name:") ──────────────────── independent
TASK 2 (Remove ABILITIES) ────────────────── independent
TASK 3 (Add HUD bar wrapper) ── prerequisite for ──┐
TASK 4 (Clean canvas artifacts) ────────────────────┤
                                                     ├──> TASK 5 (Verify messages)
TASK 5 (Message queue check) ────────────────────────┘
```

**Recommended order:** 1 -> 2 -> 3 -> 4 -> 5 (by risk, safest first)
**Parallelizable:** Tasks 1 and 2 can be done simultaneously (both pure removal).

---

## Validation Strategy (Post-Implementation)

1. **Syntax check:** Open golem.html in browser DevTools — zero console errors.
2. **Visual check:** 32px bar visible above canvas with Hebrew glyphs (left) and timer/deaths (right).
3. **No "Name: " prefix:** Glyphs render clean in the bar.
4. **No inline ABILITIES list:** Canvas top-left is clean.
5. **Full playthrough:** All 5 chambers playable, glyphs collect, abilities unlock with themed messages.
6. **Test chamber:** Press T — all abilities work, no HUD artifacts.
7. **Death/respawn:** All death types work, HUD timer continues, death count increments in bar.
8. **Ending screen:** Stats show correctly, no HUD bar interference.
9. **Message queue:** Glyph collection messages appear with fade in/out, don't overwrite narrative messages.
10. **Screen resize:** Browser window resize doesn't break layout (flexbox handles centering).

---

## Rollback Plan

If any issue arises:
- Tasks 1-2: Revert single-line changes (git diff is minimal)
- Tasks 3-4: Remove the `#game-wrapper` div and `#hud-bar` from HTML, restore CSS, restore canvas HUD code
- Task 5: No changes to make — verification only
