# Process audit — how the new development flow actually ran on SCC-451

**Written for:** Mr. Hatter, reviewing whether the gates he designed are earning their cost.

**Bottom line:** the gates found eleven real defects that the tests did not, and four of them were
in my own test assertions — pins that passed with the thing they named deleted. That is the system
working. The cost was that I misread its state twice and burned roughly ninety minutes chasing the
wrong blocker, both times because I reported from memory instead of re-reading the log.

Lane: SCC-451, merged to `main` at `aa763aa2` (PR 215). Four build commits off `4e2bbc89`,
36 files, +3474/−44.

---

## What the gates caught that nothing else would have

This is the part worth keeping. Each of these shipped green tests and passing lint right up until a
gate or a lens asked a different question.

**The absolute veto was not running in six of nine projects.** `ceremony_tier`'s critical-surface
check was written `if rows and overlaps(...)`. `scope_check.load_map` returns a falsy value both for
a repo with no map and for a map that declares nothing — so the veto silently did not run. Six of
the nine repos under `Projects/` carry no map. Meanwhile Step 1 of the *same command* falls back to
a generic surface list and correctly says OVERLAP. One command, two opposite answers about one auth
file. Found by the Edge Case Hunter lens, not by 46 passing assertions.

**No real Next.js route handler could ever be an entry point.** The exclusion was a fixed-depth glob
list, and `PurePosixPath.match` pins exact segment counts — so `app/api/chat/route.ts`, an API
endpoint, scored `tiny`, meaning "the plan is two sentences". Same lens.

**Two of my own pins were vacuous.** This is the finding I would most want you to see, because it is
the one a test suite structurally cannot report. The law-guard assertion used files matching no
declared glob, so it passed with the guard deleted. Eight hours later I wrote the *same bug again*:
the served-folder assertion used `frontend/public/`, which matches neither default glob, so it never
reached the guard it claimed to test. Only mutation testing — deliberately breaking the code and
checking the suite notices — found either.

**Nothing tested the predicate at one of its four callers.** `ship_preflight` could have bypassed the
carve-out entirely and every test still passed, because every case used either a real source file or
a path outside the product dirs, and both route identically with the carve-out gone.

The pattern across all four: **a test that has never been seen to fail is not evidence.** The house
already says this for new features (RED first). It does not say it for guards added to existing
functions, and that is exactly where all four hid.

## What cost time, and why

**I reported a stale CI failure for about an hour.** I told you the PR was red on the close-out
receipt. That had been true, and I repeated it without re-reading. When I finally read the log, a
different failure had appeared — `test_repo_template.py`, a race where git's own auto-maintenance
creates and deletes a lock file while a fixture walks the repo. Diagnosing it, re-running to prove
it was a flake, and writing up the one-line remedy was maybe twenty minutes. Believing my own
earlier summary is what cost the hour.

**I did not know the mechanism for the thing that was blocking us.** The real blocker was never the
receipt — it was that SCC-451 had two open subtasks, and the gate refuses to close a parent while
children are open. My first instinct was to re-parent SCC-452 out from under it, which would have
dismantled the guard you deliberately built. The correct answer, `landing_mode: partial`, was
already in `work-consolidation.md` and already implemented in `task_preflight.py`. Forty minutes
lost to not knowing the house's own law.

**Three command-shape violations, all mine, all the same class** — a piped gate, an `; echo EXIT=$?`
tail, and a heredoc. The hook caught each. The heredoc was refused before running; the other two ran
and were flagged after, which means for those two the exit code I read could have been a lie.

**The review's second lens never finished.** An interrupt killed it four minutes into its second
batch, so 30 of 45 mutants never ran. I recovered batch A's results from its transcript rather than
from a report it filed. The verdict is CONCERNS for that reason and no other.

## What is worth changing

**One rule, not a project.** Extend the RED-first requirement to guards: *an assertion about a guard
must use input the guard's own predicate admits, or it is testing nothing.* Both vacuous pins would
have been caught at write time by asking one question — "what does this assert if I delete the guard?"

**Mutation testing earned its place on gate code.** It found five things 87 assertions missed, two of
which were the assertions themselves. It does not belong on every lane, but on the files that decide
whether other lanes may ship, it paid for itself in one run.

**The missing model-switch gate is already minted as SCC-454.** There is no stop before the code
review on either lane, so you cannot change agents at the point where that choice matters most.

## Open, with owners

- **SCC-452** — step two, the reach score. Carries the 30 unrun mutants; the harness that generates
  them is saved at `scratchpad/saved-mutants/mutation_harness_45.py` and should ride that lane.
- **SCC-453** — the toolchain manifest. Mis-parented under SCC-451; your call whether it moves.
- **`test_repo_template.py`** — the git-maintenance race. Remedy: `git config gc.auto 0
  maintenance.auto false` in the fixture's `git init`. Not fixed here; outside this lane's subject.
- **`chore/SCC-451-inert-paths`** — merged, still on the remote, left undeleted.

## Your Actions

Nothing. Every item under "Open, with owners" above was settled on 2026-09-12 by the SCC-451
close-out; this section records the disposition so `jira_feed.py finish` reads a decided answer
rather than an absent one.

- [x] **SCC-452 — the reach score.** Built, reviewed and merged at `efd79fa4` (PR #219). Done on the
      board with its Dev Record. The saved mutant harness rode that lane: 8/8 killed, including one
      of the lane's own pins caught vacuous and rewritten.
- [x] **SCC-453 — the toolchain manifest.** Moved to **SCC-455** under Epic SCC-33, where CI/CD
      plumbing belongs. Jira refuses a subtask-to-task conversion through any API and a subtask
      cannot hang off an Epic, so the key changed; SCC-453 is closed as superseded, labelled
      `descoped`, linked `Duplicate`, and its description carried across verbatim.
- [x] **`test_repo_template.py` — the git-maintenance race.** Fixed, not deferred. `stat()` moved
      inside the `OSError` guard in `leaks()`, and `build_repo` now sets `gc.auto=0` and
      `maintenance.auto=false`. Pinned by T6 and T7; mutants restoring each half both killed;
      53/53 green.
- [x] **`chore/SCC-451-inert-paths` — the undeleted remote branch.** Deleted, local and remote,
      alongside `chore/SCC-451-reach-score`. Both proven `0` commits off `origin/main` first, and
      both the `git branch --list` and `git ls-remote` checks come back empty.
