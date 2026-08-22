---
name: test-debt-stories-are-characterization
description: "Test-debt-paydown stories (TEA-*, retrofits onto already-shipped code) are characterization — tests pass green-first as regression tripwires, not red→green; don't fake a red phase."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 73ca08eb-87a8-432b-af19-3522ff5d8898
---

When a sudo-loop story adds tests to **existing, already-correct** code (the TEA testing-architecture retrofit, or any "add a test net" story), the classic ATDD red→green model does NOT apply: the behavior is already correct, so well-written tests **pass on the first run**. Their value is as **regression tripwires** — they go red only if someone later weakens the thing under test (e.g. a Pydantic required field gains a default, a `Literal` enum is widened/dropped).

**Why:** Forcing a fake "red phase" (e.g. temporarily mutating production source to stage a failure) is dishonest engineering and risks the shipped code. Daniel values owning the nuance over performing ceremony. The honest framing is *characterization + tripwire*, and the tripwire is **proven by construction**: the negative tests (`missing_*_raises`, `off_enum_*_raises`) pass only because the real contract rejects those inputs today — weaken the contract and those exact tests fail.

**How to apply:** For a test-only/additive story — (1) write the tests, (2) run them and expect GREEN, (3) state plainly they're tripwires not red→green and that the tripwire is proven by the passing negative cases, (4) do NOT mutate source during the *dev phase* to stage a fake red, (5) at the gate, judge on **no NEW regression** vs the at-opt-in baseline (not on a red→green transition), and (6) the dev step (`/sudo-dev-story-tests`) collapses — fast-forward to `/sudo-code-review`.

**Two real exceptions where a genuine red→green still applies to a retrofit:**
- **NEW behavior** (e.g. a behavioral trigger the code doesn't yet do) — classic red-first ATDD.
- **Correct-but-UNTESTABLE behavior** (the decision is right but buried with no seam — e.g. TEA-3's `confidence_reset` firing, a branch ~30 lines deep in a ~600-line async method). Here the honest red→green is a **behavior-preserving extraction**: pull the decision into a pure helper (`_select_zone2_override`), which is RED until extracted, GREEN after. The "fix" is **testability, not behavior** — prove it with a full regression slice (TEA-3: 176 tests green) so you know nothing changed. This IS the paydown the retrofit exists for. (TEA-3 was mixed: Groups A/C characterization, Group B this extraction case.)

**Mutation-at-the-GATE is NOT the point-4 "fake red" — it's required.** Proving a test is non-vacuous by break-invariant → confirm-RED → **revert-clean** (TEA-1/10/11/3 all did this) is legitimate and expected; point 4 only forbids staging a fake red *during dev* to cosplay ATDD. Related: [[tea-retrofit-active-initiative]], [[story-status-flip-contract]], [[own-it-plainly-dont-make-excuses]].
