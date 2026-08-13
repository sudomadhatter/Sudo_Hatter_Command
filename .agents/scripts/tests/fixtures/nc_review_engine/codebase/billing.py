"""Invoice billing — FIXTURE BASE STATE for the review-engine negative control (SCC-129).

This module is fixture DATA, not production code. Nothing imports it, nothing executes it, and
`run_all.py` never discovers it — that script globs `test_*.py` in the tests directory only, one
level, never recursively. It exists so the two diffs beside it have a real, committed base to
apply against, and so the engine's repo-access lenses have a real definition to open.

Amounts are plain floats rounded to two places throughout, by fixture convention. The subject
being measured here is review behaviour, not currency representation: a Decimal rewrite would add
noise to every hunk without changing anything this fixture exists to test.
"""
from __future__ import annotations

TAX_RATE = 0.08


def tax_for(subtotal: float) -> float:
    """The tax owed on `subtotal`."""
    return round(subtotal * TAX_RATE, 2)


def invoice_total(subtotal: float) -> float:
    """What the customer owes: the subtotal with tax INCLUDED."""
    return round(subtotal + tax_for(subtotal), 2)


def new_ledger() -> dict:
    """A fresh, empty payment ledger."""
    return {"paid": 0.0}
