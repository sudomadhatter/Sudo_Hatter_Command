---
name: suite-red-file-may-have-run-nothing
description: "⛔ run_all.py's file-level count CANNOT distinguish 'one bad assertion' from 'died at import, zero cases ran'. Four files in SCC-321 were in the second state and their symptoms named the wrong cause every time. Read the per-file tally, not the file count."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b93ad8ff-4583-4d2c-96b3-58f746f45e90
  modified: 2026-08-25T18:31:52.042Z
---

`run_all.py` reports `N/61 files passed`. A file that fails is **one** entry in that list whether it
failed one assertion out of 186 or **raised before scoring a single case**. Those two states are
byte-identical in the summary, and they need completely different work.

Measured in SCC-321 (2026-08-25): four files were in the second state.

- `test_allow_scratchpad` — `os.getuid()` at MODULE level, so the import died on Windows. Reported as
  one failure; **0 of 186 cases ran.**
- `test_jira_ticket`, `test_risk_seam` — a fixture stub Windows could not launch, so the `argv.json`
  the cases read was never written and the file died at `FileNotFoundError`. **0 cases each.**
- `test_hooks_armed` — `errs(r)[0]` on an empty list → `IndexError`, taking the file down **after**
  the cases before it had passed.

**Why:** it distorts every judgement built on the count. A "flat 43→44" read as *nothing moved* while
`allow_scratchpad` had gone from 0 to 145 cases actually executing, and `main_push_gate` from 15
static greps to 69 real ones. Worse in the other direction: `subprocess.run(["sh", …])` **raises**
rather than returning a bad exit code, so the FIRST such call kills the file — the remaining cases
are not failures, they are absences, and nobody is looking for them.

**How to apply:** when a suite file is red, read its own `-- X/Y passed --` line **before** doing
anything else. **No tally at all means nothing ran** — fix the import or the fixture first; the
reported symptom is describing a corpse, not a defect. When judging progress, quote the per-file
tallies, never the file count alone. And when a case must stand down on a platform, make it a
**named failing check**, never a bare `return` — `test_main_push_gate` printed `15/15 passed`, exit
0, having tested none of the main write gate's behaviour, because a silent early return is
indistinguishable from a pass. Related: [[mac-authored-code-hides-windows-bugs]],
[[piping-a-gate-hides-its-exit-code]], [[red-test-can-die-before-its-assertion]].
