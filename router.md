# MASTER ROUTER — Sudo_Hatter_Command (the map)

You are in the LOBBY. This table is the directory: pick the workspace, then read **its** `AGENTS.md`.
Lobby = categories only; detail lives on each floor. If a request isn't listed here, **ASK — don't guess.**
Any workspace may send you BACK here ("if not here, go to root router").

> **Note:** all projects live under `Projects/`, each keeping its own git repo. "Converted" = the
> project has pointer `CLAUDE.md`/`GEMINI.md` + a workspace `AGENTS.md` (Layer-2 map) + **its own tier-2
> law only** (`.agents/rules/` + `.agents/skills/` + `.agents/INDEX.md`) — the center carries all workflow
> law (`.agents/rules/project-law.md`). Binding a converted project = reading its `.agents/INDEX.md`
> (§BIND). Legacy full-vendor projects are pending conversion.

## Artifact ownership

**Default:** every current or future directory under `Projects/` owns its artifacts in its own
`Projects/<name>/_artifacts/`, regardless of where the chat starts or which agent/tool runs it.

**Complete Sudo-managed exception registry:**

- `OpenChat-Openrouter` — Sudo-managed workspace; operational history stays in
  `_artifacts/OpenChat-Openrouter/`.

Anything not listed above follows the project-owned default. Adding an exception requires an explicit edit
to this registry.

| If the work is about… | Go to | Read first | Status |
|---|---|---|---|
| Aviation ground-school app (FastAPI / ADK / Gemini, voice CFI) | `Projects/AGY_AVIATIONCHAT/` | its `AGENTS.md` | converted (Phase 1) · standard-compliant · repo-map indexed · Phase 2 (rule reconcile) pending |
| AGY quick-start skeleton (canonical GitHub source) — the repo `/smh-new-project` clones | `Projects/sudo-project-skeleton/` | its `AGENTS.md` | skeleton source repo · freshly cloned |
| BRKN_Tattoos app | `Projects/BRKN_Tattoos/` | its `AGENTS.md` | active |
| B&L WorldWide | `Projects/B-L-WorldWide/` | its `AGENTS.md` | pending |
| NEXGen Films | `Projects/NEXGen-Films/` | its `AGENTS.md` | pending |
| NEXgen-VR-Director | `Projects/NEXgen-VR-Director/` | its `AGENTS.md` | pending |
| AviationChat ingestion pipeline — curriculum authoring + gated store ingest (upstream of the app) | `Projects/RAG_Pipeline_AC/` | its `AGENTS.md` · two-team curriculum ops → its `docs/SOP_curriculum_operations.md` | converted · standard-compliant · repo-map indexed · BMAD-lite board |
| openCode workspace | `Projects/OpenChat-Openrouter/` | its `AGENTS.md` | pending |
| Maintaining THIS home-base system | `docs/` | `docs/system-builder.md` | active |
| Setting up a NEW computer (secrets restore) · rename-day restructure | `docs/migrations/` | its `INDEX.md` → `install_guides/new_machine-migration-guide.md` | active · standing reference |
| **"What do we do next" / open tasks / what's left** | the **live Jira board** of the repo you work FROM (lobby → `SCC`; inside a project → its own key, e.g. `AVCH`) | root `AGENTS.md` §7 · `.agents/rules/jira.md` §The queue — `In Progress` → **`To Do Next`** → `To Do`, first non-empty rank wins | active · ⛔ **never `_my_resources/open_tasks/todo_list.md`** (retired as an agent source, ruling 2026-08-09 — personal notes, stale by design) |
| Reference: SOPs, PRDs, routing theory | **`docs/_scc_sops_prds/`** (every SOP + PRD) · `docs/workspace-standard.md` | its `INDEX.md` → `workflows_testing_SOP.md` | canonical |
