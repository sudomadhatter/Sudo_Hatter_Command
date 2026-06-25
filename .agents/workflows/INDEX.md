# Workflows INDEX — when to use which

Router for `.agents/workflows/`. Workflows are **longer-form reference docs for multi-stage processes** —
the map of how something runs, as opposed to `commands/` (the invocable `/slash` skills) and `rules/`
(the always-on guardrails). Read the workflow to understand the process; trigger it via its command.

| Workflow | What it documents | Reach for it when… |
|---|---|---|
| `autopilot_bmad_dev_loop.md` | The model-agnostic reference for the 4-stage Dev/QA autopilot relay (Plan → Audit → Implement → Review+Fix), its engine/harness split, the Engine Adapter, and effort-tuning. | you're running, debugging, or extending `/autopilot` — or deciding how the loop runs under a given harness. |

**Adding a workflow:** drop `<name>.md` here (the authoring source), add a row above, wire a `commands/`
entry if it's invocable, and re-run `/sync-agents`.
