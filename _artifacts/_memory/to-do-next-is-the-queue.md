---
name: to-do-next-is-the-queue
description: "The Jira column `To Do Next` is the operator's hand-picked work queue and outranks `To Do`; `_my_resources/open_tasks/todo_list.md` is RETIRED as an agent source — stale personal notes, never read."
metadata:
  node_type: memory
  type: feedback
---

**`To Do Next` is where the operator puts the card he wants started next.** Any "what's next?"
answer — a bare question about a project's board, or a session-boot command — leads with that
column, not with the `To Do` pile. Queue order: `In Progress` → **`To Do Next`** → `To Do`;
`Blocking` is surfaced as an impediment, never as a candidate to pick up.

**`_my_resources/open_tasks/todo_list.md` is retired as an agent source** (operator ruling
2026-08-09): *"the todo lists are now in jira … thats not something i need the agents reading now,
its replaced with 'To Do Next'."* It stays on disk as his personal notes. `AGENTS.md` §7 still
points "pick up" at it — that pointer is the stale thing, not the ruling.

**Two board facts the rules doc gets wrong** (verified against the live board 2026-08-09, not from
the doc): `jira.md` lists the statuses as `To Do · In Progress · In Review · Done · Deferred ·
Blocked`. The real SCC board runs `To Do · To Do Next · Blocking · In Progress · Done` — `To Do
Next` is absent from the doc entirely, and the doc's `Blocked` does not exist, so
`transition --status "Blocked"` hard-fails. `To Do Next` sits in Jira's **To Do category**
(verified), so queued work does not read as shipped.

**Per-board-optional, never SCC-hardcoded.** As of 2026-08-09 only SCC has the column; AVCH does
not, and the operator intends to add it there. Write the rule the way `jira.md` already writes
`Blocked` — honored wherever the board has it, silently absent where it doesn't — so adding the
column to a board is the whole install.

**How to apply:** on a BMAD project (AVCH), a card in `To Do Next` is the operator's **override of
the computed pick** — it beats `sprint-status.yaml`'s top `ready-for-dev`, because the YAML lags by
design (② and ③ never write it) and the dependency map has recommended stale work before. On the
lobby (SCC) there is no YAML at all, so the column is the only queue there is.

Related: [[jira-integration-live]] · [[sprint-dependency-map-recommends-stale-work]] ·
[[operator-chairs-the-board]] · [[agy-epic-keys-rot-silently]]
