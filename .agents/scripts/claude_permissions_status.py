#!/usr/bin/env python3
"""Report the Claude Code allow rows that decide on THIS machine only (SCC-392).

Claude Code merges its permissions from several files. Two of them are machine-local and never
travel to the other machine:

    ~/.claude/settings.json                user scope, outside any repo
    <repo>/.claude/settings.local.json     project scope, gitignored

and one is tracked in git, rendered from the single permission source
(``.agents/permissions/families.json`` -> ``permission_render.py``):

    <repo>/.claude/settings.json

A rule the operator grants from a terminal chat lands in one of the first two, so it takes effect
here and nowhere else - the other machine keeps asking for the same command. This script answers
the one question ``/smh-llm-approvals`` must ask before it can route such a rule into the source:
WHICH allow rows exist only on this machine? It reads, it prints, and it stops.

Usage (python3 on the Mac, python on the PC):
    python3 .agents/scripts/claude_permissions_status.py

Stdlib only. READ-ONLY - it writes nothing, anywhere, and it exits 0 whether or not it finds
machine-local rows, because finding them is the normal result rather than a fault. Exit 2 means
it could not read the tracked list at all.

Two deliberate absences, both load-bearing:

* There is NO ``--apply``, and there must never be one. Claude reads the tracked file directly,
  so a rendered row is in force the moment the file is saved: there is no store to push into and
  nothing that can be replaced or lost. That is what makes Claude's path different from
  Antigravity's (``antigravity_permissions_apply.py``), whose apply REPLACES both arrays.
* It reports ``allow`` only. ``/smh-llm-approvals`` never reads or writes any deny list, and a
  report that surfaced deny rows would invite exactly the edit that law forbids.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDERED = REPO_ROOT / ".claude" / "settings.json"
USER = Path.home() / ".claude" / "settings.json"
PROJECT = REPO_ROOT / ".claude" / "settings.local.json"
KEY = "permissions"
NOTHING_LOCAL = "no machine-local rows - every allow row here is in the tracked list"


def _allow(path: Path) -> set[str]:
    """The ``permissions.allow`` rows in ``path``. A file that is not there is EMPTY, not an error.

    Absent is the ordinary state of ``settings.local.json`` on a machine that has never needed a
    project-scope override - the same way an empty Zoo store is ordinary in ``/smh-llm-approvals``,
    and it must not read like a failure.
    """
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.get(KEY, {}).get("allow", []))


def local_only(rendered: Path = RENDERED, user: Path = USER,
               project: Path = PROJECT) -> dict[Path, list[str]]:
    """Per machine-local file, the sorted allow rows the tracked list does not carry."""
    tracked = _allow(rendered)
    return {p: sorted(_allow(p) - tracked) for p in (user, project)}


def status(rendered: Path = RENDERED, user: Path = USER, project: Path = PROJECT) -> str:
    """One line: NOTHING_LOCAL, or how many rows decide here and nowhere else."""
    if not rendered.exists():
        return f"no tracked list at {rendered}"
    found = local_only(rendered, user, project)
    total = sum(len(rows) for rows in found.values())
    if not total:
        return NOTHING_LOCAL
    counts = " ".join(f"{p.name}={len(rows)}" for p, rows in found.items() if rows)
    return f"MACHINE-LOCAL allow rows: {total} ({counts}) - they decide on this machine only"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rendered", type=Path, default=RENDERED, help="override the tracked list (tests)")
    p.add_argument("--user", type=Path, default=USER, help="override the user-scope file (tests)")
    p.add_argument("--project", type=Path, default=PROJECT, help="override the project-scope file (tests)")
    a = p.parse_args(argv)

    absent = "   (absent - counts as empty)"
    print(f"tracked : {a.rendered}")
    print(f"user    : {a.user}{'' if a.user.exists() else absent}")
    print(f"project : {a.project}{'' if a.project.exists() else absent}")
    if not a.rendered.exists():
        print(f"ERROR: no tracked list at {a.rendered} - run permission_render.py first")
        return 2
    print(f"status  : {status(a.rendered, a.user, a.project)}")
    for path, rows in local_only(a.rendered, a.user, a.project).items():
        if rows:
            print(f"\n{path} - {len(rows)} row(s) the tracked list does not carry:")
            for row in rows:
                print(f"  {row}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
