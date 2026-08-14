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
    The **same stale claim** at `.agents/commands/smh-merge-multiple-workingtrees.md:198` ("a doc-only absorb keeps
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
- [x] **S4 · split the whale** (item 5) — `test_task_preflight.py` divided at its SCC-146 seam:
      107 cases / 58.04 s + 38 cases / 41.98 s, **145 conserved exactly**, shared builders in
      `_pf_fixtures.py` (not `test_*`, so the runner does not collect it). Every block still
      passes solo in both halves.
- [x] **S7 · mutation sweep over the new machinery** — 10 declared mutants, **10/10 KILLED** by
      their named cases, one pass, zero re-aims; four of them WIDTH mutants. Closing green 25/25.
      ⚠ Its first run is the evidence for the exit-3 rule: against an **unwired**
      `test_suite_runner.py`, nine of ten came back `SWEEP ERROR — matched nothing (exit 3)`.
      Under the old two-outcome reading every one of those would have counted as a kill and the
      sweep would have certified nothing while reporting 10/10.
- [~] **S8 · template-repo fixtures** (item 9) — **DROPPED at the operator's word**
      (2026-08-14, "thats looks good this works for me"), after A2's post-split number came in at
      71.74 s against a ≤ 60 s target. This was the remaining lever for that gap; not pursued.
- [x] **S9 · re-measure every baseline** (A1, A2, A5) — below.

### SCC-159 — merge-gate residue (the 3 items that survived the wontfix ruling)

- [x] **S10 · pins + width mutants FIRST** — the C3 constraint honoured: the false-red controls
      (`INC5` epic/main absorbs, `G6` bare incident, `G6d` already-landed content) exist in the
      same change and were run against the OLD behaviour before either narrowing landed.
- [x] **S11 · stuck-landing early warning** — `task_preflight.check_stalled_landing()`. Severity
      splits on evidence quality: fresh `--fetch` ⇒ **error**, no fetch ⇒ **warn** (the
      comparison is only as good as the last fetch), and `--accept-unpushed-main` is the
      auditable offline exit that prints itself back into the output.
- [x] **S12 · ff-variant incident coherence** — the backstop's incident carve-out narrowed from a
      **skip** to a **note**: the lane's own commits are still never judged, but the containment
      loop now runs for incident refs, closing the gap where a fast-forward escaped both gates
      precisely during an incident.
- [x] **S13 · incident:incident policy** — refused in both directions, placed ABOVE the incident
      wildcard (below it, it is dead code — the M-B2 shape one arm later).

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

### A2 — run_all wall, serial vs parallel (MEASURED, this Mac, cpu_count = 10)

| Run | Wall | Result |
|---|---|---|
| serial (`--serial`), pre-split | **186.23 s** | `25/26 files passed` |
| parallel (default), pre-split | **101.67 s** | `25/26 files passed` — **target was ≤ 110 s ✓** |
| parallel, post-split, clean | **71.74 s** | `27/27 files passed` |

Both pre-split runs printed the **same summary line and the same failure**, which is the point:
parallelism changed the wall and nothing else. (That shared failure was mine and the gate was
right — this lane's new `_artifacts/` folder had no INDEX row yet. `test_check_maps` is 27/27
with the row added.)

⚠ **A2's post-split target was ≤ 60 s and the honest measured number is 71.74 s.** The floor is
the slowest single file under contention: `test_task_preflight.py` is 58 s solo and slower with
ten workers competing for git subprocesses. The remaining lever is ticket item 9 (template-repo
fixtures) — see below; whatever it measures is what gets reported.

### A1 — replaying SCC-154's sweeps with targeted kills — ⚠ NOT COMPLETED

**Status: the replay did not produce a number, and this row is open.** The adapter imports
SCC-154's own mutant table verbatim (re-typing it would prove nothing), re-points it at this
worktree, and re-derives each mutant's BLOCK from its named case — necessary because
`test_task_preflight` has since been split and SCC-159 has since changed some of the very code
SCC-154 mutated. It ran for roughly ten minutes without emitting a result and was killed.

⛔ **And it left a mutant on disk**, which is the doctrine's own warning arriving live: the
restore lives in a `finally`, and `finally` does not run when the process is killed. Residue was
`strip_fenced`'s fence-length rule in `task_preflight.py` (the W2/M-B-class narrowing:
`len(marker) >= fence[1]` dropped) — a **mutated gate, committable**, exactly the SCC-144 shape.
Caught by `git status` immediately after the kill, restored from HEAD (every real change was
already committed), and verified: `git diff HEAD -- .agents/scripts/` is empty and the affected
block re-runs 19/19.

What A1 still owes: the two timed replays. What is already proven about the mechanism they were
meant to time is in the SCC-156 and SCC-159 sweeps above — 10/10 and 9/9 targeted kills, with
the per-block timings (21.8 s for the A1 verdict block against 105 s for the whole file) showing
the same ratio A1 asks to be demonstrated on SCC-154's table specifically.

### SCC-159 — the width sweep, and the hole it found

9 mutants, all narrowings. First pass **7/9**, and both misses were worth having:

- **W-P3 SURVIVED** — hardening the no-`--fetch` path into a hard error changed nothing any case
  could see, because **nothing covered the no-fetch WARN path at all**. The severity split was
  the whole point of D1 and it was untested. The case exists now and kills the mutant.
- **W-G3 was mis-aimed, not a hole** — dropping `incident:epic` from the allow arm does not
  refuse the absorb; it falls through to the incident wildcard and is allowed **as unknown**. Only
  `INC4`'s "no decline note" assertion — the classified-allow vs lost-to-unknown distinction the
  SCC-154 review added — can see the difference. Re-aimed there, it dies.

Re-run: **9/9 killed**. Closing green after all restores: `test_git_hooks` 126/126,
`test_task_preflight` 115/115.

---

## Code Review

_(appended by `/smh-code-review`)_

## Your Actions

_(filled at hand-back)_
