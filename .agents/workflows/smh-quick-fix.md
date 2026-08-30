---
description: The LIGHTWEIGHT lane — command-centre work that touches nothing which can break. Ticket, branch, do it, gates, push, hand back. No...
platforms: [opencode, antigravity, claude, codex]
---

# /smh-quick-fix — The Lightweight Lane (SCC-162)

> **Rules in force for this command:**
> - `.agents/rules/artifacts-always-first.md` § "When to Skip" — **the definition of this lane lives
>   there and only there.** This file is the door; that entry is the law
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push
>   `main`, never force-push; every branch and commit carries the repo's Jira key
> - `.agents/rules/worktree-per-story.md` — every commit-producing lane opens a worktree (SCC-62)
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — **invoking this command IS the "skip the plan"
>   instruction**, per the closed carve-out list. A fired EJECT re-arms the gate

**Why this exists.** Operator ruling, 2026-08-15: *"not everything is a full quick dev. sometimes I
just want an agent to do something specific… this does not touch anything that can break. so we don't
need to over engineer it."* Before this, an agent had two settings — the whole Task ceremony or
improvisation — and a doc-only edit got a plan-first STOP, a worktree, a self-audit and a RED
assertion before the operator stopped it.

**Scope, from the same ruling:** *"this is only for the smh / commands, we need this for the command
center not normal cicd work."* The test is his sentence: ***things that do not affect our development
system.*** Writing a guide. Fixing a reference. Tidying a messy source-control state.

> Flow position: **`/smh-quick-fix`** → **[STOP, hand back]** → the operator's
> `/smh-close-task-merge-tree`. It never merges and never closes its own ticket.

---

## Step 0 — Qualify. This is a script, not a judgement.

⛔ **Run this before anything else, including before minting a ticket.**

```bash
REPO=$(git rev-parse --show-toplevel) && echo "Repo: $(basename "$REPO")"
python3 .agents/scripts/lane_qualify.py --repo "$REPO" --paths <every path you will touch>
```

**Pass `--repo` explicitly.** It defaults to the cwd, and the command-centre check looks for
`.agents/commands/` there — so from a subdirectory it refuses a repo that would have qualified. The
refusal is the safe direction, but a wrong answer for the right reason still sends you down the wrong
lane. *(PC: `python`, not `python3`.)*

| Verdict | What you do |
|---|---|
| `LIGHT` | carry on |
| `LIGHT-VCS` | carry on — a **declared** git-hygiene action (see Step 3's rider) |
| `TASK` | **stop.** This is `/smh-quick-dev` — it needs a plan and the literal `approved` |
| `TASK-LIGHT` | **stop — but the lane you eject to is right-sized (SCC-302).** Toolkit work with a small, measured blast radius (`--lines` ≤ 10, ≤ 2 files): `/smh-quick-dev` still owns it — assertion-first, gates and sweep all stay — but the plan may be a paragraph and the review fan-out may collapse to one inline pass. Say the verdict in the walkthrough |
| `HANDOFF` | **stop.** A deployable path; the product's one road to `main` is `/cicd-push-e2e` |
| `NOT-COMMAND-CENTRE` | **stop.** You are in a project repo; use the `cicd-*` lanes |

**No paths is `TASK`, deliberately** — unknown scope is not empty scope. If the work genuinely edits
no files, say so with `--no-file-changes` and read the rider in Step 3.

## Step 1 — Ticket and lane. Do not ask; do it.

⛔ **Never ask *"shall I mint a ticket / open a lane?"*** — that question is the over-engineering this
lane exists to remove. The operator's ask IS the decision; agents mint.

> ⭐ **But look for a home first (`work-consolidation.md` rule 1).** Minting is the agent's call, not
> the operator's — and the call starts by checking whether an **open parent** already covers this
> surface, in which case this is its next lettered Subtask (add the index row with
> `jira_feed.py index-row`, which proves the parent's other rows survived the write). **No thematic
> parent? It is a subtask on the OPEN ROLLING TICKET** (`Bugs and Updates - <YYYY-MM>` — find it by
> BOTH labels, `labels IN (bugs-and-updates, running-bug-list)`, per `jira.md` §labels) — rung 3
> since SCC-191. Mint only for work that is a lane in
> its own right on day one, and say in one line what you looked at.

```bash
acli jira workitem create --project SCC --type Task --summary "…" --description "…"
cd "$REPO" && git fetch origin                                                    # ⛔ base = origin/main
cd "$REPO" && git worktree add .claude/worktrees/<slug> -b chore/<KEY>-<slug> origin/main
cd "<the new tree>" && git branch --unset-upstream                                # origin/main start-point sets upstream to MAIN
python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>       # PC: `python`
BRANCH=$(cd "<the new tree>" && git rev-parse --abbrev-ref HEAD) && echo "Lane: $BRANCH"
python3 .agents/scripts/jira_feed.py start --key <KEY> --apply
```

Already handed a key? Use it — never mint a second. Echo the branch from `rev-parse`, never from
memory: with sibling lanes live, where you stand is not evidence of what you mean.

## Step 2 — Do the work

Surgical. The operator's ask is the scope; anything beyond it is drift — cut it or say why it stays.
No plan file, no audit, no assertion written first. **Commit explicit paths inside the worktree**, the
key leading every subject, and push:

```bash
cd "<tree>" && git add <the exact paths>
cd "<tree>" && git commit -F <message-file>      # ⛔ backticks in -m "…" EXECUTE
cd "<tree>" && git push -u origin <BRANCH>
```

**Unpushed is stranded** — branches travel between machines, worktrees do not.

## Step 3 — The gates that still apply

They are mechanical, they are cheap, and none of them is ceremony:

```bash
python3 .agents/scripts/tests/run_all.py                        # the enforcement suite
python3 .agents/scripts/workflow_lint.py --toolkit-only
python3 .agents/scripts/check_maps.py --depth3-only --strict     # if you moved or added docs
python3 .agents/scripts/tests/test_sops_prds_folder.py           # if you touched docs/_scc_sops_prds/
```

⛔ **Run them bare, never piped** — `| tail` reports the pipe's exit code, not the gate's.

> **Rider for `LIGHT-VCS`.** A git-hygiene action deletes only refs **the operator named** — never a
> swept set — and every call carries `-C` (nothing in this system guards the merge *target*). Show
> what you will delete and get the word before deleting it: the lane drops ceremony, never the
> confirmation the RISK GATE requires.

## Step 3.5 — ⛔ EJECT — re-qualify against the REAL diff

Step 0 judged what you *intended* to touch. This judges what you *did*.

```bash
python3 .agents/scripts/lane_qualify.py --repo "$REPO" \
        --paths $(cd "<tree>" && git diff --name-only origin/main...HEAD)
```

*(That `$(…)` **is** split into separate arguments in both shells — command substitution splits where
a bare `$VAR` in zsh would not. Do not "fix" it by quoting: `"$(…)"` collapses the whole file list
into one argument and the sweep silently checks nothing.)*

Anything but `LIGHT` and **this lane is over**: say so in one line, keep the branch and everything
written, and continue on `/smh-quick-dev` — which means a plan, `/smh-self-audit`, and the operator's
literal `approved` before another file is edited. **A fired tripwire re-arms the plan-first gate.**

## Step 4 — The record: a lean walkthrough, and that is all

`_artifacts/_main/<YYYY-MM-DD>_<slug>/walkthrough.md` — short by design, but never skipped: the
close-out preflight blocks without it, and `## Your Actions` is a machine contract read by
`jira_feed.py finish`.

- **`## What changed`** — one line per file, and why.
- **`## Evidence`** — the gate output you actually ran (totals lines), plus `git rev-parse HEAD`.
- **`## Your Actions`** — **required even when empty.** An unchecked `- [ ]` is something only the
  operator can **decide** and holds the ticket out of `Done`; `- [x]` is settled; prose is context.
  ⛔ **Never the ceremony's own steps** (SCC-193) — "click Merge", "re-invoke the door",
  "run `--after-merge`" are refused by `jira_feed.py`: the operator's decision to proceed is the
  sign-off, and every step after it is yours to run.

Write `task.yaml` beside it (`task_key`, `primary_repo`, `branch`, `close_command:
smh-close-task-merge-tree`, `secondary_repos: []`), then file the Dev Record. ⛔ **The manifest
first, and no `--story` (SCC-174)** — `devrecord` reads the slug out of the `branch:` you just
wrote, which is the same source `/smh-close-task-merge-tree` uses. Passing a slug by hand is how
one lane ends up with two Dev Records.

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <KEY> \
       --stage quick-fix --walkthrough <the walkthrough> \
       --outcome "<what shipped, one line>" --apply
```

## Done — stop here

Do **NOT** merge, transition the ticket, or prune the branch. That is `/smh-close-task-merge-tree`,
and **invoking it is the operator's per-merge sign-off** — one invocation authorises exactly one
merge and never carries to the next.

Print: what changed · the gate results · the branch and its push state · the walkthrough link ·
anything still owed. Then hand back.

Optional additional input (the specific ask, or a ticket key): $ARGUMENTS
