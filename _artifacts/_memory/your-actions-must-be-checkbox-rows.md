---
name: your-actions-must-be-checkbox-rows
description: "A `## Your Actions` written as a TABLE is invisible to reconcile-actions and finish, which read `- [ ]` rows only — so finish writes Done over provably open work."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ba4e43b2-b8f7-48f3-b17a-23f1396a6d8b
  modified: 2026-09-01T16:39:11.637Z
---

⛔ `## Your Actions` must be **`- [ ]` checkbox rows**, never a Markdown table.

`jira_feed.py reconcile-actions` and `jira_feed.py finish` both parse only `- [ ]` / `- [x]` lines.
A table of the same content makes both report *"`## Your Actions` is clear. Nothing is owed"* and
`check-actions` pass clean — so `finish --apply` writes **Done** to the board over work that is
measurably still outstanding. Caught on SCC-369's own close-out: acceptance row G (the Zoo
permissions apply) was a table row, `zoo_permissions_apply.py --status` proved it open, and both
scripts still said nothing was owed.

Also required by `/smh-close-task-merge-tree` Step 3, on the lane, before the PR:
`- [x] The merge itself — lands via this branch's PR` (number-free; `finish` computes it from
whether the tip is an ancestor of `origin/main`).

**Why:** the whole exit-3 HELD mechanism exists so a walkthrough that hands the operator work
cannot close as Done. The parser is the enforcement; a shape it cannot read silently disables the
gate rather than failing loudly — the same failure mode as a fenced roster reading as absent
([[walkthrough-machine-read-lines-must-be-unfenced]]).

**How to apply:** write every operator-owed item as a `- [ ]` row with its explanation indented
under it. Run `reconcile-actions` before the PR and expect **exit 3** listing the genuinely open
rows — an exit 0 on a lane you know owes something means the section is the wrong shape, not that
the work is done. Related: [[closeout-target-is-a-machine-contract]],
[[review-status-means-needs-operator]].
