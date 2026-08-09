# Walkthrough — Standardized the "what's next" open-tasks check

## What changed
Made `_my_resources/open_tasks/` a **system-wide standard** so asking "what's next / open
tasks / what's left" reads Daniel's notes for **wherever you work FROM** — lobby reads the
home-base folder; inside a converted project reads that project's own folder. READ-ONLY for
agents; always cross-check vs live project files.

Trigger = **on-demand** (router + each project's `AGENTS.md` routing row). No SessionStart hook.

## Files touched
- **aviationChat-AGY**
  - `git mv`'d 5 notes `_my_resources/_Open_Task/` → `_my_resources/open_tasks/`
    (admin_graph_rag_update, looping_workflow_prp, production-readiness-audit,
    repo-map-auto-maintenance, sprint-dependency-map); removed empty `_Open_Task/`.
  - new `_my_resources/open_tasks/todo_list.md` (skeleton).
  - `AGENTS.md` — added READ-ONLY "what's next / open tasks" routing row.
- **clean-bmad-workspace**
  - new `_my_resources/open_tasks/todo_list.md` (skeleton).
  - `AGENTS.md` — added the same routing row.
- **Lobby** — `router.md` row 20 now resolves by where-you-work-from.
- **Memory** — `my-resources-personal-area-protected.md` carve-out upgraded to system-wide.

## Scope
Converted projects only (aviationChat-AGY, clean-bmad-workspace) + home base.
jetChat, B&L WorldWide, NEXGen Films, ingestion-Pipeline-AC, openCode untouched — they
get the scaffold when converted.

## Verify
- `_my_resources/open_tasks/todo_list.md` resolves at home base + both converted projects ✓
- both project `AGENTS.md` carry the read-only open-tasks row ✓
- aviationChat `_Open_Task/` gone; 5 notes intact under `open_tasks/` ✓

## Your Actions (git — I ran nothing)
Two repos changed. From each repo root, commit explicit paths:

```sh
# home base (c:/Sudo_Hatter_Command)
git add router.md _artifacts/_home/2026-06-25_open-tasks-standard/ _artifacts/INDEX.md
git commit -m "feat(home): standardize _my_resources/open_tasks/ 'what's next' check across converted workspaces"

# aviationChat-AGY (Projects/aviationChat-AGY)
git add _my_resources/open_tasks/ AGENTS.md
git rm -r --cached _my_resources/_Open_Task 2>/dev/null
git commit -m "feat: adopt _my_resources/open_tasks/ standard; migrate _Open_Task notes; add what's-next routing row"

# clean-bmad-workspace (Projects/clean-bmad-workspace)
git add _my_resources/open_tasks/ AGENTS.md
git commit -m "feat: adopt _my_resources/open_tasks/ standard; add what's-next routing row"
```
(The `git mv` in aviationChat already staged the renames; the `git rm --cached` line is a no-op safety net.)
