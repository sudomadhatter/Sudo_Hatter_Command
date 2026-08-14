"""Parsing helpers — FIXTURE BASE STATE for the review-engine negative control (SCC-129).

⛔ `parse` takes exactly ONE argument, and that is load-bearing. `bad.diff` calls it as
`helpers.parse(raw, strict=True)` — a keyword argument that does not exist here, so the call
cannot bind. Catching that is `NC_LITERAL`, the seeded defect for the Literal-Correctness Hunter,
and it is catchable ONLY by a lens that opens this file: the diff itself looks perfectly
reasonable.

**Adding a `strict` parameter here would silently disarm that defect** while every mechanical
check stayed green — the marker would still be in `bad.diff`, and the call would simply start
working. If you came here to "fix" this signature, the thing you are fixing is the test.
"""
from __future__ import annotations


def parse(text: str) -> list[str]:
    """Split a line-item blob on commas, trimmed, dropping empties."""
    return [part.strip() for part in text.split(",") if part.strip()]
