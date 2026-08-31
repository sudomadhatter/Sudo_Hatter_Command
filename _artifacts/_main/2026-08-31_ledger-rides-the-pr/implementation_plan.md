# Implementation Plan — SCC-358 · the close-out ledger rides the PR

**Parent:** [SCC-358](https://sudo-command.atlassian.net/browse/SCC-358) · **Riders:** none — one lane
**Lane:** `chore/SCC-358-ledger-rides-the-pr` (no subtasks: six edits across two files, one repo, one coherent reordering — nothing here earns its own branch)
**Close:** `/smh-close-task-merge-tree --expect-key SCC-358`
**Lane class:** `lane_qualify.py` → `TASK` (*"toolkit path(s): .agents/commands/cicd-push-e2e.md — this changes the development system, so it takes the full lane"*), exit 1.

## Goal

**`/cicd-push-e2e` writes its bookkeeping after the merge, as a direct push to `main`, and an armed
ruleset refuses that push by design.** Measured live at the AVCH-111 close-out on 2026-08-31: the
ledger commit `6f374867` was refused by the gate, needed its own operator approval and a hand-built
`--no-ff` merge to land. With server-side rulesets now ACTIVE on both repos (lobby SCC-118 id
20756052; AviationChat AVCH-111 id 21963341), a PR with a green `main-write-gate` is the only road
to `main` — so every future epic ship strands its ledger commit exactly the same way.

**This is a port of law that already exists, not a new design.** Both sibling doors learned it
already, and one of them learned it the hard way:

| Door | What it already does | Where |
|---|---|---|
| `/smh-close-task-merge-tree` | commits the flight event + receipt **pre-merge, artifacts-only**, and carries ⛔ *"do NOT commit anything after the merge"* — the instruction that *"used to say the opposite, and that instruction was the whole of SCC-175"* | Step 2.5, Step 4 |
| `/cicd-close-story-merge-tree` | *"Run it LAST, after Steps 1–2 wrote the board, story file, and `active-context.md` — so those edits ride the story branch"* | Step 2, Step 3 |
| **`/cicd-push-e2e`** | **writes the ledger row and active-context in Step 6, after the merge** | ⛔ the holdout |

SCC-175 is not a near-miss to cite politely. It produced a non-merge commit on `main` that the write
gate correctly refused, and the refusal banner's `reset --hard` remedy then destroyed three other
sessions' uncommitted work (SCC-180). This lane closes the last door that can still reach that state.

## Ground truth (all from command output this session)

- `.agents/commands/cicd-push-e2e.md:321` — Step 6 items 1 and 2 are the ledger row and active-context,
  written while standing on `main`, after Step 4.5 proved the merge.
- `.agents/commands/cicd-push-e2e.md:124` — *"The tip you push is the tree Step 3 just gated"*. A new
  commit between the gate and the push makes that sentence false unless it is qualified.
- ⚠️ **AUDIT FINDING F2** · `.agents/commands/cicd-push-e2e.md:115-116` — Step 3's gate step ends
  *"Its report is the promotion evidence; link it in the ledger row (Step 6)."* Once S5 moves the row,
  that cross-reference points at a step that no longer holds it. It is also the natural bridge: the
  gate produces the evidence link, Step 3.5 carries it. One-word fix, `(Step 6)` → `(Step 3.5)`,
  folded into S2.
- ⚠️ **AUDIT FINDING F1** · `.agents/commands/INDEX.md:56` — the routing index describes the door's
  tail as *"…proves the merge with plain git, then CI/CD + Cloud Run deploy + live verify + **ledger**
  + epic branch deleted"*, i.e. the ledger after the merge. Lens 2's command-file row (scar SCC-66)
  requires the index to move with the door; it was absent from the first Declared Change Set and is
  added as S5b. **This is the highest-traffic copy of the wrong claim** — the index is what a routing
  agent reads instead of the door.
- `_artifacts/INDEX.md:16` columns are `| Date | Workspace | Slug | Summary | Status |`;
  `Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md:15` is `| Date | Folder | What | Status |`.
  **Neither table has a PR-number column or a merge-SHA column** — so Step 6's prose ("the PR number,
  the merge SHA") over-specifies against the table it writes to, and moving the row earlier costs
  no recorded field.
- `smh-close-task-merge-tree.md` Step 3 already settled the same question in writing:
  *"**Number-free on purpose** — the PR number is assigned when the PR is opened, which is after this
  commit is pushed. The number and merge sha go on the ticket in Step 4, where both are known."*
  `/cicd-push-e2e` Step 6.5 already posts both: `Merged to main via PR #<N> at <merge-sha>`.
- `_artifacts/INDEX.md:13` (lobby) — *"This ledger is reconciled in batch by the SessionStart hooks +
  `/smh-update-maps-indexes` — don't hand-append a row every session; get the folder right instead."*
  So Step 6's *"(and the home-base INDEX if run from the lobby)"* instructs a hand-append the lobby
  ledger's own header forbids — and it is a LOBBY row for a PROJECT ship besides.
- `main_write_gate.py --mode pr` validates the JIRA key on **every** commit in the PR range (`%B`,
  whole message). A bookkeeping commit with no key in its subject refuses the entire PR.
- `docs/_scc_sops_prds/workflows_testing_SOP.md:921` states the Step 5.5 outcome lands *"on the ticket
  and the ledger row"* — the same sentence, one altitude up. It moves with the command.
- `workflows_testing_SOP.md:3891` — the command-atlas node reads
  `S6["Step 6 — prune the epic branch\nledger row · active-context · 0 0 clean"]`.
- ⚠ **Two different things are called "the ledger row" in the SOP, and only one is in scope.**
  Lines **921** and **3891** mean a row in `_artifacts/INDEX.md` — in scope. Lines **1191** and
  **2469** mean the walkthrough's `- [x] The merge itself` checkbox in `## Your Actions` — a
  different artifact, out of scope, and not to be touched.
- `test_command_surfaces.py` blocks run to `CS-20`; `CS-19` already guards Step 5.5's presence and
  ordering with a `step()` helper that scopes a needle to one `##` section. `CS-21` is free.
- **No port trigger** (MANDATORY RULE 5): `Projects/AGY_AVIATIONCHAT/.agents/commands/`,
  `Projects/AGY_AVIATIONCHAT/docs/_scc_sops_prds/` and `Projects/NEXgen-VR-Director/.agents/commands/`
  all return *No such file or directory*. Neither in-scope file exists in a second repo.
- **No deployable paths** (MANDATORY RULE 4): the change set is `.agents/` + `docs/` only.

## Acceptance — six rows, each provable by a command

| # | Statement | The assertion that proves it |
|---|---|---|
| AC-1 | The door writes the ledger row and active-context on the epic branch, **before** `gh pr create` | `CS-21 A`: the new Step 3.5 section contains both `_artifacts/INDEX.md` and `active-context`, and `CS-21 B`: the offset of `## Step 3.5` is less than the offset of `gh pr create` |
| AC-2 | The `--after-merge` half instructs **no** repo write | `CS-21 C`: the slice from `## Step 4.5` to end of file contains no `git commit`, and Step 6's section names neither `_artifacts/INDEX.md` nor `active-context` |
| AC-3 | The pre-PR commit is instructed to carry the JIRA key in its subject | `CS-21 D`: the Step 3.5 section names `<JIRA-KEY>` inside its commit fence |
| AC-4 | Step 6 carries an explicit ⛔ against post-merge commits, naming why | `CS-21 E`: the Step 6 section matches `SCC-175` and `SCC-358` |
| AC-5 | Step 5.5's PRD-reconcile record names the ticket comment only — in the door **and** in the SOP | `CS-21 F`: `"and the ledger row"` appears in neither `cicd-push-e2e.md` nor `workflows_testing_SOP.md:921`'s row; grep both |
| AC-6 | Step 6 no longer instructs a hand-append to the home-base INDEX | `CS-21 G`: the Step 6 section does not match `home-base INDEX` |

Plus the standing gates: `run_all.py` green · `workflow_lint --toolkit-only` · `check_maps --depth3-only --strict` · `check_links` · `sop_currency` **passing on merit with the SOP staged, not `[sop-ok]`** (the usage surface genuinely moved).

## Steps

**S1 · Write `CS-21` RED first**, in `.agents/scripts/tests/test_command_surfaces.py`, immediately
after `CS-20`. Block title: `CS-21 · SCC-358 · the close-out bookkeeping rides the PR; the post-merge
half writes NOTHING`. Seven checks, A–G, exactly as the acceptance table names them. Reuse `CS-19`'s
`step()` and `after()` helpers rather than re-deriving them — and heed the comment already in that
block: **resolve the door from `ROOT`, never from `CMDS`**, or under `--case CS-21` the block dies
with an `UnboundLocalError`, which exits non-zero and is indistinguishable from a red. Run it and
**paste the RED**: A, B, C, D, E, G must fail against the unedited door; F must fail against the
unedited SOP.

**S2 · `cicd-push-e2e.md` — insert Step 3.5, "Record the landing on the lane, BEFORE the PR."**
Between Step 3 (the gate) and Step 4. It states the rule, does the two writes, and commits them with
explicit paths and the key leading the subject:

- the ledger row into `PROJECT_ROOT/_artifacts/INDEX.md` — copying the columns already in use,
  **number-free on purpose**, with the twin's own reason quoted so the next reader does not
  "fix" it back;
- the deployment into the project's `active-context.md`;
- `git add <those two paths>` then `git commit -F <message-file>` with `<JIRA-KEY>` leading the
  subject (⛔ backticks in `-m "…"` execute), because `main_write_gate.py --mode pr` reads every
  commit in the range and one unkeyed commit refuses the whole PR.

⚠️ **AUDIT FINDING F2, fixed in this same step.** `cicd-push-e2e.md:115-116` — Step 3's *"link it in
the ledger row (Step 6)"* becomes `(Step 3.5)`. Left alone it is a pointer into a step that no longer
carries the row, and it is the one sentence that tells the builder where the E2E evidence link goes.

**S3 · `cicd-push-e2e.md` Step 4 — qualify the gated-tip sentence.** *"The tip you push is the tree
Step 3 just gated"* becomes the tree Step 3 gated **plus Step 3.5's artifacts-only commit** — named
as artifacts-only for the same reason the twin's Step 2.5 is: markdown under `_artifacts/` changes
nothing the gate tested. Without this the file contradicts itself one screen apart.

**S4 · `cicd-push-e2e.md` Step 5.5 — the reconcile records to the ticket only.** *"Record it, in the
Step 6 ledger row and in the Step 6.5 ticket comment"* → the ticket comment. Same for the
`PRD: not reconciled` branch. State the reason inline in one line, because it is the one thing here
that genuinely cannot be moved: the reconcile diffs `<merge-sha>^1..<merge-sha>`, so it cannot exist
before the merge exists, and Step 6.5's comment is the only durable home left.

**S5 · `cicd-push-e2e.md` Step 6 — becomes prune + verify only.** Drop items 1 and 2 (they are now
Step 3.5) and the *"(and the home-base INDEX if run from the lobby)"* parenthetical with them. Keep
the prune, keep `0 0`. Add the ⛔ the twin already carries, in the twin's own terms: **do not commit
anything after the merge** — the gate refuses it, SCC-175 is what it cost, and SCC-358 is why this
step moved.

**S5b · ⚠️ AUDIT FINDING F1 — `.agents/commands/INDEX.md:56`.** The routing index's tail
*"…live verify + ledger + epic branch deleted"* becomes *"…live verify + epic branch deleted"*, with
the bookkeeping named where it now happens (before the PR). Lens 2's command-file row demands the
index move with the door (scar SCC-66), and this is the copy with the most readers: a routing agent
consults `commands/INDEX.md` precisely *instead of* opening the 350-line door.

**S6 · `workflows_testing_SOP.md` — three edits.** Line 921's *"on the ticket and the ledger row"* →
*"on the ticket"*. The atlas node at 3891 loses `ledger row · active-context`, and a bookkeeping node
appears before the PR node in the same diagram (`S3 --> S35 --> S4`), so the picture and the door
agree. §7's push-e2e narrative gains one sentence: the bookkeeping rides the PR, and the post-merge
half writes nothing. `flowchart TD` only — never `sequenceDiagram`.

**S7 · One changelog row** in `workflows_testing_SOP_changelog.md` under `## 2026-08`, dated
2026-08-31, ticket SCC-358, written as what changed for the operator.

**S8 · Green + sweep.** `run_all.py` green; `mutation_sweep.py` over `CS-21` — at minimum one mutant
per check that plants the removed instruction back into the post-merge half and one that moves
Step 3.5 below `gh pr create`, because an ordering guard that cannot see a move is the failure mode
`source-grep-guards-cannot-see-order` records.

⚠️ **The launcher question is now ANSWERED, not deferred** (it read "check, do not assume" in the
first draft, which is an instruction to re-derive something the audit can settle). The door's
`description:` frontmatter was read in full during Lens 2 and mentions neither the ledger nor
active-context nor Step 6 — it ends at *"prunes the epic branch and moves the epic ticket"*. No step
here changes it, and the generated launchers are thin pointers carrying only that description. **So
`sync-agents.ps1` is a no-op for this lane and is not run.** If S2 ends up rewording the frontmatter
after all, that is the one condition that re-arms it.

## Declared Change Set

- EDIT `.agents/scripts/tests/test_command_surfaces.py` — new block `CS-21`, checks A–G → AC-1…AC-6 (S1)
- EDIT `.agents/commands/cicd-push-e2e.md` — new Step 3.5, and Step 3's `(Step 6)` cross-reference → AC-1, AC-3 (S2)
- EDIT `.agents/commands/cicd-push-e2e.md` — Step 4 gated-tip sentence qualified → AC-1 (S3)
- EDIT `.agents/commands/cicd-push-e2e.md` — Step 5.5 records to the ticket only → AC-5 (S4)
- EDIT `.agents/commands/cicd-push-e2e.md` — Step 6 is prune + verify, with the ⛔ → AC-2, AC-4, AC-6 (S5)
- EDIT `.agents/commands/INDEX.md` — the door's tail description → AC-2 (S5b, audit finding F1)
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — line 921, the atlas diagram, §7 sentence → AC-5 (S6)
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row → the SOP-currency gate (S7)
- EDIT `.opencode/commands/cicd-push-e2e.md` — the full-body mirror, re-synced by byte copy → S8 (⚠ **undeclared in the first draft**; the plan wrongly concluded the sync was a no-op, and the door-parity check caught it. Recorded here because the review's drift check reconciles the diff against this list, and an honest list is the point)
- EDIT `_artifacts/_main/INDEX.md` — this session's ledger row → the standing `check_maps` F2 obligation (⚠ undeclared in the first draft; caught by the suite)
- EDIT `docs/doc-graph.json` · `docs/doc-graph.md` — regenerated and staged by the armed `pre-commit` hook, never hand-edited (⚠ undeclared in the first draft)
- EDIT `.agents/commands/cicd-push-e2e.md` — Step 6.5's comment gains the Step 5.5 PRD slot → AC-5 (S4; the edit S4 needs to be coherent, undeclared in the first draft)

## What this lane does NOT do

- **It does not touch `/smh-close-task-merge-tree` or `/cicd-close-story-merge-tree`.** The ticket
  asked for the twin to be audited; the audit ran and both are already correct, with their reasons
  written in the file. Editing a correct door to look symmetrical is churn.
- **It does not change the walkthrough's `- [x] The merge itself` row** (SOP 1191/2469). Different
  artifact, same three words.
- **It does not retire the hand-appended project ledger row** in favour of the batch reconciler.
  Both ledger headers say they are reconciled in batch, which is a real tension — but the remedy is
  to relocate the row, not to delete a record at the one moment the ship is provable
  (`limits-relocate-content-never-truncate`). Only the LOBBY parenthetical goes, and it goes because
  a project epic's row does not belong in the lobby's ledger at all.

## The live test

This lane ships through `/smh-close-task-merge-tree`, whose PR must go green on the lobby's
`main-write-gate` before the operator's click. That is the same door AVCH-111 proved yesterday, so
the landing is evidence, not ceremony.

## Self-Audit (2026-08-31)

**Level: LEDGER+BLAST** — the Declared Change Set touches a command/door surface
(`.agents/commands/cicd-push-e2e.md`) and a test others run (`test_command_surfaces.py`), so the
heavier level applies and all three lenses ran. **Mode: PRE-WORK.**

**Scope Ledger precondition.** Satisfied, and stated rather than assumed: the plan's acceptance table
carries **six** rows and each names the command that proves it. ⚠ The Jira description of
[SCC-358](https://sudo-command.atlassian.net/browse/SCC-358) carries no formal `ACCEPTANCE` block —
it is prose plus a "The fix:" paragraph — so the rows come from the plan, not the ticket. Recorded
because the precondition is a NO-GO ground and inventing its answer is what this audit exists to
catch. The ledger table itself is **empty by construction**: zero `NEW` bullets, seven `EDIT`s, so no
artefact can lack a row and no Scope Ledger finding is reachable.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  17 named paths exist on disk (all OK, listed) · 6 line-number anchors re-read in the
             LANE tree (4 exact, 2 off — F3, F4) · declared_change_set.py parse -> "incomplete": []
             · Scope Ledger: 0 NEW artefacts, so the table is empty and unfindable · lane fit: the
             change set is .agents/ + docs/ only, no backend/ frontend/ firebase/ functions/
             mobile/ .github/ -> correct door is /smh-close-task-merge-tree, as declared
read:        .agents/commands/cicd-push-e2e.md (106-200, 260-352) · .agents/commands/
             smh-close-task-merge-tree.md (350-400, 497-560, 620-640) · .agents/commands/
             cicd-close-story-merge-tree.md (grep) · .agents/commands/INDEX.md:56,58 ·
             _artifacts/INDEX.md:1-22 · Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md:13,15 ·
             docs/_scc_sops_prds/workflows_testing_SOP.md:841-880,915-925,1180-1195,3857-3900 ·
             workflows_testing_SOP_changelog.md:1-25 · test_command_surfaces.py:2756-2810 ·
             lane_qualify.py --paths … --lines 45
verdict:     findings below (F2, F3, F4)
```

```
lens:        2 Parity + Blast
checks_run:  command-file row -> commands/INDEX.md:56 describes the tail with the ledger AFTER the
             merge (F1); the four platform doors are thin launchers carrying only `description:`,
             and the door's frontmatter names neither the ledger nor Step 6, so no launcher regen
             is owed · command-NAME row -> N/A, no rename · script row -> scripts/INDEX.md has no
             test_command_surfaces entry (grep, zero hits); its only caller is run_all.py · gate/
             hook row -> none changed · path move/rename/delete row -> none · SOP row -> ARMED:
             sop_currency.py:72 lists (".agents/commands/", (".md",), "the / command menu"), so the
             SOP is owed in the SAME commit ON MERIT, and `[sop-ok]` would be wrong; the plan
             already stages it (S6, S7) · >1-repo row -> NO TRIGGER, proven: AGY .agents/commands/,
             AGY docs/_scc_sops_prds/ and NEXgen .agents/commands/ all "No such file or directory"
             · twins -> both doors sit in test_twin_parity.py NOT_PAIRED with stated reasons
             ("ships an epic to production; the lobby has no deploy"), so no fence-by-fence parity
             is demanded and the plan's "does not edit the correct twin" is the right call ·
             siblings -> `git fetch origin main` then `git worktree list`: exactly TWO trees, the
             main checkout at 344eed57 [main] and this lane at 344eed57. ZERO sibling lanes in
             flight, so zero landing-order dependencies · risk_seam classify -> {"status":
             "unclassified", "root": ".../ledger-rides-the-pr"}, permanently and correctly per
             SCC-289 (the centre is markdown; a code graph parses code), so every judgement in this
             lens came from the diff
read:        .agents/commands/INDEX.md · .agents/scripts/INDEX.md · .agents/scripts/sop_currency.py
             :20,71-72,80,109 · .agents/scripts/tests/test_twin_parity.py:87-170 ·
             git worktree list · git fetch origin main · risk_seam.py classify
verdict:     findings below (F1)
```

```
lens:        3 Pre-Mortem (bounded — attaches narratives, originates nothing)
checks_run:  the silent failure · the other-machine failure · the fresh-clone failure · the
             sibling-lands-first failure (N/A, zero siblings) — each tested against F1-F4 only
read:        (no new reads; operates on the anchored findings above)
verdict:     two narratives attached, zero originated
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/commands/INDEX.md:56` | *"…proves the merge with plain git, then CI/CD + Cloud Run deploy + live verify + ledger + epic branch deleted."* | The routing index keeps teaching the retired order after the door stops doing it — and it is the copy a routing agent reads *instead of* the 350-line door. Absent from the first Declared Change Set; Lens 2's command-file row (scar SCC-66) requires it. **Fixed inline as S5b.** | important |
| `.agents/commands/cicd-push-e2e.md:115-116` | *"Its report is the promotion evidence; link it in the ledger row (Step 6)."* | After S5 the ledger row is not in Step 6, so the one sentence telling the builder where the E2E evidence link goes points at nothing. **Fixed inline in S2** — `(Step 6)` → `(Step 3.5)`. | important |
| `_artifacts/_main/2026-08-31_ledger-rides-the-pr/implementation_plan.md` (Ground truth) | the plan cited `cicd-push-e2e.md:125`; the sentence begins at **:124** | Sends the builder one line past the sentence being amended. **Corrected inline.** | minor |
| `_artifacts/_main/2026-08-31_ledger-rides-the-pr/implementation_plan.md` (Ground truth) | the plan cited `_artifacts/INDEX.md:15`; **:15 is blank**, the header row is **:16** | An anchor to a blank line reads as "the columns are not there", which invites re-deriving a column set the ledger header explicitly forbids reordering. **Corrected inline.** | minor |

### Pre-Mortem narratives (attached, never originated)

**On F1 — the fresh-clone / other-reader failure.** Six months out, an agent deciding how to ship an
epic opens `commands/INDEX.md`, because that is the file whose whole job is to answer that question
without reading 350 lines. It reads *"live verify + ledger + epic branch deleted"*, writes the ledger
row after the merge, and the armed ruleset refuses the push. The refusal banner offers `reset --hard`
— and that is precisely the remedy that destroyed three other sessions' uncommitted work in SCC-180.
Leaving the index stale does not merely document the old flow; it reproduces the defect in the one
place a router actually looks.

**On F2 — the silent failure.** Nothing errors. The builder follows *"link it in the ledger row
(Step 6)"*, finds Step 6 is prune-and-verify, and quietly drops the `/cicd-e2e` report link. The row
lands without its promotion evidence, and the omission is invisible in every gate: `CS-21` checks
where the row is written, not what it contains. That is the shape `prose-pinning-guards-are-vacuous`
warns about, arriving through a dangling cross-reference rather than a weak guard.

### Observations (uncounted, non-blocking)

- The plan writes `python3` throughout with no `(PC: python)` note. Every step is a Mac-side gate run
  and the shipped artifacts are unaffected, so this changes no behaviour — but a builder resuming on
  the PC hits it (`two-machines-mac-and-pc`).
- Both ledger headers say the row is *"reconciled in batch"*, which sits in real tension with any door
  hand-appending one. The plan rules on it explicitly under *What this lane does NOT do* rather than
  silently picking a side, which is the right disposition for a plan; it is not a finding because the
  lane relocates the row and deletes no record.

**No sibling landing-order dependency** — measured, not assumed: two worktrees, both at `344eed57`.

Audit verdict: GO

## Approval

**Approval (2026-08-31):** "Approved" — the operator's verbatim word this turn, given at the
`/smh-plan-task SCC-358` Step 5 stop. Covers this plan and only this plan (one lane, no subtasks),
as it stood at `9415f732` (`Audit verdict: GO` recorded at that commit) — recorded at `4fdedf2f`.

Planning scope only, per `000-PLAN-FIRST-GATE`: it is not merge approval and not a ticket
transition. Edit this plan after this line and the gate re-arms at `/smh-quick-dev` Step 1.5.
