# SCC-83 — Implementation Plan: the SOP folder's prose was never checked

**Date:** 2026-08-11 · **Repo:** Sudo_Hatter_Command (lobby) · **Lane:** Task (LOCAL)
**Branch:** `chore/SCC-83-sop-content-audit` · **Base:** `ef0af3a` (clean main, SCC-82 landed)
**Subtasks:** SCC-84 · SCC-85 · SCC-86 · SCC-87

## The problem in one line

SCC-74 moved these docs where the drift-checkers could see them, and **all three checkers only ask
whether a pointer resolves — none asks whether the prose is true.**

| Checker | Reads | Blind to |
|---|---|---|
| `test_sops_prds_folder.py` | filenames, markdown **link** targets, `/command` names | backticked paths in prose |
| `check_maps.py` | backticked paths **inside table rows only** | the same path in a sentence, bullet or fence |
| `sop_currency.py` | did you *touch* the doc in the same commit | whether what you wrote is correct |

**Proof it is a live gap, and it is not theoretical:** `workflows_testing_SOP.md` still said
*"13-doc manifest"* after SCC-80 took it to 11 — stale text inside the page documenting the test
built to prevent staleness, every gate green. Found by accident during SCC-82.

**⛔ And the freshness signal is dead.** SCC-74 moved the files with `git mv`, so all twelve report
a last-commit date of `2026-08-10`. Every doc in the folder looks like it was updated yesterday.
`git log` can no longer rank these by rot; only `--follow` can, and nothing does.

## The numbers, ground-truthed (this is the load-bearing part)

A first crude sweep reported **181** missing references. **The true count is 28.** That gap is not a
footnote — it is the design constraint for SCC-87, because a check that reproduces the crude sweep is
worse than no check at all.

| Class | Count | Verdict |
|---|---|---|
| Resolve **nowhere** | **28** | the work |
| Resolve against `Projects/AGY_AVIATIONCHAT/` | 73 | project-relative, ambiguous not broken — **48 in `tea_testing_guide.md` alone** |
| Bare filenames (`conftest.py`, `walkthrough.md`) | 76 | prose shorthand, never paths |
| Branch names, URL routes, model ids, globs | 2392 | excluded before counting |

## Acceptance — every item is a command, and Step 2 makes each one fail first

| # | Statement | The assertion that proves it |
|---|---|---|
| A1 | No prose path reference in the folder resolves nowhere | new `test_sop_prose_paths.py` reports **0** unresolved, exit 0 |
| A2 | The check **fires** on a planted dead prose path | fixture: plant `docs/x/nope.md` in a sentence → check reports it |
| A3a | It stays quiet on a **bare filename** | fixture: `` `conftest.py` `` in prose → 0 findings |
| A3b | It stays quiet on a **project-relative** path | fixture: `` `backend/tests/` `` resolving under `Projects/<n>/` → 0 findings |
| A3c | It **degrades to silence** when `Projects/` is unpopulated | fixture: empty `Projects/<n>/` → 0 findings, **not** a false worklist |
| **A3d** | It stays quiet on the **non-path token classes** | fixture, one each: branch name `origin/main` · `epic/AVCH-13-x` · URL route `/api/incident/fire` · model id `openrouter/z-ai/glm-5.2` · npm scope `@firebase/rules-unit-testing` |
| A4 | The two by-design absences are never "fixed" into existence | `.agents/scripts/git-hooks/DISABLE` and `_pipeline/*` still absent; fixture proves the allow-list stays narrow, and **every entry carries a written reason** |
| A5 | The suite runs it on both machines with no wiring | `run_all.py` N/N exit 0, file auto-discovered |
| A6 | SCC-82's baseline is not given back | `workflow_lint.py --toolkit-only` exit 0, **0 errors 0 warnings** |
| A7 | The SOP moves with any usage-surface change | `sop_currency.py` exit 0, or `[sop-ok]` recorded with a reason |
| **A8** | The folder's dead freshness signal is written down | inspection: `INDEX.md` states that `git log` dates are meaningless here post-`git mv` and `--follow` is required |

> ⚠️ **AUDIT FINDING F1 (HIGH) — A3d did not exist and is the biggest hole.** A3a/b/c cover 149 of
> the crude sweep's 153 false positives. The remaining exclusion class is the **largest by far —
> 2392 tokens** — and it was thrown away by a `NOT_A_PATH` regex that was a **guess with no fixture**.
> Too narrow and the false positives come straight back; too broad and real defects vanish silently.
> An unfixtured regex deciding what is *not* worth checking is exactly the kind of invisible
> off-switch this lane exists to remove. A3d added above.
>
> ⚠️ **AUDIT FINDING F6 (MEDIUM) — S5 traced to no acceptance item**, which by this plan's own rule is
> scope creep. It is real work (it comes from SCC-87's own AC5), so the fix is A8, not a cut.

## Steps, each naming its assertion

**S1 — SCC-87 RED (does the whole set, so it goes first).** Add **T9** to the existing
`.agents/scripts/tests/test_sops_prds_folder.py`, with A2 and A3a–A3d as fixtures, **before** any doc
is edited. Run it: A2 must fail-to-fire and A1 must report 28. Paste the real output; read *which
line raised*.

> ⚠️ **AUDIT FINDING F2 (HIGH) — the plan said "write `test_sop_prose_paths.py`", and that is a
> Phase-2 tripwire: a new file where an existing one should grow.** `test_sops_prds_folder.py`
> already owns this folder — same `FOLDER`/`FOLDER_REL` constants, same `EXPECTED` manifest, same
> `det()` helper — and its **T3 is the sibling concern** (this folder's *links*), so prose paths
> belong beside it, not in a second file that re-derives the same constants and can drift from them.
> Memory `red-file-hosts-expansion-tests`: **one red file per tier; extend, never fork.** New file CUT.
>
> ⚠️ **AUDIT FINDING F3 (HIGH) — vacuous green, and this system has already shipped this exact bug.**
> In SCC-74, T3/T4 passed on an empty folder, which meant *deleting the folder would have made the
> suite healthier*. A fresh prose check would have had to rebuild that guard and could easily have
> forgotten. Extending the host **inherits it for free**: `scannable` at
> `test_sops_prds_folder.py:216` already fails loudly rather than passing on nothing. T9 must sit
> inside that same guard. This finding is a *consequence* of F2 and is the strongest argument for it.

> ⭐ **The three controls ARE the deliverable.** The crude sweep's 153 false positives came from
> exactly these classes, and A3c is the one that has burned this system repeatedly: `Projects/` is an
> empty stub in every worktree, so a naive checker calls every project path dead in every lane. Same
> ruling as `rotted_pointers()` in SCC-80 — **return nothing rather than a worklist that is mostly
> wrong**, because a signal with that hit-rate is one people learn to skip.

**S2 — SCC-84 GREEN (5 refs).** Repoint references to surfaces SCC-74/SCC-66 deleted. Two name *this
folder's own files* at their pre-move path; one names `.claude/commands/`, retired by SCC-66 in favour
of generated launcher skills. Where the target is genuinely gone, past tense — never a live-looking
path. *Assertion: A1 drops by 5.*

**S3 — SCC-85 GREEN (12 refs).** State the project root **once per document** rather than prefixing
70+ paths, then correct only what is wrong against that root, and mark generated output (`htmlcov/`)
as generated. *Assertion: A1 drops by 12, A3b still quiet.*

> ⛔ **Do NOT bulk-prefix.** It would bury the real question — whether an AviationChat field guide
> belongs in the lobby at all — under a cosmetic sweep. That is an **AVCH** architecture call and is
> explicitly out of scope here.

**S4 — SCC-86 GREEN (11 refs).** One-offs, each answered individually. Two must NOT be created:
`git-hooks/DISABLE` is a kill switch whose **absence is the armed state**, and `_pipeline/*` is
runtime output. One is a typo with teeth — the SOP writes `tests/test_sops_prds_folder.py` for
`.agents/scripts/tests/…`, in the row describing the test that guards this folder.
*Assertion: A1 reaches 0; A4 fixture proves the allow-list did not become an off-switch.*

**S5 — the freshness signal.** Record in the folder's `INDEX.md` that `git log` dates are meaningless
here post-`git mv`, and that `--follow` is required. *Assertion: inspection.*

**S6 — gates.** A5, A6, A7.

## Landing order

`chore/SCC-77-main-write-gate` also edits `workflows_testing_SOP.md` (at its pre-SCC-74 path;
verified by `git merge-tree` that rename detection carries it correctly and does **not** resurrect
`_my_resources/_quick_reference/`). **Overlap on one file, so whichever lands second merges main down
first.** No correctness dependency either way. `chore/SCC-73-memory-relocation` is empty.

## Out of scope, deliberately

- **`tea_testing_guide.md`'s residency** — 48 of the 73 project-relative refs. AVCH ticket.
- **AGY's stale `sudo_workflows_testing.md`** — different repo, needs its own key.
- Rewriting these docs for quality. This lane fixes references and builds the check that keeps them
  honest. Compaction is a separate decision with the operator.

---

## Self-Audit (2026-08-11)

**Mode:** PRE-WORK · **Right-size:** **Full** — the plan adds a check to a `run_all` test, edits a
doc that other files link to, and touches `docs/_scc_sops_prds/INDEX.md` whose rows `check_maps`
parses.

| Phase | Walked |
|---|---|
| **0 — scope + checkable list** | Change set named (1 test file, ≤10 docs, 1 INDEX). Acceptance taken from the SCC-83/84/85/86/87 ACCEPTANCE blocks. **Traceability caught one break: S5 traced to no acceptance row → F6, fixed by adding A8** (not cut — it is real work from SCC-87 AC5). Lane check: **no deployable path in the change set → LOCAL**, confirmed against `backend/ frontend/ firebase/ functions/ mobile/ .github/`. |
| **1 — blast radius** | Docs only + one test. No command renamed → no door to orphan. No rule touched → `_RULE_POINTERS` unaffected. No script signature changed → no hook breaks on someone else's commit. **`workflows_testing_SOP.md` is a usage surface → `sop_currency` fires → A7.** Sibling read: `SCC-77` overlaps on that one file; `git merge-tree` verified **clean**, rename detection carries its pre-SCC-74-path edit into the relocated file and does **not** resurrect `_my_resources/_quick_reference/`. `SCC-73` is empty. |
| **2 — over-engineering (STRICT)** | **One tripwire fired: F2**, new script where an existing one should grow. Disposition **CUT**, and cutting it also resolves F3 for free. No new command, no new rule, no new flag, no N-generalisation. |
| **3 — pre-mortem** | Walked below. |

### Pre-mortem rows that carry risk

| Scenario | Handled? | |
|---|---|---|
| **The other machine** (`python` vs `python3`) | Yes — T9 lives in the host test, invoked by `run_all.py` exactly as its 11 siblings are. No new invocation path. | ✅ |
| **Empty input reads as PASS** | **Was NOT handled — F3.** Now handled by extending inside the existing `scannable` guard. | ✅ *(after F2/F3)* |
| **A sibling lane lands first** | Yes — SCC-77 overlap named, merge-tree verified clean, whoever lands second merges main down. | ✅ |
| **The escape hatch** | Allow-list for by-design absences, **each entry carrying a written reason** (A4) — the `DISCUSSED_AS_RETIRED` precedent from SCC-74. | ✅ |
| **A gate that cannot fail** | **This was the real danger — F1.** A 2392-token exclusion regex with no fixture is a gate that silently decides what not to check. A3d makes it falsifiable. | ✅ *(after F1)* |
| **Rollback** | Doc edits and one additive test; `git revert` undoes it. Nothing irreversible: no delete, no history rewrite, no Jira transition in this lane. | ✅ |
| **Fresh clone / `core.hooksPath`** | N/A — nothing here ships as a hook. | — |
| **Four platform caches** | N/A — no menu surface changes. | — |

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | acceptance table | **HIGH** | The 2392-token `NOT_A_PATH` exclusion is an unfixtured guess. Too broad → real dead references are silently skipped and the check reads green forever; too narrow → the 153 false positives return and the signal gets ignored. | **A3d added** — one control per sub-class |
| F2 | S1 | **HIGH** | A second test file re-derives `FOLDER`, `EXPECTED` and the harness helpers, then drifts from the host that owns the same folder. | **CUT the new file; extend as T9** |
| F3 | S1 | **HIGH** | Zero tokens scanned reads as a pass — the precise bug SCC-74 shipped, where deleting the folder would have made the suite *healthier*. | Resolved by F2 — inherits `scannable` at `test_sops_prds_folder.py:216` |
| F4 | S1 scope | MED | The check reads **backticked** tokens only. Measured: exactly **2** bare path-shaped tokens exist outside backticks folder-wide, so the scope is right — but unstated, the next reader assumes total coverage. | **State it as a third row** in the INDEX mechanism-boundary table, beside `check_maps`' table-rows-only limit |
| F5 | A4 | MED | An allow-list is one line from being an off-switch. | Each entry needs a written reason + the narrowness fixture |
| F6 | S5 | MED | Step with no acceptance row = scope creep by this plan's own rule. | **A8 added** |

### Four gates

- **Verification strategy present?** Yes — every acceptance row names the command and the output that proves it, and S1 runs before any doc edit so each fix has a measurable before/after.
- **Anything irreversible?** No. Doc edits + one additive test. No delete, no rename, no force-push, no `main` merge in this lane.
- **Any step vague enough that the builder will guess?** One was: *"a check that would have caught them"* left the false-positive contract implicit. F1/A3d makes it explicit.
- **Convention fit?** Yes — extends the existing red file (`red-file-hosts-expansion-tests`), keeps the allow-list-with-reasons pattern (SCC-74 `DISCUSSED_AS_RETIRED`, SCC-82 `ap_reconciled`), and follows SCC-80's *return nothing rather than a mostly-wrong worklist* ruling.

**Findings baked into the plan above. Phases 0 and 2 re-walked after the edits; both clear.**

```
Audit verdict: GO
```
