---
name: story-worktree-prune-can-orphan-step1
description: "①'s story+red-tests commit can survive ONLY as a dangling git commit — a story-writing worktree pruned before its lane opened leaves the ticket claiming a story file that no branch carries. Recover with git fsck + cherry-pick onto the current epic tip; never re-run ① blind."
metadata: 
  node_type: memory
  type: project
  originSessionId: 41c26107-190b-4909-8b42-62beb3b11c94
  modified: 2026-08-27T16:58:17.395Z
---

**Measured 2026-08-27, AVCH-36 (story 19.4).** The 08-21 batch story-writing session committed ①'s
output (story file + ATDD reds + board flip) in per-story worktrees. Sibling lanes re-landed theirs
when each lane opened; 19.4's lane never opened, its worktree was pruned, and the commit became
dangling — while the Jira ticket (rendered at mint from that story file) still said "story written".
Nothing in the flow notices a pruned-but-unlanded ① worktree: `git worktree list`, origin branches,
and every ref search come back empty.

**Why:** the ticket description is minted FROM the story file at ① (`jira_feed.py mint`), so the
board asserts an artifact whose only copy sits in an unreachable commit. `git log --all --grep <KEY>`
finds nothing (no ref); only `git fsck --lost-found` + `git ls-tree` over dangling commits does.

**How to apply:** when a ticket names a story file that exists on no branch, run
`git fsck --lost-found`, then per dangling commit `git ls-tree -r --name-only <sha> | grep <story>`.
Found → cut the story branch off the CURRENT epic tip and `git cherry-pick <sha>` (expect a
sprint-status one-line conflict; resolve to the landed truth). Re-running ① instead silently forks
the story record ([[devrecord-story-slug-forks-the-record]]) and loses the vision-lock decisions.
Related: [[pruned-worktree-leaves-a-blocking-shell]], [[preflight-resolves-repo-from-cwd]].
