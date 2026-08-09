---
IsArtifact: true
ArtifactMetadata:
  title: SCC-41 — put the autopilot on worktrees
  type: implementation_plan
  date: 2026-08-08
---

# SCC-41 — autopilot on worktrees, landing through the normal close-out

**Ticket:** SCC-41 (epic SCC-33) · **Branch:** `chore/SCC-41-autopilot-worktrees` off `main` @ `182bee5`

## The target (operator, 2026-08-08)

> The autopilot codes in the worktree; all four agents work there, moving between code and artifacts as
> they go. When they finish I read the walkthrough, the implementation plan, and the Jira ticket — now at
> **review**. Then I run `/sudo-update-sprint-memory` and it closes the whole thing out and moves it to
> **done**.

## Where that flow breaks today — three gaps, verified

**G1 — one shared tree, isolation by prompt.** Both engines pin `$RepoRoot = "$PSScriptRoot\.."`
(claude:293 · opencode:138) and `Push-Location $RepoRoot` every stage, so **every concurrent run edits the
same checkout**. The only guard is an injected prompt: *"Any file changed in the working tree that is NOT
in the plan's list is a PARALLEL team's uncommitted work."* It also poisons the gate — pytest runs from
`$RepoRoot`, vitest from `$RepoRoot/frontend`, so story A's gate sees story B's half-finished edits, and
the red-baseline snapshot only excuses failures that predate the run.

**G2 — close-out REFUSES autopilot stories today.** `/sudo-update-sprint-memory` Step 7:
> *"`git rev-parse --abbrev-ref HEAD` must be a **`claude/*`** branch (inside the story worktree). If HEAD
> is the epic branch or `main`, this story wasn't worked in a worktree — **do NOT land**."*

The autopilot works on whatever branch the checkout happens to be on, so the last step of your flow
cannot run at all right now. **The worktree is what unblocks close-out** — that is the real payoff here,
not tidiness.

**G3 — the autopilot never touches Jira.** Zero matches for `jira`/`acli` in the engine *and* in the
command doc. The ticket moving to `review` does not happen; the orchestrator flips only the story file
and `sprint-status.yaml`.

## The corrected design — artifacts live IN the worktree

My first draft kept artifacts in the main checkout. **Wrong:** `_artifacts/` is **tracked** (886 files in
AGY) while the monitor log is gitignored (`.gitignore:87 *.log`). Tracked artifacts must ride the story
branch or they never land with it.

| Lives in the **worktree** | Lives in the **main checkout** |
|---|---|
| the code · the run folder `_artifacts/epic_<N>/<date>_autopilot-<id>/` (plan, walkthrough, decisions-log) — **tracked, lands with the story** | only `_artifacts/_autopilot-run-<story>.log` — **gitignored**, and the Monitor's stable known-upfront tail path |

One cwd for the agents, everything they read and write in one place — which is your description exactly.
**Resume** locates the worktree by story slug via `git worktree list`, then the run folder inside it
(today it scans `$artifactsRoot` for `*_<slug>`, claude:432-437).

## Three lanes, TWO engines — and they have drifted

`autopilot_claude` and `autopilot_deepseek4` drive the **same** script (`autopilot-dev-story.ps1`;
deepseek only overrides models). Only `autopilot_opencode` has its own
(`autopilot-dev-story-opencode.ps1`). **So the change lands in 2 engines and covers all 3 commands.**

But parity is not symmetric, and two gaps land inside this ticket's blast radius:

| | claude (1500 ln) | opencode (843 ln) |
|---|---|---|
| Workspace trust | 2 refs | **0** — Claude-CLI-only; opencode needs none |
| Concurrency lock `.run.lock` | 5 refs | **0** — nothing stops a double-run of the SAME story |
| Test gate | 34 refs | 15 — much thinner |
| BaselineCommit · ResumeFrom · STORY STATUS · sessions | present | present |

- The **trust step (P1) is claude-engine-only** — that half simply does not apply to opencode.
- The **opencode lane has no run lock at all.** While P1 makes *different* stories genuinely isolated,
  opencode still lacks the *same*-story guard the claude lane has. Add it — small, and squarely this
  ticket's theme.

**⚠️ A live bug found while scoping.** The opencode engine resolves python as `$RepoRoot\.venv\...` only
(line 552). AGY has **`backend/.venv` and no root `.venv`** — so that lane's gate has never found its
interpreter here; it falls through to system python. Pre-existing and independent of worktrees, but it
sits exactly where P1 edits, so fix it in the same pass by adopting the claude engine's two-candidate
lookup.

## The path — three pieces, in this order

### P1 — Worktree (unblocks G1 + G2)
Open `claude/<JIRA-KEY>-<slug>` off the story's epic branch before Stage 1; reuse it on resume, recording
the path in `_pipeline/` so a resume re-binds instead of cutting a second tree. Repoint the stage cwds
(claude:677, 926, 1028, 1108), the frontend gate (1151), and `git diff` (950, 1081) at the worktree.
Pruning stays `/sudo-close-workingtree`'s job.

**⚠️ Two day-one breakers:**
- **Gitignored assets do not travel.** A fresh worktree has no `.venv`, `node_modules`, `.env` or auth
  keys, so the gate dies immediately. Point the toolchain at the main checkout instead of duplicating it
  (junction `node_modules`, copy `.env` + keys) — a venv is a toolchain, not source, and pytest still
  imports from its cwd.
- **Workspace trust is path-keyed** (claude engine only). Every worktree is a new path and needs its own
  entry, or Stage 1 never starts.

### P2 — The orchestrator commits, on its green gate (makes G2's landing real)
Close-out lands with `git push origin HEAD:epic/...` **from inside the worktree** — so commits must exist
or there is nothing to land. Today the engine has almost no git surface: one `git diff --name-only`.

**The script commits, not the agents** — the pattern the engine already uses for story status
(*"the orchestrator owns the flip, gated on its own green test result"*), applied to git: explicit paths,
Jira key leading the subject, **no push**. Agents still never run git, and your flow needs no
hand-commit before close-out.

### P3 — Jira → `review` + the Dev Record (closes G3) — **depends on SCC-49**
On a green gate, the orchestrator also moves the **ticket** to `review` and files the Dev Record, so the
board matches what landed. Uses SCC-49's `jira_feed.py devrecord`, so **P3 cannot land until SCC-49 does.**
P1 and P2 have no such dependency.

## Risks

1. **Resume re-binding** — the riskiest edit. A resume that fails to find the tree cuts a second one and
   silently splits the story's work. Bind on slug, record the path, verify with `-DryRun` + `-ResumeFrom`.
2. **Landing conflict with SCC-49** — only `sudo_workflows_testing.md` overlaps; resolved by merging main
   before I push.
3. **Two diverged engines**, project-local — every change lands in both, and the opencode one is thinner,
   so "done in claude" is never done. Verify each lane by running it, not by reading the diff.
4. **Pre-existing, flagged not fixed:** venv paths are Windows-only and the commands drive
   `powershell.exe` — this lane has never run on the Mac. Reported, not widened into this ticket.

## Verification

`run_all.py` · `check_maps.py` · then a **real run per engine** on a small AGY story — `/autopilot_claude`
AND `/autopilot_opencode` (deepseek shares claude's script, so a `-DryRun` covers it). Each must show:
two concurrent stories cannot see each other's files · the gate runs green inside the worktree, finding
the right interpreter · `-ResumeFrom` re-binds to the SAME tree · the orchestrator's commit passes the
armed `commit-msg` hook · `/sudo-update-sprint-memory` accepts the result and lands it. A worktree change
only reasoned about is not verified.

## Scope

**AGY_AVIATIONCHAT** — both engines (`autopilot-dev-story.ps1` + `-opencode.ps1`) — plus the three
`autopilot_*.md` commands, the lobby spec `.agents/reference/autopilot_bmad_dev_loop.md` (never mentions
worktrees), and the SOP quick-reference. `NEXgen-VR-Director`, `BRKN_Tattoos`, `Fresh_Workspace_BMAD`
carry diverged copies — reported, not touched.

**Out of scope:** SCC-38 · SCC-42 · POSIX port.

---

## What the build changed about this plan (2026-08-09)

Four things the plan did not account for. Three were found by ground-truthing it against both repos
before any edit; the fourth is a correction to the plan's own verification claim.

### 1. The ticket had to split — AGY will not accept an SCC key

The engines live in `Projects/AGY_AVIATIONCHAT`, whose `.agents/jira.conf` binds it to **AVCH** behind an
**armed** `commit-msg` hook, and whose `.agents/INDEX.md` rules out the easy fix in writing:

> `jira.conf` — "One shared copy would make the gate reject AviationChat's own work items and accept the
> lobby's."

So widening AGY's keys was a settled no before it was asked. The work splits on the repo boundary:

| Ticket | Repo | Carries |
|---|---|---|
| **SCC-41** | lobby | the 3 `autopilot_*.md` launchers + their 3 generated mirrors, `autopilot_bmad_dev_loop.md`, the SOP page |
| **AVCH-50** | AGY_AVIATIONCHAT | both engines — `autopilot-dev-story.ps1`, `autopilot-dev-story-opencode.ps1` |

### 2. P3 is unblocked, and reaches the center rather than vendoring

SCC-49 landed on `main` (`64b2aa9`), so `jira_feed.py devrecord` exists. It exists **only in the lobby** —
AGY is a thin project and vendors no toolkit — so the engine resolves it at `$RepoRoot\..\..\.agents\
scripts\jira_feed.py`. That is the same "project sits under the center" assumption `$PSScriptRoot\..`
already makes, one level further out.

### 3. The epic branch is the only source of the Jira key — so it became a precondition

The plan said to cut the tree from the epic branch without saying how the engine would know which one.
It cannot be computed: **BMAD's epic number and the Jira epic key do not track each other** — BMAD epic 19
lives on `epic/AVCH-18-adk-2x-runtime`, and the commit that made it so says exactly that
(`AVCH-18 fix(epic-19): repoint the epic to AVCH-18, not the duplicate AVCH-49`). Story files carry no key
either.

Resolution: the base is **the shared checkout's current branch**, which must be an `epic/*`, exactly as
`worktree-per-story.md` describes a human doing it ("check out the epic branch before opening the
worktree"). `-EpicBranch` overrides; anything else is a hard refusal, not a guess — a story cut from
`main` cannot be landed. Two consequences fell out: the branch name takes the **story's** key (found the
way `jira_feed.py mint` dedupes) and falls back to the **epic's**, so the armed gate always has a real
work item; and the story-file lookup gained a `git ls-tree` fallback against the epic branch, because a
shared checkout parked on `main` — which `worktree-per-story.md` says is where it should stand — does not
have the story file on disk at all.

### 4. Verification: the plan asked for a real run. It has not happened, and could not here.

The plan's Verification section says "a worktree change only reasoned about is not verified." That still
stands, and it is **not satisfied**. This lane is Windows-only — `powershell.exe`, `$env:USERPROFILE`,
`.venv\Scripts\python.exe` — and the work was done on the Mac. What was actually run is in the
walkthrough's Evidence table: a `pwsh` parse of both engines, a PSScriptAnalyzer pass diffed against the
pre-change baseline, and the lobby suite. Those catch syntax and structure. They do not catch a wrong
path, a `git worktree add` that fails on a real repo, or a trust grant that misses.

**The gap is recorded where a reader will hit it, not only here:** `autopilot_bmad_dev_loop.md` §11
("What is NOT yet proven") now leads with it, and the SOP page carries a ⚠️ in §10.

### Two engines, one contract — the plan's Risk 3

The plan flagged "done in claude is never done" as a standing risk. The two blocks are now written
**function-for-function identical** and both files say so in the parameter block ("TWINS BY CONTRACT"), so
`diff` is the drift detector. That is the same convention `link-memory.ps1`/`.sh` already use here. A
shared dot-sourced module would end the drift structurally, but it adds a new load path to a lane that
cannot be executed on this machine — deliberately not taken in this pass.
