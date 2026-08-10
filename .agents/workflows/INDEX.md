# Workflows INDEX — when to use which

Router for `.agents/workflows/`. Workflows are **longer-form reference docs for multi-stage processes** —
the map of how something runs, as opposed to `commands/` (the invocable `/slash` skills) and `rules/`
(the always-on guardrails). Read the workflow to understand the process; trigger it via its command.

| Workflow | What it documents | Reach for it when… |
|---|---|---|
| `smh-update-maps-indexes.md` | Reconciling a workspace's `repo-map.md` + every `INDEX.md` + the context-hygiene **prune** + the **open-tasks list** (`todo_list.md` → `## Open Work`) against disk: a deterministic linter (`.agents/scripts/check_maps.py`, nine checks — 5 fatal + the git baseline + the context-hygiene / tier-2-law / gitnexus-freshness hints, plus an unnumbered level-2 INDEX presence check) detects drift, the workflow writes the prose a script can't (folder purpose lines, INDEX rows, the manifest). Read-mostly until an approval gate; never commits. **Fans out from the home base** (`--all` = lobby + every conformant project, each its own repo/commit); inside a project it's a single-workspace pass. | a folder/INDEX/open-task looks stale, after renames/moves, or the SessionStart drift nag fires — run `/smh-update-maps-indexes` (from the top to clean everything). |
| `smh-new-project.md` | Scaffolding a new workspace by cloning the thin `sudo-project-skeleton` repo — strip its history, git init, arm the hooks, fill the placeholders. NO toolkit is vendored (thin model, `project-law.md`). | you're standing up a new `Projects/<name>` and want it conformant from the first commit — run `/smh-new-project`. |
| `smh-slash-command-updating.md` | **A thin alias for `/smh-sync-agents -GlobalsOnly`** — refreshes the two machine-global command caches (`~/.gemini/antigravity/global_workflows`, `~/.config/opencode/commands`) from the canonical `.agents/commands/`. Mirror-exact: purges ghosts, preserves `bmad-*`, honors `platforms:`. Nothing more. | Antigravity or opencode is showing a stale menu while the lobby is fine. Prefer plain `/smh-sync-agents` — it does the locals too. |
| `sentry-security-team-avch.md` | The quarterly incident-response **DRILL** harness — a rehearsal of the runbook, deliberately NOT the live lane (that's `/cicd-mobile-error-team`) and deliberately absent from the Claude menu (`platforms: [opencode, antigravity, codex]`). | you're exercising the incident runbook on a schedule, not responding to a real page. |
| `cicd-self-audit.md` *(generated mirror of `commands/cicd-self-audit.md`)* | The pre-dev adversarial gate: pressure-tests an `implementation_plan.md` or story against the codebase + ACs **before any code is written** — a Phase 0 right-size gate (Skip/Light/Full) then phased checks for AC↔plan traceability, gaps, over-engineering, and contract breaks. Audits the plan, not a diff (shipped code → `bmad-code-review`). | you have an approved-shape plan/story and want to catch flaws while fixing is still free — run `/cicd-self-audit`. |

**Retired (2026-08-07):** `merge_main_debug.md` — died with the `main_debug` integration branch
(`git-policy.md`); the epic→`main` merge is `/cicd-push-e2e`.

**Generated mirrors:** any `cicd-*.md` / `smh-*.md` / `sentry-*.md` in this folder is **auto-copied
from `commands/` by `/smh-sync-agents`** so Antigravity (which surfaces `/` from `workflows/`, never
`commands/`) sees the dev flow. They are NOT authored here — edit the COMMAND in `.agents/commands/`,
then re-sync. Do not hand-edit or add rows for them.

⛔ **Two files here are AUTHORING SOURCES, not mirrors**, and survive only because they are named in
the `$excluded` list in `.agents/scripts/sync-agents.ps1`: `smh-update-maps-indexes.md` (the real ~40 KB
workflow — `commands/` holds a 4 KB wrapper) and `smh-adviser-board.md` (hand-authored thin launcher).
`INDEX.md` (this file) is excluded for the same reason. **That list matches by FILENAME** — renaming any
of these three without editing `$excluded` in the same commit makes the next sync classify it as a stale
mirror and DELETE it. SCC-63 hit exactly that.

**Adding a (real) workflow:** drop `<name>.md` here (the authoring source), add a row above, wire a
`commands/` entry if it's invocable, and re-run `/smh-sync-agents`.

> **Not everything explanatory belongs here.** Antigravity surfaces every file in this folder as an
> invocable `/`, so a doc that is *pure reference* — no `/` of its own, or one that only runs on a
> specific LLM — belongs in [`docs/_scc_sops_prds/`](../../docs/_scc_sops_prds/INDEX.md) instead.
> That is where `autopilot_bmad_dev_loop.md` lives: it documents a Claude/opencode-only pipeline that
> Gemini can't run, so listing it as a Gemini workflow was an invitation to run the wrong thing.
>
> It moved there in SCC-74 (2026-08-10), which retired the `.agents/reference/` folder that had held
> it since 2026-07-20. The constraint that folder existed for is unchanged and now better served:
> a doc under `docs/` is off every command surface **by construction**, so it cannot be swept into a
> mirror by a future sync — and `platforms: []` never solved that, because the sync vendors whole
> directories without platform filtering.
