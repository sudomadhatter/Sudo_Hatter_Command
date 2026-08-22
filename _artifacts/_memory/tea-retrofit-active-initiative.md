---
name: tea-retrofit-active-initiative
description: "AGY's TEA test-architecture retrofit (P1–P10) — ✅ CLOSED 2026-07-03, all 18 stories done and COMMITTED (verified 2026-07-25). Kept as the hub node ~11 memories link to; per-story detail lives in sprint-status.yaml + _artifacts/."
metadata: 
  node_type: memory
  type: project
  originSessionId: 27c1ed6c-690d-4f25-91b4-b537755e900d
  modified: 2026-07-25T19:16:40.753Z
---

**✅ CLOSED 2026-07-03. Nothing owed.** The TEA test-architecture retrofit (mentor brief D1–D4,
principles P1–P10) ran TEA-1..TEA-18 through the lobby `sudo-` loop and finished. Blockers B1–B5 all
resolved. **Commits verified landed 2026-07-25** (`backend/tia/`, `firebase/tests/`, `backend/evals/drift.py`
all tracked; merged to `main` in `dea87746` "pre-launch integration … + TEA retrofit").

*Compacted 2026-07-25 from ~57 lines of story-by-story history. That detail was never unique to this
file — `sprint-status.yaml` is the authoritative per-story tracker and `_artifacts/` holds the verdicts.
This node survives because ~11 memories link to it as "the TEA context."*

**What it left behind** (each already its own memory — that's where the reusable lesson lives):
- the coverage/level policy → [[test-priorities-matrix]] · the verified P0 map → [[agy-true-p0-surface]]
- the E2E harness → [[agy-learner-e2e-harness]] · rules-suite Java → [[firestore-rules-tests-need-java]]
- eval conventions → [[eval-harness-negative-control-convention]], [[domain-gated-fixtures-web-verify]]
- traps found along the way → [[test-live-guard-needs-live-marker]], [[governance-gate-scans-venv]],
  [[gitnexus-impact-misses-attribute-dispatch]], [[gitnexus-verify-index-fresh-after-pull]],
  [[voice-router-entitlement-vs-cost-cap]]
- the method → [[test-debt-stories-are-characterization]], [[recon-reframes-story-scope]]

**Only residual (optional, non-blocking):** re-run `/bmad-testarch-trace` to re-score the matrix — the
last one (2026-07-02) gated CONCERNS at P0 84.1%, and GAP-7 (E2E), GAP-8 and the TIA gate have all closed
since, so the score is stale-low rather than wrong.

**Honest ceilings worth remembering:** TEA-10/11/3 found no live bug (backend invariants hold — if
Specialist breakage is real it's frontend-side); and tea-9's TIA gate is a fast *local pre-push* check,
never the merge gate, because the GitNexus index is machine-local.
