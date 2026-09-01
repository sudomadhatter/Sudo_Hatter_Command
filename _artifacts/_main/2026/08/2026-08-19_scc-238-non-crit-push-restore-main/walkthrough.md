# Walkthrough — SCC-238: Add checkout restoration and post-merge pull steps to non-crit-pr-push twins

## What changed
- `.agents/commands/smh-non-crit-pr-push.md`: Added Step 9 (`git checkout main`) to restore the working checkout to `main` after reporting the PR, and Step 10 (`git pull origin main`) to pull landed changes after the operator merges the PR.
- `.agents/commands/cicd-non-crit-pr-push.md`: Added Step 9 (`git -C "$REPO" checkout main`) and Step 10 (`git -C "$REPO" pull origin main`) to keep the child project's checkout clean on `main`.
- `docs/_scc_sops_prds/workflows_testing_SOP.md`: Updated Sections 8a and 9a to document checkout restoration and post-merge pull.
- Ran `sync-agents.ps1` to mirror changes across `.agents/workflows/`, `.opencode/commands/`, etc.

## Evidence
- `workflow_lint.py --toolkit-only`: 0 error(s), 0 warning(s), 8 info (PASS)
- `test_twin_parity.py`: 51/51 passed (PASS)
- `test_sops_prds_folder.py`: 61/61 passed (PASS)
- `check_maps.py --depth3-only --strict`: 0 drift (PASS)
- `run_all.py`: 34/34 files passed (PASS)
- Commit SHA: `e515d7c`

## Your Actions
- [x] The merge itself — lands via this branch's PR
