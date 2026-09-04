---
name: review-is-narrated-until-the-block-is-in-the-walkthrough
description: "A ③ review that ran, found, and fixed everything is still INVISIBLE to close-out until its engine return (lenses_run roster + Verdict line) is pasted into the walkthrough's ## Code Review — the preflight then blocks a finished story as 'the review step has not run'."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ccec7e02-346d-4d32-b2ff-da2abcb9d9b6
  modified: 2026-09-02T19:03:39.489Z
---

**`/cicd-code-review` is not finished when the findings are fixed. It is finished when the
`## Code Review (<date>)` block — `review-runtime:`, the `lenses_run:` roster rows, `dispositions:`,
`drift:`, a `### Step 0.7` subsection with ≥3 list rows, and `Verdict: … @ <sha>` — is IN the
walkthrough, unfenced.** AVCH-109 (story 24.7, 2026-09-02) ran two full review passes in fan-out
(five lenses in isolated worktrees, then three more plus a 19-mutant sweep), closed every finding in
lane, and reached `closeout_preflight.py` with **no `Verdict:` line at all**. The review had been
narrated in two prose sections and never recorded in the one form `walkthrough_roster.py` reads.

**Why:** SCC-173's whole point — a narrated review and a run review look identical to anything
downstream. The preflight's `artifacts` row blocks on it, and the FIX is cheap only while the session
that ran the lenses is still alive: the roster is recoverable from that session's own subagent log
(the `"description":"<Lens> lens <KEY>"` entries in the transcript), and from nothing else.

**How to apply:** at the end of ③, before reporting, run
`python .agents/scripts/walkthrough_roster.py <walkthrough>` and read `verdict`, `lenses_counted`,
`drift`, `rederive_lines` (needs ≥3) — all four non-null or the review is not done. If a later
session finds the block missing: recover the lens names from the transcript's subagent descriptions
and write what actually ran, with each row's reason naming the pass and SHA. **Never invent a roster**
— a roster that claims more independence than the review had is the exact failure the parser exists
to refuse. Related: [[walkthrough-machine-read-lines-must-be-unfenced]],
[[quick-level-roster-refused-under-fanout]], [[gate-receipts-file-under-the-board-key-slug]].
