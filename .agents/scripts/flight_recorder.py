#!/usr/bin/env python3
"""flight_recorder.py - the command centre's close-out flight recorder (SCC-133, under SCC-38).

WHAT IT IS. Every Task lane already leaves evidence behind - a walkthrough with a `Verdict:` line,
gate receipts under `<task-artifacts>/gates/`, a Dev Record posted to Jira. Nothing reads ACROSS
lanes. This script records one small event file per close-out and computes, on read, which
things keep recurring: a prose rule that gets rewritten lane after lane, a gate that keeps going
red, a script that keeps being named in pitfalls. Recurrence is EVIDENCE - the ladder is
evidence (1 lane) -> candidate (2) -> action-required (3+), and the phrasing at the top rung is
"this prose rule failed N times - commission the script": executable enforcement before more prose.

WHAT IT IS NOT. Not a ticket queue, not a work list, not a rule-writer (SCC-160: found != owed).
`surface` prints PROPOSALS with their evidence pointers; the review's relevance triage or the
operator's word decides what, if anything, gets built. It never mints, never edits a rule, never
blocks a merge, and never stores a transcript - pointers, outcomes and fingerprints only.

STORAGE. One file per event: `_artifacts/_main/workflow-events/<YYYY-MM>/<KEY>_<sha7>.json`.
Not an append-only ledger: two sibling lanes appending to one file conflict at every landing;
two files never do, and "already recorded" becomes a file-exists check. There is deliberately NO
materialised candidates view - a derived file every lane regenerates is a guaranteed conflict
and a second copy that can drift; the ledger is tiny and the ladder is recomputed on every read.

KEYING. `sha` is the walkthrough's `Verdict: ... @ <sha>` sha - the house's existing notion of
"the code that landed" - NOT HEAD. `record` runs pre-merge (close-out Step 2.5) and its output is
committed as an artifacts-only commit, so HEAD moves the moment the event exists; keyed on HEAD a
resumed close-out would record a second event whose only change is the first event. `tip`
records HEAD for the audit trail. `when` is that sha's own commit date, never the wall clock, so
`record` is reproducible and the tests are deterministic.

FINGERPRINTS - mechanical, four families, no NLP:
  rule-edited:<path>   a file under .agents/rules/ in the lane's changes (the prose was rewritten)
  gate-red:<gate>      a receipt whose result is not `pass`
  verdict:<X>          a review verdict that is not PASS
  mention:<token>      a script / command / rule name inside a pitfall bullet
The master plan's "post-fix regression" trigger is dropped: nothing here can detect one
mechanically, and a rung an agent asserts by hand is the vacuous class SCC-125 measured.

Stdlib only. Imports the two scrape helpers from jira_feed.py rather than cloning them, so the
event's pitfalls/decisions are the SAME buckets the Dev Record posts - one truth, two readers.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf                                     # noqa: E402
from jira_feed import _SCRAPE_HEADS, _VERDICT_RE, scrape_bucket   # noqa: E402

SCHEMA_V = 1
EVENTS_REL = Path("_artifacts/_main/workflow-events")
RULES_PREFIX = ".agents/rules/"
# A script/command/rule NAME inside a pitfall bullet. Two shapes: `something.py|.sh|.ps1|.md`
# and a slash-command `/smh-...` or `/cicd-...`. Backticks and trailing punctuation stripped.
_MENTION_RE = re.compile(r"(?:(?<![\w/])([\w][\w\-]*\.(?:py|sh|ps1|md))\b|(/(?:smh|cicd)-[\w\-]+))")

RUNGS = ((3, "action-required"), (2, "candidate"), (1, "evidence"))


def say(msg: str) -> None:
    print(msg)


# ── paths ──────────────────────────────────────────────────────────────────────

def resolve_repo(arg: str | None) -> Path:
    start = Path(arg).resolve() if arg else Path.cwd()
    r = wf.git(["rev-parse", "--show-toplevel"], start)
    if r.returncode != 0:
        wf.die(f"not a git repo: {start}")
    return Path(r.stdout.strip()).resolve()


def events_dir(repo: Path) -> Path:
    return repo / EVENTS_REL


def load_events(repo: Path, warn: bool = True) -> list[dict]:
    """Every event file, oldest month first. A malformed file is skipped with a warning to
    stderr and NEVER raises - `surface` runs inside a SessionStart hook that must not block."""
    out: list[dict] = []
    root = events_dir(repo)
    if not root.is_dir():
        return out
    for p in sorted(root.rglob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8-sig"))
            if isinstance(data, dict) and data.get("task") and data.get("sha"):
                out.append(data)
            elif warn:
                print(f"[warn] flight_recorder: {p} is not an event - skipped", file=sys.stderr)
        except Exception as e:  # noqa: BLE001 - a boot surface swallows, reports, continues
            if warn:
                print(f"[warn] flight_recorder: {p}: {e} - skipped", file=sys.stderr)
    return out


# ── record ─────────────────────────────────────────────────────────────────────

def read_receipts(root: Path) -> dict[str, dict]:
    gates = root / "gates"
    out: dict[str, dict] = {}
    if not gates.is_dir():
        return out
    for p in sorted(gates.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(data, dict):
            out[str(data.get("gate") or p.stem)] = data
    return out


def fingerprints(changes: list[str], receipts: dict[str, dict], verdict: str,
                 pitfalls: list[str]) -> list[str]:
    fps: list[str] = []
    for path in changes:
        if path.startswith(RULES_PREFIX):
            fps.append(f"rule-edited:{path}")
    for gate, data in receipts.items():
        if str(data.get("result", "")).lower() != "pass":
            fps.append(f"gate-red:{gate}")
    if verdict and verdict.upper() != "PASS":
        fps.append(f"verdict:{verdict.upper()}")
    for bullet in pitfalls:
        for m in _MENTION_RE.finditer(bullet):
            tok = m.group(1) or m.group(2)
            fp = f"mention:{tok}"
            if fp not in fps:
                fps.append(fp)
    return fps


def build_event(repo: Path, task: str, root: Path, base: str, trigger: str) -> dict:
    wt = root / "walkthrough.md"
    if not wt.is_file():
        wf.die(f"no walkthrough at {wt} - nothing to record (the door blocks on this too)")
    text = wf.read_text(wt)
    m = _VERDICT_RE.search(text)
    if not m or not m.group(2):
        wf.die(f"{wt.name} carries no `Verdict: ... @ <sha>` line - the event is keyed on that sha")
    verdict = m.group(1).upper()
    r = wf.git(["rev-parse", "--verify", m.group(2) + "^{commit}"], repo)
    if r.returncode != 0:
        wf.die(f"verdict sha {m.group(2)} is not a commit in {repo}")
    sha = r.stdout.strip()
    tip = wf.git_head(repo) or ""
    when = wf.git(["show", "-s", "--format=%cI", sha], repo).stdout.strip()
    # Three-dot: the lane's own changes since it forked from `base`. A mid-lane absorb of main,
    # or main moving on after the fork, must not appear here.
    d = wf.git(["diff", "--name-only", f"{base}...{sha}"], repo)
    if d.returncode != 0:
        wf.die(f"git diff {base}...{sha[:7]} failed: {d.stderr.strip()[:200]}")
    changes = sorted({ln.strip() for ln in d.stdout.splitlines() if ln.strip()})

    buckets = {name: scrape_bucket(text, pat) for name, pat in _SCRAPE_HEADS.items()}
    receipts = read_receipts(root)
    try:
        wt_rel = str(wt.resolve().relative_to(repo)).replace("\\", "/")
    except ValueError:
        wt_rel = str(wt)
    return {
        "v": SCHEMA_V,
        "task": task,
        "sha": sha,
        "tip": tip,
        "trigger": trigger,
        "when": when,
        "changes": changes,
        "evidence": {
            "walkthrough": wt_rel,
            "verdict": f"{verdict} @ {sha[:7]}",
            "gates": {g: f"{str(x.get('result', '?')).lower()}@{str(x.get('sha', ''))[:7]}"
                      for g, x in receipts.items()},
        },
        "expected": {"verdict": "PASS"},
        "outcome": {"verdict": verdict},
        "decisions": buckets["decisions"],
        "pitfalls": buckets["pitfalls"],
        "followons": buckets["followons"],
        "fingerprints": fingerprints(changes, receipts, verdict, buckets["pitfalls"]),
    }


def event_path(repo: Path, ev: dict) -> Path:
    month = str(ev["when"])[:7] or "undated"
    return events_dir(repo) / month / f"{ev['task']}_{ev['sha'][:7]}.json"


def cmd_record(args) -> int:
    repo = resolve_repo(args.repo)
    root = Path(args.root)
    if not root.is_absolute():
        root = repo / root
    ev = build_event(repo, args.task, root, args.base, args.trigger)
    path = event_path(repo, ev)
    rel = str(path.relative_to(repo)).replace("\\", "/")
    if path.is_file():
        # Idempotent on (task, verdict sha): a resumed close-out returns the record it made.
        say(f"flight-recorder: {args.task} @ {ev['sha'][:7]} already recorded -> {rel}")
        sys.stdout.write(path.read_text(encoding="utf-8-sig"))
        return 0
    if not args.apply:
        say(f"flight-recorder: DRY RUN - would write {rel}")
        sys.stdout.write(json.dumps(ev, indent=2) + "\n")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ev, indent=2) + "\n", encoding="utf-8")
    say(f"flight-recorder: recorded {args.task} @ {ev['sha'][:7]} -> {rel} "
        f"({len(ev['fingerprints'])} fingerprint(s): {', '.join(ev['fingerprints']) or '-'})")
    return 0


# ── candidates / surface ───────────────────────────────────────────────────────

def ladder(events: list[dict]) -> list[dict]:
    """Rungs by DISTINCT task per fingerprint. The same task recorded at two shas is one lane
    that hit the thing once, not twice."""
    seen: dict[str, dict] = {}
    for ev in events:
        for fp in ev.get("fingerprints") or []:
            row = seen.setdefault(fp, {"fingerprint": fp, "tasks": [], "shas": [], "first": ev.get("when", ""),
                                       "last": ev.get("when", "")})
            if ev["task"] not in row["tasks"]:
                row["tasks"].append(ev["task"])
            row["shas"].append(str(ev["sha"])[:7])
            row["first"] = min(row["first"], ev.get("when", "") or row["first"])
            row["last"] = max(row["last"], ev.get("when", "") or row["last"])
    out: list[dict] = []
    for row in seen.values():
        n = len(row["tasks"])
        rung = next(name for floor, name in RUNGS if n >= floor)
        row["count"] = n
        row["rung"] = rung
        row["proposal"] = proposal(row["fingerprint"], n, rung)
        out.append(row)
    order = {"action-required": 0, "candidate": 1, "evidence": 2}
    out.sort(key=lambda r: (order[r["rung"]], -r["count"], r["fingerprint"]))
    return out


def proposal(fp: str, n: int, rung: str) -> str:
    kind, _, what = fp.partition(":")
    lanes = f"{n} lane{'s' if n != 1 else ''}"
    if rung != "action-required":
        return f"{kind} {what} seen in {lanes} - {rung}"
    if kind == "rule-edited":
        return (f"this prose rule was rewritten in {lanes} - commission the script that enforces "
                f"it ({what})")
    if kind == "gate-red":
        return f"gate `{what}` went red in {lanes} - commission the script or fix that makes it stay green"
    if kind == "verdict":
        return f"review verdict {what} in {lanes} - commission the script for whatever keeps failing review"
    return f"`{what}` named as a pitfall in {lanes} - commission the script that removes the trap"


def cmd_candidates(args) -> int:
    repo = resolve_repo(args.repo)
    rows = ladder(load_events(repo))
    if args.json:
        sys.stdout.write(json.dumps(rows, indent=2) + "\n")
        return 0
    if not rows:
        say("flight-recorder: no events recorded yet")
        return 0
    say(f"flight-recorder: {len(rows)} fingerprint(s) across {len(load_events(repo, warn=False))} event(s)")
    for r in rows:
        say(f"  [{r['rung']:<15}] {r['fingerprint']}  x{r['count']}  ({', '.join(r['tasks'])})")
        say(f"                    {r['proposal']}")
    return 0


def cmd_surface(args) -> int:
    """Boot surface: action-required rungs only, one line each, ALWAYS exit 0. Silent when there
    is nothing at that rung - the positive control lives in the test, not in this output."""
    try:
        repo = resolve_repo(args.repo)
        rows = [r for r in ladder(load_events(repo)) if r["rung"] == "action-required"]
        for r in rows:
            say(f"FLIGHT-RECORDER PROPOSAL (not owed; the review's triage or the operator's word "
                f"decides): {r['proposal']} - evidence: {', '.join(r['tasks'])} @ "
                f"{', '.join(r['shas'])}  [{r['fingerprint']}]")
    except SystemExit:
        pass                                   # wf.die inside a boot surface: swallow, exit 0
    except Exception as e:  # noqa: BLE001
        print(f"[warn] flight_recorder surface: {e}", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Close-out flight recorder (SCC-133)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--repo", help="the git repo (a worktree is fine); default = cwd's toplevel")

    p = sub.add_parser("record", help="record this lane's close-out event (pre-merge, at the verdict sha)")
    common(p)
    p.add_argument("--task", required=True, help="the Jira key, e.g. SCC-160")
    p.add_argument("--root", required=True, help="the task's artifacts folder (walkthrough.md + gates/)")
    p.add_argument("--base", default="main", help="the branch the lane forked from (default main)")
    p.add_argument("--trigger", default="close-out")
    p.add_argument("--apply", action="store_true", help="write the event file (else dry run)")
    p.set_defaults(fn=cmd_record)

    p = sub.add_parser("candidates", help="the full recurrence ladder, computed from the event files")
    common(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_candidates)

    p = sub.add_parser("surface", help="action-required proposals only; always exit 0 (boot surface)")
    common(p)
    p.set_defaults(fn=cmd_surface)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
