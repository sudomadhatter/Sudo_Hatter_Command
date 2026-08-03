"""closeout_preflight's verdict reader: lenient about markdown, strict about conclusions.

A missed verdict is the worst failure here — it reads as "the review never ran" and blocks a
story that legitimately passed. The bold case is not hypothetical: 21.8b's own walkthrough
was written `**Verdict: PASS**`, which a bare `^Verdict:` anchor does not match.
"""
from __future__ import annotations

import sys

from _harness import Cases

import closeout_preflight as cp   # noqa: E402

POSITIVE = [
    ("canonical",          "Verdict: PASS @ 64098847",           "PASS", "64098847"),
    ("bold (21.8b's own)", "**Verdict: PASS** - detail in ...",  "PASS", None),
    ("bold value",         "Verdict: **CONCERNS** @ abc1234",    "CONCERNS", "abc1234"),
    ("heading",            "## Verdict: WAIVED @ deadbee",       "WAIVED", "deadbee"),
    ("list item",          "- Verdict: FAIL @ 1234567",          "FAIL", "1234567"),
    ("blockquote + code",  "> **Verdict:** PASS @ `9f8e7d6c`",   "PASS", "9f8e7d6c"),
    ("lowercase",          "verdict: pass @ 64098847",           "PASS", "64098847"),
]
NEGATIVE = [
    ("prose mention", "Full table in the verdict file."),
    ("no verdict", "## Code Review\n\nEverything looked fine.\n"),
    ("unknown word", "Verdict: MAYBE @ 64098847"),
]


def main() -> int:
    c = Cases("verdict reader")
    for name, line, want_v, want_sha in POSITIVE:
        m = cp._VERDICT_RE.search(line)
        got_v = m.group(1).upper() if m else None
        got_sha = m.group(2) if m else None
        c.check(name, got_v == want_v and got_sha == want_sha,
                f"verdict={got_v} sha={got_sha}")
    for name, text in NEGATIVE:
        m = cp._VERDICT_RE.search(text)
        c.check(f"negative/{name}", m is None, f"matched={m.group(0) if m else None}")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
