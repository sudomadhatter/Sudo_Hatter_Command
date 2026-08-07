---
name: jira
description: "How ANY agent on this machine reads and writes the live Jira board: the authenticated `acli` CLI — no MCP, no API config, plain shell. Load whenever the board comes up outside a sudo command (what's In Progress? move this ticket, mint a ticket, JQL). Carries the command cheat-sheet, the flag traps, the ticket↔file join, and the guardrails (never invent a key; status only — placement is the operator's)."
---

# Jira operations — the board is one shell command away

**The fact every platform misses:** Jira is fully reachable from this machine RIGHT NOW via
**`acli`** (`/opt/homebrew/bin/acli`), already authenticated — the API token lives in the macOS
keychain, **never** in a repo file, a commit, or chat. There is no MCP server and none is needed:
if you can run a bash command, you can read and write the board. "I have no Jira integration" is
false by design — the CLI *is* the integration, chosen precisely so every platform (Claude Code,
Gemini, opencode, Codex, Antigravity) shares one tool with zero per-platform config.

## The map

Site: `https://sudo-command.atlassian.net` — two team-managed projects:

| Key | Project | Repo |
|---|---|---|
| `SCC` | Sudo Command Center | `Sudo_Hatter_Command` (the lobby — **this repo**) |
| `AVCH` | Aviation Chat | `Projects/AGY_AVIATIONCHAT` |

Each repo declares its own key in `.agents/jira.conf`; the armed commit-msg hook rejects the wrong
project's key. Statuses: `To Do` · `In Progress` · `In Review` · `Done` · `Deferred` — **Deferred
sits in the To Do category on purpose** (a Done-category status would make descoped work read as
shipped). Descoped work = `Deferred` + the `descoped` label.

## Reading the board

```bash
acli jira auth status                                   # am I logged in, and as whom?
acli jira workitem view SCC-14                          # TRAP: view takes the key POSITIONALLY
acli jira workitem search --jql "project = SCC AND status = 'In Progress' ORDER BY key"
acli jira project list --limit 20                       # TRAP: needs --recent/--limit/--paginate
acli jira board search                                  # board ids (it's NOT `board list`)
acli jira board list-sprints --id 2 --limit 5
```

"Work on / look at everything set to <status>" is a fully supported ask: run the JQL search, then
join each ticket to its local counterpart (join rules below).

## Writing to the board

```bash
acli jira workitem comment create --key SCC-14 --body "…"        # TRAP: needs --key
acli jira workitem transition --key SCC-14 --status "In Review" --yes  # TRAP: needs --key; --yes skips the interactive confirm
acli jira workitem create --project SCC --type Task --summary "…" --description "…"
#   children of an epic: add --parent <EPIC-KEY>; --type Epic works too
```

Smart Commits (`#comment` / `#time` / `#transition` in a commit message) also work and cost zero
automation quota — but the branch-name join already links commits, so use them sparingly.

## The ticket ↔ file join (all literal strings — no magic)

- **Branch names** carry the key immediately after the prefix (`epic|claude|chore/<JIRA-KEY>-<slug>`);
  Atlassian's GitHub app links every commit on a correctly-named branch.
- **Story files** (`_bmad/bmm/stories/`) carry `jira_key:` in their frontmatter — that is the
  machine join from a ticket back to the file (and the YAML row key, which NEVER changes).
- **Jira summaries** carry the BMAD number (`Epic 12 — …`, `12.3.4 — …`) — the human join.

## Guardrails

1. **Never invent a key.** Read it from an existing ticket or branch; if none exists, STOP and mint
   one with the operator (pairing convention above). A well-formed wrong key is worse than none —
   it silently decorates the wrong ticket.
2. **Status and comments only.** Sprint/backlog placement, priorities, and board layout are the
   operator's; machinery moves STATUS and posts evidence, nothing else.
3. **Bare-state board.** Only OPEN work gets tickets. Never resurrect finished epics as tickets —
   done work is file history (`sprint-status.yaml`, `epics.md`), not board rows.
4. **Don't double-move.** Two transitions are already automated: `/sudo-push-e2e` Step 6.5 moves the
   EPIC ticket at merge; `/sudo-update-sprint-memory` Step 4.5 moves the STORY ticket at close-out.
   Outside those, transition a ticket only when the operator asks.
5. **The token stays in the keychain.** Never echo, copy, or persist it anywhere.
