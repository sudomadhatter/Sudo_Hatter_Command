#!/usr/bin/env python3
"""Contract checks for the published-edition staleness reporter (SCC-456).

⛔ EVERY CASE RUNS THE REAL SCRIPT AGAINST A REAL THROWAWAY GIT REPO, never a mock.
The whole of this script is git plumbing and file reads; a mocked `git` would pin the mock and
assert nothing about the thing that ships. The repos are seeded here so the test passes or fails
for reasons in the code rather than for whatever this lobby happens to contain today.

THE CONTRACT UNDER TEST, and it has exactly three clauses:
  1. it NEVER blocks - exit 0 on every path, including every failure path
  2. it is SILENT when clean
  3. it is LOUD, and distinctly so, in each state it cannot measure
A reporter that can block gets disarmed within a day, and a disarmed reporter is the same as none.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from _harness import Cases, TempDir

SCRIPTS = Path(__file__).resolve().parents[1]
SCRIPT = SCRIPTS / "teaching_edition_staleness.py"
PUBLISHED_REL = "Projects/sudo-command-center"


def git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


def seed_lobby(root: Path, commits: int = 3, day_span: int = 0) -> list[str]:
    """A lobby with `commits` commits on main and an `origin/main` ref that points at the tip.

    `day_span` back-dates the FIRST commit by that many days so an age can be measured without
    waiting for wall-clock time to pass.
    """
    root.mkdir(parents=True, exist_ok=True)
    git(["init", "-q", "-b", "main"], root)
    git(["config", "user.email", "t@example.invalid"], root)
    git(["config", "user.name", "T"], root)
    shas = []
    for i in range(commits):
        (root / f"f{i}.txt").write_text(f"{i}\n", encoding="utf-8")
        git(["add", f"f{i}.txt"], root)
        # An ABSOLUTE epoch, never "40 days ago": git's approxidate parses for --date but not for
        # GIT_COMMITTER_DATE, and this script measures the COMMITTER date, so only setting both to
        # a value git accepts in both places back-dates what is actually read.
        if i == 0 and day_span:
            when = f"{int(time.time()) - day_span * 86400} +0000"
            subprocess.run(
                ["git", "commit", "-q", "-m", f"c{i}", "--date", when],
                cwd=str(root),
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, "GIT_COMMITTER_DATE": when},
            )
        else:
            git(["commit", "-q", "-m", f"c{i}"], root)
        shas.append(
            subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(root),
                check=True, capture_output=True, text=True,
            ).stdout.strip()
        )
    # A local `origin/main` ref, so the script resolves the branch the TEAM pulls rather than
    # whatever local branch a lane happens to be sitting on.
    git(["update-ref", "refs/remotes/origin/main", shas[-1]], root)
    return shas


def run(root: Path, *extra: str) -> tuple[int, str]:
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(root), *extra],
        capture_output=True,
        text=True,
    )
    return p.returncode, (p.stdout + p.stderr).strip()


def stamp(root: Path, body: str) -> None:
    pub = root / PUBLISHED_REL
    pub.mkdir(parents=True, exist_ok=True)
    (pub / ".teaching-edition-source").write_text(body, encoding="utf-8")


def main() -> int:
    c = Cases("test_teaching_edition_staleness")

    if c.block("A · a fresh stamp is SILENT and exits 0"):
        with TempDir() as tmp:
            root = tmp / "lobby"
            shas = seed_lobby(root, commits=3)
            stamp(root, f"source_commit: {shas[-1]}\nsource_date:   x\nexported:      x\n")
            rc, out = run(root)
            c.check("A1 · exit 0", rc == 0, f"rc={rc}\n{out}")
            c.check("A2 · prints nothing when current", out == "", f"out={out!r}")

    if c.block("B · a stamp older than the budget REPORTS, in days AND commits"):
        with TempDir() as tmp:
            root = tmp / "lobby"
            shas = seed_lobby(root, commits=4, day_span=40)
            stamp(root, f"source_commit: {shas[0]}\nsource_date:   x\nexported:      x\n")
            rc, out = run(root, "--budget-days", "14")
            c.check("B1 · exit 0 - it reports, it never blocks", rc == 0, f"rc={rc}\n{out}")
            c.check("B2 · names the commit distance", "3 commits behind" in out, out)
            c.check("B3 · names the day distance", "days and" in out and " 40 days" in out, out)
            c.check("B4 · names the door that fixes it",
                    "/smh-publish-teaching-edition" in out, out)

    if c.block("C · inside the budget is silent even with commits behind"):
        with TempDir() as tmp:
            root = tmp / "lobby"
            shas = seed_lobby(root, commits=4)
            stamp(root, f"source_commit: {shas[0]}\nsource_date:   x\nexported:      x\n")
            rc, out = run(root, "--budget-days", "14")
            c.check("C1 · exit 0", rc == 0, f"rc={rc}\n{out}")
            # 3 commits behind but 0 days old. The budget is the DAY axis on purpose - main takes
            # ~50 commits a day here, so a commit budget would nag on every lane by lunchtime and
            # be switched off by dinner.
            c.check("C2 · silent: behind in commits, current in days", out == "", f"out={out!r}")

    if c.block("D · the UNSTAMPED case is loud and DISTINCT"):
        with TempDir() as tmp:
            root = tmp / "lobby"
            seed_lobby(root, commits=2)
            (root / PUBLISHED_REL).mkdir(parents=True, exist_ok=True)
            rc, out = run(root)
            c.check("D1 · exit 0", rc == 0, f"rc={rc}\n{out}")
            # An unmeasurable tree is strictly worse than a measurably stale one, so it must not
            # share wording with the stale case - the reader has to be able to tell "old" from
            # "unknowable" at a glance.
            c.check("D2 · says the age cannot be measured", "cannot be measured" in out, out)
            c.check("D3 · does NOT claim a distance it does not have",
                    "commits behind" not in out, out)

    if c.block("E · every unreadable state fails OPEN and still exits 0"):
        with TempDir() as tmp:
            # E1 - no submodule checked out at all: a normal clone state, not a problem to announce
            root = tmp / "a"
            seed_lobby(root, commits=1)
            rc, out = run(root)
            c.check("E1 · absent submodule is silent, exit 0", rc == 0 and out == "",
                    f"rc={rc} out={out!r}")

            # E2 - a stamp with no readable sha
            root2 = tmp / "b"
            seed_lobby(root2, commits=1)
            stamp(root2, "exported: yesterday, by hand\n")
            rc, out = run(root2)
            c.check("E2 · unparseable stamp reports, exit 0",
                    rc == 0 and "cannot be measured" in out, f"rc={rc} out={out!r}")

            # E3 - a syntactically valid sha this lobby has never seen. A stamp from another repo
            # or from a commit that never landed is reportable, never fatal.
            root3 = tmp / "c"
            seed_lobby(root3, commits=1)
            stamp(root3, f"source_commit: {'0' * 40}\n")
            rc, out = run(root3)
            c.check("E3 · foreign sha reports, exit 0",
                    rc == 0 and "not in this lobby" in out, f"rc={rc} out={out!r}")

            # E4 - not a git repository at all. The script must not raise.
            root4 = tmp / "d"
            (root4 / PUBLISHED_REL).mkdir(parents=True, exist_ok=True)
            stamp(root4, f"source_commit: {'a' * 40}\n")
            rc, out = run(root4)
            c.check("E4 · non-git tree does not raise, exit 0", rc == 0, f"rc={rc} out={out!r}")

    if c.block("F · the SessionStart hook ARMS it"):
        hook = SCRIPTS.parent / "hooks" / "session-start-context.sh"
        body = hook.read_text(encoding="utf-8") if hook.is_file() else ""
        # ⛔ THIS IS THE CASE THAT MATTERS MOST, and it is here because of a baked audit finding.
        # As first drafted the script's only caller was a row in `.claude/settings.json`, which is
        # SANDBOX-DENIED to every agent - so the file would have landed INERT and waited on an
        # operator action nobody was going to remember. A gate nobody armed is a file, not a
        # mechanism, and this house has the scar already. The hook is registered and agent-
        # writable, so arming is part of the diff, and this row is what keeps it armed.
        # ⛔ COMMENTS ARE STRIPPED BEFORE THE SEARCH, and this is not tidiness.
        # The block's own comment names `test_teaching_edition_staleness.py`, which CONTAINS
        # `teaching_edition_staleness.py` as a substring - so a search over the whole file is
        # satisfied by the comment explaining the guard and stays green with the arming line
        # deleted. That is comment-literals-invert-source-grep-tests, and it was live in this
        # very case until the mutation sweep aimed at it.
        code = "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("#"))

        c.check("F1 · session-start-context.sh exists", bool(body), str(hook))
        c.check("F2 · an EXECUTABLE line calls teaching_edition_staleness.py",
                "teaching_edition_staleness.py" in code,
                "the reporter is not armed by the hook - it would ship inert")
        c.check("F3 · the call cannot block the hook",
                "|| TE_OUT=\"\"" in code or "|| true" in code,
                "the hook must survive a failing reporter; it opens every session")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
