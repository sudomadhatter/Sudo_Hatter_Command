# Workflows INDEX — when to use which

Router for `.agents/workflows/`. Workflows are **longer-form reference docs for multi-stage processes** —
the map of how something runs, as opposed to `commands/` (the invocable `/slash` skills) and `rules/`
(the always-on guardrails). Read the workflow to understand the process; trigger it via its command.

| Workflow | What it documents | Reach for it when… |
|---|---|---|
| `autopilot_bmad_dev_loop.md` | The model-agnostic reference for the 4-stage Dev/QA autopilot relay (Plan → Audit → Implement → Review+Fix), its engine/harness split, the Engine Adapter, and effort-tuning. | you're running, debugging, or extending `/autopilot` — or deciding how the loop runs under a given harness. |
| `1_update-maps.md` | Reconciling a workspace's `repo-map.md` + every `INDEX.md` + the context-hygiene **prune** + the **open-tasks list** (`todo_list.md` → `## Open Work`) against disk: a deterministic linter (`.agents/scripts/check_maps.py`, 6 checks) detects drift, the workflow writes the prose a script can't (folder purpose lines, INDEX rows, the manifest). Read-mostly until an approval gate; never commits. **Fans out from the home base** (`--all` = lobby + every conformant project, each its own repo/commit); inside a project it's a single-workspace pass. | a folder/INDEX/open-task looks stale, after renames/moves, or the SessionStart drift nag fires — run `/1_update-maps` (from the top to clean everything). |
| `sudo-self-audit.md` *(generated mirror of `commands/sudo-self-audit.md`)* | The pre-dev adversarial gate: pressure-tests an `implementation_plan.md` or story against the codebase + ACs **before any code is written** — a Phase 0 right-size gate (Skip/Light/Full) then phased checks for AC↔plan traceability, gaps, over-engineering, and contract breaks. Audits the plan, not a diff (shipped code → `bmad-code-review`). | you have an approved-shape plan/story and want to catch flaws while fixing is still free — run `/sudo-self-audit`. |

**Generated mirrors:** any `sudo-*.md` in this folder is **auto-copied from `commands/sudo-*` by
`/sync-agents`** so Antigravity (which surfaces `/` from `workflows/`, never `commands/`) sees the dev
flow. They are NOT authored here — edit the COMMAND in `.agents/commands/`, then re-sync. Do not hand-edit
or add rows for them.

**Adding a (real) workflow:** drop `<name>.md` here (the authoring source), add a row above, wire a
`commands/` entry if it's invocable, and re-run `/sync-agents`.
