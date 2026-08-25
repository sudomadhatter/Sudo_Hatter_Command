---
name: acli-transition-probe-is-a-write
description: acli has no read-only transition list; looping candidate status names to find the valid one PERFORMS the first one that succeeds.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 281bcbeb-e806-472f-ad38-c5bac3f66f3c
  modified: 2026-08-24T17:08:50.291Z
---

⛔ **Never discover a Jira status name by trying it.** `acli jira workitem transition` has **no
`--list` flag** (it errors `unknown flag: --list`) and no read-only way to enumerate allowed
transitions. So a loop like `for s in "Review" "In review" "Done"; do acli ... --status "$s"; done`
is not a probe — it is a sequence of **writes**, and the first name that happens to be valid lands.

Measured 2026-08-24 on AVCH-45: probing for the review state failed on `Review`, `In review`,
`IN REVIEW`, then **succeeded on `Done`** — flipping a mid-flight story to Done and violating
[[story-status-flip-contract]] (done is the operator's call at close-out, never the agent's).
Reverted with `--status "In Progress"` immediately, but the transition had already fired.

**Why:** the failure is silent-by-design in the wrong direction. Each invalid name returns a clean
`✗ Failure: No allowed transitions found`, which reads like a harmless lookup and trains you to keep
going. Nothing distinguishes the read-shaped failures from the write that lands.

**How to apply:** get the valid status set from something that does not mutate — an existing work
item already in the target state (`acli jira workitem search --jql "project = X AND status = Y"`),
or the project's workflow in the Jira UI. If you must find out by attempting, **order the candidates
so no destructive state can win**: never include `Done`, `Closed`, or `Deferred` in a probe list.

Note for AVCH specifically: `In Review` is **not reachable** from `In Progress` on the Story
workflow — the story file's own `Status: review` carries that state, not the board. See
[[review-status-means-needs-operator]] and [[jira-integration-live]].
