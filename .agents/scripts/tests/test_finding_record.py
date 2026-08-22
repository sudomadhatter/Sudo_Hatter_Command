"""step-04's finding record carries lens attribution. (SCC-233)

The Blind Hunter question is genuinely open (SCC-129 clean arm: only lens to fire on a
clean diff, both findings demoted - but n=1, and cutting on n=1 is the unanchored move
the parent bans). This part makes it ANSWERABLE: every recorded finding names its
originating lens (the src the SCC-124 trial recorded by hand), dispositions keep
attribution for findings that DIE (without dead boxes reaching the builder), and the
summary emits per-lens disposition counts. After N runs the per-lens disposition rate is
computable from the record; N is deliberately unfixed (ruling 5). RED-first.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
STEP04 = (ROOT / ".agents/skills/code-review-engine/steps/step-04-record.md").read_text(encoding="utf-8")


def main() -> int:
    c = Cases("finding_record")
    t = STEP04

    # ⛔ The literal template lines, not a count: `t.count("src=") >= 2` was satisfied by
    # PROSE alone - executed mutant (SCC-225 review wave): all three box templates stripped
    # of ` src=<lens>`, count fell 5→2, every check stayed green. A builder copies the
    # template line, so the template line is what gets pinned.
    c.check("the Decision box template line carries src=<lens>",
            "- [ ] [Review][Decision] <title> — <detail> src=<lens>" in t,
            "template line lost its attribution")
    c.check("the Patch box template line carries src=<lens>",
            "- [ ] [Review][Patch] <title> [<file>:<line>] src=<lens>" in t,
            "template line lost its attribution")
    c.check("the Defer box template line carries src=<lens> before its blocker",
            "- [ ] [Review][Defer] <title> [<file>:<line>] src=<lens> — " in t,
            "template line lost its attribution")
    c.check("multi-lens attribution uses the trial's joined form",
            "blind+edge" in t, "multi-lens form absent")
    c.check("dismissed and relevance-killed keep their attribution in the summary",
            "per-lens" in t and "dismissed" in t, "dead findings lose their lens")
    c.check("dead boxes still never reach the builder",
            "builders must never see dead boxes" in t, "the existing rule was lost")
    # Same lesson for the summary: the machine line is pinned VERBATIM. Executed mutant:
    # the line rewritten to `per-lens: <lens>=<survived>` alone - prose supplied the other
    # two words and the loose regex matched, while the record lost 2 of 3 death counts.
    c.check("the dispositions template line is the full three-count form, verbatim",
            "dispositions:    per-lens: <lens>=<survived>/<dismissed>/<relevance-killed> · …"
            in t, "the machine line lost a death count")
    c.check("the summary emits per-lens disposition counts",
            "survived" in t and "relevance-killed" in t
            and re.search(r"per-lens:.*survived", t), "counts absent from the return")
    c.check("the disposition-rate question is answerable, N deliberately unfixed",
            "N is not fixed" in t, "the enabler's purpose is unstated")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
