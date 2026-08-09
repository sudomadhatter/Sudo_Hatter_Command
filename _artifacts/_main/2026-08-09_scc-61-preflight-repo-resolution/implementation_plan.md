---
IsArtifact: true
ArtifactMetadata:
  title: SCC-61 preflight repo/branch resolution hardening — plan
  type: implementation_plan
  date: 2026-08-09
---

# SCC-61 — `cwd` is not intent: hardening repo/branch resolution in the close-out lane

## The trigger

During SCC-60's close-out on 2026-08-09, Step 1 of `/close-task-merge-tree` printed:

```
== task preflight - chore/SCC-59-update-maps-indexes ==
...
VERDICT: clear to close out and merge
```

SCC-60's branch was `chore/SCC-60-jira-rule-portability`. The preflight had resolved **a sibling lane's
branch**, run all six checks against it, and returned a clean verdict. Proceeding would have merged
SCC-59's in-flight, uncommitted-at-the-time work onto `main` under SCC-60's close-out and SCC-60's Dev
Record.

## Ground truth (verified, not assumed)

| Fact | Where |
|---|---|
| repo resolved by walking up from `cwd` for `.git` | `task_preflight.py` `git_root()` — `start = Path(arg).resolve() if arg else Path.cwd()`, then `for p in [start, *start.parents]: if (p / ".git").exists()` |
| `--branch` defaults to that repo's current HEAD | `task_preflight.py` — `branch = args.branch or git rev-parse --abbrev-ref HEAD` |
| same shape in the story lane | `closeout_preflight.py`, `jira_feed.py`, `check_maps.py` all resolve a root the same way |
| `cwd` resets at slash-command boundaries | observed directly: the shell returned to `/Users/sudohatter/Sudo_Hatter_Command` between the worktree's creation and Step 1 |
| the shared checkout was NOT on `main` | it stood on `chore/SCC-59-update-maps-indexes` — the precondition `worktree-per-story.md` assumes ("it stands on `main` … and stays there") had already been violated by a second chore lane |

**Why the script cannot catch this.** It has no input expressing *which ticket the operator meant*. Repo
and branch are both derived, so there is no pair to compare — every check is honest, and the verdict is
honest, about the wrong target. This is not a bug to fix in the script; it is a missing assertion in the
command that drives it.

**Why the existing guard did not fire.** `close-task-merge-tree` Step 0 already said *"Echo exactly
`Repo: <name> | Branch: <branch>` before any work."* That echo was produced — from belief, not from
command output. An echo written from memory can only ever confirm the memory; it cannot contradict it,
which is the sole thing it exists to do.

## Scope

**In:**

1. `close-task-merge-tree.md` **Step 0** — derive `Repo | Branch` from `git rev-parse` into pinned
   variables; require the agent to name the **expected Jira key** before running anything.
2. `close-task-merge-tree.md` **Step 1** — `--repo`/`--branch` become mandatory in the invocation; add a
   🛑 requiring the preflight's echoed header key to match the expected key, **STOP** on mismatch.
3. `worktree-per-story.md` — one new section, `⛔ cwd is not intent`, carrying the *why* for the whole
   toolkit so the paragraph does not have to be repeated (and drift) across a dozen command files.
4. The four worktree-acting commands — `sudo-close-workingtree`, `sudo-park`, `sudo-resume`,
   `sudo-merge-epic-workingtrees` — each gets the **mechanical step only**, pointing at the rule for the
   reasoning. `sudo-merge-epic-workingtrees` gets the strongest wording: it runs with the most sibling
   trees open and it *prunes*.
5. SOP currency move in `sudo_workflows_testing.md` §10, written operator-facing: what to ask an agent
   that reports a green gate.

**Out:**

- **Renaming `.claude/worktrees/`.** Measured on operator request: ~13 `.agents/` masters + 19 generated
  mirrors + 13 `_artifacts/` history files in the lobby, 36 in AGY_AVIATIONCHAT, 7 in
  OpenChat-Openrouter, plus the `claude/` branch prefix (load-bearing in `task_preflight.py`'s
  `WRONG_LANE` map and its test), three live `claude/*` branches on origin, three Jira tickets, and a
  two-machine transition window. Operator ruling 2026-08-09: **not low blast radius → parked.**
- **Changing the scripts.** The scripts are not wrong; a defaulted guess is a reasonable default. The
  missing assertion belongs where intent exists — in the command.

## Why the "why" lives in exactly one file

Repeating a warning paragraph across twelve command files is how the `_AP` twins drifted
(`sudo-commands-have-ap-twins-that-drift`). But a pointer alone is too weak — agents follow the literal
step list (`restate-alwayson-obligations-in-command-bodies`). The split resolves both: **the mechanical
step is baked into each command's step list; the reasoning is stated once in the rule.**

## Gates

`run_all.py` · `workflow_lint.py` · `sop_currency.py` (usage surfaces changed → the quick-reference must
move in the same change) · `task_preflight.py` **with `--repo` and `--branch` pinned**, which is the
change dogfooding itself.

## Known overlap

`_artifacts/_main/INDEX.md` — SCC-59 and SCC-60 both added a top row today and conflicted on it once
already during SCC-59's absorb of `origin/main`. Resolved by keeping both rows. This lane adds a third.
