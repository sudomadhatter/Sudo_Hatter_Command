"""Every rule must carry its own provenance.

A rule with a stated `why:` can be reasoned about at its edges - you can tell whether an
unusual case is inside or outside what it was protecting against. A rule without one can
only be obeyed or ignored. (Origin: 2026-08-04, after the artifact byte budget could not be
evaluated because nothing recorded where it came from; it turned out to be one day old and
had ridden in on a commit about something else.)

This is a RATCHET, not a big-bang backfill. `WITHOUT_WHY` lists the rules whose rationale
nobody ever wrote down - inventing one for them would be worse than the gap, because a
confident wrong `why:` launders a guess into a decision. So they are grandfathered, and:

  - a NEW rule with no `why:`        -> FAIL (the ratchet; provenance is required going forward)
  - a grandfathered rule gains `why:` -> FAIL, telling you to drop it from the list (no backsliding)
  - a grandfathered rule disappears   -> FAIL, so the list cannot rot

Fill one in whenever you touch one of them, then remove its name here.

    python .agents/scripts/tests/test_rule_provenance.py
"""
from __future__ import annotations

import re
import sys

from _harness import SCRIPTS, Cases

RULES = SCRIPTS.parent / "rules"

# Not a rule - it is the router for the folder.
SKIP = {"INDEX"}

# Grandfathered: rationale not stated anywhere in the rule as of 2026-08-04.
# Shrink this list; never grow it.
WITHOUT_WHY = {
    "000-PLAN-FIRST-GATE",
    "bmad_code_review_sudo_fix",
    "code-standards",
    "constitution",
    "dependency-awareness",
    "git-policy",
    "karpathy-guidelines",
    "lobby-search",
    "mermaid-diagram-preferences",
    "operator-profile",
    "powershell-encoding-safety",
    "sudo-target-resolution",
}

FRONTMATTER = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def frontmatter(text: str) -> str | None:
    m = FRONTMATTER.match(text)
    return m.group(1) if m else None


def field(block: str, key: str) -> str | None:
    m = re.search(rf"^{key}:\s*(.+?)\s*$", block, re.M)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def main() -> int:
    c = Cases("rule provenance")

    files = {p.stem: p for p in sorted(RULES.glob("*.md")) if p.stem not in SKIP}
    c.check("rules found", bool(files), f"{len(files)} rule files")

    missing_fm, missing_since, bad_date = [], [], []
    has_why, no_why = set(), set()

    for stem, path in files.items():
        block = frontmatter(path.read_text(encoding="utf-8"))
        if block is None:
            missing_fm.append(stem)
            continue

        since = field(block, "since")
        if not since:
            missing_since.append(stem)
        elif not ISO_DATE.match(since):
            bad_date.append(f"{stem}={since}")

        (has_why if field(block, "why") else no_why).add(stem)

    c.check("every rule has frontmatter", not missing_fm, ", ".join(missing_fm))
    c.check("every rule has since:", not missing_since, ", ".join(sorted(missing_since)))
    c.check("since: is an ISO date", not bad_date, ", ".join(sorted(bad_date)))

    # The ratchet: anything newly missing a why: that was not grandfathered.
    new_without_why = sorted(no_why - WITHOUT_WHY)
    c.check(
        "no NEW rule without why:",
        not new_without_why,
        "add a why: to " + ", ".join(new_without_why) if new_without_why else "",
    )

    # No backsliding: a grandfathered rule that gained a why: must leave the list.
    now_filled = sorted(WITHOUT_WHY & has_why)
    c.check(
        "WITHOUT_WHY has no filled-in rules",
        not now_filled,
        "remove from WITHOUT_WHY: " + ", ".join(now_filled) if now_filled else "",
    )

    # No rot: a grandfathered name that no longer exists must leave the list.
    stale = sorted(WITHOUT_WHY - set(files))
    c.check(
        "WITHOUT_WHY has no stale names",
        not stale,
        "no such rule, remove: " + ", ".join(stale) if stale else "",
    )

    covered = len(has_why)
    print(f"-- provenance: {covered}/{len(files)} rules state a why: "
          f"({len(WITHOUT_WHY)} grandfathered) --")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
