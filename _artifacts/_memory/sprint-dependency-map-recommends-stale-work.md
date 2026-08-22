---
name: sprint-dependency-map-recommends-stale-work
description: "AGY's scrum board (sprint_scrum_board_map.md, ex sprint-dependency-map.md) drifts days behind sprint-status.yaml and its \"run this next\" advice goes actively wrong — reconcile against the YAML before quoting it."
metadata: 
  node_type: memory
  type: project
  originSessionId: d1bc5de1-b28b-40c0-a47b-3d0e4c6de41a
  modified: 2026-08-08T17:39:50.698Z
---

**RENAMED 2026-08-02:** the board is now `sprint_scrum_board_map.md` (same folder), rebuilt by
`/sudo-update-scrum-board` (ex `/update-personal-sprint-map`) — see [[sudo-update-scrum-board-five-zones]].
The lessons below predate the rename and still bind.

`Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sprint_scrum_board_map.md` is hand-maintained
and lags `_bmad-output/implementation-artifacts/sprint-status.yaml`. On 2026-07-25 it was 5 days stale and
its headline recommendation was wrong in **both** halves: it told the operator to run `/sudo-quick-dev
debug.7` (closed 07-21, along with debug.6 and debug.8) and to start `19.1` as the main line (all of
Epic 19 was `deferred` **at that date** — it REOPENED 2026-08-08, so do not read this as current epic
state; see [[agy-epic-19-deferred-pin-cascade]]). It was also missing Epic 21 and
epic-debug-2 **entirely** — nine backlog rows invisible, which reads as an empty backlog, not a gap.

**Why:** the doc carries prose recommendations ("the one-liner", lane maps, quick-dev candidates), not just
status columns. A status table that goes stale looks stale; a *recommendation* that goes stale looks
authoritative. Nothing regenerates it — only `/sudo-update-sprint-memory` and manual passes touch it, and
neither is guaranteed to run.

**Partial fix landed 2026-07-25.** `/update-personal-sprint-map` now rebuilds the board as a fixed-order
ticket board, and its Step 1 forbids inheriting the previous board's epic list — the epic list must be
enumerated fresh from the YAML every run, which is the specific rule that would have caught the missing
Epic 21. It also keeps `done`-but-owing items visible and collapses finished epics to one row instead of
deleting them. **This does not make the doc self-maintaining** — nothing runs the command automatically,
so a board that nobody rebuilt is still exactly as stale as before. The check below still applies.

**Second failure mode, found 2026-07-27: a row can be in the WRONG LANE, not just stale.** The Quick-dev
queue carried "17.3 `/sudo_admin` tap-through" with a `/sudo-quick-dev` next-command — but 17.3 is `done`
and what it owes is a **manual live pass**, which the map's own rule table routes to the Operator queue
(`done` but owes a live test → Operator). The generator picked the adjacent row ("small, contained → Quick-dev").
It was also already tracked in `active-context.md` § Live passes, so it was a duplicate as well as
mis-laned. Re-laned on the 07-27 close-out; the queue's rows now carry a note explaining the rule.

**Why this one is nastier than staleness:** a stale row points at real work that has moved on. A mis-laned
row invents work that does not exist — it tells an agent to *develop* something whose only remaining step
is a human clicking a button, and an agent that trusts the next-command will happily open a worktree and a
story file for it. The operator caught this one by asking "where did these come from?"

**How to apply:** before acting on a row's next-command, check the underlying story's **status**. A row
recommending dev work on a `done` story is a lane error, not a backlog item — fix the lane, don't build the
thing. Then, before quoting or planning off that doc, dump ground truth first —
`python -c "import yaml; d=yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml',encoding='utf-8')); print({k:v for k,v in d['development_status'].items() if v!='done'})"`
(use `backend/.venv/Scripts/python.exe`, per [[agy-canonical-test-venv]]). The doc's own header says the
YAML wins — take that literally. When you touch the map for any reason, reconcile the *recommendation*
sections too, not just the row you came for. Note the YAML lags on purpose for in-flight worktree stories:
③ `/sudo-code-review` never writes `sprint-status.yaml` (see [[story-status-flip-contract]]), so a story
at `review` in a worktree still shows `backlog` there.
