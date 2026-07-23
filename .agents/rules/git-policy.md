---
name: git-policy
description: "Git policy: story/dev work happens in its own git worktree on a `claude/*` branch, where the agent commits FREELY (explicit paths — never `git add -A`). The story lands on `main_debug` as ONE clean push, either on Daniel's in-the-moment 'approved' or via /sudo-update-sprint-memory. `main` is reached only when Daniel asks directly or runs /sudo-push-e2e."
---

# Git Policy

> The single, canonical git rule for the whole workspace. **Agents commit and push their own work now.**
> This supersedes the old "never run git yourself — hand Daniel the command" default, which is gone:
> that default is what produced commits carrying four unrelated sessions at once.

## Branch model — `main_debug` → `main` (THE dev standard)

> The one source of truth for the branch model. Every workspace (home base + every project) uses it;
> per-workspace `AGENTS.md` GATES sections point here rather than restating it.

- **`main` is LIVE PRODUCTION — never work on it, never auto-target it, never branch a worktree from
  it.** It stays deployable.
- **All day-to-day work flows through `main_debug`** (the shared integration branch): a story worktree
  on a `claude/*` branch → lands on **`main_debug`**. This is the "one place to send everything."
- **Promotion `main_debug` → `main` is Daniel's deliberate, manual decision** — only when he asks for it
  directly, or via `/sudo-push-e2e`. An agent never promotes to `main` on its own.

## Default — you work in a worktree, and you own git inside it

**Story or dev work opens its own git worktree before the first project file is edited**, branched from
`main_debug`. One story, one worktree, one `claude/*` branch. Inside that worktree the agent commits
its own work freely — that is the entire point of the worktree. Full lifecycle, triggers, and
exemptions → **`worktree-per-story.md`** (protocol tier, loads alongside this rule).

Why: several teams run in parallel against one checkout. Their edits interleave, `git status` becomes a
soup of everybody's work, and whoever pushes last inherits all of it. A worktree per story ends that.

## The write gate — keyed on WHERE a write lands, not on the act

| Destination | Permission |
|---|---|
| Your own `claude/*` branch (commits **and** pushes) | **FREE** — no approval, loops/retries fine |
| `main_debug` | **Daniel's sign-off** — his in-the-moment "approved", or invoking `/sudo-update-sprint-memory` (which IS the sign-off) |
| `main` | **Never by an agent** — only when Daniel asks directly or runs `/sudo-push-e2e` |

Approval for a `main_debug` landing is **per-action and never carries forward**. One "approved" lands
one story; the next needs its own.

**Enforcement:** the `require-push-approval.py` PreToolUse hook (canonical source `.agents/hooks/`,
deployed to every `.claude/hooks/`) forces the approval prompt on any `git push` targeting
`main_debug`/`main` however it's wrapped, and on any `git commit` attempted while HEAD is
`main_debug`/`main` (i.e. outside a worktree — see `worktree-per-story.md` G1). `merge_pull_request`
(+ GitHub write tools) is gated in `.claude/settings.json`. The hook only ever sees the **agent's**
Bash tool — Daniel's own terminal is never affected by it.

## The landing — one story, one clean push

The story lands on `main_debug` at close-out (`/sudo-update-sprint-memory` Step 7) or on Daniel's
in-the-moment "approved". It merges **from inside the worktree**, never by checking out `main_debug`
in the shared checkout:

```bash
git fetch origin main_debug
git merge origin/main_debug        # absorb it INSIDE the worktree — conflicts surface here, isolated
git push origin claude/<slug>      # free; the branch is the rollback point
git push origin HEAD:main_debug    # THE landing (hook prompts once)
```

Checking out `main_debug` in the shared checkout to merge is **wrong** — that tree holds other teams'
uncommitted work, so the merge either refuses or drags their files through your landing. If the merge
conflicts, it conflicts in the isolated worktree: **STOP and report**, never force-push, never
blind-rebase.

## Safe-commit mechanics (always — inside the worktree too)

- **Commit your OWN work via explicit paths:** `git add path/one path/two …`.
- **NEVER `git add -A`, `git add .`, or `git add -u`** — they sweep other parallel work (other
  agents/teams, or Daniel's own uncommitted changes) into your commit. This is the most important rule,
  and the worktree does not repeal it.
- **Verify the staged set first:** `git diff --cached --stat` must show ONLY your files. If anything
  else appears, unstage it (`git restore --staged <path>`) before committing.
- **Scope the commit message** to your task/story only.
- **If a push is rejected** (remote moved under you), **STOP and report.** Do not force-push, and do
  not blind-rebase while other uncommitted work sits in the tree.

## Sync-first — check the remote before you land

Phone and desktop share branches, so landing from a **stale** branch is what causes the
diverge → rejected-push tangle. Before the landing push:

1. **Fetch and compare:** `git fetch origin main_debug`, then check whether you are behind
   (`git rev-list --count HEAD..origin/main_debug` > 0).
2. **If behind, merge `origin/main_debug` into your story branch first** (the landing block above does
   this by default) so you never land on top of a stale base.
3. **If it will not merge cleanly**, **STOP and flag it** — hand Daniel the situation. Do NOT run a
   blind merge/rebase, and never force-push.

## Always

- **Clear the Dummy GitHub Token:** The Antigravity IDE automatically injects a dummy `GITHUB_TOKEN` into the agent's environment as a sandbox security measure. Because Git and the `gh` CLI prioritize this environment variable over the Windows Credential Manager, it causes authentication failures. **Before running any `git` or `gh` commands, you MUST clear this variable** by prefixing the command or running: `Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; <command>`.
- **Validate CI/CD credentials**: Before landing on a deployment-triggering branch (`main` or `main_debug`), verify that the target repository's required secrets (e.g., `FIREBASE_SERVICE_ACCOUNT`) and variables (e.g., `FIREBASE_PROJECT_ID`) are set up on GitHub using `gh secret list` and `gh variable list`. If credentials are missing, STOP and notify Daniel before proceeding.
- The `walkthrough.md` **"Your Actions"** section records what landed — the branch, the commit range,
  and anything Daniel still has to do (a `main` promotion, a live check). It is no longer a `git add`
  command block, because the agent already ran it.

> **Web/mobile sessions** follow the same model with lighter mechanics — see `mobile-mode.md`
> → Override 1. It shares this rule's safe-commit mechanics and Sync-first.
