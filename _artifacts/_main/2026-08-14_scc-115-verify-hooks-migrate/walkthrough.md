# SCC-115 — Verify & Automate Git Hooks Migration

**Lane:** `chore/SCC-115-verify-hooks-migrate` · cut from `main` @ `d9b35ac`  
**Parent:** Grouping Task · **Lane:** LOCAL · **Close:** `/smh-close-task-merge-tree`

---

## 1. Problem & Context

Git by design does *not* copy `.git/config` or `.git/hooks` across machines or clone boundaries. While gate scripts reside in version control (`.githooks/` and `.agents/scripts/git-hooks/`), every fresh clone on a new machine starts with `core.hooksPath` unset, leaving all Jira, encoding, and SOP-currency gates dormant.

**Ticket SCC-115 Goal:** Verify how hooks migrate across machines, create a robust, automated installer for all machines (Windows, macOS, Linux) under `docs/migrations/`, and update the migration documentation.

---

## 2. What Was Built

1. **Centralized Installer Engine** — [`docs/migrations/scripts/install_git_hooks.py`](file:///c:/Sudo_Hatter_Command/docs/migrations/scripts/install_git_hooks.py):
   - Auto-discovers repo root and all git submodules in `Projects/`.
   - Configures `core.hooksPath .githooks` for each repository.
   - Sets executable (`0o755`) permissions on POSIX for all dispatchers and gate scripts.
   - Integrates with `.agents/scripts/hooks_armed.py` to audit and report armed status (with soft-warning handling for un-gated projects).
   - Supports `--verify-only`, `--json`, and `--repo <path>`.

2. **Cross-Platform Wrappers**:
   - PowerShell: [`docs/migrations/scripts/Install-GitHooks.ps1`](file:///c:/Sudo_Hatter_Command/docs/migrations/scripts/Install-GitHooks.ps1)
   - POSIX Bash: [`docs/migrations/scripts/install-git-hooks.sh`](file:///c:/Sudo_Hatter_Command/docs/migrations/scripts/install-git-hooks.sh)

3. **Automated Integration Test Suite** — [`.agents/scripts/tests/test_install_git_hooks.py`](file:///c:/Sudo_Hatter_Command/.agents/scripts/tests/test_install_git_hooks.py):
   - 19 test assertions covering discovery, arming, verify-only, JSON output, error reporting, and live repo validation.

4. **Updated Migration Runbooks**:
   - [`docs/migrations/INDEX.md`](file:///c:/Sudo_Hatter_Command/docs/migrations/INDEX.md): Step 2b updated to cite `Install-GitHooks.ps1` and `install-git-hooks.sh`.
   - [`docs/migrations/install_guides/machine_setup_card.md`](file:///c:/Sudo_Hatter_Command/docs/migrations/install_guides/machine_setup_card.md): Step 1 updated with one-shot installer commands.

---

## 3. Evidence & Verification

| # | Acceptance Requirement | Result |
|---|---|---|
| 1 | Hooks migration behavior analyzed and documented | Confirmed `core.hooksPath` is local to each clone and must be explicitly configured per machine. |
| 2 | Cross-platform installer in `docs/migrations/scripts/` | Authoring complete: Python engine + `.ps1` + `.sh` wrappers. |
| 3 | Automated test suite verifying installer logic | `test_install_git_hooks.py`: **19/19 PASSED**. |
| 4 | Live arming across all local projects | `Sudo_Hatter_Command`, `AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`, `NEXgen-VR-Director`: **ALL ARMED**. |
| 5 | Runtime gate verification | `test_hooks_armed.py`: **59/59 PASSED** (live repo reports ARMED). |
| 6 | Documentation alignment | `docs/migrations/INDEX.md` and `machine_setup_card.md` updated and verified with `sop_currency.py`. |

### Test Suite Execution Output
```
== install_git_hooks (SCC-115) ==
[PASS] discovers root repo
[PASS] discovers subprojects with .git
[PASS] skips non-git subdirectories
[PASS] total discovered count is 3
[PASS] initially core.hooksPath is unset
[PASS] arm_single_repo sets hooksPath
[PASS] arm_single_repo reports armed = True
[PASS] arm_single_repo has zero errors
[PASS] git config reflects .githooks
[PASS] verify_only does not set hooksPath
[PASS] verify_only reports unarmed
[PASS] git config remains unset
[PASS] CLI returns exit 0: rc=0
[PASS] JSON output parsed successfully
[PASS] JSON reports 0 total_errors
[PASS] JSON contains 2 results
[PASS] live repository has core.hooksPath set
[PASS] live repository reports ARMED
[PASS] live repository has 0 errors: []
-- 19/19 passed --
```

---

## 4. Your Action Required

- [x] Authenticate `acli` CLI (`acli jira auth login --web`) — completed.
- [x] Run `Install-GitHooks.ps1` to arm local repos — executed.
- [ ] Review changes and approve closing the ticket via `/smh-close-task-merge-tree`.
