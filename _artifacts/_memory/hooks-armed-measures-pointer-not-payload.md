---
name: hooks-armed-measures-pointer-not-payload
description: "hooks_armed.py reports ARMED for a repo whose .githooks holds zero gates — it checks core.hooksPath, never the directory contents."
metadata: 
  node_type: memory
  type: project
  originSessionId: f4c376eb-04da-4a4f-a6bb-30d4b71f6d57
  modified: 2026-08-26T01:23:18.782Z
---

`hooks_armed.py` (and `install_git_hooks.py --verify-only`) answer only **"is this machine pointed
at `.githooks`?"** They never open the directory. Measured 2026-08-25: `NEXgen-VR-Director` reported

```
ARMED - core.hooksPath=.githooks
```

while `.githooks/` held exactly one hook — `post-commit`, an advisory map-drift recorder that vetoes
nothing — and `.agents/scripts/git-hooks/` held zero gate scripts and none of the three `ENFORCE`
arming files. Nothing in that repo could refuse a commit.

**Why:** `core.hooksPath` and the hook files are two different problems. The config is per-machine
and never travels with a clone (which is what the arm-check exists for); the hooks are tracked files
that travel fine but simply may not have been written. Only the first was ever checked.

**How to apply:** read an `ARMED` result as *necessary, never sufficient*. Before trusting a repo's
gates, list the payload — `.githooks/` should hold 7 hooks, `.agents/scripts/git-hooks/` the gate
scripts plus `JIRA-ENFORCE` / `MAIN-PUSH-ENFORCE` / `MERGE-TARGET-ENFORCE`, and `.agents/jira.conf`
must exist. Then make one gate actually fire (`git commit --allow-empty -m "no key here"` must be
REJECTED); a gate never seen to refuse anything is being trusted on faith. Full inventory and the
copy-from source: `docs/migrations/install_guides/repo-gate-stack-setup.md` (SCC-325).

The concrete cost: NVS-69 added `.agents/jira.conf` to NEXgen to stop the Jira gate being a silent
no-op, and the conf is correct — but with no `commit-msg` hook in that repo it is inert, so the
ticket looked like it closed a hole it had only prepared to close. Same shape as
[[vscode-hides-git-hook-output]] and [[git-hooks-live-in-githooks-not-git-hooks]]: the failure is
always that nothing *looks* wrong. See also [[two-machines-mac-and-pc]] for why the pointer half is
per-machine in the first place.
