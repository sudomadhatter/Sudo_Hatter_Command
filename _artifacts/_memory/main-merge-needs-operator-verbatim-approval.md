---
name: main-merge-needs-operator-verbatim-approval
description: "Since SCC-37 (2026-08-14), minting the main-push token in any non-interactive shell REQUIRES --operator-approval '<the operator's verbatim, this-turn merge words>' — ticket status and finish directives are never merge permission."
metadata: 
  node_type: memory
  type: project
  originSessionId: fa9d9cea-f3e1-490d-a5de-dbb37666b922
  modified: 2026-08-15T02:35:45.393Z
---

`mint-push-token.sh` (lobby, since SCC-37 landed 2026-08-14) refuses to mint in a non-interactive
shell without `--operator-approval '<verbatim quote>'`. The quote is recorded in the token
(`approval=` line), printed back at mint AND at push, and `pre-push-main-approval.sh` refuses +
consumes any token without it. Single use, 30-minute TTL, mint AFTER CI green, never commit after
minting.

**Why:** mechanizes [[one-shot-permission-persists-in-context]] — a finish directive earlier in a
session, or a ticket moved to review, kept being read as standing merge permission. Now the gate
itself demands the operator's words for THIS merge, this turn.

**How to apply:** stage everything (absorb → receipts → merge --no-ff → gate ref → CI green),
then STOP — **parked merge-ready, and the OPERATOR initiates.** ⛔ Never *solicit* the approval
words (ruled 2026-08-14, after the gate "bit twice"): an agent asking "give me the words" is how
approval gets hallucinated — any warm reply starts to read as the yes — and it pressures the
operator. Park, state what is awaited (→ [[review-status-means-needs-operator]]), and wait. The
three doors: their word `approved` (or equivalent explicit this-turn words — after an
awaiting-review park, **"its done" IS the words**), `/cicd-push-e2e`, `/smh-close-task-merge-tree`.
Pass their exact words to `--operator-approval`. Never reuse an earlier quote, another lane's
quote, or paraphrase. One landing = one quote. Landing throughput is therefore serialized on the
operator by design — see [[git-branch-model-standard]] and [[closeout-target-is-a-machine-contract]].

Live consequence the same afternoon: parallel lanes queue on main one merge per push
(`main_write_gate` refuses batches server-side); a lane that merges locally and stalls before its
push silently queues everyone behind it — the close-out preflight "local main ahead of origin"
early-warning is the open follow-on for that.
