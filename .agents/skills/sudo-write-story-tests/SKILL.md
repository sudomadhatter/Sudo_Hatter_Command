---
name: sudo-write-story-tests
description: 'Command center → child project. Story prep — create the next BMAD story, then write its failing acceptance tests (ATDD red phase) before any code. Step ① of the sudo dev flow. Use when the user says "write the story" / "sudo write story" from the command center.'
---

# /sudo-write-story-tests — command center launcher (①)

Command-center (lobby) entry point for **step ①** of the sudo dev flow. It runs against a CHILD project
under `Projects/` (e.g. `AGY_AVIATIONCHAT`), never the lobby.

**Execute now:** read `.agents/commands/sudo-write-story-tests.md` (relative to the repo root) and follow
it END TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name, else
the `_my_resources/active-project.txt` pointer, else it asks Daniel — then binds every path under that
project's root (config, stories, tests, artifacts). Pass `$ARGUMENTS` through verbatim; the leading token
may name the project, e.g. `AGY_AVIATIONCHAT 11.16`.
