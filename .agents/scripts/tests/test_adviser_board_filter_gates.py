"""Adviser-board filter rework (SCC-340) — the lane's acceptance gates, made standing.

The lane shipped its gates as `verify_board_filter.sh` inside its own artifact folder, which
close-out prunes — measured by the lane's review: the day the lane lands, the rework's regression
protection dies with the folder, and nothing in this suite would notice retired vocabulary
("default triad", "stage room", "R1 READ") re-entering the command. This file ports the four
gates that must outlive the lane into the standing suite, plus the rich-text render contract the
review found had zero assertions:

  * retired vocabulary (triad / caucus / stage room / stage change / three minds / team[s])
  * the retired R1-R4 round ladder (R1 READ / R2 ATTACK / R3 BALCONY / R4 SETTLE / round ladder)
  * parallel-wave vocabulary presence (opinion wave, one-message spawns, research brief, settle it)
  * door parity (opencode mirror byte-identical, claude skill description match, the brain claims
  antigravity and carries the inline-mode law its retired hand-owned door used to hold)
  * CARD.md render-contract markers (heading template, stance note, blockquote, bold slot labels,
    and all five statement slots named in the render template — the review found THE THIRD SIDE,
    which outranks THE MOVE, absent from it)

`floor` is adjudicated exactly as the lane's script adjudicates it: only caucus-log senses fail.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parents[1]  # .agents/scripts/tests -> repo root

BRAIN = ROOT / ".agents/commands/smh-adviser-board.md"
FOLDER = ROOT / ".agents/commands/adviser-board"
# ⛔ THE HAND-OWNED ANTIGRAVITY DOOR IS GONE (SCC-394). `.agents/workflows/smh-adviser-board.md`
# was hand-authored rather than generated — a condensed variant of a 52 KB brain — and it existed
# to carry an INLINE-mode paragraph for a platform with no subagent tool. The brain carries that
# law itself now (`## Running without subagents — inline mode`, a capability self-test rather than
# a platform branch), so the generated launcher is sufficient and the hand-owned door retires with
# the surface. Block F asserts the brain still carries it, which is the substance that door held.
SKILL = ROOT / ".claude/skills/smh-adviser-board/SKILL.md"
OC = ROOT / ".opencode/commands/smh-adviser-board.md"
CARD = FOLDER / "CARD.md"

SURFACES = [BRAIN, FOLDER / "CARD.md", FOLDER / "TEAMS.md", FOLDER / "DOCTRINE.md",
            FOLDER / "THIRD-SIDE.md", FOLDER / "SPAWNS.md", FOLDER / "ROSTER.md", SKILL, OC]

RETIRED_VOCAB = re.compile(r"triad|caucus|stage room|stage change|three minds|\bteams?\b", re.I)
RETIRED_ROUNDS = re.compile(r"R1 READ|R2 ATTACK|R3 BALCONY|R4 SETTLE|four visible rounds|four rounds|round ladder", re.I)
FLOOR_CAUCUS_SENSE = re.compile(
    r"floor file|floors-to-file|floor-circulation|true of the floor|no floor|floor section|floor/card|the floor\b", re.I)


# Justified exception, mirroring the lane script's ALLOWED list: the contract file keeps its
# historical TEAMS.md filename (plan declared EDIT, not RENAME), so a line that merely REFERENCES
# the filename is a hit on the name, not on team vocabulary.
FILENAME_REF = re.compile(r"TEAMS\.md")


def _scan(pattern: re.Pattern) -> list[str]:
    """Every pattern hit over the gated surfaces, `minds/` excluded — the lane's own scope."""
    hits: list[str] = []
    for surface in SURFACES:
        if not surface.is_file():
            hits.append(f"SURFACE MISSING: {surface.relative_to(ROOT)}")
            continue
        for i, line in enumerate(surface.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                rel = surface.relative_to(ROOT)
                if "/minds/" in f"/{rel}":
                    continue
                stripped = line.strip()
                if pattern is RETIRED_VOCAB and FILENAME_REF.search(stripped) and not pattern.search(
                        FILENAME_REF.sub("", stripped)):
                    continue  # hit exists only inside the TEAMS.md filename reference
                hits.append(f"{rel}:{i}: {stripped[:160]}")
    return hits


def main() -> int:
    c = Cases("adviser-board filter gates (SCC-340, standing)")

    if c.block("A · every gated surface exists (a missing file makes greps pass vacuously)"):
        for s in SURFACES:
            c.check(f"A · {s.relative_to(ROOT)} present", s.is_file(), str(s))

    if c.block("B · zero retired vocabulary (triad/caucus/stage room/three minds/team(s))"):
        hits = _scan(RETIRED_VOCAB)
        c.check("B · zero unjustified hits", not hits, "; ".join(hits[:6]) or "clean")

    if c.block("C · zero retired R1–R4 round-ladder terms"):
        hits = _scan(RETIRED_ROUNDS)
        c.check("C · zero hits", not hits, "; ".join(hits[:6]) or "clean")

    if c.block("D · parallel-wave vocabulary present (brain + SPAWNS)"):
        brain = BRAIN.read_text(encoding="utf-8")
        spawns = (FOLDER / "SPAWNS.md").read_text(encoding="utf-8")
        c.check("D · brain carries 'opinion wave'", "opinion wave" in brain.lower())
        c.check("D · brain carries one-message parallel spawns",
                "all agent calls in a single message" in brain.lower())
        c.check("D · SPAWNS carries 'opinion wave'", "opinion wave" in spawns.lower())
        c.check("D · SPAWNS carries the orchestrator research brief",
                "research brief" in spawns.lower())
        c.check("D · brain carries the 'settle it' deepening move", "settle it" in brain.lower())

    if c.block("E · 'floor' adjudication — only caucus-log senses fail"):
        hits = _scan(FLOOR_CAUCUS_SENSE)
        c.check("E · no caucus-log sense of 'floor'", not hits, "; ".join(hits[:6]) or "clean")

    if c.block("F · door parity (opencode byte-identical · claude skill desc · inline law in brain)"):
        c.check("F · opencode mirror byte-identical to brain",
                OC.read_bytes() == BRAIN.read_bytes())
        desc = re.compile(r"^description:(.*)$", re.M)
        brain_txt = BRAIN.read_text(encoding="utf-8")
        bm = desc.search(brain_txt)
        sm = desc.search(SKILL.read_text(encoding="utf-8"))
        # ⛔ COMPARE THE VALUES, NOT THE BYTES (SCC-394 re-review). The launcher's description is
        # emitted as a QUOTED YAML scalar, because Antigravity's loader is strict YAML and an
        # unquoted value containing ": " kills the door outright. The brain's own line may be
        # quoted or not. So unwrap both before comparing, or this asserts a formatting accident
        # rather than "the launcher carries the brain's description", which is the real contract.
        def _yaml_scalar(v: str) -> str:
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                inner = v[1:-1]
                return inner.replace('\\"', '"').replace("\\\\", "\\") if v[0] == '"' else inner
            return v
        c.check("F · claude skill description matches brain description",
                bool(bm and sm) and _yaml_scalar(bm.group(1)) == _yaml_scalar(sm.group(1)))
        # ⭐ THE COMMAND MUST CLAIM THE PLATFORM IT NOW HAS A DOOR ON (SCC-394). Its hand-owned
        # Antigravity workflow was never derived from `platforms:` — that is what "hand-owned"
        # meant — so the command could publish to Antigravity while declaring three other
        # platforms, and did. With that surface retired, reach comes from the frontmatter like
        # every other command, and a missing `antigravity` here silently drops the board from
        # Antigravity's menu with nothing else in the repo noticing.
        _pl = re.search(r"^platforms:\s*\[(.*?)\]", brain_txt, re.M)
        _claims = [x.strip().strip("'\"").lower() for x in _pl.group(1).split(",")] if _pl else []
        c.check("F · the brain CLAIMS antigravity, so the launcher reaches that menu",
                "antigravity" in _claims,
                f"platforms: {_claims or 'ABSENT'} - smh-adviser-board's hand-owned Antigravity "
                f"door is retired, so reach comes from this list like every other command; "
                f"without `antigravity` here the launcher never enters that menu")
        # ⛔ AND THE LAW THAT DOOR CARRIED MUST OUTLIVE IT. The retired workflow held an
        # INLINE-mode paragraph for a platform with no subagent tool. A generated launcher
        # carries no sentences of its own, so if the brain does not state it, it is simply gone.
        c.check("F · the brain carries the inline-mode law the hand-owned door used to hold",
                "## Running without subagents" in brain_txt,
                "the retired Antigravity door was the only place the no-subagent path was "
                "written down; a launcher cannot carry it, so the brain must")

    if c.block("G · CARD.md render contract — every slot has a home in the render template"):
        card = CARD.read_text(encoding="utf-8")
        render = card.split("## Rendering", 1)[-1]
        for slot in ("THE THIRD SIDE", "THE MOVE", "COULDN'T SETTLE", "ASSUMED", "SPLIT"):
            c.check(f"G · render template names {slot}", f"**{slot}:**" in render)
        c.check("G · render template carries the heading pattern", "### {icon} {Filter} — {Mind}" in render)
        c.check("G · render template carries the italic stance note", "*{one-line stance note" in render)
        c.check("G · render template carries the blockquote prose", "> {the statement's prose" in render)

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
