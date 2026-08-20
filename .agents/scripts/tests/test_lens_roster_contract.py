"""step-01's lens-roster contract — one section, five scars, one invariant. (SCC-229/230/232)

Five sections accreted one ticket at a time all answered "which lenses actually ran, under
what constraint": lens_budget (SCC-147), review_runtime (SCC-177), cannot-launch
(SCC-173), the inline Blind-Hunter drop (SCC-203), skipped-by-mode. SCC-229 collapses
them into ONE contract built on the invariant that subsumes them. One mutation per scar
ticket pins that the consolidation lost nothing; the invariant may appear exactly once.
SCC-230's doc-truth guards and SCC-232's level checks ride the same file. RED-first.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
STEP01 = (ROOT / ".agents/skills/code-review-engine/steps/step-01-review.md").read_text(encoding="utf-8")
STEP04 = (ROOT / ".agents/skills/code-review-engine/steps/step-04-record.md").read_text(encoding="utf-8")


def main() -> int:
    c = Cases("lens_roster_contract")
    t = STEP01

    # ── the consolidation itself ──────────────────────────────────────────────
    c.check("ONE roster-contract section exists",
            len(re.findall(r"^## .*lens-roster contract", t, re.M | re.I)) == 1,
            str(re.findall(r"^## .*$", t, re.M)[:3]))
    inv = re.findall(r"ends the run in exactly one declared state", t)
    c.check("the invariant sentence is stated exactly once", len(inv) == 1, f"{len(inv)}x")
    for gone in (r"^## ⭐ `review_runtime`", r"^## When a lens cannot be launched",
                 r"^## Skipped-by-mode"):
        c.check(f"old standalone h2 gone: {gone[4:40]}",
                not re.search(gone, t, re.M), "still present as its own h2")

    # ── SCC-147: the budget axis, defined once, inside the contract ───────────
    buddefs = [m.start() for m in re.finditer(r"^### `lens_budget`", t, re.M)]
    contract_at = t.lower().find("lens-roster contract")
    c.check("SCC-147: lens_budget defined exactly once, inside the contract",
            contract_at >= 0 and len(buddefs) == 1 and buddefs[0] > contract_at,
            f"defs={len(buddefs)} contract@{contract_at}")
    c.check("SCC-147: the top-up clause still reaches only `standard`",
            "You may earn ONE top-up" in t and "Under `capped` you append nothing" in t,
            "top-up mechanics lost")
    c.check("SCC-147: review_mode and lens_budget still declared independent",
            "`lens_budget` is NOT `review_mode`" in t, "independence guard lost")

    # ── SCC-177: runtime declared by the caller + the measured expectations ───
    c.check("SCC-177: inline + `ok` is still a checked contradiction",
            "`inline` + a lens reported `ok` is a contradiction" in t, "guard lost")
    c.check("SCC-177: never re-attempt the fan-out after inline",
            "never re-attempt it after" in t, "re-fan-out ban lost")
    c.check("SCC-177: the measured runtime expectations are carried (slow = a lens, "
            "never the harness)",
            "0.19" in t and "35–65" in t and "22–44" in t, "scoring.md numbers absent")

    # ── SCC-173: launch failure is a recorded outcome ─────────────────────────
    c.check("SCC-173: the dead-lens ladder survives (retry → inline → record → floor)",
            "Retry it once" in t and "raises `severity_floor` to CONCERNS" in t,
            "ladder lost")
    c.check("SCC-173: recovered-inline never reads as a gap",
            "`recovered-inline`" in t and "cost time, not coverage" in t, "state lost")

    # ── SCC-203: the Blind Hunter is dropped, never faked ─────────────────────
    c.check("SCC-203: contamination drops the lens rather than faking it",
            "DROPPED" in t and "context contaminated" in t, "drop rule lost")
    c.check("SCC-203: the retired not-blind state cannot return",
            "retired" in t and "ok (not blind" in t, "retirement record lost")

    # ── skipped-by-mode ≠ dead ────────────────────────────────────────────────
    c.check("mode-skip is declared, uncounted, and never raises the floor",
            "lenses_na" in t and "never raises `severity_floor`" in t
            and "`4/4`, never `4/5`" in t, "distinction lost")

    # ── the return shape is unchanged (walkthrough_roster.py reads it) ────────
    c.check("step-04 still emits the lenses_run roster line",
            "lenses_run:" in STEP04, "roster line renamed or dropped")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
