# Implementation Plan: Fix SCC-450 (Antigravity Workspace Registration Failure in Remote-WSL)

Resolve Jira issue **SCC-450**: *Antigravity registers no workspace - Gemini runs outside this repo law*.

## Consequence & Problem Statement
When Antigravity starts inside VS Code Remote-WSL, the webview client running in the Windows Electron host detects `navigator.userAgent` containing `"Windows"` and sets `window.process.platform = "win32"`.

Downstream, `vscode-uri`'s `fsPath` getter checks `process.platform === "win32"` and transforms `/home/dlohn/Sudo_Hatter_Command` into `\home\dlohn\Sudo_Hatter_Command`. 

When the webview calls ConnectRPC `AddTrackedWorkspace` on the Linux `agy` daemon (`127.0.0.1:<port>`), Go's `filepath.IsAbs(workspace)` rejects `\home\dlohn\...` because on POSIX, absolute paths must start with `/`. The registration fails with:
`AddTrackedWorkspace (unknown): \home\dlohn\Sudo_Hatter_Command must be an absolute path: path is not absolute`

`agy` falls back to the nonexistent `<HOME>/.gemini/config/projects/outside-of-project.json`, leaving Gemini operating with zero registered workspace and completely blind to repository laws, skills, and gates.

---

## User Review Required

> [!IMPORTANT]
> **Zero File Modifications Occur Before Approval.**
> Execution will strictly take place within a dedicated worktree on a chore branch off `main`, in accordance with repo law.

- **Target Worktree:** `.claude/worktrees/SCC-450/`
- **Branch:** `chore/SCC-450-antigravity-workspace-posix` off `main`
- **Safety Precaution:** Before altering the binary `/home/dlohn/.gemini/bin/agy`, a pristine timestamped backup (`agy.bak.<timestamp>`) will be created and verified.

---

## Declared Change Set

- NEW `.agents/scripts/patch_agy_posix.py` — surgical binary patcher for agy web assets index.html → AC1, AC2
- NEW `.agents/scripts/check_antigravity_workspace.py` — health check and watchdog for agy POSIX workspace → AC1, AC2, AC4
- NEW `.agents/scripts/tests/test_antigravity_posix.py` — regression test suite for agy POSIX path handling → AC1, AC4
- EDIT `.agents/scripts/INDEX.md` — register new maintenance and check scripts in scripts index → AC4

---

## Proposed Changes

### Component 1: Isolated Worktree Setup
Per [AGENTS.md §6](file:///home/dlohn/Sudo_Hatter_Command/AGENTS.md#L93) and [worktree-per-story.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/worktree-per-story.md), cut the dedicated worktree:
- Path: `.claude/worktrees/SCC-450/`
- Branch: `chore/SCC-450-antigravity-workspace-posix`

---

### Component 2: Surgical Binary Patcher for `agy`
The embedded webview bundle in `/home/dlohn/.gemini/bin/agy` contains `index.html` within a standard zip archive at offset `184733042` to `188067463`.
The code:
```javascript
window.process.platform =
  ua.indexOf("Windows") >= 0
    ? "win32"
    : ua.indexOf("Macintosh") >= 0 || ua.indexOf("Mac OS") >= 0
      ? "darwin"
      : "linux";
```
Because the `agy` binary is a 64-bit Linux ELF executable running exclusively on Linux/WSL, paths passed to it must always be POSIX.

#### [NEW] [.agents/scripts/patch_agy_posix.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/patch_agy_posix.py)
A robust Python utility that:
1. Backs up `/home/dlohn/.gemini/bin/agy` to `/home/dlohn/.gemini/bin/agy.bak.<timestamp>`.
2. Locates the embedded web assets zip in the binary.
3. Updates `index.html` so that `ua.indexOf("Windows") >= 0 ? "win32"` is replaced with `? "linux"` (an exact 5-byte to 5-byte replacement, preserving identical uncompressed length).
4. Deflates and reconstructs the zip stream while preserving the exact binary offsets, central directory structure, and total file length (`213,582,080` bytes) without displacing downstream segments.
5. Sets executable permissions (`chmod +x`).
6. Supports `--check` (idempotent verification) and `--restore` (instant rollback to backup).

---

### Component 3: Permanent Watchdog, Registration & Tests
To ensure the fix survives automatic CLI updates (`agy update`):

#### [NEW] [.agents/scripts/check_antigravity_workspace.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/check_antigravity_workspace.py)
- CLI health check that verifies:
  1. Binary patch status (`index.html` in `agy` does not set `win32`).
  2. Live `agy --hub` RPC response: calls `AddTrackedWorkspace` with `/home/dlohn/Sudo_Hatter_Command` and confirms HTTP 200 OK.
  3. Log file check: parses the active `~/.gemini/antigravity/cli.log` and ensures zero occurrences of `must be an absolute path: path is not absolute`.

#### [NEW] [.agents/scripts/tests/test_antigravity_posix.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_antigravity_posix.py)
*(⚠️ AUDIT FINDING: Path aligned with repository test convention `.agents/scripts/tests/`)*
Automated pytest test suite covering:
- Binary invariant test: asserts that `agy`'s web bundle does not contain the Windows platform coercion that breaks POSIX path handling.
- RPC contract test: verifies that `AddTrackedWorkspace` accepts POSIX paths and properly tracks the repository.
- Error prevention test: fails if any backslashed path pattern is emitted.

#### [EDIT] [.agents/scripts/INDEX.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/INDEX.md)
*(⚠️ AUDIT FINDING: Registered new maintenance scripts in scripts inventory to prevent orphaned tooling)*
- Register `patch_agy_posix.py` and `check_antigravity_workspace.py` in the scripts table.

---

## Verification Plan

### Automated Tests
1. Run the patcher in `--check` mode to confirm binary integrity.
2. Run `pytest .agents/scripts/tests/test_antigravity_posix.py -v`.
3. Restart `agy --hub` (or reload VS Code window).
4. Run `.agents/scripts/check_antigravity_workspace.py` to confirm 0 errors in fresh logs.

### Manual & Live Acceptance Verification
1. **Log Inspection:** Inspect the new `~/.gemini/antigravity/cli-*.log` to verify:
   - `AddTrackedWorkspace` succeeds with 0 errors.
   - `outside-of-project.json` is NEVER requested.
2. **Live Skill Invocation (AC 3):**
   - Demonstrate Gemini natively invoking a skill from `.agents/skills/` (e.g. `/smh-sync-agents` or `/mermaid-diagram-standards`).
3. **Walkthrough:**
   - Create `walkthrough.md` with evidence matrix, logs, and test results.
   - Close Jira ticket SCC-450.

---

## Self-Audit (2026-09-12)

**Level:** LEDGER+BLAST (PRE-WORK)  
**Ticket:** SCC-450 (*Antigravity registers no workspace - Gemini runs outside this repo law*)  
**Plan:** `implementation_plan.md`

### Lens 1 — Repo Reality + Scope Ledger
```
lens:        1 Repo Reality + Scope Ledger
checks_run:  path_existence · declared_change_set_parse · dual_side_commands · lane_fit · scope_ledger
read:        .agents/scripts/tests/ · .agents/scripts/declared_change_set.py · .agents/scripts/INDEX.md
verdict:     clean (fixes applied inline)
```

#### Scope Ledger
| Created Artefact (op: NEW) | Acceptance Criteria Served | Callers / Integrations |
|---|---|---|
| `.agents/scripts/patch_agy_posix.py` | AC1, AC2 | Called by `check_antigravity_workspace.py --apply`, test suite, operator |
| `.agents/scripts/check_antigravity_workspace.py` | AC1, AC2, AC4 | Standing CLI health check, CI gate, test suite |
| `.agents/scripts/tests/test_antigravity_posix.py` | AC1, AC4 | `pytest .agents/scripts/tests/test_antigravity_posix.py`, `run_all.py` |

Precondition check: Ticket SCC-450 carries 4 concrete observable acceptance rows (AC1: clean startup log with 0 AddTrackedWorkspace errors; AC2: workspace resolves to `/home/dlohn/Sudo_Hatter_Command`; AC3: Gemini invokes `/<name>` skill live; AC4: automated test fails on backslashes). Precondition satisfied. Every created artefact maps to ≥1 acceptance row. Zero ungrounded creations.

---

### Lens 2 — Parity + Blast
```
lens:        2 Parity + Blast
checks_run:  command_parity · rule_parity · script_index · githooks · sibling_worktrees · risk_seam
read:        git worktree list · git diff origin/main...HEAD (.claude/worktrees/SCC-451-inert-paths) · risk_seam.py
verdict:     clean (findings resolved inline)
```

- **Script Index Parity:** `.agents/scripts/INDEX.md` added as an `EDIT` to avoid orphan scripts.
- **Risk Seam Classification:** `risk_seam.py classify` returned `unclassified` (standard for command centre repository; no code graph).
- **Sibling Worktrees:** Sibling worktree `.claude/worktrees/SCC-451-inert-paths` is active on `chore/SCC-451-inert-paths` and has modified `.agents/scripts/INDEX.md`. Landing dependency identified: merge conflicts on `INDEX.md` must be cleanly resolved upon rebase/merge.

---

### Lens 3 — Pre-Mortem
```
lens:        3 Pre-Mortem
checks_run:  fresh_clone_failure · cli_update_overwrite · wrong_test_discovery_runner
read:        .agents/scripts/tests/run_all.py · /home/dlohn/.gemini/bin/agy
verdict:     clean (failure modes mitigated)
```

- **Failure Narrative 1 (CLI Auto-Update):** An automated `agy update` or extension upgrade could replace the patched `/home/dlohn/.gemini/bin/agy` binary with a newly downloaded upstream binary containing the original `"win32"` string.  
  *Mitigation:* `.agents/scripts/check_antigravity_workspace.py` provides an instant check and `--apply` repair mode, and `test_antigravity_posix.py` guards this invariant in the test suite.
- **Failure Narrative 2 (Test Discovery):** Placing tests in root `tests/` would evade the repository's `.agents/scripts/tests/` discovery harness (`run_all.py`).  
  *Mitigation:* Path corrected to `.agents/scripts/tests/test_antigravity_posix.py`.

---

### Findings Summary
| Anchor | Literal Text Read | Consequence | Severity |
|---|---|---|---|
| `implementation_plan.md:38` | `declared_change_set.py parse` -> `"present": false` | Plan lacked machine-readable change set, blocking review drift checks | important (FIXED) |
| `implementation_plan.md:71` | `#### [NEW] [tests/test_antigravity_posix.py]` | Violates repo test suite convention under `.agents/scripts/tests/` | important (FIXED) |
| `.agents/scripts/INDEX.md` | Inventory of maintenance scripts | Adding new scripts without updating index causes inventory drift | suggestion (FIXED) |
| `.claude/worktrees/SCC-451-inert-paths` | `git diff --name-only origin/main...HEAD` includes `INDEX.md` | Concurrent edits to `INDEX.md` by SCC-451 requires clean rebase | suggestion (NOTED) |

### Observations
- Binary patching of `agy` must preserve the exact byte length (`213,582,080` bytes) to prevent shifting subsequent ELF sections and symbols. The patcher will verify pre- and post-patch sizes match byte-for-byte.

Audit verdict: GO
