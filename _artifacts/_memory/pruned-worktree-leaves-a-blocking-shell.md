---
name: pruned-worktree-leaves-a-blocking-shell
description: "A pruned story worktree survives as an EMPTY dir shell that blocks `git worktree add` and resists rm -rf; the branch lives on at origin with ① already complete."
metadata: 
  node_type: memory
  type: project
  originSessionId: 223472e4-73d3-4994-b640-80d8f82fe568
  modified: 2026-07-30T13:28:00.491Z
---

Closing a story worktree (`/sudo-close-workingtree`, or another session's close-out sweep)
can leave `.claude/worktrees/<slug>/` behind as an **empty directory tree** — no `.git` file,
no tracked content, just hollow `backend/`/`frontend/` shells. Meanwhile the branch is
**alive on origin** with the story's work committed.

Two failure modes, both hit on AGY 21.4 (2026-07-30):

1. **`git worktree list` shows nothing** — so it looks like ① was never run. Check
   `git branch -a --list "*<story-id>*"` and the story's own `sprint-status.yaml` row
   BEFORE re-doing any work. The row records `① COMPLETE … on worktree branch …`.
   (Same class of trap as [[landing-is-not-closeout]] and
   [[sprint-dependency-map-recommends-stale-work]].)
2. **`git worktree add` fails `fatal: '<path>' already exists`** and `rm -rf` fails
   `Device or resource busy` on the top dir (a stale Windows handle). Bash cannot clear it.
   `Remove-Item -Recurse -Force` from PowerShell does, in one call.

**Why:** the prune deletes files but the directory node survives with an OS handle on it;
git refuses to check out over a non-empty path.

**How to apply:** on any `/sudo-*` step that opens a worktree — `git fetch`, then
`git branch -a` + the board row first. If the branch exists, **re-enter it, never re-author**.
If the path is occupied, clear it with PowerShell `Remove-Item -Recurse -Force`, then
`git worktree add <path> <existing-branch>`, then re-copy the gitignored assets per
[[worktrees-do-not-inherit-gitignored-assets]] — for the emulator tier that list also
includes a junction to `firebase/tests/node_modules` (the pinned Java-17-compatible
firebase-tools; a bare `npx firebase-tools` pulls a build that demands Java 21+ and dies).
