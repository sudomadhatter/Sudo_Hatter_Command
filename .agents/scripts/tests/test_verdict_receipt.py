"""The verdict-receipt gate — a stamped verdict needs evidence the suite ran (SCC-363).

The defect this gate closes, measured live: AVCH-106's walkthrough carried `Verdict: PASS`
committed over a RED standing suite. The stamp was prose; nothing linked it to a suite run.
This file proves the gate fires on that forgery and stays quiet on legitimate commits —
mutants first, per the house law (a validator that has never flagged a mutant proves nothing
by staying quiet on the live tree).

What is deliberately NOT gated, each pinned below so a "helpful" tightening fails loudly:
FAIL stamps (recording a failure must never need a green suite), WAIVED (the operator's
act, existing precisely when gates are not green), non-walkthrough files, and hunks that
merely carry a stamp as context rather than ADDING one.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from _harness import SCRIPTS, Cases

sys.path.insert(0, str(SCRIPTS))
from verdict_receipt import added_gated_stamps, has_optout, problems  # noqa: E402


def diff_for(path: str, added: list[str], context: list[str] | None = None) -> str:
    lines = [f"diff --git a/{path} b/{path}", f"--- a/{path}", f"+++ b/{path}",
             "@@ -1,0 +1,9 @@"]
    for c in context or []:
        lines.append(f" {c}")
    for a in added:
        lines.append(f"+{a}")
    return "\n".join(lines) + "\n"


def write_receipt(repo: Path, lane: str, result: str) -> None:
    gates = repo / lane / "gates"
    gates.mkdir(parents=True, exist_ok=True)
    (gates / "suite.json").write_text(
        json.dumps({"result": result, "exit_code": 0 if result == "pass" else 1,
                    "sha": "deadbeef" * 5, "gate": "suite"}), encoding="utf-8")


def main() -> int:
    c = Cases("verdict-receipt — a Verdict stamp is evidence, evidence needs a receipt (SCC-363)")
    lane = "_artifacts/_main/2026-01-01_lane"
    wt = f"{lane}/walkthrough.md"

    if c.block("A · the gate fires on the forgery it was built for"):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            probs = problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo)
            c.check("A1 a PASS stamp with NO receipt is refused (the AVCH-106 shape)",
                    len(probs) == 1 and "NO suite receipt" in probs[0], str(probs))
            probs = problems(diff_for(wt, ["Verdict: CONCERNS @ 0000abcd"]), repo)
            c.check("A2 a CONCERNS stamp is gated exactly like PASS",
                    len(probs) == 1, str(probs))
            write_receipt(repo, lane, "fail")
            probs = problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo)
            c.check("A3 a receipt whose recorded result is `fail` does not carry a PASS "
                    "(result=fail named in the refusal)",
                    len(probs) == 1 and "result=fail" in probs[0], str(probs))
            (repo / lane / "gates" / "suite.json").write_text("{not json", encoding="utf-8")
            probs = problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo)
            c.check("A4 an unreadable receipt is a refusal, never a silent pass",
                    len(probs) == 1 and "unreadable" in probs[0], str(probs))

    if c.block("B · legitimate commits stay quiet (each carve-out pinned)"):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            write_receipt(repo, lane, "pass")
            c.check("B1 a PASS stamp WITH a passing suite receipt is allowed",
                    problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo) == [])
            c.check("B2 `warn` is a usable result (advisory findings never block a stamp)",
                    (write_receipt(repo, lane, "warn") or
                     problems(diff_for(wt, ["Verdict: CONCERNS @ 0000abcd"]), repo)) == [])
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)  # receiptless on purpose for every case below
            c.check("B3 a FAIL stamp needs no receipt (recording a failure is never gated)",
                    problems(diff_for(wt, ["Verdict: FAIL @ 0000abcd"]), repo) == [])
            c.check("B4 a WAIVED stamp needs no receipt (the operator's act)",
                    problems(diff_for(wt, ["Verdict: WAIVED @ 0000abcd"]), repo) == [])
            c.check("B5 a stamp added to a NON-walkthrough file is not this gate's business",
                    problems(diff_for(f"{lane}/notes.md", ["Verdict: PASS @ x"]), repo) == [])
            c.check("B6 a stamp present only as CONTEXT (not added) is ignored",
                    problems(diff_for(wt, ["some added prose"],
                                      context=["Verdict: PASS @ old"]), repo) == [])
            c.check("B7 a defused stamp (`Superseded stamp...`) is not a Verdict add",
                    problems(diff_for(wt, ["Superseded stamp (defused): PASS @ old"]),
                             repo) == [])
            c.check("B8 an indented stamp is not the machine-read line (unfenced law: "
                    "line start or nothing)",
                    problems(diff_for(wt, ["  Verdict: PASS @ x"]), repo) == [])

    if c.block("C · the parser and the escape hatch"):
        got = added_gated_stamps(diff_for(wt, ["Verdict: PASS @ x"]) +
                                 diff_for(f"{lane}2/walkthrough.md",
                                          ["Verdict: CONCERNS @ y"]))
        c.check("C1 a multi-file diff attributes each stamp to ITS file",
                got == {wt: ["PASS"], f"{lane}2/walkthrough.md": ["CONCERNS"]}, str(got))
        c.check("C2 the opt-out token is recognized", has_optout("x [verdict-ok] y"))
        c.check("C3 ...and its absence is recognized (the hatch cannot be always-open)",
                not has_optout("a clean message, verdict discussed in prose"))

    if c.block("D · the live tree arms the gate"):
        c.check("D1 the wrapper is dispatched from .githooks/commit-msg",
                "verdict-receipt.sh" in
                (SCRIPTS.parents[1] / ".githooks" / "commit-msg").read_text(encoding="utf-8"))
        c.check("D2 the VERDICT-ENFORCE marker ships ARMED",
                (SCRIPTS / "git-hooks" / "VERDICT-ENFORCE").is_file())

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
