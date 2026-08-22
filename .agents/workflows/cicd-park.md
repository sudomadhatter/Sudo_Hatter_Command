---
description: Park the session before switching machines — commit (explicit paths) + sync + push every story worktree branch, the epic branch...
---

# /cicd-park — Park Before Switching Machines

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/worktree-per-story.md` — one worktree per story, resolve-or-STOP, never delete through a junction

Daniel works one sprint across **desktop, laptop, and mobile**. Git branches travel; **worktrees do not.**
`.claude/worktrees/` is machine-local and not in the repo, so on the next machine `git worktree list` shows
only the main checkout. **Anything not pushed is stranded on the box you are walking away from.**

This command makes the work portable. It moves **branches** — the `claude/*` story branches, the epic
branch, and `main` only when it carries sanctioned unpushed work.

**⛔ Hard boundary:** never land a story on its epic branch — that is close-out's job
(`/cicd-close-story-merge-tree` Step 3, and only after ③ turns it green) — and never touch `main`. A
story at ① / ② carries **deliberately RED tests** — landing those on the epic branch poisons every
sibling story's regression baseline and reds the `/cicd-e2e` gate that guards the epic's merge to `main`.

Pick the work back up with `/cicd-resume`.

## Step 0 — Resolve scope (FIRST)
Per `.agents/rules/smh-target-resolution.md` **§DUAL**: BOTH repos must be parked — the lobby AND the
active project (pointer missing → ASK, never guess; fast path: no `Projects/` subfolder → one repo, do
the project half only). Echo exactly `Parking: lobby + Projects/<name>` before any git command.

**Run every git command with an explicit `-C <repo>`.** Parking spans two repos and touches trees other
lanes are still standing in, so a bare `git` that inherits `cwd` can act on the wrong one — `cwd` resets at
slash-command boundaries and is not evidence of intent (`worktree-per-story.md` → *"`cwd` is not intent"*).

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

# 2 · sync-first: absorb the story's EPIC branch INSIDE the worktree
git fetch origin epic/<JIRA-KEY>-<slug>
git merge origin/epic/<JIRA-KEY>-<slug>          # CONFLICT → resolve HERE, on the machine that has the context

# 3 · push the branch — this is the ONLY thing that makes the work portable
git push -u origin claude/<JIRA-KEY>-<story-slug>
```

- **Resolve conflicts now, not later.** The sprint board (`sprint-status.yaml`) conflicts routinely because
  every story edits its own status line; the machine you are on is the one that knows which line is right.
  A conflict left for the laptop is a conflict resolved with no context.
- **Loose files that are NOT this story's** (sync drift, stray skill deletions, orphaned scratch) — do NOT
  sweep them into the story commit. List them in the resume card as *left dirty, deliberately*.
- **Nothing to commit** is still worth a `git push` — the branch may be ahead from an earlier session.
- **Never delete a worktree on park.** It is the rollback point and it costs nothing to leave.

## Step 3 — Park the epic branch and the two main checkouts
**The epic branch travels too.** It LIVES on origin, and `/cicd-resume` checks it out on the new machine —
an unpushed epic branch strands every landed story with it:

```bash
git push origin epic/<JIRA-KEY>-<slug>           # rejected → fetch + merge first, never force
```

Then `PROJECT_ROOT` and the lobby. The shared checkouts stand on `main`, which moves only via
`/cicd-push-e2e` — so there is usually nothing to push. But **sanctioned unpushed work must not be
stranded**: loose session output (untracked `_artifacts/` run-folders are the usual catch — the record of
the session, worthless on the machine you are walking away from) goes on a short-lived `chore/<JIRA-KEY>-<slug>`
branch off `main` per `git-policy.md`, and an already-approved chore merge sitting unpushed on `main`
gets pushed now (the push-approval hook prompts — expected):

```bash
git status --porcelain                # report untracked artifact folders explicitly
git add <explicit paths>              # artifacts, docs — NEVER -A
git commit -m "<scope>: park for machine switch"     # on the chore/* branch, never on main directly
git push -u origin chore/<JIRA-KEY>-<slug>
```

## Step 4 — Write the resume card
Append (or refresh, if one is already there) a **single** stanza at the top of
`_bmad-output/active-context/active-context.md` § *Owed / Carryover Gates*. Overwrite the previous card —
one live card, never a log:

```markdown
> **🔁 MACHINE HANDOFF — parked <YYYY-MM-DD> from <machine>:** Live story branches on origin —
> `claude/<JIRA-KEY>-<slug>` (step ①/②/③, <one line: what is done, what is next>) ×N. Worktrees are LOCAL —
> `git worktree list` on the next machine WILL show nothing; that is expected, not a fresh start.
> Pick it back up with `/cicd-resume`. Left dirty on <machine>, deliberately: <paths or "nothing">.
```

Commit and push that edit inside one of the Step 2 worktrees (board files ride the story → epic
branches now, never the shared `main` checkout — the parked branches are what the next machine reads).

## Step 5 — Report
State plainly: each branch + its sha + whether it is now on origin; each repo's push result; anything left
dirty and why; and `/cicd-resume` as the next move. **If ANY push failed, say so loudly** — an unpushed
branch is work stranded on a machine Daniel is walking away from. That is the whole failure this command
exists to prevent, so never soften it.

---

**Never:** `git add -A` · force-push · rebase a pushed story branch · land a story on its epic branch
(close-out's job) · touch `main` (outside a sanctioned chore merge) · delete a worktree.

Optional additional input: $ARGUMENTS
