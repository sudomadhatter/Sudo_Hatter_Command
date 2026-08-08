"""Run every workflow-script test. Stdlib only; no pytest, no install step.

    python3 .agents/scripts/tests/run_all.py

`python3`, not `python` — there is no bare `python` on the Mac, in a script or a login shell.
Test files are auto-discovered (`test_*.py`), so a new one joins the suite with no wiring.

Exit 0 only if every case in every file passed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = sorted(p.name for p in HERE.glob("test_*.py"))


def main() -> int:
    failures = []
    for name in FILES:
        r = subprocess.run([sys.executable, str(HERE / name)],
                           capture_output=True, text=True, errors="replace")
        print((r.stdout or "") + (r.stderr or ""), end="")
        if r.returncode != 0:
            failures.append(name)
        print()
    print("=" * 60)
    print(f"{len(FILES) - len(failures)}/{len(FILES)} files passed"
          + (f"  FAILED: {', '.join(failures)}" if failures else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
