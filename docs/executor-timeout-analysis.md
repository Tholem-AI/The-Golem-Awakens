# Executor Agent Timeout Analysis

**Date:** 2026-05-16
**Context:** RIPER refactor of golem.html (1133 lines -> 1153 lines)
**Commit:** d7972d6

---

## What Happened

The executor-agent subagent timed out after 600 seconds (configured `child_timeout_seconds`) during Task 4 of the execution plan.

### Execution Timeline

| Task | Status | Time |
|------|--------|------|
| Task 1: Remove dead pushBlock() | COMPLETED | ~30s |
| Task 2: Remove BLOCK constant | DEFERRED (correct decision) | ~10s |
| Task 3: Fix ch2/c2 redundancy | COMPLETED (during reorg) | - |
| Task 4: Reorganize into 11 sections | **TIMEOUT** | 600s |
| Task 5: Update chamber-template.md | NOT REACHED | - |
| Task 6: Create beyond-scope report | NOT REACHED | - |

Task 4 was manually completed by the orchestrator after the timeout.

---

## Root Cause

**Single massive write_file operation.** Task 4 required rewriting the entire golem.html file (~1153 lines) as a single `write_file()` call. The subagent spent its entire 600-second budget on:

1. Reading the full 1100+ line file (multiple reads for context)
2. Planning the reorganization (identifying section boundaries, verifying function dependencies)
3. Generating the complete rewritten file content (~1153 lines of output)
4. Writing the file with `write_file()`

Each of these steps consumed LLM inference tokens. The subagent's `max_iterations: 50` budget was sufficient, but the `child_timeout_seconds: 600` wall-clock limit was the hard stop.

### Contributing Factors

1. **All 6 tasks delegated to a single subagent** -- the execution plan bundled 6 tasks (including the massive Task 4) into one `delegate_task` call. Task 4 consumed virtually all available time.

2. **Task 4 is a full-file rewrite** -- reorganizing a 1100+ line file means the subagent must output ~1153 lines of content. This is a token-heavy operation: each line of code is both read and regenerated.

3. **No parallelism** -- Tasks 5 (update template) and 6 (write report) are independent of Task 4 but were sequenced after it. They could have run in parallel.

4. **Single-file constraint** -- keeping golem.html as a single HTML file means there is no way to split the work across multiple files. A multi-file project would allow parallel subagents per file.

---

## Fixes

### Fix 1: Split execution into parallel subagents (RECOMMENDED)

Instead of one executor doing all 6 tasks, use batch delegation with independent tasks running concurrently:

```
delegate_task(
    tasks=[
        {goal: "Remove dead code + fix redundancy in golem.html", toolsets: ["file", "terminal"]},
        {goal: "Update chamber-template.md for BLOCK removal", toolsets: ["file"]},
        {goal: "Write beyond-scope simplifications report", toolsets: ["file"]},
    ]
)
```

Then handle the massive Task 4 (reorganization) directly as the orchestrator, since:
- You (the orchestrator) already have the full file context loaded
- No additional reads needed
- Direct `write_file()` is faster than subagent mediation

### Fix 2: Self-execute large file reorganizations

When a task involves rewriting a single file >500 lines, the orchestrator should:
1. Read the file itself (already in context from planning phase)
2. Perform the reorganization directly with `write_file()` or `patch()`
3. Only delegate the smaller independent tasks (docs, templates, reports)

**Rule of thumb:** If a single task's output exceeds 500 lines, do NOT delegate it. The overhead of subagent setup + token generation + timeout risk outweighs the benefit of isolation.

### Fix 3: Increase timeout for known-large tasks (OPTIONAL)

For projects with consistently large files, consider increasing `child_timeout_seconds` in config.yaml:

```yaml
delegation:
  child_timeout_seconds: 900  # 15 minutes instead of 10
```

This is a band-aid, not a fix. The structural fix (Fix 1 + Fix 2) is preferred.

### Fix 4: Use patch() instead of write_file() for reorganizations

For structural reorganizations where the majority of code stays the same (just reordered), a series of targeted `patch()` calls can be more efficient than one massive `write_file()`:

1. Add section delimiter comments (small patches)
2. Cut-and-paste blocks using patch() with unique anchor strings
3. Remove dead code with patch()

This approach is safer (each patch is atomic and reversible) and faster (smaller token payloads).

---

## Riper-Orchestrator Pitfall #8

This scenario is already documented in riper-orchestrator skill, Common Pitfall #8:

> "Executor-agent timeout -- The executor-agent has a 600s timeout and may stall on complex tasks or slow API calls."

The documented recovery procedure was followed correctly:
1. Check what code changes were already applied -- Task 1 confirmed (pushBlock removed)
2. Verify changes directly -- JS syntax check + browser console check passed
3. Continue remaining work manually -- Tasks 3-6 completed by orchestrator

**Recommendation:** Add prescriptive guidance to pitfall #8 about WHEN to self-execute vs delegate, specifically the 500-line rule from Fix 2 above.

---

## Lessons for Future RIPER Runs

1. **Research phase** should flag large files (>500 lines) and recommend self-execution
2. **Planning phase** should split tasks so the largest single task is <500 lines of output
3. **Execution phase** should parallelize independent tasks (docs, templates, reports) with the main code work
4. **Orchestrator** should retain large file reorganizations as direct work, delegating only surgical edits and documentation
