---
name: worktree-remove-force-eats-untracked-memories
description: git worktree remove --force deletes UNTRACKED files reached through the worktree — a memory written this session but not yet committed is gone; write memories on the lane and commit them BEFORE the prune.
metadata:
  probe: "test -e _artifacts/_memory"
  type: project
---

Measured twice in one close-out (SCC-351, 2026-08-30): a memory file written during the session
into `_artifacts/_memory/` was deleted by `git worktree remove --force`, both times, silently. All
135 TRACKED memory files survived — only the new untracked one was eaten. `link-worktree-assets.py
--unlink` does not cover the memory store, so its "3 unlinked, 0 remaining. Safe to remove" is not
a promise about untracked files reached through the tree.

**Why:** the memory store is a symlink from `~/.claude/projects/<slug>/memory` to the repo's
`_artifacts/_memory/`, so a memory written mid-session lands in the shared checkout as an UNTRACKED
file — exactly the class `--force` is defined to discard.

**How to apply:** write session memories INTO THE LANE worktree and commit them there before the
close-out reaches the prune step (that is already the preflight's authorship rule — this is why it
matters). If a memory is written after the merge, re-create it after the prune and verify it exists
(`ls`), because the prune will have taken it. Never read `--unlink`'s success line as covering
untracked work. Related: [[portable-memory-store-dot-slug-trap]],
[[worktrees-do-not-inherit-gitignored-assets]], [[story-worktree-prune-can-orphan-step1]].
