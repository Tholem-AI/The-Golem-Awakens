# Code Review: The Golem Awakens

---

## Overall Assessment

The Golem Awakens is a polished single-file platformer with solid physics foundations. The jump system (coyote time, input buffering, squash-and-stretch) is well-implemented, and the particle effects add meaningful feedback. The game is fully playable end-to-end. The main opportunities are improving the dash charge feel, adding responsive canvas scaling, and cleaning up some dead code.

---

## Critical Issues

None. The game is fully playable from start to finish.

---

## Important Improvements

### 1. Dash charge time is too long and uncommunicated

The dash requires holding Shift for 20 frames (~0.33 seconds) before it activates. During this charge, the player hovers with purple particles, but:
- There is no HUD indicator that the charge is in progress
- The hover effect is subtle and may be missed
- Most platformer dashes activate on press, not on hold-and-release

**Recommendation:** Either reduce the charge time significantly (e.g., 8-10 frames) or change to a press-to-dash pattern. If keeping the charge, add a visual indicator in the HUD:

```javascript
// In render(), add to HUD section:
if(P.dashCharge > 0) {
  X.fillStyle = 'rgba(180,80,255,' + (P.dashCharge/20) + ')';
  X.fillRect(10, 68, (P.dashCharge/20)*60, 3);
}
```

### 2. Second jump is stronger than first jump

Line 641-656: First jump velocity is `-10`, but the second (double) jump is `-13`. This means the double jump covers more vertical distance than the initial jump, which can feel unintuitive. In most platformers, the double jump is equal or slightly weaker.

**Recommendation:** Make them equal, or make the second jump slightly weaker:

```javascript
// Line 641, change -13 to -10 or -11
P.vy = P.jumps === 0 ? -10 : -10;
```

### 3. No responsive scaling

The canvas is fixed at 800x480 with no CSS scaling. On larger screens it appears tiny; on smaller screens it may clip. The `image-rendering: pixelated` rule helps with upscaling quality but the CSS doesn't actually scale the element.

**Recommendation:** Add a simple CSS scale that fits the viewport:

```css
canvas {
  display: block;
  image-rendering: pixelated;
  width: min(800px, calc(100vw - 20px));
  height: auto;
  max-height: 95vh;
}
```

Or use JavaScript to compute a scale factor at load and on resize.

### 4. Dead code: `pushBlock()` is never called

The function at line 341 (`pushBlock()`) implements tile-based block pushing using the `BLOCK` tile type. It is never invoked from `update()` or anywhere else. The active push system uses `resolvePushBlockCollision()` with the `PB` entity instead.

**Recommendation:** Either remove it or add a comment explaining it is legacy code kept for reference. This also applies to the `BLOCK` tile constant (value 6) -- no chamber places any BLOCK tiles.

---

## Suggestions

### 1. Particle system uses `splice` during iteration

`updateParticles()` at line 391 iterates backward and uses `splice()` to remove dead particles. This works correctly but reallocates the array on every removal. For a small game this is fine, but if particle counts grow:

```javascript
// Alternative: mark-and-sweep with filter
function updateParticles() {
  for (const p of particles) {
    p.x += p.vx; p.y += p.vy; p.vy += 0.1; p.life--;
  }
  particles = particles.filter(p => p.life > 0);
}
```

### 2. Redundant chamber lookup in wall rendering

Lines 720-725 inside the wall rendering block:

```javascript
const ch2 = P.chamber, c2 = chambers[ch2];
```

This re-looks up the current chamber inside the per-tile render loop. The chamber is already available as `c` from line 698. Use `c` directly instead.

### 3. No pause functionality

The game cannot be paused. Adding a simple Escape-to-pause would be a quality-of-life improvement:

```javascript
if (fresh('Escape')) {
  gameState = gameState === 'paused' ? 'playing' : 'paused';
}
```

Then skip the `update()` body when `gameState === 'paused'` and render a "Paused" overlay.

### 4. `collidesDash` push-block check uses `prevY` instead of `curY`

Line 331 in `collidesDash()`:

```javascript
if(aabb(x1, prevY, x2-x1, P.h, PB.x, PB.y, PB.w, PB.h)) return true;
```

The Y coordinate is `prevY` (the player's position before Y movement), not `curY`. During a dash, `P.vy` is forced to 0 (line 533), so the player doesn't actually move vertically and this has no practical effect. It is functionally correct but semantically inconsistent with the Y-collision context. Using `curY` would match the intent more clearly, though it would not change behavior.

---

## Positive Observations

- **Jump system is excellent.** Coyote time (8 frames), jump buffering (8 frames), and fresh-press detection via `prevKeys` are all correctly implemented. This is the kind of polish that separates good platformers from great ones.
- **Squash-and-stretch on the player** (lines 849-853) adds great visual feedback for movement states. The falling motion lines are a nice touch.
- **Particle system** provides consistent, themed feedback for every action. The shatter effect with three layers (debris, dust, sparks) is well-designed.
- **Screen fade transitions** between chambers are smooth and professional. The 300ms delay with alpha ramping is well-timed.
- **Tile-based level design with IIFE encapsulation** keeps chamber data clean and self-contained. Easy to add new chambers.
- **One-way platform implementation** (`platSolid`) correctly checks that the player was previously above the platform. This is a subtle but important detail that many implementations get wrong.
- **Glyph collection with sequential gating** (`glyphsCollected !== ch`) is a clever way to enforce progression order without separate ability flags.
- **The visual theme is cohesive.** The Egyptian/Thoth motif carries through the color palette, particle colors, chamber names, and messaging consistently.

---

## Recommended Next Steps

1. **Reduce dash charge time** -- Change from 20 frames to 8-10 frames, or switch to press-to-dash. Consider adding a HUD charge bar if keeping the hold pattern.
2. **Add responsive canvas scaling** -- A few lines of CSS or JS will make the game usable on all screen sizes.
3. **Remove dead code** -- Delete `pushBlock()` (line 341) and the unused `BLOCK` tile constant to keep the codebase clean.
4. **Add a pause toggle** -- Escape-to-pause is a small addition that improves the player experience.
