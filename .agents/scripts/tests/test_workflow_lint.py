"""wf-lint: allow-encoding-literals — the fixtures below ARE mojibake, on purpose.

workflow_lint's checks must FIRE on real defects and stay quiet on look-alikes. Without
these controls a clean lint run is indistinguishable from a dead detector.

The encoding third case is the one that caught us: `cicd-prune-context.md` documents the
mojibake pattern inside a code span, so a naive scan flags the file that says "don't do
this". The budget cases guard the opposite failure - a check so loud (115 warnings about
history nobody will touch) that the one actionable line is never read.
"""
from __future__ import annotations

import re
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

        # ⭐ In a BLOCK so the mutation sweep can address these cases: the harness's
        # `--case` filter matches BLOCK labels only, and this file declared none - so a
        # mutant naming any case here scored exit 3 (_harness.NO_MATCH) and the sweep
        # correctly refused to call it a kill. An unaddressable case cannot be swept.
        if c.block("SCC-200 the hand-back duty sits where the artifact is produced"):
            # ── SCC-200: the hand-back obligation, pinned by PLACEMENT ───────────
            #
            # ⛔ THE RECON THAT REFRAMED THIS PART. The plan assumed the rule was SILENT about
            # handing artifacts back as clickable links. It is not - the duty has been in
            # artifacts-always-first.md all along, as one blockquote up in the artifact-set
            # section. And it still did not fire: on SCC-190 the agent wrote the plan, asked for
            # approval ON that plan, ran five review lenses and a whole close-out, and handed
            # back bare paths the entire way. The operator had to ask for it outright - "I cant
            # see the artifacts unless you give me the hyper link in the chat."
            #
            # So the defect is not that the duty is unstated. It is WHERE it is stated. A rule
            # read at the top of a file is not read at the moment of the act, and the act happens
            # at exactly three seams: the plan is written (§2), approval is REQUESTED on it (§3),
            # and the walkthrough is written (§5). §3 is the sharp one - asking someone to
            # approve a document they were never handed is the defect in one sentence.
            #
            # ⭐ PINNED AS WIRING, NOT PROSE (prose-pinning-guards-are-vacuous). A marker phrase
            # alone can be pasted anywhere, so every seam must carry the marker AND a real
            # markdown-link form. The three mutants below prove the predicate can actually fail;
            # a placement check that cannot go red would read a bare-path rule as compliant.
            _MARK = "hand it back"
            _LINK = re.compile(r"\[[^\]\n]+\]\([^)\n]+\)")

            def _sections(text: str) -> dict[str, str]:
                out, cur = {}, None
                for ln in text.splitlines():
                    if ln.startswith("#"):
                        cur = ln.strip()
                        out[cur] = []
                    elif cur is not None:
                        out[cur].append(ln)
                return {k: "\n".join(v) for k, v in out.items()}

            def handback_gaps(text: str) -> list[str]:
                """Seams NOT carrying the hand-back duty. Empty list == compliant."""
                body = _sections(text)
                gaps = []
                home = next((k for k in body if k.lower().lstrip("# ").startswith(_MARK)), None)
                if home is None:
                    gaps.append("no `## Hand It Back` section")
                elif not _LINK.search(body[home]):
                    gaps.append("`## Hand It Back` shows no markdown-link form")
                for want, why in (("### 2.", "the plan is written"),
                                  ("### 3.", "approval is REQUESTED on it"),
                                  ("### 5.", "the walkthrough is written")):
                    k = next((k for k in body if k.startswith(want)), None)
                    if k is None:
                        gaps.append(f"{want} ({why}) is missing entirely")
                    elif _MARK not in body[k].lower() or not _LINK.search(body[k]):
                        gaps.append(f"{want} ({why}) does not carry the hand-back duty")
                return gaps

            def _blank_marker_in(text: str, heading: str) -> str:
                """Strip the marker from ONE section, leaving every other seam intact."""
                i = text.index(heading)
                nxt = text.find("\n### ", i + 1)
                j = nxt if nxt != -1 else len(text)
                seg = re.sub(_MARK, "(removed)", text[i:j], count=1, flags=re.I)
                return text[:i] + seg + text[j:]

            c.check("SCC-200 the rule carries the hand-back duty at ALL THREE seams",
                    not handback_gaps(_rule), "; ".join(handback_gaps(_rule)) or "?")
            # ⛔ NEGATIVE CONTROLS. Each removes the duty from ONE place; a predicate that stays
            # green on any of them is reporting the tree's cleanliness rather than measuring it.
            _m3 = _blank_marker_in(_rule, "### 3.")
            c.check("SCC-200 CONTROL: stripping the duty from the APPROVAL seam is caught",
                    any("### 3." in g for g in handback_gaps(_m3)), str(handback_gaps(_m3)))
            _m2 = _blank_marker_in(_rule, "### 2.")
            c.check("SCC-200 CONTROL: stripping it from the PLAN seam is caught",
                    any("### 2." in g for g in handback_gaps(_m2)), str(handback_gaps(_m2)))
            _mh = re.sub(r"(?im)^##\s*hand it back\s*$", "## Something Else", _rule, count=1)
            c.check("SCC-200 CONTROL: losing the `## Hand It Back` home is caught",
                    any("Hand It Back" in g for g in handback_gaps(_mh)), str(handback_gaps(_mh)))

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

        # ── SCC-82: the AP-twin check must be SATISFIABLE ────────────────────
        # It compared commit timestamps and nothing else, so a pair that had been
        # diffed and needed no port warned forever. The only way to clear it was to
        # touch the twin - a false claim encoded in a timestamp, and exactly the
        # "accepted noise" that makes a non-zero baseline useless.
        #
        # `ap_reconciled: <primary-sha>` is the twin's auditable claim: "I read the
        # primary at this sha and there is nothing to port." The danger is obvious -
        # a claim mechanism is one bad line away from being an off-switch - so the
        # cases below assert BOTH directions, and the one that matters is case D:
        # the moment the primary genuinely moves, the stamp must go stale and the
        # warning must come back on its own.
        tw = tmp / "twinrepo"
        (tw / ".agents/commands").mkdir(parents=True)
        tcmds = tw / ".agents/commands"

        def tgit(*args: str) -> str:
            r = subprocess.run(["git", *args], cwd=tw, capture_output=True,
                               text=True, errors="replace")
            return r.stdout.strip()

        # ⛔ Commit dates are PINNED, and the first RED run is why. Git timestamps
        # have 1-second resolution, so fixture commits made back-to-back land on the
        # same second and `pr_ts > ap_ts` is false - case B did not fire, and case C
        # then "passed" while proving nothing at all, because the check was silent
        # for a reason that had nothing to do with the stamp. A vacuous green that
        # looks identical to a real one is the failure this whole file guards.
        import os
        _clock = [0]

        def tcommit(msg: str) -> None:
            _clock[0] += 86400
            stamp = f"{1780000000 + _clock[0]} +0000"
            env = {**os.environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
            subprocess.run(["git", "add", "-A"], cwd=tw, capture_output=True)
            subprocess.run(["git", "commit", "-qm", msg], cwd=tw,
                           capture_output=True, env=env)

        tgit("init", "-q")
        tgit("config", "user.email", "t@t.t")
        tgit("config", "user.name", "t")

        def twin_report() -> wf.Report:
            r = wf.Report()
            lint.check_ap_twins(tw, r)
            return r

        def ap_msgs(r: wf.Report) -> str:
            return " ".join(i["msg"] for i in r.items if i["section"] == "ap-twins")

        prim, twin = tcmds / "thing.md", tcmds / "thing-AP.md"
        # The twin names its primary's stem - that is the OTHER drift signal, and
        # leaving it out here would make every case below fire for the wrong reason.
        twin.write_text("---\ndescription: x\n---\n# /thing-AP - modeled off thing\n",
                        encoding="utf-8")
        prim.write_text("---\ndescription: x\n---\n# /thing\nv1\n", encoding="utf-8")
        tcommit("both together")

        # A. Committed together -> nothing to report. If this fires, every later
        #    case is meaningless because the detector is simply always-on.
        c.check("SCC-82 A twins committed together are silent",
                not ap_msgs(twin_report()), ap_msgs(twin_report())[:140])

        # B. POSITIVE CONTROL: primary moves alone -> the check must fire. This is
        #    the behaviour being preserved, not replaced.
        prim.write_text("---\ndescription: x\n---\n# /thing\nv2 changed\n",
                        encoding="utf-8")
        tcommit("primary only")
        c.check("SCC-82 B primary committed after the twin still fires",
                "diff the twin" in ap_msgs(twin_report()), ap_msgs(twin_report())[:140])

        # C. The stamp alone must satisfy it. ⛔ The twin is deliberately NOT
        #    committed here. Committing it would make the twin newer than the
        #    primary, the timestamp path would go quiet by itself, and this case
        #    would pass identically with the feature unbuilt - which is exactly what
        #    the first draft did. Left uncommitted, silence can ONLY come from the
        #    stamp being read.
        prim_sha = tgit("log", "-1", "--format=%H", "--", str(prim))
        stamped_twin = (f"---\ndescription: x\nap_reconciled: {prim_sha}\n---\n"
                        "# /thing-AP - modeled off thing\n")
        twin.write_text(stamped_twin, encoding="utf-8")
        c.check("SCC-82 C ap_reconciled alone silences it, twin history untouched",
                not ap_msgs(twin_report()), ap_msgs(twin_report())[:140])
        tcommit("stamp the twin")

        # D. ⭐ THE CASE THE TICKET EXISTS FOR, and it is built so the OLD check
        #    would call it clean. The primary moves, then the twin is committed
        #    AFTER it while still carrying the old sha - i.e. someone touched the
        #    twin and reset the clock without diffing anything. Timestamps say
        #    "fine"; the stamp says "you reconciled against a primary that no longer
        #    exists". If the stamp were a mute button rather than a claim, this is
        #    where it would show, and it must WARN.
        prim.write_text("---\ndescription: x\n---\n# /thing\nv3 changed again\n",
                        encoding="utf-8")
        tcommit("primary moves again")
        twin.write_text(stamped_twin + "\na cosmetic edit\n", encoding="utf-8")
        tcommit("touch the twin WITHOUT diffing - the cheat this must block")
        ap_ts = tgit("log", "-1", "--format=%ct", "--", str(twin))
        pr_ts = tgit("log", "-1", "--format=%ct", "--", str(prim))
        c.check("SCC-82 D the twin is genuinely NEWER here (the old check saw clean)",
                int(ap_ts) > int(pr_ts), f"twin={ap_ts} primary={pr_ts}")
        c.check("SCC-82 D a stale stamp warns even when the twin is newer",
                "diff the twin" in ap_msgs(twin_report()), ap_msgs(twin_report())[:140])

        # E. A sha that is not the primary's current one is not a claim about
        #    anything - garbage must not buy silence. Twin is newest here too, so
        #    again only the stamp check can produce the warning.
        twin.write_text("---\ndescription: x\nap_reconciled: 0000000000000000000"
                        "000000000000000000000\n---\n# /thing-AP - modeled off thing\n",
                        encoding="utf-8")
        tcommit("bogus stamp")
        c.check("SCC-82 E a bogus ap_reconciled sha does not silence it",
                "diff the twin" in ap_msgs(twin_report()), ap_msgs(twin_report())[:140])

        # F. The pre-existing signals are untouched: a twin that stopped naming its
        #    primary, and a twin with no primary at all.
        # `thing` is a SUBSTRING of `thing-AP`, so a twin that still says its own
        # name trivially contains its primary's stem - the first draft of this case
        # could not fail. The text below names neither.
        twin.write_text(f"---\ndescription: x\nap_reconciled: {prim_sha}\n---\n"
                        "# /renamed-AP - points at nobody\n", encoding="utf-8")
        c.check("SCC-82 F a twin that stopped naming its primary still warns",
                "no longer references" in ap_msgs(twin_report()),
                ap_msgs(twin_report())[:140])
        orphan = tcmds / "orphan-AP.md"
        orphan.write_text("---\ndescription: x\n---\n# /orphan-AP\n", encoding="utf-8")
        r = twin_report()
        c.check("SCC-82 F a twin with no primary is still an ERROR",
                any(i["sev"] == "ERROR" for i in r.items if i["section"] == "ap-twins"),
                ap_msgs(r)[:140])
        orphan.unlink()

        # G. The real repo is the point of the ticket: zero warnings, and the twins
        #    that were never stale must not have been stamped to make that true.
        real = Path(__file__).resolve().parents[3]
        rep = wf.Report()
        lint.check_ap_twins(real, rep)
        c.check("SCC-82 G the live repo's AP twins report nothing",
                not [i for i in rep.items if i["section"] == "ap-twins"],
                str([i["msg"] for i in rep.items])[:200])
        # ⛔ SCC-128 rewrote this assertion, and said so rather than quietly widening a list.
        # It used to be `stamped == ["cicd-code-review-AP.md"]` — a hard-coded snapshot of
        # which twins happened to be stamped that week. SCC-128 edited `cicd-self-audit.md`,
        # which correctly woke this check on ITS twin; that twin was then genuinely diffed
        # (nothing to port) and stamped — the exact behaviour the mechanism exists to
        # reward — and the snapshot failed. A test that reds when someone does the right
        # thing teaches people to stop doing it.
        #
        # What the assertion was actually defending is unchanged and is now stated
        # directly: nobody may buy silence with a bare stamp. Every stamp must be
        # accompanied by a written reason in the same frontmatter — that is what
        # distinguishes "I read the primary and there is nothing to port" from
        # "I pasted a sha to make the linter shut up", and it is the one part a
        # touch-to-silence sweep will not bother to forge. Staleness itself is already
        # covered by the assertion above, which reads every stamp against its primary's
        # current sha.
        stamped = {p.name: wf.read_text(p)
                   for p in sorted((real / ".agents/commands").glob("*-AP.md"))
                   if "ap_reconciled" in wf.read_text(p)}
        unexplained = [n for n, t in stamped.items()
                       if "Diffed against" not in t or "nothing to port" not in t]
        c.check("SCC-82 G every stamped twin records WHY it was reconciled",
                stamped and not unexplained,
                f"stamped={sorted(stamped)} unexplained={unexplained}")

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
