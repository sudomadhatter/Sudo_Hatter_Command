# active-context — opencode home-base main

## 1. PRIME
This is the continuity brief for opencode sessions working on home-base / cross-project infrastructure in `Sudo_Hatter_Command`. It lives at `_artifacts/opencode/_main/active-context.md`.

## 5. PICK UP
No prior opencode home-base session. Read `_artifacts/opencode/main/INDEX.md` for session history and `_my_resources/open_tasks/todo_list.md` for Daniel's queue.

## 6. HAND OFF

**2026-06-28 — command/workflow audit follow-up**
- Completed:
  - `router.md` paths corrected to actual `Projects/` folder names.
  - `.gitignore` cleaned of stale root-level project entries.
  - `commands/INDEX.md` hidden from command palette via `platforms: []`.
  - `sync-agents.ps1` gained `-WhatIf`/`-DryRun` preview mode.
  - Command docs updated for `-WhatIf` and corrected command count.
  - `AGENTS.md` and `.agents/rules/artifacts-always-first.md` now explicitly direct opencode artifacts to `_artifacts/opencode/_main/` (or `opencode/<project>/`), not `_artifacts/_main/`.
- Live smoke tests passed: `sync-agents -WhatIf`, globals-only `-WhatIf`, `bmad-help` skill reachable, `check_maps.py --all` fan-out.
- `.opencode/node_modules/` deleted per Daniel approval; `.opencode/package.json` + `package-lock.json` preserved.
- Project-code changes committed as `ec791b2`; Daniel will push `main_debug` and optionally commit the remaining opencode artifacts (`_artifacts/opencode/main/`).
- Latest artifact: `_artifacts/opencode/main/2026-06-28_command-workflow-audit-fixes/walkthrough.md`.
