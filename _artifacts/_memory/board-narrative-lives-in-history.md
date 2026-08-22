---
name: board-narrative-lives-in-history
description: "Since the Wave 4 split (2026-08-03) AGY's sprint-status.yaml is bare state (~62 KB); row narrative is in _bmad-output/history/ and a note on a finished row is a lint ERROR"
metadata: 
  node_type: memory
  type: project
  originSessionId: d9adc5bc-e814-4396-b913-62eac264ecce
  modified: 2026-08-04T03:35:28.773Z
---

AGY's `sprint-status.yaml` was split 2026-08-03 (baseline commit `0752c437`, migration
`43331b58`+follow-ups): **363,334 → 62,040 bytes**, byte-for-byte lossless (reconstruction
verified against the pinned blob after every stage; `.pre-split` rollback copy held one sprint,
stored `-text` so git cannot re-normalize it).

**Where things live now:**
- `sprint-status.yaml` — bare `key: status` rows + epic banners + doctrine comments + a real
  `last_updated:` key (refreshed by `story_status.py set`). Live rows may carry a ≤120-char note.
- `_bmad-output/history/<epic>/<key>.md` — every moved row note, verbatim.
- `_bmad-output/history/CHANGELOG.md` — the change log; **close-outs append THERE now**, not to
  the board.
- `_bmad-output/history/migration-manifest.json` — the byte map; `split_sprint_status.py verify
  --sha 0752c437` re-proves losslessness any time.

**Why:** the board was 96 % narrative, over the Read limit, and growing ~15 KB/day; the one line
every writer edits (the key line) was also carrying 16 KB notes, making every merge a conflict.

**How to apply:** never add a narrative note to a board row — `workflow_lint.check_board_note_budget`
ERRORs on any note on a `done`/`descoped`/`deferred-v3`/`optional` row (the set is
`wf_common.NO_NOTE_STATUSES`, deliberately ≠ `TERMINAL`) and on any live note >120 chars.
`story_status.py set` drops the note automatically on a flip into a no-note status — that is F2 of
the wave's audit, not a bug. A pre-split project (no `_bmad-output/history/`) is exempt, so Fresh
and NEXgen boards are untouched until they migrate. See [[workflow-enforcement-scripts]],
[[sudo-update-scrum-board-five-zones]], [[multi-lane-closeout-board-merge-shape]].
