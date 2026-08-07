---
name: fresh-workspace-living-template
description: "Fresh_Workspace_BMAD is the living/golden template for new projects; propagate rule + front-door + structure changes into it (front-door isn't auto-synced) so clones start current."
metadata: 
  node_type: memory
  type: project
  originSessionId: 88faded4-0c9d-46b6-8f96-e113a34b99fb
---

`Projects/Fresh_Workspace_BMAD/` is the **golden skeleton** cloned + renamed to start every new project. Standing Daniel directive (2026-07-06): any rule / front-door-pattern / folder-convention change at the home base must ALSO land in Fresh so new projects inherit the current setup, never a from-scratch one.

**Why:** if Fresh drifts behind the lobby, every new project starts stale and has to be hand-fixed on each clone.

**How to apply:** `.agents/**` (rules/toolkit) propagate via `/sync-agents` (additive vendor into every project incl. Fresh) — see [[toolkit-sync-covers-agents-not-docs]]. Front-door files (root `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`/`INDEX.md`), `docs/`, and folder structure are NOT synced → hand-mirror into Fresh, kept generic (no product specifics; placeholders where a real project fills in). Codified as the `living-template-sync` rule in `.agents/rules/` (+ its INDEX row). Verify: a clone+rename should need only placeholder fills, not structural setup.


**RETIRED 2026-08-07 (SCC-25, Daniel's ruling).** Fresh_Workspace_BMAD is no longer the living
template and is out of `.agents/maintained-projects.txt` — sync and map fan-out skip it; structure/rule
changes NO LONGER propagate into it. It sits on disk untouched (deliberately stale, like
[[toolkit-installed-but-deliberately-unmaintained]]) until Daniel decides disposal. There is currently
NO living template — a new project would be cut from the lobby master `.agents/` directly.
