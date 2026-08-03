---
description: Review + gate a story — adversarial code review, then the test gate (suite + TEA trace + nfr + test-review) and the clean-code gate (code-standards conformance), producing a PASS/CONCERNS/FAIL/WAIVED verdict. Step ③ of the sudo dev flow.
platforms: [opencode, antigravity]
---

# /sudo-code-review — Review + Test Gate + Clean-Code Gate (③)

Thin orchestrator — runs your adversarial review, then the test gate, then the clean-code gate, and writes
ONE verdict artifact that `sudo-update-sprint-memory` reads before flipping the story to `done`.
Project-scoped (targets THIS repo). Both gates live HERE; there is no separate `/test-gate`, `/qa-gate`,
or `/lint-gate`.

> Flow position: `sudo-dev-story-tests` → **`sudo-code-review`** → `sudo-update-sprint-memory`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/sudo-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the lobby.
Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>` before any work. Every bare path below
resolves under `PROJECT_ROOT` (nested `bmad-*`/`1_*` skills bind their `{project-root}` to it); a needed
path missing under `PROJECT_ROOT` → STOP, never fall back to the lobby.

## Step 0.5 — Re-enter the story worktree if one already exists (fresh-chat resume)
Before Step 1: `git worktree list` under `PROJECT_ROOT` (`worktree-per-story` → "Resuming"). A
`claude/<story-slug>` tree exists → **cd into it and bind the diff, story file, tests, and suite commands
under it** (the built code often lives ONLY there — the shared checkout would audit an empty or stale
diff); echo `Worktree: reviewing in <path>`. None → review in `PROJECT_ROOT` as usual. Artifacts too:
this story's plan/walkthrough/verdict live in THIS tree — absent here = that step never ran; a lookalike
in the shared checkout is a SIBLING lane's, not evidence. Echo the story's ①②③ step-state before Step 1.

## Step 1 — Clean-Room Adversarial Code Review
Invoke the **`bmad-code-review`** skill on the story's diff. You MUST act as a **Clean-Room** agent: zero out any builder's bias. Your only job is to aggressively audit the final diff against the strict BDD contract. Hunt specifically for **AI Drift**, over-engineering, bloat, unnecessary abstractions, and logic flaws. Apply the actionable fixes yourself; if you change code, re-run the relevant suite(s) — scoped, not full; the ONE full-suite run lands after your last change (Step 3.1) — and paste actual output.

## Step 2 — Gate: opt-in check
Read `_bmad-output/sudo-tests.yaml`.
- **Absent** → the project has no test baseline → verdict **`WAIVED`** (do NOT block). Skip to Step 4.
- **Present** → it defines `required_tiers · l1_coverage_min · agent_bearing · nfr · waive`. Continue.

## Step 3 — Gate: run the checks (baseline-diff aware — fail only on NEW regressions)
1. **Suite — ONE full run, measured on the FINAL SHA (diff-scoped stacks).** Stacks in scope = the ones
   the diff touched (backend pytest via `backend/.venv` with the project's canonical runner flags — the ONE
   source of truth is the runner AIDEV-NOTE in `backend/requirements.txt`; frontend vitest). Run the OTHER stack only when the diff touched a shared cross-boundary surface (API/SSE
   schema, shared types/contract files) — otherwise skip it and say so (PR CI + `/sudo-e2e` still run
   both stacks before anything ships). The verdict needs the full suite green exactly ONCE, on the exact
   code that will land — never burn a full run proving greens on code you are about to change:
   - **Inherit ②'s baseline instead of re-running it — via a MECHANICAL check, not a judgment call.**
     ② Step 4.5 emits `_bmad-output/test-artifacts/certification-<story>.json`
     (`{story, sha, utc, stacks:{<stack>:{cmd, passed, skipped, failed, seconds}}}`). Read it and compare
     its `sha` to `git rev-parse HEAD` on the worktree under review:
     - **`sha` == HEAD and `failed: 0`** → adopt as the entry baseline. Cite the file. Do not re-run.
     - **File absent, `sha` mismatched, a touched stack missing from `stacks`, or any `failed` > 0** →
       run the full suite up front yourself. **Fail toward running, never toward trusting.**
     No file (a pre-contract story, or a lane that skipped ② Step 4.5) → fall back to ②'s pasted
     walkthrough totals + SHA under the same equality test; anything less specific than an exact SHA is a
     miss, not a partial credit.
   - **While reviewing/fixing, run scoped** — the story's contract file + the suites of the modules you
     touched.
   - **After your LAST code/test change, run the FULL suite once** and paste the real output; record
     `git rev-parse HEAD` beside it, and **refresh `certification-<story>.json` to your SHA** (you are now
     the certifying run). Artifact/doc-only commits after this run do NOT invalidate it — only code or test
     changes force a re-run. Changed nothing at all? Then ②'s inherited green (SHA verified) IS the
     evidence — spot-run the story's own test file as a cheap independent probe and cite both. This
     replaces the old "full suite on arrival" rule, which could land a final SHA whose full green was
     measured on a DIFFERENT (pre-fix) SHA — the new invariant is strictly stronger.
   - **Append your suite runs to the walkthrough's `## Suite Ledger`** (the table is per STORY, ②+③) —
     `scope · command · duration · result · why this run`.
   Compare against the red baseline; only failures NEW to this story count (legacy red is grandfathered). **Two guards (per
   `tests-must-gate-for-real`):** (a) **CI-entrypoint audit — change-triggered, not per-story.** Run it only
   when the diff touches `.github/workflows/**` or a test-runner config, when `sudo-tests.yaml` has no
   `ci_audit:` record, or when `git log -1 --format=%H -- .github/workflows/` differs from the recorded
   `ci_audit.sha`. When it runs: open the pipeline YAML and confirm each test job invokes the project's
   actual harness command (e.g. `npm run test:e2e`), not a divergent/partial config — a green CI check on
   a suite that never ran is a FAIL, not a pass — then write `ci_audit: {sha, date}` back into
   `sudo-tests.yaml`. When skipped, state `CI audit current as of <sha>` in the verdict. (b) Grandfathering is for *owned* legacy red
   only (known-flaky / quarantined-with-ticket) — a red that asserts strings, selectors, or preconditions
   absent from real source is **fiction, not legacy debt**; do not grandfather it, FAIL and fix/delete it.
2. **`bmad-testarch-trace`** — gate coverage vs `l1_coverage_min`.
3. **`bmad-testarch-nfr`** — when `nfr: true` or `agent_bearing: true`.
4. **`bmad-testarch-test-review`**. Also scan the CI pipeline for
   *soft* test steps (`continue-on-error`, `|| true`, blanket `.skip`/`xfail`, "report-only") — on the
   SAME change-trigger as guard (a), never per-story: each is a
   hole that reads as green. Per `tests-must-gate-for-real`, a soft gate is legitimate only as a one-run
   window carrying a named owner + a tracked expiry task — flag any that lacks both (CONCERNS floor) and
   name it in the verdict.
5. **Automate evidence** — feature stories only (numeric `E.S` ids; test-only MIN-FLOW stories like
   `tea-*` are exempt): confirm ②'s expansion pass left evidence — `automation-summary-<story>.md` under
   `_bmad-output/test-artifacts/`, or an explicit `## Automate: skipped — <rationale>` section in the
   story walkthrough. Missing BOTH → cap the verdict at **CONCERNS** and name the gap in the verdict file
   (never FAIL on this alone — stories gated before 2026-07-09 predate the check).

## Step 3.5 — Gate: clean code (ALWAYS runs — independent of Step 2's opt-in)
Invoke the **`clean-code-audit`** skill on the story diff, bound to the same worktree Step 0.5 resolved
(its standard is `.agents/rules/code-standards.md`).

- **No double drift-hunt (inside ③ only).** Step 1's adversarial review already walked these hunks —
  run the machine floor + the comment contract (§2A) only, and IMPORT Step 1's drift/bloat findings
  into the findings table (source `review`) instead of re-running the §2B ban-hunt. The full two-half
  pass is for standalone `/clean-code-audit` runs.
- **Diff-scoped.** Only code THIS story wrote is in scope; legacy debt in untouched files is noted, never
  gated on — the same grandfathering the test gate already uses.
- **This gate does NOT depend on `sudo-tests.yaml`.** A project with no test baseline still has a code
  standard, so a `WAIVED` test gate (Step 2) never waives this one.
- **A missing tool is a finding, not a skip** — `No module named ruff` means the floor is unrunnable and
  the project breaks `tests-must-gate-for-real` §2. Report it and name the fix.
- **An empty diff is a STOP, not a pass.** If the changed-file set comes back empty, say so and stop — a
  vacuously green gate is exactly what this step exists to prevent.

Fold its findings table into the verdict file **verbatim**, with the actual command output pasted. Apply
the fixes you can make safely, then re-run the affected check and paste the new output.

## Step 4 — Verdict
Combine into **PASS / CONCERNS / FAIL / WAIVED** and write
`_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` — **inside the worktree Step 0.5
resolved**, never the shared checkout (it rides the story branch through the close-out merge):
- the review (scope, the passes, each finding with `file:line` + severity + disposition),
- each gate check's result + the **actual** suite output,
- a `## Clean-Code Gate` section carrying Step 3.5's findings table and its pasted tool output,
- the overall verdict, the story id, and the current `git HEAD` ref (so `sudo-update-sprint-memory` can
  detect a stale verdict) — plus the SHA the full-suite evidence was measured on and whose run it was
  (②'s inherited or ③'s own). Any code/test diff between that SHA and HEAD invalidates the verdict.
- **FAIL** = a new test regression, a required tier missing, **or** a Step 3.5 machine-floor error on a
  changed line / a banned pattern shipped (bare `except:`, `any`, a committed secret).
- **CONCERNS** = soft issues only — including Step 3.5's judgment findings (missing story provenance, a
  stale `AIDEV-NOTE` the diff should have updated, bloat, duplication, an unowned TODO).
- **PASS** = all required tiers green **and** the clean-code floor green on changed lines.
- **WAIVED** = no test baseline (Step 2). Step 3.5 still ran — report its result inside the waiver.

> The split is deliberate: objective checks block a story, taste does not. Taste gets recorded, argued,
> and fixed on its merits — never used to stall a story on a reviewer's preference.

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
- If your fixes changed files, commit them in the story worktree (explicit paths) and refresh the
  branch/commit summary in `## Your Actions`.
- **Hard rule: NEVER finish `/sudo-code-review` with the walkthrough body left stale after applying fixes.**

## Stay in lane
Commit your review fixes inside the story worktree (explicit paths) — but **never land on `main_debug`**,
and never flip the story status or edit `sprint-status.yaml`; that is `sudo-update-sprint-memory`'s job
(it reads this verdict first, then lands the branch in its Step 7). Updating `walkthrough.md` (Step 5) is
IN lane — that is documenting the review, not flipping status.

Optional additional input: $ARGUMENTS
