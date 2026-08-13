# Walkthrough — close-out gate defects (SCC-137 + subtasks 138/139/140)

**Branch:** `chore/SCC-137-close-out-gate-defects` · **Built:** 2026-08-13
**Build HEAD:** `a9b9655` · **Reviewed HEAD:** `2d9b4fe` (post-fix — the sha the verdict and the
suite evidence are measured on)
**Plan + self-audit:** [implementation_plan.md](implementation_plan.md) (`Audit verdict: GO`, 7 findings)
**Review verdict:** `PASS @ 2d9b4fe` — see [Code Review](#code-review-2026-08-13) below

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
| M10 dotfile filter removed *(review fix)* | 2 |
| M11 `is_soft` always False *(review fix)* | 3 |
| M12 `--strict`-alone refusal removed *(review fix)* | **0 on first pass — SURVIVED**, then 2 once case J2 existed |

**16 mutants, 16 killed** — but M12 is the one worth remembering: the `--strict`-alone refusal
shipped with **no assertion behind it**, and only the mutation sweep found that. A fix nobody
can break is a fix nobody proved. Case J2 closed it.

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

## Gate at reviewed HEAD (`2d9b4fe`)

```
run_all.py                              21/21 files · 1335/1335 cases · exit 0
workflow_lint.py --toolkit-only         0 errors, 0 warnings · exit 0
check_maps.py --depth3-only --strict    exit 0     <- the gate this lane added
hooks_armed.py --repo .                 ARMED, zero findings · exit 0
```

**Case total is exactly additive** at every step — 1281 (base) → 1293 → 1299 → 1318 → 1329
→ **1335** (the review's own regression cases: W2 ×3, J2 ×2, F2's ownership guard). No commit
displaced another's tests.

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

## Code Review (2026-08-13)

```
Verdict: PASS @ 2d9b4fe
```

Suite evidence measured on **`2d9b4fe`** — the post-fix tree. Every code and test change in
this lane is at or before that sha.

**Scope:** 13 files, `main...HEAD`. **Method:** independent read-only adversarial hunt (blind
to the plan until after the code), acceptance audit against the ticket ACCEPTANCE blocks, the
command-centre gate, and the clean-code gate.

### ⚠ Layer degradation — recorded, not buried

The first clean-room hunt **was killed mid-run and produced no findings.** It began
mutation-testing by editing the *real* working tree — it replaced `gate_plan()`'s
`check_maps` entry with `pass` and clobbered an in-progress edit. Two writers on one tree
destroys the evidence base a review rests on, so it was stopped, the tree restored to HEAD and
verified byte-identical, and the lens **re-launched read-only** with a scratch-copy rule. It
did **not** get the "retry once" the contract asks for first — retrying would have repeated
the tree corruption, and that is the deviation.

The relaunch completed cleanly and proved its own restraint: it returned
`git status --short` showing only the untracked `Projects/sudo-command-center/`, nothing
modified. So the layer **did** run blind; only the first attempt was lost.

### Findings — 12 raised, 11 applied, 1 dismissed

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `hooks_armed.py` `scan()` | **MED** | `Path(".gitignore").suffix` is `''`, so a `.gitignore`/`.gitattributes`/`.keep` tracked in `.githooks/` became a *required executable hook* → `armed=False`, close-out BLOCKED with `chmod +x .githooks/.gitignore`. The same false-red class the suffix filter was added to close, left half-closed. | **applied** — third filter; case W2 pins it, mutant M10 kills 2 |
| 2 | `hooks_armed.py` docstring | **MED** | Failure modes 4 and 5 are flag-keyed, so a **flagless** gate is invisible: drop `.githooks/pre-commit` while `pre-commit-encoding.sh` stays tracked → ARMED, zero findings. The docstring and SOP claimed coverage the code lacks. | **applied as a recorded gap** — not fixed; see *Known gap* below |
| 3 | `test_check_maps.py` F2 | **MED** | The live-tree probe's teardown was a bare `finally: probe.rmdir()`. If the dir already existed, `mkdir` raised **and the finally still ran**, deleting a pre-existing directory. Measured, not theorised. | **applied** — teardown guarded on "we created it" |
| 4 | `test_check_maps.py` K | LOW | Teardown ran a bare `git worktree prune` — repo-wide, deregistering any sibling lane whose directory is currently missing (a real state here) as a side effect of running the suite. | **applied** — `remove --force` only |
| 5 | `check_maps.py` `main()` | LOW | `--strict` without `--depth3-only` was silently accepted and ran the **full** linter — which from a worktree exits 1 on the two false positives whose remedy ships the lane name to `main`. | **applied** — `ap.error()`; case J2 |
| 6 | `hooks_armed.py` `check()`/`main()` | LOW | The comment claimed the downgrade came "from the same predicate"; it was written out twice. A comment the code does not do. | **applied** — extracted `is_soft()`, both call it |
| 7 | SOP `hooks_armed` row | LOW | Opened "**Five** ways … reports all five" then enumerated three. | **applied** |
| 8 | `hooks_armed.py` `resolve_hooks_dir` | LOW | One production caller; extracted for testability, and its test re-computes `expanduser()`. | **dismissed** — a `repo / configured` implementation fails case X, so it is not tautological; the extraction is what makes the `~` bug testable at all |
| 9 | `hooks_armed.py` docstring | CONCERNS | Said "THREE WAYS A GATE IS OFF" and described flags as TRACKED-only after the change made it index **and** disk. | **applied** |
| 10 | `.agents/scripts/INDEX.md` | CONCERNS | Said "Three things switch a gate off" and still described the exact flag behaviour this lane replaced. **The lane's own self-audit named this file and the build did not touch it** — the review caught what the audit predicted. | **applied** |
| 11 | `implementation_plan.md` | CONCERNS | Cited `hooks_armed.py#L176`; the fix it describes pushed that line to 269, so the anchor still **resolved** and pointed at unrelated code. A mis-pathed reference reads as correct — worse than a dead one. | **applied** — cited by function, no `#L` anchors remain |
| 12 | `test_check_maps.py` | LOW | An `import check_maps` this lane added was unused. | **applied** — removed |

### ⛔ Known gap, carried deliberately

`hooks_armed` still cannot see a **flagless** gate whose dispatcher is dropped from the index.
It is **not derivable**: `mint-push-token.sh` is a tracked `git-hooks/*.sh` that no dispatcher
references, so a rule of *"every gate script needs a referencing dispatcher"* would fire on a
correct repo — the same wall `ARM_FLAGS` documents. Closing it needs a **declared** dispatcher
table for flagless gates. Pre-existing (modes 4 and 5 did not exist at all before this lane),
so this is a coverage gap, not a regression — **worth its own ticket.**

### Gates — all bare, no pipes

| Gate | Result |
|---|---|
| Enforcement suite | `21/21 files passed` · **1335/1335 cases** · **exit 0** |
| `workflow_lint --toolkit-only` | `0 error(s), 0 warning(s), 8 info` · **exit 0** |
| `check_maps --depth3-only --strict` | **exit 0** (the gate this lane added, gating itself) |
| `hooks_armed --repo .` | **ARMED, zero findings, exit 0** |
| SOP currency | **exit 0** — with a **positive control at exit 1** on the same surfaces without the SOP, proving it armed |
| Link + anchor | 141 relative links, **0 dead**, and **no `#L` anchors remain** in the changed docs |
| `py_compile` | 6/6 changed `.py` |
| Door parity | **n-a** — no command added, renamed or deleted |
| lint / types | **not applicable to this repo** (no venv, no ruff, no tsc) |

**Case total additive throughout:** 1281 (base) → 1293 → 1299 → 1318 → 1329 → 1335.

**Both halves of the new gate, proven on the LIVE tree:** clean → `exit 0`; seed a rowless
session folder → `exit 1` naming it; remove it → `exit 0`.

**Regression sweep across every repo** — `main`'s `hooks_armed` vs the new one, all nine
`Projects/*` plus the lobby: **no repo newly blocked.** Five went `2 → 1`, which is decision C
relaxing exactly where intended (repos that never claimed gates now warn instead of blocking).

### Acceptance matrix

| Item | Proving assertion |
|---|---|
| SCC-137 #1 — gate runs check_maps, drift BLOCKS | `SCC-138 the printed gate includes check_maps` + `…with --strict`; live end-to-end 0 → 1 → 0 |
| SCC-137 #2 — rowless folder FAILS, red-first, dies mutated | `F2 …a rowless folder seeded into the LIVE tree IS reported`; mutant "missing-row reporting disabled" killed **5** across fixture → live → gate → worktree |
| SCC-137 #3 — SCAN_IGNORES dies mutated | `L` ×4; mutant "SCAN_IGNORES emptied" killed 2 **while both mirrors survived** |
| SCC-137 #4 — proven on the LIVE tree | `F2` runs against the real `_artifacts`; `K` against a real detached worktree |
| SCC-138 — gate_plan includes it / blocks / allows / worktree-safe | `SCC-138` ×3, `G`,`H`,`I`,`J`,`J2`,`K` ×4 |
| SCC-139 — MISSING half + SCAN_IGNORES | `F2` ×3, `L` ×4 |
| SCC-140 §1 flags disk+index (all three) | `R` ×6; mutant M2 killed 6 |
| SCC-140 §2 the `continue` (four shapes) | `S`,`T`,`U`,`V`; mutants M1 (3), M5 (1) |
| SCC-140 §3 pathspec | `W` ×4, `W2` ×3; mutants M3 (3), M10 (2) |
| SCC-140 §4 tilde | `X` ×3; mutant M4 (1) |
| SCC-140 §5 two-machine | `POSIX_ONLY` guard + `Z` ×4; mutant M9 (1) |
| SCC-140 §6 cascade + missing git | `Y` ×3, `AB` ×2; mutants M6 (2), M8 (1) |
| SCC-140 §7 dead branch deleted | Deleted; deliberately untested — pinning unreachable code buys nothing |
| SCC-140 A / B / C | comment only · case A machine-first + Q derives its key · `AA` ×2, mutants M7 (1), M11 (3) |

**Drift check (the other direction):** the only diff content beyond the acceptance list is the
`make_repo` fixture correction — required by §2's third shape, which reddened 15 preflight
cases the moment the check existed — and the lane's own artifacts. **No scope creep.**

**Mutation total: 16 mutants, 16 killed.** One survived on first pass (the `--strict`-alone
refusal shipped with no assertion); case J2 closed it.

### Step 0.7 — re-derivation against current `main`

1. **Nothing moved.** `origin/main` gained **0 files** during the build; every path and line
   citation the diff makes was re-resolved and all resolve.
2. **True overlap: none.** `merge-tree --write-tree` wrote a clean tree, no conflict messages.
   `main` is fully absorbed into HEAD.
3. **No sibling lanes.** One worktree, no other `chore/*` branch local or remote. **No
   landing-order dependency exists.**

### Clean-Code Gate — PASS

**Machine floor** — `run_all` PASS (21/21, 1335/1335, exit 0) · `workflow_lint` PASS (0 errors,
0 warnings) · `sop_currency` PASS (exit 0, positive control exit 1) · `py_compile` PASS (6/6) ·
link+anchor PASS (141, 0 dead) · door parity n-a · shell/PowerShell n-a (none in diff) ·
lint/types not applicable to this repo.

**Judgment pass** — comment-contract findings #6, #9, #10, #11 all **applied**. No committed
secret, no debug output, no commented-out code, no bare `except`, no hardcoded absolute path,
no bare `python` in anything typed. Step 2B imported from the hunt above (source `review`)
rather than re-walked. Conventions: naming law n-a, prefix-permission n-a, one-door n-a,
no generated file hand-edited, both-machines honoured (`POSIX_ONLY` guard + the `nt` monkeypatch),
gate ships **armed** and has an auditable exit (`--depth3-only` without `--strict`), artifacts
present in the tree.

**Changes applied during review:** findings 1–7 and 9–12, in two commits (`471035c`, `2d9b4fe`).

---

## What is NOT done

- ~~`/smh-code-review` has not run.~~ **Done** — `Verdict: PASS @ 2d9b4fe`, 12 findings, 11
  applied and 1 dismissed with a reason. The first hunt was killed and re-run read-only; that
  degradation is recorded in the section itself, not hidden.
- **A follow-on ticket is owed** for the known gap: `hooks_armed` cannot see a *flagless* gate
  whose dispatcher is dropped from the index. Not derivable — it needs a declared dispatcher
  table. Pre-existing, so not a regression, but it is now written down in the code and the SOP.
- **Close-out is the operator's.** The preflight currently **BLOCKS**, correctly, on two things:
  1. `SCC-137 has 3 open subtask(s)` — the parent closes LAST (SCC-119's mechanism, working).
     SCC-138, SCC-139 and SCC-140 each need their Dev Record and `Done` first.
  2. `1 uncommitted change` — `Projects/sudo-command-center/`, a **separate git repo** with its
     own `.git`, created 2026-08-13 10:05 and **not part of this lane**. Left untouched; it is
     the operator's to place.
