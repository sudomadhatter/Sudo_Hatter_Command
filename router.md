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

- `Fresh_Workspace_BMAD` — living duplication template; operational history stays in
  `_artifacts/Fresh_Workspace_BMAD/`. The exception does not transfer to clones.
- `OpenChat-Openrouter` — Sudo-managed workspace; operational history stays in
  `_artifacts/OpenChat-Openrouter/`.

Anything not listed above follows the project-owned default. Adding an exception requires an explicit edit
to this registry.

| If the work is about… | Go to | Read first | Status |
|---|---|---|---|
| Aviation ground-school app (FastAPI / ADK / Gemini, voice CFI) | `Projects/AGY_AVIATIONCHAT/` | its `AGENTS.md` | converted (Phase 1) · standard-compliant · repo-map indexed · Phase 2 (rule reconcile) pending |
| AGY quick-start project skeleton (FastAPI/ADK · Next/React · Firebase) — clone to start a new project | `Projects/Fresh_Workspace_BMAD/` | its `AGENTS.md` | quick-start skeleton · standard-compliant · repo-map indexed + drift hook |
| AGY quick-start skeleton (canonical GitHub source) — the repo `/smh-new-project` clones | `Projects/sudo-project-skeleton/` | its `AGENTS.md` | skeleton source repo · freshly cloned |
| BRKN_Tattoos app | `Projects/BRKN_Tattoos/` | its `AGENTS.md` | active |
| B&L WorldWide | `Projects/B-L-WorldWide/` | its `AGENTS.md` | pending |
| NEXGen Films | `Projects/NEXGen-Films/` | its `AGENTS.md` | pending |
| NEXgen-VR-Director | `Projects/NEXgen-VR-Director/` | its `AGENTS.md` | pending |
| AviationChat ingestion pipeline — curriculum authoring + gated store ingest (upstream of the app) | `Projects/RAG_Pipeline_AC/` | its `AGENTS.md` · two-team curriculum ops → its `docs/SOP_curriculum_operations.md` | converted · standard-compliant · repo-map indexed · BMAD-lite board |
| openCode workspace | `Projects/OpenChat-Openrouter/` | its `AGENTS.md` | pending |
| Maintaining THIS home-base system | `docs/` | `docs/system-builder.md` | active |
| Setting up a NEW computer (secrets restore) · rename-day restructure | `_my_resources/migrations/` | its `INDEX.md` → `env-migration-guide.md` | active · disposable (deleted after a machine is set up) |
| **"What do we do next" / open tasks / what's left / Daniel's plans & PRPs** | `_my_resources/open_tasks/` **for where you work FROM** (lobby → home-base `_my_resources/open_tasks/`; inside a converted project → that project's `_my_resources/open_tasks/`) | `todo_list.md` (+ any plan/PRP files there) | active · **READ-ONLY** (Daniel's notes — never edit; cross-check vs live project files) |
| Reference: routing theory + transcripts | `docs/`, `_my_resources/youtube_transcripts/` | `_my_resources/docs/master-implementation-plan.md` | reference |
