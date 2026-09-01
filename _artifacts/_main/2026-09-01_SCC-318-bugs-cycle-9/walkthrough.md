# SCC-318 — Bugs and Updates, cycle 9 (consolidated lane)

**Lane:** `chore/SCC-318-bugs-cycle-9` · **Riders:** SCC-335, SCC-359, SCC-364
**Plan:** [implementation_plan.md](implementation_plan.md) · **Manifest:** [task.yaml](task.yaml)

Cycle 9's three remaining subtasks, run as ONE lane per `work-consolidation.md` rule 2. Part A
(SCC-334) had already shipped separately under SCC-333 and its key was later deleted from the board.

## What each part was, and what closed it

### SCC-335 — every acli seam decoded with the machine's locale ✅

The one that had already destroyed operator data: it corrupted SCC-318's own description on
2026-08-27. Six `subprocess.run` calls reached `acli` with `text=True` and no `encoding=`, so they
decoded with `locale.getencoding()`. `acli` is a Go binary and always writes UTF-8, so on any box
whose locale is not UTF-8 every description read came back mojibake — and since
`edit --description` **replaces** the whole field, a read-modify-write wrote the mojibake back.
`U+2B50` is lossy that way (UTF-8 `E2 AD 90`; cp1252 has no mapping for `0x90`) and cannot be
recovered from the written text at all.

Pinned all six: `jira_feed.acli` (the seam every verb rides, and the one `task_preflight` imports
rather than duplicating), `label_tasks.acli`, and four sites in `jira_ticket.py`.

The read-back guard was reporting a *mangled* line as a *deleted* line and telling the operator to
"restore the ticket from the text above" — the text above being the damaged copy, so obeying it
made the corruption permanent. It now separates the two by ASCII skeleton, names the codepoints
that changed, and says explicitly not to re-run or hand-edit from the read-back.

### SCC-364 — close-out rewrote a tree it was about to prune ✅

`jira_ticket.py done` does two things: it rewrites the ticket outline **in the tree**, then it
writes the board. `/smh-close-task-merge-tree` called it at Step 4, *after* the merge — where the
lane is merged, the door's own SCC-175 rule bans post-merge commits, and Step 5 prunes the tree. The
file write could never land, and nothing said so, because `done` exits 0 on the board half. So
`main` kept an all-unticked Plan forever while the step's prose claimed the tree was the source.

Fixed with no new code, because `jira_ticket.py` already had both halves: Step 3 now calls
`done --local` (tree only) inside the door's existing "commit this before the PR" window, so the
ticked outline rides the PR; Step 4 calls `describe`, which renders the landed outline to the board
and touches no file.

### SCC-359 — the approval-sha check that can never pass ✅

`/smh-quick-dev` Step 1.5 condition 3 demanded `git log -1 --format=%h -- <plan>` **equal** the sha
on the `— recorded at <sha>` line. `/smh-plan-task` Step 5 requires that line to carry the sha of
the commit that recorded it — unknowable until that commit exists — so the planner writes
`<pending>`, commits, and stamps the sha in a **second** commit. The plan's last touch is therefore
always the stamp, never the recorded sha, and the condition could never pass for a lane that
followed the convention. An agent reading Step 1.5 literally stops a lane the operator has already
approved.

Fixed on the **reader**, because the other remedy is circular: any scheme that records a sha *into*
the plan file changes the plan file, so "last touch equals recorded" cannot hold whichever sha is
chosen. Step 1.5 now falls through to `git diff <recorded>..<last touch> -- <plan>` and passes a
**stamp-only successor** — a diff touching the `— recorded at` line and nothing else. The no-sha
tooth is untouched: a missing operand is still a re-armed gate.

Applied to all three places the contract lives, so writer, reader and law cannot drift apart:
`smh-plan-task.md` Step 5 (what the second commit may contain), `smh-quick-dev.md` Step 1.5 (what
it will accept), `000-PLAN-FIRST-GATE.md` §3 (the law both cite).

**Twin check, answered so nobody repeats the search:** `/cicd-quick-dev` carries **no** approval-sha
box. Grepped `.agents/commands/` for `recorded at`, `git log -1 --format=%h` and "unchanged since" —
the contract appears in exactly three files, all named above. There is no twin to port to.

**A third measurement, produced by this lane itself.** SCC-359 cited SCC-347 and SCC-358. Recording
this lane's own approval reproduced it a third time: `fbd4ac20` recorded, `6126fe6d` stamped, and
the entire delta is one line — `<pending>` → the sha. It is in this branch's history as evidence.

## Constraints and decisions, recorded as they were met

- **SCC-335 is not Windows-only, as its ticket claimed — it is LOCALE-only.** `LC_ALL=C` plus
  `PYTHONUTF8=0` makes `locale.getencoding()` return `US-ASCII` on this Mac (measured), which
  reproduces the live corruption here. The test forces the locale rather than skipping on POSIX: a
  test the author can never watch fail is not a test.
- **Two fixture defects, both the family `test_jira_feed.py` already documents** — *a stub more
  generous than the tool it stands in for cannot fail on the bug it exists to catch.* The stub
  emitted `print(json.dumps(...))`, whose `ensure_ascii=True` default put every non-ASCII character
  on the wire as a pure-ASCII escape, so the first six cases **passed on a bug that was fully
  present**. Measured against the live board: real acli emits raw `e2 9b 94` / `e2 ad 90` and no
  `\uXXXX` escape appears in 7,753 bytes. The stub now writes raw UTF-8 through `sys.stdout.buffer`,
  which also models Go's locale independence.
- **The armed pre-commit encoding gate blocked the first commit, correctly.** Three raw `U+FFFD`
  characters written as test literals; `workflow_lint` cannot tell a deliberate literal from a
  corrupted byte and should not try. Switched to escapes.
- **`CS-19` was already taken** by SCC-357's block, so SCC-364's case block is `CS-23`. Caught by
  running the filter and seeing two blocks match.
- **The old "tree stays the source" sentence is now a reserved marker.** `CS-23 E` fails if Step 4
  carries it again, so the door's explanation of the fix deliberately does not quote it — a comment
  that reproduces the banned string inverts the guard (the CS-16 scar).
- **`[sop-ok]` used once, on the SCC-335 commit**, with the reasoning in the log: nothing about a
  subprocess decode is a usage surface. SCC-364 *does* move one, and stages the SOP with it.

## Your Actions

- [ ] **Verify the SCC-335 fix on the Windows PC.** This is the machine that produced the original
      corruption. Run `python .agents\scripts\jira_feed.py index-row --key SCC-373 --line "  test row" --apply`
      and confirm the description still carries `⛔` and `⭐` afterwards, then remove the test row.
      The Mac cases prove the decode; only the PC proves it against the real cp1252 console.

## Code Review (pending)
