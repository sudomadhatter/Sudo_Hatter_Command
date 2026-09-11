"""The word `approved` belongs to the operator, and no door, rule or SOP may hand it to an agent.

⛔ THE LEAK THIS FILE EXISTS TO HOLD (SCC-441 review row 8). `/cicd-autopilot-claude` grew a
parenthetical — *"both `approved` stops are the lead's"* — and the autopilot SOP said the same
in its table. The quick lane then writes the machine-read record line `walkthrough approved by
the operator @ <sha>`, which `closeout_preflight._QUICK_LANE_RE` accepts as evidence, so an agent
that took that sentence at its word could supply the operator's approval and file a record naming
him. `constitution.md` §Hard Stops and `000-PLAN-FIRST-GATE` reserve the word to Mr. Hatter; this
scan keeps every law surface saying so.

The scan is a LINE-local pattern: `` `approved` `` followed, within the same table cell or
sentence, by a possessive naming a non-operator (`the lead's`, `the agent's`, `the child's`,
`the seat's`, `the runner's`), and the reverse order. It is deliberately narrow — a wide net
fires on prose ABOUT the rule ("the agent never supplies `approved`") and trains readers to
ignore it. Block B proves it fires on the two lines that shipped.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases

ROOT = SCRIPTS.parents[1]
SURFACES = (
    ROOT / ".agents" / "commands",
    ROOT / ".agents" / "rules",
    ROOT / "docs" / "_scc_sops_prds",
)
WHO = r"(?:lead|agent|child|seat|runner)['’]s"
GRANT = re.compile(rf"`approved`[^|\n]{{0,60}}\b{WHO}\b|\b{WHO}\s+(?:own\s+)?`approved`")

# The two sentences that shipped, verbatim — the mutant control.
SHIPPED = (
    "| 1 | `/cicd-quick-dev <KEY>` | `cheshire-cat` | The build: scope check, plan, RED, GREEN, "
    "walkthrough (both `approved` stops are the lead's) |",
    "the two `approved` stops (plan, walkthrough) are the lead's; ⛔ there is no verdict here to read |",
)


def grants(text: str) -> list[tuple[int, str]]:
    """-> [(line number, line)] for every line that hands `approved` to a non-operator."""
    return [(n, ln.strip()) for n, ln in enumerate(text.splitlines(), 1) if GRANT.search(ln)]


def main() -> int:
    c = Cases("`approved` is the operator's word (SCC-441 review row 8)")

    if c.block("A · no door, rule or SOP grants `approved` to an agent"):
        files = [p for d in SURFACES for p in sorted(d.glob("*.md"))]
        c.check("the scan reads at least 60 law files (never vacuous)", len(files) >= 60,
                f"{len(files)} files")
        for p in files:
            hits = grants(p.read_text(encoding="utf-8", errors="replace"))
            c.check(f"{p.relative_to(ROOT)}: never hands `approved` to a lead, agent, child, "
                    f"seat or runner", not hits,
                    "; ".join(f"line {n}: {ln[:90]}" for n, ln in hits) or "clean")

    if c.block("B · the scan BITES (mutant controls)"):
        for shipped in SHIPPED:
            c.check(f"fires on the line that shipped: {shipped[:48]!r}…", bool(grants(shipped)),
                    "this is the exact text the review found")
        c.check("the reverse order fires too", bool(grants("the lead's own `approved` word")),
                "a rewording that swaps the halves is the same grant")
        c.check("prose ABOUT the rule does not fire",
                not grants("the agent never supplies `approved`; the word is the operator's"),
                "a wide net would train readers to ignore this scan")
        c.check("the record line itself does not fire",
                not grants("Review: none - quick lane; walkthrough approved by the operator @ abc1234"),
                "the writer names the operator, which is the point")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
