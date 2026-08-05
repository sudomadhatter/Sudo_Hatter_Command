---
name: governance-gate-scans-venv
description: "AGY's grading_events governance grep-gate (and clones) walk backend/.venv unless pruned — 16,586 files / ~273 MB per test. CLOSED 2026-08-03: this latent gap WAS the xdist tail-hang. Prune is name-based, so a venv named env311/pyenv reinstates it."
metadata:
  node_type: memory
  type: project
  originSessionId: 29a3554a-5eb7-4c23-a269-e2afd538b4cb
  modified: 2026-08-04T01:16:08.829Z
---

AGY's structural governance grep-gates (`backend/tests/routers/test_grading_event_governance_gate.py`,
the tea-14 clone `test_quiz_bank_governance_gate.py`, `test_demo_quarantine_gate.py`, and the 21.10
bypass-flag scan) walk `backend/` and READ every `.py` they find. `backend/.venv` sits directly under
`BACKEND`, so an unpruned scan reads **16,586 files / ~273 MB instead of 217** (measured 2026-08-03).

**This latent gap was not theoretical — it WAS the "xdist tail-hang."** The grading_events gate has 7
tests, each doing that read. `--dist loadfile` pins all 7 to ONE worker; with the other workers
saturating the box each read blew the 300 s ceiling, and pytest-timeout's Windows *thread* method
`os._exit`s the process — so the worker went `node down` and respawned, seven times ≈ the ~40 min of
churn recorded on 2026-08-01. It read as xdist state coupling for two days. **CI never saw it**: CI's
dependencies install into the runner's own site-packages, not under `backend/`, so CI stayed green on
the same commit. Closed as quick fix 1.1 — see [[agy-canonical-test-venv]] for the runner state.

**Status: CLOSED.** `1ea90071` (2026-08-02) rewrote the scans to prune during `os.walk`. Quick fix
1.1 (2026-08-03) confirmed it and added the pin this memory asked for a month earlier.

**Three lessons that outlive the bug:**
- **"It only fails in parallel" is NOT automatically state coupling.** Resource self-contention among
  xdist workers presents identically — same tail position, same "passes serially". Two sessions hunted
  leaked globals, import-order effects and un-reverted mocks before anyone asked what each test *costs*.
  Check the cost first; it is one measurement, and it is cheap.
- **A gitignored, machine-local artifact can be the entire cause.** Invisible to git AND to CI is
  exactly the shape that reads as mysterious.
- **Grep the board's own changelog for the file before re-investigating.** `1ea90071` and the tail-hang
  write-up were two accurate records of the same fact, one screen apart, unjoined for a day.

**How to apply:**
- **Prune DURING `os.walk`, never `rglob` + a post-hoc filter.** rglob descends into the venv before
  any filter can skip it, so the walk cost stays and a dangling junction raises from `os.scandir`.
- `EXCLUDE_DIRS = {"tests","__pycache__",".venv","venv","site-packages","node_modules",".git","build"}`
  plus `not d.startswith(".venv")` is the current shape in all four gates.
- ⚠️ **That prune is BY NAME.** A venv under `backend/` named anything else — `env311`, `pyenv`,
  `venv3` — is walked and read again and the hang returns **on that machine only**, silently. The pin
  `test_scan_never_walks_a_colocated_virtualenv` detects venvs by **`pyvenv.cfg` marker** instead, so
  that becomes a 10-second named red. Warned in the new-machine migration guide §5.
- When cloning a governance gate, copy the pruning `_scan_files()` — not the old rglob template.

See [[gitnexus-impact-misses-attribute-dispatch]] for another grep-verify-before-trusting pattern.
