---
IsArtifact: true
ArtifactMetadata:
  title: Task List — Workspace Standard + Repo-Map Hybrid + Artifacts Parity
  type: task_list
  date: 2026-06-24
---

# Task List (final snapshot)

- [x] **Part F** — rename `_experiment/` → `_routing-canary/` (git mv, history preserved) + update all live
  references (root `AGENTS.md`, `master-implementation-plan.md`, the canary's own files + README triggers).
- [x] **Part E** — reconcile rules at the `.agents/` source: `git-closeout-commits.md` → `git-policy.md`
  (canonical policy), reconcile `constitution.md` + `artifacts-always-first.md`, purge `_claude_artifacts/`
  from `prose-formatting.md`. Retire-list for engine-coupled/project copies defined (not executed).
- [x] **Part D** — artifacts org scheme into `artifacts-always-first.md` §2: workspace-bucket rule +
  random-task (`<date>_<slug>`) vs story (`<epic>/<story>`) folders.
- [x] **Part A** — write `_docs/workspace-standard.md` (Format + Upkeep, repo-map two modes, retire-list appendix).
- [x] **Part C** — home-base parity: `AGENTS.md` mandatory artifacts gate + always-load + standard ref + git
  policy alignment; new `.claude/settings.json` SessionStart hook (verified, UTF-8).
- [x] **Part B (home-base portion)** — author `.agents/scripts/generate_repo_map.py`; smoke-tested vs home base
  (scaffold ok) and vs ingestion read-only (**514 → 192 lines**, data dirs collapsed).
- [ ] **BLOCKED — lab-prove + propagate** — generate clean-bmad's `docs/repo-map.md`, wire its hook, seed the
  template, `/sync-agents`. Deferred: `Projects/clean-bmad-workspace` is in use by another team; awaiting
  Daniel's clearance + review of their work.
- [ ] **Deferred (follow-up reconcile)** — autopilot workflow + `1_*` commands still reference
  `_claude_artifacts/`; engine-coupled, needs the `.ps1` checked before moving paths.
- [x] **Close out** — `walkthrough.md`, this `task-list.md`, `active-context.md`, `INDEX.md`.
