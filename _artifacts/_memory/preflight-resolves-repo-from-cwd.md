---
name: preflight-resolves-repo-from-cwd
description: "task_preflight/closeout_preflight resolve the repo by walking up from cwd and default --branch to that HEAD, so a close-out can print a fully honest \"clear to merge\" verdict about SOMEONE ELSE'S branch."
metadata: 
  probe: "test -e .agents/rules/worktree-per-story.md"
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
SCC-59 is converting that command to a skill. See `.agents/rules/worktree-per-story.md` (it forbids chore worktrees).

## ⛔ Passing both flags is NOT enough — `--repo` must be the WORKTREE (2026-08-15, AVCH-59)

I passed `--repo` and `--branch` and `--expect-key`, all correct, and still got a **false
`VERDICT: BLOCKED`** at close-out. `--repo` named the repo's **main checkout**; the lane lives in a
worktree. The preflight then split its answers across two trees:

- **ref-based checks read the BRANCH and were right** — `base` (9 ahead, origin/main absorbed),
  `scope`, `landing`, `intent`, `branch`.
- **file-based checks read the WORKING TREE and were wrong** — `manifest` warned "no task.yaml
  declares AVCH-59" (it is in the worktree), `artifacts` listed two *other* lanes' walkthroughs,
  `gate` concluded "foreign evidence never gates this lane", and `sync` raised an ERROR for an
  unrelated uncommitted file that belonged to a different piece of work entirely.

Nothing in the output says which tree it read, so the report looks internally consistent and the
error looks like the lane's. **Point `--repo` at the tree where the branch is checked out** — the
worktree path is a legitimate `--show-toplevel` — and re-read: the same call went to
`0 error(s)`, `clear to close out and merge`.

**And the dirt was not mine.** The main checkout carried an uncommitted `README.md`; it belonged to
another lane. A wrong `--repo` makes another session's dirty tree look like your blocker — and the
temptation is to "clean it up". Don't: park or leave it, exactly as the memory-store rule says
([[commit-and-push-are-one-action]] is about YOUR work, not someone else's).

**Also: cwd persists across Bash calls.** A `cd` I ran to inspect the submodule made the very next
`python3 .agents/scripts/…` resolve against AGY and die on a missing file. Use absolute script
paths and `git -C` on every call — [[nothing-guards-the-merge-target]] is the same failure class
with a worse ending.

## ⛔ `closeout_preflight --project <name>` reads the SHARED CHECKOUT even with `--worktree` (2026-08-27, AVCH-36)

On a story lane, `--project AGY_AVIATIONCHAT` + `--worktree <path>` + correct `--branch/--expect-key`
still answered every file-based row from the checkout parked on `main`: story status "deferred",
"no walkthrough.md found", "gates: no receipt" — all three existed on the branch — and its `landed`
rows compare against **main**, while a story lane lands on the **epic branch**. `--worktree` only
adds a sync row; there is no landing-ref flag. So on an epic-lane story, expected-noise extends past
the documented `landed` row: `story`/`artifacts`/`gates` rows are checkout reads, verify each
directly on the branch (`walkthrough_roster.py --gate`, `gate_receipt.py` stamp, story frontmatter)
before believing a BLOCKED. Same family: `story_status.py set --project <name>` wrote the flip to
the checkout on 19.1 (reverted; pass the WORKTREE PATH as `--project` — that form works for
story_status and did flip both surfaces correctly on 19.4).
