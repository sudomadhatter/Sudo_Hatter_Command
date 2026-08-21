---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-212 — apply the twin standard to the cicd command bodies (66 findings re-measured at 295abe5)"
  type: implementation_plan
  date: 2026-08-21
---

# SCC-212 — apply the twin standard to the cicd command bodies

**Lane:** `chore/SCC-212-twin-content-ports` @ `295abe5` (origin/main) · worktree `.claude/worktrees/SCC-212-twin-content-ports`
**Ticket:** SCC-212 (Task, moved To Do Next → In Progress, exit 0) · **Sequencing gate:** SCC-205 is Done (Parts B + E landed) — cleared.
**Sibling lanes:** SCC-235 touches only its own plan + `_artifacts/_memory/` — no overlap, no landing-order dependency.
**review-runtime:** fan-out (probed at Step 0: the Agent tool exists in this runtime).
**Build spec:** [edit-spec.md](edit-spec.md) — every live finding with its HEAD anchor and ready-to-paste text.

## What the re-measurement found, in one paragraph

The ticket lists 84 findings; deduplicated by ID they are **66**. Seven read-only passes (one per target
file) re-measured every one against `origin/main` @ `295abe5`. **55 are still live, 11 are settled** —
landed by SCC-205 Part C (five `cicd-quick-dev` items), SCC-211 (D7, the write-gate row), or deleted
on purpose by SCC-225's approved self-audit rewrite (four items whose target structure no longer
exists on EITHER twin). Three files are untouched since the sweep and every finding on them is live:
`cicd-merge-epic-workingtrees` (14), `cicd-dev-story-tests` (14), `cicd-create-epic-sprint` (6).
**Twelve backlog edits are wrong at HEAD** — they name dead doors (`/cicd-close-workingtree`,
`/cicd-update-sprint-memory` Step 4.5), omit a now-required flag (`closeout_preflight.py --expect-key`),
would duplicate text Part E already added, or rest on a premise SCC-210/211 inverted (the story door
now runs `check-actions`/`finish`; a project-repo chore lane now HAS a door). Each is replaced by the
edit the current tree actually needs, and the walkthrough's ledger says which.

## The decisions (recommendations, with the tradeoff)

1. **Six new twin-law fences across four pairs, not zero and not everything.** Fenced only where the
   text is genuinely subject-neutral and byte-identical is possible: `memory-sweep` (clean-code pair),
   `review-runtime-probe` (quick-dev pair), `merge-empty-set-stop` · `merge-machinery-last` ·
   `merge-cross-repo-order` (merge pair), `rederive-record` (code-review pair). Two pairs join
   `FENCED_TODAY`. Everything else is a **port** — the twins legitimately differ on the merge ref, the
   spec source, the door names, the runner lines, and forcing those identical would break one side
   (the parity test's own docstring lists exactly these as legitimate). *Tradeoff:* four smh files get
   marker lines (and `memory-sweep`/`rederive-record` a wording change, because the cicd wording is
   the one that matches the rule/parser), which is smh churn on a cicd ticket. Acceptance row 4 asks
   for regions MARKED — a fence is the only marking the guard can measure.
2. **One lane, no subtasks.** Every piece is a doc edit on the same branch sharing one test file, one
   SOP edit and one sync; nothing earns its own worktree. (Step 1.6: nothing clears the bar.)
3. **The cicd-create-epic-sprint reorder mints bare, then backfills.** The backlog's wholesale move
   breaks `jira_feed.py outline` (needs `epics.md` to exist). Mint the Epic bare with the requirements
   source as description → cut the branch keyed → write `epics.md` → backfill the outline with
   `acli … edit --description-file` → commit. SCC-49 is satisfied by the end of Step 2.
4. **`cicd-quick-dev` adopts a `task.yaml` on its ad-hoc lane** (QD-C12's durable half, now
   reachable because the non-deployable door is `/smh-close-task-merge-tree`, which reads it). Four
   lines that close the AVCH-59 fork at its root; the "recorded, not fixed" paragraph is rewritten.
5. **No `mutation_sweep.py` mandate on the story lane** (DEV-03): it is bound to the lobby harness and
   does not drive pytest/vitest; the declared table + sweep discipline are what the command owes.
6. **Three Antigravity mirrors flip to thin launchers** (`cicd-merge-epic-workingtrees` 11,350 → ~22.9 KB,
   `cicd-clean-code-audit` 11,397 → ~12.2 KB, `cicd-create-epic-sprint` 7,745 → ~14.0 KB; threshold
   11,500 B in `sync-agents.ps1:577`). That is the designed mechanism; `test_command_surfaces` accepts
   it; the sync MUST run in this lane. *(⚠️ AUDIT FINDING — the first draft said two; Lens 2 measured
   the kickoff's Edit B paste at 10,233 B against 5,850 B removed.)*

## Acceptance list (Step 1) — every row checkable, with the assertion that proves it

| # | Acceptance (from the ticket) | Checked by |
|---|---|---|
| 1 | Every finding applied, or explicitly dismissed with a reason — no silent drops | `assert-scc212.py` carries **one named case per applied finding** (55 live → cases keyed by ID); `--red origin/main` shows each RED before the edit and all GREEN at HEAD. The walkthrough's `## Disposition ledger` lists all 66 IDs: `APPLIED (case …)` or `SETTLED — <what landed it, sha>` |
| 2 | Hoisted law = POINTER **and** inline obligation; a pointer that replaced the obligation is a finding | Assert cases pair each rule pointer with its inline phrase in the same file: `cicd-dev-story-tests` (8 rules in the block + NO-GO read, eject, backtick, mutation table, RED paste inline); `cicd-clean-code-audit` (`artifacts-always-first` pointer + `memory-sweep` fence); `cicd-code-review` (`tests-must-gate-for-real` pointer + guard (c)); `git-policy.md` carries the backtick clause itself |
| 3 | Nothing classified LEGITIMATE_DIFFERENCE is "fixed"; state what was left different and why | Walkthrough `## Left different, and why` (merge ref · spec source · door names · runners · `PROJECT_ROOT` binding · `--story` vs slug); `git diff --stat origin/main -- .agents/commands/smh-*.md` lists **exactly** the four smh files and only fence/row edits; `test_twin_parity.py` block D prints **0** new `twin-divergence` markers |
| 4 | Twin-parity guard passes with shared regions MARKED | `python3 .agents/scripts/tests/test_twin_parity.py` exit 0 at HEAD with 6 new ids; **RED first**: fence `memory-sweep` on the cicd side only → block B `marks no law the twin lacks` FAILS (pasted); then the smh side → green. `FENCED_TODAY` gains two pairs; B* agrees |
| 5 | One `/smh-sync-agents` run at the end; all four doors resolve for every edited command | `pwsh .agents/scripts/sync-agents.ps1` exit 0 once, after the last content edit; `python3 .agents/scripts/tests/test_command_surfaces.py` exit 0 (12 commands × opencode/workflow/skill doors); `workflow_lint.py --toolkit-only` exit 0 |
| 6 | (house) Mutation-proven | `mutation_sweep.py --table sweep.json`: every fence drifted one side (identity) and unfenced one side (symmetry) → killed by the named `test_twin_parity` row; every ported region reverted → killed by its `assert-scc212.py` case. Closing bare run green |

## Declared Change Set

- EDIT `.agents/commands/cicd-dev-story-tests.md` — rules block (8 rules), Step 0.6 absorb/link/siblings, Step 0.8 probe, NO-GO read, RED paste, rung box, Step 3.5 eject, mutation doctrine, receipt-writer certification, backtick clause, Evidence RED→GREEN (E1–E10) → 1, 2
- EDIT `.agents/commands/cicd-write-story-tests.md` — link-worktree-assets line at Step 0.5 (E2b) → 1
- EDIT `.agents/commands/cicd-merge-epic-workingtrees.md` — rules block, commits-ahead, mechanical preflight + empty-set STOP, seven-class overlap table + two ordering overrides, `-C` everywhere + assert, verdict-void + re-measurement, check-actions, Dev Record/finish per lane, bare gates + additive totals, Step 7 verify (E0–E9) → 1, 2, 4
- EDIT `.agents/commands/smh-merge-multiple-workingtrees.md` — three `twin-law` fence markers, no wording change → 4
- EDIT `.agents/commands/cicd-quick-dev.md` — Step 0.5 key/fetch/worktree/link/start/siblings, Step 0.9 probe, backtick clause, door table + Done (SCC-211 doors), ad-hoc `task.yaml` (Edits 1–5) → 1, 2, 4
- EDIT `.agents/commands/smh-quick-dev.md` — `review-runtime-probe` fence markers around the existing probe → 4
- EDIT `.agents/commands/cicd-create-epic-sprint.md` — rules block, branch-first reorder with dedupe + bare mint + outline backfill, commit+push after Steps 2/3/4, NOT-approval list, Done verification (A–C) → 1
- EDIT `.agents/commands/cicd-clean-code-audit.md` — unstaged diff, §BIND STOP, `memory-sweep` fence + pointer, scan rows moved into Step 1 (E1–E4) → 1, 2, 4
- EDIT `.agents/commands/smh-clean-code-audit.md` — `memory-sweep` fence replaces its two-line guard; pointer row → 4
- EDIT `.agents/commands/cicd-code-review.md` — Step 0.6 diff + memory clause, DIFF/HEAD_SHA re-take, guard (c), Step 4 bullets with `rederive-record` fence, ceremony paragraph (story door truth), ② probe sibling (E1–E5, E7) → 1, 2, 4
- EDIT `.agents/commands/smh-code-review.md` — `DEFERRED_WORK` row; `rederive-record` fence replaces its three-line bullet → 1, 4
- EDIT `.agents/commands/cicd-self-audit.md` — Lens 2 sibling-lane bullet bound with `-C "$PROJECT_ROOT"`, epic ref, `status --short` → 1
- EDIT `.agents/rules/git-policy.md` — backtick-in-`-m` clause under Safe-commit mechanics; `:30-32` same-session-merge clause replaced by the door (E9, E9b) → 1, 2
- EDIT `.agents/scripts/tests/test_twin_parity.py` — `FENCED_TODAY` + two pairs; stale id comments → 4
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — `LOADERS` + `cicd-dev-story-tests.md`; comment → 2
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — ② STOPs, kickoff order, twin-parity row fence roster (SOP currency, same commit as the commands) → 5
- EDIT `.opencode/commands/cicd-dev-story-tests.md` — generated mirror → 5
- EDIT `.opencode/commands/cicd-write-story-tests.md` — generated mirror → 5
- EDIT `.opencode/commands/cicd-merge-epic-workingtrees.md` — generated mirror → 5
- EDIT `.opencode/commands/smh-merge-multiple-workingtrees.md` — generated mirror → 5
- EDIT `.opencode/commands/cicd-quick-dev.md` — generated mirror → 5
- EDIT `.opencode/commands/smh-quick-dev.md` — generated mirror → 5
- EDIT `.opencode/commands/cicd-create-epic-sprint.md` — generated mirror → 5
- EDIT `.opencode/commands/cicd-clean-code-audit.md` — generated mirror → 5
- EDIT `.opencode/commands/smh-clean-code-audit.md` — generated mirror → 5
- EDIT `.opencode/commands/cicd-code-review.md` — generated mirror → 5
- EDIT `.opencode/commands/smh-code-review.md` — generated mirror → 5
- EDIT `.opencode/commands/cicd-self-audit.md` — generated mirror → 5
- EDIT `.agents/workflows/cicd-write-story-tests.md` — generated mirror → 5
- EDIT `.agents/workflows/cicd-merge-epic-workingtrees.md` — generated; FLIPS to a thin launcher (>11,500 B) → 5
- EDIT `.agents/workflows/cicd-create-epic-sprint.md` — generated; FLIPS to a thin launcher (>11,500 B) → 5
- EDIT `.agents/workflows/cicd-clean-code-audit.md` — generated; FLIPS to a thin launcher (>11,500 B) → 5
- EDIT `.agents/rules/jira.md` — the §Who-mints-tickets seam pointed at `/cicd-create-epic-sprint` Step 1.5, a step the kickoff renumbering deleted (added at the review, finding A4) → 1, 2
- NEW `_artifacts/_main/2026-08-21_scc-212-twin-content-ports/review-findings.md` — the five-lens triage → 1
- EDIT `.agents/.sync-manifest.json` — the sync engine's own record of what it wrote → 5
- EDIT `_artifacts/_main/INDEX.md` — one row for this folder → 1

### Amendment 2 (2026-08-21, at the review gate)

**The roster's count was wrong by one, in the direction that hides work.** `QD-C12` is filed
SETTLED in the roster table below, and it is not settled: its case is RED at `origin/main` and the
edit landed. **The correct counts are 56 live and 10 settled**, and the walkthrough's
`## Disposition ledger` — which acceptance row 1 names as its own checker, and which was missing
until the review found it — carries all 66 IDs with the corrected split.

**`.agents/rules/jira.md` was edited and never declared.** The kickoff renumbering left the
§Who-mints-tickets seam pointing at a `Step 1.5` that no longer exists. Declared above.

### Amendment (2026-08-21, at the review's declared-set reconciliation)

Two drift rows, both mine, both corrected above rather than argued away:

**`undeclared`: `.agents/.sync-manifest.json`.** The sync writes it alongside the mirrors and
the first draft declared the mirrors but not the manifest. Declared now.
**`unimplemented`: eight `.agents/workflows/*` bullets, removed.** The plan declared a mirror
for every edited command; only **four** actually change. An Antigravity workflow that is
already a thin launcher carries the command's DESCRIPTION and nothing else, so it regenerates
byte-identically unless that description moves — and no description moved in this lane. The
four that changed are the three that crossed 11,500 B and became launchers, plus
`cicd-write-story-tests`, whose body is still mirrored verbatim. Over-declaring is not
harmless: it is the same class of claim as under-declaring, and the reconciliation caught it.
- NEW `_artifacts/_main/2026-08-21_scc-212-twin-content-ports/implementation_plan.md` — this plan → 1
- NEW `_artifacts/_main/2026-08-21_scc-212-twin-content-ports/edit-spec.md` — the per-finding build spec → 1
- NEW `_artifacts/_main/2026-08-21_scc-212-twin-content-ports/task.yaml` — the close-out manifest → 1
- NEW `_artifacts/_main/2026-08-21_scc-212-twin-content-ports/assert-scc212.py` — harness-based assertion pass, `--red <ref>` → 1, 2, 6
- NEW `_artifacts/_main/2026-08-21_scc-212-twin-content-ports/sweep.json` — the declared mutant table → 6
- NEW `_artifacts/_main/2026-08-21_scc-212-twin-content-ports/walkthrough.md` — ledger, evidence, review, Your Actions → 1, 3

(`.claude/skills/*/SKILL.md` launchers carry only the description, which does not change — the sync
rewrites nothing there; if it does, the diff is reported, not hidden.)

## Finding roster — 66 unique IDs, by target file

| File | Live (applied) | Settled (dismissed, with reason) |
|---|---|---|
| `cicd-dev-story-tests.md` | DEV-01 02 03 04 05 06 09 10 11 12 14 15 16 17 (14) | — |
| `git-policy.md` | DEV-01 rule half · QD-C1 rule residue (`:30-32`, found by re-measurement) | **D7** — landed by SCC-211 `73c6f9c` (`:70` write-gate row) |
| `cicd-merge-epic-workingtrees.md` | MERGE-01 02 03 04 05 06 07 08 09 11 12 14 15 16 (14) | — |
| `cicd-quick-dev.md` | QD-C1(partial) C4(partial) C7 C8 C9 C10 C11(partial) C14 (8) | **C2 C3 C5 C6 C12** — SCC-205 Part C, verified line-by-line |
| `cicd-create-epic-sprint.md` | PAIR-01 02 05 06 07 08 (6) | — |
| `cicd-clean-code-audit.md` | QD-C5(HIGH) C1(partial: placement) C2(partial: placement + `Path(__file__)`) C3 C4b (5) | — |
| `cicd-code-review.md` / `smh-code-review.md` | QD-C1(+C2 folded) C3 C4 C5(partial) C6 C7 · C9 (smh) (7) | **C2 as a separate edit** — premise inverted by SCC-210/242; its truth is folded into C1's replacement |
| `cicd-self-audit.md` / `smh-self-audit.md` | QD-C2(partial: binding + ref + status) (1) | **C1 C3a C4 C5** — SCC-225 rewrite: tripwire list + Light/Full ladder deleted on BOTH twins by an approved plan; STOP-on-no-plan exists at `:56-57`; constitution scan deleted on both sides by name — settled decisions, not gaps |

⚠ **Corrected at the review: Settled = 10 · Live = 56.** `QD-C12` is listed SETTLED in the `cicd-quick-dev.md` row above and is not — see Amendment 2. Every settled ID appears in the walkthrough's `## Disposition ledger` with the sha or plan that settled it.

## Steps (each maps to acceptance rows; the assertion that proves it is named)

1. **Artifacts + INDEX row** — this folder, `task.yaml`, INDEX row (so `test_check_maps` stays green). → row 1.
2. **RED instrument** — write `assert-scc212.py` (`_harness.Cases`, one block per target file, one case per live finding, `--red <ref>` reads blobs via `git show`). Run `--red origin/main` → every case RED; paste. A case that is green before its edit is fiction → rewrite it. → rows 1, 2.
3. **RED for the fence mechanism** — add `memory-sweep` to `cicd-clean-code-audit.md` only; run `test_twin_parity.py` bare → block B red (`marks no law the twin lacks`), pasted. Then the smh side → green. This is the one port whose RED comes from the live gate, not the assertion file. → row 4.
4. **Ports, file by file, per `edit-spec.md`** — order: clean-code → self-audit → code-review → quick-dev → dev-story-tests (+ write-story-tests, git-policy) → create-epic-sprint → merge-epic-workingtrees (+ smh fences). Surgical: re-diff every anchor against HEAD before replacing; never reflow adjacent lines. **Anchor by quoted TEXT, never by line number** — *⚠️ AUDIT FINDING (x2, both lenses): the spec's F24 citation read `:100-102`; the sentence lives at `:133-134`, and applying by number would have deleted the head of Step 0.7's answer list (CS-11 red). Corrected in the spec; the rule stands for every anchor.* The quick-dev probe is numbered **Step 0.7** (after Step 0.5, before Step 1), not 0.9 — Lens 2 caught the 0 → 0.9 → 0.5 reading order. After each file: its `assert-scc212.py` block `--case`, `workflow_lint.py --toolkit-only` bare. → rows 1–4.
5. **Test pins** — `FENCED_TODAY` (+2 pairs, comments), `LOADERS` (+1) **and the `:969` scope set (+1)**. Run `test_twin_parity.py` bare here. *⚠️ AUDIT FINDING: `test_command_surfaces.py` is RED by construction between step 4 and step 8 — the `.opencode/` mirrors are byte-identity doors (`:547-548`) and they are stale until the sync regenerates them. Do NOT hand-edit a mirror to clear it; run that file at step 8 only.* → rows 2, 4.
6. **SOP** — the three paragraphs; staged in the SAME commit as the commands (no `[sop-ok]`: this lane changes what the operator's commands do). → row 5.
7. **Commit** (explicit paths, `-F <file>` — the messages quote script names), push the lane.
8. **Sync** — `pwsh .agents/scripts/sync-agents.ps1` once; commit the mirrors; `test_command_surfaces.py` bare. → row 5.
9. **Suite, stamp-first** — `gate_receipt.py run --task SCC-212 --gate suite --root <folder> --cwd <worktree> -- python3 .agents/scripts/tests/run_all.py` on the clean tree. → all rows.
10. **Mutation sweep** — declare `sweep.json` BEFORE mutating (table below), `mutation_sweep.py --table`; paste. → row 6.
11. **Walkthrough** — `review-runtime:` header, Task Checklist, Disposition ledger (66), Left-different, Evidence (RED→GREEN per row + HEAD sha), then `/smh-code-review` appends the verdict; `## Your Actions`; Dev Record via `jira_feed.py devrecord --stage quick-dev` (no `--story`). Stop; hand to `/smh-close-task-merge-tree`.

## Mutant table (declared before the sweep; every mutant drawn from the edited text or the guard's code)

| # | Mutant | File | Kills via |
|---|---|---|---|
| M1 | drift one word inside `memory-sweep` on the cicd side | `cicd-clean-code-audit.md` | `test_twin_parity` C `memory-sweep` identical |
| M2 | remove the opening `memory-sweep` marker on the smh side | `smh-clean-code-audit.md` | `test_twin_parity` B smh marks no law the twin lacks (cicd orphan) |
| M3 | drift `review-runtime-probe` on the smh side | `smh-quick-dev.md` | `test_twin_parity` C |
| M4 | remove `review-runtime-probe` fence from cicd | `cicd-quick-dev.md` | `test_twin_parity` B |
| M5 | drift `merge-machinery-last` on cicd | `cicd-merge-epic-workingtrees.md` | `test_twin_parity` C |
| M6 | remove `merge-empty-set-stop` from smh | `smh-merge-multiple-workingtrees.md` | `test_twin_parity` B |
| M7 | drift `rederive-record` on smh | `smh-code-review.md` | `test_twin_parity` C |
| M8 | drop the quick-dev pair from `FENCED_TODAY` | `test_twin_parity.py` | `test_twin_parity` B* fenced set is exactly what is declared |
| M9 | revert `--expect-key` out of the merge door's preflight call | `cicd-merge-epic-workingtrees.md` | `assert-scc212` MERGE-03 |
| M10 | revert `git diff --name-only` (unstaged) line | `cicd-clean-code-audit.md` | `assert-scc212` QD-C5 |
| M11 | revert the NO-GO read (`A \`NO-GO\` stops the lane`) | `cicd-dev-story-tests.md` | `assert-scc212` DEV-06 |
| M12 | revert `-C "$PROJECT_ROOT"` on the epic `checkout -b` | `cicd-create-epic-sprint.md` | `assert-scc212` PAIR-07 |
| M13 | revert Step 0.6's `status --short` line | `cicd-code-review.md` | `assert-scc212` QD-C3 |
| M14 | revert the backtick clause in the rule | `git-policy.md` | `assert-scc212` DEV-01-rule |
| M15 | delete the `tests-must-gate-for-real` line from `cicd-dev-story-tests`'s rules-in-force block (the file is in `LOADERS` after step 5) | `cicd-dev-story-tests.md` | `test_command_surfaces` mutation-rule LOADED — *⚠️ AUDIT FINDING: the first draft also removed the file from `LOADERS`, which empties the check's loop and lets the mutant survive; step 5 adds the file to BOTH `LOADERS` (`:826`) and the `:969` scope set* |
| M16 | put the literal `## Declared Change Set` into `cicd-quick-dev.md` | `cicd-quick-dev.md` | `test_declared_change_set` :217 absence pin (negative control — the lane must NOT trip it) |

M1–M8 are drawn from the guard's own predicates (identity/symmetry/declared set), M9–M14 from the edited text, M15 from the pin, M16 is the control that the quick-dev edits stay clear of an existing pin.

## Left different on purpose (acceptance row 3 — restated in the walkthrough with evidence)

merge target (`origin/epic/…` vs `origin/main`) · spec source (story file + certification vs `implementation_plan.md`) · close-out verbs (`devrecord --story … --closing` + `finish --landing-ref` vs `finish` default) · runners (pytest/vitest/emulators vs `run_all.py`) · `PROJECT_ROOT` binding (cicd binds one project and never the lobby; smh-* naming `smh-target-resolution` is itself a finding) · `--story <id>` vs branch slug · the preflight script (`closeout_preflight` vs `task_preflight`) · the Light/Full ladder and the tripwire list (deleted on both twins by SCC-225 — not re-added).

## Risks and what closes them

- **A backlog edit applied as written would be wrong** (12 of them). Closed by: every anchor re-taken at HEAD in `edit-spec.md`; the walkthrough ledger names the replacement per ID.
- **Fence identity after whitespace re-wrap** — the guard normalises whitespace, so wrapping differs freely; the E1 flake is pinned on `disposition`. Run `test_twin_parity.py` bare after each fence.
- **`git-policy.md:116-118` records the permission layer denying `git -C <path> merge` in auto mode.** MERGE-01 mandates the `-C` form (the rule's own mandate; smh already uses it). Recorded in the walkthrough so a refusal is read as the classifier, not the text.
- **Pins that must survive:** `RE-ARMS the plan-first gate`, `no Declared Change Set — plan-exempt lane`, the ABSENCE of `## Declared Change Set` in `cicd-quick-dev.md`, `/cicd-prune-worktree` in the merge door (CS-13 D1), `a new gate that cannot fail` + `both machines` in the clean-code audit (assert-scc205). M16 + the closing full suite prove it.
- **Context compaction mid-build** — `edit-spec.md` carries every text in full; the build reads it, not memory.

## Self-Audit (2026-08-21)

**Level:** LEDGER+BLAST (the Declared Change Set touches a rule, two gate tests, 12 command/door surfaces across four platforms) · **Mode:** PRE-WORK · **Repo:** `SCC-212-twin-content-ports` worktree, branch `chore/SCC-212-twin-content-ports` @ `295abe5` (from `rev-parse`) · Lenses 1 and 2 ran as two subagents blind to each other; Lens 3 ran after, attached to their survivors only.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  path/step existence (20 scripts, 20 commands, 10 rules, 12×3 doors, plan steps 1–11) · declared_change_set.py parse (present · 47 entries · 0 incomplete) · both machines (0 bare python; pwsh present) · lane fit (0/47 deployable paths; door = /smh-close-task-merge-tree) · argparse reality for 14 invocations the spec writes into commands · ANCHOR REALITY: 108 edit-spec anchors grepped, 106 verbatim-and-once; the six smh fence regions quoted · non-vacuity: RED instrument + live-gate RED + 16-row mutant table, killers grep-verified · Scope Ledger: 6 acceptance rows each with an observable; 8 NEW/rewrite artefacts × row, caller counts
read:        implementation_plan.md · edit-spec.md · task.yaml · the 14 command files at every anchor · git-policy.md :29-40,69-71,115-119,298-301 · jira_feed/gate_receipt/mutation_sweep/closeout_preflight/link-worktree-assets/risk_seam/declared_change_set/workflow_lint/walkthrough_roster/task_preflight argparse · sync-agents.ps1:499-606 · test_twin_parity/test_command_surfaces/test_declared_change_set/test_review_engine/test_check_maps/_harness · SOP :469-513,1936
verdict:     findings below (2)
```

```
lens:        2 Parity + Blast
checks_run:  A doors (4 platforms × 12; launcher branch :575-625) · B git-policy pins in 12 test files · C test pins on EVERY replaced/rewrapped region (40 old literals over tests + skills + assert-scc205.sh; 14 test files read at the touching lines) · D fence texts scanned for subject words; "Left different" covers every pair · E _RULE_POINTERS run over the 12 targets; new literals + new headings checked · F sop_currency surfaces vs steps 6–8 · G status --short (no memory files) · H fetch + worktree list + SCC-235 diff/status/plan · I risk_seam classify (placeholder, unclassified) · J sizes + post-edit arithmetic
read:        the 12 targets at every anchored region · git-policy.md · sync-agents.ps1 · workflow_lint.py · sop_currency.py · risk_seam.py · walkthrough_roster.py · closeout_preflight.py · jira_feed.py · gate_receipt.py · link-worktree-assets.py · tests: twin_parity, command_surfaces, declared_change_set, review_engine, doc_examples_parse, self_audit_contract, walkthrough_roster, lens_roster_contract, door_preflight_order, stale_base_refs, git_hooks, jira_feed, lane_qualify, flight_recorder, workflow_lint · assert-scc205.sh · SCC-235 implementation_plan.md
verdict:     findings below (3)
```

```
lens:        3 Pre-Mortem
checks_run:  one failure narrative per anchored finding from lenses 1–2 (silent / other-machine / fresh-clone / sibling-lands-first); nothing originated here
read:        the findings table below; the plan's steps 4, 5, 8, 10
verdict:     attached below — no unattached output kept
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `edit-spec.md:131` and `:1026` (**x2** — both lenses, same anchor) | `` `cicd-code-review.md:100-102` "the dev-side commands do not carry this header … (F24)" `` — HEAD `:100-102` is `Then answer these three, in writing. **"Nothing moved" is a reportable result**…`; the F24 sentence is at `:133-134` | Applied by line number, E7 deletes the head of Step 0.7's answer list and `test_command_surfaces.py:1016-1019` CS-11 (`answer 1`) goes red. **Pre-mortem:** the builder resumes after a compaction with the spec open and edits by the number it sees. **Fixed:** both citations now read `:133-134`; step 4 states *anchor by quoted text, never by line number*. | medium |
| `implementation_plan.md` step 10, row M15 | `drop cicd-dev-story-tests.md from LOADERS while also dropping the rule from its block` vs `test_command_surfaces.py:826-829` `unloaded = [n for n in LOADERS if …]` and `:969` `{"smh-quick-dev.md", "smh-self-audit.md"} <= set(LOADERS)` | The named killer iterates `LOADERS`; removing the file empties the loop and the mutant SURVIVES → acceptance row 6 records a survivor. **Pre-mortem:** the sweep prints one survivor, the builder "re-aims" it after the fact, and the table is no longer the one declared before mutating. **Fixed:** M15 now deletes only the rule line from the block (file stays in `LOADERS`); step 5 adds the file to `LOADERS` AND the `:969` scope set. | medium |
| `implementation_plan.md` step 5 | `Run test_twin_parity.py and test_command_surfaces.py bare` vs `test_command_surfaces.py:547-548` `if body == brain: return "ok"` … "byte identity or it is stale" | Door parity is red for all 12 commands between step 4 and step 8 by construction. **Pre-mortem:** a builder clears the red by hand-editing `.opencode/` mirrors; the next sync reverts them and the generator contract is broken silently. **Fixed:** step 5 runs `test_twin_parity.py` only and names the expected red; `test_command_surfaces.py` runs at step 8 after the sync. | low |
| `implementation_plan.md:54-55` + DCS row `.agents/workflows/cicd-create-epic-sprint.md — generated mirror` | "Two Antigravity mirrors flip" — measured: create-epic-sprint 7,745 − 5,850 + 10,233 + 1,370 + 497 ≈ 13,995 B > 11,500 (`sync-agents.ps1:577`) | A THIRD Antigravity door becomes a launcher and the walkthrough would under-report it. **Pre-mortem:** the operator opens the kickoff on Antigravity and the steps are gone — expected, but unannounced. **Fixed:** decision 6 and the DCS row say three. | low |

### Observations (uncounted)

- `edit-spec.md` cites `git-policy.md:30-32` — the two quoted lines are `:31-32` (`:30` is the bullet head); `HEAD_SHA` is read at `:45`, not `:44`. Text anchors unique; numbers off by one.
- `edit-spec.md` §5 E2 says the §BIND clause "matches `cicd-code-review.md:37-38` verbatim" — only the tail clause matches (HEAD carries a nested-skills parenthetical). It is a port; no gate compares them.
- `cicd-quick-dev` Edit 2 would have read 0 → 0.9 → 0.5 → 1; renumbered to **Step 0.7** after Step 0.5 (edit-spec §3 amended).
- `_harness._matches` is a case-insensitive substring filter: `sweep.json` `block` values must be distinctive prefixes (`"C · IDENTITY"`, `"B · SYMMETRY"`), not single letters.
- New `python3` lines in E6/E7/E8 (§1), E2 (§2) and §7 lack a `# PC: \`python\`` note; the house is inconsistent on density — add the note where a line is a command the operator types.
- `assert-scc205.sh` is not wired into `run_all.py`; its `a new gate that cannot fail` / `both machines` greps are advisory — re-run it by hand at step 9 as a control.
- `memory-sweep` fence text contains `lobby` once ("the lobby's index plus each project's own") — true on both sides, identity holds.
- `risk_seam.py classify` → `{"status": "unclassified"}` (placeholder by design; informs nothing yet).
- `_RULE_POINTERS` run over all 12 targets today: clean; every new trigger literal has its pointer after E1/Edit A.

### Sibling landing-order dependency

**SCC-235** (`chore/SCC-235-dual-surface-blast-radius` @ `dae82f8`): zero file overlap today (its diff is its own plan + `task.yaml`; dirty `_artifacts/_memory/` files are its own). Its plan intends later edits to `/cicd-self-audit`, `/cicd-code-review` Step 0.7 and `/cicd-write-story-tests` — three files this lane rewrites. **SCC-212 lands first** (doc-only, anchored at `295abe5` now). If reversed, every SCC-212 anchor in those three files goes stale and the spec must be re-measured; if SCC-235 lands second it is the *rewrite-vs-edit* class and must re-author on top, never auto-merge. Both lanes add one `_artifacts/_main/INDEX.md` row — a one-line adjacent conflict for whichever is second, trivial.

Audit verdict: GO
