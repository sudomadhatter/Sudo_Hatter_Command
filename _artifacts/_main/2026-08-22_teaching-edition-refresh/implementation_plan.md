---
IsArtifact: true
ArtifactMetadata:
  title: Refresh the shareable teaching edition against the rebuilt development workflow
  type: implementation_plan
  date: 2026-08-22
  ticket: SCC-280
  lane: claude/teaching-edition
---

# SCC-280 — refresh the shareable teaching edition

## Goal

Bring the deliberately long-lived `claude/teaching-edition` distribution branch onto current
`origin/main`, preserve only its intentional teaching/export layer, and make a fresh exported command
center teach the rebuilt workflow correctly.

The exported repository is **one command-center shell**, paired operationally with the separately
maintained [`sudo-project-skeleton`](https://github.com/sudomadhatter/sudo-project-skeleton). It starts
with no project checked out and no Jira board. The owner names the command center when
cloning/downloading it; during onboarding the command-center agent asks what to name the first project
and clones the skeleton into `Projects/<chosen-project-name>`. The owner may connect that project to
its own Jira site/project/board when one exists. The tutor does not copy the workflow into a second manual: it opens
`docs/_scc_sops_prds/workflows_testing_SOP.md` at teaching time and uses that live file as its source
of truth.

## Decisions fixed by the operator

1. **The SOP changes while the system changes.** The tutor is a curriculum and navigator over the
   local SOP, not a frozen rewrite. Each workflow stop re-opens the current SOP section and current
   command body before teaching or acting.
2. **The download is a shell, not a preconfigured organization.** The export contains no active Jira
   site/key binding and promises no board. It carries only an example plus the optional setup path for
   the day the owner creates a project/board.
3. **Naming happens at the front door.** The README and first tour stop offer
   `git clone <repo-url> <chosen-command-center-name>` (or rename the extracted folder) and carry that
   chosen name through the onboarding language. No repository-wide identity rewrite is implied by a
   local folder name.
4. **One generated export, one maintained pair.** Retire the obsolete act of exporting
   `Fresh_Workspace_BMAD` from this branch. The shareable command center pairs with the already separate
   `sudo-project-skeleton` repository. During the tour the agent asks for the first project's name,
   then `/smh-new-project <name>` clones that maintained skeleton into `Projects/<name>`; its Jira
   binding remains optional until the project has a board.
5. **Current command law applies.** Teaching commands are `/smh-tour` and
   `/smh-training on|off|status`; every live `/sudo-*` and `main_debug` instruction is removed. The
   only long-lived branch taught is `main`; work happens in the current epic/story or Task worktrees.
6. **This source branch is not the thing handed to strangers.** Its generated, scrubbed, zero-history
   export is. No publish, repository creation, invitation, or visibility change is authorized by this
   task.

## Acceptance contract

| # | Observable acceptance row | Proof |
|---|---|---|
| 1 | `origin/main` is an ancestor of the refreshed branch, and the final `origin/main...HEAD` diff contains only the intentional teaching/export layer—not obsolete provenance edits, deleted-main tests, personal notes, or old session artifacts | `git merge-base --is-ancestor origin/main HEAD`; reviewed `git diff --name-status origin/main...HEAD`; stale legacy-only paths absent |
| 2 | With training on, the tutor opens the current local SOP and relevant current command before teaching; its live workflow uses `cicd-*`/`smh-*`, current worktrees/branch gates, artifacts, review, close-out, and shipping, with no live `sudo-*` or `main_debug` lesson | validator over tutor/rule/SOP references; command-door parity; manual dry run of all checkpoints |
| 3 | A fresh owner can choose the command-center name at clone/download time; the command-center agent asks for the first project's name and clones `sudo-project-skeleton` into `Projects/<name>`; neither repository assumes a Jira board, and optional Jira setup is explained for later | exported README/tour assertions for the clone destination argument, empty initial `Projects/`, project-name prompt, exact skeleton source/destination, absent active `.agents/jira.conf`, present generic example, and `/smh-new-project` hand-off |
| 4 | The exporter produces one sanitized command-center shell and cannot emit the retired second skeleton export, Daniel's project/client identity, the real Jira site/key, secrets, personal resources, or session history | fresh export to a temporary directory; leak/path scan; manifest assertions; zero-history initialization inspection |
| 5 | `/smh-tour` and `/smh-training` resolve through the current one-door platform model: authored command bodies, generated Claude/Codex launcher skills, generated opencode commands, and Antigravity workflows; retired `.claude/commands` and old tutor doors are absent | `/smh-sync-agents -NoGlobals`; sync `-Status`; `test_command_surfaces.py`; explicit old/new door inventory |
| 6 | The teaching-edition checks are non-vacuous and the command-center gate remains green | new test first fails against the stale branch; mutant export with a retired command or active Jira binding is rejected; `run_all.py`, `workflow_lint.py --toolkit-only`, SOP currency, JSON parse, PowerShell parser/export smoke |

## Implementation steps

### 1. Rebase the product concept onto current repo reality

1. Fetch `origin/main` immediately before integration and merge it into
   `claude/teaching-edition` without rewriting or force-pushing history.
2. Resolve shared-file conflicts to the current `main` implementation. Reapply only the teaching
   layer named in the Declared Change Set; discard the branch's old provenance-only rule edits,
   obsolete generated doors, retired test, personal quick-reference/board-session changes, and old
   artifacts from the final delta.
3. Re-read the post-merge SOP headings and the current bodies for every command the tour invokes.
   This is intentionally after the merge: a remembered 2026-08-04 workflow is not evidence.

**Assertion:** acceptance 1's ancestry and final-diff checks.

### 2. Write the failing teaching-edition contract first

Add a stdlib validator and an auto-discovered test that exercise a generated shell, not merely the
source manifest. The initial run against the stale teaching layer must fail for at least: retired
`sudo-*`/`main_debug`, an active SCC Jira binding, the two-export shape, and obsolete platform doors.
The test then mutates an otherwise-valid temporary export by inserting a retired command and an
active Jira binding; both mutations must make validation fail.

**Assertion:** the recorded RED output plus the two mutant-kill assertions in acceptance 6.

### 3. Rebuild training mode as a live-SOP tutor

1. Replace `/sudo-tour` with `/smh-tour` and `/training` with `/smh-training`.
2. Keep `.training-mode` as the reversible shipped-on sentinel, but update the conditional rule and
   root routing law so the tutor must open the current SOP/current command, explain terms and gates,
   cite the source, checkpoint each stop, and never invent or remember workflow mechanics.
3. Re-map the tour to the SOP's current structure: system model and lane chooser; naming and shell
   setup; ask for the first project's name and clone `sudo-project-skeleton` into `Projects/<name>`;
   optional Jira after a board exists; plan/approval/artifacts;
   story lane; Task/lightweight lane; review/close-out/shipping; switching machines and testing.
4. Add a short teaching-edition section to this branch's SOP for the two teaching-only commands.
   Keep the workflow content in the canonical sections; the teaching section points to them rather
   than duplicating them. Record the branch-specific SOP change in its changelog.

**Assertion:** acceptance 2 plus a manual checkpoint dry run that quotes the SOP section opened at
each stop.

### 4. Make the one-shell export safe and honest

1. Update the lobby manifest and exporter for the current tree and current Python portability
   (`python3` on Mac, `python` fallback on Windows). Remove the obsolete skeleton manifest and its
   replacement files.
2. Exclude the source repo's active `.agents/jira.conf`; add only a generic
   `.agents/jira.conf.example` to the export. The README/tour state that the shell has no Jira board
   and that projects configure Jira only after their own site/project/board exists.
3. Rewrite the exported README, router, operator profile, maintained-project worklist, sentinel, and
   `.env.example` for current law. The front door offers a clone destination/folder name and explains
   that `Projects/` begins empty.
4. Run the validator automatically at the end of a real export so privacy/workflow failures block the
   artifact rather than relying on a human remembering a grep.

**Assertion:** acceptance 3 and 4 against a new temporary export.

**Follow-on boundary approved with this plan:** after SCC-280 is complete, audit and upgrade the
separate `sudo-project-skeleton` repository with the reusable project-level infrastructure added to
AviationChat, specifically including Playwright and the newer shared development/testing machinery.
That work needs its own repo binding, plan, Jira key, worktree, compatibility audit, tests, and approval;
no AviationChat product/domain behavior is copied as part of SCC-280.

### 5. Regenerate current platform doors

Run the repo's current sync locally with globals disabled. Commit only generated repo-local outputs:
the two launcher skills on `.agents/skills` and `.claude/skills`, opencode mirrors, Antigravity
workflows, and manifest changes. Confirm the retired `.claude/commands` door and all old tutor names
are gone. Do not hand-edit a generated copy.

**Assertion:** acceptance 5.

### 6. Gate, inspect, and hand off—without publishing

1. Re-fetch `origin/main`; if it moved, merge it and re-run Steps 1–5's assertions. This is how a live
   SOP update lands in the tutor: the tutor points at the file, and the branch absorbs the file.
2. Run the full command-center gate, PowerShell parser/export smoke, JSON validation, link/reference
   checks, stale-name scans, and a cold-read of the exported shell for missing paths.
3. Write `walkthrough.md` with the exact source SHA, export evidence, RED→GREEN proof, remaining human
   publication actions, and a reminder that the generated output—not this source branch—is shared.
4. Run `/smh-code-review`; fix verified in-scope findings; commit explicit paths with `SCC-280` and
   push `claude/teaching-edition`. Do not merge to `main` or create/publish an external repo.

**Assertion:** all six acceptance rows, a clean/up-to-date lane, and the pushed branch SHA.

## Parity, portability, and sibling lanes

- **Mac/Windows:** the export engine remains PowerShell, but any Python subprocess probes
  `python3` then `python`; the validator itself is stdlib Python and is run with the platform's
  available executable. Paths are resolved from the manifest/repo, not a hard-coded user directory.
- **Four platforms:** command bodies stay in `.agents/commands`; every other tutor command door is
  generated by `/smh-sync-agents`. `.claude/commands` remains retired.
- **Thin projects:** no shared tutor/toolkit is vendored into projects. Sessions launched from the
  command center keep the tutor; `/smh-new-project` remains the single project-creation path.
- **Sibling work / landing order:** SCC-270 and SCC-271 currently overlap this plan on the SOP;
  SCC-270 also overlaps `AGENTS.md`, `.agents/.sync-manifest.json`, and `.agents/scripts/INDEX.md`, and
  SCC-271 overlaps `.agents/scripts/INDEX.md`. Non-overlapping SCC-280 work may proceed, but both
  sibling lanes land before SCC-280's final integration commit. Immediately afterwards SCC-280 fetches
  and merges `origin/main`, re-reads the resulting SOP, and regenerates/retests the tutor. If either
  sibling does not land, SCC-280 does not claim final acceptance: its latest-origin work is preserved,
  then the refresh/re-gate is repeated when the sibling becomes main truth. This is not a frozen copy;
  future SOP changes are absorbed by the same repeatable merge path and read live by the tutor.

### Port checklist

The generated command center is the second copy this plan intentionally creates, so all six port
checks are explicit:

| # | Check | Plan answer |
|---|---|---|
| 1 | A git-given path is used as given | The exporter receives manifest/target paths as arguments and resolves them with PowerShell path APIs; it does not reconstruct `.git` paths or infer a checkout from `cwd`. |
| 2 | `printf`, not `echo`, for shell-facing output | No new POSIX shell is authored. PowerShell uses `Write-Host`; Python uses `print`; generated docs show commands but do not implement a shell gate. |
| 3 | Verify the file, not `$?` | Validation opens the exported files and asserts their content/path inventory. A process exit is necessary but never the only proof. |
| 4 | No thin project depends on a shared-rule path it lacks | Tutor/rule/commands remain in the command center. `/smh-new-project` creates a thin project and sessions continue to enter through the center; nothing is copied into the project. |
| 5 | Both machines | Export uses `pwsh`; every Python launch probes `python3` then `python` (and the existing hook convention may include `py`). The test/README state both Mac and Windows spellings. |
| 6 | Hooks stay repo-local and use the target's key | The shell exports no active Jira binding and arms no project Jira key. A later project copies its own example, sets its own key/site, and arms its own repo-local gate only after its board exists. |

## Declared Change Set

- EDIT `AGENTS.md` — conditional training-mode routing points at the live-SOP tutor → 2
- EDIT `.agents/commands/INDEX.md` — teaching commands in the current `smh-*` family → 2, 5
- NEW `.agents/commands/smh-tour.md` — resumable live-SOP curriculum → 2, 3
- NEW `.agents/commands/smh-training.md` — sentinel on/off/status control → 2
- EDIT `.agents/commands/smh-new-project.md` — require optional Jira site/key/auth agreement before enforcement → 3, 4
- EDIT `.agents/rules/INDEX.md` — conditional training rule classification/trigger → 2
- EDIT `.agents/rules/jira.md` — no-binding preflight for a fresh command center → 3, 4
- EDIT `.agents/jira.conf` — bind the source lobby to both its site and key so the rule can reject an authenticated-site mismatch → 3, 4
- NEW `.agents/rules/training-mode.md` — tutor behavior and live-source hard stop → 2
- EDIT `.agents/scripts/INDEX.md` — exporter and validator inventory → 4, 6
- NEW `.agents/scripts/export-teaching-edition.ps1` — current one-shell export, portable map generation, blocking validation → 4, 6
- NEW `.agents/scripts/validate_teaching_edition.py` — reusable exported-shell validator → 2, 3, 4, 6
- NEW `.agents/scripts/tests/test_teaching_edition.py` — fresh-export contract and mutants → 2, 3, 4, 5, 6
- EDIT `.agents/scripts/tests/test_twin_parity.py` — classify both teaching-only `smh-*` commands as intentionally unpaired → 5, 6
- NEW `.agents/scripts/teaching-edition/lobby.manifest.json` — current include/exclude/transform/leak contract → 3, 4
- NEW `.agents/scripts/teaching-edition/replacements/lobby-README.md` — naming, empty shell, named skeleton clone, first-project/Jira onboarding → 3, 4
- NEW `.agents/scripts/teaching-edition/replacements/jira-conf.example` — generic optional binding only → 3, 4
- NEW `.agents/scripts/teaching-edition/replacements/memory-MEMORY.md` — valid empty generic memory index for the generated shell → 3, 4
- NEW `.agents/scripts/teaching-edition/replacements/memory-README.md` — generic memory-store operating contract without source-owner history → 3, 4
- NEW `.agents/scripts/teaching-edition/replacements/maintained-projects.txt` — empty current lint worklist → 3, 4
- NEW `.agents/scripts/teaching-edition/replacements/operator-profile.md` — generic current nine-obligation operator contract → 4
- NEW `.agents/scripts/teaching-edition/replacements/jira.md` — generic no-board default and project-owned Jira operating law → 3, 4
- NEW `.agents/scripts/teaching-edition/replacements/router.md` — empty current routing shell → 3, 4
- NEW `.agents/scripts/teaching-edition/replacements/training-mode-sentinel` — tutor ships on → 2
- EDIT `.env.example` — generic command-center environment names/instructions, values absent → 4
- EDIT `.gitignore` — keep the local training-off override from dirtying a fresh clone → 2, 3
- EDIT `.agents/scripts/new-project.ps1` — validate a portable single-segment name and refuse clone/init/commit false success → 3, 6
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — branch-only teaching entry points; workflow remains canonical/live → 2, 5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — teaching-branch SOP currency row → 2, 5
- EDIT `docs/doc-graph.md` — generated navigation reflects the teaching-only commands and artifacts on this branch → 2, 5
- EDIT `docs/doc-graph.json` — machine-readable generated navigation stays paired with the Markdown graph → 2, 5
- NEW (generated) `.agents/skills/smh-tour/SKILL.md` → 5
- NEW (generated) `.agents/skills/smh-training/SKILL.md` → 5
- NEW (generated) `.agents/workflows/smh-tour.md` → 5
- NEW (generated) `.agents/workflows/smh-training.md` → 5
- EDIT (generated) `.agents/workflows/smh-new-project.md` → 3, 5
- NEW (generated) `.claude/skills/smh-tour/SKILL.md` → 5
- NEW (generated) `.claude/skills/smh-training/SKILL.md` → 5
- NEW (generated) `.opencode/commands/smh-tour.md` → 5
- NEW (generated) `.opencode/commands/smh-training.md` → 5
- EDIT (generated) `.opencode/commands/smh-new-project.md` → 3, 5
- EDIT `.agents/.sync-manifest.json` — generated tutor-door ownership → 5
- NEW `_artifacts/_main/2026-08-22_teaching-edition-refresh/walkthrough.md` — implementation and verification evidence → 1, 6

All current-main files brought in unchanged by the merge are baseline integration, not authored scope.
All legacy teaching-branch changes that are reset to `origin/main` or deleted and therefore disappear
from the final `origin/main...HEAD` diff are cleanup, not surviving product scope.

## Self-Audit (2026-08-22)

**Level:** LEDGER+BLAST

**Mode:** PRE-WORK

**Subject:** `Sudo_Hatter_Command` · `claude/teaching-edition` · SCC-280
**Plan:** `_artifacts/_main/2026-08-22_teaching-edition-refresh/implementation_plan.md`

### Lens 1 — Repo Reality + Scope Ledger

```text
lens:        1 Repo Reality + Scope Ledger
checks_run:  declared_change_set.py parsed present=True, entries=43, incomplete=[] (22 NEW · 8 EDIT · 13 DELETE)
checks_run:  acceptance precondition: six rows at plan lines 52–57; each names a file/state/command/output observable
checks_run:  named current commands/files exist: smh-new-project.md, sync-agents.ps1, workflows_testing_SOP.md, workflows_testing_SOP_changelog.md
checks_run:  planned NEW paths are absent from origin/main or are generated outputs; every planned DELETE path exists on the stale teaching branch
checks_run:  Mac tools measured: /opt/homebrew/bin/pwsh and /opt/homebrew/bin/python3; bare python absent; plan requires python3→python portability
checks_run:  lane fit: no backend/, frontend/, firebase/, functions/, mobile/, or .github/ path is declared; this is command-centre Task work
checks_run:  Scope Ledger: every NEW row carries ≥1 acceptance number; validator has two planned callers (exporter + test), test is auto-discovered by run_all.py, transforms are called by the manifest, generated doors are called by their platform catalogs
read:        implementation_plan.md; .agents/scripts/declared_change_set.py; .agents/scripts/tests/run_all.py; .agents/scripts/sync-agents.ps1; .agents/commands/smh-new-project.md; docs/_scc_sops_prds/workflows_testing_SOP.md; legacy teaching manifests/commands/rule
verdict:     clean
```

The Scope Ledger is the Declared Change Set itself: each NEW row ends in the acceptance row(s) that
require it. The lowest-caller artifact is
`.agents/scripts/teaching-edition/replacements/jira-conf.example` (one caller, the lobby manifest),
and acceptance 3/4 require that exact inactive example. No created artifact has an empty acceptance
cell.

### Lens 2 — Parity + Blast

```text
lens:        2 Parity + Blast
checks_run:  command rename inventory covers authored bodies, commands INDEX, .agents/.claude launcher skills, opencode commands, Antigravity workflows, sync manifest, and retired .claude/commands
checks_run:  training rule is cited by root AGENTS.md and rules/INDEX.md; command bodies will carry the governing git/worktree/SOP pointers required by workflow_lint
checks_run:  usage-surface half and SOP half are declared in the same change set; [sop-ok] is not planned
checks_run:  delete/rename blast is gated by the fresh-export validator plus repo-local old/new door inventory
checks_run:  the generated-copy port section answers all six port-checklist.md rows at plan lines 163–168
checks_run:  sibling worktrees measured after git fetch origin main: SCC-270 overlaps AGENTS.md, .agents/.sync-manifest.json, .agents/scripts/INDEX.md and the SOP; SCC-271 overlaps .agents/scripts/INDEX.md and the SOP; landing order/remedy is recorded at lines 147–154
checks_run:  risk_seam.py classify returned {"status":"unclassified","tiers":{}}; result informed depth and did not gate the audit
read:        .agents/commands/smh-sync-agents.md; .agents/commands/smh-new-project.md; .agents/rules/sop-currency.md; .agents/rules/port-checklist.md; .agents/scripts/workflow_lint.py::_RULE_POINTERS; git worktree list; SCC-270/SCC-271 diffs and statuses
verdict:     clean
```

### Lens 3 — Pre-Mortem

```text
lens:        3 Pre-Mortem
checks_run:  silent failure: a validator that always returns clean is killed by the retired-command and active-Jira mutants in acceptance 6
checks_run:  other-machine failure: Python spelling and path resolution are pinned in the port checklist and PowerShell smoke
checks_run:  fresh-clone failure: acceptance 3/4 inspect the actual export for no .git, empty Projects/, no active Jira binding, a naming command, and resolvable first-project hand-off
checks_run:  sibling-lands-first failure: final integration is withheld until both overlapping SOP lanes land and the merged result is regenerated/re-gated
read:        implementation_plan.md acceptance rows 3, 4, 6; steps 2, 4, 6; parity/port/sibling section
verdict:     clean
```

Lens 3 had no surviving anchored Lens 1/2 finding to attach a failure narrative to; unattached
narratives were discarded as required.

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| — | No anchored finding survived after the declared changelog path was corrected to the existing `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` and the measured sibling overlaps were added to plan lines 147–154. | None | — |

### Observations

- The exact legacy branch name is an operator-selected distribution branch, so it intentionally does
  not use the normal `chore/SCC-280-*` Task naming. It remains a `claude/*` branch; authored commits
  lead with SCC-280 and no force-push is planned.
- Publication remains a separate owner action. Passing this plan proves a scrubbed export can be made;
  it does not authorize creating a remote repository or changing visibility.

**Sibling landing-order dependency:** SCC-270 + SCC-271 → SCC-280 final integration. Development on
non-overlapping paths may begin after approval; final acceptance and push wait for the latest landed
SOP and overlapping indexes to be merged and re-gated.

Audit verdict: GO

## Implementation Amendment — full-suite completion findings

The first receipt-backed full run at `e35165bf` passed 48 of 50 test files and exposed two contained
omissions:

1. `_artifacts/_main/2026-08-22_teaching-edition-refresh/` lacked its required row in
   `_artifacts/_main/INDEX.md`.
2. `test_twin_parity.py` correctly rejected the new `/smh-tour` and `/smh-training` commands because
   neither was in a pinned pair nor declared intentionally unpaired. Both are command-center teaching
   doors with no child-project `cicd-*` equivalent, so the fix records that subject boundary in
   `NOT_PAIRED` rather than inventing fake twins.

The remaining `test_check_maps.py` failure occurred only because the sandbox denied creation of its
temporary Git worktree. The same test is rerun with Git metadata access; no product assertion is
waived. This amendment directly completes acceptance rows 5 and 6 and does not change the approved
teaching/export behavior.

## Review-Driven Amendment — exported-shell failures

The first standard fan-out at `e35165bf` returned nine unique, reproducible failures. Three independent
lenses converged on the highest-risk paths, so these are patched before any verdict:

1. The leak scan's `.git` prefix check also skipped `.githooks`, `.gitignore`, and `.gitattributes`.
2. Literal secrets containing PowerShell wildcard characters bypassed the `-like` scan.
3. `/smh-training on` depended on a source replacement file the manifest deliberately excludes.
4. `/smh-training` could not resolve an archive-opened shell without Git metadata.
5. The retired-command regex missed quoted and Markdown-link command forms.
6. Optional Jira instructions copied the project example to the lobby-relative destination.
7. Three exported MCP configs retained the source machine's absolute workspace path.
8. The exported README told owners to run the source repository's full suite, which cannot pass in the
   intentionally thinned shell.
9. The exported scripts index presented the source-only exporter as locally available.

The fixes stay within the declared teaching/export surfaces. The leak matcher now has an executable
five-case self-test plus two source mutants that must fail; the real-export contract adds quoted-command,
clone-relative MCP, generated-validator, project-local Jira, and reversible-training assertions. The
final gate and final review are measured only after these patches and regenerated platform doors land.

## Approval

Approved by Daniel on 2026-08-22 with the bounded addition recorded above:
`approved, with one addition we will handle after this is complete.` The addition makes
`sudo-project-skeleton` the named first-project pair and defers the AviationChat-derived skeleton
upgrade until SCC-280 is complete.

## Final-Review Amendment — privacy and reversibility

The first verdict-eligible fan-out at `d8b63a38` withheld PASS and reproduced six additional defects:

1. leak failures echoed the matched credential into terminal and CI transcripts;
2. unquoted dotenv values with trailing comments were parsed as the wrong needle;
3. standalone `AVCH`, spaced `Aviation Chat`, and incident-door aliases escaped the privacy manifest;
4. an export target nested under an included source directory could recurse into its own output;
5. generated opencode/Antigravity tutor mirrors were outside the retired-command validator sweep; and
6. `/smh-training off` → `on` recreated content that differed from the committed exported sentinel.

The literal review also caught an incomplete generated top-level scripts inventory. These fixes remain
inside the approved exporter, validator, tutor, SOP, tests, indexes, and artifact surfaces. Acceptance
now requires an eight-case matcher/parser self-test, a redacted real leak failure, source-recursion
refusal, generated-mirror mutation kill, expanded private-alias scan, and byte-identical sentinel
contract before a new SHA can receive the final suite receipt or review verdict.

## Final-Review Amendment — shell integrity and no-board behavior

The next clean-review fan-out at `0b24ca78` withheld PASS and exposed a final set of reproducible
fresh-shell failures. The generated command center still inherited an unconditional live-Jira rule;
training-off removed a tracked sentinel and dirtied the clone; case/encoding and escaped-value privacy
variants could bypass the source or shipped validator; a symlinked target could resolve into the source;
missing declared includes did not fail closed; generated tutor mirrors were not byte-checked; nested
project invocation could bind the wrong root; and source-only incident/exporter rows survived in the
generated catalogs.

The review-driven fixes add the two DCS paths above and otherwise remain on approved exporter, tutor,
validator, test, generated-door, SOP, and artifact surfaces. The contract is now 24 executable checks:
the shell has no ambient Jira behavior until `.agents/jira.conf` exists, training-off uses an ignored
local override, required inputs and physical target containment fail closed, generated mirrors are
byte-identical to authored commands, privacy scanning covers escaped dotenv values and UTF-16/32 text,
and source-only catalog rows are pruned by required manifest anchors. The 24/24 pass is necessary but
not sufficient; a new five-lens review, full receipt-backed suite, and clean-code audit still gate PASS.

## Final-Review Amendment — distribution-boundary closure

The first fan-out on `b6c196d8` again withheld PASS. Blind, edge, and literal review reproduced seven
distribution defects: the exported sync manifest retained ownership of an excluded incident door;
the README claimed `/smh-new-project` completed follow-up wiring that the command only prints; an
included symlink could dereference outside the source; UTF-32BE content escaped both scanners; the
normal checkout's nested `.claude/worktrees/` could be recursively exported; and the owner's Windows
username and Mac hostname were absent from both deny lists. The seventh finding was the deliberately
stale walkthrough, which remains deferred only until the final reviewed SHA and receipt exist.

The fixes stay on already declared exporter, manifest, replacement, validator, test, and artifact
paths. Acceptance now includes 27 executable checks, required line-pruning of the incident ownership
row, physical containment of every included file, five text decoders including UTF-32BE, explicit
worktree-tree exclusion plus validator rejection, and independent deny-list mutations for both
machine identifiers. A new clean fan-out is required because this amendment changed the reviewed SHA.

## Final-Review Amendment — export boundary and project binding

The fan-out on `5da739e8` withheld PASS and reproduced eight final-boundary defects: the source Jira
project key survived as a standalone operational token; Linux containment comparisons were
case-insensitive; a quoted dotenv value containing a literal backslash could be decoded into the wrong
secret; the fresh shell omitted a valid generic memory-store index; the tutor could imply that the
source-only full suite was the generated-shell gate; manifest transform destinations could traverse
outside the target; `/smh-new-project` could print success after a failed first commit; and Jira binding
declared a project key without pinning the authenticated site.

The fixes remain within the declared source binding, exporter, manifest/replacements, tutor,
new-project script, validator, tests, generated mirrors, SOP, and artifact surfaces. Acceptance now
requires a case-sensitive operational-key scan, OS-appropriate path comparison, raw and decoded dotenv
needles, generic memory-store files, the generated-shell validator as Stop 1's explicit gate, a
non-overwriting transform-traversal regression, an existing scaffold `HEAD`, and matching
`JIRA_SITE`/`JIRA_KEYS` before any board operation. A fresh full review and receipt are required on the
resulting SHA.

## Latest-Main Integration Amendment — generated navigation and local assets

Immediately before final review, `origin/main` advanced to `310824a` and was merged as required by
Step 6. That live baseline retired the tracked `.claude/hooks/` mirror, preserved machine-local Claude
settings as a linked asset, and made the SOP link to the newly generated `docs/doc-graph.md`.

The first post-merge export correctly failed twice and supplied the RED evidence for the compatibility
work. First, containment examined the physical destination of an explicitly excluded machine-local
symlink before applying the exclusion; excluded paths now skip by their in-tree name without
dereferencing, while included symlinks retain the strict physical-source check. Second, the source doc
graph is deliberately excluded because it describes omitted/private files, so the export now opts into
regenerating both doc-graph outputs against its sanitized `.agents/` + `docs/` tree using the exported
generator itself. The contract is now 30 checks, including the hermetic excluded-symlink case, and the
post-merge generated shell passes privacy, link, map, and tutor validation.

## Post-Main Review Amendment — generic Jira and fail-closed privacy

The standard review of the current-main-integrated branch reproduced six final teaching-export
defects, all within the approved distribution boundary:

1. the generic operator-profile replacement lost its required `trigger: always_on` metadata;
2. the export copied the source command center's two-board Jira topology and only renamed its keys;
3. `/smh-new-project` required only `JIRA_KEYS`, despite the binding rule requiring site and key;
4. the source Jira key was scanned in file contents but not in exported path names;
5. the shipped validator omitted two configured private literals; and
6. short credentials under explicitly secret-named dotenv keys could escape, while a permissive
   manifest could attempt to include source `.git` history that the final scanner deliberately skips.

The fixes add a readable generic Jira replacement, preserve the floor-rule trigger, synchronize the
new-project instructions on every generated platform door, and make all three privacy boundaries fail
closed. Compound verification then closed interactions in the script's printed Jira handoff, Windows
reserved project names, secret-key classification, and `.git`-as-source handling. The executable
teaching contract is now 46 checks and includes an independent regression for every verified defect.

## Final Main Refresh Amendment

Immediately before close-out, `origin/main` advanced again to
`fa490f79e95f9a77387888b62cbc2ee2a59d5742` with SCC-295. Per the operator's explicit instruction,
that SHA was merged before the final gate. The sole conflict was the additive home-base artifact index;
both rows were preserved. No tutor/export dependency moved. Acceptance requires `origin/main` to remain
an ancestor of the teaching branch, the focused 46-case contract to pass, and a new receipt-backed full
suite to be stamped after this merge.
