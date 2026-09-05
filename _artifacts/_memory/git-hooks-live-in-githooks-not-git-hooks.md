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

**Mac addendum (2026-08-06):** `core.hooksPath` is LOCAL config — it never travels, so every fresh
clone starts with it unset; the Mac set it in lobby, Fresh AND NEXgen (NEXgen's unset state above was
the old machine's, not a ruling). **AGY deliberately leaves hooksPath unset on the POSIX side**: it is a
submodule there (`.git` is a pointer file; real hooks dir is
`<lobby>/.git/modules/Projects/AGY_AVIATIONCHAT/hooks`), and machine-local stubs in that dir CHAIN
both systems — `.githooks/` (encoding + recorder) plus `scripts/git-hooks/board-stale-stamp.sh`
(post-commit + post-merge). Setting hooksPath there would silence the board stamp. Also fixed
fleet-wide that day: every tracked hook/script was committed from Windows as 100644 — git *skips* a
non-executable hook with only a warning, and an executable hook exec-ing a non-executable script
*blocks the commit* (exit 126). Exec bits are now committed (100755) in all four repos.
