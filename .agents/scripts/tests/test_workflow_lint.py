"""wf-lint: allow-encoding-literals — the fixtures below ARE mojibake, on purpose.

workflow_lint's checks must FIRE on real defects and stay quiet on look-alikes. Without
these controls a clean lint run is indistinguishable from a dead detector.

The encoding third case is the one that caught us: `cicd-prune-context.md` documents the
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
        # operator ruling: implementation_plan.md is a TWO-author doc (plan + /cicd-self-audit
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

        # ── SCC-63: the naming law is MECHANICAL, not prose ───────────────────
        # The prefix decides permissions (cicd-* binds smh-target-resolution.md =
        # one project, never the lobby; smh-* may act on the lobby), so a misnamed
        # command claims the wrong ones. Negative controls first: a check that
        # cannot fail proves nothing, and the retired prefix is the exact thing
        # this must never accept again.
        nl = tmp / "naming"
        (nl / ".agents/commands").mkdir(parents=True)
        cmds = nl / ".agents/commands"
        for good in ("cicd-code-review.md", "smh-sync-agents.md",
                     "sentry-security-team-avch.md", "cicd-code-review-AP.md",
                     "dev.md", "testarch-atdd.md", "INDEX.md"):
            (cmds / good).write_text("---\ndescription: x\n---\n", encoding="utf-8")
        rep = wf.Report()
        lint.check_naming_law(nl, rep)
        c.check("SCC-63 positive control: valid families + vendor bridges pass",
                not [i for i in rep.items if i["sev"] == "ERROR"],
                str([i["msg"] for i in rep.items])[:140])

        # ⛔ These fixture names are DELIBERATELY the retired forms and must never be
        # "fixed" by a rename sweep - they are the controls. If a sweep rewrites them
        # the check still passes while proving nothing (SCC-63: this happened once).
        for bad in ("sudo-code-review.md", "autopilot_claude.md",
                    "webm-alpha-video.md", "cicd_bad_underscore.md"):
            (cmds / bad).write_text("---\ndescription: x\n---\n", encoding="utf-8")
        rep = wf.Report()
        lint.check_naming_law(nl, rep)
        errs = " ".join(i["msg"] for i in rep.items if i["sev"] == "ERROR")
        c.check("SCC-63 negative control: the RETIRED sudo- prefix is rejected",
                "sudo-code-review.md" in errs, errs[:140])
        c.check("SCC-63 negative control: an unprefixed command is rejected",
                "webm-alpha-video.md" in errs, errs[:140])
        c.check("SCC-63 negative control: underscores are rejected (hyphens only)",
                "autopilot_claude.md" in errs and "cicd_bad_underscore.md" in errs,
                errs[:140])
        c.check("SCC-63 the vendor allowlist stays CLOSED (20 names)",
                len(lint.VENDOR_COMMANDS) == 20, str(len(lint.VENDOR_COMMANDS)))

        # ── SCC-209: the `-AP` twin freshness check is GONE ─────────────────
        # The `_AP` autopilot lane is abandoned pending a rewrite (operator ruling,
        # 2026-08-18), so the twin-freshness check and its frontmatter stamp were
        # deleted rather than left armed - an armed gate on an abandoned file only buys
        # restamps of a file nobody maintains. What survives is the one fact a reader
        # of those files still needs: they are UNMAINTAINED, and three autopilot
        # engines still invoke them by name, which is why they were kept, not deleted.
        # ⛔ This assertion is what stops the marker being quietly dropped, and it is
        #    the ONLY mechanical statement left about the trio.
        # `real` is the live lobby root - the SCC-128 block below reuses it.
        real = Path(__file__).resolve().parents[3]
        ap_files = sorted((real / ".agents/commands").glob("*-AP.md"))
        unmarked = [f.name for f in ap_files if "UNMAINTAINED" not in wf.read_text(f)]
        c.check("SCC-209 every -AP command is marked UNMAINTAINED",
                len(ap_files) == 3 and not unmarked,
                f"found={[f.name for f in ap_files]} unmarked={unmarked}")

        # ── SCC-205: the WINDOWS-ONLY invocation ─────────────────────────────
        # The venv bin dir is the one path that differs on every tool call between the two
        # machines this system runs on. Five authored surfaces hardcoded `Scripts/`, and the
        # worst of them was `cicd-close-workingtree`'s Step 4 probe: it guards an
        # IRREVERSIBLE delete, and on the Mac it reported a destroyed shared venv that was
        # never touched. A probe that cries wolf on the destructive step is one people learn
        # to skip.
        #
        # ⛔ THE THREE LOOK-ALIKES ARE THE WHOLE DIFFICULTY, and each gets a control below.
        # A file may legitimately name the Windows path as the Windows ARM of a conditional,
        # as PROSE explaining the rule, or as a test FIXTURE. Without those controls the
        # check fires on the documents that state the law correctly - the same disease as
        # `comment-literals-invert-source-grep-tests`, where the guard punishes the author
        # who wrote it down.
        bm = tmp / "bothmachines"
        cmds = bm / ".agents/commands"
        cmds.mkdir(parents=True)
        (cmds / "hardcoded.md").write_text(
            "---\ndescription: x\n---\n"
            "Run `backend/.venv/Scripts/python.exe -m pytest`.\n", encoding="utf-8")
        (cmds / "conditional.md").write_text(
            "---\ndescription: x\n---\n"
            "```bash\nVENV=backend/.venv/bin; [ -d \"$VENV\" ] || VENV=backend/.venv/Scripts\n```\n",
            encoding="utf-8")
        (cmds / "prose.md").write_text(
            "---\ndescription: x\n---\n"
            "A venv puts its executables in `.venv/Scripts/` on Windows and `.venv/bin/` on POSIX.\n",
            encoding="utf-8")
        (cmds / "adjacent.md").write_text(
            "---\ndescription: x\n---\n"
            "# the venv bin dir differs per machine - POSIX first\n"
            "$PY = \"$ROOT/backend/.venv/bin/python3\"\n"
            "if (-not (Test-Path $PY)) { $PY = \"$ROOT/backend/.venv/Scripts/python.exe\" }\n",
            encoding="utf-8")
        rep = wf.Report()
        lint.check_both_machines(bm, rep)
        bmsg = " ".join(i["msg"] for i in rep.items if i["section"] == "both-machines")
        c.check("SCC-205 A a hardcoded Windows venv path is reported",
                "hardcoded.md" in bmsg, bmsg[:160])
        c.check("SCC-205 B the Windows ARM of a conditional is NOT reported",
                "conditional.md" not in bmsg,
                "" if "conditional.md" not in bmsg else bmsg[:200])
        c.check("SCC-205 C prose stating the rule is NOT reported",
                "prose.md" not in bmsg,
                "" if "prose.md" not in bmsg else bmsg[:200])
        c.check("SCC-205 D a POSIX arm on the LINE ABOVE silences it",
                "adjacent.md" not in bmsg,
                "" if "adjacent.md" not in bmsg else bmsg[:200])
        c.check("SCC-205 E exactly ONE offender - the check is not firing on everything",
                len([i for i in rep.items if i["section"] == "both-machines"]) == 1,
                bmsg[:200])
        c.check("SCC-205 F the message names the fix, not just the sin",
                "code-standards" in bmsg and "VENV=" in bmsg, bmsg[:200])
        # G. THE LIVE TREE. Every case above runs on fixtures, so the whole class could be
        #    back on `main` with all six green. `real` is the lobby root, bound above.
        rep = wf.Report()
        lint.check_both_machines(real, rep)
        c.check("SCC-205 G the live tree hardcodes the Windows venv path NOWHERE",
                not [i for i in rep.items if i["section"] == "both-machines"],
                str([i["msg"] for i in rep.items])[:300])

        # ── SCC-128: the resurrection lint ───────────────────────────────────
        # The vendor `bmad-code-review` skill is RETIRED in favour of the house
        # `code-review-engine`, but BMAD's installer re-emits the vendor skill on every
        # regen - so "we deleted the references" is a state that undoes itself. The guard
        # has to be permanent, and it has to scan the two surfaces that can route work
        # BACK to the vendor skill: commands (what an operator invokes) and rules (what an
        # agent loads mid-run). Both spellings matter - `bmad-code-review` is the skill,
        # `bmad_code_review_sudo_fix` was the adapter rule that patched it.
        #
        # ⛔ The literals below are DELIBERATELY the retired forms. They are the negative
        # controls; a rename sweep that "fixes" them leaves a check that passes while
        # proving nothing. INDEX.md is scanned here (unlike check_commands, which skips
        # it) because a router row pointing at a retired surface IS the resurrection.
        res = tmp / "resurrect"
        (res / ".agents/commands").mkdir(parents=True)
        (res / ".agents/rules").mkdir(parents=True)
        rcmds, rrules = res / ".agents/commands", res / ".agents/rules"

        def res_report(root: Path) -> wf.Report:
            r = wf.Report()
            lint.check_retired_review_surface(root, r)
            return r

        def res_msgs(r: wf.Report) -> str:
            return " ".join(i["msg"] for i in r.items
                            if i["section"] == "retired-surface")

        # A. Positive control FIRST: a clean toolkit is silent. Without this the rest
        #    only proves the detector is always-on, which is not a detector.
        (rcmds / "clean-cmd.md").write_text(
            "---\ndescription: x\n---\nInvoke the `code-review-engine` skill.\n",
            encoding="utf-8")
        (rrules / "clean-rule.md").write_text(
            "---\nname: clean\n---\nThe engine owns the lens fan-out.\n", encoding="utf-8")
        c.check("SCC-128 A positive control: a clean toolkit is silent",
                not res_msgs(res_report(res)), res_msgs(res_report(res))[:140])

        # B. A command that routes back to the vendor skill is an ERROR.
        (rcmds / "stale-cmd.md").write_text(
            "---\ndescription: x\n---\nInvoke the **`bmad-code-review`** skill on the diff.\n",
            encoding="utf-8")
        rep = res_report(res)
        c.check("SCC-128 B a command naming the vendor skill is an ERROR",
                any(i["sev"] == "ERROR" and "stale-cmd.md" in i["msg"]
                    for i in rep.items if i["section"] == "retired-surface"),
                res_msgs(rep)[:140])

        # C. The UNDERSCORE form - the retired adapter rule - fires too. A guard that
        #    only knows the skill's spelling misses every pointer at the rule that
        #    patched it, which is the half that survives as a dangling file path.
        (rrules / "stale-rule.md").write_text(
            "---\nname: x\n---\nRead `.agents/rules/bmad_code_review_sudo_fix.md` in full.\n",
            encoding="utf-8")
        rep = res_report(res)
        c.check("SCC-128 C the underscore form (the retired rule) also fires",
                any(i["sev"] == "ERROR" and "stale-rule.md" in i["msg"]
                    for i in rep.items if i["section"] == "retired-surface"),
                res_msgs(rep)[:140])

        # D. A router row is a resurrection: INDEX.md is in scope on both surfaces.
        (rrules / "INDEX.md").write_text(
            "| `bmad_code_review_sudo_fix.md` | on-demand | run-to-completion review. |\n",
            encoding="utf-8")
        rep = res_report(res)
        c.check("SCC-128 D an INDEX row pointing at a retired surface fires",
                any(i["sev"] == "ERROR" and "INDEX.md" in i["msg"]
                    for i in rep.items if i["section"] == "retired-surface"),
                res_msgs(rep)[:140])

        # D2. The SKILLS router is in scope too, and nested - `.agents/skills/` is the door
        #     Claude and Codex actually enter through (one door per platform, SCC-66), so a
        #     row there routes an agent to the vendor skill exactly as a rule row does. It
        #     is satisfiable because no vendor `bmad-*` skill lives under `.agents/skills/`;
        #     that directory is ours.
        #     ⭐ The assertion pins the RELATIVE PATH, not the basename: ~50 skills own a
        #     file called `SKILL.md`, so a message naming only the basename cannot be acted
        #     on. Asserting the bare name would have locked in exactly that useless message.
        (res / ".agents/skills/some-skill").mkdir(parents=True)
        (res / ".agents/skills/some-skill/SKILL.md").write_text(
            "---\nname: some-skill\n---\nRun `bmad-code-review` on the diff.\n",
            encoding="utf-8")
        rep = res_report(res)
        c.check("SCC-128 D2 a nested skill file fires, and the message LOCATES it",
                any(i["sev"] == "ERROR"
                    and ".agents/skills/some-skill/SKILL.md" in i["msg"].replace("\\", "/")
                    for i in rep.items if i["section"] == "retired-surface"),
                res_msgs(rep)[:160])

        # D3. Case-insensitivity. The generator re-emits one fixed spelling; the HUMAN half
        #     of the resurrection is the half that varies, and `BMAD-Code-Review` routes an
        #     agent exactly as well as the lower-case form.
        (rcmds / "shouty.md").write_text(
            "---\ndescription: x\n---\nRun the BMAD-Code-Review skill.\n", encoding="utf-8")
        rep = res_report(res)
        c.check("SCC-128 D3 a differently-cased spelling still fires",
                any(i["sev"] == "ERROR" and "shouty.md" in i["msg"]
                    for i in rep.items if i["section"] == "retired-surface"),
                res_msgs(rep)[:160])

        # D4. ⭐ EVERY offender is reported, not just the first one per surface. A linter
        #     that names one of five resurrections and stops is materially worse, and every
        #     case above uses `any(...)` on a fresh report - so a `break` after the first
        #     `rep.err` would survive all of them. This asserts the SET, which also pins the
        #     `sorted()` walk (nothing else does).
        offenders = sorted(i["msg"].split(":")[0].replace("\\", "/")
                           for i in res_report(res).items
                           if i["section"] == "retired-surface")
        c.check("SCC-128 D4 every offender is reported, across all scanned surfaces",
                offenders == [".agents/commands/shouty.md",
                              ".agents/commands/stale-cmd.md",
                              ".agents/rules/INDEX.md",
                              ".agents/rules/stale-rule.md",
                              ".agents/skills/some-skill/SKILL.md"],
                str(offenders))

        # D5. The positive control, re-run with all three surfaces POPULATED and clean.
        #     Case A ran before `.agents/skills/` existed, so "a clean skills surface is
        #     silent" was never actually asserted - the control covered two of the surfaces
        #     it appeared to cover.
        clean = tmp / "resurrect-clean"
        for sub in ("commands", "rules", "skills/some-skill", "workflows",
                    "opencode-agents"):
            (clean / ".agents" / sub).mkdir(parents=True)
        (clean / ".agents/commands/ok.md").write_text("Run `code-review-engine`.\n",
                                                      encoding="utf-8")
        (clean / ".agents/rules/ok.md").write_text("The engine owns the fan-out.\n",
                                                   encoding="utf-8")
        (clean / ".agents/skills/some-skill/SKILL.md").write_text("---\nname: ok\n---\n",
                                                                  encoding="utf-8")
        (clean / ".agents/workflows/INDEX.md").write_text("| a | b |\n", encoding="utf-8")
        (clean / ".agents/opencode-agents/agent.md").write_text("A reviewer.\n",
                                                                encoding="utf-8")
        c.check("SCC-128 D5 positive control: ALL five populated surfaces, clean, silent",
                not res_msgs(res_report(clean)), res_msgs(res_report(clean))[:160])

        # E. The message must carry the REMEDY. Whoever trips this is mid-regen and did
        #    not read this ticket; an error that only says "no" gets worked around.
        c.check("SCC-128 E the error names the replacement engine",
                "code-review-engine" in res_msgs(rep), res_msgs(rep)[:140])

        # F. ⭐ The live tree. This case carried a one-file exemption while SCC-126 was
        #    unlanded: `cicd-code-review-AP.md` was the ONE allowed hit, because its rewire
        #    was SCC-126's (operator-approved scope transfer) and this lane may not edit it.
        #    The exemption lived HERE and not in the linter on purpose - `workflow_lint
        #    --toolkit-only` stayed honestly RED on that file, so the violation was visible
        #    at every gate instead of being silently allowed, while run_all.py stayed green.
        #
        #    ⛔ The list is EXACT, and the first draft's `all(o == ...)` was not: `all()`
        #    over an empty set is True, so that form passed against a detector gutted to
        #    `return` - the one case touching the real tree could not fail for the reason
        #    it exists. Exact-match also made the carve-out SELF-EXPIRING.
        #
        #    ⭐ IT EXPIRED, AS DESIGNED (2026-08-13, landing set 126->127->128). SCC-126
        #    landed at a4975bf, this lane absorbed it, and its rewire cleared the file -
        #    so the case went red exactly as its author predicted, and the instruction was
        #    to DELETE the exemption rather than inherit a permanent hole. Done: the live
        #    tree must now be CLEAN, with no offender at all. Keeping the old assertion
        #    would have pinned a transient broken state as the expected one forever.
        real_rep = res_report(real)
        offenders = sorted({i["msg"].split(":")[0].replace("\\", "/")
                            for i in real_rep.items
                            if i["section"] == "retired-surface"})
        c.check("SCC-128 F the live tree has NO retired-surface offender",
                offenders == [], str(offenders))

        # G. ⭐ THE WIRING. Every case above calls the function directly, so deleting its
        #    one line in main() passes all of them while `workflow_lint --toolkit-only` -
        #    what CI, the close-out gate and the clean-code floor actually run - goes
        #    permanently silent. Verified: that deletion left the SCC-128 block at 100%.
        #    This drives the real CLI in a synthetic lobby, so the call site is asserted.
        (lob / ".agents/commands/resurrect-me.md").write_text(
            "---\ndescription: x\n---\nInvoke `bmad-code-review`.\n", encoding="utf-8")
        code_res, out_res = lint_at("--toolkit-only")
        c.check("SCC-128 G the check is WIRED into --toolkit-only (exit 2 + names it)",
                code_res == 2 and "retired-surface" in out_res
                and "resurrect-me.md" in out_res,
                f"exit={code_res} {out_res.strip()[:140]}")
        (lob / ".agents/commands/resurrect-me.md").unlink()
        c.check("SCC-128 G control: with the offender gone the CLI is clean again",
                "retired-surface" not in lint_at("--toolkit-only")[1], "")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
