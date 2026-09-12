"""Apply each mutant, run its test, assert RED, then ALWAYS restore the original bytes.

A pin that passes with the code broken is not a pin. This proves each new assertion
actually kills the mutant the Test-Adequacy lens found surviving.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path("/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-451-inert-paths")
TP = REPO / ".agents/scripts/task_preflight.py"
SP = REPO / ".agents/scripts/ship_preflight.py"

# (id, file, old_text, new_text, test_file)
MUTANTS = [
    ("R4  ship_preflight: ships = changed (predicate bypassed)",
     SP,
     "    ships = tp.deployable_paths(repo, changed)",
     "    ships = changed",
     "test_ship_preflight.py"),

    ("R3  `lines <= TINY_MAX_LINES` -> `<` (off by one)",
     TP,
     "if lines <= TINY_MAX_LINES and len(counted) <= TINY_MAX_FILES:",
     "if lines < TINY_MAX_LINES and len(counted) <= TINY_MAX_FILES:",
     "test_inert_paths.py"),

    ("N2  `not g` clause dropped from the empty/absolute refusal",
     TP,
     'if not g or g.startswith("/"):',
     'if g.startswith("/"):',
     "test_inert_paths.py"),

    ("N5  served-guard directory arm dropped (parts[:-1] always)",
     TP,
     'segs = q.parts if rel.endswith("/") else q.parts[:-1]',
     "segs = q.parts[:-1]",
     "test_inert_paths.py"),
]


def run(test_file: str) -> int:
    p = subprocess.run([sys.executable, str(REPO / ".agents/scripts/tests" / test_file)],
                       capture_output=True, text=True, cwd=REPO)
    return p.returncode


def main() -> int:
    bad = []
    for mid, path, old, new, test_file in MUTANTS:
        original = path.read_text(encoding="utf-8")
        if old not in original:
            print(f"SKIP   | {mid}\n         anchor not found: {old!r}")
            bad.append(mid)
            continue
        if original.count(old) != 1:
            print(f"SKIP   | {mid}\n         anchor not unique ({original.count(old)}x)")
            bad.append(mid)
            continue
        try:
            path.write_text(original.replace(old, new), encoding="utf-8")
            rc = run(test_file)
        finally:
            path.write_text(original, encoding="utf-8")      # ALWAYS restore
        if rc == 0:
            print(f"SURVIVED | {mid}  <- the pin is VACUOUS")
            bad.append(mid)
        else:
            print(f"KILLED   | {mid}")

    # Prove the tree is back: every test green with no mutant applied.
    print("\n-- restored tree --")
    for test_file in ("test_inert_paths.py", "test_ship_preflight.py"):
        rc = run(test_file)
        print(f"{'ok ' if rc == 0 else 'RED'} | {test_file} exit={rc}")
        if rc != 0:
            bad.append(f"restore {test_file}")

    print("\nRESULT:", "ALL MUTANTS KILLED" if not bad else f"PROBLEMS: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
