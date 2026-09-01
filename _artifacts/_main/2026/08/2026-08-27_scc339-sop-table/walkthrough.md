# SCC-339 — the Start-here table renders again

Lane: `/smh-quick-fix` (LIGHT, confirmed twice: intent and real diff).
Cause: commit `3df64cf` (SCC-316) pasted the epic-branch-naming paragraph — blank lines and
all — inside the first cell of the Start-here table in the operator SOP. Blank lines terminate
a markdown table, so every row below rendered as one illegible run-on line.

## What changed

- `docs/_scc_sops_prds/workflows_testing_SOP.md` — the "know what to work on" row is a single-line
  cell again; the epic-branch paragraph moved intact to §6 "Before the loop", beside the
  `/cicd-create-epic-sprint` kickoff that cuts the branch it describes. No words were lost.
- `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line: date · SCC-339 · what
  changed for the operator.

## Evidence

- `run_all.py` — `61/61 files passed`
- `workflow_lint.py --toolkit-only` — `0 error(s), 0 warning(s), 8 info`
- `test_sops_prds_folder.py` — `61/61 passed`
- `lane_qualify.py` on the real diff — `LIGHT`
- HEAD: `5e2e0d00d99b17959365677e49a483bc651ed907`, pushed to
  `origin/chore/SCC-339-fix-sop-start-here-table`

## Your Actions

- [x] The merge itself — lands via this branch's PR

Nothing else — no operator decision is owed.
