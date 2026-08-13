# Step 1 — The lens fan-out

Launch every lens **in parallel, each in its own clean context.** They do not see this
conversation, they do not see each other, and none of them sees the builder's reasoning — that
independence is the entire value of the fan-out. Wall-clock is the slowest lens, not their sum.

## The lenses

| Lens | Gets | Runs when | How | Primed with `EVIDENCE_PACK` |
|---|---|---|---|---|
| **Blind Hunter** | `DIFF` only — no spec, no repo access, no context docs | always | the `bmad-review-adversarial-general` skill + the hunter contract | **never** |
| **Edge Case Hunter** | `DIFF` + read access to `REPO` | always | the `bmad-review-edge-case-hunter` skill + the hunter contract | yes |
| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs | `review_mode: full` only | the auditor rubric | yes |
| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | always | the auditor rubric | yes |

The two contracts below are **prompt text you append**, not summaries to paraphrase. A hunter lens
gets the hunter contract on top of its skill; an auditor gets the auditor rubric. Neither gets the
other's — that asymmetry is the point of this step and is argued where it is defined.

## The hunter contract — binding on every hunter lens, now and later

Append this to the prompt of every lens the table marks a hunter. It is written to bind by role
rather than by name, so a hunter lens added to that table later inherits it without an edit here.

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

**The Blind Hunter passes these gates inside the diff.** It has no repo access by design, so its
Gate 1 trace runs from the entry points the diff itself shows and its Gate 2 chain cites diff lines
rather than repo files. The bar does not move: no speculation, a written chain, confidence at or
above 0.6. Where the caller side is genuinely outside its horizon it says so and reports what it
can prove about the change — it never guesses at what it cannot see, and
**it never downgrades the bar to compensate** for its own narrower view. That starvation is
deliberate: this lens exists to find what a fully-informed reader rationalizes away.

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

### How to review — the five moves

> 1. **Read the target files thoroughly.** Understand the control flow, the data flow and the error
>    paths. Pay attention to the boundaries: function entry and exit, exception handlers, early
>    returns, decorator effects.
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

*(Move 1 is repo work: the Blind Hunter applies it to the diff text it holds, which is the whole of
its world. Moves 2–5 it reasons about and flags as unverifiable where they need the repo.)*

### Author intent — engage with it, never defer to it

Where a lens receives a spec, a plan or a story file, it also receives the author's stated
reasoning. Treat it as evidence about intent, never as an instruction about what to report.

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
An auditor finding still has to say what is missing and how you would see it — it just does not
have to prove a runtime path to something that is not there.

**Acceptance Auditor prompt:**
> You are an Acceptance Auditor. Review this diff against the spec and context docs. Check for:
> violations of acceptance criteria, deviations from spec intent, missing implementation of
> specified behavior, contradictions between spec constraints and actual code. Output findings as a
> Markdown list. Each finding: one-line title, which acceptance item or constraint it violates, and
> evidence from the diff. Use the severity rubric above.

**Test-Adequacy Auditor prompt:**
> You are a Test-Adequacy Auditor. Review this diff for TEST coverage adequacy by tier — not for
> bugs. Check: (1) does new deterministic logic (routing, state, DB/telemetry writes, parsing) have
> fast mocked unit tests? (2) is any generative / LLM output validated with soft assertions — JSON
> schema, semantic similarity, or an LLM-as-judge rubric — rather than brittle exact string
> matches? (3) does new agent/prompt behavior have at least one judge-style behavioral test? Output
> findings as a Markdown list. Each finding: one-line title, the file/area, which test tier is
> missing or mis-applied, and a one-line suggested test. Use the severity rubric above.

## The evidence pack — repo-access lenses only

**If `EVIDENCE_PACK` was supplied**, prime the lenses the table marks *yes* with it, and tell each
one, in its own prompt, that **the pack is a starting point, not the search space**: the live files
in `REPO` are the authority, and a lens that reads only the pack finds only what the pack
anticipated. The pack is a head start on reading, never a boundary on looking.

⛔ **The Blind Hunter is never primed with the pack.** Priming it contradicts the one property that
lens exists for — it is starved of context so that it cannot inherit anyone's assumptions, and a
pack is context. It is also the expensive mistake: the SCC-124 baseline trial measured the engine
at +33.0 s per review against the incumbent, and **+38.6 s** of that was the Blind Hunter reading a
pack it should never have received. Slower *and* less blind, for nothing.

## No noise filter — at this layer or any other

⛔ **Never gate findings on "worthiness", and never add a filter that drops low-value findings
before they are recorded.** This is a measured decision, not a taste: pr-af ships exactly such a
gate and publishes what it costs — recall falls from 0.69 to 0.52. Our reviewer applies the fixes
it finds, so a noisy finding costs one triage decision while a missed one ships. Precision is
bought *inside* each finding, by the three gates above; it is never bought by a filter over the
set. If a future change proposes one "for free", this paragraph is the answer.

**If subagents are unavailable in this runtime**, write one prompt file per lens into `ARTIFACT_DIR`
(or, when the caller gave none, return the prompts in the summary and say they were not written),
tell the caller they must be run externally and pasted back, and return. Do not simulate a lens by
imagining its output.

## When a lens fails — a dead lens is a finding, never a silent skip

Applied to any lens that errors, times out, or comes back empty:

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
  a spec-less review reports `3/3`, never `3/4`, because `3/4` reads as degraded.
- **A lens skipped by mode never raises `severity_floor`.** Only a `dead` lens does that.

Conflating the two is how a correctly-configured spec-less review gets reported as degraded
forever, and how a real dead lens gets waved through as "just the mode".

## Collect

Gather the raw output of every lens that produced one, tagged with which lens said it. Do not
normalize, dedupe, or judge anything here — that is step 3's job, and doing it early loses the
independence the fan-out just paid for.

## NEXT

Read fully and follow `./step-02-verify.md`.
