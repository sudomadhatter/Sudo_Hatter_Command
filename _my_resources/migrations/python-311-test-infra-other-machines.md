# ⚠️ Migration — every OTHER machine needs its venv rebuilt (Python 3.11 + test-infra overhaul, 2026-08-01)

Part of the `_my_resources/migrations/` kit — the Python/venv companion to
[`new_machine-migration-guide.md`](new_machine-migration-guide.md) (which covers secrets;
its §5 points here). Applies to EXISTING machines pulling the 2026-08-01 changes AND to
fresh-machine setups.

**Status:** OPEN until every machine that works on AGY_AVIATIONCHAT has run the checklist below.
Machines done: ☑ desktop (this one, 2026-08-01) · ☐ laptop · ☐ any other clone

---

## Why this task exists

On 2026-08-01 AGY_AVIATIONCHAT was realigned to **Python 3.11** (CI and prod were always 3.11;
local venvs had silently drifted to 3.14 — meaning weeks of local greens were measured on an
interpreter two versions off what ships). Same day, the test infra gained: parallel test runs
(`pytest-xdist`), a per-test hang ceiling (`timeout = 300`), and a **machine-wide suite lock**
in the root `conftest.py` (two big pytest runs on one machine now queue instead of thrashing).

**The trap: venvs are gitignored, so NONE of this travels to other machines via git.**
When another machine pulls these commits it gets the new configs and pins — but keeps its
old venv, and:

- pytest does **NOT** check `requires-python` — a stale 3.14 venv will happily keep running
  tests on the wrong interpreter, and local green goes back to being a lie **on that machine
  only**. Nothing warns you. (Only pip and the CI assert step enforce the declaration.)
- Parallel runs (`-n auto`) are available but **opt-in for now** — gate runs stay serial until
  the xdist tail-hang follow-up closes (see AGY active-context). An old venv without
  `pytest-xdist` fails loudly with `unrecognized arguments: -n` if you do opt in.
- The suite lock needs `filelock` — without it, runs still work but print
  `[suite-lock] filelock not installed — machine serialization OFF` (fail-open by design).

## The 5-minute fix (run on EACH machine, once)

```powershell
# 0. From the AGY_AVIATIONCHAT repo root, on current main_debug:
git pull

# 1. Is Python 3.11 installed on this machine?
py -0p                       # look for a -V:3.11 line
winget install Python.Python.3.11    # only if missing

# 2. Rebuild the canonical venv from 3.11 (deletes the drifted one):
Remove-Item -Recurse -Force backend\.venv
py -3.11 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Verify it didn't break anything (the actual walkthrough)

Run these four checks **in order**. Expected output shown for each.

```powershell
# CHECK 1 — the venv really is 3.11 now
backend\.venv\Scripts\python.exe --version
#   PASS: Python 3.11.x        FAIL: 3.14.x → step 2 above didn't run / wrong launcher

# CHECK 2 — the new pins landed
backend\.venv\Scripts\python.exe -m pip list | Select-String "pytest-xdist|filelock|ruff|pyrefly"
#   PASS: all four listed (xdist 3.8.0, filelock 3.24.3, ruff 0.16.0, pyrefly 1.1.1)

# CHECK 3 — a scoped run works and does NOT wait on the lock (inner loop stays instant)
backend\.venv\Scripts\python.exe -m pytest backend\tests\test_affirmative_classifier.py -q
#   PASS: green, starts immediately, NO [suite-lock] line

# CHECK 4 — the full suite on 3.11 (the real proof; serial = the current gate mode)
backend\.venv\Scripts\python.exe -m pytest backend\tests -q --timeout=300
#   PASS: same totals as the desktop baseline (≈2887 passed / 32 skipped / 0 failed —
#         exact count grows as stories land; 0 failed is the bar), in ~12 min serial.
#   (Parallel -n auto is opt-in until the xdist tail-hang follow-up closes.)
#   Any NEW failure here = a 3.11-vs-3.14 behavior difference on this machine's deps —
#   capture the traceback; that is a real finding, not a reason to roll back.
```

## Messages you may see that are FEATURES, not breakage

| Message | Meaning |
|---|---|
| `[suite-lock] another suite run holds this machine (pid … worktree …) — queued` | The lock working: something else is mid-suite on THIS machine; your run starts the moment it finishes. Never fires across machines (lock lives in that machine's %TEMP%). |
| `[suite-lock] filelock not installed — machine serialization OFF` | Old venv — run the pip install from step 2. Tests still run fine meanwhile. |
| A test fails with `Timeout >300.0s` + a stack dump | The new hang ceiling naming a wedged test — that test was hanging forever before; now it fails loudly with the culprit's stack. |

## Failure signatures → fixes

| Symptom | Cause | Fix |
|---|---|---|
| `unrecognized arguments: -n` | venv predates the xdist pin | `pip install -r backend\requirements.txt` |
| `No module named pytest` right after pulling | you caught a venv mid-rebuild, or step 2 was interrupted | re-run step 2 fully |
| VS Code can't find the interpreter / imports unresolved after the rebuild | stale interpreter path cached | the `python_inter_venv_fix` skill covers this exact case |
| Weird failures only on ONE machine | that machine skipped this checklist — venv still 3.14 | run CHECK 1; rebuild |

## Related facts

- ~~Leftover staging venvs on the desktop~~ — both `backend\.venv311` (staging) and
  `backend\.venv.old314` (rollback) were deleted after the migration verified. Other machines
  never had them; if you see any `.venv*` variant anywhere, it's cruft — delete it.
- CI is immune to all of this (fresh install every run, and the new
  "Assert runner Python satisfies requires-python" step fails loudly on drift).
- Full machine-to-machine moves (secrets etc.) are a separate checklist —
  [`new_machine-migration-guide.md`](new_machine-migration-guide.md) in this same folder
  (`_secrets/master.env` bundle; replaces the old `env-migration-guide.md`).

**Close this task** by checking off every machine at the top, after its CHECK 4 passes.
