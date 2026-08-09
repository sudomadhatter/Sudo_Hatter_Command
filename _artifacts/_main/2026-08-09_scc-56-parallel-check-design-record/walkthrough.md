# SCC-56 — `/sudo-parallel-check`: the design record (the command is **not** built)

**Task** · branch `chore/SCC-56-parallel-check-design-record` off `main` · lane **LOCAL** ·
one commit, `4ec6cce`.

## ⛔ Read this first — the ticket is NOT satisfied by this branch

SCC-56's scope is **building** `/sudo-parallel-check <parent-key>`, plus removing the parallel ruling
from `/sudo-write-story-tests` Step 1.6, updating `rules/jira.md`, the SOP page, tests in the
enforcement suite, and the four-platform sync. **None of that is here.** The operator paused the
build; what landed is the **design record** so the rulings survive the session that produced them.

The commit says so in its own words: *"Design record only. The command is NOT built — operator
paused it."*

So this branch is closeable and the ticket is **not**. See §Ticket disposition.

## What actually landed — two memory gaps that would have cost the next session

**1. `sudo-update-scrum-board-five-zones.md` described a command that no longer exists.**
`/sudo-update-scrum-board` was retired **2026-08-07** (SCC-13, commit `8144518`), but the memory
still taught it as live. This is not hypothetical drift — **the operator went looking for the command
today and could not find it.** The file now leads with the retirement, carries the recovery command

```
git show 8144518^:.agents/commands/sudo-update-scrum-board.md
```

and warns that a stale **live copy still sits in `Projects/OpenChat-Openrouter`**, which is how a
retired command comes back to life.

**2. `parallel-ok-is-a-set-property.md` is new** — and it records why a shipped label never worked.

> *"you can only have parallel-ok when it compares stories"* — operator, 2026-08-09

`parallel-ok` is a property of a **set at a moment**, never of one story. `/sudo-write-story-tests`
Step 1.6 rules it at story pickup — which mints 19.1's ticket **before 19.2's story file exists**, so
there is nothing to compare against, and it is never re-evaluated. A boolean also cannot express
`after AVCH-34`; the edge is simply lost.

**The proof it never worked is empirical, not theoretical:** *zero* tickets across `SCC` + `AVCH`
carry any of the three labels, and the `Parallel-OK` saved filter returns nothing.

Ruling: `parallel-ok` moves **out of** ① into an on-request snapshot. `quick-dev` and `blocked`
**stay** — both are per-story facts genuinely knowable at pickup.

## The four rulings the future build must honour

1. **It STATES, it never STARTS.** Names each counterpart and prints the commands to act on it.
   Touches Jira; never the working tree.
2. **Scoped to ONE parent's children** — Stories under a BMAD epic **or Tasks under a grouping
   epic**, so it answers the question for SCC's Tasks too.
3. **It is a SNAPSHOT and must detect its own staleness.** The verdict carries the set it was
   computed against (`verified <date> against N children: <keys>`); a stamped set that no longer
   matches the parent's current children reads as *"re-run me"*, never as a verdict. **Load-bearing,
   not a footnote** — an undetectably stale snapshot is precisely the failure of the sprint
   dependency map and of the `Deferred` saved filter, both of which bit on 2026-08-09.
4. **Fails toward 🔒, and prints its evidence per row.** A false 🟢 puts two lanes on the same line;
   a false 🔒 costs only serialisation. Extraction from a story file is a judgment, so it must be
   auditable.

**Prior art, and it is recoverable:** the retired `/sudo-update-scrum-board` Step 2.5 carried the
set-is-the-verdict model, the four verdicts, the touch-set authority order, and the 2026-07-31
incident that proved the grounding gate. Recover it with the `git show` above — which is exactly why
gap 1 had to be fixed before gap 2 was worth writing down.

## Ticket disposition — why SCC-56 was NOT moved to `Done`

`/close-task-merge-tree` Step 4 moves the ticket to `Done`. **That step was deliberately not taken**,
and the branch was landed without it.

Marking SCC-56 `Done` would assert on the board that `/sudo-parallel-check` exists. It does not.
Every downstream reader — the saved filters, `jira_feed.py audit`, the next session asking "what's
next?" — would take that at face value, and the paused build would be invisible. The close-out rule
that governs the neighbouring case says it plainly: *"A ticket that reads `Done` while the merge
failed is a lie on the board."* The same logic applies to a ticket that reads `Done` while its
deliverable was never written.

The ticket stays open with its full scope intact; the Dev Record on it now states exactly what landed
and what did not. **This is the operator's call to revisit** — the two honest shapes are: leave
SCC-56 open for the build (what was done), or split the design record onto its own ticket and let
SCC-56 track only the command.

## Gate

`run_all.py`, `workflow_lint.py`, link check, and the memory-index invariant — real totals in the
merge commit message. SOP currency does **not** apply: the diff touches only `_artifacts/_memory/`,
no usage surface (`.agents/commands/`, `.agents/rules/`, `.agents/scripts/`, git hooks, root
`AGENTS.md`), so the armed gate correctly stayed silent.

## Still owed

- **`/sudo-parallel-check` itself** — the whole of SCC-56's stated scope: the command, the Step 1.6
  removal from `/sudo-write-story-tests`, `rules/jira.md` label vocabulary + guardrail 4, the SOP
  page, enforcement-suite tests, four-platform sync.
- **The stale live copy in `Projects/OpenChat-Openrouter`** — a retired command still sitting where
  it can be run or re-synced. Named in the memory; not removed here.
