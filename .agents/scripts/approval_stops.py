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
            # ⛔ ORDER IS LOAD-BEARING: the longer suffixes strip first. Put the bare "*"
            # first and `Bash(git status:*)` comes back as `git status:`, which matches
            # nothing. The bare star is not a typo - SCC-375's check A2b, in
            # tests/test_settings_allowlist.py (NOT the parity battery), established that a
            # prefix ending in `/ = - :` MUST be spelled `Bash(X/*)`, because Claude reads
            # `Bash(X:*)` as `Bash(X *)`. 54 of the 153 rendered rows use it (SCC-409).
            for suffix in (":*", " *", "*"):
                if body.endswith(suffix):
                    body = body[: -len(suffix)]
                    # ⛔ ONE strip, and the `break` is what enforces it. Without it `Bash(X* *)`
                    # strips ` *` and then `*` and returns `X` - a prefix WIDER than the row that
                    # produced it, which silently marks uncovered commands as covered.
                    break
            # ⛔ An empty prefix matches EVERY command: `"rm -rf /".startswith("")` is True, so a
            # single `Bash(*)` row makes covered() answer True for everything and the door reports
            # zero stops FOREVER - the exact SCC-407 silence this script exists to end, and a
            # failure that looks identical to "nothing to harvest". A row that strips to nothing is
            # not a prefix; drop it and let the door over-report instead. Over-reporting costs the
            # operator one glance; under-reporting cost him the whole instrument.
            if not body:
                continue
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

# ⛔ SHAPES NO PERMISSION ROW CAN FIX (operator's own eight stops, 2026-09-04). Five of the eight
# were the SAME banned command retried, and an allow row for it would have changed nothing — the
# harness refuses the shape, not the program. Reporting these beside real candidates is what makes
# a list unactionable, so they are carried under their own heading WITH THEIR REMEDY.
_HARNESS_BAN = [
    (re.compile(r"(^|[;&|]\s*)sleep\s+\d"), "foreground sleep is blocked - use Monitor with an "
                                            "until-loop, or run_in_background"),
    (re.compile(r"\bgit\s+-C\b"), "git -C is auto-denied (command-shape.md rule 1) - "
                                  "write `cd <abs> && git <verb>`"),
    (re.compile(r';\s*echo\s+"?EXIT='), "the `; echo EXIT=$?` tail masks the real status "
                                        "(command-shape.md rule 2)"),
]


def harness_ban(command: str) -> str | None:
    for pattern, remedy in _HARNESS_BAN:
        if pattern.search(command):
            return remedy
    return None


def _ban_key(command: str) -> str:
    """The banned fragment itself, so the row names the offence rather than the line it sat in."""
    for pattern, _ in _HARNESS_BAN:
        m = pattern.search(command)
        if m:
            return m.group(0).strip().lstrip(";&| ").strip()
    return " ".join(command.split()[:2])


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


def _matches(seg: str, prefix: str) -> bool:
    """Does an allow PREFIX actually cover this command segment?

    ⛔ NOT a bare `startswith`. `Bash(ls *)` yields the prefix `ls`, and `"lsof -i :3000"`
    starts with `ls` - so a plain prefix test marked `lsof`, `lsblk` and `git statuses` as
    already-approved and DROPPED their stops from the report. That is the same defect as the
    bare-star bug this script was just fixed for (SCC-409), pointing the other way: one made the
    door over-report, this one made it under-report, and under-reporting is how an instrument
    goes quiet without anyone noticing. Found by code review, 2026-09-04.

    A prefix covers a segment when the segment IS the prefix, or continues it at a boundary -
    which is either a space in the segment or a prefix that already ends on a separator
    (`python3 .agents/scripts/`, `MSG=`, `git branch -d chore/`). Those are exactly the endings
    A2b requires the bare-star spelling for, so the two rules meet.
    """
    if not prefix or not seg.startswith(prefix):
        return False
    if len(seg) == len(prefix):
        return True
    return not prefix[-1].isalnum() or not seg[len(prefix)].isalnum()


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
        if not any(_matches(seg, p) for p in prefixes):
            return " ".join(seg.split()[:2])
    return None


def covered(command: str, prefixes: list[str]) -> bool:
    segs = segments(command)
    if not segs:
        return True
    return all(any(_matches(s, p) for p in prefixes) for s in segs)


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
                if block.get("type") == "tool_use":
                    inp = block.get("input") or {}
                    if block.get("name") == "Bash":
                        cmd = inp.get("command")
                        if cmd:
                            # ⛔ CARRY THE ESCALATION FLAG. The operator's stop #3 was
                            # `git worktree remove --force …` run with the sandbox OFF: the
                            # command was ALREADY on the allow list and it stopped anyway,
                            # because the escalation gate is a second, independent gate. Judging
                            # it on coverage alone marks it "covered" and HIDES it - a false
                            # negative on a stop he actually paid for.
                            pending[block.get("id")] = (
                                _iso(rec), cmd.strip(), "Bash",
                                inp.get("dangerouslyDisableSandbox") is True)
                            total += 1
                    else:
                        # Non-Bash tools stop too, and no allow row exists for them at all: his
                        # stop #1 was `Skill(code-review-engine)`, and families.json has no
                        # skill-grant kind to write. Invisible while this scan read only Bash.
                        label = block.get("name") or "?"
                        detail = inp.get("skill") or inp.get("subagent_type") or ""
                        pending[block.get("id")] = (
                            _iso(rec), "%s(%s)" % (label, detail) if detail else label,
                            "tool", False)
                        total += 1
                elif block.get("type") == "tool_result":
                    got = pending.pop(block.get("tool_use_id"), None)
                    if not got:
                        continue
                    t0, cmd, kind, escalated = got
                    raw = block.get("content")
                    text = raw if isinstance(raw, str) else json.dumps(raw)
                    if block.get("is_error") and REFUSED_BY_OPERATOR in text:
                        stops.append((0.0, "refused-by-operator", cmd))
                        continue
                    if block.get("is_error") and REFUSED_BY_CLASSIFIER in text:
                        stops.append((0.0, "refused-by-classifier", cmd))
                        continue
                    t1 = _iso(rec)
                    if not (t0 and t1 and (t1 - t0) >= wait):
                        continue
                    if kind == "tool":
                        stops.append((t1 - t0, "no-grant-kind", cmd))
                    # ⛔ BAN BEFORE SELF-EXPLAINING. `sleep 60; gh pr view 154` matches BOTH, and
                    # ordered the other way the five identical retries of it vanished into the
                    # self-explaining bin - the operator's stops #4-8, silently dropped.
                    elif harness_ban(cmd):
                        stops.append((t1 - t0, "harness-ban", cmd))
                    elif _SELF_EXPLAINING.search(cmd):
                        pass
                    elif escalated:
                        stops.append((t1 - t0, "escalation", cmd))
                    elif not covered(cmd, prefixes):
                        stops.append((t1 - t0, "waited", cmd))

    # Three buckets, because the REMEDY differs and mixing them is what makes a list unactionable:
    # `heads` is fixed by one allow row, `blocked` by a different tool, `nogrant` by nothing that
    # exists yet.
    heads: dict[str, list[float]] = collections.defaultdict(list)
    blocked: dict[str, list[float]] = collections.defaultdict(list)
    nogrant: dict[str, list[float]] = collections.defaultdict(list)
    escalated_heads: dict[str, list[float]] = collections.defaultdict(list)
    remedies: dict[str, str] = {}
    actionable = []
    for secs, kind, cmd in stops:
        if kind == "no-grant-kind":
            nogrant[cmd].append(secs)
            actionable.append((secs, kind, cmd))
            continue
        if kind == "harness-ban":
            # Key on the BANNED SHAPE, not the command's first two words. The ban usually matches
            # deep inside a compound line, so `cat > … && git -C …` keyed as `cat >` and printed a
            # `git -C` remedy under it - two rows that looked unrelated and neither of which named
            # the offence.
            key = _ban_key(cmd)
            blocked[key].append(secs)
            remedies[key] = harness_ban(cmd) or ""
            actionable.append((secs, kind, cmd))
            continue
        if kind == "escalation":
            # ⛔ NOT through report_head. An escalation stop is usually on an ALREADY-COVERED
            # command (his #3 was), so report_head finds no uncovered segment, returns None, and
            # the stop is discarded — the very false negative this class exists to surface. Its
            # remedy is the sandbox boundary, not an allow row, so it gets its own section.
            escalated_heads[" ".join(cmd.split()[:2])].append(secs)
            actionable.append((secs, kind, cmd))
            continue
        head = report_head(cmd, prefixes)
        if head is None:                                # pure shell scaffolding — no rule fixes it
            continue
        actionable.append((secs, kind, cmd))
        heads[head].append(secs)
    return {"sessions": len(files), "calls": total, "stops": actionable,
            "scaffolding": len(stops) - len(actionable), "heads": heads,
            "blocked": blocked, "nogrant": nogrant, "remedies": remedies,
            "escalated": escalated_heads}


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
    # ⛔ NEVER credit a non-Bash tool's duration as time the operator waited. `Agent(general-purpose)`
    # ran 63 times for 11h37m in this window — that is a subagent WORKING, not him sitting there,
    # and counting it put a fabricated 11 hours at the top of a report whose only value is being
    # believable about cost. Those rows are an inventory of missing grant kinds, counted not timed.
    lost = sum(s for s, k, _ in r["stops"] if k != "no-grant-kind")

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
    print("  not covered by the allow list                     : %d"
          % kinds.get("waited", 0))
    print("  ALLOWED but stopped by the escalation gate        : %d"
          % kinds.get("escalation", 0))
    print("  a tool with no grant kind at all (Skill, Agent …) : %d"
          % kinds.get("no-grant-kind", 0))
    print("  a shape the harness BANS - no row can fix it      : %d"
          % kinds.get("harness-ban", 0))
    print("  refused by you                                    : %d"
          % kinds.get("refused-by-operator", 0))
    print("  refused by the auto-mode classifier               : %d"
          % kinds.get("refused-by-classifier", 0))
    print("  wall-clock time you spent waiting                 : %s" % _hms(lost))

    _section("ONE ALLOW ROW FIXES THESE - ranked by time, not count", r["heads"])
    _section("ALREADY ALLOWED, stopped by the SANDBOX ESCALATION gate - a second, "
             "independent gate", r["escalated"])
    _section("NO ALLOW ROW FIXES THESE - the harness bans the shape", r["blocked"],
             r["remedies"])
    _section("NO GRANT KIND EXISTS - families.json cannot express these yet "
             "(COUNT only: a long run here is the tool working, not you waiting)",
             r["nogrant"], timed=False)
    print("\nNothing here proposes or writes a rule (SCC-354). The first section is what")
    print("`/smh-llm-approvals` Step 2 shows the operator; the other two are engineering.")
    return 0


def _section(title: str, data: dict, remedies: dict | None = None, timed: bool = True) -> None:
    if not data:
        return
    print("\n%s:" % title)
    key = (lambda kv: -sum(kv[1])) if timed else (lambda kv: -len(kv[1]))
    for head, waits in sorted(data.items(), key=key)[:20]:
        cost = _hms(sum(waits)) if timed else ""
        print("  %5d x  %9s   %s" % (len(waits), cost, head))
        if remedies and remedies.get(head):
            print("                          -> %s" % remedies[head])


def _hms(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return "%ds" % seconds
    if seconds < 3600:
        return "%dm%02ds" % (seconds // 60, seconds % 60)
    return "%dh%02dm" % (seconds // 3600, (seconds % 3600) // 60)


if __name__ == "__main__":
    sys.exit(main())
