---
description: Close out TASK work — a `chore/<JIRA-KEY>-<slug>` branch that never got an epic and a story, so BMAD's `/sudo-update-sprint-memory` cannot close it. Preflights mechanically (branch shape, clean+pushed, main absorbed, and THE LANE — did anything deployable change?), runs the gate the lane selects, merges to `main` with `--no-ff`, files the Dev Record and moves the ticket to Done, then prunes the branch. Invoking it IS the merge sign-off. Refuses the moment a deployable path is in the diff and hands the work to `/sudo-push-e2e`.
platforms: [opencode, antigravity]
---

# /close-task-merge-tree — Close a Task, Merge It, Prune the Tree

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never
>   force-push; every branch and every commit carries the repo's Jira key (armed 2026-08-07)
> - `.agents/rules/jira.md` — the `acli` reference, and the work-item type model this lane sits in
> - `.agents/rules/artifacts-always-first.md` — the plan is skippable on this lane; the closing
>   `walkthrough.md` is **not**, and the preflight blocks without it

**The Task lane's close-out.** The story lane ends at `/sudo-update-sprint-memory`, which reads a
sprint board, flips a story status and lands on an epic branch. **Task** work has none of those —
no epic, no story file, no board row, often no board at all — so that command has nothing to
operate on. This is the missing half: the same close-out obligations (record what was learned,
move the ticket, land the code, prune the branch) for work organised as a Task.

> **Story or Task?** One rule, one implementation — `jira_feed.py work_type()`, documented in
> `.agents/rules/jira.md` §Work-item types. **Story** = BMAD sprint work (a dotted number, a
> `debug-` marker, or a story file). **Task** = workflow / IDE / rules / skills work, filed under
> a grouping epic. If the work has a story, it does **not** come here.

**Why this command is not `sudo-*`.** Every `/sudo-*` command binds
`sudo-target-resolution.md` — *"operates on exactly ONE target — never the lobby."* Task work is
mostly toolkit work, and toolkit work lives **in** the command centre. So this joins the non-`sudo`
family (`/sync-agents`, `/update-maps-indexes`, `/new-project`) that is allowed to act on the repo
you are standing in. The naming is the permission; it is not cosmetic.

## 🛑 MANDATORY RULES (before you start)

1. **This command merges to `main`.** Invoking it IS the operator's per-merge sign-off for this one
   task — the same contract `/sudo-push-e2e` carries for an epic. The push-approval hook still
   prompts on the push; that prompt is expected, not an error. Approval is **per-action and never
   carries forward** — the next task needs its own invocation.
2. **The preflight is not advisory.** Exit 2 STOPS the command. Report what failed; never "merge
   anyway", and never re-run it with the failing check worked around.
3. **The lane is not yours to choose.** `LANE: HANDOFF` means a deployable path is in the diff.
   That is not a task, whatever the ticket says — STOP and hand it to `/sudo-push-e2e`. There is no
   override flag, deliberately.
4. **Clear GITHUB_TOKEN on push/pull**: prefix with `$env:GITHUB_TOKEN = ""` (PowerShell) or
   `env -u GITHUB_TOKEN` (Bash) to prevent stale-session auth failures.

## Step 0 — Resolve the repo (FIRST)

The repo is **where you are standing**, not a project pointer. If `$ARGUMENTS` names a folder under
`Projects/` or a path, use that; otherwise the current repo. Echo exactly `Repo: <name> | Branch:
<branch>` before any work. Do **not** read `.agents/active-project.txt` — this command's whole point
is that the command centre is a legitimate target.

## Step 1 — Preflight (mechanical — one call answers every precondition)

```bash
python3 .agents/scripts/task_preflight.py --fetch [--repo <path>] [--branch <name>]
```

It answers, from the repo rather than from your memory of it:

| Check | What a failure means |
|---|---|
| **branch** | `chore/<JIRA-KEY>-<slug>`, key immediately after the prefix, key matches `.agents/jira.conf`. An `epic/`, `claude/` or `incident/` branch is refused **by name, with the command that IS right**. |
| **sync** | clean tree, `0/0` with origin. Merging an unpushed branch puts commits on production that exist on one disk. |
| **base** | `origin/main` fully absorbed, and ≥1 commit ahead. Conflicts must surface **here**, never on `main`. |
| **scope** | ⭐ **THE LANE.** See below. |
| **artifacts** | a `walkthrough.md` mentioning the key exists. Without it the Dev Record cites nothing. |
| **worktree** | a worktree still checked out on this branch — it blocks the branch delete in Step 5. |

**⭐ The lane, and why the E2E answer is mechanical.** The one thing that makes this command
cheaper than `/sudo-push-e2e` is skipping the end-to-end suite, and the only honest justification is
*nothing that deploys changed*. That is precisely the claim an agent is worst at auditing about its
own work, so the script derives it and prints it as `LANE:`:

- **`LOCAL`** — either the repo has **no deployable surface at all** (no `backend/`, `frontend/`,
  `firebase/`, `functions/`, `mobile/`, `.github/` — the command centre's case, and exactly what
  `git-policy.md` means by *"it has no E2E suite and never will"*), or the repo deploys but this
  diff touches none of those paths. **There is no E2E gate to skip.** Proceed.
- **`HANDOFF`** — a deployable path is in the diff. **STOP.** Print which one, and say: *this is a
  product change, and the product has one road to `main` — `/sudo-push-e2e`.* Leave the branch
  exactly as it is; nothing here is undone.

Exit 2 → stop and report. Exit 1 (warnings) → read them; a "never pushed" warning in particular
means Step 3 would merge something no other machine has.

## Step 2 — Run the gate the lane selected

The preflight prints the exact commands under `gate:`. Run them and **paste the real output** — a
gate reported from intent is the failure this whole toolkit exists to remove.

In the command centre that is:

```bash
python3 .agents/scripts/tests/run_all.py        # the enforcement suite — must be N/N files passed
python3 .agents/scripts/workflow_lint.py        # toolkit self-consistency
```

Plus, because task work is almost always **docs and rules**, the two checks `/sudo-quick-dev` Step 3
runs on a docs-only diff:

- **Link + anchor check** on every path and `#L` anchor the diff touched.
- **SOP currency** — a usage-surface change (`.agents/commands/`, `.agents/rules/`,
  `.agents/scripts/`, git hooks, root `AGENTS.md`) must have moved
  `_my_resources/_quick_reference/sudo_workflows_testing.md`. The armed commit-msg gate already
  enforced this per commit, so a surprise here means a commit was made with `--no-verify` or
  `[sop-ok]` — say which.

Any failure → **STOP**. Fix it on the branch and re-run; do not carry a red gate into a merge.

## Step 3 — Merge to `main`

```bash
git checkout main
env -u GITHUB_TOKEN git pull --ff-only origin main
git merge chore/<JIRA-KEY>-<slug> --no-ff \
  -m "merge: chore/<JIRA-KEY>-<slug> -> main (task: <gate summary>)"
# 🛑 summarize the commits + changed files before pushing
env -u GITHUB_TOKEN git push origin main       # hook prompts — the expected approval moment
```

`--no-ff` keeps the task visible as one reviewable unit on `main`'s first-parent history, and
because the branch name (with its key) rides in the merge message, Jira links the merge commit to
the ticket automatically — the commit-msg hook exempts merges precisely because of that join. If the
push is rejected (remote moved), **STOP and report**; never force.

Capture the merge SHA — Step 4 puts it on the ticket.

## Step 4 — File the Dev Record, then move the ticket

**After the merge, never before.** A ticket that reads `Done` while the merge failed is a lie on the
board; a merge that landed while the record lags is one command away from correct. Take the
recoverable failure.

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <JIRA-KEY> --story <branch-slug> \
       --stage close-out --walkthrough <the walkthrough> \
       --outcome "merged to main at <merge-sha> via /close-task-merge-tree" \
       --verdict "<gate result>" \
       --decision "<a ruling made while doing it>" \
       --pitfall "<what nearly bit>" \
       --followon "<anything still owed>" --closing --apply

acli jira workitem transition --key <JIRA-KEY> --status "Done"
python3 .agents/scripts/jira_feed.py check --key <JIRA-KEY>     # must exit 0
```

**Exactly one Dev Record per ticket.** If `/sudo-quick-dev` already filed one at Step 4.5, this
**updates it in place** — **never pass `--append-new`.** `devrecord --apply` reads the ticket back
and exits 2 if the comment is not there, so a non-zero exit means the record did **not** land:
report that, do not report success.

**`--closing` clears a `Bug` flag, and this lane needs it.** A ticket arrives here typed `Bug` when
something found it broken and pulled it back out of `Done` — an audit that traced a live bug to it,
or the operator by hand. The fix you just merged IS that bug, so the type goes back to **`Task`**,
which is what the rule says this ticket is. It restores whatever `work_type()` computes, never
always `Story` — the first cut did that, and it stranded every flagged Task as a permanent `Bug`
because nothing else in the system can clear one. On a non-`Bug` ticket the flag is a silent no-op,
so it is always safe to pass.

No ticket key at all → say so in the report and skip both calls. **Never invent a key.**

## Step 5 — Prune the branch

```bash
git branch -d chore/<JIRA-KEY>-<slug>
env -u GITHUB_TOKEN git push origin --delete chore/<JIRA-KEY>-<slug>
git rev-list --left-right --count main...origin/main    # must be 0 0
git status --short                                      # must be empty
```

`-d` (never `-D`): it refuses if the branch did not merge, which is the check working. A refusal
here after a successful Step 3 means the merge did not land — go look, do not force.

If Step 1 reported a **worktree** on this branch, `-d` will fail while it exists. Run
`/sudo-close-workingtree` for that tree first — it unlinks the junctions **before** removing
anything, and a recursive delete through a junction destroys the shared `.venv` / `node_modules`
**targets**, not just the links.

## Step 6 — Verify, THEN report

Every ✅ below must come from a command you actually ran in this step, not from intent:

```bash
git rev-parse --abbrev-ref HEAD        # main
git log --oneline -1                   # the merge commit
git branch --list 'chore/<JIRA-KEY>-*' # empty
git ls-remote --heads origin 'chore/<JIRA-KEY>-*'  # empty
```

Print:

`✅ Task <JIRA-KEY> closed:`
- `Lane: LOCAL — <why the E2E gate did not apply, in the preflight's words>`
- `Gate: <the commands run + their real totals>`
- `Merged: <merge-sha> (--no-ff)` · `main 0 0, clean`
- `Jira: Dev Record filed (one record) · ticket → Done · check exit 0`
- `Pruned: chore/<JIRA-KEY>-<slug> local + remote` *(or why it was retained)*
- `Still owed: <the --followon items, or "nothing">`

Optional additional input (repo · branch): $ARGUMENTS
