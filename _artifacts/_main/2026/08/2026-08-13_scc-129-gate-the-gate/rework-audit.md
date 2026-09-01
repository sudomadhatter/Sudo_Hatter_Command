# Audit — why this lane's checks kept re-running, and what it cost

Requested by the operator mid-lane: *"we need to look at this mutation test, it seems to fail to run
correctly more than its done right. why is that? … an audit of why this test 'which slows this down
alot' keeps being implemented wrong and keeps being run multiple times."*

## First, a correction to the premise — because it changes the fix

**The mutation checks were mostly not what kept re-running.** Counted:

| Mutation run | Result | Re-run? |
|---|---|---|
| My 7-mutant battery on the clean specimen | 7/7 killed | no — first time |
| Guard's per-defect in-memory self-proofs (5) | pass every invocation | no |
| Guard's apply-check corruption proof | passes | no |
| Guard's `parse` arity counter-example | passes | no |
| Edge Case Hunter's own run (12 mutants) | 11 killed, 12th proven equivalent | no |
| Test-Adequacy's own run (7 regressions) | all reported correctly | no |
| Literal-Correctness's run | **garbage → discarded → redone hermetically** | **yes, once** |
| My self-proof predicate | **shipped broken, caught, fixed** | **yes, once** |

So 6 of 8 ran right the first time. **What actually repeated three times was the five-lens live
control** — 15 lens invocations plus 3 verify-wave roles. That is where the wall-clock went, and the
operator's instinct that something was being re-run wastefully is correct; the attribution is what I
want to sharpen, because fixing "the mutation test" would not have saved any of it.

## The five causes, in order of what they cost

### 1. ⭐ I ran step-01 and read its output as the engine's verdict — cost: 2 of the 3 rounds

The engine is **four steps**. Step-02's verify wave exists *precisely* because hunters assert and
verification is what makes a severity load-bearing — step-03 says in as many words that a revised
severity outranks the hunter's. I ran the fan-out, saw `important` findings on the clean arm, and
started fixing the fixture. Every one of those was an **unverified hunter assertion**.

When the wave finally ran, it took about four minutes and resolved the whole thing: one finding
`verified: false` (its consequence was fabricated — `refund()` disburses nothing), the other
`verified: true` but demoted to `suggestion` (real, unreachable, bounded). `suggestion` and
`nitpick` never gate. **The clean arm passed on the run I already had.**

The tell was visible the entire time and I read past it: the three repo-access lenses had *already*
dropped both findings at Gate 1 — "no entry point exists", confidence 0.3–0.35 — while the blind
lens reported them at 0.65–0.70 *with an explicit reachability caveat saying it could not check
callers*. That disagreement is not a defect. **It is the exact disagreement step-02 was built to
resolve**, and I spent two extra rounds doing by hand, badly, what the engine does by design.

### 2. I did not batch the fixes — cost: the multiplier on cause 1

Findings arrived in waves and I applied them in waves. Every fixture edit invalidates the
measurement (the evidence has to describe the shipped artifact), so each wave forced a full re-run.
Collect → triage once → fix once → re-measure once was available from the start.

### 3. I treated every true finding as a required fix — cost: scope

Most were `suggestion`-severity and never gate. Step-03's buckets exist to answer "does this change
anything"; I skipped the bucketing and worked the raw list. Six fixture defects were worth applying
and I applied them. Three more I have now recorded as deferred with reasons instead of building
them, which is what should have happened from finding one.

### 4. Shared scratchpad, colliding filenames — cost: one discarded mutation run

Step-02's dossier block tells each role to write `findings.json` and `diff.patch` "in a scratch
directory **you own**". I passed that through verbatim to parallel agents all pointed at one shared
scratchpad. Both files landed at its **root** with identical timestamps, and one lens reported its
mutation run returning results for a test function *it never wrote*, then redid the run hermetically
with both sources embedded as literals. It flagged the environment as unreliable for multi-call work
— correctly, and the cause was my prompt, not the environment.

**Fix:** give every parallel agent a unique subdirectory, or embed inputs as literals in the prompt.

### 5. One genuinely broken check of mine — cost: one wasted proof run

`changed = bool(marker) and mutated != bad_txt` can never be false: `"\n".join(text.splitlines())`
drops the trailing newline, so the mutated copy always differs whether or not anything was removed.
A marker declared in the manifest but never seeded would have scored a **green** self-proof row.
Caught by the on-disk removal proof, fixed with an explicit dropped-line count, and proven both ways
(old predicate PASS on a never-seeded marker, new predicate FAIL).

## The transferable lesson, which is worth more than the fixture

**A negative control's clean arm must be built on a surface where "correct" is decidable.** I built
it on float money arithmetic, which has an inexhaustible supply of *legitimate* edge-case findings —
sub-cent absorption, `bool` being an `int` subclass, banker's rounding, precision at scale. Three
rounds in I was ready to swap the subject to a pure string function to make the findings stop.

**That would have been the wrong fix for the right observation.** The engine was never flagging
everything; it was correctly finding real bugs in code I had called clean. The missing step was
verification, not a quieter subject. Had I changed the subject, the control would have "passed" for
the worst possible reason: I would have tuned it until the reviewer went quiet, which is exactly the
failure the clean arm exists to detect.

## What I would do differently, concretely

1. **Run the whole engine, not step-01.** Fan-out → verify → triage → floor. A hunter's `important`
   is an assertion; only the floor is a verdict.
2. **Measure once, triage once, fix once, re-measure once.** Never fix mid-collection.
3. **Give every parallel agent its own scratch directory.**
4. **Pass `DIFF` as a path or as the real content — never an abbreviation.** I hand-trimmed the diff
   into the step-02 prompts to save space and produced a patch that fails `git apply --check` at exit
   128 and drops three hunks. The compound role caught it; the engine's own step-02 warns about
   exactly this class ("a subagent inherits none of your shell variables").
5. **Budget the control explicitly.** Two arms × five lenses × N revisions is a real cost, and N
   should be declared up front. For this lane N should have been 1, with a stated rule that a
   *gating* finding earns a re-run and a `suggestion` does not.
