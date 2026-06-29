---
description: Review + gate a story — adversarial code review, then the test gate (suite + TEA trace + nfr + test-review) producing a PASS/CONCERNS/FAIL/WAIVED verdict. Step ③ of the sudo dev flow.
---

# /sudo-code-review — Review + Test Gate (③)

Thin orchestrator — runs your adversarial review, then the test gate, and writes ONE verdict artifact
that `sudo-update-sprint-memory` reads before flipping the story to `done`. Project-scoped (targets THIS
repo). The gate lives HERE; there is no separate `/test-gate` or `/qa-gate`.

> Flow position: `sudo-dev-story-tests` → **`sudo-code-review`** → `sudo-update-sprint-memory`.

## Step 1 — Adversarial code review
Invoke the **`bmad-code-review`** skill on the story's diff (its existing layers + the Test-Adequacy
lens). Apply the actionable fixes yourself; if you change code, re-run the relevant suite(s) and paste
actual output.

## Step 2 — Gate: opt-in check
Read `_bmad-output/sudo-tests.yaml`.
- **Absent** → the project has no test baseline → verdict **`WAIVED`** (do NOT block). Skip to Step 4.
- **Present** → it defines `required_tiers · l1_coverage_min · agent_bearing · nfr · waive`. Continue.

## Step 3 — Gate: run the checks (baseline-diff aware — fail only on NEW regressions)
1. **Suite** — run the `/1_run-all-tests-back_front` command (pytest + vitest). Compare against the red
   baseline; only failures NEW to this story count (legacy red is grandfathered).
2. **`bmad-testarch-trace`** — requirements→tests traceability + coverage vs `l1_coverage_min`.
3. **`bmad-testarch-nfr`** — perf / security / reliability (when `nfr: true` or `agent_bearing: true`).
4. **`bmad-testarch-test-review`** — quality/flake of the tests themselves.

## Step 4 — Verdict
Combine into **PASS / CONCERNS / FAIL / WAIVED** and write
`_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`:
- the review (scope, the passes, each finding with `file:line` + severity + disposition),
- each gate check's result + the **actual** suite output,
- the overall verdict, the story id, and the current `git HEAD` ref (so `sudo-update-sprint-memory` can
  detect a stale verdict).
- **FAIL** = a new test regression or a required tier missing. **CONCERNS** = soft issues only.
  **PASS** = all required tiers green. **WAIVED** = no baseline (Step 2).

## Step 5 — Update the story walkthrough (REQUIRED whenever you found or fixed anything)
The single closing doc for this story is `_artifacts/<epic>/<story>/walkthrough.md` (per the
`artifacts-always-first` rule — the ONE doc holding the narrative + `## Task Checklist` + `## Your
Actions`). The verdict file from Step 4 is an addendum; the **walkthrough is the living source of truth**,
so reflect the review back INTO it in place — never leave it stale (old status, old test count, no
findings):
- Append a `## Code Review (<date>)` section to the body: the verdict, each finding with `file:line` +
  disposition (applied / deferred / dismissed), and a link to `sudo-code-review-<story>.md`. If you changed
  nothing, say so ("Changes applied: none — implementation correct as-is").
- If you changed code: refresh the parts of the body your fixes made stale — the AC/test matrix + test
  counts, the pasted **actual** suite totals, and the `## Task Checklist` (tick the rows your fixes
  completed).
- If your fixes changed the files to commit, update the exact `git add … && git commit` line in
  `## Your Actions` (keep its `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer).
- **Hard rule: NEVER finish `/sudo-code-review` with the walkthrough body left stale after applying fixes.**

## Stay in lane
Never `git commit`/`push`; never flip the story status or edit `sprint-status.yaml` — that is
`sudo-update-sprint-memory`'s job (it reads this verdict first). Updating `walkthrough.md` (Step 5) is IN
lane — that is documenting the review, not flipping status or committing.

Optional additional input: $ARGUMENTS
