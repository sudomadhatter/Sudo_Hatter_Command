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
- [x] **S9a · re-measure A2 + A5** — done, table below (and re-measured again after the
      review fixes).
- [ ] **S9b · A1's two replay timings** — **NOT DONE**, root cause found, owed to the
      follow-on. Ticking this with S9a is what the review caught: one box cannot say
      "half of this is open".

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

**What A1 still owes, stated without substitution.** A1 has two halves and the load-bearing one
is *identical kill verdicts* on SCC-154's own 17 mutants — a targeted replay could hit ≤ 6 min
and still disagree with SCC-154 about which mutants died, and detecting that disagreement is the
whole reason A1 exists. **No ratio substitutes for it**, so the per-block timings this section
used to cite as consolation have been removed: they measure a different table and the review was
right that quoting them re-asserted the claim the row above had just withdrawn. What the other
sweeps do prove is that the *mechanism* works (10/10, 9/9, and 8/9 on the review fixes) — not
that SCC-154's table replays identically under it. That comparison is owed.

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

## Code Review (2026-08-14)

Verdict: CONCERNS @ cade70392b81151d01c20f4bdd4395462a2ff60d
Suite evidence measured at: `cade703` — 27/27 files, exit 0, bare and unfiltered.

**Scope.** The combined `origin/main...HEAD` diff for both tickets — 28 files, +3,746 / −2,175 —
covering SCC-156 items 1–8 and all three SCC-159 items.
**Method.** The house `code-review-engine`, `review_mode: full`, `lens_budget: standard`, five
lenses in parallel clean contexts, then an inline verify pass and a targeted-kill mutation sweep
over every fix.

### Lens degradation — reported, not silent

```
lenses_run:      5/5   (Blind Hunter: ok · Edge Case: ok · Literal-Correctness: ok (truncated,
                        see below) · Acceptance Auditor: ok · Test-Adequacy Auditor: ok)
lenses_na:       none
severity_floor:  CONCERNS
```

⚠ **All five lenses died twice before completing, and the cause was environmental, not the
review**: the machine slept mid-response, then the stream watchdog stalled at 600 s. Each was
retried per the engine's contract and all five ultimately returned real findings, so coverage is
complete — but the record should say that this took three rounds rather than one.

⚠ **The Literal-Correctness Hunter is a TRUNCATED pass and says so in its own first line.** It
received 18 of 28 changed files (the 10 withheld: `.sync-manifest.json`, the `.claude/` skill
mirror, the four `.opencode/` command mirrors, and the five `_artifacts/` files — all generated
or artifact). It then narrowed its *reported* subject further, to the five production files, on
my instruction when wall-clock ran out. It spent its one earned top-up on the `.claude/` skill
mirror and found it byte-identical.

### Step 0.7 — the blast radius, re-derived against current `main`

1. **Did anything this diff references move?** No. `origin/main` has not moved since this lane
   was cut — it is still `61f2a24`, which is also the merge-base. Nothing landed underneath this
   work, and the link+anchor sweep re-resolved every path the diff added (19 resolved, 0 broken).
2. **True overlap and merge result.** Overlap with what landed: **zero files**. `merge-tree`
   against `origin/main` is clean, so **no absorb was needed** and none was performed.
3. **Sibling-lane landing order.** `chore/SCC-155-label-tasks` is live and overlaps this lane on
   10 files. `merge-tree` between the two lanes says the four shared **command bodies auto-merge**;
   the only two conflicts are `.agents/.sync-manifest.json` and `_artifacts/_main/INDEX.md`, both
   **generated**. Whichever lands second regenerates them (`/smh-sync-agents`, and one INDEX row) —
   never a hand-merge. **There is no content dependency in either direction, so the order is free.**

### Findings

Five lenses returned ~50 findings. Six were graded `important` by more than one lens, or by one
lens with a live reproduction; those were fixed test-first in `cade703` and are the table below.
The remainder are real but non-blocking and are listed as deferred residue.

| # | file:line | sev | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `.agents/scripts/task_preflight.py:1093` | important | `--fetch` is passed, the fetch **fails**, and the landing check still hard-ERRORs on a comparison `check_sync` just warned was stale → exit 2, `VERDICT: BLOCKED`. The offline operator — the exact case the severity split exists for — is wedged on a phantom. Found by **3 lenses**, two with live reproductions. | **applied** — `check_sync` now returns whether the fetch succeeded; `main()` threads the outcome, not the flag |
| 2 | `.agents/scripts/git-hooks/pre-push-merge-backstop.sh:143` | important | `lane=claude/incident-*` matches the `claude/*` glob, so every `origin/epic/*` becomes a landing point. An epic-landed story lane riding inside a hotfix scores "landed" and ships to production through the one lane that goes straight to `main`. Measured, identical content: `chore/*` **REFUSED**, `claude/incident-*` **ALLOWED**. Found by **2 lenses**, both reproduced. | **applied** — ordered `claude/incident-*)` arm above `claude/*)`, the arm `integration_of()` already had |
| 3 | `.agents/scripts/tests/_harness.py:36` | important | A bare `--case`, `--case=`, or an empty value returned `None` = UNFILTERED. The sweep runs the whole file, prints no filter line, exits 0/1 — so a mutant that dies to **any** case is recorded as killed by a named case that never ran alone. Found by **all five lenses**. | **applied** — a lost label is now the same error class as a typo: exit 3, with a message naming the cause |
| 4 | `.agents/scripts/task_preflight.py:638` | important | `behind` was computed and never read: a **diverged** `main` was diagnosed as a stalled landing and prescribed `git push origin main`, which git rejects non-fast-forward. The stated rationale (`pull --ff-only` won't catch it) is false for divergence — that is the one shape it does catch. | **applied** — divergence gets its own diagnosis and its own remedy |
| 5 | `.agents/scripts/tests/run_all.py:71` | important | The ticket's **flagship deliverable had no killer case**: pinning `max_workers=1` left the suite 25/25 green, because every RUNALL assertion holds identically in serial. Two lenses verified live. Same for the stderr concatenation — deleting it kept the file green while a child's traceback vanished. | **applied** — causal concurrency pin (4 × 0.7 s at width 4 vs a 2.8 s serial floor) + a stderr case, both proven by mutation |
| 6 | `.agents/scripts/tests/test_task_preflight.py:299` | important | The false-red control asserted `"stalled landing" not in out` while the message says `STALLED LANDING` in caps — a **tautology**, absent whether or not the check fired. Only `code == 0` carried evidence. This lane wrote the rule banning exactly this, one block away. | **applied** — `not in out.lower()`, matching the sibling file that always did it correctly |

Two further sub-defects rode cluster 1's fix and are covered by the same block: a **behind-only**
`main` reported as "level with origin/main" (an INFO line asserting the opposite of the truth in
the commonest real state), and an **unreadable count** falling through to "? commit(s) ahead"
because the old `["?", "?"]` padding is never the string `"0"`.

### Mutation record for the fixes — 8/9, one reported survivor

Nine mutants, each the exact narrowing a lens applied by hand. Restore from byte-for-byte copies,
sha256-verified, `git status` printed at the end.

```
[R-CONC]   KILLED   the pool collapses to width 1 — the deliverable, silently gone
[R-ERR]    KILLED   a child's traceback is swallowed
[R-LOST]   KILLED   a bare --case goes back to meaning UNFILTERED
[R-EMPTY]  KILLED   an empty filter matches every block again
[R-BASES]  KILLED   incident lanes inherit the epic widening again
[R-FRESH]  KILLED   the severity split keys on the FLAG again, not the outcome
[R-DIV]    KILLED   divergence is misdiagnosed as a stalled landing again
[R-BEHIND] KILLED   a behind-only main is called 'level with origin/main' again
[R-PARSE]  ⚠ SURVIVED
restored byte-identical: True
killed 8/9 · survived 1 · defective 0
```

⚠ **R-PARSE survived and is reported rather than papered over.** The parse guard sits behind an
earlier `returncode != 0` check that dominates it: `git rev-list --left-right --count` either
fails (caught first) or prints two integers, so **no reachable input distinguishes the two**. That
makes it defensive code with no reachable case — a survivor no test can honestly close. Left in
place, named here, so the next reader does not mistake 8/9 for a missed kill.

### Gate results — every one run bare, real output pasted

| Gate | Result |
|---|---|
| **Enforcement suite** | `27/27 files passed`, **exit 0** — bare, unfiltered, after the last fix |
| **Toolkit lint** | `-- 0 error(s), 0 warning(s), 8 info --`, **exit 0** (the 8 info are UTF-8 BOMs on vendor `bmad-*` files, pre-existing) |
| **check_maps** | `--depth3-only --strict`, **exit 0** |
| **Assertion evidence** | 13 named `--case` runs green — 25 suite-runner, 19 git-hook, 17 preflight cases — plus the negative control: a mistyped label exits **3**, not 0 |
| **SOP currency** | **exit 0** with the SOP staged; **exit 1** with it removed from the same path set. Both halves proven — it can still fail |
| **Link + anchor** | **19 resolved, 0 broken**, exit 0 |
| **Door parity** | No command added, renamed or deleted. `/smh-sync-agents` re-run after the command edit: 32 workflows · 18 launcher skills · 54 `.claude/skills` · 53 `.opencode/commands` |

⚠ **One gate lied to me first, and the fix is worth recording.** `sop_currency.py --paths $CHANGED`
returned exit 0 — but **zsh does not word-split an unquoted variable**, so the gate received
`argc = 1`: one giant path string, and it checked nothing. I proved the arity before believing the
green and re-ran with `$(cat …)` expansion. The house memory
`zsh-does-not-word-split-gate-args` exists for exactly this, and the review command's own Step 0.7
warns about it in writing.

### Acceptance matrix — the ticket's own ACCEPTANCE block, item by item

| Item | Status | The assertion that proves it |
|---|---|---|
| **A1** replay SCC-154's 17-mutant sweep targeted ≤ 6 min, width sweep ≤ 2 min, **identical kill verdicts** | ⛔ **NOT MET** | No evidence exists. Root cause now known: `width_sweep.py` has no `def main(` and no `__main__` guard, so the adapter's split-before-`main` returned the whole file and `exec()` ran the entire sweep at import. Owed to the follow-on |
| **A2** `run_all` ≤ 110 s pre-split, **≤ 60 s post-split**; same summary line + exit semantics; `--serial` works; comparison run pasted | ⚠ **PARTIALLY MET** | Pre-split ≤ 110 s **MET** (101.67 s). Post-split **MISSED**: 68.57 s against ≤ 60 s. Summary-line and file-order identity **proven mechanically** (`diff` of both modes' summary lines and file order — identical), and `--serial` verified at 212.86 s vs 68.57 s parallel, both `27/27` |
| **A3** `--case` zero-match exits non-zero, with a test | ✅ **MET** | `test_suite_runner.py` — four named cases pin exit 3 across the typo, the unwired file, the vacuous block and now the **lost label**; plus the discriminator that a *failing* filtered case is 1, not 3. Live: `--case "this-label-does-not-exist-anywhere"` → **EXIT 3** |
| **A4** doctrine + command-body edits in the SAME commits as their mechanisms | ✅ **MET**, with a correction | Satisfied in `884a248`/`c8da9fb`/`76e3962`. The review found the co-committed prose carried **pre-change numbers** (105 s for a file this ticket split into 58+42; "3.4-minute suite" is the serial wall it stopped being the default). Corrected in `cade703` |
| **A5** every number re-measured at landing and pasted | ⚠ **PARTIALLY MET** | Met for A2 — see the table above, re-measured twice, second time at the landing tree. Not met for A1, which has no numbers to re-measure. The checklist row that ticked both with one box has been split |
| **A6** the closing full green stays mandatory in doctrine **and in every sweep script template** | ⚠ **MET in doctrine, unverifiable as phrased** | The doctrine half landed and is strong (`tests-must-gate-for-real.md` § *Targeted kills*). The "template" half has nothing to grep: sweep scripts are scratchpad-only under the standing SCC-145 ruling, so A6 asks for an artifact the plan rules out of existence. Honest disposition: **restate A6 as doctrine-only**, an operator call |

**Drift check (the other direction).** Nothing in the diff is outside the ticket's 9 items plus
SCC-159's 3, except the review fixes above — which are in-lane by `/smh-code-review`'s own
"commit review fixes inside the task worktree" rule.

### Clean-Code Gate

Machine floor imported from the gates above (no double run, per SCC-146). Run here:
`py_compile` clean on all changed Python; the comment contract holds — every new block carries the
measured reason for its existence, not a restatement of the code. Convention table: matches the
surrounding house style (stdlib-only harness, `main() -> int`, explicit-path commits).

One real finding, applied: **dead imports**. The `test_task_preflight.py` split copied its
15-name import tuple **whole** into both halves rather than dividing it with the cases. AST-verified
and trimmed in `cade703`; both halves and `_pf_fixtures.py` now report zero dead names.

### Why CONCERNS and not PASS or FAIL

Every gate is green and every mechanism in both tickets is delivered and now mutation-proven. The
cap comes from the acceptance list, not the code:

- **A1 is not delivered** — no replay, no numbers, no identical-verdict comparison.
- **A2's post-split target is missed** — 68.57 s against ≤ 60 s, with the remaining lever
  (template-repo fixtures, ticket item 9) descoped at the operator's word.

A strict reading of this command's own FAIL rule — *"an acceptance item the diff does not
deliver"* — could be applied to A1. I am calling **CONCERNS** because A1 is a *measurement* that
was not run rather than a mechanism that is missing, and because its root cause is now known and
written down. **That reading is the operator's to overturn**, and it is the first thing the
close-out should decide.

⚠ **On the earlier acceptance.** The operator said *"thats looks good this works for me all
targets met"* — I then corrected that A2's post-split target was **not** met, and there has been
**no re-affirmation since that correction**. So this verdict does not lean on that message as
blanket acceptance of A1 or A2.

### Deferred residue — ~~real, non-blocking, owed to ONE follow-on~~ SUPERSEDED 2026-08-15

> **Nothing below is owed.** The residue-ticket practice was retired by the operator's
> 2026-08-15 ruling (SCC-160); these 16 items were re-triaged under the new relevance gate in
> `_artifacts/_main/2026-08-15_triage-owns-relevance/walkthrough.md` — 5 survive into proposed
> Ticket A/B, 2 are ledgered ride-alongs, 8 killed with reasons, 1 (A6) stays your open ruling.
> The list stays below as the review's historical record.

Carried with the sequencing constraint that the `--case` ergonomics (1–3) are one change:

1. **No over-match guard on `--case`.** A short label matches broadly — measured `--case "CASE"` →
   7/8 blocks; on `test_git_hooks.py` a single letter like `"E"` matches all 40. A sweep records
   "killed by case P" when 22 blocks ran. Needs an exact-match mode or a loud multi-match warning.
2. **Block labels hard-truncated at 64 chars mid-word** (37 of ~65) by the bulk wiring transform,
   while the comment above each carries the full sentence — so copying the visible label fails.
3. **`--case=<label>` was uncovered** until this review added one control; the form deserves a
   row of its own alongside the two-token spelling.
4. **Ctrl-C no longer stops the suite** — `ThreadPoolExecutor.__exit__` drains every queued file,
   spawning fresh children after the interrupt. `cancel_futures=True` closes it.
5. **`run_all` exit 2 classifies as a suite `fail`** in `gate_receipt._classify`, contradicting the
   docstring's "not a statement about the suite either way". Needs a `2 → unrunnable` arm.
6. **`--serial --jobs 0` is silently coerced** — `--serial` short-circuits before the `jobs < 1`
   guard the author wrote specifically to refuse that value.
7. **A zero-file suite prints `0/0 files passed` and exits 0** — the vacuous-green class this lane
   closed one level down, still standing one level up.
8. **No invariant stops an orphan `c.check`** outside every block. Zero today (AST-verified across
   all four wired files) — but I created one *during this review* and only caught it by reading a
   case count. A meta-case should AST-walk the wired files.
9. **`wf.same_tree` is untested** while two command bodies now authorise skipping a 25-file gate
   run on its word.
10. **The step-02 verify-wave grouping has no pin** — every other invariant in that step file
    carries a regex pin plus a proven mutation string; the new rule added none.
11. **The 6d skip landed in the 4b section only** — Step 5, the other half of the pair, never
    learns it can be skipped.
12. **`merge-target-guard`'s `destination()` still says an incident lane exchanges work "never
    with a story or chore lane"** — a rule line that reads as though the gate misfired, printed
    directly under the new `incident:incident` refusal. `INC5` asserts only `"incident pipeline"
    in out`, which the stale sentence satisfies.
13. **No case for an incident ref carrying an unlanded *story* tip** — one quarter of the refused
    class, unpinned while the other three are pinned.
14. **The multi-lane transient**: `/smh-merge-multiple-workingtrees` merges lane after lane onto
    local `main`; if a push is deferred, the next lane's preflight hard-errors "STALLED LANDING"
    about a landing that is mid-flight, not stalled.
15. **A6's phrasing** — restate as doctrine-only, or write the template it asks to be grepped.
16. **`.agents/scripts/INDEX.md` still writes rot-prone counts** one clause after deleting a
    rotted one for being unmaintainable. (The misleading half — per-file numbers reading as the
    suite wall — was fixed in `cade703`.)

## The rider build (2026-08-14, post-review — rolled into this ticket at the operator's word)

The lane's own close-out fired the defect this section fixes: SCC-159's work landed HERE by the
operator's one-lane ruling, so at preflight the child was still `In Progress` — `check_children`
read the designed state as an unfinished job, BLOCKED, and the agent handed the operator a manual
Jira edit. The operator ruled twice: the parent-closes-last logic STAYS ("root 1 is just logic"),
and no flow may EVER leave the operator a board write ("No were did I ever ask to start having to
manually adjust the status of tasks in jira"). Fix approved in-ticket: "lets fix this roll this
into this ticket. I dont want to make a new one. this is tweaking" → "approved".

**The mechanism (commits 8c1b10e + 1365922):**

- `task.yaml` gains `riders: [KEY-00, ...]` — one-line flow style ONLY; the hand parser must not
  half-read a block list, and an UNREAD declaration fails CLOSED with the flow line printed.
  This lane's manifest declares `riders: [SCC-159]`.
- `check_children(riders=…)` WARNS a declared open rider with the ceremony's own transition
  command, named as an agent step ("never an operator edit"), and still hard-errors any
  undeclared open child — the error teaches the declaration as the third exit beside finish-it
  and `Deferred`, suggesting the COMPLETE line so a copy-paste never clobbers existing riders.
  Settled sibling manifests are history — their riders spare nothing. The all-closed info line
  counts riders honestly instead of claiming "all Done or Deferred".
- `/smh-close-task-merge-tree` Step 4: riders → `Done` FIRST (scoped to actual subtasks of the
  parent, so a foreign declared key is never flipped), parent LAST, plus the broken-flow guard:
  a hand-back assigning the operator data entry is a bug in the flow, never an instruction to
  relay.
- `jira.md`: the universal law under *Writing to the board* (operator acts in WORDS; agent
  performs every board write inside that ceremony; read status rules as WHEN, never WHO), the
  `In Review` definition (blocked-on-operator ONLY), and rider rows in the type table +
  subtask lifecycle. SOP doc: rider bullet, S4 mermaid node, you-act-in-words callout. Doors
  re-synced (18 launchers).

**Proof:** test-first — 9 RED each at its own assertion (6 declared controls) → 19/19 green,
including comment-immunity, lowercase normalization, settled-sibling exclusion, and the
truthful-info pin. Mutation record **10/10 killed by named cases in one pass** (membership
inverted/always/never/substring, regex line-anchor, `upper()` drop, settled-exclusion disable,
example completeness, warn→info downgrade, `main()` wiring deletion), restores sha256-verified.
Closing bare green: `run_all` 27/27 files, lint 0/0, maps clean. **Live proof on THIS lane:**
`task_preflight --expect-key SCC-156` now exits 1 (warn-only) with the SCC-159 rider
instruction printed and `VERDICT: clear to close out and merge` — the same board state that
produced `BLOCKED` before the build.

**Two gate encounters worth recording:** the `--yes` guard rightly indicted my first layout (a
transition command wrapped across physical lines reads as un-flagged; an absence assertion
quoting the verb phrase reads as a call site) — both reflowed to comply, the guard untouched.
And T6 (`test_sops_prds_folder.py`) flagged the operator's own `quick_links.md` rolled in at
their order; its name joined the by-NAME allowlist beside `INDEX.md` (it is a pure signpost —
links INTO `docs/_scc_sops_prds/`, no procedure content). **That allowlist edit is flagged for
your review below.**

**Review coverage, stated plainly:** the verdict above stands at `cade703…` — the 5-lens review
never saw commits `8c1b10e`/`1365922`. They are operator-approved, test-first, and
mutation-certified, but not LLM-reviewed; because code moved past the verdict sha, the close-out
gate correctly prints NO suite-skip and runs the full mechanical gate. Receipts re-stamped on
the clean-tree chain: suite PASS 88.0 s @ `1365922` (the parallel runner this ticket built,
timing its own close-out — the pre-ticket floor was ~205 s), lint PASS, maps PASS.

## Your Actions

Everything agent-solvable was attempted and is ticked. What is left is genuinely yours — and
per the universal law, none of it is a Jira edit.

- [x] ~~SCC-159 must leave `In Progress` before the merge~~ **Superseded by the rider build:**
      SCC-159 is declared in `task.yaml` `riders:`, the preflight warns instead of blocking,
      and the close ceremony transitions it to `Done` first, parent last — agent writes inside
      the close you invoke. Nothing here is yours to do by hand.
- [ ] **Rule on A1.** It is not delivered: no replay, no timings, no identical-verdict comparison
      against SCC-154's table. The root cause is known and written down. A strict reading of the
      review command's FAIL rule (*"an acceptance item the diff does not deliver"*) would apply;
      I called CONCERNS because A1 is a measurement that was not run, not a mechanism that is
      missing. **Overturning that to FAIL is your call.**
- [ ] **Rule on A2's missed target.** 68.57 s measured against ≤ 60 s. The remaining lever
      (template-repo fixtures, ticket item 9) was descoped at your word. Either accept 68.57 s as
      the new number and amend the ticket, or re-open item 9 in the follow-on.
- [ ] **Rule on A6's phrasing** — it asks for a "sweep script template" to be grepped, and the
      standing SCC-145 ruling keeps sweep scripts out of the tree. Restate as doctrine-only, or
      commission the template.
- [ ] **Review the T6 allowlist edit** (rider-build section above): `quick_links.md` is now
      name-allowed in `_my_resources/_quick_reference/`. If you'd rather it live elsewhere or
      under `INDEX.md`, say so and the follow-on carries it.
- [ ] **The merge itself.** This lane is merge-ready and STOPS here. `/smh-close-task-merge-tree`
      is your per-merge sign-off, and since SCC-37 the minter refuses without
      `--operator-approval '<your exact words, this turn>'`.
- [x] ~~**One follow-on ticket** for the 16 deferred residue items in the review section above~~
      **Superseded by your 2026-08-15 ruling (SCC-160):** residue tickets are retired; the 16
      items were re-triaged under the relevance gate (see
      `_artifacts/_main/2026-08-15_triage-owns-relevance/walkthrough.md`) — survivors ride the
      two proposed decided tickets awaiting your word, the rest died with reasons. This row was
      never yours to do by hand and no longer exists as work.

**Landing order vs `chore/SCC-155-label-tasks`: free.** The two lanes conflict only in
`.agents/.sync-manifest.json` and `_artifacts/_main/INDEX.md`, both generated. Whichever lands
second re-runs `/smh-sync-agents` and re-adds one INDEX row.
