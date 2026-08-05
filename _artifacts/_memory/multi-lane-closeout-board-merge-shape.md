---
name: multi-lane-closeout-board-merge-shape
description: "/sudo-merge-epic-workingtrees proven 08-01 on {21.9,21.10,21.11}: board STORY-LINES conflict at every lane merge (mechanical fix), the one-line change log auto-merges, and a lane's board line can lag its story file — flip from the story file's status."
metadata: 
  node_type: memory
  type: project
  originSessionId: 08176105-f8ef-439d-8aad-8d73828c696e
  modified: 2026-08-02T03:51:47.456Z
---

First run of the multi-lane set close-out (2026-08-01, AGY, set {21.9, 21.10, 21.11}) proved the merge
shape, and it repeats:

- **`sprint-status.yaml` story-status LINES conflict at EVERY lane merge** (adjacent lines, different
  lanes) — the resolution is mechanical, never judgment: keep the TRUNK's lines for already-landed
  siblings (their `done` is newer) + the LANE's line for its own story. The CHANGE LOG never conflicted
  across three concurrent close-outs — the one-entry-per-line design ([[landing-is-not-closeout]]'s
  29k-line lesson) works as built.
- **A lane's board line can lag its own story file** — 21.11's board line still read `ready-for-dev`
  while its story frontmatter said `review` with a ③ verdict on disk. Close-out flips from the STORY
  FILE's status; the board line advances straight to `done` (statuses only ever advance).
- **A `git status`-dirty worktree file with an EMPTY `git diff` is a CRLF phantom** (Windows) —
  `git restore` it; never commit line-ending noise as "uncommitted work" in Step 2 pre-flight.

**Why:** the next multi-lane close-out will hit the identical conflict block and should resolve it in
one pass instead of re-deriving; and a board-vs-story-file disagreement must not stall a flip.

**How to apply:** at each lane's trunk merge, expect ONE conflict block spanning the set's story lines;
keep trunk's landed lines + the lane's own. Related: [[parallel-lanes-fix-the-same-finding]] (the
overlap re-diff that makes the order safe).
