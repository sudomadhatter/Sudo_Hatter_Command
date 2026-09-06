# SCC-418 — the two false suite failures that make a gate run happen twice

**Ticket:** SCC-418 (Subtask of SCC-411, the 2026-09 rolling ticket)
**Lane:** `chore/SCC-418-suite-passes-in-one-sandbox-run`, cut from `origin/main` at `06ba80e7`
**Date:** 2026-09-05

> ⚠️ **This plan is the SECOND draft.** The first draft claimed the suite fails inside the sandbox
> systematically, on every lane run. The self-audit falsified that from this repo's own output and
> returned **NO-GO**; the corrected measurements are below and the audit section records both
> passes. The scope is now only what is reproducible.

## 1. What is actually true, measured today at `06ba80e7`

The suite does **not** fail inside the sandbox on the normal path. Measured, this tree, today:

| Where it ran | Conditions | Result |
|---|---|---|
| the lane worktree, in-sandbox | SCC-417's lane, clean | `79/79` |
| the lobby, in-sandbox | a leftover **agent** worktree present | `78/79` — `test_command_surfaces.py` |
| the lobby, in-sandbox | right after a worktree was removed mid-session | `78/79` — `test_check_maps.py` |
| the lobby, sandbox off | same tree, nothing else changed | `79/79` |

So there are two real false failures, each with a narrow and provable trigger, and neither is "the
sandbox breaks the suite".

### Cause 1 — the live-surface scan walks other checkouts

`CS-22 B` proves no LIVE file still names a retired command. Its roots are
`LIVE_DIRS = (".agents", "docs", ".opencode", ".roo", ".claude", "_bmad")`
(`test_command_surfaces.py:3884`) and its exclusions are
`SKIP = ("/_artifacts/", "/node_modules/", "/doc-graph.json", "/doc-graph.md")` (`:3895`).

`.claude` is walked whole, deliberately, and `.claude/worktrees/` sits underneath it. Every
worktree therefore contributes a second copy of the whole repo to the scan, including
`test_command_surfaces.py`, whose own body names the retired command as its subject. Measured:

```
[FAIL] CS-22 B no LIVE file names the retired /smh-slash-command-updating: 1 live file(s) still
name it: ['.claude/worktrees/agent-a913cd47ccb0e512e/.agents/scripts/tests/test_command_surfaces.py']
```

It is an oversight rather than a decision: the sibling sweep in the same file already excludes them
— `SWEEP_SKIP = {"worktrees", "_artifacts", "_my_resources", "Projects", …}` (`:1740`).

⚠️ **AUDIT FINDING (baked in).** The first draft said this fires during all lane work. It does not:
`run_all.py:213` refuses a lobby run while a **lane** worktree is checked out (SCC-190), measured
verbatim as *"run_all: REFUSING - this is the MAIN checkout on `main`, but 1 lane worktree(s) are
checked out"*. The real trigger is an **agent** worktree — the throwaway trees review lenses open —
which does not trip that guard and is left behind when a lens is killed or a run is interrupted.
One was left behind in this very session.

**RED measured at this lane's tip**, lobby, in-sandbox, with a throwaway agent worktree present.
Note the offender list names **both** kinds of checkout, so `--on-main` (the documented override the
guard itself prints) re-admits the lane worktree the guard was protecting:

```
[PASS] CS-22 B0 the live-surface scan actually read files (anti-vacuity): only 6853 file(s) scanned
[FAIL] CS-22 B no LIVE file names the retired /smh-slash-command-updating: 2 live file(s) still
name it: ['.claude/worktrees/agent-scc418redprobe/.agents/scripts/tests/test_command_surfaces.py',
'.claude/worktrees/scc-418-suite-passes-in-one-sandbox-run/.agents/scripts/tests/test_command_surfaces.py']
-- 316/317 passed --
```

This widens the trigger the audit narrowed: an agent worktree fires it on a plain lobby run, and
**any** worktree fires it the moment the operator takes the `--on-main` route the guard advertises.
The fix is unchanged — the scan must not walk other checkouts — but acceptance row A is now stated
against that measurement rather than against the agent-worktree case alone.

### Cause 2 — the worktree fixture, when the environment will not host it

`K` builds a real `git worktree` to prove `check_maps.py --depth3-only --strict` does not
false-block from a lane. The add must create `<repo>/.git/worktrees/<name>`, and after a worktree
is removed mid-session inside the sandbox that directory is left unwritable, so the add dies and
the case reports **FAIL** on its own fixture:

```
[FAIL] K worktree fixture could be created: Preparing worktree (detached HEAD 06ba80e7)
fatal: could not create directory of '.git/worktrees/lane-probe': Read-only file system
```

The file already has the right answer for an environment that cannot host the fixture — it skips
the block on Windows and says why — but that arm keys on `os.name`, and this is not the OS.

⚠️ **AUDIT FINDING (baked in).** The first draft claimed the mount is read-only "whenever a
worktree is registered at sandbox start". Falsified: SCC-417's lane run was `79/79` in-sandbox with
its worktree registered, and case K passes from this lane right now. The observed trigger is
worktree **churn** during the session, which is exactly what a close-out's Step 5 does.

## 2. Acceptance — every row runnable as written

| # | Statement | The command that proves it |
|---|---|---|
| **A** | With both a lane worktree and a throwaway agent worktree present, `run_all.py --on-main` from the lobby in-sandbox is `79/79`; today it is `78/79`, `CS-22 B` naming **both** worktrees' copies (measured above) | `python3 .agents/scripts/tests/run_all.py --on-main` from the lobby |
| **B** | `CS-22 B` reports no offender under a worktree path, and `CS-22 B0` still scans > 200 files | `python3 .agents/scripts/tests/test_command_surfaces.py` |
| **C** | The gate is not blunted: a retired-command reference on a real live surface is still reported | new case `CS-22 B-SKIP CONTROL` |
| **D** | An `add` failure that is the environment refusing prints a visible `[SKIP]` and no FAIL row; any other `add` failure still FAILS | new cases `K-ENV` (the two verbatim stderr strings above) and `K-ENV CONTROL` (`fatal: invalid reference: HEAD`) |
| **E** | Nothing changes where the fixture works: `test_check_maps.py` still runs K's four real assertions and reports `32/32` | `python3 .agents/scripts/tests/test_check_maps.py` from the lane |
| **F** | The SOP records the two expected `[SKIP]` shapes so a skip is never read as a reason to re-run elsewhere, with a changelog row in the same commit | the SOP passage at `workflows_testing_SOP.md:2509` and one changelog row |

## 3. Steps, each naming its assertion

**Step 1 — RED, both causes, at this lane's tip.** Cause 1: create a throwaway agent-shaped
worktree, run the suite from the lobby with `--on-main`, paste the `CS-22 B` failure. Cause 2: the
two `K-ENV` cases are written first and fail, because the classifier does not exist. → A, B, D

**Step 2 — the live-surface scan skips other checkouts.** Add the worktrees marker to `SKIP` in
`test_command_surfaces.py`, with `CS-22 B-SKIP` and `CS-22 B-SKIP CONTROL` written before it. → B, C

**Step 3 — classify the fixture's refusal in `test_check_maps.py`.** A module-level helper returns
True only when the message names `.git/worktrees` **and** carries one of `read-only file system`,
`device or resource busy`, `permission denied`. On True the block prints
`[SKIP] K worktree fixture - the environment refuses it: <stderr>` and adds no rows; on False `K`
fails exactly as today. → D, E

**Step 4 — SOP currency.** One passage naming both expected `[SKIP]` shapes, one changelog row,
same commit. → F

⚠️ **AUDIT FINDING (baked in).** `sop_currency.py --paths .agents/scripts/tests/test_check_maps.py`
returns clean, so the armed gate does **not** demand this. The SOP edit is owed by the house rule
(a usage change), not by the gate; the plan must not claim a gate that will not fire.

**Step 5 — mutants.** Drop the worktrees marker (killed by `CS-22 B-SKIP`); widen the skip to every
path (killed by `CS-22 B-SKIP CONTROL`); drop the `.git/worktrees` clause from the classifier so any
failure is excused (killed by `K-ENV CONTROL`); drop the errno clause (killed by `K-ENV CONTROL`);
invert the classifier (killed by `K-ENV`). Each declared with the case that kills it.

## 4. What this deliberately does NOT do

- **It does not widen the sandbox.** A read-only bind mount is not reachable from the writable-path
  list in `claude_permissions_apply.py`, and a fix needing a settings push per machine is not a fix.
- **It does not weaken either gate.** Both skips are narrow and each carries a control case that
  fails if the skip ever grows to cover a real defect. CI is unsandboxed and runs K for real.
- **It does not touch product code.** Both defects are in test files.
- **It does not claim to be the whole of the operator's "run it twice" experience.** Two other
  commands needed the sandbox off in this session — `git worktree remove` and the `.git/config`
  write behind `git branch -d`. Those are separate and not in this lane's scope.

## Declared Change Set

- EDIT `.agents/scripts/tests/test_command_surfaces.py` — `SKIP` gains the worktrees marker; two new pinned cases → B, C
- EDIT `.agents/scripts/tests/test_check_maps.py` — an environment-refusal classifier, the `[SKIP]` arm, two new pinned cases → D, E
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the two expected `[SKIP]` shapes → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row, newest first → F
- NEW `_artifacts/_main/2026-09-05_scc-418-suite-passes-in-one-sandbox-run/mutants.json` — the five mutants above → A
- NEW `_artifacts/_main/2026-09-05_scc-418-suite-passes-in-one-sandbox-run/walkthrough.md` — the record → A
- EDIT `_artifacts/_main/INDEX.md` — the depth-3 row for this lane folder → A

## Self-Audit (2026-09-05)

**Level:** LEDGER+BLAST (the change set edits two scripts). **Mode:** pre-work. **Two passes.**

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every declared path exists on disk; every quoted anchor re-read at its line;
             declared_change_set.py parse -> 7 entries, "incomplete": [];
             lane fit (no deployable path -> /smh-close-task-merge-tree is the right door);
             Scope Ledger over the two NEW artefacts; the sop_currency claim executed
read:        .agents/scripts/tests/test_command_surfaces.py:1740,3884,3895 ·
             .agents/scripts/tests/test_check_maps.py:256-313 · .agents/scripts/tests/run_all.py:213 ·
             docs/_scc_sops_prds/workflows_testing_SOP.md:2509,2511 · _artifacts/_main/INDEX.md ·
             .agents/scripts/claude_permissions_apply.py:62 · run_all.py output, both trees
verdict:     findings below (pass 1) -> clean (pass 2, after the plan was rewritten)
```

```
lens:        2 Parity + Blast
checks_run:  copies of both test files in any other repo (find over Projects/) -> none;
             INDEX rows / .githooks callers naming either file -> none;
             sibling worktrees after `git fetch origin main` -> one (this lane), no shared paths;
             risk_seam.py classify -> {"status": "unclassified", "root": "."}, as expected here;
             SOP + changelog in the same commit is already Step 4
read:        Projects/ (9 repos) · .agents/scripts/INDEX.md · .githooks/ · git worktree list
verdict:     clean
```

```
lens:        3 Pre-Mortem
checks_run:  attached failure narratives to the two anchored findings below
read:        the findings from lens 1
verdict:     clean (no unattached output)
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/tests/run_all.py:213` | `worktrees exist (SCC-190: the wrong-tree guard)`, and at run time *"run_all: REFUSING - this is the MAIN checkout on `main`, but 1 lane worktree(s) are checked out"* | Draft 1's acceptance row A could never be executed, and its cause-1 frequency claim was false. **Silent-failure narrative:** the row would have been recorded as proven by a command that refuses to run, so the lane would have shipped with an untested acceptance row | blocker |
| measured: SCC-417's lane run at `00a19197`, in-sandbox, worktree registered | `79/79 files passed` | Draft 1's cause-2 trigger was wrong, so the skip would have been written for a condition that does not occur. **Other-machine narrative:** a skip keyed on the wrong condition either never fires where it is needed or fires where the fixture would have worked, hiding a real regression on a machine nobody re-checks | blocker |
| `sop_currency.py --paths .agents/scripts/tests/test_check_maps.py` | (no output — clean) | Draft 1 cited an armed gate that does not fire for these paths; the SOP edit is owed by the house rule instead | minor |

### Observations (uncounted)

- The lane's own suite run currently fails `test_check_maps.py` F2 for a missing `_artifacts/_main/INDEX.md` row for this folder. Ordinary lane hygiene, in the change set already, not a sandbox effect.
- No copy of either test file exists under `Projects/`, so the port checklist has nothing to answer.
- No sibling lane shares a path with this change set, so there is no landing-order dependency.

```
Audit verdict: GO
```

*(Pass 1 returned `Audit verdict: NO-GO` on the two blockers above. The plan was rewritten to the
reproducible scope and both blockers are resolved in the text; this line is pass 2.)*

## Approval

(awaiting the operator's literal `approved`)
