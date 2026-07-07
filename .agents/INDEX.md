# `.agents/` INDEX — master toolkit inventory

The single source of authorship for the whole system. **Read `AGENTS.md` first** (how to act here); this is
the "what's in here" map. Edit at master, then `/sync-agents`.

| Subfolder | Holds | Dispatch via |
|---|---|---|
| `rules/` | behavioral law — constitution, karpathy-guidelines, git-policy, artifacts-always-first, mobile-mode, … | `rules/INDEX.md` |
| `commands/` | the canonical slash-command set — `/sudo-*`, `/autopilot_*`, `/sync-agents`, `/new-project`, `/merge_main_debug`, … | `commands/INDEX.md` |
| `skills/` | model-invoked capabilities | `skills/INDEX.md` |
| `workflows/` | the Antigravity workflow mirror + in-repo reference docs | `workflows/INDEX.md` |
| `bmad/` | the BMAD method install — **owned, regenerated on update, never hand-edit** | — |
| `scripts/` | maintenance — `check_maps.py`, `generate_repo_map.py`, `record_map_changes.py`, `generate_doc_graph.py`, `check-repo-map-drift.ps1`, `sync-agents.ps1`, `new-project.ps1` | — |
| `templates/` | `project-template/` — the scaffold `/new-project` clones | — |
| `hooks/` | `require-push-approval.py` — the git write-approval gate (synced into every `.claude/hooks/`) | — |
| `opencode-agents/` | opencode agent definitions | — |

Adapters `CLAUDE.md` / `GEMINI.md` here both point to `AGENTS.md`. **No GitNexus block by design** — the
toolkit is markdown, navigated by these indexes (and the doc-graph), not the code-graph.
