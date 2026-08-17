# Walkthrough — SCC-187 rank caller snippets by import (2026-08-16)

**Lane:** `chore/SCC-187-caller-ranking` · **Base:** `origin/main` @ `bc3a851` · **Repo:** Sudo_Hatter_Command
**Plan:** [implementation_plan.md](implementation_plan.md) — `Audit verdict: GO`
**Plan approval (2026-08-16):** operator, verbatim — *"approved"* — recorded here rather than in the
plan, because editing an approved plan re-arms the plan-first gate.

## What changed

| File | Why |
|---|---|
| `.agents/scripts/evidence_extract.py` | `_find_function_callers` gains `prefer=` (importer files scanned first); `_extract_one` tags every caller snippet `[importer]` / `[name-match]` and stable-sorts importers ahead **before** the cap; `_importers_of()` split out of `_build_import_context` so the importer walk runs once per finding, not once per consumer; docstring records cap provenance + the stderr-only drop hazard |
| `.agents/scripts/tests/test_evidence_extract.py` | 3 new blocks (12 cases); **all 17 sections wired into `c.block` guards**; one existing counter-example made tag-aware |
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

GREEN: `-- 5/5 passed --  -- filter 'SCC-187-A1': matched 1/16 blocks --`

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
[PASS] suite exit=0 116.1s @ 4a9a5f49        receipt: gates/suite.json
```

`workflow_lint --toolkit-only` exit 0 · `check_maps --depth3-only --strict` exit 0 ·
`test_sops_prds_folder.py` exit 0 · `test_evidence_extract.py` **127/127** ·
`test_suite_runner.py` **63/63** with ORPHAN reporting `[]`. The spawn-block harness still passes,
so the zero-subprocess guarantee is unchanged.

### Mutation sweep — 5/5 killed

`sweep.json` → [sweep-result.txt](sweep-result.txt). Table declared before mutating, drawn from the
code.

| id | Mutation | Result |
|---|---|---|
| M1 | ranking becomes filtering | KILLED by *ranking: BOTH classes survive* |
| M2 | outer sort moved after the cap | KILLED by *outer sort: a LATER identifier's importer is not crowded out* |
| M3 | the two tag literals swapped | KILLED by *ranking: a file that IMPORTS the subject is tagged [importer]* |
| M4 | `_importers_of` blind on `.py` | KILLED by *ranking: the importer sorts ahead of every name-match* |
| M5 | caller walk ignores `prefer` | KILLED by *late importer: it is COLLECTED…* |

`-- restore verified: bytes match, nothing was committed, and git diff --quiet is clean --`
`-- full file, unfiltered: … -> exit 0 -- 127/127 passed --`

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

**5. Wiring two blocks obliged wiring all seventeen.** `test_suite_runner`'s ORPHAN check failed the
file for its 117 unguarded `c.check` sites. The check is right — a half-blocked file makes `--case`
*look* like it filters while running everything unguarded. Operator ruled option A: *"I want the
option that fixes this and makes it perform the best… we dont take short cuts."* Two things stay
outside a guard on purpose: the `TARGET.is_file()` hard stop, and `src`, which section 7 reads —
guarded, it would be unbound under any filter skipping section 0 and every filtered run would die
on a `NameError`. My own wiring script had a bug worth recording: `next()` matched the **first**
`return c.finish()` — the early exit I had just added — so section 7 never got indented. Caught by
`py_compile`, fixed by taking the last match.

**Cost/benefit of that wiring:** +736/−710 lines on the test file, zero change to what it proves
(124/124 before and after the re-indent). This file had **never been mutation-swept** — it declared
no blocks, so `--case` always hit `NO_MATCH` and the sweep could never record a kill. It is
sweepable now, and `--case "SCC-187-A1"` matches 1/17 blocks instead of running the whole file.

## Landing order

`chore/SCC-164-gate-cluster` lands **first** — 7+ commits across six subtasks against this lane's
one pass. Overlap is exactly two append-style ledgers, `docs/_scc_sops_prds/workflows_testing_SOP.md`
and `_artifacts/_main/INDEX.md`; **zero code overlap**. That lane was unpushed at the time of
writing, so it could not be absorbed here — absorb `origin/main` and re-resolve both ledgers at
close-out, then re-run the suite (never before).

## Code Review (2026-08-16)

*(appended by `/smh-code-review`)*

## Your Actions

- [ ] Land `chore/SCC-164-gate-cluster` first, then absorb `origin/main` into this lane and
      re-resolve the two ledger files before closing out.
- [ ] Close out with `/smh-close-task-merge-tree --expect-key SCC-187` — invoking it is your
      per-merge sign-off; this lane never merges itself.

Decided and recorded, nothing owed: the `--pack` wiring, spill-not-truncate and `ast` symbol
definitions stay CLOSED on SCC-187 as measured (`nc_review_engine` scored 5/5 cold at `305e75d`).
The reopen trigger is deliberately a real review where the literal lens demonstrably misses a
symbol-level defect — not another proposal document.
