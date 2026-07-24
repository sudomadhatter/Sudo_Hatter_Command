---
name: sudo-park
description: 'Park the session before switching machines — commit (explicit paths) + sync + push every story worktree branch and both repos, then write a resume card. Branches travel between machines, git worktrees do not, so anything unpushed is stranded. Never lands anything on main_debug. Pairs with /sudo-resume. Use when the user says "park" / "I am switching machines" / "leaving this machine" / "heading out".'
---

# /sudo-park — command center launcher

The **leaving** half of the machine handoff. Daniel works one sprint across desktop, laptop, and mobile.
Git branches travel between machines; **git worktrees do not** — `.claude/worktrees/` is machine-local and
not in the repo, so anything not pushed is stranded on the box he walks away from.

Operates on BOTH the lobby and the active child project under `Projects/`.

**Execute now:** read `.agents/commands/sudo-park.md` (relative to the repo root) and follow it END TO END.
Its **Step 0** resolves the child project from `.agents/active-project.txt`.

**Boundary:** this never pushes a story branch onto `main_debug`. Landing a story stays
`/sudo-update-sprint-memory` Step 7, after `/sudo-code-review` turns it green — a story mid-flight carries
deliberately RED tests.

Pick the work back up on the other machine with `/sudo-resume`.
