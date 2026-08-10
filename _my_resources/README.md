## My personal thinking space

This is where **I** think — brainstorms, half-formed plans, research notes, superseded drafts.
It is not a specification of anything.

**Agents: ignore this folder unless I link you to a specific document in it.** The law is
`AGENTS.md` in this folder; read that, not this file, for how to behave here.

**Nothing in here is authoritative, and stale content is expected.** Always cross-check against the
live files in the repo before acting on anything I point you at.

### What's in here

- `open_tasks/` — features and ideas I'm working through, plus saved plans and PRPs.
  - `todo_list.md` — my personal notes. The **`## Open Tasks`** file-list inside it is kept fresh by
    `/smh-update-maps-indexes`, which mirrors the plan/PRP `.md` files I've dropped in `open_tasks/`.
    That command touches **only** that file-list — never my `## Todo list` notes or the task files.
  - ⚠️ This is **not** the work queue. "What's next" comes from the live Jira board, not from here.
- `board_sessions/` — output briefs and strategic direction from `/smh-adviser-board` sessions.
- `research_docs/` — research notes and theory (incl. the folder-as-workspace routing-system plan).
- `migrations/` — new-computer setup kit (secrets export/restore + the rename-day script) and one-off
  migration records. Start at its `INDEX.md`. **Read/run allowed when I point you at it** — see the
  standing exception in `AGENTS.md`. Deliberately disposable: delete it once a machine is set up.

### Where the real documentation lives

The SOPs and PRDs used to be in here (`_quick_reference/`, `diagrams_guides/`). **They moved to
`docs/_scc_sops_prds/` on 2026-08-10 (SCC-74)** — start at that folder's `INDEX.md`, and
`workflows_testing_SOP.md` is the one that answers "what do I type."

They moved because this folder is excluded from every drift-checker in the system, so nothing could
tell when they went stale — and they had. That exemption is deliberate and stays: it is what makes
this a safe place to think. Documentation that has to stay correct simply doesn't belong in it.
