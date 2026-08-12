---
description: Close out TASK work — a `chore/<JIRA-KEY>-<slug>` branch that never got an epic and a story, so BMAD's `/cicd-update-sprint-memory` cannot close it. Preflights mechanically (branch shape, clean+pushed, main absorbed, and THE LANE — did anything deployable change?), runs the gate the lane selects, merges to `main` with `--no-ff`, files the Dev Record and moves the ticket to Done, then prunes the worktree AND the branch (SCC-62 — unlink assets before removing the tree; a recursive delete through a junction eats the shared targets). Invoking it IS the merge sign-off. Refuses the moment a deployable path is in the diff and hands the work to `/cicd-push-e2e`.
platforms: [opencode, antigravity]
---

# /smh-close-task-merge-tree — Close a Task, Merge It, Prune the Tree

> **Rules in force for this command:**
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — why every repo/branch below is
>   pinned from command output; with sibling lanes (and their worktrees) live, where you stand is
>   not evidence of what you mean
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never
>   force-push; every branch and every commit carries the repo's Jira key (armed 2026-08-07)
> - `.agents/rules/jira.md` — the `acli` reference, and the work-item type model this lane sits in
> - `.agents/rules/artifacts-always-first.md` — the plan is skippable on this lane; the closing
>   `walkthrough.md` is **not**, and the preflight blocks without it

**The Task lane's close-out.** The story lane ends at `/cicd-update-sprint-memory`, which reads a
sprint board, flips a story status and lands on an epic branch. **Task** work has none of those —
no epic, no story file, no board row, often no board at all — so that command has nothing to
operate on. This is the missing half: the same close-out obligations (record what was learned,
move the ticket, land the code, prune the branch) for work organised as a Task.

> **Story or Task?** One rule, one implementation — `jira_feed.py work_type()`, documented in
> `.agents/rules/jira.md` §Work-item types. **Story** = BMAD sprint work (a dotted number, a
> `debug-` marker, or a story file). **Task** = workflow / IDE / rules / skills work, filed under
> a grouping epic. If the work has a story, it does **not** come here.

**Why this command is `smh-*` and not `cicd-*`.** Every `/cicd-*` command binds
`smh-target-resolution.md` — *"operates on exactly ONE target — never the lobby."* Task work is
mostly toolkit work, and toolkit work lives **in** the command centre. So this belongs to the
`smh-*` family (`/smh-sync-agents`, `/smh-update-maps-indexes`, `/smh-new-project`) — the one that
is allowed to act on the repo you are standing in. The prefix is the permission; it is not cosmetic.

## 🛑 MANDATORY RULES (before you start)

1. **This command merges to `main`.** Invoking it IS the operator's per-merge sign-off for this one
   task — the same contract `/cicd-push-e2e` carries for an epic. The push-approval hook still
   prompts on the push; that prompt is expected, not an error. Approval is **per-action and never
   carries forward** — the next task needs its own invocation.
2. **The preflight is not advisory.** Exit 2 STOPS the command. Report what failed; never "merge
   anyway", and never re-run it with the failing check worked around.
3. **The lane is not yours to choose.** `LANE: HANDOFF` means a deployable path is in the diff.
   That is not a task, whatever the ticket says — STOP and hand it to `/cicd-push-e2e`. There is no
   override flag, deliberately.
4. **Clear GITHUB_TOKEN on push/pull**: prefix with `$env:GITHUB_TOKEN = ""` (PowerShell) or
   `env -u GITHUB_TOKEN` (Bash) to prevent stale-session auth failures.

## Step 0 — Resolve the repo (FIRST) — from command output, never from belief

The repo is **where you are standing**, not a project pointer. If `$ARGUMENTS` names a folder under
`Projects/` or a path, use that; otherwise the current repo. Do **not** read
`.agents/active-project.txt` — this command's whole point is that the command centre is a
legitimate target.

**Resolve it mechanically and pin it in a variable.** `cwd` is not intent: it resets to the shared
checkout at slash-command boundaries, and the preflight finds its repo by walking *up from cwd*
looking for `.git`. Run these and read the answers:

```bash
REPO=$(cd "<the path you resolved>" && git rev-parse --show-toplevel)
BRANCH=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)
echo "Repo: $(basename "$REPO") | Branch: $BRANCH"
```

Then pin **the Jira key you intend to close** — the one from the ticket, not the one you read off
the branch. Keep both; Step 1 makes the script compare them:

```bash
EXPECTED_KEY="SCC-00"    # the ticket you MEAN, stated before any tool has answered anything
```

**Author the task manifest if the task never got one.** `task.yaml` sits in the task's
`_artifacts/_main/<date>_<slug>/` folder and is intent written down where no cwd drift can reach
it — the preflight cross-checks it and warns when it is missing:

```yaml
task_key: SCC-00
primary_repo: <repo folder name>
branch: chore/SCC-00-<slug>
close_command: smh-close-task-merge-tree
secondary_repos: []        # single-repo task — the common case
```

**Cross-repo?** Then `secondary_repos` takes the block form instead — **replace** the `[]` line, never
leave it above a second one:

```yaml
secondary_repos:
  - repo: Projects/<name>
    landing: independent-task      # or retain-on-epic
    ticket: KEY-00
```

Cross-repo work: each `secondary_repos` row is **its own ticket in its own repo** closed through
its own lane — `landing: retain-on-epic` records the exception where a commit stays on a live epic
branch and must never be presented as merged to production.

⛔ **Since SCC-94 these rows are ENFORCED, not just recorded.** For every row, the preflight blocks
unless that repo is reachable, its declared ticket key is one that repo's own `jira.conf` answers
to, it is clean and `0/0` with its origin, and its memory store passes the same integrity contract
the lobby's does. Two consequences worth knowing before you write the row:

- **The lobby cannot see a dirty project half.** Submodules are `ignore = all`, so this repo's
  `git status` is clean no matter what state the project is in. This check is the only thing that
  looks.
- **A wrong key is caught here, not at the commit.** A project answering only to `AVCH` rejects an
  `SCC`-keyed commit at its hook; declaring the wrong one used to surface after the work was done.
- The inline `[{…}]` form is **not read** — it warns and verifies nothing rather than failing open.
  Use the block form.

⛔ **Echoing `Repo | Branch` from memory defeats the only guard here.** The line exists to catch a
wrong belief about where you are standing; a self-reported echo can only ever confirm the belief.
It must come from the commands above.

## Step 1 — Preflight (mechanical — one call answers every precondition)

**`--expect-key` is required — the script refuses to run without it (SCC-64).** This is the
machine half of Step 0: the preflight now blocks, mechanically, when the resolved branch does not
carry the key you pinned — a cwd that drifted into a sibling's lane fails the key match instead of
returning a clean verdict about the wrong branch. Still pass `--repo` and `--branch`: they are
written as optional because the script can guess, and the guess is exactly what fails when a
sibling lane has moved the shared checkout.

```bash
python3 .agents/scripts/task_preflight.py --fetch --repo "$REPO" --branch "$BRANCH" --expect-key "$EXPECTED_KEY"
```

🛑 **Read the header line before you read the verdict.** It echoes the branch the script actually
resolved:

```
== task preflight - chore/<JIRA-KEY>-<slug> ==
```

If that key is not the key you named in Step 0, **STOP** — you are pointed at another lane. Say
which branch it resolved and which you meant; do not re-run it hoping for a different answer, and
never merge on a verdict whose header you did not check. (2026-08-09: this resolved a sibling's
`chore/*` branch mid-close-out and returned a clean verdict; merging it would have put another
lane's in-flight work on `main` under the wrong ticket. The script cannot catch this — it has no way
to know which ticket you meant.)

It answers, from the repo rather than from your memory of it:

| Check | What a failure means |
|---|---|
| **branch** | `chore/<JIRA-KEY>-<slug>`, key immediately after the prefix, key matches `.agents/jira.conf`. An `epic/`, `claude/` or `incident/` branch is refused **by name, with the command that IS right**. |
| **intent** | the branch's key equals `--expect-key`. A mismatch means the preflight is aimed at **another lane's branch** — the 2026-08-09 failure, now a mechanical exit 2 instead of a prose warning. |
| **manifest** | a `task.yaml` declaring this `task_key` agrees on the branch. Missing manifest = warning (author it, Step 0); a manifest naming a **different branch** = error — one of them is lying. |
| **sync** | clean tree, `0/0` with origin. Merging an unpushed branch puts commits on production that exist on one disk. Dirty files under `_artifacts/_memory/` are named separately: another session's memory is **parked or left, never swept, deleted, or committed under this task**. |
| **base** | `origin/main` fully absorbed, and ≥1 commit ahead. Conflicts must surface **here**, never on `main`. |
| **scope** | ⭐ **THE LANE.** See below. |
| **artifacts** | a `walkthrough.md` mentioning the key exists. Without it the Dev Record cites nothing. |
| **worktree** | the worktree checked out on this branch — **expected** since SCC-62, and Step 5 prunes it. It blocks the branch delete until removed, so the order in Step 5 is not optional. |

**⭐ The lane, and why the E2E answer is mechanical.** The one thing that makes this command
cheaper than `/cicd-push-e2e` is skipping the end-to-end suite, and the only honest justification is
*nothing that deploys changed*. That is precisely the claim an agent is worst at auditing about its
own work, so the script derives it and prints it as `LANE:`:

- **`LOCAL`** — either the repo has **no deployable surface at all** (no `backend/`, `frontend/`,
  `firebase/`, `functions/`, `mobile/`, `.github/` — the command centre's case, and exactly what
  `git-policy.md` means by *"it has no E2E suite and never will"*), or the repo deploys but this
  diff touches none of those paths. **There is no E2E gate to skip.** Proceed.
- **`HANDOFF`** — a deployable path is in the diff. **STOP.** Print which one, and say: *this is a
  product change, and the product has one road to `main` — `/cicd-push-e2e`.* Leave the branch
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

Plus, because task work is almost always **docs and rules**, the two checks `/cicd-quick-dev` Step 3
runs on a docs-only diff:

- **Link + anchor check** on every path and `#L` anchor the diff touched.
- **SOP currency** — a usage-surface change (`.agents/commands/`, `.agents/rules/`,
  `.agents/scripts/`, git hooks, root `AGENTS.md`) must have moved
  `docs/_scc_sops_prds/workflows_testing_SOP.md`. The armed commit-msg gate already
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

# ── Pre-flight the SERVER-SIDE gate on this exact commit (SCC-118) ──────────────────────
# `main` requires a green check named below. The merge commit you just made has never been
# to GitHub, so it carries no check and the push would be refused. Send that exact commit
# to a throwaway ref, let CI run on it, and the green travels with the SHA — a check
# attaches to a commit, not to a branch.
SHA=$(git rev-parse HEAD)
env -u GITHUB_TOKEN git push origin HEAD:refs/heads/gate/main-$SHA

sleep 10                                       # let the run register before asking for it
until gh api repos/{owner}/{repo}/commits/$SHA/check-runs \
        --jq '.check_runs[] | select(.name=="main-write-gate") | .status' \
      | grep -qx completed; do sleep 10; done

gh api repos/{owner}/{repo}/commits/$SHA/check-runs \
  --jq '.check_runs[] | select(.name=="main-write-gate") | .conclusion' | grep -qx success \
  || { echo "server-side gate is RED on $SHA — fix on the branch, do NOT push main"; exit 1; }

# Mint the single-use approval token — AFTER the pre-flight, IMMEDIATELY before the push (SCC-77).
# ⚠ ORDER IS LOAD-BEARING: the token's TTL is 30 minutes. Mint it before the CI wait and a
# slow run eats its life — everything else passes, then the push dies on "stale token" and
# the close-out has to be re-run having already done all its work (SCC-118).
sh .agents/scripts/git-hooks/mint-push-token.sh \
   --command /smh-close-task-merge-tree --branch chore/<JIRA-KEY>-<slug> --key <JIRA-KEY>

env -u GITHUB_TOKEN git push origin main       # the pre-push gate spends the token here

env -u GITHUB_TOKEN git push origin --delete gate/main-$SHA   # pre-flight ref, done with
```

**Two halves, and they are not copies of each other.** The pre-flight proves the change is
*fit* to land — the real suite ran, on a runner, at this exact commit. The token proves *you
said yes*, once, for this merge. Neither substitutes for the other, and only the second one can
ever be a judgement about intent: an agent can write a file, so it can write a token, but it
cannot make a red suite green. The server-side half exists because a merge performed on
GitHub — the web *Merge pull request* button, or the API — never touches this machine, so the
`pre-push` hook is not bypassed there, it is **absent** (SCC-118; PR #2 landed that way).
If the check is red, **STOP** — never `--no-verify`, never disable the ruleset to get past it.

**The token is the machine half of "invoking this IS the sign-off."** `.githooks/pre-push` refuses
any push landing on `main` without one, and consumes it on the way through — so this invocation
authorises exactly one merge and the next task needs its own, mechanically rather than by reading
(`git-policy.md` § "The write gate"; the failure it fixes is SCC-71's six-merges-on-one-sign-off).

⛔ **Mint last. Do not commit anything after it.** The token records the sha it was minted for, so a
commit made between the mint and the push makes the push carry a different sha and the gate refuses
it — correctly, because nothing gated that commit. If that happens: re-run the gate, then re-mint.
A refusal always discards the token, so there is never a stale one left to match by accident.

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
       --outcome "merged to main at <merge-sha> via /smh-close-task-merge-tree" \
       --verdict "<gate result>" \
       --decision "<a ruling made while doing it>" \
       --pitfall "<what nearly bit>" \
       --followon "<anything still owed>" --closing --apply

acli jira workitem transition --key <JIRA-KEY> --status "Done" --yes
python3 .agents/scripts/jira_feed.py check --key <JIRA-KEY>     # must exit 0
```

⛔ **`--yes` or acli stops on an interactive confirm no agent shell can answer.** This line shipped
without it until SCC-113; `Done` was landing on luck. `tests/test_jira_feed.py` now fails if any
`workitem transition` under `.agents/` omits it.

**Exactly one Dev Record per ticket.** If `/cicd-quick-dev` already filed one at Step 4.5, this
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

## Step 5 — Prune the worktree, THEN the branch

Since SCC-62 every commit-producing lane runs in a worktree, so a Task lane owns one by default — and
**this command prunes it.** That is what lets ad-hoc work isolate at all: the old ban on chore worktrees
existed only because nothing cleaned them up. The lane that opened the tree is the lane that closes it.

**Order matters, and getting it wrong is destructive.**

```bash
# 1. UNLINK the gitignored assets FIRST — before anything is deleted.  (PC: `python`, not `python3`)
python3 .agents/scripts/link-worktree-assets.py --unlink .claude/worktrees/<slug>

# 2. Now remove the tree.
git worktree remove .claude/worktrees/<slug>
git worktree list                                       # the tree must be gone

# 3. Only then the branch.
git branch -d chore/<JIRA-KEY>-<slug>
env -u GITHUB_TOKEN git push origin --delete chore/<JIRA-KEY>-<slug>
git rev-list --left-right --count main...origin/main    # must be 0 0
git status --short                                      # must be empty
```

⛔ **Unlink before you remove.** A recursive delete **through a junction** destroys the shared
`.venv` / `node_modules` **targets**, not just the links — it walks into the real directory and deletes
the contents. `git worktree remove` does a recursive delete. Unlink first, every time.

`-d` (never `-D`): it refuses if the branch did not merge, which is the check working. A refusal here
after a successful Step 3 means the merge did not land — go look, do not force. `-d` also fails while a
worktree still holds the branch, which is why the tree goes first.

**PC:** a pruned worktree can leave an empty shell directory behind that blocks a later
`git worktree add` at the same path; only a PowerShell delete clears it.

If the tree belongs to a **story** lane (`claude/*`) rather than this Task, it is not yours to prune —
`/cicd-close-workingtree` owns that one. Leave it and say so.

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
