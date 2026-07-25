# Workflows INDEX — when to use which

Router for `.agents/workflows/`. Workflows are **longer-form reference docs for multi-stage processes** —
the map of how something runs, as opposed to `commands/` (the invocable `/slash` skills) and `rules/`
(the always-on guardrails). Read the workflow to understand the process; trigger it via its command.

| Workflow | What it documents | Reach for it when… |
|---|---|---|
| `update-maps-indexes.md` | Reconciling a workspace's `repo-map.md` + every `INDEX.md` + the context-hygiene **prune** + the **open-tasks list** (`todo_list.md` → `## Open Work`) against disk: a deterministic linter (`.agents/scripts/check_maps.py`, 6 checks) detects drift, the workflow writes the prose a script can't (folder purpose lines, INDEX rows, the manifest). Read-mostly until an approval gate; never commits. **Fans out from the home base** (`--all` = lobby + every conformant project, each its own repo/commit); inside a project it's a single-workspace pass. | a folder/INDEX/open-task looks stale, after renames/moves, or the SessionStart drift nag fires — run `/update-maps-indexes` (from the top to clean everything). |
| `update-personal-sprint-map.md` | Refreshing the operator's personal ticket board (`sprint-dependency-map.md`) in the current project workspace: lists open stories with their next required `/slash` command, stories needing live testing/verification, blockers with reasons, closed stories in active epics, and automatically prunes closed stories when an epic is completed. | checking active work, tracking next steps per story, or refreshing the personal ticket board — run `/update-personal-sprint-map`. |
| `sudo-self-audit.md` *(generated mirror of `commands/sudo-self-audit.md`)* | The pre-dev adversarial gate: pressure-tests an `implementation_plan.md` or story against the codebase + ACs **before any code is written** — a Phase 0 right-size gate (Skip/Light/Full) then phased checks for AC↔plan traceability, gaps, over-engineering, and contract breaks. Audits the plan, not a diff (shipped code → `bmad-code-review`). | you have an approved-shape plan/story and want to catch flaws while fixing is still free — run `/sudo-self-audit`. |

**Generated mirrors:** any `sudo-*.md` in this folder is **auto-copied from `commands/sudo-*` by
`/sync-agents`** so Antigravity (which surfaces `/` from `workflows/`, never `commands/`) sees the dev
flow. They are NOT authored here — edit the COMMAND in `.agents/commands/`, then re-sync. Do not hand-edit
or add rows for them.

**Adding a (real) workflow:** drop `<name>.md` here (the authoring source), add a row above, wire a
`commands/` entry if it's invocable, and re-run `/sync-agents`.

> **Not everything explanatory belongs here.** Antigravity surfaces every file in this folder as an
> invocable `/`, so a doc that is *pure reference* — no `/` of its own, or one that only runs on a
> specific LLM — belongs in [`.agents/reference/`](../reference/INDEX.md) instead. That's where
> `autopilot_bmad_dev_loop.md` moved (2026-07-20): it documents a Claude/opencode-only pipeline that
> Gemini can't run, so listing it as a Gemini workflow was an invitation to run the wrong thing.
