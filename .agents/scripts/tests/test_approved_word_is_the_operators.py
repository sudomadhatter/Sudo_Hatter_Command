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
# The nouns: the five roles, the seat roster and its synonyms. Widened by SCC-441 review 2 (row
# 33, reproduced): the shipped grant re-worded as a seat by name, a synonym, a verb form or the
# passive was quiet. `never`/`not`/`cannot` immediately before the verb keeps a sentence quiet -
# the verb form admits only an optional modal between noun and verb, so a negation never matches.
NOUN = (r"(?:lead|agent|child|seat|runner|builder|orchestrator|cheshire cat|white rabbit|"
        r"march hare|queen of hearts|caterpillar|gnat)")
WHO = rf"{NOUN}['’]s"
VERB = r"(?:supplies|supply|writes|write|gives|give|provides|provide|types|type)"
GRANT = re.compile(
    rf"`approved`[^|\n]{{0,60}}\b{WHO}\b"
    rf"|\b{WHO}\s+(?:own\s+)?`approved`"
    rf"|\b{NOUN}\s+(?:(?:may|can|will)\s+)?{VERB}\s+`approved`"
    rf"|`approved`\s+is\s+(?:supplied|written|given|provided)\s+by\s+the\s+{NOUN}\b",
    re.IGNORECASE)

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
        # ⛔ THE SCAN FIRED ONLY ON A POSSESSIVE OF FIVE NOUNS (SCC-441 review 2 row 33,
        # reproduced): the same grant re-worded - a seat by name, a synonym for the agent, a verb
        # ("supplies", "may write"), the passive ("is supplied by") - was quiet. None of these is
        # prose ABOUT the rule; each is the grant itself. The negation ("never supplies") is the
        # one control that must stay quiet, and it is distinguishable by its own word.
        for sentence in (
                "both `approved` stops are the Cheshire Cat's",
                "the builder's `approved` is enough here",
                "the lead supplies `approved` at both stops",
                "the lead may write `approved` on the operator's behalf",
                "`approved` is supplied by the child"):
            c.check(f"SCC-441 review-2 row 33 · fires on the re-worded grant: {sentence!r}",
                    bool(grants(sentence)), "a seat name, a synonym, a verb form or the passive")
        c.check("SCC-441 review-2 row 33 · CONTROL: the negation stays quiet: "
                "'the agent never supplies `approved`'",
                not grants("the agent never supplies `approved`"),
                "never/not/cannot before the verb is the rule stated, not a grant")
        for sentence in ("the child cannot supply `approved`",
                         "the runner does not write `approved`"):
            c.check(f"SCC-441 review-2 row 33 · CONTROL: negated verb form stays quiet: {sentence!r}",
                    not grants(sentence), "not / cannot immediately before the verb")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
