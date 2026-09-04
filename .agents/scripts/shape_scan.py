#!/usr/bin/env python3
"""Measure how often the agents actually break `command-shape.md` — Claude AND Zoo (SCC-369).

This is the instrument the nag is judged by. `shape-guard.py` can only speak to Claude Code
(Zoo Code contributes no hook surface at all — `docs/migrations/terminal-permissions-guide.md`
§"there is no `onDidX` contribution"), so for the Zoo seats **measurement is the only feedback
loop there is**: run this before and after, and "are they doing better" stops being an impression.

⭐ ONE DETECTOR, TWO CALLERS. The rules are NOT re-implemented here — they are imported from
`.agents/hooks/shape-guard.py`, and `test_shape_scan.test_detector_is_the_hooks_own` fails if a
private copy ever creeps back in. A second copy would drift the moment either side is edited, and
the before/after number would stop describing what the nag actually catches.

⛔ WHY THE NEGATIVE BATTERY IS THE POINT. The first cut of this scanner lied twice, in the same
direction: it counted `grep -rn "git -C"` — a SEARCH for the literal — as a use of it, and it read
heredoc BODIES as commands. Both inflate the rate, and an inflated baseline makes the nag look
effective by arithmetic. `--self-test` runs six negative and five positive controls; the negatives
must score exactly zero or this script has no business reporting a number.

Read-only: opens Claude's `~/.claude/projects/*/*.jsonl` transcripts and Zoo's `ui_messages.json`
thread store, writes nothing tracked (module loading still caches bytecode under __pycache__/, which is gitignored).

Usage (Mac: python3 · PC: python):
    python3 .agents/scripts/shape_scan.py --self-test         # the control batteries, no data
    python3 .agents/scripts/shape_scan.py                     # both platforms, human report
    python3 .agents/scripts/shape_scan.py --claude --json     # one platform, machine-readable
    python3 .agents/scripts/shape_scan.py --sessions 25       # widen the Claude transcript window
"""
from __future__ import annotations

import argparse
import collections
import glob
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULE_RE = re.compile(r"\brule (\d)\b")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The nag's own detector. Loaded by path because `shape-guard.py` carries a hyphen and a hook
# is not an importable package — the same reason `zoo_permissions_apply.py` is loaded this way.
_HOOK = _load(ROOT / ".agents" / "hooks" / "shape-guard.py", "shape_guard")

RULE_NAMES = {1: "rule 1  git -C", 2: "rule 2  exit-echo tail", 3: "rule 3  piped gate"}


def classify(command: str) -> set[int]:
    """Which `command-shape.md` rules this command breaks, as the NAG would judge it."""
    return {int(m.group(1)) for line in _HOOK.violations(command)
            for m in [RULE_RE.search(line)] if m}


# ── controls ─────────────────────────────────────────────────────────────────────────────────

NEGATIVE_CONTROLS = [
    ('grep -rn "git -C" .agents/', "a SEARCH for the literal is not a USE of it"),
    ("cat > f <<'EOF'\ngit -C /repo status\ngit add -A\nEOF", "a heredoc body is DATA"),
    ('echo "run pytest | tail is what NOT to do"', "quoted prose is an argument"),
    ("git commit -F msg.txt", "the correct -F shape"),
    ("python3 x.py > out.txt 2>&1", "a REDIRECT is the remedy, not the fault"),
    ("cd /repo && git status --porcelain", "the shape the rule mandates"),
    ("grep -rn run_all.py .agents/ | head -20", "searching FOR a gate name is not RUNNING one"),
    ("sed -n '1,80p' .agents/scripts/tests/test_shape_guard.py | head -40",
     "reading a test file is not piping a gate"),
    ("""grep -rn '; echo "EXIT=$?"' .agents/rules/""",
     "a SEARCH for the tail literal is not a USE of it"),
]

POSITIVE_CONTROLS = [
    ('python3 t.py; echo "exit=$?"', {2}),
    ("python3 .agents/scripts/tests/run_all.py | tail -5", {3}),
    ("git -C /repo status", {1}),
    ("cd /tmp && git -C /repo log --oneline", {1}),
    ('git -C /repo status; echo "EXIT=$?"', {1, 2}),
]


def self_test() -> int:
    fired = [(c, sorted(classify(c)), why) for c, why in NEGATIVE_CONTROLS if classify(c)]
    print("NEGATIVE CONTROLS: "
          + ("PASS — all six score zero" if not fired else f"FAIL — {fired}"))
    missed = [(c, sorted(classify(c)), sorted(w))
              for c, w in POSITIVE_CONTROLS if classify(c) != w]
    print("POSITIVE CONTROLS: "
          + ("PASS — all five fire with the right rule" if not missed else f"FAIL — {missed}"))
    return 1 if (fired or missed) else 0


# ── the two stores ───────────────────────────────────────────────────────────────────────────

def _tally(commands) -> dict:
    hits = collections.Counter()
    examples = collections.defaultdict(list)
    total = 0
    for cmd in commands:
        total += 1
        for rule in classify(cmd):
            hits[rule] += 1
            if len(examples[rule]) < 2:
                examples[rule].append(cmd.replace("\n", " ⏎ ")[:130])
    return {
        "commands": total,
        "hits": {str(r): hits.get(r, 0) for r in (1, 2, 3)},
        "rates": {str(r): round(hits.get(r, 0) / total * 100, 2) if total else 0.0
                  for r in (1, 2, 3)},
        "examples": {str(r): examples.get(r, []) for r in (1, 2, 3)},
    }


def _claude_commands(sessions: int, root: str | None = None):
    """Every `Bash` tool_use command across the N newest transcripts.

    ⛔ `sessions` must be >= 1. `paths[:-1]` is a SLICE, not a count — it returns all but the
    newest transcript, so `--sessions -1` silently WIDENED the window from 1 session to 110 and
    41,853 commands, and the denominator of a figure published as standing law was wrong by 40x
    with no error (SCC-369 review). Rejected at the boundary rather than trusted at the flag.

    `root` exists so the ingest can be tested against a fixture. Without a seam, a parser that
    reads nothing scores 0.00% and is indistinguishable from perfect compliance.
    """
    if sessions < 1:
        raise ValueError(f"--sessions must be >= 1, got {sessions}")
    pattern = os.path.join(root, "*", "*.jsonl") if root else \
        os.path.expanduser("~/.claude/projects/*/*.jsonl")
    paths = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)[:sessions]
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    content = (rec.get("message") or {}).get("content")
                    if not isinstance(content, list):
                        continue
                    for blk in content:
                        if (isinstance(blk, dict) and blk.get("type") == "tool_use"
                                and blk.get("name") == "Bash"):
                            cmd = (blk.get("input") or {}).get("command") or ""
                            if cmd:
                                yield cmd
        except Exception:
            continue
    globals()["_LAST_CLAUDE_SESSIONS"] = len(paths)


def scan_claude(sessions: int = 25, root: str | None = None) -> dict:
    """Claude Code's own transcripts: every `Bash` tool_use across the N newest sessions."""
    rep = _tally(_claude_commands(sessions, root))
    rep["platform"] = "claude"
    rep["sources"] = globals().get("_LAST_CLAUDE_SESSIONS", 0)
    return rep


def _zoo_commands(roots=None):
    if roots is not None:
        return _zoo_from(list(roots))
    try:
        z = _load(ROOT / ".agents" / "scripts" / "zoo_notify.py", "zoo_notify")
        roots = z.store_roots()
    except Exception:
        globals()["_LAST_ZOO_THREADS"] = 0
        return iter(())
    return _zoo_from(roots)


def _zoo_from(roots):
    files = []
    for r in roots:
        files.extend(glob.glob(os.path.join(str(r), "*", "ui_messages.json")))
    globals()["_LAST_ZOO_THREADS"] = len(files)
    for p in files:
        try:
            with open(p, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for m in data:
            if not isinstance(m, dict):
                continue
            if m.get("ask") == "command" or m.get("say") == "command":
                txt = (m.get("text") or "").strip()
                if txt:
                    yield txt


def scan_zoo(roots=None) -> dict:
    """Zoo Code's thread store: every terminal command a seat asked for or announced."""
    rep = _tally(_zoo_commands(roots))
    rep["platform"] = "zoo"
    rep["sources"] = globals().get("_LAST_ZOO_THREADS", 0)
    return rep


# ── reporting ────────────────────────────────────────────────────────────────────────────────

def render(rep: dict) -> None:
    label = {"claude": "CLAUDE CODE (transcripts)", "zoo": "ZOO CODE (thread store)"}
    print(f"\n== {label.get(rep['platform'], rep['platform'])} — "
          f"{rep['sources']} source(s), {rep['commands']} command(s)")
    if not rep["commands"]:
        print("   no commands found — nothing to measure")
        return
    print(f"   {'rule':<26}{'hits':>7}{'rate':>9}")
    print("   " + "-" * 42)
    for r in (1, 2, 3):
        print(f"   {RULE_NAMES[r]:<26}{rep['hits'][str(r)]:>7}{rep['rates'][str(r)]:>8.2f}%")
    for r in (1, 2, 3):
        for ex in rep["examples"][str(r)]:
            print(f"     [{r}] {ex}")


def main() -> int:
    # Windows consoles default to cp1252 and cannot encode this script's own output
    # markers, so a print crashes the run and the operator sees nothing. Same guard as
    # check_maps.py and tests/_harness.py. Never raises: a non-reconfigurable stream
    # (a pipe, a StringIO under test) simply keeps its encoding.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001 - a shim, not a feature
        pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true",
                    help="run the control batteries and exit; reads no store")
    ap.add_argument("--claude", action="store_true", help="measure Claude transcripts only")
    ap.add_argument("--zoo", action="store_true", help="measure the Zoo thread store only")
    ap.add_argument("--sessions", type=int, default=25,
                    help="how many of the newest Claude transcripts to read (default 25)")
    ap.add_argument("--json", action="store_true", help="machine-readable, one object per platform")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    both = not (args.claude or args.zoo)
    reports = []
    if args.claude or both:
        reports.append(scan_claude(args.sessions))
    if args.zoo or both:
        reports.append(scan_zoo())

    if args.json:
        print(json.dumps(reports[0] if len(reports) == 1 else reports, indent=2))
    else:
        for rep in reports:
            render(rep)
        print("\nrule text: .agents/rules/command-shape.md   ·   the nag: "
              ".agents/hooks/shape-guard.py (Claude only — Zoo has no hook surface)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
