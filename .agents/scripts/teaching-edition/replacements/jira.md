---
name: jira
description: "Generic Jira operating law for a command center whose projects opt into their own site, key, and board. Load for board, backlog, ticket, sprint, or acli requests."
trigger: model_decision
triggers: [jira, ticket, the board, backlog, sprint, acli, in progress, what's next, to do next]
---

# Jira operations — optional and project-owned

## No binding means no board

A downloaded command center is a shell. It has no Jira board by default, and creating a project from
`sudo-project-skeleton` does not create one. Never infer a board from ambient Atlassian credentials.

Before any Jira read or write:

1. Resolve the named project under `Projects/<name>/`.
2. Require that project's `.agents/jira.conf`.
3. Require both `JIRA_SITE` and `JIRA_KEYS` in the binding.
4. Run `acli jira auth status` and require the authenticated site to exactly match `JIRA_SITE`.

If the file is absent, incomplete, or still contains a placeholder, say that Jira is not configured
for this project and stop. If authentication points at a different site, report the mismatch and stop
without querying either site. The command center's own shell also remains unbound unless its owner
deliberately gives it a separate board.

## Optional setup after a board exists

Only after the owner has created or selected the project's Jira site, project key, and board:

```bash
cd Projects/<name>
cp .agents/jira.conf.example .agents/jira.conf
# Set JIRA_SITE and JIRA_KEYS in .agents/jira.conf.
acli jira auth status
touch .agents/scripts/git-hooks/JIRA-ENFORCE
```

The auth token belongs in the operating system's credential store, never in `jira.conf`, a commit, or
chat. The binding answers which site/project this repository is allowed to use; authentication only
proves that the current machine can reach Atlassian.

## Reading the queue

Read `JIRA_KEYS` from the bound project; never invent, substitute, or remember a key. For each bound
key, answer “what's next?” by querying these ranks in order and stopping at the first non-empty rank:

1. `In Progress` — finish started work first.
2. `To Do Next` — the owner has deliberately chosen it, when that status exists on the board.
3. `To Do` — the backlog.

Blocked work is an impediment, not a next-work candidate. Status names are board-owned: an optional
status returning no rows is a fall-through, while a failed query is an error to report rather than a
reason to guess. Use ordinary JQL, one query per rank; JQL does not support SQL-style `CASE` ordering.

```bash
P=<one key read from JIRA_KEYS>
acli jira workitem search --fields "key,summary,status" --jql "project = $P AND status = \"In Progress\" ORDER BY key"
acli jira workitem search --fields "key,summary,status" --jql "project = $P AND status = \"To Do Next\" ORDER BY key"
acli jira workitem search --fields "key,summary,status" --jql "project = $P AND status = \"To Do\" ORDER BY key"
```

Never answer the queue from `_my_resources/open_tasks/todo_list.md`; it is personal notes, not the
live board.

## Writes and guardrails

- Never invent or reuse a ticket key because a Jira call failed.
- Never mint, transition, retype, re-parent, or delete a work item unless the active workflow calls
  for that write and the project binding/auth preflight passed.
- Read an item back after every write and verify the requested state.
- Keep repository commits bound to that repository's declared `JIRA_KEYS`; do not use a different
  project's key to satisfy a hook.
- Treat an `acli` failure inside a sandbox as “this shell could not see Jira,” not proof that a board
  or ticket does not exist. Re-run with the required authority before drawing a board conclusion.
- Ticket type and hierarchy are project workflow decisions. Follow the current project command and
  SOP rather than copying an example topology from another organization.

The command center's live workflow commands own the exact mint, review, close-out, and shipping seams.
Open the current command body before acting; this rule supplies the safe binding and board boundary,
not a second frozen copy of the development workflow.
