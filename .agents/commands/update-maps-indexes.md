---
description: From the home base, fan out and reconcile the lobby + every conformant project against disk — repo-map (mode-preserving), every INDEX.md, every AGENTS.md + README's references (dead paths, renamed commands, stale contents-lists), the context-hygiene prune, and the open-tasks list (todo_list.md → ## Open Work). Reports for approval before editing; read-mostly, never commits. Inside a project it reconciles just that one workspace, unchanged.
---

# /update-maps-indexes — Update the Maps, INDEXes, AGENTS + READMEs

Execute the workflow defined in @.agents/workflows/update-maps-indexes.md.

**Execution notes:**
- **Scope is mode-driven.** Run from the **home base** (a `Projects/` dir exists) → it **fans out**: the lobby
  **and** every **maintained** `Projects/<name>` — i.e. a workspace (has `AGENTS.md`) that is ALSO listed in
  `.agents/maintained-projects.txt` (the single allowlist, shared with `sync-agents.ps1 -Maintained`).
  Conformant-but-unlisted projects are skipped with a one-line reason. To add a project to upkeep, add its
  folder name to that file. Run from **inside a project** → just that one workspace. Scope to a single
  workspace from the lobby with the focus arg below.
- **Lead with the linter** — it does the mechanical detection. From the home base use `--all`:
  `python .agents/scripts/check_maps.py --all` (lobby + every conformant project, one combined report); inside a
  project just `python .agents/scripts/check_maps.py`. It runs nine numbered checks per workspace (5 fatal + the git-baseline signal + the context-hygiene, tier-2-local-law, and gitnexus-index-freshness hints; plus an unnumbered level-2 INDEX presence check) — one command verifies maps, INDEXes, the folder AGENTS.md law files, AND the code index.
- Steps 0–3 are read-only (detect via git + the linter, regenerate each AUTO block **in its declared mode**,
  drift-check the curated tables both ways, audit every `INDEX.md`). Steps 3.5–3.8 **propose edits** — the
  context-hygiene **prune**, the **open-tasks refresh**, the tier-2 law repairs, and the **AGENTS.md/README
  pointer reconcile** (Step 3.8: every path, `/command` name, and contents-list those files claim must match
  disk; repair pointers, never meaning) — all gated by Step 4.
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
