---
description: Live Testing Team — the human flies the app while the agent boots the dev env, watches the backend logs live, coaches the frontend...
---

# /cicd-live-testing-team — Live Testing Team (co-pilot debugging loop)

The human drives the running app; you are the flight engineer. Boot the stack, keep every instrument
in view, and turn every symptom into a **researched bug document** that the sudo dev flow
(①②③ story loop, or `/cicd-quick-dev` for small fixes) picks up afterward. This command writes
**no product code** — its output is evidence, not patches.

## Step 0 — Resolve the target project (FIRST — before anything else)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override (remainder = the area under test) → `.agents/active-project.txt` → else **STOP and ask** — never
guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`
before any work.

## Step 1 — Boot the dev environment
1. Load `PROJECT_ROOT/_bmad-output/active-context/active-context.md` and give a 3-line context summary.
2. Reap stale dev processes (node / python / uvicorn). `taskkill` is prompt-gated per call — that is
   intentional; confirm each kill. Sleep ~5s after killing so ports leave `TIME_WAIT`.
3. Start BOTH servers as **background processes** (the log stream must stay readable across turns —
   a foreground uvicorn blocks and defeats the whole command):
   - Backend, from `PROJECT_ROOT`: `"$VENV"/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
     — resolve `VENV` first, it differs per machine: `VENV=backend/.venv/bin; [ -d "$VENV" ] || VENV=backend/.venv/Scripts`
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
- **Suggested lane** — `/cicd-quick-dev` (small/contained) or the full ①②③ story loop (risky/cross-cutting)

## Step 3.5 — Trace each bug back to the ticket that shipped it (SCC-54)
This is the one command that flies the running app, so it is the one that finds bugs nobody has
noticed yet — and the board should say so. For each bug doc, take the paths from its **Proposed fix
direction** (a `file:LINE` gives the far stronger signal) and run:

```bash
python3 .agents/scripts/jira_feed.py trace --project <PROJECT> --path <file>:<line> [--path ...]
```

It reads git history only — **no board write, ever** — and prints ranked candidates, blame first.

**Then STOP and show the operator.** `trace` answers *"which ticket last touched this line"*, which
is not *"which ticket introduced this bug"*: a later unrelated edit takes the blame outright, and a
wrong flip pulls an innocent ticket out of `Done`. **Never pass a traced key to `flag` yourself.** On
the operator's word — and only then:

```bash
python3 .agents/scripts/jira_feed.py flag --key <KEY> --reason "<one sentence>" \
        --evidence "<log line / status / repro>" --found-by "/cicd-live-testing-team <date>" --apply
```

That flips `Story|Task -> Bug`, brings it back out of `Done`, and posts the reason. Close-out clears
it later — see `.agents/rules/jira.md`. If no candidate is proposed, say so and move on; a bug with
no traceable ticket is new work, not a reopen.

## Step 4 — Close out
Post a session summary table (bug → doc link → **traced ticket, if any** → suggested lane). Ask whether to keep or kill the
servers. Remove every temporary debug log you added. The fixes themselves happen in the sudo dev
flow — never in this chat.

Optional additional input (area under test / known-flaky route): $ARGUMENTS
