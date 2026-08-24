"""SCC-304 - /cicd-live-testing-team must reach for a REAL browser instrument.

⛔ THE DEFECT THIS EXISTS TO PREVENT.

`/cicd-live-testing-team` is the one command that flies a running app, so it is the one that finds
bugs nobody has noticed yet. Its Step 2 used to say, flatly:

    **You cannot see the browser.**

That was true when it was written and is no longer: Playwright is installed on this machine
(`@playwright/test` in the AGY frontend, chromium in `~/Library/Caches/ms-playwright`). While the
sentence stood, every frontend symptom reached the bug doc by relay - the agent asked the human for
one Console line, then one Network row, then component state - and what landed in `## Evidence` was
whatever survived retyping. Screenshots never landed at all.

The fix is a skill. The RISK is that the skill exists and nothing routes to it: a `SKILL.md` in
`.agents/skills/` that no command names is a file, not an instrument, and its absence from the loop
is invisible - the command still runs, still files bug docs, and still never opens a browser.

── WHAT THIS GUARD ASSERTS, AND WHY IT IS NOT A GREP FOR PROSE ──────────────────────────────
This house has three separate memories about source-grep guards going blind: a comment can satisfy
them, they cannot see ORDER, and pinning prose is vacuous. So this file pins **wiring**, a chain in
which every link is a real object on disk:

    the command body names a skill slug
        -> that slug resolves to `.agents/skills/<slug>/SKILL.md` that EXISTS
            -> whose frontmatter `name:` equals the slug

Mutants it kills, each verified by hand before this file was committed:
  * delete `.agents/skills/playwright-frontend-check/` .............. RED (link 2)
  * rename the slug in the command body only ....................... RED (link 2)
  * rename `name:` inside the skill's frontmatter .................. RED (link 3)
  * comment the reference out in the command ....................... RED (C3: the reference must
                                                                     survive comment-stripping)
A guard that only asserted "the string appears in the command" kills exactly none of the last two.

⛔ WHAT THIS FILE DELIBERATELY DOES NOT DO: launch a browser. `run_all.py` is stdlib-only by
contract and has to pass on a fresh clone, on the PC, and in CI - none of which has Playwright or a
downloaded chromium. Proving the skill's recipe actually drives a browser is a TRANSCRIPT recorded
in the lane's walkthrough, not a suite row. A suite row that needs a 150MB browser download is a
suite row that gets skipped, and a skipped row is a green that lies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
COMMAND = ROOT / ".agents/commands/cicd-live-testing-team.md"
SKILLS = ROOT / ".agents/skills"

# The slug this command is required to route to. Named here rather than derived, because the
# REQUIRE half is the point: deriving "whatever skill the command mentions" would be satisfied
# by a command that mentions no skill at all.
SLUG = "playwright-frontend-check"

# The sentence the skill replaces. It may not stand unqualified - see case C4.
BLINDNESS = "You cannot see the browser"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def strip_comments(text: str) -> str:
    """Remove HTML comments, so a reference that only lives inside one cannot satisfy C1.

    `comment-literals-invert-source-grep-tests` is a scar, not a hypothetical: a guard that
    greps raw text is satisfied by the very comment explaining why the thing was removed.
    """
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def frontmatter_name(skill_md: Path) -> str | None:
    """The `name:` from a SKILL.md's YAML frontmatter, or None if it has no frontmatter."""
    text = read(skill_md)
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    for line in text[3:end].splitlines():
        if line.strip().startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def main() -> int:
    c = Cases("live-testing browser instrument: the command routes to a skill that exists")

    if c.block("A · the inputs exist (anti-vacuity)"):
        # Every case below reads one of these two. A missing input makes the whole file pass
        # by reading nothing, which is the failure mode this block exists to make loud.
        c.check("A1 the command body resolves", COMMAND.is_file(),
                "" if COMMAND.is_file() else f"missing: {COMMAND}")
        c.check("A2 the skills master directory resolves", SKILLS.is_dir(),
                "" if SKILLS.is_dir() else f"missing: {SKILLS}")
        body = read(COMMAND) if COMMAND.is_file() else ""
        c.check("A3 the command body is substantial (not a truncated read)",
                len(body) > 2000, f"{len(body)} chars")

    body = read(COMMAND) if COMMAND.is_file() else ""
    live = strip_comments(body)

    if c.block("C · the WIRING chain - command -> skill file -> frontmatter name"):
        # ── Link 1: the command names the slug, outside of any comment ───────────
        c.check("C1 the command body names the skill slug", SLUG in live,
                "" if SLUG in live else
                f"'{SLUG}' absent from {COMMAND.name} (comments stripped) - "
                "the skill exists but nothing routes to it")

        # ── Link 2: the slug resolves to a real SKILL.md ─────────────────────────
        skill_md = SKILLS / SLUG / "SKILL.md"
        c.check("C2 the slug resolves to a SKILL.md on disk", skill_md.is_file(),
                "" if skill_md.is_file() else
                f"{skill_md.relative_to(ROOT)} does not exist - the command points at nothing")

        # ── Link 3: the frontmatter agrees with the slug ─────────────────────────
        # A SKILL.md whose `name:` disagrees with its directory is a door the harness lists
        # under one name and the command calls by another.
        if skill_md.is_file():
            fm = frontmatter_name(skill_md)
            c.check("C3 the skill's frontmatter name matches its directory", fm == SLUG,
                    "" if fm == SLUG else f"frontmatter name={fm!r}, directory={SLUG!r}")
            head = read(skill_md)[:1200]
            c.check("C4 the skill carries a description (CS-06 loadability)",
                    "description:" in head,
                    "" if "description:" in head else "no `description:` in the first 1200 chars")
        else:
            c.check("C3 the skill's frontmatter name matches its directory", False,
                    "skipped: no SKILL.md to read (C2 failed)")
            c.check("C4 the skill carries a description (CS-06 loadability)", False,
                    "skipped: no SKILL.md to read (C2 failed)")

    if c.block("D · the browser-blindness claim is retired, not merely contradicted"):
        # ⛔ The dangerous shape is a command that BOTH routes to the skill AND still tells the
        # agent it cannot see the browser. An agent reading top-to-bottom hits the blindness
        # sentence first, in the same Step, and follows it. Two instructions, one wins, and the
        # one that wins is the one that reads as a hard constraint.
        #
        # Source-grep guards cannot see ORDER, so this does not try to. It asserts the stronger
        # and simpler property: the unqualified sentence is GONE. Qualified re-use is allowed -
        # the human is still the fallback - which is why the check is on the bare string.
        c.check("D1 the bare 'cannot see the browser' claim is gone",
                BLINDNESS not in live,
                "" if BLINDNESS not in live else
                f"{COMMAND.name} still asserts \"{BLINDNESS}\" while routing to {SLUG} - "
                "an agent reading in order follows the constraint, not the instrument")

    if c.block("E · the skill has a second, independent caller (Scope Ledger)"):
        # The audit's caller-count check, made permanent: a skill whose only caller is the one
        # command that shipped it is one edit away from being unreachable. The skills INDEX is
        # the router an agent reads when it does not already know the skill exists.
        index = SKILLS / "INDEX.md"
        c.check("E1 the skills INDEX resolves", index.is_file(),
                "" if index.is_file() else f"missing: {index}")
        if index.is_file():
            c.check("E2 the skills INDEX routes to the skill", SLUG in read(index),
                    "" if SLUG in read(index) else
                    f"'{SLUG}' absent from skills/INDEX.md - the command is its only caller")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
