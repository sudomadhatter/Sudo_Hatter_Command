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
control case that fails if the exclusion ever grows to cover a real defect, and all **eleven**
mutants were killed by their declared cases, five of them narrowings the review added after proving
they survived the first sweep.

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
why on Windows — but that arm keys on `os.name`, and this is not the OS. `classify_add()` now
classifies the refusal, returning `run`, `skip` or `fail`. The `skip` arm is narrow on **both** axes:
the message must name `.git/worktrees` **and** carry one of `read-only file system`,
`device or resource busy`, `permission denied`. A bad ref, an existing worktree, a sibling
`.claude/worktrees` path, or a read-only path anywhere else still FAILS.

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

## Your Actions

- [x] The merge itself — lands via this branch's PR

Nothing else is owed. Every review finding was fixed in this lane or dismissed with its reason
recorded in the findings table; no finding produced a ticket, and nothing was deferred.

## Code Review (2026-09-06)

Verdict: PASS @ fbc0cf9e

Suite evidence measured at `fbc0cf9e36b7d70ff552b38f13fd2ce733474f9e` — the shipping SHA, after the
last code and test change. `run_all.py` in-sandbox from the lane: **79/79 files passed**, one run.

review-runtime: fan-out
lens_isolation:  worktree
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
findings:        0 decision · 19 patch · 0 defer   (2 noise-dismissed · 2 relevance kills)
dispositions:    per-lens: blind-hunter=4/1/1 · edge-case-hunter=1/1/1 · literal-correctness-hunter=2/0/0 · acceptance-auditor=7/0/0 · test-adequacy-auditor=5/0/0
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — `declared_change_set.py diff` returns all three empty against the plan's block at the shipping SHA; the block itself was amended mid-build and every amendment is recorded in the plan's Steps 2, 3 and 5 rather than left to this file
severity_floor:  none

**Scope.** The committed `origin/main...HEAD` diff: two test files, the SOP and its changelog, plus
this lane's artefacts. Nothing uncommitted.
**Method.** Five lenses, each in its own clean context; the four repo-reading lenses each in their
own isolated worktree copy of this repo at `9ca611ec`, the Blind Hunter with no repo access at all.
Findings fixed in thread, then the whole floor re-run at the shipping SHA.

**Changes applied: substantial.** The review did not rubber-stamp this lane. Three lenses
independently found that the `[SKIP]` decision was **split** between a predicate and the `if` that
consumed it, leaving the branch itself uncertified; the decision was restructured into one pure
`classify_add()` so a named case can reach all three arms. Five **narrowing** mutants were then
proven to survive the original sweep, and the sweep was re-declared at eleven and re-run.

### Findings

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `test_check_maps.py:318` (as shipped at 9ca611ec) | important | The decision was `if add.returncode != 0 and env_refuses_worktree(...)`. Widening it to `if add.returncode != 0:` excuses **every** git rejection — bad ref, existing worktree — while `K-ENV` and `K-ENV CONTROL` both stay green, because they only ever call the predicate. Undetectable on any machine where the fixture hosts, which includes CI. | applied @ fbc0cf9e — whole decision moved into `classify_add(returncode, stderr) -> run\|skip\|fail`; `K-ENV CONTROL` now pins the success arm (mutant M11, previously unreachable) |
| 2 | `test_check_maps.py:60-62` | important | `permission denied` was the one errno of three with no positive fixture. Dropping it from the tuple leaves both cases green while an EACCES machine silently returns to failing on its own scaffolding — the exact false red this lane removes. A lens reproduced `chmod 0500` on `.git/worktrees` against git 2.43 and got that errno **verbatim**, so the untested member was the most reproducible refusal of the three. | applied @ fbc0cf9e — third positive string added; mutant M9 |
| 3 | `test_command_surfaces.py` `CS-22 B-SKIP CONTROL` | important | The control pinned 3 of the 6 `LIVE_DIRS`. Adding `/.opencode/` to `SKIP` leaves the control green, `B` green, and `B0`'s anti-vacuity floor unmoved (1723 → 1650 against a threshold of 200) — silently retiring the surface whose own comment records a **measured** real offender at `.opencode/commands/smh-sync-agents.md:85`. `/.roo/` and `/_bmad/` behave the same. | applied @ fbc0cf9e — one literal per live root, routed through the real `is_skipped(scan_path(...))` composition; mutant M7 |
| 4 | `test_check_maps.py:57` / `test_command_surfaces.py` `SKIP` | important | Both path clauses survived **narrowing**: loosening `.git/worktrees` (or the SKIP marker) to a bare `worktrees` left every case green, while the loosened classifier then excuses a read-only refusal of a **lane checkout** directory — which the control's own failure message declares must still fail. | applied @ fbc0cf9e — boundary negatives added on both sides; mutants M8 and M10 |
| 5 | `test_check_maps.py:335` | suggestion | `add.stderr.strip()[:200]` trims only the ends, and git's message is two lines, so one `print()` emitted a bare unattached `fatal:` line between two PASS rows — in the branch whose entire purpose is that the operator can tell "K did not run" from "K failed" at a glance. Reproduced. | applied @ fbc0cf9e — whitespace-collapsed with `" ".join(stderr.split())` on both the skip and fail arms |
| 6 | `test_check_maps.py` `K-ENV` | suggestion | git has a **second** phrasing: when `.git/worktrees` does not exist yet — the first worktree in a repo, which is when its parent is most likely unwritable — git 2.43 says `could not create leading directories of`. Reproduced against real git. The classifier survives it only because it keys on path + errno and never on the phrase; the obvious future tightening to a phrase match would pass both cases while re-breaking the refusal. | applied @ fbc0cf9e — the measured string added as a fixture |
| 7 | `implementation_plan.md` acceptance row E | important | Row E asserted `32/32`. The file reports `37/37`, and it was never `32` on either side of the change (34 `c.check` sites before, 36 after). A reader executing row E as written must score it FAILED. | applied @ fbc0cf9e — row corrected, with the arithmetic stated |
| 8 | `implementation_plan.md` acceptance row A | important | Row A's proving command is `run_all.py --on-main` **from the lobby**, and every green in the record was a lane run. The lobby form is not runnable before the merge at all — the lobby checkout carries `main`'s copy of the test file, so it measures the unfixed code by construction. | applied @ fbc0cf9e — row restated against the command that actually proves it, with the lobby form named explicitly as the post-merge check rather than quietly scored as passed |
| 9 | `implementation_plan.md` Steps 2/5 + Declared Change Set | important | The plan declared five mutants against six shipped, and its change-set line said "SKIP gains the worktrees marker" while the diff also introduced `scan_path()`/`is_skipped()` and changed **what the loop matches against**. The approved text and the shipped work had diverged with nothing recording it. | applied @ fbc0cf9e — three `⚠️ AMENDED DURING THE BUILD` blocks record exactly where the work grew past the approved scope |
| 10 | `mutants.json` `width_note` | important | The record claimed M4/M5 were the narrowing mutants the rule asks for. Deleting one arm of a two-clause AND makes the predicate accept **more** strings — a widening. No mutant in pass 1 was a narrowing, and the surviving five prove it. | applied @ fbc0cf9e — corrected, and pass 1 is preserved in the JSON with why it was not enough |
| 11 | `implementation_plan.md` `## Approval` | important | The section still read "(awaiting the operator's literal `approved`)" in the same commit that landed the code. A later reader cannot tell an unapproved lane from an approved one whose stamp was never written. | applied @ fbc0cf9e — approval stamped with its date and scope |
| 12 | `workflows_testing_SOP.md:2511` | suggestion | The passage promised "Two `[SKIP]` shapes" and then said one of them prints nothing, sending an operator hunting for a second `[SKIP]` line the suite never emits. | applied @ fbc0cf9e — reframed as two false failures, one announced and one silent; "does not walk" also corrected to "no longer reads", which is what a result filter actually does |
| 13 | `test_check_maps.py:257` | nitpick | The pre-existing `⚠ POSIX only` comment had been pushed ~25 lines from the `if os.name != "nt"` it describes, with two unrelated cases wedged between. | applied @ fbc0cf9e — the two new cases moved above the whole K preamble, which also puts them where their own "these run on every OS" note belongs |
| 14 | `test_command_surfaces.py` B's loop | suggestion | The skip is a **result filter**, not a walk prune: `rglob` enters every worktree before `is_skipped` rejects it (measured from the lobby: 27,770 entries enumerated, 10,185 discarded). Two siblings prune instead, and `test_sops_prds_folder.py` carries a comment recording that a result filter over `ROOT.rglob` once crashed that file on Windows with WinError 3. | **dismissed** — correctness is identical, and the crash is not reachable today: deepest measured path is 187 chars (~221 on Windows against MAX_PATH 260). Its own lens rated it `suggestion` at confidence 0.65. Refactoring a green, mutation-certified loop for a latent cost fails question 2 of `code-standards` §6.5. Recorded in the code instead, with the house prune pattern named for whoever next touches that loop |
| 15 | K's `finally` teardown; other K skip arms | nitpick | Two prunable `lane-probe` phantoms and empty admin stubs survive K's deliberately repo-safe teardown; and the Windows and `.git`-absent arms of K skip silently while the new arm is loud. | **relevance-killed** — both are pre-existing and outside this diff; the teardown and those two arms are untouched by this lane. The phantoms this session created were pruned |

### Gates

- **Enforcement suite** — `python3 .agents/scripts/tests/run_all.py` from the lane, in-sandbox: `79/79 files passed`, exit 0, at `fbc0cf9e`.
- **Toolkit lint** — `workflow_lint.py --toolkit-only`: `-- 0 error(s), 0 warning(s), 8 info --`. The 8 info rows are pre-existing UTF-8 BOM notices on `testarch-*` commands, untouched here.
- **Assertion evidence** — the named cases, re-run green: `test_command_surfaces.py --case "CS-22"` → `17/17`; `test_check_maps.py --case "K"` → `37/37`, with K's four real assertions running.
- **Mutation** — 11 declared, **11 killed** by their declared cases, restore verified byte-identical against the pre-sweep `sha256` of both files.
- **SOP currency** — `sop_currency.py --paths <changed>`: clean, exit 0. The armed gate exempts `.agents/scripts/tests/`, so the SOP edit is owed by the house rule and not by the hook; it is in the same commit either way.
- **Link + anchor** — `check_links.py --base origin/main`: `clean` in-sandbox. Re-run **outside** the sandbox it reports 2 unresolved paths, both `.claude/settings.local.json` — pre-existing SCC-392 prose (2026-09-04) about a deliberately gitignored file. `git diff origin/main...HEAD -- docs/` contains **zero** occurrences of that path; only the line numbers moved under this lane's changelog row. Not introduced by this diff.
- **Door parity** — n/a: no command was added, renamed or deleted.
- **Declared change set** — `present: true`, `incomplete: []`, `undeclared: []`, `unimplemented: []`.

### Acceptance matrix

| Row | Proving assertion | Result |
|---|---|---|
| **A** | full suite from the lane, in-sandbox, with worktrees under the root | `79/79` @ `fbc0cf9e`. RED was `316/317`. ⚠️ The row's *lobby* form is not runnable pre-merge (the lobby carries `main`'s copy); named as the post-merge check |
| **B** | `CS-22 B` + `CS-22 B0` | `0 live file(s)`, `1727` files scanned against a `> 200` floor — including one run with four review-lens worktrees open, the bug's own condition arriving unstaged |
| **C** | `CS-22 B-SKIP CONTROL` | green, now one literal per live root through the real normaliser; mutants M2, M7, M8 |
| **D** | `K-ENV` + `K-ENV CONTROL` | green on all three errnos, both git phrasings, and all three arms of the decision; mutants M4, M5, M6, M9, M10, M11 |
| **E** | `test_check_maps.py` bare | `37/37`, K's four real assertions running |
| **F** | the SOP passage + one changelog row | both in the lane, same commit as the code |

### Clean-Code Gate

| Check | Result |
|---|---|
| `py_compile` on both changed files | OK |
| Banned patterns on added lines (`bare except`, unowned TODO/FIXME) | none |
| Comment contract (§1) | every new block carries its *why*; the one stale-adjacency case is finding 13, fixed |
| New abstraction with a single caller (§2) | `classify_add`, `scan_path`, `is_skipped` each have a second caller by construction — the named cases. That is the point of extracting them: a decision no case can call is the defect finding 1 records |
| Machine floor (`ruff`/`pyrefly`) | n/a — the lobby has no `backend/.venv`; `run_all.py` is this repo's floor and it is green |

### Step 0.7 — re-derivation

1. **Did anything this diff references move, rename or delete on `main`?** No. `git diff --name-only <merge-base>..origin/main` is **empty** — nothing landed on `main` since this lane was cut at `06ba80e7`, so no reference could have moved. Re-resolved anyway: every path and anchor this diff names resolves (`check_links.py` clean).
2. **True overlap and merge result.** Overlap is **empty**. `git merge-tree --write-tree --messages HEAD origin/main` wrote tree `59e0c5b6` with no conflict messages. No absorb was needed, so `HEAD` is unmoved and the verdict SHA is the tested one.
3. **Sibling lanes and landing order.** None. `git worktree list` shows only the lobby on `main` and this lane; the five review-lens worktrees were transient and are gone. No landing-order dependency.
