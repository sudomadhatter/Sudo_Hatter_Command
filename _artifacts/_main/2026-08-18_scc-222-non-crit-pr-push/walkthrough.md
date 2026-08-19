# Walkthrough — SCC-222: Create /smh-non-crit-pr-push & /cicd-non-crit-pr-push Twin Commands

## What changed
- `.agents/commands/smh-non-crit-pr-push.md`: Added and updated slash command for fast-tracking non-critical command center changes under standing ticket `SCC-186` (or auto-provisioned standing ticket) and standing branch `chore/<KEY>-standing-push` directly to PR.
- `.agents/commands/cicd-non-crit-pr-push.md`: Added project-bound twin command for fast-tracking non-critical child project changes (`Projects/<name>` such as `Projects/AGY_AVIATIONCHAT`). Automatically checks for / provisions the project's open "Standing Push Ticket" (e.g. in `AVCH`) and persistent `chore/<KEY>-standing-push` branch.
- `.agents/commands/INDEX.md`: Registered both `/cicd-non-crit-pr-push` and `/smh-non-crit-pr-push` in their respective command catalogs.
- `.agents/scripts/tests/test_twin_parity.py`: Pinned `("cicd-non-crit-pr-push.md", "smh-non-crit-pr-push.md")` in `PAIRS`.
- `docs/_scc_sops_prds/workflows_testing_SOP.md`: Documented `/cicd-non-crit-pr-push` in Section 8a & quick table, and updated Section 9a for `/smh-non-crit-pr-push` with dynamic ticket provisioning.
- Ran `sync-agents.ps1` to mirror commands to `.agents/workflows/`, `.agents/skills/`, `.claude/skills/`, and `.opencode/commands/`.

## Evidence
- `workflow_lint.py --toolkit-only`: 0 error(s), 0 warning(s), 8 info (PASS)
- `test_twin_parity.py`: 51/51 passed (PASS)
- `test_sops_prds_folder.py`: 61/61 passed (PASS)
- `test_check_maps.py`: 27/27 passed (PASS)
- `sync-agents.ps1`: mirrored across all four platform doors cleanly.

## Your Actions
- [x] The merge itself — lands via this branch's PR
