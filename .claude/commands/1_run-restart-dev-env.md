---
description: Kills existing node/python/uvicorn processes and restarts the backend (8000) and frontend (3000)
---

# /1_run-restart-dev-env — Restart Dev Environment

Execute the workflow defined in @.agents/workflows/1_run-restart-dev-env.md.

**opencode execution notes:**
- `taskkill` is gated behind `permission.bash` `ask` — Don will be prompted for each kill. That's intentional; he should confirm before zombie processes are reaped.
- Backend command: `backend\.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000`. Run from project root.
- Frontend command: `npm run dev` from `frontend/`. Sleep 5 seconds between kill and frontend start so ports exit `TIME_WAIT`.
- Per the workflow, also load `_bmad-output/active-context/active-context.md` first and output a brief context summary (this is Step 0 in the workflow).
- After both servers report healthy, confirm to Don with the URL and remind him of relevant guardrails (G2/G3/G8).

Optional additional input: $ARGUMENTS
