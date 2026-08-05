---
name: settled-decisions-are-not-gaps
description: "Never write a ruled-on product decision up as a caveat, limitation, or \"what we didn't close\" — that framing gets the decision re-proposed later; state it as the decision, with the ruling quoted."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d1bc5de1-b28b-40c0-a47b-3d0e4c6de41a
  modified: 2026-07-25T16:14:10.787Z
---

When a behaviour is a **deliberate, ruled-on decision**, document it as the decision — not under
"limitations", "caveats", "scope of the proof", or "what this pass did NOT close". On 2026-07-25 I filed
AGY's ~1-hour entitlement-revocation window under "what this pass did NOT close" after the operator
live-verified the revoke path. His correction: *"that is fine, we decided against that, it does not need
to be instant, one hour is perfectly acceptable... and that needs to be reflected."*

**Why:** a debt-shaped heading is an invitation. The next agent greps the doc, sees the settled thing
sitting in a gaps list, and writes a story to "fix" it. That is not hypothetical — it is exactly how
Epic 21's E21-FR2 came to re-raise a decision 8.19.9 had already made, and it cost a full ① plan-gate
cycle to descope again. See [[agy-authz-claim-primary-ruling]].

**How to apply:** when recording a decided behaviour — (1) give it an affirmative heading (*"Revocation is
~1 hour, and that is the decision"*, not *"Revocation is not instant"*); (2) **quote the operator's ruling
verbatim** with its date, because a quote survives paraphrase-drift where a summary doesn't; (3) label the
superseded story **terminal** — "not deferred, not backlog, not a follow-up" — since `descoped` alone
reads to some agents as a queue state; (4) keep genuinely-owed items in a *separate* section so the two
never blur. Declined fixes get the same treatment: mark them *accepted risk, no action implied*, recorded
only so they aren't rediscovered as fresh bugs. Verified-live evidence is *consistent with* the design —
never phrase it as failing to prove something the design never claimed.
