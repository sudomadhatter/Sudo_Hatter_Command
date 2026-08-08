---
description: Resume a sprint on a machine you just switched to — fetch both repos, find the live story branches on origin (NOT via git worktree list, which lies on a fresh machine), re-create the working surface, and hand off to /sudo-boot-sprint-memory. Run it as the FIRST thing after opening a lid. Pairs with /sudo-park.
---

# /sudo-resume — Pick The Sprint Back Up On This Machine

> **Rules in force for this command:**
> - `.agents/rules/worktree-per-story.md` — one worktree per story, resolve-or-STOP, never delete through a junction

Daniel works one sprint across **desktop, laptop, and mobile**. Git branches travel; **worktrees do not.**
`.claude/worktrees/` is machine-local and not in the repo, so on a machine you just switched to
`git worktree list` shows only the main checkout — and every `sudo-` step reads that as *"no tree, fresh
start."* **That is a false negative**, and acting on it re-does story work that already exists.

This command restores the working surface from what is actually on origin. It **creates**, never deletes:
the worktrees on your other machine stay exactly where they are, and both machines end up on the same
branch. That is the intended end state, not a conflict.

Parked from the other machine with `/sudo-park`.

## Step 0 — Resolve scope (FIRST)
Per `.agents/rules/sudo-target-resolution.md` **§DUAL**: BOTH repos must be refreshed — the lobby AND the
active project (pointer missing → ASK, never guess; fast path: no `Projects/` subfolder → one repo). Echo
exactly `Resuming: lobby + Projects/<name>` before any git command.

## Step 1 — Fetch both repos
In the lobby AND in `PROJECT_ROOT`:

```bash
git fetch origin --prune
git rev-parse --abbrev-ref HEAD       # the shared checkout stands on main — permanently
git checkout main                     # ONLY if it read something else
git pull --ff-only origin main        # diverged → STOP and report; do not merge blind
```

The shared checkout stands on `main` and stays there — a fresh clone lands on it, and that is now also
the working stance, not a hazard. (The old hard gate here — accidentally fast-forwarding `main` while
pulling `main_debug` — died with the integration branch on 2026-08-07.)

A `--ff-only` failure means this machine has local commits that never got parked. **Stop and report it** —
do not merge or rebase your way out. Those commits are the thing `/sudo-park` exists to prevent, and
resolving them blind is how work gets lost.

## Step 2 — Read the handoff card
Read `_bmad-output/active-context/active-context.md` § *Owed / Carryover Gates* and look for the
**🔁 MACHINE HANDOFF** stanza. It names the live branches, the step each is at, and anything the other
machine deliberately left dirty. If there is no card, continue — Step 3 is the ground truth either way.

## Step 3 — Find the in-flight work (do NOT trust `git worktree list` here)
```bash
git ls-remote --heads origin 'refs/heads/epic/*'      # the live epic branch(es) — the integration line
git ls-remote --heads origin 'refs/heads/claude/*'    # parked story branches
```
An `epic/*` branch on origin is the sprint's integration line — check it out locally so the story
worktrees below have their base (`git checkout --track origin/epic/<JIRA-KEY>-<slug>`, then back to `main`).
Every `claude/*` branch listed is **in-flight story work**, parked from another machine. Cross-check each
against `sprint-status.yaml` for its status, and report the whole set — branch, story, step — **before
touching anything**. Expect branches the handoff card does not mention: parallel sessions open their own.
(The board carries bare statuses since the Wave 4 split; a row's history, if you need it, is in
`_bmad-output/history/<epic>/<key>.md`.)

⛔ Report the YAML status as the YAML's claim, not as the truth. A story sitting at `review` is **not**
proof it is landable — the verdict lives in the lane's `walkthrough.md` under `## Code Review`, and a
`@ <sha>` older than that branch's HEAD is a stale verdict. Do not resolve that here;
`/sudo-boot-sprint-memory` owns it (Step 2b). Never recommend a close-out from this command.

## Step 4 — Re-create the working surface
Ask Daniel which story he is picking up, then match the machine:

- **Desktop / laptop (parallel stories, full git):**
  ```bash
  git worktree add --track -b claude/<JIRA-KEY>-<slug> .claude/worktrees/<slug> origin/claude/<JIRA-KEY>-<slug>
  ```
  The parked branch already descends from its epic branch, so the re-created tree sits on the right
  base; a story with no parked branch yet opens its worktree off `origin/epic/<JIRA-KEY>-<slug>` instead — never
  off `main` (`worktree-per-story`). If the local branch already exists, use
  `git worktree add .claude/worktrees/<slug> claude/<JIRA-KEY>-<slug>` and then `git pull` **inside** it — the
  branch may have moved on the other machine.

  Path already exists but is not a registered worktree (a leftover ghost directory) → `git worktree prune`,
  then remove the empty directory, then add. **Never** `git worktree add --force` over real content.

- **Mobile / cloud (one story at a time, no worktree needed):** plain
  `git checkout claude/<JIRA-KEY>-<slug>` in the main checkout. The worktree is only a convenience for running several
  stories side by side on one box — **the branch is the portable unit**, and nothing downstream requires the
  work to sit in `.claude/worktrees/`.

## Step 5 — Hand off to the boot
Say:
> "Resumed on <machine>. Live: <branches + steps>. Working surface for <story> is `<path or branch>`.
> Run `/sudo-boot-sprint-memory` to load the sprint context."

Then stop. This command restores the **git surface**; `/sudo-boot-sprint-memory` loads the **sprint
context** and picks the next story. They are different jobs — do not do the boot's work here.

---

**Never:** force-push · rebase a pushed story branch · `git worktree add --force` · delete a worktree on
the other machine's behalf · start coding (this is setup only).

Optional additional input: $ARGUMENTS
