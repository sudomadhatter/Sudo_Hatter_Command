"""closeout_preflight: the verdict reader, plus the three ways it silently lied.

Every case below the reader section exists because the shipped script got it wrong and the
self-audit of 2026-08-03 caught it by RUNNING the script against the real tree rather than
reading it. The shape worth remembering: a checker that cannot fire, or that fires on
correctly-closed history, is worse than no checker - it gets muted, and then nothing is
checked at all.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

import closeout_preflight as cp   # noqa: E402
import wf_common as wf            # noqa: E402

POSITIVE = [
    ("canonical",          "Verdict: PASS @ 64098847",           "PASS", "64098847"),
    ("bold (21.8b's own)", "**Verdict: PASS** - detail in ...",  "PASS", None),
    ("bold value",         "Verdict: **CONCERNS** @ abc1234",    "CONCERNS", "abc1234"),
    ("heading",            "## Verdict: WAIVED @ deadbee",       "WAIVED", "deadbee"),
    ("list item",          "- Verdict: FAIL @ 1234567",          "FAIL", "1234567"),
    ("blockquote + code",  "> **Verdict:** PASS @ `9f8e7d6c`",   "PASS", "9f8e7d6c"),
    ("lowercase",          "verdict: pass @ 64098847",           "PASS", "64098847"),
]
NEGATIVE = [
    ("prose mention", "Full table in the verdict file."),
    ("no verdict", "## Code Review\n\nEverything looked fine.\n"),
    ("unknown word", "Verdict: MAYBE @ 64098847"),
]

BOARD_REL = Path("_bmad-output/implementation-artifacts/sprint-status.yaml")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def build(root: Path) -> Path:
    """Two sibling stories whose ids are prefixes of one another - the collision case -
    plus one story closed under the pre-08-02 standalone-verdict scheme."""
    repo = root / "repo"
    (repo / BOARD_REL.parent).mkdir(parents=True)
    (repo / BOARD_REL).write_text(
        "development_status:\n"
        "  21-8-master-demo: done\n"
        "  21-8b-quarantine: review\n"
        "  17-2-legacy: done\n", encoding="utf-8")

    stories = repo / "_bmad/bmm/stories"
    stories.mkdir(parents=True)
    (stories / "story-21.8b-quarantine.md").write_text(
        "# Story\nStatus: review\n\n### File List\n"
        "- backend/real_file.py\n- backend/ghost_file.py\n", encoding="utf-8")
    (stories / "story-21.8-master-demo.md").write_text(
        "# Story\nStatus: done\n", encoding="utf-8")
    (stories / "story-17.2-legacy.md").write_text(
        "# Story\nStatus: done\n", encoding="utf-8")

    art = repo / "_artifacts/epic_21/story-21-8b-quarantine"
    art.mkdir(parents=True)
    (art / "walkthrough.md").write_text("## Code Review\n\n**Verdict: PASS**\n",
                                        encoding="utf-8")

    legacy = repo / "_bmad-output/implementation-artifacts"
    # SCC-63: the historical files carry the RETIRED `sudo-` prefix and were never
    # renamed (they live in project trees, not the lobby). The fallback must still
    # find them, so the fixture keeps the old name on purpose.
    (legacy / "sudo-code-review-17.2.md").write_text("# Review\nVerdict: PASS\n",
                                                     encoding="utf-8")
    (repo / "backend").mkdir()
    (repo / "backend/real_file.py").write_text("x = 1\n", encoding="utf-8")

    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "seed")
    return repo


def sections(rep: wf.Report, section: str) -> list[tuple[str, str]]:
    return [(i["sev"], i["msg"]) for i in rep.items if i["section"] == section]


def main() -> int:
    c = Cases("closeout_preflight")

    for name, line, want_v, want_sha in POSITIVE:
        m = cp._VERDICT_RE.search(line)
        got_v = m.group(1).upper() if m else None
        got_sha = m.group(2) if m else None
        c.check(f"verdict/{name}", got_v == want_v and got_sha == want_sha,
                f"verdict={got_v} sha={got_sha}")
    for name, text in NEGATIVE:
        m = cp._VERDICT_RE.search(text)
        c.check(f"verdict/negative/{name}", m is None,
                f"matched={m.group(0) if m else None}")

    # ── F4: a sibling's artifacts must not answer for this story ──────────────
    c.check("slug/exact", wf.slug_matches("21-8b", "21-8b"), "")
    c.check("slug/21-8 does NOT match 21-8b (sibling collision)",
            not wf.slug_matches("21-8", "21-8b"), "")
    c.check("slug/an id still matches its full key",
            wf.slug_matches("21-8b", "21-8b-demo-data-quarantine"), "")
    c.check("story_id strips the descriptive tail",
            wf.story_id("21-8b-demo-data-quarantine") == "21-8b",
            wf.story_id("21-8b-demo-data-quarantine"))

    with TempDir() as tmp:
        repo = build(tmp)

        rep = wf.Report()
        cp.check_artifacts(repo, "21-8-master-demo", rep)
        msgs = " | ".join(m for _, m in sections(rep, "artifacts"))
        c.check("F4 story 21.8 does not read 21.8b's walkthrough",
                "quarantine" not in msgs, msgs[:90])

        rep = wf.Report()
        cp.check_artifacts(repo, "21-8b-quarantine", rep)
        c.check("F4 its own walkthrough still resolves",
                "INFO" in [s for s, _ in sections(rep, "artifacts")],
                str(sections(rep, "artifacts"))[:90])

        # ── F2: history closed under the old scheme is not "unreviewed" ───────
        rep = wf.Report()
        cp.check_artifacts(repo, "17-2-legacy", rep)
        found = sections(rep, "artifacts")
        c.check("F2 pre-08-02 story falls back to the standalone verdict file",
                bool(found) and all(s != "ERROR" for s, _ in found)
                and any("legacy" in m or "pre-08-02" in m for _, m in found),
                str(found)[:110])

        # SCC-63: the fallback globs BOTH prefixes. The fixture above is the RETIRED
        # `sudo-` name (real history, never renamed); this proves the new one resolves
        # too, and that a sweep collapsing the pair to one prefix is caught.
        c.check("SCC-63 the retired sudo- artifact name still resolves",
                cp.legacy_verdict(repo, "17-2-legacy") is not None,
                "back-compat glob lost the sudo- prefix - every historic story goes red")
        newname = repo / "_bmad-output/implementation-artifacts/cicd-code-review-19.9.md"
        newname.write_text("# Review\nVerdict: PASS\n", encoding="utf-8")
        c.check("SCC-63 the cicd- artifact name resolves as well",
                cp.legacy_verdict(repo, "19-9") is not None,
                "back-compat glob lost the cicd- prefix")
        newname.unlink()

        rep = wf.Report()
        cp.check_artifacts(repo, "21-8-master-demo", rep)
        c.check("F2 the fallback does not paper over a genuinely unreviewed story",
                any(s == "ERROR" for s, _ in sections(rep, "artifacts")),
                str(sections(rep, "artifacts"))[:90])

        # ── F3: "could not check" must never print like "checked, clean" ──────
        rep = wf.Report()
        cp.check_landed(repo, "21-8b-quarantine", rep)
        landed = sections(rep, "landed")
        c.check("F3 no id-bearing branch -> WARN, not a silent INFO",
                bool(landed) and landed[0][0] == "WARN" and "NOT verified" in landed[0][1],
                str(landed)[:110])

        git(repo, "branch", "story/21-8b-quarantine")
        rep = wf.Report()
        cp.check_landed(repo, "21-8b-quarantine", rep)
        c.check("F3 an id-bearing branch IS found",
                any("story/21-8b-quarantine" in m for _, m in sections(rep, "landed")),
                str(sections(rep, "landed"))[:110])

        rep = wf.Report()
        cp.check_landed(repo, "21-8b-quarantine", rep, "no-such-branch")
        c.check("F3 --branch overrides the search",
                any("no-such-branch" in m for _, m in sections(rep, "landed")),
                str(sections(rep, "landed"))[:110])

        # ── F6: the File List is a claim, and claims get checked ──────────────
        rep = wf.Report()
        cp.check_file_list(repo, "21-8b-quarantine", rep)
        fl = sections(rep, "file-list")
        c.check("F6 a real tracked file verifies",
                any(s == "INFO" and "1/2" in m for s, m in fl), str(fl)[:110])
        c.check("F6 a claimed-but-absent file is an ERROR",
                any(s == "ERROR" and "ghost_file" in m for s, m in fl), str(fl)[:110])

        rep = wf.Report()
        cp.check_file_list(repo, "21-8-master-demo", rep)
        c.check("F6 a story with no File List warns rather than passing",
                any(s == "WARN" for s, _ in sections(rep, "file-list")),
                str(sections(rep, "file-list"))[:110])

    # ── wf.same_tree — the predicate two commands trust to SKIP a 25-file gate (SCC-156 #9)
    # `/smh-quick-dev` 4b and `/smh-code-review` accept a receipt across an absorb when
    # `same_tree(receipt_sha, HEAD)` says the trees are byte-identical. It was untested while
    # authorizing that skip. Three states, measured on a real repo: a merge commit with an
    # IDENTICAL tree (the case SHA-equality gets wrong) -> True; a real content change ->
    # False; an unknown sha -> None (unknown is never "same").
    with TempDir() as tmp:
        d = tmp / "st"
        d.mkdir()
        git(d, "init", "-q", "-b", "main")
        git(d, "config", "user.email", "t@t.t")
        git(d, "config", "user.name", "t")
        (d / "a.txt").write_text("a\n", encoding="utf-8")
        git(d, "add", "a.txt")
        git(d, "commit", "-qm", "one")
        base = git(d, "rev-parse", "HEAD").stdout.strip()
        # A REAL merge commit whose tree equals the base: the lane changes a.txt and changes it
        # back (two commits, net no-op), then lands --no-ff on main. Two parents, new sha,
        # byte-identical tree - exactly the shape SHA-equality calls stale (review: an empty
        # commit had stood in for it, which is a weaker case than the one the docstring names).
        git(d, "checkout", "-qb", "noop")
        (d / "a.txt").write_text("tmp\n", encoding="utf-8")
        git(d, "commit", "-qam", "touch")
        (d / "a.txt").write_text("a\n", encoding="utf-8")
        git(d, "commit", "-qam", "untouch")
        git(d, "checkout", "-q", "main")
        git(d, "merge", "--no-ff", "-q", "-m", "merge noop", "noop")
        merged = git(d, "rev-parse", "HEAD").stdout.strip()
        parents = git(d, "rev-list", "--parents", "-n", "1", "HEAD").stdout.split()
        c.check("same_tree · a MERGE commit (2 parents) with an IDENTICAL tree is True (sha-equality would say stale)",
                base != merged and len(parents) == 3 and wf.same_tree(d, base, merged) is True,
                f"{base[:7]} vs {merged[:7]} parents={len(parents) - 1}")
        empty = merged
        (d / "a.txt").write_text("b\n", encoding="utf-8")
        git(d, "commit", "-qam", "change")
        changed = git(d, "rev-parse", "HEAD").stdout.strip()
        c.check("same_tree · a content change is False",
                wf.same_tree(d, base, changed) is False, f"{base[:7]} vs {changed[:7]}")
        c.check("same_tree · an unknown sha is None, never True (unknown is not 'same')",
                wf.same_tree(d, base, "0" * 40) is None
                and wf.same_tree(d, "deadbeef" * 5, empty) is None, "")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
