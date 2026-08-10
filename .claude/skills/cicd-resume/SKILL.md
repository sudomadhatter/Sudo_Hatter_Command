---
name: cicd-resume
description: 'Pick the sprint back up on a machine you just switched to — fetch both repos, find the live story branches on origin (NOT via git worktree list, which shows nothing on a fresh machine), re-create the worktree or check the branch out, then hand off to /cicd-boot-sprint-memory. Pairs with /cicd-park. Use when the user says "resume" / "I am on the laptop now" / "picking back up on this machine".'
---

# /cicd-resume — command center launcher

The **arriving** half of the machine handoff. On a machine you just switched to, `git worktree list` shows
only the main checkout — worktrees are machine-local — and every `cicd-` step misreads that as "fresh
start." This restores the working surface from what is actually on origin, so no story gets re-done.

It creates; it never deletes. The worktrees on the other machine stay put, and both machines end up on the
same branch — that is the intended end state.

Operates on BOTH the lobby and the active child project under `Projects/`.

**Execute now:** read `.agents/commands/cicd-resume.md` (relative to the repo root) and follow it END TO
END. Its **Step 0** resolves the child project from `.agents/active-project.txt`.

**Boundary:** this restores the **git surface** only. `/cicd-boot-sprint-memory` loads the **sprint
context** and picks the next story — different job, run it after.
