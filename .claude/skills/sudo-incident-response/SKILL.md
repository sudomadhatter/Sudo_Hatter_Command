---
name: sudo-incident-response
description: 'Command center → child project. Drill a project''s incident-triage runbook against a Sentry issue (interactive lane) — the TEST HARNESS for the 16.1 runbook, not the product. Use when the user says "run the incident drill" / "sudo incident response" from the command center.'
---

# /sudo-incident-response — command center launcher (incident drill)

Command-center (lobby) entry point for the **incident triage drill**. It runs a project's canonical triage
runbook (`.github/claude/incident-triage.md`) against a Sentry issue, in the **interactive lane**, inside a
CHILD project under `Projects/` (e.g. `AGY_AVIATIONCHAT`), never the lobby. This is the interactive drill —
NOT the always-live headless GitHub Actions lane (Story 16.2).

**Execute now:** read `.agents/commands/sudo-incident-response.md` (relative to the repo root) and follow it
END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name, else the
`.agents/active-project.txt` pointer, else it asks which project — then loads that project's runbook and
executes it verbatim, writing ONLY the report under that project's root. Pass `$ARGUMENTS` through verbatim;
the leading token may name the project, the remainder is the issue id / `latest`, e.g.
`AGY_AVIATIONCHAT latest` or `AGY_AVIATIONCHAT 7607174913`.
