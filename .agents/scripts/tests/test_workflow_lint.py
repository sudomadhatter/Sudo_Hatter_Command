"""wf-lint: allow-encoding-literals — the fixtures below ARE mojibake, on purpose.

workflow_lint's checks must FIRE on real defects and stay quiet on look-alikes. Without
these controls a clean lint run is indistinguishable from a dead detector.

The encoding third case is the one that caught us: `sudo-prune-context.md` documents the
mojibake pattern inside a code span, so a naive scan flags the file that says "don't do
this". The budget cases guard the opposite failure - a check so loud (115 warnings about
history nobody will touch) that the one actionable line is never read.
"""
from __future__ import annotations

import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir

import wf_common as wf          # noqa: E402
import workflow_lint as lint    # noqa: E402

FIXTURES = {
    # prose mojibake: a real cp1252 round-trip of an em dash
    "prose-mojibake.md": "Rebuild the board â€” then stamp it.\n".encode("utf-8"),
    # bytes that are not valid UTF-8 at all
    "undecodable.md": b"valid text then a bad byte: \xff\xfe done\n",
    # the SAME digraph, but quoted as an example inside a code span
    "quoted-only.md": ("Normalize encoding (no `â€”` mojibake "
                       "— use a real em dash).\n").encode("utf-8"),
    # and inside a fenced block
    "fenced-only.md": ("Example:\n\n```\nbad: â€”\n```\n").encode("utf-8"),
}
EXPECTED = {
    "prose-mojibake.md": {"WARN"},
    "undecodable.md": {"ERROR"},
    "quoted-only.md": set(),
    "fenced-only.md": set(),
}


def _oversize(proj: Path):
    """Grow the fixture board past the size cap, lint, then restore."""
    p = proj / wf.BOARD_REL
    original = p.read_bytes()
    p.write_bytes(original + b"# pad\n" * (lint.BOARD_SIZE_CAP // 6 + 1))
    rep = wf.Report()
    lint.check_board_note_budget(proj, rep)
    p.write_bytes(original)
    return rep


def main() -> int:
    c = Cases("encoding scanner control")
    with TempDir() as tmp:
        paths = []
        for name, data in FIXTURES.items():
            (tmp / name).write_bytes(data)
            paths.append((name, tmp / name))

        rep = wf.Report()
        lint.scan_encoding(paths, rep)

        got: dict[str, set[str]] = {n: set() for n in FIXTURES}
        for item in rep.items:
            for name in FIXTURES:
                if item["msg"].startswith(name):
                    got[name].add(item["sev"])

        for name, want in EXPECTED.items():
            c.check(name, got[name] == want,
                    f"expected {want or 'silence'}, got {got[name] or 'silence'}")

        # strip_code must not swallow the whole document
        kept = wf.strip_code("before `x` after")
        c.check("strip_code keeps prose", "before" in kept and "after" in kept, kept)

        # ── The opt-out: a file may legitimately CARRY these bytes as data ─────
        # wf_common.py holds a literal U+FFFD as REPLACEMENT_CHAR, so without this the
        # gate blocked every commit that touched the gate. Both directions asserted:
        # the marker must silence it, and its ABSENCE must not.
        (tmp / "detector.md").write_bytes(
            (lint.ENCODING_OPT_OUT + "\nthis file discusses � on purpose\n").encode("utf-8"))
        (tmp / "no-marker.md").write_bytes("no marker, same content �\n".encode("utf-8"))
        rep = wf.Report()
        lint.scan_encoding([("detector.md", tmp / "detector.md"),
                            ("no-marker.md", tmp / "no-marker.md")], rep)
        msgs = [(i["sev"], i["msg"]) for i in rep.items]
        c.check("opt-out silences a file that carries the bytes as DATA",
                not any("detector.md" in m for _, m in msgs), str(msgs)[:110])
        c.check("without the marker the SAME content still fires",
                any(s == "ERROR" and "no-marker.md" in m for s, m in msgs), str(msgs)[:110])

        # ── SCC-51: the artifact BYTE budgets are gone, and must stay gone ────
        # The 8 KB / 10 KB caps (and check_artifact_budgets) were removed 2026-08-08 by
        # operator ruling: implementation_plan.md is a TWO-author doc (plan + /sudo-self-audit
        # §7), so a fixed cap truncates the auditor. This asserts nothing re-introduces a byte
        # threshold - the standard now lives as judgement in artifacts-always-first.md.
        c.check("SCC-51 no byte-budget check exists on the linter",
                not hasattr(lint, "check_artifact_budgets") and not hasattr(lint, "_BUDGETS"),
                "a byte threshold was re-added - see artifacts-always-first.md 'Dense, not short'")
        _rule = (SCRIPTS.parent / "rules" / "artifacts-always-first.md").read_text(encoding="utf-8")
        c.check("SCC-51 the rule states the standard that replaced the cap",
                "NO byte cap" in _rule and "Length is NEVER a reason to omit" in _rule,
                "artifacts-always-first.md lost the 'dense, not short' standard")

        # ── Wave 4: the board note budget - the rule that keeps the split won ─
        proj4 = tmp / "proj4"
        (proj4 / wf.BOARD_REL).parent.mkdir(parents=True)
        (proj4 / "_bmad-output/history").mkdir(parents=True)  # post-split marker
        (proj4 / wf.BOARD_REL).write_text(
            "last_updated: 2026-08-03\n"
            "development_status:\n"
            "  4-1-done-with-note: done   # this finished row should carry NOTHING\n"
            "  4-2-live-long: review   # " + "x" * 200 + "\n"
            "  4-3-live-ok: review   # short ruling note, well under the cap\n"
            "  4-4-done-bare: done\n", encoding="utf-8")
        rep = wf.Report()
        lint.check_board_note_budget(proj4, rep)
        msgs = [(i["sev"], i["msg"]) for i in rep.items]
        c.check("W4 a note on a done row is an ERROR",
                any(s == "ERROR" and "4-1-done-with-note" in m for s, m in msgs),
                str(msgs)[:120])
        c.check("W4 an over-cap note on a live row is an ERROR",
                any(s == "ERROR" and "4-2-live-long" in m for s, m in msgs), str(msgs)[:120])
        c.check("W4 positive control: a short live note and a bare done row pass",
                not any(("4-3-live-ok" in m or "4-4-done-bare" in m) for _, m in msgs),
                str(msgs)[:120])
        rep_big = _oversize(proj4)
        c.check("W4 board over the size cap is an ERROR",
                any(i["sev"] == "ERROR" and "bytes" in i["msg"] for i in rep_big.items), "")
        # W4 flood cap: an unmigrated-but-history-bearing board must not emit 200 errors.
        # Silence and a flood mute a check equally; the summary line keeps the count honest.
        proj6 = tmp / "proj6"
        (proj6 / wf.BOARD_REL).parent.mkdir(parents=True)
        (proj6 / "_bmad-output/history").mkdir(parents=True)
        rows = "".join(f"  6-{n}-x: done   # note {n}\n" for n in range(40))
        (proj6 / wf.BOARD_REL).write_text("development_status:\n" + rows, encoding="utf-8")
        rep = wf.Report()
        lint.check_board_note_budget(proj6, rep)
        errs = [i for i in rep.items if i["sev"] == "ERROR"]
        c.check("W4 a flood is capped, and the remainder is COUNTED not dropped",
                len(errs) == lint.MAX_NOTE_ERRORS + 1
                and any("30 more note violation" in i["msg"] for i in errs),
                f"{len(errs)} errors")

        # pre-split board (no history/): rules stay off - the check must not fire
        # on a project that has not migrated
        proj5 = tmp / "proj5"
        (proj5 / wf.BOARD_REL).parent.mkdir(parents=True)
        (proj5 / wf.BOARD_REL).write_text(
            "development_status:\n  5-1-x: done   # legacy note, pre-split\n",
            encoding="utf-8")
        rep = wf.Report()
        lint.check_board_note_budget(proj5, rep)
        c.check("W4 pre-split project is exempt (info only)",
                not any(i["sev"] == "ERROR" for i in rep.items),
                str([i["msg"] for i in rep.items])[:100])

        # ── Wave 5: the pre-commit encoding gate ──────────────────────────────
        # A gate that blocks nothing and a gate that blocks everything both end up
        # disabled, so both directions are asserted.
        import subprocess
        repo = tmp / "hookrepo"
        (repo / ".agents/scripts").mkdir(parents=True)
        for f in ("wf_common.py", "workflow_lint.py"):
            (repo / ".agents/scripts" / f).write_bytes((SCRIPTS / f).read_bytes())
        subprocess.run(["git", "init", "-q"], cwd=repo)
        subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=repo)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo)

        def staged(*names: str, fix: bool = False) -> tuple[int, str]:
            subprocess.run(["git", "add", *names], cwd=repo, capture_output=True)
            r = subprocess.run(
                [sys.executable, str(repo / ".agents/scripts/workflow_lint.py"),
                 "--staged"] + (["--fix"] if fix else []),
                cwd=repo, capture_output=True, text=True, errors="replace")
            return r.returncode, r.stdout + r.stderr

        (repo / "clean.md").write_bytes("Rebuild the board — then stamp it.\n".encode("utf-8"))
        code, _ = staged("clean.md")
        c.check("W5 clean UTF-8 does not block a commit", code == 0, f"exit={code}")

        (repo / "broken.md").write_bytes(b"text then a bad byte: \xff\xfe done\n")
        code, out = staged("broken.md")
        c.check("W5 undecodable bytes BLOCK the commit",
                code == 2 and "COMMIT BLOCKED" in out, f"exit={code}")

        (repo / "moji.md").write_bytes("board â€” then\n".encode("utf-8"))
        code, out = staged("moji.md", fix=True)
        c.check("W5 --fix repairs a cp1252 round-trip to a real em dash",
                "—" in (repo / "moji.md").read_text(encoding="utf-8"),
                repr((repo / "moji.md").read_text(encoding="utf-8"))[:60])

        # `git add` is cumulative - broken.md is still in the index from the case above,
        # and leaving it there would make this assert the wrong thing entirely.
        subprocess.run(["git", "reset", "-q"], cwd=repo, capture_output=True)
        (repo / "untouched.md").write_bytes(b"not staged \xff\xfe\n")
        code, _ = staged("moji.md")
        c.check("W5 an UNSTAGED broken file is not the commit's problem",
                code == 0, f"exit={code}")

        # ── SCC-64: --toolkit-only must never resolve a project ──────────────
        # A root Task close-out was going red/green on whichever product project
        # happened to sit in .agents/active-project.txt. The flag stops BEFORE
        # resolve_project_root; the bare run is kept as the contrast control.
        lob = tmp / "lobby"
        for d in (".agents/scripts", ".agents/commands", ".agents/rules", "Projects"):
            (lob / d).mkdir(parents=True)
        for f in ("wf_common.py", "workflow_lint.py"):
            (lob / ".agents/scripts" / f).write_bytes((SCRIPTS / f).read_bytes())

        def lint_at(*args: str) -> tuple[int, str]:
            r = subprocess.run([sys.executable,
                                str(lob / ".agents/scripts/workflow_lint.py"), *args],
                               cwd=lob, capture_output=True, text=True, errors="replace")
            return r.returncode, r.stdout + r.stderr

        code_bare, out_bare = lint_at()
        c.check("SCC-64 control: a bare run with no project dies on resolution",
                code_bare == 2 and "no project resolved" in out_bare,
                f"exit={code_bare} {out_bare.strip()[:90]}")
        code_tk, out_tk = lint_at("--toolkit-only")
        c.check("SCC-64 --toolkit-only lints the toolkit with NO project resolved",
                "toolkit-only" in out_tk and "no project resolved" not in out_tk,
                f"exit={code_tk} {out_tk.strip()[:120]}")
        c.check("SCC-64 --toolkit-only + --project is refused",
                lint_at("--toolkit-only", "--project", "x")[0] == 2, "")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
