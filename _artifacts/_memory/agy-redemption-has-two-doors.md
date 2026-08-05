---
name: agy-redemption-has-two-doors
description: AGY school-code redemption runs through TWO paths that both mint the access claim — the REST endpoint AND the HR agent tool; a claim-contract change must land in both or you ship a free-access bypass.
metadata: 
  node_type: memory
  type: project
  originSessionId: 58e40149-855d-4111-aaa7-4bcc8efdb5da
  modified: 2026-07-24T17:45:52.940Z
---

AGY has **two** school-code redemption doors, and both mint the Firebase custom claim that
gates the paid agents:

1. `POST /api/redeem-school-code` → `backend/routers/entitlement.py` (the obvious one).
2. `execute_attach_school_code` in `backend/agents/hr/tools.py` — Mrs. Coleman (the HR agent)
   lets a solo student attach a code conversationally (Story 17.10). It reuses the SAME
   `schools_service.redeem_seat`, then mints the claim itself.

**Any change to what redemption grants must land in BOTH doors, or the HR path becomes a
bypass.** Story 21.1 made redemption default-OFF (mint `school_code` only, never `entitled`);
the plan fixed only `entitlement.py`. The self-audit (F1, P0) caught that `hr/tools.py` was
still minting `{entitled: True}` unconditionally — a full default-OFF bypass via the chat agent.
Both were brought to the same D1 rule (fresh → `school_code` only; ALREADY → `entitled` iff the
member is `active`, guarded fail-closed).

**How to apply:** when touching redemption / entitlement claim behavior (Epic 21.2 server-truth
revoke, Epic 18 billing→entitled, any seat/claim change), `grep -rn "redeem_seat" backend/ --include=*.py`
first and update every caller's claim-minting to match — don't trust that the REST endpoint is the
only path. This is the redemption-specific case of [[new-read-on-shared-endpoint-regresses-siblings]].
Related: [[agy-school-seat-cap-fails-closed]] (the shared `redeem_seat` seat-cap behavior).
