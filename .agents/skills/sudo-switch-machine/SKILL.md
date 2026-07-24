---
name: sudo-switch-machine
description: 'Machine handoff for a sprint worked across desktop/laptop/mobile. PARK before closing a lid — commit + sync + push every story worktree branch and both repos, then write a resume card. RESUME on arrival — fetch, re-create the worktrees the new machine cannot see, report what is live. Never lands anything on main_debug. Use when the user says "switching machines" / "parking" / "I am on the laptop now" / "sudo switch machine".'
---

# /sudo-switch-machine — command center launcher

Machine handoff for work that spans desktop, laptop, and mobile. Git branches travel between machines;
**git worktrees do not** — `.claude/worktrees/` is machine-local and not in the repo, so on a second machine
`git worktree list` shows nothing and every `sudo-` step misreads that as "fresh start." This command parks
the work so it survives the trip, and restores the surface on arrival.

Operates on BOTH the lobby and the active child project under `Projects/`.

**Execute now:** read `.agents/commands/sudo-switch-machine.md` (relative to the repo root) and follow it
END TO END. Its **Step 0** resolves the child project from `.agents/active-project.txt`; **Step 1** picks
PARK vs RESUME (from `$ARGUMENTS`, else auto-detect, else ask).

Run it as `/sudo-switch-machine park` before closing a lid, `/sudo-switch-machine resume` after opening one.

**Boundary:** this never pushes a story branch onto `main_debug`. Landing a story stays
`/sudo-update-sprint-memory` Step 7, after `/sudo-code-review` turns it green.
