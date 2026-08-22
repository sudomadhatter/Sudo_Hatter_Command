---
name: closeout-target-is-a-machine-contract
description: "SCC-64: `task_preflight.py` now REQUIRES `--expect-key`, cross-reads a `task.yaml` manifest, and `workflow_lint --toolkit-only` stops root close-outs inheriting active-project.txt. The prose guard became an exit code."
metadata:
  type: project
---

Since 2026-08-09 (SCC-64) "which ticket/repo/branch am I closing?" is a **validated machine
contract**, not agent judgment:

- **`task_preflight.py --expect-key <KEY>` is REQUIRED.** A bare run exits 2. If the resolved
  branch carries a different key it exits 2 naming *both* keys — so a `cwd` that drifted into a
  sibling lane now fails the match instead of returning a clean verdict about the wrong branch
  (the [[preflight-resolves-repo-from-cwd]] failure, now mechanical).
- **`task.yaml`** in the task's `_artifacts/_main/<date>_<slug>/` folder — `task_key`,
  `primary_repo`, `branch`, `close_command`, `secondary_repos[{repo, landing, ticket}]` — written
  at task START where drift can't reach. Declared-branch mismatch = error; **missing = warning**
  that prints the schema (adoption is incremental; a check that reddens all history gets routed
  around). `landing: retain-on-epic` is how a cross-repo commit that stays on a live epic branch is
  recorded instead of being presented as merged to production.
- **Dirty `_artifacts/_memory/` files get their own error block** with park-don't-sweep wording —
  two lanes share one store, and "cleaning" a sibling's memory to get green was the near-miss.
- **`workflow_lint.py --toolkit-only`** stops before `resolve_project_root`, so a root Task
  close-out no longer goes red/green on whichever product project sits in `.agents/active-project.txt`.
  Three consecutive close-outs had to explain away a red as "pre-existing, different project" —
  teaching an agent that some reds are fine is how reds die.

**Why the scripts changed after SCC-61 said they shouldn't:** SCC-61's missing piece was an
*intent input*, not script logic. `--expect-key` supplies the intent; the comparison follows.

The prose discipline in `worktree-per-story.md` §"cwd is not intent" still governs every OTHER
script. Related: [[one-door-per-platform-per-command]], [[cross-repo-work-needs-a-ticket-per-repo]].
