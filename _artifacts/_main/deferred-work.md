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
