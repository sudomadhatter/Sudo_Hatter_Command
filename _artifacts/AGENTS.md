# `_artifacts/` — LOCAL LAW (shared memory)

You are in the home base's **shared memory**. This file is the 10-second law of the place and **the single
authority on where a session folder goes**. Canon for the plan-first protocol:
`.agents/rules/artifacts-always-first.md` (+ root `AGENTS.md` §5). Folder shape, archive policy, worked
examples → `README.md`. The session ledger → `INDEX.md`.

## The law
- **READ**: scan `INDEX.md` newest-rows-first — don't walk the tree.
- **FIRST decide WHERE, by the cwd you are working FROM:**
  - **cwd = a project** (`Projects/<name>/`) → **stop; you do not write here.** Write to that project's own
    `_artifacts/`, and read `Projects/<name>/_artifacts/AGENTS.md` first — it is the authority there and it
    names buckets this file does not.
  - **cwd = the home base** → here, by the bucket rule below.
- **THEN pick the bucket — first match wins. This list is complete; nothing else routes:**
  1. **story** (id `E.S`) → nest under the epic parent `epic_<E>/<story>/` (create `epic_<E>/` if missing;
     TEA / non-numeric story ids → `tea/<story>/`). Parent = the story id, **not** the tool — autopilot,
     BMAD and hand-dev all nest the same.
  2. **project work** (about one `Projects/<name>/`, done from here) → the per-project bucket
     `<project-folder-name>/…`, named exactly for the project folder. **Create it if missing, else reuse.**
  3. **main / home-base / cross-project work** (the standard, master `.agents/`, the router, lobby wiring)
     **or no home yet** → `_main/<YYYY-MM-DD>_<slug>/`.
  4. **opencode agents** → the same rules applied *inside* `opencode/` (`opencode/<project>/`,
     `opencode/_main/`, `opencode/<project>/<epic>/<story>/`) — never the generic buckets above.
- **NEVER** drop a story/session folder at a root that has an epic parent. **NEVER** write to the retired
  `_claude_artifacts/` / `_opencode_artifacts/` stores — if a story's `source:` line names one, that is dead
  history; write here.
- Session folder set: `implementation_plan.md` (approved BEFORE edits) + ONE `walkthrough.md` ending in
  `## Task Checklist` + `## Your Actions` — **no separate `task-list.md`**.
- After writing, update that bucket's `active-context.md` (the hand-off). **Do not hand-append an `INDEX.md`
  row**: the ledger is reconciled in batch by the SessionStart hooks + `/update-maps-indexes`. Getting the
  folder right is what you owe.
- History is immutable: old rows keep old paths; retire to `_archived/`, never delete.
- **Finding history:** a project's work may live in BOTH the home-base bucket `<project>/` and the
  project-local `Projects/<name>/_artifacts/` — check both.
