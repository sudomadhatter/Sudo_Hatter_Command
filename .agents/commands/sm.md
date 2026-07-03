---
description: BMAD Scrum Master tasks — story prep, sprint planning, sprint status
platforms: [opencode]
---

No dedicated SM persona skill exists in this Claude install (the BMAD update removed it). Route on the user's intent:

- create the next story    → invoke `bmad-create-story`
- plan / generate a sprint → invoke `bmad-sprint-planning`
- check sprint status      → invoke `bmad-sprint-status`

If the intent is unclear, default to `bmad-create-story`.

User input: $ARGUMENTS
