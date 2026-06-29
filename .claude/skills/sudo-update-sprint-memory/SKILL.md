---
name: sudo-update-sprint-memory
description: 'Command center → child project. Story close-out save — advance the closed story to done (invoking this IS Daniel''s sign-off; only red tests block), code-verify, route learnings to specs/rules/memory, prune active-context. Run as the LAST step closing a story. Use when the user says "close out" / "save the session" / "sudo update sprint memory".'
---

# /sudo-update-sprint-memory — command center launcher (G1 close-out)

Command-center (lobby) entry point for the end-of-session story close-out. It saves into a CHILD project
under `Projects/` (e.g. `AGY_AVIATIONCHAT`), never the lobby — except Claude auto-memory, which is global.

**Execute now:** read `.agents/commands/sudo-update-sprint-memory.md` (relative to the repo root) and
follow it END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name,
else the `_my_resources/active-project.txt` pointer, else it asks Daniel — then advances the story, routes
learnings, and prunes under that project's root only. Pass `$ARGUMENTS` through verbatim.
