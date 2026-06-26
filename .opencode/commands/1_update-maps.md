---
description: Reconcile the home-base repo map and every INDEX.md against what's actually on disk. Regenerates _docs/repo-map.md (mode-preserving), drift-checks the curated tables, audits each INDEX, then reports for approval before editing. Read-mostly; never commits.
---

# /1_update-maps — Update the Maps & INDEX.md files (home base)

Execute the workflow defined in @.agents/workflows/1_update-maps.md.

**Execution notes:**
- Steps 0–3 are read-only: use git (`git status --short`, `git diff --name-status`) to detect what moved,
  regenerate the repo-map AUTO block **in its declared mode** (this repo = `--mode content`), drift-check the
  curated tables both directions, and reconcile every home-base `INDEX.md` against its real folder.
- Run the deterministic linter first — it does the mechanical detection:
  `python .agents/scripts/check_maps.py` (no vendored `scripts/` copy here; the home base runs the master).
- Step 4 is a hard STOP: present the findings report and wait for approval before editing anything outside
  `_artifacts/` (per @.agents/rules/artifacts-always-first.md).
- **`Projects/` are SEPARATE repos** — each has its own `docs/repo-map.md` + its own `/1_update-maps`. This
  workflow never descends into them; it reconciles the LOBBY only.
- `.agents/*/INDEX.md` are the MASTER here (editable) — fix them, then `/sync-agents` pushes the copies to
  `.claude/`/`.opencode/`.
- `_my_resources/` is off-limits EXCEPT `open_tasks/` (read-only). Never commit/push — hand Daniel the git
  command (git-policy).

Optional input: $ARGUMENTS  (focus folder, or `--dry-run` to stop after the report).
