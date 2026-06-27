---
IsArtifact: true
ArtifactMetadata:
  title: "Task list — clean-workspace mirror fix + main_debug standard (todo item 3)"
  type: task_list
  date: 2026-06-27
  todo_item: 3
---

# Task list (final)

## Phase 1 — re-vendor item-2 engine into the migrated projects
- [x] Investigate Fresh vs AGY vs lobby — isolate real divergences (engine stale; opencode unfiltered)
- [x] Re-vendor `/sync-agents -Target` into Fresh + AGY (additive .agents + filtered .claude/.opencode)
- [x] Verify engine (`GlobalsOnly` x4), counts, platform filter both directions

## Phase 2 — `main_debug` → `main` as the canonical dev standard
- [x] Audit full blast radius of the branch model (root AGENTS ✓, AGY ✓, git-policy SILENT ← root cause, Fresh main-only)
- [x] `git-policy.md` — add canonical "Branch model — main_debug → main" section (single source of truth)
- [x] Canonicalize hook → master `.agents/hooks/require-push-approval.py` + `sync-agents.ps1` deploys to every `.claude/hooks/`
- [x] Root `AGENTS.md` §6 — point at git-policy.md branch model; update hook source ref
- [x] Fresh `AGENTS.md` §8 — rewrite main-only → main_debug; delete 3 `merge_main.md` copies
- [x] Project template `AGENTS.md` — add GATES pointer (new clones born standard)
- [x] Re-sync lobby + Fresh + AGY; verify hook gates main_debug everywhere, git-policy identical, Fresh 36/35/31

## Pending (Daniel)
- [ ] Create `main_debug` on the Fresh repo (`git branch main_debug main && git push -u origin main_debug`); GitHub: default base → main_debug, protect `main`
- [ ] Run the 3 surgical per-repo commits (walkthrough → Your Actions) on `main_debug`, verifying staged set excludes `_my_resources/`
- [ ] Restart opencode to pick up the refreshed global command cache

## Out of scope → later items
- [ ] Mobile/desktop rules (item 4) — `mobile-mode.md` now vendored into both projects
- [ ] Rename project folders to match git repos (item 5)
- [ ] `Ingestion_pipeline_AvCh` migration (old `.agent/` / `_claude_artifacts/` layout)
