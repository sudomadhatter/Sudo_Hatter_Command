# `docs/` — LOCAL LAW (home-base documentation)

Workspace docs for the home base. Load per task — nothing here is a startup payload except
`repo-map.md`, which the SessionStart hook injects.

## The law
- `workspace-standard.md` — **THE structure contract** (PATH CONTRACT, tier model, upkeep loop).
  Canonical copy lives HERE; each project carries a vendored copy. **`docs/` is NOT covered by
  `/smh-sync-agents`** — edit the canon here, re-vendor to projects deliberately (per-project pass).
- `repo-map.md` — hybrid navigation index. **CURATED header: hand-edited. AUTO body (between the
  sentinels): machine-owned** — regenerate via `.agents/scripts/generate_repo_map.py` (mode-preserving;
  match the header's documented `--ignore`/`--mode`), never hand-edit inside the sentinels.
- `system-builder.md` — how to grow/maintain the home base itself (`/smh-new-project`, `/smh-sync-agents`,
  workspace-conversion rules). Was `_system/AGENTS.md` until 2026-07-25; `_system/` no longer exists.
- `gitnexus.md` — Tier-2 code-graph guidance (static; pointer target from the root `AGENTS.md`).
- `.maps-state.json` — machine-managed drift anchor (`check_maps.py --set-anchor`, run AFTER
  committing). Never hand-edit.
- `doc-graph.md` / `doc-graph.json` — generated doc-wiring graph (regen via
  `.agents/scripts/generate_doc_graph.py`). Report-only; never hand-edit.
- Added/removed a file here → the repo-map AUTO body will drift; run `/smh-update-maps-indexes` (or the
  generator) before hand-off.
