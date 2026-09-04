# SCC-271 — walkthrough

**Lane:** `chore/SCC-271-jira-feed-write-truth` · **Ticket:** SCC-271 (Subtask, Part B of SCC-262)
**Tree:** `.claude/worktrees/SCC-271-jira-feed-write-truth` · **Base:** `origin/main` @ `7c5721c`
(originally cut at `9d7863b`; `origin/main` absorbed at close-out — see *Landing order* below)
**Lane type:** `/smh-quick-dev` (TASK — `lane_qualify` refused the light lane on toolkit paths)
**Verdict:** no LLM review ran — this is a `/smh-quick-dev` lane, so the deterministic gates ARE
the verdict, and the preflight said so out loud: *no review Verdict line in this task's own
walkthrough - the full gate runs*. All three ran, green, at the landing sha.

---

## What shipped

**`jira_feed.py` had two defects on the same surface: it wrote to a ticket correctly and then
misreported what it had done.** Both were hit in one session, on SCC-269's own record-filing, by
following the ceremony exactly as written.

### 1. `index-row` called its own correct write "data loss" — and exited 2

Filing SCC-269's row onto the fresh rolling ticket printed:

```
⛔ SCC-262's description was REPLACED and the read back is MISSING 1 line(s) that were there before:
    (empty - this cycle has taken no work yet)
  … Restore the ticket from the text above before doing anything else - this is data loss, not a
  formatting difference.
```

The INDEX was intact. Nothing was lost.

**Three correct lines producing a wrong answer:** `cmd_index_row` snapshotted every prior line into
`keep` (`:2792`); `index_append` then deliberately dropped the `(empty …)` placeholder (`:2744`) —
its documented job; and the read-back falsified the result against the **pre-drop** snapshot
(`:2822`). The guard asked *"did every line survive?"* when the command's own contract is *"every
line survives **except** the placeholder I am replacing."*

**Why it mattered more than a bad message.** Exit 2 — a caller chaining on `&&` reads a good write
as failure. The text instructs the reader to undo a correct write. And it fired on the **first row
of every fresh rolling ticket**, which is this command's most predictable use. This guard is the one
place `work-consolidation.md` puts a *mechanism* instead of a policy, because real index loss
(SCC-164's Part E row) is silent and unrecoverable — **a guard that cries wolf on first use is a
guard being trained out of the system.**

**Fixed** by falsifying against what `index_append` *composed* (`after`) rather than against
everything that was there. The teeth are unchanged: a line composed into `after` that does not come
back is still loss, still exit 2, still named. The deliberate replacement is now **reported** —
`· replaced the INDEX placeholder …` — rather than swallowed, because a deletion the operator cannot
see is the same class of problem the guard exists to catch.

*Confirmed both ways in the field before a line was written:* it fired on SCC-262's Part A row, and
ran clean (`67 prior line(s) intact`) on Part B once a real row existed.

### 2. `--append-new` manufactured the exact state `check` calls a defect

`find_devrecord` already filters by story id, so `prior` is non-`None` **only when the id matches**.
That made "one id, two records" the flag's *only reachable effect* — the state `record_story_id`'s
own docstring names as *"the failure SCC-49 wrote `check` for"*. The legitimate two-records case
(two lanes, two ids) never needed the flag: `prior` is `None` there and it creates anyway.

**The system already knew.** Seven command bodies plus the SOP say *"never `--append-new`"* —
`smh-close-task-merge-tree.md:553,:600` · `smh-quick-dev.md:474` ·
`smh-merge-multiple-workingtrees.md:339` · `cicd-close-story-merge-tree.md:369` ·
`cicd-quick-dev.md:376` · `cicd-merge-epic-workingtrees.md:249` ·
`workflows_testing_SOP.md:2204`. A ban repeated by hand in seven places and enforced in none.

**Fixed:** refused over a matching prior — exit 2, naming the remedy. Seven prose bans became one
guard. `--help` now states the ban instead of advertising the footgun.

**Not a defect, recorded so it is not re-litigated:** the duplicate record also lacked its `Outcome`
line. That was operator error in the invoking call (no `--outcome` passed), not a code fault.

---

## Assert-first — the RED proof

Written and **run before the fix**, exactly as `/smh-quick-dev` requires:

```
--case "SCC-271 index-row"   -> 4/7 passed
  FAILED: the first row on a FRESH index exits 0
          ...and does NOT cry data loss over the placeholder
          ...and the deliberate replacement is REPORTED, not silent

--case "SCC-271 devrecord"   -> 3/6 passed
  FAILED: --append-new over a MATCHING prior is refused (exit 2)
          ...and the ticket still carries exactly ONE record
          ...and the refusal names the remedy
```

All four controls were green **before and after** — the teeth case (a genuinely dropped line still
exits 2 and names it), `--append-new` with no prior, and a second lane under a different id.

### ⚠ One existing assertion was INVERTED, not deleted

`test_jira_feed.py:631` read *"`--append-new`: opts out of the one-record rule"* (exit 0, two
comments). It **pinned a footgun**. It now pins the guard, with a comment saying why, and mutant
**M4** proves the new form fails without the fix. Flagging it because editing a test to match new
behaviour is precisely how a vacuous green gets made.

## Evidence

```
test_jira_feed.py (full)                    -> 415/415 passed
mutation_sweep (5 mutants)                  -> sweep clean: 5/5 killed by their declared case
                                               restore verified, git diff --quiet 05833ee clean
run_all.py                                  -> 48/48 files passed
workflow_lint.py --toolkit-only             -> 0 error(s), 0 warning(s), 8 info
lane_qualify (intent + real diff)           -> TASK, both times (toolkit paths — correct lane)
```

**Re-run bare at the LANDING sha, after `origin/main` was absorbed** — the gates above ran on the
pre-absorb tree, which is not the tree that merges:

```
run_all.py                  -> exit 0, 48/48 files passed
workflow_lint --toolkit-only-> exit 0, 0 error(s), 0 warning(s), 8 info
check_maps --depth3-only --strict -> exit 0, silent
task_preflight              -> exit 1 (the one WARN is the worktree Step 5 removes)
                               VERDICT: clear to close out and merge · LANE: LOCAL · GATES: ARMED
```

Run **bare, never piped** — a pipe hands back `tail`'s exit code, so a red gate reads as green.
That is why each line above carries its own `exit 0` and not just its last line of output.

The five mutants, each killed by the one case that pins it: revert B1 · gut B1's teeth the other way
(bless a real drop) · silence the replacement report · revert B2 · **over-fire** B2 (refuse even with
no prior, breaking the second-lane path).

## The audit earned its keep

`/smh-self-audit` returned **GO** with three findings, all baked into the plan before any code:

1. **HIGH** — `sop_currency.py:77` gates `.agents/scripts/*.py`; the plan had said "no SOP edit
   expected". **The first commit was rejected by the armed gate, exactly as predicted.** The SOP
   genuinely needed the clause — a command that used to succeed now exits 2 — so `[sop-ok]` would
   have been the wrong dodge.
2. **HIGH** — the plan had no `## Declared Change Set` block, so `/smh-code-review`'s drift check
   would have passed vacuously. Added; it parses.
3. **MED** — the landing-order dependency below.

## ⚠ Landing order — SETTLED

**SCC-269 landed first** (PR #52, `7c5721c`), then this lane absorbed it. Both lanes appended a row
to `_artifacts/_main/INDEX.md` for the same date, so the absorb **conflicted on exactly that file** —
predicted here before either lane opened a PR, and it happened exactly as written.

**Resolved by keeping BOTH rows**, newest first (SCC-271 above SCC-269), matching the table's own
ordering. Counted rather than eyeballed: each side carried **176** rows over a common **175**, and
the resolution carries **177**. `INDEX.md` was the only file the two lanes both touched.

Dropping either row would have been the silent, unrecoverable index loss this ticket exists to stop —
the same class as SCC-164's Part E row. Recording the arithmetic because *"I kept both"* and
*"I kept both and nothing else moved"* are different claims, and only the second one is checkable.

## Your Actions

- [x] The merge itself — lands via this branch's PR.
- [x] The fixes, tests, mutants and gates — done and evidenced above.
- [x] The `_artifacts/_main/INDEX.md` conflict — resolved on this lane, both rows kept, counted.

Nothing is owed. **`GEMINI.md`'s three model-specific rules** — surfaced by the sibling lane, not by
this one — are already filed as **SCC-279** and are not this ticket's work.
