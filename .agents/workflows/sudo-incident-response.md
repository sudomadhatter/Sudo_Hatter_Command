---
description: Drill harness that executes a project's incident-triage runbook against a Sentry issue. The TEST HARNESS for Story 16.1's runbook — not the product. Interactive drill lane.
platforms: [opencode, antigravity, codex]
---

# /sudo-incident-response — Incident Triage Drill Harness

Thin harness. Its **entire job** is to execute a project's canonical triage runbook
(`.github/claude/incident-triage.md`) against a Sentry issue, in the **interactive lane**, and drop the
report in that project's artifacts. It exists **solely to run/drill the runbook** — the runbook is the
product; this command is the test harness (Story 16.1, AC-8). The always-live headless lane is Story 16.2.

> This is NOT a debugging skill of its own. It carries **no triage logic** — all of that lives in the
> runbook. If the runbook changes, this command needs no edit.

## Step 0 — Resolve the target project (FIRST — before anything else)
Run from the **command center** (the lobby), this operates on exactly ONE child project under `Projects/`,
never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path — check FIRST, STOP here if it matches)** — if this repo has **no**
   `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip to the binding rule. Do NOT
   read `active-project.txt`, parse `$ARGUMENTS` for a project name, or ask which project.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is the
   target; consume that first token (the remainder is the real argument — issue id / `latest`). Write the
   name alone into `.agents/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under `Projects/`,
   use it.
3. **Ask** — else STOP and ask which project we're working in (e.g. AGY_AVIATIONCHAT) — never guess, never
   operate on the lobby.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule:** the runbook, the codebase it reads, and every bare path resolve **under `PROJECT_ROOT`**.

## Step 1 — Load the runbook
Read `PROJECT_ROOT/.github/claude/incident-triage.md`. If it is missing, STOP and say so — this project has
no triage runbook yet (Story 16.1 ships it for AGY_AVIATIONCHAT). Never improvise triage logic in its place.

## Step 2 — Execute the runbook verbatim (interactive lane)
Run the runbook end to end with:
- `ISSUE` = the remaining `$ARGUMENTS` token (a Sentry issue/short id), or **`latest`** if none given.
- `PROJECT` = the runbook's default (`python-fastapi`) unless `$ARGUMENTS` names another slug.
- **Lane = interactive** → Sentry **MCP** transport; GitNexus enrichment when available; honor **every**
  guardrail (read-only; write ONLY the report; never merge/PR/push; anchor at the event's release SHA).

Follow the runbook's five steps and its graceful-degrade rules exactly — this harness adds nothing and
skips nothing.

## Step 3 — Land the report
The runbook writes the interactive-lane report to
`PROJECT_ROOT/_artifacts/debugging/<YYYY-MM-DD>_<issue-slug>/incident-report.md`. Post a **clickable
Markdown link** to it in the chat, plus a one-line summary (what broke · confidence · proposed fix).

## Drill mode (AC-8 acceptance evidence)
To drill: force a P1 first (the Story-11.5 pattern, `PROJECT_ROOT/_test_scripts/sentry_smoke_test.py` → a
fatal `P1_RKP_MANIFEST_FAILURE`), then run `/sudo-incident-response latest`. A **pass** = the human confirms
the report names the planted failure, the correct file, and a sane fix. That human confirmation is the
story's acceptance evidence; record the report path + verdict in the story's Completion Notes.

Optional additional input (issue id / `latest` / project slug): $ARGUMENTS
