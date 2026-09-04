# `_artifacts/` — LOCAL LAW (shared memory)

You are in the home base's **shared memory**. This file is the 10-second law of the place and **the single
authority on where a session folder goes**. Canon for the plan-first protocol:
`.agents/rules/artifacts-always-first.md` (+ root `AGENTS.md` §5). Folder shape, archive policy, worked
examples → `README.md`. The session ledger → `INDEX.md`.

## The law
- **READ**: scan `INDEX.md` newest-rows-first — don't walk the tree.
- **Route by ownership, never cwd or tool:**
  1. **Non-exempt project work** → stop; write to `Projects/<name>/_artifacts/` and read that store's
     `AGENTS.md` first. This remains true when the chat starts in the lobby.
  2. **Sudo-managed exception work** → the matching named bucket here. The complete registry is in
     `router.md`; currently only `Fresh_Workspace_BMAD/` and `OpenChat-Openrouter/`.
  3. **main / home-base / cross-project work** → `_main/<YYYY-MM-DD>_<slug>/`.
- Inside an exception bucket, story work nests under `epic_<E>/<story>/`; TEA/non-numeric story ids may use
  `tea/<story>/`. Parentage follows the work, not the tool.
- **NEVER** drop a story/session folder at a root that has an epic parent. **NEVER** write to the retired
  `_claude_artifacts/` / `_opencode_artifacts/` stores — if a story's `source:` line names one, that is dead
  history; write here.
- Session folder set: `implementation_plan.md` (approved BEFORE edits) + ONE `walkthrough.md` ending in
  `## Task Checklist` + `## Your Actions` — **no separate `task-list.md`**.
- After writing, update that bucket's `active-context.md` (the hand-off). **Do not hand-append an `INDEX.md`
  row**: the ledger is reconciled in batch by the SessionStart hooks + `/smh-update-maps-indexes`. Getting the
  folder right is what you owe.
- History is immutable: old rows keep old paths; retire to `_archived/`, never delete.
- **Finding history:** non-exempt project history has one authoritative home: the project's own
  `_artifacts/`. Only registered exceptions use named home-base buckets.
