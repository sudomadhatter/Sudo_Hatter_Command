---
name: git-hooks-live-in-githooks-not-git-hooks
description: "The lobby, AGY and Fresh set core.hooksPath=.githooks — installing to .git/hooks looks successful and does nothing"
metadata: 
  node_type: memory
  type: project
  originSessionId: d9adc5bc-e814-4396-b913-62eac264ecce
  modified: 2026-08-04T01:59:43.680Z
---

`core.hooksPath = .githooks` is set in the **lobby, AGY_AVIATIONCHAT and Fresh_Workspace_BMAD**;
NEXgen-VR-Director leaves it unset. When it is set, git reads **only** that directory — a hook
written to `.git/hooks/` is never executed.

**Why:** an installer that assumes `.git/hooks` prints "installed" and installs *nothing*. On
2026-08-03 the encoding pre-commit gate went in that way and was inert in 3 of 4 repos; it was only
caught because NEXgen (the one repo with `hooksPath` unset) blocked a commit while AGY silently
passed the identical bytes. A gate that silently does not run is worse than no gate — see
[[workflow-enforcement-scripts]].

**How to apply:** resolve the hook dir before writing — `git -C <repo> config --get core.hooksPath`,
relative to the repo root, falling back to `.git/hooks`. Then **prove it fires**: stage a file that
must fail, commit, and assert git's own exit code is non-zero AND `HEAD` did not move. Do not check
`$?` after a pipeline — that is the last command's status, not git's, and it will read as success.
Where `.githooks/` is tracked (all three) the hook travels through git and needs no per-machine
install; where it is not, every clone installs once because `.git/` never travels.
