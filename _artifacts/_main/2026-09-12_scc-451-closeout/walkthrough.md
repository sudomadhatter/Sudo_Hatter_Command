---
ticket: SCC-451
lane: chore/SCC-451-closeout
riders: []
base: origin/main @ efd79fa4
---

# SCC-451 close-out — the random CI red, and the last four open rows

SCC-451 landed in two pieces and stayed open on purpose. Step one shipped the inert-path predicate
and `ceremony_tier`; step two shipped SCC-452's measured reach score, merged at `efd79fa4` as
PR #219. What kept the parent open after that was not code — it was four unsettled rows in its own
`## Your Actions`, one of which said, in writing, that SCC-451 could not close honestly.

This lane settles all four and fixes the one that was a real defect.

## The random CI red, fixed rather than deferred a second time

`test_repo_template.py` had been reddening CI at random — one red in four runs of identical code, on
run `34703459646`, against a diff that touched no template file. The cause was measured, not guessed.

`leaks()` walks a **live** directory tree looking for paths that carry an absolute template root.
Its `p.stat()` call sat **outside** the `try/except OSError` that guarded only `read_text()`.
Meanwhile `git commit` inside `build_repo` spawns git's `run_auto_maintenance()`, which creates and
deletes `.git/objects/maintenance.lock` in that very tree. A file that vanished between `is_file()`
and `stat()` therefore escaped as an unhandled `FileNotFoundError` and killed the entire run — and
because the window is milliseconds wide, it hit roughly one run in four.

Two halves, because they answer two different questions:

- **`stat()` moves inside the guard.** A path that disappeared mid-walk cannot be a leak, so the
  detector's honest answer is to skip it, never to crash the run that asked. This covers every
  builder that walks a live tree, not only the one measured.
- **`build_repo` sets `gc.auto=0` and `maintenance.auto=false`.** The fixture repo exists for one
  commit and has nothing to maintain, while the rest of the file clones, hard-links and chmods that
  same tree read-only. Removing the trigger is worth doing even with the detector hardened.

### The pin was vacuous first, and that is the part worth reading

T6 reproduces the race deterministically. The **first** version patched `Path.stat` to always raise
for the lock file — and the mutant that restores the original defect **survived it**.

The reason is a detail no amount of reasoning would have produced: `is_symlink()` calls `lstat()`,
which is `stat(follow_symlinks=False)`, so the **first** stat of any path in that walk comes from the
symlink check, not from the code under test. A blanket raise therefore fired inside `is_file()` —
which swallows `OSError` and returns `False` — and the bare `p.stat()` being tested was never
reached at all. The pin asserted something true about a code path that never ran.

The pin now patches `is_file()` to **unlink the file and return `True`**, which is exactly what git
does: the walk sees a file, and it is genuinely gone a moment later. It carries a **control** proving
a real template leak planted beside the vanishing file is still reported, because a detector that can
no longer go red would be worse than the crash it replaced.

This is the second vacuous pin in the SCC-451 family, after SCC-452's empty-path guard. Both were
caught the same way — by mutating, not by re-reading.

## Task Checklist

- [x] `leaks()` hardened so a vanishing file is skipped, not fatal
- [x] `build_repo` no longer spawns background git maintenance
- [x] T6 pins the race by real deletion in the real window, with a control
- [x] T7 pins the fixture's config
- [x] Mutants restoring each half both killed, by named case
- [x] All five `## Your Actions` rows on the inert-paths walkthrough settled with evidence
- [x] The process-audit walkthrough gained the `## Your Actions` section `finish` requires
- [x] SCC-453 rehomed and SCC-456 minted, so no open child blocks the parent

## Evidence

| Gate | Result |
|---|---|
| `test_repo_template.py` | 53/53 |
| Mutant sweep | 2/2 killed, tree restored byte-identical |
| `run_all.py` | 92/92 files |
| `workflow_lint --toolkit-only` | 0 errors, 0 warnings |

| Mutant | Must kill | Outcome |
|---|---|---|
| `stat()` moved back outside the guard | T6 · a file that vanishes | KILLED |
| the fixture's gc/maintenance config deleted | T7 · the fixture repo | KILLED |

## The board changes this lane made

Closing SCC-451 honestly needed three board corrections, all of them recorded rather than assumed:

**SCC-453 moved to SCC-455 under Epic SCC-33.** The toolchain manifest was a subtask of SCC-451 by
mis-parenting only — it is CI/CD plumbing, not path classification — and it blocked the parent while
SCC-451's own subject was finished. Jira refuses a subtask-to-task conversion through every API
(`acli` and the REST edit endpoint both answer *"The issue type selected is invalid"*), and a subtask
cannot hang directly off an Epic, while every existing task under SCC-33 is Done. So the key changed:
SCC-455 carries the description verbatim, and SCC-453 is closed as superseded, labelled `descoped`,
linked `Duplicate`, with a comment explaining that the board's only terminal column is `Done`.

**The credential-free ruleset receipt moved to AVCH-153.** SCC-451's description claimed lobby work
that cannot exist here — the lobby has no `arm_rulesets.py`; both copies live in AviationChat and the
skeleton. The 2,083-character block was cut from SCC-451 and appended to AVCH-153 verbatim, and both
writes were read back byte-identical to intent.

**The `sudo-command-center` door drift is SCC-456.** Measured rather than described: the two
quick-dev doors differ from their masters by **690** and **502** lines — they are the retired
`/smh-dev-task-tests` body, so a new project cloned from that template ships a dev door matching no
rule in the system — against **28** and **54** lines of placeholder drift on the standing-push pair.

## Code Review (2026-09-12)

Not run as a fan-out. This lane is one test-file fix plus artifact edits, and the substantive check
that applies to it — can the new pins actually fail? — was run as a mutation sweep instead, which is
the stronger evidence for guard code: 2/2 killed by named case, and the first version of T6 was
rejected *because* the sweep failed it.

## Your Actions

- **Merge the PR when its check is green.** One test file and artifacts; the lobby runs one check
  (`main-write-gate`), which runs `run_all.py` and `workflow_lint`.
- **SCC-451 closes on merge.** Its children are settled — SCC-452 Done, SCC-453 rehomed — and every
  action row is ticked, so `jira_feed.py finish` will write `Done` rather than hold.
