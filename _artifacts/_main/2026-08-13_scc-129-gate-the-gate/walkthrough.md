# SCC-129 — Gate the gate: seeded bad-diff fixture + engine reviews its own diff

- **Ticket:** SCC-129 (Subtask of SCC-116) · **Branch:** `chore/SCC-129-gate-the-gate` off `main` @ 5dadcd6
- **Plan:** [implementation_plan.md](implementation_plan.md) — `Audit verdict: GO`, approved by the operator
- **Fixture:** `.agents/scripts/tests/fixtures/nc_review_engine/` · **Guard:** `.agents/scripts/tests/test_review_fixture.py`

## What shipped, in one paragraph

The review engine now has a permanent negative control. A seeded bad diff, a clean control diff and
the committed base they both apply to live under `fixtures/nc_review_engine/`, with **one defect per
lens** so a live run also proves each of the five lenses is alive. The ticket's literal wording —
"a permanent negative-control fixture in the test suite: the engine must REJECT a seeded bad diff" —
**could not be built as written**, and deciding what it becomes instead was the first real decision
of the lane. The engine is five markdown files executed by an LLM; the enforcement suite is
stdlib-only, deterministic and LLM-free. So the halves are split: a **mechanical** guard that asserts
the fixture is INTACT (60 cases, every `run_all.py`, forever) and a **live** control run at the review
gate with its output recorded here. The mechanical half is the padlock, not the inspection — it is
what stops the control being silently neutered later, which is how controls actually die.

## Task Checklist

- [x] Fixture built: `bad.diff`, `clean.diff`, `manifest.json`, `spec.md`, `spec-refunds.md`,
      `codebase/`, `README.md`, `live_runs.jsonl`
- [x] One seeded defect per lens, `_negative_control: true`, `NC_`-prefixed ids (eval-harness convention)
- [x] `test_review_fixture.py` joins `run_all.py` by auto-discovery — 60 cases, intactness only
- [x] RED proven before GREEN (0/25 → 47/47 → 60/60)
- [x] On-disk removal proof: `run_all.py` goes red when a seeded defect is deleted
- [x] Live control, bad arm: all five seeded defects reported
- [x] Live control, clean arm: no gating finding after verification
      - finding: the clean arm needed three revisions; two were my process error, not the fixture's — see § Process audit
- [x] Both count lines refreshed (SOP **and** `scripts/INDEX.md` — the audit caught that it is pinned twice)
- [x] Artifacts ledger row added (`check_maps` gates it)

## Evidence — every acceptance item, with the assertion that proves it

### 1–4. The mechanical guard, RED before GREEN

**RED** — the guard written before the fixture existed. Note these are *assertion* failures, not a
setup crash: every check reported its own row, which is what distinguishes a real red from a file
that died on import.

```
== review-engine negative control (SCC-129) — fixture intactness ==
[FAIL] fixture directory exists: missing: …/fixtures/nc_review_engine
[FAIL] manifest.json exists and is non-empty: absent
[FAIL] bad.diff exists and is non-empty: absent
[FAIL] clean.diff exists and is non-empty: absent
…
[FAIL] the five engine lenses each carry exactly one seeded defect: missing=['acceptance', 'blind', 'edge', 'literal', 'test-adequacy'] unexpected=[] count=0
[FAIL] both diffs touch ONLY paths inside the fixture: no paths parsed at all
-- 0/25 passed --
EXIT=1
```

**GREEN** — after the fixture landed, and after the two additions the live control earned:

```
-- 60/60 passed --
EXIT=0
```

### 5. `run_all.py` goes red when a seeded defect is removed

Performed on the code that actually ships. `NC_LITERAL`'s marker line was deleted from `bad.diff`
and the suite run **bare** (no pipe — a pipe returns the *pipe's* exit code):

```
[FAIL] NC_LITERAL: still seeded in bad.diff, exactly once: marker 'helpers.parse(raw, strict=True)'
       found 0x in added lines (want 1) — restore the marker line verbatim, or redesign the defect
       and update manifest.json in the SAME commit — never delete one half
[FAIL]   ^ NC_LITERAL: that check is proven able to fail: the mutation removed 0 line(s) and left
       0 match(es) — it cannot demonstrate this check detects its own removal
[FAIL] bad.diff still applies to the committed base: git apply --check exit 128: error: corrupt
       patch at line 43 — the fixture drifted from codebase/; regenerate the diff against it
============================================================
21/22 files passed  FAILED: test_review_fixture.py
run_all EXIT=1
```

**Three independent detectors fired**, which is the design working: the intactness check (carrying
its remedy), the self-proof (correctly reporting it cannot demonstrate detection of an
already-absent marker), and the apply-check rot guard. Restored from a pristine copy and verified
**byte-identical** — `e22c2941…f1f47b4ff` before and after.

Worth noting which row is the fix from § "What the control found in its own fixture" row 2: the
self-proof line above is the one that, under the original predicate, would have reported **PASS**.

### 6. Live control — the bad arm

Every one of the five seeded defects was reported. Attribution below is *which lens reported it*,
which is the part that proves each lens is alive rather than merely that "some findings came back".

| Seeded | Designated lens | Reported by | Asserted severity |
|---|---|---|---|
| `NC_BLIND` — `invoice_total` subtracts the tax its docstring says is included | blind | **blind**, literal, edge, acceptance | critical ×3 |
| `NC_EDGE` — `unit_price` divides by an unguarded `quantity` | edge | **edge**, blind, acceptance | important / critical |
| `NC_LITERAL` — `helpers.parse(raw, strict=True)`, an argument that does not exist | literal | **literal**, edge | critical ×2 |
| `NC_ACCEPT` — `record_payment` clamps a negative the spec says MUST raise | acceptance | **acceptance**, blind, edge | critical / important |
| `NC_TESTADQ` — new deterministic logic, no test at any tier | test-adequacy | **test-adequacy**, blind, acceptance | important |

**The lens discrimination is the real result, and it is sharper than the totals.** Two defects are
reachable only through a specific lens's inputs, and the fan-out behaved exactly as designed:

- **The Blind Hunter did NOT claim `NC_LITERAL`.** It has no repo access, so it could not open
  `helpers.parse` — and rather than guessing, it filed the uncertainty inside a lower-severity
  finding and said the signature was "outside my view". That is the contract's *"never lower the bar
  because your view is narrower"* working.
- **The Literal-Correctness Hunter opened `codebase/helpers.py:16`, quoted `def parse(text: str)`,
  and declined `NC_EDGE` and `NC_ACCEPT` by name** — the first because it needs a particular value to
  reach the line (so full Gate 1 binds and no caller exists), the second because "the problem is
  spec-relative, not symbol-level". A lens refusing findings outside its discipline is the fan-out
  paying for itself.
- The IDE's own type checker independently flagged `strict` as an unexpected keyword the moment
  `NC_LITERAL` was written — corroboration that the seeded defect is real, from a tool with no
  knowledge of this fixture.

**One unseeded true positive.** The Edge Case Hunter found that `NaN`/`Infinity` bypass
`record_payment`'s `amount < 0` guard entirely (`nan < 0` is `False`), permanently poisoning the
ledger so that every later comparison is false — reached from one `json.loads` literal. Not seeded,
entirely correct, and evidence the lenses are reviewing rather than pattern-matching the manifest.

### 7. Live control — the clean arm

**Step-01 fan-out** (third revision of the clean diff — the first two were fixed in response to
true findings, see § Process audit):

| Lens | Result |
|---|---|
| Edge Case Hunter | **zero findings** — 11/12 mutants killed, 12th proven equivalent over 400k random inputs |
| Literal-Correctness | **zero findings** |
| Acceptance Auditor | **zero findings** — traced every acceptance item, recorded refunds as satisfied |
| Test-Adequacy | suggestions only — *"the unit tier here is above average… I executed all 9 cases: 9/9 pass"* |
| Blind Hunter | **2 × important** |

**Step-02 verify wave** — this is the stage that decides it, and the stage I originally skipped.
The three repo-access lenses had already dropped both of the Blind Hunter's findings at Gate 1
("no entry point exists", confidence 0.3–0.35) while the blind lens reported them at 0.65–0.70
with an explicit reachability caveat. That is not a defect — **it is the exact disagreement step-02
exists to resolve.**

| Blind Hunter's finding | `verified` | Revised | Why |
|---|---|---|---|
| Sub-cent amounts absorbed → over-refund ceiling bypassed "without bound" | **false** | `important` → **nitpick** | The arithmetic is real, but the consequence is fabricated: `refund()` disburses nothing — it is a pure dict mutation with no gateway, transfer or I/O — and every sub-cent call is *individually legal* (`0.001 > 10.0` is `False`), so no ceiling is bypassed. |
| `True` passes every guard, silently refunds 1.00 | **true** | `important` → **suggestion** | Every mechanical claim checks out (`bool` <: `int`, so `math.isfinite(True)` is `True`). Demoted on impact, not accuracy: zero importers repo-wide, harm bounded at a phantom 1.00. |

**I re-derived all three load-bearing claims myself** rather than taking them: `0.001 > 10.0` is
`False`; the module defines only `tax_for`, `invoice_total`, `new_ledger` — no disbursement path;
and `grep -rn "import billing" --include="*.py"` returns nothing. All three hold.

**Step-03 triage:** `suggestion` and `nitpick` never gate (§5), so

```
lenses_run:      5/5   (all ok)
lenses_na:       none
findings:        0 decision · 0 patch · 2 defer   (0 dismissed)
severity_floor:  none
notes:           verify wave ran (2 findings -> verifier + compound); 2 compound findings, both
                 about the run's own plumbing rather than the code; see the control-integrity
                 caveats below
```

**The clean arm passes — and it passes because verification did its job, not because the subject
was changed until the findings stopped.** That distinction is the whole point, and I nearly got it
wrong: three rounds in I was about to swap the subject to a pure string function to silence the
findings. The engine was never flagging everything; it was correctly finding real bugs, and the
missing step was step-02.

### ⚠ Two control-integrity events, both found by the run itself

Recorded prominently because a negative control that quietly loses its integrity is worse than none.

1. **The answer key was readable, and the prohibition did not cover step-02 roles.** The step-02
   verifier — the role whose revised severities *decide the clean arm's outcome* — read
   `README.md`, then disclosed it unprompted: *"you should weigh that claim knowing I had the README
   in context."* The compound role read `manifest.json` too and said its prompt never carried the
   prohibition. On the bad arm the prohibition did not exist yet at all, and the Test-Adequacy lens
   read the manifest. **Fixed:** the README's prohibition now binds step-2 roles exactly as hard as
   step-1 lenses, and says why.

   **How much survives:** every seeded defect has at least one finder that could not have read the
   key — `NC_BLIND`, `NC_EDGE`, `NC_TESTADQ` via the Blind Hunter and Acceptance Auditor (no repo
   access at all), `NC_ACCEPT` via the Acceptance Auditor (diff + spec only), and `NC_LITERAL` via
   the Edge Case Hunter, which **declined the answer key unprompted** — *"that is the fixture's
   answer key, and reading it would turn this into a readback instead of a review"* — and found it
   by opening `helpers.py`. The bad-arm result stands; the severity *column* from the contaminated
   roles is corroboration, not independent confirmation, and is labelled as such.

2. **I hand-trimmed the diff in the step-02 prompts.** Caught by compound synthesis: the patch I
   pasted declares `+29,27` but supplies 15 lines, fails `git apply --check` at exit 128, and drops
   the `import math` hunk, the guard's 12-line rationale docstring, and the entire 75-line test
   file. Step-02 says in as many words to substitute **the real content** — *"a subagent inherits
   none of your shell variables"* — and I substituted an abbreviation to save prompt space. Both
   roles nonetheless worked from the real module (the verifier reconstructed and executed it), and
   the conclusions were independently re-derived above before being accepted. **The rule for next
   time: pass `DIFF` as the path, or the full content — never a summary of it.**

### 8. The engine on this lane's own diff

`/smh-code-review` Step 1 — the engine on the `main...HEAD` diff at `2ff1829` (16 files, 1520 diff
lines). Findings and the canonical `Verdict:` line are in `## Code Review` below.

### Step 0.7 — blast radius re-derived against current `main`

Three answers, in writing, as the command requires:

1. **Did anything this diff REFERENCES move on `main`?** No. `git diff --name-only $(merge-base)..main`
   returns **zero files** — `main` is still at `5dadcd6`, the sha this lane branched from. Every path
   this diff names was re-resolved anyway by the link sweep: 0 broken.
2. **True overlap and conflict?** Against `main`: none, and `merge-tree` produces a clean tree. But a
   **sibling lane appeared while I built** — `chore/SCC-144-merge-target-guard` @ `91218aa` — and it
   overlaps on **two files**: `.agents/scripts/INDEX.md` and
   `docs/_scc_sops_prds/workflows_testing_SOP.md`. `merge-tree` says both **auto-merge** with no
   textual conflict.
3. **Landing order, and what breaks if it is reversed?** ⭐ **This lane should land FIRST.** SCC-144
   changes `.githooks/pre-push`, `.githooks/commit-msg` and the hook scripts — commit-and-push
   machinery — and the standing rule forces those lanes to the END. This lane touches no gate
   machinery.

   **The real dependency is semantic, not textual, and auto-merge is exactly why it is dangerous.**
   SCC-144 adds `test_git_hooks.py`, a **23rd** test file. The moment it lands, my two refreshed
   count lines (*"1762 checks across 22 files"*) are wrong — and because both files auto-merge, git
   will report success while leaving a stale number in the operator's SOP page. **Whoever lands
   second owns re-measuring and updating both lines**, and it will be SCC-144. Named here so it is
   inherited rather than rediscovered.

### 9. Full gate, bare — at the landing sha `2ff1829`

Every gate run **bare**; a pipe returns the pipe's exit code, which is how a red gate reads green.

```
python3 .agents/scripts/tests/run_all.py                  -> 22/22 files, 1762/1762 cases, EXIT=0
python3 .agents/scripts/workflow_lint.py --toolkit-only   -> 0 error(s), 0 warning(s), 8 info, EXIT=0
python3 .agents/scripts/check_maps.py --depth3-only --strict                              EXIT=0
python3 .agents/scripts/sop_currency.py --paths <changed> --message "<subject>"            EXIT=0
py_compile on all 3 changed .py files                                                      ok
link + anchor sweep over the diff's markdown                              0 broken
door parity: 0 commands touched · deployable paths in diff: 0
```

**Additivity is measured, not inherited.** I ran the suite in `main`'s own checkout rather than
trusting the number in the brief:

```
main @ 5dadcd6:  21/21 files, 1702/1702 cases
this tree:       22/22 files, 1762/1762 cases
delta:           +1 file, +60 cases  ==  test_review_fixture.py's own 60/60
```

Exactly additive — nothing displaced another file's tests.

⚠ **Both count lines will go stale when SCC-144 lands** — see the landing-order note below. That is
the same silent rot `scripts/INDEX.md`'s own text warns about, now with a named owner.

## What the control found in its own fixture

The control was pointed at the fixture that houses it, and it found six real defects in this lane's
own work. Each is recorded with what it cost and what fixed it.

| # | Found by | Defect in MY work | Fix |
|---|---|---|---|
| 1 | acceptance (bad arm) | **One spec governed both diffs**, so the auditor correctly reported every section the diff in front of it did not implement. Harmless noise on the bad arm; **fatal** on the clean arm, where three "missing implementation" findings would have failed the control while the engine was working perfectly. | split into `spec.md` + `spec-refunds.md`, one per change; re-ran the acceptance lens, and it then recorded refunds as "correctly absent" |
| 2 | removal proof | **My own self-proof could not fail.** `changed = mutated != bad_txt` is *always* true, because `"\n".join(splitlines())` drops the trailing newline — so a marker declared in the manifest but never seeded would score a green self-proof row. | replaced the text comparison with an explicit dropped-line count; proven both ways (old predicate PASS on a never-seeded marker, new predicate FAIL) |
| 3 | test-adequacy (bad arm) | **The spec renumbering rotted `NC_TESTADQ`'s pointer** — the manifest and README cited `spec.md §5`, which the split turned into "Conventions". | corrected to §4, **and** given a `spec_must_contain` pin so the existing generic loop guards it for free |
| 4 | test-adequacy (bad arm) | **Nothing mechanically asserted `helpers.parse`'s arity** — the precondition `NC_LITERAL` rests on. Neither diff touches `helpers.py`, so `git apply --check` never reads it; the marker check only proves the *call* is still there. `helpers.py` warned in prose, and prose is exactly what this guard's own docstring says cannot gate. | an `ast` check asserting `parse` takes exactly one parameter and no `**kwargs`, with a counter-example on the very "fix" the README warns against |
| 5 | test-adequacy (bad arm) | **"Does the clean control ship a test" was satisfied by a filename.** Gutting the body to `pass` kept it green. | additionally require the added test lines to carry an assertion, with its own counter-example |
| 6 | test-adequacy (bad arm) | **The "two consecutive misses" escalation rule had no state to compute "consecutive" from** — evidence lands in a different lane's walkthrough each time, with nothing linking runs. | `live_runs.jsonl` + shape checks. Deliberately **not** asserting every defect was hit: a red on an honest miss would pressure the next person to omit it, and a log of successes only is not a log |

Findings deliberately **not** acted on, with the reason:

- **A judge-style behavioral test lane** that re-runs the engine and asserts properties of fresh
  output (test-adequacy, suggestion). Correct and genuinely better than a pinned transcript — but
  adding an LLM-calling lane to a stdlib-only, LLM-free suite is a real scope decision that belongs
  in its own ticket, which the auditor itself said. **Not folded in.**
- **`import billing` falsifies `billing.py`'s "Nothing imports it"** (literal, nitpick). Dismissed
  with reason: the importer exists only inside `clean.diff`, which is **never applied** — only
  `git apply --check`ed. The sentence is true of the committed tree, which is the only tree there is.
- **Pin that `run_all.py`'s discovery is non-recursive** so a future `glob`→`rglob` could not start
  collecting files under `fixtures/` (test-adequacy, suggestion). Real, and a genuinely nice
  functional check is available. **Deferred:** it guards a hypothetical future edit to a *different*
  file, this fixture's correctness does not depend on it (`test_billing.py` exists only inside a diff
  that is never applied), and the plan's boundary says do not grow scope. Recorded rather than
  silently dropped.
- **Execute the clean arm's specimen tests inside the guard** rather than grepping for `assert`
  (test-adequacy, suggestion). The sharpest of the deferred set: tests asserting a *wrong* value
  would keep the guard green while the fixture modelled a failing test as its specimen. I executed
  all 9 by hand this lane (9/9) and killed 7/7 mutants against them, so the specimen is correct
  today — but nothing keeps it correct. **Deferred to its own ticket** because applying a diff and
  executing its contents inside `run_all.py` is a new capability for this suite, not a tweak.

## Process audit — why the live control ran three times

Requested by the operator, and it is the most useful thing in this document.

**The mutation checks were mostly not the problem.** My 7-mutant battery on the clean specimen killed
7/7 first time. The Edge lens ran 12 and killed 11, proving the 12th equivalent across 400k random
inputs. Test-Adequacy ran 7 regressions. What repeated was the **five-lens live control**, three
times, and the causes are separable:

1. **⭐ The dominant cause: I ran step-01 and read its output as the engine's verdict.** The engine is
   four steps. Step-02's verify wave exists *precisely* because hunters assert and verification is
   what makes a severity load-bearing — step-03 says a revised severity outranks the hunter's. Every
   `important` I chased on the clean arm was an unverified hunter assertion that should have gone
   through the wave the first time. When the wave finally ran, the repo-access lenses had already
   independently dropped both of those findings at Gate 1 ("no entry point exists", confidence
   0.3–0.35) while the blind lens reported them at 0.65–0.7 with an explicit reachability caveat.
   **That disagreement is not a defect — it is the exact disagreement step-02 was built to resolve**,
   and I spent two extra rounds doing by hand what the engine does by design.
2. **I did not batch the fixes.** Findings arrived in three waves and I applied them in three waves.
   Every fixture edit invalidates the measurement — the evidence has to describe the shipped artifact
   — so each wave cost a full re-run. Collecting all findings, triaging once, fixing once and
   re-measuring once was available and I did not take it.
3. **I treated every true finding as a required fix.** Most were `suggestion`-severity and never
   gated. Step-03's buckets exist to answer "does this change anything"; I skipped the bucketing and
   acted on the raw list.
4. **Shared scratchpad, colliding filenames.** Step-02's dossier block says each role writes
   `findings.json` and `diff.patch` "in a scratch directory you own", and I passed that through
   verbatim to parallel agents pointed at one shared scratchpad. Both files landed at its **root**
   (timestamps identical), and one lens reported its mutation run returning results for a test
   function it never wrote, then redid the run hermetically. Fix: give every parallel agent a unique
   subdirectory, or embed inputs as literals.
5. **One real bug of mine** — the self-proof that could not fail (row 2 above). Caught by the removal
   proof, which is the check doing its job.

**The transferable lesson**, and it is worth more than the fixture: *the clean arm of a negative
control must be built on a surface where "correct" is decidable.* I built it on float money
arithmetic, which has an inexhaustible supply of legitimate edge-case findings — sub-cent absorption,
`bool` being an `int` subclass, banker's rounding, precision at scale. Three rounds in, I was about to
change the subject to a pure string function to make the findings stop. That would have been the
wrong fix for the right observation: the engine was not flagging everything, it was correctly finding
real bugs, and the missing step was verification, not a quieter subject.
