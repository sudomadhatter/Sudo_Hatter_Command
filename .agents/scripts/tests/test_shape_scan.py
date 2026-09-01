"""shape_scan.py — the measurement the nag is judged by (SCC-369).

This file exists because the FIRST cut of this scanner lied twice, in the same direction:
it counted a `grep` **for** the literal `"git -C"` as a use of it, and it read heredoc BODIES
as commands. Both inflate the violation rate, and an inflated baseline makes the nag look
effective by arithmetic rather than by behaviour. The six-case negative battery below is the
whole point of the file; the positives only prove it is not dead.

⭐ THE STRUCTURAL ASSERTION is `test_detector_is_the_hooks_own`. The scan and the nag MUST
share one detector. If the scanner keeps a private copy, the two drift the moment either is
edited, and the before/after number stops describing what the nag actually catches.

run_all.py executes test files bare (python3 <file>, no pytest), so the __main__ harness at
the bottom is what makes this file COUNT (house scar: suite-red-file-may-have-run-nothing).
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCAN = ROOT / ".agents" / "scripts" / "shape_scan.py"
HOOK = ROOT / ".agents" / "hooks" / "shape-guard.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── the batteries, stated here so a reader sees them without opening the script ──────────────

NEGATIVE = [
    ('grep -rn "git -C" .agents/', "a SEARCH for the literal is not a USE of it"),
    ("cat > f <<'EOF'\ngit -C /repo status\ngit add -A\nEOF", "a heredoc body is DATA"),
    ('echo "run pytest | tail is what NOT to do"', "quoted prose is an argument"),
    ("git commit -F msg.txt", "the correct -F shape"),
    ("python3 x.py > out.txt 2>&1", "a REDIRECT is the remedy, not the fault"),
    ("cd /repo && git status --porcelain", "the shape the rule mandates"),
]

POSITIVE = [
    ('python3 t.py; echo "exit=$?"', {2}),
    ("python3 .agents/scripts/tests/run_all.py | tail -5", {3}),
    ("git -C /repo status", {1}),
    ("cd /tmp && git -C /repo log --oneline", {1}),
    ('git -C /repo status; echo "EXIT=$?"', {1, 2}),
]


def test_negative_battery_scores_zero():
    """⛔ The load-bearing one. Any hit here means the baseline is inflated."""
    scan = _load(SCAN, "shape_scan")
    bad = [(cmd, sorted(scan.classify(cmd)), why) for cmd, why in NEGATIVE if scan.classify(cmd)]
    assert not bad, f"negative controls fired — the scanner is over-counting: {bad}"


def test_positive_battery_fires_with_the_right_rule():
    scan = _load(SCAN, "shape_scan")
    wrong = [(cmd, sorted(scan.classify(cmd)), sorted(want))
             for cmd, want in POSITIVE if scan.classify(cmd) != want]
    assert not wrong, f"positive controls mis-classified (got, wanted): {wrong}"


def test_detector_is_the_hooks_own():
    """⭐ One detector, two callers — asserted by IDENTITY, never by grepping the source.

    ⛔ This check used to be a source-grep, and it could not fail. `"shape-guard.py" in src` is
    satisfied by the file's own DOCSTRING (the house scar `comment-literals-invert-source-grep-tests`),
    and the three "leaked" names are dodged by renaming them. Reproduced by mutation in review: a
    full private re-implementation of all three rules, then DIVERGED from the hook, left the file
    8/8 green while the scan and the nag disagreed on `pytest | tail` (SCC-369 review).

    So ask the object, not the text: the module the scanner actually loaded must BE the hook file.
    """
    scan = _load(SCAN, "shape_scan")
    loaded = getattr(scan, "_HOOK", None)
    assert loaded is not None, "shape_scan.py exposes no _HOOK — it is not loading the nag's detector"
    assert Path(loaded.__file__).resolve() == HOOK.resolve(), (
        f"the scanner's detector is {loaded.__file__}, not the nag's {HOOK} — "
        f"a second copy drifts from what the nag actually catches")


def test_scan_and_hook_agree_on_every_gate_spelling():
    """⛔ The differential the identity check cannot make on its own.

    A fresh fork agrees on the eleven controls by construction; drift is what comes LATER, outside
    them. So walk every spelling the rule-3 regex claims to know and require the two callers to
    return the SAME rule numbers — that is what a private copy cannot survive.
    """
    scan = _load(SCAN, "shape_scan")
    hook = _load(HOOK, "shape_guard")
    spellings = ["python3 .agents/scripts/tests/run_all.py", "python3 -m pytest", "npx vitest run",
                 "ruff check .", "pyrefly check", "npx tsc --noEmit", "npm run test",
                 "npm run lint", "python3 .agents/scripts/tests/test_shape_scan.py"]
    RULE_RE = re.compile(r"\brule (\d)\b")
    disagree = []
    for gate in spellings:
        cmd = f"{gate} | head -20"
        theirs = {int(m.group(1)) for line in hook.violations(cmd)
                  for m in [RULE_RE.search(line)] if m}
        if scan.classify(cmd) != theirs or theirs != {3}:
            disagree.append((cmd, sorted(scan.classify(cmd)), sorted(theirs)))
    assert not disagree, f"scan and hook disagree (cmd, scan, hook): {disagree}"


def test_classify_agrees_with_the_hook_on_every_control():
    """The scan's rule numbers must be the hook's, case by case — not merely the same shape."""
    scan = _load(SCAN, "shape_scan")
    hook = _load(HOOK, "shape_guard")
    for cmd, _why in NEGATIVE:
        assert not hook.violations(cmd), f"hook fires where the scan is silent: {cmd!r}"
    for cmd, want in POSITIVE:
        n = len(hook.violations(cmd))
        assert n == len(want), f"hook found {n} violations, scan wanted {sorted(want)}: {cmd!r}"
        assert scan.classify(cmd) == want, f"scan disagrees with the hook on {cmd!r}"


def test_self_test_flag_runs_both_batteries_and_exits_zero():
    p = subprocess.run([sys.executable, str(SCAN), "--self-test"],
                       capture_output=True, text=True, cwd=str(ROOT), timeout=60)
    assert p.returncode == 0, f"--self-test exited {p.returncode}\n{p.stdout}\n{p.stderr}"
    out = p.stdout
    assert "NEGATIVE CONTROLS: PASS" in out, f"negative battery not reported: {out!r}"
    assert "POSITIVE CONTROLS: PASS" in out, f"positive battery not reported: {out!r}"


def test_json_report_is_well_formed():
    """A live run over whatever transcripts this machine holds. Shape, not a pinned number.

    The BASELINE percentages are evidence for the walkthrough, not an assertion: they move
    with every session that accrues, so pinning them here would rot within a day.
    """
    p = subprocess.run([sys.executable, str(SCAN), "--claude", "--sessions", "3", "--json"],
                       capture_output=True, text=True, cwd=str(ROOT), timeout=180)
    assert p.returncode == 0, f"exit {p.returncode}\n{p.stderr}"
    rep = json.loads(p.stdout)
    assert rep["platform"] == "claude"
    assert isinstance(rep["commands"], int)
    assert set(rep["rates"]) == {"1", "2", "3"}, f"rates must cover all three rules: {rep}"
    for k, v in rep["rates"].items():
        assert 0.0 <= v <= 100.0, f"rate {k} out of range: {v}"


def test_scan_reads_both_stores():
    """The Zoo half is what makes 'are the Zoo seats doing better' answerable at all."""
    src = SCAN.read_text(encoding="utf-8")
    assert "def scan_claude" in src and "def scan_zoo" in src, (
        "shape_scan.py must measure BOTH stores; Zoo has no hook surface, so measurement "
        "is the only instrument it gets")


def test_ingest_actually_reads_a_fixture_store():
    """⛔ THE ONE THAT WAS MISSING. A dead parser scores 0.00% and reads as perfect compliance.

    Reproduced in review three ways — renaming the `Bash` tool filter, breaking the Zoo message
    filter, and pointing HOME at an empty directory — each left the suite 8/8 green while the
    scan reported zero commands. `test_json_report_is_well_formed` runs live and pins no numbers
    (correct — they rot daily), but it never asserted `commands > 0`, so an empty result satisfied
    it. This asserts the arithmetic against a fixture whose answers are known (SCC-369 review).
    """
    scan = _load(SCAN, "shape_scan")
    known = ["git -C /repo status",                      # rule 1
             'python3 x.py; echo "EXIT=$?"',             # rule 2
             "cd /repo && git status --porcelain"]       # clean
    with tempfile.TemporaryDirectory() as td:
        proj = Path(td) / "claude" / "a-project"
        proj.mkdir(parents=True)
        (proj / "t.jsonl").write_text("\n".join(
            json.dumps({"message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": c}}]}})
            for c in known), encoding="utf-8")

        rep = scan.scan_claude(sessions=5, root=str(Path(td) / "claude"))
        assert rep["commands"] == 3, f"the Claude ingest read {rep['commands']} of 3: {rep}"
        assert rep["hits"]["1"] == 1 and rep["hits"]["2"] == 1 and rep["hits"]["3"] == 0, rep
        assert rep["rates"]["1"] == 33.33, f"the arithmetic is wrong: {rep['rates']}"

        zroot = Path(td) / "zoo"
        (zroot / "thread-1").mkdir(parents=True)
        (zroot / "thread-1" / "ui_messages.json").write_text(
            json.dumps([{"say": "command", "text": c} for c in known]), encoding="utf-8")
        zrep = scan.scan_zoo(roots=[zroot])
        assert zrep["commands"] == 3, f"the Zoo ingest read {zrep['commands']} of 3: {zrep}"
        assert zrep["hits"]["1"] == 1 and zrep["hits"]["2"] == 1, zrep


def test_sessions_below_one_is_refused():
    """⛔ `paths[:-1]` is a SLICE, not a count — it WIDENED the window from 1 to 110 sessions."""
    scan = _load(SCAN, "shape_scan")
    for bad in (0, -1):
        try:
            scan.scan_claude(sessions=bad)
        except ValueError:
            continue
        raise AssertionError(f"--sessions {bad} was accepted; a negative slice silently widens "
                             f"the window and corrupts the denominator of a published figure")


def test_script_is_indexed():
    idx = (ROOT / ".agents" / "scripts" / "INDEX.md").read_text(encoding="utf-8")
    assert "shape_scan.py" in idx, ".agents/scripts/INDEX.md has no row for shape_scan.py"


if __name__ == "__main__":
    import traceback
    _fns = [(n, f) for n, f in sorted(globals().items())
            if n.startswith("test_") and callable(f)]
    _failed = []
    for _name, _fn in _fns:
        try:
            _fn()
        except BaseException:
            _failed.append(_name)
            traceback.print_exc()
    print(f"-- {len(_fns) - len(_failed)}/{len(_fns)} passed --")
    # ⛔ `FAILED:` must START the line — mutation_sweep.judge() reads it with startswith().
    if _failed:
        print(f"FAILED: {', '.join(_failed)}")
    sys.exit(1 if _failed else 0)
