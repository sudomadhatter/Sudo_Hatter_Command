# Walkthrough — SCC-155 — plan-the-whole-Task + labelling surface v2 + user-tasks close-out

**Lane:** `chore/SCC-155-label-tasks` in `.claude/worktrees/label-tasks`
**Plan:** [implementation_plan.md](implementation_plan.md) · **Manifest:** [task.yaml](task.yaml)
**Operator rulings this lane:** retire `/cicd-parallel-check` (reuse the logic, delete the
command, only *after* the replacements are complete) · add a whole-Task planner · **"no sub task
we need to one shot this"** — SCC-155 itself gets no Subtasks, all three clusters land here.

---

## Task Checklist

- [x] **A1 — one labelling engine, two commands.** `parallel_check.py` → `label_tasks.py` by
      `git mv` (history preserved). Story mode serves `/cicd-label-tasks`; **task mode** serves
      `/smh-label-tasks` with its own grounding ladder (branch-diff → sibling `task.yaml`'s plan →
      the ticket's own description; ambiguity counts as an EDIT). Both stamp `parallel-ok` **and**
      `quick-dev`, and both post a verdict comment on the parent.
- [x] **A2 — `/smh-plan-task` plans the whole Task in one shot.** Propose-and-STOP → mint the
      Subtasks → per subtask: cut the worktree, write the plan into that lane, self-audit, commit
      and **push**, update the ticket → finish by invoking `/smh-label-tasks` and printing the
      parallel table.
- [x] **A3 — batch approval is recorded evidence, never self-written.** One STOP presents every
      plan, its audit verdict and the parallel table; the operator's **verbatim** words are
      recorded into each plan (the SCC-37 quote pattern). `000-PLAN-FIRST-GATE.md` gains a narrow
      clause with four mandatory conditions; any edit to a plan re-arms the gate.
- [x] **A4 — open operator actions hold the ticket out of `Done`.** `jira_feed.py finish` reads
      the walkthrough's `## Your Actions`: open `- [ ]` items → post a "User tasks" comment, add
      the `user-tasks` label, climb the `Awaiting Review` → `In Review` ladder, and REFUSE `Done`.
      Four outcomes, four exit codes. Missing walkthrough or missing section is a **refusal**.
- [x] **A5 — the retirement is complete, and it ran LAST.** `cicd-parallel-check.md` deleted, its
      four generated doors pruned by `sync-agents`, both INDEXes updated, live references
      repointed. The sweep that originally found 28 files now returns only history
      (`_artifacts/` walkthroughs) and the memory store — see `## Your Actions`.
- [x] **A6 — documented + green.** SOP updated in the same commits (the gate is armed); suite,
      lint and maps stamped through `gate_receipt.py`; mutation sweep declared from the diff, run
      as one pass, sources restored in a `finally`.

---

## Evidence

Every run below is pasted from the actual terminal, with the sha it was measured on.

### Assert-first: the RED runs came before the code

| Cluster | RED (before) | GREEN (after) | Commit |
|---|---|---|---|
| A — the engine | **49/65** | **65/65** | `47a7ebf` |
| C — `finish` | **152/165** | **165/165** | `9ebb008` |
| Mutation gap-closing cases | see the sweep below | **78/78** · **173/173** | `1e76a85` |
| Code-review fixes | **84/87** · **176/186** | **88/88** · **193/193** | `7f83358` |
| The ten rolled-in findings | **91/95** · **196/197** · **145/147** | **101/101** · **197/197** · **147/147** | `028e6cf` |

Two RED-honesty problems were caught *in* the RED runs and are worth recording, because both are
the "a red can lie" class:

- The first RED aborted the whole file at `AttributeError: module 'label_tasks' has no attribute
  'gate_task'` — later cases never reported at all. Fixed with a `refuses()` helper that returns a
  string for a missing function, so **every case lands on its own assertion**.
- *"story mode refuses a Task parent"* passed for the **wrong reason**: `gate_bmad` already exited
  because the summary had no `Epic N`, not because of the type. Fixed by asserting the refusal
  TEXT and moving the type check first. **This exact class came back in the mutation sweep** —
  see below.

Three more vacuous greens were caught before commit: two inherited `set_labels` cases passed
because a non-empty dict is truthy under the old boolean signature; five `finish` cases passed
because **argparse also exits 2 on an unknown verb**, which is precisely what the fail-closed
cases asserted.

### The floor, at `1e76a850` (receipts committed in-tree under `gates/`)

```
[PASS] suite exit=0 196.9s @ 1e76a850
        receipt: gates/suite.json
25/25 files passed

[PASS] lint  exit=0 0.2s @ 1e76a850   (workflow_lint --toolkit-only: 0 errors, 0 warnings)
[PASS] maps  exit=0 0.1s @ 1e76a850   (check_maps --depth3-only --strict)
```

`lint` and `maps` stamp `[DIRTY TREE]`, and `dirty_paths` records exactly why: the receipts
written moments earlier in the same sequence. Artifacts-only — the SCC-154 exemption — and the
suite receipt itself is clean.

### Mutation record — 32 mutants, drawn from the diff

Mutants were drawn from `label_tasks.py` and `jira_feed.py`, **never from the assertions** (a
mutant derived from the test it must fail is circular, SCC-144). The table mixes **width**
narrowings with **existence** deletions, because SCC-154 proved an existence-only sweep certifies
that the code runs, not that the tests cover it. One pass, sources restored in a `finally`,
`git status` re-checked at the end.

**First sweep: 16/32 killed.** Every one of the 16 survivors was a real gap, and two were the
pass-for-the-wrong-reason class recurring inside its own follow-up:

- **`gate_bmad`'s type check could be deleted green.** The Task parent in that case also has no
  `Epic N` in its summary, so the *grouping-epic* refusal fires instead — and I had put
  `/smh-label-tasks` in that message too. Right answer, wrong reason, a second time. Now pinned on
  `"is a Task, not an Epic"`, the sentence only the type arm can produce.
- **`ground_child`'s task arm had ZERO execution.** Every case feeds `resolve` a pre-built packet
  whose fixture hand-writes the `authority` and `next_command` that `ground_child` is supposed to
  *compute*. Deleting the ticket rung and blanking the unlock command both survived a full green
  run. It is now driven directly, in a bare temp dir where the third rung is the only one left.

Thirteen named cases closed the sixteen gaps; the stub gained `no_status` (a column the board does
not carry: the call is recorded but the status does not move), because `stuck_status` blocks every
rung at once and so can never tell *"fell through to the second"* from *"never tried"*.

**Second sweep: 32/32, every mutant killed by a NAMED case, sources restored clean.**

| # | Kind | Mutant | Killed by |
|---|---|---|---|
| LT1 | existence | `gate_task` refusal removed | task mode refuses an Epic parent… |
| LT2 | width | `("epic","")` → `("epic",)` | …refuses an UNTYPED parent too |
| LT3 | existence | `gate_bmad` type check removed | …refuses for the TYPE, not the summary's shape |
| LT4 | width | type check narrowed to `== "subtask"` | …refuses for the TYPE, not the summary's shape |
| LT5 | width | plan join exact → `startswith` | a FOREIGN task_key does not ground this key |
| LT6 | existence | `plan.is_file()` guard removed | a task.yaml with no plan grounds nothing |
| LT7 | existence | tri-state `None` arm removed | label_plan leaves an unassessed label alone |
| LT8 | width | `"eligible" not in q` dropped | a quick_dev block with no `eligible` is UNASSESSED |
| LT9 | width | action join `" "` → `","` | an eligible child GAINS quick-dev in the same pass |
| LT10 | width | `resolve_mode` hard-coded `"story"` | a Task parent derives task mode with no flag |
| LT11 | existence | `--mode` override ignored | --mode overrides the board when its type is wrong |
| LT12 | width | `no-plan` → always `no-story` | an ungrounded Subtask reads 'no-plan' |
| LT13 | existence | ungrounded `quick_dev` `False` → `None` | an UNGROUNDED child LOSES a stale quick-dev |
| LT14 | width | `COMMAND[mode]` → `COMMAND['story']` | a task-mode stamp says re-run /smh-label-tasks |
| LT15 | existence | the ticket rung removed | a Subtask with only a DESCRIPTION is grounded |
| LT16 | existence | the unlock command blanked | ground_child names /smh-plan-task as the unlock |
| LT17 | width | packet `mode` hard-coded | an ungrounded Subtask reads 'no-plan' |
| JF1 | existence | missing section returns `[]` not `None` | a walkthrough with NO section refuses |
| JF2 | existence | section-end `break` removed | a checkbox OUTSIDE the section is not an action |
| JF3 | width | break narrowed to `## ` only | a top-level `# ` heading closes the section too |
| JF4 | width | **both** checkbox guards widened | a walkthrough with no open items closes |
| JF5 | existence | walkthrough-exists check removed | a MISSING walkthrough refuses |
| JF6 | existence | HELD exit `3` → `0` | holding is its own exit code |
| JF7 | existence | HELD branch bypassed | an open operator action REFUSES to write Done |
| JF8 | existence | HELD dry-run guard removed | a HELD dry run posts/labels/moves nothing |
| JF9 | existence | label add removed | the ticket is labelled user-tasks |
| JF10 | width | label write clobbers the set | adding user-tasks PRESERVES every label |
| JF11 | existence | ladder loop removed | a status ladder is attempted before giving up |
| JF12 | width | ladder narrowed to one rung | a board missing the FIRST rung lands on the second |
| JF13 | existence | `--yes` dropped from the close | the close carries --yes (+ the repo yes-guard) |
| JF14 | existence | post-transition verification removed | a close that REPORTS success but does not land |
| JF15 | width | already-Done short circuit removed | an already-Done ticket transitions nothing |

**`JF4` and the compensating pair — resolved, not just recorded.** It could not be killed by
mutating either checkbox guard alone: `_OPEN_ITEM_RE` required `[ ]` and `_CHECKED_ITEM_RE`
rejected `[x]`, so each masked the other's absence and `_CHECKED_ITEM_RE` was provably dead. The
first draft of this walkthrough recorded that as deliberate belt-and-braces; the review pushed
back correctly — a dead guard that *reads* live is how the pair becomes a real hole the day
someone widens the other half, with no mutant able to reach it. `_CHECKED_ITEM_RE` is **deleted**,
and `JF4'` now kills on `_OPEN_ITEM_RE` alone.

### Sweeps #1 (re-run) and #2 — the review-fix regions

The fixes moved five of sweep #1's anchors and added code no mutant had touched, so the table was
re-derived rather than re-asserted. **Sweep #1 re-run: 27/32, no survivors** (5 anchors moved).
**Sweep #2, 20 mutants over the changed and new regions: 19/20 killed, each by a NAMED case.**

It also caught **two of my own new cases being vacuous**, which is the whole reason the sweep runs
after the fixes and not only before them:

- The ladder case asserted "at most one transition" and "the string is absent" — both true when
  the script **crashes**, which is exactly what the mutant did. Re-anchored on `exit == 3` and a
  positive `UNKNOWN` in the output.
- The nested-fence fixture put its open checkbox *outside* the `~~~` block, so it passed whether
  or not the fence rule held. Rewritten so everything that must stay invisible is inside it.

**The one live survivor, deliberately left:** `NF13` — `cmd_plan`'s console `[NO-PLAN]` label. It
needs a stub-driven `cmd_plan` case, which is finding #23's deferred work; the board-facing
verdict for the same child *is* pinned. It is a console string, and it is the only mutant in
either sweep still standing.

---

## Code Review (2026-08-14)

Verdict: PASS @ effc2935

Suite evidence measured at `effc2935` (receipts re-stamped after the roll-in).

**This verdict was CONCERNS @ `7f833584` and was RAISED to PASS.** The cap was the ten
deferred findings; the operator ruled *"no we do this ticket roll it in"* this session, so
they are applied here rather than carried. No row in the findings table is deferred, and no
mutant in any of the three sweeps survives.

**Scope.** `main...HEAD`, 46 files, clean tree. **Method.** `/smh-code-review`: the five-lens
`code-review-engine` fan-out, an acceptance audit against the plan's A1–A6, the command-centre
gate, and `/smh-clean-code-audit`'s remainder.

**Lenses: 5/5 ran, all `ok`, none dead, none `n/a`** (`review_mode: full`, `lens_budget:
standard`). The Literal-Correctness lens reports a **truncated pass** — 20 of 46 files, the cap
working as designed; the 26 withheld are generated door mirrors and artifacts, named in its
output. It spent its one earned top-up on the SOP to verify a test's precondition, and confirmed
it. Raw floor from the engine: **CONCERNS**.

**Why PASS.** Every gate green on the changed set; every acceptance item evidenced by a named
assertion; two criticals, ten importants and the remainder all fixed test-first; three mutation
sweeps with zero survivors. Nothing is left above noise.

### Findings

All `applied`, RED first: rows 1–14 in `7f83358`, rows 15–24 plus #11/#13 in `028e6cf`, and two vacuous-case tightenings the third sweep forced in `effc293`.

| # | file:line | Sev | Failure scenario | Disp |
|---|---|---|---|---|
| 1 | `jira_feed.py` `open_actions` | **critical** | A `# PC: …` comment inside a ```bash block in `## Your Actions` reads as a heading, ends the section, returns `[]` (not `None`, so no refusal) → **ticket closes over owed operator work**. 26/92 existing walkthroughs carry that shape. Reproduced live. | applied |
| 2 | `jira_feed.py` `open_actions` | **critical** | A doc quoting `## Your Actions` inside a fence wins the heading match; its ticked example rows return `[]` and the **real section below is never read**. | applied |
| 3 | `label_tasks.py` `set_labels` / tests | **critical** | The board-**write** path had no coverage at all — no `--apply`, no acli stub. A mutant discarding the computed label set and writing the ticket's existing labels back **survived 78/78**. | applied |
| 4 | `jira_feed.py` `cmd_finish` | important | `user-tasks` added on hold, **never stripped** on the clean close → the `labels = user-tasks` filter accumulates Done tickets and the signal decays to noise. | applied |
| 5 | `jira_feed.py` `cmd_finish` | important | Exit `2` overloaded onto two **board** failures, while its docstring and both close-out tables define `2` as "the artifact is wrong, nothing was written" → the agent hunts a defect in a walkthrough that is fine, forever. | applied |
| 6 | `jira_feed.py` `cmd_finish` | important | A held `finish` **stacked** a new comment per re-run — and re-running is the designed happy path. N near-identical comments, none marked current. | applied |
| 7 | `jira_feed.py` `cmd_finish` | important | A failed comment post returned early, **skipping the label and the ladder** → the ticket is held and says nothing about why: the exact loss the verb exists to prevent. | applied |
| 8 | `jira_feed.py` ladder | important | An unverifiable read-back (`view_fields` → `None`) was read as "did not move" → the ticket transitions a **second** time to a column nobody asked for, then reports "no review column on this board" — false on both counts. | applied |
| 9 | `jira_feed.py` ladder | important | A ticket already at `In Review` was dragged **backwards** to `Awaiting Review`. | applied |
| 10 | `jira_feed.py` `open_actions` | important | Continuation lines dropped, while `smh-quick-dev.md:320` publishes *"Continuation lines indented under it ride along"* as a **machine contract**. | applied |
| 11 | `jira_feed.py` `open_actions` | important | Three more fail-opens: an empty `- [ ]`, a **second** `## Your Actions` section, and a `###` sub-heading ending the section. | applied |
| 12 | `label_tasks.py` `gate_bmad` | important | `--mode story` provably **inert** on `plan`: the gate refused on the very type the flag exists to override, handing the operator back to the command they came from. | applied |
| 13 | `label_tasks.py` `gate_task` | important | `gate_bmad` hands a Subtask parent here saying "a Subtask and its Subtasks are Task work"; this **accepted** it, then died on "no children". Nothing nests under a Subtask. | applied |
| 14 | `label_tasks.py` `_ASCII_FOLD` | nitpick | Task-mode console printed `[NO-STORY] no plan` — two names for one verdict, and "story" is the word the mode exists to say does not apply. | applied |
| 15 | `label_tasks.py` `find_task_plan` | important | **Rung 2 is unreachable in the planner's own flow.** It scans `repo/_artifacts`, but `/smh-plan-task` commits each plan to that *lane's* branch/worktree — never to the checkout the labeller reads. Found independently by two lenses. | applied |
| 16 | `label_tasks.py` `ground_child` | important | Compounding #15: `story_branch` matches on the **ticket key**, so rung 1 fires for every planned lane, whose branch carries only `_artifacts/` — stripped by `source_paths` to **zero** source paths. Authority reads `branch-diff` on an empty set, and an empty touch-set is disjoint from everything → **manufactured 🟢** on the primary use case. | applied |
| 17 | `smh-quick-dev.md` Step 1.5 | important | The batch re-arm test names a commit **no artifact records** — the comparison has no right-hand side, so an agent following it literally declares the plan unchanged. | applied |
| 18 | `smh-plan-task.md` Step 5 | important | The approval quote is committed but **never pushed**, and no tree is named — the artifact that unlocks the batch path can sit local in N worktrees. | applied |
| 19 | `label_tasks.py` `mark_umbrellas` | suggestion | Runs in **task mode too**: a Subtask summarised `2.1` beside `2.1.1` becomes an umbrella — no verdict row, **no label write at all**. Silent exclusion is the failure this engine exists to prevent. | applied |
| 20 | `label_tasks.py` `cmd_check` | suggestion | Gained an unconditional board round-trip and a **new exit 2**, breaking the `0`/`1` contract both command docs publish, purely to choose one word in one message. | applied |
| 21 | `jira.md` guardrail 4 | suggestion | The transition table is declared closed, but the ladder writes `Awaiting Review`/`In Review`, which it does not carry. | applied |
| 22 | `task_preflight.py` | suggestion | Requires a walkthrough but not the `## Your Actions` section, so `finish`'s refusal fires only **after** the merge has landed. | applied |
| 23 | `label_tasks.py` `cmd_plan` | suggestion | Mode wiring untested at the entrypoint; the console-label mutant (NF13) is the one live sweep survivor. | applied |
| 24 | `cmd_finish` / `set_labels` | suggestion | `finish` never re-reads its comment and label writes, though acli exits 0 on writes it did not perform (`swallow`); stripping the last managed label sends `--labels ""`, verified only against the stub. | applied |

Two lens claims were **refuted** on verification and are recorded as such: `adf_text` is defined
locally at `label_tasks.py:169` and `parent_facts` does emit `type`, so the feared `NameError`
and mode-inversion do not exist.

### Step 0.7 — re-derivation against current `main`

- **Nothing moved.** `main` is still `61f2a24` — identical to this lane's merge-base — so no path,
  anchor, rule pointer or script this diff names was relocated under it. `merge-tree HEAD × main`
  is clean. No absorb was needed, which is why the reviewed sha and the built sha are the same.
- **True overlap with `main`: none** (empty intersection).
- **Sibling-lane landing order: `chore/SCC-156-lane-speed` is live and overlaps on 10 files.**
  `merge-tree` predicts exactly two conflicts, both in **generated/index** files
  (`.agents/.sync-manifest.json`, `_artifacts/_main/INDEX.md`) — resolved by regenerating, never
  by hand-merging. The eight prose/command files auto-merge. Neither lane depends on the other;
  whichever lands **second** absorbs `main` and re-runs `sync-agents`.

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `25/25 files passed`, exit 0 — receipt `gates/suite.json` @ `7f833584` |
| `workflow_lint --toolkit-only` | `0 error(s), 0 warning(s), 8 info`, exit 0 |
| `check_maps --depth3-only --strict` | exit 0 |
| Assertion evidence | `test_label_tasks.py` **88/88**, `test_jira_feed.py` **193/193**, both run **bare** |
| SOP currency | exit 0 |
| Link + anchor | clean for this diff; 2 dead rows in `_artifacts/_main/INDEX.md` are pre-existing history, **not** introduced here |
| Door parity | clean — both new commands and the rename carry all 4 doors; the retired command has 0 doors and no brain |

### Acceptance matrix

| Item | Verdict | The assertion that proves it |
|---|---|---|
| A1 one engine, two commands, both labels, comment on parent | satisfied | `--apply actually WRITES the computed set to the board` · `and the STRIP reaches the board too` · `the stamped verdict comment is POSTED, not just rendered` · `a task-mode stamp tells you to re-run /smh-label-tasks` |
| A2 `/smh-plan-task` plans the whole Task in one shot | satisfied | Every specified step is in the body, and its grounding claims are now true: `#15 it grounds on the PLAN committed to that lane's own branch` |
| A3 batch approval is recorded evidence | satisfied | The 000 clause, the four conditions restated where they are acted on, and `— recorded at <sha>` giving the re-arm test a real second operand (#17); Step 5 names the tree and requires the push (#18) |
| A4 open actions hold the ticket out of `Done` | satisfied | `a `#` comment INSIDE a fence does not end the section` · `a FENCED example never wins over the real section` · `closing clean STRIPS user-tasks` · `holding is its own exit code` · 30 `finish` cases total |
| A5 retirement complete, LAST | satisfied | `no stamp anywhere names the retired /cicd-parallel-check`; all 4 doors purged; every surviving mention is a rename note |
| A6 documented + green | satisfied | Receipts at `7f833584`; suite 25/25; two `[sop-ok]` opt-outs recorded below |

### Clean-Code Gate — PASS

`py_compile` exit 0 (4 files). Over the fix diff: **0** bare `except`, **0** hardcoded absolute
or `C:/` paths, **0** secret-shaped literals, **0** unowned `TODO`/`FIXME`, **0** bare `python`.
**15** blocks carry `SCC-155:` provenance plus the reason (§2A). §2C conventions: naming law,
prefix-is-permission, one-door-per-platform, generated-files-not-edited (no command body changed
in the fix commit, so no re-sync was owed), gates-ship-armed, and every-gate-has-an-exit all hold.
§2B is imported from Step 1 rather than re-walked, per this command's own instruction.

**Changes applied:** 14 findings fixed test-first in `7f83358`. Nothing was dismissed.

---

## Your Actions

- [x] **Install a review column on the SCC board.** Done — you created it and named it
      **`Review Required`**. It now leads `finish`'s ladder, which turns the no-column
      fall-through from the LIVE path into the corner case it was always meant to be.
      `--review-status` overrides the whole ladder, so a later rename on the board is a flag on
      one invocation rather than an edit here and a release.
- [x] **Run the memory audit.** Done. Those rows were **doubly** stale: they named
      `/sudo-parallel-check`, a name SCC-63's naming law retired *before* this lane renamed it
      again. The lesson still bites, so it was a mechanical repair rather than a retirement —
      the rename history is recorded, both current commands are named, and the store now says
      `quick-dev` has a second writer. Floor 46/46; index 18,485 / 25,600 bytes.
- [x] **The ten deferred findings.** Rolled into this ticket on your ruling; no follow-on exists.
      All applied test-first — every row in the findings table above reads `applied`.

Nothing is owed. The boxes are ticked rather than the section deleted, on purpose:
`jira_feed.py finish` reads this section, and an absent one is a refusal, not a pass — which is
this lane's own cluster C, applied to itself.

### Still worth your eye at close-out — not blockers, and not owed work

- **Landing order against `chore/SCC-156-lane-speed`.** Live, and it overlaps this lane on 10
  files. `merge-tree` predicts two conflicts, both in generated/index files
  (`.agents/.sync-manifest.json`, `_artifacts/_main/INDEX.md`) — resolved by **regenerating**,
  never by hand-merging. Whichever lands second absorbs `main` and re-runs `sync-agents`.
- **`Review Required` is asserted, not observed.** No ticket sits in that column yet, so the exact
  status string is pinned by test and by your word, not by a live transition. The first genuinely
  held close-out proves it; if the string is off, the ladder falls through, the `user-tasks` label
  still carries the signal, and `--review-status` fixes it with no code change.
