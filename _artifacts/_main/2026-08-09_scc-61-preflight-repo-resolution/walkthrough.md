---
IsArtifact: true
ArtifactMetadata:
  title: SCC-61 preflight repo/branch resolution hardening — walkthrough
  type: walkthrough
  date: 2026-08-09
---

# SCC-61 — a clean verdict about the wrong branch

## What was wrong

`/close-task-merge-tree` Step 1 ran during SCC-60's close-out and printed:

```
== task preflight - chore/SCC-59-update-maps-indexes ==
-- 0 error(s), 0 warning(s) --
VERDICT: clear to close out and merge
```

The lane being closed was `chore/SCC-60-jira-rule-portability`. Every check the preflight ran was
correct; all of them ran against **a sibling lane's branch**. Acting on that verdict would have merged
SCC-59's then-unfinished work to `main` under SCC-60's ticket and SCC-60's Dev Record.

Two mechanisms combined:

1. **`task_preflight.py` derives both inputs.** `git_root()` starts at `Path.cwd()` when `--repo` is
   absent and walks parents looking for `.git`; `--branch` falls back to that repo's `HEAD`.
2. **`cwd` had silently reset** to the shared checkout at the slash-command boundary — and the shared
   checkout was standing on `chore/SCC-59-update-maps-indexes`, because a second chore lane was live in
   it. `worktree-per-story.md` assumes the lobby *"stands on `main` … and stays there"*; with two chore
   lanes, it doesn't.

**The script cannot detect this.** Nothing in its inputs expresses which ticket the operator meant, so
there is no pair to compare. It is not a script bug — it is a missing assertion in the command.

**And the guard that existed could not fire.** Step 0 already required an echo of
`Repo: <name> | Branch: <branch>`. That echo was produced from belief rather than command output, so it
confirmed the wrong belief instead of contradicting it. A self-reported check can only ever agree with
the thing it is checking.

## What changed

| File | Change |
|---|---|
| `.agents/commands/close-task-merge-tree.md` | **Step 0** now derives `REPO`/`BRANCH` via `git rev-parse` into pinned shell variables and requires the agent to name **the Jira key it intends to close** first. **Step 1** makes `--repo`/`--branch` mandatory in the invocation and adds a 🛑 requiring the preflight's echoed header key to match the expected key — mismatch is a **STOP**, not a retry. |
| `.agents/rules/worktree-per-story.md` | New section **`⛔ cwd is not intent — pin --repo and --branch on every script`**: names all four resolving scripts, states why the failure is silent by construction, and carries the piped-exit-code corollary. |
| `.agents/commands/sudo-close-workingtree.md` | `--branch` promoted from optional to explicit; check the echoed slug before reading the result. |
| `.agents/commands/sudo-park.md` | every git command takes an explicit `-C <repo>` — parking spans two repos and other lanes' trees. |
| `.agents/commands/sudo-resume.md` | bind later commands to the tree just created; a fresh worktree is the one place `cwd` is guaranteed *not* to be. |
| `.agents/commands/sudo-merge-epic-workingtrees.md` | strongest wording — it runs with the most sibling trees open **and it prunes**. |
| `_my_resources/_quick_reference/sudo_workflows_testing.md` | §10 operator-facing block: a green check can be true about the wrong branch, and the one question to ask — *which branch did the gate name?* |

The reasoning lives in the rule **once**; each command carries only the mechanical step. Repeating the
paragraph twelve times is how the `_AP` twins drifted, but a bare pointer is too weak because agents
follow the literal step list — so: steps in the commands, *why* in the rule.

## Gate results

| Gate | Result |
|---|---|
| `tests/run_all.py` | **10/10 files passed**, exit 0 |
| `tests/test_command_surfaces.py` | **5/5 passed**, exit 0 |
| `sop_currency.py` | **exit 0** — usage surfaces moved with the quick-reference in the same change |
| `workflow_lint.py` | exit 2 — **1 error, unchanged**: AGY `19-5-adk-agent-evaluation-stage-2` active with no story file (pre-existing, AVCH-45; identical before and after this change) |
| `task_preflight.py --repo … --branch …` | see below — the change dogfooding itself |

## Decisions

- **The scripts were not changed.** A defaulted guess is a reasonable default; the assertion belongs
  where intent exists, which is the command driving the script.
- **The `.claude/worktrees/` rename stays parked.** Measured at operator request: ~13 `.agents/` masters
  + 19 generated mirrors + 13 `_artifacts/` history files in the lobby, 36 in AGY_AVIATIONCHAT, 7 in
  OpenChat-Openrouter, plus the `claude/` branch prefix (load-bearing in `task_preflight.py`'s
  `WRONG_LANE` map and its test), three live `claude/*` branches on origin, three tickets, and a
  two-machine transition window. Operator ruling: not low blast radius → parked. Recorded here so the
  measurement is not re-done.
- **`close-task-merge-tree` keeps ONE canonical body.** Verified against `sync-agents.ps1`: `platforms:`
  filters **commands only** — skills publish through `Sync-Dir`, an unfiltered tree copy — so no
  frontmatter can give Codex the skill while hiding it from Claude. SCC-59's shape is therefore the only
  working one, and removing the Claude skill would take `/close-task-merge-tree` away from Codex
  entirely, which was the original complaint.

## Pitfalls

- **The Antigravity mirror silently changed shape.** These edits pushed the command body past
  Antigravity's 12k workflow cap, so `.agents/workflows/close-task-merge-tree.md` regenerated as a thin
  launcher (198 lines removed). That is the designed mechanism, not a regression — but it means a
  grep for the new text against the workflow mirror returns 0 and looks like a failed sync.
- **`| tail` fakes a pass.** During this same session a merge conflict printed `=== EXIT: 0 ===` because
  the pipeline's status is `tail`'s. Every gate above was run unpiped via `out=$(cmd); rc=$?`. This is
  the same read-a-failure-as-a-pass shape as the bug being fixed, and it bit twice on 2026-08-09.
- **The operator's memory files were live in a sibling lane's tree.** `_artifacts/_memory/` and
  `~/.claude/projects/.../memory/` are the same directory, so two memories written mid-session appeared
  as uncommitted files inside SCC-59's branch. They were parked to scratchpad and restored onto this
  branch — neither swept into SCC-59 nor deleted.

## Follow-ons

- `check_maps.py --set-anchor --all` and a GitNexus re-index remain owed from SCC-59 now that its
  commits exist.
- **AVCH-51's commit belongs on the live Epic 19 branch** and must not be presented as merged to
  production — separate lifecycle decision, explicitly not taken here.
