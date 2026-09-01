# SCC-187 — rank caller snippets by import, and record what the caps mean

**Ticket:** SCC-187 · **Lane:** `chore/SCC-187-caller-ranking` · **Base:** `origin/main` @ `bc3a851`
**Repo:** Sudo_Hatter_Command (command centre) · **Date:** 2026-08-16

## What this is

`evidence_extract.py --findings` builds the dossier that step-02 of the review engine hands its
verifier and compound roles. Its caller search is a bare repo-wide regex, so a common identifier
pulls in unrelated files, and those arrive presented as ground truth. This lane ranks them by a
signal that already ships and is never consulted, and records two things the docstring does not say.

⭐ **The reward is cleaner verification, not more findings.** Nothing here is expected to change what
a review *finds*; it changes what the verifier has to wade through to confirm it.

**Scope is deliberately small.** The larger proposal this came from (wire `--pack` in, spill instead
of truncate, symbol definitions via `ast`) is CLOSED on the ticket as measured — `nc_review_engine`'s
live run at `305e75d` scored 5/5 cold, including `NC_LITERAL`, the exact defect class it targeted.

## Ground truth read before planning (not recalled)

| Fact | Where |
|---|---|
| `_find_function_callers` matches `\b<ident>\s*\(` repo-wide, returns `"<rel>:<line>\n<snippet>"` | `evidence_extract.py:339-365` |
| It is reached only from `_extract_one` — i.e. `--findings` mode, which step-02 runs on every review producing a finding | `:880` · `steps/step-02-verify.md:94` |
| `_python_importers` / `_ts_importers` both return **repo-relative paths** — directly usable as a membership set | `:408-452` · `:530-554` |
| `_build_import_context` already computes that list **and throws it away**, keeping only a formatted string | `:557-582` |
| Callers are deduped then sliced `[:_CALLER_SNIPPETS]` (10) | `:879-881` |
| `_note()` writes to **stderr only**; callers paste stdout | `:151-154` |
| `_PACK_MAX_CHARS = 16000` is transcribed from pr-af `evidence.py:488`, never derived here | `:94` |

**The fixture already carries both classes** for a finding on `src/pkg/target.py` naming `target_fn`,
so no new base fixture is needed for A1: `src/pkg/user_chain.py` imports **and** calls it, while
`caller_visible.py`, `sibling.py` and `blast_deep.py` call it with **no import**
(`tests/test_evidence_extract.py:143-200`).

## Acceptance — every item checkable by a command

| # | Statement | The assertion that proves it |
|---|---|---|
| **A1** | Caller snippets carry `[importer]` or `[name-match]`, importer hits sort first, and **both classes survive** | new case over `build_python_repo`: assert `user_chain.py` tagged `[importer]`, `caller_visible.py` tagged `[name-match]`, both present, importer's index < name-match's index |
| **A2** | An importer late in scan order **survives both caps** and appears in the output | new case, purpose-built fixture: 12 name-match callers sorting ahead of `zz_importer.py`; assert the importer is present. **Verified RED at plan time** — see the audit finding below |
| **A3** | The docstring records cap **provenance** (transcribed vs derived) and the **stderr-only drop hazard** for whoever wires `--pack` in later | **inspection**, quoted into the walkthrough. The guard case originally planned here was CUT as prose-pinning — see F2 |
| **A4** | Every SCC-123 invariant still holds — stdlib only, zero process spawning, degrade-never-traceback, exit 2 for usage errors | the existing 103-case guard passes bare, spawn-block harness included |

⛔ **A1 is tagging and ordering ONLY — never a filter.** A hard import filter would drop
attribute-dispatch call sites (`self.<attr>.<method>()`), which the module docstring names as exactly
the shape a review needs to see. The "both survive" half of A1 is the guard against that, and M1
below is the mutant that proves the guard is real.

## Steps

**S1 — RED (A1).** Add the case to `test_evidence_extract.py` asserting tags, order and both-survive
over the existing `build_python_repo`. Run it, paste the red, and read *which line raised* — a case
that dies in setup looks identical to one that fails its assertion.

**S2 — RED (A2).** Add the cap-ordering case with its own fixture: 12 name-match callers named to
sort ahead of `zz_importer.py` in `_repo_files`' sorted walk.

> ⚠️ **AUDIT FINDING F1 — the original plan could not have satisfied this, and TWO caps must be
> fixed, not one.** `_find_function_callers` caps its **own** repo walk at `_CALLER_SNIPPETS`
> (`evidence_extract.py:346-348`: `if len(snippets) >= _CALLER_SNIPPETS: break`). Measured on the
> fixture above: the importer is correctly resolved by `_python_importers`, and is **absent from the
> returned snippets entirely** — the walk stopped ten files earlier. A sort in `_extract_one` cannot
> reorder a snippet that was never collected. **Both halves are required:**
>
> 1. **Inner — the walk order.** `_find_function_callers(repo, ident, exclude_rel, prefer=())`
>    scans `prefer` files first, then the rest, each group in `_repo_files`' existing sorted order
>    (so the result stays deterministic). This is what gets the importer *collected*.
> 2. **Outer — the cross-identifier sort.** `_extract_one` slices `[:_CALLER_SNIPPETS]` across up to
>    8 identifiers, so identifier #1 can still fill the cap on its own. The stable sort must precede
>    that slice. This is what keeps the importer *after* the merge.
>
> Fixing only the inner cap leaves the multi-identifier case broken; only the outer leaves the
> single-identifier case broken. **M2 and M5 in the sweep are the two guards.**

**S3 — A3 is an inspection item, not a test.**

> ⚠️ **AUDIT FINDING F2 — the guard case originally planned here is CUT.** A test asserting that a
> docstring passage exists is prose-pinning: it greps prose for prose, any mutant is killed by
> retyping the words, and the house rule is explicit that such guards are vacuous
> (`.agents/rules/tests-must-gate-for-real.md` § the source-grep blind spots). A3 is verified by
> inspection and recorded in the walkthrough — which the lane explicitly permits.

**S4 — GREEN.** Minimal implementation, in this order:

1. **Extract `_importers_of(repo, rel) -> list[str]`** — the extension dispatch currently inlined in
   `_build_import_context:571-577`. Pure refactor, no behavior change.
2. **`_build_import_context(repo, rel, importers=None)`** — accept a precomputed list. ⭐ Without
   this, `_extract_one` walks the repo **twice per finding** (once for the context, once for
   tagging), each under its own 10 s deadline. The operator's ask was *"added speed and accuracy"*;
   a doubled walk trades one for the other.
3. **`_find_function_callers(..., prefer=())`** — scan `prefer` files first, then the rest, each
   group in `_repo_files`' sorted order. Per F1 this is what gets a late importer collected at all.
4. **In `_extract_one`** — compute the importer set **once**, pass it as `prefer` to every
   `_find_function_callers` call and as `importers` to `_build_import_context`, tag each snippet by
   the `rel` in its header, **stable-sort importers first, THEN dedupe and slice**.
5. **Docstring** — the two passages for A3.

**S5 — the receipt run.** Commit first (a receipt over uncommitted code records `DIRTY` and inherits
as invalid), then the one full suite run through the writer:

```bash
python3 .agents/scripts/gate_receipt.py run --task SCC-187 --gate suite \
    --root _artifacts/_main/2026-08-16_SCC-187-caller-ranking --cwd <worktree> \
    -- python3 .agents/scripts/tests/run_all.py
```

**S6 — the mutation sweep**, declared before mutating and drawn **from the code**, via
`mutation_sweep.py --table _artifacts/_main/2026-08-16_SCC-187-caller-ranking/sweep.json`:

| id | Mutation | Must be killed by |
|---|---|---|
| **M1** | drop non-importer snippets instead of ranking them (the filter this lane exists to forbid) | A1 "both survive" |
| **M2** | move the outer sort to after the `[:_CALLER_SNIPPETS]` slice | A2 (multi-identifier half) |
| **M3** | invert the two tag literals | A1 tag assertion |
| **M4** | `_importers_of` returns `[]` for `.py` | A1 order assertion |
| **M5** | `_find_function_callers` ignores `prefer` and walks `_repo_files` unmodified | A2 (inner-cap half, per F1) |

A survivor is a finding. A mutant whose `original` text does not appear verbatim is **DEFECTIVE — a
SKIP that counts as a survivor** — and must be re-aimed before it is believed.

## Landing-order dependency — measured, not assumed

`git -C .claude/worktrees/gate-cluster diff --name-only origin/main...HEAD` against my intended set:

| File | Their lane | This lane | Class |
|---|---|---|---|
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | yes | yes (SOP-currency gate) | **ledger — real overlap** |
| `_artifacts/_main/INDEX.md` | yes | yes (new artifacts row) | **ledger — real overlap** |
| everything else | gate scripts, `jira_feed.py`, `closeout_preflight.py`, `task_preflight.py`, close-out command | `evidence_extract.py` + its test | none |

**`chore/SCC-164-gate-cluster` lands FIRST.** It is 7+ commits deep across six subtasks; this lane is
one small pass. Both overlaps are append-style ledgers, so the reconcile is additive rather than a
rewrite. **If it lands first:** absorb `origin/main` and re-resolve both ledger files before the gate
— re-run the suite after, never before. **If this lane somehow lands first:** nothing of theirs
breaks; they absorb and re-resolve the same two files.

⚠ That lane is **unpushed** (no remote branch as of this writing), so it cannot be absorbed until it
is. Do not wait on it inside this lane — land on the ledgers as they stand and reconcile at close-out.

## Gate note

`sop_currency.py` fires on `.agents/scripts/**/*.py`, so the `evidence_extract.py` commit **must**
stage `docs/_scc_sops_prds/workflows_testing_SOP.md` in the same commit. `.agents/scripts/tests/` is
exempt and `skills/` is not a surface. A1 changes real output shape that a reader of the SOP would
meet, so this is a genuine SOP update — **not** a `[sop-ok]` case.

## Out of scope — do not let these creep in

Wiring `--pack` into the review commands · spill-not-truncate in `build_pack` · symbol definitions via
`ast` · any TS/JS parser · any repo-wide symbol index. All CLOSED on SCC-187 as measured. ⛔ If the
`--pack` wiring is ever revived, wiring and spill ship **together or not at all** — wiring alone
introduces silent evidence loss (the A3 hazard passage exists to tell that person).

---

## Self-Audit (2026-08-16)

**Mode:** PRE-WORK · **Right-size:** Light+ — a contained edit to one script no other script imports
(`grep` confirms only its own test imports it), but it changes an **output shape a review role
consumes** and touches a usage surface, so Phase 3's external-state rows were walked rather than
skipped. Phases 0-2 full, Phase 3 selective, Phase 4 full.

**Phase 0 — scope, checkable list.** Change set: `evidence_extract.py` (4 functions),
`tests/test_evidence_extract.py` (2 new cases), `docs/_scc_sops_prds/workflows_testing_SOP.md`,
this artifacts folder, `_artifacts/_main/INDEX.md`. Acceptance A1-A4 traced both directions: every
item has a step, and every step traces to an item — **except** the A3 guard case, which traced to no
item that inspection could not cover and was CUT (F2). No deployable path in the set, so the lane is
correct: `.agents/scripts/` and `docs/` only.

**Phase 1 — blast radius.** `_build_import_context` has exactly **2 call sites**, both inside
`evidence_extract.py` (`:781` in `build_pack`, `:893` in `_extract_one`); an optional third parameter
is safe for both. No hook, no `.githooks/` caller, no `scripts/INDEX.md` signature claim to update.
`_find_function_callers` has **1 call site** (`:880`). Sibling lanes read live — see the landing-order
table above; the two ledger overlaps are real and named.

**Phase 2 — over-engineering.** One tripwire fired: **a gate that cannot fail** (F2, the prose-pinning
guard) → CUT. `prefer=()` and `importers=None` were each challenged as speculative parameters and both
survive: they are required by a **current** acceptance item (A2 and the doubled-walk cost
respectively), not by a hypothetical. No new command, no new rule, no new script, no clone-and-tweak.

**Phase 3 — pre-mortem, external-state rows only.** *Other machine* — pure stdlib, no interpreter name
in any shipped path; the plan's own commands say `python3` (PC: `python`) ✅. *Empty input* — an empty
importer set makes every snippet `[name-match]` and leaves order unchanged; A1 asserts **both** classes
so it cannot read as a vacuous pass ✅. *Sibling lane lands first* — handled, both overlaps are
append-style ledgers ✅. *Rollback* — one commit on a chore branch, nothing irreversible, no Jira
transition, no delete ✅. *Four platform caches* — N/A, no command or menu surface changes ✅.

### Findings

| # | Where | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| **F1** | `evidence_extract.py:346-348` | **HIGH** | `_find_function_callers` breaks its own walk at `_CALLER_SNIPPETS`. **Measured:** with 12 name-match callers sorting ahead of `zz_importer.py`, the importer resolves correctly via `_python_importers` but is **absent from the returned snippets** — the walk stopped ten files earlier. The planned downstream sort would have shipped green while doing nothing for the case A2 exists to cover | **FIXED IN PLAN** — S2/S4 now require BOTH the inner walk-order `prefer` and the outer sort; M5 added to the sweep |
| **F2** | plan S3 (as written) | LOW | A test asserting a docstring passage exists is prose-pinning — it greps prose for prose and any mutant is killed by retyping the words | **CUT** — A3 is an inspection item, recorded in the walkthrough |
| **F3** | `evidence_extract.py:781,:893` | INFO | Signature change to `_build_import_context` — verified safe, 2 internal call sites, optional param with a default | no action |
| **F4** | `tests/test_evidence_extract.py:143-200` | INFO | A1's fixture claim verified by execution: `user_chain.py` is both importer and caller; `blast_deep.py` / `caller_visible.py` / `sibling.py` are callers only. The importer currently sorts **LAST**, so the RED is unambiguous rather than incidental | no action |

**Landing-order dependency:** `chore/SCC-164-gate-cluster` lands **first** — 7+ commits across six
subtasks vs. this one small pass. Overlap is exactly two append-style ledgers
(`docs/_scc_sops_prds/workflows_testing_SOP.md`, `_artifacts/_main/INDEX.md`); zero code overlap. That
lane is currently **unpushed**, so it cannot be absorbed yet — do not block on it; land on the ledgers
as they stand and reconcile at close-out.

### The four quick gates

- **Verification strategy present?** ✅ Every acceptance item names the command that proves it, and
  A2's red was demonstrated at plan time rather than asserted.
- **Anything irreversible?** ✅ No. One commit on a chore branch; no delete, no rename, no history
  rewrite, no Jira transition, no `main` merge.
- **Any step vague enough that the builder will guess?** ✅ Resolved — F1 was exactly that gap, and
  the two required halves are now written out explicitly.
- **Convention fit?** ✅ Artifacts in `_artifacts/_main/<date>_<slug>/`, sweep through
  `mutation_sweep.py`, receipt through `gate_receipt.py`, SOP staged in the same commit.

Audit verdict: GO
