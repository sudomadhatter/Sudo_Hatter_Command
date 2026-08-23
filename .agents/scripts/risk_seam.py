#!/usr/bin/env python3
"""The risk-classification seam the reviews and audits call. (SCC-228 seam · SCC-278 body)

`/smh-code-review` Step 0.7 and `/smh-self-audit`'s Parity + Blast lens want to know which of the
changed files are risky and which changed functions have no test. SCC-228 built this seam so the
audit could land before a classifier existed; SCC-224 was meant to fill it with GitNexus and left
it empty, so for two tickets `classify()` returned `unclassified` for every input and the lens ran
on nothing. This file is the fill: the answer now comes from the local **code graph**.

The seam's contract, and what `test_risk_seam.py` pins:

- `classify(paths, root=None)` returns the fixed shape
      {"status": "unclassified" | "classified", "test_links": int,
       "tiers": {<path>: {risk, flows, untested}}}
  `risk` is the HIGHEST risk score among that file's changed functions (a file is as risky as its
  worst change, not its average). `flows` is how many affected flows touch it. `untested` names the
  changed functions the graph found no test for.
- ⛔ `test_links` is how many TESTED_BY edges name a real subject, and it is what tells you whether
  `untested` means anything. **In the command centre it is 0** — the graph's 24 test edges all point
  at builtins or a test's own assert methods, so `untested` lists every changed function whether or
  not it is tested. `risk` and `flows` are unaffected (CALLS resolves 22135/22135). When
  `test_links` is 0, read `untested` as "the graph has no opinion", never as a finding.
- `gates_audit(result)` is **False for every possible return** — the classifier INFORMS the lens, it
  never gates the audit. A future classifier that wants a veto must change that function and its
  test in the same commit, which is exactly the visibility this seam exists to force.

─── ⛔ It degrades. It never depends. ──────────────────────────────────────────────────────────
The graph is machine-local, absent from a fresh clone, absent from a new worktree, and stale the
moment you commit. **The pure-Python path stays the normal one** (operator ruling 2026-08-19). So
every unusable state — no CLI, no graph, a graph built at a different commit, a tool that errors,
hangs, or answers nonsense — returns the same defined `unclassified` shape this file has always
returned. An audit that cannot run because a machine-local index is missing is a worse defect than
an audit with less context.

**Freshness is checked against the graph's own stamp**, not a timestamp: `git_head_sha` in the db's
`metadata` table must equal `HEAD`. Same check `check_maps.py` check 9 makes, for the same reason —
a graph one commit behind answers confidently about code that no longer exists.

**The base is a MERGE-BASE, never the branch name.** `--base main` is a two-dot diff: it includes
everything that landed on `main` since the lane started, which measured 104 files for a 12-file
lane. `git merge-base HEAD main` is the lane's own work. This is the single most expensive mistake
available here, because the wrong answer looks entirely normal.

**The CLI is PROBED, never named.** `pipx` installs it to `~/.local/bin`, which is NOT on `PATH` in
every shell this runs from — measured on this Mac, in this repo. Naming a binary and assuming it
resolves is the exit-127 class of bug (SCC-77): it fails silently and looks like a quiet answer.

Stdlib only; `python3` (Mac) / `python` (PC). Never imports the `code_review_graph` package — it is
a pipx-isolated tool, not a library, and importing it would make this script unrunnable everywhere
the tool is not installed. CLI:  risk_seam.py classify <path> [<path> ...]
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

FIXED_UNCLASSIFIED: dict = {"status": "unclassified", "tiers": {}}

TIMEOUT_S = 90
"""A hung tool must not wedge a review. Past this, the seam degrades like any other failure."""

TRUNKS = ("main", "origin/main", "master", "origin/master")
"""Merge-base candidates, in order. The first that resolves wins."""


def _unclassified() -> dict:
    """A FRESH dict every time — callers mutate what they are handed."""
    return {"status": "unclassified", "tiers": {}}


def _rooted(result: dict, top: "Path | None") -> dict:
    """Echo WHICH repo the answer is about, whenever one was resolved (SCC-289).

    ⛔ Without this a caller cannot tell "no graph in the project" from "I classified the wrong
    tree". The four review/audit doors run from the command centre while reviewing a PROJECT
    worktree; before `--repo` existed they all resolved the CENTRE, which has no graph, so every
    project review returned `unclassified` and read as a missing index. The echo makes the mistake
    visible in the output the reviewer already pastes.

    Absent when no root resolved at all — and absent on the empty-input early return, which stays
    byte-identical to the shape SCC-228 froze.
    """
    if top is not None:
        result["root"] = str(top)
    return result


def _git(root: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                           text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _repo_root(root: str | os.PathLike | None) -> Path | None:
    if root:
        return Path(root)
    top = _git(Path.cwd(), "rev-parse", "--show-toplevel")
    return Path(top) if top else None


def _test_link_count(root: Path) -> int:
    """How many TESTED_BY edges name a REAL subject in this repo. Unreadable reads as 0.

    ⛔ NOT `count(*)`, and the difference is the whole point. Measured in the command centre
    2026-08-22, during SCC-270's own review: the graph held **24** TESTED_BY edges and **not one**
    named a subject under test. 21 pointed at bare builtins (`str`, `Path`, `mkdir`, `isinstance`)
    and 3 at a test class's own `assertEqual`/`assertIn`. A raw count would have reported 24 and
    read as "the test layer works".

    What it actually means when this returns 0: the graph has **no test-link data**, so every
    changed function lands in `untested` — including the thoroughly tested ones. `untested` is then
    NOISE, not signal, and the callers say so. The call graph is unaffected: CALLS resolved
    22135/22135 in the same measurement, so `risk` and `flows` stay trustworthy while this does not.

    Two shapes count as junk: a subject with no `/` in it (a bare unresolved name — a builtin, or a
    method the resolver could not place), and a subject whose own file is a test file (a test's
    internal helper, not a thing under test).
    """
    db = root / ".code-review-graph" / "graph.db"
    if not db.exists():
        return 0
    try:
        import sqlite3
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            rows = con.execute(
                "SELECT source_qualified FROM edges WHERE kind = 'TESTED_BY'").fetchall()
        finally:
            con.close()
    except Exception:                       # noqa: BLE001 — no edges table, corrupt db: 0, not a crash
        return 0
    real = 0
    for row in rows:
        subject = str((row[0] if row else "") or "")
        if "/" not in subject:              # a bare name the resolver never placed
            continue
        base = subject.split("::", 1)[0].rsplit("/", 1)[-1]
        if base.startswith("test_") or base.endswith("_test.py"):
            continue                        # a test's own helper, not a subject under test
        real += 1
    return real


def _graph_is_fresh(root: Path) -> bool:
    """The graph's own `git_head_sha` must equal HEAD. Anything unreadable reads as NOT fresh."""
    db = root / ".code-review-graph" / "graph.db"
    if not db.exists():
        return False
    try:
        import sqlite3
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            row = con.execute(
                "SELECT value FROM metadata WHERE key = 'git_head_sha'").fetchone()
        finally:
            con.close()
    except Exception:                       # noqa: BLE001 — corrupt db is "not fresh", not a crash
        return False
    stamp = (row[0] if row and row[0] else "").strip()
    head = _git(root, "rev-parse", "HEAD")
    return bool(stamp and head and stamp == head)


def _cli() -> str | None:
    """`PATH` first, then pipx's default bin dir — probed, never assumed (see the module docstring)."""
    found = shutil.which("code-review-graph")
    if found:
        return found
    fallback = Path.home() / ".local" / "bin" / "code-review-graph"
    return str(fallback) if fallback.exists() else None


def _base(root: Path) -> str | None:
    """The lane's merge-base with the first trunk that resolves. None → let the tool default."""
    for trunk in TRUNKS:
        mb = _git(root, "merge-base", "HEAD", trunk)
        if mb:
            return mb
    return None


def _rel(root: Path, path: str) -> str | None:
    """Repo-relative POSIX form. The tool emits absolute paths; callers pass relative ones."""
    p = Path(path)
    if p.is_absolute():
        try:
            p = p.relative_to(root)
        except ValueError:
            return None
    return p.as_posix()


def _flow_files(flow: object) -> set[str]:
    """Which files a flow touches, tolerating the shapes this key can take.

    ⛔ Deliberately permissive: `affected_flows` was EMPTY in every run available when this was
    written, so its populated shape is unverified. Reading three plausible keys and shrugging at a
    fourth degrades to `flows: 0` — a tier that under-reports — where a KeyError would take the
    whole classification down. `test_risk_seam.py` case L is what will surface the real shape the
    first time a run populates it.
    """
    if not isinstance(flow, dict):
        return set()
    out: set[str] = set()
    for key in ("file_path", "file"):
        val = flow.get(key)
        if isinstance(val, str):
            out.add(val)
    val = flow.get("files")
    if isinstance(val, list):
        out.update(v for v in val if isinstance(v, str))
    return out


def _detect_changes(root: Path, exe: str) -> dict | None:
    cmd = [exe, "detect-changes", "--repo", str(root)]
    base = _base(root)
    if base:
        cmd += ["--base", base]
    try:
        r = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True,
                           timeout=TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    try:
        out = json.loads(r.stdout)
    except ValueError:
        return None
    return out if isinstance(out, dict) else None


def classify(paths: list[str], root: str | os.PathLike | None = None) -> dict:
    """Risk tiers for `paths`, from the local code graph. `unclassified` whenever it cannot.

    A requested path the graph has nothing to say about is simply ABSENT from `tiers` — never a
    fabricated `0.0`. "Not in this diff" and "changed but low risk" are different facts, and a
    reviewer acting on the second when the first is true is exactly the confident-wrong answer this
    seam is supposed to prevent.
    """
    if not paths:
        return _unclassified()
    top = None
    try:
        top = _repo_root(root)
        if top is None or not _graph_is_fresh(top):
            return _rooted(_unclassified(), top)
        exe = _cli()
        if not exe:
            return _rooted(_unclassified(), top)
        data = _detect_changes(top, exe)
        if data is None:
            return _rooted(_unclassified(), top)

        wanted = {}
        for given in paths:
            rel = _rel(top, given)
            if rel:
                wanted.setdefault(rel, given)

        tiers: dict[str, dict] = {}
        for fn in data.get("changed_functions") or []:
            if not isinstance(fn, dict) or fn.get("is_test"):
                continue
            rel = _rel(top, str(fn.get("file_path") or ""))
            if rel not in wanted:
                continue
            score = fn.get("risk_score")
            tier = tiers.setdefault(wanted[rel], {"risk": 0.0, "flows": 0, "untested": []})
            if isinstance(score, (int, float)):
                tier["risk"] = max(tier["risk"], float(score))

        for gap in data.get("test_gaps") or []:
            if not isinstance(gap, dict):
                continue
            rel = _rel(top, str(gap.get("file") or gap.get("file_path") or ""))
            key = wanted.get(rel)
            if key in tiers and gap.get("name"):
                tiers[key]["untested"].append(str(gap["name"]))

        for flow in data.get("affected_flows") or []:
            for touched in _flow_files(flow):
                rel = _rel(top, touched)
                key = wanted.get(rel)
                if key in tiers:
                    tiers[key]["flows"] += 1

        return _rooted(
            {"status": "classified", "test_links": _test_link_count(top), "tiers": tiers}, top)
    except Exception:                       # noqa: BLE001 — ⛔ the seam degrades, never raises
        return _rooted(_unclassified(), top)


def gates_audit(result: dict) -> bool:
    """The audit-semantics pin: NO classifier return gates the audit — it informs the
    Parity + Blast lens and nothing else. Deliberately ignores its input."""
    _ = result
    return False


USAGE = (
    "usage: risk_seam.py classify [--repo <repo-root>] <path> [<path> ...]\n"
    "  --repo  the repository the paths belong to. Default: the git repo of CWD.\n"
    "          Pass it from any door that reviews a tree it is not standing in - a review run\n"
    "          from the command centre with no --repo classifies the CENTRE (SCC-289).\n"
)


def _bad(msg: str) -> int:
    print(f"risk_seam.py: {msg}\n{USAGE}", file=sys.stderr)
    return 2


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] != "classify":
        print(USAGE, file=sys.stderr)
        return 2

    rest, root, paths, i = args[1:], None, [], 0
    while i < len(rest):
        a = rest[i]
        if a == "--repo":
            # ⛔ A bare --repo is exit 2, never a silent fall back to CWD. An unset shell variable
            # expands to nothing, and the quiet fallback is exactly the wrong-tree answer this
            # flag exists to stop.
            if i + 1 >= len(rest):
                return _bad("--repo needs a value")
            root, i = rest[i + 1], i + 2
            continue
        if a.startswith("--repo="):
            root = a.split("=", 1)[1]
            if not root:
                return _bad("--repo needs a value")
            i += 1
            continue
        # ⛔ AN UNKNOWN FLAG IS AN ERROR, NOT A PATH. Falling through to `paths.append` meant a
        # one-character typo (`--rep`) left `root` unset, and `classify` then answered about CWD -
        # the command centre - with a confident `root` echo naming the wrong tree. That is exactly
        # the silent fallback `--repo` exists to stop, arriving through the back door.
        if a.startswith("--"):
            return _bad(f"unknown option {a}")
        paths.append(a)
        i += 1

    if not paths:
        return _bad("classify needs at least one path")
    print(json.dumps(classify(paths, root=root), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
