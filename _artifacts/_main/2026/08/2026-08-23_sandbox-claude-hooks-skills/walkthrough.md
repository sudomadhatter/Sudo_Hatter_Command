---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-300: Eliminate Claude Hook Mirror and Direct-Wire Canonical Hooks"
  type: walkthrough
  date: 2026-08-23
---

# SCC-300: Eliminate Claude Hook Mirror and Direct-Wire Canonical Hooks

## Overview & Consequence
Claude Code's internal OS sandbox strictly denies filesystem write access under `.claude/hooks/` and `.claude/skills/` at any depth, even when `sandbox.filesystem.allowWrite` includes the entire workspace. 

Prior to this fix, whenever `main` updated a hook (such as the recent SCC-299 fix to `guard-cwd-escape.py`), git merges (`git merge origin/main`, `git pull`, `git checkout`) in any lane worktree failed with `Operation not permitted: unable to unlink old '.claude/hooks/...'`. Additionally, `/smh-sync-agents` failed in-session when attempting to write `.claude/skills/`.

### What Changed
1. **Direct Hook Execution**: [settings.json](file:///Users/sudohatter/Sudo_Hatter_Command/.claude/settings.json) now wires all hooks (`allow-scratchpad.py`, `require-push-approval.py`, `guard-cwd-escape.py`, `allow-readonly-chain.py`, `rule-trigger.py`) directly to `.agents/hooks/*.py` via `run-hook.sh`. `.agents/hooks/` is the single source of truth and is explicitly writable in the sandbox.
2. **Retired `.claude/hooks/`**: The duplicate `.claude/hooks/` directory has been completely untracked and removed from git. Git will never touch `.claude/hooks/` during worktree merges or checkouts.
3. **Graceful Sandbox Handling in `sync-agents.ps1`**: [sync-agents.ps1](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/sync-agents.ps1) no longer attempts to mirror `.claude/hooks/` and catches `.claude/skills/` sandbox write blocks gracefully in-session, warning the operator while successfully updating `.agents/skills/`, `.agents/workflows/`, `.opencode/commands/`, and machine-global caches.
4. **Clean Verification**: All hook tests ([test_cwd_escape_hook.py](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/tests/test_cwd_escape_hook.py), [test_allow_scratchpad.py](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/tests/test_allow_scratchpad.py), [test_allow_readonly_chain.py](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/tests/test_allow_readonly_chain.py), [test_command_surfaces.py](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/tests/test_command_surfaces.py)) were updated to assert direct `.agents/hooks/` single-source wiring.

---

## Task Checklist
- [x] **A1**: `.claude/settings.json` wires all hooks directly to `.agents/hooks/*.py` through `run-hook.sh`.
- [x] **A2**: `.claude/hooks/` is untracked and deleted from git.
- [x] **A3**: `sync-agents.ps1` removes `.claude/hooks/` sync and handles `.claude/skills/` sandbox restrictions gracefully.
- [x] **A4**: Test suites assert `.agents/hooks/` wiring; all tests and mutation sweeps pass cleanly.
- [x] **A5**: Memory and SOP documentation updated.

---

## Evidence

### Test Suite Execution
- `python3 .agents/scripts/tests/test_cwd_escape_hook.py` → **51/51 passed**
- `python3 .agents/scripts/tests/test_allow_scratchpad.py` → **186/186 passed**
- `python3 .agents/scripts/tests/test_allow_readonly_chain.py` → **149/149 passed**
- `python3 .agents/scripts/tests/test_command_surfaces.py` → **216/216 passed**
- `python3 .agents/scripts/workflow_lint.py --toolkit-only` → **0 errors, 0 warnings**
- `python3 .agents/scripts/check_maps.py --depth3-only --strict` → **Exit 0**
- `python3 .agents/scripts/tests/run_all.py` → **59/59 test files passed**

### Mutation Sweep (`sweep.json`)
```
== mutation_sweep @ SCC-300-sandbox-claude-hooks-skills [chore/SCC-300-sandbox-claude-hooks-skills] - worktree ==
-- sweep: 3 mutant(s) over 1 file(s) @ bca230cb --
KILLED    M1 cwd-escape hook wiring check rejects stray .claude/hooks path
            KILLED by M7 it points directly to .agents/hooks/guard-cwd-escape.py (the single source)
KILLED    M2 scratchpad allow hook wiring check rejects stray .claude/hooks path
            KILLED by WIRING · it points directly to .agents/hooks/allow-scratchpad.py
KILLED    M3 readonly-chain hook wiring check rejects stray .claude/hooks path
            KILLED by WIRING · it points directly to .agents/hooks/allow-readonly-chain.py
-- restore verified: bytes match, nothing was committed, and `git diff --quiet bca230cb` is clean --
-- sweep clean: 3/3 killed by their declared case --
```

### Commit SHA
`ebade3b`

---

## Suite Ledger
| Test File | Result | Total Checks |
|---|---|---|
| `test_cwd_escape_hook.py` | PASS | 51/51 |
| `test_allow_scratchpad.py` | PASS | 186/186 |
| `test_allow_readonly_chain.py` | PASS | 149/149 |
| `test_command_surfaces.py` | PASS | 216/216 |
| `run_all.py` | PASS | 59/59 files |

---

review-runtime: fan-out

## Code Review (2026-08-23)

Verdict: PASS @ ebade3b

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- test-adequacy · ok
- acceptance-auditor · ok
lenses_counted: 4/4

dispositions:    per-lens: blind-hunter=0/0/0 · edge-case-hunter=0/0/0 · test-adequacy=0/0/0 · acceptance-auditor=0/0/0
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — declared set is identical to diff

### Step 0.7 — re-derivation
1. What landing ref moved under this diff: none (clean on `origin/main` at `5c0be93`).
2. True overlap + merge-tree result: overlap empty, `merge-tree` clean (sha `4ed56364d124b2fc12ad12215e5e6b778893f5b1`).
3. Sibling-lane landing-order dependency: independent of live sibling lanes (`chore/SCC-295-label-tasks-dot-strip`, `claude/teaching-edition`).

### Acceptance Matrix
| Acceptance Item | Description | Evidence / Assertion |
|---|---|---|
| A1 | Direct hook wiring in `.claude/settings.json` | `test_cwd_escape_hook.py` (M7), `test_allow_scratchpad.py` (WIRING), `test_allow_readonly_chain.py` (WIRING) |
| A2 | Retirement and removal of `.claude/hooks/` | `git status` shows 9 files deleted in `.claude/hooks/` |
| A3 | Graceful sandbox handling in `sync-agents.ps1` | `sync-agents.ps1` try/catch block around `.claude/skills` write + `.claude/hooks` sync target removed |
| A4 | Test suite & mutation sweep pass | `test_cwd_escape_hook.py` (51/51), `test_allow_scratchpad.py` (186/186), `test_allow_readonly_chain.py` (149/149), `test_command_surfaces.py` (216/216), `run_all.py` (59/59 files), `sweep.json` (3/3 killed) |
| A5 | Memory and SOP documentation updated | `sandbox-denies-writes-under-dot-claude-hooks-skills.md`, `workflows_testing_SOP.md`, `claude-permission-sandboxed.md` |

### Clean-Code Gate
- `workflow_lint.py --toolkit-only` → **0 error(s), 0 warning(s)**
- `check_maps.py --depth3-only --strict` → **Exit 0 (clean index & maps)**
- `sop_currency.py` → **Passed (SOP staged in commit)**

### Findings
Changes applied: none — implementation verified correct as-is.

---

## Your Actions
- [x] Commit and verify lane changes on `chore/SCC-300-sandbox-claude-hooks-skills` (Automated: `e62276a`)
- [ ] Merge `chore/SCC-300-sandbox-claude-hooks-skills` via `/smh-close-task-merge-tree` or operator PR merge.
