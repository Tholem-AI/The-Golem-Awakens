# Physics Research Report — Movement, Jump & Double-Jump

**Date:** 2026-05-16
**File analyzed:** `golem.html` (lines 547-751)
**Purpose:** Research phase for physics tuning aligned with human reaction time principles

---

## 1. Current Physics Values (from source)

### Horizontal Movement (lines 547-561)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Ground acceleration | `0.1 px/frame^2` | Applied when input != 0 and on ground |
| Air acceleration | `0.4 px/frame^2` | Applied when input != 0 and airborne |
| Max speed | `5 px/frame` | Hard clamp on `Math.abs(P.vx)` |
| Friction (decel) | `0.45 px/frame^2` | Applied when no input |

### Gravity & Terminal (lines 618-622)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Gravity | `0.28 px/frame^2` | Applied every frame when `!onGround` |
| Terminal velocity | `5 px/frame` (down) | Hard clamp `if (P.vy > 5)` |

### Jump Logic (lines 703-731)

| Parameter | Value | Notes |
|-----------|-------|-------|
| First jump vy | `-10 px/frame` | Line 708, 716 |
| Double jump vy | `-13 px/frame` | Lines 708, 724 |
| Max jumps | `1` (initial) / `2` (after glyph 1) | Line 141, 493 |
| Coyote time | `8 frames` (~133ms) | Lines 676, 694, 711, 719 |
| Jump buffer | `8 frames` (~133ms) | Line 730 |
| Variable jump height | **NONE** | No cut-on-release logic |

---

## 2. Current Calculated Jump Metrics

### First Jump (vy = -10, g = 0.28)

- **Time to peak:** 35.7 frames (~595ms)
- **Peak height:** 178.6 px (~5.6 tiles at 32px)
- **Descent time:** 44.6 frames (~744ms)
- **Total airtime:** 80.4 frames (~1340ms)
- **Time in top 10% of arc:** 22.6 frames (~377ms)

### Double Jump (vy = -13, g = 0.28)

- **Time to peak:** 46.4 frames (~774ms)
- **Peak height:** 301.8 px (~9.4 tiles)
- **Descent time:** 69.3 frames (~1155ms)
- **Total airtime:** 115.7 frames (~1929ms)
- **Time in top 10% of arc:** 29.4 frames (~489ms)
- **Height vs first jump:** 69% higher

### Horizontal Movement

- **Time to max speed (ground):** 50 frames (~834ms)
- **Time to max speed (air):** 12 frames (~208ms)
- **Time to stop from max:** 11.1 frames (~185ms)
- **Stopping distance:** 27.8 px (~0.9 tiles)
- **Tiles/sec:** 9.4 tiles/sec

---

## 3. User Requirements

1. **Horizontal speed ~1/2 current**
2. **First jump: half initial speed, same max height, float at top**
3. **Double jump: smaller arc with same float feel**
4. **Align with human reaction time** (250ms baseline = ~15 frames at 60fps)

---

## 4. Calculated Target Values

### Horizontal: Halve Speed (keep same acceleration profile)

| Parameter | Current | Target | Change Factor |
|-----------|---------|--------|---------------|
| Max speed | 5.0 px/frame | **2.5 px/frame** | x0.50 |
| Ground accel | 0.1 px/frame^2 | **0.05 px/frame^2** | x0.50 |
| Air accel | 0.4 px/frame^2 | **0.2 px/frame^2** | x0.50 |
| Friction | 0.45 px/frame^2 | **0.225 px/frame^2** | x0.50 |

**Effect:** All timing (time to max, time to stop) remains identical. Speed is halved, so distance covered is halved. Tiles/sec drops from 9.4 to 4.7.

### First Jump: Half Speed, Same Height -> New Gravity

The math:
```
h = vy^2 / (2*g)
Same height => g_new = g_old * (vy_new^2 / vy_old^2)
g_new = 0.28 * (5^2 / 10^2) = 0.28 * 0.25 = 0.07
```

| Parameter | Current | Target |
|-----------|---------|--------|
| First jump vy | -10 px/frame | **-5 px/frame** |
| Gravity | 0.28 px/frame^2 | **0.07 px/frame^2** |
| Terminal velocity | 5 px/frame | **2.5 px/frame** |

### Double Jump: Smaller Arc

Target: ~75% of first jump height = ~134 px (~4.2 tiles)

```
vy = -sqrt(2 * g_new * target_height)
vy = -sqrt(2 * 0.07 * 134) = -4.33 px/frame
```

| Parameter | Current | Target |
|-----------|---------|--------|
| Double jump vy | -13 px/frame | **-4.33 px/frame** |

### Variable Jump Height (NEW)

```javascript
// After jump execution, before move-Y:
if (!jumpHeld && P.vy < -2) P.vy = -2;
```

This gives players agency to do short hops (minimum ~29 px / ~0.9 tiles) by tapping the jump button.

---

## 5. Complete Target Value Summary

| Parameter | Current | Target | Change |
|-----------|---------|--------|--------|
| Max horizontal speed | 5.0 | **2.5** | x0.50 |
| Ground accel | 0.10 | **0.050** | x0.50 |
| Air accel | 0.40 | **0.200** | x0.50 |
| Friction | 0.45 | **0.225** | x0.50 |
| Gravity | 0.28 | **0.070** | x0.25 |
| Terminal velocity | 5.0 | **2.5** | x0.50 |
| First jump vy | -10.0 | **-5.0** | x0.50 |
| Double jump vy | -13.0 | **-4.33** | x0.47 |
| Variable jump cutoff | (none) | **-2** | NEW |
| Coyote time | 8 frames | **8-12 frames** | same or +50% |
| Jump buffer | 8 frames | **8-12 frames** | same or +50% |

---

## 6. Key Metric Comparisons (Before vs After)

| Metric | Before | After | Ratio |
|--------|--------|-------|-------|
| First jump height | 179 px | **179 px** | 1.00 (same) |
| First jump airtime | 80 frames | **161 frames** | 2.00x |
| Double jump height | 302 px | **134 px** | 0.44x |
| Double jump airtime | 116 frames | **133 frames** | 1.15x |
| Top-10% float time | 23 frames | **45 frames** | 2.00x |
| Horizontal tiles/sec | 9.4 | **4.7** | 0.50x |
| Time to peak (1st jump) | 36 frames | **71 frames** | 2.00x |

---

## 7. Human Reaction Time Alignment

| Feature | Current | Assessment |
|---------|---------|------------|
| Coyote time | 8f (133ms) | 0.5x reaction window. Consider 12-15f for slower pace. |
| Jump buffer | 8f (133ms) | 0.5x reaction window. Consider 12-15f. |
| Variable jump window | N/A | NEW: 43f (714ms) for first jump >> 250ms reaction time. Excellent. |
| First jump ascent | 36f (595ms) | NEW: 71f (1191ms). Plenty of time to react mid-air. |

**Assessment:** The reduced gravity naturally creates more float, which gives players more time to react and make decisions mid-air. The variable jump height cutoff window (43 frames / 714ms) is nearly 3x the average human reaction time, giving generous control.

---

## 8. Implementation Locations in golem.html

| Change | Line(s) | Current Code | Target Code |
|--------|---------|--------------|-------------|
| Ground accel | 555 | `P.vx += inputX * (P.onGround ? 0.1 : 0.4)` | `P.vx += inputX * (P.onGround ? 0.05 : 0.2)` |
| Max speed clamp | 556 | `if(Math.abs(P.vx)>5) P.vx = inputX*5` | `if(Math.abs(P.vx)>2.5) P.vx = inputX*2.5` |
| Friction | 558-559 | `P.vx = Math.max(0, P.vx-0.45)` / `P.vx = Math.min(0, P.vx+0.45)` | `P.vx = Math.max(0, P.vx-0.225)` / `P.vx = Math.min(0, P.vx+0.225)` |
| Gravity | 620 | `P.vy += 0.28` | `P.vy += 0.07` |
| Terminal velocity | 622 | `if(P.vy>5) P.vy=5` | `if(P.vy>2.5) P.vy=2.5` |
| First jump vy (buffer) | 708 | `P.vy = P.jumps===0 ? -10 : -13` | `P.vy = P.jumps===0 ? -5 : -4.33` |
| First jump vy (coyote) | 716 | `P.vy = -10` | `P.vy = -5` |
| Double jump vy | 724 | `P.vy = -13` | `P.vy = -4.33` |
| Variable jump height | NEW (after 731) | (none) | `if(!jumpHeld && P.vy < -2) P.vy = -2` |

---

## 9. Chamber Retuning Concerns

With the new physics, existing chambers may need adjustment:

- **First jump height unchanged** (179 px / 5.6 tiles) — vertical reach same
- **Double jump height reduced** from 302 px to 134 px (9.4 tiles -> 4.2 tiles)
  - Any design that relies on double-jump reaching ~9 tiles will break
  - Double jump is now only ~4.2 tiles (vs 5.6 for first jump)
- **Horizontal speed halved** — gap crossings that required sprinting may need wider platforms or shorter gaps
- **Falling is 4x slower** (gravity 0.28 -> 0.07) — pit hazards may feel less urgent

---

## 10. Design Considerations

1. **Gravity is global** — the 0.07 gravity affects dash charging (line 565: `P.vy = P.vy * 0.1 + 0.028`) which hardcodes 0.028 (= 0.28/10). This should update to 0.007.

2. **Terminal velocity match** — setting terminal to 2.5 (matching max horizontal) gives consistent feel.

3. **Coyote/buffer** — 8 frames works for the current speed but 12-15 frames would better match the slower, more deliberate pace of the tuned physics.

4. **Variable jump height** — the -2 cutoff gives a ~29 px minimum jump. Consider if this should be -1.5 or -2.5 for different feel.

5. **Dash charging** uses `P.vy * 0.1 + 0.028` — the 0.028 should become 0.007 (= 0.07/10) to maintain the 1/10th gravity intent.
