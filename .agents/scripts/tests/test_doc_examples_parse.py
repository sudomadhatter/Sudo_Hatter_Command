"""No document teaches a machine-read block in a form its own parser rejects. (SCC-240)

⛔ THE DEFECT THIS FILE EXISTS FOR, measured on SCC-210 (2026-08-20).

Every place the `lenses_run:` roster was taught showed it INSIDE a fenced code block, and
`walkthrough_roster.strip_fenced` deletes fenced content before anything reads the document —
deliberately, because SCC-154 paid for that rule with a live miss. So an agent doing exactly
what the instruction said ("pasted VERBATIM") produced an artifact the close-out gate could
not see, and the refusal said "NO `lenses_run:` roster" while the roster sat visibly in the
file. Two preflight round trips to diagnose, on a lane that had done nothing wrong.

⭐ WHY THIS IS THE PART THAT MAKES RECURRENCE IMPOSSIBLE. Repairing the four documents is a
one-time fix; nothing stopped the next author re-fencing the example, and no check anywhere
joined "what the docs teach" to "what the parser accepts". This file is that join: it extracts
every taught example FROM THE DOCUMENTS THEMSELVES and runs it through the REAL parser. There
is no fixture of what the docs are supposed to say — a fixture would drift from the docs, which
is the same disease one layer up.

⛔ EXTRACTED AS WRITTEN, FENCE AND ALL. The region handed to the parser is the region a reader
copies: if the example sits in a fence, the fence markers come with it, because that is what
lands in the walkthrough. Dedenting, unfencing or "cleaning" the region here would test a form
nobody is taught and hide the exact defect this file was written for.

THE TWO KINDS OF SITE, and why they are judged differently (SCC-240 plan, decision 1):

  * a **paste-ready example** — concrete lens names, meant to be copied into a walkthrough.
    It MUST parse exactly as written. Fencing one is the defect.
  * a **return template** — `<placeholder>` rows, the engine's output contract. It stays
    fenced (`test_review_engine.py` and `test_lens_roster_contract.py` both locate it BY its
    fence and round-trip it filled), so instead it must carry the ⛔ instruction telling the
    reader the fence is illustration and must not be pasted.

The classifier is a property of the rows, not a list of filenames: a roster row carrying a
`<placeholder>` is a template row. A hard-coded file list would have to be maintained by the
same person who forgets to unfence.

Stdlib only, no pytest — same contract as everything else under this directory.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import declared_change_set as dcs  # noqa: E402
import walkthrough_roster as roster  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]

# Where a machine-read block is TAUGHT. Commands are the doors an operator types; the engine
# skill is what the review itself reads. `.agents/workflows/` and `.opencode/commands/` are
# GENERATED mirrors of the commands - scanning them would report every finding twice and make
# the failure list unreadable, and `test_command_surfaces.py` already proves they match their
# brain byte-for-byte, so a fixed brain is a fixed mirror.
TEACHING_GLOBS = (
    ".agents/commands/*.md",
    ".agents/skills/code-review-engine/*.md",
    ".agents/skills/code-review-engine/steps/*.md",
)

# ⛔ FROZEN (SCC-209). It names the roster in prose and teaches no block; it is excluded because
# it may not be EDITED, so a finding against it would be a red nobody is allowed to clear.
FROZEN = (".agents/commands/cicd-code-review-AP.md",)

FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
PLACEHOLDER_RE = re.compile(r"<[^>]+>")

# The instruction a fenced TEMPLATE must carry, matched on its load-bearing claim rather than
# on a whole sentence: the words that have to survive a rewrite are "fence" and the fact that
# fences are stripped. Anchored to the roster contract's own scar number so a reader who deletes
# it has to delete a citation too.
TEMPLATE_WARNING_RE = re.compile(
    r"fence[^.\n]*\bstrip|strip[^.\n]*\bfence|never (?:paste|copy|inside)[^.\n]*fence",
    re.I)


def teaching_files() -> list[Path]:
    out: list[Path] = []
    for g in TEACHING_GLOBS:
        out.extend(sorted(ROOT.glob(g)))
    return [p for p in out if str(p.relative_to(ROOT)).replace("\\", "/") not in FROZEN]


def fence_spans(lines: list[str]) -> list[tuple[int, int]]:
    """(open_idx, close_idx) per fenced block, CommonMark closing rule.

    Same rule as `walkthrough_roster.strip_fenced`: a fence closes on the SAME marker kind at
    at least the opening length, so a ``` inside a ~~~ block does not close it. An unclosed
    fence runs to end-of-file - which is what the stripper does too, and the safe direction.
    """
    spans: list[tuple[int, int]] = []
    open_at: int | None = None
    kind, width = "", 0
    for i, ln in enumerate(lines):
        m = FENCE_RE.match(ln)
        if not m:
            continue
        marker = m.group(1)
        if open_at is None:
            open_at, kind, width = i, marker[0], len(marker)
        elif marker[0] == kind and len(marker) >= width:
            spans.append((open_at, i))
            open_at = None
    if open_at is not None:
        spans.append((open_at, len(lines) - 1))
    return spans


def roster_examples(text: str) -> list[dict]:
    """Every `lenses_run:` example in one document, extracted the way a reader copies it.

    Fenced -> the region INCLUDES its fence markers, because that is what gets pasted.
    Unfenced -> the header plus the contiguous lines under it, which is the roster's own
    contiguity rule (`walkthrough_roster.parse`) applied to the document.
    """
    lines = text.splitlines()
    spans = fence_spans(lines)
    out: list[dict] = []
    for i, ln in enumerate(lines):
        if not roster._ROSTER_HEAD_RE.match(ln):
            continue
        span = next(((a, b) for a, b in spans if a < i <= b), None)
        if span:
            region, fenced = lines[span[0]: span[1] + 1], True
        else:
            end = i + 1
            while end < len(lines) and lines[end].strip():
                end += 1
            region, fenced = lines[i:end], False
        rows = [r for r in region if re.match(r"^\s*[-*]\s", r)]
        # A TEMPLATE is one whose every roster row is a placeholder. "Every", not "any": the
        # paste-ready examples carry a placeholder `lenses_na:` row beside two concrete lens
        # rows, and `any` would misfile both commands as templates - which is precisely the
        # pair this file has to fail on today.
        template = bool(rows) and all(PLACEHOLDER_RE.search(r) for r in rows)
        out.append({"line": i + 1, "region": "\n".join(region),
                    "fenced": fenced, "template": template, "rows": len(rows)})
    return out


def as_walkthrough(region: str) -> str:
    """The region dropped into the smallest walkthrough a caller would paste it into."""
    return "# W\n\n## Code Review\n\n" + region + "\n\nVerdict: PASS @ abc1234\n"


def declared_examples(text: str) -> list[dict]:
    """Every taught `## Declared Change Set` block, extracted the same way."""
    lines = text.splitlines()
    spans = fence_spans(lines)
    out: list[dict] = []
    for i, ln in enumerate(lines):
        if not re.match(r"^\s*##\s+Declared Change Set\s*$", ln):
            continue
        span = next(((a, b) for a, b in spans if a <= i <= b), None)
        if span:
            region = lines[span[0] + 1: span[1]]
        else:
            # ⛔ The EXAMPLE, not the rest of the section. Walking to the next `##` heading
            # works in a plan and over-reaches badly anywhere else: in this parser's own
            # module docstring it swallowed the "Consumers and their stakes" prose bullets,
            # which `ATTEMPT` then reported as three malformed declarations - a red about
            # the extractor wearing the costume of a red about the document. The block is
            # the contiguous run of bullets under the heading, which is what a reader copies.
            region = []
            for ln2 in lines[i + 1:]:
                s = ln2.strip()
                if not s:
                    if region:
                        break
                    continue
                if not re.match(r"^[-*+]\s", s):
                    break
                region.append(ln2)
        out.append({"line": i + 1, "region": "\n".join(region)})
    return out


def main() -> int:
    c = Cases("doc examples parse (SCC-240)")
    files = teaching_files()

    if c.block("D · every taught roster parses AS TAUGHT"):
        # ⭐ ANTI-VACUITY FIRST. Every check below loops over what the scan found, and a loop
        # over an empty list passes while proving nothing - a renamed directory or a typo'd
        # glob would read as "all documents clean" forever.
        c.check("D0 · the scan reached a real corpus",
                len(files) >= 20, f"only {len(files)} teaching file(s) globbed")
        found = [(p, ex) for p in files for ex in roster_examples(p.read_text(encoding="utf-8"))]
        c.check("D0b · ...and that corpus really teaches the roster",
                len(found) >= 4,
                f"{len(found)} `lenses_run:` example(s) found - the four known sites are the "
                f"two review commands, SKILL.md and step-04-record.md")

        paste = [(p, ex) for p, ex in found if not ex["template"]]
        c.check("D0c · ...including paste-ready examples, not only templates",
                len(paste) >= 2,
                f"{len(paste)} paste-ready example(s) - if this is 0 the row below is vacuous")

        broken = []
        for p, ex in paste:
            got = roster.parse(as_walkthrough(ex["region"]))["lenses"]
            if not got:
                broken.append(f"{p.relative_to(ROOT)}:{ex['line']}"
                              f"{' [fenced]' if ex['fenced'] else ''}")
        c.check("D1 · a paste-ready roster example parses through the REAL parser, "
                "exactly as the document writes it",
                not broken,
                f"{len(broken)} taught example(s) yield ZERO lenses when pasted verbatim: "
                f"{broken} - the instruction says VERBATIM and the parser strips fences "
                f"before it reads (SCC-154), so copying the example satisfies nobody")

        # The other half of the same claim: a template may keep its fence, but only if the
        # document TELLS the reader the fence is illustration. Silence there is the same
        # defect wearing a different hat - the reader copies what they see either way.
        unwarned = []
        for p, ex in found:
            if not ex["template"] or not ex["fenced"]:
                continue
            if not TEMPLATE_WARNING_RE.search(p.read_text(encoding="utf-8")):
                unwarned.append(f"{p.relative_to(ROOT)}:{ex['line']}")
        c.check("D2 · a fenced TEMPLATE says the fence is illustration and must not be "
                "pasted",
                not unwarned,
                f"{len(unwarned)} fenced template(s) with no such instruction: {unwarned}")

        # ⛔ NEGATIVE CONTROL, and it is not decoration: D1 loops over documents, so if the
        # extractor silently returned a region the parser happens to like, D1 would be green
        # on a broken corpus. This proves the machinery still SEES a fenced roster as empty.
        fenced_ctl = "```\nlenses_run:\n- blind-hunter · ok\n- edge · ok\n```"
        plain_ctl = "lenses_run:\n- blind-hunter · ok\n- edge · ok"
        c.check("D3 · (control) the check can still fail: a fenced roster reads as ZERO "
                "lenses and the same rows unfenced read as two",
                roster.parse(as_walkthrough(fenced_ctl))["lenses"] == []
                and len(roster.parse(as_walkthrough(plain_ctl))["lenses"]) == 2,
                "if this ever passes trivially the whole file is measuring nothing")

    if c.block("C · every taught Declared Change Set block parses AS TAUGHT"):
        # ⛔ WRITTEN GREEN, AND SAYING SO IS THE POINT (SCC-240 walkthrough). The roster half
        # above is red today; this half is not - the only taught declared-set example lives in
        # `declared_change_set.py`'s own docstring and already parses. It is pinned anyway
        # because the ticket's acceptance row 6 covers both blocks, and because the NEXT
        # example somebody adds to a command file is the one that will be wrong.
        sources = [ROOT / ".agents/scripts/declared_change_set.py"] + files
        found = []
        for p in sources:
            for ex in declared_examples(p.read_text(encoding="utf-8")):
                found.append((p, ex))
        c.check("C0 · the scan found a taught declared-set example (anti-vacuity)",
                bool(found), "no `## Declared Change Set` example anywhere - either the "
                             "teaching surface moved or the extractor is blind")
        broken = []
        for p, ex in found:
            # A docstring example is indented by Python, not by its author; a reader copying
            # it dedents without thinking. Dedent is applied HERE and nowhere else, and only
            # by the region's own common indent - never to a markdown example.
            region = ex["region"]
            if p.suffix == ".py":
                pad = min((len(l) - len(l.lstrip()) for l in region.splitlines() if l.strip()),
                          default=0)
                region = "\n".join(l[pad:] for l in region.splitlines())
            r = dcs.parse("## Declared Change Set\n" + region)
            if not r["entries"] or r["incomplete"]:
                broken.append(f"{p.relative_to(ROOT)}:{ex['line']} "
                              f"entries={len(r['entries'])} incomplete={r['incomplete']}")
        c.check("C1 · a taught declared-set example parses with entries and NO incomplete "
                "bullets",
                not broken, f"{len(broken)}: {broken}")
        bad = dcs.parse("## Declared Change Set\n\n- EDIT `a.md` no arrow here\n")
        c.check("C2 · (control) the check can still fail: a bullet with no `→` is reported "
                "incomplete",
                bad["incomplete"] and not bad["entries"], str(bad))

    if c.block("G · the verify wave names ONE grouping owner, in ONE place"):
        # SCC-210 sent 46 findings where there were 29 unique claims, because step-02 said
        # both "serialize ... one object per finding" and "verify each CLAIM once - fan the
        # query in", and read together the first sounds like "send everything, let the
        # verifier group". Nothing here is machine-wired - the fix is a document saying who
        # and when - so these are doc-truth pins, the weakest tier, and mutant M6 is what
        # proves they can fail.
        raw = (ROOT / ".agents/skills/code-review-engine/steps/step-02-verify.md"
               ).read_text(encoding="utf-8")
        # ⛔ WHITESPACE-NORMALISED, ON PURPOSE. These sentences are prose in a wrapped markdown
        # file, so where the line breaks fall is an editor's decision and not the contract. A
        # pin that reads the raw text is really asserting a line width: re-wrapping a paragraph
        # - which every edit to it does - turns it red for a reason nobody can act on, and the
        # cure people reach for is deleting the check. What is pinned is the WORDS and their
        # ORDER; both survive a re-wrap, and neither survives the rule being removed.
        t = re.sub(r"\s+", " ", raw)
        c.check("G1 · the dossier bullet says the caller groups BEFORE it serialises",
                "Group first, then serialise" in t
                and "AFTER the self-gate has read the raw count and BEFORE you serialise" in t,
                "the ordering is unstated - an agent reads 'serialize the findings' first "
                "and groups afterwards, or not at all")
        c.check("G2 · the 1:1 JSON contract is stated where the grouping is, not only "
                "three paragraphs later",
                "one object per finding — grouping never collapses it" in t,
                "grouping reads as permission to send fewer findings")
        c.check("G3 · the SCC-156 paragraph DEFERS to that bullet instead of restating "
                "a second rule",
                "the roles receive groups and never form them" in t,
                "the two paragraphs still read as competing instructions")
        # The structural claim, and the one a mutant cannot dodge by keeping the words while
        # moving them: the owner is named BEFORE the serialise instruction, inside the same
        # bullet. Order is what made the old text ambiguous, so order is what is pinned.
        i_group = t.find("Group first, then serialise")
        i_ser = t.lower().find("serialize the step-1 findings")
        c.check("G4 · ...and it is named BEFORE the serialise instruction it governs",
                0 <= i_group < i_ser,
                f"group@{i_group} serialise@{i_ser} - stated after, it is a correction "
                f"nobody reads in time")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
