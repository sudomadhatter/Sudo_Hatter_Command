---
name: thin-projects-center-owns-workflow-law
description: Projects carry NO vendored toolkit — only their own rules/skills/INDEX.md plus repo-local enforcement; binding a project means reading its .agents/INDEX.md.
metadata:
  type: project
---

**Converted 2026-08-07 (SCC-31 · AVCH-23).** AGY, NEXgen-VR, RAG_Pipeline_AC and the skeleton repo
were stripped of the vendored toolkit — ~7,000 files, ~1M lines. A project's `.agents/` now holds
**only**: its own `rules/` + `skills/` + an **`INDEX.md` that routes them**, plus the repo-local
enforcement set. Everything shared — rules, `/` commands, skills, scripts, sync — lives once
in the lobby and is already loaded because sessions run from there.

**The load-bearing obligation:** binding a project MEANS reading `PROJECT_ROOT/.agents/INDEX.md` and
honoring its `Load` column. Missing in a converted project → **STOP**, never a shrug. Five anchors
enforce it: §BIND, `constitution.md`, `project-law.md`, both `AGENTS.md`, and `check_maps.py`.

**Why:** one edit at the center now reaches every project and platform — the per-project sync burden is
gone. Vendored copies drifted, and the duplicate skill registrations polluted every session.

**How to apply:** authoring test — *would this be true in a project we haven't built yet?* → tier 1
(center). *Does it name this product's components, contracts, stack, domain?* → tier 2 (that project,
routed from its INDEX). Never fork a shared rule into a project; never write a project-specific rule
into the master. Contract: `.agents/rules/project-law.md`. See
[[repo-local-enforcement-never-centralizes]] for the files this does NOT apply to. (The old `Fresh_Workspace_BMAD` living-template was RETIRED 2026-08-07 — `/new-project` now clones
`sudomadhatter/sudo-project-skeleton`. Verified 2026-08-09: Fresh still sits under `Projects/` but no
longer carries an autopilot engine, so it is a leftover directory, not the template.)
