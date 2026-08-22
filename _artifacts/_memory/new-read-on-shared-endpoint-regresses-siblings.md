---
name: new-read-on-shared-endpoint-regresses-siblings
description: "adding a NEW Firestore read (or a scoped check) to a shared admin endpoint silently regresses sibling tests whose mocks don't stub it — run the existing suite, coerce defensively, exempt the privileged path"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ebb156cf-44d9-4163-925d-addc662d5cc6
---

AGY 17.7: two regressions the plan's blast-radius trace missed, both caught only by running the EXISTING suite (not the new ATDD contract) — "additive → no break" and "super unaffected" were both false.

- **R-1 (500 via junk mock doc):** `get_students` gained a `schools_service.get_school(code)` lookup to populate a new `StudentListItem.school_name`. 17.5's roster test mocks `get_db` as a bare MagicMock → the new schools read returned a MagicMock, `.get("name")` → non-str → **pydantic ValidationError 500s the whole roster**. Also cross-test contamination: a leaked `get_db` patch from `test_tenancy_gate` made it flake only in combined runs. Fix: `raw = doc.get("name","") if isinstance(doc, dict) else ""; name = str(raw) if raw else ""` — a non-dict/malformed registry doc degrades to `""`, never 500s.
- **R-2 (404 on the privileged path):** `get_curriculum_graph` individual mode gained a `scoped_user_query(...).where(document_id()==uid)` tenancy check. The existing super_admin `test_get_graph_individual` mocks only the graph service, never seeds a `users` doc → empty → **404 instead of 200** (and `build_graph` never called). Fix: **short-circuit the whole scoped block for super_admin** (`getattr(scope,"role",None) != "super_admin"`) — operator exempt, no extra read, pre-change behavior byte-for-byte preserved. Match the sibling gate's predicate style.

**Why:** a new read/branch on a SHARED endpoint is exercised by every sibling test of that endpoint, whose mocks were written before the read existed. The ATDD contract passes (it stubs the new read); the regression hides in the neighbors.

**How to apply:** after adding any new read/scoped-check to a shared handler, (1) run the endpoint's WHOLE existing test file + any tenancy/gate suite, not just the new contract; (2) coerce every external-read result to its DTO type defensively (`isinstance` + `str()`), so a junk/mocked doc can't 500; (3) exempt the privileged/global path from a new scoped read so you don't 404 it. Related: [[atdd-mock-shape-must-match-backend-contract]], [[relocating-drops-mount-guards]], [[agy-canonical-test-venv]].
