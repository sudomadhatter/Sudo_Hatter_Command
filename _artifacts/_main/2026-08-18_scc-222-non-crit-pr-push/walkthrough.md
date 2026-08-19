# Walkthrough — SCC-222: Create /smh-non-crit-pr-push command

## What changed
- `.agents/commands/smh-non-crit-pr-push.md`: Added new slash command for fast-tracking non-critical command center changes under standing ticket `SCC-186` and standing branch `chore/SCC-186-standing-push` directly to PR.
- `.agents/commands/INDEX.md`: Registered `/smh-non-crit-pr-push` in the command catalog table.
- `docs/_scc_sops_prds/workflows_testing_SOP.md`: Documented `/smh-non-crit-pr-push` in quick-reference table, Section 9a, and command index.
- Ran `sync-agents.ps1` to mirror command to `.agents/workflows/`, `.agents/skills/`, `.claude/skills/`, and `.opencode/commands/`.

## Evidence
- `workflow_lint.py --toolkit-only`: 0 error(s), 0 warning(s), 8 info (PASS)
- `test_sops_prds_folder.py`: 61/61 passed (PASS)
- `sync-agents.ps1`: generated launcher skill and mirrored across all platform surfaces cleanly.

## Your Actions
- [x] The merge itself — lands via this branch's PR
