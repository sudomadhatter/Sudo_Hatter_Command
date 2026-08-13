# Step 1 — The lens fan-out

Launch every lens **in parallel, each in its own clean context.** They do not see this
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

Append to the prompt of every lens whose `How` cell names this contract — today the Blind Hunter
and the Edge Case Hunter. A hunter lens added to that table later is bound by this section too;
adding its row is what routes it, so **the `How` cell is the wiring and is not optional.**

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

## The literal-correctness lens — the one lens with a real token cost

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

**Diff-scoped, never whole-repo.** The subject is the changed lines. Repo access exists so the lens
can open the real definition of what those lines lean on; it is not a licence to sweep. An
unbounded version of this lens is the one thing this engine cannot afford to run on every review.

**An empty patch set → the lens early-exits.** No changed patches means there is nothing to verify:
it returns zero findings and is recorded **`ok`**, never `dead` and never `n/a`. A lens that
correctly found nothing to do has not degraded anything, and the other two scorings both corrupt
the record — `dead` would raise `severity_floor` to CONCERNS on every clean diff forever, and `n/a`
would report a fully-run review as partially skipped.

**A 20-file cap.** Take the first 20 changed files. On a diff wider than that, the cap is reported
in the lens's own output — a truncated pass that says so is evidence; one that stays quiet is a
false all-clear over the files it never opened.

**Spill above ~9,000 chars.** Past that, write the patch material to a context file in
`ARTIFACT_DIR` and hand the lens the path instead of the text. When no `ARTIFACT_DIR` was supplied,
say so and reduce the file count rather than inlining an oversized prompt.

### Full mode and capped mode — defined here, once

A caller **names** the mode; it never re-defines the caps. Cost governance lives with the lens that
incurs the cost, because a cap that each caller restates is a cap that drifts per caller.

| Mode | Used by | The caps |
|---|---|---|
| `full` | interactive callers | as written above; the lens may **earn** ONE top-up past the file cap by naming the specific file and what it is looking for — never a sweep, and never "to be thorough" |
| `capped` | `/cicd-code-review-AP` (autopilot) | the same caps, MANDATORY, and no top-up — an overnight loop multiplies every token it spends, and nobody is watching it spend them |

## The auditor rubric — Acceptance Auditor and Test-Adequacy Auditor

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
before they are recorded.** This is a measured decision, not a taste: pr-af ships exactly such a
gate and publishes what it costs — recall falls from 0.69 to 0.52. Our reviewer applies the fixes
it finds, so a noisy finding costs one triage decision while a missed one ships. Precision is
bought *inside* each finding, by the three gates above, never by a filter over the set. If a future
change proposes one "for free", this paragraph is the answer.

## When a lens cannot be launched, or fails

**If subagents are unavailable in this runtime**, write one prompt file per lens into `ARTIFACT_DIR`
(or, when the caller gave none, return the prompts in the summary and say they were not written),
tell the caller they must be run externally and pasted back, and return. Do not simulate a lens by
imagining its output.

**A dead lens is a finding, never a silent skip.** Applied to any lens that errors, times out, or
comes back empty:

1. **Retry it once.** Transient tool and API failures are the common case.
2. **Still failing → run that lens INLINE yourself, here, in this context.** A lens is a prompt,
   not a privileged tool; losing the parallelism costs time, not coverage.
3. **Record the degradation** in the returned summary — name the lens, the failure, the recovery.
   "4 lenses ran" and "3 ran plus 1 rerun inline" are different evidence and must read differently.
4. **Only a lens that is still dead after BOTH the retry and the inline rerun raises the floor.**

The three end states, and the one that costs you:

| End state | Recorded as | Effect on the floor |
|---|---|---|
| ran first time, or after the retry | `ok` | none |
| died, then produced findings when rerun inline | `recovered-inline` | **none — coverage is complete** |
| died, and the inline rerun also failed | `dead` | **raises `severity_floor` to CONCERNS** |

A lens recovered inline cost time, not coverage, so it must never be scored as a gap. A lens that
never produced findings at all leaves a surface unexamined, and an unknown is never a pass.

## Skipped-by-mode is not the same as dead — and the difference is load-bearing

The Acceptance Auditor **does not run** in `review_mode: no-spec`, because there is nothing for it
to audit against. That is the mode working correctly, not a lens dying.

- Record it on `lenses_na`, **not** as a failure, and **not** inside the `<n>/<applicable>` count —
  a spec-less review reports `4/4`, never `4/5`, because `4/5` reads as degraded.
- **A lens skipped by mode never raises `severity_floor`.** Only a `dead` lens does that.

Conflating the two is how a correctly-configured spec-less review gets reported as degraded
forever, and how a real dead lens gets waved through as "just the mode".

## Collect

Gather the raw output of every lens that produced one, tagged with which lens said it. Do not
normalize, dedupe, or judge anything here — that is step 3's job, and doing it early loses the
independence the fan-out just paid for.

## NEXT

Read fully and follow `./step-02-verify.md`.
