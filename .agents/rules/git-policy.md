---
name: git-policy
description: "Git default: NEVER run commit/push yourself — hand Daniel the exact command. Only commit/push when Daniel explicitly delegates that specific action; then commit your OWN files via explicit paths, never git add -A."
---

# Git Policy

> The single, canonical git rule for the whole workspace. Supersedes the older "commit at story
> close-out" stance — there is only one policy now: **you hand Daniel the command** unless he
> explicitly delegates a specific commit/push to you.

## Branch model — `main_debug` → `main` (THE dev standard)

> The one source of truth for the branch model. Every workspace (home base + every project) uses it;
> per-workspace `AGENTS.md` GATES sections point here rather than restating it.

- **`main` is LIVE PRODUCTION — never work on it, never auto-target it.** It stays deployable.
- **All day-to-day work flows through `main_debug`** (the shared integration branch): a `claude/*`
  session branch → PR → **`main_debug`**. This is the "one place to send everything."
- **Promotion `main_debug` → `main` is Daniel's deliberate, manual decision** — done only when he is
  happy and confident it won't break production. An agent never promotes to `main` on its own.

### Write-approval gate — free on your OWN branch; the button on the owner's
The gate keys on **where a write lands**, not the act of pushing:
- **FREE:** push freely to your own `claude/*` session branch (loops/retries fine); open/update PRs.
- **APPROVAL (per-action, never carries forward):** any write to an **owner branch** —
  `main_debug` or `main` — i.e. a direct `git push` to either, or merging a PR into them. `main` is
  **extra-protected**: never push/PR/merge to it directly; reach it only via the manual promotion above.
- **Enforcement:** the `require-push-approval.py` PreToolUse hook (canonical source `.agents/hooks/`,
  deployed to every `.claude/hooks/` by `/sync-agents`) forces the approval prompt on any `git push`
  targeting `main_debug`/`main` however it's wrapped; `merge_pull_request` (+ GitHub write tools) is
  gated in `.claude/settings.json`. Approve a merge into `main_debug` by invoking `/merge_main_debug` —
  invoking it IS the per-action approval.

## Default — you do NOT run git

**Never run `git commit` or `git push` yourself.** Instead, the `walkthrough.md` "Your Actions"
section hands Daniel the exact command(s) to run. This holds at every stage — mid-work AND at
close-out. The record of the command exists whether Daniel runs it or (by exception) delegates it.

> **Web/mobile sessions are the exception.** On a phone there is no terminal to paste into, so the
> `mobile-mode.md` lane takes over: the agent commits/pushes its own files (same safe-commit mechanics
> below) and **asks before opening a PR**. See `mobile-mode.md` → Override 1.

This pairs with the plan-first gate: no project-file edits without an approved `implementation_plan.md`
(see `artifacts-always-first`), and "done" is earned, not implied (see `completion-not-illusion`).

## The only exception — Daniel explicitly delegates

If Daniel explicitly tells you to run a specific commit or push in that moment ("go ahead and commit
this", "you push it"), you may — for that action only. A standing approval does NOT carry to the next
commit; each delegation is one-time. When delegated, follow the safe-commit mechanics below.

## Sync-first — always check the remote before you commit (or recommend the commit)

Phone and desktop share branches, so a commit made on a **stale** branch is what causes the
diverge → rejected-push tangle. Before you produce the "Your Actions" commit recommendation (desktop)
**or** commit/push yourself (mobile / delegated), ALWAYS check the remote first:

1. **Fetch and compare:** `git fetch origin <branch>`, then check whether the local branch is behind
   origin (e.g. `git status -sb` shows `behind`, or `git rev-list --count <branch>..origin/<branch>` > 0).
2. **If behind, lead with the pull.** The recommended command block (or your own sequence) MUST start
   with `git pull --ff-only origin <branch>` *before* `git add`/`commit`/`push`, so neither machine ever
   commits on top of a stale branch.
3. **If the branches have DIVERGED** (a fast-forward pull isn't possible), **STOP and flag it** — hand
   Daniel the situation. Do NOT recommend or run a blind merge/rebase, and never force-push.

This is the written form of the desktop habit "pull before you work": the agent checks for you and
bakes the pull into the recommendation whenever the branch is behind.

## Safe-commit mechanics (apply ONLY when delegated)

- **Commit your OWN work via explicit paths:** `git add path/one path/two …`.
- **NEVER `git add -A`, `git add .`, or `git add -u`** — they sweep other parallel work (other
  agents/teams, or Daniel's own uncommitted changes) into your commit. This is the most important rule.
- **Verify the staged set first:** `git diff --cached --stat` must show ONLY your files. If anything
  else appears, unstage it (`git restore --staged <path>`) before committing.
- **Scope the commit message** to your task/story only.
- **Push only if the push was also delegated** — it is a distinct outward action needing its own
  go-ahead. Push your work as its own commit; never bundle other work.
- **If a push is rejected** (remote moved under you), **STOP and report.** Do not force-push, and do
  not blind-rebase while other uncommitted work sits in the tree.

## Always

- **Check the remote first** (Sync-first above) — the "Your Actions" command block leads with
  `git pull --ff-only` whenever the branch is behind, before add/commit/push.
- The `walkthrough.md` "Your Actions" documents the exact `git add` (explicit paths) + `commit` +
  `push` commands either way — so the record exists whether Daniel or (by delegation) you run them.
