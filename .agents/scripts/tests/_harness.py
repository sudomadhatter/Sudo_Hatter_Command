"""Shared plumbing for the workflow-script tests.

Stdlib only and no pytest, matching the scripts under test — these have to run on a fresh
machine before anything is installed, which is exactly when the workflow scripts get used.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

NO_MATCH = 3
"""Exit code for a filter that selected NOTHING to run (SCC-156).

Distinct from 1 on purpose. A mutation sweep reads a non-zero exit as "the mutant was
killed" and a zero as "it survived" — so a typo'd `--case` label, a file that declares no
blocks, or a block that matches and asserts nothing must be neither. They are an error in
the SWEEP, not evidence about the code, and 3 is what says so.
"""


def _case_filter() -> str | None:
    """`--case <substring>` / `--case=<substring>`, read straight off argv.

    No argparse: these files are run bare by the sweep, by run_all and by hand, and an
    arg parser that rejects an unknown flag would turn a harmless extra argument into a
    dead suite. Anything that is not --case is ignored.
    """
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--case" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--case="):
            return a.split("=", 1)[1]
    return None


class Cases:
    def __init__(self, title: str) -> None:
        self.title = title
        self.rows: list[tuple[str, bool, str]] = []
        self.filter = _case_filter()
        self.blocks_seen = 0
        self.blocks_run = 0
        print(f"== {title} ==")

    def block(self, label: str) -> bool:
        """Guard for one named block of cases: `if c.block("B · the target"): ...`

        ⛔ An `if`, never a context manager. These files are written as sequential inline
        `with TempDir():` blocks rather than functions, and a context manager cannot skip
        its own body — `__enter__` returning False still runs everything under it. The
        truthiness of a plain call is the only thing that can.

        Unfiltered, every block runs and this is always True, so a file reads and behaves
        exactly as it did before it was wired.
        """
        self.blocks_seen += 1
        if self.filter is None or self.filter.lower() in label.lower():
            self.blocks_run += 1
            return True
        return False

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        self.rows.append((name, bool(ok), detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))

    def finish(self) -> int:
        failed = [n for n, ok, _ in self.rows if not ok]
        print(f"-- {len(self.rows) - len(failed)}/{len(self.rows)} passed --")
        if failed:
            print("FAILED: " + ", ".join(failed))
        if self.filter is not None:
            print(f"-- filter '{self.filter}': matched "
                  f"{self.blocks_run}/{self.blocks_seen} blocks --")
            if not self.blocks_run or not self.rows:
                why = ("no block matched" if not self.blocks_run
                       else "the matched block ran no cases")
                print(f"NO CASES RAN: {why} — this is a filter error, not a result.")
                return NO_MATCH
        return 1 if failed else 0


def run_script(name: str, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(SCRIPTS / name), *args],
                       capture_output=True, text=True, errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


class TempDir:
    """A scratch directory that cleans up even after a chmod'd read-only file."""

    def __enter__(self) -> Path:
        self.path = Path(tempfile.mkdtemp(prefix="wfscripts-"))
        return self.path

    def __exit__(self, *exc: object) -> None:
        def force(func, path, _info):  # read-only files (and .git objects) on Windows
            Path(path).chmod(0o700)
            func(path)
        shutil.rmtree(self.path, onerror=force)
