---
IsArtifact: true
ArtifactMetadata:
  type: walkthrough
  workspace: _main
  date: 2026-07-09
  slug: automate-evidence-gate
  status: done
---

# Walkthrough — Automate-evidence seam closed in the sudo dev flow (lobby + AGY + Fresh)

**What this closes:** the `testing_audit_BDD` finding that 13 of 14 Epic-8 ATDD stories finished green with no `bmad-testarch-automate` expansion pass and nothing caught it — because ②'s Step 4 was the only step with no evidence requirement, and ③'s gate never asked whether it ran.

## Changes (5 edits, 4 master files in `.agents/commands/`)

1. **`sudo-dev-story-tests.md` — Step 4**: automate must now *leave evidence* — persist `_bmad-output/test-artifacts/automation-summary-<story>.md`, or write a `## Automate: skipped — <rationale>` section into the walkthrough when expansion is genuinely N/A. A silent skip is an unfinished Step 4.
2. **`sudo-dev-story-tests.md` — Step 5 checklist**: 4th mandatory checkbox — *Automate evidence (Step 4)* — summary exists OR explicit skip-rationale in the walkthrough (noted as living with TEA outputs, not in `ARTIFACT_DIR`). Cites the audit finding as the bug it closes (house style).
3. **`sudo-code-review.md` — Step 3, new check 5 "Automate evidence"**: feature stories only (numeric `E.S`; `tea-*`/MIN-FLOW test-only stories exempt); missing summary AND missing skip-rationale → verdict **capped at CONCERNS** with the gap named in the verdict file; never FAIL on this alone (stories gated before 2026-07-09 predate the check).
4. **`sudo-dev-story-tests_AP.md` — implement Step 3**: same *leave evidence* requirement ("The QA gate checks for this evidence — a silent skip surfaces as CONCERNS").
5. **`sudo-code-review_AP.md` — gate**: same check 5 inserted; Verdict renumbered to 6.

Design choices: **CONCERNS, not FAIL** (visible without retro-blocking legacy); **explicit-skip escape hatch** (skipping stays possible, *silent* skipping doesn't); **`tea-*` exemption** (MIN-FLOW test-only stories ARE the automate pass — requiring a second one would be circular).

## Propagation & verification (all green)

- `/sync-agents` run 3× (lobby+globals, AGY, Fresh). Surface counts: lobby `.claude/commands` 19 · `.opencode/commands` 44 · opencode global 44 · antigravity global 24 · workflow mirror 18 sudo-*; AGY 20/44; Fresh 27/52. (Pre-existing benign warning: `sudo-update-sprint-memory.md` > Antigravity's 12k workflow guard — mirrored anyway, unrelated to this change.)
- **Hash verification:** each of the 4 files is byte-identical (md5) across every surface that carries it — lobby `.agents/commands` + `.agents/workflows` + `.opencode/commands` (+ `.claude/commands` for the universal `_AP` pair; the two interactive commands are `platforms: [opencode, antigravity]` and reach Claude via their skill launchers reading the master), both projects' vendored copies of all of those, and both machine-global caches. Hashes: `1787504e…` (dev), `36a64261…` (review), `065ec57f…` (dev_AP), `a6206313…` (review_AP).
- Content check: "Automate evidence" present in both review files + the interactive dev checklist; "Leave evidence" present in the `_AP` dev file — across lobby + AGY + Fresh.
- Audit doc remediation **P1-6 marked DONE** — note the audit now lives at `_my_resources/open_tasks/testing_audit_BDD.md` (Daniel moved it from `docs/` into his open-tasks queue).

## Not done here (unchanged scope)

- The 13 legacy stories' actual automate backfill = audit remediation **P1-4** (risk-based: 8.20.x cost caps → 8.21.x grading moat → 8.19.x admin surfaces), a separate pass.
- CI holes P0-1..P0-3 (main_debug trigger, deploy-backend test job, journeys pack) — still open in the audit.

## Task Checklist

- [x] implementation_plan.md written + approval on record (Daniel in-chat: "lets fix those and make sure its fixed in the aviationchat and the freshworkspace")
- [x] 4 lobby masters edited (5 edits)
- [x] /sync-agents: lobby + globals, AGY_AVIATIONCHAT, Fresh_Workspace_BMAD
- [x] Hash-verified byte-identical on every surface incl. both global caches
- [x] Audit doc P1-6 flipped to DONE
- [x] INDEX.md ledger row appended

## Your Actions

1. **Restart opencode** (global commands cache was refreshed).
2. Commit per repo (all on `main_debug`; scoped adds so unrelated drift stays out):

```powershell
# Lobby (c:\Sudo_Hatter_Command)
git add .agents/commands/sudo-dev-story-tests.md .agents/commands/sudo-code-review.md .agents/commands/sudo-dev-story-tests_AP.md .agents/commands/sudo-code-review_AP.md .agents/workflows/sudo-dev-story-tests.md .agents/workflows/sudo-code-review.md .opencode/commands/sudo-dev-story-tests.md .opencode/commands/sudo-code-review.md .opencode/commands/sudo-dev-story-tests_AP.md .opencode/commands/sudo-code-review_AP.md .claude/commands/sudo-dev-story-tests_AP.md .claude/commands/sudo-code-review_AP.md _artifacts/_main/2026-07-09_automate-evidence-gate/ _artifacts/INDEX.md _my_resources/open_tasks/testing_audit_BDD.md
git commit -m @'
feat(testing): testing_audit_BDD deliverable + automate-evidence enforcement in sudo dev flow

Audit: TEA strong (7/03 PASS) but 13/14 ATDD stories skipped the automate pass;
real CI holes = ungated main_debug, test-less backend deploy, journeys pack.
Fix: sudo-dev-story-tests Step 4 evidence + close-out checkbox; sudo-code-review
gate check 5 (missing evidence -> CONCERNS cap); same in _AP variants.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@

# AGY_AVIATIONCHAT (c:\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT)
git add .agents/commands/sudo-dev-story-tests.md .agents/commands/sudo-code-review.md .agents/commands/sudo-dev-story-tests_AP.md .agents/commands/sudo-code-review_AP.md .agents/workflows/sudo-dev-story-tests.md .agents/workflows/sudo-code-review.md .opencode/commands/sudo-dev-story-tests.md .opencode/commands/sudo-code-review.md .opencode/commands/sudo-dev-story-tests_AP.md .opencode/commands/sudo-code-review_AP.md .claude/commands/sudo-dev-story-tests_AP.md .claude/commands/sudo-code-review_AP.md
git commit -m @'
chore(agents): vendor automate-evidence gate fix from lobby master (/sync-agents 2026-07-09)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@

# Fresh_Workspace_BMAD (c:\Sudo_Hatter_Command\Projects\Fresh_Workspace_BMAD)
# (same add list as AGY, same commit message)
```

3. If `git status` in a project shows other `.agents/`/`.opencode/` files touched by the sync that you haven't reviewed, they're pre-existing master↔vendor drift the mirror reconciled — review before widening the add.
