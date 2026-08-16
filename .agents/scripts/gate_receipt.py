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

The TASK lane (SCC-146) has no board for the resolver to find, so it passes `--root` with
the task's own artifacts dir and receipts land at `<root>/gates/<gate>.json` instead —
riding the chore branch through the merge exactly like story receipts ride theirs.
`--task` is an alias for `--story` (same receipt field):

    gate_receipt.py run --task SCC-146 --gate suite \
        --root _artifacts/_main/<date>_<slug> --cwd <worktree> -- python3 .agents/scripts/tests/run_all.py

FOUR results, not two. `unrunnable` is its own state because `No module named ruff` means
the floor never ran, and the house rule is that a missing tool is a FINDING, not a skip
(`/cicd-code-review` Step 3.5). Collapsing it into `fail` loses that distinction; collapsing
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
    # Wave 4 (3) review, finding R5 - the exit-1-vs-exit-2 ambiguity the Wave 4 audit left
    # open under "Four gates". A tool that grades its own findings (workflow_lint: 1 =
    # warnings, 2 = errors) loses that grading if every non-zero collapses to `fail`. The
    # caller declares which code means "advisory findings, nothing blocking" via
    # --warn-exit; it is a FOURTH result, never a pass, so the finding still has to be
    # read - it just does not block. Without this, an all-warnings lint reads `fail` in the
    # verdict's evidence and the gate gets ignored, which is the failure this whole receipt
    # contract exists to prevent.
    # AIDEV-NOTE: ONE declared code per call, never a set - that is what stops a real error
    # (exit 2) being laundered into advice. Test 2d pins it; 2e pins the unflagged default.
    if warn_exit is not None and exit_code == warn_exit:
        return "warn"
    return "fail"


def receipt_dir(project: Path, story: str, flat: bool = False) -> Path:
    # `flat` is the Task lane (SCC-146): `project` is already the one task's artifacts dir
    # (`_artifacts/_main/<date>_<slug>/`), so receipts land at <root>/gates/<gate>.json with
    # no story segment. Default False keeps the story lane and closeout_preflight's calls
    # byte-identical.
    if flat:
        return project / "gates"
    return project / wf.GATES_REL / wf.norm_id(story)



def _porcelain_z_paths(z: str) -> list[str]:
    """Paths from `git status --porcelain -z`, in git's order, both sides of a rename/copy.

    Entries are NUL-terminated `XY path`; when X or Y is R/C the ORIGINAL path follows as
    its own NUL-terminated field. Untracked (`??`) and ignored (`!!`) rows are ordinary
    entries. Nothing here is quoted, so what comes back is the exact filename."""
    fields = z.split("\0")
    out: list[str] = []
    k = 0
    while k < len(fields):
        entry = fields[k]
        k += 1
        if not entry:
            continue
        xy, path = entry[:2], entry[3:]
        if path:
            out.append(path)
        if ("R" in xy or "C" in xy) and k < len(fields) and fields[k]:
            out.append(fields[k])          # the rename/copy SOURCE - dirt too
            k += 1
    return out


def _own_output_rel(work: Path, out_dir: Path) -> str | None:
    """The receipt's OWN output dir as a repo-root-relative prefix, or None.

    `git status --porcelain` reports paths relative to the top of the work tree, and
    `out_dir` is absolute, so the two only compare through `rev-parse --show-toplevel`.
    Returns with a TRAILING SLASH: the prefix is anchored on the directory boundary, so a
    sibling merely NAMED like the dir (`gates_old/`, `gatesnotes.md`) is not swallowed by
    a bare `startswith("gates")`. None when the dir is outside this work tree - and None
    means NO exemption, which is the strict behaviour this script had before.
    """
    top = wf.git(["rev-parse", "--show-toplevel"], work).stdout.strip()
    if not top:
        return None
    try:
        rel = out_dir.resolve().relative_to(Path(top).resolve())
    except (ValueError, OSError):
        return None
    return rel.as_posix().rstrip("/") + "/"


def _measure_dirt(work: Path, out_dir: Path) -> list[str]:
    """Tree dirt, MINUS the receipt this script is about to write (SCC-178).

    The writer's own output lands inside the tree it measures (`<root>/gates/<gate>.json`),
    so the second stamp of a lane read DIRTY because the first one's receipt was untracked -
    and every lane paid a second full suite run to clear a smudge it had made itself.
    The exemption is the writer's OWN directory and nothing else: not `_artifacts/`, not
    every `gates/`, not a sibling of it. `task_preflight` reads `dirty_paths` to decide
    whether a gate SKIP is authorized, so anything wider hands out that skip over real dirt.

    ⛔ The collapse. `git status` reports an untracked DIRECTORY as ONE entry, so a story
    lane whose whole `_bmad-output/gates/` is new reports the ANCESTOR, not our dir - and
    that ancestor also holds OTHER stories' receipts, which are somebody else's output.
    Ancestor entries are therefore re-read with `-uall` (scoped by pathspec, so the expansion
    is one subtree, not the repo) and the file-level paths are filtered individually.
    """
    raw = _porcelain_z_paths(wf.git(["status", "--porcelain", "-z"], work).stdout)
    own = _own_output_rel(work, out_dir)
    if not own:
        return raw
    paths: list[str] = []
    for entry in raw:
        if entry.endswith("/") and own.startswith(entry):
            sub = _porcelain_z_paths(
                wf.git(["status", "--porcelain", "-z", "-uall", "--", entry], work).stdout)
            paths.extend(sub or [entry])
        else:
            paths.append(entry)
    return [x for x in paths if not x.startswith(own)]


def cmd_run(project: Path, story: str, gate: str, command: list[str],
            allow_fail: bool, cwd: Path | None, warn_exit: int | None = None,
            flat: bool = False) -> int:
    if not command:
        wf.die("no command given - put it after `--`")
    work = cwd or project
    sha_before = wf.git_head(work)
    # `-z`: NUL-separated, NO C-quoting, and a rename/copy entry carries its ORIGINAL path
    # as the next field. The line-form parse (`ln[3:].split(" -> ")[-1]`) kept the quotes on
    # any path git quotes (non-ASCII, tabs, a literal quote) and dropped a rename's old side —
    # both are misreads of the tree the receipt claims to describe (SCC-154 review #7,
    # fixed SCC-160). Both sides of a rename are dirt: the reader that exempts
    # `_artifacts/`-only dirt must SEE `code.py -> _artifacts/x.md` moved code.
    # ...and the receipt this run is about to write is NOT dirt - see _measure_dirt (SCC-178).
    out_dir = receipt_dir(project, story, flat)
    dirty_paths = _measure_dirt(work, out_dir)
    dirty = bool(dirty_paths)

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
        # WHICH paths were dirty, so a READER can apply policy (e.g. task_preflight exempts
        # `_artifacts/`-only dirt, C6). The recorder itself stays strict: `dirty_tree` is
        # unchanged and this field is additive — an older receipt without it gets no
        # exemption anywhere. A rename records BOTH paths (old and new are each dirt).
        "dirty_paths": dirty_paths,
        "totals": _totals(output),
        "command": command,
        "cwd": str(work),
        "duration_s": elapsed,
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output_tail": output[-1500:],
    }
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


def receipt_defect(data: dict | None) -> str | None:
    """The RESULT half of receipt validity, shared by every reader (SCC-154, finding 10:
    one receipt format, one reader — the rationale task_preflight already imports this
    module under). Returns the defect (`unreadable`, `result=fail`, ...) or None when the
    result is usable (pass/warn). Staleness and dirty-tree POLICY stay with the caller —
    the two consumers deliberately differ there (closeout_preflight: tree-identity + warn
    on dirt; task_preflight: code-fresh + `_artifacts/`-exempt dirt)."""
    if data is None:
        return "unreadable"
    if data.get("result") not in ("pass", "warn"):
        return f"result={data.get('result')}"
    return None


def check_receipt(repo: Path, data: dict, gate: str, target: str | None,
                  rep: wf.Report) -> None:
    """One receipt against one target commit. Shared with closeout_preflight so the two
    never disagree about what 'stale' means. The RESULT half reads through
    receipt_defect() — the same helper task_preflight reads — so the two consumers cannot
    drift about what a usable result is (SCC-154 review: this docstring claimed that
    unification one commit before it was true)."""
    if data.get("result") == "warn":
        # Advisory findings: recorded, never blocking. Still WARN-not-INFO so it is read.
        rep.warn("gates", f"{gate}: advisory findings only (exit {data.get('exit_code')}) "
                          f"- not blocking, but read them")
    elif receipt_defect(data):
        rep.err("gates", f"{gate}: {receipt_defect(data)} "
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


def load_receipt(project: Path, story: str, gate: str, rep: wf.Report,
                 flat: bool = False) -> dict | None:
    path = receipt_dir(project, story, flat) / f"{gate}.json"
    if not path.is_file():
        rep.err("gates", f"{gate}: NO RECEIPT - the gate has no evidence it ran")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rep.err("gates", f"{gate}: unreadable receipt ({exc})")
        return None


def cmd_check(project: Path, story: str, require: list[str], advisory: bool,
              sha: str | None, cwd: Path | None, flat: bool = False) -> int:
    # The receipt was stamped wherever the gate RAN (often a story worktree), so the repo
    # that resolves its commits may not be the project root.
    repo = cwd or project
    target = sha or wf.git_head(repo)
    rep = wf.Report()

    for gate in require:
        data = load_receipt(project, story, gate, rep, flat)
        if data is not None:
            check_receipt(repo, data, gate, target, rep)

    rep.print_human(f"gate_receipt check - {wf.norm_id(story)}")
    code = rep.exit_code()
    if advisory and code == 2:
        print("-- ADVISORY MODE: reporting only, not blocking "
              "(remove --advisory to enforce) --")
        return 0
    return code


def cmd_list(project: Path, story: str, flat: bool = False) -> int:
    out_dir = receipt_dir(project, story, flat)
    if not out_dir.is_dir():
        where = f"{project}/gates" if flat else f"{wf.GATES_REL}/{wf.norm_id(story)}"
        print(f"(no receipts under {where})")
        return 1
    for path in sorted(out_dir.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        print(f"{d['gate']:>12}  {d['result']:<10} exit={d['exit_code']:<4} "
              f"{str(d.get('sha'))[:8]}  {d.get('totals') or ''}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Execute gates and record tamper-evident receipts")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # SCC-146: `--task` is an argparse ALIAS for `--story` (one dest, one receipt field —
    # no schema churn), and `--root <dir>` is the Task lane's resolver bypass: no board
    # exists there, so wf.resolve_project_root() would die. With --root, receipts live at
    # <root>/gates/<gate>.json; without it, behaviour is byte-identical to before.
    p_run = sub.add_parser("run")
    p_run.add_argument("--story", "--task", dest="story", required=True)
    p_run.add_argument("--gate", required=True)
    p_run.add_argument("--project")
    p_run.add_argument("--root", help="task-lane receipts root (the task's _artifacts dir); "
                                      "bypasses project resolution entirely")
    p_run.add_argument("--cwd", help="run the command here (e.g. a worktree) instead of the project root")
    p_run.add_argument("--allow-fail", action="store_true",
                       help="always exit 0; the receipt still records the true result")
    p_run.add_argument("--warn-exit", type=int, metavar="N",
                       help="exit code N means ADVISORY findings, not failure (e.g. "
                            "workflow_lint: 1=warnings, 2=errors -> --warn-exit 1). "
                            "Records result=warn: non-blocking, but never a pass.")
    p_run.add_argument("command", nargs=argparse.REMAINDER)

    p_check = sub.add_parser("check")
    p_check.add_argument("--story", "--task", dest="story", required=True)
    p_check.add_argument("--project")
    p_check.add_argument("--root", help="task-lane receipts root; see `run --root`")
    p_check.add_argument("--require", required=True, help="comma-separated gate names")
    p_check.add_argument("--sha", help="check against THIS commit (the shipping sha) "
                                       "instead of the current HEAD")
    p_check.add_argument("--cwd", help="resolve commits in this repo/worktree - use the same "
                                       "one `run --cwd` used, or its shas are unknown here")
    p_check.add_argument("--advisory", action="store_true",
                         help="report but do not block (first-sprint rollout only)")

    p_list = sub.add_parser("list")
    p_list.add_argument("--story", "--task", dest="story", required=True)
    p_list.add_argument("--project")
    p_list.add_argument("--root", help="task-lane receipts root; see `run --root`")
    p_list.add_argument("--cwd", help="anchor for a RELATIVE --root; without it a relative "
                                      "root resolves against the invoker's cwd")

    args = ap.parse_args()
    # ⛔ With --root the resolver is never called — that is the entire point (SCC-146):
    # the Task lane has no board file for it to find, and a "helpful" fallback here would
    # resurrect the exact blocker this flag removes. Without --root, unchanged.
    flat = bool(getattr(args, "root", None))
    if flat and getattr(args, "project", None):
        wf.die("--project and --root are mutually exclusive - --root IS the receipts "
               "root, and a project resolution beside it could only disagree (SCC-154)")
    if flat:
        cwd_arg = getattr(args, "cwd", None)
        if args.cmd == "run" and not cwd_arg:
            # Without --cwd, root-mode `run` executed the gate INSIDE the artifacts dir and
            # recorded `fail` for a suite that never ran — a fabricated result from the one
            # tool whose whole point is that results cannot be fabricated (SCC-146 review
            # finding 5, adjacent id 10).
            wf.die("run --root requires --cwd: without it the gate executes inside the "
                   "artifacts dir and records `fail` for a suite that never ran (SCC-154)")
        root = Path(args.root)
        if not root.is_absolute() and cwd_arg:
            # A relative --root resolves against --cwd WHEN SUPPLIED: from the wrong
            # checkout, `run` landed the receipt as an untracked stray with success-shaped
            # output (SCC-146 review finding 5 / compound C5) — which is why `run` REQUIRES
            # --cwd above. For `check`/`list` the flag is optional and a relative root
            # without it still resolves against the invoker's cwd — read-only, and the
            # failure is a loud "no receipt", never a stray write (SCC-154 review).
            root = Path(cwd_arg).resolve() / root
        project = root.resolve()
    else:
        project = wf.resolve_project_root(args.project)

    if args.cmd == "run":
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        cwd = Path(args.cwd).resolve() if args.cwd else None
        return cmd_run(project, args.story, args.gate, command, args.allow_fail, cwd,
                       args.warn_exit, flat)
    if args.cmd == "check":
        gates = [g.strip() for g in args.require.split(",") if g.strip()]
        return cmd_check(project, args.story, gates, args.advisory, args.sha,
                         Path(args.cwd).resolve() if args.cwd else None, flat)
    return cmd_list(project, args.story, flat)


if __name__ == "__main__":
    sys.exit(main())
