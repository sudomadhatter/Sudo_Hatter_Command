---
IsArtifact: true
ArtifactMetadata:
  title: SCC-214 — template-clone fixtures for the two git-repo-per-scenario suites
  type: implementation_plan
  date: 2026-08-21
---

# SCC-214 — Rebuild the two git-repo-per-scenario test files from a template clone

**Lane:** `chore/SCC-214-template-clone-tests` (worktree `.claude/worktrees/scc-214-template-clone-tests`, cut from `origin/main` @ `8ab7d64`, fast-forwarded to `f25d7cb` at 14:05 on the operator's word)
**Ticket:** SCC-214 (Task, standalone — `In Progress` since this lane's Step 0.5)
**Review runtime probe (Step 0):** `review-runtime: fan-out` — this runtime has the `Agent` tool.
**Sibling lane:** `chore/SCC-213-memory-obligation-audit` runs in parallel (see § Sibling lanes).

## Goal

`run_all.py` is already parallel, so its wall clock is the slowest file. The ticket names the two files that set that floor — `test_task_preflight.py` and `test_git_hooks.py` — and rules the fix: build one template repo, then **reset from a template clone per scenario, never a shared mutable repo**. Both files or neither.

## What was measured before anything was designed (clean run, idle machine, monotonic clock — `measure/before/report.txt`)

Same machine as the ticket's measurement (this Mac, 10 CPUs), same run mode (`python3 .agents/scripts/tests/run_all.py`, default parallel width). A first attempt used `/usr/bin/time` and was discarded: the system clock stepped backwards mid-run, so every wall-clock number from it is fiction. `measure/measure.py` times with `time.monotonic()` and records the load average at every step.

| What | Measured | Ticket said |
|---|---|---|
| `run_all.py` full, 41/41 files | **135.6 s** | 139.7 s |
| `test_task_preflight.py` solo | **113.7 s** · `186/186 passed` | 117.2 s |
| `test_git_hooks.py` solo | **77.8 s** · `151/151 passed` | 96.2 s |
| `test_task_preflight_receipts.py` solo (shares `_pf_fixtures`) | 49.0 s · `39/39 passed` | — |

**Where the time actually goes** (`measure/profile_split.py` wraps the builders in place and runs each file's `main()`):

| File | Repo construction (the ticket's premise) | The cost the ticket did not see |
|---|---|---|
| preflight | `make_repo` ×90 = **21.4 s (19 %)**; `branch` ×87 = 10.5 s (per-scenario work, stays); `secondary` ×13 = 2.4 s | `task_preflight.py` runs ×105 = **70.3 s (62 %)** — and the **first** run after each fresh `acli` stub averages **0.73 s** against **0.34 s** for a warm one: 88 fresh stubs → **~34 s** |
| git_hooks | builder-internal git ×~480 calls = **~10.6 s (14 %)** | scenario `git commit` ×124 = **36.5 s**, `git push` ×34 = 17.1 s — the **first** hook-running op in each fresh repo averages **0.48 s** against **0.15 s** later: 72 repos → **~24 s** |

**The mechanism, isolated** (`measure/stall_probe.py`, `measure/inode_probe.py`): this Mac assesses every **newly created executable file** once, on its first launch. Idle: 0.19–0.28 s for a bare `#!/bin/sh\nexit 0`, 0.004–0.03 s thereafter. Under the suite's parallel load the same first launch measured 1.6–2.8 s (the assessor serialises). A **hard link** to an already-launched file is instant (0.006 s); a byte copy, an APFS clone and a byte-identical new file all pay the full first-launch cost again — **the assessment is per inode**. Both target files create fresh executables per scenario: preflight a new `acli` launcher per block (`board()`), git_hooks two to five hook scripts per repo. That — not `git init` — is the larger half of what the ticket is paying for.

**Consequence for the target.** The ticket projects ~50 s for the suite from repo construction alone. Measured, construction is 19 % and 14 % of the two files. The design below takes both levers the measurement exposes and projects (solo) **preflight ≈ 61 s, git_hooks ≈ 45 s, receipts ≈ 35 s**, so a suite wall of **~65–80 s** — about half of today, short of ~50 s. Reaching ~50 s needs one more thing this ticket does not rule on: splitting `test_task_preflight.py` at a block seam into two files (the SCC-156 precedent that created `_pf_fixtures.py`). **Default in this lane: not done** — it is a third conversion, and the ticket lists two. It is one sentence at the approval stop if the operator wants it here.

## Acceptance (ticket rows, verbatim) → the assertion that proves each

| # | Acceptance | Assertion (RED first) | Lives in |
|---|---|---|---|
| 1 | Full `run_all.py` wall clock posted BEFORE and AFTER, same machine, same run mode. Target ~50 s. A claimed number without a pasted comparison does not close this | `measure/before/report.txt` (above) and `measure/after/report.txt` from the same `measure.py`, both pasted into the walkthrough with the load averages. The target is addressed honestly above | walkthrough § Evidence |
| 2 | Every scenario in both files starts from a fresh clone — proven by a test that FAILS if state leaks between scenarios, not by inspection | NEW `test_repo_template.py`: a commit, a config key, an untracked file, an in-place edit of a regular file and a replaced hook in clone A are all invisible in clone B and in a clone C cut afterwards; a push from one preflight scenario is invisible to the next scenario's `origin`; an in-place write through a shared executable **raises**; and mutant **M1** (clone from the previous scenario instead of the template — the literal "scenario N sees N-1") is seen killing it | `test_repo_template.py` blocks T1–T4; `sweep.json` M1 |
| 3 | Case count unchanged in both files | `-- 186/186 passed --` and `-- 151/151 passed --` before and after; **no block in either file is edited** — only the builder functions above `main()` | the two files' own transcripts |
| 4 | Full enforcement suite green | `gate_receipt.py run --gate suite` receipt at `gates/suite.json`, stamped on the committed tree | `gates/suite.json` |

## Design decisions (rulings the builder follows)

1. **One template per builder signature per process, not per block.** The ticket says "one template repo per block"; the kwargs tuple is the finer and correct key (`make_repo(t)` ×57, `make_repo(t, deployable=True)` ×4, … — 12 shapes in preflight, 3 in receipts, 4 in git_hooks). Identical isolation, fewer builds, and a `--case` single-block run builds exactly what it needs. The template root is one process-wide scratch dir (`tempfile.mkdtemp`, removed at `atexit` with the same read-only-tolerant `rmtree` `TempDir` uses). `run_all.py` runs each file in its own process, so nothing is shared across files.
2. **A scenario gets a byte-identical copy (`shutil.copytree`) into its own `TempDir`.** Regular files are copied. **Executable files are hard-linked to the template's inode, and the template's executables are frozen read-only (`0o555`) after the build.** The link is what carries the one-time assessment across scenarios (the measured mechanism); the freeze is what makes a shared inode *not* shared state: an in-place write raises `PermissionError` instead of leaking. Git itself never writes a file in place (temp + rename), so every git operation on a scenario's hook — checkout, merge, a branch that changes it — is isolated by construction. `os.link` failing (cross-device, a platform that refuses) falls back to `copy2`: correctness identical, only the speed property degrades; the module exposes `HARD_LINKS` so the test asserts the inode share only where links are possible.
   ⚠️ **AUDIT FINDING (Lens 2, anchored `_harness.py:186-189`):** `TempDir.__exit__`'s `rmtree` handler — `def force(func, path, _info):  # read-only files (and .git objects) on Windows` / `Path(path).chmod(0o700)` — fires on the PC for every read-only file, and a chmod through a hard link changes the **template's** inode: the freeze would last exactly one block on Windows. Ruling: **hard links only where the assessor exists — `HARD_LINKS = (os.name != "nt") and <link probe succeeded>`**; the PC copies executables (today's semantics exactly, and the first-launch stall does not exist there). On the Mac, POSIX `rmtree` never touches a writable directory's read-only files, so the handler never runs.
3. **No path into the template survives in a clone.** The remote URL in `.git/config` is absolute, so every clone gets `git remote set-url origin <its own bare>`; `FETCH_HEAD` (written by `make_pushable`'s fetch) is deleted from the template after the build. The leak test greps each clone's `.git` for the template root and requires zero hits.
4. **`board()` writes the launcher once per process.** The `acli` launcher + `board_stub.py` go into the template root, assessed once; each call writes only `board_state.json` into the scenario's root and sets `PF_BOARD_STATE`. `ACLI_BIN` points at the shared launcher. `preflight()`'s "test the FILE, not the env var" guard keeps working unchanged — the state file still dies with its `TempDir`, the launcher no longer does.
5. **Builders keep their names, signatures, return values and defaults.** `_pf_fixtures.make_repo` → body becomes `_build_repo`, `make_repo` clones it; `test_git_hooks.make_repo / make_pushable / make_carveout_repo` likewise. A second `make_repo` into an occupied root still raises `FileExistsError` (the clone refuses when any top-level template entry already exists in the destination — today's `mkdir()` did the same). **No block in either file changes**, which is how acceptance 3 is held.
6. **A template is cached only after its build succeeded.** A builder that raises leaves nothing behind; the next call for that key builds again.
7. **Not converted, and why:** `secondary()` (13 calls, 2.4 s — noise), the RH-B block's hand-rolled repo (one scenario), `branch()` (per-scenario work by definition), and `task_preflight.py`'s own runtime (out of scope: "any change to what the two files ASSERT" is banned, and the script under test is not a fixture).
8. **`.agents/scripts/INDEX.md:61` is wrong after this lands** — it says the template lever "was descoped, so that gap is open, not closed". The paragraph gets this lane's measured numbers. Not a usage surface, no SOP staging; `.agents/scripts/tests/` is exempt from the SOP gate (`sop_currency._EXEMPT_PREFIXES`), so no commit here needs `[sop-ok]`. The "58 s / 51 s / 42 s" figures quoted as examples in `smh-quick-dev.md` are another machine's prose and are **not** edited (usage surface + twin parity for a number that is illustrative).
9. **Both machines.** Nothing here hardcodes `python3`; the stall is macOS's assessor — on the PC the win is the construction share only, and the walkthrough says so. Hard links exist on NTFS; the fallback covers anything else.

## Declared Change Set

- NEW `.agents/scripts/tests/_repo_template.py` — `clone(key, build, dest)`: template cache, copy-with-linked-executables, freeze, `HARD_LINKS` probe, atexit cleanup → 2, 3
- NEW `.agents/scripts/tests/test_repo_template.py` — T1 helper contract (leak, freeze, occupied root, build-once) · T2 preflight builders + shared launcher · T3 git_hooks builders + inode share · T4 failed build caches nothing → 2
- EDIT `.agents/scripts/tests/_pf_fixtures.py` — `make_repo` → `_build_repo` + clone + `set-url`; `board()` one launcher per process → 1, 2, 3
- EDIT `.agents/scripts/tests/test_git_hooks.py` — builders only (`make_repo`, `make_pushable`, `make_carveout_repo` → `_build_*` + clone); zero edits below `def main()` → 1, 2, 3
- EDIT `.agents/scripts/INDEX.md` — the run_all paragraph: template lever landed, new measured numbers → 1

### Amendment — Part B (2026-08-21), inside this one block on purpose

- EDIT `.agents/scripts/tests/test_task_preflight.py` — keeps blocks 1–13, the REFUSALS; imports pruned → B1, B2
- NEW `.agents/scripts/tests/test_task_preflight_contract.py` — blocks 14–25, the CONTRACT half → B1, B2
- NEW `_artifacts/_main/2026-08-21_scc-214-template-clone-tests/measure/floor.py` — the per-file contended profiler that chose and proved the seam → B1
- NEW `_artifacts/_main/2026-08-21_scc-214-template-clone-tests/measure/blocktime.py` — the per-block timer the seam came from → B1

## Execution order

1. **RED** — write `test_repo_template.py` first, against today's builders, with `import _repo_template` guarded so a missing module is a failing *row*, not a setup death. Rows that fail today for the right reason: `builds == 1` per key (today every call builds), one launcher per process (today one per `board()` call), hook inode shared across two `make_pushable` scenarios (today two inodes), in-place write through an executable raises (today it succeeds). Rows that pass today are **characterization** and are labelled so in the walkthrough — they exist to be the cases M1–M11 must kill.
2. `_repo_template.py`.
3. `_pf_fixtures.py`; then `test_git_hooks.py` builders.
4. **GREEN** — `test_repo_template.py` bare; then `test_task_preflight.py`, `test_git_hooks.py`, `test_task_preflight_receipts.py`, `test_ship_preflight.py` bare (the four consumers of the edited builders) — counts must read 186 / 151 / 39 / 102.
5. Commit (explicit paths). Then **stamp-first**: `gate_receipt.py run --task SCC-214 --gate suite --root <this folder> --cwd <worktree> -- python3 .agents/scripts/tests/run_all.py`.
6. Mutation sweep: `mutation_sweep.py --table sweep.json` (table below, pinned to exact source text once the code exists).
7. **AFTER** measurement: `measure/measure.py` → `measure/after/report.txt`, idle machine, monotonic clock, same command. Paste both reports into the walkthrough.
8. `/smh-code-review` → walkthrough → Dev Record.

## Mutant table (declared BEFORE mutating; every mutant is a decision in the code above, not a reading of the cases)

| # | Mutant (the decision it inverts) | File | Named case it must kill |
|---|---|---|---|
| M1 | cache the **destination** instead of the template (`_CACHE[key] = dest`) — every later clone copies the previous scenario: the literal shared-mutable failure | `_repo_template.py` | T1 `a clone does not see its predecessor's commit` |
| M2 | drop the `0o555` freeze | `_repo_template.py` | T1 `an in-place write through a shared executable raises` |
| M3 | link every file, not only executables | `_repo_template.py` | T1 `editing a regular file in one clone leaves the other untouched` |
| M4 | copy executables instead of linking (the speed property, narrowing) | `_repo_template.py` | T3 `a hook shares the template inode` |
| M5 | drop `set-url` after the clone (stale absolute remote) | `_pf_fixtures.py` | T2 `a push from one scenario is invisible to the next scenario's origin` |
| M6 | write the launcher into the scenario root on every `board()` call | `_pf_fixtures.py` | T2 `one launcher per process` |
| M7 | cache the template before `build()` runs | `_repo_template.py` | T4 `a failed build caches nothing` |
| M8 | delete the occupied-destination refusal | `_repo_template.py` | T1 `a second clone into an occupied root refuses` |
| M9 | narrowing: drop `ci` from preflight's key | `_pf_fixtures.py` | T2 `make_repo(ci=True) after make_repo() carries the workflow file` |
| M10 | narrowing: drop `arm` from git_hooks' key | `test_git_hooks.py` | T3 `make_repo(arm=False) after make_repo() carries no flag` |
| M11 | keep `FETCH_HEAD` in the template | `_repo_template.py` | T3 `no clone carries a path into the template root` |

A sweep that ends with any survivor, or any DEFECTIVE row, is a finding, not a note.

## Sibling lanes (read at Step 0.5, re-read at 14:10)

`chore/SCC-213-memory-obligation-audit` — worktree at `f25d7cb`, **no committed or uncommitted diff yet**. Its expected set is `_artifacts/_memory/**` (and possibly `.agents/rules/**`); this lane's set is `.agents/scripts/tests/**` + `.agents/scripts/INDEX.md`. **Zero file overlap, and no gate crossing:** their `test_memory_store.py` is in the suite this lane runs and this lane does not touch the store; this lane's new test file joins their suite only after it lands, and it reads nothing of theirs. Landing order is free. If SCC-213 lands first, this lane absorbs `main` and re-stamps — the AFTER number stays valid (memory files are not on the suite's hot path).

## Both machines

Mac measured here. PC: `python` not `python3`; hard links on NTFS; no first-launch assessor, so only the construction share is saved there — the walkthrough's numbers are labelled Mac.

## Open questions

None blocking. One decision at the approval stop, default **no**: also split `test_task_preflight.py` into two files to reach the ticket's ~50 s. Everything else in this plan proceeds as written on `approved`.

## Self-Audit (2026-08-21)

**Level:** LEDGER+BLAST · **mode:** PRE-WORK. The Declared Change Set edits `_pf_fixtures.py` (imported by three test files) and adds a module two files will import — "a script others import".

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path the plan names exists on disk (20/20 `ok`, listed in the audit shell transcript)
             `declared_change_set.py parse` → present: true, 5 entries, incomplete: []
             both-machines: no `python3` hardcoded in shipped code; stdlib only; `measure/measure.py` is artifact-only
             lane fit: no deployable path in the set (tests/, scripts/INDEX.md) → `/smh-close-task-merge-tree` is the door
             quoted claims re-read: `sop_currency.py:82` `_EXEMPT_PREFIXES = (".agents/scripts/tests/",)`; `INDEX.md:61` "descoped, so that gap is open"; `smh-quick-dev.md:294` "58 s … 51 s … 42 s"; builder defs at `_pf_fixtures.py:72,167,187,209`, `test_git_hooks.py:64,97,118,190`
             Scope Ledger precondition: the ticket carries 4 acceptance rows, each with a concrete observable (wall clock pasted · a test that FAILS on leak · counts unchanged · suite green)
             empirical (`measure/clone_probe.py`): a copied repo with linked 0o555 executables reads `git status` clean, HEAD == base, `ls-remote` against its OWN bare, a push moves the clone's bare only, a merge through the linked hooks returns rc 0, an in-place write raises PermissionError, template bytes intact, 0 paths into the template inside the clone's `.git`
read:        implementation_plan.md · _pf_fixtures.py · test_git_hooks.py:1-190 · test_task_preflight_receipts.py:423-425 · _harness.py · run_all.py:58 · sop_currency.py:63-110 · .agents/scripts/INDEX.md:61 · .agents/commands/smh-quick-dev.md:294 · measure/before/report.txt
verdict:     clean
```

**Scope Ledger** (created artefact × the acceptance row that requires it):

| Created (op NEW) | Plan step | Acceptance row |
|---|---|---|
| `.agents/scripts/tests/_repo_template.py` | 2 | 2 (the leak proof is a test of this contract), 3 (builders unchanged → counts unchanged) |
| `.agents/scripts/tests/test_repo_template.py` | 1 | 2 |

Caller count, printed: `grep -rl _repo_template .agents .githooks` → **0 today**; after this plan, 3 (`_pf_fixtures.py`, `test_git_hooks.py`, `test_repo_template.py`) — all created or edited by this plan, which is the honest shape for a fixture helper. No empty acceptance cell → no ledger finding.

```
lens:        2 Parity + Blast
checks_run:  a script others import: `_pf_fixtures` callers = test_ship_preflight.py, test_task_preflight.py, test_task_preflight_receipts.py (all four consumers run bare in plan step 4); `.githooks/` + `git-hooks/` call nothing under tests/ (grep: none); `scripts/INDEX.md` row → the plan edits :61
             command / rule / door: none touched → twins n/a, `workflow_lint` pointers n/a
             gate or hook: none shipped
             path move/rename/delete: none
             SOP: `.agents/scripts/tests/` exempt; INDEX.md not a surface → no `[sop-ok]`, no SOP staging
             `_artifacts/_memory/`: not touched
             file in >1 repo: `ls Projects/*/.agents/scripts/tests/{test_git_hooks,_pf_fixtures}.py` → no copies (the three projects carry tests/ dirs, not these files) → port rule clear
             sibling worktrees after `env -u GITHUB_TOKEN git fetch origin main` (origin/main f25d7cb): `scc-213-memory-obligation-audit` = `_artifacts/_main/2026-08-21_scc-213-*/{task.yaml,walkthrough.md}`, `_artifacts/_memory/a-defer-needs-a-structural-blocker.md`, `_artifacts/_memory/review-status-means-needs-operator.md` → zero overlap with this set
             risk seam: `risk_seam.py classify` → status unclassified (placeholder; informs only)
             the other machine: `_harness.TempDir.__exit__` read in full → finding below
read:        _harness.py:181-190 · .githooks/commit-msg · git worktree list + per-tree diff/status · Projects/*/.agents/scripts/tests/ · risk_seam.py output
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  attached the other-machine narrative to Lens 2's anchored finding; the sibling-lands-first and fresh-clone narratives found no anchored finding to attach to and are discarded
read:        the findings table below
verdict:     findings below (attachment only)
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/tests/_harness.py:186-189` | "def force(func, path, _info):  # read-only files (and .git objects) on Windows / Path(path).chmod(0o700) / func(path)" | On the PC `rmtree` of a scenario dir raises on the frozen 0o555 hook, the handler chmods it 0o700 **through the hard link**, and the template's inode is writable for every later scenario — the freeze that makes a shared inode "not state" lasts one block on Windows. Pre-mortem: the silent other-machine class — nothing writes a hook in place today, so it would never have been seen. **Fix baked into decision 2:** links only where `os.name != "nt"` and the probe succeeds; the PC copies executables (its semantics today; no assessor there). | important |

### Observations (uncounted)

- `test_task_preflight_receipts.py:423-425` — `repo_dir.mkdir()` then `make_repo(repo_dir, walkthrough=False)`: the destination **exists and is empty**. The occupied-root refusal (decision 5) must be per top-level template entry (`repo/`, `origin.git/`), never "dest exists".
- `.agents/scripts/INDEX.md:61` quotes "~69 s parallel against ~213 s serial (measured 2026-08-14)"; this lane measured 135.6 s on 2026-08-21 on the same Mac. Write both with dates; the assessor mechanism is why the number is machine-state-dependent. Do not overwrite history.
- `measure/measure.py` calls `os.getloadavg()` — absent on Windows. Artifact-only; the AFTER run is on this Mac.
- `run_all.py:58` `FILES = sorted(p.name for p in HERE.glob("test_*.py"))` — the new test auto-joins; `_repo_template.py` is not collected. Read, not assumed.
- The template root is removed at `atexit`; a SIGTERM-killed file leaks one small `wfscripts-tpl-*` dir in TMPDIR. `run_all.stop_running` sends SIGINT first, so the normal interrupt path cleans up.

### Sibling landing-order dependency

None. SCC-213's set and this set share no file; their memory edits are not on this suite's hot path; this lane's new test reads nothing of theirs. Either lane may land first; the later one absorbs `main` and re-stamps.

Audit verdict: GO

---

## Part B (amendment, 2026-08-21) — split `test_task_preflight.py`, and close acceptance row 1

**Operator ruling, verbatim, in two messages:** *"Explain this 45 seconds what's the value to work here? We are not opening a new ticket it's add it to this one or we scrape it"* → then, after the value was measured and put to them: *"Nope fix that here, test it then we will close this ticket out"* → and the gate word: *"Approved"*. So this is scope added to SCC-214, not a new ticket, and Part A's `## Your Actions` decision row is answered by doing it.

### Why, measured before deciding

Part A left the suite at 94.8 s against the ticket's ~50 s. The open question was whether a split would actually move it, because `_repo_template` caches **per process** and `run_all.py` gives each file its own — so splitting a file DUPLICATES its template builds and could eat the gain.

Measured with `measure/floor.py` (mimics `run_all`'s pool exactly, but records each file's wall):

| | Before the split | After the split |
|---|---|---|
| **suite wall** | **94.0 s** | **61.7 s** |
| slowest file | `test_task_preflight.py` **81.8 s** | `test_task_preflight.py` 49.5 s |
| runner-up | `test_jira_feed.py` 45.1 s | `test_task_preflight_contract.py` 46.1 s |
| sum of files | 370.3 s | 390.3 s |
| perfect-packing floor (work ÷ 10) | 37.0 s | **39.0 s** |

The duplicated-template cost is real and visible — sum-of-files rose 370.3 → 390.3 s — and it did not matter, because the wall was floor-bound, not work-bound. It is now nearly work-bound: five files sit between 41 s and 50 s against a 39.0 s packing limit, so **splitting further buys almost nothing**. The next real lever would be reducing total work, and the biggest single remaining file is `test_jira_feed.py` — a file this ticket never touched.

### The seam was chosen by measurement

`measure/blocktime.py` timed all 25 blocks in one process (73.9 s of block time) and the cut is the balance point: **38.8 s stays, 35.1 s moves**. It also falls on a real thematic boundary — refusals stay, contract moves.

**Declared Change Set:** the Part B rows are folded into the single `## Declared Change Set` block above, where `declared_change_set.py` reads them — a second heading is not a second block.

### Acceptance (Part B) → the assertion

| # | Acceptance | Assertion | 
|---|---|---|
| B1 | The suite wall drops materially and the ~50 s target is addressed with a measured number, not a projection | `measure/floor.py` before/after, same instrument, minutes apart: **94.0 s → 61.7 s**; plus the gate receipt at the shipping sha |
| B2 | **Case count unchanged** — the split loses nothing | `106 + 80 = 186`, exactly the count the single file carried. This is the only way a split can go wrong, and it is countable |
| B3 | Every other consumer of `_pf_fixtures` still green | `test_task_preflight_receipts.py` 39/39 · `test_ship_preflight.py` 102/102 · `test_repo_template.py` 46/46 |

**No mutant is owed for Part B.** A file split changes no decision in any swept file — `_repo_template.py`, `_pf_fixtures.py` and `test_git_hooks.py` are byte-identical across it — so the 22-mutant table stands unchanged, and it is re-run at the shipping sha to prove exactly that.

**Part B self-audit (Lens 1 + 2, anchored).** Lens 1: every path exists; the block boundary was read from the file (`test_task_preflight.py:895` `# ── SCC-110 · the whole point`), not guessed — the first two attempts asserted the wrong offset and *failed loudly* rather than splitting in the wrong place, which is the guard working. Lens 2: `run_all.py:57` `FILES = sorted(p.name for p in HERE.glob("test_*.py"))` — the new file auto-joins with no wiring, confirmed by the 43-file count in the measurement; `.agents/scripts/INDEX.md:61` is the one doc naming these files and it is in the change set; `sop_currency._EXEMPT_PREFIXES` covers `.agents/scripts/tests/`, so no SOP staging is owed. No sibling lane is live. **Audit verdict: GO**
