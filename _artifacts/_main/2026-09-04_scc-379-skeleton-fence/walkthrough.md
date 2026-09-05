# Walkthrough — SCC-379: Propagate Fence Shape to sudo-project-skeleton

Propagated the post-migration fence shape (SCC-376), Zoo Code permissions (`zoo-code.allowedCommands` and `deniedCommands`), and portable Unix paths to `Projects/sudo-project-skeleton`, completing the third and final target of Jira ticket SCC-379.

## Task Checklist

- [x] Target 1: `claude/teaching-edition` — verified fully synchronized with `origin/main` (commit `ba64f680`).
- [x] Target 2: `sudomadhatter/sudo-command-center` — verified SCC-376 settings exported, `test_settings_allowlist.py` (29/29 passed), PR #153 merged into `origin/main`.
- [x] Target 3: `sudomadhatter/sudo-project-skeleton` — updated `.vscode/settings.json`, `.claude/settings.local.json.example-pc`, and `.claude/settings.local.json.example-mac`.
  - Had to use `git add -f .vscode/settings.json` because `.gitignore` in skeleton ignores `.vscode/` while `settings.json` is tracked.
- [x] Push commit `ee1a2b2be1e60bfc100baf6358d871649d013f74` to `sudomadhatter/sudo-project-skeleton` `main`.
- [x] Update `Sudo_Hatter_Command` submodule pointer for `Projects/sudo-project-skeleton` to `ee1a2b2be1e60bfc100baf6358d871649d013f74`.

## Evidence

### Acceptance Criteria Verification

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| A | `Projects/sudo-project-skeleton/.vscode/settings.json` carries `zoo-code` permissions and portable python interpreter | PASS | `python.defaultInterpreterPath` is `${workspaceFolder}/.venv/bin/python`; `zoo-code.useAgentRules: true`; `allowedCommands` (125); `deniedCommands` (105). |
| B | Strip Windows-only rules (`.exe`, `\Scripts\`, `powershell.exe`) and portable `~/` paths | PASS | Replaced drive letters with `~/Sudo_Hatter_Command` and `/tmp`; removed 8 Windows `.exe` rules from `example-pc`; removed stray `powershell` from `example-mac`. 0 legacy patterns detected. |
| C | Submodule pointer update committed and pushed | PASS | Pushed commit `ee1a2b2b` to `sudo-project-skeleton` `origin/main`; pointer staged in worktree. |

### Suite Output

```
============================= test session starts ==============================
collected 29 items

.agents/scripts/tests/test_settings_allowlist.py ............................. [100%]

============================== 29 passed in 0.04s ==============================
```

```
HEAD SHA in sudo-project-skeleton: ee1a2b2be1e60bfc100baf6358d871649d013f74
```

## Suite Ledger

| Scope | Command | Duration | Result | Why this run |
|---|---|---|---|---|
| unit | `python3 .agents/scripts/tests/test_settings_allowlist.py` | 0.04s | 29 passed | Certification run for fence shape & permissions parity |
| static | `python3 -c "import json..."` | 0.01s | clean | Verify 0 legacy `.exe` / `\Scripts\` patterns in skeleton settings |

## Your Actions

- [x] The merge itself — lands via this branch's PR

