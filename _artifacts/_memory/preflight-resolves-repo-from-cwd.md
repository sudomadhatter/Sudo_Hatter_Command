---
name: preflight-resolves-repo-from-cwd
description: "task_preflight/closeout_preflight resolve the repo by walking up from cwd and default --branch to that HEAD, so a close-out can print a fully honest \"clear to merge\" verdict about SOMEONE ELSE'S branch."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f3e01c24-9b74-4562-ba18-4cc66697fffd
  modified: 2026-08-09T15:28:37.708Z
---

`task_preflight.py` resolves the repo by walking up from **cwd** looking for `.git`
(`git_root()`, ~line 56-68) and defaults `--branch` to that repo's current HEAD (~line 300).
`closeout_preflight.py` has the same shape. **cwd resets to the main checkout at slash-command
boundaries**, so a close-out invoked from a worktree lane can silently resolve the lobby instead.

2026-08-09, SCC-60: Step 1 printed `== task preflight - chore/SCC-59-update-maps-indexes ==` …
`VERDICT: clear to close out and merge`. Every check was honest — about the wrong branch.
Proceeding would have merged another lane's in-flight work to `main` under my ticket's close-out.

**Why:** the script cannot know which ticket you *meant* to close, so there is no mismatch it
could detect. And `close-task-merge-tree`'s Step 0 asks you to echo `Repo: <name> | Branch:
<branch>` — which I did, **from belief rather than command output**, so the one guard that exists
could not catch the one thing it is for. Same defect class as reading a sandboxed `acli` failure
as board state ([[jira-integration-live]]).

**How to apply:** pass `--repo <path>` **and** `--branch <name>` explicitly whenever a worktree is
in play — that is exactly when cwd and intent diverge. Derive the Step 0 echo from an actual
`git -C <path> rev-parse --abbrev-ref HEAD`, never from memory, and confirm the resolved Jira key
is the ticket you are closing before reading the verdict at all.

The doc fix (Step 0 derives from output + names the expected key; Step 1 asserts key match and
STOPs on mismatch) was scoped 2026-08-09 and **deferred** — so this memory is the only place it
lives. It now belongs in `.agents/skills/close-task-merge-tree/SKILL.md`, not the command file:
SCC-59 is converting that command to a skill. See [[worktree-per-story-forbids-chore-worktrees]].
