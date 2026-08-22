"""SCC-285 · the commands must quote the session directive VERBATIM.

⛔ THE DEFECT THIS EXISTS TO PREVENT.

Claude Code injects a standing directive into the system prompt. Its exact text is a constant
compiled into the binary (`dkm`, injected under feature name `tengu_heron_brook`):

    Do not call the AgentTool unless the user requested it

Five house commands rebutted it by quoting it as *"do not use subagents unless the user requested
it"* — a paraphrase that **does not name the tool**. An agent reads its real system prompt, reads a
command arguing against a sentence that is not in it, and takes the gap as an escape hatch. It did
exactly that on 2026-08-22:

    _artifacts/_main/2026-08-22_code-review-graph-swap/walkthrough.md:227
    review-runtime: inline (blocked: ... "Do not call the AgentTool unless the user requested it".
    ... and the directive names that tool specifically.)

The review ran INLINE — no independent lens — because the rebuttal missed by four words.

⛔ WHY A GREP GUARD AND NOT PROSE. The paraphrase reached five files because people write the
rebuttal from memory. Prose cannot stop that; a gate can. This file is the gate.

── THE TWO HALVES, AND WHY BOTH ARE REQUIRED ────────────────────────────────────────────────
A guard that only bans the wrong string is satisfied by DELETING the rebuttal entirely — which
removes the very sentence that makes the fan-out legal, a strictly worse outcome than the bug.
So:

  BAN     - no paraphrase variant appears anywhere under .agents/commands/
  REQUIRE - every command that rebuts the directive carries the VERBATIM string

Neither half alone is a check. Block D fails this file's own gate in both directions before it is
believed (`tests-must-gate-for-real.md` § Mutation Testing).

⛔ SOURCE OF TRUTH. `DIRECTIVE` below is the binary's constant, byte for byte. If Anthropic changes
the injected text, this file is what goes red first — that redness is correct, and the fix is to
re-read the constant from the binary, never to loosen the assertion:

    strings -a "$(readlink -f "$(command -v claude)")" | grep "unless the user requested it"
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

CMDS = Path(__file__).resolve().parents[2] / "commands"

DIRECTIVE = "Do not call the AgentTool unless the user requested it"
"""Verbatim, from the Claude Code binary. Not a summary, not a re-wording."""

REBUTTERS = [
    "cicd-code-review.md",
    "smh-code-review.md",
    "cicd-dev-story-tests.md",
    "cicd-quick-dev.md",
    "smh-quick-dev.md",
]
"""The commands that argue the directive is satisfied. Each MUST carry `DIRECTIVE` verbatim."""

PARAPHRASE = re.compile(r"subagents?\s+unless", re.I)
"""Every observed wrong form collapses to this: `use subagents unless`, `spawn subagents unless`.

⛔ Deliberately NOT a list of the three known variants. The defect is people re-wording from
memory, so the next variant is one nobody has written yet. This matches the SHAPE.
"""


def norm(text: str) -> str:
    """Whitespace-collapsed, so a quote wrapped across two lines still matches.

    ⛔ Load-bearing, not tidiness: 4 of the 8 original occurrences were line-wrapped mid-quote
    (`smh-code-review.md:171-172` splits after the word `do not`). A raw `in` check reads those
    files as clean and the guard is vacuous on exactly the sites it was written for.
    """
    return " ".join(text.split())


def body(name: str) -> str:
    p = CMDS / name
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def main() -> int:
    c = Cases("directive-quote: commands quote the session directive verbatim")

    if c.block("A · the inputs exist (anti-vacuity)"):
        # Every row below loops over files. A loop over a missing tree passes silently.
        c.check("A1 the commands directory resolves", CMDS.is_dir(), f"CMDS={CMDS}")
        files = sorted(CMDS.glob("*.md"))
        c.check("A2 there are commands to scan", len(files) >= 20, f"{len(files)} *.md found")
        missing = [n for n in REBUTTERS if not (CMDS / n).is_file()]
        c.check("A3 every pinned rebutter exists on disk", not missing, f"missing={missing}")

    if c.block("B · BAN - no paraphrase of the directive survives anywhere"):
        hits = []
        for p in sorted(CMDS.glob("*.md")):
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if PARAPHRASE.search(line):
                    hits.append(f"{p.name}:{n}")
        c.check("B1 zero paraphrase variants under .agents/commands/",
                not hits,
                "" if not hits else
                f"paraphrased at {hits} - quote the directive verbatim: {DIRECTIVE!r}")

    if c.block("C · REQUIRE - every rebutter carries the directive verbatim"):
        target = norm(DIRECTIVE)
        for name in REBUTTERS:
            c.check(f"C1 {name} quotes the directive verbatim",
                    target in norm(body(name)),
                    f"{name} rebuts the directive without quoting it - "
                    f"a ban-only guard is satisfied by deleting the rebuttal")

    if c.block("D · ⛔ COUNTER-EXAMPLES - a check never seen failing is not a check"):
        # Both halves, both directions, against synthetic text - never the real tree.
        c.check("D1 BAN fires on the exact string that shipped the bug",
                bool(PARAPHRASE.search('*"do not use subagents unless the user requested it"*')),
                "the regex misses the literal defect it was written for")
        c.check("D2 BAN fires on the OTHER shipped variant",
                bool(PARAPHRASE.search('*"do not spawn subagents unless the user asks"*')),
                "the regex is pinned to one wording")
        c.check("D3 BAN fires on the singular form",
                bool(PARAPHRASE.search("do not call a subagent unless asked")),
                "`subagents?` is not doing its job")
        c.check("D4 BAN does NOT fire on the correct directive",
                not PARAPHRASE.search(DIRECTIVE),
                "the guard cannot be satisfied - it reds on the very text it demands")
        c.check("D5 REQUIRE fails when the rebuttal is deleted",
                norm(DIRECTIVE) not in norm("a command with no rebuttal at all"),
                "the REQUIRE half passes over an empty body")
        c.check("D6 REQUIRE survives a mid-quote line wrap",
                norm(DIRECTIVE) in norm("reading *\"Do not call the\nAgentTool unless the user\nrequested it\"* is satisfied"),
                "norm() is not collapsing wraps - 4 of the 8 real sites are wrapped")
        c.check("D7 REQUIRE rejects a near-miss paraphrase",
                norm(DIRECTIVE) not in norm('*"Do not call the Agent tool unless the user requested it"*'),
                "REQUIRE accepts `Agent tool` for `AgentTool` - the check is not verbatim")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
