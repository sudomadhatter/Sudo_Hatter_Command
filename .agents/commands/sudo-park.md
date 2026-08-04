---
description: Park the session before switching machines — commit (explicit paths) + sync + push every story worktree branch and both repos, then write a resume card. Run it as the LAST thing before closing a lid. Branches travel between machines, worktrees do not. Never lands anything on main_debug. Pairs with /sudo-resume.
---

# /sudo-park — Park Before Switching Machines

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/worktree-per-story.md` — one worktree per story, resolve-or-STOP, never delete through a junction

Daniel works one sprint across **desktop, laptop, and mobile**. Git branches travel; **worktrees do not.**
`.claude/worktrees/` is machine-local and not in the repo, so on the next machine `git worktree list` shows
only the main checkout. **Anything not pushed is stranded on the box you are walking away from.**

This command makes the work portable. It moves **branches**, never `main_debug`.

**⛔ Hard boundary:** never push a story branch onto `main_debug`. Landing a story is
`/sudo-update-sprint-memory` Step 7, and only after ③ turns it green. A story at ① / ② carries
**deliberately RED tests** — landing those on the shared line poisons every other story's regression
baseline and reds the `/sudo-e2e` gate that guards promotion to `main`.

Pick the work back up with `/sudo-resume`.

## Step 0 — Resolve scope (FIRST)
Per `.agents/rules/sudo-target-resolution.md` **§DUAL**: BOTH repos must be parked — the lobby AND the
active project (pointer missing → ASK, never guess; fast path: no `Projects/` subfolder → one repo, do
the project half only). Echo exactly `Parking: lobby + Projects/<name>` before any git command.

## Step 1 — Guard: worktrees must never be committable (BEFORE any `git add`)
A worktree directory holds a `.git` **file**, so a blanket `git add` records it as a **gitlink (mode
160000)** with no `.gitmodules`. Pulling that on another machine creates **empty directories at exactly the
paths `git worktree add` needs**, and re-creating the worktree there fails. In BOTH repos:

```bash
git check-ignore -q .claude/worktrees/ || echo "NOT IGNORED — fix before parking"
git ls-files -s .claude/worktrees/          # must be EMPTY; any 160000 line is the bug
```
- Not ignored → add `.claude/worktrees/` to `.gitignore`.
- Gitlinks present → `git rm --cached <each path>` (index only — the working directories survive), commit
  that with the ignore rule, and say so in the report.

## Step 2 — Park every story worktree
`git worktree list` under `PROJECT_ROOT`. **Count them and say the number out loud** — parallel sessions
open trees you did not, so never assume you know the set. For EACH `claude/*` tree, **cd into it** and:

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
- **Never delete a worktree on park.** It is the rollback point and it costs nothing to leave.

## Step 3 — Park the two main checkouts
For `PROJECT_ROOT` and then the lobby, on `main_debug`:

```bash
git status --porcelain                # report untracked artifact folders explicitly
git add <explicit paths>              # artifacts, docs, board edits — NEVER -A
git commit -m "<scope>: park for machine switch"
git push origin main_debug
```

Untracked `_artifacts/` run-folders are the usual catch here — they are the record of the session and are
worthless on the machine you are walking away from.

## Step 4 — Write the resume card
Append (or refresh, if one is already there) a **single** stanza at the top of
`_bmad-output/active-context/active-context.md` § *Owed / Carryover Gates*. Overwrite the previous card —
one live card, never a log:

```markdown
> **🔁 MACHINE HANDOFF — parked <YYYY-MM-DD> from <machine>:** Live story branches on origin —
> `claude/<slug>` (step ①/②/③, <one line: what is done, what is next>) ×N. Worktrees are LOCAL —
> `git worktree list` on the next machine WILL show nothing; that is expected, not a fresh start.
> Pick it back up with `/sudo-resume`. Left dirty on <machine>, deliberately: <paths or "nothing">.
```

Commit and push that edit with Step 3 (it rides `main_debug`, so every machine sees it).

## Step 5 — Report
State plainly: each branch + its sha + whether it is now on origin; each repo's push result; anything left
dirty and why; and `/sudo-resume` as the next move. **If ANY push failed, say so loudly** — an unpushed
branch is work stranded on a machine Daniel is walking away from. That is the whole failure this command
exists to prevent, so never soften it.

---

**Never:** `git add -A` · force-push · rebase a pushed story branch · push a story branch to `main_debug` ·
delete a worktree.

Optional additional input: $ARGUMENTS
