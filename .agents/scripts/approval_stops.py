#!/usr/bin/env python3
"""Find the commands that STOPPED the workflow waiting for the operator's approval.

⛔ THE DEFECT THIS EXISTS TO FIX (SCC-407). `/smh-llm-approvals` Step 1 harvested Claude
transcripts for a `tool_result` carrying `is_error` and the text *"doesn't want to proceed with
this tool use"* — that is a command the operator **REFUSED**. But the door's whole purpose is the
opposite event: the trivial command that stopped and waited, which he then approved. An approval he
GRANTS leaves no error record anywhere in the transcript, so the door was structurally blind to
every one of them.

Measured 2026-09-04 on this machine: the old harvest found **one** refusal across 20 sessions and
reported "nothing to harvest" — in a window where **316** calls waited over 20 seconds and **83**
waited over a minute. It was not a tuning problem; it was reading the wrong event.

**Why a stop costs more than the seconds.** It breaks the prompt cache. The turn resumes against a
cold cache and the whole context is billed again, so each interruption is charged twice: once in the
operator's attention, once on the invoice. That is why the ranking here is by TIME WAITED as well as
by count — the expensive stop is not the frequent one, it is the one he was away from.

Three signals, because no single one is sufficient:

  1. LATENCY  — pair each Bash `tool_use` with its `tool_result` and measure the gap. Direct
     evidence a human was asked. Noisy on its own: `gh pr checks --watch` legitimately blocks for
     ten minutes with nobody asked.
  2. COVERAGE — replay the command against the RENDERED allow list. Structural, and predictive: an
     uncovered command has not stopped him yet only because it has not run yet.
  3. CLASSIFIER — a second `is_error` string, *"denied by the Claude Code auto mode classifier"*,
     that the old harvest never looked for at all. It fired three times in the session that found
     this bug.

Latency AND uncovered together is the high-confidence set: it waited, and there is a reason it
would. Read-only; writes nothing; exits 0 with no findings.
"""
from __future__ import annotations

import argparse
import collections
import datetime as _dt
import glob
import json
import os
import re
import sys
from pathlib import Path

# The two `is_error` strings that mean "this never ran". Neither is the common case, which is why
# reading only these is what broke the door.
REFUSED_BY_OPERATOR = "doesn't want to proceed with this tool use"
REFUSED_BY_CLASSIFIER = "denied by the Claude Code auto mode classifier"

# A command that waited at least this long almost certainly waited on a person. Median across 6,646
# paired calls on this machine is 0.3s and p90 is 4.4s, so 20s sits far outside the working
# distribution rather than at its edge.
DEFAULT_WAIT = 20.0


def _iso(rec: dict) -> float | None:
    t = rec.get("timestamp")
    if not t:
        return None
    try:
        return _dt.datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def allow_prefixes(repo: Path) -> list[str]:
    """The Bash prefixes the RENDERED Claude list currently approves.

    Read from the rendered file rather than from families.json: the rendered list is what Claude
    actually decides with, and a source that has not been rendered yet would over-report coverage.
    """
    cfg = json.loads((repo / ".claude" / "settings.json").read_text(encoding="utf-8"))
    out = []
    for rule in cfg.get("permissions", {}).get("allow", []):
        if rule.startswith("Bash(") and rule.endswith(")"):
            body = rule[5:-1]
            for suffix in (":*", " *"):
                if body.endswith(suffix):
                    body = body[: -len(suffix)]
                    break
            out.append(body)
    return out


# Shell preamble that is never the reason a prompt appeared — it is scaffolding around the command
# that was. Skipped when choosing the head to REPORT; still judged for coverage.
_PREAMBLE = re.compile(
    r"^(set|export|cd|for|while|until|if|then|else|elif|fi|do|done|case|esac|exit|local|shift"
    r"|trap|echo|printf|:"
    # Python statement keywords. Not shell scaffolding but the same problem: a heredoc whose
    # marker the `<<` cut did not reach (a nested quote, a `$(cat <<X)` wrapper) leaks its BODY
    # in as candidate segments, and `import json` then ranks as one of the operator's costliest
    # interruptions. No allow rule can be written for a line of Python.
    r"|import|from|def|class|return|pass|raise|assert|with|try|except|finally|yield|elif)\b"
)

# A wait this command explains by itself. `timeout 900 …` blocking for 900s is the command working,
# not the operator being asked, and crediting it would put the noisiest rows at the top of a report
# whose whole point is ranking by cost.
#
# ⛔ `\d+`, NOT `\d`, and no trailing `\b`. Written as `\b(timeout\s+\d|…)\b` it matched `timeout 9`
# inside `timeout 900` and then failed the word boundary against the second `0` — so the exact rows
# it existed to drop stayed at the top of the ranking, and looked like real findings.
#
# ⛔ And NO leading `\b` before the flag alternatives. `\b--watch` can never match: `\b` needs a
# word char on one side, and both the space and the `-` are non-word, so the boundary does not
# exist. Written that way it silently credited every `--watch` run as an operator stop.
_SELF_EXPLAINING = re.compile(r"(\btimeout\s+\d+|\bsleep\s+\d+|--watch|--follow|\btail\s+-[a-zA-Z]*f)")

# A segment that can head an allow rule: a program name, a path, or a variable holding one. Rows
# like `-rl '^riders:'` and `print({k:(v if` are continuation lines of a wrapped command that the
# line split cut in half - real text from the transcript, but never the thing that was approved,
# and a rule can no more be written for them than for `done`.
_LOOKS_LIKE_COMMAND = re.compile(r"""^["']?[\w./$~][\w./$~+-]*(\s|$)""")


def segments(command: str) -> list[str]:
    """The pieces Claude judges separately.

    ⛔ Cut the heredoc body off first. A `python3 - <<'PY' … PY` block contains lines like `done`
    and `print('---')` that split into nonsense segments and then report as uncovered *commands* —
    the first version of this ranked `---` as the operator's top interruption.

    ⛔ But do NOT then keep only the first line, which was the second version's fix. `set -e` on
    line 1 and the real command on line 2 is an ordinary shape, and first-line-only reports the
    scaffolding and loses the command — its own control case caught that. Every line before the
    heredoc marker is a candidate; `_PREAMBLE` and `_LOOKS_LIKE_COMMAND` do the discriminating.
    """
    out = []
    for line in command.split("<<")[0].splitlines():
        for seg in re.split(r"&&|\|\||;", line):
            seg = seg.strip().lstrip("(").strip()
            seg = re.sub(r"^\w+=\S*\s+", "", seg)      # drop `VAR=value ` prefixes
            if not seg or re.match(r"^\w+=", seg):      # a bare assignment is not a command
                continue
            out.append(seg)
    return out


def report_head(command: str, prefixes: list[str]) -> str | None:
    """The two words to show the operator: the first uncovered, non-preamble segment.

    ⛔ Returns None when every segment is shell scaffolding, and the caller DROPS that stop. This
    report's contract is "each row is one allow rule away from never stopping you again" — a row
    reading `for i` or `set -e` cannot be fixed by any rule, so carrying it makes the list longer
    and the decision harder, which is the opposite of the door's job.
    """
    segs = segments(command)
    for seg in segs:
        if _PREAMBLE.match(seg) or not _LOOKS_LIKE_COMMAND.match(seg):
            continue
        if not any(seg.startswith(p) for p in prefixes):
            return " ".join(seg.split()[:2])
    return None


def covered(command: str, prefixes: list[str]) -> bool:
    segs = segments(command)
    if not segs:
        return True
    return all(any(s.startswith(p) for p in prefixes) for s in segs)


def scan(repo: Path, sessions: int, wait: float) -> dict:
    prefixes = allow_prefixes(repo)
    files = sorted(
        glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")),
        key=os.path.getmtime,
        reverse=True,
    )[:sessions]

    stops: list[tuple[float, str, str]] = []   # (seconds waited, kind, command)
    total = 0
    for path in files:
        pending: dict[str, tuple[float | None, str]] = {}
        try:
            lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                rec = json.loads(line)
            except (ValueError, TypeError):
                continue
            content = (rec.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use" and block.get("name") == "Bash":
                    cmd = (block.get("input") or {}).get("command")
                    if cmd:
                        pending[block.get("id")] = (_iso(rec), cmd.strip())
                        total += 1
                elif block.get("type") == "tool_result":
                    got = pending.pop(block.get("tool_use_id"), None)
                    if not got:
                        continue
                    t0, cmd = got
                    raw = block.get("content")
                    text = raw if isinstance(raw, str) else json.dumps(raw)
                    if block.get("is_error") and REFUSED_BY_OPERATOR in text:
                        stops.append((0.0, "refused-by-operator", cmd))
                    elif block.get("is_error") and REFUSED_BY_CLASSIFIER in text:
                        stops.append((0.0, "refused-by-classifier", cmd))
                    else:
                        t1 = _iso(rec)
                        if (t0 and t1 and (t1 - t0) >= wait
                                and not covered(cmd, prefixes)
                                and not _SELF_EXPLAINING.search(cmd)):
                            stops.append((t1 - t0, "waited", cmd))

    heads: dict[str, list[float]] = collections.defaultdict(list)
    actionable = []
    for secs, kind, cmd in stops:
        head = report_head(cmd, prefixes)
        if head is None:                                # pure shell scaffolding — no rule fixes it
            continue
        actionable.append((secs, kind, cmd))
        heads[head].append(secs)
    return {"sessions": len(files), "calls": total, "stops": actionable,
            "scaffolding": len(stops) - len(actionable), "heads": heads}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".", help="repository root (default: cwd)")
    ap.add_argument("--sessions", type=int, default=20, help="newest transcripts to read")
    ap.add_argument("--wait", type=float, default=DEFAULT_WAIT,
                    help="seconds a call must wait before it counts as a stop")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()

    r = scan(Path(a.repo).resolve(), a.sessions, a.wait)
    kinds = collections.Counter(k for _, k, _ in r["stops"])
    lost = sum(s for s, _, _ in r["stops"])

    if a.json:
        print(json.dumps({
            "sessions": r["sessions"], "calls": r["calls"],
            "kinds": dict(kinds), "seconds_lost": round(lost, 1),
            "heads": {h: {"count": len(v), "seconds": round(sum(v), 1)}
                      for h, v in r["heads"].items()},
        }, indent=2))
        return 0

    print("approval-stops: %d Bash call(s) across the %d newest Claude session(s)"
          % (r["calls"], r["sessions"]))
    if not r["stops"]:
        print("  no stops found - nothing waited on you and nothing was refused")
        return 0
    print("  waited >= %.0fs and not covered by the allow list : %d"
          % (a.wait, kinds.get("waited", 0)))
    print("  refused by you                                    : %d"
          % kinds.get("refused-by-operator", 0))
    print("  refused by the auto-mode classifier               : %d"
          % kinds.get("refused-by-classifier", 0))
    print("  wall-clock time you spent waiting                 : %s"
          % _hms(lost))
    print("\nranked by time waited - the expensive stop is the one you were AWAY from:")
    ranked = sorted(r["heads"].items(), key=lambda kv: -sum(kv[1]))
    for head, waits in ranked[:25]:
        print("  %5d x  %9s   %s" % (len(waits), _hms(sum(waits)), head))
    print("\nEach of these would be covered by one allow row. `/smh-llm-approvals` Step 2 shows")
    print("them to the operator; nothing here proposes or writes a rule (SCC-354).")
    return 0


def _hms(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return "%ds" % seconds
    if seconds < 3600:
        return "%dm%02ds" % (seconds // 60, seconds % 60)
    return "%dh%02dm" % (seconds // 3600, (seconds % 3600) // 60)


if __name__ == "__main__":
    sys.exit(main())
