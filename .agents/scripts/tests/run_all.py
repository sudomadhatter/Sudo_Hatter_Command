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
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = sorted(p.name for p in HERE.glob("test_*.py"))

# Every child still running, so an interrupt can END them rather than wait them out.
_RUNNING: set[subprocess.Popen] = set()
_RUNNING_LOCK = threading.Lock()


def run_one(name: str) -> tuple[str, int, str]:
    p = subprocess.Popen([sys.executable, str(HERE / name)], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, errors="replace")
    with _RUNNING_LOCK:
        _RUNNING.add(p)
    try:
        out, err = p.communicate()
    finally:
        with _RUNNING_LOCK:
            _RUNNING.discard(p)
    return name, p.returncode, (out or "") + (err or "")


def stop_running() -> int:
    """Terminate every child still running; returns how many were told to stop."""
    with _RUNNING_LOCK:
        procs = list(_RUNNING)
    for p in procs:
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
    failures: list[str] = []
    ex = ThreadPoolExecutor(max_workers=jobs)
    futs = [ex.submit(runner, f) for f in files]
    try:
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
    except KeyboardInterrupt:
        for f in futs:
            f.cancel()                                  # queued files never start
        ex.shutdown(wait=False, cancel_futures=True)
        stop_running()                                  # running children end now
        raise
    ex.shutdown(wait=True)
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Run every workflow-script test.")
    ap.add_argument("--jobs", type=int, default=None,
                    help="how many test files to run at once (default: CPU count)")
    ap.add_argument("--serial", action="store_true",
                    help="one file at a time — the escape hatch, equivalent to --jobs 1")
    args = ap.parse_args()

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
