---
name: grep-reads-the-branch-you-are-parked-on
description: "A repo checkout sitting on a stale branch reports stale file content to EVERY search tool, and no grep result names the commit it read — scope derived this way is fiction."
metadata: 
  probe: "test -e docs/migrations"
  node_type: memory
  type: reference
  originSessionId: 960c30f6-ee99-40cd-a99b-1a6860271651
  modified: 2026-08-15T17:21:38.342Z
---

A shared checkout parked on a long-lived branch (an `epic/*`, a lane you forgot you were on)
returns **that branch's** file content to `grep`, `find`, Read, and every agent search. Nothing in
the output says which commit it came from, so the results look identical to ground truth.

**2026-08-15, AVCH-58.** Swept AGY for dead migration kit references (`docs/migrations/`, relocated from `_my_resources/` under SCC-89) from the main
checkout, which sat on `epic/AVCH-18-adk-2x-runtime` — 11 commits behind `main`. Found 5 files and
wrote a whole ticket around them, headlining a "broken secrets path that strands a fresh machine."
Re-running the identical sweep inside a worktree cut from `main` returned a different set: **AVCH-53
had already fixed 3 of them**, two more were historical records quoting old paths as data, and the
real remainder was **one line**. The ticket had to be re-summarised and re-described before any edit
landed.

**Same trap one layer up:** local `main` itself was 4 commits behind `origin/main`. The first
blast-radius derivation compared against local `main` and reported "0 files landed while you built"
— also false. `/smh-code-review` Step 0.7 exists for exactly this and caught it.

⛔ **2026-08-15, third strike, and this one was INSIDE the review.** `/smh-code-review` Step 0.5 uses
`git diff --name-only main...HEAD`. The three-dot form resolves the merge-base against **local**
`main` — 4 commits behind `origin/main` — so it reported **12 files, four of which the lane never
touched**: other lanes' landed work, presented as this diff. Against `origin/main` the true diff was
**8**. A lane cut with `worktree add … origin/main` is *especially* exposed, because its base is
ahead of the local ref every later command silently compares to. **Use `origin/main...HEAD` for any
diff you will reason about**, and treat a bare `main` in any command as a stale ref until proven.

⚠️ Same session, adjacent trap: `git worktree add <path> -b <branch> origin/main` sets the new
branch's **upstream to `origin/main`**. `push.default=simple` refuses on the name mismatch, so it is
not a live round — but the safety net is a *global config value*, and in a repo with no `pre-push`
hook nothing else is looking. `git branch --unset-upstream` immediately, then `push -u` on the first
push.

**How to apply:** before deriving scope from a search, echo what you are reading —
`git -C <repo> rev-parse --abbrev-ref HEAD` and `git -C <repo> rev-list --count origin/main..main`.
Sweep inside a worktree cut from `main`, or fetch and compare against `origin/main`, never against a
local ref you have not just refreshed. Treat a scope derived from an unverified checkout as a draft.

Related: [[grep-skips-gitignored-projects]] · [[preflight-resolves-repo-from-cwd]] ·
[[check-maps-stale-is-false-in-worktrees]] · [[recon-reframes-story-scope]]
