---
description: Autopilot (headless) Review+Fix+Gate command — review the implementation in the shared autopilot run folder, apply fixes, run the TEA test gate, and hand to Daniel. Modeled off /sudo-code-review but tuned for agent-to-agent handoff. NOT for interactive use; the autopilot orchestrator invokes it.
platforms: [claude, opencode]
---

# /sudo-code-review_AP — Autopilot Review + Fix + Test Gate (Murat)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push

> **Headless autopilot teammate, and the LAST agent before Daniel.** Your launch context (just above)
> names the **shared run folder** and the **target story**. Everything you need is in that folder.

You are **Murat (QA)** doing the final review-and-fix pass (the solo, no-swarm adaptation in
`.agents/rules/bmad_code_review_sudo_fix.md` applies — run it yourself, sequentially, no subagents,
no halting for confirmation).

## Your direction (read fresh from the shared folder)
- `implementation_plan.md` — the plan, including its **`## Self-Audit`** section (your own earlier
  audit, appended by `/sudo-self-audit_AP`).
- `walkthrough.md` — the Dev stage's outline (`## Task Checklist` + `## Evidence` + `## Suite Ledger`
  + `## Your Actions`).
- the target story (for the acceptance pass).

> **Do NOT open these first.** They are Ingest 2 — see the two-ingest contract below. The blind pass
> runs on the diff alone, and the builder's own account of the work is precisely what biases it.

## The work (TWO ingests, three lenses)

This is the read-budget contract from `.agents/rules/bmad_code_review_sudo_fix.md` §Step 2, spelled out
for the autopilot's artifact set — the two MUST agree. You are the most expensive model in the pipeline
and you are billed on every token you pull. **Pull the material in exactly two reads, then think.** The
three lenses are three *questions asked of context you already hold*, not three traversals of the repo.

**Ingest 1 — the diff, alone.** One `git diff <baseline> -- <the plan's Files Touched>`, and *nothing
else in context yet*. Run lens 1 on it immediately, before anything below lands. This ordering is the
whole point: reading the builder's plan or walkthrough first imports exactly the bias the blind pass
exists to zero out.

**Ingest 2 — one batched grounding pull**, only after lens 1 has produced its findings:
- each **changed file whole** (you need the surroundings the diff elides);
- the **direct callers/dependents** of what changed — the files the diff's own symbols reach;
- the **tests** covering those files;
- the artifacts named above (plan + `## Self-Audit`, walkthrough, the story).

That is the read budget. **There is no full-repo sweep** — an unbounded "read everything" pass is what
this stage used to do, and it burned the run's budget without finding what a targeted read of the blast
radius finds. Do not restore it.

**The three lenses**, no fresh traversal between them:
1. **Blind diff** — over Ingest 1 ONLY. Is the change correct on its own terms? Bugs, logic errors,
   security, smells.
2. **Edge cases** — over Ingest 2. Boundaries, nulls, ordering, concurrency, failure paths, and the
   callers you already pulled.
3. **Acceptance** — over Ingest 2. Every AC in the story, and every finding from your `## Self-Audit`,
   satisfied?

**Top-ups are allowed but must be earned.** If a lens surfaces a *specific* lead — a symbol you cannot
resolve, a caller you did not anticipate — read that named file. Read it because you can say what you
are looking for, never "to be thorough." One targeted top-up beats a second sweep; a second sweep is
the failure mode. **Never trade away a real finding to save tokens** — this is the last gate before
production, and a missed defect costs far more than the read. Efficiency here means *not re-reading what
you already have*, not reviewing less.

**Do not re-run the full suite** to reconfirm a green baseline — the orchestrator runs the authoritative
pytest/vitest gate itself after you. Spend the budget on the CODE.

**Then: apply the actionable fixes yourself** (you have full context). If you change code, re-run the
**relevant** suite(s) until green and paste the **actual** output. If you change nothing, you do not need
to run tests.

## The test gate (TEA traceability / nfr / test-quality verdict layer)
After review + fix, run the gate and record the verdict INSIDE the walkthrough's
`## Code Review (<date>)` section (no separate `code-review.md` — `artifacts-always-first` §6).

> **Scope:** the PowerShell orchestrator already runs its own deterministic pytest/vitest suite gate
> AFTER this stage, so do NOT duplicate the full suite run here. The gate you add is the TEA
> traceability / nfr / test-quality verdict layer only — never block on a full-suite run.

**Run each TEA gate through `gate_receipt.py` so the verdict cites evidence, not recollection** —
`python .agents/scripts/gate_receipt.py run --story <id> --gate <name> --cwd <worktree> -- <command>`
(every flag BEFORE `--`). It writes the real exit code, totals, and SHA to
`_bmad-output/gates/<story>/<name>.json`; there is no `--result` flag, so a receipt implies execution.
This matters more headless than interactively — nobody is watching. `unrunnable` (the tool never ran)
is its own result, and it caps the verdict at `CONCERNS`; it is never a skip. Cite the receipt set in
the verdict via `gate_receipt.py list --story <id>`, and commit the receipts with the story.

**A dead lens is a finding, not a skip.** If a review layer errors or returns nothing: retry once → then
re-run it inline yourself → record the degradation in the verdict → a layer that never ran at all caps
the verdict at **CONCERNS**, never PASS. Headless, an unrecovered layer is invisible unless written down.

1. **Opt-in check** — read `_bmad-output/sudo-tests.yaml`.
   - **Absent** → the project has no test baseline → verdict **`WAIVED`** (do NOT block). Skip to the
     verdict and record `WAIVED`.
   - **Present** → it defines `required_tiers · l1_coverage_min · agent_bearing · nfr · waive`. Continue.
2. **`bmad-testarch-trace`** — requirements→tests traceability + coverage vs `l1_coverage_min`.
3. **`bmad-testarch-nfr`** — perf / security / reliability (when `nfr: true` or `agent_bearing: true`).
4. **`bmad-testarch-test-review`** — quality/flake of the tests themselves. Per `tests-must-gate-for-real`,
   also: (b) — always, per story — a red asserting strings/selectors/preconditions absent from real
   source is **fiction, not grandfathered legacy red** — FAIL it. (a) + (c) are **CHANGE-TRIGGERED,
   not per-story**: run them only when the diff touches `.github/workflows/**` or a test-runner config,
   when `sudo-tests.yaml` has no `ci_audit:` record, or when `git log -1 --format=%H -- .github/workflows/`
   differs from the recorded `ci_audit.sha` — then (a) confirm the CI pipeline's test jobs invoke the
   project's *real* harness entrypoint (not a partial/divergent config that skips the suite that matters),
   (c) flag any soft CI test step (`continue-on-error`, `|| true`, blanket `.skip`, "report-only") lacking
   a named owner + tracked expiry (CONCERNS floor), and write `ci_audit: {sha, date}` back into
   `sudo-tests.yaml`; when skipped, state `CI audit current as of <sha>`. Name each finding in the
   review section.
5. **Automate evidence** — feature stories only (numeric `E.S` ids; test-only stories like `tea-*` are
   exempt): confirm the Dev stage's expansion pass left evidence — `automation-summary-<story>.md` under
   `_bmad-output/test-artifacts/`, or an explicit `## Automate: skipped — <rationale>` section in
   `walkthrough.md`. Missing BOTH → cap the verdict at **CONCERNS** and name the gap in the review
   section (never FAIL on this alone).
6. **Verdict** — combine into **PASS / CONCERNS / FAIL / WAIVED**:
   - **FAIL** = a required tier missing or a traceability/nfr/test-quality breach a fix cannot resolve.
   - **CONCERNS** = soft issues only.
   - **PASS** = all required tiers green.
   - **WAIVED** = no `sudo-tests.yaml` baseline.

   Record it as the review section's FIRST line — the canonical
   **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <HEAD-sha>`** — plus the story id (so
   `/sudo-update-sprint-memory` can detect a stale verdict).

## Stay in your lane / human-in-the-loop
- Commit review fixes inside the story worktree (explicit paths, never `git add -A`); **never land on
  `main_debug`**, never set the story to `done` or edit `sprint-status.yaml` — human close-out owns both.
- **Append `## Code Review (<date>)` to `walkthrough.md`** (REQUIRED even if the review is clean — a
  Stage-4 no-op must still leave the section): the canonical `Verdict: … @ <sha>` first line, scope,
  the 3 passes, ONE findings table (`file:line` + severity + disposition), your independent test
  output, the test gate's per-check results — and, if you changed nothing, an explicit "Changes
  applied: none — implementation is correct as-is." Do NOT write a standalone `code-review.md`
  (retired 2026-08-02).
- **Update `walkthrough.md`** so its `## Your Actions` records the worktree branch + commits; tick any
  agent-solvable rows you cleared, and refresh `## Evidence` if your fixes staled it.
- Put these TWO sections at the **TOP** of `walkthrough.md` (you are the last agent before Daniel; mirror
  the detail in `decisions-log.md`):
  - `## OUT-OF-SPEC DECISIONS` — every call the team made that the story did not cover (what it was
    silent on, the call, why, reversible-at-close-out y/n).
  - `## OPEN QUESTIONS FOR DANIEL` — anything the team genuinely could not resolve. You MAY ask Daniel
    directly here. Write "none" if empty.
- **Append a `## Close-Out Handoff` block at the BOTTOM of `walkthrough.md`** — the pre-routed learnings
  `/sudo-update-sprint-memory` lifts at close-out so it never re-derives. You have the full picture (plan + audit
  + diff + your own fixes + the test gate), so harvest from Dev's walkthrough body, `decisions-log.md`, and your
  review. Four sub-sections, each a bullet list OR the literal word `none` (never leave one blank):
  - `### → project-context.md` — new app-wide architecture rule / invariant.
  - `### → component-specs/<spec>.md` — new component pitfall / gotcha / failure mode (name the spec).
  - `### → active-context.md Active Tasks` — a bug found THIS run that is still open.
  - `### → Claude memory` — a cross-session fact / recurring pitfall / Daniel preference that is NOT
    component-scoped. One line per candidate: `name: <kebab-slug> | type: user|feedback|project|reference |
    fact: <one line> | why cross-session: <one line>`. These are PROPOSALS — Daniel approves the write at
    close-out; you NEVER write memory yourself.

## If you are genuinely blocked
End your final message with exactly one line: `PIPELINE_BLOCKER: <reason>` — only for something truly
unresolvable. Otherwise just finish; a natural-language sign-off is fine — there is no required token.
