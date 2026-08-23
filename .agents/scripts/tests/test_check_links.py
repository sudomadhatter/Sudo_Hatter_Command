"""SCC-285 · `check_links.py` — the seven conventions, each pinned by the false positive it caused.

⛔ WHY EVERY CASE HERE IS A SCAR, NOT A GUESS.

`check_links.py` exists because `/smh-clean-code-audit`'s "Link + anchor" row was PROSE — the only
row on the machine floor with no command. Agents improvised a matcher, and the improvisation
reported **31 unresolved paths of which ~30 were false**.

Writing the real checker reproduced that failure three more times before it settled:

    draft 1  ->  31 false      (short citations unknown)
    draft 2  -> 168 false      (`lstrip("./")` ate the dot off every `.agents/...` path)
    draft 3  ->  18 false      (project-relative paths, narrative ledgers)
    draft 4  ->   5, all real  -> 0 after the docs were corrected

Every row below is one of those drafts' false positives, frozen so it cannot come back. A checker
that cries wolf is worse than no checker: it teaches the reader to skip the one real hit.

⛔ AND IT MUST STILL BITE. Block E is the other half — `tests-must-gate-for-real` §5: prove a check
both REJECTS and ALLOWS, or it is not a gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _harness import Cases, TempDir
import check_links as CL

# A synthetic tracked set. Deliberately NOT the live tree: a test that reads whatever the repo
# contains today passes or fails for reasons unrelated to the code under test.
TRACKED = {
    ".agents/rules/git-policy.md",
    ".agents/rules/jira.md",
    ".agents/scripts/INDEX.md",
    ".agents/scripts/tests/test_twin_parity.py",
    ".agents/scripts/check_links.py",
    "docs/_scc_sops_prds/workflows_testing_SOP.md",
    "_artifacts/_main/INDEX.md",
    "README.md",
}


def resolver(tmp: Path, main: Path | None = None) -> CL.Resolver:
    return CL.Resolver(tmp, main, tracked=set(TRACKED))


def main() -> int:
    c = Cases("check_links: the seven conventions, and it can still fail")


    with TempDir() as tmp:
        r = resolver(tmp)

        if c.block("A · the resolver is populated (anti-vacuity)"):
            _ok = bool(r.tracked)
            c.check("A1 the tracked set is non-empty", _ok,
                    "" if _ok else "an empty tracked set resolves nothing and every row below passes vacuously")
            _ok = len(r.by_suffix) > len(r.tracked)
            c.check("A2 the suffix index was built", _ok,
                    "" if _ok else "by_suffix is not indexing tails - convention 1 cannot work")

        if c.block("B · the SEVEN conventions each resolve (the false positives, frozen)"):
            _ok = (r.resolve("tests/test_twin_parity.py", "docs/x.md") == ".agents/scripts/tests/test_twin_parity.py")
            c.check("B1 convention 1 - a SHORT citation resolves to the real path", _ok,
                    "" if _ok else "docs cite a tail; draft 1 called 30 live files dead over this")
            _ok = (r.resolve("../../.agents/rules/jira.md", "docs/_scc_sops_prds/SOP.md") == ".agents/rules/jira.md")
            c.check("B2 convention 2 - a RELATIVE ../.. link resolves from the citing file", _ok,
                    "" if _ok else "`..` is not being normalised against the citing directory")
            # ⛔ THE lstrip TRAP. `".agents/x".lstrip("./")` -> `"agents/x"`, because lstrip takes a
            # character SET. It turned every house rule into a dead link in draft 2 (168 findings),
            # and `sop_currency.py:_norm` already carried a comment warning about it.
            _ok = CL._strip_dot_slash(".agents/rules/git-policy.md") == ".agents/rules/git-policy.md"
            c.check("B3 convention 2b - a leading dot is NOT eaten (the lstrip trap)", _ok,
                    "" if _ok else "lstrip('./') ate the leading dot - every .agents/ path reads as dead")
            _ok = CL._strip_dot_slash("./README.md") == "README.md"
            c.check("B3b `./` IS still stripped", _ok,
                    "" if _ok else "the leading ./ is not being removed")
            _ok = r.resolve(".agents/scripts/check_links.py", "docs/x.md") is not None
            c.check("B4 convention 3 - a file this BRANCH added resolves", _ok,
                    "" if _ok else "resolving against main's index makes every file the lane added read as dead")
            (tmp / "gitignored").mkdir()
            (tmp / "gitignored" / "asset.md").write_text("x", encoding="utf-8")
            _ok = resolver(tmp).resolve("gitignored/asset.md", "docs/x.md") is not None
            c.check("B5 convention 4 - an untracked file that EXISTS still resolves", _ok,
                    "" if _ok else "a gitignored asset present on disk is being called dead")
            _ok = bool(CL.URL.match("https://example.com/x.md"))
            c.check("B6 convention 5a - a URL is not a path claim", _ok,
                    "" if _ok else "URLs are being resolved as paths")
            _ok = (bool(CL.PLACEHOLDER.search("path/to/file.md")) and bool(CL.PLACEHOLDER.search("_artifacts/<KEY>/plan.md")))
            c.check("B7 convention 5b - a placeholder is not a path claim", _ok,
                    "" if _ok else "placeholders are being resolved as real paths")
            _ok = "dead/example.md" not in CL.strip_fences("before\n```\ndead/example.md\n```\nafter")
            c.check("B8 convention 5c - a fenced example is stripped before scanning", _ok,
                    "" if _ok else "fenced illustrations are being read as claims")
            _ok = r.resolve(".agents/rules/", "README.md") is not None
            c.check("B9 convention 5d - a DIRECTORY resolves", _ok,
                    "" if _ok else "a directory link is being reported dead")
            _ok = "backend/requirements.txt".startswith(CL.PROJECT_ROOTS)
            c.check("B10 convention 6 - a child-project path is not this repo's to resolve", _ok,
                    "" if _ok else "cicd-* commands cite the target project's tree; those are not lobby paths")
            _ok = "_artifacts/_main/INDEX.md".endswith(CL.NARRATIVE_LEDGERS)
            c.check("B11 convention 7 - the narrative ledgers are declared", _ok,
                    "" if _ok else "a ledger row naming a deleted file is history, not a broken link")
            # The continuity brief is one too, and `check_maps.py` is the authority: it carries
            # `PRUNE_KEEP_BLOCKS = 10`, so the house already models this file as a dated log whose
            # old end is PRUNED. A path in a five-week-old block is a mention; the fix is the prune.
            _ok = "_artifacts/_main/active-context.md".endswith(CL.NARRATIVE_LEDGERS)
            c.check("B12 convention 7b - the CONTINUITY BRIEF is a ledger (check_maps prunes it)", _ok,
                    "" if _ok else "11 dead paths in 2026-07 session blocks report as this lane's defects")
            _ok = not "_artifacts/_main/2026-08-22_lane/walkthrough.md".endswith(CL.NARRATIVE_LEDGERS)
            c.check("B12b ...and a WALKTHROUGH is not one - the exemption stays narrow", _ok,
                    "" if _ok else "exempting story artifacts would blind the checker to the live tree")

        if c.block("E · ⛔ IT MUST STILL BITE - REJECTS as well as ALLOWS"):
            _ok = r.resolve("docs/this_file_does_not_exist.md", "README.md") is None
            c.check("E1 a genuinely dead path IS reported", _ok,
                    "" if _ok else "the checker resolves everything - it can never fail, so it is not a gate")
            _ok = r.resolve(".agents/rules/no_such_rule.md", "README.md") is None
            c.check("E2 a dead path with a REAL first segment is reported", _ok,
                    "" if _ok else "a plausible-looking dead path slips through")
            _ok = r.resolve("tests/test_nothing_here.py", "README.md") is None
            c.check("E3 a suffix that matches NOTHING is reported", _ok,
                    "" if _ok else "the suffix index is matching too loosely")
            # The end-to-end path, not just the resolver: scan() must actually emit the finding.
            (tmp / "doc.md").write_text("see [x](docs/nope.md) and `.agents/rules/git-policy.md`\n",
                                        encoding="utf-8")
            dead, anchors, checked = CL.scan(tmp, resolver(tmp), ["doc.md"])
            _ok = len(dead) == 1 and "docs/nope.md" in dead[0] and checked == 2
            c.check("E4 scan() reports the dead one and not the live one", _ok,
                    "" if _ok else f"scan is not discriminating: dead={dead} checked={checked}")

        if c.block("F · anchors - `#L` must name lines the target has"):
            (tmp / "five.md").write_text("1\n2\n3\n4\n5\n", encoding="utf-8")
            _ok = CL.check_anchor(tmp, "five.md", "#L2-L4") is None
            c.check("F1 an in-range anchor is accepted", _ok,
                    "" if _ok else "a valid anchor is rejected")
            _ok = CL.check_anchor(tmp, "five.md", "#L9") is not None
            c.check("F2 an anchor past the end is REPORTED", _ok,
                    "" if _ok else "an anchor naming a line the file does not have passes")
            _ok = CL.check_anchor(tmp, "five.md", "#L4-L2") is not None
            c.check("F3 a reversed range is REPORTED", _ok,
                    "" if _ok else "an end-before-start range passes")
            _ok = CL.check_anchor(tmp, "five.md", "#some-heading") is None
            c.check("F4 a non-line anchor is ignored, not guessed at", _ok,
                    "" if _ok else "a markdown heading anchor is being treated as a line range")

        if c.block("G · an EMPTY input is not a pass"):
            # `tests-must-gate-for-real` §5 - a check whose empty input reads as a pass is worse
            # than no check. scan() over no files must report zero CHECKED, never zero DEAD.
            dead, anchors, checked = CL.scan(tmp, resolver(tmp), [])
            _ok = checked == 0 and not dead
            c.check("G1 an empty file list checks nothing and finds nothing", _ok,
                    "" if _ok else f"checked={checked} dead={dead}")
            (tmp / "empty.md").write_text("", encoding="utf-8")
            dead, _, checked = CL.scan(tmp, resolver(tmp), ["empty.md"])
            _ok = checked == 0 and not dead
            c.check("G2 an empty document yields no claims", _ok,
                    "" if _ok else "an empty document is producing findings")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
