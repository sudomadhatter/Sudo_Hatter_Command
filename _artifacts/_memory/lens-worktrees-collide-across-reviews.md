---
name: lens-worktrees-collide-across-reviews
description: "Review lens worktrees reuse lens-* names across reviews and across REPOS, so a new fan-out silently reads a stale tree at the wrong sha unless the SCC-313 probe is run."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 42287b1f-0feb-472a-9487-a63859121077
  modified: 2026-08-31T23:45:09.980Z
---

`code-review-engine` cuts a worktree per repo-reading lens. Everyone names them `lens-<name>` in the
session scratchpad, so **the next review's `git worktree add` fails with `already exists`** — and if
that failure is swallowed (`&& echo`, `>/dev/null 2>&1`), the lens is handed a directory that looks
right and is a **different repo at a different sha**.

Measured 2026-08-31 on SCC-358: three of four intended lens trees were leftovers from the AVCH-111
review — sha `449fa4f4`, no `.agents/commands/` at all, because they were **AviationChat** worktrees
sitting in the lobby's scratchpad. `git rev-parse --show-toplevel` named the right directory while
`git rev-parse HEAD` named the wrong sha. Unchecked, three of five lenses would have reviewed the
wrong repository while the roster recorded `lens_isolation: worktree`.

**Why:** a stale worktree still belongs to whichever repo created it, and that repo may be a
submodule — so the lobby's `git worktree list` does not show it, and `git worktree prune` will not
remove a directory that still exists. Eleven had accumulated across AVCH-101/111 reviews.

**How to apply:** name lens trees with the ticket key (`scc358-lens-edge`), and **always run the
SCC-313 verification probe before launching** — from inside each tree, `git rev-parse --show-toplevel`
AND `git rev-parse --short HEAD` AND one grep proving the tree actually carries the change under
review. A toplevel check alone passes on a stale tree. Remove them at close-out with
`git worktree remove` **from the owning repo** (check `git status --porcelain` is empty first —
[[worktree-remove-force-eats-untracked-memories]]).

Related: [[bash-cwd-resets-to-main-checkout]] · [[pruned-worktree-leaves-a-blocking-shell]] ·
[[exercise-the-real-cicd-doors]]
