---
name: sudo-create-epics-stories-sprint
description: 'Command center → child project. Epic kickoff — create the epic + its stories, generate the sprint board, then interactively risk-score every story P0–P3 (test levels) with Daniel. Phase A, before the per-story dev loop. Use when the user says "create the epics and sprint" / "kick off the epic" / "sudo create epics stories sprint" from the command center.'
---

# /sudo-create-epics-stories-sprint — command center launcher (Phase A / epic kickoff)

Command-center (lobby) entry point that turns a batch of requirements into an epic, its stories, a populated
sprint board, and a Daniel-confirmed P0–P3 risk map — the step BEFORE `/sudo-write-story-tests`. Runs against
a CHILD project under `Projects/`, never the lobby.

**Execute now:** read `.agents/commands/sudo-create-epics-stories-sprint.md` (relative to the repo root) and
follow it END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name,
else the `_my_resources/active-project.txt` pointer, else it asks Daniel — then binds every path under that
project's root. Its **Step 3 is an interactive hard stop**: risk-score each story P0–P3 with Daniel, one at a
time. Pass `$ARGUMENTS` through verbatim; the leading token may name the project, e.g.
`AGY_AVIATIONCHAT _my_resources/open_tasks/fix_list_admin_sudoadmin.md`.
