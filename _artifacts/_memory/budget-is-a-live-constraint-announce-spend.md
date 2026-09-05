---
name: budget-is-a-live-constraint-announce-spend
description: Announce any subagent/fan-out spend BEFORE launching it, and when the operator says the budget is gone, no spawn happens without his word — silence while burning credits nearly ended SCC-351.
metadata:
  type: feedback
---

During SCC-351's close-out (2026-08-30) the operator said, escalating across one hour: "you used
all my ticket subscription", "You maxed out my subscription weekly limit… stay in task and fix
this", "no comuunitation you just are running the shit out of my credits", "talk or this session
and ticket are over". The work itself was correct (the review gate caught real defects) — the
failure was spending without narrating: a 5-lens fan-out, then one more lens to satisfy the roster
gate, launched with no heads-up while he watched credits drain. Also: two background agents froze
when the machine SLEPT mid-run — a hung agent may be the box sleeping, not the model working.

**Why:** he pays per token in real money and plans his week around the limit; an unannounced spawn
is spending his budget without consent, and silence reads as a runaway loop even when the ceremony
is going well.

**How to apply:** before ANY Agent/fan-out launch, say in one line what will be spawned and why it
is required (which gate demands it); after a budget complaint, NOTHING spawns without his explicit
word — find the inline/manual path instead (the engines document one: assessor-run passes,
recovered-inline, n/a-with-reason). While a long ceremony runs, narrate one line per step so he can
see it converging. Related: [[close-the-loop-dont-hand-back-decisions]],
[[exercise-the-real-cicd-doors]].
