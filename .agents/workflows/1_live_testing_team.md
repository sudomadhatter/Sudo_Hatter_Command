---
description: Live Testing Team — Daniel flies the app, Claude watches the backend logs live. Co-pilot loop that logs ROOT causes (verified vs docs) and produces a fix plan. Writes no code.
---

# /1_live_testing_team — Live Testing Team

Execute the workflow defined in @.agents/workflows/1_live_testing_team.md.

**Claude Code execution notes:**
- Start BOTH servers as **background processes** (Bash `run_in_background`) so the log stream stays
  readable across turns — foreground uvicorn blocks and defeats the whole command.
- Backend: `backend\.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload` from project root (reload = added debug logs apply without a restart).
- Frontend: `npm run dev` from `frontend/`; sleep ~5s after the kill so ports leave TIME_WAIT.
- `taskkill` is gated behind a per-call prompt — that's intentional; confirm before reaping.
- Re-read the captured backend output on every turn: proactively flag tracebacks/errors,
  reactively deep-dive when Daniel reports a symptom.
- **Instruments (Phase 1.5):** backend logs (always), browser DevTools (ask Daniel for one specific
  line), Firestore via `get_db()`, Cloud Run via `gcloud` (ask first), temporary debug logs. Lead
  with the cheapest channel; always ask before reaching outside the local box.
- This command writes NO code. It produces `debug-watch-log.md` + a fix plan. Actual fixes go
  through the artifacts protocol (this chat after approval, or a dev chat).

Optional additional input (area under test / known-flaky route): $ARGUMENTS
