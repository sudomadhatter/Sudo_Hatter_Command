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
review-level: standard

## Outcome

`claude/teaching-edition` is refreshed through `origin/main` SHA
`c8f9c8c57708c745b29778269666f5e9b9829867`. It now builds one sanitized, zero-history command-center
shell whose tutor opens the current local SOP and current command bodies at every checkpoint. The tutor
does not preserve a second, stale copy of the workflow.

The owner can choose the command-center folder name at clone/download time. The tour then asks what to
name the first project and runs `/smh-new-project <name>`, which clones the paired
`sudo-project-skeleton` into `Projects/<name>`. A fresh shell and fresh project have no assumed Jira
board. Project-local Jira configuration is taught only after that project has a site, key, and board.

The shareable artifact is the generated export. This branch maintains the export recipe; SCC-280 does
not publish a repository, change visibility, or modernize the paired skeleton.

## Source and integration

- Final source main: `c8f9c8c57708c745b29778269666f5e9b9829867`.
- Final main integration commit: `0c66c7de5ab3402efe585b75fc0ef903d04729f2`.
- `git merge-base --is-ancestor origin/main HEAD` returned 0.
- The final merge reconciled two additive ledgers and three generated surfaces. SCC-280, SCC-293, and
  SCC-304 records were all preserved; command mirrors and the document graph were regenerated.
- Final product delta: 45 paths relative to `origin/main`; Declared Change Set reports no incomplete,
  undeclared, or unimplemented paths.

## What changed

- Added `/smh-tour` and reversible `/smh-training on|off|status`, with current Claude/Codex, opencode,
  and Antigravity doors.
- Bound every tutor stop to `docs/_scc_sops_prds/workflows_testing_SOP.md` plus the relevant live command.
- Rebuilt the exporter as a one-shell distribution with blocking privacy and integrity validation.
- Added a generic, inactive Jira example and a binding-first Jira rule: no project binding means no board.
- Hardened `/smh-new-project` so a safe user-chosen name becomes `Projects/<name>`, clone/init/commit
  failures cannot be reported as success, and Jira stays optional until a real board exists.
- Added the real-export contract, negative controls, generated navigation, and SOP currency updates.

## Generated export evidence

The final focused run at `0c66c7de` produced one shell with:

```text
copied      : 2676 files
excluded    : 62 files
structure   : 4 empty folders kept
substituted : 5674 tokens across 353 files
line-pruned : 9 source-only catalog rows
transformed : 9 files
leak scan   : 42 needles, 0 hits
validator   : TEACHING EDITION VALID
contract    : 46/46 passed
```

The generated shell has no `.git` history, active `.agents/jira.conf`, source worktree, private
account/host/project literals, or retired `/sudo-*` tutor instruction. Mutants prove those states are
rejected rather than merely absent from one happy-path export.

## Tour checkpoint dry-run

This is a non-mutating stop-by-stop inspection. It proves what the agent must open and report; it does
not create a sample project or fake a Jira board.

| Stop | Live sources opened | Checkpoint output verified |
|---|---|---|
| 0 | SOP Start here and §1–§4; `AGENTS.md`; `router.md` | Asks for the command-center name; teaches destination-name clone/archive rename, plan-first, owner sign-off, and persistence. |
| 1 | SOP §10 and §14; `.agents/scripts/INDEX.md`; exported validator | Runs the generated-shell validator, explains optional integrations without reading secrets, and states that the shell has no Jira board or binding. |
| 2 | `smh-new-project.md`; `new-project.ps1` | Asks “What do you want to name your first project?”, validates one portable folder segment, clones the canonical skeleton to `Projects/<name>`, and leaves Jira unconfigured. |
| 3 | SOP §5, §8, and §9 plus the chosen lane command | Explains story, project quick-dev, command-center Task, and lightweight command-center lanes; owner can state why the chosen lane fits. |
| 4 | SOP §6, §10, §11, §14 and the five current story/ship command bodies | Teaches RED→GREEN, literal approval, adversarial review, story landing versus epic shipping, and stops instead of inventing a ticket when no board exists. |
| 5 | SOP §7, §12–§19 and current Task close-out/operations commands | Covers close-out, machine switching, optional live queue/autopilot, incidents, command atlas, remaining actions, and optional training-off. |

Every stop begins with the live-source hard stop: if the SOP and command disagree, the tutor reports the
mismatch and pauses instead of teaching remembered mechanics.

## Acceptance evidence

| # | Result | Evidence |
|---|---|---|
| 1 | Pass | Latest `origin/main` is an ancestor of HEAD; final integration and overlap are recorded above. |
| 2 | Pass | Six-stop live-SOP curriculum, current-command inventory checks, generated-door parity, and manual checkpoint dry-run. |
| 3 | Pass | Real scaffold test asks for/uses a name, clones the canonical skeleton to `Projects/First_Project`, creates its own HEAD and hooks, and prints project-local optional Jira setup. |
| 4 | Pass | Zero-history real export, 42-needle/0-hit leak scan, fail-closed privacy controls, one-shell manifest, and shipped validator. |
| 5 | Pass | Repo-local generated surfaces are synchronized; retired tutor doors and commands are rejected. |
| 6 | Pass | Focused 46/46 and receipt-backed full suite 61/61 at `0c66c7de`; clean-code and review gates below. |

## Gate evidence

| Gate | Result |
|---|---|
| `test_teaching_edition.py` | 46/46 passed after final main merge |
| receipt-backed `tests/run_all.py` | 61/61 files passed in 139.9 s; `gates/suite.json`, clean tree, SHA `0c66c7de` |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 existing BOM information notices |
| Python compile | validator and focused contract compile cleanly |
| PowerShell parser | exporter and new-project script parse cleanly |
| `sync-agents.ps1 -Status` | every repo-local invocable surface matches its master |
| SOP currency | pass; SOP and changelog are updated on this branch |
| `check_links.py --base origin/main` | 247 claims checked; 0 branch-introduced failures; two baseline `PROJECT_ROOT` placeholders remain |
| Declared Change Set | present; incomplete 0, undeclared 0, unimplemented 0 |

## Paired skeleton boundary

The canonical repository was inspected read-only at
`d463613fa03e75bc46d2dd719be10937ebeefcd7`. It contains `.agents/jira.conf.example` and no active
`.agents/jira.conf`, which matches the no-board teaching contract. No skeleton file was changed here.
The broader AviationChat-derived skeleton upgrade—especially Playwright and current reusable development
machinery—is deliberately a separate follow-on with its own repository binding, plan, tests, and approval.

## Clean-Code Gate

Result: PASS.

- Machine floor: full suite, toolkit lint, Python/PowerShell parse, SOP currency, link delta, and sync
  status all pass for the authored change.
- Human floor: no credential values, source-specific absolute paths, debug residue, broad exception
  handling, or commented-out implementation were introduced.
- One audit finding was returned and fixed: the tutor's runtime-state path was written as one
  backticked nonexistent path, so it now names the real directory and filename without creating a false
  link claim. The two remaining link reports are baseline placeholders and were dismissed by diff scope.

## Code Review

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted: 5/5
lenses_na: none

dispositions: per-lens findings with a reproduced wrong output were applied and regression-tested; duplicate findings were merged; non-reproducing lowercase-key and platform-CI suggestions were dismissed with the canonical-key and current-machine boundaries recorded.
drift: declared=43 · changed=45 (two artifact/index carve-outs) · incomplete=0 · undeclared=0 · unimplemented=0

The review ran in fan-out at standard depth, followed by evidence verification and compound synthesis.
It repeatedly withheld PASS as real distribution-boundary issues were reproduced. Applied fixes include
literal `.git` boundaries, safe secret matching, no credential echo, physical source containment,
UTF-16/32 privacy scanning, generic always-on operator law, generic project-owned Jira, site/key/auth
agreement, path-level Jira-key scanning, Windows-reserved names, false-success prevention, generated
navigation, and the real project-clone handoff. Each surviving finding has an executable regression in
the 46-check contract.

### Step 0.7 — re-derivation

1. **Referenced movement:** `origin/main` advanced through `310824a`, `fa490f7`, and finally `c8f9c8c`; all were absorbed. The latest movement landed SCC-293 and SCC-304, adding link/review and Playwright machinery that the fresh export and full suite now exercise.
2. **True overlap and merge:** the latest merge reconciled `.sync-manifest.json`, `_artifacts/_main/INDEX.md`, the SOP changelog, and both doc-graph outputs. Both ledgers remain additive, generated files were rebuilt, no conflict marker survives, and `origin/main` is an ancestor.
3. **Sibling landing order:** SCC-293 and SCC-304 are landed and absorbed; no remaining sibling is a teaching-edition dependency. Skeleton modernization remains a separately authorized follow-on, not a landing dependency.

## Task Checklist

- [x] The merge itself — lands via this branch's PR
- [x] Re-pull and merge the latest `origin/main` without rewriting the teaching branch.
- [x] Replace the stale tutor with a live-SOP curriculum using current command families.
- [x] Teach command-center naming and named first-project creation from the maintained skeleton.
- [x] Export one sanitized shell with no assumed Jira board.
- [x] Regenerate current platform doors and reject retired tutor surfaces.
- [x] Run focused, full-suite, clean-code, drift, and review gates against the final main integration.
- [x] Keep the paired-skeleton modernization outside this first fix.

## Your Actions

- [x] SCC-280 engineering is complete; sharing/publishing the generated export remains an
  owner-controlled action.
- [ ] Create the replacement standalone skeleton-modernization ticket now that SCC-286 is closed;
  keep SCC-280 at `Review Required` until that follow-on ticket exists.

Verdict: PASS @ 0c66c7de5ab3402efe585b75fc0ef903d04729f2
