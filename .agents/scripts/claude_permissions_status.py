#!/usr/bin/env python3
"""Report the Claude Code allow rows that decide on THIS machine only (SCC-392).

Claude Code merges its permissions from several files. Two of them are machine-local and never
travel to the other machine:

    ~/.claude/settings.json                user scope, outside any repo
    <repo>/.claude/settings.local.json     project scope, gitignored

and one is tracked in git, rendered from the single permission source
(``.agents/permissions/families.json`` -> ``permission_render.py``):

    <repo>/.claude/settings.json

Checked and deliberately NOT read: ``~/.claude.json`` carries a legacy per-project
``projects[*].allowedTools`` array. Measured 2026-09-04 on this machine, all three project entries
are EMPTY, so nothing is missed by leaving it out - recorded here so the next reader does not have
to re-derive it.

A rule the operator grants from a terminal chat lands in one of the first two, so it takes effect
here and nowhere else - the other machine keeps asking for the same command. This script answers
the one question ``/smh-llm-approvals`` must ask before it can route such a rule into the source:
WHICH allow rows exist only on this machine? It reads, it prints, and it stops.

Usage (python3 on the Mac, python on the PC):
    python3 .agents/scripts/claude_permissions_status.py

Stdlib only. READ-ONLY - it writes nothing, anywhere, and it exits 0 whether or not it finds
machine-local rows, because finding them is the normal result rather than a fault. Exit 2 means
it could not read one of the three files - the tracked list is missing, or a file that IS there
does not parse - and it always says WHICH.

Two deliberate absences, both load-bearing:

* There is NO ``--apply`` HERE. The tracked file is live the moment it is saved — inside THIS
  repo. The apply that does exist, ``claude_permissions_apply.py`` (SCC-415), writes USER scope
  (``~/.claude/settings.json``) so the rows also hold in project checkouts and worktrees, and it
  widens the sandbox — the one file an agent is barred from writing, so the operator runs it, the
  same way he runs the Antigravity and Zoo applies. This script stays the read-only half.
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

    An EMPTY file is also empty - it declares no rows, which is not damage.

    A file that IS there, holds something, and does not parse is a different thing, and so is one
    that cannot be read at all. Both name themselves and become exit 2. The door tells the operator
    that pruning a now-redundant row from ``~/.claude/settings.json`` is his own edit to make, so a
    stray comma there must say WHICH file - not die in a traceback part-way through the door's
    Step 1. Measured 2026-09-04: under the Bash sandbox this repo's ``.claude/settings.local.json``
    is a mount artifact that raises ``PermissionError``, and the door's own advertised command died
    on it.
    """
    if not path.exists():
        return set()
    try:
        raw = path.read_text(encoding="utf-8-sig")   # a Windows-authored file carries a BOM
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"{path} could not be read - {exc}") from exc
    if not raw.strip():
        return set()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not readable JSON - {exc}") from exc
    # `or {}` / `or []`, never a .get default: `{"permissions": null}` is legal JSON, the default
    # does not fire for an explicit null, and `.get` on None is an AttributeError (edge lens).
    return set((data.get(KEY) or {}).get("allow") or [])


def local_only(rendered: Path = RENDERED, user: Path = USER,
               project: Path = PROJECT) -> dict[Path, list[str]]:
    """Per machine-local file, the sorted allow rows the tracked list does not carry."""
    tracked = _allow(rendered)
    return {p: sorted(_allow(p) - tracked) for p in (user, project)}


def status(rendered: Path = RENDERED, user: Path = USER, project: Path = PROJECT) -> str:
    """One line: NOTHING_LOCAL, or how many rows decide here and nowhere else.

    The headline counts DISTINCT rules, not (file, row) pairs - Claude offers the same grant at
    user and project scope, so one rule granted twice is still one rule that does not travel. The
    per-file split is labelled by ROLE rather than by filename, because both files are called
    ``settings.json`` and the tracked one is too.
    """
    if not rendered.exists():
        return f"no tracked list at {rendered}"
    found = local_only(rendered, user, project)
    distinct = set().union(*found.values())
    if not distinct:
        return NOTHING_LOCAL
    counts = " ".join(f"{role}={len(found[path])}"
                      for role, path in (("user", user), ("project", project)) if found.get(path))
    return f"MACHINE-LOCAL allow rows: {len(distinct)} ({counts}) - they decide on this machine only"


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
    try:
        report = status(a.rendered, a.user, a.project)
        found = local_only(a.rendered, a.user, a.project)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"status  : {report}")
    for path, rows in found.items():
        if rows:
            print(f"\n{path} - {len(rows)} row(s) the tracked list does not carry:")
            for row in rows:
                print(f"  {row}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
