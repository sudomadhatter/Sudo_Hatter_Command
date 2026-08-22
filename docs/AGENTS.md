# `docs/` — LOCAL LAW (home-base documentation)

Workspace docs for the home base. Load per task — nothing here is a startup payload except
`repo-map.md`, which the SessionStart hook injects.

## The law
- `workspace-standard.md` — **THE structure contract** (PATH CONTRACT, tier model, upkeep loop).
  Canonical copy lives HERE; each project carries a vendored copy. **`docs/` is NOT covered by
  `/smh-sync-agents`** — edit the canon here, re-vendor to projects deliberately (per-project pass).
- **`_scc_sops_prds/`** — **every SOP and PRD in the system** (SCC-74, 2026-08-10): the pages that
  tell the *operator* what to do and what to type. Start at its `INDEX.md`. `workflows_testing_SOP.md`
  is THE quick reference and is protected by an armed commit-msg gate — change how the system is USED
  and it moves in the same commit (`.agents/rules/sop-currency.md`). The folder is pinned by
  `.agents/scripts/tests/test_sops_prds_folder.py` in `run_all`: manifest, INDEX-vs-disk both ways,
  live links, and every `/command` reference resolving to a real master. **Adding or removing a doc
  here means three edits in one commit — the file, a row in that INDEX, and a name in that test's
  `EXPECTED` set** — the manifest is a contract, and the suite stays red until all three land.
  ⛔ Procedural docs do NOT go in `_my_resources/`; that folder is excluded from every drift-checker,
  which is exactly why the thirteen SCC-74 found there had rotted.
  **Machine-setup guides are not SOPs** and live one level up, here in `docs/` — read once per
  machine, not during work. That is a scope line, not an exemption: they are still inside `docs/`,
  so `check_maps.py` still covers them.
- `md_feedback_setup_guide.md` — installing the **MD Feedback** MCP server (annotations read straight
  from markdown) for Claude, opencode and Antigravity on a new machine. Moved up out of
  `_scc_sops_prds/` on 2026-08-10 under the setup-vs-SOP line above.
- `repo-map.md` — hybrid navigation index. **CURATED header: hand-edited. AUTO body (between the
  sentinels): machine-owned** — regenerate via `.agents/scripts/generate_repo_map.py` (mode-preserving;
  match the header's documented `--ignore`/`--mode`), never hand-edit inside the sentinels.
- `system-builder.md` — how to grow/maintain the home base itself (`/smh-new-project`, `/smh-sync-agents`,
  workspace-conversion rules). Was `_system/AGENTS.md` until 2026-07-25; `_system/` no longer exists.
- `code-review-graph.md` — code-graph guidance (static; pointer target from the root `AGENTS.md`).
- `.maps-state.json` — machine-managed drift anchor (`check_maps.py --set-anchor`, run AFTER
  committing). Never hand-edit.
- `doc-graph.md` / `doc-graph.json` — generated doc-wiring graph (regen via
  `.agents/scripts/generate_doc_graph.py`). Report-only; never hand-edit.
- Added/removed a file here → the repo-map AUTO body will drift; run `/smh-update-maps-indexes` (or the
  generator) before hand-off.
