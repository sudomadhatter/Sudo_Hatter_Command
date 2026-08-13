---
IsArtifact: true
ArtifactMetadata:
  title: SCC-126 — the literal-correctness lens — walkthrough
  type: walkthrough
  date: 2026-08-13
---

# SCC-126 — The literal-correctness lens, capped in the autopilot

Lane: `chore/SCC-126-literal-lens` · tree `.claude/worktrees/scc-126-literal-lens` · cut from
`main @ 36e1ffe` · implementation commit `7b14f91`.

**First of three parallel lanes.** The parent spec (SCC-116) planned 126→127→128→129 sequentially.
A file-overlap audit on 2026-08-13 found the only true collision between 126/127/128 was
`cicd-code-review-AP.md`, wanted by both this lane (cost cap) and SCC-128 (rewire). The operator
approved moving that file's rewire **into this lane**, which made all three disjoint and let them
run at once. The transfer is recorded on both Jira tickets, not just here.

## Task Checklist

- [x] **Step A — RED.** 17 new cases in `test_review_engine.py`, written in that file's own
      discipline: each binds a *relationship* (a table cell, an anchored line) rather than a
      vocabulary, and each ships a counter-example proven to make it go red.
  - ⚠ One of those guards was itself vacuous on first write — see *What fought back*.
- [x] **Step B — GREEN.** The lens lands in `step-01-review.md`; `SKILL.md` lens arithmetic follows.
- [x] **Step C — the transferred scope.** `cicd-code-review-AP.md` rewired onto the engine in
      capped mode; SOP staged in the same commit.
- [x] **Step D — sync + full gate.** `sync-agents.ps1`, then both gates bare.
- [ ] **Step E — stopwatch.** ⛔ **Closed by operator ruling, not run.** See below.

## Evidence

| Acceptance item | Assertion that proves it | RED | GREEN |
|---|---|---|---|
| A 5th lens exists, always runs, is wired to the hunter contract, and is pack-primed | 3 cases binding the table row's `Runs when` / `How` / pack cells | absent — `'\| **Literal-Correctness Hunter** \| ...' not present` | pass |
| The discipline reaches the lens as prompt text, not narration | 3 cases anchored `^>` (blockquote = what is sent) | absent | pass |
| The lens is bounded four ways | 5 cases: diff-scoped · empty-patch early-exit · early-exit scores `ok` · 20-file cap · ~9k spill | absent | pass |
| Mode is defined once and callers only name it | 4 cases incl. the `capped` and `full` mode-table rows | absent | pass |
| Lens arithmetic agrees in both files that state it | `4/4 never 4/5` pinned in `step-01` **and** `SKILL.md` | the old `3/3` pin failed as designed | pass |

```
RED    python3 .agents/scripts/tests/test_review_engine.py   -> exit 1, 391/440, 49 failures
       every failure named a real absent string, e.g.
       "steps/step-01-review.md: '...' not present, so the proof would be vacuous"
       (read as: the assertion failed, not the setup)
GREEN  python3 .agents/scripts/tests/test_review_engine.py   -> 440/440 after sync
```

**Lane gate, bare (no pipes — a piped gate reports `tail`'s exit code), at `7b14f91`:**

```
python3 .agents/scripts/tests/run_all.py                -> 21/21 files, 1383/1383 cases, exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only -> 0 errors, 0 warnings, 8 info, exit 0
```

Case total 1329 → 1383, exactly additive: this lane displaced no existing test.

## Suite Ledger

| scope | command | result | why this run |
|---|---|---|---|
| engine guard | `test_review_engine.py` (bare) | 391/440 → 440/440 | the RED, then the GREEN |
| full enforcement suite | `run_all.py` (bare) | 21/21 files, 1383/1383, exit 0 | lane gate |
| toolkit lint | `workflow_lint.py --toolkit-only` (bare) | 0/0, exit 0 | lane gate |

## What fought back

- **⭐ The guard caught a vacuous guard of its own.** The pack-priming check's counter-example
  string was `+ the hunter contract | yes |` — which is **not unique**: it occurs first on the
  **Edge Case Hunter's** row. `.replace(old, new, 1)` therefore mutated a different lens, left the
  row under test untouched, and the check passed against content it was supposed to reject. This
  is precisely the class SCC-125's F3 recorded (*a guard on the description of a rule is not a
  guard on the rule*), and this time the file's own anti-vacuity rows caught it during the build
  rather than a reviewer catching it after. Counter-example now names the discipline text, which is
  unique to the new row.
- **Two audit findings were baked in before any code was written**, both of which look like a pass
  if you get them wrong:
  - *F1* — the engine's "subagents unavailable" branch writes prompt files and returns. That is
    right for an interactive caller who can paste them back; **headless it is a review that
    silently never ran**, and the autopilot would read it as clean. The AP caller now runs every
    lens inline and sequentially in that runtime, and records that it did.
  - *F6* — the empty-patch early-exit had to be scored `ok`. Scored `dead` it raises
    `severity_floor` to CONCERNS on **every clean diff forever**; scored `n/a` it reports a
    fully-run review as partially skipped.
- **The `3/3` pin was load-bearing.** Adding a lens changes an arithmetic sentence in two files;
  the existing pin failing was the signal that the second file (`SKILL.md`) had no guard of its own.
  It has one now.

## Step E — the stopwatch, and why there is no number

⛔ **Not run. Closed by operator ruling on 2026-08-13**, quoted in the plan: *"we already did this,
it passes the stopwatch test, we are developing and switching, it is much more accurate."*

That applies the SCC-124 amended acceptance rule — *a better process that is more accurate wins if
the two are close in time* — a second time, to the same trade, by the authority that amended it.
SCC-124 recorded the original `≤` bar as **not met** (337.6 s vs 304.7 s, +10.8 %) and ruled GO on
accuracy; this lens is the epic's largest single accuracy gain.

**The cost of that ruling, stated rather than buried:** there is no measured wall-clock for the
5-lens engine, and the attribution window closes permanently once SCC-127's verify wave lands — no
later measurement can separate this lens's cost from that wave's. The four caps in Step B are what
bound the risk, and `capped` mode binds it hardest where it would multiply overnight.

## Your Actions

- Landed on `chore/SCC-126-literal-lens` (`7b14f91`), pushed, tree clean.
- **Landing-order dependencies for the sibling lanes**, both real:
  1. **SCC-128's resurrection lint needs this lane on `main` first.** That lint scans every command
     for `bmad-code-review`; the AP file was this lane's to clean, so if the lint arms first it goes
     red on a file SCC-128 may not edit.
  2. **`cicd-code-review-AP.md:9` carries `ap_reconciled: <sha>`** pinned to `cicd-code-review.md`,
     which SCC-128 rewrites. Whichever lane lands second owes a re-diff and a restamp of that one
     frontmatter line — for SCC-128 that is its **only** permitted touch of the AP file. The lint
     warns rather than errors, so this will not block a merge; it will just quietly go stale.
- Still owed: `/smh-code-review` (Step 4 gate) and then `/smh-close-task-merge-tree`, which is
  yours — invoking it is the merge sign-off.
