"""gate_receipt.py — make a claimed gate result impossible to fabricate (Wave 1.3).

Today a gate result is prose an agent types into a walkthrough. Nothing links "ruff clean"
to ruff actually having run, at which commit, over which files. This script closes that by
inverting the flow: it EXECUTES the gate and writes the receipt from the real exit code.
There is no `--result` flag. You cannot hand it a verdict.

    gate_receipt.py run   --story 21.8b --gate ruff -- ruff check backend/
    gate_receipt.py check --story 21.8b --require ruff,pytest [--sha X] [--cwd W] [--advisory]
    gate_receipt.py list  --story 21.8b

EVERY flag goes BEFORE `--`. Everything after it is the gate command verbatim, so a
trailing `--project X` becomes two more arguments to the tool under test, not a flag.

Receipts land in `_bmad-output/gates/<story>/<gate>.json`.

FOUR results, not two. `unrunnable` is its own state because `No module named ruff` means
the floor never ran, and the house rule is that a missing tool is a FINDING, not a skip
(`/sudo-code-review` Step 3.5). Collapsing it into `fail` loses that distinction; collapsing
it into `pass` is how a green gets faked. `warn` (opt-in via `--warn-exit N`) is the same
argument one level down: a tool that grades its OWN findings — `workflow_lint` exits 1 for
warnings and 2 for errors — has that grading erased if every non-zero is `fail`, and a
verdict citing `lint: fail` when the tool found zero errors is evidence that gets ignored.
`warn` is non-blocking but never a pass, so the finding still has to be read.

A receipt also records whether the tree was DIRTY. A receipt stamped at SHA X taken over
uncommitted edits is not evidence about SHA X, and `check` says so.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf

# Totals are EVIDENCE, so they are only ever quoted from the tool's own summary line.
# No match -> totals stays null; a fabricated count is worse than an absent one.
_TOTALS_PATTERNS = (
    re.compile(r"^=+ .*\b\d+ (?:passed|failed|error).*?=+$", re.MULTILINE),   # pytest
    re.compile(r"^\s*Tests\s+.*\b\d+ (?:passed|failed).*$", re.MULTILINE),    # vitest
    re.compile(r"^Found \d+ error.*$", re.MULTILINE),                         # ruff
    re.compile(r"^\s*(?:INFO )?\d+ error(?:s)? \(.*\)\s*$", re.MULTILINE),    # pyrefly
)

# Signatures of "the tool never ran", distinct from "the tool ran and failed".
_UNRUNNABLE = (
    "No module named", "is not recognized as", "command not found",
    "cannot find the path", "ModuleNotFoundError", "ImportError while loading conftest",
)


def _totals(output: str) -> str | None:
    for pat in _TOTALS_PATTERNS:
        m = pat.search(output)
        if m:
            return m.group(0).strip().strip("= ")
    return None


def _classify(exit_code: int, output: str, warn_exit: int | None = None) -> str:
    if exit_code == 0:
        return "pass"
    tail = output[-4000:]
    if exit_code in (9009, 127) or any(s in tail for s in _UNRUNNABLE):
        return "unrunnable"
    # A tool that grades its own findings (workflow_lint: 1 = warnings, 2 = errors) loses
    # that grading if every non-zero collapses to `fail`. The caller declares which code
    # means "advisory findings, nothing blocking" via --warn-exit; it is a FOURTH result,
    # never a pass, so the finding still has to be read - it just does not block. Without
    # this, an all-warnings lint reads `fail` in the verdict's evidence and the gate gets
    # ignored, which is the failure this whole receipt contract exists to prevent.
    if warn_exit is not None and exit_code == warn_exit:
        return "warn"
    return "fail"


def receipt_dir(project: Path, story: str) -> Path:
    return project / wf.GATES_REL / wf.norm_id(story)


def cmd_run(project: Path, story: str, gate: str, command: list[str],
            allow_fail: bool, cwd: Path | None, warn_exit: int | None = None) -> int:
    if not command:
        wf.die("no command given - put it after `--`")
    work = cwd or project
    sha_before = wf.git_head(work)
    dirty_r = wf.git(["status", "--porcelain"], work)
    dirty = bool(dirty_r.stdout.strip())

    started = time.time()
    try:
        proc = subprocess.run(command, cwd=str(work), capture_output=True,
                              text=True, errors="replace", shell=False)
        exit_code, output = proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError as exc:            # the executable itself is absent
        exit_code, output = 127, f"command not found: {exc}"
    elapsed = round(time.time() - started, 1)

    sha_after = wf.git_head(work)
    result = _classify(exit_code, output, warn_exit)
    # A commit landing mid-run means the receipt describes no single tree.
    if sha_before and sha_after and sha_before != sha_after:
        result = "unrunnable"
        output += f"\n[gate_receipt] HEAD moved {sha_before[:8]} -> {sha_after[:8]} mid-run"

    data = {
        "gate": gate,
        "story": wf.norm_id(story),
        "result": result,
        "exit_code": exit_code,
        "sha": sha_after,
        "dirty_tree": dirty,
        "totals": _totals(output),
        "command": command,
        "cwd": str(work),
        "duration_s": elapsed,
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output_tail": output[-1500:],
    }
    out_dir = receipt_dir(project, story)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{gate}.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    flag = "  [DIRTY TREE]" if dirty else ""
    print(f"[{result.upper()}] {gate} exit={exit_code} {elapsed}s "
          f"@ {(sha_after or '?')[:8]}{flag}")
    if data["totals"]:
        print(f"        totals: {data['totals']}")
    print(f"        receipt: {path.relative_to(project)}")
    if result in ("pass", "warn") or allow_fail:
        return 0
    return 1 if result == "fail" else 2


def check_receipt(repo: Path, data: dict, gate: str, target: str | None,
                  rep: wf.Report) -> None:
    """One receipt against one target commit. Shared with closeout_preflight so the two
    never disagree about what 'stale' means."""
    if data.get("result") == "warn":
        # Advisory findings: recorded, never blocking. Still WARN-not-INFO so it is read.
        rep.warn("gates", f"{gate}: advisory findings only (exit {data.get('exit_code')}) "
                          f"- not blocking, but read them")
    elif data.get("result") != "pass":
        rep.err("gates", f"{gate}: result={data.get('result')} "
                         f"(exit {data.get('exit_code')})")
        return
    sha = str(data.get("sha") or "")
    if target and sha != target:
        # TREE comparison, not SHA equality: a branch that landed via a merge commit has a
        # new SHA and an identical tree, and that receipt is still evidence about this code.
        identical = wf.same_tree(repo, sha, target)
        if identical is None:
            rep.warn("gates", f"{gate}: recorded at {sha[:8]}, which is not a commit in "
                              f"{repo.name} (worktree-only or pruned) - CANNOT verify freshness")
        elif identical:
            rep.info("gates", f"{gate}: pass @ {sha[:8]} - different commit than "
                              f"{target[:8]}, identical tree")
        else:
            rep.err("gates", f"{gate}: STALE - passed at {sha[:8]}, "
                             f"code differs from {target[:8]}")
            return
    if data.get("dirty_tree"):
        rep.warn("gates", f"{gate}: passed over a DIRTY tree - "
                          f"the receipt's SHA is not what was tested")
    if not target or sha == target:
        rep.info("gates", f"{gate}: pass @ {sha[:8]}"
                          f"{' - ' + data['totals'] if data.get('totals') else ''}")


def load_receipt(project: Path, story: str, gate: str, rep: wf.Report) -> dict | None:
    path = receipt_dir(project, story) / f"{gate}.json"
    if not path.is_file():
        rep.err("gates", f"{gate}: NO RECEIPT - the gate has no evidence it ran")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rep.err("gates", f"{gate}: unreadable receipt ({exc})")
        return None


def cmd_check(project: Path, story: str, require: list[str], advisory: bool,
              sha: str | None, cwd: Path | None) -> int:
    # The receipt was stamped wherever the gate RAN (often a story worktree), so the repo
    # that resolves its commits may not be the project root.
    repo = cwd or project
    target = sha or wf.git_head(repo)
    rep = wf.Report()

    for gate in require:
        data = load_receipt(project, story, gate, rep)
        if data is not None:
            check_receipt(repo, data, gate, target, rep)

    rep.print_human(f"gate_receipt check - {wf.norm_id(story)}")
    code = rep.exit_code()
    if advisory and code == 2:
        print("-- ADVISORY MODE: reporting only, not blocking "
              "(remove --advisory to enforce) --")
        return 0
    return code


def cmd_list(project: Path, story: str) -> int:
    out_dir = receipt_dir(project, story)
    if not out_dir.is_dir():
        print(f"(no receipts under {wf.GATES_REL}/{wf.norm_id(story)})")
        return 1
    for path in sorted(out_dir.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        print(f"{d['gate']:>12}  {d['result']:<10} exit={d['exit_code']:<4} "
              f"{str(d.get('sha'))[:8]}  {d.get('totals') or ''}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Execute gates and record tamper-evident receipts")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--story", required=True)
    p_run.add_argument("--gate", required=True)
    p_run.add_argument("--project")
    p_run.add_argument("--cwd", help="run the command here (e.g. a worktree) instead of the project root")
    p_run.add_argument("--allow-fail", action="store_true",
                       help="always exit 0; the receipt still records the true result")
    p_run.add_argument("--warn-exit", type=int, metavar="N",
                       help="exit code N means ADVISORY findings, not failure (e.g. "
                            "workflow_lint: 1=warnings, 2=errors -> --warn-exit 1). "
                            "Records result=warn: non-blocking, but never a pass.")
    p_run.add_argument("command", nargs=argparse.REMAINDER)

    p_check = sub.add_parser("check")
    p_check.add_argument("--story", required=True)
    p_check.add_argument("--project")
    p_check.add_argument("--require", required=True, help="comma-separated gate names")
    p_check.add_argument("--sha", help="check against THIS commit (the shipping sha) "
                                       "instead of the current HEAD")
    p_check.add_argument("--cwd", help="resolve commits in this repo/worktree - use the same "
                                       "one `run --cwd` used, or its shas are unknown here")
    p_check.add_argument("--advisory", action="store_true",
                         help="report but do not block (first-sprint rollout only)")

    p_list = sub.add_parser("list")
    p_list.add_argument("--story", required=True)
    p_list.add_argument("--project")

    args = ap.parse_args()
    project = wf.resolve_project_root(args.project)

    if args.cmd == "run":
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        cwd = Path(args.cwd).resolve() if args.cwd else None
        return cmd_run(project, args.story, args.gate, command, args.allow_fail, cwd,
                       args.warn_exit)
    if args.cmd == "check":
        gates = [g.strip() for g in args.require.split(",") if g.strip()]
        return cmd_check(project, args.story, gates, args.advisory, args.sha,
                         Path(args.cwd).resolve() if args.cwd else None)
    return cmd_list(project, args.story)


if __name__ == "__main__":
    sys.exit(main())
