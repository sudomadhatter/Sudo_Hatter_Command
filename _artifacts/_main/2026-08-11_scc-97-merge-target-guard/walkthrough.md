---
IsArtifact: true
ArtifactMetadata:
  title: SCC-97 — nothing guards the merge target
  type: walkthrough
  date: 2026-08-11
---

# Walkthrough — SCC-97

**Branch:** `chore/SCC-97-merge-target-guard` · **Lane:** LOCAL

## The gap

Every git guard in this toolkit protects the branch you merge **from** — `--expect-key`, the
preflight header line, pinning `$REPO`, and `worktree-per-story`'s *"cwd is not intent"*, which is
written about which tree you **review** and which diff counts as evidence.

**Nothing looks at the branch you merge onto.**

On 2026-08-11, during the seven-lane landing, `cd <worktree> && git checkout main` ran in one tool
call and a **bare `git merge <lane>`** ran in a later one. The working directory had reset to the
shared checkout, which was standing on `chore/SCC-89-migrations-to-docs`. The merge landed a
production merge commit **on that sibling lane's branch** and reported success.

**It is invisible by construction.** The merge output, the changed-file list, and the commit message
all read correctly — the message says `-> main` because that is what was typed. It surfaced only by
running `git rev-parse --abbrev-ref HEAD` afterwards and not recognising the answer.

This is not a report about someone else's incident. It happened in this session, to this procedure,
in the same hour the procedure was being written down.

## What landed

1. **The memory** — `_artifacts/_memory/nothing-guards-the-merge-target.md`, indexed under the git
   section of `MEMORY.md`. It carries the failure, **why the existing rules did not cover it**, the
   mechanical guard, and the recovery. It cross-links `preflight-resolves-repo-from-cwd` (the same
   disease aimed at the *report* rather than the merge) and `one-shot-permission-persists-in-context`
   (the other way a merge goes wrong: right branch, unauthorised) rather than restating them.
2. **The rule** — `.agents/rules/git-policy.md` §Safe-commit mechanics gains a ⛔ block: `-C` on every
   call, the pre-merge assertion, and the recovery. *The memory explains; the rule binds.*

## The recovery, recorded because it is not obvious

**Do not reset and do not force.** The wrongly-placed merge commit is usually correct in every way
except which pointer moved:

```bash
git diff --name-only <main-tip> <sha>     # tree carries nothing from the wrong branch
git log -1 --format='%p' <sha>            # first parent IS main's tip
git -C <tree-holding-main> merge --ff-only <sha>
```

That puts it exactly where it belonged. The sibling branch keeps its uncommitted work untouched —
which is what makes this recoverable at all, and why reaching for `reset --hard` would have been the
expensive mistake. This is the sequence that was actually used.

## Evidence

```
python3 .agents/scripts/tests/test_memory_store.py     -> exit 0   46/46 passed
   index 22,786 B — 89% of the 25 KB cap, below the 90% audit trigger
python3 .agents/scripts/tests/run_all.py               -> exit 0   13/13 files passed
python3 .agents/scripts/workflow_lint.py --toolkit-only-> exit 0   0 errors, 0 warnings
```

All bare. **Note the memory index sits at 89%** — one point under the trigger. The next memory
written will raise `MEMORY AUDIT DUE`, and that is the designed behaviour, not a problem to pre-empt.

Verdict: PASS @ (this commit)
