"""Every call site of `bmad-create-story` names where the story file lands (SCC-260).

BMAD's own skill sets `default_output_file = {implementation_artifacts}/{story_key}.md`
(`.claude/skills/bmad-create-story/SKILL.md:76`). The house convention is somewhere else
entirely — measured on AGY 2026-08-21: **139** story files under `_bmad/bmm/stories/`, **zero**
under `_bmad-output/implementation-artifacts/`. Every downstream door (`cicd-write-story-tests`
Step 1, boot Step 2b's "next story", close-out's status flip) reads the house path.

⛔ BMAD IS NOT EDITED AND NOT OVERRIDDEN — operator ruling, 2026-08-21. No `_bmad/custom/*.toml`,
no patch to the vendored skill. The convention is held **at our call sites**: a command that
invokes the skill and says nothing lets BMAD's default win by silence, and `/sm`'s create-story
route did exactly that. Naming the directory next to the invocation is the whole fix.

Section-scoped on purpose: a file that names the path in some unrelated section, twenty
headings away from the invocation, has not told the reader anything at the moment it matters.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir

COMMANDS = SCRIPTS.parent / "commands"

SKILL = "bmad-create-story"
HOUSE_DIR = "_bmad/bmm/stories/"
BMAD_DEFAULT = "_bmad-output/implementation-artifacts/"

MIN_CALLERS = 2
"""`cicd-write-story-tests.md` and `sm.md` as of SCC-260. A floor, not a census — if the
skill is renamed or the commands folder moves, "every caller names the path" would be
vacuously true of zero callers and this scan would report a clean pass over nothing."""


def sections(text: str) -> list[tuple[str, int, str]]:
    """-> [(heading or "" for the preamble, 1-based start line, body incl. the heading)].

    A `###` child opens its own section: the invocation and the path have to sit close
    enough that a reader following the command finds them together.

⛔ FENCE-AWARE. A `# comment` on the first column of a ```bash block is byte-identical to an
`<h1>`, and the very fix this scan demanded plants one. Un-guarded, the section ended AT the
code it was checking for and the body check reported a section a third of its real length.
    """
    out: list[tuple[str, int, str]] = []
    head, start, buf = "", 1, []
    fenced = False
    for n, raw in enumerate(text.splitlines(), 1):
        if raw.lstrip().startswith("```"):
            fenced = not fenced
        if not fenced and re.match(r"^#{1,6}\s+\S", raw):
            if buf:
                out.append((head, start, "\n".join(buf)))
            head, start, buf = raw.strip(), n, [raw]
        else:
            buf.append(raw)
    if buf:
        out.append((head, start, "\n".join(buf)))
    return out


def offenders(folder: Path) -> tuple[list[tuple[str, int, str, str]], int, int]:
    """-> ([(file, line, heading, why)], files read, sections that invoke the skill)."""
    bad: list[tuple[str, int, str, str]] = []
    files = sorted(folder.glob("*.md"))
    callers = 0
    for path in files:
        for head, line, body in sections(path.read_text(encoding="utf-8")):
            if SKILL not in body:
                continue
            callers += 1
            if HOUSE_DIR not in body:
                bad.append((path.name, line, head or "(preamble)",
                            f"invokes `{SKILL}` without naming `{HOUSE_DIR}` — BMAD's own "
                            f"`{BMAD_DEFAULT}` default wins by silence"))
            elif BMAD_DEFAULT in body:
                bad.append((path.name, line, head or "(preamble)",
                            f"names BOTH `{HOUSE_DIR}` and `{BMAD_DEFAULT}` beside the "
                            f"invocation — the destination has to be unambiguous"))
    return bad, len(files), callers


def report(rows: list[tuple[str, int, str, str]]) -> str:
    if not rows:
        return ""
    return ("\n      " + "\n      ".join(f"{f}:{n}  {h}  — {why}" for f, n, h, why in rows)
            + f"\n      REMEDY: name `{HOUSE_DIR}` in the same section as the invocation. "
              f"Never a `_bmad/custom/*.toml` override — BMAD is not edited.")


def main() -> int:
    c = Cases("the story output path is pinned at every call site (SCC-260)")

    if c.block("G1 · the live command surface"):
        bad, n_files, callers = offenders(COMMANDS)
        c.check(f"the scan found at least {MIN_CALLERS} `{SKILL}` call sites "
                "(zero callers is a FAIL, not a pass)",
                callers >= MIN_CALLERS, f"{callers} caller section(s) across {n_files} files")
        c.check(f"every section invoking `{SKILL}` names `{HOUSE_DIR}`",
                not bad, f"{len(bad)} call site(s) leave it to BMAD" + report(bad))

    if c.block("G2 · the scan fires on each way a call site can go wrong"):
        with TempDir() as tmp:
            plant = tmp / "cmds"
            plant.mkdir()

            def one(body: str) -> list[tuple[str, int, str, str]]:
                (plant / "z.md").write_text(body, encoding="utf-8")
                return offenders(plant)[0]

            c.check("caught: a bare route with no path (the `/sm` defect, verbatim)",
                    len(one("- create the next story    → invoke `bmad-create-story`\n")) == 1,
                    "this is the line SCC-260 was raised on")

            c.check("caught: the path named in a DIFFERENT section",
                    len(one(f"## Route\ninvoke `{SKILL}`\n\n## Notes\nstories live in "
                            f"`{HOUSE_DIR}`\n")) == 1,
                    "twenty headings away is not next to the invocation")

            c.check("caught: BMAD's default named alongside the house path",
                    len(one(f"## Step 1\ninvoke `{SKILL}` — writes to `{HOUSE_DIR}` "
                            f"(or `{BMAD_DEFAULT}`)\n")) == 1,
                    "two destinations is no destination")

            c.check("quiet: the invocation and the path in one section",
                    not one(f"## Step 1 — Create the story\nInvoke the **`{SKILL}`** skill. This "
                            f"writes the story file under `{HOUSE_DIR}` with its ACs.\n"),
                    "the shape cicd-write-story-tests.md already uses")

            c.check("a `# comment` in a ```fence``` does not split the invocation off the path",
                    not one(f"## Step 1\nInvoke `{SKILL}`.\n```bash\n# writes the file\nls\n```\n"
                            f"The story lands under `{HOUSE_DIR}`.\n"),
                    "a fence between the two must not become a section boundary")

            c.check("quiet: a command that never invokes the skill is not policed",
                    not one("## Step 1\nRead the story file and get on with it.\n"),
                    "the law is about call sites, not about the word `stories`")

            c.check("a preamble invocation (a file with no headings at all) is still a call site",
                    offenders(plant)[2] >= 0 and len(one(f"invoke `{SKILL}`\n")) == 1,
                    "`/sm` has no `##` headings — a heading-only walk would skip it entirely")

            empty = tmp / "empty"
            empty.mkdir()
            _, n, callers = offenders(empty)
            c.check("an empty folder yields zero callers, so the floor FAILS it",
                    callers < MIN_CALLERS, f"read {n} files, {callers} callers")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
