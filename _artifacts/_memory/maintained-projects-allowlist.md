---
name: maintained-projects-allowlist
description: Maintained set = lobby + AGY_AVIATIONCHAT + NEXgen-VR-Director — but NEVER trust an enumeration: the ONE list is .agents/maintained-projects.txt (read it each time). NEXgen is a bare gitlink in the lobby (no .gitmodules entry, no ignore=all) — committing inside it dirties the lobby until you bump the pointer.
metadata: 
  node_type: memory
  type: project
  originSessionId: 695db3e1-db11-4d97-ae14-3b25a2966da9
  modified: 2026-08-01T00:01:57.212Z
---

The maintained set (verified 2026-07-31): the lobby (command center) + **AGY_AVIATIONCHAT** + **Fresh_Workspace_BMAD** + **NEXgen-VR-Director** (added since 07-14 — enumerations go stale, the file is the truth). The other child repos under `Projects/` (AGY_JETCHAT, B-L-WorldWide, BRKN_Tattoos, NEXGen-Films, OpenChat-Openrouter, RAG_Pipeline_AC) are **NOT** kept current and must not be touched by toolkit/map upkeep. (Set 2026-07-14 after a manual `Get-ChildItem Projects/* | sync` loop wrongly updated all 8.)

**NEXgen-VR-Director gitlink quirk (2026-07-31):** it is tracked in the lobby as a bare gitlink with NO `.gitmodules` entry — unlike AGY/Fresh (`ignore = all`), so any commit inside NEXgen leaves ` M Projects/NEXgen-VR-Director` in the lobby until you commit a pointer bump (`chore: bump NEXgen-VR-Director submodule — <what>`, the established pattern). Toolkit changes committed inside NEXgen therefore always end with that lobby bump, or the lobby tree stays dirty.

**The single source of truth:** `.agents/maintained-projects.txt` — one project folder name per line (blanks/#comments ignored); the lobby is always maintained and is not listed. To add a project to upkeep, add its name to this ONE file.

**⚠️ SUPERSEDED 2026-08-07 (SCC-31): this is now the LINT worklist ONLY.** `sync-agents.ps1` no longer
reads it — `-Maintained` and project targets both exit with an error, because projects carry no vendored
toolkit to sync ([[thin-projects-center-owns-workflow-law]]). `Fresh_Workspace_BMAD` was de-listed
(SCC-25, frozen). Current list: AGY_AVIATIONCHAT + NEXgen-VR-Director.

**Historically, both fan-out mechanisms honored it (2026-07-14, commit d6c1bbc):**
- `check_maps.py` `fan_out_targets()` → `--all` / `/1_update-maps` lint the lobby + listed projects only; conformant-but-unlisted repos print `[skip] ... not in .agents/maintained-projects.txt`. Missing file = legacy fallback (all conformant).
- `sync-agents.ps1 -Maintained` → the ONLY sanctioned "sync everything": lobby + listed projects. **Never hand-loop over `Projects/*`** — that hits repos we deliberately don't sync (the original mistake).

**Why "conformant" wasn't enough:** the old marker was just "has an `AGENTS.md`", which 4 projects satisfy (AGY, BRKN, Fresh, RAG) — two more than Daniel wants maintained. The allowlist is the intentional narrowing. (Fresh was the golden skeleton and was itself RETIRED 2026-08-07 — new projects are cut from the lobby master now, so it is off the list too.) Related: [[toolkit-sync-covers-agents-not-docs]].
