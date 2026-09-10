# Walkthrough — SCC-437 LLM Approval Stops Harvest

## 1. Overview
Harvested approved commands that stopped agents during recent workflows across Claude Code, Zoo Code, and Antigravity into canonical source `.agents/permissions/families.json` via `/smh-llm-approvals`.

Operator approval received verbatim: **"all"**.

## 2. Rows Landed in Shared Source (`families.json`)
Rendered via `permission_render.py` across `.claude/settings.json`, `.vscode/settings.json`, and `.agents/permissions/antigravity.json`:

- **`allow-git-push`**: Added `Bash(env -u GITHUB_TOKEN git push origin claude/*)` and its `-u`, `--set-upstream`, and `-q` twins to Claude's render to eliminate the 15m08s stop on Claude pushing to story branches.
- **`allow-pytest`**: Widened to Antigravity (`["claude", "antigravity"]`) to allow `command(pytest)` / `unsandboxed(pytest)`.
- **`allow-npx-next`**: Widened to Antigravity (`["claude", "antigravity"]`) to allow Next.js build runs.
- **`allow-npx-tsc`**: Widened to Antigravity (`["claude", "antigravity"]`) to allow TypeScript checks.
- **`allow-npx-eslint`**: Added new family for linter runs on Claude and Antigravity.
- **`allow-firebase-projects-list`**: Added new family for read-only project listings on Claude and Antigravity.
- **`allow-gcloud-version`**: Added new family for version probes on Claude and Antigravity.
- **`allow-gsutil-ls`**: Added new family for read-only GCS bucket listings on Claude and Antigravity.
- **`allow-pwsh`**: Added `command(pwsh \.agents/scripts/.*)` and `unsandboxed(pwsh \.agents/scripts/.*)` to Antigravity render for direct script executions without requiring `-NoProfile -File`.

## 3. Picks Refused by Fence / Safety Laws
The following broad rules were present in local `~/.claude/settings.json` or stopped calls and could not be promoted to tracked shared source:
- **`Bash(acli:*)`**: Refused by fence deny row `command(acli jira workitem delete)`. (Narrow subcommands like `view`, `create`, `search`, `comment`, `edit`, `transition` are already granted).
- **`Bash(chmod:*)`**: Refused by fence deny row `command(chmod -[a-zA-Z]*R[a-zA-Z]* 777)`.
- **`Bash(gh:*)` & `Bash(env -u GITHUB_TOKEN gh:*)`**: Refused by fence deny rows `command(gh pr merge)`, `command(gh repo delete)`, `command(gh release delete)`.
- **`Bash(npx:*)`**: Refused by battery test A5 (`npx create-next-app` must prompt for package downloads).
- **`Bash(python:*)`**: Refused by ONE-INTERPRETER law (`test_settings_allowlist.py` A3 — system standard is `python3`).
- **`rm -f` / `rm node_modules` / `git reset` / `git branch` (bare)**: Destructive commands forbidden from auto-allow by git policy and constitution.
- **`firebase deploy`**: Refused by constitution Ask First gate (`Before modifying CI/CD, deployment, or environment configs`).

## 4. Verification Evidence
- **Permission Parity Render**:
  ```bash
  python3 .agents/scripts/permission_render.py --check
  # Output: permission_render: in sync (zoo, claude, antigravity)
  ```
- **Test Suite**:
  ```bash
  python3 .agents/scripts/tests/run_all.py --on-main
  # Output: 83/83 files passed (exit code 0)
  ```
- **Stops Reduction**:
  `approval_stops.py` uncovered command count dropped from **14** to **12** (wall-clock wait reduced from 1h40m to 1h25m). The top stop (`2 x 15m08s env -u`) was completely eliminated. All remaining stops are destructive or invalid command shapes.

## Code Review (2026-09-09)

Verdict: PASS @ 1c541916

## Your Actions
1. Apply the harvested Claude rows into machine-level user scope (`~/.claude/settings.json`):
   ```bash
   python3 .agents/scripts/claude_permissions_apply.py --apply
   ```
2. Reload VS Code window to apply the Antigravity store updates.
3. Merge the pull request once opened.
