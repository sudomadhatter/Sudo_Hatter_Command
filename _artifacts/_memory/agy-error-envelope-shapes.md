---
name: agy-error-envelope-shapes
description: "AGY backend error responses come in TWO shapes — HTTPException wraps the payload under body.detail, but app-level exception handlers (429 rate-limit, 500) return a TOP-LEVEL body.error; a FE read narrowed to detail.error.message silently swallows the 429 and any top-level 4xx."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 21e3b4cc-0878-4828-b1a9-eb886c8abc71
---

AGY frontend error-mapping must handle two envelope shapes, and they are NOT interchangeable:

- **`HTTPException(status_code=4xx, detail={...})`** (e.g. `admin_login` 401 in `backend/routers/admin_auth.py`) → FastAPI serializes as `{"detail": {"success":false, "error":{"message":...}}}`. Payload lives at **`body.detail.error.message`**.
- **App-level `@app.exception_handler(...)`** returns a **TOP-LEVEL** envelope `{"success":false, "error":{"message":...}}` (NO `detail` wrapper): the **429** rate-limit `custom_rate_limit_handler` (`backend/main.py`, message "Rate limit exceeded: …") and the **500** `unhandled_exception_handler` (`backend/middleware/error_middleware.py`, the STUDENT "…study progress is safe." copy). Payload lives at **`body.error.message`**.

**The trap (Story 17.1 CR-1, code review):** `adminApi.adminLogin` narrowed its read to `body.detail.error.message` to stop the 500 student copy leaking into the admin card — which ALSO swallowed the 429 rate-limit message (admin then saw a bare "Authentication failed (429)"). **Correct pattern:** read `body.detail.error.message` first (the credential 401), THEN fall back to top-level `body.error.message` **only for 4xx** (`res.status < 500`) — surfaces genuine client errors (429) while keeping the 5xx student copy suppressed. The student-side `frontend/src/lib/api.ts` has a long-noted vaguer relative of this bug (active-context pitfall "api.ts error path may be broken for detail.error.code").

Both envelope shapes still carry the frozen dual wire keys `catigory` (typo) + `category` — never touch just one. Related AGY wire-contract gotcha: [[voice-router-entitlement-vs-cost-cap]].
