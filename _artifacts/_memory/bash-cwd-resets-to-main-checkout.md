---
name: bash-cwd-resets-to-main-checkout
description: "The Bash tool RESETS cwd to the primary working directory (the MAIN checkout) whenever a command cd's outside the workspace root — /tmp, the scratchpad, another repo. Every relative path afterwards silently reads MAIN instead of the worktree you are working in, and both files exist, so nothing errors."
metadata:
  node_type: memory
  type: feedback
---

**The mechanism.** Bash cwd persists between calls *until* a command `cd`s outside the
workspace root (`/tmp`, the session scratchpad, a sibling repo). The harness then resets cwd
to the **primary working directory** — for this system that is the MAIN checkout
`/Users/sudohatter/Sudo_Hatter_Command`, never the worktree. It prints
`Shell cwd was reset to …`, one line, easy to read past.

⛔ **Why it is silent and expensive.** When you work in a worktree, the same relative path
exists in BOTH trees and both are valid git repos. `sed -n '325,348p' .agents/scripts/tests/x.py`
does not error — it answers about MAIN's copy. Confirmed twice on SCC-164:

- **Part 3** — `mutation_sweep.py` was WRITTEN into the main checkout after a `cd` into the
  scratchpad. Caught only by diffing `git -C <main> status` against `git -C <worktree> status`.
- **Part 4** — a file read as "the lane's" was main's 333-line copy while the lane's was 463.
  The tell was an arithmetic one: 333 + 130 (the part's own additions) = 463.

**How to apply.** In any worktree lane, treat relative paths as unusable:

1. **Absolute paths for every file read/write**, and `git -C <abs>` for every git call — the
   rule [[nothing-guards-the-merge-target]] already imposes on git, extended to file I/O.
2. Never end a command in a foreign directory. Prefer `git -C /abs/worktree worktree add …`
   over `cd /tmp && …`; if you must cd out, assume cwd is gone afterwards.
3. **Cross-check by size, not by belief.** `wc -l` the file in BOTH trees before trusting a
   structural read of it. A stale copy answers every question plausibly.

Related: [[preflight-resolves-repo-from-cwd]] (the same class, one layer up — a script that
resolves its repo from CWD reported on the wrong branch) · [[nothing-guards-the-merge-target]].
