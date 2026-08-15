"""Shared fixtures for the task_preflight suites (SCC-156).

Split out when `test_task_preflight.py` was divided at its SCC-146 seam: the file was 1,557
lines and 105 s, the single slowest thing in `run_all`, so it set the floor for the whole
parallel suite. Both halves build the same fixture repos, so the builders live here rather
than being duplicated or imported across test files.

Not named `test_*`, deliberately — `run_all.py` auto-discovers by that prefix and this module
declares no cases of its own.
"""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from _harness import run_script

JIRA_CONF = '# test fixture\nJIRA_KEYS="SCC"\n'

WALKTHROUGH = """---
type: walkthrough
story: SCC-11
---

# SCC-11 — a task

## Task Checklist
- [x] did the thing

## Your Actions

Nothing is owed.
"""

# The same walkthrough WITHOUT the section `jira_feed.py finish` reads. Its own fixture so the
# positive control above stays a real control (SCC-155).
WALKTHROUGH_NO_ACTIONS = """---
type: walkthrough
story: SCC-11
---

# SCC-11 — a task

## Task Checklist
- [x] did the thing
"""


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit(repo: Path, message: str) -> None:
    git(repo, "add", "-A")            # fixture only; the real lane is explicit-paths
    git(repo, "commit", "--no-verify", "-q", "-m", message)


MANIFEST = ("task_key: SCC-11\nprimary_repo: repo\nbranch: chore/SCC-11-thing\n"
            "close_command: smh-close-task-merge-tree\nsecondary_repos: []\n")


def make_repo(root: Path, *, deployable: bool = False, remote: bool = True,
              walkthrough: bool = True, manifest: bool = True, hooks: bool = True,
              ci: bool = False) -> Path:
    """A repo standing on `main`, optionally with a bare origin it is in sync with."""
    repo = root / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "config", "commit.gpgsign", "false")
    write(repo, ".agents/jira.conf", JIRA_CONF)
    write(repo, ".agents/scripts/tests/run_all.py", "# fixture\n")
    # SCC-110: a repo carrying `.agents/jira.conf` is CLAIMING a commit gate, so the fixture
    # has to carry the hook that enforces it and the per-machine switch that runs it. Without
    # these the fixture modelled a repo in a state none of the real ones are in — declared
    # gates, nothing running them — and the arm-check rightly objected.
    if hooks:
        write(repo, ".githooks/commit-msg", "#!/bin/sh\nexit 0\n")
        (repo / ".githooks/commit-msg").chmod(0o755)
        # SCC-140: the dispatcher alone was NOT enough, and the gap was the bug. This fixture
        # declared a Jira project and shipped the hook that enforces it while tracking ZERO
        # gate scripts - so every dispatcher's `[ -x ... ] || exit 0` allowed the operation,
        # and the arm-check certified ARMED with no findings. No real repo is in that state;
        # the fixture was modelling the defect. It now carries the inner script the dispatcher
        # actually calls, and the flag that arms it.
        write(repo, ".agents/scripts/git-hooks/commit-msg-jira.sh", "#!/bin/sh\nexit 0\n")
        (repo / ".agents/scripts/git-hooks/commit-msg-jira.sh").chmod(0o755)
        write(repo, ".agents/scripts/git-hooks/JIRA-ENFORCE", "armed\n")
        git(repo, "config", "core.hooksPath", ".githooks")
    write(repo, "README.md", "# fixture\n")
    if deployable:
        write(repo, "backend/app.py", "x = 1\n")
        write(repo, "frontend/page.tsx", "export default () => null\n")
    if ci:
        # A repo carrying CI. Independent of `deployable` on purpose: the whole point of
        # SCC-118's split is that these two are different questions, and the fixture has to
        # be able to ask them separately.
        write(repo, ".github/workflows/gate.yml", "name: gate\non: [push]\n")
    if walkthrough:
        write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/walkthrough.md", WALKTHROUGH)
    if manifest:
        write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml", MANIFEST)
    commit(repo, "SCC-11 chore: base")
    if remote:
        bare = root / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], capture_output=True)
        git(repo, "remote", "add", "origin", str(bare))
        git(repo, "push", "-q", "-u", "origin", "main")
    return repo


def branch(repo: Path, name: str, files: dict[str, str], *, push: bool = True) -> None:
    git(repo, "checkout", "-q", "-b", name)
    for rel, text in files.items():
        write(repo, rel, text)
    commit(repo, "SCC-11 chore: the work")
    if push:
        git(repo, "push", "-q", "-u", "origin", name)


# ── The board stub (SCC-119) ───────────────────────────────────────────────────
# `check_children` is the first thing in this script that talks to the network, and these
# fixtures use REAL Jira keys (SCC-11 exists). Without a stub the suite would query the live
# board once per preflight - slow, machine-dependent, and green or red by accident. The stub
# is a real executable for the same reason jira_feed's is: the production path (subprocess,
# --json, exit code) then runs unchanged.
BOARD_STUB = r'''
import json, os, sys
state = json.load(open(os.environ["PF_BOARD_STATE"], encoding="utf-8"))
args = sys.argv[1:]
if args[:3] != ["jira", "workitem", "search"]:
    print("stub: unhandled " + " ".join(args), file=sys.stderr)
    sys.exit(9)
fields = ""
if "--fields" in args:
    fields = args[args.index("--fields") + 1]
# The real acli REJECTS `parent` as a --fields value on search (exit 1). Enforced here so a
# caller that asks for it fails in the suite exactly as it would in production - otherwise
# the natural mistake reads as "no children" and the gate passes vacuously.
if "parent" in [f.strip() for f in fields.split(",")]:
    print("Error: field 'parent' is not allowed", file=sys.stderr)
    sys.exit(1)
if state.get("fail"):
    print("Error: the search failed", file=sys.stderr)
    sys.exit(1)
print(json.dumps([{"key": k, "fields": {"status": {"name": s}, "summary": "child"}}
                  for k, s in state.get("children", [])]))
'''


def board(root: Path, children: object = (), fail: bool = False) -> None:
    """Point ACLI_BIN at a stub board holding `children` = [(key, status), ...]."""
    stub_py = root / "board_stub.py"
    stub_py.write_text(BOARD_STUB, encoding="utf-8")
    if os.name == "nt":
        launcher = root / "acli.bat"
        launcher.write_text(f'@echo off\r\n"{sys.executable}" "{stub_py}" %*\r\n',
                            encoding="utf-8")
    else:
        launcher = root / "acli"
        launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{stub_py}" "$@"\n',
                            encoding="utf-8")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    state = root / "board_state.json"
    state.write_text(json.dumps({"children": list(children), "fail": fail}),
                     encoding="utf-8")
    os.environ["ACLI_BIN"] = str(launcher)
    os.environ["PF_BOARD_STATE"] = str(state)


def preflight(repo: Path, *extra: str, expect: str = "SCC-11") -> tuple[int, str]:
    # --expect-key is REQUIRED since SCC-64; the fixtures' branches carry SCC-11.
    # A childless board by default, unless this repo's test set one up - so every pre-SCC-119
    # case keeps its exact verdict and none of them reach the real network.
    #
    # ⚠ Test the FILE, not the env var. Each block runs in its own TempDir, so the state file
    # is deleted at the end of the block while `os.environ` survives the whole process - an
    # env-var-only guard left every later block pointing at a path that no longer exists, the
    # stub crashed, and eleven previously-clean cases went red for a reason that had nothing
    # to do with what they test.
    state = os.environ.get("PF_BOARD_STATE")
    if not state or not Path(state).exists():
        board(repo.parent)
    return run_script("task_preflight.py", "--repo", str(repo),
                      "--expect-key", expect, *extra)


# ── Fixtures shared across blocks — MODULE level, deliberately (SCC-156) ─────────────
# These were nested inside the blocks that first needed them. Under `--case` a block can
# run alone, so a helper defined inside a sibling block is simply not there: five blocks
# died with UnboundLocalError the first time every block was run solo. A fixture used by
# more than the block that introduced it belongs where every block can see it.
def secondary(t: Path, *, keys: str = "AVCH", clean: bool = True, pushed: bool = True,
              store: str | None = "ok", checked_out: bool = True) -> Path:
    """A sibling repo under `Projects/`, like a real submodule checkout.

`Projects/` is gitignored in the primary so the sibling reads as untracked-but-clean -
which is what `ignore = all` produces for real, and is exactly why the primary's own
`git status` cannot see a dirty project half."""
    proj = t / "repo" / "Projects" / "SECONDARY"
    proj.mkdir(parents=True)
    if not checked_out:
        return proj                                   # an empty stub: submodule not init'd
    git(proj, "init", "-q", "-b", "main")
    git(proj, "config", "user.email", "t@example.com")
    git(proj, "config", "user.name", "T")
    git(proj, "config", "commit.gpgsign", "false")
    write(proj, ".agents/jira.conf", f'JIRA_KEYS="{keys}"\n')
    write(proj, "README.md", "# secondary\n")
    if store:
        mem = "_artifacts/_memory"
        write(proj, f"{mem}/a-fact.md",
              "---\nname: a-fact\ndescription: one fact\n---\n\nThe fact.\n")
        # "broken" seeds an ORPHAN: a memory file with no index line, invisible to every
        # session. Same defect check_store() catches in the lobby - the point of this case
        # is that here it must BLOCK, not merely be reported.
        index = "# Index\n- [A fact](a-fact.md) - hook\n" if store == "ok" else "# Index\n"
        write(proj, f"{mem}/MEMORY.md", index)
    commit(proj, "AVCH-1 chore: base")
    bare = t / "secondary-origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], capture_output=True)
    git(proj, "remote", "add", "origin", str(bare))
    if pushed:
        git(proj, "push", "-q", "-u", "origin", "main")
    if not clean:
        write(proj, "uncommitted.md", "in flight\n")
    return proj

def with_secondary(t: Path, ticket: str = "AVCH-53", **kw) -> Path:
    repo = make_repo(t)
    write(repo, ".gitignore", "Projects/\n")
    write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml",
          "task_key: SCC-11\nprimary_repo: repo\nbranch: chore/SCC-11-thing\n"
          "close_command: smh-close-task-merge-tree\nsecondary_repos:\n"
          f"  - repo: Projects/SECONDARY\n    landing: independent-task\n"
          f"    ticket: {ticket}\n")
    commit(repo, "SCC-11 chore: declare the secondary repo")
    git(repo, "push", "-q", "origin", "main")
    branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
    secondary(t, **kw)
    return repo


ADIR = "_artifacts/_main/2026-08-08_scc-11-thing"

def stamp_and_verdict(repo: Path, verdict: str, *, receipt: bool = True,
                      commit_docs: bool = True) -> str:
    """The real close-out shape: receipt stamped on a CLEAN tree at the code sha,
then the walkthrough (verdict citing that sha) lands as an artifacts-only commit."""
    sha = git(repo, "rev-parse", "HEAD").stdout.strip()
    if receipt:
        run_script("gate_receipt.py", "run", "--task", "SCC-11",
                   "--gate", "suite", "--root", str(repo / ADIR),
                   "--cwd", str(repo),
                   "--", sys.executable, "-c", "print('ok')")
    # The indented decoy is deliberate: prose ABOUT a verdict must never read as one.
    # VERDICT_RE anchors at line start; an unanchored mutant matches the decoy's FAIL
    # and every PASS case here goes red (the comment-literals-invert-grep class).
    write(repo, f"{ADIR}/walkthrough.md",
          WALKTHROUGH
          + "\n  (the reviewer writes Verdict: FAIL @ 0000000 when the gate is red)\n"
          + f"\n## Code Review (2026-08-08)\n\nVerdict: {verdict} @ {sha}\n")
    if commit_docs:
        commit(repo, "SCC-11 chore: walkthrough + receipts (artifacts only)")
        git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
    return sha


