#!/usr/bin/env python3
"""The Declared Change Set block - parse and diff. (SCC-226)

`artifacts-always-first.md` §plan contents has always required the plan to carry "every
file touched with links"; this module gives that requirement its ONE machine-readable
form and the parser consumers share, instead of each re-reading prose:

    ## Declared Change Set

    - EDIT `path/to/file.md` — why this file moves → A
    - NEW `path/new.py` — what it is → A, F
    - DELETE `path/dead.md` → C

One repo-relative path per bullet. Op marker NEW / EDIT / DELETE (an optional
parenthetical qualifier after the op - "EDIT (wholesale rewrite)" - is accepted and
ignored). The text after the arrow (→ or ->) maps the bullet to the acceptance row(s)
it serves. A bullet that fails the grammar is REPORTED in `incomplete`, never guessed
into the entries.

Consumers and their stakes:
- SCC-227 Scope Ledger: the created set = entries with op NEW.
- SCC-231 drift check: `diff(declared, changed)` - `undeclared` (edited, never
  declared; *important* per file) and `unimplemented` (declared, untouched;
  *suggestion* per file). An ABSENT block is a defined result (`present: False`),
  which the caller turns into its own important finding - absence must never read
  as "nothing declared, nothing drifted".

Stdlib only; runs as `python3` (Mac) / `python` (PC). CLI:
    declared_change_set.py parse <plan.md>
    declared_change_set.py diff  <plan.md> --changed <path> [<path> ...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^##\s+Declared Change Set\s*$", re.MULTILINE)
# planning dirs never count as drift - same carve-out as label_tasks' set math
PLANNING = ("_artifacts/", "_bmad/", "_bmad-output/", "_my_resources/")
BULLET = re.compile(
    r"^-\s*(?P<op>NEW|EDIT|DELETE)"          # the fixed three (SCC-226)
    r"(?:\s*\([^)]*\))?"                     # optional qualifier: EDIT (generated)
    r"\s+(?:`(?P<qp>[^`]+)`|(?P<bp>[^\s`]+))"  # ONE path, backticked or bare
    r"(?:\s+[—–-]+\s+(?P<why>[^→]*?))?"      # prose sep needs whitespace BOTH sides,
                                             # or an in-filename hyphen splits the path
    r"\s*(?:→|->)\s*(?P<row>.+?)\s*$")       # the acceptance-row mapping (required)


def parse(text: str) -> dict:
    """-> {present: bool, entries: [{path, op, row}], incomplete: [raw bullet, ...]}."""
    m = HEADING.search(text)
    if not m:
        return {"present": False, "entries": [], "incomplete": []}
    body = text[m.end():]
    nxt = re.search(r"^#{1,2}\s+\S", body, re.MULTILINE)   # section ends at the next h1/h2
    if nxt:
        body = body[: nxt.start()]
    entries, incomplete = [], []
    for raw in (ln.rstrip() for ln in body.splitlines()):
        if not raw.lstrip().startswith("- "):
            continue
        b = BULLET.match(raw.strip())
        if b:
            entries.append({"path": (b["qp"] or b["bp"] or "").strip(), "op": b["op"],
                            "row": b["row"].strip()})
        else:
            incomplete.append(raw.strip())
    return {"present": True, "entries": entries, "incomplete": incomplete}


def diff(declared: list[str], changed: list[str]) -> dict:
    """Two set differences, both sides normalised; planning dirs never drift."""
    def norm(paths: list[str]) -> set[str]:
        out = set()
        for p in paths:
            p = p.strip()
            while p.startswith("./"):     # a "./" PREFIX - lstrip("./") is a char set
                p = p[2:]                 # and would eat the dot of ".agents/"
            if p and not p.startswith(PLANNING):
                out.add(p)
        return out
    dec, chg = norm(declared), norm(changed)
    return {"undeclared": sorted(chg - dec), "unimplemented": sorted(dec - chg)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    p_parse = sub.add_parser("parse", help="parse a plan's block to JSON")
    p_parse.add_argument("plan")
    p_diff = sub.add_parser("diff", help="declared vs changed, both directions")
    p_diff.add_argument("plan")
    p_diff.add_argument("--changed", nargs="+", required=True,
                        help="changed paths (e.g. from git diff --name-only)")
    a = ap.parse_args()
    plan = Path(a.plan)
    if not plan.is_file():
        print(f"declared_change_set: no such plan: {plan}", file=sys.stderr)
        return 2
    r = parse(plan.read_text(encoding="utf-8"))
    if a.verb == "diff":
        r = {"present": r["present"],
             **diff([e["path"] for e in r["entries"]], list(a.changed))}
    print(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
