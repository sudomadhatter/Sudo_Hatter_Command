# SCC-129 — Gate the gate: seeded bad-diff fixture + engine reviews its own diff

- **Ticket:** SCC-129 (Subtask of SCC-116) — *"Permanent negative-control fixture in the test
  suite: engine must REJECT a seeded bad diff and PASS a clean one (a check that cannot fail is a
  finding). Then /smh-code-review runs the new engine on its own final diff."*
- **Branch:** `chore/SCC-129-gate-the-gate` @ 5dadcd6 (off main) · worktree
  `.claude/worktrees/gate-the-gate`
- **Spec:** `_artifacts/_main/2026-08-12_scc-116-house-review-engine/implementation_plan.md` §SCC-129
- **Baseline gate:** run_all 21/21 files, 1702/1702 cases · workflow_lint --toolkit-only 0/0 ·
  check_maps green

## The shape decision — what "the engine must reject" becomes

The engine is five markdown files executed by an LLM; the enforcement suite is stdlib-only and
deterministic. "The engine rejects the bad diff" cannot be a unit test in `run_all.py` as written.
Three options were on the table:

- **(a) Reference implementation of step-03's scoring in Python** — rejected: a second source of
  truth that drifts from the markdown that actually runs. It would test the copy, not the engine.
- **(b) Record one live run and assert the recording** — rejected: characterization. Proves the
  engine rejected the diff once, not that it will again; the recording rots silently.
- **(c) Split the halves** — **chosen.** A mechanical, permanent guard on the FIXTURE (the thing a
  deterministic suite *can* hold), and a live negative control at the review gate with evidence in
  the walkthrough (the thing only an LLM run can prove). The mechanical half is what stops the
  control from being silently neutered later — the exact way this kind of control dies — and its
  test says honestly that it asserts intactness, not engine behavior.

## Checkable acceptance list (fixed in Step 1 of /smh-quick-dev)

| # | Item | Proving assertion |
|---|---|---|
| 1 | Fixture dir `.agents/scripts/tests/fixtures/nc_review_engine/` exists, permanent: `bad.diff`, `clean.diff`, `manifest.json`, `spec.md`, `codebase/`, `README.md` | structure checks in the new test file |
| 2 | Exactly one seeded defect per lens — {blind, edge, literal, acceptance, test-adequacy} | set-equality check |
| 3 | `test_review_fixture.py` in run_all asserts intactness: each defect marker present exactly once in `bad.diff` ADDED lines; `clean.diff` carries none; both diffs `git apply --check`; spec still carries the violated clause | the test file itself, run via run_all |
| 4 | Every intactness check is self-proving (per-defect in-memory mutation → red; defect list non-empty first) | the mutation loop inside the test |
| 5 | run_all goes red when a defect is removed on disk | one-time proof, RED pasted in walkthrough, then restored |
| 6 | Live: engine on `bad.diff` reports all 5 defects, `severity_floor: FAIL` | pasted engine summary in walkthrough |
| 7 | Live: engine on `clean.diff` → no critical/important, `severity_floor: none` | pasted engine summary in walkthrough |
| 8 | `/smh-code-review` runs the engine on this lane's own final diff | `Verdict: … @ <sha>` line in walkthrough |
| 9 | Full gate green at landing sha; case total additive from 1702 with the delta stated; SOP suite-count line refreshed | pasted bare runs |

## Fixture design

**Layout** (all under `.agents/scripts/tests/fixtures/nc_review_engine/`):

```
manifest.json      _negative_control: true, NC_ ids (eval-harness convention)
bad.diff           unified diff vs codebase/ — five seeded defects, one per lens
clean.diff         unified diff vs codebase/ — correct, spec-consistent, tested change
spec.md            the STORY_FILE for the acceptance lens; carries the clause NC_ACCEPT violates
codebase/          committed BASE state both diffs apply to (billing.py, helpers.py)
README.md          what this is + the exact caller-contract invocation for the live control
```

`run_all.py` globs `test_*.py` non-recursively in `tests/`, so nothing under `fixtures/` is
executed as a test. `sop_currency.py` exempts `.agents/scripts/tests/` — no SOP gate trigger,
but the SOP's suite-count line (currently "1091 checks across 21 files, measured 2026-08-12",
already stale) is refreshed in the landing commit anyway.

**The base module** — `codebase/billing.py` (correct) + `codebase/helpers.py` (`parse(text)`,
one argument, the real definition the literal lens must open). Diff paths point at the real
repo-relative fixture paths, so `git apply --check` runs from the repo root against the committed
base, and a live run's repo-access lenses open real committed files.

**The five seeded defects** — one per lens, each catchable ONLY with that lens's inputs where
possible (literal needs the repo definition; acceptance needs the spec; blind is provable in-diff):

| id | lens | seeded defect | marker (`diff_must_contain`) | expected severity |
|---|---|---|---|---|
| `NC_BLIND` | blind | `invoice_total` returns `subtotal - tax_amount` while the docstring in the same hunk says the total INCLUDES tax — silent wrong result, provable from the diff alone | `return subtotal - tax_amount` | critical |
| `NC_EDGE` | edge | new `unit_price` divides by `quantity` with no zero guard, zero reachable | `return total / quantity` | important |
| `NC_LITERAL` | literal | `helpers.parse(raw, strict=True)` — the committed `parse(text)` takes one argument; the call cannot bind | `helpers.parse(raw, strict=True)` | critical |
| `NC_ACCEPT` | acceptance | `record_payment` clamps a negative amount to 0; `spec.md` §2 says it MUST raise `ValueError` (also pinned: `spec_must_contain: "MUST raise ValueError"`) | `amount = 0` (uniqueness asserted) | critical |
| `NC_TESTADQ` | test-adequacy | all this new deterministic logic lands with zero test files in the diff — asserted as a property (`no test file paths in bad.diff`) plus its marker | `def unit_price(` | important |

Expected live outcome on `bad.diff`: 3 critical + 2 important surviving as `patch`/`decision` →
`severity_floor: FAIL` per step-03 §5. Attribution target: each designated lens reports its own
defect (for `NC_LITERAL`/`NC_ACCEPT` only the designated lens has the inputs to). Any shortfall is
reported honestly in the walkthrough and judged at the gate, not papered over.

**`clean.diff`** — adds a correct `refund()` (raises on negative, mirroring the spec) PLUS a unit
test for it in the same diff. Substantive enough that a flag-everything reviewer would flag it;
correct, spec-consistent and tested so an honest one must return no critical/important. Both
halves, always: the bad-diff half alone cannot distinguish a working reviewer from one that
rejects everything.

## The mechanical guard — `test_review_fixture.py`

Stdlib-only, no pytest, `Cases` harness, same as every sibling. Docstring states the honesty
boundary up front: **this file asserts the fixture is INTACT — it never asserts an LLM found
anything.** Checks:

- **A. Structure** — every fixture file exists non-empty; manifest parses (JSON, stdlib);
  `_negative_control` is `true`; every id `NC_`-prefixed and unique.
- **B. Lens coverage** — defect lens set == the five lenses, exactly.
- **C. Intactness** — each `diff_must_contain` present **exactly once** in `bad.diff`'s added
  (`+`) lines (exactly-once keeps the removal proof meaningful); `NC_ACCEPT`'s
  `spec_must_contain` present in `spec.md`.
- **D. Self-proof** — defect list asserted non-empty FIRST (`all()` over empty is the exact trap
  named in the brief), then per-defect: drop the marker line in memory → check C must go red.
- **E. Clean control** — `clean.diff` non-empty, contains NO defect marker in its added lines.
- **F. Apply-cleanly (rot guard)** — `git apply --check` passes for both diffs against the
  committed base, run bare via subprocess from repo root; plus one in-memory corruption proving
  the apply-check can fail. A diff that stopped applying is a control that silently died.
- **G. Test-adequacy property** — `bad.diff` names no test file in its paths; `clean.diff` does.

⚠️ AUDIT FINDING (baked in): **every red must be actionable for a stranger.** The first person to
see one of these checks fail is whoever edits the fixture months from now. Each failure detail
names the `NC_` id, the file, and the remedy — "restore the marker line, or redesign the defect
and update `manifest.json` in the same commit" — so the gate teaches instead of just refusing
(same principle as the resurrection lint naming its replacement).

Estimated ~40–50 cases; exact count stated in the walkthrough with the additive total.

## Steps

1. **RED** — write `test_review_fixture.py` first, run it: fails on structure (no fixture dir).
   Paste the RED, reading which line raised (structure check, not setup death).
2. **GREEN** — build the fixture (codebase, diffs, manifest, spec, README); run the new test
   green; run the on-disk removal proof (delete `NC_LITERAL`'s marker line from `bad.diff` →
   run_all red → paste → restore byte-identical → green).
3. **Live negative control** — run the engine per its own SKILL.md as the caller: once on
   `bad.diff` (`review_mode: full`, `STORY_FILE: spec.md`, `lens_budget: standard`,
   `WORKTREE`/`REPO` = this worktree, `HEAD_SHA` = current), once on `clean.diff`. Paste both
   summaries into the walkthrough §Evidence. The README records this exact invocation so any
   future session can re-run the control.
4. **SOP refresh + INDEX row** — update the suite-count line in BOTH places that pin it:
   `docs/_scc_sops_prds/workflows_testing_SOP.md` ("1091 checks across 21 files") **and**
   `.agents/scripts/INDEX.md:50` ("1091 cases across 21 files" — ⚠️ AUDIT FINDING: the plan
   originally named only the SOP; the INDEX line even self-describes this exact rot). Add the
   artifacts-ledger row to `_artifacts/_main/INDEX.md`, first cell trailing-slash per SCC-96
   (check_maps gates it).
5. **Commit** (explicit paths, key-prefixed subjects, `-F` if any message carries a backtick),
   walkthrough + `task.yaml` per the artifact contract.
6. **Review gate** — `/smh-code-review`: the engine on this lane's own final diff (acceptance
   item 8 — the integration test the ticket names), acceptance audit, machine floor, verdict into
   the walkthrough. Then STOP for the operator's close-out.

## Traps already paid for, answered

1. **Prose-pinning (SCC-125)** — the guard pins fixture BYTES and manifest WIRING (marker→diff,
   lens→set), never descriptions. No engine prose is pinned here at all.
2. **Guard in the wrong file (SCC-126)** — the guard lives in its own `test_review_fixture.py`
   guarding files it names by path. It adds nothing to `test_review_engine.py`.
3. **Counter-example uniqueness** — this lane adds NO text to any engine file, so no existing
   `str.replace` counter-example can be disarmed. Inside the new test, exactly-once assertions
   protect its own mutations.
4. **Blockquote convention (SCC-127)** — the live run follows step-01's assembly convention as
   written; nothing here edits it.
5. **A check that cannot fail** — every check is proven red first (in-memory per-defect forever;
   on-disk once, pasted). Non-empty asserted before any quantified check.
6. **Run gates bare** — all pasted runs are bare invocations reading `$?` directly; no pipes.
7. **No carve-outs** — nothing here is temporary; nothing to self-expire.

## Boundaries

- **No engine file is touched.** The engine's five markdown files, `test_review_engine.py`, and
  both review commands stay byte-identical. SCC-143 (`lens_budget` default) is adjacent and
  untouched.
- No noise/worthiness filter anywhere (epic boundary, restated).
- The live control is run at this lane's review gate and documented as repeatable in the README;
  it is NOT wired into every future `/smh-code-review` run — mandating a 2× engine spend per
  review is that command's contract change, its own ticket if ever wanted (same discipline that
  kept SCC-143 out of SCC-128).

## Risks

- **Live-control attribution** — a lens may miss its designated defect (LLM nondeterminism). The
  defects are designed loud (critical/important, single-hunk provable), but if a run misses one,
  the honest record is the shortfall + a re-run, not a softened acceptance item. Two consecutive
  misses of the same defect = the defect is not loud enough → redesign that defect, re-prove
  intactness, re-run. That is the control doing its job on the engine.
- **`git apply --check` platform drift** — runs via the same subprocess pattern the harness
  already uses; worktree paths resolved from repo root, not CWD.
- **Fixture Python is deliberately wrong but syntactically valid** — nothing compiles or imports
  `codebase/` (run_all never globs it; py_compile in the clean-code audit is diff-scoped and
  these files are new — they compile fine; the *defects* are semantic).

## Self-Audit (2026-08-13)

**Mode:** PRE-WORK · **Right-size: Full** (adds a file to the enforcement suite — the gate itself).
Subject pinned from command output: `Repo: gate-the-gate | Branch: chore/SCC-129-gate-the-gate`
(worktree of Sudo_Hatter_Command @ 5dadcd6). Plan:
`_artifacts/_main/2026-08-13_scc-129-gate-the-gate/implementation_plan.md` · Ticket: SCC-129.

- **Phase 0 — scope/traceability:** change set = 1 new test file, 1 new fixture dir (6 files),
  2 count-line refreshes (SOP + scripts/INDEX), 1 artifacts-INDEX row, walkthrough + task.yaml.
  All 9 acceptance items trace to steps; every step traces back (Step 5 is lane mechanics). No
  deployable path → correct lane. Checkable list fixed in the plan table.
- **Phase 1 — blast radius:** no file is moved, renamed, deleted, or edited beyond the two count
  lines — new files only, so no reference can break. `run_all.py` auto-discovers `test_*.py`
  non-recursively (fixtures never execute); `sop_currency` exempts `.agents/scripts/tests/`;
  ban-scan (engine dir) and resurrection lint (5 surfaces) never see the fixture; encoding gate
  sees plain ASCII. **Caught:** the suite count is pinned in TWO files, not one — baked into
  Step 4. `check_maps`: session-folder row required (SCC-96 shape); `tests/` itself carries no
  INDEX (verified none exists today, suite green without it). Sibling lanes: `git worktree list`
  shows none live — no landing-order dependency. SCC-143, if it lands first, touches
  `cicd-code-review.md` only — zero overlap with this change set.
- **Phase 2 — over-engineering (strict):** no new command/rule/script/flag; the test file follows
  the one-file-per-subject convention beside `test_review_engine.py`. The `git apply --check` rot
  guard traces to acceptance item 3 (a diff that stopped applying is a dead control). README
  traces to items 6–7 (repeatable live-run contract). Nothing generalizes past N=1. Tripwire
  "a gate that cannot fail" answered by per-check self-proofs. Clean.
- **Phase 3 — pre-mortem:** both machines: stdlib + `git` in PATH (the system is git-driven on
  both); nothing hardcodes `python3`. Fresh clone: fixture travels in-repo, no hook involved.
  Gate-fires-on-a-stranger: every red names the NC id + remedy (baked in above). Escape hatch:
  redesigning the fixture = updating diff + manifest together in one auditable commit — allowed
  by design, no bypass token needed. Empty input: defect list proven non-empty before any
  quantified check; missing git/manifest = red, never skip. Platform caches: no menu change.
  Rollback: pure revert of added files + two lines.
- **Findings table:**

  | file:line | severity | failure scenario | disposition |
  |---|---|---|---|
  | plan §Step 4 (was: SOP only) | important | scripts/INDEX.md:50 count line rots silently — the line itself says so | baked into Step 4 |
  | plan §guard checks | suggestion | a red a stranger can't act on gets `--no-verify`d or reverted blind | baked in: actionable failure details |

- **Four gates:** verification strategy per item — yes, the acceptance table names each proving
  assertion. Irreversible — nothing (Jira start already done, standard). Vague steps — defect
  design is concrete to the marker string; live-control attribution rule stated (two misses →
  redesign, honestly recorded). Convention fit — Cases harness, NC_/`_negative_control`
  convention, SCC-96 row shape, artifacts-always-first.

Audit verdict: GO
