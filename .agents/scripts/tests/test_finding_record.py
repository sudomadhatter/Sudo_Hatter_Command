"""step-04's finding record carries lens attribution. (SCC-233, re-pinned by SCC-447)

Every recorded finding names its originating lens (the `src` the SCC-124 trial recorded by
hand), the per-lens counts keep attribution for findings that DIE (without dead boxes reaching
the builder), and the summary emits those counts so a lens's hit rate is computable from the
record rather than argued.

⛔ WHAT SCC-447 CHANGED HERE, and why the file did not shrink. The vocabulary moved — the
`Decision` and `Patch` boxes became `Fix` and `Escalate`, each carrying the `repro <id>` its
receipt is keyed on, and the death counts became `reproduced`/`dropped`/`recorded`. The reason
for the counts inverted, which is the part worth reading: they existed to make the open Blind
Hunter question ANSWERABLE after N runs. SCC-447 answered it by retiring that lens on the
measurement already on disk, so the counts now serve the rule that replaced the question —
**a lens is added back by measurement, never by argument** — and the record is where that
measurement has to come from. RED-first.
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
    c.check("the Fix box template line carries src=<lens> and its repro id",
            "- [ ] [Review][Fix] <title> [<file>:<line>] src=<lens> · repro <id>" in t,
            "template line lost its attribution or its receipt key")
    c.check("the Escalate box template line carries src=<lens>, its repro id and a recommendation",
            "- [ ] [Review][Escalate] <title> [<file>:<line>] src=<lens> · repro <id> · "
            "recommend: <one line>" in t,
            "template line lost its attribution, its receipt key or its recommendation")
    c.check("the Defer box template line carries src=<lens> and repro before its blocker",
            "- [ ] [Review][Defer] <title> [<file>:<line>] src=<lens> · repro <id> — " in t,
            "template line lost its attribution")
    c.check("multi-lens attribution uses the trial's joined form",
            "edge+test-adequacy" in t, "multi-lens form absent")
    c.check("dropped findings keep their attribution in the summary",
            "per-lens" in t and "dropped" in t, "dead findings lose their lens")
    c.check("dead boxes still never reach the builder",
            "builders must never see dead boxes" in t, "the existing rule was lost")
    # Same lesson for the summary: the machine line is pinned VERBATIM. Executed mutant:
    # the line rewritten to `per-lens: <lens>=<survived>` alone - prose supplied the other
    # two words and the loose regex matched, while the record lost 2 of 3 death counts.
    c.check("the dispositions template line is the full three-count form, verbatim",
            "dispositions:    per-lens: <lens>=<reproduced>/<dropped>/<recorded> · …"
            in t, "the machine line lost a count")
    c.check("the summary emits per-lens disposition counts",
            "reproduced" in t and "dropped" in t
            and re.search(r"per-lens:.*reproduced", t), "counts absent from the return")
    # ⛔ The PURPOSE of the counts, pinned positively. Without this sentence the three counts
    # read as bookkeeping, and the first agent under context pressure drops them as noise.
    # They are the only evidence a retired lens could ever come back on.
    c.check("the counts are stated as the calibration signal a lens returns on",
            "by measurement rather than by argument" in t,
            "the enabler's purpose is unstated — the counts read as bookkeeping")
    # ⛔ ANTI-VACUITY. Every check above is a substring test over one file; an empty or
    # missing step-04 would satisfy none of them by failing, but a TRUNCATED one could pass
    # the negative-shaped checks. Assert the body exists before trusting any of it.
    c.check("step-04 has a body to check", len(t) > 2000,
            f"step-04-record.md is {len(t)} chars — too short to carry the record contract")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
