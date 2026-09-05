# Implementation Plan — SCC-379: Propagate Fence Shape to sudo-project-skeleton

Propagate the post-migration fence shape (SCC-376), Zoo Code permissions (`zoo-code.allowedCommands` and `deniedCommands`), and portable Unix paths to `Projects/sudo-project-skeleton`, completing the third and final target of Jira ticket SCC-379.

## User Review Required

> [!IMPORTANT]
> `sudo-project-skeleton` is the template cloned whenever `/smh-new-project` runs. Updating it ensures every newly cloned project starts with:
> 1. Portable `~/` filesystem allow paths rather than hardcoded Windows `c:/` drive paths.
> 2. Clean Linux/macOS binary permissions (stripping `.exe`, `\Scripts\`, and `powershell.exe`).
> 3. Pre-configured Zoo Code allow/deny command fences in `.vscode/settings.json`.

## Acceptance Criteria

- **A**: `Projects/sudo-project-skeleton/.vscode/settings.json` carries `zoo-code.useAgentRules`, `zoo-code.allowedCommands`, and `zoo-code.deniedCommands`, and `python.defaultInterpreterPath` uses `${workspaceFolder}/.venv/bin/python`.
- **B**: No Windows-only spelling (`.exe`, `\Scripts\`, `powershell.exe`) and no `git -C *` rule remains in `Projects/sudo-project-skeleton/.claude/settings.local.json.example-pc` or `settings.local.json.example-mac`.
- **C**: Submodule pointer update committed and pushed in `sudo-project-skeleton`.

## Declared Change Set

- EDIT `Projects/sudo-project-skeleton/.vscode/settings.json` — python interpreter path and zoo-code fence → A
- EDIT `Projects/sudo-project-skeleton/.claude/settings.local.json.example-pc` — WSL/Ubuntu paths and strip Windows-only binary rules → B
- EDIT `Projects/sudo-project-skeleton/.claude/settings.local.json.example-mac` — portable paths and strip powershell → B

## Proposed Changes

### Projects/sudo-project-skeleton

#### [MODIFY] .vscode/settings.json
- Replace `python.defaultInterpreterPath`: `${workspaceFolder}\\.venv\\Scripts\\python.exe` with `${workspaceFolder}/.venv/bin/python`.
- Add `"zoo-code.useAgentRules": true`.
- Add `"zoo-code.allowedCommands"` and `"zoo-code.deniedCommands"` arrays seeded from the standard command center configuration.

#### [MODIFY] .claude/settings.local.json.example-pc
- Replace Windows drive paths (`c:/Sudo_Hatter_Command`, etc.) with `~/Sudo_Hatter_Command` and `/tmp`.
- Strip 8 Windows-only rules: `Bash(python.exe:*)`, `Bash(.venv/Scripts/python:*)`, `Bash(.venv/Scripts/python.exe:*)`, `Bash(cargo.exe:*)`, `Bash(rustc.exe:*)`, `Bash(pytest.exe:*)`, `Bash(powershell:*)`, `Bash(powershell.exe:*)`.
- Add `Bash(.venv/bin/python:*)`.

#### [MODIFY] .claude/settings.local.json.example-mac
- Replace `/Users/{{USER}}/Sudo_Hatter_Command` with `~/Sudo_Hatter_Command`.
- Remove stray `Bash(powershell:*)`.

## Verification Plan

### Automated Tests
- Validate JSON syntax of modified JSON files in `Projects/sudo-project-skeleton`.
- Verify absence of `.exe` and `\Scripts\` in skeleton settings.
- Run `python3 .agents/scripts/tests/test_settings_allowlist.py`.


## Self-Audit (2026-09-04)

### Lens 1: Repo Reality + Scope Ledger
- `lens`: 1 Repo Reality + Scope Ledger
- `checks_run`:
  - Verified all declared paths exist in `Projects/sudo-project-skeleton`.
  - Verified `declared_change_set.py parse` parsed all 3 entries with 0 incomplete.
  - Confirmed no deployable product paths in `Sudo_Hatter_Command` are touched.
- `read`: `Projects/sudo-project-skeleton/.vscode/settings.json`, `Projects/sudo-project-skeleton/.claude/settings.local.json.example-pc`, `Projects/sudo-project-skeleton/.claude/settings.local.json.example-mac`.
- `verdict`: clean

### Lens 2: Parity + Blast
- `lens`: 2 Parity + Blast
- `checks_run`:
  - Inspected sibling worktrees (`chore/SCC-406-deny-fence-trim`, `chore/SCC-398-stale-knowledge-audit`). Zero colliding file edits.
  - Evaluated blast radius: changes update template configurations in `sudo-project-skeleton`, ensuring future clones get working Zoo Code and Claude permissions without native Windows baggage.
- `read`: sibling worktree diffs, `git status`.
- `verdict`: clean

### Lens 3: Pre-Mortem
- `lens`: 3 Pre-Mortem
- `checks_run`:
  - Verified that `${workspaceFolder}/.venv/bin/python` is portable across Mac and Linux/WSL.
  - Verified that Zoo Code arrays include necessary allow and deny sentinels.
  - Verified that `~` path expansions in `settings.local.json.example-pc` work across Mac and Ubuntu/WSL.
- `read`: `docs/migrations/terminal-permissions-guide.md`.
- `verdict`: clean

Audit verdict: GO
