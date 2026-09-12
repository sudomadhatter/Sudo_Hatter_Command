"""N9: `ceremony_tier` ignores the repo's own declared rows and always uses GENERIC."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path("/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/SCC-451-inert-paths")
TP = REPO / ".agents/scripts/task_preflight.py"

OLD = """    hits = (sc.overlaps(rels, rows, fragments=False) if rows
            else sc.overlaps(rels, list(sc.GENERIC), fragments=True))"""
NEW = """    hits = sc.overlaps(rels, list(sc.GENERIC), fragments=True)"""

original = TP.read_text(encoding="utf-8")
if original.count(OLD) != 1:
    print(f"anchor not unique/found: {original.count(OLD)}")
    raise SystemExit(1)

try:
    TP.write_text(original.replace(OLD, NEW), encoding="utf-8")
    p = subprocess.run([sys.executable, str(REPO / ".agents/scripts/tests/test_inert_paths.py")],
                       capture_output=True, text=True, cwd=REPO)
    rc = p.returncode
    failed = [ln for ln in p.stdout.splitlines() if ln.startswith("[FAIL]")]
finally:
    TP.write_text(original, encoding="utf-8")

print("KILLED" if rc != 0 else "SURVIVED  <- the pin is VACUOUS")
for ln in failed[:6]:
    print("   ", ln[:150])

p2 = subprocess.run([sys.executable, str(REPO / ".agents/scripts/tests/test_inert_paths.py")],
                    capture_output=True, text=True, cwd=REPO)
print(f"restored: exit={p2.returncode}")
raise SystemExit(0 if rc != 0 and p2.returncode == 0 else 1)
