---
IsArtifact: true
ArtifactMetadata:
  title: SCC-41 / AVCH-50 — the autopilot runs each story in its own worktree
  type: walkthrough
  date: 2026-08-09
---

# SCC-41 / AVCH-50 — the autopilot runs each story in its own worktree

Plan: [implementation_plan.md](implementation_plan.md)
Branches: `chore/SCC-41-autopilot-worktrees` (lobby) · `chore/AVCH-50-autopilot-worktrees` (AGY)

The autopilot now opens the story's own git worktree before Stage 1, runs every stage inside it, and on
its own green gate commits the tree and moves the ticket to **In Review**. It still never pushes, never
touches `main`, and never marks a story `done`.

## Your Actions

Read first, because it changes what you type:

1. **Launch from the epic branch.** The engine cuts the story tree from whatever `PROJECT_ROOT` has
   checked out, and refuses to start unless that is an `epic/*`. Switch there first, or pass
   `-EpicBranch epic/<KEY>-<slug>`. It refuses rather than guesses — a story branched off `main` cannot
   be landed.
2. **Nothing to commit by hand any more.** On green the run leaves the work committed on
   `claude/<KEY>-<story-slug>`, the story at `review`, and the ticket at In Review with its Dev Record.
   Your step is `/sudo-update-sprint-memory` — it lands the branch on the epic branch, flips `done`, and
   prunes the tree.
3. **⚠️ First run must be `-DryRun`.** See Evidence — none of this has been executed. `-DryRun` creates
   nothing and prints the tree, branch and base it *would* use. Then a small story at `-MaxStage 2`, on
   **each** engine (deepseek shares the claude script, so it rides along).
4. **Two branches to merge**, in either order — they are independent files in independent repos.
   `chore/SCC-51-artifact-budget-standard` is still unmerged and also touches the SOP page; whichever of
   SCC-41/SCC-51 lands second will need `git merge origin/main` first (never a rebase — it is pushed).

## Task Checklist

- [x] Ground-truth the plan against both repos before editing
  - Found the ticket had to split (AGY's armed gate answers only to **AVCH**, and its own `.agents/INDEX.md`
    forbids widening `jira.conf`) → minted **AVCH-50** for the engine half.
  - Found P3's dependency cleared: SCC-49 is on `main` @ `64b2aa9`, so `jira_feed.py devrecord` exists.
  - Found the epic branch is the **only** source of the Jira key → it became a launch precondition.
- [x] **P1 — the worktree**, both engines
- [x] **P2 — the orchestrator commits**, both engines
- [x] **P3 — ticket to In Review + Dev Record**, both engines
- [x] Two pre-existing opencode gaps, both inside the edited region
- [x] Lobby: 3 launchers + 3 generated mirrors + the loop spec + the SOP page
- [x] Record honestly what was NOT verified, in the places a reader hits

## What changed, and why it is the shape it is

### The tree is what makes the result *closeable* — that is the payoff, not tidiness

`/sudo-update-sprint-memory` Step 7:

> `git rev-parse --abbrev-ref HEAD` must be a **`claude/*`** branch (inside the story worktree). If HEAD
> is the epic branch or `main`, this story wasn't worked in a worktree — **do NOT land**.

The autopilot worked on whatever branch the checkout happened to be on. So the last step of the intended
flow — "I read the walkthrough, then run `/sudo-update-sprint-memory` and it closes the whole thing out"
— could not run at all. Not "not automated yet": a dead end. Isolation is the other half, and it is real
(the test gate used to see sibling lanes' uncommitted edits, so a red belonged to nobody), but the
landing is the reason this was blocking.

`worktree-per-story.md` has listed **"the autopilot engines"** in its Trigger from the start. The engines
simply never honoured it. Layout is that rule's, verbatim:
`.claude/worktrees/<story-slug>/` on `claude/<JIRA-KEY>-<story-slug>`, cut from the epic branch.

### Everything moved into the tree, including the artifacts

`_artifacts/` is **tracked** — the run folder has to ride the story branch or it never lands with the
story. So `$WorkRoot` (new) replaces `$RepoRoot` at every stage cwd, both test suites, both
`git diff --name-only $BaselineCommit` scope reads, the pytest-node-id file probe, the story file, and
`sprint-status.yaml`. `$RepoRoot` stays only where it should: locating the script, resolving the epic
branch, and the toolchain fallbacks below. Code and artifacts under one root is also exactly the working
style asked for — the agents move between them without leaving the tree.

The only thing deliberately left in the shared checkout is the monitor tail log
(`_artifacts/_autopilot-run-<story>.log`) — gitignored via `*.log`, and its path has to be known before
the tree exists so the launcher can `tail` it.

### Three things that would have broken on day one

| | Why it breaks | What it does now |
|---|---|---|
| **Workspace trust** | keyed on the exact cwd string; every worktree is a new path. Granting `$RepoRoot` leaves Stage 1 dying on *"this workspace has not been trusted"* | grant moved to `$WorkRoot`, after the tree exists (and skipped on `-DryRun`, since it writes `~/.claude.json`) |
| **Gitignored assets don't travel** | a fresh tree has no `.env`, no `auth_keys/`, no `node_modules`, no venv — the gate dies immediately | `auth_keys/` + the `.env` files copied in; `frontend/node_modules` **junctioned** at the shared copy; the interpreter falls back to the shared `backend/.venv`. A venv and `node_modules` are toolchain, not source — pytest still collects from the worktree's cwd |
| **The shared checkout may be on `main`** | `worktree-per-story.md` says it should be — and then the story file isn't on disk to look up | story resolution falls back to `git ls-tree` against the epic branch; `Get-StoryHead` reads `Status`/`baseline_commit` from the blob until the tree exists |

A pruned worktree leaves a **husk directory** that blocks the next `worktree add`. That is reported
plainly with the exact `Remove-Item` to run — and never `--force`'d over, which would silently adopt
whatever is sitting there as the story's tree.

### The scope prompt had to be inverted, not just repointed

The old text asked agents to mentally subtract other lanes' edits — isolation by please:

> *Any file changed in the working tree that is NOT in the plan's list is a PARALLEL team's uncommitted
> work — do NOT treat it as your scope.*

In an isolated tree that is now false, and harmful: everything dirty **is** this story's. The prompt now
says the opposite — own the whole diff, read and write only under `$WorkRoot`, and *you do not run git*.
Both wordings are kept and selected on the real condition, because `-NoWorktree` still lands in a shared
checkout.

### The orchestrator commits — the agents still never touch git

Same pattern the engine already used for the story-status flip: *the orchestrator owns it, gated on its
own green test result*. `git-policy.md`'s gates hold literally:

- **G2 explicit paths** — the path list is built from three unambiguous NUL-separated git outputs
  (`diff --name-only`, `diff --cached --name-only`, `ls-files --others --exclude-standard`), printed, and
  passed to `git add --`. **`git add -A`/`.`/`-u` appears nowhere in either file** (verified by grep —
  the only matches are the comments saying so). Deliberately *not* a `status --porcelain` parse: that
  encodes renames as a two-field record and quotes exotic names, and a mis-parse means committing the
  wrong file. `--exclude-standard` also keeps the bootstrapped `.env`/`auth_keys` and the junctioned
  `node_modules` out by construction.
- **G3 no push** · **G4 never `main`** — neither engine contains a `git push` at all.

Subject leads with the Jira key so the **armed** `commit-msg` gate passes — and `.githooks/` is tracked,
so it materializes in the worktree and really does fire there. A rejection leaves the work **staged** and
prints git's own message; a swallowed hook message is the most confusing way for this to fail.

### Two opencode gaps closed in the same pass

Both sat inside the region P1 was already editing:

1. **No `.run.lock` at all.** The claude engine has guarded a double-run of the same story since day one;
   this one never did. The worktree fixes isolation *between* stories — it does nothing about the same
   story twice. Added, PID + process-start-ticks (a bare PID is unsafe: the OS reuses a dead process's
   PID, which would make a stale lock look alive), with the matching `finally` release.
2. **The interpreter has never been found.** It resolved python as `$RepoRoot\.venv\...` **only**.
   AviationChat has `backend/.venv` and no root `.venv` — so that lane silently fell through to system
   python, which has no pytest, on every run it has ever done here. Now uses the claude engine's
   candidate list.

## Evidence

| AC | Evidence |
|---|---|
| Every stage runs in the story's tree | `$WorkRoot` replaces `$RepoRoot` at 10 sites in the claude engine and 5 in opencode (stage cwd ×4/×2, frontend gate, baseline job, scope-diff reads ×2, node-id probe, sprint-status); 51 / 41 `WorkRoot` references total |
| A resume re-binds, never re-cuts | `Find-StoryWorktree` matches the **slug** in the branch, then the path leaf, from `git worktree list --porcelain` — per the rule's "Match by the `<story-slug>` in the branch/path, not by cwd" |
| The commit obeys G2/G3/G4 | `grep -n 'add -A\|add \.\|add -u'` and `grep -n 'git.*push'` over both engines return **comments only** — no such call exists |
| Both engines parse | `pwsh` `[Parser]::ParseFile` → **PARSE OK** on both (9,705 tokens / claude); `Get-Help -Full` renders |
| The change introduces no new static defects | PSScriptAnalyzer (Error+Warning, house rules `PSAvoidUsingWriteHost` + `PSAvoidUsingEmptyCatchBlock` excluded) diffed against the **pre-change baseline**: claude 20 → 22, opencode 8 → 12. Every new one is `PSUseSingularNouns` (cosmetic, and `Get-ProcStartTicks` was already in the baseline) plus one `PSReviewUnusedParameter` on `$JiraKey` that is a false positive — it is read at `autopilot-dev-story-opencode.ps1:292` |
| Lobby suite green | `python3 .agents/scripts/tests/run_all.py` → **8/8 files passed**, both before and after the `origin/main` merge |
| The generated mirrors were not left stale | all three (`.claude/commands/autopilot_claude.md`, `…_deepseek4.md`, `.opencode/commands/autopilot_opencode.md`) verified byte-identical to their `.agents/` source at `HEAD` before copying, and identical after |
| `main` absorbed without losing the other lane's work | `git merge origin/main` (7 commits: SCC-52 + SCC-53) — auto-merged, **zero conflicts**; `git diff origin/main` on the SOP page shows only this change's §10 rewrite |

```
pwsh [Parser]::ParseFile  → PARSE OK  scripts/autopilot-dev-story.ps1
                          → PARSE OK  scripts/autopilot-dev-story-opencode.ps1
PSScriptAnalyzer vs baseline → no new findings of substance (see table)
python3 .agents/scripts/tests/run_all.py → 8/8 files passed
```

## What is NOT verified — read this before the first real run

**No stage of either engine has been executed.** The lane is Windows-only (`powershell.exe`,
`$env:USERPROFILE`, `.venv\Scripts\python.exe`) and this was built on the Mac. Parsing and static
analysis catch syntax and structure; they do not catch a wrong path, a `git worktree add` that fails
against a real repo, a trust grant that misses, or a junction that Windows refuses.

The first real run has to show, **per engine**:

- two concurrent stories cannot see each other's files
- the gate runs green **inside** the tree and finds the right interpreter
- `-ResumeFrom` re-binds to the SAME tree instead of cutting a second one
- the orchestrator's commit passes the armed `commit-msg` hook
- `/sudo-update-sprint-memory` accepts the result and lands it

This is recorded where a reader will hit it, not only here: `autopilot_bmad_dev_loop.md` §11 leads with
it, and the SOP page carries a ⚠️ in §10.

Also **reported, not fixed** (unchanged from the plan): `NEXgen-VR-Director`, `BRKN_Tattoos` and
`Fresh_Workspace_BMAD` carry diverged engine copies and did not get this change; the POSIX port stays out
of scope.

---

## Rolled in mid-flight: the base-drift check now names the overlapping files

Asked for during the build, after another team landed SCC-52 + SCC-53 on `main` while this branch was
open. The question was whether to notify lanes on every merge to `main`. The answer was no — and the
reasoning is worth keeping, because the notification version is the obvious one:

- **"Rebase if needed" is the wrong verb.** `git-policy.md` / `sudo-resume.md` list *rebase a pushed
  story branch* alongside force-push under **Never**. A prompt that suggests it invites the one thing
  the policy forbids. The house move is `git merge origin/main`, and the other lane's own SCC-52 commit
  (`a62e0bd Merge remote-tracking branch 'origin/main' into chore/SCC-52-…`) is that verb in practice.
- **A merge-time ping cannot know whether it matters.** Of the 16 files that landed, exactly **one**
  touched this branch. A 15/16-irrelevant alert trains you to ignore the one that isn't.
- **Interrupting a live lane is itself a hazard.** Absorbing `main` mid-story drags other lanes'
  changes into the diff a review is scoped on — and a `git merge` under a running dev server has
  already wedged this system once.
- **It cannot reach them anyway.** A `post-merge` hook fires only on the machine that merged.

And the check already existed, at the better moment: `task_preflight.py` errors `origin/main has N
commit(s) NOT on <branch> - merge origin/main into this branch first`. What it could not tell you was
whether that mattered. So the improvement is precision, not a new channel:

| | Before | Now |
|---|---|---|
| Behind, files disjoint | `7 commit(s) NOT on <branch>` | `+ no file overlap: origin/main moved on 16 file(s), none of the 8 this branch touched - the merge should be clean` |
| Behind, files collide | *(identical output)* | `+ 2 file(s) changed on BOTH sides - resolve by keeping both sides' facts, never by picking a winner: <paths>` |

**Where it lives:** `wf_common.base_overlap()` (answers the question) + `report_overlap()` (prints it),
so the two preflights cannot drift on the *answer* while disagreeing on the prose — the same failure the
engines' TWINS-BY-CONTRACT note guards against. Callers:

- `task_preflight.check_base` — the task lane, against `origin/main`.
- `closeout_preflight.check_landed` — the **story** lane, against the epic branch, on the not-yet-landed
  path. That is the moment the operator goes and does the landing merge, and it is where the multi-lane
  case actually bites (`worktree-per-story.md`: *"The epic branch moves under you… never assume the base
  you opened on"*).

A no-overlap result is printed deliberately. "Behind, but on files you never touched" is a real answer;
leaving it silent is how a clean absorb reads as an unknown risk. The list caps at 12 names
(`OVERLAP_SHOWN`) but the **count is always exact** — a hundred paths is a wall that gets scrolled past,
which is the same as printing nothing.

**Evidence:** 4 new cases in `test_task_preflight.py` — the disjoint case states "no file overlap" and
does **not** cry conflict; the same-file case names `docs/shared.md` and carries the resolution rule.
`test_task_preflight.py` 39/39 · full suite **8/8 files, 242 cases**.

**Verified on this very situation:** `git merge origin/main` into this branch auto-merged all 7 commits
with **zero conflicts**, and `git diff origin/main` on the one overlapping file shows only this change's
own §10 rewrite — nothing of SCC-52/53's was dropped.
