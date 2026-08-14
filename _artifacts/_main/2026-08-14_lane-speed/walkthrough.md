# Walkthrough — SCC-156 + SCC-159 (one lane, one landing)

**Branch** `chore/SCC-156-lane-speed` off `main` @ `61f2a24` · worktree `.claude/worktrees/lane-speed`
**Operator ruling (2026-08-14, verbatim)**: *"do SCC-156 and its sub task in the same working tree
just one push. one story then the other. we need to pick up the pace."* — SCC-156 worked to
completion first, then SCC-159. Lane key / `--expect-key`: **SCC-156**.

Plan + self-audit (verdict **GO**, 7 findings baked in): [implementation_plan.md](implementation_plan.md).

---

## Task Checklist

### SCC-156 — sweep + suite speed

- [x] **S1 · `--case` block filter** (ticket item 1, acceptance A3) — `_harness.py` gains
      `Cases.block(label) -> bool` and `--case <substring>`, plus a third exit code.
  - The guard is an `if`, not a context manager: these files are sequential inline
    `with TempDir():` blocks, and a CM cannot skip its own body — `__enter__` returning False
    still runs everything under it.
  - **Exit contract pinned** (audit F1): `0` matched-and-passed · `1` matched-and-failed ·
    **`3` the filter selected nothing** — typo'd label, unwired file, or a matched block that
    ran zero checks. A sweep reads non-zero as "killed", so a vacuous green had to be made
    impossible to mistake for a result.
  - Wired **39 blocks** into `test_git_hooks.py` and **25** into `test_task_preflight.py` by a
    tokenize-based transform that never re-indents multi-line string interiors (a re-indented
    stub source would have silently changed fixture data while every count still matched).
  - ⚠ **The transform's own catch**: five `test_task_preflight` blocks defined helpers
    (`with_secondary`, `ADIR`, `stamp_and_verdict`) *inside* the block that introduced them, so
    running one block alone died with `UnboundLocalError`. Found by running **every block solo**
    before trusting any label (audit F2), fixed by hoisting those fixtures to module level.
- [x] **S2 · targeted-kill + width doctrine** (item 2, acceptance A6) —
      `.agents/rules/tests-must-gate-for-real.md` § Mutation Testing.
  - Recon finding that changed the work: **the closing-green mandate did not exist in the rule.**
    A6 protects a sentence that was only ever in a scratchpad sweep script, so this lane *writes*
    it rather than preserving it.
  - Added: the three-outcome read of a targeted kill (non-zero killed · **0 = re-run the full file
    before believing a survivor** · **3 = sweep error, never a kill**), the ban on parallelizing
    the mutant loop, WIDTH mutants as a first-class technique, and the mandatory closing full-file
    green after byte-identical restores.
- [x] **S3 · parallel `run_all.py`** (item 4, acceptance A2) — `ThreadPoolExecutor` over the same
      per-file subprocesses; `--jobs N` (default CPU count), `--serial` escape hatch.
  - `ex.map` yields in **input order**, so the transcript stays alphabetical however the children
    finish — a transcript that reshuffles run to run cannot be diffed against a previous one.
  - The CI invocation string is unchanged and still bare; `test_main_write_gate_ci.py:93` pins it.
  - `--jobs 0` exits **2** rather than being coerced: a caller who typed it believes something
    untrue about the run.
- [x] **S5 · the four one-sentence command fixes** (item 6) + the `--case` consumers (item 3)
  - **6a** `smh-quick-dev` Step 3 — **stamp-first**: the receipt run IS the suite run; never
    `run_all` bare "to check" and then again through the writer. A red receipt is the mechanism
    working.
  - **6b** `smh-code-review` Step 3 — deleted the false sentence claiming an absorb
    auto-invalidates the receipt. It is false because freshness is a **TREE** comparison
    (`wf_common.same_tree` → `git diff --quiet`), not a sha comparison, so a no-op or
    artifacts-only absorb leaves the receipt valid. Replaced with the ONE-re-stamp rule.
    The **same stale claim** at `smh-merge-multiple-workingtrees.md:198` ("a doc-only absorb keeps
    the Verdict valid") was corrected in the same commit — SCC-154 had already disproven the
    doc-only exemption in the sibling file and left this copy behind.
  - **6c** `smh-close-task-merge-tree` — under a code-fresh verdict, **cite** the review's
    link+anchor and SOP sweeps instead of re-walking them; the armed commit-msg gate and CI at the
    landing sha remain the nets.
  - **6d** `smh-merge-multiple-workingtrees` — the final lane's 4b and Step 5's combined gate skip
    one run when `wf.same_tree` says the trees are byte-identical; unknown sha ⇒ run both.
- [x] **S6 · close-out overlap (item 7) + verify-wave grouping (item 8)**
  - Item 7: push the CI gate ref, then draft the merge summary and Dev Record **during** the ~50 s
    wall. The token mint, the push and the Jira transition stay strictly post-green — the TTL
    ordering is the reason that sequence exists.
  - Item 8: step-02 groups findings sharing `file:line` **and** claimed behavior into ONE
    verification query, as **query-fan-in / result-fan-out** — N findings → 1 query → N indexed
    results. Both engine invariants preserved explicitly: the **raw pre-dedupe count** still feeds
    the self-gate, and the **by-index join** still holds. Additive only (audit F7:
    `test_review_engine.py:397-443` pins step-02's sentences).
- [ ] **S4 · split the whale** (item 5)
- [ ] **S7 · mutation sweep over the new machinery** (first live targeted-kill run)
- [ ] **S8 · template-repo fixtures** (item 9)
- [ ] **S9 · re-measure every baseline** (A1, A2, A5)

### SCC-159 — merge-gate residue (the 3 items that survived the wontfix ruling)

- [ ] **S10 · pins + width mutants FIRST** (compound C3's sequencing, carried from SCC-154)
- [ ] **S11 · stuck-landing early warning**
- [ ] **S12 · ff-variant incident coherence**
- [ ] **S13 · incident:incident policy**

---

## Evidence

### A3 — `--case` zero-match exits non-zero (C3)

RED first. `test_suite_runner.py` written before `Cases.block` existed:

```
-- 2/16 passed --
FAILED: CASE · unfiltered runs every block, CASE · unfiltered prints no filter note,
CASE · --case runs only the matching block, CASE · the filtered tally counts only what ran,
CASE · match is case-insensitive, CASE · match is a substring of the label, not the whole label,
CASE · a typo'd label exits 3, CASE · the zero-match message names the filter,
CASE · zero match runs no cases at all, CASE · a file declaring no blocks exits 3 under a filter,
CASE · a matched block running zero checks exits 3, CASE · a sibling block with a real case still
exits 0, CASE · a failing filtered case exits 1, not 3, CASE · the FAILED line still names the case
```

⚠ **The first RED was 5/16 and three of those passes were vacuous** — they matched on the absence
of a string in a traceback, so a crashing harness scored them green. Every one was tightened to
require positive evidence (`rc == 0 and "-- 4/4 passed --" in out and …`) before the mechanism was
written; the honest RED is the 2/16 above, and the two remaining passes are controls (an unwired
file still runs green unfiltered; an unfiltered failure is still exit 1).

GREEN after `_harness.py`:

```
-- 25/25 passed --      (16 CASE cases + 9 RUNALL cases)
bare exit: 0
```

Zero-match, live:

```
-- 0/0 passed --
-- filter 'NOSUCHBLOCK': matched 0/3 blocks --
NO CASES RAN: no block matched — this is a filter error, not a result.
rc=3
```

### F2 — every block runs solo (the proof a sweep's labels can be trusted)

First run, before the fixture hoist — **5 of 25 blocks failed solo**, all `UnboundLocalError`:

```
--- test_task_preflight.py :: SCC-154 A1 · verdict RESOLUTION …  (rc=1)
    "--root", str(repo / ADIR), "--cwd", str(repo),
UnboundLocalError: cannot access local variable 'ADIR' where it is not associated with a value
```

After hoisting the shared fixtures to module level:

```
every block passes solo
```

…and the timings are the point of the whole ticket — the A1 verdict block runs in **21.8 s** and
the A2/A4 blocks in **1.3 s**, against the 105 s the full file costs:

```
[ok ]   9.2s  rc=0  -- 8/8 passed --    SCC-154 A0 · conjunct killers …
[ok ]  21.8s  rc=0  -- 19/19 passed --  SCC-154 A1 · verdict RESOLUTION …
[ok ]   1.3s  rc=0  -- 1/1 passed --    SCC-154 A2 · a SKIP spares the SUITE only (C4)
[ok ]   1.3s  rc=0  -- 1/1 passed --    SCC-154 A4 · reader-side dirt exemption (C6)
```

### Case-count conservation across the block wiring

| File | Before | After |
|---|---|---|
| `test_git_hooks.py` | `-- 114/114 passed --` | `-- 114/114 passed --` |
| `test_task_preflight.py` | `-- 145/145 passed --` | `-- 145/145 passed --` |

### Toolkit lint after the command-body + doc edits

```
-- 0 error(s), 0 warning(s), 8 info --      (the 8 info are pre-existing BOMs on vendor testarch-* files)
LINT EXIT: 0
```

### Door parity

`/smh-sync-agents` run after the command edits: 32 antigravity workflows · 18 generated launcher
skills · 54 `.claude/skills` dirs · 53 `.opencode/commands` · global caches mirror-exact. The
engine's `.claude/skills/code-review-engine/steps/step-02-verify.md` mirror moved with its master.

### A2 — run_all wall, serial vs parallel

_(pending — re-measured at the landing sha; the first run was killed by a session teardown)_

---

## Code Review

_(appended by `/smh-code-review`)_

## Your Actions

_(filled at hand-back)_
