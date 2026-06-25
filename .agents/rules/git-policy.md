---
name: git-policy
description: "Git default: NEVER run commit/push yourself — hand Daniel the exact command. Only commit/push when Daniel explicitly delegates that specific action; then commit your OWN files via explicit paths, never git add -A."
---

# Git Policy

> The single, canonical git rule for the whole workspace. Supersedes the older "commit at story
> close-out" stance — there is only one policy now: **you hand Daniel the command** unless he
> explicitly delegates a specific commit/push to you.

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

- The `walkthrough.md` "Your Actions" documents the exact `git add` (explicit paths) + `commit` +
  `push` commands either way — so the record exists whether Daniel or (by delegation) you run them.
