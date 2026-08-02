# `_my_resources/` — LOCAL LAW (Daniel's personal area — PROTECTED)

You are in Daniel's **personal area**. Default posture: **READ-ONLY**, read only what a task or a
routing row points you at. What's here → `README.md`.

## The law
- **NEVER create, edit, move, or delete anything here on your own.** Touch a file only when Daniel
  explicitly directs you to that file, in the moment. (An approval elsewhere doesn't carry in here.)
- **STANDING EXCEPTIONS:**
  - `open_tasks/todo_list.md` — `/update-maps-indexes` refreshes the `## Open Tasks` file-list inside (only that list; his `## Todo list` prose and task files stay his).
  - `_quick_reference/` — Agents are ALLOWED to read, reference, and update quick-reference documents (e.g., `sprint_scrum_board_map.md`, `sudo_workflows_testing.md`) as needed/directed.
  - `migrations/` — the new-computer setup kit (secrets export/restore, rename-day script) + one-off
    migration records. Agents are ALLOWED to read it and RUN its scripts **once Daniel points them at a
    migration** (`/sudo-resume`, "set up this machine", "restore my secrets") — the whole folder exists to
    be executed, so read-only would make it useless. Start at `migrations/INDEX.md`. Still no unprompted
    edits, and **never print secret values** — key names only. Deliberately disposable: it sits here rather
    than at the top level so it can be deleted outright once a machine is set up.
- `open_tasks/todo_list.md` — Daniel's "what's next" queue. Check the todo list for sub projects if they're listed under '## Sub-Projects Todo Lists'.  Surfaced READ-ONLY on "pick up" and on
  "what's next / open tasks" asks. **Cross-check against live project files** — notes can be stale.
- `board_sessions/` (Adviser Board session output briefs — output from `/sudo-adviser-board`).
- `diagrams_guides/` (his reference diagrams — see its `INDEX.md`), `youtube_transcripts/` (source
  notes + strategy plans), `docs/` (his docs, incl. the master-implementation-plan).
- This folder is deliberately **excluded** from repo-map regen + linter scans and from GitNexus
  (`--ignore _my_resources`; "don't even read" in `check_maps.py`) — do not "fix" that.
