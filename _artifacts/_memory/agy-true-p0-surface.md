---
name: agy-true-p0-surface
description: "AGY's verified true-P0 code surface (Daniel-confirmed + GitNexus-grounded 2026-06-29): the Specialist Orchestrator (ALL) + the RAG/Librarian (ALL) are P0 because everything stems from the Specialist and all info comes from the RAG; plus FAA grounding, Sully override, admin auth, PII scrubbing. TEA-5's coverage scope covers only ~half — the RAG (tools/) + RAG services + PII (observability/) are OUTSIDE it."
metadata:
  node_type: memory
  type: project
  originSessionId: 73ca08eb-87a8-432b-af19-3522ff5d8898
---

The verified true-P0 surface for the AGY coverage push (Daniel-confirmed 2026-06-29, ground-truthed via GitNexus). It is BROADER than the AI-principles TEA risk map, which only tagged R-P6 (FAA) + R-P3 (Sully) as Prio-P0. Daniel's rule: **"everything stems from the Specialist Agent; all information used is from the RAG search"** → both are P0 in their ENTIRETY, not just the guards inside them.

| P0 surface | File(s) | In TEA-5 cov scope (`agents/specialist`+`routers`)? |
|---|---|---|
| **Specialist Orchestrator (ALL)** | `backend/agents/specialist/agent.py` (`SpecialistOrchestrator` @297–3441, ~24 methods) + `sub_agents/` (reasoner, socratic_teacher) | ✅ |
| **RAG / Librarian (ALL)** | `backend/tools/librarian.py` (`Librarian` @30–343, `perform_investigation`; DB2 rerank / GCS fetch / graph edges) | ❌ `tools/` |
| RAG dossier assembly | `backend/services/{dossier_context_builder,learning_context_service,lesson_plan_builder}.py` | ❌ `services/` |
| Sully safety override | `backend/routers/sully_spike_websocket.py` (`ConsequenceTracker.on_eval`) | ✅ |
| confidence_reset | `backend/services/strategy_roulette.py` | ❌ `services/` |
| Admin auth / JWT | `backend/routers/admin_auth.py` (`_verified_admin_payload`) | ✅ |
| PII scrubbing | `backend/observability/sentry_init.py` (`_before_send`) | ❌ `observability/` |
| Specialist HTTP entry | `backend/routers/specialist.py` (`specialist_chat`) | ✅ |

**Why:** the TEA risk register was scoped to the mentor's AI-behavior principles (P1–P10), NOT a full threat model — so it missed (a) the foundational reach (Specialist + RAG = everything downstream), (b) security (admin auth), (c) privacy (PII scrub). All confirmed REAL in code (no phantoms) and mostly already partly-tested (the in-scope half measured 54.02% branch at TEA-5).

**How to apply:**
1. The P0-coverage push must **EXPAND the coverage `source`** beyond TEA-5's `agents/specialist`+`routers` to also cover `tools/librarian.py` + the RAG `services/` files + `observability/sentry_init.py`. Scope to the SPECIFIC P0 files (whole-dir `source` would dilute the number with non-P0 code).
2. Per [[test-priorities-matrix]], P0 = **100%** + Unit+Integration+E2E+Manual. The Specialist is huge (3144 lines, 54% today) → 100% is a substantial multi-story effort, and E2E needs E2E tooling (Ask-First).
3. This map is core content for **TEA-8's `testing-standards.md`** (codify which code is P0).

Relates to [[test-priorities-matrix]], [[tea-retrofit-active-initiative]], [[recon-reframes-story-scope]].
