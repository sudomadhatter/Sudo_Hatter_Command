# `_artifacts/` — LOCAL LAW (shared memory)

You are in the home base's **shared memory**. This file is the 10-second law of the place — a
digest, not the canon. Canon: `.agents/rules/artifacts-always-first.md` + root `AGENTS.md` §5.
Structure how-to → `README.md`. The scannable session ledger → `INDEX.md` (placement rules in its header).

## The law
- **READ**: scan `INDEX.md` newest-rows-first — don't walk the tree.
- **WRITE by the bucket rule — artifacts go where you work FROM:**
  - project work → per-project bucket `<project-folder-name>/` (create if missing, else reuse)
  - main / home-base / cross-project work → `_main/`
  - **stories → nest under the epic parent** `epic_<E>/<story>/` (create `epic_<E>/` if missing;
    TEA / non-numeric story ids → `tea/`); true one-off → `<YYYY-MM-DD>_<slug>/`
  - opencode agents → same rules inside `opencode/` (never the generic `_main/`)
- **NEVER** drop a story/session folder at a root that has an epic parent; **NEVER** write to the
  retired `_claude_artifacts/`/`_opencode_artifacts/` stores.
- Session folder set: `implementation_plan.md` (approved BEFORE edits) + ONE `walkthrough.md` ending
  in `## Task Checklist` + `## Your Actions` — **no separate `task-list.md`**.
- After writing: append a row to `INDEX.md` (+ the bucket's depth-3 `INDEX.md` if it has one) and
  update that bucket's `active-context.md` (the hand-off).
- History is immutable: old rows keep old paths; retire to `_archived/`, don't delete.
