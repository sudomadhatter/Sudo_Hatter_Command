"""test_walkthrough_roster — a Verdict is a conclusion; the roster is the evidence (SCC-173/177).

The defect: `Verdict: PASS @ <sha>` with zero lenses run merged cleanly, because the only
record a review left was the line asserting its own result. Found by SCC-163's self-audit while
that lane was closing, and nothing in the repo could have caught it.

⛔ EVERY CASE HERE PINS WIRING, NOT PROSE. The retired shape (SCC-125) is a source grep that
asserts a document mentions a word; those are blind three ways and this file must not add a
fourth instance. So: fixtures round-trip through the real parser, and the two preflights are
asserted to CALL it rather than to contain its name.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import walkthrough_roster as roster  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
POST = "_artifacts/_main/2026-08-16_lane/walkthrough.md"      # in scope
PRE = "_artifacts/_main/2026-08-10_lane/walkthrough.md"       # legacy

STEP07 = ("## Step 0.7 — re-derivation\n\n"
          "1. What moved: nothing moved.\n"
          "2. What that changes here: nothing.\n"
          "3. What was re-measured: the three anchors.\n\n")


def wt(verdict: str = "PASS", sha: str = "abc1234", roster_rows: str | None = None,
       runtime: str | None = None, step07: bool = True) -> str:
    out = "# W\n\n"
    if runtime:
        out += f"review-runtime: {runtime}\n\n"
    if step07:
        out += STEP07
    out += "## Code Review\n\n"
    if roster_rows is not None:
        out += "lenses_run:\n" + roster_rows + "\n"
    out += f"\nVerdict: {verdict} @ {sha}\n"
    return out


ALL_OK = "- correctness · ok\n- edge · ok\n- security · ok\n"
ONE_DEAD = "- correctness · ok\n- edge · ok\n- security · dead — budget exhausted\n"
ALL_INLINE = ("- correctness · recovered-inline\n- edge · recovered-inline\n"
              "- security · recovered-inline\n")


def main() -> int:
    c = Cases("walkthrough roster (SCC-173 + SCC-177)")

    if c.block("E1 · a PASS with no roster is UNKNOWN, and UNKNOWN blocks"):
        ok, why = roster.judge(wt(roster_rows=None), POST, "PASS")
        c.check("E1 · `Verdict: PASS` with no `lenses_run:` BLOCKS",
                not ok and "NO `lenses_run:` roster" in " ".join(why),
                "this is the shipped defect: the verdict asserts the review's conclusion and "
                f"nothing asserts the review happened. {why}")
        c.check("E1b · ...and the refusal says how to fix it, not just that it failed",
                "recovered-inline" in " ".join(why) and "## Code Review" in " ".join(why), why)

    if c.block("E2 · the contradiction, and the floor that is NOT one"):
        ok, why = roster.judge(wt(roster_rows=ONE_DEAD), POST, "PASS")
        c.check("E2 · PASS + a DEAD lens is a contradiction and BLOCKS",
                not ok and "DEAD lens" in " ".join(why),
                f"a lens that saw nothing cannot support a PASS: {why}")
        # ⭐ THE ESCAPE HATCH, AND IT MUST NOT BE AN ACCIDENT. The engine's own contract raises
        # the floor to CONCERNS when a lens is still dead after retry + inline rerun. If this
        # blocked too, a lane with one dead lens could never close and the gate would be routed
        # around instead of used. The plan's first draft got this backwards; F4 corrected it.
        ok, why = roster.judge(wt(verdict="CONCERNS", roster_rows=ONE_DEAD), POST, "CONCERNS")
        c.check("E2b · CONCERNS + a DEAD lens is CONSISTENT and passes",
                ok, f"this is the designed floor and the only exit that is not a bypass: {why}")
        ok, why = roster.judge(wt(roster_rows=ALL_OK), POST, "PASS")
        c.check("E2c · (control) PASS with every lens ok passes", ok, str(why))

    if c.block("E3 · FAIL blocks on its own account"):
        ok, why = roster.judge(wt(verdict="FAIL", roster_rows=ALL_OK), POST, "FAIL")
        c.check("E3 · FAIL blocks even with a full roster", not ok, str(why))

    if c.block("E4 · the dated cutoff is the scope limiter, not a warn tier"):
        ok, why = roster.judge(wt(roster_rows=None), PRE, "PASS")
        c.check("E4 · a pre-cutoff lane with no roster is LEGACY and passes",
                ok and "legacy" in " ".join(why).lower(),
                "130 of 142 walkthroughs have no roster; retrofitting them is not the ask")
        ok, why = roster.judge(wt(roster_rows=None), POST, None)
        c.check("E4b · no verdict at all is OUT OF SCOPE - this module says nothing",
                ok and not why,
                "the lightweight lane has no verdict by design; a roster demand there would "
                "be this gate inventing a second rule for itself")
        # ⛔ The cutoff is a LITERAL, not "today". The plan first wrote it as the day E ships,
        # which would have made the lane that BUILT the parser legacy — the first lane it did
        # not bind would be the one that wrote it (F28).
        c.check("E4c · the cutoff is pinned to a literal date, not computed from the clock",
                roster.CUTOFF == "2026-08-15",
                f"CUTOFF={roster.CUTOFF} - a computed cutoff exempts its own lane and answers "
                f"differently on the two machines")
        c.check("E4d · the lane's date comes from the ARTIFACT FOLDER, not a file timestamp",
                roster.lane_date(POST) == "2026-08-16"
                and roster.lane_date("/x/y/no-date-here/walkthrough.md") is None,
                "a checkout rewrites mtime and a rebase rewrites git log; the folder name is "
                "the only date that survives both")

    if c.block("E7 · Step 0.7's re-derivation must be three lines, and may say nothing moved"):
        ok, why = roster.judge(wt(roster_rows=ALL_OK, step07=False), POST, "PASS")
        c.check("E7 · a missing re-derivation BLOCKS",
                not ok and "re-derivation" in " ".join(why), str(why))
        short = wt(roster_rows=ALL_OK, step07=False).replace(
            "## Code Review", "## Step 0.7\n\n1. only one line.\n\n## Code Review", 1)
        ok, why = roster.judge(short, POST, "PASS")
        c.check("E7b · one line is not three", not ok, str(why))
        c.check("E7c · (control) 'nothing moved' counts - the cheap answer is allowed",
                roster.judge(wt(roster_rows=ALL_OK), POST, "PASS")[0],
                "the silent answer is what is banned, not the short one")

    if c.block("I3 · a declared `inline` runtime and a lens reporting `ok` disagree"):
        # F20. Under `inline` the ladder runs ONCE, so `recovered-inline` is the only legal
        # per-lens state — an `ok` means a fan-out was attempted against the declaration, or
        # the header is wrong. Either way the data contradicts itself, and that shows up here.
        ok, why = roster.judge(wt(roster_rows=ALL_OK, runtime="inline"), POST, "PASS")
        c.check("I3 · header `inline` + a lens `ok` BLOCKS",
                not ok and "inline" in " ".join(why) and "`ok`" in " ".join(why), str(why))
        ok, why = roster.judge(wt(roster_rows=ALL_INLINE, runtime="inline"), POST, "PASS")
        c.check("I3b · (control) `inline` + every lens `recovered-inline` passes", ok, str(why))
        ok, why = roster.judge(wt(roster_rows=ALL_OK, runtime="fan-out"), POST, "PASS")
        c.check("I3c · (control) `fan-out` + every lens `ok` passes", ok, str(why))
        c.check("I3d · the runtime header round-trips through the parser",
                roster.parse(wt(runtime="inline"))["runtime"] == "inline"
                and roster.parse(wt())["runtime"] is None,
                "the header is a machine field; if the parser cannot read it, I3 is decoration")

    if c.block("P · the parser reads the shapes people actually write"):
        c.check("P1 · `·`, `:` and `|` all separate a lens from its state",
                all(len(roster.parse(f"lenses_run:\n- edge {sep} ok\n")["lenses"]) == 1
                    for sep in ("·", ":", "|")),
                "one separator would make the roster a spelling test")
        c.check("P2 · backticked lens names and states parse",
                roster.parse("lenses_run:\n- `blind-hunter` · `dead`\n")["lenses"]
                == [{"lens": "blind-hunter", "state": "dead", "notes": ""}])
        c.check("P3 · notes after an em dash are kept, not dropped",
                roster.parse("lenses_run:\n- edge · dead — ran out of budget\n"
                             )["lenses"][0]["notes"] == "ran out of budget",
                "the note is the only place a dead lens explains itself")
        c.check("P4 · a stray bullet elsewhere does not extend the roster",
                len(roster.parse("lenses_run:\n- edge · ok\n\n## Later\n\n- not a lens\n"
                                 )["lenses"]) == 1,
                "a roster that swallows the rest of the document reports lenses nobody ran")
        c.check("P5 · no roster is an empty list, never an exception",
                roster.parse("# nothing here\n")["lenses"] == [])

    if c.block("W · BOTH preflights call the one parser - asserted by wiring, not by grep"):
        # ⛔ The retired shape is `assert "walkthrough_roster" in source` — a source grep that a
        # comment satisfies and that cannot see whether the call is reachable. These import the
        # modules and check the binding is the SAME OBJECT, so a second copy of the logic, a
        # shadowed name or a dead import all fail.
        import closeout_preflight
        import task_preflight
        c.check("W1 · closeout_preflight's `roster` IS this module",
                closeout_preflight.roster is roster,
                "story lanes close through this file; a private copy would drift")
        c.check("W2 · task_preflight's `roster` IS this module",
                task_preflight.roster is roster,
                "Task lanes close through this file - the ticket names closeout_preflight "
                "first, but smh lanes never touch it")
        for mod, name in ((closeout_preflight, "closeout_preflight"),
                          (task_preflight, "task_preflight")):
            src = Path(mod.__file__).read_text(encoding="utf-8")
            c.check(f"W3 · {name} actually CALLS judge(), not merely imports it",
                    re.search(r"roster\.judge\s*\(", src) is not None,
                    "an import with no call is a gate that never runs")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
