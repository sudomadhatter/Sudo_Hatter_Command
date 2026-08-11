---
name: git-policy
description: "Git policy: main is the ONLY long-lived branch. Each epic gets a short-lived `epic/<JIRA-KEY>-<slug>` branch off main; story/dev work happens in its own git worktree on a `claude/*` branch off the epic branch, where the agent commits FREELY (explicit paths — never `git add -A`). The story lands on its epic branch on Daniel's in-the-moment 'approved' or via /cicd-update-sprint-memory. The epic reaches `main` only through /cicd-push-e2e — full gate + E2E green + Daniel's sign-off."
---

# Git Policy

> The single, canonical git rule for the whole workspace. **Agents commit and push their own work now.**
> This supersedes the old "never run git yourself — hand Daniel the command" default, which is gone:
> that default is what produced commits carrying four unrelated sessions at once.

## Branch model — epic branches → `main` (THE dev standard)

> The one source of truth for the branch model. Every workspace (home base + every project) uses it;
> per-workspace `AGENTS.md` GATES sections point here rather than restating it.
>
> **History note:** the previous standard (`main_debug` as a long-lived integration branch) was
> retired 2026-08-07 — every repo's `main_debug` was fast-forwarded into `main` and deleted. If a
> doc, memory, or artifact still says `main_debug`, it predates that migration; the artifact stays
> as history, but the procedure it describes is dead.

- **`main` is LIVE PRODUCTION and the ONLY long-lived branch — never work on it directly, never
  auto-target it, never branch a worktree straight from it for story work.** It stays deployable;
  on projects with CI/CD, a push to `main` IS a deploy.
- **Each epic gets one short-lived branch: `epic/<JIRA-KEY>-<slug>`, cut from `main`** at epic
  kickoff (`/cicd-create-epic-sprint`). All of the epic's stories integrate there. This is the
  "one place to send everything" — scoped to the epic, not eternal.
- **Story work happens in a worktree on a `claude/<JIRA-KEY>-<slug>` branch cut from the epic
  branch**, and lands back on the epic branch at close-out (see "The landing").
- **Ad-hoc work outside any epic** — quick fixes, toolkit/system maintenance — takes a short-lived
  `chore/<JIRA-KEY>-<slug>` branch off `main`, merged back to `main` in the same session with
  Daniel's per-action sign-off. The gate is per-repo: the lobby runs
  `python3 .agents/scripts/tests/run_all.py` (it has **no E2E suite and never will** — no
  `frontend/`); deploying repos run the light gate (tests + build), and epic merges add `/cicd-e2e`.
  **The command that does this is `/smh-close-task-merge-tree`** (SCC-49) — invoking it IS the
  sign-off, the same contract `/cicd-push-e2e` carries for an epic. It will not decide the gate
  from prose: `task_preflight.py` derives the lane from the repo and the diff, and a `chore/*`
  branch that touches `backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/` or `.github/`
  is refused outright and handed to `/cicd-push-e2e` — a change that reaches deployable code is a
  product change no matter what its ticket is called.

### Every branch and every commit carries a Jira key (armed 2026-08-07)

- **The key goes immediately after the prefix**: `chore/SCC-11-acli-wrapper`, never
  `chore/fix-SCC-11`. Atlassian's GitHub app joins on the key as a literal string and reads the
  **branch name** too — a correctly-named branch links every commit on it, including one whose
  message forgot the key.
- **The key must match the repo.** Each repo declares its project in `.agents/jira.conf`:
  `SCC` = the lobby, `AVCH` = AviationChat. An `SCC` key inside AviationChat is **rejected** — that
  is the guardrail working, not friction to route around.
- **`commit-msg` is in ENFORCE mode** (`.agents/scripts/git-hooks/JIRA-ENFORCE`, tracked). A commit
  with no valid key for that repo is refused outright. Merge/revert/fixup/squash messages and
  in-progress rebases are exempt. Bypass once with `--no-verify`; disarm by deleting the flag.
- **A rejected commit is a no-op** — the staged set is untouched, nothing to undo.
- **Operating the board itself** (reading tickets, JQL, transitions, minting) is its own rule:
  `.agents/rules/jira.md` — the `acli` cheat-sheet, flag traps, and the ticket↔file join. The board
  is reachable from any shell-capable agent; no MCP or per-platform config exists or is needed.
- **The epic reaches `main` exactly one way: `/cicd-push-e2e`** — the full gate (backend suite +
  frontend build + `/cicd-e2e` GREEN) plus Daniel's explicit sign-off, then the merge. An agent
  never merges to `main` on its own initiative. The epic branch is deleted after it merges:
  branches are short-lived by design; nothing accumulates.

## The write gate — keyed on WHERE a write lands, not on the act

| Destination | Permission |
|---|---|
| Your own `claude/*` story branch (commits **and** pushes) | **FREE** — no approval, loops/retries fine |
| The epic branch (`epic/*`) — a story landing | **Daniel's sign-off** — his in-the-moment "approved", or invoking `/cicd-update-sprint-memory` (which IS the sign-off) |
| A `chore/*` branch (commits and pushes) | **FREE** — the merge back to `main` is what's gated |
| `main` | **Only through `/cicd-push-e2e`** (epic merge, full gate + sign-off) or **`/smh-close-task-merge-tree`** (task merge — preflight + the lane's gate; invoking it IS the sign-off), or Daniel's direct in-the-moment ask. Never on an agent's own initiative. |

Approval for an epic-branch landing or a `main` merge is **per-action and never carries forward**.
One "approved" lands one story; the next needs its own.

**Enforcement — two layers, and only the first one counts.**

1. ⭐ **`.githooks/pre-push` (SCC-77) — this is the gate.** It refuses any push landing on `main`
   without a single-use approval token, and spends the token on the way through. The two `main`
   doors mint it at their sign-off step (`.agents/scripts/git-hooks/mint-push-token.sh`), after the
   merge commit exists and immediately before the push. The token lives in the **common** git dir,
   so every worktree on the machine shares exactly one; it records the sha it was minted for, so
   anything committed after the sign-off is refused. Armed by the tracked
   `.agents/scripts/git-hooks/MAIN-PUSH-ENFORCE`; bypass once with `git push --no-verify`.
   Pure POSIX `sh` **on purpose** — see below.
2. `require-push-approval.py` **PreToolUse hook** (canonical source `.agents/hooks/`, deployed to
   every `.claude/hooks/`) — prompts earlier and reads better, but it is Claude-only and nothing
   depends on it. `merge_pull_request` (+ GitHub write tools) is gated in `.claude/settings.json`.
   It only ever sees the **agent's** Bash tool; the operator's own terminal is never affected.

⛔ **Why layer 1 refuses to depend on an interpreter.** Layer 2 was, for weeks, the *entire* claimed
enforcement — and it had never executed once. `.claude/settings.json` invoked it as
`powershell -NoProfile -Command "python ..."` and the Mac has **neither** binary (only `pwsh` and
`python3`), so it exited 127 in silence on every push, as did all four SessionStart hooks. Six
merges reached `main` on one sign-off (SCC-64 → SCC-69, 2026-08-09) with nothing in the way. A git
hook is the only layer both machines, all four agent platforms, and the operator's own terminal
share — so the gate is `sh`, with no interpreter probe and no Python anywhere in its path.

**What this buys, and what it does not.** An agent can write files, so an agent can write a token.
This is not a security boundary against a determined agent and must not be described as one. It
converts a silent violation into a deliberate, traceable one, and it closes the drift failure this
rule keeps losing to — a close-out command whose body stays in context and still reads exactly as
valid on task six as on task one. Merges via `gh pr merge` or the GitHub web UI never reach a local
hook at all; that gap is tracked under SCC-75.

## A commit is not done until it is pushed

**`git commit` and `git push` are ONE action. Never end a turn, a step, or a command with a commit sitting
unpushed.** An unpushed commit is invisible to every other machine and to the operator, who then has to
discover and push it by hand — which is exactly the manual sync this toolkit exists to remove.

This applies to **every repo you touched**, not just the one the work started in. A `/smh-sync-agents` run
writes to the lobby *and* each maintained project, so a change to one master file dirties three repos;
committing the one you were thinking about and leaving the other two is the common form of this failure.
Sync also runs *after* commits sometimes — re-check `git status` at the end and commit-and-push whatever
the sync just wrote.

**Close every piece of work with this, per repo touched:**

```bash
git status --short                                   # must be empty
git rev-list --left-right --count <branch>...origin/<branch>   # must be "0 0"
```

`0 0` + clean, in **every** repo, or the work is not finished. State the result per repo — an unverified
"pushed" is how this hides.

⛔ The only exception is a story branch mid-flight, which is governed by "The landing" below: its commits
stay local until the landing pushes `HEAD:epic/<JIRA-KEY>-<slug>`. That is about *which ref* receives the push, never
a licence to leave work uncommitted or a landing unpushed.

## The landing — one story, one clean push

The story lands on its **epic branch** at close-out (`/cicd-update-sprint-memory` Step 7) or on
Daniel's in-the-moment "approved". It merges **from inside the worktree**, never by checking out the
epic branch in the shared checkout:

```bash
git fetch origin epic/<JIRA-KEY>-<slug>
git merge origin/epic/<JIRA-KEY>-<slug>        # absorb it INSIDE the worktree — conflicts surface here, isolated
git push origin HEAD:epic/<JIRA-KEY>-<slug>    # THE landing
```

⛔ **Do NOT push the story branch itself.** The **local** branch is the rollback point, and it survives
a failed landing push completely untouched. Pushing story branches on every landing is what left 10
stale `claude/*` on origin by 2026-07-27.

**A story branch reaches origin exactly one way: `/cicd-park`.** That is the entire point of park —
*"the ONLY thing that makes the work portable"* — and `/cicd-resume` reads `git ls-remote --heads origin
'refs/heads/claude/*'` to find in-flight work. The epic branch, by contrast, LIVES on origin — park
pushes it too, and resume checks it out on the new machine.

**The invariant this buys: a `claude/*` branch on origin means "parked, in-flight, on another machine."**
Nothing else. Keep it true — it is what makes `/cicd-resume` trustworthy on a cold machine.
(`incident-*` branches come from the Epic-16 incident pipeline, not story flow; they are outside this rule
and must not be swept by it.)

Checking out the epic branch in the shared checkout to merge is **wrong** — the shared checkout stands
on `main` and stays there; pulling story landings through it drags other teams' uncommitted work into
your merge. If the landing merge conflicts, it conflicts in the isolated worktree: **STOP and report**,
never force-push, never blind-rebase.

**Board files live on the epic branch too.** `sprint-status.yaml`, `active-context.md`, and story
files are edited in the story worktree (or on the epic branch directly at close-out) — never in the
shared `main` checkout, which only advances when the epic merges. This is what makes the shared
checkout boring: it is always exactly production.

## Safe-commit mechanics (always — inside the worktree too)

- **Commit your OWN work via explicit paths:** `git add path/one path/two …`.
- **NEVER `git add -A`, `git add .`, or `git add -u`** — they sweep other parallel work (other
  agents/teams, or Daniel's own uncommitted changes) into your commit. This is the most important rule,
  and the worktree does not repeal it.
- **Verify the staged set first:** `git diff --cached --stat` must show ONLY your files. If anything
  else appears, unstage it (`git restore --staged <path>`) before committing.
- **Scope the commit message** to your task/story only, and **lead the subject with the repo's Jira
  key** (`SCC-11 fix(sync): …`). The `commit-msg` hook rejects a subject without one.
- **Hook output is invisible in VS Code's Source Control panel** — it goes to `View → Output → Git`.
  A commit made from the panel that a hook merely *warns* about looks like a clean success. This is
  how a wrong-key commit reached AviationChat's `main` on 2026-08-07, and it is why the gate is
  armed rather than warning.
- **If a push is rejected** (remote moved under you), **STOP and report.** Do not force-push, and do
  not blind-rebase while other uncommitted work sits in the tree.

### ⛔ Pin the merge TARGET, not just the source — `-C` on every call, and assert before you merge

Every guard above protects the branch you are merging **from**. Nothing protects the branch you are
merging **onto**, and on 2026-08-11 that gap put a production merge commit on a sibling lane's
branch: `cd <worktree> && git checkout main` ran in one step, and a **bare** `git merge <lane>` ran
in a later one, by which point the working directory had reset to the shared checkout — which was
standing on `chore/SCC-89-…`. It reported success. The output, the changed-file list and the commit
message (`-> main`, because that is what was typed) were all indistinguishable from a correct merge.

- **A `cd` is not a lock.** Pass `-C "$REPO"` on every `git` invocation rather than relying on where
  a previous step left you.
- **Assert the target immediately before merging**, and let it stop you:

  ```bash
  test "$(git -C "$REPO" rev-parse --abbrev-ref HEAD)" = "main" || { echo "NOT ON main — STOP"; exit 1; }
  ```

- **On the two `main` lanes this assertion is already mechanical (SCC-77).**
  `mint-push-token.sh` **refuses to mint unless `HEAD` is `main`**, and it is called between the
  merge and the push — so a token cannot be minted from a sibling lane, and a merge that landed on
  the wrong branch cannot produce one. That covers `/cicd-push-e2e` and
  `/smh-close-task-merge-tree`. It does **not** cover a bare `git merge` typed by hand, which is why
  the assertion above stays the rule rather than the fallback.

- **Recovery, if it happens anyway — do not reset and do not force.** The merge commit is usually
  correct in every way except which pointer moved. Verify its tree carries nothing from the wrong
  branch (`git diff --name-only <main-tip> <sha>`), confirm its first parent is `main`'s tip
  (`git log -1 --format='%p' <sha>`), then `git merge --ff-only <sha>` from the tree that holds
  `main`. The sibling branch keeps its uncommitted work untouched.

See `_artifacts/_memory/nothing-guards-the-merge-target.md`.

## Sync-first — check the remote before you land

Phone and desktop share branches, so landing from a **stale** branch is what causes the
diverge → rejected-push tangle. Before the landing push:

1. **Fetch and compare:** `git fetch origin epic/<JIRA-KEY>-<slug>`, then check whether you are behind
   (`git rev-list --count HEAD..origin/epic/<JIRA-KEY>-<slug>` > 0).
2. **If behind, merge `origin/epic/<JIRA-KEY>-<slug>` into your story branch first** (the landing block above
   does this by default) so you never land on top of a stale base.
3. **If it will not merge cleanly**, **STOP and flag it** — hand Daniel the situation. Do NOT run a
   blind merge/rebase, and never force-push.

The same applies one level up: before `/cicd-push-e2e` merges an epic into `main`, it first merges
`origin/main` INTO the epic branch (absorbing any hotfixes that shipped mid-epic), re-gates, and only
then merges to `main` — so `main` never receives an unresolved conflict.

## Always

- **Clear the Dummy GitHub Token:** The Antigravity IDE automatically injects a dummy `GITHUB_TOKEN` into the agent's environment as a sandbox security measure. Because Git and the `gh` CLI prioritize this environment variable over the Windows Credential Manager, it causes authentication failures. **Before running any `git` or `gh` commands, you MUST clear this variable** by prefixing the command or running: `Remove-Item Env:\GITHUB_TOKEN -ErrorAction Ignore; <command>`.
- **Validate CI/CD credentials**: Before landing on a deployment-triggering branch (`main`), verify that the target repository's required secrets and variables are set up on GitHub using `gh secret list` and `gh variable list` (WIF-based workflows need neither — check what the workflow actually references). If credentials are missing, STOP and notify Daniel before proceeding.
- The `walkthrough.md` **"Your Actions"** section records what landed — the branch, the commit range,
  and anything Daniel still has to do (an epic promotion via `/cicd-push-e2e`, a live check). It is no
  longer a `git add` command block, because the agent already ran it.

> **Web/mobile sessions** follow the same model with lighter mechanics — see `mobile-mode.md`
> → Override 1. It shares this rule's safe-commit mechanics and Sync-first.
