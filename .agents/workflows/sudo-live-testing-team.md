---
description: Live Testing Team — the human flies the app while the agent boots the dev env, watches the backend logs live, coaches the frontend DevTools check, and files researched bug docs that feed the sudo story flow. Writes NO product code.
---

# /sudo-live-testing-team — Live Testing Team (co-pilot debugging loop)

The human drives the running app; you are the flight engineer. Boot the stack, keep every instrument
in view, and turn every symptom into a **researched bug document** that the sudo dev flow
(①②③ story loop, or `/sudo-quick-dev` for small fixes) picks up afterward. This command writes
**no product code** — its output is evidence, not patches.

## Step 0 — Resolve the target project (FIRST — before anything else)
Run from the **command center** (the lobby), this operates on exactly ONE child project under `Projects/`,
never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path — check FIRST, STOP here if it matches)** — if this repo has **no**
   `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip ahead. Do NOT read
   `active-project.txt`, parse `$ARGUMENTS` for a project name, or ask which project.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is
   the target; consume that first token (the remainder is the real argument — area under test). Write the
   name alone into `.agents/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under `Projects/`, use it.
3. **Ask** — else STOP and ask which project we're working in — never guess, never operate on the lobby.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

## Step 1 — Boot the dev environment
1. Load `PROJECT_ROOT/_bmad-output/active-context/active-context.md` and give a 3-line context summary.
2. Reap stale dev processes (node / python / uvicorn). `taskkill` is prompt-gated per call — that is
   intentional; confirm each kill. Sleep ~5s after killing so ports leave `TIME_WAIT`.
3. Start BOTH servers as **background processes** (the log stream must stay readable across turns —
   a foreground uvicorn blocks and defeats the whole command):
   - Backend, from `PROJECT_ROOT`: `backend\.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
     (`--reload` = temporary debug logs apply without a restart)
   - Frontend, from `PROJECT_ROOT/frontend`: `npm run dev`
4. Health-check both (backend `/health`, frontend root), then hand over the URL: **you fly, I watch.**

## Step 2 — The co-pilot loop (repeat until the human ends the session)
- **Re-read the captured backend output every turn.** Proactively flag tracebacks, 4xx/5xx, and silent
  anomalies even when unprompted; deep-dive reactively the moment the human reports a symptom.
- **You cannot see the browser.** For frontend symptoms, coach the human with ONE specific ask at a
  time — the exact Console error line, the failing Network row (URL + status + response body), the
  component state — never a vague "check DevTools".
- **Instruments, cheapest first:** backend logs (always on) → browser DevTools via the human →
  Firestore reads (`get_db()`) → temporary debug logs (reload picks them up; remove at close) →
  Cloud Run / `gcloud` (ask first). Always ask before reaching outside the local box.

## Step 3 — Recon every confirmed symptom into a bug doc
For each distinct bug, research the ROOT cause: read the code path, correlate the log evidence, and
check claims against the docs — mark every finding **verified** (evidence in hand) vs **docs-say**
(plausible, needs confirmation). Then file one doc per bug at
`PROJECT_ROOT/_artifacts/debugging/<YYYY-MM-DD>_live-testing/<n>-<slug>.md` containing:
- **Symptom** — what the human saw, in their words
- **Evidence** — exact log lines / network rows / console output captured
- **Root cause** — ranked hypotheses, each tagged verified vs docs-say
- **Proposed fix direction** — where the fix lives, NOT the fix itself
- **Suggested lane** — `/sudo-quick-dev` (small/contained) or the full ①②③ story loop (risky/cross-cutting)

## Step 4 — Close out
Post a session summary table (bug → doc link → suggested lane). Ask whether to keep or kill the
servers. Remove every temporary debug log you added. The fixes themselves happen in the sudo dev
flow — never in this chat.

Optional additional input (area under test / known-flaky route): $ARGUMENTS
