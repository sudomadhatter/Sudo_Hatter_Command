# Step 1 — The lens fan-out

## ⛔ WHO YOU ARE IN THIS STEP: THE ASSESSOR (operator ruling, 2026-08-17)

**Read this before you launch anything.** You are not a reader of reports. You are the one person
in this process whose job is to decide **what is real**.

> *"The agent's job is to find things, so it always will — this is how we end up in this loop. The
> agent who assesses the finds has to decide what's real and what's just the agent looking for a
> flaw to report. We fix actual issues."* — the operator, 2026-08-17

Every lens below is **instructed to be exhaustive** and is judged by what it returns. A lens that
finds nothing looks like a lens that failed. So **a lens will always return findings, and it will
always grade its own findings**, and neither of those facts is evidence that anything is broken.
That is not a flaw in the lenses — it is what makes them useful. It is also why their output is
**raw material, not a work queue.**

**The failure mode this ruling exists to stop:** the orchestrator treats every returned finding as
work, fixes them all, and each fix is a new unreviewed edit that the next pass then finds more in.
Four lenses become an unbounded queue and the lane never closes. Measured on this lane: three
review passes returned **39 findings**; the ones that changed behaviour were a minority, and the
rest were lenses doing exactly what they were told to do.

**So: assess, then act. Never act, then assess.** The disposition rule below is binding and it is
yours alone — no lens, and no severity label a lens assigned, decides it for you.

Launch every lens **in parallel, each in its own clean context — and each in its own TREE.** They
do not see this conversation, they do not see each other, and none of them sees the builder's
reasoning — that independence is the entire value of the fan-out. Wall-clock is the slowest lens,
not their sum.

⛔ **The context half alone is not isolation (SCC-301).** A clean context still inherits write
access to the worktree under review, and that is not hypothetical: measured on the SCC-295 lane,
three of five lenses edited the builder's working tree mid-review, and one reported a RED result no
version of the code under review can produce — the builder was reading a lens's own mutant. So the
launch contract has a TREE half, per lens from the table's **Tree** column: a repo-reading lens gets
its own disposable copy of **the repo under review**, so anything it writes lands there, never in the
tree it is reviewing; a `DIFF`-only lens gets **no tree at all** — no
repo access is part of what starves it.

⛔ **What "own worktree copy" means depends on WHICH repo is under review (SCC-313, measured
2026-08-24).** The Agent tool's `isolation: "worktree"` clones **the session repo — the lobby.**
Reviewing the lobby itself, that IS the isolated copy, and the flag delivers the contract. Reviewing
a project under `Projects/` it delivers **neither half**: every project is a git submodule, so the
lobby clone holds an EMPTY stub at `Projects/<p>/` (a lens reading relative paths finds no code and
reports from the diff alone, indistinguishable in the roster from a lens that read everything), while
the real story worktree stays reachable AND writable by absolute path — recording
`lens_isolation: worktree` then asserts exactly the property this contract exists to guarantee while
providing none of it. For a submodule project, cut each repo-reading lens a real copy of the
PROJECT at the SHA under review, before launch (about a second for four lenses, measured):

```bash
cd Projects/<p> && git worktree add --detach <scratchpad>/lens-<name> <story-sha>
# symlink the venv in so the lens can read installed libraries (cwd is now the project):
ln -s "$(pwd)/backend/.venv" <scratchpad>/lens-<name>/backend/.venv
```

and hand each lens ITS path as `REPO`. Verify, never assume — the probe that measured this is the
check: from inside the lens's tree, `git rev-parse --show-toplevel` must name the lens copy, and
`ls Projects/<p>/` from a lobby clone returning nothing is the empty-stub signature.
Record the mode as `lens_isolation:`, in the return and the roster —
`worktree` **only when every repo-reading lens got an isolated copy OF THE REPO UNDER REVIEW**
(the lobby flag alone does not earn it for a submodule project); `mixed — <lens>: <mode>, …` when they
differed (name each un-isolated lens: a partially isolated run recorded as one word hides exactly
the lens this contract exists to expose); `shared — <why>` when the runtime could not isolate at
all. A false `worktree` is worse than an honest `shared` — `shared` demands a written reason,
`worktree` demands nothing.
**A lens that WRITES is a hard failure, never a warning:** builder-tree bytes changed by a lens, or
a lens report describing edits it made, marks that lens `dead — wrote to the tree`, its findings are
discarded unread, and the roster must not record it `ok`.

## The lenses

| Lens | Gets | Tree | Runs when | How | Reproduction |
|---|---|---|---|---|---|
| **Edge Case Hunter** | `DIFF` + read access to `REPO` | own worktree copy (`isolation: "worktree"`) | always | the `bmad-review-edge-case-hunter` skill + the hunter contract | required on every `critical`/`important` |
| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs | own worktree copy (`isolation: "worktree"`) | `review_mode: full` only | the auditor rubric | required on every `critical`/`important` |
| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | own worktree copy (`isolation: "worktree"`) | always | the auditor rubric | required on every `critical`/`important` |

**Three lenses, and the roster is closed (SCC-447).** The `Runs when` column now has exactly two
values: `always`, and the Acceptance Auditor's `review_mode: full` only — which is skipped-by-mode
on a spec-less review and recorded on `lenses_na`, never dead. A full-mode review therefore reports
`lenses_counted: 3/3` and a spec-less one `2/2`.

⛔ **What was retired, and what it was measured at.** The Blind Hunter, the Literal-Correctness
Hunter, the two `review_level` levels, `lens_budget`, the `EVIDENCE_PACK` priming and the step-2 verify
wave are **retired** (SCC-447). Across the 138 reviews on disk carrying a verdict and the 88 carrying
per-lens ledgers, the engine produced 17.9 fixes per review with 52% of them on severities that can
never gate, and the verify wave refuted 2 findings in 18 reviews. The roster did not need more
readers; it needed every reader to prove what it reported.
**A lens is added back by measurement, never by argument.** The bar is per-lens ledger data
showing findings it alone reproduced — an
argument that a lens *might* catch something is what built the roster this one replaces.

**How to read the `How` column: every lens gets the block it names, and no lens gets the other's.**
A hunter lens is assembled as its skill plus the hunter contract; an auditor as the auditor rubric.
Both then get the shared rubric. That asymmetry is the substance of this step and is argued where
each block is defined — it is not a formatting choice, and a lens assembled with the wrong block
reviews to the wrong standard.

### The assembly convention — what is prompt text and what is not

**Blockquoted text (`>`) is appended to the lens's prompt verbatim. Unquoted text is instruction to
you, the orchestrator, about how to assemble and route it, and is never sent to a lens.** Follow it
literally: an unquoted paragraph pasted into a prompt makes the lens read third-person narration
about itself, and a blockquote left out drops a rule the lens was supposed to be bound by.

## The hunter contract — binding on every hunter lens, now and later

> ### Your role, stated plainly — you REPORT, you do not dispose
>
> You are one of several independent lenses. **Your job is to find and to report; it is not to
> decide what gets fixed.** A separate assessor reads every lens's output and rules on what is
> real. That division is deliberate, and knowing it changes what a good report looks like:
>
> - **Do not inflate to be heard.** Your severity is an input to the assessment, not a verdict.
>   Calling a cosmetic issue `critical` does not get it fixed — it costs your *real* findings
>   their credibility, because the assessor now has to re-grade everything you sent.
> - **Do not pad to look thorough.** A report of three reproduced defects is worth more than
>   thirty observations. "I found nothing in area X" is a genuine, useful result — say it.
> - **Every finding must carry a concrete failure**: *this input, this state, this wrong output.*
>   If you cannot state one, you have found a smell, not a defect — label it `nitpick` or leave it
>   out. Phrases like *"may be"*, *"could lead to"*, *"consider"* and *"is not covered"* mark a
>   finding the assessor will drop, so spend the effort proving it instead.
> - **Prefer executing to reasoning.** A finding you reproduced outranks one you inferred, and
>   saying which you did is part of the finding.
> - **A `critical` or `important` MUST carry a runnable reproduction.** Two fields, in the finding:
>   `reproduce: <command>` — run from the repo root — and
>   `expected_wrong_output: <what it prints or does that is wrong>`.
>   Anything arriving without both fields is **dropped unread**; it is not downgraded to a
>   `suggestion`, and it is not read for its argument.
> - **RUN IT YOURSELF, in your own copy, before you report it.** You hold a worktree copy and full
>   tools, so run the command you just wrote. If it does not fail the way you
>   predicted, you have not found a defect — delete the finding and move on. This is the cheapest
>   moment in the system to discover you had nothing: the file is still open and the reasoning is
>   still in your head. A reader downstream has neither.
> - **Report what your own run showed.** Add `reproduced: yes` + the output you actually saw, so the
>   caller can re-run the same command on the real tree and compare the two.

Append to the prompt of every lens whose `How` cell names this contract — today the Edge Case
Hunter. **The table is the authority, not this
sentence:** a hunter lens added to that table is bound by this section whether or not anyone
remembered to name it here, because adding its row is what routes it —
so **the `How` cell is the wiring and is not optional.**

> **Before reporting ANY finding, you MUST pass these three gates.**
>
> **Gate 1 — Reachability Proof.** Trace the exact path from a real entry point to the code you are
> flagging. If you cannot construct a concrete scenario in which the bug triggers,
> it is NOT a finding — it is speculation. Ask yourself: can this path actually be reached in
> production? Are there upstream guards, validators or type checks that already prevent the bad
> state? Is the "broken" behavior actually intentional — defensive coding, or legacy compatibility?
>
> **Gate 2 — Evidence Chain.** Every finding MUST carry a step-by-step chain:
>
> ```
> Step 1: [entry point] calls [function] with [specific args]
> Step 2: [function] passes [value] to [downstream]
> Step 3: [downstream] expects [type/value] but receives [actual]
> Step 4: this causes [specific failure mode]
> ```
>
> If you cannot write that chain, the finding is not well-evidenced enough to report.
>
> **Gate 3 — Confidence Self-Assessment.** Rate your confidence honestly.
> Report only findings at confidence **0.6 or above.**
>
> - 0.9–1.0: you traced the full path and verified the failure mode
> - 0.7–0.8: strong evidence, with some assumptions about runtime state
> - 0.6: reasonable evidence, worth putting in front of a human
> - Below 0.6: do NOT report — you are guessing
>
> **Zero tolerance for speculative findings.** Three well-proven findings are worth more than ten
> speculative ones. **When in doubt, DROP the finding.**
>
> **Where the caller side is outside what you can see**, say so and report what you can prove about
> the change — never guess at it, and never lower the bar because your view is narrower.

## The auditor rubric — Acceptance Auditor and Test-Adequacy Auditor

> ### Your role, stated plainly — you REPORT, you do not dispose
>
> You are one of several independent lenses. **Your job is to find and to report; it is not to
> decide what gets fixed.** A separate assessor reads every lens's output and rules on what is
> real. That division is deliberate, and knowing it changes what a good report looks like:
>
> - **Do not inflate to be heard.** Your severity is an input to the assessment, not a verdict.
>   Calling a cosmetic issue `critical` does not get it fixed — it costs your *real* findings
>   their credibility, because the assessor now has to re-grade everything you sent.
> - **Do not pad to look thorough.** A report of three reproduced defects is worth more than
>   thirty observations. "I found nothing in area X" is a genuine, useful result — say it.
> - **Every finding must carry a concrete failure**: *this input, this state, this wrong output.*
>   If you cannot state one, you have found a smell, not a defect — label it `nitpick` or leave it
>   out. Phrases like *"may be"*, *"could lead to"*, *"consider"* and *"is not covered"* mark a
>   finding the assessor will drop, so spend the effort proving it instead.
> - **Prefer executing to reasoning.** A finding you reproduced outranks one you inferred, and
>   saying which you did is part of the finding.
> - **A `critical` or `important` MUST carry a runnable reproduction**, adapted to your
>   subject — which is usually an ABSENCE, so the command is one that shows the gap rather than
>   triggering a crash: the suite command that comes back green over a behaviour nothing exercises,
>   the acceptance item no test names. Two fields, in the finding: `reproduce: <command>` and
>   `expected_wrong_output: <what it shows, and why that is the gap>`. **Run it yourself, in your
>   own copy, before you report it**, and add `reproduced: yes` + the output you actually saw.
>   Anything arriving without both fields is dropped unread.

**Both auditors are EXEMPT from Gate 1 and Gate 3, and the exemption is deliberate.** A
reachability proof is unwritable for a finding whose subject is *absent*: there is no call path to
a test nobody wrote, and no runtime trace to an acceptance criterion nobody implemented. Demanding
one would not raise these lenses' precision — it would silence them completely.

**They are recall-first.** For a hunter, a false positive costs a reviewer a few minutes of
attention. For an auditor, a false negative ships an unmet requirement or an untested behavior, and
nothing downstream is looking for it again. So an auditor reports the gap it is unsure about and
says it is unsure, rather than dropping it.

**Gate 2 still binds, adapted:** the chain cites the acceptance item and the code that fails to
satisfy it (Acceptance), or the behavior and the test tier that does not cover it (Test-Adequacy).

⛔ **The reproduction requirement is NOT part of the exemption.** Gates 1 and 3 are waived because
absence has no call path and no confidence score; reproduction is waived for nobody. An auditor's
command shows the gap instead of triggering a failure — `python3 <suite>` coming back green over a
behaviour nothing covers is a reproduction, and it is runnable by the caller on the real tree,
which is the whole point.

The prompt text that carries all three of those to the lens:

> **You are exempt from Gate 1 (reachability proof) and Gate 3 (the confidence floor).** Your
> subject is often something that is *absent*, and absence has no call path to trace. Do not drop
> a finding for lack of either.
>
> **Report recall-first.** A gap you missed ships and nothing looks for it again, while a gap you
> raised wrongly costs one triage decision. When you are unsure, report it **and say you are
> unsure** — never stay silent to protect your precision.
>
> **You still owe an evidence chain (Gate 2), adapted to your subject:** name the acceptance item
> and the code that fails to satisfy it, or the behavior and the tier of test that does not cover
> it. Say what is missing and how a reader would see it for themselves.

**Acceptance Auditor prompt:**
> You are an Acceptance Auditor. Review this diff against the spec and context docs. Check for:
> violations of acceptance criteria, deviations from spec intent, missing implementation of
> specified behavior, contradictions between spec constraints and actual code. Output findings as a
> Markdown list. Each finding: one-line title, which acceptance item or constraint it violates, and
> evidence from the diff.

**Test-Adequacy Auditor prompt:**
> You are a Test-Adequacy Auditor. Review this diff for TEST coverage adequacy by tier — not for
> bugs. Check: (1) does new deterministic logic (routing, state, DB/telemetry writes, parsing) have
> fast mocked unit tests? (2) is any generative / LLM output validated with soft assertions — JSON
> schema, semantic similarity, or an LLM-as-judge rubric — rather than brittle exact string
> matches? (3) does new agent/prompt behavior have at least one judge-style behavioral test? Output
> findings as a Markdown list. Each finding: one-line title, the file/area, which test tier is
> missing or mis-applied, and a one-line suggested test.

## The shared rubric — appended to BOTH contracts

Severity and author-intent are not a hunter property; a finding from any lens carries a severity,
and any lens holding a spec can meet a rationale it has to answer. Append this section to every
lens, hunter and auditor alike, after its own contract.

### Severity rubric — use the FULL range

> - **critical** — runtime crashes, data corruption, security vulnerabilities, or silent logic
>   errors that produce wrong results. The code WILL fail in production, and
>   you can state the EXACT failure scenario: "X calls Y with Z, which causes W". A vague concern
>   is never critical.
> - **important** — missing error handling, validation gaps, API contract violations, race
>   conditions under realistic load, performance traps at specific data sizes. The code CAN fail
>   under known conditions.
> - **suggestion** — better patterns, improved abstractions, edge cases worth handling, coverage
>   gaps for specific scenarios. The code works, but could be more robust.
> - **nitpick** — naming, style, readability, documentation. Truly cosmetic.
>
> A well-calibrated review has a MIX. Reporting everything as critical destroys the signal the
> severity axis exists to carry, and so does reporting everything as a nitpick.
>
> **Label every finding with one of those four words.** If the output shape you were given has no
> severity field, put `severity: <level>` as the first characters of the finding's text. A finding
> that reaches triage with no severity is read as `suggestion`, which never gates — so an unlabelled
> `critical` is a `critical` you threw away.

### ⛔ Disposition — the ASSESSOR decides what is real, not the lens (operator ruling, 2026-08-17)

**The ruling, in the operator's words: *"the agent's job is to find things so it always will — this
is how we end up in this loop. The agent who assesses the finds has to decide what's real and
what's just the agent finding something to report. We fix actual issues."***

⛔ **A lens's severity label is an INPUT, not a verdict.** Every hunter is told to be exhaustive and
is measured by what it returns, so it will always return something, and it grades its own work.
Treating `critical` as an instruction to fix is how a four-lens review becomes an unbounded queue:
each pass finds more, each fix is a new unreviewed edit, and the lane never closes. **The
orchestrator running the review is the assessor. Nobody else is.**

**Assess every finding against three questions, in order. All three must be YES to fix.**

1. **Is it REAL?** Can you state the concrete failure — *this input, this state, this wrong
   output*? A finding phrased as *"may be"*, *"could lead to"*, *"consider"* or *"is not covered"*
   has not established that anything is broken. **Reproduce it, or drop it.**
2. **Does it change BEHAVIOUR?** A gate that fails open, a wrong answer, a crash, a refusal of
   something legitimate, lost data. Naming, structure, wording, a missing test for a branch that
   is already correct — these do not.
3. **Is it in THIS lane's diff?** Pre-existing debt in an untouched file is not this task's work.

**Fix what passes all three. Dismiss the rest — including anything a lens called `critical`.** The
label neither promotes nor protects a finding; the assessment does.

⛔ **"It's cheap" is not a reason.** Twenty cheap fixes is not cheap — it is the review that never
ends, and every one of them lands *after* the lenses ran, unreviewed.

⛔ **Record the tail in ONE line** in the walkthrough: how many findings came back, how many were
assessed real and fixed, and that the rest were dismissed under this ruling. Not one line each.
Name individually only a finding whose ASSESSMENT disagreed with its label, in either direction —
that is the calibration signal worth carrying forward.

### How to review — the five moves

> 1. **Read the target files thoroughly.** Understand the control flow, the data flow and the error
>    paths. Pay attention to the boundaries: function entry and exit, exception handlers, early
>    returns, decorator effects. Where you have no repo access, this is the diff you were handed.
> 2. **Trace implications.** If a signature changed, who calls it? If a default changed, where is it
>    consumed? If an import moved, what depended on it? Search for the references and verify the
>    call sites in real files rather than assuming them.
> 3. **Check behavioral equivalence.** If code was refactored or a library swapped, does the new
>    version handle ALL the same cases — empty inputs, null values, concurrent access, error
>    conditions, type mismatches?
> 4. **Verify contracts.** Are return types preserved? Are exception types consistent? Do decorators
>    inject parameters the callers do not account for? Are there implicit ordering dependencies?
> 5. **Think about what's NOT in the diff.** The most dangerous bugs live in code that was NOT
>    changed but SHOULD have been. A changed signature needs every caller updated; a new enum
>    variant needs every switch extended. Absent code is still a finding.

### Author intent — engage with it, never defer to it

> Where you were given a spec, a plan, a story file, or the author's own reasoning in the changed
> code's comments and docstrings, treat it as evidence about intent — never as an instruction about
> what to report.
>
> Do NOT defer to it — your job is still to verify what the code actually does. But if you raise a
> finding that contradicts a design choice the author has explicitly justified, your finding
> MUST engage with the author's stated rationale on its merits, rather than ignore it.
>
> - A `try`/`except` the author labeled "fail-soft by design because <reason>" is not a
>   silent-failure bug — it is a stated design choice. To flag it you must rebut the reason given,
>   not write as though it was never given.
> - A gap the author explained ("this branch is unreachable because <upstream guard>") is not an
>   unhandled case — verify the guard first, then flag it only if the guard does not hold.
>
> Where the author is silent on the choice your finding targets, the finding stands on its own.
> Engagement is required only where the author explicitly addressed the same point.

## When this contract and a vendor skill disagree, the contract wins

Two lenses are assembled on top of vendor skills this engine does not own and does not edit
(`bmad-*` files are regenerated from upstream). Their instructions were written for a different
harness and collide with the contract in three known places. **Say which wins, in the lens's own
prompt, every time — an unresolved collision is resolved by the model at random.**

| The vendor skill says | The contract says | Append this |
|---|---|---|
| produce at least N findings, and treat zero as suspicious | report only what clears the three gates | *"Zero findings is a valid, reportable result. Never invent, pad, or lower your confidence bar to reach a count, and never stop to ask for guidance because you found nothing."* |
| return only a fixed JSON shape, nothing else | every finding needs severity, confidence and an evidence chain | *"Keep the required output shape. Carry the severity, the confidence and the evidence chain INSIDE its free-text field, beginning with `severity: <level>` and `confidence: <n>`."* |
| do not editorialize, never judge code good or bad | classify every finding on the four-word severity rubric | *"A severity label is a required classification, not an opinion. Apply it."* |

## No noise filter — at this layer or any other

⛔ **Never gate findings on "worthiness", and never add a filter that drops low-value findings
before they are recorded.** Our reviewer applies the fixes it finds, so a noisy finding costs one
triage decision while a missed one ships. Precision is bought *inside* each finding, by the three
gates above, never by a filter over the set.

**The fence (SCC-230):** this ruling applies where findings are anchored to a diff. Where there
is no diff — plan and story audits — the anchor rule of SCC-225 governs instead: no anchor,
delete. External benchmarks are cited with source and version, or they are not cited — the recall
figure that used to sit here carried neither and is gone.

## ⭐ THE LENS-ROSTER CONTRACT — five scars, one section, one invariant (SCC-229)

**Every lens in the roster ends the run in exactly one declared state — `ok` ·
`recovered-inline` · skipped-by-mode (on `lenses_na`, with its reason) · `dead` — and never in no
state at all.** Everything below is that sentence applied: the runtime says how lenses launch, the
failure ladder says what a death becomes, and the mode-skip rule says which
absences are health, not damage. Each subsection carries the ticket that paid for it. A future
miss **amends one of these lists — it never adds a section**: five separate sections bolted on by
five separate tickets is exactly the accretion SCC-229 collapsed.

**The measured runtime expectation (SCC-177 · scoring.md, 2026-08-12, 6 runs):** orchestration is
at parity everywhere — pack build 0.19–0.36 s, lens-wave overhead 35–65 s, triage+record 22–44 s.
**A slow run means a lens, never the harness** — the slowest measured lens was Edge Case at
220.5 s (Arm A mean), an order of magnitude past everything the
orchestration does. Investigate the lens before touching the harness.

### `review_runtime` — the caller already answered "can this runtime fan out?", so do not re-ask (SCC-177)

The caller probes for subagent availability at its Step 0 and passes the answer down as
`review_runtime: fan-out | inline`. **Read it before you launch anything.**

| `review_runtime` | What you do | What the roster says |
|---|---|---|
| `fan-out` | the parallel fan-out above, and the failure ladder below when a lens dies | `ok`, or `recovered-inline` for a lens that took the ladder |
| `inline` | **the ladder runs ONCE**: every lens executes inline and sequentially in this context | `recovered-inline` for every lens that RAN — `ok` is not a legal state here |
| absent | probe it yourself, act on what you find, and **report which one you got** in `notes` | as above, per what the probe returned |

⛔ **Under `inline`, never attempt the fan-out first "just in case", and never re-attempt it after
an inline run.** The sequence `fan-out → fail → inline → fan-out again` burns the budget twice,
re-orders the blind lens behind whatever the first attempt loaded into context, and produces a
roster whose states disagree with the declared runtime. A declared `inline` is not a fallback the
caller expects you to try to escape — it is the caller telling you the escape does not exist.

⛔ **`inline` + a lens reported `ok` is a contradiction, and it is checked downstream.**
`walkthrough_roster.py` blocks a lane whose header says `inline` while any lens claims `ok`, because
under a single-pass inline ladder `recovered-inline` is the only state a lens can reach. If you find
yourself writing `ok` under `inline`, either the header is wrong or a fan-out happened against the
declaration; say which in `notes` rather than smoothing the roster to match.

⭐ **The blind lens may start at the frozen-diff commit, concurrently with the caller's suite run.**
It reads `DIFF` and nothing else, so it has no dependency on a gate result and needs no tree — it
can run while the receipt is still being produced. The only requirement is that the record says so:
**the sha the lenses ran against and the sha on the receipt must be the same value**, and the
caller's walkthrough states both. Different shas mean the review and the evidence describe different
code, which is the one thing the concurrency must not buy.

### A lens that cannot launch, or dies (SCC-173)

**If subagents are unavailable in this runtime**, write one prompt file per lens into `ARTIFACT_DIR`
(or, when the caller gave none, return the prompts in the summary and say they were not written),
tell the caller they must be run externally and pasted back, and return. Do not simulate a lens by
imagining its output.

⭐ **A caller may override that return, and one already does.** Handing prompts back assumes someone
is there to run them; **in a headless pipeline nobody is, and returning unrun prompts is a review
that silently never ran** while the caller reads it as clean. So a caller MAY instruct you to run
the lenses INLINE and sequentially in your own context instead — a headless caller with no
subagent tool must — and that instruction wins over the paragraph above. Running a lens inline is not
simulating one: you execute its real prompt and report its real output, losing the parallelism and
the separate context, not the coverage. **Record in `notes` that the lenses ran inline.**

⛔ **An inline lens still owes its reproduction.** Running in your context does not exempt it from
the hunter contract: it writes `reproduce:` and `expected_wrong_output:`, runs the command, and
deletes the finding when the command does not fail as predicted. An inline run is where that is
easiest to skip and where skipping it is least visible.

⛔ **First, the distinction this whole section turns on: a lens that ran and found nothing is NOT
a dead lens.** "Zero findings" is a valid, reportable result that every lens is explicitly allowed
to return — it is `ok`, and it never raises the floor. What follows applies only to a lens that
produced **no usable output at all**: it errored, it timed out, it returned nothing where a report
was due, or it never launched. Conflating the two would cap every clean review at CONCERNS, which
is the opposite of what this contract is for.

**A dead lens is a finding, never a silent skip.** Applied to any lens that errors, times out, or
returns no usable output:

1. **Retry it once.** Transient tool and API failures are the common case.
2. **Still failing → run that lens INLINE yourself, here, in this context.** A lens is a prompt,
   not a privileged tool; losing the parallelism costs time, not coverage.
3. **Record the degradation** in the returned summary — name the lens, the failure, the recovery.
   "3 lenses ran" and "2 ran plus 1 rerun inline" are different evidence and must read differently.
4. **Only a lens that is still dead after BOTH the retry and the inline rerun raises the floor.**

The three end states, and the one that costs you:

| End state | Recorded as | Effect on the floor |
|---|---|---|
| ran first time, or after the retry | `ok` | none |
| died, then produced findings when rerun inline | `recovered-inline` | **none — coverage is complete** |
| died, and the inline rerun also failed | `dead` | **raises `severity_floor` to CONCERNS** |

A lens recovered inline cost time, not coverage, so it must never be scored as a gap. A lens that
never produced findings at all leaves a surface unexamined, and an unknown is never a pass.

### Skipped-by-mode is not the same as dead — and the difference is load-bearing

The Acceptance Auditor **does not run** in `review_mode: no-spec`, because there is nothing for it
to audit against. That is the mode working correctly, not a lens dying.

- Record it on `lenses_na`, **not** as a failure, and **not** inside the `<n>/<applicable>` count —
  a spec-less review reports `2/2`, never `2/3`, because `2/3` reads as degraded.
- **A lens skipped by mode never raises `severity_floor`.** Only a `dead` lens does that.

Conflating the two is how a correctly-configured spec-less review gets reported as degraded
forever, and how a real dead lens gets waved through as "just the mode".

## Collect

> ⭐ **A finding that becomes work looks for a home first (`work-consolidation.md` rule 1, SCC-170).**
> When a survivor is real but out of this lane's scope, it is a lettered **Subtask under an open
> parent** whose surface it belongs to before it is ever a new Task — the parent's index row goes on
> with `jira_feed.py index-row` (it reads the description back and refuses if a prior row went
> missing). **And when no thematic parent fits, it goes on the OPEN ROLLING TICKET** (`Bugs and Updates - <YYYY-MM>` — find it by BOTH labels, `labels IN (bugs-and-updates, running-bug-list)`, per `jira.md` §labels) as a subtask — rung 3
> since SCC-191. Mint only for work that is a lane in its own right on day one, and name what you
> looked at. Judgment, not a gate.

Gather the raw output of every lens that produced one, tagged with which lens said it. Do not
normalize, dedupe, or judge anything here — that is step 3's job, and doing it early loses the
independence the fan-out just paid for.

## NEXT

Read fully and follow `./step-02-verify.md`.
