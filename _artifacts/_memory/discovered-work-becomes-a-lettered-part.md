---
name: discovered-work-becomes-a-lettered-part
description: "Out-of-scope work found mid-task does NOT become a new ticket — it becomes the next lettered PART of an existing parent Task, minted as a SUBTASK under it (parent description = the index), and the parent runs as ONE branch with the subtasks as riders. Verbatim 2026-08-15: 'we are not developing 3 task for every 1 we try to fix.' Being promoted to law on SCC-170."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ce65cc5a-a1af-4f79-be33-c2f12f606bd3
  modified: 2026-08-16T00:56:03.653Z
---

**The rule:** when a lane turns up real work it genuinely cannot land (out of its named SCOPE,
or a blocking-gate decision it has no ruling for), the disposition is **not a new ticket**. Find
the existing parent Task whose subject already covers that surface (match on SCOPE overlap — the
open ticket whose parts name the same file/script) and mint it as the next lettered **PART** —
**as a SUBTASK under that parent** (`Part E of SCC-164`, with its own `ACCEPTANCE E` and
`SCOPE E`), plus ONE index row in the parent's description. The operator runs the parent as ONE
branch with every subtask a `riders:` entry in `task.yaml` (SCC-156); the close-out flips the
riders, then the parent.

⛔ **Ruled 2026-08-15 — parts live as SUBTASKS, never as text in the parent.** SCC-164's parts
first landed as comments/description blocks ("A, B, C, D… as notes") and the operator's verdict was
"a mess… we need to move these all to sub task." The parent description is an INDEX only.

**Why:** *"we are not developing 3 task for every 1 we try to fix"* (verbatim, 2026-08-15). One
fix spawning three tickets is the residue-ticket loop one level up — the queue never drains. This
extends [[review-findings-are-not-a-work-queue]] past review findings to **anything** discovered
mid-task. Look first — check the board for an open parent that covers the surface — then add it there.
If nothing fits, minting is fine: say in one line what you looked at. Operator, same day: *"the goal
is the agent looks first and tries … this is not black and white."* Judgment, not a gate.

**How to apply — and the parent-index write is the dangerous half.** `acli jira workitem edit
--description` **REPLACES** the whole field, so a careless index update silently deletes rows —
it happened the same day: E7 was appended to SCC-164 by one session while another rewrote the
description, and E7 had to be recovered from a transcript. So:

1. `acli jira workitem view <KEY> --json --fields description` → walk the ADF for `text` /
   `hardBreak` nodes to recover the raw plain text (the rendered `view` output is reformatted and
   is NOT safe to write back).
2. Create the SUBTASK first (`create --type Subtask --parent <KEY> --description-file`), then
   insert its one-line row into the parent index at an asserted anchor — refuse to write if the
   anchor is missing or the fetched text differs from what you last read.
3. Write, then **READ IT BACK** and assert every prior row/heading survived. Never trust the write.

Match the house style: the defect, the measured evidence with `file:line`, the reproduction, a
numbered `ACCEPTANCE`, a `SCOPE` list, and any shared open decision named as shared.

**Worked example:** SCC-163's review found that the blind adversarial pass is law with nothing
enforcing it. That became **SCC-164 Part E** (2026-08-15) — not SCC-167 — because SCC-164 already
owned command-surface correctness and already carried the identical arm-vs-warn open decision.
Related: [[blocking-gates-need-a-quoted-ruling]] · [[settled-decisions-are-not-gaps]] ·
[[lightweight-lane-for-specific-no-break-work]].
