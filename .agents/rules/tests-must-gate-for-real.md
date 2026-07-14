---
name: tests-must-gate-for-real
description: "Activates whenever a test is written, a CI/quality gate is scaffolded or reviewed, or a suite is marked report-only/soft/skip. A test only protects you if it fails for the RIGHT reason, CI runs the REAL suite, and no gate is soft forever."
---

# A Test Only Counts If It Actually Gates

## When This Applies
Writing acceptance/ATDD tests (①), scaffolding or editing a CI pipeline / quality gate
(`bmad-testarch-ci`, workflow YAML), and every test-gate review (③). Applies to Claude,
autopilot, and manual / Antigravity workflows alike.

## The Trap
A red test READS as protection. A CI job that says "E2E" READS as coverage. A `continue-on-error`
step with a "flip to hard gate later" comment READS as a temporary measure. All three can be hollow:
- A red that asserts strings/selectors/endpoints **the codebase never had** fails identically whether
  the feature is unbuilt or the assertion is invented — so it can never go green, and it proves nothing.
- A CI job can run a *different, partial* test config than the one that matters and still show a green
  check — the real suite never ran.
- "Report-only FOR NOW" with no owner and no expiry silently becomes "report-only forever."

## The Rule
1. **A red must fail for the RIGHT reason — grounded in real source.** Before a red counts as a valid
   ATDD red, verify every asserted string, selector, endpoint, and **precondition** against the actual
   code (grep the producing surface; read the page/handler). The red must fail because the feature is
   *unbuilt*, never because the test invented a literal or misread the auth / precondition model. A test
   asserting copy absent from source, or calling an auth-gated page "public," is **fiction, not a red** —
   fix or delete it; never let it ride. (See [[atdd-mock-shape-must-match-backend-contract]].)
2. **CI must run the REAL suite entrypoint.** The gate must execute the project's actual harness command
   — the *same* one the local gate runs (`npm run test:e2e`, the full pytest suite, …) — not a divergent
   or partial config that silently skips the suite that matters. When reviewing a gate, confirm the job's
   command invokes the real entrypoint and that the tests you think protect the branch actually executed.
3. **A soft gate is a ONE-RUN window with a named owner + a tracked expiry — never open-ended.**
   `continue-on-error`, `|| true`, `.skip`, `xfail`, and grandfathered "legacy red" are all forms of *not
   gating*. Each is legitimate only briefly — to prove a brand-new harness on CI once — and only if it
   carries a named owner and a tracked task to close it. In review, flag any soft/report-only test step
   that lacks both as a finding (CONCERNS floor). Grandfathering "fail only on NEW regressions" is real,
   but legacy red must be **examined and owned** (quarantined-with-ticket), not unexamined permanent
   failure a fiction test can hide inside.

## Why
Source: AGY 2026-07-13. `frontend/e2e/hanger-talk.spec.ts` asserted four UI strings ("Free Learning
Materials", "Hanger Talk Series", …) that appear **0×** in the frontend source, against a route that is
auth-gated (renders `null` when logged out) — the test called it "public." It never passed. Meanwhile CI
ran the plain `playwright.config.ts`, which `testIgnore`s `journeys/**`, so the REAL TEA-16 emulator
harness (6/6 green locally the whole time) never ran on CI at all; the failing job was
`continue-on-error: true` — "report-only FOR NOW" — left open indefinitely. Three independent holes —
fiction red at ①, wrong CI entrypoint, report-only-forever — each of which this rule closes. The guard is
cheap (grep the source, check the CI command, put an owner on every soft gate); the failure — a suite that
looks green while protecting nothing — is not.
