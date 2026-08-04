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

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
