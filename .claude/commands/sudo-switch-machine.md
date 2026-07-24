---
description: Machine handoff — park the session before switching machines (commit + sync + push every story worktree and both repos, then write a resume card), or resume on arrival (fetch, re-create the worktrees the new machine cannot see, report what is live). Run it as the LAST thing before closing a lid and the FIRST thing after opening one. Never lands anything on main_debug — that stays /sudo-update-sprint-memory Step 7.
---

# /sudo-switch-machine — Machine Handoff (park ⇄ resume)

Daniel works one sprint across **desktop, laptop, and mobile**. Git branches travel; **worktrees do not.**
`.claude/worktrees/` is a local git construct that is not in the repo, so on any other machine
`git worktree list` shows only the main checkout — and every `sudo-` step reads that as *"no tree, fresh
start."* **That is a false negative**, and acting on it re-does story work that already exists.

This command closes that gap from both ends. It moves **branches**, never `main_debug`.

**⛔ Hard boundary:** this command NEVER pushes a story branch onto `main_debug`. Landing a story is
`/sudo-update-sprint-memory` Step 7, and only after ③ turns the story green. A story at ① / ② carries
**deliberately RED tests** — landing those on the shared line poisons every other story's regression
baseline and reds the `/sudo-e2e` gate that guards promotion to `main`.

## Step 0 — Resolve scope (FIRST)
Two separate git repos are in play and BOTH must be parked:
1. **The lobby** — the repo you are standing in (`Sudo_Hatter_Command`). Holds `_artifacts/`, `.agents/`,
   board sessions, open tasks.
2. **The active project** — read `.agents/active-project.txt`; set `PROJECT_ROOT = Projects/<name>`. If the
   pointer is missing or the file is absent, ASK which project — never guess.
   (**Sub-project fast path:** if this repo has no `Projects/` subfolder, you ARE the project — lobby and
   project are the same repo. Do the project half only.)

Echo exactly `Scope: lobby + Projects/<name>` before any git command.

## Step 1 — Pick the direction
- `$ARGUMENTS` contains `park` / `leaving` / `out` → **PARK**.
- `$ARGUMENTS` contains `resume` / `arriving` / `in` → **RESUME**.
- **No argument (the usual case)** — auto-detect, then say which you picked and why:
  - Any uncommitted change, any unpushed commit, or any live worktree → **PARK**.
  - Clean everywhere AND `git ls-remote --heads origin 'refs/heads/claude/*'` returns branches that have
    no local worktree → **RESUME**.
  - Both look true, or neither does → ASK. Do not guess with a dirty tree.

---

# PARK — leaving this machine

Work outward: story worktrees first (they hold the fragile in-flight work), then the two main checkouts.

## P0 — Guard: worktrees must never be committable (check BEFORE any `git add`)
A worktree directory holds a `.git` **file**, so a blanket `git add` records it as a **gitlink (mode
160000)** with no `.gitmodules`. Pulling that on another machine creates **empty directories at exactly the
paths `git worktree add` needs**, and re-creating the worktree there fails. (This really happened in AGY,
commit `d098dc63`; fixed 2026-07-23.) In BOTH repos:

```bash
git check-ignore -q .claude/worktrees/ || echo "NOT IGNORED — fix before parking"
git ls-files -s .claude/worktrees/          # must be EMPTY; any 160000 line is the bug
```
- Not ignored → add `.claude/worktrees/` to `.gitignore`.
- Gitlinks present → `git rm --cached <each path>` (index only — the working directories survive), commit
  that with the ignore rule, and say so in the report.

## P1 — Park every story worktree
`git worktree list` under `PROJECT_ROOT`. For EACH `claude/*` tree, **cd into it** and:

```bash
# 1 · commit — EXPLICIT PATHS ONLY, never `git add -A`
git status --porcelain                # show Daniel what is loose, path by path
git add <this story's paths>
git diff --cached --stat              # must show ONLY this story's files
git commit -m "wip(<story>): park for machine switch — <one line of where it stands>"

# 2 · sync-first: absorb main_debug INSIDE the worktree
git fetch origin main_debug
git merge origin/main_debug           # CONFLICT → resolve HERE, on the machine that has the context

# 3 · push the branch — this is the ONLY thing that makes the work portable
git push -u origin claude/<story-slug>
```

- **Resolve conflicts now, not later.** The sprint board (`sprint-status.yaml`) conflicts routinely because
  every story edits its own status line; the machine you are on is the one that knows which line is right.
  A conflict left for the laptop is a conflict resolved with no context.
- **Loose files that are NOT this story's** (sync drift, stray skill deletions, orphaned scratch) — do NOT
  sweep them into the story commit. List them in the resume card as *left dirty, deliberately*.
- **Nothing to commit** is still worth a `git push` — the branch may be ahead from an earlier session.

## P2 — Park the two main checkouts
For `PROJECT_ROOT` and then the lobby, on `main_debug`:

```bash
git status --porcelain                # report untracked artifact folders explicitly
git add <explicit paths>              # artifacts, docs, board edits — NEVER -A
git commit -m "<scope>: park for machine switch"
git push origin main_debug
```

Untracked `_artifacts/` run-folders are the usual catch here — they are the record of the session and are
worthless on the machine you are walking away from.

## P3 — Write the resume card
Append (or refresh, if one is already there) a **single** stanza at the top of
`_bmad-output/active-context/active-context.md` § *Owed / Carryover Gates*. Overwrite the previous card —
one live card, never a log:

```markdown
> **🔁 MACHINE HANDOFF — parked <YYYY-MM-DD> from <machine>:** Live story branches on origin —
> `claude/<slug>` (step ①/②/③, <one line: what is done, what is next>) ×N. Worktrees are LOCAL —
> `git worktree list` on the next machine WILL show nothing; that is expected, not a fresh start.
> Resume with `/sudo-switch-machine resume`. Left dirty on <machine>, deliberately: <paths or "nothing">.
```

Commit and push that edit with P2 (it rides `main_debug`, so every machine sees it).

## P4 — Report
State plainly: each branch + its sha + whether it is now on origin; each repo's push result; anything left
dirty and why; and the one-line resume instruction. **If ANY push failed, say so loudly** — an unpushed
branch is work stranded on a machine Daniel is walking away from. That is the whole failure this command
exists to prevent, so never soften it.

---

# RESUME — arriving on a machine

## R1 — Fetch both repos
```bash
git fetch origin --prune              # in the lobby AND in PROJECT_ROOT
git status -sb                        # on main_debug in each
git pull --ff-only origin main_debug  # diverged → STOP and report; do not merge blind
```

## R2 — Find the live stories (do NOT trust `git worktree list` here)
```bash
git ls-remote --heads origin 'refs/heads/claude/*'
```
Every branch listed that is ahead of `origin/main_debug` is **in-flight story work**. Cross-check each
against `sprint-status.yaml` and the handoff card from P3 to get its step. Report the set before touching
anything.

## R3 — Re-create the working surface
Ask Daniel which story he is picking up, then match the machine:

- **Desktop / laptop (parallel stories, full git):**
  ```bash
  git worktree add --track -b claude/<slug> .claude/worktrees/<slug> origin/claude/<slug>
  ```
  (If the local branch already exists, `git worktree add .claude/worktrees/<slug> claude/<slug>` — then
  `git pull` inside it; the branch may have moved on the other machine.)
- **Mobile / cloud (one story at a time, no worktree needed):** plain
  `git checkout claude/<slug>` in the main checkout. The worktree is only a convenience for running several
  stories side by side on one box — **the branch is the portable unit**, and nothing downstream requires the
  work to sit in `.claude/worktrees/`.

## R4 — Hand off to the boot
Say:
> "Resumed on <machine>. Live: <branches + steps>. Working surface for <story> is `<path or branch>`.
> Run `/sudo-boot-sprint-memory` to pick up the sprint."

Then stop. This command restores the surface; it does not start work.

---

**Never:** `git add -A` · force-push · rebase a pushed story branch · push a story branch to `main_debug` ·
delete a worktree on park (it is the rollback point, and it costs nothing to leave).

Optional additional input: $ARGUMENTS
