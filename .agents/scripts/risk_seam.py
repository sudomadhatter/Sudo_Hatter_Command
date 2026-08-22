#!/usr/bin/env python3
"""The risk-classification seam - placeholder implementation. (SCC-228)

The rebuilt self-audit (SCC-227) wants risk classification as CONTEXT for its
Parity + Blast lens - where risk actually lives in the tree. The real classifiers are
SCC-223 (command centre) and SCC-224 (product); neither is a prerequisite, so the
audit lands first against this seam and they swap in later WITHOUT touching the audit
command file - the command names `risk_seam.classify`, never an implementation.

The seam's contract, and the one promise `test_risk_seam.py` pins:

- `classify(paths)` returns the fixed shape
      {"status": "unclassified" | "classified", "tiers": {<path>: <classifier data>}}
  The placeholder always returns `unclassified` with empty tiers - a DEFINED result,
  not an error, on any input including none.
- `gates_audit(result)` is **False for every possible return** - the classifier
  INFORMS the lens, it never gates the audit. A future classifier that wants a veto
  must change that function and its test in the same commit, which is exactly the
  visibility this seam exists to force. A code graph is NOT required here: the
  pure-Python path is the normal one (operator ruling, 2026-08-19).

Stdlib only; `python3` (Mac) / `python` (PC). CLI:  risk_seam.py classify <path> ...
"""
from __future__ import annotations

import json
import sys

FIXED_UNCLASSIFIED: dict = {"status": "unclassified", "tiers": {}}


def classify(paths: list[str]) -> dict:
    """Placeholder: every path set is `unclassified`. SCC-223/224 replace this body
    (or delegate from it) - the signature and return shape are the seam."""
    _ = paths  # read, deliberately unused: the placeholder classifies nothing
    return {"status": "unclassified", "tiers": {}}


def gates_audit(result: dict) -> bool:
    """The audit-semantics pin: NO classifier return gates the audit - it informs the
    Parity + Blast lens and nothing else. Deliberately ignores its input."""
    _ = result
    return False


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] != "classify":
        print("usage: risk_seam.py classify <path> [<path> ...]", file=sys.stderr)
        return 2
    print(json.dumps(classify(args[1:]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
