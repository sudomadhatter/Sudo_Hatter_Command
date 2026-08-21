#!/usr/bin/env python3
"""The Declared Change Set block - parse and diff. (SCC-226)

`artifacts-always-first.md` §2 (Create the artifact folder + plan) has always required
the plan to carry "every file touched with links"; this module gives that requirement
its ONE machine-readable form and the parser consumers share, instead of each
re-reading prose:

    ## Declared Change Set

    - EDIT `path/to/file.md` — why this file moves → A
    - NEW `path/new.py` — what it is → A, F
    - DELETE `path/dead.md` → C

One repo-relative path per bullet. Op marker NEW / EDIT / DELETE (an optional
parenthetical qualifier after the op - "EDIT (wholesale rewrite)" - is accepted and
ignored). The LAST arrow (→ or ->) on the line is the row separator - prose before it
may itself contain arrows ("rename foo → bar") without corrupting the mapping. The
text after that arrow maps the bullet to the acceptance row(s) it serves. A line that
ATTEMPTS a bullet (any list marker, or an op word first) but fails the grammar is
REPORTED in `incomplete`, never guessed into the entries and never silently skipped -
`* NEW ...` must not read as a clean block. Fenced example bullets are stripped before
the scan (the SCC-154 scar: walkthrough_roster paid for that rule with a live miss).
A second `## Declared Change Set` heading is reported in `incomplete`, not silently
discarded - amendments belong INSIDE the one block (an h3 inside it does not end it).

Consumers and their stakes:
- SCC-227 Scope Ledger: the created set = entries with op NEW.
- SCC-231 drift check: `diff(declared, changed)` - `undeclared` (edited, never
  declared; *important* per file) and `unimplemented` (declared, untouched;
  *suggestion* per file). An ABSENT block is a defined result (`present: False`),
  which the caller turns into its own important finding - absence must never read
  as "nothing declared, nothing drifted". An absent plan FILE is a loud exit-2
  error, not present:false - a wrong path is a broken invocation, not a state.
  The diff verb carries `incomplete` through: grammar-rejected bullets must stay
  visible at review time, or every rejection presents as pure undeclared drift.

Stdlib only; runs as `python3` (Mac) / `python` (PC). CLI:
    declared_change_set.py parse <plan.md>
    declared_change_set.py diff  <plan.md> --changed [<path> ...]
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
# a line is a bullet ATTEMPT if it opens with a list marker (marker + space, per
# markdown - `*(italic prose)*` is not a list), a no-space `-OP` slip, or an op word;
# attempts that fail LEFT+arrow land in incomplete. Plain prose in the section is neither.
ATTEMPT = re.compile(r"^(?:[-*+]\s|-(?=NEW|EDIT|DELETE)|(?:NEW|EDIT|DELETE)\b)")
ARROW = re.compile(r"\s*(?:→|->)\s*")
LEFT = re.compile(
    r"^-\s*(?P<op>NEW|EDIT|DELETE)"          # the fixed three (SCC-226)
    r"(?:\s*\([^)]*\))?"                     # optional qualifier: EDIT (generated)
    r"\s+(?:`(?P<qp>[^`]+)`|(?P<bp>[^\s`]+))"  # ONE path, backticked or bare
    r"(?:\s+[—–-]+\s+(?P<why>.*))?\s*$")     # prose sep needs whitespace BOTH sides,
                                             # or an in-filename hyphen splits the path

FENCE = re.compile(r"^(\s{0,3})(`{3,}|~{3,})(.*)$")

# The left-half rejection, named once so the reason and the grammar cannot drift apart. It
# spells the op vocabulary out because "did not match `<OP> <path>`" is only useful to someone
# who already knows what the three ops are - which is exactly the reader who did not need it.
_LEFT_WHY = ("the left side is not `<OP> <path>` - the op marker is NEW, EDIT or DELETE, "
             "then ONE repo-relative path (backticked or bare)")


def strip_fenced(text: str) -> str:
    """Code fences removed before the scan - fenced EXAMPLE bullets are not entries.

    Same contract as walkthrough_roster.strip_fenced (SCC-154): fences close per
    CommonMark - same marker kind, at least the opening length. An unclosed fence
    drops everything after it, the safe direction (nothing fenced ever parses).
    """
    out, marker, mlen = [], None, 0
    for ln in text.splitlines():
        f = FENCE.match(ln)
        if marker is None:
            if f:
                marker, mlen = f.group(2)[0], len(f.group(2))
            else:
                out.append(ln)
        else:
            if f and f.group(2)[0] == marker and len(f.group(2)) >= mlen \
                    and not f.group(3).strip():
                marker = None
    return "\n".join(out)


def parse(text: str) -> dict:
    """-> {present: bool, entries: [{path, op, row}], incomplete: [raw bullet, ...]}."""
    text = strip_fenced(text)
    heads = list(HEADING.finditer(text))
    if not heads:
        return {"present": False, "entries": [], "incomplete": []}
    m = heads[0]
    body = text[m.end():]
    nxt = re.search(r"^#{1,2}\s+\S", body, re.MULTILINE)   # section ends at the next h1/h2
    if nxt:
        body = body[: nxt.start()]
    entries, incomplete = [], []
    if len(heads) > 1:
        incomplete.append("(a second '## Declared Change Set' heading exists - only "
                          "the first block is read; merge them, amendments go inside "
                          "the one block)")
    for raw in (ln.rstrip() for ln in body.splitlines()):
        s = raw.strip()
        if not s or not ATTEMPT.match(s):
            continue
        arrows = list(ARROW.finditer(s))
        if arrows:
            a = arrows[-1]                     # the LAST arrow is the row separator
            left, row = s[: a.start()], s[a.end():]
            b = LEFT.match(left.rstrip())
            if b and row.strip():
                entries.append({"path": (b["qp"] or b["bp"] or "").strip(),
                                "op": b["op"], "row": row.strip()})
                continue
            # ⛔ WHICH HALF FAILED (SCC-240). This used to be a bare `incomplete.append(s)`,
            # so the author was handed back the bullet they had already read and had to
            # re-derive this grammar from the module to find out what it wanted. Measured on
            # SCC-210: three rejected bullets, one grammar read, one repair.
            # ⛔ PRECEDENCE IS DECLARED, NOT INCIDENTAL. A bullet can fail BOTH halves at once
            # (`- foo → ` has no op AND no row text); the LEFT side wins, because the arrow is
            # already there and the op marker is the edit that has to happen first. Unstated,
            # this reads differently to every author who meets it.
            why = _LEFT_WHY if not b else "the row text after the last `→` is empty"
        else:
            why = ("no `→` row separator - every bullet ends `→ <the acceptance row it "
                   "serves>`")
        # The RAW BULLET STAYS, with the reason appended. Every consumer reads these rows as
        # strings - this file's own tests, the self-audit's Lens 1, and both review twins'
        # drift step, which grades `incomplete` *important* per bullet.
        incomplete.append(f"{s}  ← {why}")
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
    p_diff.add_argument("--changed", nargs="*", required=True,
                        help="changed paths (e.g. from git diff --name-only); an "
                             "empty re-taken diff is a legitimate boundary state")
    a = ap.parse_args()
    plan = Path(a.plan)
    if not plan.is_file():
        print(f"declared_change_set: no such plan: {plan}", file=sys.stderr)
        return 2
    r = parse(plan.read_text(encoding="utf-8"))
    if a.verb == "diff":
        # incomplete rides along: a grammar-rejected bullet at review time must stay
        # distinguishable from real drift, or rejections drown the undeclared list
        r = {"present": r["present"], "incomplete": r["incomplete"],
             **diff([e["path"] for e in r["entries"]], list(a.changed))}
    print(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
