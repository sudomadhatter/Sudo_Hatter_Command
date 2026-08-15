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
--jobs), which is not a statement about the suite either way.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = sorted(p.name for p in HERE.glob("test_*.py"))


def run_one(name: str) -> tuple[str, int, str]:
    r = subprocess.run([sys.executable, str(HERE / name)],
                       capture_output=True, text=True, errors="replace")
    return name, r.returncode, (r.stdout or "") + (r.stderr or "")


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

    failures = []
    # ex.map yields in INPUT order, so the transcript stays alphabetical however the
    # children finish. Each file's output lands whole — never interleaved mid-line.
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for name, rc, out in ex.map(run_one, FILES):
            print(out, end="")
            if rc != 0:
                failures.append(name)
            print()
    print("=" * 60)
    print(f"{len(FILES) - len(failures)}/{len(FILES)} files passed"
          + (f"  FAILED: {', '.join(failures)}" if failures else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
