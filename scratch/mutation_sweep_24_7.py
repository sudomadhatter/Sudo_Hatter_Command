"""Story 24.7 Step-4 mutation sweep — ONE run, code-derived mutants, then restore.

Declared table (mutant · file · the NAMED case that must kill it):
  M1 INVERT the checkride-day boundary (`>= today` -> `> today`)
     · backend/agents/hr/lifecycle.py
     · test_today_does_not_fire (TestDateMatrixAndTodaySeam)
  M2 DELETE the consumed-marker check (trigger re-fires forever)
     · backend/agents/hr/lifecycle.py
     · test_date_passed_consumed_never_refires (TestLifecycleStateMachine)
  M3 NARROW the deferral exit (deferred row rests DORMANT instead of INCOMPLETE)
     · backend/agents/hr/lifecycle.py
     · test_date_passed_consumed_and_deferred_re_arms_as_incomplete
  M4 INVERT the completeness gate (partial profiles rest DORMANT)
     · backend/agents/hr/lifecycle.py
     · test_partial_profile_is_incomplete (TestLifecycleStateMachine)
  M5 DELETE the success guard in the SSE mapper (failed tool calls would emit events)
     · backend/agents/hr/agent.py
     · test_failed_calls_emit_nothing (TestSseAdapterEventMapping)

KILL = the named suite file exits non-zero under the mutant. After the sweep the
sources are restored byte-for-byte and re-checked.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "Projects/AGY_AVIATIONCHAT/.claude/worktrees/24-7-coleman-adk-rebuild"
BACKEND = ROOT / "backend"
PY = BACKEND / ".venv/Scripts/python.exe"
TESTFILE = "tests/agents/test_hr_lifecycle_24_7.py"

MUTANTS = [
    (
        "M1 checkride-day boundary inverted",
        BACKEND / "agents/hr/lifecycle.py",
        "    if checkride >= today:",
        "    if checkride > today:",
        "test_today_does_not_fire",
    ),
    (
        "M2 consumed-marker check deleted",
        BACKEND / "agents/hr/lifecycle.py",
        "    if profile.get(DATE_PASSED_CONSUMED_KEY):",
        "    if False:",
        "test_date_passed_consumed_never_refires",
    ),
    (
        "M3 deferral exit narrowed to DORMANT",
        BACKEND / "agents/hr/lifecycle.py",
        "        if profile.get(DATE_PASSED_DEFERRED_KEY):\n            return INCOMPLETE",
        "        if profile.get(DATE_PASSED_DEFERRED_KEY):\n            return DORMANT",
        "test_date_passed_consumed_and_deferred_re_arms_as_incomplete",
    ),
    (
        "M4 completeness gate inverted",
        BACKEND / "agents/hr/lifecycle.py",
        "below (FR12).\n        return INCOMPLETE",
        "below (FR12).\n        return DORMANT",
        "test_partial_profile_is_incomplete",
    ),
    (
        "M5 SSE mapper success guard deleted",
        BACKEND / "agents/hr/agent.py",
        "        if not isinstance(response, dict) or response.get(\"success\") is not True:\n            return None",
        "        if not isinstance(response, dict):\n            return None",
        "test_failed_calls_emit_nothing",
    ),
]


def run_suite() -> int:
    proc = subprocess.run(
        [str(PY), "-m", "pytest", TESTFILE, "-q", "--no-header",
         "-p", "no:cacheprovider", "--timeout=120"],
        cwd=str(BACKEND), capture_output=True, text=True,
    )
    return proc.returncode


def main() -> int:
    originals = {}
    results = []
    try:
        for name, path, old, new, killer in MUTANTS:
            text = path.read_text(encoding="utf-8")
            originals[path] = text
            if old not in text:
                results.append((name, "DEFECTIVE (anchor not found)"))
                continue
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            code = run_suite()
            outcome = "KILLED" if code != 0 else "SURVIVED"
            results.append((name, f"{outcome} by {killer}"))
            path.write_text(originals[path], encoding="utf-8")
    finally:
        for path, text in originals.items():
            if path.read_text(encoding="utf-8") != text:
                path.write_text(text, encoding="utf-8")
                print(f"RESTORED {path}")
    print()
    print("MUTANT TABLE")
    survived = 0
    for name, outcome in results:
        print(f"  {outcome:38s}  {name}")
        if "SURVIVED" in outcome or "DEFECTIVE" in outcome:
            survived += 1
    print(f"survivors: {survived}")
    # closing green: the suite bare, unfiltered, once
    final = run_suite()
    print(f"closing green exit code: {final}")
    return 1 if survived or final != 0 else 0


if __name__ == "__main__":
    sys.exit(main())
