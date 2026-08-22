---
IsArtifact: true
ArtifactMetadata:
  title: Teaching edition refresh walkthrough
  type: walkthrough
  date: 2026-08-22
  ticket: SCC-280
  lane: claude/teaching-edition
---

# SCC-280 — teaching edition refresh

review-runtime: fan-out

## Outcome

The long-lived teaching branch now builds one sanitized, zero-history command-center shell from the
current command-center implementation. The tutor reads the local
`docs/_scc_sops_prds/workflows_testing_SOP.md` and relevant command body at every teaching stop rather
than carrying a frozen copy of the workflow.

The exported shell begins with an empty `Projects/` directory and no active Jira binding. Its front
door lets the owner choose the command-center folder name. During the tour, the agent asks what to
name the first project and routes through `/smh-new-project <name>` to clone
`https://github.com/sudomadhatter/sudo-project-skeleton` into `Projects/<name>`. Jira remains optional
until that project has a site, project, and board.

The generated export is the shareable artifact. This source branch is the maintained export recipe;
SCC-280 does not create a public repository or change repository visibility.

## Source and integration

- Source `origin/main`: `5069d4df42e79f02bf80061725bdd75b3cc0e573`
- Main integration commit: `abbdb0a637e595858d9c5359dec5098e20ef75ef`
- `origin/main` was re-fetched at final integration and remained on the same SHA.
- SCC-271 is present in that source SHA. SCC-270 remains an explicit landing-order dependency until
  its separate lane reaches `main`; SCC-280 will not claim final acceptance before that refresh.

## What changed

- Added `/smh-tour` and `/smh-training on|off|status` with current generated doors for Claude/Codex,
  opencode, and Antigravity.
- Bound training mode to the live SOP and current command bodies.
- Rebuilt the exporter and manifest as a one-shell distribution with blocking validation.
- Replaced active Jira configuration with an inactive generic example in generated output.
- Added a real-export contract test and mutation controls for retired commands and active Jira state.
- Removed the legacy branch's two-export concept, old tutor doors, personal notes, and session artifacts
  from the final `origin/main...HEAD` product delta.

## RED to GREEN

The first new contract run against the stale exporter failed before product changes: the old exporter
could not enumerate the current hidden-file tree, and the generated shell failed the current teaching
contract. After implementation, a fresh export produced:

```text
Copied files: 2665
Excluded paths: 22
Created empty directories: 4
Identity substitutions: 4872 across 321 files
Replacement transforms: 6
Leak scan: 38 needles, 0 hits
TEACHING EDITION VALID
test_teaching_edition.py: 7/7 passed
```

The same test injects two bad states into otherwise-valid exports. A retired `/sudo-tour` reference
and an active `.agents/jira.conf` binding are both rejected, proving the validator can fail.

## Acceptance evidence

| # | Result | Evidence |
|---|---|---|
| 1 | Pending final SCC-270 absorb | Current `origin/main` is already an ancestor; final diff reconciliation waits for the named sibling dependency. |
| 2 | Pass | Tutor/rule validator, live-SOP assertions, current command inventory, and tour checkpoint inspection. |
| 3 | Pass | Real export asserts the clone destination syntax, project-name prompt, exact skeleton URL/destination, empty `Projects/`, no active Jira binding, and optional Jira path. |
| 4 | Pass | Real export, zero-history assertion, 38-needle leak scan, manifest inventory, and removed second-export path. |
| 5 | Pass | `sync-agents.ps1 -Status` clean; `test_command_surfaces.py` 185/185; retired doors absent. |
| 6 | Pending final full gate | Focused test 7/7, SOP test 61/61, toolkit lint 0 errors/0 warnings, Python compile and JSON parse green. Full receipt and review follow the last content commit. |

## Evidence

| Check | Result |
|---|---|
| `python3 .agents/scripts/tests/test_teaching_edition.py` | 7/7 passed, including both negative controls |
| `python3 .agents/scripts/tests/test_command_surfaces.py` | 185/185 passed |
| `python3 .agents/scripts/tests/test_sops_prds_folder.py` | 61/61 passed |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | 0 errors, 0 warnings; 8 informational BOM notices |
| `pwsh ... sync-agents.ps1 -Status` | Repo-local mirrors and launcher skills match their generated sources |
| `python3 -m py_compile ...` | Validator and teaching-edition test compile |
| manifest JSON parse | Valid |
| `git diff --check origin/main` | Clean |

## Task Checklist

- [x] Merge current `origin/main` without rewriting the teaching branch.
- [x] Replace the stale tutor with a live-SOP curriculum using current command families.
- [x] Teach command-center naming and named first-project creation from the maintained skeleton.
- [x] Export one sanitized shell with no assumed Jira board.
- [x] Regenerate all current platform doors and remove retired tutor doors from the final delta.
- [x] Prove the validator rejects retired-command and active-Jira mutants.
- [ ] Re-absorb `main` after SCC-270 lands, run the final full gate and review, then push the branch.

## Your Actions

- [x] None required for SCC-280 implementation. The separate skeleton modernization will be planned
  after this refresh is complete; it is not hidden inside this lane.

## Follow-on boundary

After SCC-280 is complete, plan a separate upgrade of `sudo-project-skeleton` using only reusable
project infrastructure learned from AviationChat, specifically Playwright and newer shared
development/testing machinery. That follow-on gets its own repository binding, Jira key, plan,
worktree, compatibility audit, tests, and approval.
