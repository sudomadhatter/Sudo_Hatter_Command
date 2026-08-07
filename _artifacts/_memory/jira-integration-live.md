---
name: jira-integration-live
description: "Jira is LIVE for both repos as of 2026-08-07 — SCC (lobby) and AVCH (AviationChat). Every branch and commit carries a key; the commit-msg hook is ARMED (ENFORCE), so a keyless or wrong-project commit is rejected outright."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8bc78088-0a6e-4b75-b4eb-edc817c5fe79
  modified: 2026-08-07T22:09:45.398Z
---

Set up 2026-08-07 at `https://sudo-command.atlassian.net`. Two **team-managed** projects, one board
each (team-managed allows only one board per project; extra boards need a saved filter from **global**
nav, not from inside the project):

| Project | Key | Repo | Board | Sprints |
|---|---|---|---|---|
| Sudo Command Center | `SCC` | `Sudo_Hatter_Command` (lobby) | 2 | on — Sprint 1 active, runs to the Sep 1 soft launch |
| Aviation Chat | `AVCH` | `AGY_AVIATIONCHAT` | 3 | on |

**The join is a literal string.** Atlassian's *GitHub for Atlassian* app links a commit/branch/PR to a
work item by finding `KEY-number` verbatim — there is no other mechanism. It reads the **branch name**
too, so a correctly-named branch covers every commit on it even if one message forgets the key. See
[[git-branch-model-standard]].

**The gate is ARMED, in both repos.** `.agents/scripts/git-hooks/commit-msg-jira.sh` via a
`.githooks/commit-msg` shim; mode flag `.agents/scripts/git-hooks/JIRA-ENFORCE` is **tracked on
purpose** — untracked it would be armed on one machine and silent on every other clone. A commit with
no valid key for that repo is **refused**, and a rejected commit is a no-op (staged set untouched).
Each repo declares its project in `.agents/jira.conf`; an `SCC` key inside AviationChat is rejected by
design.

Exempt: merge/revert/fixup/squash subjects and in-progress rebases. Kill switch:
`.agents/scripts/git-hooks/DISABLE`. Bypass once: `--no-verify`.

**Deliberately NOT checked: whether the ticket exists.** A live lookup would put a network round-trip
on every commit and fail closed offline. A well-formed but wrong key is caught downstream — it simply
never appears on any ticket's Development panel.

**`acli` is the tool, not MCP.** `acli` 1.3.22, authenticated as `sudomadhatter@gmail.com`, token in
the macOS keychain. One binary any model can shell out to — MCP would be per-tool config drifting
across all four platforms. Flag traps: `view` takes the key **positionally** (`--key` is only on
`transition`); `project list` needs one of `--recent/--limit/--paginate`; it's `board search` and
`board list-sprints --id N`, not `board list`; `comment create` needs `--key`.

**Statuses:** `To Do` · `In Progress` · `In Review` · `Done` · `Deferred`. `Deferred` sits in the
**`To Do` category** on purpose — a Done-category status would auto-resolve and make descoped work read
as *shipped*. Descoped work goes to `Deferred` + the `descoped` label (the two were merged; team-managed
can't customise Resolution). Saved filters: `AVCH Deferred` (10003), `SCC Deferred` (10004).

**Free-tier limits shape the design.** Jira Free caps automation at 100 runs/month, so the design leans
on **Smart Commits** (`#comment` `#time` `#transition`), which cost zero quota. GitHub Free cannot put
rulesets on private repos (verified `403`), so there is **no server-side block on `main`** — an alarm,
not a lock. Daniel committed to GitHub Pro 2026-08-07; once active, `main` becomes unpushable except
through a passing PR and the docs' "alarm not lock" sections need updating.

**Docs:** `_my_resources/diagrams_guides/system/jira_integration_guide.md` (the why) and
`_my_resources/_quick_reference/jira_manual.md` (the by-hand how-to; relocated there by the operator 2026-08-07). Both carry a live-vs-not-built ledger — keep it honest.

**Still not built:** the `acli` wrapper in `.agents/scripts/`, a `pre-push` branch-name check, a CI job
failing PRs with unkeyed commits, and the `/sudo-*` wiring. That last one has **five reserved seats**
marked `JIRA-HOOK` on the stopped `epic/toolkit-centralization` branch (`sudo-create-epic-sprint.md`,
`sudo-push-e2e.md`, `sudo-update-sprint-memory.md`, `require-push-approval.py` ×2).

**How to apply:** never invent a Jira number — read it from the ticket. Branch and commit with the key
for the repo you are standing in. See [[vscode-hides-git-hook-output]] for why a warning-only gate was
not enough.
