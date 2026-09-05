# SCC-412 — harvest `git branch -d worktree-agent-` into the permission source

**Lane:** `chore/SCC-412-worktree-agent-allow` off `origin/main` @ `4a9f013a`
**Origin:** operator pick at the `/smh-llm-approvals` Step 2 gate, 2026-09-05.

## Why this is a lane and not the fast path

`/smh-llm-approvals` Step 4 carries an exemption that skips the plan, the audit and the review for
harvest work, on the condition that the change set touches **exactly four** paths:
`families.json`, `antigravity.json`, `.claude/settings.json`, `.vscode/settings.json`.

This change set has **six**. The door's own words: *"A fifth path, or a touched `hooks` block, voids
the exemption and the work takes the full lane."* Run, not eyeballed.

⭐ **And the two extra paths are not optional.** Adding any Zoo allow row moves the tracked count
from 125 to 127, which turns `test_zoo_permissions.py::test_guide_currency` **red** until
`terminal-permissions-guide.md` is updated. So Step 3's gate *requires* the edit that Step 4's guard
*forbids*: the fast path can never be used for a harvest that adds a Zoo allow row. That is a defect
in the door, recorded here and filed on SCC-411, not worked around.

## The pick, and what it is

The harness generates one `worktree-agent-<hash>` branch per subagent worktree; the close-out
deletes it. Measured across the 20 newest sessions: **6 stops**, the operator waiting to approve
deleting the agent's own scratch.

Three rendered rows, one family (`allow-git-branch`), no new family:

| platform | row | why this spelling |
|---|---|---|
| Zoo | `git branch -d worktree-agent-` | literal prefix; longer than the `git branch -d` deny, so it wins by length exactly as `chore/` does |
| Zoo | `git branch -d "worktree-agent-` | the quoted twin, matching the six that already exist for chore/claude/epic |
| Claude | `Bash(git branch -d worktree-agent-*)` | **bare star** — the prefix ends in `-`, and Claude reads `Bash(X:*)` as `Bash(X *)` (battery A2b) |

Antigravity gets nothing: the family is `only: ["zoo", "claude"]` and this lane does not widen it.

## Acceptance — every row checkable by a command

| # | Statement | The command that proves it |
|---|---|---|
| A | The three rows render, and only those | `git diff` of the four permission files |
| B | `permission_render.py --check` prints **in sync** for all three platforms | that command |
| C | The prefix reaches **no** protected branch — `chore/`, `claude/`, `epic/`, `main`, or a bare name — on either platform | run `zoo_verdict` / `claude_verdict` against each target |
| D | `git branch -r` is **absent**, on evidence | `git branch -rd` deletes a remote-tracking ref; `-a`/`--list`/`--merged` refuse to combine with a delete |
| E | No other allow row added, widened or re-spelled | `git diff` of `families.json` is one family's arrays +3 rows |
| F | `run_all.py` green at the tip | that command |

## Declared Change Set

- EDIT `.agents/permissions/families.json` — three rows into `allow-git-branch`, and its `why` → A, E
- EDIT `.vscode/settings.json` — the two rendered Zoo rows → A, B
- EDIT `.claude/settings.json` — the one rendered Claude row → A, B
- EDIT `docs/migrations/terminal-permissions-guide.md` — count line 125→127 and the family row → F
- EDIT `docs/.maps-state.json` — maps baseline re-anchored at 4a9f013a (housekeeping, declared not hidden)
- NEW `_artifacts/_main/2026-09-05_scc-412-worktree-agent-allow/task.yaml` — lane manifest
- NEW `_artifacts/_main/2026-09-05_scc-412-worktree-agent-allow/implementation_plan.md` — this plan
- NEW `_artifacts/_main/2026-09-05_scc-412-worktree-agent-allow/walkthrough.md` — the lane's record

`.agents/permissions/antigravity.json` is **deliberately not** in this list — the family does not
render there, and if that file moves the change was not what this plan describes.

## What this lane will NOT do

- **No `git branch -r`.** Measured 2026-09-05: `git branch -rd origin/<ref>` deleted the
  remote-tracking ref in a throwaway repo. `--list`, `-a` and `--merged` all refuse
  (`fatal: cannot use -a with -d`). Excluded on evidence.
- **No `--unset-upstream` or `--set-upstream-to`**, the costliest stops. Offered and declined.
- **No read-form rows.** `--list`, `-a` and `--show-current` are already allowed on Claude; they
  were never the cost.
