# Walkthrough — Bulletproof Testing Strategy (TEA Gate), Phase A

**Date:** 2026-06-28 · **Workspace:** _main (lobby, toolkit-wide) · **Status:** Phase A complete, synced, verified · UNCOMMITTED

## What this session did
Wired the BMAD TEA test agents into Daniel's manual dev flow as a set of `sudo-` orchestrator commands (thin wrappers that CALL existing TEA/BMAD workflows — no logic rewritten), with a test gate baked into review and a verdict-check at close-out. Built Phase A (the human lane) only; Phase B (autopilots) deferred.

## The flow that now exists
```
sudo-boot-sprint-memory  → ① sudo-write-story-tests → ② sudo-dev-story-tests → ③ sudo-code-review → sudo-update-sprint-memory
```
- **sudo-write-story-tests** = `bmad-create-story` → `bmad-testarch-atdd` (story + failing tests first)
- **sudo-dev-story-tests** = `bmad-dev-story` plan → auto `sudo-self-audit` → implement → `bmad-testarch-automate`
- **sudo-code-review** = `bmad-code-review` → gate (`/1_run-all-tests-back_front` + `trace` + `nfr` + `test-review`) → PASS/CONCERNS/FAIL/WAIVED verdict artifact
- **sudo-update-sprint-memory** = reads the verdict (gate before `done`) → flip → learnings/prune
- **sudo-boot-sprint-memory** = boot + story "pick up" (sprint-status + next story + next command)

## Changes (master `.agents/`, then synced)
- **New:** `sudo-write-story-tests`, `sudo-dev-story-tests`, `sudo-code-review`.
- **Renamed:** `1_self-audit-stress-test`→`sudo-self-audit`; `update-sprint-context`→`sudo-update-sprint-memory` (+verdict-check); `boot-sprint-context`→`sudo-boot-sprint-memory` (+pick-up + ⛔ not-the-master-"pick up" note).
- **Lens:** added Test-Adequacy Auditor (4th layer) to `bmad-code-review/steps/step-02-review.md`.
- **References:** updated `autopilot_claude/mobile`, `bmad-code-review_AP`, `1_self-audit-stress-test_AP`, `opus-reviewer`, `artifacts-always-first`, `commands/INDEX`, `workflows/INDEX`, the dev-loop diagram. `_AP` variants and the `1_self-audit-stress-test.md` workflow file deliberately KEPT.
- **Sync:** `/sync-agents` → lobby + AGY_AVIATIONCHAT + Fresh_Workspace_BMAD + global caches; purged 18 local ghost files; regenerated `docs/doc-graph`.

## Findings
1. **`1_run-all-tests-back_front` KEPT, not retired** — its referenced workflow file never existed; the command carries pytest+vitest inline (it IS the muscle). `sudo-code-review` calls it.
2. **`/sync-agents` doesn't ghost-purge local command dirs** (only globals) — renames leave ghosts; purged by hand. Saved to memory `sync-leaves-local-command-ghosts`.

## Not done (next)
AviationChat opt-in (`sudo-tests.yaml` + L1/L2/L3 reference tests) · Phase B autopilots (claude/mobile/opencode, per-project scripts) · CI (`bmad-testarch-ci`).

## ⚠️ Intermingled uncommitted work (NOT this session)
`.agents/rules/constitution.md` (+1 clickable-links line), the `_artifacts/INDEX.md` "clickable-artifact-links-rule" row, and the `_artifacts/_main/2026-06-28_clickable-artifact-links-rule/` folder belong to a **separate** session — commit them separately.

## Task Checklist
- [x] 3 new sudo commands · [x] 3 renames (+verdict-check, +pick-up) · [x] Test-Adequacy lens
- [x] All canonical references updated (human cmds; `_AP` kept) · [x] runner kept (finding)
- [x] Sync lobby + 2 projects + globals · [x] purge 18 ghosts · [x] regen doc-graph · [x] verify clean
- [ ] (next) AviationChat opt-in tests · [ ] Phase B autopilots · [ ] CI

## Your Actions
Agents don't commit. To commit THIS session's work (excludes the clickable-links session) on `main_debug`:
```bash
git add .agents/commands/sudo-*.md \
        ".agents/commands/1_self-audit-stress-test.md" .agents/commands/1_self-audit-stress-test_AP.md \
        .agents/commands/boot-sprint-context.md .agents/commands/update-sprint-context.md \
        .agents/commands/INDEX.md .agents/commands/autopilot_claude.md .agents/commands/autopilot_mobile.md .agents/commands/bmad-code-review_AP.md \
        .agents/opencode-agents/opus-reviewer.md .agents/rules/artifacts-always-first.md \
        .agents/skills/bmad-code-review/steps/step-02-review.md .agents/workflows/INDEX.md \
        _my_resources/diagrams_guides/system/autopilot_bmad_dev_loop.md docs/doc-graph.json docs/doc-graph.md \
        .claude/ .opencode/ _artifacts/_main/2026-06-28_testing-strategy-tea-gate/
git restore --staged .agents/rules/constitution.md   # keep the clickable-links rule in its own commit
git commit -m "feat(toolkit): sudo- TEA-gated dev flow (write-tests/dev/code-review+gate) + boot/update sprint-memory renames + test-adequacy review lens

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Then re-vendor any project commits as needed (AGY_AVIATIONCHAT, Fresh_Workspace_BMAD each have their own `.claude/.opencode` updates from sync — commit per-repo).
