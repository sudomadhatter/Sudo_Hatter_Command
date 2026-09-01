# SCC-57 — `To Do Next` is the queue, `Blocking` is the status

**Task** under **SCC-12** (*Jira — system rules and workflows*) · branch
`chore/SCC-57-to-do-next-is-the-queue` off `main` · lane **LOCAL**.

## Why

The operator added a **`To Do Next`** column to the SCC board and asked that it be the answer to
"what's next?" — whether that question arrives as `/sudo-boot-sprint-memory` or as a bare question in
chat. Nothing in the system knew the column existed, so the answer came back as the eleven-card
`To Do` pile in key order with his one deliberately-chosen card buried in it.

## What the board actually says (queried, not read from the docs)

| | SCC | AVCH |
|---|---|---|
| statuses live | `To Do` · **`To Do Next`** · **`Blocking`** · `In Progress` · `Done` | `To Do` · `In Progress` · `In Review` · `Deferred` · `Done` |

`.agents/rules/jira.md` declared a single shared set — `To Do · In Progress · In Review · Done ·
Deferred · Blocked` — which was wrong in **two** ways beyond the missing column:

- **`Blocked` does not exist on either board.** The real name is **`Blocking`**, and two tickets
  (SCC-23, SCC-46) sit in it right now. `transition --status "Blocked"` fails outright. This was a
  live defect independent of the feature, and SCC-55 could not fix it — that ticket explicitly
  declares `.agents/rules/jira.md` **out of scope** ("already current and stays the canonical
  agent-facing copy") while it refreshes the two human mirrors under `_my_resources/`.
- **The two boards were never the same set.** `In Review` and `Deferred` are AVCH-only; the doc
  presented all of it as universal.

`To Do Next` was verified to sit in Jira's **To Do category**, not Done — so queued work does not
read as shipped. That was the one way the column could have been built wrong, and it wasn't.

## The ruling this encodes

> *"the todo lists are now in jira, I may take notes there but thats not something i need the agents
> reading now, its replaced with 'To Do Next'"* — operator, 2026-08-09

`In Progress` → **`To Do Next`** → `To Do`, first non-empty rank wins. `Blocking` is surfaced as an
impediment and is never offered as something to start.
`_my_resources/open_tasks/todo_list.md` is **retired as an agent source**.

## Changed

| File | What |
|---|---|
| `.agents/rules/jira.md` | per-board status table replacing the single wrong list; new **§The queue** with the rank order, the verified per-rank queries, and the `todo_list.md` prohibition |
| `AGENTS.md` | "what's next?" added to the named Jira triggers (§on-demand rules); §7 `pick up` repointed from `todo_list.md` to the board |
| `.agents/commands/sudo-boot-sprint-memory.md` | Step 0 gains a **lobby answer** instead of a dead end; Step 2b makes `To Do Next` the operator's override of the computed YAML pick |
| `_my_resources/_quick_reference/sudo_workflows_testing.md` | SOP currency (three usage surfaces changed) — operator-facing `⭐ To Do Next` block in *Start here*, plus the per-board status facts in §11 |
| `_artifacts/_memory/to-do-next-is-the-queue.md` (+ index row) | the ruling, so it is not re-proposed |
| `_my_resources/_quick_reference/jira_manual.md` · `_my_resources/diagrams_guides/system/jira_integration_guide.md` | **scope widened deliberately** — SCC-55 landed mid-task and rewrote both status tables *without* `To Do Next` (it predated the column). One row each rather than ship a freshly-refreshed reference that omits the status the operator just made canonical. SCC-55 had already fixed `Blocking` in these two; the agent-facing rule was the copy it declared out of scope |

## Two design decisions

**1. Per-board-optional, never SCC-hardcoded.** The operator said *"if we can use this I will also add
it to AVCH."* So the rule is written the way `jira.md` already writes an optional status — honored
where the board has it, silently skipped where it doesn't. **Creating the column in the Jira UI is the
entire install.** Verified this is real rather than assumed:

```
status = "To Do Next"  on AVCH (no such column) → exit 0, zero rows
status = "Nonsense Status"                      → exit 1, hard error
```

It degrades silently *because* SCC creating the column registered the name site-wide. An empty rank is
therefore genuinely "nothing queued", and a non-zero exit is a real failure worth reporting — the two
are distinguishable, which is what makes the fall-through safe to write as an instruction.

**2. On a BMAD project the column outranks `sprint-status.yaml`.** `/sudo-boot-sprint-memory` computes
the next story from the YAML, and that YAML **lags by design** — ② and ③ never write it, only close-out
does. A card the operator placed by hand beats a stale computed row. When the two disagree the command
now reports **both** and leads with the board, rather than silently swapping one for the other.

## Pitfall — the JQL I nearly shipped

The first draft of §The queue carried a single elegant query that ranked the statuses inline:

```sql
ORDER BY CASE WHEN status = 'In Progress' THEN 1 WHEN status = 'To Do Next' THEN 2 ELSE 3 END, key
```

**It is not valid JQL.** Jira rejects it at the parser: *"'when' is a reserved jql word."* It reads
like SQL, and a rule doc is exactly where a plausible-looking query survives forever unrun, because
nothing executes a fenced code block. Replaced with four flat per-rank queries, each executed against
the live board before being written down. The ⛔ note naming `CASE WHEN` as invalid is deliberate — the
next agent will reach for it too.

## Pitfall — `cp` of a whole shared file carried another branch's base

The memory ruling was written into the operator's checkout first, then moved here with
`cp _artifacts/_memory/MEMORY.md <worktree>/` — copying the **entire file** to transport a **one-line**
addition. That checkout was sitting on `chore/SCC-55-jira-docs-refresh`, whose base predated SCC-50 and
SCC-51, so the copy silently reverted line 97 to a row pointing at
`artifact-budgets-are-scoped-not-universal.md` — a file SCC-51 deleted — and re-stranded its
replacement. It would have merged clean and undone two closed tickets.

**The count did not catch it. The sets did.** Rows and files both read 140/140, because one dangling row
and one stranded file cancel out in a count. Only `stranded == 0 and dangling == 0` fails on it:

```
STRANDED: ['limits-relocate-content-never-truncate.md']
DANGLING: ['artifact-budgets-are-scoped-not-universal.md']
```

Fix: `git checkout -- MEMORY.md` to restore the branch's own version, then re-apply the single line as an
edit. **Move a diff, never a file.** This is the second time in two days that the memory invariant caught
a defect a clean merge produced — the first was SCC-50's, from the opposite direction.

## Gate

- `python3 .agents/scripts/tests/run_all.py` — see the merge commit message for the file count
- `python3 .agents/scripts/workflow_lint.py` — from the lobby root this resolves to the AGY board;
  its one error (`active story with NO story file: 19-5-adk-agent-evaluation-stage-2`) is
  **pre-existing** and unrelated, same as SCC-50/51/54 recorded
- link + anchor check across the touched `.md`
- SOP currency: satisfied by the `sudo_workflows_testing.md` change in the same commit

## Still owed

- **`jira_feed.py mint` cannot mint a pure Task.** Found while scoping this: with no `--story` it
  tracebacks — `AttributeError: 'NoneType' object has no attribute 'lower'` at `wf_common.norm_id`
  via `resolve_story_file`. Every SCC ticket is a Task, so the lobby's whole board has to be minted by
  hand through `acli` (which is how SCC-57 itself was created). Not fixed here — it is a script defect,
  not a docs one.
- The column exists only on SCC. Adding it to AVCH is a UI action whenever the operator wants it; no
  code or rule change is needed.
