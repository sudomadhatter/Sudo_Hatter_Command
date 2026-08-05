---
name: worktree-per-story
description: "Fires when a sudo story lane (① /sudo-write-story-tests · ② /sudo-dev-story-tests · /sudo-quick-dev · autopilot) starts work that will produce commits — and ONLY there. One story, one worktree, one `claude/*` branch, opened off `main_debug` BEFORE the first edit, committed freely inside, landed at close-out and pruned by /sudo-close-workingtree. Ad-hoc non-story work NEVER opens a worktree — it edits `main_debug` directly. Read-only sessions exempt. Pairs with git-policy.md."
---

# Worktree Per Story

> **Why this exists.** Several teams run in parallel against one checkout. Their edits interleave in the
> same files, `git status` becomes a soup of everybody's work, and whoever pushes last inherits all of
> it — so a commit titled "formalize the TEA framework" ships four unrelated sessions and the message
> can only honestly describe one of them. A worktree per story ends that. Each story gets an isolated
> tree, commits only its own files, and lands as one clean push.

## The standing environment — parallel teams are the NORM

Up to **four story lanes — sometimes more — run this system at once**: separate sessions, separate
models, sometimes separate platforms (Claude Code, opencode, Antigravity, Codex, an autopilot engine),
all against the same project repo. One story = one worktree = one `claude/<story-slug>` branch is what
makes that survivable. Assume from your first command that you are NOT alone in the repo:

- **The shared checkout is a lobby, not your desk.** Its `git status` routinely shows other lanes'
  dirty files and half-landed syncs. Never sweep, revert, or "fix" a file you did not change — report
  it and move on. (G2's explicit-paths rule exists precisely so several lanes can share one checkout
  without committing each other's work.)
- **`origin/main_debug` moves under you.** Another lane can land mid-session, so your branch base is
  stale by default — merge `origin/main_debug` into the story branch before landing (the landing
  sequence in `git-policy.md`); never assume the base you opened on.
- **The board files are everyone's files.** `sprint-status.yaml`, `active-context.md`, and the sprint
  map are edited by EVERY lane — the #1 merge-conflict surface (2026-07-31: a three-block conflict
  soup was committed to active-context.md exactly this way). Resolve by keeping BOTH sides' facts —
  parallel lanes record different true things; picking a winner erases someone's work.
- **Sibling lanes collide on shared surfaces.** Two lanes have shipped the same fix from one triage
  doc; two stories have planned edits to the same function. Before landing, re-diff your branch
  against the live sibling `claude/*` branches, and honor any set-wide LANDING RULE posted on the
  project's sprint board — while one is active, no lane lands alone.

## Trigger — the sudo story lanes, automatic there, ONLY there

**A worktree opens when a sudo story lane starts work that will produce story commits** — ①
`/sudo-write-story-tests`, ② `/sudo-dev-story-tests`, `/sudo-quick-dev`, the autopilot engines — **BEFORE
the first project file is edited.** Automatic inside those lanes; the agent does not ask each time. The
lane that opens the tree is the lane that closes it: the story lands at close-out
(`/sudo-update-sprint-memory` Step 7) and `/sudo-close-workingtree` prunes the tree + branches (its
Step 8). **Never open a worktree outside a sudo story lane.** Ad-hoc work Daniel asks for
conversationally — quick fixes, toolkit/system maintenance, doc edits — edits the main checkout directly
on `main_debug`: Daniel runs solo, nothing else is on the branch mid-session, and an orphan tree that no
close-out will ever prune is exactly what this boundary prevents. Unsure whether you're in a lane? You're
not — work on `main_debug` (or ask).

```
EnterWorktree  →  .claude/worktrees/<story-slug>/  on branch  claude/<story-slug>
```

Branched from **`main_debug`**, never from `main`. The `worktree.baseRef: "head"` setting makes the new
worktree inherit the current HEAD, so **confirm HEAD is `main_debug` before opening it** — if you are
somewhere else, get to `main_debug` first (or say so out loud if you are deliberately stacking on
another story's branch).

### Exempt — no worktree needed

- **Ad-hoc non-story work** — anything outside the sudo story lanes (see Trigger): edit and commit on
  `main_debug` with explicit paths; the push-approval hook still prompts.
- **Read-only sessions** — questions, recon, code reading, reviews that write no project file.
- **`/sudo-push-e2e`** — it operates *on* branches (`main_debug` → `main`), so it must run in the main
  checkout.
- **Daniel says otherwise** — an explicit "just do it here" in the moment wins.

## Resuming — a fresh chat picks the story back up

A worktree outlives the chat that opened it. A **new session** — fresh context, a `/compact`, a
different model, or simply a different chat window — that resumes an in-flight story must **re-enter the
existing worktree**: not open a second one, and not work in the shared checkout. Before `EnterWorktree`
fires (and at the top of any `sudo-*` step that will read or edit story files), look first:

```
git worktree list        # is there already a  claude/<story-slug>  tree?
```

- **A tree for this story slug exists** → that IS your workspace. `cd` into it and bind every path — story
  file, ① red tests, `_artifacts/…`, test commands — under it. Its branch already carries the ① / earlier-②
  commits, and **the story file and red tests often live ONLY in that tree, never in the shared checkout** —
  so a session that skips this step is blind to the very work it was invoked to continue, and will either
  re-do ① or wrongly report the story missing.
- **No tree yet** → this is the first work session; open one per the Trigger above.

Never open a second worktree for a slug that already has one, and never fall back to editing in the shared
checkout because the tree "looked empty" from where you happened to be standing. Match by the `<story-slug>`
in the branch/path, not by cwd.

## Inside the worktree — commit freely

The worktree is your box. Commit your own work as you go; no approval, no handing Daniel a command.
The safe-commit mechanics from `git-policy.md` still apply in full:

| Gate | Rule |
|---|---|
| **G1 · Location** | Story-lane commits happen only inside a worktree, on a `claude/*` branch — HEAD at `main_debug`/`main` during a story lane means you are in the shared checkout: open the worktree first. Sanctioned ad-hoc (non-lane) work commits on `main_debug` by design (see Trigger). (The `require-push-approval.py` hook prompts either way.) |
| **G2 · Scope** | `git add <explicit paths>` only. **`git add -A` / `.` / `-u` are banned** — they sweep other teams' work into your commit. Verify with `git diff --cached --stat` that only your files are staged. |
| **G3 · Push** | No pushes to `main_debug` during development. Pushing your own `claude/*` branch is free at any time. |
| **G4 · `main`** | Never. Only Daniel, directly or via `/sudo-push-e2e`. |

## Artifacts are authored in the tree

Every file a story step writes — story file, red tests, implementation plan, self-audit, walkthrough,
automation summary, the ③ verdict — is authored INSIDE the story's worktree, rides the story branch,
and lands with the close-out merge. Never write a story-scoped artifact to the shared checkout. The
reader's corollary: a story's artifacts live in ITS tree — absence there means that step never ran. A
lookalike found in the shared checkout or a sibling tree is ANOTHER lane's work; reading it as this
story's evidence is how a session derails (2026-08-01: a sibling's ③ verdict sitting in the shared
checkout read as "this story's review is done", and the confusion cost the actual run).

## Close-out — the landing

The story lands on `main_debug` as **one clean push**, triggered by either:

- **`/sudo-update-sprint-memory`** — invoking it IS Daniel's sign-off (Step 7 does the landing), or
- **Daniel's in-the-moment "approved"** — per-action, never carries to the next story.

**Several sibling lanes live at close-out time** (the standing multi-team case, or a LANDING RULE posted
on the project's sprint board): the set goes through **`/sudo-merge-epic-workingtrees`** — the one-shot
close-out for ALL live lanes: overlap map, dependency-ordered merges with per-lane test gates, landing,
each story flipped `done`, the combined gate, then every tree and branch pruned. No lane lands alone
while a set is declared.

Close-out runs **inside the worktree**, so its `sprint-status.yaml`, `active-context.md`, and story-file
edits ride the story branch and land with the story — instead of sitting in the shared tree waiting to
be hunk-picked out of somebody else's diff. The landing sequence itself is in `git-policy.md`
("The landing"): merge `origin/main_debug` into the story branch *inside the worktree*, then
`git push origin HEAD:main_debug`. Never check out `main_debug` in the shared checkout to merge.

⚠️ **That push does NOT update the shared checkout's `main_debug`** — it moves the remote and
`origin/main_debug` only, leaving `refs/heads/main_debug` where it was. Landing without reconciling
afterwards puts the shared tree one story behind **per landing**, and since the board files are edited
there, the next `pull --ff-only` refuses. `git-policy.md` → **"Reconcile the shared checkout"** is a
mandatory part of every landing, not an optional tidy-up.

Afterwards, once the landing on `main_debug` is verified, the worktree and git branch (`claude/<story-slug>`) are pruned via `/sudo-close-workingtree` (auto-invoked by `/sudo-update-sprint-memory` Step 8) to keep local disk and remote GitHub clean.


## Hard stops

- NEVER edit a project file for sudo-lane story work before its worktree is open — and NEVER open a
  worktree outside a sudo story lane (an orphan tree no close-out will prune).
- NEVER branch a worktree from `main`.
- NEVER `git add -A` / `.` / `-u`, inside a worktree or out.
- NEVER check out `main_debug` in the shared checkout to merge a story — other teams' uncommitted work
  lives there.
- NEVER push to `main`. That is Daniel's, via `/sudo-push-e2e`.
