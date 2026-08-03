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


class Cases:
    def __init__(self, title: str) -> None:
        self.title = title
        self.rows: list[tuple[str, bool, str]] = []
        print(f"== {title} ==")

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        self.rows.append((name, bool(ok), detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))

    def finish(self) -> int:
        failed = [n for n, ok, _ in self.rows if not ok]
        print(f"-- {len(self.rows) - len(failed)}/{len(self.rows)} passed --")
        if failed:
            print("FAILED: " + ", ".join(failed))
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
