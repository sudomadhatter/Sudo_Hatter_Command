---
description: Scaffold a new project workspace under Projects/ with the routing design baked in.
---

# /new-project

Create a new workspace under `Projects/<name>` that is born with the folder-as-workspace routing
design: pointer `CLAUDE.md`/`GEMINI.md`, a workspace `AGENTS.md` (Map/Mission/Support + routing
table), a vendored `.agents/` toolkit, an `_artifacts/<name>/` memory folder, and its own git repo.

Argument (`$ARGUMENTS`): the new project's folder name.

Run (PowerShell):

```
& ".agents/scripts/new-project.ps1" -Name "$ARGUMENTS"
```

Then finish the wiring (the one manual step): add a row to `router.md` mapping the kind of work to
`Projects/$ARGUMENTS/`, and confirm the project appears under `Projects/` (already git-ignored by the
home base, with its own initialized repo).
