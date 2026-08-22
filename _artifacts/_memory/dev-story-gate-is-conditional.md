---
name: dev-story-gate-is-conditional
description: "sudo-dev-story-tests pre-dev gate is conditional — stop & ask ONLY if the agent has real questions, before starting dev; else proceed autonomously."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6fc84b3c-1b22-4acd-bdae-5abbf001b059
---

`sudo-dev-story-tests` Step 2.5 (between self-audit and implement) is a **conditional** gate, NOT a mandatory "approved" stop:
- If the agent has real questions for the human (genuine ambiguity, a human-only decision, contradictory ACs, an unresolvable audit concern) → STOP, ask them up front, touch no project file until answered. This explicitly overrides the bmad-dev-story skill's hardwired "never pause / implement to completion" directive — but only at this one point, and only when there are questions.
- If there are no questions → proceed straight to implement; don't manufacture one.

**Why:** The underlying [bmad-dev-story](.agents/skills/bmad-dev-story/SKILL.md) skill is an autonomous implementer with no plan-approval pause (its "PLAN mode" referenced by the command doesn't actually exist in the skill), so without this step the human lane "just starts coding." Daniel wanted ask-only-when-needed, not a forced approval gate on every story. Related: [[restate-alwayson-obligations-in-command-bodies]], [[close-out-command-is-daniels-signoff]].
