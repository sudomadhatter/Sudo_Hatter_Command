"""SCC-304 - /cicd-live-testing-team must reach for a REAL browser instrument.

⛔ THE DEFECT THIS EXISTS TO PREVENT.

`/cicd-live-testing-team` is the one command that flies a running app, so it is the one that finds
bugs nobody has noticed yet. Its Step 2 used to say, flatly:

    **You cannot see the browser.**

That was true when it was written and is no longer: Playwright is installed on the project under
test. While the sentence stood, every frontend symptom reached the bug doc by relay - the agent asked
the human for one Console line, then one Network row, then component state - and what landed in
`## Evidence` was whatever survived retyping. Screenshots never landed at all.

The fix is a skill. The RISK is that the skill exists and nothing routes to it: a `SKILL.md` in
`.agents/skills/` that no command names is a file, not an instrument, and its absence from the loop
is invisible - the command still runs, still files bug docs, and still never opens a browser.

── WHY THIS FILE IS SHAPED THE WAY IT IS: THREE HOLES, ALL MEASURED ──────────────────────────
The first version of this guard asserted that the slug STRING appeared in the command. A review
lens broke it three ways in a row, and every fix below is a measured kill, not a precaution:

  1. ⛔ **A token is not an instruction.** Replacing the routing bullet with
     *"do NOT load the `playwright-frontend-check` skill here"* left the slug present and the guard
     **10/10 green** - the exact defect this file exists to prevent, fully restored, certified clean.
     So C1 now requires the IMPERATIVE (`ROUTES`) and separately bans a NEGATION on any line that
     carries the slug.
  2. ⛔ **`BLINDNESS` as a literal pinned one spelling of the claim, not the claim.** *"You have no
     eyes on the browser"* and *"The agent cannot see the browser directly"* both passed 10/10. That
     is `prose-pinning-guards-are-vacuous` - the scar this docstring already cited while committing
     it. D1 is a regex over the claim's SHAPE now, with a CONTROL row proving a reworded form dies.
  3. ⛔ **Existence is not content.** `C2` only asked whether `SKILL.md` exists, so truncating BOTH
     copies to `# Playwright frontend check\n\nTODO.` left this file AND `test_command_surfaces.py`
     green - everything the lane shipped, deletable in silence. Block B pins the instrument's
     CHANNEL ROSTER: API tokens inside the code fence, never prose, so fix 2's scar does not apply
     to fix 3.

⛔ **The mutants that matter are the ones drawn from the SHIPPED FILES, not from these cases.**
Case-derived mutants are circular - they prove the suite agrees with itself. `sweep.json` carries
the negated-routing and gutted-skill mutants precisely because they once survived.

⛔ WHAT THIS FILE DELIBERATELY DOES NOT DO: launch a browser. `run_all.py` is stdlib-only by
contract and has to pass on a fresh clone, on the PC, and in CI - none of which has Playwright or a
downloaded chromium. Proving the recipe DRIVES a browser is a transcript in the lane's walkthrough.
Proving the recipe still SAYS what it must is block B, which is deterministic and costs nothing -
the two are different claims and only the first one needs a browser.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
COMMAND = ROOT / ".agents/commands/cicd-live-testing-team.md"
# The Antigravity door. `/smh-sync-agents` mirrors this command WHOLE (it is under the
# launcher-stub size cap), so this is a second LIVE copy of the instruction, not a stub that
# follows the master by reference. Checked for the same properties as the master.
WORKFLOW = ROOT / ".agents/workflows/cicd-live-testing-team.md"
BODIES = (COMMAND, WORKFLOW)
SKILLS = ROOT / ".agents/skills"

# The slug this command is required to route to. Named here rather than derived, because the
# REQUIRE half is the point: deriving "whatever skill the command mentions" would be satisfied
# by a command that mentions no skill at all.
SLUG = "playwright-frontend-check"

# ⛔ BACKTICKED, so `playwright-frontend-checker` cannot satisfy it. A bare substring test passed
# 10/10 against that rename, because the real slug is a PREFIX of the longer one.
ROUTES = re.compile(rf"load the `{re.escape(SLUG)}` skill", re.I)

# A line that names the slug while telling the agent NOT to use it routes nowhere. Measured: the
# negated bullet kept every other case green.
NEGATION = re.compile(r"\b(do not|don'?t|never|no longer|instead of|rather than|not)\s+load\b", re.I)

# The claim the skill retires, matched by SHAPE not spelling: subject + inability + perception +
# browser, all inside one sentence. Kills "you cannot see the browser", "the agent can't view the
# browser", "you have no eyes on the browser".
BLINDNESS_RE = re.compile(
    r"(?i)\b(you|the agent|i|it)\b[^.\n]{0,30}\b(cannot|can'?t|have no|has no|is unable to)\b"
    r"[^.\n]{0,30}\b(see|view|read|observe|eyes on)\b[^.\n]{0,20}browser")

# The capture channels the instrument is worthless without. API tokens inside the code fence -
# not prose - so rewording the surrounding text cannot satisfy or break them.
CHANNELS = ("page.on('console'", "page.on('pageerror'", "page.on('requestfailed'",
            "page.on('response'", "r.text()", "browser.close()")


def read(p: Path) -> str:
    """Text, or "" when the file cannot be read.

    ⛔ `utf-8-sig`, never `utf-8`: a BOM makes `text.startswith("---")` false, so `frontmatter_name`
    returns None and C3 reds on a file whose frontmatter is plainly correct. Eight command files in
    this repo carry a BOM today (PowerShell 5.1 writes one by default and half this system is a PC);
    `wf_common.read_text` and the sibling `test_command_surfaces.py` both already do this.

    ⛔ Returns "" rather than raising: an unreadable input must fail a NAMED case in block A, not
    kill the process with a `PermissionError`. A traceback exits non-zero with no `FAILED:` line,
    which `mutation_sweep.judge()` classifies as a SWEEP ERROR rather than a kill - so a crash here
    would corrupt every sweep that touches this file.
    """
    try:
        return p.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def strip_comments(text: str) -> str:
    """Remove HTML comments, so a reference that only lives inside one cannot satisfy C1.

    `comment-literals-invert-source-grep-tests` is a scar, not a hypothetical: a guard that
    greps raw text is satisfied by the very comment explaining why the thing was removed.
    """
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # An opener with no closer (the closing line deleted in the same edit) left the whole
    # comment INTACT, so the slug inside it still satisfied C1. Everything from an unmatched
    # `<!--` to EOF is commented out as far as a markdown reader is concerned.
    return re.sub(r"<!--(?!.*?-->).*\Z", "", text, flags=re.S)


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


def js_fence(text: str) -> str:
    """The INSTRUMENT's ```js block, or "" — block B's subject.

    ⛔ Not "the first js fence": the skill opens with a short `createRequire` snippet, and taking
    `[0]` measured 299 chars and reported every capture channel missing. The instrument is the
    LARGEST js fence, which is stable under reordering and under adding more small examples.
    """
    fences = re.findall(r"```js\n(.*?)```", text, re.S)
    return max(fences, key=len) if fences else ""


def _bom_probe() -> Path | None:
    """A BOM-prefixed SKILL.md in a temp dir — proves `read()` strips it (CTL1c)."""
    import tempfile
    d = Path(tempfile.mkdtemp())
    f = d / "SKILL.md"
    f.write_bytes(b"\xef\xbb\xbf---\nname: bom-probe\ndescription: x\n---\n\nbody\n")
    return f


_BOM_PROBE = _bom_probe()


def main() -> int:
    c = Cases("live-testing browser instrument: the command routes to a skill that exists")

    if c.block("A · the inputs exist and are READABLE (anti-vacuity)"):
        # Every case below reads one of these. A missing or unreadable input makes the whole file
        # pass by reading nothing, which is the failure mode this block exists to make loud.
        missing = [str(p.relative_to(ROOT)) for p in BODIES if not p.is_file()]
        c.check("A1 both live command bodies resolve (master + Antigravity mirror)",
                not missing, "" if not missing else f"missing: {missing}")
        c.check("A2 the skills master directory resolves", SKILLS.is_dir(),
                "" if SKILLS.is_dir() else f"missing: {SKILLS}")
        # ⛔ `read()` swallows OSError, so a file that EXISTS but cannot be read reaches here as "".
        # A1 alone would pass it; this is the case that catches it.
        thin = [f"{p.relative_to(ROOT)}={len(read(p))}"
                for p in BODIES if p.is_file() and len(read(p)) <= 2000]
        c.check("A3 both bodies are substantial and readable (not empty, not truncated)",
                not thin, "" if not thin else f"unreadable or suspiciously short: {thin}")

    live = {p: strip_comments(read(p)) for p in BODIES}

    if c.block("C · the WIRING chain - command -> skill file -> frontmatter name"):
        # ── Link 1a: every live body carries the IMPERATIVE, not merely the token ────
        silent = [str(p.relative_to(ROOT)) for p in BODIES if not ROUTES.search(live[p])]
        c.check("C1 every live command body ROUTES to the skill (imperative, not just the slug)",
                not silent, "" if not silent else
                f"no `load the \\`{SLUG}\\` skill` instruction in {silent} (comments stripped) - "
                "the slug may still appear, which is exactly the hole this case closes")

        # ── Link 1b: and does not tell the agent to skip it ──────────────────────────
        negated = []
        for p in BODIES:
            for i, line in enumerate(live[p].splitlines(), 1):
                if SLUG in line and NEGATION.search(line):
                    negated.append(f"{p.relative_to(ROOT)}:{i}")
        c.check("C1b no live body NEGATES the routing instruction", not negated,
                "" if not negated else
                f"a line names {SLUG} while telling the agent not to load it: {negated}")

        # ── Link 2: the slug resolves to a real SKILL.md ─────────────────────────────
        skill_md = SKILLS / SLUG / "SKILL.md"
        c.check("C2 the slug resolves to a SKILL.md on disk", skill_md.is_file(),
                "" if skill_md.is_file() else
                f"{skill_md.relative_to(ROOT)} does not exist - the command points at nothing")

        # ── Link 3: the frontmatter agrees with the slug ─────────────────────────────
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

    if c.block("B · the skill still CARRIES an instrument, not just a heading"):
        # ⛔ C2 is existence-only. Truncating the skill to `# Title\n\nTODO.` left this file and
        # `test_command_surfaces.py` BOTH green (door parity holds when master and mirror are
        # gutted equally), so everything the lane shipped was deletable in silence.
        skill_md = SKILLS / SLUG / "SKILL.md"
        body = read(skill_md)
        fence = js_fence(body)
        c.check("B1 the skill body is substantial", len(body) > 3000, f"{len(body)} chars")
        c.check("B2 the skill ships a runnable js instrument block", len(fence) > 400,
                f"js fence = {len(fence)} chars")
        gone = [t for t in CHANNELS if t not in fence]
        c.check("B3 the instrument registers every capture channel", not gone,
                "" if not gone else f"missing from the js fence: {gone}")
        # `pageerror` is the channel an agent most often forgets, and forgetting it produces a
        # confident "no JS errors" about a page that threw. It gets its own case.
        stated = (re.search(r"(?i)pageerror[^.\n]{0,60}\bnot\b[^.\n]{0,40}console", body) is not None
                  or re.search(r"(?i)`pageerror`.{0,400}?\bNOT in\b.{0,20}`?CONSOLE", body, re.S)
                  is not None)
        c.check("B4 the skill explains that pageerror is NOT console", stated,
                "" if stated else "the pageerror-vs-console distinction is not stated")

    if c.block("D · the browser-blindness claim is retired, not merely respelled"):
        # Source-grep guards cannot see ORDER, so this does not try to. It asserts the stronger,
        # simpler property: the claim is GONE in any spelling. Qualified reuse ("ask the human for
        # what a script cannot reach") is allowed - that sentence never says the agent cannot SEE.
        blind = []
        for p in BODIES:
            m = BLINDNESS_RE.search(live[p])
            if m:
                blind.append(f"{p.relative_to(ROOT)}: {m.group(0)!r}")
        c.check("D1 no door still claims the agent cannot see the browser (any wording)",
                not blind, "" if not blind else
                f"still asserts browser-blindness while routing to {SLUG}: {blind} - "
                "an agent reading in order follows the constraint, not the instrument")

    if c.block("E · the skill has a second, independent caller (Scope Ledger)"):
        # A skill whose only caller is the one command that shipped it is one edit away from
        # being unreachable. The skills INDEX is the router an agent reads when it does not
        # already know the skill exists.
        index = SKILLS / "INDEX.md"
        c.check("E1 the skills INDEX resolves", index.is_file(),
                "" if index.is_file() else f"missing: {index}")
        if index.is_file():
            c.check("E2 the skills INDEX routes to the skill", f"`{SLUG}`" in read(index),
                    "" if f"`{SLUG}`" in read(index) else
                    f"'{SLUG}' absent from skills/INDEX.md - the command is its only caller")

    if c.block("CONTROL · the matchers are seen FAILING, not just passing"):
        # ⛔ Every case above is an assertion that something IS present. None of them ever
        # exercises the matcher against input that must NOT match, so `strip_comments` and
        # `BLINDNESS_RE` were defended by docstring alone. 18 sibling suites carry CONTROL rows;
        # this is that convention.
        c.check("CTL1 strip_comments hides a slug that lives only in a comment",
                (_ctl := (SLUG not in strip_comments(f"<!-- load the `{SLUG}` skill -->"))),
                "" if _ctl else "a commented-out reference would satisfy C1")
        c.check("CTL1b strip_comments also hides a slug behind an UNTERMINATED comment",
                (_ctl := (SLUG not in strip_comments(f"ok\n<!-- removed\n load the `{SLUG}` skill later"))),
                "" if _ctl else "an unclosed <!-- leaves the slug visible, so C1 passes on a door that routes nowhere")
        c.check("CTL1c read() strips a UTF-8 BOM (8 command files carry one)",
                (_ctl := (frontmatter_name(_BOM_PROBE) == "bom-probe" if _BOM_PROBE else True)),
                "" if _ctl else "a BOM makes frontmatter look absent and reds C3 on a correct file")
        c.check("CTL2 ROUTES rejects a bare mention with no imperative",
                (_ctl := (not ROUTES.search(f"the `{SLUG}` skill produced this JSON"))),
                "" if _ctl else "ROUTES matches a passing mention, so C1 is back to token-matching")
        c.check("CTL3 ROUTES rejects a longer slug that merely starts with ours",
                (_ctl := (not ROUTES.search(f"load the `{SLUG}er` skill"))),
                "" if _ctl else "a prefix rename would satisfy C1")
        c.check("CTL4 NEGATION catches the measured negated bullet",
                (_ctl := (NEGATION.search(f"do NOT load the `{SLUG}` skill here") is not None)),
                "" if _ctl else "the exact bullet that passed 10/10 is still not caught")
        for probe in ("You cannot see the browser",
                      "You have no eyes on the browser",
                      "The agent cannot see the browser directly"):
            c.check(f"CTL5 BLINDNESS_RE catches {probe!r}",
                    (_ctl := (BLINDNESS_RE.search(probe) is not None)),
                    "" if _ctl else "a reworded blindness claim would pass D1")
        c.check("CTL6 BLINDNESS_RE does NOT fire on the legitimate fallback sentence",
                (_ctl := (BLINDNESS_RE.search(
                    "The human flies; ask them only for what a script cannot reach.") is None)),
                "" if _ctl else "D1 would red-wall the correct text")
        c.check("CTL7 frontmatter_name returns None on a body with no frontmatter",
                (_ctl := (frontmatter_name(ROOT / ".agents/skills/INDEX.md") is None)),
                "" if _ctl else "frontmatter_name invents a name for a file that has none")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
