---
name: sudo-boot-sprint-memory
description: 'Command center → child project. Session boot / BMAD story pick-up — reads a child project''s active-context + sprint-status, surfaces the next story and which sudo- step to run. This is the normal place to set the active project for the session. Use when the user says "boot" / "pick up the sprint" from the command center.'
---

# /sudo-boot-sprint-memory — command center launcher (G1)

Command-center (lobby) entry point for the session boot / story pick-up. It reads a CHILD project under
`Projects/` (e.g. `AGY_AVIATIONCHAT`), never the lobby — and is the normal place to **set the active
project** for the rest of the session.

**Execute now:** read `.agents/commands/sudo-boot-sprint-memory.md` (relative to the repo root) and follow
it END TO END. Its **Step 0** resolves the child — a leading `$ARGUMENTS` project name (which it writes to
the `_my_resources/active-project.txt` pointer so later commands inherit it), else the existing pointer,
else it asks Daniel — then binds every path under that project's root. Run it as
`/sudo-boot-sprint-memory AGY_AVIATIONCHAT` to switch focus to that project.
