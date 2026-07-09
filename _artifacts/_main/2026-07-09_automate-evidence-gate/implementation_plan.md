---
IsArtifact: true
ArtifactMetadata:
  type: implementation_plan
  workspace: _main
  date: 2026-07-09
  slug: automate-evidence-gate
  status: approved
---

# Implementation Plan — Close the automate-evidence seam in the sudo dev flow

**Approval:** Daniel, in-chat 2026-07-09 — *"lets fix those and make sure its fixed in the aviationchat and the freshworkspace"* — approving the exact two edits proposed at the end of the `testing_audit_BDD` verification (extended to the `_AP` twins, which carry the identical seam).

## Why (from `_my_resources/docs/testing_audit_BDD.md` §4.4 + the follow-up verification)

13 of 14 Epic-8 ATDD stories finished with **no `bmad-testarch-automate` expansion pass** and nothing caught it:
- In `/sudo-dev-story-tests`, Step 4 (Automate) is the ONLY step with no evidence requirement — Step 5's mandatory checklist enforces plan/audit/walkthrough but never mentions the automation summary.
- In `/sudo-code-review`, the gate's four checks (suite, trace, nfr, test-review) never ask whether ②'s Step 4 ran — all 13 stories legitimately earned PASS/CONCERNS.

## Change set (lobby masters in `.agents/commands/`, then vendor to projects)

1. **`sudo-dev-story-tests.md`**
   - Step 4: require persisting the automation summary (`_bmad-output/test-artifacts/automation-summary-<story>.md`) or an explicit `## Automate: skipped — <rationale>` section in the walkthrough.
   - Step 5 checklist: add the automate-evidence item (4th checkbox; noted as not an `ARTIFACT_DIR` file).
2. **`sudo-code-review.md`**
   - Step 3: add check **5. Automate evidence** — feature stories only (numeric `E.S` ids; MIN-FLOW/`tea-*` test-only stories exempt); missing summary AND missing skip-rationale → cap verdict at **CONCERNS** (never FAIL on this alone — legacy predates the check).
3. **`sudo-dev-story-tests_AP.md`** — same evidence requirement in IMPLEMENT mode's automate step.
4. **`sudo-code-review_AP.md`** — same gate check 5.

## Propagation
- Edit ONLY the lobby masters, then run **`/sync-agents`** so the vendored copies in `Projects/AGY_AVIATIONCHAT` and `Projects/Fresh_Workspace_BMAD` (plus the lobby `.claude/`/`.opencode/` mirrors, the Antigravity workflow mirror, and machine-global caches) all pick up the change — the canonical fix path per ROOT LAW §4.
- Verify with Bash `diff`/hash per project (NOT Glob — it false-negatives under `Projects/`).

## Out of scope
- No behavior change to `bmad-testarch-automate` itself; no retro-editing of the 13 legacy stories (their backfill is remediation P1-4 in the audit, a separate risk-based pass).
- No `git commit`/`push` — commit commands handed to Daniel in the walkthrough (desktop git policy).

## Verification
- Grep each edited master for the new check text; diff vendored copies in both projects against the masters (expect byte-identical); confirm the Antigravity workflow mirror picked up the two sudo-* files it mirrors.
