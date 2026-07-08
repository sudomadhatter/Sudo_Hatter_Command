# active-context — opencode home-base main

## 1. PRIME
This is the continuity brief for opencode sessions working on home-base / cross-project infrastructure in `Sudo_Hatter_Command`. It lives at `_artifacts/opencode/_main/active-context.md`.

## 5. PICK UP
Last opencode home-base session: 2026-07-07 `/1_update-maps` fan-out (see §6 below + `_artifacts/opencode/_main/2026-07-07_update-maps-fanout/walkthrough.md`). Lobby + Fresh fully lint-clean; AGY has 2 deferred code-fix flags (`coverage` + `.ruff_cache` — both 1-line additions to master scripts, awaiting Daniel's go-ahead). Daniel needs to commit the 3 repos (commands in the walkthrough) + re-anchor (`check_maps.py --set-anchor --all`). Read `_my_resources/open_tasks/todo_list.md` for Daniel's queue.

## 6. HAND OFF

**2026-07-07 — /1_update-maps fan-out (lobby + AGY + Fresh)**
- Executed `/1_update-maps --all` from the home base. Scope expanded mid-run when Daniel clarified the command now includes **level-2 INDEX.md upkeep** (new scope) — I had initially (incorrectly) dismissed the level-2 flags as out of scope.
- **Edits applied (docs/markdown only — no code):**
  - Regenerated all 3 `docs/repo-map.md` AUTO blocks (lobby mode=content; AGY mode=content; Fresh mode=auto), mode-preserving, each workspace's documented `--ignore`.
  - Refreshed AGY `_my_resources/open_tasks/todo_list.md` `## Open Work` manifest: `fix_list.md`→`fix_list_admin_sudoadmin.md`, +`tdad_stack_install_guide.md`. Prose + task files untouched.
  - Created **76 level-2 `INDEX.md` files** across 3 workspaces (12 lobby + 40 AGY + 21 Fresh + 3 in AGY gitignored folders = disk-only). Delegated AGY + Fresh to 2 parallel general subagents; did lobby myself.
  - Fixed depth-3 `_artifacts/opencode/_main/INDEX.md`: added this session's row + backticked the folder-name token in the prior row (linter matching requires backticks).
- **Final lint (`check_maps.py --all`):** Lobby ✅ clean · Fresh ✅ clean · AGY 🚩 2 deferred code-fix flags + 1 hint · RAG_Pipeline_AC 🚩 NOT conformant (out of scope).
- **2 deferred code fixes (awaiting Daniel's go-ahead — outside "docs only" scope):**
  1. Add `"coverage"` to `DEFAULT_IGNORES` in lobby master `.agents/scripts/generate_repo_map.py` (vendoring drift — AGY/Fresh vendored copies already have it; the `--all` linter uses the lobby master generator → false-positive STALE on AGY `frontend/coverage/`).
  2. Add `".ruff_cache"` to `SCAN_IGNORES` in lobby master `.agents/scripts/check_maps.py` (versioned build cache; creating an INDEX there is futile).
  Both are 1-line additions + `/sync-agents`. Exact diffs in the walkthrough.
- **Hint:** AGY `_bmad-output/active-context/active-context.md` is 243 lines with no dated blocks — can't auto-prune; flagged for Daniel's review.
- **NOT committed** — git commands handed to Daniel in the walkthrough (surgical `git add` per repo; never `git add -A` because each repo has pre-existing untracked/modified files that aren't mine). Re-anchor with `check_maps.py --set-anchor --all` AFTER committing.
- Latest artifact: `_artifacts/opencode/_main/2026-07-07_update-maps-fanout/walkthrough.md`.

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
- Project-code changes committed as `ec791b2`; Daniel will push `main_debug` and optionally commit the remaining opencode artifacts (`_artifacts/opencode/_main/`).
- Latest artifact: `_artifacts/opencode/_main/2026-06-28_command-workflow-audit-fixes/walkthrough.md`.
