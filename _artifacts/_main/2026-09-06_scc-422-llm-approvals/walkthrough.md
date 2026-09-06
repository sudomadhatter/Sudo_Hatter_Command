# Walkthrough — SCC-422 LLM Approval Stops Harvest

## 1. Overview
Harvested approved commands that stopped agents during recent workflows across Claude Code and Antigravity into canonical source `.agents/permissions/families.json` via `/smh-llm-approvals`.

Operator approval received verbatim: **"all of them"**.

## 2. Rows Landed in Shared Source (`families.json`)
Rendered to `.claude/settings.json`:
- **`allow-firebase-hosting-disable`**: Added `firebase hosting:disable` for Claude teardowns and tests.
- **`allow-unlink`**: Added `unlink` for worktree asset cleanup (`unlink backend/.venv`).
- **`allow-gh-pr`**: Widened Claude render with `Bash(gh pr edit:*)` and `Bash(env -u GITHUB_TOKEN gh pr edit:*)` for updating PR metadata.
- **`allow-gh-run`**: Widened Claude render with `Bash(gh run watch:*)` and `Bash(env -u GITHUB_TOKEN gh run watch:*)` for CI monitoring.
- **`allow-git-push`**: Widened Claude render with quiet variants `Bash(env -u GITHUB_TOKEN git push -q origin chore/*)`, `-q -u`, and `-q --set-upstream`.
- **`allow-git-worktree`**: Widened Claude render with `Bash(git worktree prune*)`.
- **`allow-java`**: Widened platform reach to include Claude (`Bash(java -version:*)`).

## 3. Picks Refused by Fence / Safety Laws
The following broad rules were present in local `~/.claude/settings.json` and could not be promoted to tracked shared source:
- **`Bash(acli:*)`**: Refused by fence deny row `command(acli jira workitem delete)`. (Individual subcommands like `view`, `create`, `search`, `comment`, `edit`, `transition` are already granted).
- **`Bash(chmod:*)`**: Refused by fence deny row `command(chmod -[a-zA-Z]*R[a-zA-Z]* 777)`.
- **`Bash(gh:*)` & `Bash(env -u GITHUB_TOKEN gh:*)`**: Refused by fence deny rows `command(gh pr merge)`, `command(gh repo delete)`, `command(gh release delete)`.
- **`Bash(npx:*)`**: Refused by battery test A5 (`npx create-next-app` must prompt for package downloads).
- **`Bash(python:*)`**: Refused by ONE-INTERPRETER law (`test_settings_allowlist.py` A3 — system standard is `python3`).

## 4. Verification Evidence
- **Permission Parity Render**:
  ```bash
  python3 .agents/scripts/permission_render.py --check
  # Output: permission_render: in sync (zoo, claude, antigravity)
  ```
- **Test Suite**:
  ```bash
  python3 .agents/scripts/tests/run_all.py
  # Output: 80/80 files passed (exit code 0)
  ```
- **Stops Reduction**:
  `approval_stops.py` uncovered command count dropped from **7** to **3**.

## Code Review (2026-09-06)

Verdict: PASS @ e2ce6fa2

## Your Actions
1. Apply the harvested Claude rows into machine-level user scope (`~/.claude/settings.json`):
   ```bash
   python3 .agents/scripts/claude_permissions_apply.py --apply
   ```
2. Merge the resulting pull request on GitHub once opened.
