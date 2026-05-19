# Execution Plan: showMessage System Refactor

**Date**: 2026-05-19
**Target**: `golem.html` (1234 lines)
**Status**: Plan — ready for executor-agent handoff
**Phase**: RIPER → Plan

---

## 1. Objective

Replace the single-slot message system (one `messageText` + `messageTimer` global) with a FIFO-queued, phased-fade message system supporting:
- 3-second fade-in, auto-calculated display hold, 3-second fade-out
- Message queue with max depth for overlapping events
- Auto-duration based on text length for readability
- "Forever" messages (ending screen) with immediate display + queue flush
- Updated guard at line 1193 for the new queue architecture
- Easy optimizations identified during research

---

## 2. Current State (Baseline)

| Component | Current Code | Line(s) |
|-----------|-------------|---------|
| Global state | `let messageText = ''; let messageTimer = 0;` | 248-249 |
| showMessage function | `function showMessage(txt,dur){ messageText=txt; messageTimer=dur\|\|120; }` | 553 |
| Countdown in update() | `if(messageTimer>0) messageTimer--;` | 666 |
| Render logic | `if(messageTimer>0 && messageText){ const alpha=Math.min(1, messageTimer/30); ... }` | 1165-1169 |
| Guard | `if(ch===0 && glyphsCollected===0 && messageTimer<=0){ ... "I awaken..." hint ... }` | 1193-1196 |

**12 call sites** (see research-message-system.md Section 2):
- 2 via `killAndRespawn` wrapper (lines 735, 858)
- 10 direct calls (lines 482, 590, 617-620, 626, 630, 646, 656, 1226)
- Durations range from 60 to 150 frames (1-2.5s display), plus 99999 for ending

---

## 3. Design

### 3.1 New Global State (replaces lines 248-249)

```js
// Replace:
//   let messageText = '';
//   let messageTimer = 0;

// With:
let messageQueue = [];          // FIFO queue: [{text, hold, phase, elapsed}, ...]
                                 // phase: 'fadeIn' | 'display' | 'fadeOut'
                                 // hold:   frames at full opacity (auto-calculated or from dur arg)
                                 // elapsed: frames spent in current phase
```

### 3.2 Constants (added near existing constants, ~line 54)

```js
const MSG_FADE_IN_FRAMES   = 180;   // 3 seconds at 60fps
const MSG_FADE_OUT_FRAMES  = 180;   // 3 seconds at 60fps
const MSG_MAX_QUEUE_DEPTH  = 5;     // max pending messages
const MSG_CHARS_PER_FRAME  = 0.35;  // ~21 chars/sec reading speed, ~15 frames per char
const MSG_MIN_HOLD         = 90;    // minimum display time (1.5s at full opacity)
const MSG_MAX_HOLD         = 360;   // maximum display time (6s — prevents very long text from lingering)
const MSG_FOREVER_THRESHOLD = 99999; // sentinel for permanent messages
```

### 3.3 Auto-Duration Calculation

Reading speed: average reader reads ~200-250 wpm. For short game messages:
- Formula: `Math.floor(text.length / MSG_CHARS_PER_FRAME)`
- Clamped to `[MSG_MIN_HOLD, MSG_MAX_HOLD]`
- The provided `dur` argument acts as a *minimum floor* — auto-duration only increases, never decreases below it.

```js
function calcDisplayDuration(text, providedDur) {
    const auto = Math.floor(text.length / MSG_CHARS_PER_FRAME);
    const dur = providedDur || MSG_MIN_HOLD;
    return Math.min(MSG_MAX_HOLD, Math.max(dur, auto));
}
```

### 3.4 New showMessage() Function (replaces line 553)

```js
function showMessage(txt, dur) {
    const isForever = (dur || 0) >= MSG_FOREVER_THRESHOLD;

    if (isForever) {
        // "Forever" messages: clear queue, display immediately in 'display' phase
        messageQueue = [{ text: txt, hold: dur || MSG_FOREVER_THRESHOLD, phase: 'display', elapsed: 0 }];
        return;
    }

    // Dedup: skip if same text is already at the front of queue (prevents spam)
    if (messageQueue.length > 0 && messageQueue[0].text === txt) return;

    // Queue if room available
    if (messageQueue.length < MSG_MAX_QUEUE_DEPTH) {
        const hold = calcDisplayDuration(txt, dur);
        messageQueue.push({ text: txt, hold: hold, phase: 'fadeIn', elapsed: 0 });
    }
    // Silently drop if queue full (preserve max depth constraint)
}
```

**Key behaviors:**
- "Forever" messages (duration >= 99999) **always** flush the queue and display immediately
- Identical consecutive messages are deduplicated (optimization #1)
- Queue silently drops messages beyond max depth (prevents backlog during rapid events)

### 3.5 Update Loop (replaces line 666)

```js
// Replace: if(messageTimer>0) messageTimer--;
// With:
if (messageQueue.length > 0) {
    const msg = messageQueue[0];
    msg.elapsed++;

    if (msg.phase === 'fadeIn' && msg.elapsed >= MSG_FADE_IN_FRAMES) {
        msg.phase = 'display'; msg.elapsed = 0;
    } else if (msg.phase === 'display' && msg.elapsed >= msg.hold) {
        msg.phase = 'fadeOut'; msg.elapsed = 0;
    } else if (msg.phase === 'fadeOut' && msg.elapsed >= MSG_FADE_OUT_FRAMES) {
        messageQueue.shift();  // completed — next message auto-starts
    }
}
```

**Note:** "Forever" messages stay in 'display' phase indefinitely (hold = 99999, will not reach threshold during gameplay).

### 3.6 Render Logic (replaces lines 1165-1169)

```js
// Replace:
//   if(messageTimer>0 && messageText){
//     const alpha=Math.min(1, messageTimer/30);
//     X.fillStyle='rgba(212,168,75,'+alpha+')';
//     X.font='bold 18px serif'; X.textAlign='center';
//     X.fillText(messageText, W/2, H/2-60);
//   }

// With:
if (messageQueue.length > 0) {
    const msg = messageQueue[0];
    let alpha = 1;
    if (msg.phase === 'fadeIn') alpha = msg.elapsed / MSG_FADE_IN_FRAMES;
    else if (msg.phase === 'fadeOut') alpha = 1 - (msg.elapsed / MSG_FADE_OUT_FRAMES);

    X.fillStyle = 'rgba(212,168,75,' + alpha + ')';
    X.font = 'bold 18px serif'; X.textAlign = 'center';

    // Optimization #2: text shadow for readability on busy backgrounds
    X.shadowColor = 'rgba(0,0,0,0.7)'; X.shadowBlur = 4;
    X.fillText(msg.text, W/2, H/2 - 60);
    X.shadowBlur = 0;  // reset to avoid affecting other renders
}
```

### 3.7 Guard Update (replaces line 1193)

```js
// Replace:
//   if(ch===0 && glyphsCollected===0 && messageTimer<=0){
// With:
if(ch===0 && glyphsCollected===0 && messageQueue.length===0){
```

This is a simple 1-character conceptual change: `messageTimer<=0` becomes `messageQueue.length===0`. Both evaluate to "no message currently showing."

### 3.8 No Changes Needed at Call Sites

All 12 call sites keep their existing signatures. The function signature `showMessage(txt, dur)` is preserved — only the internal behavior changes.

---

## 4. Execution Steps (Ordered)

### Step 1: Add Constants (~line 54)

**File:** `golem.html`
**Action:** Insert message system constants after the existing physics constants block (after line 60, before line 62).

```js
/* ── Message system constants ── */
const MSG_FADE_IN_FRAMES   = 180;
const MSG_FADE_OUT_FRAMES  = 180;
const MSG_MAX_QUEUE_DEPTH  = 5;
const MSG_CHARS_PER_FRAME  = 0.35;
const MSG_MIN_HOLD         = 90;
const MSG_MAX_HOLD         = 360;
const MSG_FOREVER_THRESHOLD = 99999;
```

**Validation:** No runtime impact yet — constants only.

---

### Step 2: Replace Global State (lines 248-249)

**File:** `golem.html`
**Action:** Replace:
```js
let messageText = '';
let messageTimer = 0;
```
With:
```js
let messageQueue = [];
```

**Validation:** `messageText` and `messageTimer` are only used at lines 553, 666, 1165-1169, 1193 — all of which are modified in subsequent steps.

---

### Step 3: Replace showMessage() (line 553)

**File:** `golem.html`
**Action:** Replace the single-line function with the full implementation including `calcDisplayDuration` helper.

**Before (line 553):**
```js
function showMessage(txt,dur){ messageText=txt; messageTimer=dur||120; }
```

**After:**
```js
/* ── Message queue system ── */
function calcDisplayDuration(text, providedDur) {
    const auto = Math.floor(text.length / MSG_CHARS_PER_FRAME);
    const dur = providedDur || MSG_MIN_HOLD;
    return Math.min(MSG_MAX_HOLD, Math.max(dur, auto));
}
function showMessage(txt, dur) {
    const isForever = (dur || 0) >= MSG_FOREVER_THRESHOLD;
    if (isForever) {
        messageQueue = [{ text: txt, hold: dur || MSG_FOREVER_THRESHOLD, phase: 'display', elapsed: 0 }];
        return;
    }
    if (messageQueue.length > 0 && messageQueue[0].text === txt) return;
    if (messageQueue.length < MSG_MAX_QUEUE_DEPTH) {
        messageQueue.push({ text: txt, hold: calcDisplayDuration(txt, dur), phase: 'fadeIn', elapsed: 0 });
    }
}
```

**Validation:** All 12 call sites use `showMessage(txt, dur)` — signature preserved. No call-site changes needed.

---

### Step 4: Replace Update Loop Timer (line 666)

**File:** `golem.html`
**Action:** Replace:
```js
if(messageTimer>0) messageTimer--;
```
With:
```js
if(messageQueue.length>0){const m=messageQueue[0];m.elapsed++;if(m.phase==='fadeIn'&&m.elapsed>=MSG_FADE_IN_FRAMES){m.phase='display';m.elapsed=0;}else if(m.phase==='display'&&m.elapsed>=m.hold){m.phase='fadeOut';m.elapsed=0;}else if(m.phase==='fadeOut'&&m.elapsed>=MSG_FADE_OUT_FRAMES){messageQueue.shift();}}
```

**Note:** Keep it as a single line to match the minified style of the surrounding code (line 666 is currently a single line).

**Validation:** The `portalLockMsg` decrement on line 667 is unaffected.

---

### Step 5: Replace Render Logic (lines 1165-1169)

**File:** `golem.html`
**Action:** Replace the message render block.

**Before:**
```js
if(messageTimer>0 && messageText){
    const alpha=Math.min(1, messageTimer/30);
    X.fillStyle='rgba(212,168,75,'+alpha+')';
    X.font='bold 18px serif'; X.textAlign='center';
    X.fillText(messageText, W/2, H/2-60);
}
```

**After:**
```js
if(messageQueue.length>0){
    const m=messageQueue[0];
    let alpha=1;
    if(m.phase==='fadeIn')alpha=m.elapsed/MSG_FADE_IN_FRAMES;
    else if(m.phase==='fadeOut')alpha=1-(m.elapsed/MSG_FADE_OUT_FRAMES);
    X.fillStyle='rgba(212,168,75,'+alpha+')';
    X.font='bold 18px serif'; X.textAlign='center';
    X.shadowColor='rgba(0,0,0,0.7)'; X.shadowBlur=4;
    X.fillText(m.text, W/2, H/2-60);
    X.shadowBlur=0;
}
```

---

### Step 6: Update Guard (line 1193)

**File:** `golem.html`
**Action:** Replace `messageTimer<=0` with `messageQueue.length===0`.

**Before:**
```js
if(ch===0 && glyphsCollected===0 && messageTimer<=0){
```

**After:**
```js
if(ch===0 && glyphsCollected===0 && messageQueue.length===0){
```

---

## 5. Optimizations Included

### Optimization 1: Message Dedup (in showMessage)
**What:** If the same text is at the front of the queue, skip adding a duplicate.
**Why:** Prevents queue fill-up from repeated events (e.g., rapid portal lock attempts — though `portalLockMsg` already handles this).
**Cost:** One string comparison per call.

### Optimization 2: Text Shadow for Readability (in render)
**What:** `X.shadowColor='rgba(0,0,0,0.7)'; X.shadowBlur=4;` around fillText.
**Why:** Message text is currently plain on potentially busy backgrounds (stars, tiles, particles). Shadow ensures contrast.
**Cost:** Two property sets per frame when message visible. Reset with `X.shadowBlur=0` immediately after.

### Optimization 3: Max Queue Depth (in showMessage)
**What:** Silently drop messages when queue exceeds 5 entries.
**Why:** Prevents unbounded memory growth and excessive message backlog during rapid-fire events.
**Cost:** None — early return.

---

## 6. Additional Optimization Opportunities (Noted but Not Included)

These are low-effort improvements the executor *may* add if scope allows:

### A4: Urgency/Override Mode
Death messages could `unshift` to front instead of `push`. Current design: death messages are rare enough that queueing is acceptable. Would require adding a third parameter `showMessage(txt, dur, urgent)`.

### A5: Pre-measured text width
If messages have very different widths, centered text may "jump" between messages. Could add a subtle background pill/box. Low priority — current messages are all short enough to not cause visual issues.

### A6: Easing curves
Current fade is linear. A simple ease-in-out (`t < 0.5 ? 2*t*t : -1+(4-2*t)*t`) would make fades feel smoother. Can be added later as polish.

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| "Forever" message never clears | Low | High | Only triggered by `transitionEnding()` which sets `gameState='ending'` and blocks further game logic |
| Queue depth causes backlog | Low | Low | Max depth of 5; typical overlap scenarios involve 1-2 simultaneous messages |
| Fade timing feels too slow | Medium | Low | 3s fade is explicit requirement; can be tuned by changing `MSG_FADE_IN_FRAMES` |
| Auto-duration too aggressive | Low | Low | Clamped to [90, 360] frames (1.5-6s); existing durations preserved as minimum |
| Breaking change to guard logic | Very low | High | Simple equality check replacement; same boolean semantics |

---

## 8. Validation Checklist

After implementation:
- [ ] Game loads without console errors
- [ ] "I awaken..." intro message shows with smooth fade-in/fade-out
- [ ] "I awaken..." hint at top of screen appears only after intro message fully completes
- [ ] Glyph collection messages display with readable hold times
- [ ] Death messages queue behind ability messages (not clobbered)
- [ ] Ending "forever" message clears queue and displays permanently
- [ ] Test chamber messages queue correctly
- [ ] Portal lock message (70 frames) has adequate display time via auto-duration
- [ ] No memory leaks (queue empties between messages)
- [ ] Text shadow renders correctly on all backgrounds

---

## 9. Effort Estimate

- **Lines changed:** ~15 lines replaced, ~10 lines added (constants)
- **Net change:** ~25 lines added, ~5 lines removed = +20 lines
- **Complexity:** Low — single-file, no new dependencies, no architectural changes
- **Estimated implementation time:** 1 executor session

---

## 10. Files Affected

| File | Lines | Change Type |
|------|-------|-------------|
| `golem.html` | 54, 248-249, 553, 666, 1165-1169, 1193 | Modify (6 locations) |

No new files created. No files deleted. Single-file architecture preserved per governance rule 3.

---

**Plan Status: APPROVED FOR EXECUTION**
Ready for executor-agent to implement steps 1-6 sequentially.
