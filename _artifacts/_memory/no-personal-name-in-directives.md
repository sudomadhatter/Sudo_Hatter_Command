---
name: no-personal-name-in-directives
description: "Don't hardcode \"Daniel\" in command/skill directive bodies — the toolkit is shared by a team; use a generic referent."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6fc84b3c-1b22-4acd-bdae-5abbf001b059
---

When authoring or editing the `.agents/` command/skill bodies, do NOT write the user's name ("Daniel") into the instructions — "it could be anyone on my team." Use a generic referent instead (e.g. "the human", "ask which project", "if it wasn't handed to you").

**Why:** The sudo-* toolkit is shared across the team and synced to every project + surface; a directive that names one person reads wrong for everyone else who runs it.

**How to apply:** New/edited directive text stays name-free. Note this is about *directive bodies the agent executes* — lots of pre-existing toolkit text still says "Daniel" ("ask Daniel", "Daniel's call at close-out", the _AP files, `## OPEN QUESTIONS FOR DANIEL`); a full toolkit-wide sweep of those is a separate, deliberate task — confirm scope before doing it (the standing rule is [[own-it-plainly-dont-make-excuses]] / "don't break what works"). The "Your Actions" walkthrough section convention comes from `artifacts-always-first`. Related: [[restate-alwayson-obligations-in-command-bodies]].
