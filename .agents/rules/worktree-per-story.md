---
name: worktree-per-story
description: "Fires when a sudo story lane (① /sudo-write-story-tests · ② /sudo-dev-story-tests · /sudo-quick-dev · autopilot) starts work that will produce commits — and ONLY there. One story, one worktree, one `claude/*` branch, opened off the story's EPIC branch (`epic/<JIRA-KEY>-<slug>`) BEFORE the first edit, committed freely inside, landed at close-out and pruned by /sudo-close-workingtree. Ad-hoc non-story work NEVER opens a worktree — it takes a `chore/*` branch off main. Read-only sessions exempt. Pairs with git-policy.md."
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
all against the same project repo. One story = one worktree = one `claude/<JIRA-KEY>-<story-slug>` branch is what
makes that survivable. Assume from your first command that you are NOT alone in the repo:

- **The shared checkout is a lobby, not your desk.** It stands on `main` — production — and stays
  there. Its `git status` can still show other lanes' dirty files and half-landed syncs. Never sweep,
  revert, or "fix" a file you did not change — report it and move on. (G2's explicit-paths rule exists
  precisely so several lanes can share one checkout without committing each other's work.)
- **The epic branch moves under you.** Another lane can land on `epic/<JIRA-KEY>-<slug>` mid-session, so your
  branch base is stale by default — merge `origin/epic/<JIRA-KEY>-<slug>` into the story branch before landing
  (the landing sequence in `git-policy.md`); never assume the base you opened on.
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
conversationally — quick fixes, toolkit/system maintenance, doc edits — takes a short-lived `chore/<JIRA-KEY>-<slug>`
branch off `main` (no worktree, no `claude/*` branch), merged back to `main` in the same session with
Daniel's sign-off; an orphan tree that no close-out will ever prune is exactly what this boundary
prevents. Unsure whether you're in a lane? You're not — take a `chore/*` branch (or ask).

```
EnterWorktree  →  .claude/worktrees/<story-slug>/  on branch  claude/<JIRA-KEY>-<story-slug>
```

Branched from **the story's epic branch (`epic/<JIRA-KEY>-<slug>`)**, never from `main`. The epic
branch is cut from `main` at epic kickoff (`/sudo-create-epic-sprint`); if it doesn't exist yet,
that step was skipped — go back and run it. The `worktree.baseRef: "head"` setting makes the new
worktree inherit the current HEAD, so **check out the epic branch before opening the worktree** — if
you are somewhere else, get there first (or say so out loud if you are deliberately stacking on
another story's branch).

### Exempt — no worktree needed

- **Ad-hoc non-story work** — anything outside the sudo story lanes (see Trigger): `chore/<JIRA-KEY>-<slug>`
  branch off `main`, explicit paths, merged back with sign-off; the push-approval hook still prompts
  on the `main` merge.
- **Read-only sessions** — questions, recon, code reading, reviews that write no project file.
- **`/sudo-push-e2e`** — it operates *on* branches (`epic/<JIRA-KEY>-<slug>` → `main`), so it must run in the
  main checkout.
- **Daniel says otherwise** — an explicit "just do it here" in the moment wins.

## Resuming — a fresh chat picks the story back up

A worktree outlives the chat that opened it. A **new session** — fresh context, a `/compact`, a
different model, or simply a different chat window — that resumes an in-flight story must **re-enter the
existing worktree**: not open a second one, and not work in the shared checkout. Before `EnterWorktree`
fires (and at the top of any `sudo-*` step that will read or edit story files), look first:

```
git worktree list        # is there already a  claude/<JIRA-KEY>-<story-slug>  tree?
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
| **G1 · Location** | Story-lane commits happen only inside a worktree, on a `claude/*` branch — HEAD at `main` during a story lane means you are in the shared checkout: open the worktree first. Ad-hoc (non-lane) work commits on its `chore/*` branch by design (see Trigger). (The `require-push-approval.py` hook prompts on `main` either way.) |
| **G2 · Scope** | `git add <explicit paths>` only. **`git add -A` / `.` / `-u` are banned** — they sweep other teams' work into your commit. Verify with `git diff --cached --stat` that only your files are staged. |
| **G3 · Push** | No pushes to the epic branch during development — the landing at close-out is the one sanctioned push there. Pushing your own `claude/*` branch is free at any time. |
| **G4 · `main`** | Never. Only Daniel, via `/sudo-push-e2e` (epic merge) or a direct in-the-moment ask (chore merge). |

## Artifacts are authored in the tree

Every file a story step writes — story file, red tests, implementation plan, self-audit, walkthrough,
automation summary, the ③ verdict — is authored INSIDE the story's worktree, rides the story branch,
and lands with the close-out merge. Never write a story-scoped artifact to the shared checkout. The
reader's corollary: a story's artifacts live in ITS tree — absence there means that step never ran. A
lookalike found in the shared checkout or a sibling tree is ANOTHER lane's work; reading it as this
story's evidence is how a session derails (2026-08-01: a sibling's ③ verdict sitting in the shared
checkout read as "this story's review is done", and the confusion cost the actual run).

## Close-out — the landing

The story lands on its **epic branch** as **one clean push**, triggered by either:

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
("The landing"): merge `origin/epic/<JIRA-KEY>-<slug>` into the story branch *inside the worktree*, then
`git push origin HEAD:epic/<JIRA-KEY>-<slug>`. Never check out the epic branch in the shared checkout to merge.

The shared checkout needs **no reconcile after a landing** — it stands on `main`, which only moves when
the epic merges via `/sudo-push-e2e`. (Under the retired `main_debug` model the shared checkout fell one
story behind per landing and needed a mandatory fast-forward; that whole failure mode died with the
long-lived integration branch.)

Afterwards, once the landing on the epic branch is verified, the worktree and git branch
(`claude/<JIRA-KEY>-<story-slug>`) are pruned via `/sudo-close-workingtree` (auto-invoked by
`/sudo-update-sprint-memory` Step 8) to keep local disk and remote GitHub clean. The epic branch itself
is pruned later, by `/sudo-push-e2e`, after the epic merges to `main`.

## Hard stops

- NEVER edit a project file for sudo-lane story work before its worktree is open — and NEVER open a
  worktree outside a sudo story lane (an orphan tree no close-out will prune).
- NEVER branch a story worktree from `main` — stories branch from the epic branch.
- NEVER `git add -A` / `.` / `-u`, inside a worktree or out.
- NEVER check out the epic branch in the shared checkout to merge a story — land from inside the
  worktree; the shared checkout stays on `main`.
- NEVER push to `main`. That is Daniel's, via `/sudo-push-e2e`.
