# SCC-271 — walkthrough

**Lane:** `chore/SCC-271-jira-feed-write-truth` · **Ticket:** SCC-271 (Subtask, Part B of SCC-262)
**Tree:** `.claude/worktrees/SCC-271-jira-feed-write-truth` · **Base:** `origin/main` @ `9d7863b`
**Lane type:** `/smh-quick-dev` (TASK — `lane_qualify` refused the light lane on toolkit paths)
**Verdict:** pending `/smh-code-review`

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

## ⚠ Landing order — read before absorbing `main`

**SCC-269 lands first.** Both lanes append to `_artifacts/_main/INDEX.md`. This lane's row had to be
written now (`check_maps` F2 fails the suite without it), so **the absorb after SCC-269 merges will
conflict on that file**. The resolution is **keep both rows** — SCC-269's `2026-08-22_scc-269-…` row
*and* this lane's `2026-08-22_scc-271-…` row. Dropping either is the exact index-loss class this
ticket exists to fix.

## Your Actions

- [ ] Merge **SCC-269** first (its PR), then this lane — the ledger conflict above resolves by
  keeping both rows.
- [x] The fixes, tests, mutants and gates — done and evidenced above.
