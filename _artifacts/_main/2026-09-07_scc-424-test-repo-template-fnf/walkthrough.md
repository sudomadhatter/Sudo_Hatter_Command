# Walkthrough — SCC-424: Fix FileNotFoundError Escape in `test_repo_template.py`

**Ticket:** SCC-424 (Task)
**Lane:** `chore/SCC-424-test-repo-template-fnf`, cut from `origin/main` at `9878aa7c`
**Plan:** [implementation_plan.md](implementation_plan.md)
**Date:** 2026-09-07

## What this closes, in one paragraph

Under concurrent runner execution in CI (observed on PR #187 attempt 1), `test_repo_template.py` failed after 11 successful cases with `[FAIL] no unexpected error escaped a block: FileNotFoundError(2, 'No such file or directory')`. The root causes were twofold in `_repo_template.py`: `shared_root()` was memoised on `_ROOT` without verifying that the directory still existed on disk, returning a purged directory that caused subsequent `mkdtemp` calls to fail with `FileNotFoundError`; and `_verify_sealed()` was blind to deleted template roots (`Path.rglob("*")` returns `[]` on missing directories), allowing `clone()` to attempt `.iterdir()` on a deleted path. We fixed both at the source: `shared_root()` now self-heals by regenerating `_ROOT` and purging stale cache entries if the directory is missing, while `_verify_sealed()` and `clone()` defensively assert that template directories exist, raising `TemplateCorrupted` with full context rather than letting `FileNotFoundError` escape. Additionally, `test_repo_template.py:main()` now formats unhandled exceptions with full error text and traceback location.

## Task Checklist
- [x] Reproduce and isolate defect with failing RED assertions in `test_repo_template.py` (`T5 · deleted-template-dir` and `shared_root` recovery).
- [x] Implement self-healing in `_repo_template.shared_root()`: detect missing directory on disk, clear `_CACHE`, and create a fresh temporary root.
- [x] Add defensive assertions in `_repo_template._verify_sealed()` and `_repo_template.clone()` to reject non-existent template roots with `TemplateCorrupted`.
- [x] Enhance `test_repo_template.py:main()` unhandled error formatting with `{type(exc).__name__}: {exc}{loc}` to prevent missing paths from being hidden behind bare `repr(exc)`.
- [x] Add assertion in `test_repo_template.py:T1` that `rt.shared_root().is_dir()` exists.
- [x] Verify all test suites and full regression suite (`run_all.py` 81/81 passed).
- [x] Update `_artifacts/_main/INDEX.md` with the SCC-424 entry.

## Evidence

### 1. RED Phase Verification
Before the fix, running `test_repo_template.py --case T5` failed with the exact unhandled errors:
```
[FAIL] a cached template deleted from disk is REFUSED with TemplateCorrupted: raised FileNotFoundError(2, 'No such file or directory') — expected TemplateCorrupted
[FAIL] shared_root() heals and returns an existing directory if deleted: /tmp/wfscripts-tpl-grhqvtnr is not a directory
-- 6/8 passed --
FAILED: a cached template deleted from disk is REFUSED with TemplateCorrupted, shared_root() heals and returns an existing directory if deleted
```

### 2. GREEN Phase Verification
After applying the fixes to `_repo_template.py`:
```
== repo template clones (SCC-214) ==
-- tree: scc-424-test-repo-template-fnf [chore/SCC-424-test-repo-template-fnf] - worktree --
...
[PASS] a cached template deleted from disk is REFUSED with TemplateCorrupted: raised TemplateCorrupted('cached template /tmp/wfscripts-tpl-act1tfwt/wfscripts-tpl-rr445avy no longer exists on disk - a scenario or sibling cleanup removed the template root (SCC-424)') — expected TemplateCorrupted
[PASS] shared_root() heals and returns an existing directory if deleted: /tmp/wfscripts-tpl-nl5zwf7d is not a directory
-- 8/8 passed --
```

Full file run of `test_repo_template.py`:
```
-- 49/49 passed --
```

Preflight consumers (`test_git_hooks.py`, `test_task_preflight.py`, `test_task_preflight_receipts.py`):
```
test_git_hooks.py: -- 163/163 passed --
test_task_preflight.py & test_task_preflight_receipts.py: -- 39/39 passed --
```

### 3. Linters & Gate Checks
- `python3 .agents/scripts/workflow_lint.py --toolkit-only`: `0 error(s), 0 warning(s)`
- `python3 .agents/scripts/check_maps.py --depth3-only --strict`: `37/37 passed, exit 0`

## Suite Ledger
Running `python3 .agents/scripts/tests/run_all.py` across all 81 test files:
```
============================================================
81/81 files passed
```

## Step 0.7 — re-derivation

1. **Did anything this diff references move, rename or delete on main?** No. `git diff --name-only <merge-base>..origin/main` shows no overlapping modifications; main is clean.
2. **True overlap and merge result.** Overlap is empty. Changes are strictly confined to `_repo_template.py` and `test_repo_template.py`.
3. **Sibling lanes and landing order.** None. This task lane lands directly on main as a chore branch.

## Code Review (2026-09-07)

lenses_run:
- `blind-hunter` · `ok`
- `edge-case-hunter` · `ok`
- `code-standards` · `ok`
- `acceptance-auditor` · `ok`
- `test-adequacy-auditor` · `ok`

lenses_na: none

dispositions: per-lens: blind-hunter=0/0/0 · edge-case-hunter=0/0/0 · code-standards=0/0/0 · acceptance-auditor=0/0/0 · test-adequacy-auditor=0/0/0

drift: undeclared=0 · unimplemented=0 · incomplete=0

Verdict: PASS @ b1af567c

### Review Findings & Verification
1. **Defensive Guarantees**: `shared_root()` ensures `_ROOT` is valid and recreates it if purged, clearing `_CACHE` to eliminate dangling references.
2. **Deterministic Errors**: `_verify_sealed()` and `clone()` now explicitly catch deleted directories and raise `TemplateCorrupted` with informative paths and keys, preventing bare `FileNotFoundError` from escaping to the outer harness.
3. **Preserved Observability**: In `test_repo_template.py:main()`, unexpected escapes will format the exception message and traceback source location, avoiding silent diagnostic loss.
4. **Zero Regressions**: All 81 test suites pass with zero failures or skips in `run_all.py`.

## Your Actions

- [x] The merge itself — lands via this branch's PR
