---
name: review-status-means-needs-operator
description: "Operator ruling 2026-08-14: `review`/`In Review` = the ticket needs something from the operator that the agent cannot do. An escalation flag, never a routine stage for Tasks."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f6e3053-d4b6-40eb-8dd6-bfa2e3469d85
  modified: 2026-08-15T02:45:09.860Z
---

**The ruling (2026-08-14, during SCC-156):** *"Review is reserved for storys that need someting form me. something you can not do."*

A Task's normal life is `In Progress` → `Done`, and `Done` is written by the close-out ceremony the operator invokes. `review` is NOT a resting state for finished work — it is a flag meaning "blocked on the operator: a decision, an authorization, an action outside the agent's reach."

**Why:** During SCC-156 the agent treated `review` as "dev finished, awaiting sign-off" (the BMAD story contract from [[story-status-flip-contract]]) and framed Dev Records and hand-backs that way. That is AVCH/BMAD **story-lane** law and does not cross into the SCC Task lane. The old `jira.md` line "In Review is finished work waiting on a human" was close enough to the BMAD prior to invite this misread. **That follow-on has LANDED** (verified 2026-08-21, SCC-213): the misleading sentence is gone and `.agents/rules/jira.md` §Statuses now carries the ruling in the status table — `In Review` = "blocked-on-operator ONLY … never a resting state for finished work". The same table also records that `In Review` exists on **AVCH only**, not on SCC.

**How to apply:** Never move an SCC Task (or subtask) to `review` because the build finished. Use it only when the walkthrough's `## Your Actions` has a genuine operator-only item blocking progress. Dev Record `Outcome:` lines should never say "-> review" for a task that is simply merge-ready.

**The universal law this sits under (operator, 2026-08-14 — ALL lanes, AVCH included):** the
operator acts in **WORDS only** — `approved`, "its done", or invoking a command. The **agent
performs every board write**, always inside a ceremony those words triggered, never on its own
judgment. A flow that leaves the operator a manual Jira edit is **broken by definition** — the
agent stops and says so; it never punts the edit. Status-as-gate gates the AGENT, never the
operator: *"there are so many gates thats not one I want."* Rule text must be phrased as WHEN
(inside which ceremony), never WHO (human vs agent) — the WHO phrasing is what turned a
self-certification ban into operator data entry ([[story-status-flip-contract]]).

**The full loop (operator, same ruling):** *"I will tell you its done then you move it to done and close the working tree and merge to main."*

1. Agent hits an operator-only item → ticket to `review`, `## Your Actions` names exactly what, lane parks merge-ready. Agent STOPS — and never solicits approval words ([[main-merge-needs-operator-verbatim-approval]]).
2. Operator does their part and says **"its done"** (their words, that turn). That IS the approval for that one landing — not a fourth door, door 1's words.
3. Agent runs the whole close ceremony: rider/subtask tickets → Done FIRST (clears `check_children`), preflight, merge to main + push with those words quoted in the token, parent ticket → Done, worktree pruned. **The agent performs every Jira write; the operator performs none** — "No were did I ever ask to start having to manually adjust the status of tasks in jira."
4. One "its done" = one landing. The next lane needs its own.
