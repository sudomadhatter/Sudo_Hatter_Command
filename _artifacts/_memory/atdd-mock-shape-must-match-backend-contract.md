---
name: atdd-mock-shape-must-match-backend-contract
description: An ATDD FE mock that uses a value the real backend never emits is a vacuous green — the unit passes but production breaks; verify the mock shape against what the backend actually sends.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8ebfe008-5c3f-429e-963f-889cdd7a2dd1
---

An ATDD/unit test's mock must reproduce the shape the REAL backend emits, not a convenient shape — otherwise the red→green is vacuous against production.

**Concrete instance (AGY Story 17.5, 2026-07-11, caught by the /sudo-self-audit step):** the FE roster red test mocked an un-onboarded student as `name: ""`, so a naive FE check `!s.name` lit the "Not onboarded yet" branch and the unit test passed. But `get_students` (admin_dashboard.py) NEVER emits an empty name — `data.get("name", "Unknown Pilot")` + the DTO constructor coerce a nameless student to the sentinel string `"Unknown Pilot"`. In production the FE receives `name: "Unknown Pilot"` (truthy) → `!s.name` is false → the row renders the sentinel, violating the AC. Fix: predicate `s.name && s.name !== "Unknown Pilot"`, plus a Step-4 test case with the real production shape.

**Why:** unit mocks are authored from the test writer's mental model, which can silently diverge from the backend's actual output contract (defaults, sentinels, coercions). The suite goes green on the mocked shape while the wired system fails — a false-green that survives ATDD because no test exercises the real emitted value. This is the mock-shape-divergence sibling of [[test-live-guard-needs-live-marker]] (live-guard swallow) and [[eval-harness-negative-control-convention]] (control-field ignored) — same class (vacuous green), different mechanism.

**How to apply:** in the self-audit (Step 2 of /sudo-dev-story-tests) and in code review, for any FE/consumer test, grep the producing endpoint for its default/sentinel/coercion behavior and confirm the mock matches what it ACTUALLY sends — especially for "absent field" cases (empty string vs a default sentinel vs null). If they differ, add a test with the production shape, not just the convenient one. Ground-truth by what the backend emits, not by what the mock assumes.
