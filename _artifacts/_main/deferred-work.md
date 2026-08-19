# Deferred work — the center's BLOCKED-work ledger

This is the `DEFERRED_WORK` file the code-review engine's caller contract names, for toolkit
lanes (the center is its own caller). **Nothing in this file is owed, and nothing in it becomes a
ticket** (operator rulings 2026-08-15, both): an entry exists ONLY because the lane that found it
structurally could not hold the fix — another live lane owned the file, the fix lives in another
repo, or it waits on an open decision. "Pre-existing" is not a reason to be here; a survivor with
no blocker is fixed in the lane that found it. An entry is picked up by the lane its blocker
names, or deleted when its reason dies. No close-out mints a ticket from this file, and no
review proposes one from it.

Format per entry: `- <title> [<file>] — <why it matters> · blocked by <live lane | repo | decision> · from <review>`.

## SCC-160 first live run — re-triage of the SCC-156 + SCC-154 residues (2026-08-15)

All three entries this ledger opened with were **fixed in-thread on `chore/SCC-160-fix-in-thread`**
(operator ruling the same day: survivors are fixed in the lane, not parked): Ctrl-C now stops
`run_all` (queue cancelled, children terminated — the review's one-word fix was measured
insufficient and replaced); a zero-file suite is exit 2; `dirty_paths` reads `porcelain -z` and
records both sides of a rename (direction measured: the old parse would have exempted moved
code). None of them had a structural blocker — under the recut `defer` definition they should
never have been here. The ledger is empty; that is its correct resting state.
## SCC-205 · the `-AP` law assertions in `test_review_engine.py`

**Blocker: an open decision** — the `_AP` rewrite.

SCC-209 removed the `_AP` maintenance obligation from `workflow_lint` and marked the three files
`UNMAINTAINED` ("do not diff, port to, or restamp"). But `test_review_engine.py` still carries eight
live law assertions against `cicd-code-review-AP.md` (`lens_budget: capped`, the inline-lens mandate,
the blind-lens ordering, the floor clause), and its tree-derived `CALLER_FILES` completeness row
*requires* that file to stay pinned. So the next change to engine law reds the suite until someone
edits a file the repo has declared frozen — **the trap SCC-209 defused in one check, relocated into
another.**

Not closable in this lane, both directions:
- Deleting the `-AP` files is forbidden by the plan's Part A (three autopilot engines invoke them by
  name; a missing command makes a headless stage improvise silently instead of failing).
- Un-pinning them from `CALLER_FILES` breaks the row that exists to stop a caller joining the engine
  unnoticed — the row that caught this lane's own `cicd-quick-dev` omission.

Found by the acceptance-auditor lens, 2026-08-18. Resolve with the `_AP` rewrite decision.
