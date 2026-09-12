#!/usr/bin/env python3
"""repro_receipt.py - a reproduction is a receipt, and a receipt implies execution. (SCC-447)

    repro_receipt.py run --root <artifacts> --id <finding-id> --cwd <worktree> [--replace] -- <command...>

Runs the finding's `reproduce:` command on the tree at --cwd and writes
`<root>/gates/repro/<id>.json` from the TRUE exit code. There is no `--result` flag: you cannot
hand it a verdict. EVERY flag goes BEFORE `--`; everything after it is the command verbatim.

WHY THE DOOR RUNS IT AGAIN. A lens proves a defect exists in ITS OWN worktree copy, which it
may have edited - SCC-295 measured three of five lenses writing to the builder's tree, and one
reporting a RED that no version of the real code could produce. Only a run on the REAL tree
proves the defect exists in the code that ships, and only a receipt proves the run happened.
The lens's own run leaves no receipt; its evidence is the `reproduced: yes` line it pasted,
which the engine reads as text (it holds no Bash and cannot run anything, by design).

THREE results, and the exit code says which, so a caller can branch on it:

    reproduced      the command FAILED (non-zero)  - the finding is real on this tree  exit 0
    not-reproduced  the command exited 0           - the finding is DROPPED, counted   exit 1
    unrunnable      the command never RAN          - nobody has learned anything       exit 2

⛔ `unrunnable` is its own result because a typo'd executable exits 127 - non-zero - and a naive
"non-zero means reproduced" would stamp every finding whose command is broken. A missing tool,
a `ModuleNotFoundError`, a `command not found` are the signatures `gate_receipt.py` already
refuses to read as a result, and this reads them the same way. The honest cost: a reproduction
whose failure IS an import error of the product's own module reads `unrunnable`, and the door
has to look at it rather than have it silently fixed or silently dropped. That is the right
direction to fail.

One receipt per finding id. An existing id refuses (exit 2) without `--replace`, because two
receipts for one finding is two stories. `walkthrough_roster.py` resolves the file beside the
walkthrough and refuses a `fixed`/`held` row whose receipt is absent or does not say
`reproduced`. Same shape as `gate_receipt.py`, kept separate because a gate receipt is one per
gate NAME and a reproduction is one per FINDING; the dirty-tree read is shared with it, so the
two cannot disagree about what dirt is (a sandbox mask is not dirt, and this writer's own
output is not dirt).

Both machines: stdlib only, `python3`/`python` never assumed by callers.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_receipt as gr   # noqa: E402  - the dirty-tree reader and the unrunnable signatures
import wf_common as wf      # noqa: E402

_ID_RE = re.compile(r"^[\w.\-]+$")
RESULT_EXIT = {"reproduced": 0, "not-reproduced": 1, "unrunnable": 2}


def classify(exit_code: int, output: str) -> str:
    """The three results. Exit 0 is the one that means the finding is NOT there."""
    if exit_code == 0:
        return "not-reproduced"
    tail = output[-4000:]
    if exit_code in (9009, 127) or any(s in tail for s in gr._UNRUNNABLE):
        return "unrunnable"
    return "reproduced"


def cmd_run(root: Path, fid: str, cwd: Path, command: list[str], replace: bool) -> int:
    if not command:
        wf.die("no command given - put it after `--`")
    if not _ID_RE.match(fid):
        wf.die(f"--id {fid!r} is not a finding id: letters, digits, `.`, `-` and `_` only - "
               f"it names the receipt file")
    sha = wf.git_head(cwd)
    if not sha:
        wf.die(f"--cwd {cwd} is not inside a git working tree - a receipt is evidence about a "
               f"commit, and this tree has none")
    out_dir = root / "gates" / "repro"
    path = out_dir / f"{fid}.json"
    if path.exists() and not replace:
        wf.die(f"receipt {path} already exists - one receipt per finding id; pass --replace to "
               f"run again and overwrite it")

    dirty_paths = gr._measure_dirt(cwd, out_dir)
    try:
        proc = subprocess.run(command, cwd=str(cwd), capture_output=True,
                              encoding="utf-8", text=True, errors="replace", shell=False)
        exit_code, output = proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError as exc:            # the executable itself is absent
        exit_code, output = 127, f"command not found: {exc}"
    result = classify(exit_code, output)

    data = {
        "id": fid,
        "result": result,
        "command": command,
        "cwd": str(cwd),
        "exit_code": exit_code,
        "sha": sha,
        "dirty_tree": bool(dirty_paths),
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output_tail": output[-1500:],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    label = {"reproduced": "REPRODUCED", "not-reproduced": "NOT REPRODUCED",
             "unrunnable": "UNRUNNABLE"}[result]
    flag = "  [DIRTY TREE]" if dirty_paths else ""
    print(f"[{label}] {fid} exit={exit_code} @ {sha[:8]}{flag}")
    print(f"        receipt: {path}")
    return RESULT_EXIT[result]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run a finding's reproduce command on the real tree and write its receipt")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--root", required=True,
                       help="the lane's artifacts dir; receipts land at <root>/gates/repro/<id>.json")
    p_run.add_argument("--id", required=True, help="the finding id the walkthrough row cites as `repro <id>`")
    p_run.add_argument("--cwd", required=True,
                       help="the worktree to run in - REQUIRED, because without it the command runs "
                            "wherever the caller stood and records a result about nothing (SCC-154)")
    p_run.add_argument("--replace", action="store_true",
                       help="overwrite an existing receipt for this id (default: refuse)")
    p_run.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    cwd = Path(args.cwd).resolve()
    root = Path(args.root)
    if not root.is_absolute():
        root = cwd / root
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    return cmd_run(root.resolve(), args.id, cwd, command, args.replace)


if __name__ == "__main__":
    sys.exit(main())
