---
name: acli-cannot-reparent-a-subtask
description: "acli has no way to move a subtask to a different parent — so \"split this ticket in half\" is not a board operation, and a partial landing must keep the original parent open."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 100e17d0-7dc2-41d5-bd8c-bb4a23d449bf
  modified: 2026-08-16T08:52:54.303Z
---

`acli` cannot re-parent an existing work item. Verified mechanically 2026-08-16 during SCC-164's
close-out: `acli jira workitem edit --help` has no `--parent` flag, and `acli jira workitem
edit --generate-json` emits a schema with only `assignee`, `description`, `issues`, `labelsToAdd`,
`labelsToRemove`, `summary`, `type` — no `parent`. (`workitem create` **does** take `--parent`, which
is what makes the gap easy to miss: you can birth a child under a chosen parent, never move one.)

**Why it matters:** the obvious response to a partial landing is "close the parent, open a fresh one
for the second half." That is not available. The only two things you can actually do are both worse
than leaving it alone:

- close the parent anyway → the carried subtasks are stranded under a `Done` parent, which is exactly
  the board lie `/smh-close-task-merge-tree` Step 4 forbids
- recreate the subtasks under a new parent → duplicates that lose their comments, Dev Records and history

**How to apply:** on a `landing_mode: partial` lane, the original parent **stays open** and the next
lane reuses it — this is what the landed rule in `smh-close-task-merge-tree.md` Step 4 means by *"the
parent closes at that lane's ceremony, when the last child does."* "A new task for the second half"
means a new **lane** (branch + worktree + `task.yaml` riders), never a new parent ticket. If a genuine
re-parent is ever unavoidable, it needs the REST API (`PUT /rest/api/3/issue/{key}` with
`fields.parent`), not acli.

Related: [[jira-integration-live]] · [[cross-repo-work-needs-a-ticket-per-repo]] ·
[[review-status-means-needs-operator]]
