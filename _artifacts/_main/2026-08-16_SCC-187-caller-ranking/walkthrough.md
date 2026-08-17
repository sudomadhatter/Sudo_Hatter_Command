# Walkthrough — SCC-187 rank caller snippets by import (2026-08-16)

**Lane:** `chore/SCC-187-caller-ranking` @ `76daa64` · **Base:** `origin/main` @ `bc3a851` · **Repo:** Sudo_Hatter_Command
**Plan:** [implementation_plan.md](implementation_plan.md) — `Audit verdict: GO`
**Plan approval (2026-08-16):** operator, verbatim — *"approved"* — recorded here rather than in the
plan, because editing an approved plan re-arms the plan-first gate.

## What changed

| File | Why |
|---|---|
| `.agents/scripts/evidence_extract.py` | `_find_function_callers` gains `prefer=` (importer files scanned first); `_extract_one` tags every caller snippet `[importer]` / `[name-match]` and stable-sorts importers ahead **before** the cap; `_importers_of()` split out of `_build_import_context` so the importer walk runs once per finding, not once per consumer; docstring records cap provenance + the stderr-only drop hazard |
| `.agents/scripts/tests/test_evidence_extract.py` | 8 new blocks; **every section wired into `c.block` guards** — 19 sections, 23 selectable blocks; one existing counter-example made tag-aware |
| `.agents/scripts/tests/test_suite_runner.py` | new **NESTED** check: ORPHAN's blind sibling — a whole block declared inside another block is unreachable by `--case`, so its label silently returns `NO_MATCH` |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | the tags now visible in review evidence, and that `--pack` is still unwired (SOP-currency gate) |
| `_artifacts/_main/INDEX.md` | the session row `check_maps` requires |

**Scope held.** No deployable path in the diff (checked). Everything the ticket lists as CLOSED —
`--pack` wiring, spill-not-truncate, `ast` symbol definitions, a TS parser, a repo-wide index — stayed
closed; nothing was built toward any of them.

## Evidence

### A1 — snippets are tagged, importers sort first, both classes survive

RED (before): the importer was **last** and nothing carried a tag.

```
[FAIL] ranking: a file that IMPORTS the subject is tagged [importer]: user_chain tagged ''
[FAIL] ranking: a file that only NAME-MATCHES is tagged [name-match]: caller_visible tagged ''
[FAIL] ranking: the importer sorts ahead of every name-match: importer at 3, name-matches at [],
       order is ['src/pkg/blast_deep.py','src/pkg/caller_visible.py','src/pkg/sibling.py','src/pkg/user_chain.py']
```

GREEN: `-- 5/5 passed --  -- filter 'SCC-187-A1': matched 5/23 blocks --`

### A2 — a late importer survives both caps

RED (before) — and this is the audit's F1 reproducing exactly:

```
[FAIL] late importer: it is COLLECTED despite sorting past the walk's own cap:
       the importer never made it into the snippets; got
       ['pkg/aa_00_caller.py' ... 'pkg/aa_09_caller.py']
```

GREEN: `-- 4/4 passed --`. Second half (2e, across identifiers) GREEN: `-- 3/3 passed --`.

### A3 — the docstring records provenance and the hazard

By inspection (the planned guard case was cut as prose-pinning — F2). `evidence_extract.py` now
carries **THE CAPS: WHAT WAS TRANSCRIBED, AND WHAT WAS DERIVED (SCC-187)**, stating that every cap
was transcribed from pr-af `evidence.py` @ `8593130` and none re-derived here, that
`_PACK_MAX_CHARS = 16000` cannot hold this repo's own 48,800-byte main script (whose first 400
lines alone are ~20,300), and — under a ⛔ — that `_note()` writes to stderr while callers paste
stdout, so a dropped file is invisible to the lens, and **wiring `--pack` in without fixing that is
a net negative**.

### A4 — every SCC-123 invariant intact

Full suite through the receipt writer, on the landing code, clean tree:

```
[PASS] suite exit=0 113.1s @ 76daa64f        receipt: gates/suite.json
```

`workflow_lint --toolkit-only` exit 0 · `check_maps --depth3-only --strict` exit 0 ·
`test_sops_prds_folder.py` exit 0 · `run_all.py` **32/32 files** · `test_evidence_extract.py` **144/144** ·
`test_suite_runner.py` **79/79** with ORPHAN and NESTED both reporting `[]`. The spawn-block harness still passes,
so the zero-subprocess guarantee is unchanged.

### Mutation sweep — 11/11 killed

`sweep.json` → [sweep-result.txt](sweep-result.txt). Table declared before mutating, drawn from the
code.

| id | Mutation | Result |
|---|---|---|
| M1 | ranking becomes filtering | KILLED by *ranking: BOTH classes survive* |
| M2 | outer sort moved after the cap | KILLED by *outer sort: a LATER identifier's importer is not crowded out* |
| M3 | the two tag literals swapped | KILLED by *ranking: a file that IMPORTS the subject is tagged [importer]* |
| M4 | `_importers_of` blind on `.py` | KILLED by *ranking: the importer sorts ahead of every name-match* |
| M5 | caller walk ignores `prefer` | KILLED by *late importer: it is COLLECTED…* |
| M6 | the reserve removed — importers starve the name-match class | KILLED by *reserve: the name-match class SURVIVES a cap-filling importer group* |
| M7 | membership becomes a SUBSTRING test | KILLED by *membership is EXACT: a path CONTAINING an importer's path is not promoted* |
| M8 | tags vanish when nothing imports the subject | KILLED by *zero importers: snippets are STILL tagged, all [name-match]* |
| M9 | the precomputed importer list accepted but not SPENT | KILLED by *findings mode: IMPORTED BY carries the real importers* |
| M10 | snippet path cut at the FIRST colon | KILLED by *a colon in the path: the importer is still tagged [importer]* |
| M11 | a truncated walk still ASSERTS `[name-match]` | KILLED by *truncated walk: the tag degrades to [unranked], never [name-match]* |

M6–M11 were **added by the code review**, which is the point of running one: M7 then *survived*
its own new case. The fixture had no importer at all, so `importer_set` was empty and the exact
test and the substring test agreed on every row — a green that proved nothing. `util.py` now
genuinely imports the subject while `sub/util.py` only name-matches, so the substring mutant
promotes the decoy and the row fails.

`-- restore verified: bytes match, nothing was committed, and git diff --quiet is clean --`
`-- full file, unfiltered: … -> exit 0 -- 144/144 passed --`

## What fought back

**1. The pre-work audit killed the approved design.** A2 was written as "sort before the `[:10]`
slice" — unachievable, because `_find_function_callers` caps its **own** walk at `_CALLER_SNIPPETS`.
Measured, not reasoned: with 12 name-match callers ahead of it, the importer resolved correctly and
was **absent from the output entirely**. A sort cannot reorder a snippet never collected, so two
caps moved instead of one.

**2. The first red died in setup, not on its assertion.** `min()` over an empty list raised
`ValueError` — and a red that raises is indistinguishable from a red that asserts. Rewritten to
compute defensively and fail with the actual order printed.

**3. A shipped counter-example was about to go vacuous.** `not any(s.startswith("src/pkg/target.py:"))`
is False for *every* snippet once snippets lead with a tag — so it would have passed forever while
testing nothing. Now read through `caller_files()`, which strips the tag; its docstring says why.

**4. ⭐ A surviving mutant proved a green case was testing the wrong half.** M2 SURVIVED the first
sweep: the 2d fixture names one identifier, so `prefer` already put the importer at index 0 and the
outer sort had nothing to do. The outer sort only bites *across* identifiers, where a noisy first
identifier fills all ten slots before a later identifier's importer is considered. Case 2e builds
exactly that. **The sweep found this, not the review** — which is the entire argument for the sweep.

**5. Wiring two blocks obliged wiring all nineteen.** `test_suite_runner`'s ORPHAN check failed the
file for its 117 unguarded `c.check` sites. The check is right — a half-blocked file makes `--case`
*look* like it filters while running everything unguarded. Operator ruled option A: *"I want the
option that fixes this and makes it perform the best… we dont take short cuts."* Two things stay
outside a guard on purpose: the `TARGET.is_file()` hard stop, and `src`, which section 7 reads —
guarded, it would be unbound under any filter skipping section 0 and every filtered run would die
on a `NameError`. My own wiring script had a bug worth recording: `next()` matched the **first**
`return c.finish()` — the early exit I had just added — so section 7 never got indented. Caught by
`py_compile`, fixed by taking the last match.

**Cost/benefit of that wiring:** +1073/−703 lines on the test file, zero change to what it proves
(124/124 before and after the re-indent itself; the growth past that is new cases, not new plumbing). This file had **never been mutation-swept** — it declared
no blocks, so `--case` always hit `NO_MATCH` and the sweep could never record a kill. It is
sweepable now, and `--case "SCC-187-A1"` matches 5/23 blocks instead of running the whole file.

## Landing order

`chore/SCC-164-gate-cluster` lands **first** — 7+ commits across six subtasks against this lane's
one pass. Overlap is exactly two append-style ledgers, `docs/_scc_sops_prds/workflows_testing_SOP.md`
and `_artifacts/_main/INDEX.md`; **zero code overlap**. That lane was unpushed at the time of
writing, so it could not be absorbed here — absorb `origin/main` and re-resolve both ledgers at
close-out, then re-run the suite (never before).

## Code Review (2026-08-16)

**Verdict: PASS @ `76daa64f`** — 5-lens engine, `review_mode: full`, `lens_budget: standard`,
`lenses_run: 5/5`. Every finding below was **fixed in this lane before the verdict**; nothing was
deferred, and no finding was turned into a ticket.

### Findings

| # | file:line | Severity | Finding | Disposition |
|---|---|---|---|---|
| 1 | `evidence_extract.py` `_find_function_callers` | **FAIL** | **Real regression.** With ≥10 importers the preferred group filled the cap and the `[name-match]` class was erased entirely — the attribute-dispatch call sites this module exists to surface. Reproduced against `origin/main`, which returns the opposite. | fixed — separate budgets per group plus a reserved slot (M6) |
| 2 | `evidence_extract.py` `_extract_one` | **FAIL** | A deadline-truncated importer walk still asserted `[name-match]`, i.e. *"this file does not import the subject"* — a claim the truncated walk cannot support. The note saying the walk was partial goes to stderr, which no consumer of stdout reads. | fixed — walks return `(importers, complete)`; the tag degrades to `[unranked]` (M11) |
| 3 | `evidence_extract.py` `_snippet_file` | **FAIL** | A POSIX path may contain `:`, and the snippet header is `<rel>:<line>`. Splitting on the first colon cut `pkg/a:b.py:3` to `pkg/a`, so a genuine importer was tagged `[name-match]` while `IMPORTED BY` listed it — the same JSON object contradicting itself. The test helper repeated the bug, so it could not see it. | fixed — `rsplit(":", 1)`, helper corrected (M10) |
| 4 | `evidence_extract.py` `_importers_of` | **CONCERNS** | Hoisting the walk into `_extract_one` dropped `_build_import_context`'s skip-dir guard, buying a full repo walk per `node_modules/` finding whose result is then discarded. | fixed — guard restored at the single new home |
| 5 | `test_evidence_extract.py` block 6 | **CONCERNS** | The spawn-block harness was declared *inside* another block, so `--case` could never select it: the label returns `NO_MATCH`, which `mutation_sweep` records as SWEEP ERROR rather than a kill. ORPHAN cannot see this class. | fixed — dedented, **and** a new `NESTED` check added over all 13 wired files, with two controls |
| 6 | `evidence_extract.py` docstring | **CONCERNS** | The byte count was stale by ~4.8 KB *on the commit that introduced it* — a self-invalidating figure. | fixed — stated as bounds, with the reason |
| 7 | `test_evidence_extract.py` block A1f | **CONCERNS** | Found by the post-fix sweep, not the lenses: M7 survived because the exact-membership fixture had no importer, so both branches agreed and the row proved nothing. | fixed — real importer added, plus a counter-example row |

### Gates

| Gate | Result |
|---|---|
| Suite receipt | `[PASS] suite exit=0 113.1s @ 76daa64f`, clean tree, `32/32` files |
| `test_evidence_extract.py` | **144/144** |
| `test_suite_runner.py` | **79/79**, ORPHAN `[]` and NESTED `[]` |
| `workflow_lint --toolkit-only` | exit 0 — 0 errors, 0 warnings, 8 info |
| `sop_currency.py` | exit 0 |
| `py_compile` | exit 0 on all three changed `.py` |
| Mutation sweep | **11/11 killed**, restore verified |

### Acceptance

| Item | Verdict |
|---|---|
| **A1** tags + order + both classes survive | MET — and hardened: finding 1 showed "both classes survive" was false above 9 importers |
| **A2** a late importer survives BOTH caps | MET |
| **A3** docstring provenance + drop hazard | MET by inspection |
| **A4** every SCC-123 invariant | MET — stdlib only, zero spawning, degrade-never-traceback, exit 2 for usage errors, `python3` throughout |

### Clean-Code Gate — PASS

Machine floor green on the changed set: `run_all.py` 32/32 exit 0 · `workflow_lint --toolkit-only`
0 errors 0 warnings · `sop_currency` exit 0 · `py_compile` exit 0 · 4 Markdown links resolved, 0
dead · door parity n/a (no command added, renamed or deleted). No linter or type checker exists in
this repo — **not applicable**, not skipped.

One judgment finding, applied: four new comment blocks carried the *reason* but not the ticket key,
against the comment contract's "the key AND what it was for". `SCC-187` added to each. No secret,
no debug output, no commented-out code, no hardcoded absolute path, no bare `python`. The one
`except Exception` in the diff logs its reason and converts to a **FAILED row**, so it is a guard
that can be seen to fire, not a swallow.

**Two blocks share the label `0 · the subject exists and refuses nonsense`** — checked, and correct:
they are mutually exclusive branches of the missing-subject early return, so exactly one is ever
reachable and `--case "0 ·"` selects whichever is live.

## Your Actions

- [ ] Land `chore/SCC-164-gate-cluster` first, then absorb `origin/main` into this lane and
      re-resolve the two ledger files before closing out.
- [ ] Close out with `/smh-close-task-merge-tree --expect-key SCC-187` — invoking it is your
      per-merge sign-off; this lane never merges itself.

Decided and recorded, nothing owed: the `--pack` wiring, spill-not-truncate and `ast` symbol
definitions stay CLOSED on SCC-187 as measured (`nc_review_engine` scored 5/5 cold at `305e75d`).
The reopen trigger is deliberately a real review where the literal lens demonstrably misses a
symbol-level defect — not another proposal document.
