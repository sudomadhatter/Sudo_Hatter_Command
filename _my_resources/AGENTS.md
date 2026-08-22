# `_my_resources/` — LOCAL LAW (Daniel's thinking space — IGNORED BY DEFAULT)

You are in Daniel's **personal thinking and brainstorming space**. This is where he works ideas out,
not where the system is specified.

## The law (operator ruling 2026-08-10, SCC-74)

- **⛔ IGNORE this folder entirely unless Daniel links you to a specific document in it.** Not
  "read it lightly", not "skim it for context" — do not open it. A link from him, in the moment, is
  the only entry ticket, and it admits *that document*, not the folder.
- **NEVER create, edit, move, or delete anything here.** An approval given elsewhere does not carry
  in here.
- **Nothing here is authoritative.** It is a scratchpad: half-formed plans, superseded notes, and
  thinking-out-loud. **Staleness here is fine by design.** If something in here disagrees with the
  live repo, the repo is right — always cross-check before acting on anything you were pointed at.

### Why the door is closed rather than ajar

This folder is deliberately excluded from repo-map regen, from linter scans, and from GitNexus
(`--ignore _my_resources`; "don't even read" in `check_maps.py`) — **do not "fix" that.** The
exemption is the point: it is what makes this a safe place to think out loud.

The cost of that exemption used to be paid by the wrong files. Thirteen procedural documents — the
SOPs and PRDs that tell the operator what to type — lived in here, inside the one folder every
drift-checker is forbidden to look at. They rotted quietly for months, and nothing was *able* to
notice: the index they sat under listed 2 files that did not exist and omitted 4 that did.

**SCC-74 moved all of them to `docs/_scc_sops_prds/`,** which is scanned, tested, and gated. So the
two folders now get opposite treatment on purpose:

| | `docs/` | `_my_resources/` (here) |
|---|---|---|
| what it is | the **maintained** surface | **thinking space** |
| staleness | must never happen | fine by design |
| agents | read it, keep it correct | **ignore unless linked** |

A procedural doc found in here is therefore a defect — it belongs in `docs/_scc_sops_prds/`, and
`.agents/scripts/tests/test_sops_prds_folder.py` (T6, in `run_all`) fails if one reappears.

## STANDING EXCEPTIONS (the only automatic entries)

- **`open_tasks/todo_list.md`** — `/smh-update-maps-indexes` refreshes the `## Open Tasks` file-list
  inside it (only that list; his `## Todo list` prose and the task files stay his).
  ⛔ It is **NOT** an agent source for "what's next" — that was retired 2026-08-09. The queue is the
  live Jira board (`In Progress` → `To Do Next` → `To Do`) per `.agents/rules/jira.md`.
- **`migrations/`** — the new-computer setup kit (secrets export/restore, rename-day script) and
  one-off migration records. Agents may read it and **run its scripts** once Daniel points them at a
  migration (`/cicd-resume`, "set up this machine", "restore my secrets") — the folder exists to be
  executed, so read-only would make it useless. Being pointed at it *is* the link this law requires.
  Start at `migrations/INDEX.md`. Still no unprompted edits, and **never print secret values** — key
  names only. Deliberately disposable: it lives here rather than at the top level so it can be
  deleted outright once a machine is set up.

## What's in here

`board_sessions/` (output briefs from `/smh-adviser-board`) · `migrations/` (above) · `open_tasks/`
(his plans, PRPs and todo list) · `research_docs/` (research + theory notes). Inventory →
`README.md`.
