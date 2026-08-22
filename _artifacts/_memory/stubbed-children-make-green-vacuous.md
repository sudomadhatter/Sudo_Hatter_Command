---
name: stubbed-children-make-green-vacuous
description: "A page-level test that vi.mocks its child panels proves NAVIGATION, not the panels — \"N passed, first execution ever\" is a claim about what actually EXECUTED, so check what the file stubs before believing a coverage claim"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fd0be18a-da49-4433-b48f-a3bff6f02bf6
  modified: 2026-07-27T02:55:08.662Z
---

**2026-07-26 (story 21.5 ③, independent second pass).** Both new `/sudo_admin` panels —
`NdaVaultPanel.tsx` + `BackupsPanel.tsx`, **393 lines on a P0 story** — had **zero** component tests.
The story's only frontend test, `sudo_admin.nda-vault-backups.red.test.tsx`, `vi.mock`s both panels out
as marker stubs so it can assert tab navigation without mounting heavy trees. That is the correct
contract for *that* file. But it meant the headline result — *"the frontend contract tier now runs, 7
passed, first execution ever"* — proved the **tabs**, not the panels. Search, date bounds, export
wiring, error slots and empty states were executed by nothing.

**Why:** the tell is that every frontend defect in that story was found by **reading**, never by a
runner — two in the builder's own review pass (a silently-dropped export failure, a see-vs-export
filter divergence) and a third in the independent pass (the sibling panel dropped *thrown* export
failures, so an expired JWT made the disaster-recovery Export button do nothing at all). A green suite
over stubbed children is not weak coverage, it is **absent** coverage wearing a green badge, and the
"first execution ever" framing makes it read as *more* assurance than it is.

**How to apply:**
- Before quoting a suite as evidence for a component, **grep that test file for `vi.mock` of the thing
  you are claiming coverage for.** If it is stubbed, the file says nothing about it.
- A panel gets its own `components/<area>/__tests__/<Panel>.test.tsx`. In AGY this is the house
  convention (11 sibling panels have one) and the precedent is Story 8.19.8's
  `SchoolAdminManagement.test.tsx` — a component-level backfill for a panel that had shipped with only
  page + e2e coverage. Page-level and component-level are different tiers; one never substitutes.
- This does NOT contradict [[red-file-hosts-expansion-tests]]: that rule keeps a story's tests in one
  red file **per stack/tier**. A stubbed page test and a panel test are different tiers.
- Corollary for a builder reviewing their own work: a same-session self-review re-derives from the same
  mental model that wrote the gap, so it is systematically blind to *missing* tests — it audits the code
  that exists, not the coverage that doesn't. That review self-declared as non-independent and asked for
  a second pass; the second pass found 9 more items. Take that ask seriously.

Related: [[agy-frontend-vitest-harness]], [[sudo-admin-jsdom-oom-machine-bound]],
[[red-file-hosts-expansion-tests]], [[test-priorities-matrix]], [[e2e-gate-fiction-test-guardrails]].
