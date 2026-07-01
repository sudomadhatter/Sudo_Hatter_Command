---
title: clean-bmad-workspace — Workspace-Standard Cleanup + Repo-Map Index — Walkthrough
type: walkthrough
workspace: clean-bmad-workspace
date: 2026-06-25
status: COMPLETE — awaiting Daniel's commit/push (2 repos)
plan: ./implementation_plan.md
---

# Walkthrough — clean-bmad workspace-standard cleanup

## What this was
Conform `clean-bmad-workspace` (Daniel's clean-shell clone-template) to `_docs/workspace-standard.md`,
clean up the stale store, build the navigation index, and lock down his personal area — as the safe
rehearsal before the same recipe is applied to the live **aviationChat** project.

## What changed — in the clean-bmad repo (`Projects/clean-bmad-workspace/`)
| WS | Change | Files |
|---|---|---|
| WS5 | `_01_My/` → `_my_resources/` (parent rename only; subfolders verbatim; `git mv` preserved history) | 3 renamed |
| WS5 | New protective README — personal area, may be stale, agents don't edit/reference unless Daniel says/links | `_my_resources/README.md` |
| WS2 | Vendored the standard + the index generator | `docs/workspace-standard.md`, `scripts/generate_repo_map.py` |
| WS1 | AGENTS.md rewritten to the 9-section standard; MAP de-references the dead store; `_my_resources/` guardrail added to §8 GATES; `artifacts-always-first` added to ALWAYS-LOAD | `AGENTS.md` |
| WS3 | Built the navigation index — hand-authored curated header (to-find-X + knowledge map, `_my_resources/` flagged) + generated auto body (`--ignore _bmad`, 95 lines) | `docs/repo-map.md` |
| WS4 | Marked the dead store deprecated (not deleted — vendored cmds + autopilot engine still write there until the master pass) | `_claude_artifacts/README.md` |

## What changed — in the home-base repo (`Sudo_Hatter_Command/`)
- **Corrected the "another team / off-limits" mischaracterization** in 6 live docs (it's Daniel's clean-shell
  template): `_my_resources/diagrams_guides/system/{gitnexus-usage-guide,complete-system-overview,updated_folder_file_structure_diagram}.md`,
  `_docs/workspace-standard.md` (appendix), `_artifacts/_home/active-context.md` (live 5.4/5.5).
- `router.md` status: `first conversion (next)` → `converted · standard-compliant (repo-map indexed)`.
- This session's artifacts: `implementation_plan.md`, this `walkthrough.md`, `task-list.md`; `active-context.md`
  + `INDEX.md` updated.
- (Left as dated history: the 2026-06-24 INDEX row, the gitnexus-spike plan, and the workspace-standard
  session walkthrough/task-list. Offered to scrub if Daniel wants a clean sweep.)

## Verification (real output)
- **git status (clean-bmad):** `M AGENTS.md`, `M _claude_artifacts/README.md`, 3× `R _01_My/… -> _my_resources/…`,
  `?? _my_resources/README.md`, `?? docs/repo-map.md`, `?? docs/workspace-standard.md`, `?? scripts/generate_repo_map.py`.
- **Format checklist (workspace-standard Part 1): all 7 ✓** — CLAUDE/GEMINI adapters · numbered AGENTS.md +
  routing table + up-route · `.agents/` vendored + opencode.json points at it · `docs/repo-map.md` present ·
  home-base `active-context.md` exists · registered in `router.md` · vendored `docs/workspace-standard.md`.
- **`_01_My` residual:** only inside `_my_resources/Visual_Diagrams/total_workspace_guide_overview.md:77`
  (Daniel's own personal doc — **left untouched by design**; it's protected & may be stale).
- **repo-map generator:** ran clean (exit 0), `mode=auto`, `_bmad` excluded → 95-line navigable map; backend
  signatures captured; `.venv`/`node_modules`/`_artifacts`/`_claude_artifacts` correctly ignored.

## ⚠️ Your Actions (I do not commit/push — git-policy)
**Two separate repos changed.** Review, then run:

**1) clean-bmad repo:**
```bash
cd "c:/Sudo_Hatter_Command/Projects/clean-bmad-workspace"
git add -A
git status                      # confirm the renames + new files look right
git commit -m "chore: conform to workspace-standard + add repo-map index; _01_My -> _my_resources (protected); deprecate _claude_artifacts"
git push
```

**2) home-base repo:**
```bash
cd "c:/Sudo_Hatter_Command"
git add -A
git status
git commit -m "docs: correct clean-bmad 'off-limits' mischaracterization (it's Daniel's clean-shell template); router status; clean-bmad cleanup artifacts"
git push
```

## Open / next
- **Pending master pass (out of scope here):** repoint the vendored `.claude`/`.opencode` commands + the
  `scripts/autopilot-dev-story.ps1` engine off `_claude_artifacts/` → home-base `_artifacts/` (verify the
  engine's `$RepoRoot` binding first), then delete `_claude_artifacts/`.
- **Next milestone (Daniel's gate):** clean-bmad cleanup verified ✓ → apply the same recipe to the live
  **aviationChat** project (its own assessment + implementation_plan + approval; it's the real 1,450-file app).
- Optional: re-run `_routing-canary/` (AGENTS.md renumber = routing-structure change) and a live cold-route test.
