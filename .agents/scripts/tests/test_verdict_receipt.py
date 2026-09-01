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
import subprocess
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


def git_repo(td: str) -> Path:
    """A REAL git repo. The receipt is now read from the INDEX, so a bare temp dir cannot
    stand in for one — and that is the point: the old fixture wrote receipts to disk and
    never staged them, which is exactly the fail-open the index read closes (review finding)."""
    repo = Path(td)
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", *cmd], cwd=repo, capture_output=True, text=True, check=True)
    return repo


def write_receipt(repo: Path, lane: str, result: str, *, stage: bool = True) -> None:
    gates = repo / lane / "gates"
    gates.mkdir(parents=True, exist_ok=True)
    (gates / "suite.json").write_text(
        json.dumps({"result": result, "exit_code": 0 if result == "pass" else 1,
                    "sha": "deadbeef" * 5, "gate": "suite"}), encoding="utf-8")
    if stage:
        subprocess.run(["git", "add", f"{lane}/gates/suite.json"], cwd=repo,
                       capture_output=True, text=True, check=True)


def main() -> int:
    c = Cases("verdict-receipt — a Verdict stamp is evidence, evidence needs a receipt (SCC-363)")
    lane = "_artifacts/_main/2026-01-01_lane"
    wt = f"{lane}/walkthrough.md"

    if c.block("A · the gate fires on the forgery it was built for"):
        with tempfile.TemporaryDirectory() as td:
            repo = git_repo(td)
            probs = problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo)
            c.check("A1 a PASS stamp with NO receipt is refused (the AVCH-106 shape)",
                    len(probs) == 1 and "does not exist" in probs[0], str(probs))
            probs = problems(diff_for(wt, ["Verdict: CONCERNS @ 0000abcd"]), repo)
            c.check("A2 a CONCERNS stamp is gated exactly like PASS",
                    len(probs) == 1, str(probs))
            write_receipt(repo, lane, "fail")
            probs = problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo)
            c.check("A3 a receipt whose recorded result is `fail` does not carry a PASS "
                    "(result=fail named in the refusal)",
                    len(probs) == 1 and "result=fail" in probs[0], str(probs))
            # The corruption must be STAGED to be seen — the gate reads the index, not the
            # disk. (This case caught its own fixture: writing only to disk left A3's `fail`
            # receipt in the index, and the refusal correctly still said `result=fail`.)
            (repo / lane / "gates" / "suite.json").write_text("{not json", encoding="utf-8")
            subprocess.run(["git", "add", f"{lane}/gates/suite.json"], cwd=repo,
                           capture_output=True, text=True, check=True)
            probs = problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo)
            c.check("A4 an unreadable receipt is a refusal, never a silent pass",
                    len(probs) == 1 and "unreadable" in probs[0], str(probs))
            # ⛔ THE FAIL-OPEN THIS READ CLOSES (review finding): the house bans `git add -A`,
            # so staging the walkthrough alone leaves the receipt untracked on disk. The old
            # `Path.is_file()` check saw it and passed, landing a stamp the commit's own tree
            # cannot evidence.
            subprocess.run(["git", "rm", "--cached", "-q", f"{lane}/gates/suite.json"],
                           cwd=repo, capture_output=True, text=True, check=True)
            write_receipt(repo, lane, "pass", stage=False)
            probs = problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo)
            c.check("A5 a receipt on DISK but NOT STAGED is refused - the commit must carry "
                    "its own evidence",
                    len(probs) == 1 and "NOT STAGED" in probs[0], str(probs))

    if c.block("B · legitimate commits stay quiet (each carve-out pinned)"):
        with tempfile.TemporaryDirectory() as td:
            repo = git_repo(td)
            write_receipt(repo, lane, "pass")
            c.check("B1 a PASS stamp WITH a passing suite receipt is allowed",
                    problems(diff_for(wt, ["Verdict: PASS @ 0000abcd"]), repo) == [])
            c.check("B2 `warn` is a usable result (advisory findings never block a stamp)",
                    (write_receipt(repo, lane, "warn") or
                     problems(diff_for(wt, ["Verdict: CONCERNS @ 0000abcd"]), repo)) == [])
        with tempfile.TemporaryDirectory() as td:
            repo = git_repo(td)  # receiptless on purpose for every case below
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
            # ⛔ REVERSED at review (SCC-363). This asserted the OPPOSITE — that an indented
            # stamp is exempt, "line start or nothing". Measured against the real readers, that
            # was a hole: `walkthrough_roster._CLI_VERDICT_RE` (leading class `[>\-*#\s]*`)
            # FINDS `  Verdict: PASS` and judges it, while `wf.VERDICT_RE` does not — so the
            # exemption let an author write a stamp one gate acts on and this one ignored.
            c.check("B8 an INDENTED stamp is gated too - the roster reader finds it, so a "
                    "leading-whitespace stamp is a hole, never a carve-out",
                    len(problems(diff_for(wt, ["  Verdict: PASS @ x"]), repo)) == 1)
            c.check("B8b a blockquoted/bulleted stamp is gated on the same reasoning",
                    len(problems(diff_for(wt, ["> - **Verdict:** PASS @ x"]), repo)) == 1)

    if c.block("F · the stamp spellings the HOUSE READERS accept (review findings, reproduced)"):
        # ⛔ The gate refused ONE spelling; `closeout_preflight._VERDICT_RE`,
        # `walkthrough_roster._CLI_VERDICT_RE` and jira_feed's copy all accept
        # `^[>\-*#\s]*\**\s*Verdict:` CASE-INSENSITIVELY — closeout's own comment says "humans
        # write **Verdict: PASS** and ## Verdict: CONCERNS". So bolding the line recommitted the
        # very AVCH-106 forgery this gate exists for. Gate what any reader will act on.
        with tempfile.TemporaryDirectory() as td:
            repo = git_repo(td)   # receiptless: every spelling below must be REFUSED
            for label, stamp in [
                ("bare", "Verdict: PASS @ s"),
                ("bold", "**Verdict: PASS @ s**"),
                ("heading", "## Verdict: PASS @ s"),
                ("blockquote", "> Verdict: PASS @ s"),
                ("bullet", "- Verdict: PASS @ s"),
                ("indented", "  Verdict: PASS @ s"),
                ("lowercase", "verdict: pass @ s"),
                ("spaced-colon", "Verdict : PASS @ s"),
            ]:
                c.check(f"F1 {label} stamp is gated ({stamp!r})",
                        len(problems(diff_for(wt, [stamp]), repo)) == 1)
            # And the carve-outs must SURVIVE the widening - a gate that refuses everything is
            # as useless as one that refuses nothing.
            c.check("F2 FAIL is still ungated in every decoration",
                    problems(diff_for(wt, ["**Verdict: FAIL @ s**", "## Verdict: WAIVED @ s"]),
                             repo) == [])
            c.check("F3 the defusal spelling is still not an add",
                    problems(diff_for(wt, ["Superseded stamp (defused): PASS @ old"]), repo) == [])

        # `git commit -v` appends the staged DIFF below a scissors line; git strips it before
        # storing. `[verdict-ok]` is a literal in this repo's own sources, so grepping the raw
        # file gave any `-v` commit touching them a bypass whose token never reached the log.
        SCISSORS = "# ------------------------ >8 ------------------------"
        c.check("F4 a token appearing only in the commit -v DIFF is NOT an opt-out "
                "(the bypass must be in the message git keeps)",
                not has_optout(f"SCC-1 chore: a change\n\n{SCISSORS}\n"
                               f"+OPTOUT = \"{'[verdict-ok]'}\"\n"))
        c.check("F5 ...and a real token in the message still opts out",
                has_optout("SCC-1 chore: a change [verdict-ok]\n"))
        c.check("F6 a token in a stripped COMMENT line is not an opt-out either",
                not has_optout("SCC-1 chore: a change\n# hint: [verdict-ok] bypasses\n"))

        # ⛔ A receipt that PARSES but is not an object used to reach `receipt_defect`, whose
        # `.get` raised AttributeError uncaught. Because `problems()` runs BEFORE both hatches
        # in `main()`, that traceback made the gate impossible to disarm OR bypass: armed,
        # `[verdict-ok]`, and marker-deleted all died the same way (review finding, reproduced).
        for shape in ("[]", '"a string"', "42", "true"):
            with tempfile.TemporaryDirectory() as td:
                repo = git_repo(td)
                (repo / lane / "gates").mkdir(parents=True, exist_ok=True)
                (repo / lane / "gates" / "suite.json").write_text(shape, encoding="utf-8")
                subprocess.run(["git", "add", f"{lane}/gates/suite.json"], cwd=repo,
                               capture_output=True, check=True)
                try:
                    probs = problems(diff_for(wt, ["Verdict: PASS @ s"]), repo)
                    ok = len(probs) == 1 and "unusable" in probs[0]
                    detail = str(probs)
                except Exception as exc:                     # noqa: BLE001 - that IS the defect
                    ok, detail = False, f"raised {type(exc).__name__}: {exc}"
                c.check(f"F7 a receipt that parses to a non-object ({shape}) is REFUSED "
                        "cleanly, never a traceback", ok, detail)

    if c.block("C · the parser and the escape hatch"):
        got = added_gated_stamps(diff_for(wt, ["Verdict: PASS @ x"]) +
                                 diff_for(f"{lane}2/walkthrough.md",
                                          ["Verdict: CONCERNS @ y"]))
        c.check("C1 a multi-file diff attributes each stamp to ITS file",
                got == {wt: ["PASS"], f"{lane}2/walkthrough.md": ["CONCERNS"]}, str(got))
        c.check("C2 the opt-out token is recognized", has_optout("x [verdict-ok] y"))
        c.check("C3 ...and its absence is recognized (the hatch cannot be always-open)",
                not has_optout("a clean message, verdict discussed in prose"))

    if c.block("E · END TO END - the script's own exit code, driven through real git"):
        # ⛔ THE GAP THIS CLOSES (review finding): blocks A-C import three PURE functions and
        # never call `main()`, so everything between "problems() returned a list" and "git
        # refused the commit" was untested — the staged-diff read, the `has_optout`
        # short-circuit, the `armed` branch, and the `return 1` itself. Each of these mutants
        # left the file GREEN: `return 1` -> `return 0`; `armed = ...is_file()` -> `False`;
        # deleting the exec line of the wrapper. A gate built to stop unproven claims cannot
        # itself rest on one.
        script = SCRIPTS / "verdict_receipt.py"

        def run_gate(repo: Path, message: str) -> int:
            msg = repo / "MSG"
            msg.write_text(message, encoding="utf-8")
            return subprocess.run([sys.executable, str(script), "--repo", str(repo),
                                   "--message-file", str(msg)],
                                  capture_output=True, text=True).returncode

        with tempfile.TemporaryDirectory() as td:
            repo = git_repo(td)
            (repo / ".agents" / "scripts" / "git-hooks").mkdir(parents=True, exist_ok=True)
            (repo / ".agents" / "scripts" / "git-hooks" / "VERDICT-ENFORCE").write_text(
                "armed\n", encoding="utf-8")
            (repo / lane).mkdir(parents=True, exist_ok=True)
            (repo / wt).write_text("# w\n\nVerdict: PASS @ 0000abcd\n", encoding="utf-8")
            subprocess.run(["git", "add", wt], cwd=repo, capture_output=True, check=True)

            c.check("E1 ARMED + stamp + no receipt -> the script EXITS 1 (the refusal path "
                    "runs; `return 1`->`return 0` dies here)",
                    run_gate(repo, "SCC-1 chore: stamp it") == 1)
            c.check("E2 ...and the opt-out token turns that same commit into exit 0",
                    run_gate(repo, "SCC-1 chore: stamp it [verdict-ok]") == 0)

            (repo / ".agents" / "scripts" / "git-hooks" / "VERDICT-ENFORCE").unlink()
            c.check("E3 DISARMED (marker deleted) is warn-only -> exit 0 (pins the `armed` "
                    "branch, which `armed = False` would otherwise fake)",
                    run_gate(repo, "SCC-1 chore: stamp it") == 0)

            (repo / ".agents" / "scripts" / "git-hooks" / "VERDICT-ENFORCE").write_text(
                "armed\n", encoding="utf-8")
            write_receipt(repo, lane, "pass")
            c.check("E4 a real staged receipt lets the same armed commit through (exit 0)",
                    run_gate(repo, "SCC-1 chore: stamp it") == 0)

            # The staged-diff read itself: a config that changes git's path prefix must not
            # blind the gate. `diff.noprefix` produces `+++ path` and `mnemonicPrefix` `+++ i/path`,
            # either of which made the old FILE_RE match nothing and pass in SILENCE.
            subprocess.run(["git", "rm", "--cached", "-q", f"{lane}/gates/suite.json"],
                           cwd=repo, capture_output=True, check=True)
            for key in ("diff.noprefix", "diff.mnemonicPrefix"):
                subprocess.run(["git", "config", key, "true"], cwd=repo,
                               capture_output=True, check=True)
                c.check(f"E5 {key}=true still REFUSES (the gate pins its own diff config; "
                        "without that it failed open silently)",
                        run_gate(repo, "SCC-1 chore: stamp it") == 1)
                subprocess.run(["git", "config", "--unset", key], cwd=repo,
                               capture_output=True, check=True)

    if c.block("G · the SHELL SEAM runs (verdict-receipt.sh had zero execution coverage)"):
        # ⛔ 49 lines of real logic — the DISABLE kill switch, the python3->python->py probe,
        # the MERGE_HEAD/rebase carve-outs, the subject carve-outs and the exec — and NOTHING
        # ran it: replacing the final `exec` with `exit 0` left the whole suite 68/68 green
        # (review finding, executed). These cases drive the wrapper itself, as a real hook.
        import shutil
        wrapper_src = SCRIPTS / "git-hooks" / "verdict-receipt.sh"

        def seam(repo: Path, message: str) -> int:
            msg = repo / "MSG"
            msg.write_text(message, encoding="utf-8")
            return subprocess.run(["sh", str(repo / ".agents/scripts/git-hooks/verdict-receipt.sh"),
                                   str(msg)], cwd=repo, capture_output=True, text=True).returncode

        with tempfile.TemporaryDirectory() as td:
            repo = git_repo(td)
            (repo / ".agents" / "scripts" / "git-hooks").mkdir(parents=True, exist_ok=True)
            # Copy the whole scripts dir (minus tests): gate_receipt has its own imports, and
            # a partial copy fails at import time - which LOOKS like the gate refusing.
            shutil.copytree(SCRIPTS, repo / ".agents" / "scripts", dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("tests", "__pycache__"))
            shutil.copy2(wrapper_src, repo / ".agents/scripts/git-hooks/verdict-receipt.sh")
            (repo / ".agents/scripts/git-hooks/VERDICT-ENFORCE").write_text("armed\n",
                                                                            encoding="utf-8")
            (repo / lane).mkdir(parents=True, exist_ok=True)
            (repo / wt).write_text("# w\n\nVerdict: PASS @ 0000abcd\n", encoding="utf-8")
            subprocess.run(["git", "add", wt], cwd=repo, capture_output=True, check=True)

            c.check("G1 the wrapper REFUSES a receiptless stamp (exit 1) - the `exec` line is "
                    "reached, so replacing it with `exit 0` dies here",
                    seam(repo, "SCC-1 chore: stamp it") == 1)
            c.check("G2 ...and honours the opt-out token through the wrapper",
                    seam(repo, "SCC-1 chore: stamp it [verdict-ok]") == 0)
            # ⛔ 'Merge '* was REMOVED from the subject carve-outs at review: every real merge
            # sets MERGE_HEAD (already carved out by state), so the text case only added an
            # escape anyone could type. This pins that it is gone.
            c.check("G3 a subject merely BEGINNING 'Merge ' does NOT skip the gate "
                    "(the state check is the merge carve-out, not the text)",
                    seam(repo, "Merge the review sections into the walkthrough") == 1)
            (repo / ".git" / "MERGE_HEAD").write_text("0" * 40 + "\n", encoding="utf-8")
            c.check("G4 a real merge IS carved out (MERGE_HEAD present)",
                    seam(repo, "Merge branch 'x'") == 0)
            (repo / ".git" / "MERGE_HEAD").unlink()
            c.check("G5 the fixup!/squash!/Revert carve-outs still hold",
                    seam(repo, 'fixup! SCC-1 chore: stamp it') == 0
                    and seam(repo, 'Revert "SCC-1 chore: stamp it"') == 0)
            (repo / ".agents/scripts/git-hooks/DISABLE").write_text("", encoding="utf-8")
            c.check("G6 the DISABLE kill switch stops the seam dead",
                    seam(repo, "SCC-1 chore: stamp it") == 0)
            (repo / ".agents/scripts/git-hooks/DISABLE").unlink()
            c.check("G7 removing DISABLE re-arms it (the switch is not one-way)",
                    seam(repo, "SCC-1 chore: stamp it") == 1)

    if c.block("D · the live tree arms the gate"):
        # ⛔ COMMENT-STRIPPED, and that is the whole point (review finding, executed): this row
        # used to grep the raw file for "verdict-receipt.sh" — which the HEADER COMMENT at the
        # top of commit-msg also contains. Deleting the entire dispatch block and leaving the
        # comment kept this check, and all 68 suite files, green while the gate never ran. The
        # house memory `comment-literals-invert-source-grep-tests` names this exact shape, and
        # `test_zoo_team.py` block C already strips comments for the .ps1 for the same reason.
        hook_raw = (SCRIPTS.parents[1] / ".githooks" / "commit-msg").read_text(encoding="utf-8")
        hook_code = "\n".join(l for l in hook_raw.splitlines()
                              if not l.lstrip().startswith("#"))
        c.check("D0 the comment-strip actually strips (a check that cannot fail proves nothing)",
                "verdict-receipt.sh" in hook_raw
                and "5. verdict" not in hook_code)
        c.check("D1 the wrapper is EXEC'd from .githooks/commit-msg (code, not the comment)",
                'exec "$VERDICT"' in hook_code and "verdict-receipt.sh" in hook_code,
                "the dispatch block is gone from the executable half of the hook")
        c.check("D2 the VERDICT-ENFORCE marker ships ARMED",
                (SCRIPTS / "git-hooks" / "VERDICT-ENFORCE").is_file())
        # The marker NAME is load-bearing and is declared in two places that must agree — a
        # rename in one leaves the gate permanently warn-only (review finding F3).
        import verdict_receipt as _vr
        c.check("D3 the MARKER main() reads is the file that actually ships",
                (SCRIPTS.parents[1] / _vr.MARKER).is_file(), f"MARKER={_vr.MARKER}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
