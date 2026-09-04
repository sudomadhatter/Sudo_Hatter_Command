# `.agents/` INDEX — master toolkit inventory

The single source of authorship for the whole system. **Read `AGENTS.md` first** (how to act here); this is
the "what's in here" map. Edit at master, then `/smh-sync-agents`.

| Subfolder | Holds | Dispatch via |
|---|---|---|
| `rules/` | behavioral law — constitution, karpathy-guidelines, git-policy, artifacts-always-first, mobile-mode, … | `rules/INDEX.md` |
| `commands/` | the canonical slash-command set — `/cicd-*`, `/smh-*`, `/sentry-*` | `commands/INDEX.md` |
| `skills/` | model-invoked capabilities, and the LAUNCHER door — **this is Codex's and Antigravity's `/` surface**, read natively by both, so every `SKILL.md` here is invocable as `/<name>` | `skills/INDEX.md` |
| `reference/` | long-form reference docs deliberately OFF every command surface (e.g. the autopilot relay reference — a Claude/opencode-only pipeline Gemini can't run) | `reference/INDEX.md` |
| `bmad/` | the BMAD method install — **owned, regenerated on update, never hand-edit** | — |
| `scripts/` | maintenance — `check_maps.py`, `generate_repo_map.py`, `record_map_changes.py`, `generate_doc_graph.py`, `check-repo-map-drift.ps1`, `sync-agents.ps1`, `new-project.ps1` | — |
| `templates/` | `project_overview_guide.md` — the skeleton a project copies to its `docs/`, kept current story-by-story (SCC-357). *(The `project-template/` scaffold this row used to name was retired 2026-08-07 with the thin-project conversion — `docs/workspace-standard.md` records that; the row outlived it.)* | — |
| `hooks/` | `require-push-approval.py` — the git write-approval gate (synced into every `.claude/hooks/`) | — |
| `opencode-agents/` | opencode agent definitions | — |

Adapters `CLAUDE.md` / `GEMINI.md` here both point to `AGENTS.md`. **No code-graph block by design here** —
this INDEX is the human/agent map. The scripts in `scripts/` *are* graph-indexed (they are the bulk of the
lobby graph); the routing between markdown files is the doc-graph's job, not the code-graph's.
