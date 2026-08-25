"""Run every workflow-script test. Stdlib only; no pytest, no install step.

    python3 .agents/scripts/tests/run_all.py              # Mac
    python  .agents/scripts/tests/run_all.py              # PC (python.org has no `python3`)
    python3 .agents/scripts/tests/run_all.py --serial     # one file at a time
    python3 .agents/scripts/tests/run_all.py --jobs 4     # a fixed width

This system is driven from two machines and they disagree on the name. Nothing here hardcodes
it — `sys.executable` carries whichever interpreter launched this file down to the child test
processes, and the git hooks probe `python3 -> python -> py`. Only the command YOU type differs.
Test files are auto-discovered (`test_*.py`), so a new one joins the suite with no wiring.

Files run CONCURRENTLY by default (SCC-156). The parallelism is threads over the SAME
per-file subprocesses this always used — the work happens in child processes, so the GIL is
irrelevant and there is no `fork` semantics to differ on Windows. Each file already owned its
own TempDirs, its own env and its own cwd because it always ran in its own process; that is
what makes them safe to overlap, and `--serial` is the escape hatch when a suspected
interaction needs ruling out.

⛔ What parallelism may NOT change, because CI, four command bodies and `gate_receipt`'s
classifier all read them: the summary line `N/N files passed`, the `FAILED: …` list, the exit
code, and the ALPHABETICAL order of the printed transcript. Output is buffered per file and
emitted in file order, never in completion order — a transcript that reshuffles run to run
cannot be diffed against a previous one.

Exit 0 only if every case in every file passed. Exit 2 = this runner was misconfigured (a bad
--jobs) or found NOTHING to run, which is not a statement about the suite either way. Ctrl-C
stops the run: queued files are cancelled, never started (SCC-156 review #4/#7, fixed SCC-160).
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from pathlib import Path

# SCC-190 · the tree guard. ⛔ OPTIONAL BY CONSTRUCTION: this runner is copied into bare temp
# dirs by its own tests and by anything probing it, and a guard that cannot find its helper must
# degrade to silence, never take the suite down with it. A runner that refuses to start is a
# worse defect than the one the guard exists to prevent.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import wf_common as wf  # noqa: E402
except Exception:           # noqa: BLE001 - any import failure means "no guard", not "no suite"
    wf = None

HERE = Path(__file__).resolve().parent
FILES = sorted(p.name for p in HERE.glob("test_*.py"))

# Every child still running, so an interrupt can END them rather than wait them out.
_RUNNING: set[subprocess.Popen] = set()
_RUNNING_LOCK = threading.Lock()
_STOPPING = False   # set by stop_running(); a worker that has not spawned yet must not


def run_one(name: str) -> tuple[str, int, str]:
    # The Popen window: a worker between "future started" and "child registered" is
    # invisible to both `cancel()` and `stop_running()`'s snapshot (review, Blind Hunter).
    # Two checks close it — refuse to spawn once stopping began, and if the stop landed
    # while this child was being spawned, terminate it the moment it is registered.
    if _STOPPING:
        return name, 130, f"{name}: not started (interrupted)\n"
    # ⛔ PARENT AND CHILD MUST SHARE AN ENCODING - that invariant is real, and mismatching it
    # turned every `·` into U+FFFD which the parent's own stdout then could not encode. What
    # was wrong was WHICH encoding: this pinned both ends at the LOCALE, and on the PC that is
    # cp1252, which cannot represent `⛔` (U+26D4) or `⭐` (U+2B50) - characters the suite's own
    # case NAMES carry. So the child raised UnicodeEncodeError mid-print and died, and the file
    # was scored as one ordinary failure. 22 files were red for this and this alone; the runs
    # that read 61/61 were made in a shell that happened to export PYTHONIOENCODING=utf-8.
    # Both ends are now pinned at UTF-8 - the only encoding that can hold what the suite prints.
    # `os.environ` is set once in `main()` (the children inherit it, as WF_ON_MAIN already does).
    p = subprocess.Popen([sys.executable, str(HERE / name)], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True,
                         encoding="utf-8", errors="replace")
    with _RUNNING_LOCK:
        _RUNNING.add(p)
        late = _STOPPING
    if late:
        try:
            p.terminate()
        except OSError:
            pass
    try:
        out, err = p.communicate()
    finally:
        with _RUNNING_LOCK:
            _RUNNING.discard(p)
    return name, p.returncode, (out or "") + (err or "")


def stop_running(grace: float = 1.0) -> int:
    """End every child still running; returns how many were told to stop.

    POSIX: SIGINT first, so a child unwinds its `with TempDir():` blocks (a plain terminate
    leaks every scratch repo the interrupted files had open), then `terminate()` for any
    still alive after `grace`. Windows has no SIGINT to send a child: terminate.
    """
    global _STOPPING
    with _RUNNING_LOCK:
        _STOPPING = True
        procs = list(_RUNNING)
    if os.name != "nt":
        for p in procs:
            try:
                p.send_signal(signal.SIGINT)
            except OSError:
                pass
        for p in procs:
            try:
                p.wait(timeout=grace)
            except subprocess.TimeoutExpired:
                pass
            except OSError:
                pass
    for p in procs:
        if p.poll() is None:
            try:
                p.terminate()
            except OSError:
                pass
    return len(procs)


def run_pool(files: list[str], jobs: int, runner=run_one) -> list[str]:
    """Run `files` through a pool of `jobs`, print each transcript in FILE order, and
    return the names that failed. Factored out so the interrupt path is testable without
    a signal: a `runner` that raises KeyboardInterrupt stands in for Ctrl-C.

    ⛔ The interrupt path does TWO things, and the second is the one that matters.
    `Executor.map` already cancels not-yet-started futures when its iteration dies, so
    `cancel_futures=True` alone was never the whole fix the SCC-156 review named: with N
    workers each mid-file, `__exit__`'s `shutdown(wait=True)` still WAITED for all N children
    to finish — an 88 s suite that would not stop. So on interrupt: cancel the queue (nothing
    more starts) AND `stop_running()` (every child in flight is terminated). Measured, not
    believed: the case that pins this drives a real interrupt into a pool of sleeping children.
    """
    global _STOPPING
    _STOPPING = False          # a fresh pool starts un-stopped (the latch is per run)
    failures: list[str] = []
    ex = ThreadPoolExecutor(max_workers=jobs)
    futs: list = []
    try:
        # Submits live INSIDE the try: an interrupt during submission must take the same
        # exit as one during the wait, or it escapes with the "cancelled" message printed
        # and every file quietly running to completion under the atexit join.
        for f in files:
            futs.append(ex.submit(runner, f))
        # Results are read in INPUT order, so the transcript stays alphabetical however the
        # children finish. Each file's output lands whole — never interleaved mid-line.
        # ⛔ A short-timeout poll, not a bare `.result()`: a main thread parked in a lock
        # wait does not see an interrupt until a future completes (and never, on Windows),
        # which is what made Ctrl-C land only after the in-flight children finished. Waking
        # four times a second costs nothing and makes the interrupt land within 250 ms.
        for fut in futs:
            while True:
                try:
                    name, rc, out = fut.result(timeout=0.25)
                    break
                except FuturesTimeout:
                    continue
            print(out, end="")
            if rc != 0:
                failures.append(name)
            print()
    except BaseException:
        # KeyboardInterrupt - and ANY runner exception (a Popen OSError: EMFILE under a
        # huge --jobs, a missing interpreter). Either way nothing more may start and
        # nothing may keep running behind a traceback.
        for f in futs:
            f.cancel()                                  # queued files never start
        ex.shutdown(wait=False, cancel_futures=True)
        stop_running()                                  # running children end now
        raise
    ex.shutdown(wait=True)
    return failures


def main() -> int:
    # ⛔ PIN BOTH ENDS OF THE PIPE AT UTF-8 BEFORE ANYTHING PRINTS OR SPAWNS (SCC-321).
    # Windows defaults a NON-CONSOLE stdout - which is exactly what every child here gets - to
    # cp1252, and cp1252 cannot encode `⛔`/`⭐`, which this suite's own case names carry. The
    # child raises UnicodeEncodeError mid-print and is scored as an ordinary red; the parent
    # then cannot print the child's output either. Setting it in `os.environ` is what reaches
    # the children: `Popen` passes no `env=`, so they inherit this process's, as WF_ON_MAIN
    # already relies on. Windows-only - on POSIX the streams are already UTF-8 and there is
    # nothing to correct, so the Mac stays byte-identical.
    if os.name == "nt":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        for _stream in (sys.stdout, sys.stderr):
            if hasattr(_stream, "reconfigure"):
                _stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Run every workflow-script test.")
    ap.add_argument("--jobs", type=int, default=None,
                    help="how many test files to run at once (default: CPU count)")
    ap.add_argument("--serial", action="store_true",
                    help="one file at a time — the escape hatch, equivalent to --jobs 1")
    ap.add_argument("--on-main", action="store_true",
                    help="allow the run even though this is the MAIN checkout and lane "
                         "worktrees exist (SCC-190: the wrong-tree guard)")
    args = ap.parse_args()

    # ⛔ WHICH TREE IS THIS? Printed FIRST, every run, because the cheapest possible fix for
    # "I ran the suite in the wrong tree" is being told which tree before the suite starts.
    _top, _br, _is_main = (wf.say_tree("run_all", HERE) if wf is not None
                           else (str(HERE), "", False))
    # And a refusal for the one shape that is almost never intentional: standing in the MAIN
    # checkout, on the mainline, while lane worktrees are checked out on chore/* or epic/*.
    # That is lane work being measured against a tree that does not contain it. `--on-main` is
    # the deliberate spelling for the times it IS what you meant (a pre-merge sanity run).
    # ⛔ The body lives in `wf_common.tree_guard` since SCC-240, because the HARNESS asks the
    # same question for every single-file run - one body, so the two answers cannot drift.
    if args.on_main:
        # ⛔ PROPAGATE THE OVERRIDE, or `--on-main` refuses itself through its own children:
        # every test file is harness-based and the harness guards too. `Popen` below passes no
        # `env=`, so the children inherit this process's environment as-is.
        os.environ["WF_ON_MAIN"] = "1"
    if wf is not None:
        _refusal = wf.tree_guard(HERE, who="run_all.py", allow_main=args.on_main,
                                 tag=(_top, _br, _is_main))
        if _refusal:
            print(_refusal, file=sys.stderr)
            return 2

    jobs = 1 if args.serial else (args.jobs if args.jobs is not None
                                  else (os.cpu_count() or 1))
    if jobs < 1:
        # Never silently coerce to 1 or to unlimited: a caller who typed 0 believes
        # something about this run that is not true, and a suite result handed back under
        # that belief is worse than no result.
        print(f"run_all: --jobs must be >= 1 (got {jobs})", file=sys.stderr)
        return 2

    if not FILES:
        # ⛔ Zero files is not a green suite. `0/0 files passed` + exit 0 is the vacuous-green
        # class the harness closed one level down (a filter that selected nothing exits 3);
        # one level up it was still standing (SCC-156 review #7). A tests dir that has lost
        # its files — a bad checkout, a sparse clone, a wrong `--root` — must not authorize
        # a gate SKIP with a PASS receipt.
        print(f"run_all: no test_*.py files found under {HERE} - nothing ran, this is not "
              f"a suite result", file=sys.stderr)
        return 2

    try:
        failures = run_pool(FILES, jobs)
    except KeyboardInterrupt:
        print("\nrun_all: interrupted - queued files cancelled, running children terminated",
              file=sys.stderr)
        return 130
    print("=" * 60)
    print(f"{len(FILES) - len(failures)}/{len(FILES)} files passed"
          + (f"  FAILED: {', '.join(failures)}" if failures else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
