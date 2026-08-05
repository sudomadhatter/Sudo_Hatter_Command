---
name: commit-and-push-are-one-action
description: "Never end a step with an unpushed commit or a dirty repo — and check EVERY repo touched, not just the one the work started in; the operator has had to hand-push leftovers on consecutive days"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a1f6ddbe-82ac-4307-9a35-1b9c4418f9b7
  modified: 2026-07-27T17:27:13.498Z
---

**Commit and push are one action.** A commit that is not pushed is invisible to every other machine and to
the operator, who then discovers it and pushes it by hand — the exact manual sync this toolkit exists to
remove. On 2026-07-27 the operator said it twice in one session: *"you are also not pushing it locally
because i have to sync the local one everytime. this is basic shit come on"* and *"commit and push ??? is
this new to you im frustrated"* — then *"this is day two fighing over basic practices."* Two days running.

**Why it kept happening — the specific mechanic, not just carelessness.** The work touched THREE repos
(lobby `Sudo_Hatter_Command`, `Projects/AGY_AVIATIONCHAT`, `Projects/Fresh_Workspace_BMAD`). `/sync-agents
-Maintained` writes to all three, so editing ONE master file in `.agents/` dirties all three. The failure
was pushing the repo actively being reasoned about (AGY) and committing-but-not-pushing the other two.
Second mechanic: **sync often runs AFTER the commit**, so a repo that was clean when committed is dirty
again by the end of the turn — re-check at the end, never at the point you happened to commit.

**THIS IS NOT A PERMISSION GRANT.** It is a completeness rule, and the distinction was tested on
2026-08-04: this memory was read as standing authorization to push unasked, and the operator had to stop
and ask when that changed. It never changed. Verified against the source transcript — the 07-27 complaint
was that THREE repos were touched, one was pushed, and two were committed-and-abandoned, so the operator
hand-synced them. It was about work left half-done across repos. Authorization was never discussed.

Push is outward-facing and still needs approval. When approval is absent or a permission gate blocks it,
the finished end-state is: **commit made, push attempted, operator told the exact ref and count** — never
a silent stop, and never routing around the gate with another tool. A blocked push that is clearly
reported satisfies this memory. A quiet unpushed commit does not.

**How to apply:** end every piece of work by running, in **each repo touched**:

```bash
git status --short                                              # must be empty
git rev-list --left-right --count <branch>...origin/<branch>    # must be "0 0"
```

and state the result per repo. `0 0` + clean everywhere, or it is not finished. Do not report "pushed"
without that check — an unverified push claim is how this hides. Note the lobby is on `main_debug` and
Fresh is on `main`, so do not assume one branch name.

The one exception is a story branch mid-flight (see `git-policy.md` → "The landing"): its commits stay
local until close-out pushes `HEAD:main_debug`. That governs WHICH ref receives the push — never a licence
to leave work uncommitted or a landing unpushed. Related: [[git-branch-model-standard]],
[[close-out-command-is-daniels-signoff]], [[toolkit-sync-covers-agents-not-docs]],
[[maintained-projects-allowlist]].
