---
name: worktree-per-story
description: "Fires on any story or development work that will produce commits. Open a dedicated git worktree branched from `main_debug` BEFORE editing the first project file — one story, one worktree, one `claude/*` branch — commit freely inside it, and land it on `main_debug` as ONE clean push at Daniel's sign-off. Read-only sessions are exempt. Pairs with git-policy.md."
activation: Protocol (every work session that writes files)
---

# Worktree Per Story

> **Why this exists.** Several teams run in parallel against one checkout. Their edits interleave in the
> same files, `git status` becomes a soup of everybody's work, and whoever pushes last inherits all of
> it — so a commit titled "formalize the TEA framework" ships four unrelated sessions and the message
> can only honestly describe one of them. A worktree per story ends that. Each story gets an isolated
> tree, commits only its own files, and lands as one clean push.

## Trigger — automatic, do not ask

**Any story or development work that will produce commits opens its own worktree BEFORE the first
project file is edited.** This is automatic; the agent does not ask permission each time.

```
EnterWorktree  →  .claude/worktrees/<story-slug>/  on branch  claude/<story-slug>
```

Branched from **`main_debug`**, never from `main`. The `worktree.baseRef: "head"` setting makes the new
worktree inherit the current HEAD, so **confirm HEAD is `main_debug` before opening it** — if you are
somewhere else, get to `main_debug` first (or say so out loud if you are deliberately stacking on
another story's branch).

### Exempt — no worktree needed

- **Read-only sessions** — questions, recon, code reading, reviews that write no project file.
- **`/sudo-push-e2e`** — it operates *on* branches (`main_debug` → `main`), so it must run in the main
  checkout.
- **Daniel says otherwise** — an explicit "just do it here" in the moment wins.

## Inside the worktree — commit freely

The worktree is your box. Commit your own work as you go; no approval, no handing Daniel a command.
The safe-commit mechanics from `git-policy.md` still apply in full:

| Gate | Rule |
|---|---|
| **G1 · Location** | Commit only from inside a worktree, on a `claude/*` branch. HEAD is `main_debug`/`main` → **do not commit** — you are in the shared checkout. Open the worktree first. (The `require-push-approval.py` hook prompts if you try.) |
| **G2 · Scope** | `git add <explicit paths>` only. **`git add -A` / `.` / `-u` are banned** — they sweep other teams' work into your commit. Verify with `git diff --cached --stat` that only your files are staged. |
| **G3 · Push** | No pushes to `main_debug` during development. Pushing your own `claude/*` branch is free at any time. |
| **G4 · `main`** | Never. Only Daniel, directly or via `/sudo-push-e2e`. |

## Close-out — the landing

The story lands on `main_debug` as **one clean push**, triggered by either:

- **`/sudo-update-sprint-memory`** — invoking it IS Daniel's sign-off (Step 7 does the landing), or
- **Daniel's in-the-moment "approved"** — per-action, never carries to the next story.

Close-out runs **inside the worktree**, so its `sprint-status.yaml`, `active-context.md`, and story-file
edits ride the story branch and land with the story — instead of sitting in the shared tree waiting to
be hunk-picked out of somebody else's diff. The landing sequence itself is in `git-policy.md`
("The landing"): merge `origin/main_debug` into the story branch *inside the worktree*, then
`git push origin HEAD:main_debug`. Never check out `main_debug` in the shared checkout to merge.

Afterwards the worktree is **kept on disk**, not auto-removed — it is the rollback point if the landing
needs revisiting.

## Hard stops

- NEVER edit a project file for story/dev work before the worktree is open.
- NEVER branch a worktree from `main`.
- NEVER `git add -A` / `.` / `-u`, inside a worktree or out.
- NEVER check out `main_debug` in the shared checkout to merge a story — other teams' uncommitted work
  lives there.
- NEVER push to `main`. That is Daniel's, via `/sudo-push-e2e`.
