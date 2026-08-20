"""risk_seam.py — the risk-classification seam the self-audit calls. (SCC-228)

SCC-223 (command centre) and SCC-224 (product) are the real classifiers and neither
exists yet; the audit lands FIRST behind this seam. What these cases pin is the seam's
one load-bearing promise: **the classifier INFORMS the Parity+Blast lens, it never
gates the audit** — so when a real classifier replaces the placeholder, the audit's
meaning cannot silently change. Written RED first. Stdlib only, no pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import risk_seam as rs  # noqa: E402


def main() -> int:
    c = Cases("risk_seam")

    # ── the placeholder satisfies the fixed shape ─────────────────────────────
    r = rs.classify([".agents/commands/smh-self-audit.md", ".agents/scripts/x.py"])
    c.check("placeholder returns the fixed shape",
            r.get("status") == "unclassified" and r.get("tiers") == {}, str(r))
    c.check("empty input is the same defined shape, not an error",
            rs.classify([]) == {"status": "unclassified", "tiers": {}},
            str(rs.classify([])))

    # ── identical audit semantics, placeholder vs populated ───────────────────
    # gates_audit IS the seam's semantics: False for every possible return. A real
    # classifier that wants to gate must change this function - and this test.
    populated = {"status": "classified",
                 "tiers": {".agents/scripts/x.py": {"risk": "P0", "why": "gate script"}}}
    c.check("a placeholder return never gates the audit",
            rs.gates_audit(r) is False, str(rs.gates_audit(r)))
    c.check("a POPULATED classifier return never gates the audit either",
            rs.gates_audit(populated) is False, str(rs.gates_audit(populated)))
    c.check("even a malformed return cannot gate the audit",
            rs.gates_audit({"status": "P0-EVERYTHING-ON-FIRE"}) is False,
            str(rs.gates_audit({"status": "P0-EVERYTHING-ON-FIRE"})))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
