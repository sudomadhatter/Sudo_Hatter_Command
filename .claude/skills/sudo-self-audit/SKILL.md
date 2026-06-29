---
name: sudo-self-audit
description: 'Command center → child project. Pre-dev plan/story audit — pressure-tests an implementation_plan.md or story against the codebase and ACs to catch gaps, over-engineering, and contract breaks BEFORE coding. Auto-invoked by /sudo-dev-story-tests; also runnable standalone. Use when the user says "audit the plan" / "sudo self audit".'
---

# /sudo-self-audit — command center launcher

Command-center (lobby) entry point for the pre-dev adversarial plan audit. It operates on a plan/story
inside a CHILD project under `Projects/` (e.g. `AGY_AVIATIONCHAT`), never the lobby.

**Execute now:** read `.agents/commands/sudo-self-audit.md` (relative to the repo root) and follow it END
TO END. Its **Step 0** resolves which child to target — a leading `$ARGUMENTS` project name, else the
`_my_resources/active-project.txt` pointer (already set when `/sudo-dev-story-tests` auto-invokes this),
else it asks Daniel — then traces the plan against that project's codebase only. Pass `$ARGUMENTS` through
verbatim.
