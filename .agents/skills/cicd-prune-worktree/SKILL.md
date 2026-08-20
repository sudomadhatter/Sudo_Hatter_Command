---
name: cicd-prune-worktree
description: 'Command center → child project. The story lane''s DISK UTILITY — it moves no code. Verify a story branch has already been merged into its epic branch, prune its local git worktree, and delete both local and remote (GitHub) branches. Called by /cicd-close-story-merge-tree and /cicd-merge-epic-workingtrees; type it yourself only when a cleanup was skipped or failed. Use when the user says "prune the worktree" / "clean up that tree".'
---

# /cicd-prune-worktree — Command Center Launcher

Command-center (lobby) entry point for verifying and pruning merged story worktrees and git branches.
It **moves no code**: it confirms a landing that already happened, preserves anything uncommitted, unlinks the
shared assets, removes the tree, and only then deletes branches.

**Execute now:** read `.agents/commands/cicd-prune-worktree.md` (relative to the repo root) and follow it END TO END.
