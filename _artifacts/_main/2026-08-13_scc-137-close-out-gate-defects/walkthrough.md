# Walkthrough — close-out gate defects (SCC-137 + subtasks 138/139/140)

**Branch:** `chore/SCC-137-close-out-gate-defects` · **Built:** 2026-08-13 · **Build HEAD:** `a9b9655`
**Plan + self-audit:** [implementation_plan.md](implementation_plan.md) (`Audit verdict: GO`, 7 findings)

---

## What was wrong, in one line each

The close-out gate lied in **two directions** and both lies reached `main`.

- **It printed GREEN while the linter was RED.** `gate_plan()` built the lane gate from
  `run_all` + `workflow_lint` only, so it could not fail on a linter it never ran. Twice in one
  day the two disagreed and only the linter was right.
- **It printed ARMED while the gates were off.** `hooks_armed` had **five** ways to do that —
  the tool whose entire job is not doing that.

---

## The commits

| SHA | Ticket | What |
|---|---|---|
| `1d31369` | SCC-137 | lane artifacts + the previous lane's carried doc changes |
| `509de15` | SCC-138 | `check_maps --depth3-only --strict` wired into `gate_plan()` |
| `e0b1e10` | SCC-139 | the live-tree MISSING half + `SCAN_IGNORES`' first coverage |
| `447540e` | SCC-140 | five false greens, two false reds |
| `a9b9655` | SCC-140 | the N+1 cascade, one verdict per state, the two-machine reds |

---

## Evidence

### Red first — every fix, before it existed

| Assertions | Red looked like |
|---|---|
| G/H/I/J (`--strict`) | `rc=2` — argparse rejecting an unknown flag |
| SCC-138 gate wiring | `check_maps.py` absent from the printed gate |
| R/S/T/U/V (`hooks_armed`) | **`errors=[]`** — the vacuous ARMED, reproduced exactly |
| W (pathspec) | `hooks=['README.md', 'commit-msg', 'helper.sh', …]` |
| Y (cascade) | 5 errors, 4 of them printing `(None)` |
| AA (CLI exit) · AB (missing git) | `rc=2` where `check()` warns · raw `FileNotFoundError` |

Two cases were **green-first by design** and say so: `SCAN_IGNORES` and the `nt` branch of
`is_executable` are characterization of behaviour that already worked. For those the mutation
*is* the evidence.

### Mutation — nine mutants, nine killed

| Mutant | Cases killed |
|---|---|
| M1 restore the bare `continue` | 3 |
| M2 flags read the index only | 6 |
| M3 pathspec stops filtering non-hooks | 3 |
| M4 no longer expands `~` | 1 |
| M5 zero gate scripts is fine again | 1 |
| M6 the N+1 cascade returns | 2 |
| M7 CLI drops `check()`'s downgrade | 1 |
| M8 missing git raises again | 1 |
| M9 the `nt` branch goes dead | 1 |
| *(check_maps)* `--strict` ignored | 1 |
| *(check_maps)* gate entry without `--strict` | 1 — and **only** the token assertion, proving the pin is on the wiring |
| *(check_maps)* `SCAN_IGNORES` emptied | 2 — **mirrors survived**, so it is not "everything fails" |
| *(check_maps)* missing-row reporting disabled | **5**, across fixture → live tree → gate → worktree |

Source verified **byte-for-byte identical** to its committed state after every sweep.

### The worktree proof (SCC-138 AC3, audit F2)

Run against a **real detached worktree**, because the false positives need the real repo map:

- bare `check_maps` there → **exit 1**, reporting `AUTO block is STALE` and
  `on disk but not in map: <lane>/` — a remedy that would write the lane name into the map
  bound for `main`.
- `--depth3-only --strict` → **neither false positive**.
- a seeded rowless folder → **still blocks**. The gate kept its teeth.

The test points the *working copy* at the worktree rather than running the worktree's own
script: `git worktree add` checks out **HEAD**, so the other way round the case goes green only
after the commit it exists to prove. POSIX-only — on Windows a pruned worktree leaves a shell
that blocks a later `add`.

---

## Gate at build HEAD

```
run_all.py                              21/21 files · 1329/1329 cases · exit 0
workflow_lint.py --toolkit-only         exit 0
check_maps.py --depth3-only --strict    exit 0     <- the gate this lane added
```

**Case total is exactly additive** at every step — 1281 (base) → 1293 → 1299 → 1318 → 1329. No
commit displaced another's tests.

### The lane graded its own homework — so it was checked twice

This branch rewrites `hooks_armed.py` and `task_preflight.py`, the scripts its own close-out
runs. `main`'s **entire** toolchain (`task_preflight` + `hooks_armed` + `wf_common` +
`jira_feed`, all at `main`) was exported and run against this branch:

| | branch copy | `main` copy |
|---|---|---|
| exit | 2 | 2 |
| errors | children open · 1 uncommitted | children open · 1 uncommitted |
| GATES | ARMED | ARMED |
| VERDICT | BLOCKED | BLOCKED |

**Identical.** The rewrite did not move the verdict. The only difference is that `main`'s copy
does not print the `check_maps` gate line, because it does not have it yet.

Live repo re-checked after the stricter rules: **ARMED, zero findings, exit 0** — the lane is
not self-blocked (audit F6).

---

## Deliberate departures from the plan, recorded

1. **The SOP path in the plan was wrong.** It named
   `_my_resources/_quick_reference/sudo_workflows_testing.md` — that is **AGY's** copy. The
   lobby's, and the one `sop_currency.py` enforces, is
   `docs/_scc_sops_prds/workflows_testing_SOP.md` (`SOP_DOC`, `sop_currency.py:60`). Corrected
   in the plan.
2. **`make_repo` had to change.** The preflight fixture declared a Jira project and shipped the
   dispatcher while tracking **zero** gate scripts — it was modelling the defect, and 15 cases
   went red the moment the check existed. That is the ticket's own prediction; the fixture now
   carries the inner script and the flag.
3. **The dead `NOT CLEAR` branch was deleted, not pinned.** An assertion over unreachable code
   buys nothing and makes a dead branch look load-bearing.
4. **Decision A: no code change**, one comment. It is not the deleted-vs-never-had question the
   index doctrine exists for, and over-claiming is the safe direction.

---

## What is NOT done

- **`/smh-code-review` has not run.** No review verdict exists yet, so this document carries
  none. Absence of a `Verdict:` line here means the step has not run — not that it passed.
- **Close-out is the operator's.** The preflight currently **BLOCKS**, correctly, on two things:
  1. `SCC-137 has 3 open subtask(s)` — the parent closes LAST (SCC-119's mechanism, working).
     SCC-138, SCC-139 and SCC-140 each need their Dev Record and `Done` first.
  2. `1 uncommitted change` — `Projects/sudo-command-center/`, a **separate git repo** with its
     own `.git`, created 2026-08-13 10:05 and **not part of this lane**. Left untouched; it is
     the operator's to place.
