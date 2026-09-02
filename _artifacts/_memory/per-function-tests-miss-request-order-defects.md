---
name: per-function-tests-miss-request-order-defects
description: "A suite that drives each function against a hand-built fixture certifies COMPONENTS, not the assembled machine — defects that live BETWEEN functions in production request order stay invisible and ship green."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ccec7e02-346d-4d32-b2ff-da2abcb9d9b6
  modified: 2026-09-02T16:23:19.482Z
---

**A per-function test suite can be 100% green while the feature has never once worked.** AVCH-109
(story 24.7) certified at ② with 3261 passing tests; its centrepiece — the agent noticing a passed
checkride date — fired for **zero users**. Every test handed one function a fixture already in the
state that function expected, and asserted it behaved. All of them were right. The defect was that
the login `GET` called the session-start observer and CONSUMED the trigger before the chat `POST`
(the only door that can ask the question) ever ran. **No test drove the two in order**, so nothing
could see it.

**Why:** the fixture IS the missing coverage. Hand-building the input state silently asserts "some
caller produces this", which is exactly the claim that was false — production's `get_student_profile`
never returns the empty dict the INDOC branch was written against, and production's login always
runs before the chat. Three more defects hid in the same blind spot: a branch that bound no variable
(NameError for every pre-rebuild user), markers nothing ever cleared (a once-per-account-lifetime
trigger), and a rehydrate that mis-authored replayed turns.

**How to apply:** for any feature whose behaviour spans more than one entry point, buy a **seam
test** — drive the REAL endpoints in production ORDER against real storage, stubbing only the
outermost dependency (the model, the payment provider). One such test per feature spine, not per
function. Two rules make it real: assert on the *stream/state*, never the status code, when the
handler catches its own exceptions (a 200 carrying an error event looks identical to success); and
`assert not doc.get(KEY)` passes vacuously when the code never writes KEY at all — assert the key is
PRESENT and falsy when the fix is supposed to clear it.

Related: [[stubbed-children-make-green-vacuous]] (the mock-depth version of the same blindness),
[[prose-pinning-guards-are-vacuous]], [[test-certification-at-shipping-sha]].
