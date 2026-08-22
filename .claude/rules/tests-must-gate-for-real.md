---
name: tests-must-gate-for-real
description: "Activates whenever a test is written, a CI/quality gate is scaffolded or reviewed, or a suite is marked report-only/soft/skip. A test only protects you if it fails for the RIGHT reason, CI runs the REAL suite, and no gate is soft forever."
trigger: glob
globs: ["**/tests/**", "**/*.test.*", "**/*.spec.*", "**/*.feature", "**/conftest.py", ".github/workflows/**"]
paths:
  - "**/tests/**"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*.feature"
  - "**/conftest.py"
  - ".github/workflows/**"
# Path-scoped. `globs:` is Antigravity's field; `paths:` is Claude Code's, and Claude
# loads this file ONLY when it reads a file matching one of them. Both lists are the
# same set on purpose — one classification, two readers (test_rule_frontmatter.py).

---

# A Test Only Counts If It Actually Gates

## When This Applies
Writing acceptance/ATDD tests (①), scaffolding or editing a CI pipeline / quality gate
(`bmad-testarch-ci`, workflow YAML), and every test-gate review (③). Applies to Claude,
autopilot, and manual / Antigravity workflows alike.

## The Trap
A red test READS as protection. A CI job that says "E2E" READS as coverage. A `continue-on-error`
step with a "flip to hard gate later" comment READS as a temporary measure. All three can be hollow:
- A red that asserts strings/selectors/endpoints **the codebase never had** fails identically whether
  the feature is unbuilt or the assertion is invented — so it can never go green, and it proves nothing.
- A CI job can run a *different, partial* test config than the one that matters and still show a green
  check — the real suite never ran.
- "Report-only FOR NOW" with no owner and no expiry silently becomes "report-only forever."

## The Rule
1. **A red must fail for the RIGHT reason — grounded in real source.** Before a red counts as a valid
   ATDD red, verify every asserted string, selector, endpoint, and **precondition** against the actual
   code (grep the producing surface; read the page/handler). The red must fail because the feature is
   *unbuilt*, never because the test invented a literal or misread the auth / precondition model. A test
   asserting copy absent from source, or calling an auth-gated page "public," is **fiction, not a red** —
   fix or delete it; never let it ride. (See [[atdd-mock-shape-must-match-backend-contract]].)
2. **CI must run the REAL suite entrypoint.** The gate must execute the project's actual harness command
   — the *same* one the local gate runs (`npm run test:e2e`, the full pytest suite, …) — not a divergent
   or partial config that silently skips the suite that matters. When reviewing a gate, confirm the job's
   command invokes the real entrypoint and that the tests you think protect the branch actually executed.
3. **A soft gate is a ONE-RUN window with a named owner + a tracked expiry — never open-ended.**
   `continue-on-error`, `|| true`, `.skip`, `xfail`, and grandfathered "legacy red" are all forms of *not
   gating*. Each is legitimate only briefly — to prove a brand-new harness on CI once — and only if it
   carries a named owner and a tracked task to close it. In review, flag any soft/report-only test step
   that lacks both as a finding (CONCERNS floor). Grandfathering "fail only on NEW regressions" is real,
   but legacy red must be **examined and owned** (quarantined-with-ticket), not unexamined permanent
   failure a fiction test can hide inside.
4. **Certification is measured at the SHIPPING SHA — feedback runs are not certification.** Scoped suites
   and the blast-radius pass are *feedback*: cheap, early, at the point of maximum uncertainty. The full
   suite is *certification*, and it has exactly ONE legitimate moment — after the last code or test change,
   at the SHA that will ship. Consequences, all binding:
   - **The (totals, SHA) pair is a contract, not decoration.** Totals MUST come from a run at exactly the
     SHA named beside them. Any code or test change after that run **voids it** — re-run. **Artifact/doc-only
     changes are exempt** (a walkthrough edit after the run does not invalidate it).
   - **Never certify before a step that adds tests.** A full-suite run ordered ahead of a coverage-expansion
     pass produces totals that stale the moment expansion lands. Order certification last.
   - **Only citable forms count.** Where a harness makes isolated results untrustworthy, only the citable
     form may be pasted as evidence — e.g. an emulator tier must be run **FULL-TREE**; `-k`/single-file
     emulator runs are debug-only, never citable (sibling conftests global-mock the tree, and collection
     dominates their cost anyway).
   - **A structural red is a wiring proof, never a behavior proof.** Source-contains asserts cannot see
     ORDER — a guard relocated below the write it protects passes them identically. Behavioral coverage is
     therefore **owed**, not optional. Give every scenario a **positive control** (the unguarded path must
     still do the thing), or the test passes against a helper that does nothing at all. **Proving a new
     test non-vacuous is a mutation — the procedure is § Mutation Testing below**, which is where the
     *relocate, never delete* technique now lives, alongside the shape it does not transfer to and the
     two rules that bind every mutant whatever its shape.

5. **A gate that cannot fail is a finding — and shipping one is a FAIL, not a note.** Report-only
   jobs, `|| true`, `continue-on-error`, a check whose EMPTY input reads as a pass, a `grep` guard that
   matches its own explanatory comment: each of these reports green having verified nothing, which is
   strictly worse than no gate, because the green is read as evidence. **Prove a new check both
   REJECTS and ALLOWS** — one half is not a gate. A check seen passing but never seen failing is a
   description of intent, not a gate. (House incident: a fiction spec rode to production behind a
   report-only E2E job that had never once been red.)
6. **Run gates BARE — a pipe returns the PIPE's exit code, not the gate's.** `run_all.py | tail -5`
   exits 0 when `tail` succeeds, however red the suite was, and `set -o pipefail` is not on by default
   in the shell an agent spawns. Run the gate on its own line, read `$?` immediately, and redirect to a
   file if you need to trim the output: `gate > out.txt 2>&1; echo "EXIT=$?"`. The same trap wears two
   other hats — `cmd && other` loses the code the same way, and `zsh` does not word-split an unquoted
   argument string, so a gate invoked through a variable can silently receive one long argument.

## Mutation Testing — proving a check can actually fail

A test you have never seen fail is a claim, not a check. **Mutation is how the claim gets tested:**
break the thing on purpose and watch a NAMED case die. Rule 1 is *why* this is owed; Rule 4 is *when*;
this is the **procedure**, and it is named here so it can be found by anyone grepping for how to do it.

**Declare the table BEFORE you mutate.** One row per mutant — the mutant, the file, and **the named
case it must kill** — and run them as **ONE sweep**, never one at a time. A sweep improvised one mutant
at a time cannot check itself; a declared one can. **A surviving mutant is a finding.** Record the
finished table in the walkthrough: each mutant, its file, its named case, and the outcome.

### The techniques — and which shape each one is for

- **RELOCATE the guard** — for a structural guard and a behavioral test in the **same file**. Move the
  guard below the write it protects: the structural reds stay green (they cannot see ORDER) and only
  the new behavioral test fires. ⛔ **Never DELETE it** — deletion kills both tests and isolates
  nothing. That is how this technique was first got wrong (AGY 21.8b), and for a long time it was the
  *only* technique written down.
- **INVERT the decision** — for **gates, hooks and shell checks**, where there is nothing to relocate.
  Flip one refusal to an allow, one comparison, one exit code. This is the shape the technique above
  does not transfer to, so anyone mutating a gate was following advice designed for a different
  problem — and improvised instead.
- **CODE-DERIVED, never case-derived** — draw every mutant from a **decision in the source under test**,
  never by reading your own cases and asking what would break them. Case-derived mutants are circular:
  they prove only that the suite agrees with itself. Measured in SCC-144 — its 14 case-derived mutants
  were all killed, and a later set drawn from the code left **24 of 25 surviving**, every survivor a
  hole the first sweep had reported as covered. That is [[prose-pinning-guards-are-vacuous]] recurring
  one level up, *inside* the mutation pass.
- **RESTORE on interrupt, and never start dirty** — restore in a `finally`/trap, refuse to start against
  a dirty tree, and re-check `git status` when the sweep ends. In SCC-144 a `timeout`-killed sweep left
  `commit-msg-jira.sh` **mutated on disk, uncommitted** — reverted to the exact bug that lane existed to
  remove. A mutated gate is committable, and residue in a dirty tree is indistinguishable from your own
  work. ⭐ **Since SCC-179 none of this clause is self-reported: `.agents/scripts/mutation_sweep.py`
  enforces every word of it** — it refuses to start when a table file is dirty (naming the file and
  this reason), restores in a `finally` and on SIGTERM, and proves the end state twice over, against
  the pre-sweep bytes and against the pinned pre-sweep sha. It was written because this paragraph
  existed and did not hold: `8681d83` shipped a live mutant into the gate anyway.
- **The scoped `--case` runs are not the sweep's last word** — run the **FULL file, unfiltered, once**
  before the next commit. `8681d83` is what a scoped subset misses: every named case was green, the
  mutant was still in the tree, and the cost was a red receipt, a diagnosis, a fix commit and another
  full suite run. `mutation_sweep.py` does this run itself and fails the sweep on it.
- **Read the harness's exit 3.** `_harness.NO_MATCH` means the `--case` filter selected NOTHING. A
  sweep that reads any non-zero as "killed" turns a typo'd label into evidence, so a kill needs a
  non-zero exit that is not 3, a `FAILED:` line, and the **declared** case named on it. Anything else
  is an error in the SWEEP, not a result about the code.

- **WIDTH, not only existence** — a deletion mutant proves a case notices the behaviour is *gone*. It
  proves **nothing about the boundary**, and a narrowing is the shape real regressions take. So sweep
  **narrowings** too: drop one member from a matched class, shorten a range, require one extra
  condition, disable one arm of a rule that has several. SCC-154's existence sweep killed 17/17 and its
  review still found that width was uncertified; a second sweep of 7 narrowings — a character class
  losing one marker, a fence rule ignoring the opening length, an allow-arm losing one destination —
  killed 7/7 by named case and is the only reason those boundaries are known to be held.

### Targeted kills — run the NAMED case, not the whole file

A mutant is a claim about **one** case. Running the entire file to test it buys nothing and costs the
file's full wall: SCC-154's 17-mutant sweep spent ~21 minutes running two large suites 17 times over,
to watch one named case die each time.

**So run the killer alone** — `python3 <suite> --case "<block label>"` (`_harness.py`'s block filter,
SCC-156) — and read its exit code with the sweep's three outcomes kept distinct:

| Exit | Means | The sweep does |
|---|---|---|
| non-zero (1) | the named case FAILED | **KILLED** — this is the result you declared |
| 0 | the named case passed with the mutant in place | **not yet a survivor** — re-run that mutant against the **whole file** before believing it. A mis-aimed label and a genuine hole look identical from one filtered run, and only the full file can tell them apart |
| **3** | the filter selected nothing — a typo'd label, an unwired file, a matched block with no cases | **a sweep error, never a verdict.** Fix the label and re-run. ⛔ Reading 3 as a kill is the failure this exit code exists to prevent: every mutant would "die" and the sweep would certify nothing |

⛔ **Never parallelize the mutant loop.** Mutants edit shared files on disk; two in flight at once mean
neither result is about the mutant you think it is. The *cases* inside one run may be concurrent; the
loop over mutants is strictly sequential.

⭐ **The closing full green is MANDATORY, and it is not the same run as the kills.** When the sweep ends
— after every restore is verified byte-identical against its pre-sweep `sha256` — run the affected test
**FILES bare, unfiltered**, and require green. Targeted kills prove each mutant died; only the closing
green proves the tree you are handing back is the tree you started with. A sweep that ends on a filtered
run has verified nothing about the other 140 cases in the file it just edited 17 times. Every sweep
script carries this step; a sweep report without it is incomplete evidence, not a fast one.

### A mutant that removes nothing is DEFECTIVE — not a coverage gap

**The survivor you must not believe.** If the mutant's edit does not appear in the original text, or it
does not actually remove the behaviour it claims to remove, it proved nothing: it is a **SKIP that
counts as a survivor**, and it must be **re-aimed before it is believed.** Verify every mutant's edit
against the original text *before* the sweep runs.

SCC-144's `M3` commented out one `echo` of a two-line message; the second line still printed the word
the case asserts, so the case passed — **correctly**. Re-aimed at the whole block it killed, and
re-aiming it exposed a code path with no case at all. Reading that survivor as a coverage gap would
have bought a test for a hole that did not exist while the real one stayed open.

## Why
Source: AGY 2026-07-13. `frontend/e2e/hanger-talk.spec.ts` asserted four UI strings ("Free Learning
Materials", "Hanger Talk Series", …) that appear **0×** in the frontend source, against a route that is
auth-gated (renders `null` when logged out) — the test called it "public." It never passed. Meanwhile CI
ran the plain `playwright.config.ts`, which `testIgnore`s `journeys/**`, so the REAL TEA-16 emulator
harness (6/6 green locally the whole time) never ran on CI at all; the failing job was
`continue-on-error: true` — "report-only FOR NOW" — left open indefinitely. Three independent holes —
fiction red at ①, wrong CI entrypoint, report-only-forever — each of which this rule closes. The guard is
cheap (grep the source, check the CI command, put an owner on every soft gate); the failure — a suite that
looks green while protecting nothing — is not.

**Rule 4 source: AGY story 21.8b, 2026-08-02.** `/cicd-dev-story-tests` Step 3 mandated the full-suite run
*before* Step 4 (`bmad-testarch-automate`) — the step whose whole job is adding tests. Following the spec
literally produced totals (3008 @ `66069c99`) that staled the instant expansion landed; the agent caught it
and paid a SECOND full run (3012 @ `7423eadf`) to hand ③ a valid pair. One full backend suite is **278 s
serial**, so the mis-ordering cost ~4.6 min per story, every story, to buy back an invariant the ordering
had broken. Separately, the story's first mutation check *deleted* the guard — which killed the structural
test too, isolating nothing; only the *relocate* mutation proved the behavioral test carried its own weight.
Both failures are ordering/technique errors that read as diligence, which is exactly why they need to be
written down. (See [[source-grep-guards-cannot-see-order]], [[stubbed-children-make-green-vacuous]].)
