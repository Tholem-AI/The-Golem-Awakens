# Fix: Left/Right Input Asymmetry Bug

## Goal

Fix the directional input asymmetry where pressing both Left and Right simultaneously always resolves to Right (because `inputRight()` is evaluated second and overwrites `inputX`). The fix should resolve ties by using the **most recently pressed** horizontal direction key, matching standard platformer input priority.

## Current context / assumptions

- **File:** `golem.html` (single-file HTML game, ~2513 lines)
- **Bug location:** Lines 1272-1273 in the `update()` function
  ```js
  let inputX = 0;
  if(inputLeft()) inputX=-1;
  if(inputRight()) inputX=1;
  ```
- **Root cause:** Sequential if-statements with no tie-breaking logic. Right always wins.
- **Input abstraction:** `inputLeft()` returns `keys['ArrowLeft'] || keys['KeyA']` (line 608). `inputRight()` returns `keys['ArrowRight'] || keys['KeyD']` (line 609).
- **Key state:** `keys{}` (line 582), `prevKeys{}` (line 583). Event listeners: keydown (line 585), keyup (line 601).
- **Existing direction tracking:** `P.facing` (line 514), `P.lastFacing` (line 519), `P.dashDir` (line 512). No per-key recency tracking exists.
- **Call sites:** `inputLeft()`/`inputRight()` called ONLY at lines 1272-1273. No gamepad/touch input to consider.
- **All consumers of `inputX` (lines 1274-1280, turn lean, facing, dash, acceleration/friction) work identically regardless of value. No code depends on "Right always wins."**
- **Reset:** `resetGameState()` resets `keys={}` and `prevKeys={}` at line 2359.

## Proposed approach

Introduce a lightweight `lastDirKey` global variable (int: -1=left, 0=none, 1=right) that tracks which horizontal direction key was **most recently pressed**. When both directions are held, use `lastDirKey` as the tiebreaker. On keyup, recalculate from remaining held keys.

This is a **minimal, surgical change** that:
- Adds only 1 new global variable and ~10 lines of code total
- Preserves all existing abstraction layers (`inputLeft()`/`inputRight()`)
- Is zero-cost outside the rare "both held" edge case
- Follows the existing code style (flat globals, direct key access)

## Step-by-step plan

### Step 1: Add `lastDirKey` global variable

**File:** `golem.html` — after line 583 (after `let prevKeys = {};`)

**Insert:**
```js
let lastDirKey = 0; // -1=left, 0=none, 1=right (most recently pressed horizontal key)
```

**Validation gate:** File parses without JS syntax errors. No runtime impact yet.

---

### Step 2: Update keydown handler to track recency

**File:** `golem.html` — inside the keydown listener (lines 585-600)

**After** line 586 (`keys[e.code] = true;`), insert horizontal key tracking:

```js
// Track most recently pressed horizontal direction key
if(e.code === 'ArrowLeft' || e.code === 'KeyA') lastDirKey = -1;
if(e.code === 'ArrowRight' || e.code === 'KeyD') lastDirKey = 1;
```

**Full keydown handler after edit:**
```js
document.addEventListener('keydown', function(e){
  keys[e.code] = true;

  // Track most recently pressed horizontal direction key
  if(e.code === 'ArrowLeft' || e.code === 'KeyA') lastDirKey = -1;
  if(e.code === 'ArrowRight' || e.code === 'KeyD') lastDirKey = 1;

  /* Title screen: any key starts the game */
  if(gameState==='title'){
    startGame();
    e.preventDefault();
    return;
  }
  // ... rest unchanged
});
```

**Validation gate:** Pressing Left or Right alone still moves the character in the correct direction. No regression on single-key input.

---

### Step 3: Update keyup handler to recalculate on release

**File:** `golem.html` — line 601

**Replace:**
```js
document.addEventListener('keyup', function(e){ keys[e.code] = false; });
```

**With:**
```js
document.addEventListener('keyup', function(e){
  keys[e.code] = false;
  // Recalculate lastDirKey when a horizontal key is released
  if(e.code === 'ArrowLeft' || e.code === 'ArrowRight' || e.code === 'KeyA' || e.code === 'KeyD'){
    if(inputLeft() && inputRight()) lastDirKey = 0; // both still held by alternate key, neutralize
    else if(inputLeft()) lastDirKey = -1;
    else if(inputRight()) lastDirKey = 1;
    else lastDirKey = 0;
  }
});
```

**Rationale:** When a direction key is released, we check which keys remain pressed. If both sides still have a key held (e.g., player was holding A+D and releases D, but S was also... no, S isn't horizontal), we need the correct remaining direction. If `ArrowLeft` and `KeyD` are both held and `ArrowLeft` is released, `inputLeft()` is now false, `inputRight()` is true, so `lastDirKey = 1` (correct). If `ArrowLeft` and `ArrowRight` are both held and `ArrowRight` is released, `inputLeft()` is true, `inputRight()` is false, so `lastDirKey = -1` (correct). The `both still held` case (e.g., holding A+D and releasing a non-direction key) can't happen here because the handler only fires when a direction key is released, so if both are still true after release, it means alternate keys on each side are held — neutralize to 0 and let the next keydown set the tiebreaker.

**Validation gate:** Releasing one direction key while the other is held still moves in the remaining direction. Releasing both keys stops horizontal movement.

---

### Step 4: Modify input resolution to use `lastDirKey` as tiebreaker

**File:** `golem.html` — lines 1271-1273

**Replace:**
```js
let inputX = 0;
if(inputLeft()) inputX=-1;
if(inputRight()) inputX=1;
```

**With:**
```js
let inputX = 0;
if(inputLeft()) inputX=-1;
if(inputRight()) inputX=1;
if(inputLeft() && inputRight()) inputX = lastDirKey || 1;
```

**Rationale:** The existing two lines handle the single-direction case (one true, one false). The third line catches only the "both held" case and resolves the tie using `lastDirKey`. If `lastDirKey` is 0 (shouldn't happen when both are held, but defensive), defaults to 1 (right) — preserving the original behavior as a fallback.

**Alternative (cleaner):** Replace all three lines with:
```js
let inputX = 0;
if(inputLeft() && !inputRight()) inputX = -1;
else if(!inputLeft() && inputRight()) inputX = 1;
else if(inputLeft() && inputRight()) inputX = lastDirKey || 1;
```
This is slightly more explicit but functionally identical. **Recommendation: Use the 3-line addition approach (first version) for minimal diff and easier review.**

**Validation gate:** When both Left+Right are held, direction follows the most recently pressed key. Releasing and pressing one side updates the direction immediately.

---

### Step 5: Reset `lastDirKey` in `resetGameState()`

**File:** `golem.html` — line 2359

**Replace:**
```js
keys={}; prevKeys={};
```

**With:**
```js
keys={}; prevKeys={}; lastDirKey=0;
```

**Validation gate:** Game reset returns to a clean state. No stale `lastDirKey` persists across resets.

---

## Files likely to change

| File | Lines affected | Change type |
|------|----------------|-------------|
| `golem.html` | ~583 (new variable) | Insert 1 line |
| `golem.html` | ~586 (keydown) | Insert 3 lines |
| `golem.html` | ~601 (keyup) | Replace 1 line with ~9 lines |
| `golem.html` | ~1272-1273 (input resolution) | Add 1 line |
| `golem.html` | ~2359 (reset) | Append to existing line |

**Total: ~15 lines of code changed in a single file.**

## Tests / validation

### Manual browser verification test plan

**Prerequisites:** Open `golem.html` in a browser (Chrome/Firefox/Safari). Start the game.

| # | Test case | Steps | Expected result |
|---|-----------|-------|-----------------|
| 1 | Single Left | Hold `ArrowLeft` only | Character moves left |
| 2 | Single Right | Hold `ArrowRight` only | Character moves right |
| 3 | Left then Right (both held) | Hold `ArrowLeft`, then press `ArrowRight` | Character moves right |
| 4 | Right then Left (both held) | Hold `ArrowRight`, then press `ArrowLeft` | Character moves left |
| 5 | Release last-held while both held | Hold both, release the one you pressed last | Character switches to the remaining direction |
| 6 | Release remaining while both held | Hold both, release the one you pressed first | Character stops (no horizontal input) |
| 7 | WASD + Arrows mixed | Hold `A`, then press `ArrowRight` | Character moves right |
| 8 | WASD + Arrows mixed reverse | Hold `ArrowLeft`, then press `D` | Character moves left |
| 9 | Game reset | Hold both directions, then reset game | Clean state, no stale direction |
| 10 | Dash direction | Hold both, press last-held direction, dash | Dash fires in last-held direction |

### Automated validation (if applicable)

Not applicable — single-file HTML game with no test framework. Manual verification is the primary validation method.

**Syntax validation:** Run `node -c golem.html` or open in browser DevTools Console to confirm no JS parse errors after edits.

## Risks, tradeoffs, and open questions

### Risks (all low)

1. **Keyup recalculation edge case:** If a player holds `A`+`D` simultaneously (both sides), then releases `A` — `inputLeft()` becomes false, `inputRight()` stays true, so `lastDirKey=1`. This is correct behavior. The tricky case is holding `A`+`D` (both held, `lastDirKey` set by last press), then releasing `ArrowLeft` (which isn't even held) — this can't trigger the keyup handler for `ArrowLeft` since it wasn't pressed. No issue.

2. **Performance:** The keyup recalculates `inputLeft()`/`inputRight()` (two OR checks each). This is negligible overhead (4 boolean checks on a rare event).

3. **Alternate key combinations:** If player holds `ArrowLeft` and `KeyD` simultaneously, both `inputLeft()` and `inputRight()` return true. The `lastDirKey` correctly reflects whichever was pressed last.

### Tradeoffs

- **Keeps the fix local to input resolution** — doesn't modify `inputLeft()`/`inputRight()` abstractions, preserving clean separation between key-state and input logic.
- **`lastDirKey || 1` fallback** preserves original "right wins" behavior if `lastDirKey` somehow ends up 0 while both are held (defensive, shouldn't occur).

### Optimization opportunities (noted, low priority)

- The keyup recalculates `inputLeft()` and `inputRight()` which do redundant OR checks. Could cache `keys` lookups locally, but this is a micro-optimization in an already negligible path.
- Could consolidate the keyup direction key list into a constant array for maintainability, but the inline check is clear enough for this small scope.
