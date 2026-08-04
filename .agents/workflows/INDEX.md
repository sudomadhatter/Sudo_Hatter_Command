# Workflows INDEX — when to use which

Router for `.agents/workflows/`. Workflows are **longer-form reference docs for multi-stage processes** —
the map of how something runs, as opposed to `commands/` (the invocable `/slash` skills) and `rules/`
(the always-on guardrails). Read the workflow to understand the process; trigger it via its command.

| Workflow | What it documents | Reach for it when… |
|---|---|---|
| `update-maps-indexes.md` | Reconciling a workspace's `repo-map.md` + every `INDEX.md` + the context-hygiene **prune** + the **open-tasks list** (`todo_list.md` → `## Open Work`) against disk: a deterministic linter (`.agents/scripts/check_maps.py`, nine checks — 5 fatal + the git baseline + the context-hygiene / tier-2-law / gitnexus-freshness hints, plus an unnumbered level-2 INDEX presence check) detects drift, the workflow writes the prose a script can't (folder purpose lines, INDEX rows, the manifest). Read-mostly until an approval gate; never commits. **Fans out from the home base** (`--all` = lobby + every conformant project, each its own repo/commit); inside a project it's a single-workspace pass. | a folder/INDEX/open-task looks stale, after renames/moves, or the SessionStart drift nag fires — run `/update-maps-indexes` (from the top to clean everything). |
| `new-project.md` | Scaffolding a new workspace from the `Fresh_Workspace_BMAD` living template — clone, rename the placeholders, vendor the master toolkit, register it for upkeep. | you're standing up a new `Projects/<name>` and want it conformant from the first commit — run `/new-project`. |
| `slash_command_updating.md` | Authoring and revising the command surface itself: frontmatter contract (`description:` = when it fires, `platforms:` = reach), where the master lives, and the `/sync-agents` propagation step every change needs. | you're adding, renaming, or retiring a `/command` and need the surrounding contract — run `/slash_command_updating`. |
| `merge_main_debug.md` | Merging a reviewed PR into `main_debug` — the per-action approval button in the branch model (`git-policy.md`). Not a story close-out. | a reviewed branch is ready to land on the integration branch — run `/merge_main_debug`. |
| `security_team_aviationchat.md` | The quarterly incident-response **DRILL** harness — a rehearsal of the runbook, deliberately NOT the live lane (that's `/sudo-mobile-error-team`) and deliberately absent from the Claude menu (`platforms: [opencode, antigravity, codex]`). | you're exercising the incident runbook on a schedule, not responding to a real page. |
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
