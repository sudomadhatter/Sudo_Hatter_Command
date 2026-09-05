---
name: toolkit-sync-covers-agents-not-docs
description: Toolkit-wide edits — master .agents/ auto-syncs to every project + command surface (edit master only); docs/ is NOT synced and must be edited per-project.
metadata: 
  probe: "test -e .agents/scripts/sync-agents.ps1"
  node_type: memory
  type: project
  originSessionId: bf3140de-d49f-4344-905c-7f15c7a243fd
---

**⚠️ SCOPE CHANGED 2026-08-07 (SCC-31): sync no longer touches projects at all.** It targets the lobby's
own `.claude/`+`.opencode/` plus the machine-global caches (opencode · Antigravity · Codex), and that is
the whole surface — every project reads the toolkit from the center instead
([[thin-projects-center-owns-workflow-law]]). The `bmad/` carve-out below is now moot (nothing vendors),
but its principle became the general rule → [[repo-local-enforcement-never-centralizes]]. Original note:

The `.agents/` toolkit has ONE source of truth: the lobby's `.agents/`. Edit there only. A periodic
background sync (and the manual `/sync-agents` → `.agents/scripts/sync-agents.ps1`) mirrors it to the
lobby's `.claude/`+`.opencode/` command surfaces and vendors it into every `Projects/<name>/.agents/`
+ their command surfaces — leaving files byte-identical across lobby + aviationChat + fresh-workspace.
Rules live ONLY in `.agents/rules/` (read directly; there is no `.claude/rules/`).

**Carve-out — `.agents/bmad/` is PROJECT-OWNED, NOT synced** (as of 2026-06-27). `sync-agents.ps1` now
`/XD`-excludes `bmad/` from the project vendor (via `Sync-Dir -ExcludeDirs`), because BMAD's `config.{toml,yaml}`
hold per-project identity (`project_name`) and BMAD self-installs per repo. So each workspace owns its own BMAD
name — lobby=`Sudo_Hatter_Command`, AGY=`AGY_AVIATIONCHAT`, Fresh=`Fresh_Workspace_BMAD`. Before this fix, the
vendor robocopied master's `bmad/` over every project, which is why all three wrongly read `aviationChat-AGY`.
Edit each project's `.agents/bmad/` directly — a sync will NOT propagate or clobber it.

**`docs/` is NOT synced.** `docs/workspace-standard.md`, aviationChat's `docs/file_structure_rules/*`,
and `docs/doc-graph.{md,json}` must be edited in EACH location by hand. `doc-graph.{md,json}` is
generated — rebuild with `python .agents/scripts/generate_doc_graph.py` after editing rules/commands.

**Why:** a toolkit-wide rule change touches ~20 files × 3 repos × 3 surfaces; knowing what auto-propagates
(`.agents/`) vs. what needs manual per-project edits (`docs/`) prevents both missed copies and wasted work.

**How to apply:** edit master `.agents/` → `sync-agents.ps1 -NoGlobals` for the lobby (avoids touching the
machine-global opencode/Antigravity caches) + `-Target <project>` per project (never touches globals) →
then hand-edit the `docs/` copies and regenerate `doc-graph`. See [[autopilot-engine-is-project-local]].
