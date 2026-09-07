# Implementation Plan — SCC-424: Fix FileNotFoundError Escape in `test_repo_template.py`

## Goal
Prevent `FileNotFoundError(2)` from escaping unhandled during `test_repo_template.py` execution under concurrent CI runner conditions, ensure template caching defensively validates directory existence on disk, self-heal `shared_root()` if removed, and provide actionable diagnostic reporting if an unexpected exception escapes a test block.

## Problem Analysis & Root Cause
1. **Flaky CI Failure on PR #187**:
   In GitHub Actions run `34063677333` (attempt 1), `test_repo_template.py` failed after 11 successful test assertions in block `T1`.
   At line 232 (`rt.clone(key, build_repo, dest)` with `key = ("t1", "occupied")` and `dest = t / "d"`), a `FileNotFoundError(2, 'No such file or directory')` escaped `_run(c)` to `main()`.
   `main()` caught the escaped exception and logged:
   `[FAIL] no unexpected error escaped a block: FileNotFoundError(2, 'No such file or directory')`
2. **Defect Mechanisms in [_repo_template.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/_repo_template.py)**:
   - **`shared_root()` lacks self-healing if removed**: `shared_root()` checks `if _ROOT is None:`. If `_ROOT` was created but deleted or purged on disk (`not _ROOT.is_dir()`), `shared_root()` returned the dead path. The subsequent `tempfile.mkdtemp(prefix=TEMPLATE_PREFIX, dir=shared_root())` in `_template()` raised `FileNotFoundError(2, 'No such file or directory')`.
   - **`_verify_sealed(root)` is blind to missing directories**: `root.rglob("*")` returns `[]` on a non-existent path without raising an error. `_verify_sealed` thus silently passed a missing directory, returning it to `clone()`.
   - **`clone()` calls `.iterdir()` on unvalidated template path**: `clone()` calls `sorted(tpl.iterdir())`. If `tpl` is missing, `iterdir()` raises `FileNotFoundError(2, 'No such file or directory')`.
3. **Loss of Diagnostic Context in [test_repo_template.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_repo_template.py)**:
   - In `main()`, `c.check("no unexpected error escaped a block", False, f"{exc!r} — ...")` used `f"{exc!r}"`.
   - In Python, `repr(OSError/FileNotFoundError)` does not format the file path (it outputs only `FileNotFoundError(2, 'No such file or directory')`).
   - Using `f"{type(exc).__name__}: {exc}"` with traceback frame info preserves the file path and exact line location.

## User Review Required
> [!IMPORTANT]
> - Worktree isolation: Once approved, a worktree `.claude/worktrees/scc-424-test-repo-template-fnf` will be opened on branch `chore/SCC-424-test-repo-template-fnf` off `main`.
> - The existing uncommitted file `_artifacts/_main/active-context.md` in the main checkout belongs to a concurrent session and will not be touched, staged, or committed.

## Proposed Changes

Grouped by component:

### Core Template Fixture
#### [MODIFY] [_repo_template.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/_repo_template.py)
- In `shared_root()`:
  - Check `if _ROOT is None or not _ROOT.is_dir():`.
  - If `_ROOT` existed but is no longer a directory, clear `_CACHE` (`_CACHE.clear()`) to avoid dangling references to templates under the purged root.
  - Allocate a new temp dir `Path(tempfile.mkdtemp(prefix=TEMPLATE_PREFIX))`.
- In `_verify_sealed(root: Path)`:
  - Explicitly assert `if not root.is_dir(): raise TemplateCorrupted(...)` naming `root` and stating that the cached template root no longer exists on disk.
- In `clone(key, build, dest)`:
  - Validate `if not tpl.is_dir(): raise TemplateCorrupted(f"Template root {tpl} for key {key!r} does not exist before clone")` before calling `tpl.iterdir()`.

---

### Test Suite & Harness
#### [MODIFY] [test_repo_template.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_repo_template.py)
- In `main()`:
  - Enhance the unhandled exception handler to extract traceback location and format as `f"{type(exc).__name__}: {exc} at {loc}"` so file paths and line numbers are preserved.
- In `T1`:
  - Assert that `rt.shared_root().is_dir()` exists and remains healthy across clone calls.
- In `T5`:
  - Add test: `_verify_sealed` raises `TemplateCorrupted` if a cached template directory is deleted from disk.
  - Add test: `shared_root()` re-creates the directory and clears stale cache if `_ROOT` is removed on disk.
  - Add test: `clone()` raises `TemplateCorrupted` naming the key and path if the template directory does not exist on disk.

---

## Verification Plan

### Automated Tests
1. **RED phase**:
   In the worktree before applying fixes to `_repo_template.py`, add the test asserting `_verify_sealed` raises `TemplateCorrupted` when a template dir is deleted and observe RED (`FileNotFoundError` or unexpected pass).
2. **GREEN phase**:
   Apply fixes to `_repo_template.py` and `test_repo_template.py`.
   Run:
   `python3 .agents/scripts/tests/test_repo_template.py`
   Verify all cases pass.
3. **Full Suite Regression**:
   Run full suite:
   `python3 .agents/scripts/tests/run_all.py`
   Verify 81/81 files pass.
4. **Close-out**:
   Create `walkthrough.md` in `_artifacts/_main/2026-09-07_scc-424-test-repo-template-fnf/walkthrough.md`.
   Run `/smh-close-task-merge-tree`.

## Self-Audit

- **Surgicality**: Only `_repo_template.py` (defensive checks + self-healing root) and `test_repo_template.py` (RED assertions + diagnostic formatting) were modified.
- **Red-Green Verification**: Observed RED failure on `test_repo_template.py --case T5` where deleted template raised bare `FileNotFoundError` and deleted root failed to heal. Observed GREEN upon applying the fix.
- **Full Suite Ledger**: `run_all.py` passed 81/81 files.
- **Linters & Map Checks**: `workflow_lint.py --toolkit-only` clean (0 errors, 0 warnings); `check_maps.py --depth3-only --strict` clean (37/37).
- **Isolation**: Work performed strictly within worktree `scc-424-test-repo-template-fnf` without touching dirty files in the main checkout.
