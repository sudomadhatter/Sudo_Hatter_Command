---
description: From the home base, fan out and reconcile the lobby + every conformant project against disk — repo-map (mode-preserving), every INDEX.md, the context-hygiene prune, and the open-tasks list (todo_list.md → ## Open Work). Reports for approval before editing; read-mostly, never commits. Inside a project it reconciles just that one workspace, unchanged.
---

# /1_update-maps — Update the Maps, INDEXes & open-tasks list

Execute the workflow defined in @.agents/workflows/1_update-maps.md.

**Execution notes:**
- **Scope is mode-driven.** Run from the **home base** (a `Projects/` dir exists) → it **fans out**: the lobby
  **and** every conformant `Projects/<name>` (one with an `AGENTS.md`). Run from **inside a project** → just that
  one workspace, exactly as before. Scope to a single workspace from the lobby with the focus arg below.
- **Lead with the linter** — it does the mechanical detection. From the home base use `--all`:
  `python .agents/scripts/check_maps.py --all` (lobby + every conformant project, one combined report); inside a
  project just `python .agents/scripts/check_maps.py`. It runs nine numbered checks per workspace (5 fatal + the git-baseline signal + the context-hygiene, tier-2-local-law, and gitnexus-index-freshness hints; plus an unnumbered level-2 INDEX presence check) — one command verifies maps, INDEXes, the folder AGENTS.md law files, AND the code index.
- Steps 0–3 are read-only (detect via git + the linter, regenerate each AUTO block **in its declared mode**,
  drift-check the curated tables both ways, audit every `INDEX.md`). Steps 3.5–3.6 **propose edits** — the
  context-hygiene **prune** and the **open-tasks refresh** — gated by Step 4.
- Step 4 is a hard STOP: present one findings report (grouped by workspace in a fan-out) and wait for approval
  before editing anything outside `_artifacts/` (per @.agents/rules/artifacts-always-first.md).
- **Each project is its own repo** → in a fan-out, edits land per repo and the close-out hands Daniel **one
  commit + one `--set-anchor` per touched repo** (never cross-commit). `--set-anchor --all` re-anchors them all.
- `.agents/*/INDEX.md` are the MASTER at the home base (editable) — fix them, then `/sync-agents` pushes copies
  to `.claude/`/`.opencode/`. (In a project they're vendored: fix at master, re-sync.)
- `_my_resources/` is off-limits **except one surgical write** — the `## Open Work` file-list in
  `todo_list.md` (Step 3.6 mirrors it to the `open_tasks/*.md` files). His `## Todo list` prose + the task files
  stay untouched. Never commit/push — hand Daniel the git command (git-policy).

Optional input: `$ARGUMENTS`. Use a project name or `.` to focus a single workspace; use `--dry-run` to run only the linter and produce the findings report, then **stop** before proposing any edits (the linter is read-only by default). Do **not** pass `--dry-run` to `check_maps.py` — it is not a supported flag.
