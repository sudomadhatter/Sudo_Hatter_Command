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
Copied files: 2666
Excluded files: 49
Created empty directories: 4
Identity substitutions: 4886 across 322 files
Replacement transforms: 6
Leak scan: 39 needles, 0 hits
TEACHING EDITION VALID
test_teaching_edition.py: 12/12 passed
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
| 6 | Pending final full gate | Focused test 12/12, SOP test 61/61, toolkit lint 0 errors/0 warnings, Python compile and JSON parse green. Full receipt and review follow the last content commit. |

## Evidence

| Check | Result |
|---|---|
| `python3 .agents/scripts/tests/test_teaching_edition.py` | 12/12 passed, including retired-command, active-Jira, Git-prefix, and wildcard-secret negative controls |
| `python3 .agents/scripts/tests/test_command_surfaces.py` | 185/185 passed |
| `python3 .agents/scripts/tests/test_sops_prds_folder.py` | 61/61 passed |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | 0 errors, 0 warnings; 8 informational BOM notices |
| `pwsh ... sync-agents.ps1 -Status` | Repo-local mirrors and launcher skills match their generated sources |
| `python3 -m py_compile ...` | Validator and teaching-edition test compile |
| manifest JSON parse | Valid |
| `git diff --check origin/main` | Clean |

The first receipt-backed full run passed 48/50 files and found two completion omissions rather than
being reported green: the missing `_artifacts/_main/INDEX.md` row and missing twin-parity declarations
for the two teaching-only `smh-*` commands. Both were corrected in this lane. Its other map-test
failure was the restricted sandbox refusing the test's temporary Git worktree; the test and full
suite are rerun with Git metadata access after the corrections.

## Review fixes before the final verdict

The first clean-room fan-out found nine unique failures. All passed the relevance gate because each
reproduced a wrong export, a dead advertised command, or false privacy evidence; all were fixed in this
lane:

| Surface | Reproduced failure | Applied disposition |
|---|---|---|
| exporter `.git` skip | `.githooks`/`.gitignore` were skipped by a raw prefix | directory-boundary matcher plus mutation-killed self-test |
| exporter literal scan | bracket-bearing secrets were interpreted as wildcard patterns | ordinal literal matcher plus mutation-killed self-test |
| `/smh-training on` | its restore template was excluded from the product | self-contained sentinel creation |
| archive root | `git rev-parse` failed before any training action | live-SOP upward fallback; Git checkout behavior retained |
| retired-command validator | quotes and Markdown brackets bypassed the regex | URL-safe negative-lookbehind matcher plus real export mutant |
| Jira onboarding | relative destination could bind the lobby | both paths explicitly use `Projects/<name>/.agents/` |
| MCP configs | source-machine absolute workspace survived | exact-root substitution to `--workspace=.` plus export assertion |
| README verification | source full suite fails in a deliberately thin shell | generated stdlib validator ships and is the documented gate |
| scripts index | source-only exporter looked available in the product | explicit source-only inventory label; product validator retained |
| leak failure transcript | matched `.env` values were printed verbatim | findings redact both token and potentially secret-bearing path |
| dotenv parser | `secret # comment` produced a needle containing the comment | unquoted inline comments stripped; quoted hashes preserved |
| private aliases | standalone `AVCH` and spaced `Aviation Chat` survived a green export | substitution and blocking privacy lists cover every reproduced form |
| nested target | an output under an included source folder could self-enumerate | target must resolve outside the source tree, including `-WhatIf` |
| generated tutor mirrors | stale `/sudo-*` lessons outside authored files passed validation | every generated tutor door joins the live-surface scan plus mutant |
| training sentinel | `off` → `on` restored different bytes | one canonical three-line payload is exported and embedded in the command |
| scripts top-level inventory | both new scripts were absent from the auto-listed block | exporter and validator appear in the folder inventory |

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
