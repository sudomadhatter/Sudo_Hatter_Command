---
name: smh-close-task-merge-tree
description: Close out TASK work — a `chore/<JIRA-KEY>-<slug>` branch that never got an epic and a story, so BMAD's `/cicd-update-sprint-memory` cannot close it. Preflights mechanically (branch shape, clean+pushed, main absorbed, and THE LANE — did anything deployable change?), runs the gate the lane selects, then lands it THROUGH A PULL REQUEST: `land_pr.py` pushes the branch, opens the PR and prints the link, and the operator's Merge click is the sign-off — a prose-only lane may self-merge, everything else stops and waits. Re-invoked as `--after-merge <KEY>` it files the Jira Dev Record, moves the Task to Done, and prunes the worktree AND the branch (SCC-62 — unlink assets before removing the tree; a recursive delete through a junction eats the shared targets). The local token push is kept as break-glass only. Refuses the moment a deployable path is in the diff and hands the work to `/cicd-push-e2e`.
---

# Close Task Merge Tree

Native skill entry point for the non-BMAD Task close-out. The workflow body stays in one canonical file
so its safety gates cannot drift between command surfaces.

**Execute now:** read `.agents/commands/smh-close-task-merge-tree.md` relative to the repository root and
follow it **END TO END**, passing the user's arguments through verbatim. Invoking this skill is the
operator's per-merge sign-off exactly as defined by that command. If the command file is absent, STOP and
report the missing canonical workflow; never reconstruct the close-out from memory.
