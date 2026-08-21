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

from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import walkthrough_roster as roster  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
POST = "_artifacts/_main/2026-08-16_lane/walkthrough.md"      # in scope
PRE = "_artifacts/_main/2026-08-10_lane/walkthrough.md"       # legacy

STEP07 = ("## Step 0.7 — re-derivation\n\n"
          "1. What moved: nothing moved.\n"
          "2. What that changes here: nothing.\n"
          "3. What was re-measured: the three anchors.\n\n")


RECENT = "_artifacts/_main/2026-08-20_lane/walkthrough.md"     # dispositions/drift era
DISPO = "dispositions:    per-lens: blind=1/2/0 · edge=2/0/1"
DRIFT = "drift:           undeclared=0 · unimplemented=0 · incomplete=0 — clean"


def wt(verdict: str = "PASS", sha: str = "abc1234", roster_rows: str | None = None,
       runtime: str | None = None, step07: bool = True, na: str | None = None,
       dispo: str | None = None, drift: str | None = None) -> str:
    out = "# W\n\n"
    if runtime:
        out += f"review-runtime: {runtime}\n\n"
    if step07:
        out += STEP07
    out += "## Code Review\n\n"
    if roster_rows is not None:
        out += "lenses_run:\n" + roster_rows + "\n"
    if na is not None:
        out += f"lenses_na:       {na}\n"
    if dispo is not None:
        out += dispo + "\n"
    if drift is not None:
        out += drift + "\n"
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

    if c.block("NA · a DROPPED lens is READABLE, and a fan-out cannot justify one (SCC-203)"):
        # ⛔ THE STATE WITH NO MACHINE READER. step-01 retired `ok (not blind — context held
        # <what>)` and records a dropped Blind Hunter on `lenses_na:` instead. That is the right
        # record, and until now nothing downstream could read it - `lenses_na:` is a separate
        # field, so the row never reached the roster regex and a dropped lens was invisible to
        # both preflights.
        DROP = "blind-hunter · n/a — context contaminated (held the plan and walkthrough)"
        ok, why = roster.judge(wt(roster_rows=ALL_INLINE, runtime="inline", na=DROP), POST, "PASS")
        c.check("NA1 · an `inline` lane may DROP the blind lens and still pass",
                ok, f"this is the SCC-203 ruling's designed end state, not a degradation: {why}")
        ok, why = roster.judge(wt(roster_rows=ALL_OK, runtime="fan-out", na=DROP), POST, "PASS")
        c.check("NA2 · a `fan-out` lane that drops a lens BLOCKS",
                not ok and "fan-out" in " ".join(why),
                "a subagent starts clean BY CONSTRUCTION, so `context contaminated` is not a "
                "statement this runtime can make; dropping the one lens whose value comes from "
                f"starvation and then passing is the whole defect: {why}")
        ok, why = roster.judge(wt(roster_rows=ALL_INLINE, runtime="inline",
                                  na="blind-hunter"), POST, "PASS")
        c.check("NA3 · an `n/a` with NO reason BLOCKS",
                not ok and "no reason" in " ".join(why),
                f"bare `n/a` is indistinguishable from a lens nobody bothered to run: {why}")
        ok, why = roster.judge(wt(roster_rows=ALL_OK, runtime="fan-out", na="none"), POST, "PASS")
        c.check("NA4 · (control) `lenses_na: none` is the normal answer and passes",
                ok, f"the common case must not block or the field will be omitted: {why}")
        got = roster.parse(wt(roster_rows=ALL_INLINE, runtime="inline", na=DROP))["lenses_na"]
        # ⛔ THE HYPHEN CONTROL. `blind-hunter` carries a hyphen and so does the separator form,
        # so a separator matched without surrounding whitespace splits the NAME: lens `blind`,
        # reason `hunter · n/a — ...`. That parses, reads as reasoned, and names a lens that does
        # not exist. Asserting the exact name is what catches it - a truthy check would not.
        c.check("NA5 · (parser) the dropped lens NAME survives its own hyphen, with its reason",
                [(l["lens"], bool(l["reason"])) for l in got] == [("blind-hunter", True)],
                f"expected [('blind-hunter', True)], got {got}")
        c.check("NA6 · (control) no `lenses_na:` field means zero dropped lenses",
                roster.parse(wt(roster_rows=ALL_OK))["lenses_na"] == [],
                "an absent field must not fabricate a dropped lens")

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
    # Its OWN block, not part of I3: the spelling tolerance is a separate claim from the
    # contradiction rule, and a mutant that breaks one should not be attributable to the other.
    if c.block("I3-S · both header spellings, because the contract and the header disagree"):
        # ⛔ The caller contract spells the INPUT `review_runtime` (house style, beside
        # `review_mode` and `lens_budget`); the walkthrough header is `review-runtime`. An agent
        # reading one and writing the other produces a header this parser would not see - and an
        # unread header is not an error anyone is told about: `runtime` comes back None, I3 never
        # fires, and the gate reports clean. Reading both is the only version that fails closed.
        c.check("I3e · BOTH spellings are read - an underscore header is not silently ignored",
                roster.parse("review_runtime: inline\n")["runtime"] == "inline"
                and roster.parse("review-runtime: inline\n")["runtime"] == "inline",
                "the contract says `review_runtime`, the header says `review-runtime`; a parser "
                "that reads only one turns the other into a silent no-op")
        ok, why = roster.judge(
            wt(roster_rows=ALL_OK).replace("# W\n", "# W\n\nreview_runtime: inline\n", 1),
            POST, "PASS")
        c.check("I3f · ...and the underscore header BLOCKS the same contradiction",
                not ok and "inline" in " ".join(why),
                f"I3e proves the parser reads it; this proves the block still fires on it: {why}")

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

    if c.block("P-F · a FENCED roster is an EXAMPLE, and the instructions teach it fenced"):
        # ⛔ SELF-INFLICTED, AND FOUND BY THIS LANE'S OWN INLINE REVIEW. The Step 4 text this lane
        # wrote shows the roster inside a ``` block, so copying the example was enough to satisfy
        # the gate. `task_preflight` was safe (it strips fences first, SCC-154 finding 8);
        # `closeout_preflight` passed RAW text, so the identical file passed the story-lane gate
        # and was refused by the Task-lane one. The fence rule now lives in the PARSER, which is
        # the only place two callers cannot disagree about it.
        fenced = ("# W\n\n## Step 0.7\n\n1. a\n2. b\n3. c\n\n## Code Review\n\n"
                  "Paste the block the engine returned:\n\n"
                  "```\nlenses_run:\n- blind-hunter · ok\n- edge · ok\n```\n\n"
                  "Verdict: PASS @ abc1234\n")
        c.check("P-F1 · a roster that exists ONLY inside a fence is not a roster",
                roster.parse(fenced)["lenses"] == [],
                "the instruction's own example would otherwise close a lane that ran nothing")
        ok, why = roster.judge(fenced, POST, "PASS")
        # ⛔ AMENDED BY SCC-240, and the amendment is the point. This case used to assert the
        # refusal was the WORD-FOR-WORD "NO `lenses_run:` roster" message - "exactly as if it
        # had none". The blocking half was always right and is unchanged; the message half was
        # the defect: a lane whose roster is visibly in the file, correctly formatted, told
        # only that it has no roster. It cost two preflight round trips on SCC-210. What is
        # pinned now is that it still BLOCKS *and* that it says which of the three things
        # happened - block F owns the full three-way contract.
        c.check("P-F2 · ...so the lane BLOCKS - and since SCC-240 it says the fence is why",
                not ok and "fence" in " ".join(why).lower(), str(why))
        c.check("P-F3 · (control) unfencing the same rows makes it a real roster",
                len(roster.parse(fenced.replace("```\n", ""))["lenses"]) == 2,
                "if this fails the stripper eats real content, which is the opposite failure")
        # CommonMark closing rule: a ~~~ block whose body contains ``` must not leak (SCC-154's
        # measured miss, ported with the logic rather than re-derived from the description).
        nested = ("# W\n\n## Code Review\n\n~~~\nlenses_run:\n- a · ok\n```\n- b · ok\n~~~\n\n"
                  "Verdict: PASS @ abc1234\n")
        c.check("P-F4 · a ``` inside a ~~~ block does not re-open the scan",
                roster.parse(nested)["lenses"] == [],
                "the first cut of this walker toggled on ANY marker, leaking the inner lines")

    if c.block("P-R · a RE-REVIEW appends, so the LAST roster governs"):
        # ⛔ THE SAME FIRST-VS-LAST BUG THIS LANE ALREADY SHIPPED ONCE, one layer down. At
        # `task_preflight`'s call site it was `found[0]` where the rest of the function reads
        # `found[-1]`; here the parser returned the FIRST `lenses_run:` block. Consequence is
        # identical and worse: a lane whose first pass had a dead lens, and which then did exactly
        # what the refusal asked - re-run the review - is judged on the superseded roster. The
        # remedy for a dead lens could never clear it, and the lane is wedged by the evidence of
        # its own fix.
        rr = ("# W\n\n## Step 0.7\n\n1. a\n2. b\n3. c\n\n"
              "## Code Review (2026-08-16)\n\nlenses_run:\n- blind · dead — timed out\n\n"
              "Verdict: FAIL @ aaa1111\n\n"
              "## Code Review (2026-08-17)\n\nlenses_run:\n- blind · ok\n- edge · ok\n\n"
              "Verdict: PASS @ bbb2222\n")
        got = roster.parse(rr)["lenses"]
        c.check("P-R1 · the LAST roster is the one read",
                [l["state"] for l in got] == ["ok", "ok"],
                f"read {got} - the first roster is the one the re-review replaced")
        ok, why = roster.judge(rr, POST, "PASS")
        c.check("P-R2 · ...so a re-reviewed lane is not blocked by its cleared dead lens",
                ok, f"the re-review is the documented remedy; blocking on it makes the remedy "
                    f"unreachable: {why}")
        # And the direction that must still block: clean first, dead after.
        pf = ("# W\n\n## Step 0.7\n\n1. a\n2. b\n3. c\n\n"
              "## Code Review (2026-08-16)\n\nlenses_run:\n- blind · ok\n\nVerdict: PASS @ a\n\n"
              "## Code Review (2026-08-17)\n\nlenses_run:\n- blind · dead — died\n\n"
              "Verdict: PASS @ b\n")
        ok, why = roster.judge(pf, POST, "PASS")
        c.check("P-R3 · (control) clean-then-DEAD still blocks - last means last, not best",
                not ok and "DEAD lens" in " ".join(why),
                f"taking the last roster must not become taking the most favourable one: {why}")

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

    if c.block("W-B · the gate BLOCKS - the routing, not just the call (behaviour)"):
        # ⛔ W1-W3 prove the parser is reached. They cannot see WHERE ITS ANSWER GOES, and the
        # call site routes on one word: `(rep.info if ok_roster else rep.err)`. Flip that to
        # `rep.info` unconditionally and every check above stays green while the gate reports a
        # rosterless PASS as clean - a warn-tier gate, which is the exact thing the operator's
        # ruling forbids ("I dont see a case in enterprise dev where a warn should make it to
        # prod"). Only running the real function and reading the SEVERITY closes that.
        # ⛔ Imported HERE, not borrowed from block W. A `--case W-B` run skips W entirely, so a
        # name bound only there is unbound in this block — and the failure mode is a traceback
        # AFTER the first case fails, which the sweep reads as "exit 1 with no `FAILED:` line"
        # and refuses to score. A block that cannot be run alone cannot kill a mutant alone.
        # Found by this lane's own sweep: EI-8 and EI-9 both came back unattributable.
        import closeout_preflight
        import task_preflight
        import wf_common as wf

        def sev(rep, section: str) -> list[str]:
            return [i["sev"] for i in rep.items if i["section"] == section]

        with TempDir() as tmp:
            art = tmp / "_artifacts/_main/2026-08-16_lane/story-scc-999-x"
            art.mkdir(parents=True)
            page = art / "walkthrough.md"

            page.write_text(wt(roster_rows=None), encoding="utf-8")
            rep = wf.Report()
            closeout_preflight.check_artifacts(tmp, "scc-999-x", rep)
            c.check("W-B1 · a rosterless PASS is an ERROR out of closeout_preflight",
                    "ERROR" in sev(rep, "artifacts"),
                    f"the parser blocks but the gate does not: {sev(rep, 'artifacts')} - "
                    f"{[i['msg'] for i in rep.items][:2]}")

            page.write_text(wt(roster_rows=ALL_OK), encoding="utf-8")
            rep = wf.Report()
            closeout_preflight.check_artifacts(tmp, "scc-999-x", rep)
            c.check("W-B2 · (control) the same lane WITH a roster is not an error",
                    "ERROR" not in sev(rep, "artifacts"),
                    f"a full roster must not block, or the gate is unusable: "
                    f"{[i['msg'] for i in rep.items]}")

            # ⛔ W-B3: the LATEST stamp governs, and this call site had it backwards. A re-review
            # APPENDS - so FAIL-then-PASS is a lane that was FIXED. Judging the roster against
            # `found[0]` handed the parser the superseded FAIL and blocked a lane the rest of
            # check_gate had already cleared, re-planting the any(FAIL)-over-all-hits defect
            # whose own remedy (re-run the review) could then never clear it. Held on the parser
            # boundary because that is where the wrong verdict would arrive.
            two = wt(verdict="FAIL", roster_rows=ALL_OK) + "\n\nVerdict: PASS @ def5678\n"
            stamps = re.findall(r"Verdict:\s*(PASS|FAIL)", two)
            c.check("W-B3 · (fixture) the re-review fixture really carries FAIL then PASS",
                    stamps == ["FAIL", "PASS"], str(stamps))
            c.check("W-B3b · the LAST stamp is what judge() must be handed",
                    roster.judge(two, POST, stamps[-1])[0]
                    and not roster.judge(two, POST, stamps[0])[0],
                    "if both answers agreed, the first-vs-last choice would be untestable here")

            # ...and W-B4 is the same claim against the REAL call site, which is the only place
            # the first-vs-last choice is actually made. W-B3b proves the two verdicts disagree;
            # only this proves task_preflight hands over the right one.
            lane = tmp / "lane" / "_artifacts" / "_main" / "2026-08-16_re-review"
            lane.mkdir(parents=True)
            (lane / "task.yaml").write_text(
                "task_key: SCC-999\nbranch: chore/SCC-999-x\n", encoding="utf-8")
            (lane / "walkthrough.md").write_text(two, encoding="utf-8")
            rep = wf.Report()
            task_preflight.check_gate(tmp / "lane", [lane / "walkthrough.md"], "LOCAL",
                                      "SCC-999", "chore/SCC-999-x", rep)
            fails = [i["msg"] for i in rep.items
                     if i["sev"] == "ERROR" and "Verdict FAIL" in i["msg"]]
            c.check("W-B4 · a re-reviewed FAIL→PASS lane is NOT blocked by its cleared FAIL",
                    not fails,
                    f"the superseded stamp was handed to the parser and blocked a fixed lane: "
                    f"{fails}")

    # ── SCC-231/233 · the record lines have a MACHINE tier (2026-08-20) ───────────────────
    # This lane's own review found both obligations prose-only against a measured 12/142
    # compliance base rate for prose law - so presence is gated HERE, in the one parser both
    # preflights already read, with the same date-scoping mechanism as CUTOFF.
    if c.block("H · dispositions: and drift: are required in the dispo era"):
        full = wt(roster_rows=ALL_OK, dispo=DISPO, drift=DRIFT)
        d = roster.parse(full)
        c.check("H1 · parse reads the dispositions payload",
                d["dispositions"] == "per-lens: blind=1/2/0 · edge=2/0/1",
                repr(d["dispositions"]))
        c.check("H2 · parse reads the drift payload",
                d["drift"] is not None and d["drift"].startswith("undeclared=0"),
                repr(d["drift"]))
        c.check("H3 · both read None when absent",
                roster.parse(wt(roster_rows=ALL_OK))["dispositions"] is None
                and roster.parse(wt(roster_rows=ALL_OK))["drift"] is None, "")
        two = full + "\n## Code Review (re-run)\n\nlenses_run:\n" + ALL_OK + \
              "dispositions:    per-lens: blind=9/9/9\n" + DRIFT + "\nVerdict: PASS @ beef123\n"
        c.check("H4 · the LAST dispositions line governs (a re-review appends)",
                roster.parse(two)["dispositions"] == "per-lens: blind=9/9/9",
                repr(roster.parse(two)["dispositions"]))

        ok, why = roster.judge(wt(roster_rows=ALL_OK, drift=DRIFT), RECENT, "PASS")
        c.check("H5 · a dispo-era lane with NO dispositions line BLOCKS",
                not ok and any("dispositions" in w for w in why), str(why))
        ok, why = roster.judge(wt(roster_rows=ALL_OK, dispo=DISPO), RECENT, "PASS")
        c.check("H6 · a dispo-era lane with NO drift line BLOCKS",
                not ok and any("drift" in w for w in why), str(why))
        ok, why = roster.judge(wt(roster_rows=ALL_OK, dispo=DISPO, drift=DRIFT),
                               RECENT, "PASS")
        c.check("H7 · both lines present passes clean", ok, str(why))
        ok, why = roster.judge(wt(roster_rows=ALL_OK), POST, "PASS")
        c.check("H8 · a pre-2026-08-20 lane is EXEMPT from both (not retroactive law)",
                ok, str(why))

    # ── SCC-240 · the refusal names WHICH way the roster was lost, and the reader RUNS ────
    # ⛔ THE COST THIS BUYS BACK, measured on SCC-210 (2026-08-20). Three rejections presented
    # as one sentence - "Verdict PASS with NO `lenses_run:` roster" - while the roster was
    # visibly in the file. The first was a roster inside a fence (stripped before reading,
    # SCC-154); the second a blank line after the header (the contiguity rule, `parse` above);
    # each cost a full preflight round trip plus a read of this parser's internals to diagnose,
    # because there was no way to ASK this module what it saw. ~12 minutes on one lane, and it
    # recurs on every lane that writes a roster, which is every reviewed lane.
    #
    # ⛔ NEITHER RULE IS RELAXED HERE, and that is the ticket's own DO NOT list: `strip_fenced`
    # exists because a canonical verdict pasted as evidence inside a fence once became the
    # governing verdict, and contiguity is what stops a stray bullet elsewhere in the document
    # silently extending the roster. What changes is that the refusal EXPLAINS itself.
    if c.block("F · the refusal says WHY, and the reader can be RUN"):
        import json
        import subprocess

        MOD = Path(__file__).resolve().parents[1] / "walkthrough_roster.py"

        fenced = ("# W\n\n## Step 0.7\n\n1. a\n2. b\n3. c\n\n## Code Review\n\n"
                  "```\nlenses_run:\n- blind-hunter · ok\n- edge · ok\n```\n\n"
                  + DISPO + "\n" + DRIFT + "\n\nVerdict: PASS @ abc1234\n")
        gap = ("# W\n\n## Step 0.7\n\n1. a\n2. b\n3. c\n\n## Code Review\n\n"
               "lenses_run:\n\n- blind-hunter · ok\n- edge · ok\n\n"
               + DISPO + "\n" + DRIFT + "\n\nVerdict: PASS @ abc1234\n")
        absent = wt(roster_rows=None, dispo=DISPO, drift=DRIFT)
        good = wt(roster_rows=ALL_OK, runtime="fan-out", dispo=DISPO, drift=DRIFT)

        # F1-F1c · the CLI. It is a library today - no `main()`, no `if __name__` - so the
        # only way to learn what it saw was to write a throwaway script against its internals,
        # which is the defect underneath the other two: nothing could be CHECKED until the
        # close-out refused it.
        r = subprocess.run([sys.executable, str(MOD), "--help"],
                           capture_output=True, text=True)
        c.check("F1 · the module runs as a command at all",
                r.returncode == 0 and "usage" in (r.stdout + r.stderr).lower(),
                f"rc={r.returncode} out={(r.stdout + r.stderr)[:120]!r} - a library-only "
                f"reader can only be interrogated by writing a script against its internals")

        with TempDir() as tmp:
            page = tmp / "_artifacts/_main/2026-08-16_lane/walkthrough.md"
            page.parent.mkdir(parents=True)

            page.write_text(good, encoding="utf-8")
            r = subprocess.run([sys.executable, str(MOD), str(page)],
                               capture_output=True, text=True)
            payload = {}
            for blob in (r.stdout, r.stdout[r.stdout.find("{"):]):
                try:
                    payload = json.loads(blob)
                    break
                except Exception:
                    continue
            c.check("F1b · on a good walkthrough it PRINTS what it parsed and exits 0",
                    r.returncode == 0
                    and len(payload.get("lenses", [])) == 3
                    and payload.get("runtime") == "fan-out"
                    and payload.get("dispositions") and payload.get("drift")
                    and payload.get("rederive_lines") == 3,
                    f"rc={r.returncode} stdout={r.stdout[:200]!r} err={r.stderr[:120]!r}")

            page.write_text(fenced, encoding="utf-8")
            r = subprocess.run([sys.executable, str(MOD), str(page)],
                               capture_output=True, text=True)
            c.check("F1c · on a REFUSED walkthrough it exits non-zero and prints the reason",
                    r.returncode == 1 and "fence" in (r.stdout + r.stderr).lower(),
                    f"rc={r.returncode} out={(r.stdout + r.stderr)[:200]!r} - a self-check "
                    f"that exits 0 on a block the gate will refuse is worse than none")

            r = subprocess.run([sys.executable, str(MOD), str(tmp / "nope.md")],
                               capture_output=True, text=True)
            c.check("F1d · a missing file is a loud exit 2, never a verdict about content",
                    r.returncode == 2 and not r.stdout.strip(),
                    f"rc={r.returncode} out={r.stdout[:100]!r} err={r.stderr[:100]!r}")

        # F2 · the fenced case, named as fenced.
        ok, why = roster.judge(fenced, POST, "PASS")
        blob = " ".join(why)
        c.check("F2 · a roster lost to a code FENCE is named as fenced, with the reason "
                "the fence rule exists",
                not ok and "fence" in blob.lower() and "SCC-154" in blob,
                f"the roster is visibly in the file and the refusal says it is absent: {why}")

        # F3 · the contiguity case. SCC-210 hit this SECOND, after fixing the fence, and got
        # the identical sentence - which is why "it says nothing useful" is the defect rather
        # than "it says the wrong thing".
        ok, why = roster.judge(gap, POST, "PASS")
        blob = " ".join(why)
        c.check("F3 · a roster ended by a BLANK LINE after its header is named as "
                "non-contiguous",
                not ok and "contiguous" in blob.lower(),
                f"the second rejection must not present as the first: {why}")

        # F4 · the control that keeps the other two honest. A genuinely absent roster must
        # still read exactly as it did - if the new branches leak into this message the
        # refusal starts blaming a fence that was never there.
        ok, why = roster.judge(absent, POST, "PASS")
        blob = " ".join(why)
        c.check("F4 · a genuinely ABSENT roster keeps today's message, unchanged",
                not ok and "NO `lenses_run:` roster" in blob
                and "recovered-inline" in blob and "## Code Review" in blob,
                f"the existing refusal is load-bearing and was not the defect: {why}")
        c.check("F4b · ...and it does NOT blame a fence or contiguity that was never there",
                "fence" not in blob.lower() and "contiguous" not in blob.lower(),
                f"a diagnosis that fires on every case diagnoses nothing: {why}")

        # F5 · the same three states, readable off `parse` - so the CLI above and `judge`
        # are reading data rather than each re-deciding. `parse` stays total: flags, not
        # verdicts.
        # ⛔ `.get`, never `[...]`. A missing key raises, and a traceback AFTER the first
        # case is what a mutation sweep reads as "exit 1 with no FAILED: line" and refuses to
        # score - so the block that proves the flags exist could not itself be swept.
        c.check("F5 · parse reports the fenced-header state as data",
                roster.parse(fenced).get("roster_header_fenced") is True
                and roster.parse(gap).get("roster_header_fenced") is False
                and roster.parse(absent).get("roster_header_fenced") is False,
                f"fenced={roster.parse(fenced).get('roster_header_fenced')} "
                f"gap={roster.parse(gap).get('roster_header_fenced')} "
                f"absent={roster.parse(absent).get('roster_header_fenced')}")
        c.check("F5b · parse reports the empty-header state as data",
                roster.parse(gap).get("roster_header_empty") is True
                and roster.parse(absent).get("roster_header_empty") is False
                and roster.parse(good).get("roster_header_empty") is False,
                f"gap={roster.parse(gap).get('roster_header_empty')} "
                f"absent={roster.parse(absent).get('roster_header_empty')} "
                f"good={roster.parse(good).get('roster_header_empty')}")

        # F6 · precedence. A roster that is BOTH fenced and (inside the fence) blank-separated
        # must name the fence - it is the outer cause, and unfencing is the whole remedy.
        both = ("# W\n\n## Step 0.7\n\n1. a\n2. b\n3. c\n\n## Code Review\n\n"
                "```\nlenses_run:\n\n- blind-hunter · ok\n```\n\n"
                + DISPO + "\n" + DRIFT + "\n\nVerdict: PASS @ abc1234\n")
        ok, why = roster.judge(both, POST, "PASS")
        c.check("F6 · fenced AND gapped names the FENCE - the outer cause, and the one "
                "whose fix subsumes the other",
                not ok and "fence" in " ".join(why).lower(),
                f"sending the author to fix the blank line inside a block that is stripped "
                f"whole is a second wasted round trip: {why}")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
