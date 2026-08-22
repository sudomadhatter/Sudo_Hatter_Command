---
name: red-test-can-die-before-its-assertion
description: A red test that dies in SEEDING/setup fails identically whether or not the behaviour works — check WHERE it fails before trusting a red or writing a story to fix it
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7c61bd5b-6cad-4c69-b6de-8ce2dea9c7a9
  modified: 2026-07-27T02:54:45.965Z
---

**2026-07-26 (story 21.3 ②).** A failing test is only evidence about the behaviour it names **if it
reached the assertion**. `test_coleman_session_emulator_e2e.py::test_EMU_DUR_002` was failing on
`AttributeError: 'FieldWriteResult' object has no attribute 'success'` — the dataclass exposes
`accepted` (`profile_service.py`) and never had `success`. It died during **seeding**, so it failed
identically whether or not durable cross-instance Coleman history worked. One-line fix and it went
**green** — the feature had been built all along, and the test's own "fails RED today" docstring was stale.

**2026-07-26 (story 21.5 ③, independent pass) — the SAME defect, rediscovered hours later by a second
lane that had no idea 21.3 had just fixed it.** Both lanes shipped byte-identical code
(`assert result.accepted`); the close-out merge conflicted only on the comment. 21.5 had been carrying
EMU_DUR_002 as grandfathered legacy across ①, ② **and** a full review pass, on the strength of
"it reproduces on `main_debug`". **Reproducing on the trunk proves a failure is not YOURS. It does not
prove it is LEGITIMATE.** Two independent lanes paying to rediscover one typo is the standing cost of
skipping the check below.

**Why:** a harness bug wearing a red test's clothes is indistinguishable from a legitimate red if you
only read the pass/fail column. It is worse than a plain broken test, because a red is *supposed* to be
there — so it gets grandfathered as "known legacy red", or worse, a story gets written to build a feature
that already exists. This trap hit three times inside one story (①'s reds twice, then this one), then a
fourth time in a different story — which is why it is a standing check, not a one-off note.

**How to apply:**
- Read the actual traceback of every red before accepting it — specifically **which line** raised. Setup /
  fixture / seeding frame = the test is broken, not the code. Assertion frame = a real red.
- A red whose docstring claims "fails RED today" is a claim with a date on it. Re-verify it before
  building against it; features land from other lanes.
- This is the diagnostic half of `tests-must-gate-for-real` — that rule says a red must fail for the RIGHT
  reason; this says *how you check*: look at where it died, not that it died.
- Corollary for reviews: never grandfather a red as "pre-existing legacy" without opening its failure.
  See [[e2e-gate-fiction-test-guardrails]] for the sibling failure (a red asserting strings absent from
  real source) and [[test-live-guard-needs-live-marker]] for the vacuous-green sibling.

Related: [[e2e-gate-fiction-test-guardrails]], [[test-debt-stories-are-characterization]],
[[recon-reframes-story-scope]], [[agy-backend-emulator-e2e-tier]].
