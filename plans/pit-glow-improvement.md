# PIT Tile Glow Improvement — Execution Plan

**Date:** 2026-06-03
**Status:** DRAFT — Ready for Implementation
**Target file:** `golem.html` (Section 10. RENDER, lines 1884-1895)
**Scope:** Visual-only render changes. Zero gameplay/mechanics impact.

---

## 1. Problem Statement

Three issues with the current PIT tile glow:

### 1.1 Teal rim alpha violates spec minimum
- **Spec:** `Visual-Story-Design.md` §4.3 line 183: "PIT rim vs bg | Teal alpha >= 0.25 at pulse peak"
- **Current:** `glow*0.28` where glow ranges [0, 0.6], so max alpha = 0.168
- **Violation:** 0.168 < 0.25 spec minimum (67% of required value)
- **Location:** `golem.html` line 1887

### 1.2 Glow doesn't reflect actual 1.1x death hitbox
- **Current:** Glow is a 1px rim on all 4 sides of the 32px tile (fills exactly within tile bounds)
- **Actual:** `inPit()` uses Manhattan distance threshold `1.1*T = 35.2px` from pit center
  - A player center within 35.2px (Manhattan) of pit center triggers death
  - This extends ~4.2px beyond each tile edge in cardinal directions
  - Death zone extends into adjacent AIR tiles but has NO visual indication
- **Location:** `inPit()` at lines 693-705; render at lines 1884-1895

### 1.3 Inconsistent with other hazard tile visual language
- MAGICAL_WALL (lines 1966-1988): Multi-layered visual — seafoam veil + hex core + spark particles
- CRACKED (lines 1954-1964): Bevel + full X-pattern + edge glow when breakable
- END_PORTAL (lines 1919-1930): Layered emerald glow with core
- PIT: Currently has thin 1px rim only — under-presents danger

---

## 2. Innovation Checkpoint: 1.1x Hitbox Visualization

**Problem:** How to visually communicate that the death zone extends ~4.2px beyond tile edges?

### Alternative A: Concentric fading border rings (RECOMMENDED)
**Approach:** Draw 3px-wide outer glow band extending beyond tile boundary, fading from teal to transparent.

**Implementation:**
- Layer 1 (existing rim, 1px): `rgba(92,179,175, peak_alpha)` at tile edge — sharp boundary
- Layer 2 (3px band): `rgba(92,179,175, peak_alpha * 0.5)` drawn 2px beyond tile edge on all 4 sides
- Layer 3 (1px band): `rgba(92,179,175, peak_alpha * 0.25)` drawn 4px beyond tile edge on all 4 sides
- Total visible danger zone: 5px beyond tile edge (slightly overshoots 4.2px for safety margin)
- Uses only `fillRect` — no shadowBlur or gradients
- Pulse sync: all layers use same `now/600+x` phase

**Pros:**
- Directly maps to the 1.1x Manhattan distance concept
- Multiple fade layers create depth perception — player sees "danger aura"
- Consistent with END_PORTAL's layered approach (concentric squares)
- Minimal line count (~8 additional lines)
- No per-frame allocation or new data structures

**Cons:**
- May overlap with adjacent tiles if pits are edge-adjacent to other tiles (rare in current chambers)
- Outer glow could be subtle at low pulse phases

### Alternative B: Dashed perimeter indicator
**Approach:** Draw a dashed/segmented rectangle ~4px beyond tile edges, pulsing with glow phase.

**Implementation:**
- Outer rect at `px-4, py-4` with size `T+8, T+8`
- Use `setLineDash([3,3])` for dashed effect, or manual fillRect segments
- Color: `rgba(92,179,175, glow * 0.20)`
- Pulse: same phase as rim glow

**Pros:**
- Clear visual boundary — dashed line explicitly says "edge of danger"
- More distinct from solid fill tiles — easy to distinguish from walls/platforms

**Cons:**
- `setLineDash` may not work well at pixel-art resolution (800x480)
- Dashed aesthetic breaks the solid-pixel visual language of the game
- Would need `lineDashOffset` management to pulse (more complex)
- Doesn't convey "gradient of danger" — binary safe/unsafe

### Alternative C: Corner glow triangles / chamfered extension
**Approach:** Draw small triangular corner extensions at the 4 corners of the tile, suggesting the danger "bleeds" outward diagonally.

**Implementation:**
- 4px triangles at each corner, drawn with `beginPath/moveTo/lineTo/closePath`
- Color: `rgba(92,179,175, glow * 0.15)`
- Combined with widened rim for cardinal direction coverage

**Pros:**
- Elegant, minimal visual footprint
- Consistent with chamfered PLATFORM edge design (Phase 5.5)

**Cons:**
- Manhattan distance extends in cardinal directions, not diagonal — visually misleading
- Corner-only coverage doesn't communicate the full 35.2px threshold
- Weak signal at pulse trough

### Decision: Alternative A (Concentric fading border rings)
**Rationale:** Best maps to the actual death geometry, consistent with existing visual language (END_PORTAL uses same concentric approach), minimal code, no new API calls. The multi-layered fade creates a "void energy bleeding outward" effect fitting the narrative (Obsidian = void, pit = death zone).

---

## 3. Ordered Implementation Tasks

### TASK 1: Fix teal rim alpha to meet spec minimum

**File:** `golem.html`, lines 1887-1889
**Change:** Adjust multiplier from `0.28` to `0.42`

```
BEFORE:
  X.fillStyle='rgba(92,179,175,'+(glow*0.28)+')';

AFTER:
  X.fillStyle='rgba(92,179,175,'+(glow*0.42)+')';
```

**Math verification:**
- glow range: [0, 0.6] (from `Math.sin(now/600+x)*0.3+0.3`, clamped since sin ∈ [-1,1])
- Wait: `Math.sin()*0.3+0.3` gives range [0, 0.6] when sin goes from -1 to +1
- At peak: glow=0.6, alpha = 0.6 * 0.42 = **0.252 >= 0.25** ✓
- At trough: glow=0, alpha = 0 * 0.42 = **0** (rim disappears at trough — this is OK, consistent with pulse design)
- Mid-pulse: glow=0.3, alpha = 0.3 * 0.42 = **0.126**

**Lines affected:** 1 line (line 1887)
**Lines added:** 0
**Risk:** None — pure visual multiplier change

---

### TASK 2: Add inner glow intensity boost

**File:** `golem.html`, line 1890
**Change:** Increase inner glow multiplier from `0.15` to `0.22`

```
BEFORE:
  X.fillStyle='rgba(71,158,153,'+(glow*0.15)+')'; X.fillRect(px,py,T,3);

AFTER:
  X.fillStyle='rgba(71,158,153,'+(glow*0.22)+')'; X.fillRect(px,py,T,3);
```

**Rationale:** Teal Deep inner glow peaking at 0.132 (was 0.09) — still subtle but more visible. Matches the increased rim intensity for proportional balance.

**Math verification:**
- Peak: 0.6 * 0.22 = **0.132** (was 0.09)
- Still lower than rim peak (0.252) — maintains depth hierarchy (rim > inner)

**Lines affected:** 1 line (line 1890)
**Lines added:** 0
**Risk:** None — proportional scaling of existing element

---

### TASK 3: Extend visible glow beyond tile boundary (1.1x hitbox)

**File:** `golem.html`, lines 1884-1895
**Change:** Insert 3 concentric glow bands after the obsidian fill, before the rim

```
BEFORE (lines 1884-1895):
} else if(t===PIT){
    X.fillStyle=COLORS.pit; X.fillRect(px,py,T,T);
    const glow=Math.sin(now/600+x)*0.3+0.3;
    X.fillStyle='rgba(92,179,175,'+(glow*0.28)+')';
    X.fillRect(px,py,T,1); X.fillRect(px,py+T-1,T,1);
    X.fillRect(px,py,1,T); X.fillRect(px+T-1,py,1,T);
    X.fillStyle='rgba(71,158,153,'+(glow*0.15)+')'; X.fillRect(px,py,T,3);
    ...

AFTER:
} else if(t===PIT){
    X.fillStyle=COLORS.pit; X.fillRect(px,py,T,T);
    const glow=Math.sin(now/600+x)*0.3+0.3;
    // Outer danger glow — extends beyond tile to reflect 1.1x hitbox (35.2px Manhattan)
    const ext=5; // px extension (covers ~4.2px actual + 0.8px safety margin)
    X.fillStyle='rgba(92,179,175,'+(glow*0.12)+')';
    X.fillRect(px-ext,py,T+ext*2,ext); X.fillRect(px-ext,py+T,T+ext*2,ext);
    X.fillRect(px-ext,py,ext,T+ext*2); X.fillRect(px+T,py,ext,T+ext*2);
    // Sharp rim at tile boundary
    X.fillStyle='rgba(92,179,175,'+(glow*0.42)+')';
    X.fillRect(px,py,T,1); X.fillRect(px,py+T-1,T,1);
    X.fillRect(px,py,1,T); X.fillRect(px+T-1,py,1,T);
    // Inner teal depth
    X.fillStyle='rgba(71,158,153,'+(glow*0.22)+')'; X.fillRect(px,py,T,3);
    ...
```

**Math verification of outer glow:**
- Extension: 5px beyond tile edge (covers actual 4.2px + margin)
- Outer band alpha peak: 0.6 * 0.12 = **0.072** (subtle, doesn't compete with rim)
- Outer band alpha trough: 0 (disappears at pulse low)
- Outer band is always less intense than rim at same phase — depth hierarchy: inner(0.132) > rim(0.252) > outer(0.072) wait... the rim should be brightest. Let me reconsider.

**Revised alpha hierarchy (brightest to dimmest at peak):**
1. Rim at tile edge: `0.252` — strongest visual boundary
2. Inner depth fill: `0.132` — subtle depth inside tile
3. Outer danger glow: `0.072` — faint extension beyond tile

This hierarchy is correct — rim is brightest, inner is moderate, outer is dimmest. The outer glow creates a "halo" effect that extends the perceived danger zone without overpowering the main tile.

**Lines affected:** ~12 lines (lines 1884-1895 block)
**Lines added:** ~6 (outer glow band + comment)
**Risk:** Low — fillRect on AIR space adjacent to tile; no overlap issues with current chamber layouts (pits always bordered by WALL or AIR, never by another hazard tile at the 5px extension boundary)

---

### TASK 4: Enhance champagne hairline cracks to match new intensity

**File:** `golem.html`, line 1891
**Change:** Increase crack stroke alpha multiplier from `0.15` to `0.22`

```
BEFORE:
  X.strokeStyle='rgba(197,179,145,'+(glow*0.15)+')'; X.lineWidth=1;

AFTER:
  X.strokeStyle='rgba(197,179,145,'+(glow*0.22)+')'; X.lineWidth=1;
```

**Rationale:** Champagne cracks at 0.15 peaked at 0.09 — barely visible. At 0.22, they peak at 0.132, matching the inner glow intensity. Maintains proportional balance: cracks are subtle secondary detail, not primary hazard signal.

**Lines affected:** 1 line (line 1891)
**Lines added:** 0
**Risk:** None

---

## 4. Complete Before/After Diff

```diff
 } else if(t===PIT){
     X.fillStyle=COLORS.pit; X.fillRect(px,py,T,T);
     const glow=Math.sin(now/600+x)*0.3+0.3;
+    // Outer danger glow — extends 5px beyond tile to reflect 1.1x hitbox (35.2px Manhattan)
+    const ext=5;
+    X.fillStyle='rgba(92,179,175,'+(glow*0.12)+')';
+    X.fillRect(px-ext,py,T+ext*2,ext); X.fillRect(px-ext,py+T,T+ext*2,ext);
+    X.fillRect(px-ext,py,ext,T+ext*2); X.fillRect(px+T,py,ext,T+ext*2);
     X.fillStyle='rgba(92,179,175,'+(glow*0.28)+')';
+    X.fillStyle='rgba(92,179,175,'+(glow*0.42)+')';
     X.fillRect(px,py,T,1); X.fillRect(px,py+T-1,T,1);
     X.fillRect(px,py,1,T); X.fillRect(px+T-1,py,1,T);
-    X.fillStyle='rgba(71,158,153,'+(glow*0.15)+')'; X.fillRect(px,py,T,3);
+    X.fillStyle='rgba(71,158,153,'+(glow*0.22)+')'; X.fillRect(px,py,T,3);
-    X.strokeStyle='rgba(197,179,145,'+(glow*0.15)+')'; X.lineWidth=1;
+    X.strokeStyle='rgba(197,179,145,'+(glow*0.22)+')'; X.lineWidth=1;
     X.beginPath(); X.moveTo(px+5,py); X.lineTo(px+T/2,py+T/3); X.lineTo(px+T-5,py); X.stroke();
     X.beginPath(); X.moveTo(px+5,py+T); X.lineTo(px+T/2,py+2*T/3); X.lineTo(px+T-5,py+T); X.stroke();
     X.beginPath(); X.moveTo(px,py+T/2-T/6); X.lineTo(px+T/6,py+T/2); X.lineTo(px,py+T/2+T/6); X.stroke();
     X.beginPath(); X.moveTo(px+T,py+T/2-T/6); X.lineTo(px+5*T/6,py+T/2); X.lineTo(px+T,py+T/2+T/6); X.stroke();
```

**Net line count change:** +6 lines (4 fillRect for outer glow + 1 const ext + 1 comment)
**Total new lines in render block:** 21 (was 15)

---

## 5. Validation Gates

### Gate 1: Spec Compliance
- [ ] Teal rim alpha at pulse peak >= 0.25
  - Verify: glow=0.6, alpha=0.6*0.42=0.252 >= 0.25 ✓
- [ ] Visual at glance at 800x480 resolution
  - Verify: Outer glow extends 5px beyond tile — visible as teal halo

### Gate 2: Consistency Check
- [ ] Color palette uses only brand tokens (Seafoam `#5CB3AF` = `92,179,175`; Teal Deep `#479E99` = `71,158,153`; Champagne `#C5B391` = `197,179,145`)
  - Verify: All rgba values match existing palette ✓
- [ ] No `shadowBlur` or gradients used
  - Verify: Only `fillRect` and `stroke` primitives ✓
- [ ] Matches existing visual language
  - Verify: Concentric layers consistent with END_PORTAL approach ✓

### Gate 3: No Gameplay Impact
- [ ] `inPit()` function unchanged (lines 693-705)
  - Verify: No changes to collision logic ✓
- [ ] Chamber data unchanged
  - Verify: No changes to tile layouts ✓
- [ ] No new constants, data structures, or allocations
  - Verify: Only inline render code ✓

### Gate 4: Code Quality
- [ ] No syntax errors (JS parse check)
- [ ] No browser console errors at 800x480
- [ ] `python3 tools/chamber_diff.py --strict` passes (chamber data untouched)
- [ ] File still loads via `file://` protocol
- [ ] Outer glow doesn't visually clash with adjacent tiles in any chamber

### Gate 5: Visual QA at 800x480
- [ ] Pit rim clearly visible against Midnight bg (#12121F) at all pulse phases where glow > 0.1
- [ ] Outer glow visible but not overpowering — doesn't obscure adjacent tiles
- [ ] Champagne cracks visible at pulse peak but subtle at trough
- [ ] Overall hierarchy maintained: rim > inner > outer > cracks

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Outer glow overlaps adjacent hazard tiles | Low | Visual clash | Current chambers: pits bordered by WALL/AIR only. 5px extension won't reach adjacent tiles (min gap = 32px between tiles). |
| Glow too subtle at low pulse | Medium | Missed danger cue | Pulse trough has alpha=0 (existing behavior). Mid-pulse outer glow at 0.036 is subtle but present. Rim at mid-pulse = 0.126, still visible. |
| Performance impact | Negligible | None | 4 additional fillRect calls per PIT tile, already in render loop. No measurable impact. |
| Breaking existing chambers | None | None | Render-only change; no data/collision modifications. |

---

## 7. Summary of Alpha Values (Before vs After)

| Element | Color | Before (peak) | After (peak) | Spec |
|---------|-------|---------------|--------------|------|
| Teal rim (tile edge) | `rgba(92,179,175,a)` | 0.168 | **0.252** | >= 0.25 ✓ |
| Inner glow (top 3px) | `rgba(71,158,153,a)` | 0.09 | **0.132** | N/A (design) |
| Outer glow (5px ext) | `rgba(92,179,175,a)` | — | **0.072** | N/A (new) |
| Champagne cracks | `rgba(197,179,145,a)` | 0.09 | **0.132** | N/A (design) |

**Pulse phase = 0.6 (sin=+1):**
- Rim: `0.6 * 0.42 = 0.252`
- Inner: `0.6 * 0.22 = 0.132`
- Outer: `0.6 * 0.12 = 0.072`
- Cracks: `0.6 * 0.22 = 0.132`

**Pulse phase = 0.3 (sin=0, mid):**
- Rim: `0.3 * 0.42 = 0.126`
- Inner: `0.3 * 0.22 = 0.066`
- Outer: `0.3 * 0.12 = 0.036`
- Cracks: `0.3 * 0.22 = 0.066`

**Pulse phase = 0.0 (sin=-1, trough):**
- All alpha = 0 (existing behavior preserved)
