---
description: Review + gate a story — adversarial code review, then the test gate (suite + TEA trace + nfr + test-review) producing a PASS/CONCERNS/FAIL/WAIVED verdict. Step ③ of the sudo dev flow.
platforms: [opencode, antigravity]
---

# /sudo-code-review — Review + Test Gate (③)

Thin orchestrator — runs your adversarial review, then the test gate, and writes ONE verdict artifact
that `sudo-update-sprint-memory` reads before flipping the story to `done`. Project-scoped (targets THIS
repo). The gate lives HERE; there is no separate `/test-gate` or `/qa-gate`.

> Flow position: `sudo-dev-story-tests` → **`sudo-code-review`** → `sudo-update-sprint-memory`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this command operates on exactly ONE child project under
`Projects/`, never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path — check this FIRST, and STOP here if it matches)** — if this repo has
   **no** `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip straight to the
   binding rule. Do NOT read `active-project.txt`, parse `$ARGUMENTS` for a project name, or ask which
   project — cases 1–3 below are command-center-only (the lobby that hosts children under `Projects/`).
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is
   the target; consume that first token (the remainder is the real argument — story id, focus, …). Write
   the name alone into `.agents/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under
   `Projects/`, use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* —
   never guess, never operate on the lobby.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule (applies to EVERY step below):** every "THIS repo", every `{project-root}`, and every bare
path (`_bmad-output/…`, `_bmad/…`, `_artifacts/…`, story files, test commands) resolves **under
`PROJECT_ROOT`**. When you invoke any nested `bmad-*` / `1_*` skill, bind its `{project-root}` to
`PROJECT_ROOT`, run it against that directory, and read/write only there. If a needed path is missing under
`PROJECT_ROOT`, STOP and say so — never fall back to the lobby.

## Step 1 — Clean-Room Adversarial Code Review
Invoke the **`bmad-code-review`** skill on the story's diff. You MUST act as a **Clean-Room** agent: zero out any builder's bias. Your only job is to aggressively audit the final diff against the strict BDD contract. Hunt specifically for **AI Drift**, over-engineering, bloat, unnecessary abstractions, and logic flaws. Apply the actionable fixes yourself; if you change code, re-run the relevant suite(s) and paste actual output.

## Step 2 — Gate: opt-in check
Read `_bmad-output/sudo-tests.yaml`.
- **Absent** → the project has no test baseline → verdict **`WAIVED`** (do NOT block). Skip to Step 4.
- **Present** → it defines `required_tiers · l1_coverage_min · agent_bearing · nfr · waive`. Continue.

## Step 3 — Gate: run the checks (baseline-diff aware — fail only on NEW regressions)
1. **Suite** — run the `/1_run-all-tests-back_front` command (pytest + vitest). Compare against the red
   baseline; only failures NEW to this story count (legacy red is grandfathered). **Two guards (per
   `tests-must-gate-for-real`):** (a) confirm CI runs the *same real entrypoint* this gate runs — open the
   pipeline YAML and check each test job invokes the project's actual harness command (e.g.
   `npm run test:e2e`), not a divergent/partial config that silently skips the suite that matters; a green
   CI check on a suite that never ran is a FAIL, not a pass. (b) Grandfathering is for *owned* legacy red
   only (known-flaky / quarantined-with-ticket) — a red that asserts strings, selectors, or preconditions
   absent from real source is **fiction, not legacy debt**; do not grandfather it, FAIL and fix/delete it.
2. **`bmad-testarch-trace`** — requirements→tests traceability + coverage vs `l1_coverage_min`.
3. **`bmad-testarch-nfr`** — perf / security / reliability (when `nfr: true` or `agent_bearing: true`).
4. **`bmad-testarch-test-review`** — quality/flake of the tests themselves. Also scan the CI pipeline for
   *soft* test steps (`continue-on-error`, `|| true`, blanket `.skip`/`xfail`, "report-only"): each is a
   hole that reads as green. Per `tests-must-gate-for-real`, a soft gate is legitimate only as a one-run
   window carrying a named owner + a tracked expiry task — flag any that lacks both (CONCERNS floor) and
   name it in the verdict.
5. **Automate evidence** — feature stories only (numeric `E.S` ids; test-only MIN-FLOW stories like
   `tea-*` are exempt): confirm ②'s expansion pass left evidence — `automation-summary-<story>.md` under
   `_bmad-output/test-artifacts/`, or an explicit `## Automate: skipped — <rationale>` section in the
   story walkthrough. Missing BOTH → cap the verdict at **CONCERNS** and name the gap in the verdict file
   (never FAIL on this alone — stories gated before 2026-07-09 predate the check).

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
The single closing doc for this story is `_artifacts/<epic>/<story>/walkthrough.md` — if it wasn't handed
to you, find it there (per the `artifacts-always-first` rule — the ONE doc holding the narrative +
`## Task Checklist` + `## Your Actions`). The verdict file from Step 4 is an addendum; the **walkthrough is
the living source of truth**, so reflect the review back INTO it in place — never leave it stale (old status,
old test count, no findings):
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
