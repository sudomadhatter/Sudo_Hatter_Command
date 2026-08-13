# Implementation plan — close-out gate defects (SCC-137 + subtasks 136/138/139)

**Branch:** `chore/SCC-137-close-out-gate-defects`
**Close command:** `/smh-close-task-merge-tree --expect-key SCC-137`
**Written:** 2026-08-13

---

## 1. The ticket set, and why one branch

One Bug with three subtasks, **one branch, one worktree, one merge** — because this is one
job: **the close-out gate lies in two different directions and both lies reach `main`.**

| Key | Type | Role |
|---|---|---|
| SCC-137 | **Bug — the parent** | the gate reports GREEN while `check_maps` is RED |
| SCC-138 | Subtask | wire `check_maps` into `gate_plan()`, worktree-safe |
| SCC-139 | Subtask | the two untested halves of `check_maps`' own contract |
| SCC-140 | Subtask | `hooks_armed` / `task_preflight` — the gate reports ARMED when gates are off |

**SCC-136 was re-parented from `Bug` to `Subtask` under SCC-137 in the Jira UI, and the move
minted a NEW key: it is now SCC-140.** `acli` cannot perform the conversion — `workitem edit`
exposes `--type` but there is no `parent` field in its flags or in its `--generate-json`
schema. That is almost certainly why SCC-119 deleted its `Subtask→Bug` hierarchy-conversion
spike.

⚠️ **The move dropped the summary and the whole description** (the summary came out as the
literal string `SCC-136`, the body empty). Both were rewritten on SCC-140 to the **reduced
scope actually being built** — §2 below — rather than restoring the original defect dump.
`SCC-136` no longer resolves; every reference in this lane reads SCC-140.

The shape also satisfies SCC-119's ruling exactly: **breakage is recorded on the parent**
(SCC-137 is the Bug) and **no subtask carries the `Bug` label**.

**Why one branch and not three.** SCC-119's minting threshold is that *a piece earns a subtask
only when it earns its own branch AND worktree.* These three do not: SCC-138 is ~4 lines plus a
flag, SCC-139 is two assertions, SCC-140 is ~40 lines in one file. They keep their board rows
for visibility, but three worktrees and three close-outs for that much code is the ceremony
this repo keeps warning itself about. **Deviation recorded:** `/smh-close-task-merge-tree`
says a Subtask closes *"exactly like a Task: its own branch, its own gate, its own Done."*
Here the three share the parent's branch and gate; each still gets its own `Done`.

**Commit order is 138 → 139 → 136**, deliberately: SCC-138 makes the gate stricter, so the
larger SCC-140 change lands *under* the better gate, and this branch's own close-out is the
first thing to run the gate it just built.

---

## 2. Scope — the value line

The reward/risk cut, held deliberately lean. Two failure directions, and they are not
symmetric:

- **False green** — says ARMED / GREEN when it isn't. The close-out prints *"clear to close
  out and merge"* over unchecked commits. Total product failure; this is what we buy down.
- **False red** — blocks on a lie. Costs an hour, then costs the gate: a gate you route
  around is a gate you deleted.

### IN

| # | Item | Direction | Size |
|---|---|---|---|
| 1 | `check_maps` in `gate_plan()`, worktree-safe (SCC-138) | false green | ~6 lines |
| 2 | live-tree MISSING assertion + `SCAN_IGNORES` test (SCC-139) | false green | ~25 lines test |
| 3 | arm flags read **disk AND index**, all three (SCC-140 §1) | false green | ~4 lines |
| 4 | tracked flag whose script is untracked is reported, not skipped (SCC-140 §2) | false green | ~6 lines |
| 5 | `.githooks/` pathspec stops crossing slashes (SCC-140 §3) | false red | ~2 lines |
| 6 | `expanduser()` on `core.hooksPath` (SCC-140 §4) | false red | 1 line |
| 7 | `os.name` guards on test cases D, F, N (SCC-140 §5) | dead gate on the PC | 3 lines |
| 8 | git-absent `try`, and stop the N+1 `(None)` cascade (SCC-140 §6) | message quality | ~6 lines |
| 9 | delete the unreachable `NOT CLEAR` branch (SCC-140 §7) | dead code | −4 lines |
| 10 | `is_executable` Windows branch via monkeypatch (SCC-140 §5) | two-machine coverage | ~8 lines test |
| 11 | CLI exit aligned with `check()` for a never-claimed repo (SCC-140 decision C) | one state, one verdict | ~2 lines |

### OUT — recorded, not forgotten

- **Decision A** (`claims_gates` reads disk vs index) — a consistency complaint with no
  real-world trigger in these repos. **One comment line saying it is deliberate**, so the
  next review stops re-finding it. No code change, no test.
- **TOCTOU between `is_file()` and `stat()`** — noise-level.
- **Most of the original SCC-140 item 7** — `git_root` walk-up, absolute-`hooksPath` branch,
  `GIT_CONFIG_GLOBAL` nulling. Branch coverage for branches that have never failed. Item 10
  above is the one kept, because it is the branch that cannot be executed on this machine.
- **SCC-137 "NOT IN SCOPE"** — stale maps anchor, GitNexus re-index, PC cache sync. Operator
  and machine chores.

**Rough total: ~40 lines of source, ~60 of test.** The tickets as written are roughly double
that, and the extra half buys branch coverage rather than protection.

---

## 3. The discipline that makes this worth doing

Every assertion below is **red-first and mutation-proven**. This is not ceremony — it is the
direct lesson of SCC-125, where 30 guard rows pinned the *prose* describing a behaviour and a
file mutated to the exact opposite meaning scored a clean 323/323.

For each new assertion:

1. Write it and **watch it fail** against today's code. A test authored in the same context as
   the fix confirms; it never falsifies.
2. Make it pass.
3. **Mutate the fix and watch the assertion die.** If it survives the mutation, it is pinning
   the wrong thing.

Record the red output and the mutation result in the walkthrough. An assertion whose red was
never seen is not evidence.

---

## 4. The work, in commit order

### Commit 1 — `SCC-138` the lane gate runs the linter

**Problem.** `task_preflight.gate_plan()` builds the LOCAL lane's gate from exactly two
entries — `run_all.py` and `workflow_lint.py`. `check_maps.py` is absent, so the gate cannot
fail on a linter it never runs. SCC-124 landed a session folder with no INDEX row and SCC-119
nearly did, both with `run_all` reporting 21/21 PASS.

**The trap, handled rather than discovered.** `check_maps` run from a worktree emits two
guaranteed false positives — *"AUTO block is STALE"* and *"on disk but not in map:
`<lane-name>/`"* — because its home-base label is the CWD basename, and its printed remedy
ships the lane name to `main`.

**The fix, small because the seam already exists.** `check_maps.py` already has
`--depth3-only`, which runs *only* the depth-3 `_artifacts` INDEX reconciliation — precisely
the trustworthy subset, excluding both false-positive sources. It cannot gate today because
it ends in a hardcoded `sys.exit(0)` (it was built as a SessionStart nag).

- Add `--strict` so `--depth3-only --strict` exits 1 when there are problems. The bare
  `--depth3-only` keeps exiting 0 — SessionStart must not start blocking.
- `gate_plan()` appends `python3 .agents/scripts/check_maps.py --depth3-only --strict` when
  the script exists.

> ⚠️ **AUDIT FINDING F3 — measured, so the flag is not gold-plating.** Bare `check_maps.py`
> **already exits 1** on a missing INDEX row (verified 2026-08-13 with a seeded probe folder).
> The defect is therefore *only* that `gate_plan()` never calls it — not that the linter cannot
> gate. `--strict` is still required, because bare `check_maps` run from a worktree **exits 1 on
> false positives**: reproduced in a detached worktree, it emitted *"AUTO block is STALE"* and
> *"on disk but not in map: `wt-probe/`"* — the lane name — with a printed remedy that would
> write that lane name into the map bound for `main`. Record this comparison in the walkthrough
> so the flag never reads as an unjustified addition.

> ⚠️ **AUDIT FINDING F1 — the gate runs a SUBSET, and must say so.** `--depth3-only` runs check 7
> (depth-3 INDEX reconciliation) **only**. Checks 1–6 — AUTO-block freshness, level-2 INDEX
> presence, structure conformance — stay ungated at close-out. That is correct for this defect
> (both incidents were missing INDEX rows) and *necessary* to dodge the worktree false block, but
> SCC-137 AC1 says *"the lane gate runs check_maps"*. **Do not let the walkthrough repeat that
> wording unqualified** — a reader will believe the full linter runs. State the subset and the
> reason.

**Assert first:**
- A seeded session folder with no INDEX row → gate command exits 1. *(red before the flag exists)*
- A clean tree → exits 0.
- **Empty input is not a pass by accident** (F7): a repo with no `_artifacts/` yields no problems
  and so exits 0 under `--strict`. Defensible — nothing can drift — but assert it deliberately
  rather than leaving it to read as the Phase-2 vacuous-gate tripwire.
- Run from **inside a worktree**: the two false-positive rows do not appear and do not block;
  a real missing row still does.
- `gate_plan()` includes the check_maps entry for a repo that ships it. Pin the **wiring**
  (the returned command list) **including the `--strict` token** — the entry without it is a gate
  that cannot fail. Never pin the docstring.

> ⚠️ **AUDIT FINDING F2 — the worktree assertion is the most expensive item here and had one
> line.** There is **no live worktree** on this lane, so the test must create one
> (`git worktree add --detach <tmp>`) and tear it down with `remove --force` + `prune`. Two known
> hazards apply: a pruned worktree leaves a blocking shell on Windows, and worktrees do not
> inherit gitignored assets. Specify the fixture; guard or skip it on `nt`. The teardown was
> proven on the Mac during this audit; **the PC path is unproven.**

**Mutation:** drop the `--strict` handling → the missing-row case must go green, and the
assertion must die.

---

### Commit 2 — `SCC-139` close check_maps' own untested halves

**Problem 1.** `tests/test_check_maps.py` case F filters `"stale row" in p` — nothing asserts
the live tree reports no **MISSING** rows. Half the contract is untested, which is exactly how
a folder-without-a-row sails through.

**Problem 2.** `SCAN_IGNORES` has zero test hits. It rode in on SCC-135 as a carried operator
change with no acceptance item.

**Assert first:**
- **Live tree, missing rows.** Seed a session folder under `_artifacts/_main/` with no INDEX
  row, assert the linter reports it, remove the seed. Must be red today.
- **`SCAN_IGNORES`.** A directory named in the set is skipped; one not in it is scanned.
  Mutation: empty the set → the assertion must die.

Both on the **live tree**, not only a fixture — a fixture-only assertion is what left this
hole open.

> ⚠️ **AUDIT FINDING F5 — do not write the `SCAN_IGNORES` test against the gate's code path; it
> would be vacuous.** `SCAN_IGNORES` is consumed at `check_maps.py:394`, `:410` and `:417` — the
> repo-map scan. It is **not** used by `_check_depth3_tree`, which filters on `_archived` and
> dotfiles only. So SCC-138's gate and SCC-139's `SCAN_IGNORES` coverage exercise **different
> code paths**, despite reading as one job. A `SCAN_IGNORES` assertion driven through
> `--depth3-only` would pass no matter what the set contains — the exact vacuous green this
> ticket exists to close. Drive it through the scan path, and prove the mutation kills it there.

---

### Commit 3 — `SCC-140` the arm-check stops reporting false ARMED

`hooks_armed.py`. Four changes, all in `scan()`.

**3a. Arm flags: read disk AND index (item 1b).** The hooks check `[ -f <flag> ]` — the
**disk**. `scan()` reads the **index**. `sop-currency.sh:12` documents the disarm procedure as
*"delete `.agents/scripts/git-hooks/SOP-ENFORCE`"*. So following the documented disarm leaves
the tool reporting ARMED. Report a flag that is tracked but absent from disk: the gate is
warn-only and the tool must say so.

> ⚠️ **AUDIT FINDING F4 — this is ALL THREE flags, not just the SOP one.** Verified 2026-08-13:
> every arm flag is read from **disk** at runtime — `commit-msg-jira.sh:85` (`[ -f … ]`),
> `pre-push-main-approval.sh:38` (`[ -f … ] || exit 0`), and `SOP-ENFORCE` at
> `sop_currency.py:165` (`(repo / ENFORCE_MARKER).exists()` — one layer deeper than the shell,
> which is why a grep of the hook scripts alone appears to show it unread). `scan()` reads all
> three from the index. Cover **more than one flag** in the assertion; a single-flag test would
> under-state a three-flag defect.

*Assert:* tracked flag, deleted from disk → ERROR naming the flag. *Mutation:* revert to
index-only → dies.

**3b. A tracked flag whose script is untracked is reported (items 1a, 1c, 1d, 1e).**
[hooks_armed.py:176](../../../.agents/scripts/hooks_armed.py#L176) reads
`if script not in script_names: continue` — one line causing four of the ticket's five listed
defects. Realistic trigger: a project scaffolded by `/smh-new-project` carries `jira.conf` and
`.githooks/` while the gate scripts arrive later — that repo certifies ARMED with zero gate
scripts. Replace the bare `continue`: if the flag is tracked but its script is not, that is a
finding, not a skip. Also validate that the `via` hook named in `ARM_FLAGS` is tracked (1e).

*Assert:* the four shapes — (a) script git-rm'd, flag still tracked; (c) tracked flag,
untracked script; (d) `jira.conf` + hooks + zero gate scripts; (e) `ARM_FLAGS` naming an
untracked hook. Each must be **not armed** with a named finding. *Mutation:* restore the
`continue` → all four die.

**3c. Pathspec (item 4).** `git ls-files -- '.githooks/*'` crosses slashes — verified: it
returns `.githooks/README.md` and `.githooks/sub/nested.sh`. Both become "required executable
hooks" via `Path(p).name`, so adding a README hard-blocks close-out with *"hook 'README.md' is
not executable."* Restrict to top-level entries.

*Assert:* a tracked `.githooks/README.md` and a nested file are not treated as hooks; the four
real dispatchers still are.

**3d. `expanduser()` (item 5).** `Path("~/hooks").is_absolute()` is `False`, so a tilde path
resolves under the repo and a correctly-armed machine reads NOT ARMED. One line.

---

### Commit 4 — `SCC-140` robustness, dead code, and the two-machine red

**4a. The `(None)` cascade (item 6).** On a fresh clone with `hooksPath` unset, `resolved` is
`None` and the hook loop emits four more errors reading *"absent from the directory git
actually reads (None)"*. Five errors, one true, at the exact moment a human reads this output
for the first time. Return after the unset/unresolvable error.

**4b. Missing `git` binary (item 6).** `subprocess.run(["git", ...])` raises a bare
`FileNotFoundError` traceback. Wrap the three helpers.

**4c. Delete the dead `NOT CLEAR` branch (item 2).** Traced and confirmed unreachable: when
`claims_gates` is true every scan ERROR becomes `rep.err`, so `e` is non-zero and `BLOCKED`
always wins; the `elif` cannot be reached. If it ever were, its text and exit code disagree
(text says not-clear, `rep.exit_code()` returns 1). **Delete the four lines. No test** —
pinning dead code pays to keep something that does nothing.

**4d. Windows guards (item 3).** Test cases D, F and N call `.chmod(0o644)` with no `os.name`
guard. On the PC `is_executable` correctly returns `True` for any existing file, so all three
are **guaranteed red** — the suite is decorative on one of two machines. Guard them, and add
the monkeypatched `nt` branch test (item 10) so the Windows path is covered from the Mac.

**4e. Decision B — the live-repo tests.** Cases A and Q assert against the live repo, so they
go red on any machine with `core.hooksPath` unset. The fix is a **message, not architecture**:
detect the unarmed machine first and report *"THIS MACHINE is not armed — run
`git config core.hooksPath .githooks`"* rather than *"live repo reports ARMED: false"*, which
reads as though the script is broken. Keep the assertion; change the diagnosis. Case Q derives
its key from the resolved branch instead of the hardcoded `SCC-110` literal.

**4f. Decision C — CLI exit.** Nothing in the system gates on the standalone CLI; the only
programmatic caller is `task_preflight` via `check()`, and the SOP documents the CLI as
something a human types. Align it: a never-claimed repo exits 1, matching `check()`. Two lines,
and the exit code stops depending on which entry point was used.

**4g. Decision A — comment only.** Add one line at `claims_gates` recording that the
filesystem read is deliberate. No code change.

---

## 5. Gate

Run bare — a piped gate reports `tail`'s exit code, and `zsh` does not word-split unquoted
variables into separate args.

```
python3 .agents/scripts/tests/run_all.py
python3 .agents/scripts/workflow_lint.py --toolkit-only
python3 .agents/scripts/check_maps.py --depth3-only --strict
```

**Case totals must be additive.** Record the base count before the first commit; the final
count must equal base + new. A total that is not additive means one lane's tests displaced
another's.

⚠ **This branch rewrites the scripts its own close-out executes.** The lane grades its own
homework: a false red blocks the close-out, a false green means the gate lies about itself.
Mitigation — before the close-out, run `task_preflight.py` **from `main`'s copy** of the
script against this branch and confirm the two agree:

```
git show main:.agents/scripts/task_preflight.py > /tmp/preflight_main.py
python3 /tmp/preflight_main.py --repo . --branch chore/SCC-137-close-out-gate-defects \
        --expect-key SCC-137
```

A disagreement between the two is a finding, not a nuisance.

---

## 6. Close-out

One branch, one merge, one prune. Order matters and is **mechanically enforced**:
`check_children()` blocks the parent close while any child is open, and
`/smh-close-task-merge-tree` re-asserts it immediately before the transition.

1. **SCC-138, SCC-139, SCC-140 → Done.** Their work landed on this branch; every commit
   carries its own subtask key. Dev Record + transition for each.
2. **SCC-137** — `/smh-close-task-merge-tree --expect-key SCC-137` does the real close: the
   preflight, the gate, the `--no-ff` merge, the Dev Record, the transition, the prune. It
   will refuse to run while any of the three is still open, which is the check working.

For the three subtasks, the board rows come from the same mechanism the close-out uses — not
a hand-edit:

```
python3 .agents/scripts/jira_feed.py devrecord --key <KEY> --story close-out-gate-defects --apply
acli jira workitem transition --key <KEY> --status "Done" --yes
python3 .agents/scripts/jira_feed.py check --key <KEY>     # must exit 0
```

`--yes` is required; `jira_feed.py check` must exit 0 or the transition did not take.

**Carried in from the working tree:** the SCC-125 INDEX row, the MEMORY.md three-ways edit and
`prose-pinning-guards-are-vacuous.md`. Documentation from the previous lane, rolled in here
rather than left dirty on `main`.

**SOP currency:** any change under `.agents/scripts/*.py` is a surface ("the safety-net
scripts"), so most commits here owe an SOP edit in the SAME commit; `.agents/scripts/tests/`
is exempt, so a test-only commit does not.

⚠️ **CORRECTION (build, 2026-08-13):** this plan first named
`_my_resources/_quick_reference/sudo_workflows_testing.md`. That is **AGY's** copy. The lobby's
SOP — the one `sop_currency.py` actually enforces — is
[`docs/_scc_sops_prds/workflows_testing_SOP.md`](../../../docs/_scc_sops_prds/workflows_testing_SOP.md)
(`SOP_DOC`, `sop_currency.py:60`).

---

## 7. Risks

| Risk | Handling |
|---|---|
| The lane rewrites its own close-out gate | Cross-check against `main`'s copy of the preflight (§5) |
| `--strict` turns the SessionStart nag into a blocker | The bare `--depth3-only` keeps its `exit 0`; only `--strict` gates. Assert both. |
| A new assertion pins prose rather than wiring | Every assertion mutation-proven before it counts (§3) — SCC-125's F3 |
| Three tickets closed outside the close-out command | Same commands, `check` must exit 0 for each; children before parent |
| `origin/main` moves mid-lane | The preflight blocks at exit 2; absorb `main` into the branch, never rebase over it |

---

## Self-Audit (2026-08-13)

**Mode:** PRE-WORK — nothing built yet. **Right-size: FULL** — the plan touches a gate
(`task_preflight`), a script other scripts import (`hooks_armed`, imported by `task_preflight`
and `test_main_push_gate`), and a usage surface (a new flag + an exit-code change), so every
phase was walked.

**Repo/branch echoed from command output:** `Sudo_Hatter_Command` |
`chore/SCC-137-close-out-gate-defects`.

| Phase | Walked |
|---|---|
| **0 — scope + checkable list** | Change set: 4 scripts, 3 test files, the SOP doc, this folder, `INDEX.md`. Acceptance taken from the ACCEPTANCE blocks of SCC-137/138/139 (authority 1) plus the rewritten SCC-140 body. **Traceability clean both ways** — every acceptance item has a plan step, no plan step is orphaned. **Lane check: LOCAL** — no `backend/ frontend/ firebase/ functions/ mobile/ .github/` path is touched, so `/smh-close-task-merge-tree` is the right door. |
| **1 — blast radius** | `git worktree list` + `git branch --list 'chore/*'` + `git ls-remote --heads origin 'chore/*'`: **no sibling lanes, local or remote**; single worktree. **No landing-order dependency exists.** Callers swept: `hooks_armed` → `task_preflight`, `test_hooks_armed`, `test_main_push_gate`; `check_maps` → `run_all`, the SessionStart nag, `/smh-update-maps-indexes`. `scripts/INDEX.md` carries a `hooks_armed.py` row describing behaviour this plan changes — it must move with the code. |
| **2 — over-engineering** | One tripwire fired and was **cleared with evidence, not argument**: a *new config flag* (`--strict`). See F3. All others clear — no new command, no new rule, no new script, no clone-and-tweak, no N=1 generalisation. The plan **deletes** error handling for an impossible state rather than adding it (§4c). |
| **3 — pre-mortem** | Rows below. |

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | §4 Commit 1 | MED | The gate wires `--depth3-only`, which runs check 7 only; checks 1–6 stay ungated at close-out. SCC-137 AC1 says *"the lane gate runs check_maps"* — repeated unqualified, a future reader believes the full linter runs. | **Baked in.** Design kept; plan and walkthrough must state the subset and why. |
| F2 | §4 Commit 1 | MED | SCC-138 AC3 needs proof from inside a worktree. **No worktree is live**, so the test must create and tear one down. The method was one line; two known hazards apply (a pruned worktree blocks re-add on Windows; worktrees skip gitignored assets). | **Baked in.** Fixture specified; guard or skip on `nt`. Teardown proven on Mac, **PC path unproven**. |
| F3 | §4 Commit 1 | MED | The plan implied `check_maps` could not gate. It can — bare exit **1** on a missing row (measured). Left unrecorded, `--strict` reads as an unjustified flag under the Phase-2 tripwire. | **Baked in.** Measured comparison recorded, including the reproduced worktree false positives. |
| F4 | §4 Commit 3a | MED | Item 1b was written around the SOP flag alone. Verified it is **all three** — `commit-msg-jira.sh:85`, `pre-push-main-approval.sh:38`, `sop_currency.py:165`. A single-flag test under-states a three-flag defect. | **Baked in.** Assertion must cover more than one flag. |
| F5 | §4 Commit 2 | **HIGH** | `SCAN_IGNORES` is read at `check_maps.py:394/410/417` — the repo-map scan — and **never by `_check_depth3_tree`**, which filters on `_archived` and dotfiles only. A `SCAN_IGNORES` assertion driven through the gate's `--depth3-only` path **passes regardless of the set's contents**: a vacuous green inside the ticket that exists to kill vacuous greens. | **Baked in.** Drive it through the scan path; prove the mutation kills it there. |
| F6 | §5 | INFO | The live repo passes the new stricter rules (3 flags tracked **and** on disk, 6 gate scripts tracked, both declared `via` hooks tracked), so this lane's close-out is not self-blocked — **but it therefore cannot serve as a positive control.** | Recorded. Every new assertion needs a genuinely broken fixture plus mutation proof. |
| F7 | §4 Commit 1 | LOW | A repo with no `_artifacts/` yields no problems → exit 0 under `--strict`. Empty input reading as PASS is a Phase-2 tripwire. | **Baked in.** Defensible; assert it deliberately rather than leaving it implicit. |

### Pre-mortem rows

- **The other machine.** `gate_plan()` already emits `python3` (lines 770/776) and the new entry
  matches that convention, so nothing new breaks — `python3` not existing on the PC is
  **pre-existing and out of scope here**. F2's worktree teardown is the one genuinely unproven
  Windows path.
- **A fresh clone.** The new gate entry is a printed command, not a hook — nothing ships
  silently OFF. ✅
- **Empty input.** F7 — assertion added.
- **The gate fires on someone else's commit.** First victim is the next Task close-out with a
  drifted INDEX; the message is `check_maps`' own, which already names the missing row and the
  remedy. ✅
- **The escape hatch.** `--strict` is opt-in at the call site and the bare nag keeps `exit 0`,
  so there is a legitimate, auditable exit. ✅
- **The four platform caches.** No menu or command-body change → no door regeneration owed. ✅
- **A sibling lane lands first.** None exist (Phase 1). ✅
- **Rollback.** Code is revertible. **Irreversible:** the Jira transitions, the `main` merge, the
  branch prune, and the already-executed `Bug→Subtask` move that minted SCC-140 and destroyed
  the original summary and description. That one is **done and cannot be undone** — the
  rewritten SCC-140 body is now the only record of scope, which is why it was written to the
  kept scope rather than left empty.

### Four gates

- **Verification strategy present?** Yes — §3's red-first/mutation loop plus per-commit
  assertions. Two were underspecified and are now fixed (F2, F5).
- **Anything irreversible?** Yes — see the rollback row. Gated: subtasks close before the parent,
  and the merge is one invocation on one sign-off.
- **Any step vague enough that the builder will guess?** Two were (F2's worktree fixture, F5's
  `SCAN_IGNORES` path); both tightened. **Still open:** §6 says the SOP doc must move but does
  not name which rows — the builder names the exact surfaces (`--strict`, the CLI exit change)
  when they write it. `scripts/INDEX.md`'s `hooks_armed.py` row likewise moves with the code.
- **Convention fit?** Artifacts in `_artifacts/_main/<date>_<slug>/`, audit appended into the
  plan (never standalone), `task.yaml` keyed to the parent, INDEX row present, `check_maps`
  green. ✅

```
Audit verdict: GO
```

Seven findings, all baked into the sections they affect. None is UNSAFE. **F5 is the one that
mattered**: it would have shipped a vacuous test inside the ticket whose entire purpose is
killing vacuous tests.
