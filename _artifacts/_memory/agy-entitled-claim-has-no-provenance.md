---
name: agy-entitled-claim-has-no-provenance
description: "AGY's `entitled` custom claim is ONE boolean with no record of who granted it, and every revoker does `existing.pop(\"entitled\")` — so Epic 18's billing webhooks will clear school-granted access and vice versa; settle provenance at 18.1's ① or it surfaces as a refund/lockout bug at 18.2."
metadata: 
  node_type: memory
  type: project
  originSessionId: 27c1ed6c-690d-4f25-91b4-b537755e900d
  modified: 2026-07-25T19:05:15.134Z
---

**The paywall is already live — Epic 18 does not turn it on.** `is_entitled()` in
`backend/middleware/entitlements.py` has gated the three paid agents (`specialist`, `sully`, `igor`)
since 8.19.9. It is one dict lookup, zero I/O:

```python
return claims.get("entitled") is True
```

Solo students have no claim → they hit `BetaLockPopup` ("no way to pay your way in yet — that's by
design") → `/earlyaccess` waitlist. **18.1 adds a third *minting door*, not a new wall** (E18-FR1:
"zero new gate logic"). Nothing a user sees changes until a checkout page is *reachable*, so Epic 18
does **not** need a feature branch — the real switches are the popup's CTA link and the Stripe key.

**The landmine.** `entitled` carries no provenance. Writers today:
- `routers/entitlement.py` — school redeem (+ F2 recovery re-mint)
- `agents/hr/tools.py::attach_school_code` — the second redemption door
- `services/schools_service.py::set_member_access` — admin toggle; on revoke it does
  `existing.pop("entitled", None)`

Epic 18 makes that **five** writers (18.1 checkout grant, 18.2 webhook revoke). Because any revoker
clears the single shared boolean:
- solo subscriber → joins a school → cancels the personal plan → **loses school access they're paying
  for through the school**
- school admin revokes a student who is also an individual subscriber → **their paid subscription
  silently stops working** (refund + support ticket)

E18-NFR2 ("a revocation always wins over a stale grant") makes fail-closed *amplify* this, not contain
it. The 18-2 sprint line already promises *"school-granted claims NEVER touched by billing"* — that
promise needs a data model to be true.

**Fix shape that doesn't reopen 21.2:** keep `entitled` as the boolean the gate reads (so `is_entitled`
never changes and stays zero-I/O) but **compute it at mint time from per-source flags**
(`school_entitled` / `paid_entitled`, or a sources list). Each writer clears only its own source and
recomputes. Claim-primary, fail-closed, and the ~1h TTL ruling all hold. Decide it at **18.1's ①
Vision Lock** — at 18.2 it's a migration.

Same class of bug as [[agy-redemption-has-two-doors]] (21.1 F1 was a P0 bypass because a second door
minted the claim unconditionally). Adding writers to an unowned claim is how that repeats.

**18.4 (free lesson) is `deferred` 2026-07-25** — it was the only Epic 18 story that changes solo
behavior the day it ships. On resume: the consumed-flag check goes on the Specialist route *after* the
gate returns un-entitled, **never inside `is_entitled()`** — that is exactly what 21.2 was descoped for.

Related: [[agy-authz-claim-primary-ruling]], [[voice-router-entitlement-vs-cost-cap]].
