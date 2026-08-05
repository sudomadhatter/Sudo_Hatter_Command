---
name: agy-school-seat-cap-fails-closed
description: "AGY schools/{code} docs with no max_seats field silently fail closed — redeem_seat treats a missing cap as 0, so EVERY redemption 404s as REDEEM_FULL even at zero enrollment."
metadata: 
  node_type: memory
  type: project
  originSessionId: f8a6b1f1-691b-4b33-9dc3-d6673f1dc56b
  modified: 2026-07-20T20:28:32.624Z
---

`redeem_seat` (`backend/services/schools_service.py`) counts `users where school_code == code` inside a
transaction against `max_seats`. If a `schools/{code}` doc was created without ever setting `max_seats`,
the field reads as missing/`None` → the fail-closed guard treats that as a cap of 0 → **every** redemption
returns `REDEEM_FULL`, indistinguishable from "the cohort is genuinely full" — this looked exactly like a
real capacity problem for TESTPILOT even though `seats_redeemed: 0` (nobody had ever gotten in). Diagnosed
2026-07-19/20 (AGY debug-1.4) via `backend/scripts/set_school_max_seats.py --dry-run`, which reports
`max_seats_before` — `None` is the tell, not a number at the limit.

**Why:** fail-closed on a missing cap is the correct security default (never over-admit), but it produces a
misleading symptom ("no more spots" on a school nobody has joined) that reads like a full-cohort bug, not a
provisioning gap.

**How to apply:** before debugging a "no more spots" / `REDEEM_FULL` report for any school code, dry-run
`set_school_max_seats.py --code <CODE> --seats <N> --dry-run` first and check `max_seats_before` — `None`
means the school was never given a cap, not that it filled up. When onboarding a NEW school, always set
`max_seats` explicitly at creation; don't rely on a default. See [[relocating-drops-mount-guards]] for the
sibling AGY pattern of "the fix is in re-verifying an assumed root cause against real data before coding."
