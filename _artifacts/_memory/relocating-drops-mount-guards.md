---
name: relocating-drops-mount-guards
description: "Moving a conditionally-mounted component into a render guard silently drops its mount preconditions — re-assert every guard the old `{cond && <X/>}` carried."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: cb43509f-08ae-4bb4-bd59-bd39f9901414
  modified: 2026-07-20T20:28:21.492Z
---

Relocating a component out of a conditional JSX mount (`{cond && <X/>}`) into an early-return render
guard **silently drops the preconditions the old mount enforced** — the new guard only re-implements the
conditions you explicitly re-type. AGY 17.9 relocated `SchoolCodeGate` from a post-paint overlay
(`dashboard/page.tsx:639`, mounted `{sessionReady && <SchoolCodeGate/>}`) into a pre-paint guard keyed on
`entitlementChecked` (a client-only ID-token read that resolves **before** `sessionReady`). That dropped the
`sessionReady` gate → `SchoolCodeGate`'s Redeem → `redeemSchoolCode` → `authenticatedFetch`, which **throws
before the backend session cookie exists** (AGY invariant, also in `project-context.md`: "API calls MUST be
gated behind `sessionReady`") → a live window where Redeem lands in a spurious "Something went wrong". Fix:
hold ONLY the gate branch on `sessionReady` (`if (!sessionReady) return null;`) so the loader owns the screen
until the gate is actionable; entitled/solo users still paint immediately.

**Why:** the bug survived a green ②: the ATDD/integration tests mocked `sessionReady:true`, so the timing race
was invisible to tests — only the ③ clean-room review, reading the *diff against the removed mount*, caught it.
This is exactly the class the review gate exists for. See [[agy-error-envelope-shapes]] (another "the FE read
narrowed a precondition" AGY regression) and [[shared-registration-file-entangles-stories]].

**How to apply:** when a story RELOCATES or UNWRAPS a conditionally-mounted component, diff against the OLD
mount site and enumerate every guard it carried (`sessionReady`, auth, feature flags, `isLoaded`, error
boundaries) — re-assert each in the new location or justify dropping it. When you add the fix, pin it with a
test that drives the dropped condition false (the ATDD suite won't, since it mocks the happy path true).

**Confirmed again 2026-07-20** (AGY debug-1.3, HRChat "Proceed to Specialist" button move out of a
static post-map render into an inline `messages.map` slot): applied proactively this time, not review-caught
— every guard (`isCleared`, `clearedReason === "indoc"` video gate, `onClick`) was re-asserted before dev
finished, plus a new `clearedMessageIndex === null` end-of-list fallback for the case clearance fires before
any message exists. The rule is worth keeping as a standing dev-time checklist item, not just a review catch.
