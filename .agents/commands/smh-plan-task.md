---
description: Plan a WHOLE Task and all its subtasks in one shot — propose the breakdown, mint the Subtasks on the operator's go, then per subtask write an implementation plan, audit it, cut its worktree and push its branch, and update its ticket; finish by labelling the set with /smh-label-tasks so you can see which lanes run in parallel. The Task lane's answer to "write all the stories first". Ends at ONE approval stop for the whole set. Use when the user says "plan this task" / "smh plan task".
platforms: [opencode, antigravity, claude, codex]
---

# /smh-plan-task — Plan the whole Task, subtasks and all (SCC-155)

> **Rules in force for this command:**
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — including its **batch clause**, which this command
>   is the only writer of: one recorded approval covers the plans it lists, and nothing else
> - `.agents/rules/jira.md` §Subtasks — the SCC-119 hierarchy, and guardrail 2 (placement is the
>   operator's) and 3 (minting off your own reading is speculative work)
> - `.agents/rules/worktree-per-story.md` — every commit-producing lane opens a worktree, Task
>   lanes included (SCC-62); §"cwd is not intent" is why every branch below is pinned from
>   command output
> - `.agents/rules/artifacts-always-first.md` — each lane's plan lives in **that lane's tree**, at
>   `_artifacts/_main/<YYYY-MM-DD>_<slug>/implementation_plan.md`
> - `.agents/rules/git-policy.md` — explicit paths only, never push `main`

**The Task lane's version of "write all the stories first."** BMAD's parallel lever needs every
story on disk before the set can be compared; the Task lane had no equivalent, so subtasks were
planned one at a time and `/smh-label-tasks` had nothing to ground. This command is that missing
step: it plans the **whole** Task at once and leaves every lane grounded, cut, pushed and labelled.

> Flow position: **`/smh-plan-task`** → *(per lane)* `/smh-quick-dev` → `/smh-code-review` →
> **[STOP]** → `/smh-close-task-merge-tree`. The parent closes LAST.

## 🛑 MANDATORY RULES

1. **PROPOSE the breakdown, then STOP.** Nothing is minted until the operator says go
   (`jira.md` guardrails 2 and 3). This is the single most important stop in the command: an
   agent that mints its own reading fills the board with work nobody chose.
2. **ONE approval stop at the end, and the operator's words are the artifact.** You never write
   the word `approved` yourself, in a plan, a heading, or a button label — recording your own
   approval is precisely how the plan-first gate gets bypassed.
3. **Every lane is grounded before the labeller runs.** A plan that is not committed and pushed
   does not exist for the next machine, and an ungrounded lane locks the whole set.
4. **No deployable paths.** If a subtask's plan reaches `backend/`, `frontend/`, `firebase/`,
   `functions/`, `mobile/` or `.github/`, that lane is not Task work — say so and route it to
   `/cicd-push-e2e`. There is no override.

## Step 0 — Resolve the repo and the parent (FIRST) — from command output, never belief

```bash
REPO=$(cd "<the path you resolved>" && git rev-parse --show-toplevel)
echo "Repo: $(basename "$REPO")"
acli jira workitem view <PARENT-KEY>        # read its ACCEPTANCE block and its type
```

The parent must be a **`Task`**. An `Epic` is refused — its children are Stories (or Tasks that own
their own Subtasks); use `/cicd-create-epic-sprint` for the former and run this against one of the
Tasks for the latter. A `Subtask` is refused too: `hierarchyLevel: -1` is the floor and nothing
nests under it.

Move it to `In Progress` now, at the plan, not at the merge (SCC-113):

```bash
python3 .agents/scripts/jira_feed.py start --key <PARENT-KEY> --apply    # PC: `python`
```

Read the exit code — `0` carry on · `3` stop and ask (it is `Blocking`/`In Review`/`Deferred`) ·
`2` stop, the key is wrong · `4` transport failure, carry on and retry later.

## Step 1 — Fix the parent's checkable list

From, in authority order: the ticket's **ACCEPTANCE** block → the operator's stated intent this
session → you write 2–6 checkable statements and echo them. **Every item must be checkable by a
command or an inspection** — that is what makes the subtasks provable later. If the intent will not
reduce to checkable statements, say so and stop.

## Step 2 — ⭐ PROPOSE the breakdown, then STOP

Read the parent's checkable list and ask **one** question of each piece of work in it:

> **Does this piece earn its own `chore/<KEY>-<slug>` branch in its own worktree?**

- **No** → it stays a checklist line in the parent's plan or `ACCEPTANCE` block. Three edits in one
  commit are not three subtasks, and a ticket with no branch is a row nothing will ever write to.
- **Yes** → it is a `Subtask` under the parent.

Print one line per proposed subtask, each naming the branch it would get and the acceptance items
it carries. **If nothing clears the bar, say so — one lane is the normal answer for most Tasks**,
and the operator's ruling on SCC-155 itself was exactly that.

⛔ **STOP HERE.** Write nothing to the board until the operator says go.

On the go, mint each one — parented to this ticket, bare, no `--assignee`:

```bash
acli jira workitem create --project <PROJ> --type Subtask --parent <PARENT-KEY> \
  --summary "…" --description "…"
```

## Step 2.5 — ⭐ Pick the MODE: one consolidated lane, or a lane per subtask (SCC-170)

> Governed by `.agents/rules/work-consolidation.md` — rule 2 ("when able, ONE worktree and ONE branch
> for the whole Task") and rule 1 ("look for a home before you mint"). Read it if this is the first
> consolidated lane you have cut.

**Answer this before you cut anything, and say why in one line.** Two modes exist and the choice is
yours — the operator ruled it judgment, not ceremony (*"when able use one workingtree/branch to
develope the whole ticket including subtasks"*).

| | **CONSOLIDATED** — one lane for the whole Task | **PER-SUBTASK** — a lane each |
|---|---|---|
| When | same repo, same lane class, no genuine need for parallelism — **the default when able** | the subtasks really do run side by side (a 🟢 set from Step 4), or different repos |
| Worktree / branch | **ONE**, keyed by the **parent**: `chore/<PARENT-KEY>-<slug>` | one per subtask, keyed by the subtask |
| Plan | **ONE** `implementation_plan.md` with N part sections | one per lane |
| Manifest | `riders:` lists **every** subtask key, written at cut time | no riders |
| Commits | **the SUBTASK's key leads each commit** — each child's dev panel shows its own commits, and a part reverts as a unit | the lane's own key |
| Gate | **ONCE**, at the tip, through the receipt writer | once per lane |
| Close-out | ONE ceremony: riders flip first, parent last | one per lane |

**Cutting a CONSOLIDATED lane** — the whole Step 3 loop collapses to one tree:

```bash
git -C "$REPO" fetch origin                                   # ⛔ the base is origin/main, never a bare `main`
git -C "$REPO" worktree add .claude/worktrees/<slug> -b chore/<PARENT-KEY>-<slug> origin/main
git -C "<the new tree>" branch --unset-upstream               # a start-point of origin/main sets upstream to MAIN
python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>   # PC: `python`
BRANCH=$(git -C "<the new tree>" rev-parse --abbrev-ref HEAD)
echo "Lane: $BRANCH"
```

⛔ **`git branch --unset-upstream` is not optional.** Branching from `origin/main` sets this lane's
upstream to `main` itself, so a later bare `git push` targets **main** and a bare `git status` reports
"ahead of main" — this lane hit exactly that.

Then write ONE plan with a part section per subtask, and ONE `task.yaml` declaring them all:

```yaml
task_key: <PARENT-KEY>
primary_repo: <repo folder name>
branch: chore/<PARENT-KEY>-<slug>
close_command: smh-close-task-merge-tree
secondary_repos: []
riders: [<SUBKEY-1>, <SUBKEY-2>, …]        # one line, flow form — a block list is UNREAD
```

**Build order is Step 4's output, not a preference.** Run the labeller first if the set is large: parts
that share a file are sequenced, and whichever part makes the *rest of this lane* cheaper goes first.
Then run `/smh-quick-dev` once per part **inside that one tree**, and close the whole thing with a
single `/smh-close-task-merge-tree --expect-key <PARENT-KEY>`.

**If the lane must ship before every part is built:** write `landing_mode: partial` into `task.yaml` and
**trim `riders:` to the subset that actually landed.** The declared riders flip, the parent stays open,
and the remainder becomes the next `chore/<PARENT-KEY>-<slug2>` lane. `task_preflight.py` checks the
trim against the lane's commits and refuses a rider that leads no commit there.

## Step 3 — Per subtask: plan it, audit it, cut it, push it

**PER-SUBTASK mode only** — in CONSOLIDATED mode Step 2.5 already cut the one tree, and the per-subtask
plan/audit/cut/push loop below collapses into part sections of that lane's single plan.

**For each subtask, in dependency order.** Everything here happens **inside that lane's own tree**.

```bash
git -C "$REPO" worktree add .claude/worktrees/<slug> -b chore/<SUBKEY>-<slug> main
python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>   # PC: `python`
BRANCH=$(git -C "<the new tree>" rev-parse --abbrev-ref HEAD)
echo "Lane: $BRANCH"
```

Then, in that tree:

1. **Write `implementation_plan.md`** into `_artifacts/_main/<YYYY-MM-DD>_<slug>/`, right-sized.
   Each acceptance item maps to a step, and **each step names the assertion that will prove it** —
   `/smh-quick-dev` Step 2 turns those into the checks it writes RED.
2. **Write `task.yaml` beside it** — this is what grounds the lane for the labeller, so it is not
   optional:
   ```yaml
   task_key: <SUBKEY>
   primary_repo: <repo folder name>
   branch: chore/<SUBKEY>-<slug>
   close_command: smh-close-task-merge-tree
   secondary_repos: []
   ```
3. **Invoke `/smh-self-audit`** on that plan. It appends `## Self-Audit (<date>)` and a canonical
   `Audit verdict: GO | NO-GO`. **A NO-GO stops that lane** — fix the plan and re-audit. Do not
   carry a NO-GO into the batch stop.
4. **Commit and push the lane** (explicit paths; the key leads the subject):
   ```bash
   git -C "<tree>" add _artifacts/_main/<date>_<slug>/implementation_plan.md \
                       _artifacts/_main/<date>_<slug>/task.yaml
   git -C "<tree>" commit -F <message-file>     # ⛔ backticks in -m "…" EXECUTE
   git -C "<tree>" push -u origin chore/<SUBKEY>-<slug>
   ```
   **Unpushed is stranded** — branches travel between machines, worktrees do not.
5. **Update the subtask ticket** so the board points at the plan:
   ```bash
   acli jira workitem edit --key <SUBKEY> --yes --description "…checkable list… \
     Plan: _artifacts/_main/<date>_<slug>/implementation_plan.md on chore/<SUBKEY>-<slug>"
   ```
   The tree stays the single source of truth; the ticket carries the pointer.

## Step 4 — Label the set

```bash
/smh-label-tasks <PARENT-KEY>
```

Every lane is now grounded by a **committed plan on a pushed branch**, which is the strongest
evidence short of code. Print its table unedited: the 🟢 set can run side by side, 🔒 rows name
what they wait on, ⚡ marks the lanes small enough for one light `/smh-quick-dev` pass.

## Step 5 — ⭐ ONE approval stop, for the whole set

Present, in one message:

- every subtask, its branch, its plan path, and its `Audit verdict:`
- the parallel table from Step 4
- anything a lane's audit flagged that the operator should rule on

Then **STOP and wait.** Per `000-PLAN-FIRST-GATE`, these are **not** approval: "ok" · "looks good" ·
"continue" · clicking an option you wrote · being told to do the work · answering your clarifying
question · the operator **correcting** a plan (a correction narrows it, and you stop again).

**On approval, record the operator's VERBATIM words** into each approved plan, under its audit
section:

```markdown
**Batch approval (2026-08-14):** "<the operator's exact words, this turn>" — covers the plans
listed in `/smh-plan-task <PARENT-KEY>` Step 5: <SUBKEY-1>, <SUBKEY-2>, …
```

**Then commit it in EACH lane's own tree and PUSH — and record the resulting sha into the same
line, as `— recorded at <sha>`.** Three things about that sentence are load-bearing, and all three
were missing (SCC-155 review #17/#18):

- **The sha, or the downstream check has nothing to compare against.** `/smh-quick-dev` Step 1.5
  says the plan must be unchanged *since the commit that recorded the approval* — with only a date
  and a quote on the page, an agent has one computed value and no second operand, and an agent that
  wants to proceed will call it unchanged. Write the sha and the comparison becomes real.
- **Each lane's own tree.** The plans were committed back in Step 3 in **N different worktrees**,
  on N different branches. There is no single tree where "commit that with the plans" means
  anything; naming the wrong one silently drops the approval from every other lane.
- **Pushed, per this command's own MANDATORY RULE 3** — *a plan that is not committed and pushed
  does not exist for the next machine*. The approval quote is the artifact that unlocks the batch
  path, so an unpushed one strands the whole batch on this laptop. **That quote is the artifact** — the same pattern the main-write gate
uses for merges (SCC-37), and for the same reason: an agent can write a plan, so it can write the
word "approved"; it cannot manufacture the operator's sentence.

⚠️ **The batch approval covers those plans as they stand.** Edit a plan afterwards and its gate
re-arms — that lane stops for its own approval at `/smh-quick-dev` Step 1.5.

## Report

- `Parent: <PARENT-KEY> — <n> subtasks minted` *(or "no breakdown: one lane, and why")*
- one row per lane: `<SUBKEY> · chore/<SUBKEY>-<slug> · plan @ <path> · Audit verdict: GO · pushed`
- `Parallel: <the 🟢 set> · Locked: <rows> · Quick-dev: <keys>`
- `Batch approval recorded: <yes, quoting> | STOPPED, awaiting the operator`
- `Next: /smh-quick-dev in each 🟢 lane; the parent closes LAST`

⛔ Never end by starting one of the lanes. The next move is the operator's.

Optional additional input (a parent Task key, or the intent): $ARGUMENTS
