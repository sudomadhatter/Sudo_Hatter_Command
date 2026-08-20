"""The self-audit twins' structural contract. (SCC-227)

The 2026-08-18 failure was ARCHITECTURAL: 8 lenses each handed a findings[] schema
filled it (44 findings, ~half manufactured), and the back-loaded refutation pass died
unfinished - the run delivered nothing. The rebuild's load-bearing choices are all
FILE-CHECKABLE, so this file pins them as mutations: a fourth lens, a returning phase
skeleton, a dropped anchor rule, a lost canonical output - each fails here before it
ships. The AMENDMENT RULE is the contract's own change-control: a miss amends marker
lists / anchor definitions / ledger rules; it never adds a lens.

Written RED first against the pre-rewrite files. Stdlib only, no pytest.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SMH = (ROOT / ".agents/commands/smh-self-audit.md").read_text(encoding="utf-8")
CICD = (ROOT / ".agents/commands/cicd-self-audit.md").read_text(encoding="utf-8")

# The canonical contract sentences BOTH twins must carry verbatim - presence in each
# IS the twin-parity check for the law half (mechanics may diverge, stated as such).
CANON = {
    "anchor grammar": "anchor = `<path>:<line>` | `<path>` | `step <N>` — with the literal text read, quoted",
    "anchor rule": "No anchor, no finding — deleted, not demoted",
    "coverage beats findings": "Full coverage with zero findings is a complete, successful run",
    "corroboration": "Corroboration affects SORT ORDER only",
    "pre-mortem bound": "It CANNOT originate a finding",
    "ledger finding shape": "no acceptance row requires it",
}
# the anchor grammar, compiled: a finding row's anchor cell must carry one of the
# three forms plus a quoted literal somewhere in the row
ANCHOR_RE = re.compile(r"(\S+\.\w+:\d+|\S+/\S+|step \d+)")


def main() -> int:
    c = Cases("self_audit_contract")

    for name, t in (("smh", SMH), ("cicd", CICD)):
        lenses = re.findall(r"^## Lens [123]\b.*$", t, re.MULTILINE)
        c.check(f"{name}: exactly three lenses, no more ever",
                len(lenses) == 3, str(lenses))
        c.check(f"{name}: the amendment rule sits ABOVE the lens definitions",
                "AMENDMENT RULE" in t and "## Lens 1" in t
                and t.index("AMENDMENT RULE") < t.index("## Lens 1"),
                f"amend@{t.find('AMENDMENT RULE')} lens1@{t.find('## Lens 1')}")
        c.check(f"{name}: the phase skeleton is GONE (a returning ## Phase N is the "
                f"accretion vector)",
                not re.search(r"^## Phase \d", t, re.MULTILINE),
                str(re.findall(r"^## Phase \d.*$", t, re.MULTILINE)[:2]))
        c.check(f"{name}: canonical verdict line survives (plan-task 3.3 + quick-dev "
                f"box read it)",
                "Audit verdict: GO | NO-GO" in t, "verdict line missing")
        c.check(f"{name}: output is appended as ## Self-Audit (<date>)",
                "## Self-Audit (<date>)" in t, "section template missing")
        c.check(f"{name}: wired to the Declared Change Set parser",
                "declared_change_set.py" in t, "parser not named")
        c.check(f"{name}: risk context arrives via the seam, informs-only",
                "risk_seam" in t and "gates_audit" in t, "seam wiring missing")
        c.check(f"{name}: the coverage return block is the fixed schema",
                all(k in t for k in ("checks_run:", "read:", "verdict:")),
                "schema keys missing")
        c.check(f"{name}: levels are scope-named, never verdict-named",
                "LEDGER+BLAST" in t and "PROCEED / STOP" not in t,
                "level naming wrong")
        for label, sentence in CANON.items():
            c.check(f"{name}: canon [{label}]", sentence in t, sentence[:60])

    # ── the anchor grammar does real work on real rows ────────────────────────
    anchored = '| `.agents/scripts/foo.py:42` | "def classify(paths)" | breaks the seam | important |'
    unanchored = '| the plan feels over-scoped | — | agents may overbuild | important |'
    c.check("an anchored finding row satisfies the grammar",
            bool(ANCHOR_RE.search(anchored)), anchored)
    c.check("an unanchored finding row FAILS the grammar - deleted, not demoted",
            not ANCHOR_RE.search(unanchored), unanchored)

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
