# Implementation Plan — SCC-388 (and riders SCC-389, SCC-390, SCC-391)

Resync project and seed shells, thin-convert `sudo-command-center`, `BRKN_Tattoos`, and `B-L-WorldWide`, add an automated test gate in `test_rule_frontmatter.py` and `check_maps.py` preventing unrouted or drifted project rule sets, correct `AGENTS.md` §3 protocol-size figure, and verify the `teaching-edition` shell branch.

## User Review Required

> [!IMPORTANT]
> This is a consolidated Task lane on `chore/SCC-388-resync-shells-gate` carrying its three subtasks as riders:
> - **SCC-389**: Thin-convert `sudo-command-center` seed and route its own law
> - **SCC-390**: Thin-convert `BRKN_Tattoos` and `B-L-WorldWide` (both route zero law)
> - **SCC-391**: Automated test gate in `test_rule_frontmatter.py` and `check_maps.py`
> 
> Fresh clone template `sudo-project-skeleton` was previously verified clean (0 rule copies, 1 template row). `Fresh_Workspace_BMAD` was formally retired on 2026-09-04 and is excluded.

## Open Questions

None. The audit in `_artifacts/_main/2026-09-04_project-law-audit/walkthrough.md` and the three subtasks define the exact scope and acceptance requirements.

## Declared Change Set

- EDIT `AGENTS.md` — correct protocol-size "~44 KB" to measured "96.6 KB" (94.4 KB min) → D
- EDIT `.agents/scripts/tests/test_rule_frontmatter.py` — extend gate to scan all non-retired Projects and verify rule routing / tier-1 copy bans → C
- EDIT `.agents/scripts/check_maps.py` — catch unrouted project rules and tier-1 rule copies in structure conformance → C
- EDIT `Projects/sudo-command-center/.agents/INDEX.md` — thin project index routing surviving rules → A
- EDIT `Projects/sudo-command-center/.agents/rules/INDEX.md` — update project rules index → A
- NEW `Projects/sudo-command-center/.agents/rules/.gitkeep` — maintain empty rules dir → A
- EDIT `Projects/BRKN_Tattoos/.agents/INDEX.md` — thin project index routing surviving product rules → B
- EDIT `Projects/BRKN_Tattoos/.agents/rules/INDEX.md` — update product rules index → B
- EDIT `Projects/B-L-WorldWide/.agents/INDEX.md` — thin project index template routing surviving rules → B
- EDIT `Projects/B-L-WorldWide/.agents/rules/INDEX.md` — update rules index → B
- NEW `Projects/B-L-WorldWide/.agents/rules/.gitkeep` — maintain empty rules dir → B

## Proposed Changes

### 1. Part A (SCC-389): Thin-convert `sudo-command-center` seed

Strip the 24 stale tier-1 shared rule copies from `Projects/sudo-command-center/.agents/rules/`:
- `000-PLAN-FIRST-GATE.md`, `artifacts-always-first.md`, `code-standards.md`, `collaborative-debug-first.md`, `completion-not-illusion.md`, `constitution.md`, `dependency-awareness.md`, `git-policy.md`, `jira.md`, `karpathy-guidelines.md`, `living-template-sync.md`, `lobby-search.md`, `mermaid-diagram-preferences.md`, `mobile-mode.md`, `operator-profile.md`, `port-checklist.md`, `powershell-encoding-safety.md`, `project-law.md`, `reproduce-before-you-fix.md`, `smh-target-resolution.md`, `sop-currency.md`, `tests-must-gate-for-real.md`, `work-consolidation.md`, `worktree-per-story.md`.
- Also strip obsolete/retired rules: `prose-formatting.md` (retired SCC-333) and `training-mode.md`.
- Keep `.gitkeep` in `Projects/sudo-command-center/.agents/rules/`.
- Replace `Projects/sudo-command-center/.agents/INDEX.md` and `rules/INDEX.md` with thin project law routers.

### 2. Part B (SCC-390): Thin-convert `BRKN_Tattoos` and `B-L-WorldWide`

#### `BRKN_Tattoos`:
- Delete the 15 stale tier-1 rule copies from `Projects/BRKN_Tattoos/.agents/rules/`:
  `000-PLAN-FIRST-GATE.md`, `artifacts-always-first.md`, `code-standards.md`, `collaborative-debug-first.md`, `completion-not-illusion.md`, `constitution.md`, `dependency-awareness.md`, `git-policy.md`, `karpathy-guidelines.md`, `living-template-sync.md`, `lobby-search.md`, `mermaid-diagram-preferences.md`, `mobile-mode.md`, `powershell-encoding-safety.md`, `prose-formatting.md`, `tests-must-gate-for-real.md`.
- Delete obsolete workflow adapter `bmad_code_review_sudo_fix.md`.
- Retain surviving product rules: `adk_file_formating.md`, `bmad_code_review_fast_path.md`, `credential-resolution.md`, `frontend-architecture.md`, `prompt-tdd.md`, `pyrefly-paths.md`, `useEffect-dep-array-stability.md`, `voice-agent-architecture.md`.
- Write `Projects/BRKN_Tattoos/.agents/INDEX.md` and `rules/INDEX.md` with proper `Load` and `Trigger` rows routing each of the 8 surviving product rules.
- Clean up obsolete vendored tier-1 folders (`commands/`, `workflows/`, `templates/`, `bmad/`, `opencode-agents/`, `hooks/`, maintenance scripts) under `Projects/BRKN_Tattoos/.agents/` per `project-law.md`.

#### `B-L-WorldWide`:
- Delete the 15 stale tier-1 rule copies from `Projects/B-L-WorldWide/.agents/rules/`.
- Delete obsolete workflow adapter `bmad_code_review_sudo_fix.md`.
- Add `.gitkeep` in `Projects/B-L-WorldWide/.agents/rules/`.
- Write `Projects/B-L-WorldWide/.agents/INDEX.md` and `rules/INDEX.md` following the thin project model template (with `constitution.project.md` guidance).
- Clean up obsolete vendored tier-1 folders (`commands/`, `workflows/`, `templates/`, `opencode-agents/`, `hooks/`, maintenance scripts) under `Projects/B-L-WorldWide/.agents/` per `project-law.md`.

### 3. Part C (SCC-391): Automated Test Gate

#### Extend `test_rule_frontmatter.py`:
- Scan each maintained/active project directory in `ROOT / "Projects"` (excluding `Fresh_Workspace_BMAD` and stubs without `.agents`):
  1. **Unrouted rule check**: Assert every `*.md` rule file in `Projects/<name>/.agents/rules/` (excluding `INDEX.md`) has a matching `Load` row in `Projects/<name>/.agents/INDEX.md`.
  2. **Dangling row check**: Assert every rule row in `Projects/<name>/.agents/INDEX.md` (excluding template guidance like `constitution.project.md` marked "Create this first") points to a rule file that exists on disk.
  3. **Tier-1 copy ban**: Assert that no project rule filename matches any tier-1 lobby rule name in `ROOT/.agents/rules/`.
  4. **Non-empty rule set check**: Assert that if a project has rule files on disk, its `.agents/INDEX.md` does not have 0 rule rows.
  5. Support dotted filenames (e.g. `constitution.project.md`) in `LOAD_ROW` regex: `r"^\|\s*`([A-Za-z0-9_.\-]+)\.md`\s*\|\s*([^|]+?)\s*\|"`.

#### Extend `check_maps.py`:
- In `check_conformance()` for projects, detect tier-1 rule copies in `.agents/rules/` and flag present-but-empty `INDEX.md` when rule files exist on disk.

### 4. Part D: Protocol size correction in `AGENTS.md` §3
- Update `Together ~44 KB — which is why they are conditional rather than floor` to `Together ~96.6 KB (measured) — which is why they are conditional rather than floor`.

### 5. Part E: Verify `teaching-edition` shell status
- Confirm and document in walkthrough: `teaching-edition` is a git branch (`remotes/origin/claude/teaching-edition`) in `Sudo_Hatter_Command`, not a directory under `Projects/`.

## Verification Plan

### Automated Tests
- `python3 .agents/scripts/declared_change_set.py parse <plan>` → verify 0 incomplete entries.
- `python3 .agents/scripts/tests/test_rule_frontmatter.py --case "project rule sets are thin, routed, and free of tier-1 copies"` → verify RED on existing unrouted/copied rules, then GREEN after fixes.
- `python3 .agents/scripts/tests/test_rule_frontmatter.py` → full suite passes cleanly.
- `python3 .agents/scripts/tests/run_all.py` → full 71+ test suites pass cleanly.
- `python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/2026-09-04_scc-388-resync-shells-gate/sweep.json` → verify mutants killed.
- `python3 .agents/scripts/check_maps.py` → verify workspace passes cleanly.

## Self-Audit (2026-09-04)

### Lens 1: Repo Reality + Scope Ledger
- `lens`: 1 Repo Reality + Scope Ledger
- `checks_run`:
  - Verified all declared paths exist or are slated for creation.
  - Verified `declared_change_set.py parse` parsed all 11 entries with 0 incomplete.
  - Confirmed no deployable product paths (`backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/`, `.github/`) in Sudo_Hatter_Command are touched.
- `read`: `AGENTS.md`, `.agents/scripts/tests/test_rule_frontmatter.py`, `.agents/scripts/check_maps.py`, `Projects/*/.agents/INDEX.md`.
- `verdict`: clean

### Lens 2: Parity + Blast
- `lens`: 2 Parity + Blast
- `checks_run`:
  - Inspected sibling worktrees (`SCC-392-claude-approvals-harvest`, `SCC-393-approvals-fast-path`). Zero colliding file edits.
  - Evaluated cross-repo submodule blast radius: edits to `Projects/sudo-command-center`, `Projects/BRKN_Tattoos`, and `Projects/B-L-WorldWide` are strictly under their `.agents/` folders, completing thin-project conversion according to `project-law.md`.
- `read`: sibling worktree diffs, `git status`.
- `verdict`: clean

### Lens 3: Pre-Mortem
- `lens`: 3 Pre-Mortem
- `checks_run`:
  - Verified regex for `LOAD_ROW` supports dotted filenames (`constitution.project.md`).
  - Verified exclusion of retired `Fresh_Workspace_BMAD`.
  - Verified template row handling for unpopulated projects (`sudo-project-skeleton`).
- `read`: `_artifacts/_main/2026-09-04_project-law-audit/walkthrough.md`.
- `verdict`: clean

Audit verdict: GO
