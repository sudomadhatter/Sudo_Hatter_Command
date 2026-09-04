# SCC-163 — walkthrough

**Lane:** `chore/SCC-163-gate-hardening` · **Base:** `main` @ `8ae2e25` · **LANE: LOCAL**
**Plan:** [implementation_plan.md](implementation_plan.md) — `Audit verdict: GO`, approval *"approved"* @ `12efa6d`
**Two gate defects, one branch**, per the operator's scope ruling: *"add it to the SCC-163 I want to
keep as much on one ticket as possible."* They share no files, so each proved independently.

## Task Checklist

- [x] **A1** RED first: a case reproducing `chore ← epic` by fast-forward, seen failing
- [x] **A2** the push is REFUSED and prints the standard banner
- [x] **A3** `refs/heads/epic` covered; the `:105` ref filter **documented as a ruled omission**
- [x] **A4** no regression on the four ALLOW pairings — `epic←main`, `epic←story`, `story←epic`, `main←epic`
  - ⚠ `EP2` had to be re-fixtured to an **unpushed** epic, or it passed against its own mutant
- [x] **A5** mutation sweep drawn from the code, declared in the plan before code existed
- [x] **B1** RED first against a **real corpus**; AVCH-58's pre-correction section caught
  - ⚠ the fixture lives at `9674880d` in **AGY_AVIATIONCHAT** — vendored, not fetched
- [x] **B2** flags rows asking the operator to create / place / rule on ticket work
- [x] **B3** does **not** flag the three allowed classes — the hard part, and the corpus proved why
- [x] **B4** fenced examples are not rows; `_unfenced` reused, not re-derived
- [x] **B5** status-note rows declared out of scope **in the code**
- [x] **B6** mutation sweep drawn from the code
  - ⚠ the sweep harness itself scored two crashed suites as survivors — fixed, re-run
- [x] SOP + `scripts/INDEX.md` + `_artifacts/_main/INDEX.md` landed with their surfaces

## Evidence

HEAD at implementation: **`918f15f`**. Every assertion below drives the real script or the real
function and reads its verdict; the one structural pin reads **executable lines only**.

### A — the backstop was blind to `epic/*`

**RED** (`test_git_hooks.py --case "EP · …"`, before a line of the fix existed) — 6/12, and the
reproduction is the ticket's, exactly:

```
 * [new branch]      chore/SCC-163-lane -> chore/SCC-163-lane
[FAIL] EP1 · ...and nothing reached the remote: b57c54ae…  refs/heads/chore/SCC-163-lane
[FAIL] EP1 · a chore lane carrying an UNLANDED epic is REFUSED
[FAIL] EP1 · ...and the refusal names the epic
[FAIL] EP1 · ...and prints the standard banner
[FAIL] EP6 · the epic enumeration is keyed to chore/* only
[FAIL] EP6 · ...and the omission is documented with its reason
-- 6/12 passed --
```

The five ALLOW controls (`EP2`, `EP2b`, `EP3`, `EP4`, `EP5`) passed here **and** after — that is
what makes them controls rather than tests of the fix.

**GREEN** — `12/12`, and the whole file `129/129 → 141/141`, exit 0.

**The fix is four words in a `case`, and all the difficulty is in why it is not one word in the
`for`.** Three arms of `merge-target-guard`'s own judge table (`target:source`) say an epic inside a
lane is legitimate:

| pairing | verdict | consequence |
|---|---|---|
| `chore:epic` | **refuse** | the defect — must enumerate |
| `story:epic` | allow | a story lane absorbing its own epic **is** `/cicd-park`, run daily |
| `incident:epic` | allow | *"absorbing main (or an epic) is the everyday mid-incident move"* |
| `epic:story` / `main:epic` | allow | pushed ref is `epic/*` or `main` — declined at the ref filter |

So the enumeration is keyed on the lane class, mirroring the `BASES` switch beside it: `chore/*` only.

> ⚠️ **`EP2` was re-fixtured mid-build, and the reason is the case's whole value.** Written with the
> epic pushed to `origin`, a blanket widening *still* scores `landed=1` through the `claude/*` arm of
> the `BASES` switch — so the control would have passed against **the exact mutant it exists to
> kill** (A-M2). With the epic local, `BASES` is `origin/main` alone and only the lane-class arm keeps
> it green. `EP2b` keeps the pushed shape as a second control.

**The `:105` omission is ruled, not overlooked** — operator: *"A3. no we dont need it."* `epic:chore`
and `epic:epic` remain escapable by fast-forward. Both are named in the script with the reason:
judging a pushed epic needs a **third** candidate set that *excludes* `claude/*`, because stories
landing on the epic is what an epic IS, and a false red there sits on `/cicd-push-e2e`. `EP4` pins
the current behaviour so a later widening goes red and explains itself.

### B — `## Your Actions` was prose

**RED, twice, and the first one was not good enough.** The bare run raised
`AttributeError: module 'jira_feed' has no attribute 'banned_action_rows'` — honest, but it kills the
file before any assertion, and `red-test-can-die-before-its-assertion` says read *which line raised*.
A no-op stub produced the real red:

```
[FAIL] B1 · AVCH-58 row 1 (fold into AVCH-54 / mint its own key) is FLAGGED
[FAIL] B4 · 'Mint a ticket for the N deferred items' is FLAGGED
[FAIL] B5.1x / B5.2x / B5.3x · a REAL banned row from the same corpus IS flagged
[FAIL] B7 · finish prints the banned-row banner
[FAIL] B9 · check-actions reports the fixture's one banned row
-- 212/220 passed --
```

Every **positive** failed; every **negative control** passed vacuously on a detector that does
nothing — which is exactly why the positives carry the proof.

**GREEN** — `197/197 → 221/221`, exit 0.

**⭐ The corpus was measured before the rule was written, and it changed the design.**
`open_actions()` over every `.md` in `_artifacts/`: **101 walkthroughs carry the section, 25
unchecked rows.** The ticket's B2 phrase list, read literally, flags **8 of 25 — at most 4 real**:

| row | naive | correct | why |
|---|---|---|---|
| `**SOP-nag ticket … your call**` | FLAG | **FLAG** | proposes a residue ticket |
| `Decide whether finding 13 earns a ticket` | FLAG | **FLAG** | the banned shape, by name |
| `**File the follow-on Task** …` | FLAG | **FLAG** | the banned shape, by name |
| `**Rule the landing order.**` | FLAG | **allow** | merge sequencing |
| `**Decide whether the CONCERNS is worth clearing…**` | FLAG | **allow** | a product decision |
| `**Rule on A1** / `A2` / `A6`` | FLAG | **allow** | acceptance disputes — the operator's own call |

All four false positives are things Step 5 **permits**. So a bare verb is never a trigger: the
detector fires on **verb × ticket-work object**, and a bare ticket key is deliberately not an object
(`"Merge AVCH-59 to main"` and `"Move SCC-99 to Done"` both carry one and are both allowed). The
seven real allow-rows are pinned as negative controls; three real banned rows from the same corpus
are pinned as positives, so the suite cannot pass by never firing.

**Arming, per the ruling *"1. yes"*:** `finish` prints a `⛔ BANNED ACTION ROW` banner and **holds
exactly as before** — the verdict is unchanged, the diagnosis is new. `--strict-actions` refuses and
**ships disarmed**. A block here would fire *after* the merge, trading a held ticket for an erroring
close-out.

### Two vacuous greens, both caught by the reds themselves

1. **`B8` passed before the flag existed.** `--strict-actions` was undefined, so argparse exited 2 on
   *unrecognized arguments* — the same 2 a real refusal returns. `code == 2` was satisfied by the
   feature **being absent**. Now paired with the banner, plus a clean-input half proving the flag
   discriminates rather than blanket-refusing.
2. **The mutation harness scored two crashed suites as survivors.** It counted `[FAIL]` lines and
   ignored the exit code; `B-M3`/`B-M4` crashed the suite (`AttributeError` at `B5.1`) and emitted
   zero `[FAIL]` lines, so a *killed* mutant read as *survived*. The kill signal is now the **exit
   code** — the same `piping-a-gate-hides-its-exit-code` shape, aimed at the tool meant to catch it.

### Mutation sweep — 8/8 killed, 0 survivors, 0 defective, tree CLEAN after restore

Declared in the plan **before code existed**, drawn from the fix's own lines, run as one sweep.

| # | Mutant | Killed by |
|---|---|---|
| A-M1 | drop `refs/heads/epic` from the chore arm | `EP1` |
| A-M2 | blanket widening (move it into the bare enumeration) | `EP2`, `EP3` |
| A-M3 | retarget the arm `chore/*)` → `claude/*)` | `EP1` |
| A-M4 | widen the `:105` filter to accept `refs/heads/epic/*` | `EP4`, `EP6` |
| B-M1 | defeat fence stripping in `_unfenced` | `B6` |
| B-M2 | add a bare ticket key to `_TICKET_OBJECT` | **`B5.1/B5.3/B5.5` — the live corpus only** |
| B-M3 | drop the object requirement (`if verb`) | crash at `B5.1` |
| B-M4 | drop the verb requirement (`if obj`) | crash at `B5.5` |

> ⭐ **B-M2 is the one worth reading.** It was declared to be killed by `B2`/`B3` — the ticket's own
> named negative controls — and it **was not**. "Merge" and "Move" are not banned verbs, so a
> bare-key object never reaches those rows. The only cases that catch it are the **real corpus rows**
> pinned in `B5`. Without the corpus work, that mutation would have shipped undetected.

## Code Review (2026-08-15)

Verdict: CONCERNS @ eb9030b
Suite evidence measured on: eb9030b — `run_all.py` **PASS exit 0, 92.4s**, receipt `gates/suite.json` stamped CLEAN

**Scope** — the 12-file `main...HEAD` diff: the backstop hook, `jira_feed.py`, their two test files, a
vendored fixture, `scripts/INDEX.md`, the SOP, and this lane's artifacts.
**Method** — Step 0.7 re-derivation against current `main`; adversarial pass; acceptance audit against
SCC-163's own ACCEPTANCE A/B blocks; the command-centre gate; `/smh-clean-code-audit`'s machine floor;
a 9-mutant sweep.

### ⛔ Why this is CONCERNS and not PASS — the blind pass did not run

`lenses_run: 0/4 — Blind Hunter dead · Edge Case Hunter dead · Acceptance Auditor dead · Test-Adequacy dead`

Four clean-context lenses were dispatched on the diff at `8681d83`. **All four returned empty; none
executed.** This is the same failure SCC-162's merge commit records ("the code-review-engine lens
fan-out could not spawn clean-context agents in this session"), making it the **second confirmed
instance**.

Per `code-review-engine/steps/step-01-review.md:398`, a lens still dead after the retry and the
inline rerun **raises `severity_floor` to CONCERNS**, and the caller may escalate but never soften.
So this verdict is the floor, not a judgement call.

An inline adversarial pass **was** run and it found three real defects (below, all fixed). It is
recorded as an inline pass and **not** as the blind one: `step-01-review.md:372` — *"Reporting a
fully-informed lens as the blind one is a false record."* I wrote this code; reviewing it with full
context is exactly the bias the Blind Hunter exists to remove.

⭐ **Nothing in this repo would have caught that.** `closeout_preflight.py` reads the `Verdict:` line
and nothing about lenses; the only thing touching `lenses_run` is a prose pin on the skill document.
A `Verdict: PASS @ <sha>` with zero lenses run merges cleanly today. Recorded as **SCC-164 Part E**
(E1–E7) on the operator's ruling, *"yes we need to fix it… this is not the first time you have done
this."*

### Findings

| # | file:line | sev | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `jira_feed.py` `_BANNED_VERB`/`_TICKET_OBJECT` | **FAIL-class** | Verb and object were searched **independently**, so `open`/`file` matched as NOUNS. Four honest rows flagged: *"The SCC-99 ticket is still open"*, *"Ticket SCC-12 remains open"*, *"Open the ticket and read the Dev Record"*, *"The task file is in `_artifacts/`"*. A false red here teaches agents to stop writing honest rows — the precise cost B3 warns about. | **applied @ 8681d83** — bound into one phrase; `open` dropped from the creation verbs; pinned as `B10.1–B10.4` |
| 2 | `test_jira_feed.py` (coverage) | **FAIL-class** | Deleting the `fold … into <KEY>` pattern left the suite **green** — the only row exercising it also said *"board placement"* and kept flagging through a different pattern. A shape acceptance **B2 names by name** was invisible to deletion. Found by a surviving mutant, not by reading. | **applied @ 8681d83** — `B11` pins all six shapes individually |
| 3 | `jira_feed.py` `_BANNED_PATTERNS[0]` | **FAIL-class** | `B11` then went red on the real thing: **`"mint its own AVCH key"`** — the exact AVCH-58 phrase this ticket exists to catch — never matched the creation pattern. The project token `AVCH` sat between the article and the noun. Row 1 still flagged via `board placement`, which is *why it went unnoticed*: the known-positive passed while the shape it was meant to prove did not. | **applied @ 8681d83** — `(?:[A-Z]{2,10}\s+)?`, all-caps only; *"file the report about the ticket"* probed and still allowed |
| 4 | `test_jira_feed.py` `B8` | **CONCERNS** | `B8` passed **before `--strict-actions` existed**: argparse exits 2 on an unrecognized argument, the same 2 a real refusal returns, so the assertion was satisfied by the feature being **absent**. | **applied @ 918f15f** — exit code paired with the banner, plus a clean-input half proving it discriminates |
| 5 | mutation harness (scratchpad) | **CONCERNS** | The sweep counted `[FAIL]` lines and ignored the exit code, so two mutants that **crashed** the suite emitted zero `[FAIL]` lines and scored as **survivors**. A vacuous green in the tool brought to prevent vacuous greens (`piping-a-gate-hides-its-exit-code`). | **applied** — kill signal is now the exit code |
| 6 | `test_git_hooks.py` `EP2` | **CONCERNS** | `EP2` was first written with the epic **pushed**. A blanket widening still scores `landed=1` through the `claude/*` arm of the `BASES` switch, so the control would have passed against **the exact mutant it exists to kill** (A-M2). | **applied @ 918f15f** — re-fixtured to a local epic; `EP2b` keeps the pushed shape |
| 8 | `jira_feed.py:1408` | **FAIL-class — shipped** | ⛔ **A mutation-sweep mutant (B-M5) was COMMITTED AND PUSHED into the gate** at `8681d83`. The sweep applies a mutant, runs the suite, and restores in a `finally`; that restore did not hold. B-M5 strips the ticket-noun clause from pattern 5, so the detector fires on a bare *"rule on"* / *"decide"* — the exact false-positive class findings 1–3 were spent killing. It would have flagged every honest acceptance dispute. **Caught only by the full suite**; every scoped run I used while iterating skipped the `B5` corpus block. This is the live instance of `tests-must-gate-for-real`'s written warning that *"a mutated gate is committable."* | **applied @ eb9030b** — restored, 231/231, and the rest of the diff swept by signature for other stranded mutants (none) |
| 7 | `pre-push-merge-backstop.sh` `$SCOPES` | **noise — dismissed** | Unquoted `$SCOPES` relies on word-splitting. Considered and cleared: the enclosing `for other in $(git for-each-ref …)` already depends on the identical sh semantics, so this adds no new dialect risk; the hook is `#!/bin/sh`. | dismissed — no new exposure |

**Changes applied: 7 of 8 findings fixed in thread** (finding 7 dismissed with reason). Nothing left this lane as future work.

### Acceptance matrix

| item | delivered by | proving assertion |
|---|---|---|
| A1 RED first | `EP1` | seen RED: push exit 0, `chore/SCC-163-lane` on the remote — the ticket's reproduction |
| A2 refused + banner | `EP1` ×3 | REFUSED, names `epic/SCC-163-thing`, prints the standard banner |
| A3 epic covered; `:105` ruled | `SCOPES` chore arm + the `:105` comment | `EP6` ×3 — wiring read from **executable lines only** |
| A4 no regression, 4 ALLOW arms | `EP2`, `EP2b`, `EP3`, `EP4`, `EP5` | green before **and** after; A-M2 kills them |
| A5 sweep from code | A-M1…A-M4 | declared in the plan pre-code; 4/4 killed |
| B1 RED, real corpus | `B1` ×3 | AVCH-58 vendored from `9674880d` (AGY repo); row 1 flagged, rows 2–3 not |
| B2 flags create/place/rule | `B4`, `B5.1x–B5.3x`, `B11` ×6 | each of six shapes pinned **alone** |
| B3 the three allowed classes | `B2`, `B3`, `B5.1–B5.7`, `B10.1–B10.4` | 7 live-corpus rows + 4 probe rows unflagged |
| B4 fenced ≠ rows | `B6` | reuses `_unfenced`; B-M1 kills it |
| B5 status notes out of scope | code comment + `B1` rows 2–3 | stated in the code, proved by the fixture |
| B6 sweep from code | B-M1…B-M5 | 5/5 killed |

**Reverse direction — scope creep:** none. The one step that traced to no acceptance item (an
authoring-time call site in `/smh-code-review` Step 5) was cut at plan time as audit finding B-F1.

### Gates

| gate | result |
|---|---|
| Enforcement suite | `run_all.py` → **29/29 files, exit 0, 92.4s @ eb9030b**. ⚠ It went **RED at `8681d83`** and that red is what surfaced finding 8 — the receipt doing its job |
| Toolkit lint | `workflow_lint.py --toolkit-only` → **0 errors, 0 warnings**, 8 info (pre-existing BOMs) |
| Assertion evidence | `EP1–EP6` 12/12 · `test_jira_feed.py` 231/231 (197 baseline → +34) · `test_git_hooks.py` 141/141 (129 baseline → +12) |
| SOP currency | landed with its surfaces at `918f15f`, **no `[sop-ok]`**; later commits are artifacts-only |
| Link + anchor | `check_maps.py --depth3-only --strict` → exit 0 |
| Door parity | n/a — no command added, renamed or deleted |
| Mutation sweep | **9/9 killed, 0 survivors, 0 defective**; tree CLEAN after restore |

### Step 0.7 — re-derivation against current `main`

1. **What moved:** `origin/main` is unchanged at `8ae2e25`; this lane is 7 ahead / 0 behind. But
   **local `main` = `7dcf558`, ahead of origin and unpushed** — `chore/SCC-169-keyway-quickstart`
   merged into it mid-lane. ⛔ This **supersedes this lane's own committed audit line** *"Sibling
   lanes: none"*, which was true when written and false hours later.
2. **True overlap + merge-tree:** `_artifacts/_main/INDEX.md`, and `git merge-tree` confirms a real
   **CONFLICT** — both lanes add a ledger row at the top of the same table. Resolve by keeping both.
   ⚠ Comparing against `origin/main` alone reported **zero** overlap and missed it entirely.
3. **Landing order:** local `main` carries an unpushed SCC-169 merge. **Local `main` was deliberately
   NOT absorbed** — doing so would pull that unlanded work into this chore lane, and *this ticket's
   own Part A* would then correctly refuse the push. The gate would be right. The lane stays based on
   `origin/main`; the `INDEX.md` conflict is resolved at close-out.

## Your Actions

- [ ] **Merge and close out** — `/smh-close-task-merge-tree --expect-key SCC-163`. Invoking it is
      the per-merge sign-off; one invocation, one merge. The lane is pushed and clean.

*(Nothing else is owed. Part A's `:105` omission and Part B's status-note exclusion are both ruled
and recorded in the code — they are settled decisions, not open items, and per this ticket's own
Part B they would be banned rows if written as ones.)*
