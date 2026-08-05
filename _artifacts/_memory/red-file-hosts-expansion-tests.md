---
name: red-file-hosts-expansion-tests
description: "AGY frontend convention — post-green /bmad-testarch-automate expansion tests AND /sudo-code-review patch tests are appended as extra describe/it blocks INSIDE the story's own `.red.test.tsx`, not a new file"
metadata: 
  node_type: memory
  type: project
  originSessionId: 30de0369-2770-48ff-bef5-20f81142fc67
---

On AGY, a story's `*.red.test.tsx` is the ONE permanent home for all of that story's component
tests across its whole lifecycle — the ATDD red block (T1–T5) plus the `/bmad-testarch-automate`
expansion block (E1–E5) plus any `/sudo-code-review` patch tests (E6, E7, …) all live in the same
file, reusing the same file-scoped `vi.mock` seam. Precedent: CostDashboard → CurriculumBrainGraph
(Story 8.22.2).

**Why:** the convention is invisible from any one file's name (`.red` sounds red-phase-only), so agents
keep minting a second `*.expansion.test.tsx` / `*.exam-overlay.test.tsx`. In 8.22.2 the GLM lane did
exactly that and the manual lane had to fold the duplicate back in and delete it. Per-file vitest import
cost is real, so one file per component surface is also cheaper.

**How to apply:** when expanding coverage or adding review-patch tests for an existing story, EXTEND the
story's `.red.test.tsx` with a new `describe(... expansion)` / `it(...)` block — do NOT create a sibling
test file. Same rule the [[agy-frontend-vitest-harness]] memory states for SpecialistChat. Only the
review's own new fixes get new `it`s (E6/E7 in 8.22.2), each pinning one patch.
