# SCC-147 — interactive review callers name `lens_budget: standard`

**Ticket:** SCC-147 · **Lane:** `chore/SCC-147-lens-budget` · **Off:** `main` @ `0677441`
**Plan:** `implementation_plan.md` (this folder), audited GO before any edit.
**Parallel lane:** SCC-148 (`task_preflight` incident misroute) — disjoint file set, landing order free.

## Task Checklist

- [x] Step 0 — repo + lane resolved from `rev-parse`; SCC-147 moved to In Progress at the tree.
  - Sibling-lane read found `chore/SCC-145-mutation-doctrine` live at session start. **It landed on
    `main` mid-lane** (the operator said so), so the lane was fast-forwarded onto `0677441` before
    the first edit rather than absorbing a merge later.
- [x] Step 1 — checkable list fixed from the ticket's own ACCEPTANCE block (A1–A5 in the plan).
- [x] Step 1.5 — plan written, `/smh-self-audit` run (Full), **verdict GO**, two of its own findings
  baked back into the plan before work started (the AP-twin note had to be rewritten whole, not
  patched; the case delta was +8, not the +6 first written).
- [x] Step 1.6 — subtasks: **nothing clears the bar.** Four small edits in one commit are not four
  branches.
- [x] Step 2 — RED first, on the guard, before either command was touched.
- [x] Step 3 — GREEN: one row per interactive caller, twin note rewritten, doors regenerated.
  - **The removal proof was run twice, because the first run was invalid.** See Evidence.
  - The AP-twin stamp gate (SCC-82) and the artifacts INDEX gate both fired on this work and both
    were satisfied properly rather than silenced. See Evidence.
- [x] Step 3.5 — eject tripwire checked: no deployable path, not story work, list stayed checkable.
- [x] Step 4 — review gate (`/smh-code-review`) — five lenses, **verdict PASS @ `548db66`**.
  - **The review changed the outcome.** The guard shipped in the first commit could be defeated
    four ways, all four proven on disk rather than argued, and the fixes are in `7e4f406`.
  - The `RESTORE` trap fired a **second** time during the review's own sweep. Both occurrences are
    written up under Evidence, because the second one proves the first was not carelessness.

## Evidence

### The defect, stated against the source

`.agents/skills/code-review-engine/steps/step-01-review.md:153-161` defines `lens_budget` once and
says, in as many words, that **a caller naming none gets `capped`** — the safe default, chosen
because the cost of guessing wrong the other way is an unbounded overnight spend nobody is watching.
`SKILL.md:32` repeats the default in the input table.

`/cicd-code-review-AP` named `capped` explicitly. Neither interactive caller named anything:

| Caller | Before | Effect |
|---|---|---|
| `/cicd-code-review` Step 1 table | no `lens_budget` row | silently ran the autopilot budget |
| `/smh-code-review` Step 1 table | no `lens_budget` row | same — rewired to the engine in SCC-128, same omission |

Nothing was unsafe (the caps still bound). What was lost is the **one top-up** the literal-correctness
lens can earn by naming the file it wants and why — the thing it is supposed to have when a human is
sitting in front of the review. **The ticket's second acceptance item is answered by measurement:
`/smh-code-review` carried the identical omission**, so it got the identical fix.

> ⚠️ **Read that last paragraph with review finding 7.** The top-up is what `standard` is *defined*
> to buy, and it is what the ticket is written around — but the review established that step-01
> never actually delivers it to the lens (the clause is unquoted, so it never reaches the prompt).
> The naming defect this ticket fixes is real and worth fixing on its own: a caller that states its
> budget is correct whether or not the engine's top-up wiring works, and the wiring is a separate,
> older engine defect now filed as a follow-on. **What this lane must not do is claim a behavioural
> win it cannot demonstrate**, which is why both shipped rows were reworded to stop promising one.

### A1 + A2 — the rows exist, in the callers' own invocation tables

`.agents/commands/cicd-code-review.md:50` and `.agents/commands/smh-code-review.md:137`. Each row
**names** the budget and deliberately does **not** restate the caps — step-01 owns those numbers,
because a cap each caller repeats is a cap that drifts. **The wording shipped is the review's, not
the plan's:** the first version restated step-01's top-up clause in the same sentence that forbade
restating caps, which three lenses caught independently. Both rows now carry the AP twin's already
pinned formula — *"This command does not define what the caps are; step-01 of the engine does,
once"* — so the primary and its twin have **converged** on the wording rather than diverged.

### A3 — the guard reads the CALLERS' bodies, not step-01's claim about them

`test_review_engine.py`: `CALLER_FILES` grows from one entry to three; two `CHECKS` tuples key to
`.agents/commands/cicd-code-review.md` and `.agents/commands/smh-code-review.md`.

This is SCC-126's finding **F7** applied to its own follow-on: a rule about a caller that lives only
in the callee's file is a rule nothing enforces — reverting the caller left all 440 cases green while
the wiring was gone. Every pre-existing `lens_budget` check in this file asserts step-01's *text*.
Those still pass when a caller silently drops its budget, which is exactly how this defect survived.

The counter-example for each new check is **`capped`**, not a nonsense string. `capped` is the exact
value these two silently inherited, and a row that says `capped` reads as deliberate — so the check
has to **reject** it, not merely notice an absent word.

**RED** (`red-01-guard.txt`, bare, `EXIT=1`) — and it is an assertion failure, not a setup death; it
names the missing row per caller:

```
-- 749/755 passed --
[FAIL] interactive caller /cicd-code-review: invocation table passes lens_budget standard
[FAIL]   ^ counter-example applies: .agents/commands/cicd-code-review.md: '| `lens_budget` | `standard`' not present, so the proof would be vacuous
[FAIL]   ^ counter-example is rejected: check survives its own counter-example — it cannot fail on content
[FAIL] interactive caller /smh-code-review: invocation table passes lens_budget standard
[FAIL]   ^ counter-example applies: .agents/commands/smh-code-review.md: '| `lens_budget` | `standard`' not present, so the proof would be vacuous
```

**GREEN** (`green-01-guard.txt`, bare, `EXIT=0`): `-- 755/755 passed --` at the fix commit; the
review's fixes take this guard to **762/762** and the fixture guard to **68/68**.

⚠️ **The pattern shown in that RED is not the pattern that shipped.** The review proved it could be
defeated four ways without touching the value it pins. What ships is anchored to the invocation
table and closes the cell — see the `## Code Review` findings table, rows 1–3.

### A4 — the guard fails when the budget line is removed — and the first proof of that was INVALID

⛔ **This is the finding this lane produced against itself, and it is worth more than the fix.**

The first removal sweep ran while the fix was **still uncommitted**. The restore step was
`git checkout -- <file>`, which restores from `HEAD` — and `HEAD` did not yet contain the row. So
`git checkout` reverted **the fix**, not the mutation. The consequences, visible in the recorded
output:

- the second caller's red **also carried the first caller's failure**, because the first caller was
  never actually restored;
- the closing "both restored — guard must be green again" run came back **red**, asserting the
  opposite of what the line above it claimed;
- the working tree was left with **both rows silently gone**, which `grep -c` confirmed.

Had the sweep stopped after the first mutant — the common shape — it would have read as a clean
kill, and the fix would have been quietly absent from the commit. **A restore that restores the wrong
thing is indistinguishable from a passing proof** unless the sweep also re-asserts green at the end,
which is precisely why `RESTORE` is one of the four named techniques in `tests-must-gate-for-real.md`
§ Mutation Testing (SCC-145, landed on `main` two commits before this lane started).

Re-run against the **committed** fix (`4319722`), so restore returns to the fixed state
(`red-02-removal-proof.txt`) — each mutant killed **independently**, each restore verified green
before the next mutant is applied:

```
=== MUTANT: delete the lens_budget row from .agents/commands/cicd-code-review.md ===
dropped 1 line(s) -- mutation applied
guard EXIT=1  (1 = KILLED)          -- 752/755 passed --
[FAIL] interactive caller /cicd-code-review: invocation table passes lens_budget standard
RESTORED -> guard EXIT=0  -- 755/755 passed --

=== MUTANT: delete the lens_budget row from .agents/commands/smh-code-review.md ===
dropped 1 line(s) -- mutation applied
guard EXIT=1  (1 = KILLED)          -- 752/755 passed --
[FAIL] interactive caller /smh-code-review: invocation table passes lens_budget standard
RESTORED -> guard EXIT=0  -- 755/755 passed --
```

Each mutant asserts that the mutation actually applied (`dropped 1 line(s)`, and the script raises if
the count is anything but 1) — SCC-129's lesson that a mutant declared but never seeded scores a
green self-proof.

**INVERT sweep** (`red-03-invert-proof.txt`), the code-derived mutant the ticket did not name: flip
the **value** rather than delete the row. This is the realistic drift — a later editor sets `capped`
deliberately and the row still reads as configured. Both killed, both restored green:

```
=== MUTANT: standard -> capped in .agents/commands/cicd-code-review.md ===
guard EXIT=1  (1 = KILLED)   -- 752/755 passed --   RESTORED -> EXIT=0  755/755
=== MUTANT: standard -> capped in .agents/commands/smh-code-review.md ===
guard EXIT=1  (1 = KILLED)   -- 752/755 passed --   RESTORED -> EXIT=0  755/755
```

**4 mutants declared, 4 killed, 0 survivors, tree clean after each.**

### A5 — no drift left behind, and two gates fired on this work

**The AP twin.** `cicd-code-review-AP.md`'s divergence note read *"the primary passes none and takes
the `capped` default … raised as a follow-on against /cicd-code-review, not patched from inside its
twin."* **This ticket IS that follow-on**, so patching only its first line would have left a live
pointer to work that was now done. Bullet 1 was rewritten whole. "THREE divergences remain" stays
true — the **values** still diverge, which is the point.

**The SCC-82 stamp gate then refused the commit's successor, correctly.** `workflow_lint` reported:

```
[FAIL] SCC-82 G the live repo's AP twins report nothing:
  ['cicd-code-review-AP.md: ap_reconciled names fb3a9ba, but cicd-code-review.md is now at 4319722 - diff the twin and restamp']
```

That stamp is an auditable claim — *"I read the primary at this sha and there is nothing to port"* —
and it is deliberately not a mute switch. So the diff was actually taken
(`git diff fb3a9ba..HEAD -- .agents/commands/cicd-code-review.md`): **one hunk**, the new
`lens_budget` row. Nothing to port, because the twin already names `capped` in its own contract
block. Restamped to `43197223063bc249e6994694530b46b76dbd5c9b` **with that reasoning written into
the comment above it**, per the linter's own "every stamped twin records WHY" check.

**The doors.** `.opencode/commands/` copies are full bodies and were regenerated by `sync-agents`
(both carry the row — verified by `grep -c`). The `.agents/workflows/` Antigravity mirrors are
**thin launchers by design** (the 12k-char cap) and carry no table rows at all — verified, not
assumed: `grep -c review_mode` returns 0 there too, so this is the shape of every mirror, not a gap
in this one.

**The artifacts ledger.** `check_maps` failed with `_artifacts/_main/INDEX.md: missing row for
2026-08-14_scc-147-lens-budget/` — added.

### Gate at the landing sha — `548db66`

Every command run **bare** (a piped gate reports the pipe's exit code, not the gate's — and
`${PIPESTATUS[0]}` is bash-only, which bit this session once already in `zsh`).

| Gate | Result | Exit |
|---|---|---|
| `python3 .agents/scripts/tests/run_all.py` | 23/23 files, **1891/1891 cases** | `0` |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info | `0` |
| `python3 .agents/scripts/check_maps.py --depth3-only --strict` | clean | `0` |

**The case total is exactly additive, and both figures were predicted before they were measured.**
`main`'s baseline is **1875** (at `0677441`).

| Stage | Adds | Total | Made of |
|---|---|---|---|
| the fix (`964fdbd`) | +8 | **1883** | 2 checks × 3 sub-assertions (the check, "counter-example applies", "counter-example is rejected") + 2 `CALLER_FILES` existence checks |
| the review's fixes (`548db66`) | +8 | **1891** | +1 caller-set discovery, +1 `CALLER_FILES` completeness, +3 per-caller "names a budget", +2 "exactly ONE row", +1 in `test_review_fixture.py` (67 → 68) |

The pre-work audit's first arithmetic said +6, corrected itself to +8 **in the plan before any
edit**, and the measurement matched. Raw output: `green-02-run-all.txt` ·
`green-03-workflow-lint.txt` · `green-04-check-maps.txt` · `red-04-review-mutation-sweep.txt`.

## Your Actions

Everything agent-solvable was done in-lane. What is left is genuinely yours:

- **Close out with `/smh-close-task-merge-tree`** — invoking it is the merge sign-off, and this
  lane never merges, transitions or prunes on its own.
- **⚠️ Ledger conflict with SCC-148, expected and benign.** Both lanes append a row to
  `_artifacts/_main/INDEX.md` and nothing else overlaps. Whichever lands **second** reconciles by
  **keeping both rows** — the same resolution SCC-145 and SCC-129 used. Order is free otherwise.
- **A follow-on ticket is owed** (review finding 7, deferred with reasons): `lens_budget: standard`
  may buy nothing today, because step-01's top-up clause is unquoted and so never reaches the lens,
  and the truncation rule hands the lens a *count* of withheld files rather than their names. That
  is an engine defect older than this ticket. The `nc_review_engine` fixture is already the right
  acceptance test for it — run `bad.diff` under `capped` and under `standard`; `NC_LITERAL` should
  appear only under `standard`. I have not filed it, because minting tickets is your seam.

**Nothing is owed to the SOP.** `workflows_testing_SOP.md:1689` already stated the intended split
("Typed by hand it runs `standard`"); this lane made the commands match the page, so every commit
carries `[sop-ok]` with that justification in the log rather than a no-op doc edit.

---

## Code Review (2026-08-14)

Verdict: PASS @ 548db660b4ecb64ba0e17c1e79f52c1ba7d3b1cf
Suite evidence measured on that same sha: `run_all` 23/23 files, **1891/1891 cases**, exit 0.

**Scope** — `main...HEAD`, 18 files: 3 command masters, 2 guards, 2 generated `.opencode` doors,
the sync manifest, and this lane's artifacts. Code+doors were passed to the engine; the artifacts
are Ingest 2 by construction.
**Method** — the house `code-review-engine` at `lens_budget: standard` (the value this ticket
adds, so the lane's first act was to exercise its own fix), then the command-centre gate, then the
clean-code pass.

```
lenses_run:      5/5   (Blind Hunter ok · Edge Case ok · Literal-Correctness ok ·
                        Acceptance Auditor ok · Test-Adequacy ok)
lenses_na:       none  (review_mode: full — the plan is the spec)
findings:        4 patch · 2 defer · 3 dismissed
severity_floor:  none  (every `important` finding was FIXED in 7e4f406, not carried)
notes:           no degradation; no lens retried or rerun inline. Patch material spilled to
                 ARTIFACT_DIR/review-context-diff.txt (10,433 chars > the ~9,000 inline
                 threshold); 7 files, well under the 20-file cap, so nothing was withheld.
```

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `test_review_engine.py:879` | **important** | **The guard could not see POSITION.** `^\|\s*`lens_budget`\s*\|\s*`standard`` with `re.M` matched any table row anywhere in a 17 KB file. Move the row out of the engine-invocation table into an appendix, an HTML comment, or a fenced "example" block and the caller passes **no** budget, silently takes `capped` — the exact defect this ticket exists to remove — with every case green. Proven on disk: mutant survived, 755/755, exit 0. | **applied** — anchored to `^\|\s*`HEAD_SHA`` + a contiguous run of table rows, which any blank line or prose terminates |
| 2 | `test_review_engine.py:879` | **important** | **The pin never closed the cell.** It stopped at the value token, so 300 characters of prose after `standard` could invert it — `"…was the SCC-147 value and is now WITHDRAWN — pass `capped` on every run"` — and stay green. An LLM reading that table passes `capped`. Proven on disk. | **applied** — tempered `(?:(?!capped)[^\|\n])*\|` reads to the closing pipe and refuses `capped` inside the cell. This is why neither row's prose may name `capped`; they say "the autopilot's budget" |
| 3 | `test_review_engine.py:879` | **important** | **A second, contradictory row was invisible.** `re.search` returns on first match. A later `## Step 3.9 — budget override` section carrying `\| `lens_budget` \| `capped` \| ` left the Step 1 row untouched and the whole gate green. | **applied** — the rows are now **counted**: exactly one `lens_budget` row per caller |
| 4 | `nc_review_engine/README.md:51` | **important** | **The negative control's own budget was unguarded prose.** Flip the fixture's `lens_budget` to `capped` and `NC_LITERAL` — catchable *only* by opening `codebase/helpers.py`, which `bad.diff` does not touch, i.e. only via the top-up `standard` allows — becomes unreachable. The control silently stops discriminating between lenses, which is the entire point of SCC-129, at 67/67 green. | **applied** — added to `test_review_fixture.py`'s pinned-literal list (68 cases) |
| 5 | `cicd-code-review.md:50` · `smh-code-review.md:137` | suggestion ×3 | **Both rows restated the cap they forbade restating** — "the ONE top-up it can earn by naming the file it wants and why" is step-01:160's caps cell reproduced, in the same sentence as "never restate the caps", across four files once the generated doors are counted, with nothing binding any copy to step-01. Found independently by three lenses. | **applied** — both rows now use the AP twin's already-pinned shape: name the budget, then "does not define what the caps are; step-01 of the engine does, once" |
| 6 | `test_review_engine.py` (scope) | suggestion | **The fix closed the defect, not the class.** Three callers pinned by hand; a fourth wired on tomorrow could name nothing, take `capped`, and stay green because no check knows it exists. | **applied** — `CALLER_FILES` is now asserted to **be** the set of commands invoking the engine, derived from the commands, plus a per-caller "names a budget" check |
| 7 | `step-01-review.md:160` | **important** | ⭐ **`standard` may be behaviourally identical to `capped` today.** The only difference between the budgets is the top-up at step-01:160 — and that line is **unquoted**, while step-01:25-26 (pinned twice by this very guard) says unquoted text is orchestrator instruction that *never reaches a lens*. The truncation rule compounds it: the lens is handed a **count** of withheld files, never their names, so it cannot "name the specific file it wants" even if it knew it could. Verified by grep: "top-up" occurs once in the engine, outside every blockquote. | **deferred** — this is an **engine** defect in step-01, older than this ticket and untouched by it; wiring it changes the engine's own contract, which is precisely what this ticket's author declined to smuggle in from inside a twin. **Follow-on owed.** What this lane did do is stop the caller rows *promising* a top-up the engine may not deliver |
| 8 | `nc_review_engine` A/B probe | suggestion | No live engine run is recorded for this lane; the fixture is a ready-made A/B (run `bad.diff` under `capped` vs `standard` — `NC_LITERAL` should appear only under `standard`). | **deferred** — it is the correct discriminator, and finding 7 predicts it would show **no** difference today. It belongs to the follow-on that fixes the wiring, where it becomes the acceptance test |
| 9 | `ap_reconciled` sha · opencode AP door · required-vs-optional wording | — | Three claims raised as "I am unsure". | **dismissed with evidence** — see below |

### Dismissed, with the measurement rather than an opinion

- *"`ap_reconciled` names a sha that cannot contain the row it describes."* Sound as a principle,
  wrong here, and the lens named the check itself: the lane used two commits.
  `git log -1 --format=%H -- .agents/commands/cicd-code-review.md` returns exactly the stamped sha,
  and `git cat-file -p <sha>:…` contains the row.
- *"The opencode door for the AP twin is stale or missing."* All three `-AP` masters have no
  opencode door, uniformly, and `workflow_lint --toolkit-only` owns door parity at 0 errors.
- *"A fourth surface (`opus-reviewer.md`) names no budget."* True, and **correct as it stands**: it
  loads the doctrine rather than invoking the engine, and it is a Stage-4 autopilot role, so
  `capped` — the default — is the right answer for it. The ruling is now recorded in the guard's
  comment so nobody re-derives it.

### Gates

| Gate | Command | Result |
|---|---|---|
| Enforcement suite | `python3 .agents/scripts/tests/run_all.py` | 23/23 files, **1891/1891**, exit 0 |
| Toolkit lint | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info, exit 0 |
| Maps | `python3 .agents/scripts/check_maps.py --depth3-only --strict` | exit 0 |
| Assertion evidence | re-ran the Step 2 RED assertions | GREEN — both caller cases pass |
| SOP currency | `sop_currency.py --paths $(cat …) --message …` | **both arms**: exit 1 without `[sop-ok]`, exit 0 with it |
| Link + anchor | every path and line anchor the diff names | all resolve; the 5 cited line anchors match their claimed content |
| Door parity | no command added/renamed/deleted | `workflow_lint` green; `.opencode` copies regenerated and carry the row |

⚠️ **The SOP gate's first run was a false green** — `--paths $CHANGED` unquoted in `zsh` arrives as
**one** argument, so the gate checked nothing and exited 0. Re-run with `$(cat …)`, `argc` printed
as proof, and only then were both arms real. That is the trap `/smh-code-review` Step 0.7 warns
about, hit inside the review that quotes the warning.

### Step 0.7 — blast radius re-derived against current `main`

1. **Nothing this diff references moved.** `main` has not advanced since the merge-base
   (`0677441`); `git diff $BASE..main` is **0 files**.
2. **True overlap: none. `merge-tree` is clean** (returns a tree sha, no conflict messages).
3. **Sibling lane: `chore/SCC-148-incident-guard` is live**, holding `task_preflight.py`,
   `git-policy.md`, `scripts/INDEX.md`, its test, and its own artifact folder. **Zero overlap with
   this lane's code.** ⚠️ But both lanes must append a row to `_artifacts/_main/INDEX.md`, so that
   **ledger will conflict at the second merge** — resolved by **keeping both rows**, exactly as
   SCC-145 and SCC-129 did. Landing order is otherwise free in either direction.

### Clean-Code Gate (`/smh-clean-code-audit`, Step 3.5)

Machine floor, all bare: `run_all` exit 0 · `workflow_lint --toolkit-only` exit 0 · `sop_currency`
proven on both arms · `python3 -m py_compile` on the changed guards exit 0 · link+anchor sweep all
resolving. Judgment pass over the SOP conventions, importing Step 1's drift findings rather than
re-hunting: **no new findings.** The comment contract is met the way this repo means it — every
comment added states a constraint the code cannot show (which mutant a regex clause kills, and why
the fixture row is pinned when its neighbours are existence-only), not a restatement of the line
below it. No TODO, no dead code, no reformatting of untouched lines.

### Mutation evidence — the reviewer's own sweep

`red-04-review-mutation-sweep.txt`: **11 mutants declared, 11 killed, 0 survivors**, tree restored
clean. The four that mattered are M5/M6/M7 (RELOCATE: appendix, HTML comment, fenced block), M8
(inversion inside the cell), M9 (a contradicting second row), M10 (an unpinned fourth caller) and
M11 (the control's own budget) — every one of which **survived** before the fixes.

⛔ **`RESTORE` is done from COPIES, never `git checkout --`.** This lane was bitten by that twice:
once in the original removal proof and again during the review's own first sweep, each time because
`git checkout` restores from `HEAD` and the fix being defended was still uncommitted, so the
"restore" silently reverted the fix instead of the mutation. The second occurrence is what proves
the first was a design flaw in the procedure rather than one careless moment — the tell both times
was the sweep's closing "everything restored, must be green" line coming back **red**, which is the
only reason either was caught.
