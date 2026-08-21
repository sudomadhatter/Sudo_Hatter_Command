---
name: review-lenses-die-on-suite-output
description: A review lens told to run run_all.py fills its OWN context and dies without returning — filter every command you hand a subagent.
metadata: 
  node_type: memory
  type: project
  originSessionId: eeee4141-7130-43af-8b2b-50bfa56213a5
  modified: 2026-08-21T03:29:15.960Z
---

Measured 2026-08-20 on SCC-201. The five-lens fan-out (`code-review-engine`) was launched twice
and **every lens died without returning** — 200–400 KB of transcript each, then silence, no
completion notification, no task record. Not a crash: **context exhaustion inside the lens.**

The cause was the caller's, not the lenses'. Three lens prompts said *"you can run the tests — do
it"*, and `run_all.py` prints every passing case across 40 files. One lens was additionally told to
apply three mutants and re-run the suite each time. That output lands in the **lens's** context.
A 143 KB diff (over half of it generated mirrors — byte-copies of files already in the diff) was
the other half of the burn.

**Why:** a subagent's context is invisible from the orchestrator. The failure looks like a hang,
and the transcript file cannot be read back to diagnose it without overflowing the orchestrator
too — so the only signal is *large file, then no writes*.

**How to apply:**
- **Never tell a subagent to run `run_all.py` bare.** Give it the filtered form:
  `python3 test_<x>.py --case "<substring>" 2>&1 | grep -E "^\[FAIL|passed" | tail -10`.
- Prefer a throwaway script that imports the function and prints ONE line over running a test file.
- Hand lenses a **code-only diff** — exclude `.opencode/`, `.agents/workflows/` and artifacts;
  they are byte-copies and prose. On SCC-201 that was 143 KB → 66 KB.
- Give each lens an explicit tool-call budget and tell it to return when it hits it.
- If the fan-out dies anyway, run the review **inline and record it as inline** — the engine drops
  the Blind Hunter rather than fake it, and the floor caps at CONCERNS. See
  [[piping-a-gate-hides-its-exit-code]] for the sibling trap in the orchestrator's own shell.
