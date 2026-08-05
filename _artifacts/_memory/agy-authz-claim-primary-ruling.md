---
name: agy-authz-claim-primary-ruling
description: "AGY authorization is claim-primary by STANDING operator ruling (8.19.9, re-affirmed 2026-07-24 when Epic 21's story 21.2 was descoped) — never propose putting Firestore reads on the entitlement gate; rulings live in docstrings, grep before writing an FR that changes a gate."
metadata: 
  node_type: memory
  type: project
  originSessionId: d2746ce5-6825-4874-8fa6-5a17773ce9da
  modified: 2026-07-25T16:03:35.838Z
---

AGY's entitlement gate is **claim-primary and stays that way**. `is_entitled()`
(`backend/middleware/entitlements.py`) is a pure `claims.get("entitled") is True` lookup with **zero
datastore reads**, and a revoke lands at the next ID-token refresh (~1hr), bounded by `check_cost_cap`
(close 4029). Ruled in story 8.19.9 ("no instant kill switch"), **re-affirmed 2026-07-24** when Epic 21's
story **21.2 (server-truth revocation gate) was DESCOPED** — terminal, not deferred.

**Do not propose a per-connect Firestore read on this gate again.** The reasons, so they don't have to be
re-derived: the stale-claim hour grants only more Sully/Igor (tenancy runs through `scoped_user_query`,
which never reads the claim, so there's no cross-student data dimension) and spend is already capped
(the 4030-gate / 4029-cost-cap split is [[voice-router-entitlement-vs-cost-cap]]);
whereas 3 fail-closed reads on a path that today has zero I/O means one Firestore hiccup denies **every**
student at once. RFC 7009 + Firebase's own docs (`check_revoked` for sensitive operations only) make
claim-primary the industry standard, not debt. If instant revoke is ever genuinely needed the shape is
`fb_auth.revoke_refresh_tokens(uid)` at revoke **plus** `check_revoked=True` on the `verify_id_token` the
WS handlers already call — and `check_revoked` **alone does nothing** (it detects token revocation and
disabled accounts, never custom-claim staleness).

**The transferable lesson: this codebase records operator rulings in DOCSTRINGS, and an epic brief can
re-raise a settled decision without noticing.** Epic 21 wrote E21-FR2 to "fix" exactly what
`entitlements.py:32` already documented as deliberately-not-wired. Before authoring an FR that changes an
existing gate, default, or contract, **grep the target surface for a prior ruling** — the justification
is usually sitting in the docstring of the function you're about to rewrite. Related: the same file's
`max_seats` fail-closed default has its own recorded rationale ([[agy-school-seat-cap-fails-closed]]).

**Descope process (the house standard, now in the sprint-status STATUS DEFINITIONS legend):** never mark
unbuilt work `done` (a false `done` corrupts every trace and retro); never delete the row (that destroys
the decision and guarantees it gets re-proposed — which is what happened here); and move every FR/NFR
that traced ONLY to the dropped story so nothing is orphaned. 21.2 took E21-FR2 + NFR3 + NFR5 with it;
NFR2/NFR4 survived via 21.12/21.3. Precedent rows: `7-8-load-testing`, `21-2-server-truth-revocation-gate`.
See [[story-status-flip-contract]] and [[close-out-command-is-daniels-signoff]].

Claim *minting* is a separate surface with its own trap — it has two doors
([[agy-redemption-has-two-doors]]); this memory covers the *reading* side only.

**Known issue left open** (filed 2026-07-24, operator declined the fix): `schools_service.py:296-301`
swallows a revoke-time claim-mint failure — the member doc and roster read `revoked` while the token keeps
`entitled` **indefinitely** (not 1hr; nothing re-reads the member doc), and the toggle still reports
success. Low probability, unbounded duration, no admin signal. Full record:
`Projects/AGY_AVIATIONCHAT/_artifacts/epic_21/story-21-2-server-truth-revocation-gate/decision-record.md`.

**Re-affirmed a THIRD time on 2026-07-25**, unprompted, when the operator live-verified the revoke path
(toggled a student's access off, confirmed access removed — 21.1's Manual tier, both polarities). Their
words: *"it does not need to be instant, one hour is perfectly acceptable; we decided against doing that
story."* **The hour is the product decision, not a caveat, not debt, and not a gap** — write it up that
way. Filing it under "limitations" or "what we didn't close" is a mis-framing that invites the next agent
to propose 21.2 again; that is exactly how E21-FR2 got written the first time. 21.2 is terminal.

The swallowed revoke-time mint failure above is likewise **accepted risk, still declined** — record it so
it isn't rediscovered as a fresh bug, but imply no action. Only two things here are genuinely owed, and
both are runtime ops rather than design questions: the `firestore.rules` members-deny **deploy** and the
idempotent **backfill** run. All three (those two plus the mint-failure) share a property worth knowing —
they are invisible from the happy path, so a green manual toggle says nothing about any of them.
