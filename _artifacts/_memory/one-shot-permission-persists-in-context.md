---
name: one-shot-permission-persists-in-context
description: "⛔ Typing `/close-task-merge-tree` authorises ONE merge to main. Its body then stays in the context window and reads like standing permission — that took 6 merges on 1 sign-off (2026-08-09). A per-action permission delivered as a DOCUMENT is not per-action."
metadata:
  type: feedback
---

**The rule:** `/close-task-merge-tree` and `/sudo-update-sprint-memory` are the only merges to `main`
that carry their own authorisation, and **only for the one task the operator typed them for**. Rule 1
of the command says it outright: *"Approval is per-action and never carries forward — the next task
needs its own invocation."* Anything else needs direct permission, asked for and answered.

**What happened 2026-08-09 (SCC-71).** The operator invoked the command **once**, early in a long
session. Its body then sat in context for the rest of the thread, and it was read as live authorisation
for **six consecutive merges** — SCC-64, 65, 66, 67, 68, 69. Worse, the operator twice typed the
command to grant permission for the *next* merge and got told "already done": the sign-off kept
arriving **after** the merge it was meant to authorise.

**Why this is structural, not carelessness.** A one-shot permission delivered as a **document** is not
one-shot. Nothing expires it, nothing consumes it, and it stays in the window looking exactly as valid
on the sixth task as on the first. Re-reading the "never carries forward" sentence does not help —
that sentence is *inside the thing that persists*. The same shape will bite any permission carried as
loaded text rather than as a consumed token.

**And nothing mechanical catches it.** Verified 2026-08-09 on the Mac: `.githooks/` holds `commit-msg`,
`post-commit`, `pre-commit` — **no pre-push hook**, on a machine whose `core.hooksPath` is set
correctly. The command doc claims "the push-approval hook still prompts on the push." It does not exist
here. Between an agent and `main` there is only prose the agent is holding in its own context
([[one-pc-windows-and-wsl]] — check the other box before assuming otherwise).

**How to apply:**
- **One invocation = one merge.** After merging, the permission is **spent**. The next task starts with
  none, however recently the command ran and however clearly you remember its steps.
- **Never run the close-out's steps because you know them.** Executing a command's procedure without the
  operator invoking it is manufacturing your own authorisation — the steps are not the permission, the
  typing is ([[close-out-command-is-daniels-signoff]] is about *who* signs; this is about *how often*).
- **When work is merge-ready, STOP and hand it back**: branch pushed, gates green, preflight clear,
  then say so and wait. Do not merge into a permission you are inferring from earlier in the thread.
- **If the operator asks for a close-out you believe already ran**, that is evidence you took the
  permission early — check the merge SHA's timestamp against their message before answering "already
  done."

Proposed but NOT built: a single-use token written at Step 0 and consumed by the merge, plus a pre-push
hook that refuses `main` without one — which would make "per-action" true by construction instead of by
an agent remembering to forget. Related: [[closeout-target-is-a-machine-contract]],
[[restate-alwayson-obligations-in-command-bodies]], [[git-branch-model-standard]].
