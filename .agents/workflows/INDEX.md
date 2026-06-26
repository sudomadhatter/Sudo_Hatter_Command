# Workflows INDEX — when to use which

Router for `.agents/workflows/`. Workflows are **longer-form reference docs for multi-stage processes** —
the map of how something runs, as opposed to `commands/` (the invocable `/slash` skills) and `rules/`
(the always-on guardrails). Read the workflow to understand the process; trigger it via its command.

| Workflow | What it documents | Reach for it when… |
|---|---|---|
| `autopilot_bmad_dev_loop.md` | The model-agnostic reference for the 4-stage Dev/QA autopilot relay (Plan → Audit → Implement → Review+Fix), its engine/harness split, the Engine Adapter, and effort-tuning. | you're running, debugging, or extending `/autopilot` — or deciding how the loop runs under a given harness. |
| `1_update-maps.md` | Reconciling the LOBBY's `_docs/repo-map.md` + every home-base `INDEX.md` against disk: a deterministic linter (`.agents/scripts/check_maps.py`, 4 checks) detects drift, the workflow writes the prose a script can't (folder purpose lines, INDEX rows). Read-mostly; never commits. Lobby-only — projects run their own. | a folder/INDEX looks stale, after renames/moves, or the SessionStart drift nag fires — run `/1_update-maps`. |

**Adding a workflow:** drop `<name>.md` here (the authoring source), add a row above, wire a `commands/`
entry if it's invocable, and re-run `/sync-agents`.
