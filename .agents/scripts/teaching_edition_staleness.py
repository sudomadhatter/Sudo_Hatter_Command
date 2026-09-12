#!/usr/bin/env python3
"""Report how far the PUBLISHED teaching edition has drifted behind `main`.

`Projects/sudo-command-center` is a sanitized export of this lobby, not a hand-maintained repo, and
team members keep their command centre current by pulling it. Before SCC-456 the export recorded
nothing about its source, so the copy the team pulled sat eight days and ~400 commits stale with no
signal anywhere that it had: staleness was not merely unnoticed, it was UNMEASURABLE. The exporter
now writes `.teaching-edition-source`, and this reads it.

⛔ THIS REPORTS. IT NEVER BLOCKS, AND IT ALWAYS EXITS 0.
A gate that fired on every lobby lane the moment `main` moved would be switched off within a day,
and a muted gate is the same as no gate. Same contract as the three staleness reporters already
running at SessionStart (`check-repo-map-drift.ps1`, `check_maps.py --depth3-only`,
`record_map_changes.py --nag`): never blocks, fails open, silent when clean.

THE BUDGET IS IN DAYS, NOT COMMITS, AND THAT IS A DELIBERATE DEPARTURE FROM THE PLAN'S WORDING.
Measured on this repo 2026-09-12: `main` takes ~50 commits a day (397 in the eight days the
published copy was stale; 1912 in thirty). A commit budget calibrated to "about a week" today means
"about two days" the moment the rate changes, so the threshold would drift without anyone touching
it. Days are the stable axis and they are also the axis the concern is actually stated on - the
edition does not need to match every commit, it needs to not rot for months. The commit count is
still REPORTED, because "700 commits behind" is the number that conveys the size of the gap.

Exit 0 always.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PUBLISHED_REL = "Projects/sudo-command-center"
STAMP_NAME = ".teaching-edition-source"
DEFAULT_BUDGET_DAYS = 14

SHA_RE = re.compile(r"^source_commit:\s*([0-9a-f]{40})\s*$", re.M)


def git(args: list[str], cwd: Path) -> str | None:
    """Return stripped stdout, or None on any failure. Never raises."""
    try:
        # `encoding=` is pinned, never left to `text=True` alone (SCC-335): the machine locale
        # decodes captured bytes on the Windows side and a mojibake sha is a silent wrong answer.
        out = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True,
            encoding="utf-8", errors="replace", timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="lobby root (default: cwd)")
    ap.add_argument(
        "--budget-days",
        type=int,
        default=DEFAULT_BUDGET_DAYS,
        help=f"days of drift tolerated before the line prints (default: {DEFAULT_BUDGET_DAYS})",
    )
    a = ap.parse_args()

    repo = Path(a.repo).resolve()
    published = repo / PUBLISHED_REL

    # Not every clone carries the submodule checked out, and a lobby without it is a normal state,
    # not a problem to announce. Silence.
    if not published.is_dir():
        return 0

    stamp = published / STAMP_NAME

    if not stamp.is_file():
        # The LOUD case, and the one that is true today. An unstamped published tree cannot be
        # measured at all, which is strictly worse than being measurably stale - so it says so
        # rather than staying quiet, and it names the door that fixes it.
        print(
            f"⚠️  The published teaching edition carries no {STAMP_NAME} — its age cannot be "
            f"measured. Run /smh-publish-teaching-edition to stamp and refresh it."
        )
        return 0

    try:
        text = stamp.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0

    m = SHA_RE.search(text)
    if not m:
        print(
            f"⚠️  {PUBLISHED_REL}/{STAMP_NAME} has no readable `source_commit:` line — "
            f"the published edition's age cannot be measured."
        )
        return 0

    sha = m.group(1)

    # The sha is read from the PUBLISHED tree but resolved against the LOBBY's history, because
    # that is the history it names. A sha the lobby does not have means the stamp came from a
    # different repo or from a commit that never landed - reportable, never fatal.
    if git(["cat-file", "-e", f"{sha}^{{commit}}"], repo) is None:
        print(
            f"⚠️  The published teaching edition names source commit {sha[:8]}, which is not in "
            f"this lobby's history — its age cannot be measured."
        )
        return 0

    # origin/main, never the local branch: a lane's own HEAD is not what the team pulls.
    base = "origin/main" if git(["rev-parse", "--verify", "origin/main"], repo) else "main"

    behind_raw = git(["rev-list", "--count", f"{sha}..{base}"], repo)
    days_raw = git(["show", "-s", "--format=%ct", sha], repo)
    now_raw = git(["log", "-1", "--format=%ct", base], repo)

    if behind_raw is None or days_raw is None or now_raw is None:
        return 0

    try:
        behind = int(behind_raw)
        days = max(0, (int(now_raw) - int(days_raw)) // 86400)
    except ValueError:
        return 0

    if days < a.budget_days:
        return 0

    print(
        f"⚠️  The published teaching edition is {days} days and {behind} commits behind "
        f"{base} (stamped {sha[:8]}). Your team pulls that copy — "
        f"run /smh-publish-teaching-edition to refresh it."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
