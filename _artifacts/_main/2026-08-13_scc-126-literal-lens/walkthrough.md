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

- [x] **Step A — RED.** 16 new guard entries (48 harness cases) in `test_review_engine.py`, written
      in that file's own discipline: each binds a *relationship* (a table cell, an anchored line)
      rather than a vocabulary, and each ships a counter-example proven to make it go red. The
      review took the file to **40 new entries**, 8 of which read the caller's own body.
  - ⚠ Three of those guards were themselves vacuous — one caught by the harness during the build,
    two more while fixing the review. See *What fought back*.
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

⚠ **Why that RED says 49 and not 51.** Seventeen touched entries × 3 harness cases = 51. Two of
them passed anyway, and for a reason worth keeping: the pack-priming entry's counter-example string
was not yet unique, so it mutated the Edge Case Hunter's row instead of the new lens's and both its
proof-rows went green. **The vacuous guard masked two of its own RED failures.** Fixing the
counter-example is what took the count to its true 51; the recorded 49 is the honest measurement of
the state it was taken in, not a miscount.

**Lane gate, bare (no pipes — a piped gate reports `tail`'s exit code), at `d920322`** — the sha
that lands, measured after the review fixes:

```
python3 .agents/scripts/tests/run_all.py                -> 21/21 files, 1456/1456 cases, exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only -> 0 errors, 0 warnings, 8 info, exit 0
python3 .agents/scripts/sop_currency.py --paths <3>     -> exit 0 (control without the SOP: exit 1)
python3 -m py_compile test_review_engine.py             -> OK
```

**Case total 1335 → 1456, exactly additive**: 40 new guard entries × 3, plus one structure check for
the caller file. This lane displaced no existing test. (`1335` is main's own recorded baseline at
`36e1ffe`; an earlier draft of this section said `1329`, which was two commits stale — the
conclusion held but the arithmetic offered as its proof did not.)

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
- **⭐ The review's lesson is one level up from SCC-125's.** That task learned *pin the wiring, not
  the prose*. This one learned **pin it in the file that has to hold** — every rule about the
  autopilot caller lived in the engine's own step file, so reverting the caller left 440 cases green
  while the behavior the ticket is named for was gone. A guard in the wrong file is not a guard.
  And two of the three vacuous counter-examples here were created **by writing more prose**: adding
  a paragraph containing `"raises the floor"` silently disarmed an unrelated existing check, because
  `.replace(old, new, 1)` takes the first hit. Uniqueness of a counter-example is not a property you
  establish once — it is one any later edit can take away.

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

## Code Review (2026-08-13)

**Verdict: PASS @ d920322**
Suite evidence measured at `d920322` — the same sha, after every fix below was applied. No code or
test change followed that run.

**Scope:** `main...HEAD`, 12 files — the engine's `SKILL.md` + `step-01` + `step-03`, the AP caller,
the guard file, the SOP, and this lane's artifacts.
**Method:** clean-room adversarial subagent on the diff alone (read-only, no conversation context;
plan and walkthrough opened only afterwards) · acceptance audit against the Step 1 list · the
command-centre gate · the clean-code machine floor.

**Layers:** blind hunt `ok` (ran first time, 18 findings) · acceptance audit `ok` · machine floor
`ok`. No layer died; nothing ran inline; nothing capped the verdict.

### Step 0.7 — re-derivation against current `main`

1. **Nothing moved.** `main` is still `36e1ffe`; 0 files landed since the merge-base, so no path,
   rule pointer or script this diff names was relocated under it.
2. **True overlap: none.** `merge-tree --write-tree` produced a clean tree, no conflict messages.
3. **Both siblings live but empty** (SCC-127, SCC-128 still at `36e1ffe`). Two landing-order
   dependencies stand, both recorded in `## Your Actions`.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `step-01-review.md` §Scope | important | Three caps sat in **unquoted** text, which this file itself defines as orchestrator-only and *"never sent to a lens"*. The lens was told to be EXHAUSTIVE and handed repo access, while *"not a licence to sweep"* and *"report the truncation"* never reached it — so the unbounded sweep the section exists to prevent was the guaranteed outcome, and its disclosure requirement was structurally impossible | **applied** — lens-facing half blockquoted and routed; orchestrator half kept and made explicit |
| F2 | `step-01-review.md` §dead-lens | important | *"A dead lens is a finding… applied to any lens that comes back empty"* also describes a lens that RAN and correctly found nothing. Read literally, every clean review caps at CONCERNS — the F6 failure at diff-wide scale | **applied** — zero findings is explicitly not a dead lens; the contract now binds *no usable output* |
| F3 | `step-01-review.md` §modes | important | The lens's `full` mode collided with `review_mode: full`. An autopilot review is normally both at once, so the collision's natural resolution was *"caps are advisory"* — overnight, unattended | **applied** — renamed `lens_budget: standard\|capped`, stated independent of `review_mode` in three places, unnamed defaults to `capped` |
| F4 | `SKILL.md:23-40` | important | The AP passed `capped` as free text; the caller-contract table had no row for it, so dropping the token in a later edit would leave the lens uncapped with nothing — contract, guard or linter — noticing | **applied** — `lens_budget` is now a contract row with its default stated |
| F5 | `cicd-code-review-AP.md` §inline | important | The inline-lens instruction **this lane added** destroyed the Blind Hunter's blindness: the engine is invoked after Ingest 2, so inline execution means the "blind" lens already holds the plan, walkthrough and pack — and the record would still call it blind | **applied** — inline runs the blind lens FIRST on the diff alone; otherwise recorded `ok (not blind — context held <what>)` |
| F6 | `step-01-review.md:288` vs AP | important | Same trigger, opposite action: the engine says *write prompts and return*, the AP says *run them inline*. The engine's own doctrine — *"an unresolved collision is resolved by the model at random"* | **applied** — the engine now states a caller MAY override, and that inline ≠ simulating |
| F7 | `test_review_engine.py` | important | **Every check lived in step-01 — the engine's claim ABOUT its caller.** Reverting `cicd-code-review-AP.md` to its pre-change solo review left all 440 cases green and lint clean while the literal lens never ran in the autopilot at all — the one behavior this ticket is named for | **applied** — 8 checks read the caller's own body; mutation test kills 24 cases |
| F8 | `step-01` §cap → `step-04` | important | A 20-file truncation had no route into anything the caller sees: not a finding, not a `note`. A 40-file story returns `5/5`, `severity_floor: none`, silence — and 20 files were never literal-checked | **applied** — orchestrator carries it into `notes`; the lens must report it as its first output line |
| F9 | `step-01-review.md:32` | important | The hunter-contract enumeration still said *"today the Blind Hunter and the Edge Case Hunter"* after a third was added, giving textual support for assembling the new lens **without** Gates 1–3 | **applied** — enumeration updated and the table declared the authority over it |
| F10 | `step-01` Gate 1 vs charter | important *(raised from suggestion)* | Gate 1 demands a production reachability trace; the lens's charter names *code that will not compile* and *a method that does not exist*, which have no entry point at all. With *"when in doubt, DROP"*, the lens must discard exactly the class it was added to catch | **applied** — a stated Gate 1 adaptation, scoped to always-raised violations; state-dependent ones still owe the full trace |
| F11 | `step-03-triage.md:17` | suggestion | The `source` vocabulary enumerated four lenses; findings from the fifth arrive with no defined value and the agent invents one | **applied** — `literal` added |
| F12 | `test_review_engine.py` caps | suggestion | The cap checks bound the **bolded headlines**. `**A 20-file cap.**` stays true while *"at most 20"* becomes *"at most 200"* — all cases green, cap gone | **applied** — every cap regex now binds the number, the threshold and the destination |
| F13 | `workflows_testing_SOP.md` | suggestion | Omitted the change that actually moves the cost (one agent → orchestrator + five lenses, three pack-primed), and *"the one real token cost in the engine"* mistranslated the research doc's *"the only **item**"* — among four upgrade items, not among five lenses | **applied** — both corrected; the fivefold grounding replication is now the first bullet |
| F14 | `cicd-code-review-AP.md:36` | suggestion | Told the reviewing agent the engine runs *"a verify wave"*; step-02 is a documented pass-through until SCC-127, so severities are unverified hunter assertions that map straight to FAIL/CONCERNS | **applied** — states plainly that severities are unverified today |
| F15 | `step-01` `standard` row | suggestion | `standard` budget binds no caller today — the two interactive commands are not wired to the engine yet | **dismissed** — that wiring is SCC-128's scope, named in this lane's own boundaries. Not a defect here |
| F16 | `walkthrough.md` | suggestion | RED recorded 49 where a clean reconstruction gives 51, and additivity was stated `1329 → 1383` when main's baseline is `1335` — the conclusion held, the arithmetic offered as its proof did not | **applied** — baseline corrected to `1335 → 1456`; the 49-vs-51 gap explained (the vacuous guard masked two of its own RED failures) |
| F17 | `step-01-review.md:374` | nitpick | *"4 lenses ran"* example stale with five lenses, three lines above the scoring table | **applied** |
| F18 | `cicd-code-review-AP.md:143` | nitpick | ~125-char line in a file wrapped near 100 | **applied** |
| NEW-1 | `test_review_engine.py` | important | Found while fixing: my own new prose made `"raises the floor"` non-unique, so `.replace(old, new, 1)` mutated the zero-findings paragraph instead of item 4 — that check could no longer fail | **applied** — counter-example names the retry+inline clause |
| NEW-2 | `step-01-review.md:35` | suggestion | The F9 rewrap broke `the \`How\` cell is the wiring and is not optional` across a newline, breaking an existing guard | **applied** — rewrapped |

### Clean-Code Gate

| Check | Result |
|---|---|
| `run_all.py` (bare) | **21/21 files, 1456/1456, exit 0** |
| `workflow_lint.py --toolkit-only` (bare) | **0 errors, 0 warnings, 8 info, exit 0** |
| `sop_currency.py` on the changed set | **exit 0**; positive control without the SOP → **exit 1** (gate proven to still have teeth, not assumed) |
| `py_compile` on the guard file | **OK** |
| Link + anchor, 4 changed docs | all resolve — `./step-02-verify.md` / `./step-04-record.md` are steps-relative and exist; the rest (`sudo-tests.yaml`, `deferred-work.md`, `decisions-log.md`, `gate_receipt.py`) are child-project runtime artifacts the AP command already named before this diff |
| Door parity | no command added, renamed or deleted — `cicd-code-review-AP` has no skill/workflow/opencode door by design (`platforms: [claude, opencode]`, invoked by name from the three autopilot bodies) |
| Comment contract | the guard file's new blocks each state *why* the check exists, and the two review-derived ones cite the failure they prevent |

### Acceptance matrix

| Item | Where the diff satisfies it | Proving assertion |
|---|---|---|
| 5th lens exists, always runs, hunter-contract-wired, pack-primed | `step-01` lens table row | 3 checks binding the row's `Runs when` / `How` / pack cells |
| The discipline reaches the lens | `step-01` blockquote | 3 checks anchored `^>` |
| Bounded four ways | `step-01` §Scope | 8 checks binding the numbers, threshold, destination and scoring word |
| Mode defined once; callers only name it | `step-01` §`lens_budget` | 6 checks incl. both table rows and the NOT-`review_mode` prohibition |
| AP runs the engine in capped mode | `cicd-code-review-AP.md` | **8 checks reading the caller's own body**; reverting it kills 24 cases |
| Lens arithmetic agrees across files | `step-01` + `SKILL.md` | `4/4 never 4/5` pinned in both |

**Changes applied:** 19 of 20 findings applied, 1 dismissed with a reason.

## Your Actions

- Landed on `chore/SCC-126-literal-lens` — `7b14f91` (implementation) + `199ef5d` (artifacts) +
  `d920322` (review fixes). Pushed, tree clean.
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
