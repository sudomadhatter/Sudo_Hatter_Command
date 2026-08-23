---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-300: Eliminate Claude Hook Mirror and Handle Sandbox Write Restrictions"
  type: implementation_plan
  date: 2026-08-23
---

# SCC-300: Eliminate Claude Hook Mirror and Handle Sandbox Write Restrictions

## Goal & Background Context
Claude Code enforces an OS kernel sandbox that strictly forbids write access under `.claude/hooks/` and `.claude/skills/` (even when `sandbox.filesystem.allowWrite` includes the workspace). 

This produced two critical failure modes:
1. **Git Operations (`git merge origin/main`, `checkout`, `pull`) Broken**: Because `.claude/hooks/` was a git-tracked mirror of `.agents/hooks/`, any merge bringing in hook updates from `main` tried to unlink/modify `.claude/hooks/*` files. The OS sandbox denied this with `Operation not permitted`, blocking lane merges and task close-outs (observed on SCC-298).
2. **/smh-sync-agents In-Session Blocked**: `sync-agents.ps1` failed when trying to write `.claude/skills/` from inside a sandboxed session.

### The Architectural Fix
- **Direct Wiring for Hooks**: Wire `.claude/settings.json` directly to `.agents/hooks/*.py` through `run-hook.sh`. `.agents/hooks/` is already the single source of truth and is explicitly writable in the sandbox (`ALLOW <repo>/.agents/hooks/`).
- **Retire `.claude/hooks/`**: Untrack and remove `.claude/hooks/` from git entirely. Git will never touch `.claude/hooks/` during merges.
- **Graceful Sandbox Handling in `sync-agents.ps1`**: Update `sync-agents.ps1` to stop syncing `.claude/hooks/` and catch/warn gracefully on `.claude/skills/` writes when running in sandboxed sessions while fully maintaining `.agents/skills/`, `.agents/workflows/`, `.opencode/commands/`, and machine caches.

---

## Checkable Acceptance List
- [ ] **A1**: `.claude/settings.json` wires all hooks directly to `.agents/hooks/*.py` via `run-hook.sh`.
- [ ] **A2**: `.claude/hooks/` is removed from git tracking and deleted from the repository.
- [ ] **A3**: `sync-agents.ps1` removes `.claude/hooks/` sync and cleanly handles `.claude/skills/` in sandboxed sessions.
- [ ] **A4**: Test suites (`test_cwd_escape_hook.py`, `test_allow_scratchpad.py`, `test_allow_readonly_chain.py`, `test_command_surfaces.py`) assert `.agents/hooks/` wiring and pass cleanly.
- [ ] **A5**: Memory and SOP documentation are updated to reflect single-source hook wiring and sandbox handling.

---

## Declared Change Set
- EDIT .claude/settings.json → A1
- DELETE .claude/hooks/allow-readonly-chain.py → A2
- DELETE .claude/hooks/allow-scratchpad.py → A2
- DELETE .claude/hooks/guard-cwd-escape.py → A2
- DELETE .claude/hooks/log-rule-load.sh → A2
- DELETE .claude/hooks/require-push-approval.py → A2
- DELETE .claude/hooks/rule-trigger.py → A2
- DELETE .claude/hooks/run-hook.sh → A2
- DELETE .claude/hooks/session-start-context.sh → A2
- DELETE .claude/hooks/INDEX.md → A2
- EDIT .agents/scripts/sync-agents.ps1 → A3
- EDIT .agents/scripts/tests/test_cwd_escape_hook.py → A4
- EDIT .agents/scripts/tests/test_allow_scratchpad.py → A4
- EDIT .agents/scripts/tests/test_allow_readonly_chain.py → A4
- EDIT .agents/scripts/tests/test_command_surfaces.py → A4
- EDIT _artifacts/_memory/sandbox-denies-writes-under-dot-claude-hooks-skills.md → A5
- EDIT docs/migrations/install_guides/claude-permission-sandboxed.md → A5
- EDIT docs/_scc_sops_prds/workflows_testing_SOP.md → A5

---

## Proposed Changes

### Configuration
#### [MODIFY] [.claude/settings.json](file:///Users/sudohatter/Sudo_Hatter_Command/.claude/settings.json)
Update hook execution targets:
- `PreToolUse`: `.agents/hooks/allow-scratchpad.py`, `.agents/hooks/require-push-approval.py`, `.agents/hooks/guard-cwd-escape.py`, `.agents/hooks/allow-readonly-chain.py`
- `UserPromptSubmit`: `.agents/hooks/rule-trigger.py`

### Plumbing & Sync
#### [DELETE] `.claude/hooks/*`
Untrack and remove all 9 duplicate hook files in `.claude/hooks/`.

#### [MODIFY] [.agents/scripts/sync-agents.ps1](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/sync-agents.ps1)
- Remove `.claude/hooks` sync target.
- Wrap `.claude/skills` directory sync in a sandbox-aware try/catch block that reports an informative warning if the OS sandbox blocks the write.

### Test Verification
#### [MODIFY] [.agents/scripts/tests/test_cwd_escape_hook.py](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/tests/test_cwd_escape_hook.py)
Assert that `.claude/settings.json` wires `.agents/hooks/guard-cwd-escape.py`.

#### [MODIFY] [.agents/scripts/tests/test_allow_scratchpad.py](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/tests/test_allow_scratchpad.py)
Assert that `.claude/settings.json` wires `.agents/hooks/allow-scratchpad.py`.

#### [MODIFY] [.agents/scripts/tests/test_allow_readonly_chain.py](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/tests/test_allow_readonly_chain.py)
Assert that `.claude/settings.json` wires `.agents/hooks/allow-readonly-chain.py`.

#### [MODIFY] [.agents/scripts/tests/test_command_surfaces.py](file:///Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/tests/test_command_surfaces.py)
Remove `.claude/hooks` from `SWEEP_ROOTS`.

### Memory & SOP
#### [MODIFY] [_artifacts/_memory/sandbox-denies-writes-under-dot-claude-hooks-skills.md](file:///Users/sudohatter/Sudo_Hatter_Command/_artifacts/_memory/sandbox-denies-writes-under-dot-claude-hooks-skills.md)
Document that `.claude/hooks/` is retired in favor of direct `.agents/hooks/` wiring and record sandbox write handling for `.claude/skills/`.

#### [MODIFY] [docs/migrations/install_guides/claude-permission-sandboxed.md](file:///Users/sudohatter/Sudo_Hatter_Command/docs/migrations/install_guides/claude-permission-sandboxed.md)
Update documentation to reflect direct `.agents/hooks/` execution.

#### [MODIFY] [docs/_scc_sops_prds/workflows_testing_SOP.md](file:///Users/sudohatter/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md)
Document the single-source hook architecture and sandbox sync note.

---

## Verification Plan

### Automated Tests
- Case-specific test runs:
  ```bash
  python3 .agents/scripts/tests/test_cwd_escape_hook.py
  python3 .agents/scripts/tests/test_allow_scratchpad.py
  python3 .agents/scripts/tests/test_allow_readonly_chain.py
  python3 .agents/scripts/tests/test_command_surfaces.py
  ```
- Full suite execution:
  ```bash
  python3 .agents/scripts/tests/run_all.py
  ```
- Linter & maps verification:
  ```bash
  python3 .agents/scripts/workflow_lint.py --toolkit-only
  python3 .agents/scripts/check_maps.py --depth3-only --strict
  ```

---

## Self-Audit (2026-08-23)

- **Repo Reality & Scope Ledger**: Clean diff against master `.agents/hooks/`. Elimination of `.claude/hooks/` permanently removes the git merge conflict surface.
- **Parity & Blast**: Hooks run identically through `run-hook.sh` since `run-hook.sh` already resolves `$ROOT/$SCRIPT` relative to `CLAUDE_PROJECT_DIR`.
- **Pre-Mortem**: Does Claude Code support hooks pointing to `.agents/hooks/`? Yes, `settings.json` executes `sh "$CLAUDE_PROJECT_DIR/.agents/hooks/run-hook.sh" .agents/hooks/<name>.py`, which already works for lines 76-88 (`.agents/scripts/*`).

**Audit verdict: GO**
