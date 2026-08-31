"""closeout_preflight: the verdict reader, plus the three ways it silently lied.

Every case below the reader section exists because the shipped script got it wrong and the
self-audit of 2026-08-03 caught it by RUNNING the script against the real tree rather than
reading it. The shape worth remembering: a checker that cannot fire, or that fires on
correctly-closed history, is worse than no checker - it gets muted, and then nothing is
checked at all.
"""
from __future__ import annotations

import re
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


# ── SCC-210 · driving the script FROM OUTSIDE, and the fixture that lets it speak ────
#
# Everything the three blocks at the bottom of this file assert is behaviour
# `closeout_preflight.py` does not have YET, and the two flags they name (`--expect-key`,
# `--no-fetch`) are today answered by argparse with `SystemExit(2)` and a usage line.
# In-process that SystemExit would take this whole file down mid-run - a red that kills
# the suite reads exactly like a suite that crashed, and only one of those is evidence.
# So: subprocess, exit code + joined output, and one guard (`rejected`) whose only job is
# to keep "the flag does not exist yet" from being scored as "the check fired and blocked".

CP_SCRIPT = Path(cp.__file__).resolve()

_FINDING_RE = re.compile(r"^\[(ERROR|WARN|INFO)\s*\]\s*([\w-]+):\s*(.*)$", re.MULTILINE)


def _spawn(repo: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(CP_SCRIPT), *args], cwd=str(repo),
                       capture_output=True, text=True, errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def run_cp(repo: Path, *args: str) -> tuple[int, str]:
    """The script as a child process, stdout and stderr joined, cwd INSIDE the fixture.

    cwd matters: `main()` looks for a lobby by walking up from cwd and syncs it too, so a
    run launched from the real checkout would fold this repo's own working state into a
    fixture's findings.

    The retry covers exactly ONE future shape and nothing else. `task_preflight` made
    `--expect-key` REQUIRED (SCC-64); if SCC-210 does the same here, the CP-FR and CP-MEM
    fixtures - which are about freshness and about memory, not about intent - would die on
    a usage error instead of measuring the thing they exist for. It fires only on argparse's
    own "required" message and only when the caller did not pass the flag, so it can never
    soften CP-EK, which passes it on every run.
    """
    rc, out = _spawn(repo, *args)
    if ("the following arguments are required" in out and "--expect-key" in out
            and "--expect-key" not in args):
        rc, out = _spawn(repo, *args, "--expect-key", "SCC-11")
    return rc, out


def rejected(out: str, flag: str) -> bool:
    """True when argparse REFUSED the flag - i.e. it does not exist yet.

    ⛔ This is the guard the whole red rests on. An unknown option exits 2, and 2 is also
    this script's BLOCKING code, so `rc == 2` on its own would let "the flag is missing"
    masquerade as "the check ran and blocked" - a green-looking red that proves nothing."""
    return "unrecognized arguments" in out and flag in out


def findings(out: str, sev: str | None = None, needle: str | None = None) -> list[str]:
    """The `[SEV  ] section: msg` rows of a human report, filtered, message only."""
    return [msg for s, _section, msg in _FINDING_RE.findall(out)
            if (sev is None or s == sev) and (needle is None or needle in msg)]


def verdict_line(out: str) -> str:
    """The one line an agent acts on. Empty string when none was printed - never None,
    because `"STALE" in None` would be the crash-in-setup this file must not have."""
    hits = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("VERDICT:")]
    return hits[-1] if hits else ""


def lane_repo(root: Path) -> Path:
    """A close-out lane with NOTHING wrong with it - the only fixture whose verdict line
    is readable evidence.

    `build()` above is a deliberately BROKEN tree (a ghost file, a sibling collision, no
    active-context), which is right for the reader cases and useless for these three: the
    verdict is computed `if errors -> BLOCKED, elif not fresh -> STALE, else clear`, so a
    fixture carrying one error can never show freshness on that line no matter how the
    script is fixed. Measured on this fixture today: 0 errors, 1 warning, exit 1,
    `VERDICT: clear to close out`.

    It also carries a REAL `origin` - a local bare repo - because the target state fetches
    by DEFAULT, and a fetch with no remote fails, which would make every default run look
    stale for a reason that is the fixture's fault rather than the script's.
    """
    repo = root / "lane"
    (repo / BOARD_REL.parent).mkdir(parents=True)
    (repo / BOARD_REL).write_text("development_status:\n  30-1-fresh: review\n",
                                  encoding="utf-8")
    ctx = repo / "_bmad-output/active-context"
    ctx.mkdir(parents=True)
    (ctx / "active-context.md").write_text("# active context\n", encoding="utf-8")

    stories = repo / "_bmad/bmm/stories"
    stories.mkdir(parents=True)
    (stories / "story-30.1-fresh.md").write_text(
        "# Story\nStatus: review\n\n### File List\n- backend/real.py\n", encoding="utf-8")

    # The artifact folder's date is pre-CUTOFF ON PURPOSE: walkthrough_roster.judge treats
    # a legacy lane as a note rather than a block, so the roster rules cannot inject the
    # error that would take over the verdict line these cases have to read.
    art = repo / "_artifacts/2026-08-01_epic_30/story-30-1-fresh"
    art.mkdir(parents=True)
    (art / "walkthrough.md").write_text("## Code Review\n\n**Verdict: PASS**\n",
                                        encoding="utf-8")

    # A TRACKED memory store. Untracked, git would collapse the whole directory into one
    # `?? _artifacts/_memory/` row and CP-MEM would be measuring git's output folding
    # rather than the script's classification.
    (repo / "_artifacts/_memory").mkdir(parents=True)
    (repo / "_artifacts/_memory/index.md").write_text("# memory index\n", encoding="utf-8")
    (repo / "notes").mkdir()
    (repo / "notes/ordinary.md").write_text("one\n", encoding="utf-8")
    (repo / "backend").mkdir()
    (repo / "backend/real.py").write_text("x = 1\n", encoding="utf-8")

    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "seed")
    # Two sibling lanes and one pre-Jira branch, all at the same commit: CP-EK is about
    # which key the NAME carries, never about what the branch contains.
    git(repo, "branch", "claude/SCC-11-mine")
    git(repo, "branch", "claude/SCC-22-sibling")
    git(repo, "branch", "claude/xdist-tail-hang")
    # CHECKED, not fired and forgotten. A silent failure in any of these three leaves the
    # lane with NO upstream, and `check_sync` then degrades to "no upstream to compare
    # against" - still exit 1, still zero ERRORs, so FR0 keeps passing while the fixture has
    # quietly stopped being the thing FR1-FR4 measure. Under the default-ON fetch it is worse
    # still: the fetch itself fails, `fresh` goes False, the verdict says STALE, and FR4 goes
    # red blaming the implementer for a dead `origin`. A broken fixture has to say so HERE.
    bare = subprocess.run(["git", "init", "-q", "--bare", str(root / "origin.git")],
                          capture_output=True, text=True)
    assert bare.returncode == 0, f"lane_repo: bare origin init failed: {bare.stderr}"
    added = git(repo, "remote", "add", "origin", str(root / "origin.git"))
    assert added.returncode == 0, f"lane_repo: remote add origin failed: {added.stderr}"
    pushed = git(repo, "push", "-q", "-u", "origin", "main")
    assert pushed.returncode == 0, f"lane_repo: push -u origin main failed: {pushed.stderr}"
    return repo



# ── OV · SCC-357 · the project overview guide, checked at the STORY close-out ────────
#
# The lobby keeps its SOP honest with a commit-msg gate. A project cannot use that shape:
# its usage surface is `backend/` + `frontend/`, which every commit touches, so the gate
# would fire on every commit and `[sop-ok]` would become reflex — and a gate opted out of
# by reflex checks nothing (`sop-currency.md` says so itself). The unit of change in a
# project is the STORY, so the check lives here.
#
# ⛔ THE CUTOFF IS THE WHOLE REASON THIS CAN BE AN ERROR AT ALL. This script is also run by
# `/cicd-prune-worktree` and `/cicd-merge-epic-workingtrees`, so an unconditional error
# would block the PRUNE of every story saved before the guide law existed, the moment a
# project gains a guide — a red whose only remedy is to re-run a save on a story that is
# already `Done`. Dated exemption, same mechanism as `walkthrough_roster.CUTOFF`, and the
# lane's date comes from `roster.lane_date` rather than a second parser.
def ov_repo(root: Path, date: str = "2026-09-02", guide: bool = True,
            line: str | None = None, edit_guide: bool = False) -> Path:
    """`lane_repo`, plus a guide and a dated artifact folder, posed for one OV case."""
    repo = lane_repo(root)
    art = repo / "_artifacts/2026-08-01_epic_30"
    art.rename(repo / f"_artifacts/{date}_epic_30")
    art = repo / f"_artifacts/{date}_epic_30/story-30-1-fresh"
    if line:
        wt = art / "walkthrough.md"
        wt.write_text(wt.read_text(encoding="utf-8") + f"\n## Evidence\n\n{line}\n",
                      encoding="utf-8")
    if guide:
        (repo / "docs").mkdir(exist_ok=True)
        (repo / "docs/project_overview_guide.md").write_text(
            "# Overview\n\n```mermaid\nflowchart TD\n  A --> B\n```\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "pose")
    git(repo, "push", "-q", "origin", "main")
    # The lane itself: a story branch off main, so `<base>...HEAD` is a real comparison.
    git(repo, "checkout", "-q", "-b", "claude/SCC-30-fresh")
    if edit_guide:
        (repo / "docs/project_overview_guide.md").write_text(
            "# Overview\n\n```mermaid\nflowchart TD\n  A --> B --> C\n```\n",
            encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "SCC-30 docs(guide): the new hop")
    return repo


def ov(out: str, sev: str) -> list[str]:
    """Rows of the `overview` SECTION at one severity.

    ⛔ Deliberately NOT `findings(out, sev, "overview")`: that helper filters on the MESSAGE,
    so it would pass or fail on whether the word happens to appear in the prose, and a later
    reword of a message would turn a behavioural check red for no behavioural reason. The
    section is the machine-readable half of the row — assert on that.
    """
    return [msg for s, section, msg in _FINDING_RE.findall(out)
            if s == sev and section == "overview"]


def ov_run(repo: Path) -> tuple[int, str]:
    return run_cp(repo, "--story", "30-1", "--expect-key", "SCC-30",
                  "--branch", "claude/SCC-30-fresh", "--no-fetch")


def main() -> int:
    c = Cases("closeout_preflight")
    if c.block("OV · SCC-357 · the project overview guide is edited, or the walkthrough says why"):
        # OV1 · a project with no guide yet must not be blocked — AVCH-112 writes the first
        # edition, and every close-out between now and then still has to work.
        with TempDir() as tmp:
            rc, out = ov_run(ov_repo(tmp, guide=False))
            c.check("OV1 no guide in the project -> WARN, never an error",
                    bool(ov(out, "WARN")) and not ov(out, "ERROR"),
                    out.strip()[-400:])

        # OV2 · the guide moved on this lane. Nothing else is asked for.
        with TempDir() as tmp:
            rc, out = ov_run(ov_repo(tmp, edit_guide=True))
            c.check("OV2 guide edited on the lane -> INFO",
                    bool(ov(out, "INFO")) and not ov(out, "ERROR"),
                    out.strip()[-400:])

        # OV3 · unchanged, and the walkthrough accounts for it. The em-dash spelling is the
        # one the command writes; the regex must not depend on it.
        with TempDir() as tmp:
            rc, out = ov_run(ov_repo(
                tmp, line="Project overview guide: unchanged - no flow, part or contract moved."))
            c.check("OV3 guide unchanged + the walkthrough says why -> INFO",
                    bool(ov(out, "INFO")) and not ov(out, "ERROR"), out.strip()[-400:])

        # OV4 · THE RED THIS EXISTS FOR: unchanged, unaccounted for, and the lane is dated
        # after the law. Step 3.5 of the save never ran.
        with TempDir() as tmp:
            rc, out = ov_run(ov_repo(tmp))
            c.check("OV4 guide unchanged and unaccounted for -> ERROR",
                    bool(ov(out, "ERROR")), out.strip()[-400:])

        # OV5 · the same unaccounted lane, dated BEFORE the law. Exempt, and it says so.
        with TempDir() as tmp:
            rc, out = ov_run(ov_repo(tmp, date="2026-07-15"))
            c.check("OV5 a lane dated before the cutoff is EXEMPT, not blocked",
                    not ov(out, "ERROR") and bool(ov(out, "INFO")), out.strip()[-400:])

        # OV6 · ⛔ CONTROL. The line has to CLAIM one of the two states the check accepts.
        # "updated" is a word an agent would happily write while having done nothing, and
        # accepting it would make the whole check satisfiable by prose.
        with TempDir() as tmp:
            rc, out = ov_run(ov_repo(
                tmp, line="Project overview guide: updated where it mattered."))
            c.check("OV6 CONTROL a line that claims neither `unchanged` nor `absent` does NOT satisfy",
                    bool(ov(out, "ERROR")), out.strip()[-400:])


    # ── VR · LEGACY COVERAGE · the reader itself, read with no fixture at all ───────────
    if c.block("VR · legacy · the verdict reader's regex, and the slug predicates beside it"):
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

        # ── F4: a sibling's artifacts must not answer for this story ──────────
        c.check("slug/exact", wf.slug_matches("21-8b", "21-8b"), "")
        c.check("slug/21-8 does NOT match 21-8b (sibling collision)",
                not wf.slug_matches("21-8", "21-8b"), "")
        c.check("slug/an id still matches its full key",
                wf.slug_matches("21-8b", "21-8b-demo-data-quarantine"), "")
        c.check("story_id strips the descriptive tail",
                wf.story_id("21-8b-demo-data-quarantine") == "21-8b",
                wf.story_id("21-8b-demo-data-quarantine"))

    # ── FX · LEGACY COVERAGE · the same rules, now driven over a real (broken) tree ─────
    if c.block("FX · legacy · F2/F3/F4/F6 driven over the deliberately BROKEN fixture"):
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

            # ── F2: history closed under the old scheme is not "unreviewed" ───
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

            # ── F3: "could not check" must never print like "checked, clean" ──
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

            # ── F6: the File List is a claim, and claims get checked ──────────
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
    # A two-letter prefix is not a selector: `--case "ST"` matched this block AND CP-EK,
    # because "must" contains it. Measured, then renamed.
    if c.block("SAMETREE · legacy · the predicate two commands trust to SKIP a gate"):
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

    # ── CP-EK · the intent argument this script has never had (SCC-210) ────────────────
    # On 2026-08-09 a close-out preflight resolved a SIBLING lane's branch and printed
    # "clear to close out" about the wrong work. `task_preflight` answered that with a
    # REQUIRED `--expect-key` and one rule: cwd is not intent, so the ticket the operator
    # MEANT has to arrive as an argument and the branch has to agree with it. This script
    # still has no intent argument at all - hand it `--branch` and `find_branches` returns
    # `[explicit]`, which is then checked without ever being compared to anything.
    # The key segment has to come off the branch NAME, and the one branch-key regex that was
    # already shipped cannot be reused: `task_preflight.BRANCH_RE` (task_preflight.py:68,
    # `^chore/([A-Z][A-Z0-9]*)-(\d+)-(.+)$`) is anchored to `chore/` because that is the Task
    # lane's only branch shape, so against the story lanes below - `claude/*`, and `epic/*` -
    # it matches nothing and an intent check built on it would be dead code that always
    # passes. What these three cases REQUIRE, and what the SCC-210 plan PROPOSES rather than
    # quotes, is a prefix-agnostic form of it: `^[a-z]+/([A-Z][A-Z0-9]*-\d+)-`. The rows
    # below pin the BEHAVIOUR, never a pattern - any regex that reads the key off these
    # fixture branch names satisfies them.
    # Every finding below must NAME the flag, so `--expect-key` greps to the intent verdict.
    if c.block("CP-EK · SCC-210 · --expect-key: cwd is not intent, and the branch must "
               "carry the key you meant"):
        with TempDir() as tmp:
            repo = lane_repo(tmp)
            base = ("--story", "30-1", "--project", str(repo))
            MISSING = "--expect-key does not exist yet (argparse: unrecognized arguments)"

            rc, out = run_cp(repo, *base, "--branch", "claude/SCC-22-sibling",
                             "--expect-key", "SCC-11")
            gone = rejected(out, "--expect-key")
            errs = findings(out, "ERROR", "expect-key")
            # BOTH keys, because a message naming only one of them cannot tell an agent
            # whether the branch is wrong or the key it typed is.
            c.check("EK1 --expect-key SCC-11 aimed at claude/SCC-22-sibling ERRORs, naming "
                    "the key MEANT and the key FOUND",
                    (not gone) and rc == 2
                    and any("SCC-11" in m and "SCC-22" in m for m in errs),
                    MISSING if gone else f"rc={rc} intent errors={errs}")

            rc, out = run_cp(repo, *base, "--branch", "claude/SCC-11-mine",
                             "--expect-key", "SCC-11")
            gone = rejected(out, "--expect-key")
            errs = findings(out, "ERROR", "expect-key")
            c.check("EK2 the branch that DOES carry SCC-11 raises no intent error",
                    (not gone) and not errs,
                    MISSING if gone else f"rc={rc} intent errors={errs}")

            rc, out = run_cp(repo, *base, "--branch", "claude/xdist-tail-hang",
                             "--expect-key", "SCC-11")
            gone = rejected(out, "--expect-key")
            errs = findings(out, "ERROR", "expect-key")
            warns = findings(out, "WARN", "expect-key")
            # WARN and not silence: refusing every pre-Jira branch would make the flag
            # unusable on real history, but saying NOTHING repeats F3 above - "I could not
            # check" printing identically to "I checked and it is clean".
            c.check("EK3 a pre-Jira branch with NO key segment WARNs - never errors, and "
                    "never goes quiet",
                    (not gone) and not errs and bool(warns),
                    MISSING if gone else f"rc={rc} errors={errs} warns={warns}")

            # ⛔ EK0 · REQUIREDNESS IS THE GUARD (SCC-210 review). Every row above PASSES the flag, so all of
            # them stay green when `required=True` becomes `required=False` - measured: the
            # whole 39-file suite survives that one-token edit, and the mutant then prints
            # `VERDICT: clear to close out` for a run aimed at a sibling lane, which is the
            # 2026-08-09 failure restored. `_spawn` and not `run_cp`, deliberately: run_cp's
            # retry exists to re-supply this exact flag, so asking it would soften the one
            # signal being asserted. `test_task_preflight.py` carries the sibling row.
            rc, out = _spawn(repo, *base, "--branch", "claude/SCC-22-sibling")
            c.check("EK0 a bare run with NO --expect-key is REFUSED, not quietly allowed",
                    rc == 2 and "--expect-key" in out
                    and "the following arguments are required" in out,
                    f"rc={rc} out={out.strip()[-200:]}")

            # ⛔ EK4 · `find_branches` runs `git branch --list --all`, so a branch that exists
            # only as a remote ref arrives as `origin/claude/SCC-22-sibling`. Anchored at
            # `^[a-z]+/`, the key regex ate `origin/` and read the key as ABSENT - downgrading
            # a wrong-lane ERROR (exit 2) to a pre-Jira WARN (exit 1, non-blocking) on the one
            # path where it is hardest to spot: a parked sibling whose local branch is gone.
            rc, out = run_cp(repo, *base, "--branch", "origin/claude/SCC-22-sibling",
                             "--expect-key", "SCC-11")
            errs = findings(out, "ERROR", "expect-key")
            c.check("EK4 a REMOTE-tracking wrong-lane branch ERRORs like its local twin",
                    rc == 2 and any("SCC-11" in m and "SCC-22" in m for m in errs),
                    f"rc={rc} intent errors={errs} warns={findings(out, 'WARN', 'expect-key')}")

    # ── CP-FR · the freshness state has to reach the line an agent acts on (SCC-210) ───
    # `--fetch` is opt-in here, and the unfetched path emits an INFO - exit-code-neutral,
    # three lines above a VERDICT that still reads "clear to close out". SCC-193 A already
    # fixed this shape in `task_preflight`: `BooleanOptionalAction, default=True`, the
    # unfetched path WARNs, and the verdict line itself carries the staleness
    # (task_preflight.py ~1457-1465 and ~1516-1537).
    if c.block("CP-FR · SCC-210 · freshness belongs ON the verdict line, not three lines "
               "above it"):
        with TempDir() as tmp:
            repo = lane_repo(tmp)
            base = ("--story", "30-1", "--project", str(repo),
                    "--branch", "claude/SCC-11-mine")
            MISSING = "--no-fetch does not exist yet (argparse: unrecognized arguments)"

            rc_def, out_def = run_cp(repo, *base)
            v_def = verdict_line(out_def)
            # A PRECONDITION, asserted separately rather than assumed: the verdict is
            # `if errors -> BLOCKED, elif not fresh -> STALE, else clear`, so FR2 is only
            # reachable while this fixture reports zero errors. If this row ever fails, the
            # three below are measuring the fixture and not the script.
            # ...and the ahead/behind comparison ACTUALLY RAN. Zero errors is not enough:
            # if `origin` is dead, `check_sync` prints "no upstream to compare against",
            # which is a WARN - exit still 1, ERRORs still none - so this row would stay
            # green over a fixture that has stopped comparing anything at all.
            synced = findings(out_def, "INFO", "0/0 with origin")
            c.check("FR0 precondition · the fixture reports 0 errors AND compared against a "
                    "LIVE origin, so the VERDICT line is where freshness has to show",
                    rc_def == 1 and not findings(out_def, "ERROR")
                    and v_def.startswith("VERDICT:") and bool(synced),
                    f"rc={rc_def} errors={findings(out_def, 'ERROR')} "
                    f"synced={synced} {v_def!r}")

            rc_nf, out_nf = run_cp(repo, *base, "--no-fetch")
            gone = rejected(out_nf, "--no-fetch")
            v_nf = verdict_line(out_nf)
            c.check("FR1 --no-fetch is an ACCEPTED flag (the offline opt-out from a "
                    "default-ON fetch)",
                    not gone, MISSING if gone else f"rc={rc_nf} {v_nf!r}")
            c.check("FR2 with --no-fetch the VERDICT line ITSELF carries STALE",
                    (not gone) and "STALE" in v_nf,
                    MISSING if gone else (v_nf or "(no VERDICT line printed)"))
            # SEVERITY, never the exit code. `rc_nf != 0` is ALREADY true on this fixture
            # for an unrelated reason - the walkthrough verdict carries no `@ <sha>`, which
            # WARNs - so it stays true under a fix that leaves the unfetched path an INFO.
            # Measured, twice: a mutant doing the whole job EXCEPT emitting `rep.warn` on
            # that path left the old exit-code assertion GREEN and the whole block green -
            # it survived. The footnote this row is named for IS the severity, so the
            # severity is what it reads.
            stale_warn = findings(out_nf, "WARN", "LAST fetch")
            c.check("FR3 the unfetched path WARNs rather than INFOs - a stop, not a footnote",
                    (not gone) and bool(stale_warn),
                    MISSING if gone else f"rc={rc_nf} WARN/LAST fetch={stale_warn}")
            # Control, and it has to keep passing: the fix is default-ON freshness, not a
            # verdict that says STALE unconditionally.
            c.check("FR4 control · the DEFAULT run does NOT print the stale verdict - "
                    "freshness is on by default",
                    v_def.startswith("VERDICT:") and "STALE" not in v_def,
                    v_def or "(no VERDICT line printed)")

            # ⛔ FR5 · SCC-210 review · THE TWO REMEDIES MUST DIFFER, because the fixes are different acts. A
            # failed fetch is an uplink to repair; `--no-fetch` is a flag to drop. Collapsing
            # the ternary so both arms print "re-run WITHOUT --no-fetch" survived the whole
            # suite - and every shipped invocation passes the DEFAULT, so that arm is the one
            # an agent actually meets, being told to remove a flag it never typed.
            dead = repo / "no-such-remote.git"
            git(repo, "remote", "set-url", "origin", str(dead))
            rc_bad, out_bad = run_cp(repo, *base)
            v_bad = verdict_line(out_bad)
            c.check("FR5 a FAILED fetch names the uplink, never 'drop --no-fetch'",
                    "STALE" in v_bad and "FAILED" in v_bad and "--no-fetch" not in v_bad,
                    v_bad or "(no VERDICT line printed)")

        # ⛔ FR6 · SCC-210 review · the fold ACROSS repos. `main()` computes freshness as
        # `check_sync(project) and check_sync(lobby) and check_sync(worktree)`; the door
        # ALWAYS passes `--worktree`, and no row above ever did - the string did not appear in
        # this file at all. Dropping `and fresh` from the worktree term turned STALE back into
        # "clear to close out", with the whole suite green.
        #
        # ⛔ ONLY THE WORKTREE MAY BE STALE, and the first cut of this row got that wrong:
        # pointing `--worktree` at the SAME repo as `--project` under `--no-fetch` makes the
        # PROJECT term false too, so the verdict still said STALE with the mutant in place and
        # the mutant SURVIVED. The row read the WARN rows, not the fold. So: two independent
        # repos, the DEFAULT fetch, and a dead remote on the worktree alone - the project term
        # stays fresh, and only the fold can carry the staleness to the verdict.
        with TempDir() as tmp2:
            repo2 = lane_repo(tmp2)
            wtree = lane_repo(tmp2 / "second")
            git(wtree, "remote", "set-url", "origin", str(tmp2 / "no-such-remote.git"))
            base2 = ("--story", "30-1", "--project", str(repo2),
                     "--branch", "claude/SCC-11-mine")
            rc_w, out_w = run_cp(repo2, *base2, "--worktree", str(wtree))
            v_w = verdict_line(out_w)
            proj_fresh = findings(out_w, "INFO", "0/0 with origin")
            # ⛔ KEYED ON THE INTENT, NOT ON THE LABEL TEXT. This read
            # `"worktree: fetch FAILED"` — the literal label — and SCC-211 changed that label
            # to name WHICH tree ("the worktree you named (lane)"), so the needle stopped
            # matching while the behaviour it guards was untouched: the verdict still said
            # STALE and the fold still worked. A row that goes red on a better message is a
            # row coupled to prose rather than to meaning. What FR6 must prove is that the
            # failing fetch was the WORKTREE's and not the project's; that is what this asks.
            wt_failed = [f for f in findings(out_w, "WARN", "fetch FAILED")
                         if "worktree" in f.lower()]
            c.check("FR6 a stale --worktree alone makes the VERDICT stale - the fold is real",
                    "STALE" in v_w and bool(proj_fresh) and bool(wt_failed),
                    f"rc={rc_w} verdict={v_w!r} project-fresh={proj_fresh} "
                    f"worktree-failed={wt_failed}")

    # ── CP-MEM · another session's memory is not this lane's dirt (SCC-210) ────────────
    # `check_sync` folds every dirty path into one "N uncommitted change(s) - commit before
    # closing out". `task_preflight` (~926, ~952-960) splits `_artifacts/_memory/` into its
    # own class carrying the ruling, because the two lanes share ONE store: if another
    # session wrote those files, the instruction the generic message gives - commit them -
    # is the exact act the ruling forbids, and it is how a close-out gets green by sweeping
    # somebody else's unfinished work under this story's key.
    if c.block("CP-MEM · SCC-210 · another session's memory is not this lane's dirt"):
        with TempDir() as tmp:
            repo = lane_repo(tmp)
            base = ("--story", "30-1", "--project", str(repo),
                    "--branch", "claude/SCC-11-mine")

            rc_clean, _ = run_cp(repo, *base)
            (repo / "_artifacts/_memory/x.md").write_text(
                "# written by ANOTHER session\n", encoding="utf-8")
            rc_mem, out_mem = run_cp(repo, *base)
            (repo / "notes/ordinary.md").write_text("two\n", encoding="utf-8")
            rc_both, out_both = run_cp(repo, *base)
            dirty = git(repo, "status", "--porcelain").stdout.strip().splitlines()

            # The memory-named rows are dropped BEFORE counting. A correct split is free to
            # word its own row with the same phrase ("1 uncommitted change(s) in memory files
            # under _artifacts/_memory/ - ... never sweep ..."); greping every ERROR row would
            # then read [1, 1] and hold this row red against an implementation MEM2 passes -
            # pinning the phrasing instead of the split. Excluding still catches both real
            # failures: no split at all (2), and a split that leaves a stray generic row.
            generic = [m for m in findings(out_both, "ERROR", "uncommitted change(s)")
                       if "_artifacts/_memory/" not in m]
            counts = [int(m.group(1)) for msg in generic
                      for m in [re.search(r"(\d+) uncommitted change", msg)] if m]
            c.check("MEM1 the generic uncommitted count EXCLUDES the memory file (1, not 2)",
                    counts == [1], f"dirty={dirty} generic={generic}")

            mem = [m for m in findings(out_both) if "_artifacts/_memory/" in m]
            # The RULING is the payload, not the count: a second row that merely repeats
            # "commit before closing out" about the memory path has split the reporting and
            # kept the wrong instruction. "never sweep" is the phrase that carries it.
            c.check("MEM2 the memory file gets its OWN finding, carrying the park-or-leave "
                    "ruling",
                    bool(mem) and any("never sweep" in m for m in mem),
                    str(mem) if mem else "no finding names _artifacts/_memory/ at all - the "
                                         "memory file is inside the generic count")

            # Control: only the REPORTING splits. Memory dirt alone still moves the exit
            # from 1 (warnings) to 2 (blocking), and both classes together stay at 2.
            c.check("MEM3 control · both classes still BLOCK; the exit code does not move",
                    rc_clean == 1 and rc_mem == 2 and rc_both == 2,
                    f"clean={rc_clean} memory-only={rc_mem} both={rc_both}")

            # ⛔ MEM4 · SCC-210 review · READ the memory-only run, do not merely count its exit code. MEM1 and
            # MEM2 both look at `out_both`, so a split that emits a generic row for ZERO
            # ordinary files - "project: 0 uncommitted change(s) - commit before closing out",
            # a fabricated instruction about nothing - survived all three rows. Measured.
            gen_mem = [m for m in findings(out_mem, "ERROR", "uncommitted change(s)")
                       if "_artifacts/_memory/" not in m]
            c.check("MEM4 a memory-ONLY lane gets NO generic 'commit before closing out' row",
                    not gen_mem, f"generic rows on a lane whose only dirt is memory: {gen_mem}")

            # ⛔ MEM5 · SCC-210 review · THE SHAPE CO-07 WAS WRITTEN FOR, which the rows above cannot express.
            # They dirty memory as an UNTRACKED file (`?? `, no leading space) alongside a
            # tracked one, and git lists tracked entries first - so the memory line is never
            # line 0 and never in the ` M ` form. A tracked, MODIFIED memory file listed FIRST
            # is the ordinary shape (someone edited MEMORY.md), and against it a `.strip()`
            # over the whole porcelain blob ate the leading space, shifted `ln[3:]` by one,
            # and dropped the file into the generic class - handing out the one instruction
            # the ruling forbids. Reproduced against the shipping script before the fix.
            git(repo, "add", "-A")
            git(repo, "commit", "-m", "SCC-11 seed memory + notes")
            (repo / "_artifacts/_memory/x.md").write_text("edited\n", encoding="utf-8")
            rc_tracked, out_tracked = run_cp(repo, *base)
            porcelain = git(repo, "status", "--porcelain").stdout
            mem_rows = [m for m in findings(out_tracked) if "_artifacts/_memory/" in m]
            gen_rows = [m for m in findings(out_tracked, "ERROR", "uncommitted change(s)")
                        if "_artifacts/_memory/" not in m]
            c.check("MEM5 a TRACKED-modified memory file, listed FIRST, still reaches the "
                    "memory class - never the generic 'commit' instruction",
                    bool(mem_rows) and not gen_rows,
                    f"porcelain={porcelain!r} memory rows={mem_rows} generic={gen_rows}")

            # ⛔ MEM6 · SCC-210 review · a memory path git has to QUOTE. `status --porcelain` octal-quotes any
            # path holding a non-ASCII byte, so `café.md` arrives as `"_artifacts/_memory/
            # caf\303\251.md"`, `ln[3:]` starts with `"`, and the class test misses again -
            # the same misroute by a second route. `task_preflight` passes
            # `-c core.quotepath=false` and records the incident that forced it.
            (repo / "_artifacts/_memory/café-lesson.md").write_text("x\n", encoding="utf-8")
            _, out_utf8 = run_cp(repo, *base)
            mem_utf8 = [m for m in findings(out_utf8) if "_artifacts/_memory/" in m]
            c.check("MEM6 a memory path git QUOTES (non-ASCII) is counted in the memory class",
                    any("2 dirty file(s)" in m for m in mem_utf8),
                    f"memory rows={mem_utf8}")

    # ══ SCC-211 · THE TREE THAT GETS GATED IS DERIVED, NOT TAKEN ON TRUST ═════════════════
    #
    # This door checked the lane's worktree only `if args.worktree:`. The command body says in
    # bold that the flag is not optional — but argparse did not, and `/cicd-prune-worktree`
    # calls this same script WITHOUT it. In that shape the project root stands on `main`,
    # spotless, while the lane's tree is dirty, and the run answered "clean" and cleared the
    # close-out.
    #
    # ⛔ MAKING THE FLAG REQUIRED WAS THE OBVIOUS FIX AND IT IS THE WEAKER ONE. A required flag
    # can still be pointed at the wrong tree — that is "cwd is not intent" wearing a flag — and
    # it breaks every existing caller that does not pass one. Asking git which tree holds the
    # branch cannot be forgotten and cannot be aimed wrong, so the tree is DERIVED, and
    # `--worktree` survives as an additional explicit tree rather than as the only one.
    if c.block("SCC-211 · a dirty LANE worktree is caught with no --worktree flag"):
        with TempDir() as tmp:
            repo = lane_repo(tmp)
            wt = tmp / "lane-tree"
            git(repo, "worktree", "add", "-q", str(wt), "claude/SCC-11-mine")
            (wt / "backend" / "real.py").write_text("x = 999  # uncommitted, in the lane\n",
                                                    encoding="utf-8")
            rc, out = run_cp(repo, "--story", "30-1", "--project", str(repo),
                             "--branch", "claude/SCC-11-mine", "--expect-key", "SCC-11",
                             "--no-fetch")
            dirt = findings(out, "ERROR", "uncommitted")
            c.check("SCC-211 the lane's dirt is found without being told where to look",
                    bool(dirt), f"rc={rc} " + out.strip()[-400:])
            c.check("SCC-211 ...and the tree it names is the LANE's, not the project root",
                    any("lane-tree" in d for d in dirt), " | ".join(dirt) or out.strip()[-400:])
            c.check("SCC-211 ...so the verdict cannot read clear",
                    "clear to close out" not in verdict_line(out).lower(), verdict_line(out))

        # ⛔ THE POSITIVE CONTROL. Worktrees are the NORM in this system, so a check that
        # refused every lane with one would false-red the shipping path on almost every
        # close-out — which is how a gate gets routed around instead of used.
        with TempDir() as tmp:
            repo = lane_repo(tmp)
            git(repo, "worktree", "add", "-q", str(tmp / "lane-tree"), "claude/SCC-11-mine")
            rc, out = run_cp(repo, "--story", "30-1", "--project", str(repo),
                             "--branch", "claude/SCC-11-mine", "--expect-key", "SCC-11",
                             "--no-fetch")
            c.check("SCC-211 CONTROL: a CLEAN lane worktree raises no sync error",
                    not findings(out, "ERROR", "uncommitted"), out.strip()[-300:])

        # And `--worktree` still means something: an explicit third tree is measured too, so
        # the flag is an ADDITION to the derived answer rather than the only source of it.
        with TempDir() as tmp:
            repo = lane_repo(tmp)
            other = tmp / "some-other-tree"
            git(repo, "worktree", "add", "-q", str(other), "claude/SCC-22-sibling")
            (other / "notes" / "ordinary.md").write_text("dirty\n", encoding="utf-8")
            rc, out = run_cp(repo, "--story", "30-1", "--project", str(repo),
                             "--branch", "claude/SCC-11-mine", "--expect-key", "SCC-11",
                             "--worktree", str(other), "--no-fetch")
            c.check("SCC-211 an explicitly named tree is still measured",
                    any("some-other-tree" in d for d in findings(out, "ERROR", "uncommitted")),
                    out.strip()[-400:])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
