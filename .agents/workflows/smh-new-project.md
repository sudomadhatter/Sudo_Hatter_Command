---
description: Scaffold a new project workspace under Projects/ by cloning the thin skeleton — no vendored toolkit.
---

# /smh-new-project

Create a new workspace under `Projects/<name>` by cloning the **thin skeleton**
(`sudomadhatter/sudo-project-skeleton`): pointer `CLAUDE.md`/`GEMINI.md`, a workspace `AGENTS.md`
(Map/Mission/Support + routing table), a tier-2 `.agents/` holding only its OWN law, `_bmad/` +
`_bmad-output/`, `_artifacts/`, the FastAPI/Next stack, and its own git repo with hooks armed.

**It carries NO shared toolkit** — no `/` commands, no shared rules, no skills, no sync. Sessions run
from this command center, so tier 1 is already loaded (`.agents/rules/project-law.md`).

Argument (`$ARGUMENTS`): the new project's folder name.

Run (PowerShell):

```
& ".agents/scripts/new-project.ps1" -Name "$ARGUMENTS"
```

Then finish the wiring — the script prints these, do them in order:

1. **`router.md`** — add a row mapping the kind of work to `Projects/$ARGUMENTS/`.
2. **Submodule** — `git submodule add <remote-url> Projects/$ARGUMENTS` if it should travel with the
   lobby (`Projects/` is git-ignored here otherwise).
3. **Placeholders** — grep the new project for `{{` and `<PROJECT_NAME>`: `AGENTS.md`,
   `.agents/INDEX.md`, `_bmad-output/project-context.md`, `_my_resources/open_tasks/todo_list.md`.
4. **Localize the map** — `python3 .agents/scripts/generate_repo_map.py --root "Projects/$ARGUMENTS"
   --ignore _my_resources,_bmad --mode auto` (run from the lobby; the template's AUTO tree carries the
   skeleton's own root name until you regenerate, so `check_maps` would flag it stale).

**Optional, when it gets a Jira board:** `cp .agents/jira.conf.example .agents/jira.conf`, set
`JIRA_KEYS`, then `touch .agents/scripts/git-hooks/JIRA-ENFORCE` to arm REJECT mode. Until then the
commit gate no-ops — a fresh project is never blocked by a board it doesn't have yet.

**Optional:** add it to `.agents/maintained-projects.txt` if the `check_maps --all` lint should cover it.
