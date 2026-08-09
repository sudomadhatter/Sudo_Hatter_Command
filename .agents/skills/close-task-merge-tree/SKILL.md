---
name: close-task-merge-tree
description: 'Close out non-BMAD Task work on a chore/JIRA-KEY-slug branch: mechanically preflight the lane, run its gate, merge to main with --no-ff, file the Jira Dev Record, move the Task to Done, and prune the branch. Invoking this skill is the operator merge sign-off. Use when the user says "close this Task branch", "close-task-merge-tree", or asks to merge and prune a chore branch.'
---

# Close Task Merge Tree

Native skill entry point for the non-BMAD Task close-out. The workflow body stays in one canonical file
so its safety gates cannot drift between command surfaces.

**Execute now:** read `.agents/commands/close-task-merge-tree.md` relative to the repository root and
follow it **END TO END**, passing the user's arguments through verbatim. Invoking this skill is the
operator's per-merge sign-off exactly as defined by that command. If the command file is absent, STOP and
report the missing canonical workflow; never reconstruct the close-out from memory.
