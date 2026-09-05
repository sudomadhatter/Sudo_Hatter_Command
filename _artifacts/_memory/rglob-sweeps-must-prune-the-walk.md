---
name: rglob-sweeps-must-prune-the-walk
description: "A result-filter on rglob does NOT protect the WALK — on Windows the walk dies inside .venv on over-long torch dist-info paths; prune with os.walk dirnames[:] instead."
metadata: 
  node_type: memory
  type: reference
  originSessionId: ccec7e02-346d-4d32-b2ff-da2abcb9d9b6
  modified: 2026-09-02T01:53:37.590Z
---

**Filtering `.venv` out of `rglob()` RESULTS is not the same as not walking it.** Source-sweep
guard tests (AGY: the 19.1 explicit-key sweep, the 14.2 dossier guard) excluded `.venv` from their
results but `BACKEND_ROOT.rglob("*.py")` still traversed it — and on Windows, `os.scandir` throws
`FileNotFoundError` (WinError 3) on paths past MAX_PATH, which torch's
`dist-info/licenses/third_party/...` tree exceeds. The guard then ERRORS on any machine whose venv
is correct (torch was the lock pin), Windows-only, while passing on POSIX/CI — a fourth way
source-grep guards are blind, and a [[mac-authored-code-hides-windows-bugs]] instance.

**Why:** these failures masquerade as venv skew (they rode inside AVCH-109's "18 env-only reds" and
survived the venv sync that cured the other 15).

**How to apply:** any repo-tree sweep prunes the walk itself — `for dirpath, dirnames, filenames in
os.walk(root): dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED)` — never
`rglob` + result filter. Prove non-vacuously: the pruned walk must still collect real prod files
(AVCH-109 probe: 221 files, `main.py` present, zero `.venv` leakage). Fixed at AVCH-109 `b2ff2ba4`.
See also [[source-grep-guards-cannot-see-order]].
