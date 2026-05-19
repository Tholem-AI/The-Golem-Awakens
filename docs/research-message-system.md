# showMessage System — Research Findings

**Date**: 2026-05-19
**Target**: `golem.html` (1234 lines, single-file HTML5 canvas game)
**Game loop**: 60fps via `requestAnimationFrame`

---

## 1. Current Architecture

The message system is a **single-slot, first-come-first-served** display with a countdown timer.

### Global State (lines 248-249)
```js
let messageText = '';
let messageTimer = 0;
```

### Function Definition (line 553)
```js
function showMessage(txt, dur) { messageText = txt; messageTimer = dur || 120; }
```
- Overwrites whatever message is currently showing.
- No queuing — overlapping calls silently clobber each other.

### Countdown (line 666, inside `update()`)
```js
if(messageTimer > 0) messageTimer--;
```
- Decrements every frame (1/60s per tick).
- No special handling for zero — just stops decrementing.

### Render Logic (lines 1165-1169)
```js
if(messageTimer > 0 && messageText) {
    const alpha = Math.min(1, messageTimer / 30);
    X.fillStyle = 'rgba(212,168,75,' + alpha + ')';
    X.font = 'bold 18px serif'; X.textAlign = 'center';
    X.fillText(messageText, W/2, H/2 - 60);
}
```

**Current fade behavior:**
- `alpha = messageTimer / 30`, clamped to max 1.0
- This means: message appears at FULL opacity immediately, then stays fully opaque until `messageTimer < 30`, then fades out over the last 30 frames (0.5s).
- **There is NO fade-in.** The message pops in instantly.
- **Fade-out is only 0.5 seconds** (30 frames at 60fps).

**Position:** Centered horizontally (`W/2`), vertically at `H/2 - 60` (y = 180 on a 480px canvas).

---

## 2. All Call Sites (12 calls)

### 2.1 `killAndRespawn` — wrapper (line 94)
```js
showMessage(msg, duration);
```
Called from 2 places:

| Line | Context | Message | Duration (frames) | Duration (seconds) |
|------|---------|---------|-------------------|--------------------|
| 735 | Magical wall collision | `"The barrier consumes you..."` | 90 | 1.5s |
| 858 | Pit/fall death | `"The void claims clay..."` | 90 | 1.5s |

### 2.2 Direct calls

| Line | Context | Message | Duration (frames) | Duration (seconds) |
|------|---------|---------|-------------------|--------------------|
| 482 | Push block placed in slot | `"The weight settles."` | 80 | 1.33s |
| 590 | Locked portal attempt | `"The seal demands Knowledge..."` | 70 | 1.17s |
| 617 | Glyph 1 collected | `"Knowledge lifts me."` | 120 | 2.0s |
| 618 | Glyph 2 collected | `"Speed courses through me."` | 120 | 2.0s |
| 619 | Glyph 3 collected | `"Strength returns."` | 120 | 2.0s |
| 620 | Glyph 4 collected | `"Clay becomes Wisdom."` | 120 | 2.0s |
| 626 | Ending (test mode) | `"The Ibis speaks: 'You were clay...'"` | 99999 | forever |
| 630 | Ending (normal) | `"The Ibis speaks: 'You were clay...'"` | 99999 | forever |
| 646 | Exit test chamber | `"Back to chamber X."` | 60 | 1.0s |
| 656 | Enter test chamber | `"Test chamber — all abilities unlocked."` | 90 | 1.5s |
| 1226 | Game start | `"I awaken..."` | 150 | 2.5s |

---

## 3. Coupling: `messageTimer` as a Guard (line 1193)

```js
if(ch === 0 && glyphsCollected === 0 && messageTimer <= 0) {
    X.fillStyle = '#665a4a'; X.font = '14px serif'; X.textAlign = 'center';
    X.fillText('I awaken...', W/2, 60);
}
```

**Purpose:** The `"I awaken..."` hint text at the top of the screen only appears after the initial `showMessage('I awaken...', 150)` intro message has faded out. The `messageTimer <= 0` check prevents both the full-screen message and the hint from showing simultaneously.

**Impact of change:** This coupling means that if we replace the single `messageTimer` with a queue-based system, we need an equivalent "is any message currently showing?" check here. Options:
- `messageQueue.length > 0` (if queue includes currently-displaying message)
- A separate boolean flag `isMessageShowing`
- `activeMessage !== null` (if we track the current display separately from the queue)

---

## 4. Overlap Scenarios (Current Behavior)

The system has **no overlap protection**. These scenarios can cause issues:

1. **Death during ability unlock:** If the player falls into a pit right after collecting a glyph, the death message (`"The void claims clay..."`) immediately overwrites the ability message. The ability message was only visible for a fraction of a second.

2. **Portal lock during push block:** Placing a push block (`"The weight settles."`, 80 frames) then immediately trying a locked portal (`"The seal demands Knowledge..."`, 70 frames) — second message overwrites the first.

3. **Test chamber transitions:** `"Back to chamber X."` (60 frames) is very short and can be interrupted by death messages.

4. **Game start overlap:** `"I awaken..."` (150 frames) at game start can be overwritten if the player immediately dies.

---

## 5. Required Changes

### 5.1 New showMessage() signature
- Display duration should be **longer** so users can actually read.
- Full **fade-in over 3 seconds** (180 frames).
- Full **fade-out over 3 seconds** (180 frames).
- Hold at full opacity for the message display duration.

**Total lifecycle per message:** fade-in (180) + display (dur) + fade-out (180).
For a typical 2s message: 180 + 120 + 180 = 480 frames = 8 seconds total.

### 5.2 Queue System for Overlapping Messages
- When a new message arrives while one is already displaying, queue it instead of clobbering.
- The currently-displaying message should NOT be interrupted — let it complete its full lifecycle.
- After the current message fully fades out, dequeue and start the next one.
- Consider a **max queue depth** (e.g., 3-5) to prevent message backlog during rapid-fire events.
- The 99999-frame ending messages should probably **clear the queue** or be treated as a special "final" state.

### 5.3 Decouple `messageTimer` Guard
- Line 1193 (`messageTimer <= 0`) needs to become `isNoMessageShowing()`.
- If using a queue where the front element is the active message: `messageQueue.length === 0`.
- If using a separate `activeMessage` + `pendingQueue` design: `activeMessage === null`.

---

## 6. Proposed Design

```js
// Replace: let messageText = ''; let messageTimer = 0;

// New state:
let messageQueue = [];       // [{text, duration, phase, elapsed}, ...]
// phase: 'fade-in' | 'display' | 'fade-out'
// duration: frames at full opacity (the "hold" time)
// elapsed: frames spent in current phase

const FADE_IN_FRAMES  = 180;  // 3 seconds
const FADE_OUT_FRAMES = 180;  // 3 seconds
const MAX_QUEUE_DEPTH = 5;

// New function:
function showMessage(txt, dur) {
    if (gameState === 'ending') {
        // Special case: ending message replaces everything
        messageQueue = [{ text: txt, duration: dur, phase: 'display', elapsed: 0 }];
        return;
    }
    if (messageQueue.length < MAX_QUEUE_DEPTH) {
        messageQueue.push({ text: txt, duration: dur || 120, phase: 'fade-in', elapsed: 0 });
    }
}

// Update loop (replace line 666):
if (messageQueue.length > 0) {
    const msg = messageQueue[0];
    msg.elapsed++;
    if (msg.phase === 'fade-in' && msg.elapsed >= FADE_IN_FRAMES) {
        msg.phase = 'display'; msg.elapsed = 0;
    } else if (msg.phase === 'display' && msg.elapsed >= msg.duration) {
        msg.phase = 'fade-out'; msg.elapsed = 0;
    } else if (msg.phase === 'fade-out' && msg.elapsed >= FADE_OUT_FRAMES) {
        messageQueue.shift();  // remove completed message, next one auto-starts
    }
}

// Render logic (replace lines 1165-1169):
if (messageQueue.length > 0) {
    const msg = messageQueue[0];
    let alpha = 1;
    if (msg.phase === 'fade-in') alpha = msg.elapsed / FADE_IN_FRAMES;
    else if (msg.phase === 'fade-out') alpha = 1 - (msg.elapsed / FADE_OUT_FRAMES);
    X.fillStyle = 'rgba(212,168,75,' + alpha + ')';
    X.font = 'bold 18px serif'; X.textAlign = 'center';
    X.fillText(msg.text, W/2, H/2 - 60);
}

// Guard (line 1193) change:
// From: messageTimer <= 0
// To:   messageQueue.length === 0
```

---

## 7. Optimization Opportunities

1. **Shared text measurement:** If multiple messages have different widths, the centered text may shift. Could pre-measure or add a subtle background pill/box.

2. **Message dedup:** If the same message is called rapidly (e.g., player repeatedly hits a locked portal — though `portalLockMsg` already prevents this), the queue could fill with identical messages. A simple `if (msg.text === messageQueue[0]?.text) return;` check could prevent this.

3. **Urgency/override mode:** Death messages or critical warnings could optionally `unshift` to the front of the queue instead of appending, ensuring important messages display sooner.

4. **Text shadow:** The current message is plain text on potentially busy backgrounds. Adding `X.shadowColor/shadowBlur` would improve readability regardless of background.

---

## 8. Summary

| Aspect | Current | Needed |
|--------|---------|--------|
| Storage | Single text + timer | Queue of message objects |
| Fade-in | None (instant) | 180 frames (3s) |
| Fade-out | 30 frames (0.5s) | 180 frames (3s) |
| Overlap | Clobber (last wins) | Queue, sequential display |
| Guard (line 1193) | `messageTimer <= 0` | `messageQueue.length === 0` |
| Call sites to audit | 12 calls, durations 60-99999 | All should work; may want to adjust durations for longer hold times |
