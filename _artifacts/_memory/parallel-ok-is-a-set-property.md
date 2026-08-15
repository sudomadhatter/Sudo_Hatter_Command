---
name: parallel-ok-is-a-set-property
description: "`parallel-ok` is a property of a SET at a moment, never of one story — so ① Step 1.6 cannot rule it (the siblings don't exist yet). Operator ruled 2026-08-09: it moves out of ① into an on-request parent-scoped pass. SCC-155 renamed that pass and gave it a Task-lane twin: /cicd-label-tasks (BMAD stories) and /smh-label-tasks (Subtasks), which now stamp quick-dev too. blocked STAYS in ①."
metadata: 
  node_type: memory
  type: project
  originSessionId: 58bf5a3c-75d2-4401-ab8f-a7bcaa3b2740
  modified: 2026-08-09T10:48:05.466Z
---

**The rule:** *"you can only have parallel-ok when it compares stories"* (operator, 2026-08-09).
A story is never parallel-safe on its own — only **beside a named set**, at a named moment.

**Why ① cannot rule it.** `/sudo-write-story-tests` Step 1.6 mints story 19.1's ticket **before**
19.2's story file exists, so at that instant there is nothing to compare against. It is then never
re-evaluated. A boolean label also **cannot express `🔒 after AVCH-34`** — the edge is lost. Proof it
never worked: **zero** tickets across `SCC` + `AVCH` carry any label, and the `Parallel-OK` saved
filter returns nothing.

**OPERATOR RULING 2026-08-09 — it moves out of ①.** Step 1.6 keeps `quick-dev` and `blocked` (both
are per-story facts knowable at pickup); `parallel-ok` becomes **on request**, once all the stories
for a parent are written → the parent-scoped pass.

⚠️ **That pass has been renamed TWICE; only the current names work.** SCC-56 shipped it as
`/sudo-parallel-check`, SCC-63's naming law made it `/cicd-parallel-check`, and **SCC-155 retired
that outright** and split it in two: **`/cicd-label-tasks <EPIC-KEY>`** for BMAD stories and
**`/smh-label-tasks <TASK-KEY>`** for a Task's Subtasks — one engine, `.agents/scripts/label_tasks.py`.
Both now stamp **`quick-dev` alongside `parallel-ok`**, tri-state: a label the pass did not assess is
left alone rather than stripped. So ① is no longer quick-dev's only writer.

**The four rulings that define SCC-56:**

1. **It STATES, it never STARTS.** Names each counterpart, prints the commands to act on it. Touches
   Jira; never the working tree.
2. **Scoped to ONE parent's children** — Stories under a BMAD epic **or Tasks under a grouping
   epic** (the operator said "or the task under an epic"), so it also answers the question for SCC's
   Tasks.
3. **It is a SNAPSHOT and must detect its own staleness.** Writing another story can invalidate it,
   so the verdict carries the set it was computed against — `verified <date> against N children:
   <keys>`. A stamped set that no longer matches the parent's current children reads as *"re-run
   me"*, never as a verdict. **This is the load-bearing part**, not a footnote — an undetectably
   stale snapshot is the exact failure of [[sprint-dependency-map-recommends-stale-work]] and of the
   `Deferred` saved filter (both hit 2026-08-09).
4. **Fails toward 🔒, and prints its evidence per row.** A false 🟢 puts two lanes on the same line
   (→ [[parallel-lanes-fix-the-same-finding]]); a false 🔒 costs only serialisation. Extraction from
   a story file is a judgment, so it must be auditable.

**Why a stored label is safe HERE but was not in ①:** the rot came from a per-story writer that could
never see the set. An epic-scoped pass that recomputes and **rewrites every ticket in that parent in
one go** is self-correcting on re-run. Same field, different writer, opposite property.

**The hard part is extraction, not the set math.** Distinguishing "will modify" from "mentions":
story 19.1 names `google_llm.py:119` (a path inside the venv — a reference) and
`debug_greeting.py:59` with *"leave the script's bare init alone"*. It also says **"NO
`firestore_session.py` changes — that is 19.2 entirely"** — a negative declaration handing a file to
a named sibling, the strongest free signal in the corpus. Across **123 AGY story files**: 105 name
`backend/`/`frontend/` source paths, 58 carry negative declarations, only **29** have a `**Task**`
checklist — so there is no single field to parse. Agent extracts semantically, script does the math.

**Spec source:** the retired `/sudo-update-scrum-board` Step 2.5 →
[[sudo-update-scrum-board-five-zones]] (recover with `git show 8144518^:...`).

**Precondition has teeth today:** epic 19 has **5 stories on the board and 1 story file**, so
the parent-scoped pass could not run on it — the same fact `workflow_lint` reports as its one
standing ERROR (`19-5-adk-agent-evaluation-stage-2`, active, no story file).

**How to apply:** never re-add a parallel ruling to ①; never trust a `parallel-ok` label whose stamp
does not match the parent's current children; when unsure, 🔒.
