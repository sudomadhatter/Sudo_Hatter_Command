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

Launch every lens **in parallel, each in its own clean context.** They do not see this
conversation, they do not see each other, and none of them sees the builder's reasoning — that
independence is the entire value of the fan-out. Wall-clock is the slowest lens, not their sum. **in parallel, each in its own clean context.** They do not see this
conversation, they do not see each other, and none of them sees the builder's reasoning — that
independence is the entire value of the fan-out. Wall-clock is the slowest lens, not their sum.

## The lenses

| Lens | Gets | Runs when | How | Primed with `EVIDENCE_PACK` |
|---|---|---|---|---|
| **Blind Hunter** | `DIFF` only — no spec, no repo access, no context docs | always | the `bmad-review-adversarial-general` skill + the hunter contract | **never** — starved by design |
| **Edge Case Hunter** | `DIFF` + read access to `REPO` | always | the `bmad-review-edge-case-hunter` skill + the hunter contract | yes |
| **Literal-Correctness Hunter** | `DIFF` + read access to `REPO` | always | the literal-correctness discipline + the hunter contract | yes |
| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs | `review_mode: full` only | the auditor rubric | **never** — cannot verify it |
| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | always | the auditor rubric | yes |

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



Append to the prompt of every lens whose `How` cell names this contract — today the Blind Hunter,
the Edge Case Hunter and the Literal-Correctness Hunter. **The table is the authority, not this
sentence:** a hunter lens added to that table is bound by this section whether or not anyone
remembered to name it here, because adding its row is what routes it —
so **the `How` cell is the wiring and is not optional.** (The Literal-Correctness Hunter carries one stated adaptation to
Gate 1, written in its own section above; everything else here binds it unchanged.)

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
> **If you were given no repo access**, run both traceable gates inside the diff you were handed:
> Gate 1 starts from the entry points the diff itself shows, and Gate 2 cites diff lines rather
> than repo files. The bar does not move. Where the caller side is outside what you can see, say
> so and report what you can prove about the change — never guess at it, and never lower the bar
> because your view is narrower.

**The Blind Hunter passes these gates inside the diff.** That is what the last paragraph above is
for: it has no repo access by design, so its trace runs on the diff text, and
**it never downgrades the bar to compensate** for the narrower view. The starvation is deliberate —
this lens exists to find what a fully-informed reader rationalizes away — so do not "help" it by
handing it the repo or the pack.

## The literal-correctness lens — deliberately line-level

**What per-lens cost is actually MEASURED (Arm A means, 3 runs/arm —
`_artifacts/_main/2026-08-12_scc-124-baseline-trial/scoring.md`):** Edge Case Hunter 220.5 s (the
slowest lens in 5 of 6 runs) · Blind Hunter 180.9 s · Acceptance Auditor 127.4 s · Test-Adequacy
75.3 s. **This lens is unmeasured — it postdates that trial (SCC-126)**, so no cost claim about it
is funded until the SCC-232 measurement runs. And cost is not the whole ledger: the Edge Case
Hunter is the most expensive lens measured AND produced the SCC-129 trial's one unseeded true
positive (NaN/Infinity bypassing an `amount < 0` guard, because `nan < 0` is False).

The other four lenses are high-altitude: topology, lifecycle, acceptance criteria, test tiers.
This one is deliberately not, and the gap it closes is one the harness this discipline is ported
from measured against a benchmark and then confessed in its own docstring: a multi-agent
architectural review reliably surfaces the high-level findings and **systematically glides over
the meticulous line-level check** — is the code, *as literally written*, correct against the actual
definitions of the symbols it depends on? Almost every defect such a review misses is one
symbol-level assumption violation: a called method that does not exist, an argument that is the
wrong variable, a type that is not the assumed subclass, a value dereferenced that can be nil, a
comparison whose invariant does not hold, code that will not compile.

The prompt text that carries the discipline to the lens:

> You are a Literal-Correctness Hunter. For each changed line, identify every external thing the
> code DEPENDS ON and RELIES ON being true — every call, argument, assignment, condition and type
> assumption — then open the actual definition and verify the assumption holds. Where the ground
> truth contradicts what the code assumes, that is a finding.
>
> **Be EXHAUSTIVE, not selective.** Walk EVERY changed call, argument, assignment, condition and
> type assumption, one at a time. Emit a finding for EVERY violation you confirm.
>
> This is a reasoning DISCIPLINE, not a bug checklist. The violation kinds named above are
> illustrative of what a symbol-level assumption failure looks like — they are not an enumeration
> to pattern-match, and a violation that resembles none of them is still a finding.

### Scope — four rules, and they are what keep this lens affordable

⛔ **Two of these you enforce as the orchestrator, by choosing what you hand over. Two must reach
the lens itself** — so they are blockquoted below and appended to its prompt like every other rule.
Per the assembly convention above, unquoted text never reaches a lens, and **a cap the lens is
never told about is a cap it can neither honour nor report.**

**Orchestrator-enforced, before the lens is launched:**

**A 20-file cap.** Hand over at most **20** changed files' patches, taken in the diff's own order.
When the diff changed more, you MUST tell the lens WHICH files it did not receive — the paths,
never just a count — because the blockquote below orders the lens to NAME what it did not get, and
the `standard` top-up is earned by naming a specific withheld file: neither is possible from a
number (SCC-147). Carry the truncation into the engine's returned `notes` yourself as well. A
truncated pass that says so is evidence; one that stays quiet is a false all-clear over every file
nobody opened.

**Spill above ~9,000 chars.** Past that, write the patch material to a context file in
`ARTIFACT_DIR` and hand the lens the path instead of the text. When no `ARTIFACT_DIR` was supplied,
say so and reduce the file count rather than inlining an oversized prompt.

**An empty patch set → the lens early-exits.** No changed patches means there is nothing to verify,
so do not launch it at all: record **`ok` with zero findings**, never `dead` and never `n/a`. A lens
correctly given nothing to do has not degraded anything, and the other two scorings both corrupt
the record — `dead` would raise `severity_floor` to CONCERNS on every clean diff forever, and `n/a`
would report a fully-run review as partially skipped.

**Appended to the lens's prompt, verbatim:**

> **Your subject is the diff, never the repository — diff-scoped, never whole-repo.** Repo access
> exists for exactly one purpose: opening the real definition of a symbol that the changed lines
> lean on. It is **not a licence to sweep.** Do not survey files the diff did not change looking
> for other work, and do not widen into "related" code. Every file you open must be traceable to a
> specific symbol on a specific changed line.
>
> **If you were told you received fewer files than the diff changed, say so as the FIRST line of
> your output**, naming what you got and what you did not. A reader must never mistake a truncated
> pass for a clean one, and you are the only one in a position to say which this was.

**Its cost axis `lens_budget` is defined ONCE, inside THE LENS-ROSTER CONTRACT below**
(SCC-229 moved it there with the other lens-state law; the caps above are what that axis
governs, and nothing about them changed).

### Gate 1, adapted for this lens — and the adaptation is load-bearing

**This lens is bound by the hunter contract, with one stated adaptation to Gate 1.** Its charter
names violation kinds with *no runtime entry point at all* — code that will not compile, a called
method that does not exist, a type that cannot bind. Demanding a production reachability trace for
those would silence the lens on precisely the defects it was added to catch, which is the same trap
the auditors' exemption already documents one section below.

The prompt text that carries the adaptation:

> **Gate 1 is adapted for you, and only for you.** Where the violation is one the compiler or the
> runtime raises *whenever the changed line executes at all* — a symbol that does not exist, a
> signature that cannot bind, a type that cannot hold — **the changed line IS the reachability
> proof** and you owe no further trace. Name the definition you opened and quote what it actually
> says.
>
> Where the violation instead depends on a *particular value or state* reaching that line — a nil
> that is only sometimes nil, an invariant that holds on most inputs — **Gate 1 binds in full** and
> you owe the ordinary trace. Gates 2 and 3 bind unchanged in both cases.

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

## The evidence pack — repo-access lenses only

**If `EVIDENCE_PACK` was supplied**, prime the lenses the table marks *yes* with it, and tell each
one, in its own prompt, that **the pack is a starting point, not the search space**: the live files
in `REPO` are the authority, and a lens that reads only the pack finds only what the pack
anticipated. The pack is a head start on reading, never a boundary on looking.

That instruction is why the rule is *repo-access lenses only*, and why the two lenses without repo
access are excluded for two different reasons:

⛔ **The Blind Hunter is never primed with the pack.** Priming it contradicts the one property that
lens exists for — it is starved of context so that it cannot inherit anyone's assumptions, and a
pack is context. It is also the expensive mistake: in the SCC-124 baseline trial the Blind Hunter
alone ran **+38.6 s** slower while reading a pack it should never have received, against a +33.0 s
wall-clock delta for the whole review. Slower *and* less blind, for nothing.

⛔ **The Acceptance Auditor is not primed either** — for the opposite reason. It has no repo access,
so it cannot do the one thing the pack instruction demands: check the pack against the live files.
A pack it cannot verify is exactly the shared-anchor bias the instruction exists to prevent, and it
would arrive as authority rather than as a starting point. It audits the diff against the spec,
which is the pair of documents it can actually hold to account.

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
state at all.** Everything below is that sentence applied: the budget axis says what a lens may
spend, the runtime says how lenses launch, the failure ladder says what a death becomes, the drop
rule says when the Blind Hunter's only honest state is `n/a`, and the mode-skip rule says which
absences are health, not damage. Each subsection carries the ticket that paid for it. A future
miss **amends one of these lists — it never adds a section**: five separate sections bolted on by
five separate tickets is exactly the accretion SCC-229 collapsed.

**The measured runtime expectation (SCC-177 · scoring.md, 2026-08-12, 6 runs):** orchestration is
at parity everywhere — pack build 0.19–0.36 s, lens-wave overhead 35–65 s, triage+record 22–44 s.
**A slow run means a lens, never the harness** — the slowest measured lenses were Edge Case at
220.5 s and the Blind Hunter at 180.9 s (Arm A means), an order of magnitude past everything the
orchestration does. Investigate the lens before touching the harness.

### `lens_budget` — the literal-correctness lens's cost axis, defined here, once (SCC-147)

⛔ **`lens_budget` is NOT `review_mode`, and the two are independent.** `review_mode`
(`full` | `no-spec`) says whether a spec exists, and gates the Acceptance Auditor. `lens_budget`
(`standard` | `capped`) governs only the literal-correctness lens's cost. **A review is routinely `review_mode: full`
and `lens_budget: capped` at the same time** — that is the autopilot's normal state, and reading
`review_mode: full` as permission to relax these caps is the expensive mistake this paragraph
exists to prevent.

A caller **names** its `lens_budget`; it never re-defines the caps. Cost governance lives in ONE place, because a cap each caller restates is a cap that drifts per caller.
**A caller that names none gets `capped`** — the safe default, because the cost of guessing wrong
in the other direction is an unbounded overnight spend nobody is watching.

| `lens_budget` | Used by | The caps |
|---|---|---|
| `standard` | interactive callers | MANDATORY as written in that lens's Scope section; the lens may additionally **earn** ONE top-up past the file cap by naming the specific file and what it is looking for — never a sweep, and never "to be thorough" |
| `capped` | `/cicd-code-review-AP` (autopilot), and any caller that names nothing | the same caps, MANDATORY, and **no top-up** — an overnight loop multiplies every token it spends, and nobody is watching it spend them |

**The top-up must REACH the lens, and it must reach ONLY the `standard` lens.** The table above is
the definition, and a table cell is unquoted — orchestrator text, which the assembly convention
says never enters a prompt. Left at that, `standard` and `capped` are behaviourally identical
(SCC-147). So the clause is blockquoted below, and you append
it **only when the caller passed `lens_budget: standard`**. Under `capped` you append nothing —
the same convention that caused the defect is the enforcement, because a lens that was never handed
the clause has no top-up to spend.

> **You may earn ONE top-up past the file cap.** If a withheld file becomes necessary — you can
> name the file and the specific symbol or assumption you must verify inside it — open that one
> file from the repo, and say in your output that you did, naming the file and why. ONE means one:
> never a second file, never a sweep, and never "to be thorough".

### `review_runtime` — the caller already answered "can this runtime fan out?", so do not re-ask (SCC-177)

The caller probes for subagent availability at its Step 0 and passes the answer down as
`review_runtime: fan-out | inline`. **Read it before you launch anything.**

| `review_runtime` | What you do | What the roster says |
|---|---|---|
| `fan-out` | the parallel fan-out above, and the failure ladder below when a lens dies | `ok`, or `recovered-inline` for a lens that took the ladder |
| `inline` | **the ladder runs ONCE**: every lens executes inline and sequentially in this context, blind lens FIRST on the diff alone — and where this context is already contaminated, **the Blind Hunter is DROPPED** rather than faked (§ below) | `recovered-inline` for every lens that RAN — `ok` is not a legal state here |
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
the lenses INLINE and sequentially in your own context instead — `/cicd-code-review-AP` does
exactly this — and that instruction wins over the paragraph above. Running a lens inline is not
simulating one: you execute its real prompt and report its real output, losing the parallelism and
the separate context, not the coverage. **Record in `notes` that the lenses ran inline**, and where
a lens's value depends on context starvation, say what it was exposed to (→ the Blind Hunter
caveat, next).

⛔ **Inline execution costs the Blind Hunter its blindness unless the ORDER protects it.** That lens
is defined as `DIFF`-only; run inline, it inherits whatever your context already holds. A caller
mandating inline execution must therefore run the blind lens **first — on the diff alone, before
any spec, plan, walkthrough or evidence pack is pulled into context.** Done in that order the lens
is genuinely blind and scores `recovered-inline` like any other — `/cicd-code-review-AP` is built
exactly this way, splitting its ingests so the blind lens lands between them.

### ⛔ When the order cannot protect the Blind Hunter, the lens is DROPPED — not faked (SCC-203)

**Operator ruling, 2026-08-17, after a review on this engine's own lane degraded silently:**

> *"subagents as the default, and when they're genuinely unavailable, drop the blind lens rather
> than fake it. Running it inline and counting it in the roster is the worst of the three — it
> costs tokens and produces a record that says the review was **more independent than it was**."*

**The condition is CONTEXT CONTAMINATION, not the runtime.** Inline is fine when the context is
clean and the blind lens goes first. What is never fine is running that lens in a context that
**already holds the plan, the walkthrough, or the builder's own reasoning** — which is the normal
state of the agent that just built the diff. There the lens can only confirm what the builder
already believes: real tokens, zero independent signal.

So when you cannot get it a clean context — the order was impossible, or you ARE the builder and
your context is already contaminated — **do not run it.** Record it on `lenses_na` as
`blind-hunter · n/a — context contaminated (<what it held>)`, **never as `ok`, never as
`recovered-inline`, and never inside the count.** The previous rule allowed
`ok (not blind — context held <what>)`; that state is **retired**, because a roster carrying a lens
that ran without its defining property reports a review that was more independent than it was.

⭐ **And it costs less than it looks.** The Blind Hunter is the ONLY lens whose value depends on
starvation. Edge-Case and Literal-Correctness are handed repo access on purpose, the Acceptance
Auditor needs the spec, and Test-Adequacy needs the test files — being informed is their design.
Dropping one lens is a smaller review; faking it is a false one.

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
   "5 lenses ran" and "4 ran plus 1 rerun inline" are different evidence and must read differently.
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
  a spec-less review reports `4/4`, never `4/5`, because `4/5` reads as degraded.
- **A lens skipped by mode never raises `severity_floor`.** Only a `dead` lens does that.

Conflating the two is how a correctly-configured spec-less review gets reported as degraded
forever, and how a real dead lens gets waved through as "just the mode".

## Collect

> ⭐ **A finding that becomes work looks for a home first (`work-consolidation.md` rule 1, SCC-170).**
> When a survivor is real but out of this lane's scope, it is a lettered **Subtask under an open
> parent** whose surface it belongs to before it is ever a new Task — the parent's index row goes on
> with `jira_feed.py index-row` (it reads the description back and refuses if a prior row went
> missing). **And when no thematic parent fits, it goes on the OPEN ROLLING TICKET** (`Bugs and Updates - <YYYY-MM>`, label `bugs-and-updates`; `SCC-190` today) as a subtask — rung 3
> since SCC-191. Mint only for work that is a lane in its own right on day one, and name what you
> looked at. Judgment, not a gate.

Gather the raw output of every lens that produced one, tagged with which lens said it. Do not
normalize, dedupe, or judge anything here — that is step 3's job, and doing it early loses the
independence the fan-out just paid for.

## NEXT

Read fully and follow `./step-02-verify.md`.
