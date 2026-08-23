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

⛔ WHY A GATE AND NOT PROSE. The paraphrase reached five files because people write the rebuttal
from memory. Prose cannot stop that; a gate can. This file is the gate.

── THE TWO HALVES, AND WHY BOTH ARE REQUIRED ────────────────────────────────────────────────
A guard that only bans the wrong string is satisfied by DELETING the rebuttal entirely — which
removes the very sentence that makes the fan-out legal, a strictly worse outcome than the bug. So:

  BAN     - no quotation that PURPORTS to be this directive says anything but the verbatim text
  REQUIRE - every rebutter carries the verbatim quote AT ITS OPERATIVE SITE

Neither half alone is a check. Block D fails this file's own gate in both directions.

⛔ FOUR HOLES THE FIRST VERSION SHIPPED WITH, and how each is closed. All four were found by
ADVERSARIAL PROBING of this file — the operator's own probe script and two review lenses that
executed the guard's code against synthetic inputs. None was found by block D, because block D's
counter-examples were drawn from the shapes already handled. That is the lesson: counter-examples
derived from what you already fixed cannot find what you missed.

  H1 · BAN was LINE-SCOPED. It ran `PARAPHRASE.search(line)` over `.splitlines()`, so `\\s+` could
       never span a newline — while `norm()` was applied to REQUIRE only. A paraphrase wrapped
       between `subagents` and `unless` shipped GREEN. The docstring had even recorded that 4 of
       the 8 real sites were wrapped mid-quote; the fix was applied to one half and not the other.
       CLOSED: `unwrap()` runs on both halves, and block D2/D3 pin a wrapped paraphrase.

  H2 · BAN matched only ADJACENT tokens (`subagents?\\s+unless`). Every re-wording with a word
       between them — `subagents for the review unless` — or a different spelling — `sub-agents`,
       `Agent tools` — shipped GREEN, in a check whose docstring claimed it "matches the SHAPE".
       CLOSED: the ban no longer pattern-matches wording at all. See § How BAN works now.

  H3 · REQUIRE was not verbatim. `norm()` collapsed *every* whitespace run, so `AgentTool  unless`
       (two spaces) satisfied a case literally named "rejects a near-miss paraphrase".
       CLOSED: `unwrap()` collapses a LINE WRAP to exactly one space and nothing else, so internal
       spacing stays significant. D8 pins it.

  H4 · REQUIRE was OCCURRENCE-BLIND — `target in body`, anywhere. Three files carry the directive
       twice (the SCC-203 narration AND the rebuttal), so deleting the whole rebuttal paragraph —
       the exact deletion this half exists to prevent — left the guard green in 3 of 5 files.
       Reproduced by a lens: 17/17 passed with the rebuttal gone.
       CLOSED: REQUIRE anchors to the operative site. See § How REQUIRE works now.

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
REPO = Path(__file__).resolve().parents[3]
SOP = REPO / "docs" / "_scc_sops_prds" / "workflows_testing_SOP.md"
"""⛔ The SOP is scanned too, and that is not scope creep — it is the MEASURED second vector.
The paraphrase spread to five commands AND to the SOP by the same copy-from-memory route, and
the SOP is the document agents are routed to read for this law. A ban that covers one of the
two surfaces it demonstrably spread across is a ban with a hole in it."""

DIRECTIVE = "Do not call the AgentTool unless the user requested it"
"""Verbatim, from the Claude Code binary. Not a summary, not a re-wording."""

REBUTTERS = [
    "cicd-code-review.md",
    "smh-code-review.md",
    "cicd-dev-story-tests.md",
    "cicd-quick-dev.md",
    "smh-quick-dev.md",
]
"""The commands that argue the directive is satisfied. Each MUST carry `DIRECTIVE` at that claim."""

# ── How BAN works now ────────────────────────────────────────────────────────────────────────
# The old ban guessed at WORDING and lost twice: it missed re-phrasings (H2) and it over-fired on
# legitimate prose — a lens reproduced `never fan out to subagents unless the probe returned
# fan-out` reddening the suite with a remedy message that did not apply.
#
# ⭐ So the ban no longer looks at wording at all. It looks at the SHAPE OF THE CLAIM: a quoted
# string that purports to BE this directive. Any quotation naming a subagent/Agent-tool concept
# and carrying an `unless` clause is asserting "the directive says this" — and there is exactly
# one right answer. Unquoted prose is never a quotation, so it cannot be wrong, and the whole
# over-fire class disappears.
QUOTED = re.compile(r'"([^"\n]{10,240})"')
"""Every double-quoted span. The command files write the quote as *"…"*, inside the markdown."""

CLAIMS_TO_BE_DIRECTIVE = re.compile(r"sub[-\s]?agents?|agent[-\s]?tools?|agenttool", re.I)
"""A quotation mentioning this concept AND `unless` is claiming to be the directive."""


def unwrap(text: str) -> str:
    """Collapse a LINE WRAP to exactly one space. Nothing else.

    ⛔ This is not `" ".join(text.split())`, and the difference is the whole of hole H3. Collapsing
    every whitespace run makes `AgentTool  unless` compare equal to `AgentTool unless`, so a check
    calling itself verbatim silently accepts a near-miss. Collapsing only `\\s*\\n\\s*` tolerates
    the hard wrapping these files use — load-bearing, since 2 of the 8 original sites were wrapped
    mid-quote (`cicd-code-review.md:200-201` and `smh-code-review.md:171-172`, both breaking after
    `*"do not`) — while leaving internal spacing significant.
    """
    return re.sub(r"\s*\n\s*", " ", text)


def body(name: str) -> str:
    p = CMDS / name
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def bad_quotes(text: str) -> list[str]:
    """Quotations that claim to be the directive but are not it, verbatim.

    Runs on `unwrap`ped text so a quote broken across lines is still one quotation (H1).
    """
    out = []
    for m in QUOTED.finditer(unwrap(text)):
        span = m.group(1)
        if CLAIMS_TO_BE_DIRECTIVE.search(span) and re.search(r"\bunless\b", span, re.I):
            if DIRECTIVE not in span:
                out.append(span)
    return out


# ── How REQUIRE works now ────────────────────────────────────────────────────────────────────
# ⛔ Presence-anywhere was hole H4. Three of these files carry the directive TWICE — once in the
# SCC-203 narration, once in the operative rebuttal — so `target in body` stayed true after the
# rebuttal was deleted whole. The operative site is the one that says the directive is SATISFIED;
# that word is what makes the sentence a rebuttal rather than a mention, so that is what we anchor
# to. Delete the rebuttal and the anchor goes with it.
SATISFIED = re.compile(r"\bsatisfied\b", re.I)
ANCHOR_WINDOW = 400
"""Chars either side of `satisfied` the verbatim quote must fall within. The real sites sit
within ~120; the margin absorbs re-wrapping without letting a mention three paragraphs away count."""


def rebuts_verbatim(text: str) -> bool:
    flat = unwrap(text)
    for m in SATISFIED.finditer(flat):
        window = flat[max(0, m.start() - ANCHOR_WINDOW): m.end() + ANCHOR_WINDOW]
        if DIRECTIVE in window:
            return True
    return False


def looks_like_a_rebuttal(text: str) -> bool:
    """Does this file ARGUE the directive is satisfied - whatever it is named?

    ⛔ WHY THIS EXISTS. `REBUTTERS` is a hand-written list, and block C loops over it, so the
    REQUIRE half only ever reaches files somebody remembered to add. A sixth command that argues
    the directive is satisfied - and there will be one; five appeared in a single lane - is
    unguarded from the day it is written, and unguarded in exactly the silent way: block C stays
    green because it never looked. Block R derives the set from the tree and refuses any file the
    list has not caught up with.

    The shape, not the wording: a `satisfied` sitting near a claim about subagents that turns on
    an `unless`. That is what a rebuttal to this directive IS, and it is the same window
    `rebuts_verbatim` measures - so a file this returns True for is a file block C can judge.
    """
    flat = unwrap(text)
    for m in SATISFIED.finditer(flat):
        window = flat[max(0, m.start() - ANCHOR_WINDOW): m.end() + ANCHOR_WINDOW]
        if CLAIMS_TO_BE_DIRECTIVE.search(window) and re.search(r"\bunless\b", window, re.I):
            return True
    return False


def main() -> int:
    c = Cases("directive-quote: commands quote the session directive verbatim")


    if c.block("A · the inputs exist (anti-vacuity)"):
        # Every row below loops over files. A loop over a missing tree passes silently.
        c.check("A1 the commands directory resolves", CMDS.is_dir(),
                "" if CMDS.is_dir() else f"CMDS={CMDS} does not resolve")
        files = sorted(CMDS.glob("*.md"))
        c.check("A2 there are commands to scan", len(files) >= 20,
                "" if len(files) >= 20 else f"only {len(files)} *.md found - the glob found nothing")
        missing = [n for n in REBUTTERS if not (CMDS / n).is_file()]
        c.check("A3 every pinned rebutter exists on disk", not missing,
                "" if not missing else f"missing={missing}")
        # ⛔ A3 passes over an EMPTY list (`missing` is []), and block C is a loop over the same
        # list - so an emptied REBUTTERS guts the REQUIRE half in silence. `>=`, not `==`: the
        # anti-vacuity property is "populated", and pinning the count would red a correct change
        # that legitimately adds a sixth rebutter.
        c.check("A4 the rebutter list is populated (anti-vacuity for block C)",
                len(REBUTTERS) >= 5,
                "" if len(REBUTTERS) >= 5 else f"REBUTTERS has {len(REBUTTERS)} entries")

    if c.block("R · the rebutter set is DERIVED from the tree, not remembered"):
        derived = sorted(f.name for f in CMDS.glob("*.md")
                         if looks_like_a_rebuttal(f.read_text(encoding="utf-8", errors="replace")))
        c.check("R1 the derivation FINDS the rebuttals (anti-vacuity)",
                len(derived) >= 5,
                "" if len(derived) >= 5 else
                f"the shape matcher found only {derived} - if it finds nothing, R2 passes on air")
        unpinned = sorted(set(derived) - set(REBUTTERS))
        c.check("R2 every command that argues the directive is satisfied is PINNED",
                not unpinned,
                "" if not unpinned else
                f"{unpinned} argue(s) the directive is satisfied and are absent from REBUTTERS, so "
                f"block C never checks them - add them to the list")
        # ⛔ AND IT MUST BITE. A matcher that cannot see a NEW rebuttal is the hand-written list
        # again, wearing a loop. This is the sixth command, written the way the fifth was.
        sixth = ("Do not stop to ask. The standing directive *\"Do not call the AgentTool unless "
                 "the user requested it\"* is **satisfied here** - the operator typed the command.")
        c.check("R3 a NEW rebuttal is recognised by shape",
                looks_like_a_rebuttal(sixth),
                "the derivation cannot see a rebuttal it was not told about - R2 is decoration")
        c.check("R4 an ordinary command is NOT swept in",
                not looks_like_a_rebuttal(
                    "Run the gates. The acceptance list is satisfied when every row is green."),
                "the shape matcher fires on any `satisfied`; that would pin half the tree and "
                "block C would demand a quote from commands that make no such claim")

    if c.block("B · BAN - no quotation claims to be this directive and gets it wrong"):
        hits = []
        scanned = sorted(CMDS.glob("*.md")) + ([SOP] if SOP.is_file() else [])
        for p in scanned:
            for span in bad_quotes(p.read_text(encoding="utf-8", errors="replace")):
                hits.append(f"{p.name}: {span[:90]!r}")
        c.check("B0 the SOP is on the scan list (anti-vacuity)", SOP.is_file(),
                "" if SOP.is_file() else f"{SOP} is missing - the second re-seed vector is unscanned")
        c.check("B1 no misquotation of the directive in the commands or the SOP",
                not hits,
                "" if not hits else
                f"{len(hits)} misquotation(s); the only correct text is {DIRECTIVE!r} -> {hits}")

    if c.block("C · REQUIRE - every rebutter quotes it verbatim AT THE CLAIM"):
        for name in REBUTTERS:
            ok = rebuts_verbatim(body(name))
            c.check(f"C1 {name} quotes the directive verbatim where it claims 'satisfied'",
                    ok,
                    "" if ok else
                    f"{name} has no verbatim quote within {ANCHOR_WINDOW} chars of 'satisfied' - "
                    f"the rebuttal was deleted or re-worded")

    if c.block("D · ⛔ COUNTER-EXAMPLES - a check never seen failing is not a check"):
        # ⛔ Every row here is drawn from a hole this file SHIPPED WITH, not from a shape it
        # already handled. That is the correction: the first version's counter-examples all
        # confirmed the fix that was already in, so they could not see H1-H4.
        real = '*"do not use subagents unless the user requested it"* is satisfied here'
        _ok = bool(bad_quotes(real))
        c.check("D1 BAN fires on the exact string that shipped the bug", _ok,
                "" if _ok else "the guard misses the literal defect it was written for")

        # H1 - the wrap that shipped green. Reproduced by two independent lenses.
        wrapped = 'a session directive reading *"do not use subagents\nunless the user requested it"*'
        _ok = bool(bad_quotes(wrapped))
        c.check("D2 BAN fires on a paraphrase WRAPPED between `subagents` and `unless` (H1)", _ok,
                "" if _ok else "BAN is line-scoped again - a wrapped paraphrase ships green")

        # H2 - the re-wordings the old adjacency regex could not see.
        for label, text in [
            ("words in between", '*"do not use subagents for the review unless the user requested it"*'),
            ("hyphenated",       '*"do not use sub-agents unless the user requested it"*'),
            ("spaced",           '*"do not use sub agents unless the user requested it"*'),
            ("Agent tools",      '*"do not use Agent tools unless the user requested it"*'),
            ("other shipped",    '*"do not spawn subagents unless the user asks"*'),
        ]:
            _ok = bool(bad_quotes(text))
            c.check(f"D3 BAN fires on a re-worded paraphrase - {label} (H2)", _ok,
                    "" if _ok else f"the {label} spelling ships green")

        _ok = not bad_quotes(f'*"{DIRECTIVE}"* is satisfied here')
        c.check("D4 BAN does NOT fire on the correct directive", _ok,
                "" if _ok else "the guard cannot be satisfied - it reds on the very text it demands")

        # The over-fire a lens reproduced: legitimate UNQUOTED prose about the probe.
        _ok = not bad_quotes("never fan out to subagents unless the probe returned fan-out")
        c.check("D5 BAN does NOT fire on legitimate unquoted prose about subagents", _ok,
                "" if _ok else "BAN over-fires on ordinary prose and prints a remedy that does not apply")

        _ok = not bad_quotes('got read as *"this runtime is inline"* and a review ran')
        c.check("D6 BAN ignores a quotation that is not about this directive", _ok,
                "" if _ok else "BAN fires on unrelated quotations")

        # H4 - the deletion that shipped green in 3 of 5 files.
        two_sites = (f'the narration says *"{DIRECTIVE}"* got read as inline.\n\n'
                     f'⛔ Do not ask a second question. The standing directive '
                     f'*"{DIRECTIVE}"* is satisfied here.')
        _ok = rebuts_verbatim(two_sites)
        c.check("D7 REQUIRE passes when the rebuttal is present alongside a narration copy", _ok,
                "" if _ok else "REQUIRE cannot see a genuine rebuttal")
        # ⛔ This body MUST still contain the word `satisfied`, far from the quote. Without it the
        # case passes for the WRONG reason — the loop never runs — and the anchor is never
        # exercised. Caught by mutant M7 surviving: `window = flat` (presence-anywhere restored)
        # left this row green, which is the definition of a vacuous counter-example.
        narration_only = (f'the narration says *"{DIRECTIVE}"* got read as inline.\n\n'
                          + "filler prose that stands between the two. " * 20 +
                          "\n\nThe test-adequacy requirement is satisfied by the probe.")
        _ok = not rebuts_verbatim(narration_only)
        c.check("D8 REQUIRE FAILS when only the narration copy survives (H4)", _ok,
                "" if _ok else "REQUIRE is occurrence-blind again - deleting the rebuttal ships green")
        _ok = not rebuts_verbatim("a command with no rebuttal at all")
        c.check("D9 REQUIRE fails when the rebuttal is deleted entirely", _ok,
                "" if _ok else "REQUIRE passes over an empty body")

        # H3 - `norm()` collapsed every run and made a near-miss compare equal.
        _ok = (rebuts_verbatim('reading *"Do not call the\nAgentTool unless the user\n' 'requested it"* is satisfied'))
        c.check("D10 REQUIRE survives a mid-quote line wrap", _ok,
                "" if _ok else "unwrap() is not collapsing wraps - 4 of the 8 real sites are wrapped")
        _ok = (not rebuts_verbatim('*"Do not call the AgentTool  unless the user requested it"* ' 'is satisfied'))
        c.check("D11 REQUIRE rejects a double-spaced near-miss (H3)", _ok,
                "" if _ok else "internal spacing is being collapsed - the check is not verbatim")
        _ok = (not rebuts_verbatim('*"Do not call the Agent tool unless the user requested it"* ' 'is satisfied'))
        c.check("D12 REQUIRE rejects `Agent tool` for `AgentTool`", _ok,
                "" if _ok else "REQUIRE accepts a near-miss - the check is not verbatim")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
