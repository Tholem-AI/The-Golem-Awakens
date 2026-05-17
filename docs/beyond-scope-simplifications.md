# Beyond-Scope Simplifications

Identified during the research phase for the golem.html refactor. These are **not** part of the refactor scope (which is structural reorganization only) but are documented for future consideration.

---

## 1. Jump Velocity Equalization

**Current:** First jump uses `P.vy = -5`, double jump uses `P.vy = -4.33` (line ~737).
**Impact:** Double jump is noticeably weaker than the first jump, creating inconsistent player feel.
**Suggestion:** Equalize both to the same value (e.g., `-4.65` average) or make the difference intentional via a config constant.
**Lines:** ~737 in `update()`

## 2. Pause Toggle

**Current:** No pause functionality exists. Game runs continuously.
**Impact:** Players cannot pause (e.g., to read a message, take a break).
**Suggestion:** Add a simple `P` key handler that sets `gameState = 'paused'` and skips the `update()` call while still running `render()`.
**Effort:** ~10 lines

## 3. Responsive Canvas Scaling

**Current:** Canvas is fixed at 800x480. On smaller screens it may overflow.
**Impact:** Poor UX on mobile/tablet; the game doesn't adapt to viewport size.
**Suggestion:** Add CSS rule:
```css
canvas { max-width: 100vw; max-height: 100vh; object-fit: contain; }
```
This keeps the 800x480 internal resolution but scales the displayed size to fit the viewport.
**Lines:** Style block (lines 6-10)
**Effort:** 1 CSS line

## 4. BLOCK Tile Constant Cleanup

**Current:** `BLOCK=6` is defined (line 21), referenced in `solid()` (line 330) and `render()` (line 886), but no chamber data uses it.
**Impact:** Dead code path that will never execute but adds to code size.
**Suggestion:** Remove `BLOCK=6` from constants, remove `t===BLOCK` from `solid()`, remove the `else if(t===BLOCK)` render branch (lines 886-890).
**Lines:** 21, 330, 886-890
**Risk:** LOW but requires careful editing of two separate functions. Deferred to avoid introducing bugs during the structural refactor.

## 5. Input Normalization

**Current:** Arrow keys and WASD are listed separately in every input check.
**Example:** `keys['ArrowLeft']||keys['KeyA']` appears in multiple places.
**Suggestion:** Create a direction abstraction:
```js
function inputLeft() { return keys['ArrowLeft'] || keys['KeyA']; }
function inputRight() { return keys['ArrowRight'] || keys['KeyD']; }
function inputUp() { return keys['ArrowUp'] || keys['KeyW'] || keys['Space']; }
```
**Lines:** Multiple locations in `update()` (~575-576, ~733-734)
**Effort:** ~5 new functions, replace ~6 call sites

## 6. Message Queue System

**Current:** `showMessage()` replaces any existing message immediately.
**Impact:** If multiple events fire in the same frame, only the last message is shown.
**Suggestion:** Implement a message queue (`messageQueue = []`) that cycles through messages as each one expires.
**Lines:** 446 (showMessage definition), 1086-1091 (message render)
**Effort:** ~15 lines

## 7. Camera / Viewport System

**Current:** Chamber is always centered on screen with hardcoded `ox`/`oy` offset (line 804-805).
**Impact:** Chambers are limited to fitting within 800x480. Can't create larger levels.
**Suggestion:** Extract a `camera` object with `x`, `y`, `shake` properties. Use camera offsets instead of hardcoded centering.
**Lines:** 804-805 in `render()`, all render pixel calculations
**Effort:** Moderate (~30 lines)

## 8. Sound Effects

**Current:** No audio.
**Impact:** Missing sensory feedback for key game events (jump, dash, glyph collect, push, break, death).
**Suggestion:** Add Web Audio API with short generated sounds (no external files needed — use oscillator-based sounds).
**Effort:** Moderate (~50 lines for sound engine + call sites)

## 9. Touch/Mobile Controls

**Current:** Keyboard-only.
**Impact:** Game unplayable on touch devices.
**Suggestion:** Add on-screen virtual D-pad and action buttons for mobile.
**Effort:** High (~100+ lines for UI + touch event handling)

## 10. Code Comment Improvement

**Current:** Some sections have minimal or no comments. The push block system has detailed comments but the jump/dash systems could use more.
**Suggestion:** Add JSDoc-style comments to all public functions for future reference.
**Effort:** Low (~50 comment lines)

---

## Priority Ranking

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| P0 | #3 Responsive Canvas | 1 line | High — makes game playable on mobile |
| P1 | #2 Pause Toggle | ~10 lines | Medium — basic UX improvement |
| P1 | #4 BLOCK Cleanup | ~5 edits | Low — dead code removal |
| P2 | #1 Jump Equalization | 1 line | Medium — feel improvement |
| P2 | #5 Input Normalization | ~10 lines | Low — code cleanliness |
| P3 | #6 Message Queue | ~15 lines | Low — edge case improvement |
| P3 | #10 Code Comments | ~50 lines | Low — developer experience |
| P4 | #7 Camera System | ~30 lines | Medium — enables larger chambers |
| P4 | #8 Sound Effects | ~50 lines | Medium — sensory improvement |
| P5 | #9 Touch Controls | ~100 lines | High — but large effort |

---

**Note:** These should each be planned and executed as separate tasks, not batched into the refactor.
