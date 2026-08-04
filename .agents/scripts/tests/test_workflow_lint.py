"""workflow_lint's checks must FIRE on real defects and stay quiet on look-alikes. Without
these controls a clean lint run is indistinguishable from a dead detector.

The encoding third case is the one that caught us: `sudo-prune-context.md` documents the
mojibake pattern inside a code span, so a naive scan flags the file that says "don't do
this". The budget cases guard the opposite failure - a check so loud (115 warnings about
history nobody will touch) that the one actionable line is never read.
"""
from __future__ import annotations

import sys
from pathlib import Path

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

        # ── F7: artifact budgets, scoped to work that is still moving ─────────
        proj = tmp / "proj"
        (proj / wf.BOARD_REL).parent.mkdir(parents=True)
        (proj / wf.BOARD_REL).write_text(
            "development_status:\n  9-1-live: review\n  9-2-closed: done\n",
            encoding="utf-8")
        for slug, size in (("story-9-1-live", 12_000), ("story-9-2-closed", 40_000)):
            d = proj / "_artifacts" / "epic_9" / slug
            d.mkdir(parents=True)
            (d / "walkthrough.md").write_text("x" * size, encoding="utf-8")
        main_d = proj / "_artifacts" / "_main" / "some-initiative"
        main_d.mkdir(parents=True)
        (main_d / "implementation_plan.md").write_text("y" * 30_000, encoding="utf-8")

        rep = wf.Report()
        lint.check_artifact_budgets(proj, rep)
        msgs = [(i["sev"], i["msg"]) for i in rep.items]
        c.check("F7 an IN-FLIGHT story over budget warns",
                any(s == "WARN" and "9-1-live" in m for s, m in msgs), str(msgs)[:120])
        c.check("F7 a CLOSED story is counted as history, not warned",
                any(s == "INFO" and "closed-story" in m for s, m in msgs)
                and not any(s == "WARN" and "9-2-closed" in m for s, m in msgs),
                str(msgs)[:120])
        c.check("F7 _main/ initiative plans are out of scope",
                not any("some-initiative" in m for _, m in msgs), str(msgs)[:120])
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
