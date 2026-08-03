"""workflow_lint's encoding scanner must FIRE on real corruption and stay quiet on quoted
examples. Without this control a clean lint run is indistinguishable from a dead detector.

The third case is the one that caught us: `sudo-prune-context.md` documents the mojibake
pattern inside a code span, so a naive scan flags the file that says "don't do this".
"""
from __future__ import annotations

import sys

from _harness import Cases, TempDir

import wf_common as wf          # noqa: E402
import workflow_lint as lint    # noqa: E402

FIXTURES = {
    # prose mojibake: a real cp1252 round-trip of an em dash
    "prose-mojibake.md": "Rebuild the board â€” then stamp it.\n".encode("utf-8"),
    # bytes that are not valid UTF-8 at all
    "undecodable.md": b"valid text then a bad byte: \xff\xfe done\n",
    # the SAME digraph, but quoted as an example inside a code span
    "quoted-only.md": ("Normalize encoding (no `â€”` mojibake "
                       "— use a real em dash).\n").encode("utf-8"),
    # and inside a fenced block
    "fenced-only.md": ("Example:\n\n```\nbad: â€”\n```\n").encode("utf-8"),
}
EXPECTED = {
    "prose-mojibake.md": {"WARN"},
    "undecodable.md": {"ERROR"},
    "quoted-only.md": set(),
    "fenced-only.md": set(),
}


def main() -> int:
    c = Cases("encoding scanner control")
    with TempDir() as tmp:
        paths = []
        for name, data in FIXTURES.items():
            (tmp / name).write_bytes(data)
            paths.append((name, tmp / name))

        rep = wf.Report()
        lint.scan_encoding(paths, rep)

        got: dict[str, set[str]] = {n: set() for n in FIXTURES}
        for item in rep.items:
            for name in FIXTURES:
                if item["msg"].startswith(name):
                    got[name].add(item["sev"])

        for name, want in EXPECTED.items():
            c.check(name, got[name] == want,
                    f"expected {want or 'silence'}, got {got[name] or 'silence'}")

        # strip_code must not swallow the whole document
        kept = wf.strip_code("before `x` after")
        c.check("strip_code keeps prose", "before" in kept and "after" in kept, kept)
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
