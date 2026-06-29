---
name: sudo-code-review
description: 'Command center → child project. Review + gate a story — adversarial code review, then the test gate (suite + TEA trace + nfr + test-review) producing a PASS/CONCERNS/FAIL/WAIVED verdict. Step ③ of the sudo dev flow. Use when the user says "review the story" / "sudo code review" from the command center.'
---

# /sudo-code-review — command center launcher (③)

Command-center (lobby) entry point for **step ③** of the sudo dev flow. It reviews + gates a story inside
a CHILD project under `Projects/` (e.g. `AGY_AVIATIONCHAT`), never the lobby.

**Execute now:** read `.agents/commands/sudo-code-review.md` (relative to the repo root) and follow it END
TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name, else the
`_my_resources/active-project.txt` pointer, else it asks Daniel — then runs the review, the test gate, and
writes the verdict under that project's root only. Pass `$ARGUMENTS` through verbatim; the leading token
may name the project, e.g. `AGY_AVIATIONCHAT 11.16`.
