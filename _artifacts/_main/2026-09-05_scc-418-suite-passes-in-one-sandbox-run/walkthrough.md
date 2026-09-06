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

**The decision lives in ONE pure function, and that is a review fix, not the first cut.** This
shipped first as a bare `env_refuses_worktree(stderr)` predicate that the call site combined with
`add.returncode != 0`. Three lenses independently proved the cost: widening that branch to
`if add.returncode != 0:` excuses every git rejection while both classifier cases stay green, on
any machine where the fixture hosts — which includes CI. A decision split across a predicate and an
`if` is a decision only half of which any case can reach. `classify_add(returncode, stderr)` now
returns `run`, `skip` or `fail`, the branch reads the verdict and does not re-decide, and all three
arms are pinned by name.

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
| GREEN, same, with **four** review-lens worktrees open under the root | `CS-22 B` reports `0 live file(s)` — the bug's own condition, live, not firing |
| GREEN, `test_check_maps.py` | `37/37`, K's four real assertions still run |
| `[SKIP]` branch, forced verbatim stderr *(hand-run probe, not a standing case)* | `33/33` — exactly K's four cases drop out, one `[SKIP]`, zero FAIL rows, exit 0 |
| Mutants, pass 2 | **11/11 killed, each by its declared case**, restore byte-identical |
| **Full suite, from the lane, IN the sandbox, one run** | **`79/79` files passed** |

⚠️ **What acceptance row A can and cannot claim before the merge.** The row's lobby form
(`run_all.py --on-main` from the lobby) is **not runnable on this lane**: the lobby checkout carries
`main`'s copy of the test file, so a lobby run measures the unfixed code by construction. The lane
rows above exercise the identical condition — a worktree nested under the workspace root carrying a
second copy of the tests — and the four-lens row is that condition arriving on its own rather than
being staged. The lobby form is the post-merge check, and it is named here rather than quietly
scored as passed.

## Mutation sweep

Declared before the sweep, code-derived, run sequentially, restored in a `finally`, restore verified
byte-identical against the pre-sweep `sha256` of both files. Full table in [mutants.json](mutants.json).

**The sweep ran twice, and pass 1 was not good enough.** Its six mutants were all existence
deletions or a polarity flip — every one killed, which read as certification. The review lenses then
proved that **five narrowings survive it**, and the rule's § WIDTH clause is exactly about that
shape. Pass 2 declares eleven and kills eleven.

| # | Kind | Mutant | File | Declared killer | Outcome |
|---|---|---|---|---|---|
| M1 | existence | drop the worktrees marker from `SKIP` | `test_command_surfaces.py` | `CS-22 B-SKIP` | KILLED |
| M2 | existence | widen the skip to every path | `test_command_surfaces.py` | `CS-22 B-SKIP CONTROL` | KILLED |
| M3 | existence | match the ABSOLUTE path, not the relative one | `test_command_surfaces.py` | `CS-22 B-SKIP` | KILLED |
| M4 | existence | delete the `.git/worktrees` clause | `test_check_maps.py` | `K-ENV CONTROL` | KILLED |
| M5 | existence | delete the errno clause | `test_check_maps.py` | `K-ENV CONTROL` | KILLED |
| M6 | polarity | invert the errno clause | `test_check_maps.py` | `K-ENV` | KILLED |
| **M7** | **narrowing** | widen `SKIP` by one live root (`/.opencode/`) | `test_command_surfaces.py` | `CS-22 B-SKIP CONTROL` | KILLED *(survived pass 1)* |
| **M8** | **narrowing** | loosen the marker to a bare `worktrees` | `test_command_surfaces.py` | `CS-22 B-SKIP CONTROL` | KILLED *(survived pass 1)* |
| **M9** | **narrowing** | drop ONE errno member (`permission denied`) | `test_check_maps.py` | `K-ENV` | KILLED *(survived pass 1)* |
| **M10** | **narrowing** | loosen the path needle to a bare `worktrees` | `test_check_maps.py` | `K-ENV CONTROL` | KILLED *(survived pass 1)* |
| **M11** | **narrowing** | the success arm returns `skip` instead of `run` | `test_check_maps.py` | `K-ENV CONTROL` | KILLED *(unreachable in pass 1)* |

Three of the five are worth stating plainly, because each is a real regression shape rather than a
theoretical one. **M7** widens the skip onto `.opencode` — the surface whose own comment records a
*measured* real offender — and `CS-22 B0`'s anti-vacuity floor cannot see it, because the scan count
only falls from 1723 to 1650 against a threshold of 200. **M9** drops the one errno member that a
lens reproduced live against git 2.43: `chmod 0500` on `.git/worktrees` yields verbatim
`Permission denied`, so the untested member was the *most* reproducible refusal of the three.
**M11** was not merely unkilled in pass 1, it was unreachable: while the decision was split between
a predicate and an `if` at the call site, no case could reach the success arm at all.

Pass 1's record also called M4 and M5 narrowings. That was wrong — deleting one arm of an AND makes
the predicate accept *more* strings, which is a widening — and it is corrected in the JSON.

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
