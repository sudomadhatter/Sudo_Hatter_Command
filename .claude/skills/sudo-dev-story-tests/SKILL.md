---
name: sudo-dev-story-tests
description: 'Command center → child project. Develop a story test-first — plan, auto self-audit the plan, implement, then auto-expand coverage. Step ② of the sudo dev flow. Use when the user says "dev the story" / "sudo dev story" from the command center.'
---

# /sudo-dev-story-tests — command center launcher (②)

Command-center (lobby) entry point for **step ②** of the sudo dev flow. It runs against a CHILD project
under `Projects/` (e.g. `AGY_AVIATIONCHAT`), never the lobby.

**Execute now:** read `.agents/commands/sudo-dev-story-tests.md` (relative to the repo root) and follow it
END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name, else the
`_my_resources/active-project.txt` pointer, else it asks Daniel — then binds every path (and every nested
`bmad-*` skill's `{project-root}`) under that project's root. Pass `$ARGUMENTS` through verbatim; the
leading token may name the project, e.g. `AGY_AVIATIONCHAT 11.16`.
