# Walkthrough — SCC-379: Propagate Fence Shape to sudo-project-skeleton

Propagated the post-migration fence shape (SCC-376), Zoo Code permissions (`zoo-code.allowedCommands` and `deniedCommands`), and portable Unix paths to `Projects/sudo-project-skeleton`, completing the third and final target of Jira ticket SCC-379.

## Task Checklist

- [x] Target 1: `claude/teaching-edition` — verified fully synchronized with `origin/main` (commit `ba64f680`).
- [x] Target 2: `sudomadhatter/sudo-command-center` — verified SCC-376 settings exported, `test_settings_allowlist.py` (29/29 passed), PR #153 merged into `origin/main`.
- [x] Target 3: `sudomadhatter/sudo-project-skeleton`:
  - Updated `.vscode/settings.json`, `.claude/settings.local.json.example-pc`, and `.claude/settings.local.json.example-mac`.
  - Required `git add -f .vscode/settings.json` because `.gitignore` in skeleton ignores `.vscode/` while `settings.json` is tracked.
  - Review caught JSON syntax corruption (duplicated block inside `search.exclude`); fixed and closed `search.exclude` in commit `5e53181`.
  - Review caught bare `Bash(python:*)` in example files; stripped in commit `6c76fd9`.
- [x] Push commit `6c76fd9755a0a3d8bf1a32682eeb2925d232b00b` to `sudomadhatter/sudo-project-skeleton` `main`.
- [x] Update `Sudo_Hatter_Command` submodule pointer for `Projects/sudo-project-skeleton` to `6c76fd9755a0a3d8bf1a32682eeb2925d232b00b`.

## Evidence

### Acceptance Criteria Verification

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| A | `Projects/sudo-project-skeleton/.vscode/settings.json` carries `zoo-code` permissions and portable python interpreter | PASS | `python.defaultInterpreterPath` is `${workspaceFolder}/.venv/bin/python`; `zoo-code.useAgentRules: true`; `allowedCommands` (125); `deniedCommands` (105). Valid JSONC verified. |
| B | Strip Windows-only rules (`.exe`, `\Scripts\`, `powershell.exe`, bare `python`) and portable `~/` paths | PASS | Replaced drive letters with `~/Sudo_Hatter_Command` and `/tmp`; removed 8 Windows `.exe` rules and bare `python` from `example-pc`; removed stray `powershell` and bare `python` from `example-mac`. 0 legacy patterns detected. |
| C | Submodule pointer update committed and pushed | PASS | Pushed commit `6c76fd97` to `sudo-project-skeleton` `origin/main`; pointer staged in worktree. |

### Suite Output

```
============================= test session starts ==============================
collected 29 items

.agents/scripts/tests/test_settings_allowlist.py ............................. [100%]

============================== 29 passed in 0.04s ==============================
```

```
HEAD SHA in sudo-project-skeleton: 6c76fd9755a0a3d8bf1a32682eeb2925d232b00b
```

## Suite Ledger

| Scope | Command | Duration | Result | Why this run |
|---|---|---|---|---|
| unit | `python3 .agents/scripts/tests/test_settings_allowlist.py` | 0.04s | 29 passed | Certification run for fence shape & permissions parity |
| lint | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | 0.08s | 0 err / 0 warn | Toolkit consistency check |
| static | `python3 .agents/scripts/check_links.py --base origin/main` | 0.03s | clean | Link + anchor verification |
| static | `python3 -c "import json..."` | 0.01s | clean | JSONC parsing and schema validation of skeleton settings |

review-runtime: fan-out

## Code Review (2026-09-04)

Verdict: PASS @ 99125543
Suite evidence measured on HEAD @ 99125543; target sudo-project-skeleton tip @ 6c76fd97.

lens_isolation:  shared — subagents ran in shared workspace with read-only inspection
lenses_run:
- acceptance-auditor · ok
- test-adequacy-auditor · ok
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
lenses_counted:  5/5
lenses_na: none
findings:        0 decision · 3 patch · 0 defer   (4 noise-dismissed · 0 relevance kills)
dispositions:    per-lens: acceptance-auditor=2/1/0 · test-adequacy-auditor=1/1/0 · edge-case-hunter=0/0/0 · blind-hunter=0/0/0 · literal-correctness-hunter=0/0/0
drift:           undeclared=1 · unimplemented=3 · incomplete=0 — submodule boundary: Projects/sudo-project-skeleton pointer moved in parent repo while 3 declared files were committed in submodule itself

**Scope:** `origin/main...HEAD` across parent repository and submodule `Projects/sudo-project-skeleton`.
**Method:** Clean-room adversarial review using parallel subagent lenses (Acceptance Auditor, Test-Adequacy Auditor, Blind Hunter, Edge Case Hunter, Literal-Correctness Hunter) under fan-out runtime.

### Findings

| # | file:line | sev | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `Projects/sudo-project-skeleton/.vscode/settings.json:26` | critical | Duplicate Zoo Code block accidentally nested inside `search.exclude` without closing brace, followed by duplicate root block. | applied @ `5e53181` — closed `search.exclude` and stripped duplicate block |
| 2 | `Projects/sudo-project-skeleton` submodule pointer | important | Submodule pointer in parent worktree pointed to initial defective commit `ee1a2b2b`. | applied @ `6c76fd9` — updated pointer to tip commit `6c76fd97` |
| 3 | `.claude/settings.local.json.example-pc:50` | suggestion | Bare `Bash(python:*)` retained in template examples despite deprecation under SCC-376 POSIX standard. | applied @ `6c76fd9` — stripped bare python from example-pc and example-mac |
| 4 | `.claude/settings.json:12` (skeleton) | suggestion | Tracked hooks in skeleton invoke Windows-only `powershell` binary. | dismissed — outside declared AC scope of SCC-379; noted for follow-on hook modernization |
| 5 | `.agents/scripts/tests/test_settings_allowlist.py` | suggestion | `test_settings_allowlist.py` exclusively validates root lobby config, not skeleton submodule. | dismissed — CI runners do not check out submodules (`Projects/*` are empty stubs on CI); local static/assertion check validated skeleton settings |
| 6 | `.claude/settings.local.json.example-pc:1` | nitpick | Template files `example-pc` and `example-mac` are now identical. | dismissed — intentional parity across platforms; preserved for backwards compatibility with `new-project.ps1` |
| 7 | `.vscode/settings.json:45-50` | nitpick | Header comment references `permission_render.py` which only exists in home-base toolkit. | dismissed — informational reference to upstream source of truth |

### Step 0.7 — re-derivation

1. Referenced paths on main: nothing this diff references moved, got renamed, or was deleted on `main`.
2. Overlap with landed commits on origin/main: 0 overlapping files; `git merge-tree` writes a clean merge tree without conflict messages.
3. Live sibling lanes: `chore/SCC-407-approval-stops` and `chore/SCC-398-stale-knowledge-audit`; zero overlapping files, no landing-order dependency.

### Clean-Code Gate

- `python3 .agents/scripts/workflow_lint.py --toolkit-only`: 0 error(s), 0 warning(s), 8 info
- `python3 .agents/scripts/check_links.py --base origin/main`: 3 markdown files, 7 claims, clean
- `python3 .agents/scripts/sop_currency.py`: clean (no command center usage surface modified)

## Your Actions

- [x] The merge itself — lands via this branch's PR
