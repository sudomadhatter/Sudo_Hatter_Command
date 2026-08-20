"""declared_change_set.py — the machine-readable form of the plan's touch-list. (SCC-226)

The block already existed as prose law (`artifacts-always-first.md` §plan contents: "every
file touched with links"); SCC-226 gives it ONE fixed shape and this parser. Consumers:
the self-audit's Scope Ledger (SCC-227) reads the created set, the code-review drift check
(SCC-231) diffs declared against the real diff. Absence is a DEFINED case for both - a
plan with no block must parse to present=False, never crash, because the vacuous-green
mutation (absent block silently reading as "nothing declared, nothing drifted") is exactly
what SCC-231's important-severity finding exists to catch.

Written RED first against the module. Stdlib only, no pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import declared_change_set as dcs  # noqa: E402


BLOCK = """---
IsArtifact: true
---

# Plan

## Declared Change Set

- EDIT `.agents/rules/artifacts-always-first.md` — name the block → A
- NEW `.agents/scripts/declared_change_set.py` — stdlib parser → A, F
- EDIT (wholesale rewrite) `.agents/commands/smh-self-audit.md` — three lenses → B
- DELETE `.agents/old/dead.md` → C
- EDIT `.agents/scripts/INDEX.md` — rows for the new scripts
- `.agents/scripts/risk_seam.py` — forgot the op marker → C

## Execution order
"""

NO_BLOCK = """# Plan

## Goal
Ship it.
"""


def main() -> int:
    c = Cases("declared_change_set")

    # ── the fixed shape parses ────────────────────────────────────────────────
    r = dcs.parse(BLOCK)
    c.check("block found", r["present"] is True, str(r["present"]))
    by = {e["path"]: e for e in r["entries"]}
    c.check("EDIT bullet: path + op + row",
            by.get(".agents/rules/artifacts-always-first.md", {}).get("op") == "EDIT"
            and by[".agents/rules/artifacts-always-first.md"]["row"] == "A",
            str(by.get(".agents/rules/artifacts-always-first.md")))
    c.check("NEW bullet carries a multi-row mapping verbatim",
            by.get(".agents/scripts/declared_change_set.py", {}).get("row") == "A, F",
            str(by.get(".agents/scripts/declared_change_set.py")))
    c.check("a parenthetical qualifier after the op is accepted",
            by.get(".agents/commands/smh-self-audit.md", {}).get("op") == "EDIT",
            str(by.get(".agents/commands/smh-self-audit.md")))
    c.check("DELETE with no prose still maps its row",
            by.get(".agents/old/dead.md", {}).get("op") == "DELETE"
            and by[".agents/old/dead.md"]["row"] == "C",
            str(by.get(".agents/old/dead.md")))

    # ── incomplete is REPORTED, never guessed ─────────────────────────────────
    c.check("a bullet missing its row mapping lands in incomplete",
            any("INDEX.md" in raw for raw in r["incomplete"]), str(r["incomplete"]))
    c.check("a bullet missing its op marker lands in incomplete",
            any("risk_seam" in raw for raw in r["incomplete"]), str(r["incomplete"]))
    c.check("incomplete bullets are NOT entries",
            ".agents/scripts/risk_seam.py" not in by and
            ".agents/scripts/INDEX.md" not in by, str(sorted(by)))

    # ── absence is a defined case ─────────────────────────────────────────────
    r2 = dcs.parse(NO_BLOCK)
    c.check("no block parses to present=False with empty sets",
            r2["present"] is False and r2["entries"] == [] and r2["incomplete"] == [],
            str(r2))

    # ── the two-sided diff (SCC-231's left-hand side) ─────────────────────────
    d = dcs.diff([e["path"] for e in r["entries"]],
                 [".agents/rules/artifacts-always-first.md",
                  ".agents/scripts/declared_change_set.py",
                  ".agents/commands/cicd-quick-dev.md"])
    c.check("edited-but-never-declared is drift.undeclared",
            d["undeclared"] == [".agents/commands/cicd-quick-dev.md"], str(d))
    c.check("declared-but-untouched is drift.unimplemented",
            sorted(d["unimplemented"]) == [".agents/commands/smh-self-audit.md",
                                           ".agents/old/dead.md"], str(d))
    c.check("planning dirs never count as drift",
            dcs.diff([], ["_artifacts/_main/x/implementation_plan.md",
                          "_bmad-output/y.md"])["undeclared"] == [],
            str(dcs.diff([], ["_artifacts/_main/x/implementation_plan.md"])))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
