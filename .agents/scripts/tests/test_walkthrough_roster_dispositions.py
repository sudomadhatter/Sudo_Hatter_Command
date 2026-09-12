"""walkthrough_roster — the findings table is READ, and the stamp is refused on an open row. (SCC-447 Part 3)

⛔ WHAT THIS FILE EXISTS FOR. SCC-441 spent a week of API credits in a review loop with no stop
condition an agent could reach: the floor was computed from whatever the lenses first returned,
fixing never lowered it, and the only road from CONCERNS to PASS was another full fan-out. The
corrected doctrine (`code-standards.md` §6.5/§7, ruled 2026-09-11) gives the floor exactly two ways
down, both evidence: a receipt showing the command does NOT fail, or a fix with a pin seen red
then green. This file is the machine tier of that ruling — the close-out reads the findings table
and refuses a stamp that the rows do not support.

The refusals, each with its positive control (a gate seen only refusing is a description of intent):

  * a `fixed` row on a `nitpick`/`suggestion` — the policy for those is a COUNT, never a fix;
  * a `fixed` row with no `pin <test>` — a fix without a test seen red is an unreviewed edit;
  * a `fixed`/`held` critical/important whose `repro <id>` receipt is absent — named by path;
  * a receipt that does not say `reproduced` — a dropped finding is not fixed;
  * a `held` row whose `patch <path>` is absent — the fix must be WRITTEN, not promised;
  * PASS or CONCERNS with an open reproduced critical (a held critical is open) — that is FAIL;
  * PASS or CONCERNS with a reproduced `important` neither `fixed` nor `held` — "finish the fix";
  * PASS with a held important — CONCERNS (authority) is the consistent verdict;
  * two `lenses_run:` rosters with no operator line — one review per lane;
  * and the pre-cutoff lanes, SCC-441's own included, are UNTOUCHED.

Scope is `DISPOSITION_CUTOFF`, a LITERAL date (E4c): a computed cutoff exempts its own lane.
Fixtures round-trip through the real parser; the receipt cases use a real temp tree.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import walkthrough_roster as roster  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
POST = "_artifacts/_main/2026-09-13_lane/walkthrough.md"      # in scope
EDGE = "_artifacts/_main/2026-09-12_lane/walkthrough.md"      # ON the cutoff: in scope
PRE = "_artifacts/_main/2026-09-10_lane/walkthrough.md"       # exempt
SCC441 = REPO / "_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/walkthrough.md"

STEP07 = ("### Step 0.7 — re-derivation\n\n"
          "1. What moved: nothing moved.\n"
          "2. What that changes here: nothing.\n"
          "3. What was re-measured: the three anchors.\n\n")
ROSTER = "lenses_run:\n- edge · ok\n- acceptance · ok\n- test-adequacy · ok\n"
DISPO = "dispositions:    per-lens: edge=1/0/0 · acceptance=0/0/0 · test-adequacy=0/0/1\n"
DRIFT = "drift:           undeclared=0 · unimplemented=0 · incomplete=0 — clean\n"
HEAD = "| # | file:line | sev | lens | failure scenario | disposition |\n|---|---|---|---|---|---|\n"
HEAD_REPRO = ("| # | file:line | sev | lens | failure scenario | repro | disposition |\n"
              "|---|---|---|---|---|---|---|\n")

FIXED = "fixed @abc1234 · pin test_x.py:B1 · repro f1"
HELD = "held — ask-first: security rules · repro f1 · patch gates/repro/f1.patch"


def row(n: int, sev: str, dispo: str, repro: str | None = None) -> str:
    cells = [str(n), "`x.py:10`", sev, "edge", "the wrong thing happens"]
    if repro is not None:
        cells.append(repro)
    cells.append(dispo)
    return "| " + " | ".join(cells) + " |\n"


def wt(verdict: str = "PASS", rows: str = "", head: str = HEAD, roster: str = ROSTER,
       second: str | None = None, rereview: str | None = None, restamp: bool = False,
       fenced_example: bool = False) -> str:
    """A post-doctrine walkthrough: Step 0.7, one `## Code Review` with a roster, the two record
    lines, ONE findings table, a stamp — and optionally a second roster or a re-stamp section."""
    out = "# W\n\nreview-runtime: fan-out\n\n" + STEP07 + "## Code Review (2026-09-13)\n\n"
    if fenced_example:
        out += "For reference the engine returns:\n\n```\nlenses_run:\n- example · ok\n```\n\n"
    out += roster + "lenses_na:       none\n" + DISPO + DRIFT + "\n"
    if rows:
        out += head + rows + "\n"
    out += f"Verdict: {verdict} @ abc1234\n"
    if second is not None:
        out += "\n## Code Review (2026-09-14, re-review)\n\n"
        if rereview:
            out += rereview + "\n\n"
        out += second + "lenses_na:       none\n" + DISPO + DRIFT + f"\nVerdict: {verdict} @ def5678\n"
    if restamp:
        out += ("\n## Code Review (2026-09-14, re-stamp after fixes)\n\n"
                f"Verdict: {verdict} @ def5678\n"
                "retest: scoped — pins: test_x.py:B1 · suite: run_all 88/88 @ def5678\n"
                "review: carried from the one review @ abc1234 — no lens re-run\n")
    return out


def _receipt(lane: Path, fid: str, result: str = "reproduced") -> Path:
    p = lane / "gates" / "repro" / f"{fid}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"id": fid, "result": result, "exit_code": 3 if result == "reproduced" else 0,
                             "command": ["python3", "-c", "x"], "cwd": ".", "sha": "abc1234",
                             "dirty_tree": False, "output_tail": "boom",
                             "recorded_at": "2026-09-13T00:00:00+00:00"}), encoding="utf-8")
    return p


def _patch(lane: Path, fid: str) -> Path:
    p = lane / "gates" / "repro" / f"{fid}.patch"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("diff --git a/x.py b/x.py\n", encoding="utf-8")
    return p


def main() -> int:
    c = Cases("walkthrough roster — dispositions and the stamp (SCC-447)")

    # ── C · the cutoff is a literal, and the lane's date decides scope ──────────────────
    if c.block("C · the cutoff is a LITERAL, and scope is by lane date"):
        c.check("C1 · DISPOSITION_CUTOFF is the literal 2026-09-12, not computed from the clock",
                getattr(roster, "DISPOSITION_CUTOFF", None) == "2026-09-12",
                f"got {getattr(roster, 'DISPOSITION_CUTOFF', None)!r} - a computed cutoff exempts "
                f"its own lane and answers differently on the two machines (E4c)")
        ok, why = roster.judge(wt(rows=row(1, "nitpick", FIXED)), PRE, "PASS")
        c.check("C2 · a PRE-cutoff lane with a fixed nitpick is untouched (not retroactive law)",
                ok, str(why))
        ok, why = roster.judge(wt(rows=row(1, "nitpick", FIXED)), EDGE, "PASS")
        c.check("C3 · a lane dated ON the cutoff is IN scope", not ok, str(why))

    # ── P · the parser reads the table, and only a table with the two named columns ──────
    if c.block("P · parse reads the findings table by its `sev` and `disposition` columns"):
        d = roster.parse(wt(rows=row(1, "important", FIXED) + row(2, "nitpick", "recorded")))
        rows = d.get("findings")
        c.check("P1 · parse returns the rows, with severity and the disposition word",
                isinstance(rows, list) and len(rows) == 2
                and rows[0].get("sev") == "important" and rows[0].get("word") == "fixed"
                and rows[1].get("sev") == "nitpick" and rows[1].get("word") == "recorded",
                f"got {rows!r}")
        c.check("P2 · the `repro <id>` token and the `pin` are read off the disposition cell",
                bool(rows) and rows[0].get("repro") == "f1" and rows[0].get("pin") is True,
                f"got {rows and rows[0]!r}")
        d = roster.parse(wt(rows=row(1, "important", "fixed @abc · pin t.py:B1", repro="f7"),
                            head=HEAD_REPRO))
        c.check("P3 · a `repro` COLUMN supplies the id when the disposition cell does not",
                d.get("findings") and d["findings"][0].get("repro") == "f7",
                f"got {d.get('findings')!r}")
        d = roster.parse(wt(rows=row(1, "important", HELD)))
        c.check("P4 · the `patch <path>` token is read",
                d.get("findings") and d["findings"][0].get("patch") == "gates/repro/f1.patch",
                f"got {d.get('findings')!r}")
        audit = ("| # | file:line | Severity | Category | Finding | Disposition |\n|---|---|---|---|---|---|\n"
                 "| 1 | y.py:8 | CONCERNS | comment-contract | no provenance | applied |\n")
        ok, why = roster.judge(wt(rows="").replace("Verdict:", audit + "\nVerdict:", 1), POST, "PASS")
        c.check("P5 · the clean-code audit's table (FAIL/CONCERNS severities) raises no refusal",
                ok, f"its rows are not review findings and must not be judged as such: {why}")
        # `.get`, never `[...]`: a missing key must be a FAILED: line the sweep can score, not a
        # traceback it refuses to (the SCC-240 F5 rule).
        c.check("P6 · a walkthrough with no table parses to an empty list, never an exception",
                roster.parse(wt()).get("findings") == [], f"got {roster.parse(wt()).get('findings')!r}")
        c.check("P7 · a header lacking the `disposition` column is not a findings table",
                roster.parse(wt(rows="| a | b |\n", head="| sev | note |\n|---|---|\n")).get("findings") == [],
                "a table that merely mentions severity must not be read as the record")

    # ── S · a `nitpick`/`suggestion` is a count, never a fix ─────────────────────────────
    if c.block("S · a fixed nitpick or suggestion refuses"):
        for sev in ("nitpick", "suggestion"):
            ok, why = roster.judge(wt(rows=row(1, sev, FIXED)), POST, "PASS")
            c.check(f"S1 · a `fixed` {sev} row REFUSES",
                    not ok and sev in " ".join(why) and "recorded" in " ".join(why),
                    f"the policy for a {sev} is nothing at all, a count - twenty cheap fixes is "
                    f"the audit that never ends: {why}")
        ok, why = roster.judge(wt(rows=row(1, "nitpick", "recorded") + row(2, "suggestion", "recorded")),
                               POST, "PASS")
        c.check("S2 · (control) `recorded` nitpicks and suggestions pass", ok, str(why))

    # ── F · a fixed row owes a pin and a receipt that reproduced ─────────────────────────
    if c.block("F · a fixed critical/important owes `pin` and a `repro` receipt on disk"):
        ok, why = roster.judge(wt(rows=row(1, "important", "fixed @abc1234 · repro f1")), POST, "PASS")
        c.check("F1 · a `fixed` row with no `pin` REFUSES and names the pin",
                not ok and "pin" in " ".join(why),
                f"a fix without a test seen red then green is an unreviewed edit: {why}")
        ok, why = roster.judge(wt(rows=row(1, "important", "fixed @abc1234 · pin t.py:B1")), POST, "PASS")
        c.check("F2 · a `fixed` row with no `repro <id>` REFUSES and names the token",
                not ok and "repro <id>" in " ".join(why), str(why))
        with TempDir() as tmp:
            lane = tmp / "_artifacts/_main/2026-09-13_lane"
            lane.mkdir(parents=True)
            page = lane / "walkthrough.md"
            for sev in ("critical", "important"):
                ok, why = roster.judge(wt(rows=row(1, sev, FIXED)), page, "PASS")
                c.check(f"F3 · a `fixed` {sev} whose receipt is ABSENT refuses and NAMES the path",
                        not ok and str(lane / "gates" / "repro" / "f1.json") in " ".join(why),
                        f"the refusal must say where it looked: {why}")
            rc = _receipt(lane, "f1")
            ok, why = roster.judge(wt(rows=row(1, "important", FIXED)), page, "PASS")
            c.check("F4 · (control) receipt present, `reproduced` - the fixed row PASSES",
                    ok, f"receipt at {rc}: {why}")
            ok, why = roster.judge(wt(rows=row(1, "important", "fixed @abc · pin t.py:B1", repro="f1"),
                                      head=HEAD_REPRO), page, "PASS")
            c.check("F4b · (control) the id from a `repro` COLUMN resolves the same receipt",
                    ok, str(why))
            _receipt(lane, "f2", result="not-reproduced")
            ok, why = roster.judge(wt(rows=row(1, "important", FIXED.replace("f1", "f2"))), page, "PASS")
            c.check("F5 · a receipt that says NOT reproduced cannot back a `fixed` row",
                    not ok and "not-reproduced" in " ".join(why),
                    f"a dropped finding is not fixed; a fix of a non-defect is a new unreviewed "
                    f"edit: {why}")
            _receipt(lane, "f3", result="unrunnable")
            ok, why = roster.judge(wt(rows=row(1, "important", FIXED.replace("f1", "f3"))), page, "PASS")
            c.check("F5b · an `unrunnable` receipt cannot back a `fixed` row either",
                    not ok and "unrunnable" in " ".join(why),
                    f"a command that never ran proved nothing: {why}")

    # ── H · a held row owes its receipt AND its written patch ────────────────────────────
    if c.block("H · a held row owes a receipt and a patch on disk"):
        with TempDir() as tmp:
            lane = tmp / "_artifacts/_main/2026-09-13_lane"
            lane.mkdir(parents=True)
            page = lane / "walkthrough.md"
            ok, why = roster.judge(wt("CONCERNS", rows=row(1, "important", HELD)), page, "CONCERNS")
            c.check("H1 · a `held` row whose receipt is absent refuses, naming the path",
                    not ok and "f1.json" in " ".join(why), str(why))
            _receipt(lane, "f1")
            ok, why = roster.judge(wt("CONCERNS", rows=row(1, "important", HELD)), page, "CONCERNS")
            c.check("H2 · a `held` row whose PATCH is absent refuses, naming the path",
                    not ok and "f1.patch" in " ".join(why),
                    f"held means the fix is WRITTEN and only permission is missing: {why}")
            ok, why = roster.judge(wt("CONCERNS", rows=row(1, "important",
                                                         "held — spec-conflict · repro f1")),
                                   page, "CONCERNS")
            c.check("H3 · a `held` row with no `patch <path>` at all refuses",
                    not ok and "patch" in " ".join(why), str(why))
            _patch(lane, "f1")
            ok, why = roster.judge(wt("CONCERNS", rows=row(1, "important", HELD)), page, "CONCERNS")
            c.check("H4 · (control) receipt + patch present: a held important under CONCERNS PASSES",
                    ok, f"this is the authority ground, the designed CONCERNS: {why}")
            repo_rel = HELD.replace("patch gates/repro/f1.patch",
                                    "patch _artifacts/_main/2026-09-13_lane/gates/repro/f1.patch")
            ok, why = roster.judge(wt("CONCERNS", rows=row(1, "important", repo_rel)), page, "CONCERNS")
            c.check("H4b · (control) a REPO-relative patch path (the clickable form) resolves too",
                    ok, str(why))

    # ── V · the floor at the stamp, on the rows still OPEN ──────────────────────────────
    if c.block("V · the verdict must match the open rows"):
        with TempDir() as tmp:
            lane = tmp / "_artifacts/_main/2026-09-13_lane"
            lane.mkdir(parents=True)
            page = lane / "walkthrough.md"
            _receipt(lane, "f1")
            _patch(lane, "f1")
            for v in ("PASS", "CONCERNS"):
                ok, why = roster.judge(wt(v, rows=row(1, "critical", HELD)), page, v)
                c.check(f"V1 · {v} with a HELD critical refuses - an open reproduced critical is FAIL",
                        not ok and "FAIL" in " ".join(why),
                        f"a held critical is still open; the operator's word is what closes it: {why}")
            for v in ("PASS", "CONCERNS"):
                for dispo in ("applied @abc1234", "open", "escalate — to the operator", ""):
                    ok, why = roster.judge(wt(v, rows=row(1, "important", dispo)), page, v)
                    c.check(f"V2 · {v} with an important `{dispo or '(blank)'}` - neither fixed nor "
                            f"held - refuses and says finish the fix",
                            not ok and "finish the fix" in " ".join(why),
                            f"there is no third bucket; the stamp is refused, not softened: {why}")
            ok, why = roster.judge(wt("PASS", rows=row(1, "important", HELD)), page, "PASS")
            c.check("V3 · PASS with a held important refuses - CONCERNS is the consistent verdict",
                    not ok and "CONCERNS" in " ".join(why), str(why))
            ok, why = roster.judge(wt("PASS", rows=row(1, "critical", "dropped — no reproduction")
                                      + row(2, "critical", "out-of-lane — SCC-9 rider")
                                      + row(3, "important", "ruled — approved")
                                      + row(4, "important", FIXED)), page, "PASS")
            c.check("V4 · (control) dropped, out-of-lane, ruled and fixed rows are CLOSED - PASS passes",
                    ok, f"these are the four ways a row closes for THIS lane: {why}")
            ok, why = roster.judge(wt("PASS", rows=row(1, "critical", FIXED)), page, "PASS")
            c.check("V5 · (control) a fixed critical with its receipt supports a PASS", ok, str(why))

    # ── R · one review per lane: a second roster needs the operator's line ──────────────
    if c.block("R · a second roster needs the operator's written word"):
        ok, why = roster.judge(wt(second=ROSTER), POST, "PASS")
        c.check("R1 · two `lenses_run:` rosters with no operator line REFUSE",
                not ok and "roster" in " ".join(why).lower() and "operator" in " ".join(why).lower(),
                f"one review per lane; a re-review converted 1 in 7 and cost a full roster every "
                f"time: {why}")
        ok, why = roster.judge(wt(second=ROSTER,
                                  rereview='re-review: approved by the operator — "run it again"'),
                               POST, "PASS")
        c.check("R2 · (control) with `re-review: approved by the operator — \"<his words>\"` it PASSES",
                ok, str(why))
        ok, why = roster.judge(wt(second=ROSTER, rereview="re-review: approved by the operator"),
                               POST, "PASS")
        c.check("R3 · the line must QUOTE his words - a bare claim of approval is not the word",
                not ok, str(why))
        ok, why = roster.judge(wt(restamp=True), POST, "PASS")
        c.check("R4 · a RE-STAMP section with no roster reads the earlier roster and PASSES",
                ok, f"the re-stamp is the designed second section - verdict, retest, carried "
                    f"review - and it carries no roster on purpose: {why}")
        c.check("R4b · ...and parse counts ONE roster header there",
                roster.parse(wt(restamp=True)).get("roster_headers") == 1,
                f"got {roster.parse(wt(restamp=True)).get('roster_headers')!r}")
        ok, why = roster.judge(wt(fenced_example=True), POST, "PASS")
        c.check("R5 · a FENCED example roster above the real one is not a second roster",
                ok, f"headers are counted on the STRIPPED text, like everything here: {why}")
        c.check("R5b · ...and parse counts one header, not two",
                roster.parse(wt(fenced_example=True)).get("roster_headers") == 1,
                f"got {roster.parse(wt(fenced_example=True)).get('roster_headers')!r}")

    # ── L · SCC-441's own walkthrough is pre-cutoff and UNTOUCHED ───────────────────────
    if c.block("L · the lane that motivated this is legacy to it"):
        text = SCC441.read_text(encoding="utf-8") if SCC441.is_file() else ""
        c.check("L0 · (fixture) SCC-441's walkthrough is on disk with two rosters and `applied` rows",
                text.count("lenses_run:") == 2 and "| applied @" in text, "the fixture moved")
        ok, why = roster.judge(text, SCC441, "CONCERNS")
        blob = " ".join(why).lower()
        c.check("L1 · none of the new refusals fire on it",
                "finish the fix" not in blob and "repro <id>" not in blob and "operator" not in blob
                and "gates/repro" not in blob,
                f"a rule applied retroactively to the lane it was written from: {why}")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
