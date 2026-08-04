# ⚠️ Migration — every OTHER machine needs its venv rebuilt (Python 3.11 + test-infra overhaul + vitest suite lock, 2026-08-01; gate went PARALLEL 2026-08-03)

Part of the `_my_resources/migrations/` kit — the Python/venv companion to
[`new_machine-migration-guide.md`](new_machine-migration-guide.md) (which covers secrets;
its §5 points here). Applies to EXISTING machines pulling the 2026-08-01 changes AND to
fresh-machine setups.

**Status:** OPEN until every machine that works on AGY_AVIATIONCHAT has run the checklist below.

| Machine | OS → which column | Done | Best `-n` (measure once) | Notes |
|---|---|---|---|---|
| **Laptop** (8-core) | Windows | ☑ 2026-08-01 · re-verified parallel 2026-08-03 | **`-n 4`** (206.81 s, vs `auto`/8 = 261.76 s) | The box every measurement in this doc came from |
| **Desktop** (64 GB RAM) | Windows | ☐ | ☐ time `4 / 6 / 8 / auto` | Same commands as the laptop — **nothing extra to install** |
| **Mac** (64 GB RAM) | macOS | ☐ | ☐ time `4 / 6 / 8 / auto` | Needs `python3.11`, `temurin@17`, Node, + `pwsh` for any `.ps1`. See ⛔ **§2 of `INDEX.md`** — the secrets restore script does NOT work here |

**Two independent axes — don't collapse them.** *OS* decides which command column you use. *Power*
decides only your `-n` value and is otherwise handled automatically (`-n auto` reads the core count).
The desktop is the proof they are independent: **Windows and fast.** A faster machine never gets a
reduced checklist — every step below is correctness, not performance (see
*"My machine is much faster…"*).

⚠️ **Both 64 GB machines are fast enough to HIDE the venv-walk bug** rather than fail on it — CHECK 4's
unconditional file-count bound is what catches it there. Do not weaken that assertion.

---

## Why this task exists

On 2026-08-01 AGY_AVIATIONCHAT was realigned to **Python 3.11** (CI and prod were always 3.11;
local venvs had silently drifted to 3.14 — meaning weeks of local greens were measured on an
interpreter two versions off what ships). Same day, the test infra gained: parallel test runs
(`pytest-xdist`), a per-test hang ceiling (`timeout = 300`), and a **machine-wide suite lock**
in the root `conftest.py` (two big pytest runs on one machine now queue instead of thrashing).

**The trap: venvs are gitignored, so NONE of this travels to other machines via git.**
When another machine pulls these commits it gets the new configs and pins — but keeps its
old venv, and:

- pytest does **NOT** check `requires-python` — a stale 3.14 venv will happily keep running
  tests on the wrong interpreter, and local green goes back to being a lie **on that machine
  only**. Nothing warns you. (Only pip and the CI assert step enforce the declaration.)
- **Parallel runs are the GATE MODE since 2026-08-03** (quick fix 1.1): `-n auto --dist loadfile`,
  matching `pr-check.yml`. This was "opt-in, gate stays serial" until then. An old venv without
  `pytest-xdist` fails loudly with `unrecognized arguments: -n` — which on a stale machine now
  breaks the *normal* command, not an optional one. **Nothing new to install:** `pytest-xdist` and
  `filelock` are pinned in `backend/requirements.txt`, so the step-2 rebuild below is the whole fix.
- ⚠️ **Name the venv `.venv` and keep it directly under `backend/`.** Several backend tests are
  source-grep gates that walk `backend/` and read every `.py` they find; they skip virtualenvs **by
  directory name** (`.venv*` plus a fixed list). A venv named anything else — `env311`, `pyenv`,
  `venv3` — is walked and read instead: **16,586 files / ~273 MB per test** rather than 217. Serially
  that is merely slow; under `-n auto` it blows the 300s timeout and pytest-timeout kills and
  respawns the worker on every trip — **~40 minutes of `node down` churn with no error naming the
  cause.** That is exactly the bug quick fix 1.1 closed. The guard
  `test_scan_never_walks_a_colocated_virtualenv` now fails loudly and names the directory, but only
  once you run the suite.
- The suite lock needs `filelock` — without it, runs still work but print
  `[suite-lock] filelock not installed — machine serialization OFF` (fail-open by design).

**Late 2026-08-01 addition — the FRONTEND got the same suite lock** (`cae06a78` on `main_debug`):
full `vitest run`s on one machine now queue instead of thrashing (measured before the lock: two
concurrent full runs took 481s/1074s vs a healthy 178s, collected only 57–81 of 84 files, and
reported shifting failure sets). **Unlike the Python side, this needs ZERO per-machine work** —
the lock is tracked code (`frontend/vitest.global-setup.ts`, wired via `globalSetup` in
`frontend/vitest.config.ts`) with zero new npm dependencies, so it arrives complete with
`git pull`. Details in "The vitest side" section below.

## The 5-minute fix (run on EACH machine, once)

> **The only axis that needs branching is OS, not machine power.** `-n auto` already scales itself to
> the core count, so a fast machine needs no different setup — it needs different *commands*. Pick your
> column and use it consistently; `$PY` below is shorthand for the venv's interpreter.

**Windows (PowerShell)**
```powershell
git pull                                   # 0. from the AGY_AVIATIONCHAT repo root, on main_debug
py -0p                                     # 1. look for a -V:3.11 line
winget install Python.Python.3.11          #    only if missing
Remove-Item -Recurse -Force backend\.venv  # 2. rebuild (deletes the drifted one)
py -3.11 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
#   $PY = backend\.venv\Scripts\python.exe
```

**macOS (zsh/bash)**
```bash
git pull                                   # 0. from the AGY_AVIATIONCHAT repo root, on main_debug
python3.11 --version                       # 1. installed?
brew install python@3.11                   #    only if missing
rm -rf backend/.venv                       # 2. rebuild (deletes the drifted one)
python3.11 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
#   $PY = backend/.venv/bin/python
```

**macOS also needs, once:** `brew install --cask temurin@17` (Firestore rules-emulator suite) · Node
(`brew install node`) · **`pwsh`** (`brew install --cask powershell`) if you intend to run
`Restore-EnvMaster.ps1` from the migration kit — those scripts are PowerShell.
`rename-fix.ps1` is Windows-only by design (it rewrites `%USERPROFILE%` paths); do not run it on a Mac.

## Verify it didn't break anything (the actual walkthrough)

Run these checks **in order**. `$PY` = the interpreter path from your column above
(`backend\.venv\Scripts\python.exe` on Windows, `backend/.venv/bin/python` on macOS).

```bash
# CHECK 1 — the venv really is 3.11 now
$PY --version
#   PASS: Python 3.11.x        FAIL: 3.14.x → step 2 above didn't run / wrong launcher

# CHECK 2 — the new pins landed        (Windows: pipe to `Select-String` instead of `grep -E`)
$PY -m pip list | grep -E "pytest-xdist|filelock|ruff|pyrefly"
#   PASS: all four listed (xdist 3.8.0, filelock 3.24.3, ruff 0.16.0, pyrefly 1.1.1)

# CHECK 3 — a scoped run works and does NOT wait on the lock (inner loop stays instant)
$PY -m pytest backend/tests/test_affirmative_classifier.py -q
#   PASS: green, starts immediately, NO [suite-lock] line

# CHECK 4 — the full suite on 3.11, PARALLEL (the real proof; this is the gate mode since 08-03)
$PY -m pytest backend/tests -n auto --dist loadfile -q
#   PASS: 0 failed. Reference totals 2026-08-03: 3024 passed / 35 skipped / 0 failed
#         (the passed count grows as stories land; 0 failed is the bar).
#   TIMING IS MACHINE-SPECIFIC AND NOT A SIGNAL — see "Tune -n on this machine" below.
#   Any NEW failure here = a real behavior difference on this machine's deps —
#   capture the traceback; that is a real finding, not a reason to roll back.

# CHECK 4b — only if CHECK 4 is red and you need to tell "this machine" from "xdist" apart
$PY -m pytest backend/tests -q --timeout=300
#   Serial, one variable. Green here + red above = a parallelism problem, not an interpreter one.
```

### ⚠️ A hung CHECK 4 looks DIFFERENT on each OS

Both are the same bug — almost always a virtualenv being walked (see the venv-naming ⚠️ above).
Confirm either way with `$PY -m pytest backend/tests -k test_scan_never_walks_a_colocated_virtualenv`,
which names the offending directory.

| OS | What you see | Why |
|---|---|---|
| **Windows** | workers die — `node down` + respawn, ~5 min apart, near the end of the run | no `SIGALRM`, so pytest-timeout uses the **thread** method and `os._exit`s the whole worker process |
| **macOS** | ordinary test failures with a `Timeout >300s` traceback naming each test; workers survive | `SIGALRM` available → the **signal** method raises inside the test |

**On a fast machine this bug may never trip the timeout at all** — it would just tax every run
silently, forever. **Nothing extra for you to do about it:** the guard asserts an unconditional
file-count bound (`< 2000` scanned files) alongside the timeout, and a file count is
machine-independent — so CHECK 4 fails on a fast Mac exactly as it would on a slow laptop. This is
already handled; it is recorded here only so nobody "optimises" that bound away later thinking the
timeout covers it. It does not.

### Tune `-n` on this machine (do this once)

`-n auto` = core count, and **auto is not always fastest**. Every xdist worker re-imports the whole
backend tree (firebase, genai, adk), so past a point the import cost outweighs the extra parallelism.
Measured on the 8-core laptop, 2026-08-03:

| Workers | Wall clock |
|---|---|
| `-n 8` (= `auto` there) | 261.76 s |
| `-n 4` | **206.81 s** |

Half the workers, 21% faster. On a many-core machine `auto` may be **slower** than a smaller number —
so time `-n 4`, `-n 6`, `-n 8` and `-n auto` once, and use the winner for local full runs. CI stays
`auto` (4 vCPU, where `auto` ≈ 4 anyway). This is a local speed preference only; it changes no gate.

## Messages you may see that are FEATURES, not breakage

| Message | Meaning |
|---|---|
| `[suite-lock] another suite run holds this machine (pid … worktree …) — queued` | The lock working: something else is mid-suite on THIS machine; your run starts the moment it finishes. Never fires across machines (lock lives in that machine's %TEMP%). **Fires from vitest too now** — same wording, same meaning. |
| `[suite-lock] holder pid … is gone — reclaiming the lock.` (vitest) | A previous full run was hard-killed (Task Manager, closed chat) and left its lock behind; the new run detected the dead PID and took over. Self-healing, nothing to do. |
| `[suite-lock] filelock not installed — machine serialization OFF` | Old venv — run the pip install from step 2. Tests still run fine meanwhile. |
| A test fails with `Timeout >300.0s` + a stack dump | The new hang ceiling naming a wedged test — that test was hanging forever before; now it fails loudly with the culprit's stack. |

## "My machine is much faster — do I still need the locks?"

Asked every time a beefier box joins. **Yes, and the locks are not a weak-laptop workaround.** Keep
the setup identical; the only thing that legitimately varies per machine is the `-n` value above.

Two different things get called "parallel", and only one of them is locked:

| | What it is | Locked? |
|---|---|---|
| **Inside one suite** | `pytest -n auto --dist loadfile`; vitest's default worker pool (no `maxWorkers` cap is set) | **No — always on**, and it already claims every core |
| **Between whole-suite runs** | two lanes each starting a FULL run on one machine | **Yes** — one full pytest run and one full vitest run at a time |

Because a single run already saturates the cores, a second concurrent full run oversubscribes by the
same *proportion* on 8 cores or 32. More cores make each run finish sooner; they do not stop two runs
from fighting. Serializing whole runs is therefore near throughput-optimal on any machine — it costs
**latency to whoever asks second**, not total throughput, and that run starts the instant the first ends.

**What a bigger machine does buy you, for free:** the two locks are separate files
(`agy_aviationchat_suite.lock` vs `agy_aviationchat_vitest_suite.lock`), so **backend and frontend
suites may already run at the same time**. On the 8-core laptop that cross-stack overlap was still
risky — a concurrent backend suite stretched the frontend run 222 s → 322 s and blew a 15 s timeout on
a 2.1 s test. With plenty of RAM and fast NVMe that is exactly the case that becomes safe. That is the
real concurrency win, and it needs no configuration.

**Override, if you ever truly want concurrent full runs:** `AGY_SUITE_LOCK=0` — the same variable for
BOTH stacks. Set it per-invocation; never default it anywhere.

## Failure signatures → fixes

| Symptom | Cause | Fix |
|---|---|---|
| `unrecognized arguments: -n` | venv predates the xdist pin | `pip install -r backend/requirements.txt` |
| `No module named pytest` right after pulling | you caught a venv mid-rebuild, or step 2 was interrupted | re-run step 2 fully |
| VS Code can't find the interpreter / imports unresolved after the rebuild | stale interpreter path cached | the `python_inter_venv_fix` skill covers this exact case |
| Weird failures only on ONE machine | that machine skipped this checklist — venv still 3.14 | run CHECK 1; rebuild |

## The vitest side (nothing to rebuild — read once, then forget)

The frontend twin of the pytest lock, added late 2026-08-01 (`cae06a78`). Other machines get it
for free with `git pull` — it is ordinary tracked TypeScript, zero new dependencies, and the lock
itself lives per-machine in `%TEMP%\agy_aviationchat_vitest_suite.lock` (never travels, never
conflicts across machines). What it does, so its messages don't surprise you:

- **Full `vitest run`s queue per machine** — a second full run prints the queued message (same
  wording as pytest's) and starts the instant the first finishes.
- **Scoped runs never wait** — `npx vitest run <file-or-pattern>` starts instantly, always.
  Watch mode never takes the lock either.
- **Dead holders self-heal** — the lock records the holder's PID; a waiter that finds the PID
  dead reclaims in ~5s (verified with a real Task-Manager kill). No filelock/kernel magic here:
  Node has none, so it's an atomic `mkdir` + PID liveness check.
- **`AGY_SUITE_LOCK=0` bypasses it** (the SAME env var bypasses the pytest lock — one switch,
  both stacks; never default it anywhere).
- **It's an economizer, not a gate** — if the lock can't even be created it warns and runs anyway.
  45-minute ceiling, then it errors naming the holder and the lock path to delete.
- Only prerequisite is a current `node_modules` (`npm ci` in `frontend/` if vitest is missing) —
  which every machine needed anyway.

⚠️ **The two locks are per-STACK by design** — a backend pytest run and a frontend vitest run
still share the box, and that overlap alone measurably slows the frontend (222s→322s) enough to
trip the load-sensitive 15s testTimeout on jsdom-heavy specs. If you see exactly one frontend
timeout flake while the backend suite is churning, re-run it; the real fix (per-file jsdom/
transform cost) is a filed follow-on in AGY active-context.

## The full playbook — how to do this again

> **Commands below are PowerShell/Windows**, written from the 2026-08-01 run and deliberately left as
> the original record. The *procedure* is OS-independent; on macOS substitute per the macOS column
> above (`python3.11`, `backend/.venv/bin/python`, `grep -E` for `Select-String`, `rm -rf` for
> `Remove-Item -Recurse -Force`, `ps aux | grep` for `Get-Process`).

The sections above cover a machine *catching up*. This section is the complete procedure for
**repeating the whole operation** — the next interpreter bump (3.12, 3.13…), another project, or
any "the env drifted and nobody noticed" crisis. It is written from the 2026-08-01 run, where every
step below was either done right the first time or paid for the hard way. Traps are marked ⚠️.

### Phase 0 — Diagnose before touching anything

```powershell
py -0p                                                        # every interpreter on the machine
Get-Content backend\.venv\pyvenv.cfg                          # version = ? command = ? (provenance!)
Select-String "python-version" .github\workflows\pr-check.yml # what CI runs
Select-String "^FROM" Dockerfile                              # what prod runs
Select-String "requires-python|target-version" pyproject.toml # what is DECLARED
```

All five must name the same version. Any disagreement = drift. Two extra tells:
- `pyvenv.cfg`'s `command =` names a path that no longer exists → the venv was carried through a
  repo move and is a time bomb (stale `.pyc` tracebacks, IDE interpreter confusion).
- More than one venv (`.venv` at repo root, `.venv311`, anything) → delete down to ONE
  (`backend/.venv`) as part of the job, whatever else you do.

⚠️ **pytest enforces none of this.** Only pip (at install) and the CI assert step check
`requires-python`. A wrong venv runs tests silently forever. That is why Phase 0 is manual.

### Phase 1 — Check for live consumers, then STAGE, never swap hot

```powershell
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
  Where-Object { $_.CommandLine -match 'AGY_AVIATIONCHAT' } |
  Select-Object ProcessId, CommandLine
```

⚠️ **Non-zero result = STOP.** Deleting/rebuilding a venv under a running suite produces
unattributable false-REDs across every lane using it — this is exactly how "the whole company is
blocked" happened on 2026-08-01. Also announce a freeze: **no team starts a test run until the
swap is done** (the suite lock queues big runs, but a freeze keeps small runs out too).

Build the new env BESIDE the old one, verify it cold, and only then swap:

```powershell
py -3.11 -m venv backend\.venvSTAGE
backend\.venvSTAGE\Scripts\python.exe -m pip install -r backend\requirements.txt
backend\.venvSTAGE\Scripts\python.exe -m pip check          # "No broken requirements found"
# when the process check above returns ZERO rows:
Rename-Item backend\.venv backend\.venv.oldXXX              # park as rollback, don't delete yet
Rename-Item backend\.venvSTAGE backend\.venv
```

⚠️ First-time installs for a NEW interpreter download the entire wheel set fresh (different
`cp3XX` tags — torch alone is ~2.5 GB). Budget 15–30 min; do not assume a hung pip.

### Phase 2 — Prove it, one variable at a time

- **Serial only** (`-q --timeout=300`, no `-n`) while the interpreter is the variable under test —
  a parallel failure is ambiguous between "new Python" and "xdist".
- ⚠️ **Full output to a persistent file, NEVER `| tail`:**
  `... -m pytest backend\tests -q --timeout=300 -rf > proof.log 2>&1`
  Every `| tail` run that dies early (kill, crash, IDE restart) loses the failure names. This cost
  us three diagnostic runs in one night.
- ⚠️ **Chat/IDE restarts kill agent-launched runs** (they are child processes). If a restart is
  possible, launch detached via Task Scheduler:
  ```powershell
  # write a one-line .cmd that cd's to the repo and runs pytest > log, then:
  schtasks /create /f /tn "proof-run" /sc once /st 23:59 /tr "%TEMP%\proof.cmd"
  schtasks /run /tn "proof-run"     # fires now, survives everything
  schtasks /delete /tn "proof-run" /f   # cleanup afterwards
  ```
- **Pass = EXACT totals match** the known-good baseline (passed AND skipped AND failed). Run it
  more than once — three passes closed it here. Any new failure is a real finding: capture the
  traceback; it is a version incompatibility, not a reason to roll back blind.

### Phase 3 — Declare it so drift can never be silent again

Already done for AGY (keep on the next bump): `requires-python` in `pyproject.toml` under
`[project]`, and the `pr-check.yml` "Assert runner Python satisfies requires-python" step, which
reads the declaration instead of restating the number — so the pin and the declaration cannot
drift apart. Prove the assert **bites both ways** (passes on the right version, exits 1 on the
wrong one) before trusting it.

### Phase 4 — Clean up, or the leftovers bite

⚠️ **Delete the parked/staging venvs once green** — they are not harmless:
- Any `.venv*` under `backend/` lands inside `test_grading_event_governance_gate`'s `rglob` scan
  and can triple it (~16k → ~48k files), blowing the 300s ceiling. This produced a real timeout.
- A leftover venv is exactly the "wrong venv" trap (S2) that manufactured a phantom known-failure
  which sat on the sprint board for two close-outs.
- `.gitignore` carries `.venv*/` so they never show as 10k phantom changes in the IDE again.

### Phase 5 — Propagate

1. Commit + push the config changes (explicit paths — the 2026-08-01 sweep-commit `c887257d` is
   the counterexample to imitate never).
2. Check off every machine at the top of THIS doc as it runs the 5-minute fix + 4 checks.
3. If any skill/spec was corrected during the work: **upstream to the lobby `.agents/` master
   FIRST, then `/sync-agents`** — ⚠️ syncing while the master is stale overwrites the corrected
   project copy with the old wrong one (happened tonight; caught).
4. One line to every active lane: "merge `origin/main_debug` before your next test run."

### Reference — where each fact lives

| Fact | Source of truth |
|---|---|
| Which runner flags are canonical (serial vs `-n auto`) | runner AIDEV-NOTE in `backend/requirements.txt` |
| Declared interpreter | `pyproject.toml` `requires-python` |
| The full 2026-08-01 record (evidence, measurements, traps) | `_artifacts/_main/2026-08-01_python-env-fix/walkthrough.md` |
| Why the gate went parallel, and the venv-naming hazard | `_artifacts/quick_fixes/quick-fix-1.1-xdist-tail-hang/walkthrough.md` (2026-08-03) |
| Machine-wide suite lock, backend (queued ≠ hung) | root `conftest.py` |
| Machine-wide suite lock, frontend | `frontend/vitest.global-setup.ts` (wired in `frontend/vitest.config.ts`) |
| Frontend flake driver (jsdom setup/transform ≈85% of wall clock) | AIDEV-NOTE in `frontend/vitest.config.ts` + AGY active-context follow-on |

## Related facts

- ~~Leftover staging venvs on the laptop~~ — both `backend\.venv311` (staging) and
  `backend\.venv.old314` (rollback) were deleted after the migration verified. Other machines
  never had them; if you see any `.venv*` variant anywhere, it's cruft — delete it.
- CI is immune to all of this (fresh install every run, and the new
  "Assert runner Python satisfies requires-python" step fails loudly on drift).
- Full machine-to-machine moves (secrets etc.) are a separate checklist —
  [`new_machine-migration-guide.md`](new_machine-migration-guide.md) in this same folder
  (`_secrets/master.env` bundle; replaces the old `env-migration-guide.md`).

**Close this task** by checking off every machine at the top, after its CHECK 4 passes.
