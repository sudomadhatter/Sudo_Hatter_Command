# SCC-418 — the suite passes in ONE sandboxed run

**Ticket:** SCC-418 (Subtask of SCC-411, the 2026-09 rolling ticket)
**Lane:** `chore/SCC-418-suite-passes-in-one-sandbox-run`, cut from `origin/main` at `06ba80e7`
**Plan:** [implementation_plan.md](implementation_plan.md) · **Mutants:** [mutants.json](mutants.json)
**Date:** 2026-09-05

## What this closes, in one paragraph

Two checks in the test suite were reporting FAIL for reasons that had nothing to do with the code
they exist to protect, and a FAIL on a machine you trust is answered by running the whole gate again
somewhere else. That is the "we run it every time, then run it again outside" cost. Both are now
fixed at the source rather than worked around: the live-surface scan no longer reads other people's
checkouts, and case K's worktree fixture reports a loud `[SKIP]` when the machine refuses to host
it instead of failing on its own scaffolding. Neither gate was weakened — each fix ships with a
control case that fails if the exclusion ever grows to cover a real defect, and all six mutants
were killed by their declared cases.

## The correction that came first

The plan's first draft claimed the suite fails inside the sandbox systematically, on every lane run.
The self-audit falsified both of its central claims from this repo's own output and returned
**NO-GO**. The wrong-tree guard at `run_all.py:213` refuses a lobby run while a lane worktree is
checked out, which made the draft's acceptance row A unrunnable as written; and SCC-417's lane run
was `79/79` in-sandbox with its worktree registered, which falsified the draft's trigger for cause 2.
The plan was rewritten to the reproducible scope and both corrections are baked into its text.

**Then the RED went the other way and widened it again.** Measured from the lobby with a throwaway
agent worktree present, `CS-22 B` named **two** offenders, not one:

```
[FAIL] CS-22 B no LIVE file names the retired /smh-slash-command-updating: 2 live file(s) still
name it: ['.claude/worktrees/agent-scc418redprobe/.agents/scripts/tests/test_command_surfaces.py',
 '.claude/worktrees/scc-418-suite-passes-in-one-sandbox-run/.agents/scripts/tests/test_command_surfaces.py']
-- 316/317 passed --
```

The second is a **lane** worktree. The guard does refuse a bare lobby run — but it prints `--on-main`
as its own documented override, and the moment you take that route it re-admits the very checkout it
was protecting. So the trigger is not a rare leftover: it is any worktree plus the escape hatch the
tool itself recommends.

## Cause 1 — the live-surface scan walked other checkouts

`CS-22 B` proves no LIVE file still names a retired command. `.claude` is walked whole and
deliberately so (`.claude/rules/` is a live generated mirror beside it), and `.claude/worktrees/`
sits underneath. Every lane and every throwaway agent tree is therefore a full second copy of the
repo inside the scan — including a copy of `test_command_surfaces.py`, whose own `RETIRED` tuple
names the retired command as its subject. The check went red on a sibling's files and green only on
the days nobody else had a tree open. The sibling sweep in the same file already excluded them
(`SWEEP_SKIP = {"worktrees", …}`, `:1740`); `CS-22 B` was the one scan that did not.

**The trap inside the fix, which is why the change is two lines and not one.** `SKIP` was matched
against `f.as_posix()` — the **absolute** path. A lane checkout lives at
`<root>/.claude/worktrees/<lane>/`, so adding the marker alone would have skipped **every file of a
lane run** and reported a vacuous clean scan of nothing, from inside the very tree it was asked to
check. The match is now normalised to the path *relative to* `ROOT`, which makes the marker mean the
only thing it should ever mean: another checkout nested under this one. Mutant `M3` is exactly this
edit, and `CS-22 B-SKIP` kills it.

## Cause 2 — the fixture, when the environment will not host it

Case K builds a real `git worktree` to prove `check_maps.py --depth3-only --strict` does not
false-block from a lane. The add must create `<repo>/.git/worktrees/<name>`, and that directory is
left unwritable inside the sandbox after a worktree is removed mid-session:

```
[FAIL] K worktree fixture could be created: Preparing worktree (detached HEAD 06ba80e7)
fatal: could not create directory of '.git/worktrees/lane-probe': Read-only file system
```

The file already had the right answer for a machine that cannot host the fixture — it skips and says
why on Windows — but that arm keys on `os.name`, and this is not the OS. `env_refuses_worktree()`
now classifies the refusal. It is narrow on **both** axes: the message must name `.git/worktrees`
**and** carry one of `read-only file system`, `device or resource busy`, `permission denied`. A bad
ref, an existing worktree, or a read-only path anywhere else still FAILS.

**The live state is intermittent, so it was not left to weather.** Removing a worktree mid-session
reproduced the busy-admin-directory error but not the read-only one on this attempt, so the branch
was proven directly with a positive control that forces the verbatim measured stderr:

```
BASELINE (fixture hosts normally)      exit=0  -- 37/37 passed --
FORCED environment refusal             exit=0  -- 33/33 passed --
  [SKIP] K worktree fixture - the environment refuses it: Preparing worktree (detached HEAD 06ba80e7)
restore verified byte-identical: True
```

Exactly K's four real assertions drop out, one loud line is printed, no FAIL row is added, and the
file still exits green. CI is unsandboxed, so there the fixture is always built for real.

## Evidence

| What | Result |
|---|---|
| RED, `CS-22 B`, lobby `--on-main`, agent worktree present | `316/317` — two offenders, both worktree copies |
| RED, `CS-22 B-SKIP` before the fix | `FAILED: CS-22 B-SKIP` (`318/319`) |
| GREEN, `test_command_surfaces.py` from the lane | `319/319`, `CS-22 B0` still scanning 1727 files |
| GREEN, same, with an agent worktree nested under the lane root | `319/319` — the operator's failure shape, fixed |
| GREEN, `test_check_maps.py` | `37/37`, K's four real assertions still run |
| `[SKIP]` branch, forced verbatim stderr | `33/33`, one `[SKIP]`, zero FAIL rows, exit 0 |
| Mutants | **6/6 killed, each by its declared case** |
| **Full suite, from the lane, IN the sandbox, one run** | **`79/79` files passed** |

## Mutation sweep

Declared before the sweep, code-derived, run sequentially, restored in a `finally`, residue checked
afterwards. Full table in [mutants.json](mutants.json).

| # | Mutant | File | Declared killer | Outcome |
|---|---|---|---|---|
| M1 | drop the worktrees marker from `SKIP` | `test_command_surfaces.py` | `CS-22 B-SKIP` | KILLED |
| M2 | widen the skip to every path | `test_command_surfaces.py` | `CS-22 B-SKIP CONTROL` | KILLED |
| M3 | match the ABSOLUTE path, not the relative one | `test_command_surfaces.py` | `CS-22 B-SKIP` | KILLED |
| M4 | drop the `.git/worktrees` clause | `test_check_maps.py` | `K-ENV CONTROL` | KILLED |
| M5 | drop the errno clause | `test_check_maps.py` | `K-ENV CONTROL` | KILLED |
| M6 | invert the classifier | `test_check_maps.py` | `K-ENV` | KILLED |

M4 and M5 are the **narrowing** mutants: each drops one arm of a two-clause AND, and each is caught
by a control string exercising exactly the arm that was dropped — one naming the admin directory
with a git errno (`File exists`), one carrying our errno on a different path (`/tmp/x`). Without
both, the two clauses would be certified only jointly, which is the boundary a real regression walks
through.

## SOP currency

One aside added beside the wrong-tree-guard passage in
[workflows_testing_SOP.md](../../../docs/_scc_sops_prds/workflows_testing_SOP.md), naming both
expected `[SKIP]` shapes and stating plainly that neither is a reason to re-run the suite elsewhere,
plus one row in
[workflows_testing_SOP_changelog.md](../../../docs/_scc_sops_prds/workflows_testing_SOP_changelog.md),
same commit. The armed gate does not demand this — `sop_currency.py` exempts
`.agents/scripts/tests/` — so the edit is owed by the house rule, not by the hook.

## What this deliberately does NOT do

It does not widen the sandbox: a read-only bind mount is not reachable from the writable-path list
in `claude_permissions_apply.py`, and a fix needing a settings push per machine is not a fix. It
does not touch product code — both defects were in test files. And it does not claim to be the whole
of the "run it twice" experience: `git worktree remove` still leaves a busy admin stub that only
`git worktree prune` outside the sandbox clears, which happened once during this lane's own cleanup.
That is worktree plumbing rather than the test suite, it is already recorded in the
sandbox-mountpoints memory as the standing remedy, and it is named here so the boundary of this
lane's claim is explicit.
