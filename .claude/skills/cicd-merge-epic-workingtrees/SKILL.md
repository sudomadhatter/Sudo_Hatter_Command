---
name: cicd-merge-epic-workingtrees
description: 'Command center → child project. One-shot close-out for ALL of an epic''s live story worktrees — read every tree, check each story, fix/merge in dependency order with per-lane test gates, land on the epic branch, flip each story to done, run the combined gate, then prune every tree and branch (the epic branch itself merges to main later via /cicd-push-e2e). Use when the user says "merge the worktrees" / "close out all the lanes" / "sudo merge epic workingtrees", or when /cicd-close-story-merge-tree meets multiple live worktrees.'
---

# /cicd-merge-epic-workingtrees — Command Center Launcher

Command-center (lobby) entry point for reconciling and landing several parallel story worktrees as one set.

**Execute now:** read `.agents/commands/cicd-merge-epic-workingtrees.md` (relative to the repo root) and follow it END TO END.
