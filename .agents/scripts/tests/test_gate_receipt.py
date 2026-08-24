"""gate_receipt.py must make a fabricated gate result impossible.

The positive case is trivial; the load-bearing cases are negative — a failing command, a
missing tool, a claimed-but-never-run gate, and a receipt that goes stale the moment HEAD
moves. Needs a real commit graph, so it builds a throwaway git repo.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir, run_script

BOARD_REL = Path("_bmad-output/implementation-artifacts/sprint-status.yaml")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def build(root: Path) -> Path:
    repo = root / "repo"
    (repo / BOARD_REL.parent).mkdir(parents=True)
    (repo / BOARD_REL).write_text("development_status:\n  21-8b-x: review\n", encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    git(repo, "add", str(BOARD_REL).replace("\\", "/"))
    git(repo, "commit", "-qm", "seed")
    return repo


def main() -> int:
    c = Cases("gate_receipt")
    if c.block("gate_receipt · core: stamp, verify, staleness and the dirty_paths readback"):
        with TempDir() as tmp:
            repo = build(tmp)

            def gr(*args: str) -> tuple[int, str]:
                # every flag precedes `--`; anything after it is the gate command verbatim
                return run_script("gate_receipt.py", args[0], "--project", str(repo), *args[1:])

            def receipt(gate: str) -> dict:
                return json.loads((repo / "_bmad-output" / "gates" / "21-8b" / f"{gate}.json")
                                  .read_text(encoding="utf-8"))

            code, _ = gr("run", "--story", "21.8b", "--gate", "green",
                         "--", sys.executable, "-c", "print('ok')")
            r = receipt("green")
            c.check("1 passing cmd -> pass", code == 0 and r["result"] == "pass", f"exit={code}")

            code, _ = gr("run", "--story", "21.8b", "--gate", "pytest", "--", sys.executable, "-c",
                         "import sys; print('=== 3 failed, 275 passed in 12.0s ==='); sys.exit(1)")
            r = receipt("pytest")
            c.check("2 failing cmd -> fail, never pass",
                    code == 1 and r["result"] == "fail", f"exit={code} result={r['result']}")
            c.check("2b totals quoted from the tool's own summary",
                    r["totals"] == "3 failed, 275 passed in 12.0s", f"totals={r['totals']!r}")

            # --warn-exit: a tool that GRADES its own findings keeps that grading. Without it
            # an all-warnings workflow_lint reads `fail` in the verdict and the gate is ignored.
            code, _ = gr("run", "--story", "21.8b", "--gate", "lintwarn", "--warn-exit", "1",
                         "--", sys.executable, "-c",
                         "import sys; print('-- 0 error(s), 3 warning(s) --'); sys.exit(1)")
            c.check("2c --warn-exit: warnings are `warn`, non-blocking, never `pass`",
                    code == 0 and receipt("lintwarn")["result"] == "warn",
                    f"exit={code} result={receipt('lintwarn')['result']}")
            # ...and the SAME flag must not launder a real error exit into advisory
            code, _ = gr("run", "--story", "21.8b", "--gate", "linterr", "--warn-exit", "1",
                         "--", sys.executable, "-c",
                         "import sys; print('-- 2 error(s) --'); sys.exit(2)")
            c.check("2d --warn-exit does NOT launder a real failure",
                    code == 1 and receipt("linterr")["result"] == "fail", f"exit={code}")
            # and without the flag the old collapse still applies (no silent behaviour change)
            code, _ = gr("run", "--story", "21.8b", "--gate", "nolabel",
                         "--", sys.executable, "-c", "import sys; sys.exit(1)")
            c.check("2e without --warn-exit, exit 1 is still `fail`",
                    receipt("nolabel")["result"] == "fail", "")

            code, _ = gr("run", "--story", "21.8b", "--gate", "ruff",
                         "--", "definitely-not-a-real-binary-xyz", "check")
            c.check("3 missing tool -> unrunnable (a finding, not a skip)",
                    code == 2 and receipt("ruff")["result"] == "unrunnable", f"exit={code}")

            code, _ = gr("run", "--story", "21.8b", "--gate", "pyrefly",
                         "--", sys.executable, "-c", "import nope_not_here")
            c.check("3b missing module -> unrunnable",
                    receipt("pyrefly")["result"] == "unrunnable", "")

            code, _ = gr("check", "--story", "21.8b", "--require", "green")
            c.check("4 check green at HEAD -> 0", code == 0, f"exit={code}")

            code, out = gr("check", "--story", "21.8b", "--require", "green,pytest")
            c.check("5 a failed gate blocks", code == 2 and "result=fail" in out, f"exit={code}")

            code, out = gr("check", "--story", "21.8b", "--require", "green,vitest")
            c.check("6 a claimed-but-unrun gate blocks",
                    code == 2 and "NO RECEIPT" in out, f"exit={code}")

            code, out = gr("check", "--story", "21.8b", "--require", "green,vitest", "--advisory")
            c.check("7 --advisory reports without blocking",
                    code == 0 and "NO RECEIPT" in out and "ADVISORY" in out, f"exit={code}")

            (repo / "newfile.txt").write_text("x", encoding="utf-8")
            git(repo, "add", "newfile.txt")
            git(repo, "commit", "-qm", "second")
            code, out = gr("check", "--story", "21.8b", "--require", "green")
            c.check("8 HEAD moves -> the receipt is STALE",
                    code == 2 and "STALE" in out, f"exit={code}")

            (repo / "dirty.txt").write_text("y", encoding="utf-8")
            gr("run", "--story", "21.8b", "--gate", "dirtygate",
               "--", sys.executable, "-c", "print('ok')")
            c.check("9a a dirty tree is recorded", receipt("dirtygate")["dirty_tree"] is True, "")
            code, out = gr("check", "--story", "21.8b", "--require", "dirtygate")
            c.check("9b a dirty tree warns rather than silently passing",
                    code == 1 and "DIRTY" in out, f"exit={code}")

            # ── 9c-9e · dirty_paths READBACK: what the recorder writes is what the tree holds ──
            # (SCC-154 review #7, ledgered; fixed in-thread SCC-160). The line-form parse kept
            # git's C-quoting on a non-ASCII name and dropped a rename's OLD side. The reader
            # (`task_preflight`) exempts `_artifacts/`-only dirt from staling a receipt, so a
            # misread decides whether a gate SKIP is authorized. Direction, measured: a quoted
            # artifacts path was NOT exempted (safe, but a false full-gate); a rename OUT of
            # code INTO `_artifacts/` recorded only the artifacts side and WOULD have exempted
            # moved code (unsafe). Both are pinned on exact filenames now.
            (repo / "dirty.txt").unlink()
            art = repo / "_artifacts"
            art.mkdir()
            (art / "caf\u00e9 notes.md").write_text("é\n", encoding="utf-8")   # non-ASCII + space
            git(repo, "add", "_artifacts")     # staged, so the path itself is listed (not the dir)
            # The fixture's receipts dir (`_bmad-output/gates/`) is itself untracked dirt in
            # every case here; it is filtered so the assertions read only the planted paths.
            def planted(gate: str) -> list[str]:
                return [x for x in receipt(gate)["dirty_paths"]
                        if not x.startswith("_bmad-output/")]
            gr("run", "--story", "21.8b", "--gate", "quoted",
               "--", sys.executable, "-c", "print('ok')")
            got = planted("quoted")
            c.check("9c a non-ASCII filename is recorded UNQUOTED, exactly",
                    got == ["_artifacts/caf\u00e9 notes.md"], f"got={got!r}")
            git(repo, "rm", "-q", "--cached", "_artifacts/caf\u00e9 notes.md")
            (art / "caf\u00e9 notes.md").unlink()

            (repo / "code.py").write_text("x = 1\n", encoding="utf-8")
            git(repo, "add", "code.py")
            git(repo, "commit", "-qm", "code")
            git(repo, "mv", "code.py", "_artifacts/moved.md")       # staged rename OUT of code
            gr("run", "--story", "21.8b", "--gate", "renamed",
               "--", sys.executable, "-c", "print('ok')")
            got = planted("renamed")
            c.check("9d a staged rename records BOTH sides (the code side is dirt too)",
                    sorted(got) == ["_artifacts/moved.md", "code.py"], f"got={got!r}")
            c.check("9e ...so an `_artifacts/`-only exemption cannot fire on moved code",
                    not all(str(x).startswith("_artifacts/") for x in got), f"got={got!r}")
            git(repo, "mv", "_artifacts/moved.md", "code.py")       # put it back for later cases
            git(repo, "reset", "-q")

            code, out = gr("run", "--story", "21.8b", "--gate", "x", "--result", "pass",
                           "--", sys.executable, "-c", "print(1)")
            c.check("10 there is no way to hand in a verdict",
                    code != 0 and "unrecognized" in out.lower(), f"exit={code}")

            # ── F5: staleness is a property of the TREE, not of the sha ───────────
            # A story branch that lands via a merge commit produces a new HEAD with an
            # identical tree. Calling that stale blocks every honest receipt, and a hard
            # gate that always blocks gets `--advisory` forever.
            git(repo, "add", "-A")          # earlier cases left the tree dirty on purpose
            git(repo, "commit", "-qm", "settle")
            trunk = git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
            git(repo, "checkout", "-qb", "sidebranch")
            (repo / "story_work.txt").write_text("the story's change\n", encoding="utf-8")
            git(repo, "add", "story_work.txt")
            git(repo, "commit", "-qm", "story work")
            gr("run", "--story", "21.8b", "--gate", "treegate", "--", sys.executable, "-c", "print(1)")
            side_sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            git(repo, "checkout", "-q", trunk)
            # --no-ff: a real merge commit, so HEAD differs while the tree is identical
            git(repo, "merge", "-q", "--no-ff", "-m", "merge story", "sidebranch")
            head_after_merge = git(repo, "rev-parse", "HEAD").stdout.strip()
            code, out = gr("check", "--story", "21.8b", "--require", "treegate")
            c.check("12 a merge commit with an identical tree is NOT stale",
                    code == 0 and side_sha != head_after_merge and "identical tree" in out,
                    f"exit={code} {out.splitlines()[-2] if out else ''}")

            code, out = gr("check", "--story", "21.8b", "--require", "treegate",
                           "--sha", side_sha)
            c.check("13 --sha pins the comparison to the shipping commit",
                    code == 0 and "STALE" not in out, f"exit={code}")

            (repo / "backend.py").write_text("real change\n", encoding="utf-8")
            git(repo, "add", "backend.py")
            git(repo, "commit", "-qm", "a real code change")
            code, out = gr("check", "--story", "21.8b", "--require", "treegate")
            c.check("14 a genuine content change IS still stale",
                    code == 2 and "STALE" in out, f"exit={code}")

            code, out = gr("check", "--story", "21.8b", "--require", "treegate",
                           "--sha", "0" * 40)
            c.check("15 an unknown target sha warns, never silently passes",
                    "CANNOT verify" in out, out.strip().splitlines()[-2] if out else "")

            # a commit landing mid-run means the receipt describes no single tree
            code, _ = gr("run", "--story", "21.8b", "--gate", "moving", "--", sys.executable, "-c",
                         f"import subprocess,pathlib;"
                     f"p=pathlib.Path(r'{repo}');"
                     f"(p/'mid.txt').write_text('m');"
                     f"subprocess.run(['git','add','mid.txt'],cwd=str(p));"
                     f"subprocess.run(['git','commit','-qm','mid'],cwd=str(p))")
            c.check("11 HEAD moving mid-run -> unrunnable",
                    receipt("moving")["result"] == "unrunnable",
                    f"result={receipt('moving')['result']}")

    # ── SCC-146: the Task lane — receipts in a repo with NO board anywhere ─────────
    # The lobby has `_bmad-output/` but no board file, by definition: Task work has no
    # sprint board, and resolve_project_root() dies without one. `--root` must bypass
    # the resolver entirely and land the receipt at <root>/gates/<gate>.json, so the
    # Task close-out reads the same evidence the story lane gets.
    #
    # cwd is pinned INSIDE the temp dir for this block: a mutant that quietly falls
    # back to the resolver must die "no project resolved" — never walk up from the
    # tests directory, resolve a REAL project on this machine, and write into it.
    import os
    prev_cwd = os.getcwd()
    if c.block("SCC-146/154 · the Task lane: --root with no board anywhere, and root-mode hardening"):
        with TempDir() as tmp2:
            try:
                lobby = tmp2 / "lobby"
                lobby.mkdir()
                git(lobby, "init", "-q")
                git(lobby, "config", "user.email", "t@t.t")
                git(lobby, "config", "user.name", "t")
                (lobby / "README.md").write_text("# no board here\n", encoding="utf-8")
                git(lobby, "add", "README.md")
                git(lobby, "commit", "-qm", "seed")
                aroot = lobby / "_artifacts" / "_main" / "2026-08-14_thing"
                aroot.mkdir(parents=True)
                os.chdir(lobby)

                def root_receipt() -> dict:
                    return json.loads((aroot / "gates" / "suite.json")
                                      .read_text(encoding="utf-8"))

                # A1 — and --task is the alias for --story: same field, no schema churn.
                code, out = run_script("gate_receipt.py", "run", "--task", "SCC-00",
                                       "--gate", "suite", "--root", str(aroot),
                                       "--cwd", str(lobby),
                                       "--", sys.executable, "-c", "print('ok')")
                wrote = code == 0 and (aroot / "gates" / "suite.json").is_file()
                c.check("16 SCC-146 --root: receipt lands at <root>/gates/<gate>.json, no board",
                        wrote and root_receipt()["result"] == "pass",
                        f"exit={code} " + out.strip()[-150:])
                c.check("16b SCC-146 --task aliases --story (same receipt field)",
                        wrote and root_receipt()["story"] == "scc-00",
                        root_receipt()["story"] if wrote else "(no receipt)")

                # A2 — the control that makes 16 a BYPASS, not a new resolver default:
                # the same boardless repo WITHOUT --root still dies in the resolver.
                code, out = run_script("gate_receipt.py", "run", "--story", "SCC-00",
                                       "--gate", "suite", "--project", str(lobby),
                                       "--", sys.executable, "-c", "print('ok')")
                c.check("17 SCC-146 without --root the boardless repo still cannot resolve",
                        code == 2 and "cannot resolve project" in out,
                        f"exit={code} " + out.strip()[-150:])

                # A3 in root mode: fresh passes, a content change is STALE, --sha re-pins.
                code, out = run_script("gate_receipt.py", "check", "--task", "SCC-00",
                                       "--require", "suite", "--root", str(aroot),
                                       "--cwd", str(lobby))
                c.check("18 SCC-146 check --root: fresh receipt at HEAD -> 0",
                        code == 0, f"exit={code}")
                orig_sha = git(lobby, "rev-parse", "HEAD").stdout.strip()
                (lobby / "code.py").write_text("x = 1\n", encoding="utf-8")
                git(lobby, "add", "code.py")
                git(lobby, "commit", "-qm", "code moved")
                code, out = run_script("gate_receipt.py", "check", "--task", "SCC-00",
                                       "--require", "suite", "--root", str(aroot),
                                       "--cwd", str(lobby))
                c.check("18b SCC-146 check --root: content moved -> STALE, exit 2",
                        code == 2 and "STALE" in out, f"exit={code}")
                code, out = run_script("gate_receipt.py", "check", "--task", "SCC-00",
                                       "--require", "suite", "--root", str(aroot),
                                       "--cwd", str(lobby), "--sha", orig_sha)
                c.check("18c SCC-146 check --root --sha pins to the shipping commit",
                        code == 0 and "STALE" not in out, f"exit={code}")

                # list --root reads what run --root wrote.
                code, out = run_script("gate_receipt.py", "list", "--task", "SCC-00",
                                       "--root", str(aroot))
                c.check("19 SCC-146 list --root reads the root-mode receipts",
                        code == 0 and "suite" in out, f"exit={code} " + out.strip()[-100:])

                # ── SCC-154: root-mode hardening (review finding 5 / compound C5, finding 13) ──
                # 20 — run --root WITHOUT --cwd must DIE, not execute the gate inside the
                # artifacts dir and record `fail` for a suite that never ran.
                code, out = run_script("gate_receipt.py", "run", "--task", "SCC-00",
                                       "--gate", "nocwd", "--root", str(aroot),
                                       "--", sys.executable, "-c", "print('ok')")
                c.check("20 SCC-154 run --root without --cwd dies, naming the requirement",
                        code == 2 and "requires --cwd" in out
                        and not (aroot / "gates" / "nocwd.json").is_file(),
                        f"exit={code} " + out.strip()[-150:])

                # 21 — a RELATIVE --root resolves against --cwd, never the invoker's cwd: from
                # the wrong checkout the receipt landed as an untracked stray with
                # success-shaped output.
                os.chdir(tmp2)      # the invoker's cwd is deliberately NOT the repo
                code, out = run_script("gate_receipt.py", "run", "--task", "SCC-00",
                                       "--gate", "rel", "--root",
                                       "_artifacts/_main/2026-08-14_thing", "--cwd", str(lobby),
                                       "--", sys.executable, "-c", "print('ok')")
                stray = tmp2 / "_artifacts" / "_main" / "2026-08-14_thing" / "gates" / "rel.json"
                c.check("21 SCC-154 a relative --root resolves against --cwd, not invoker cwd",
                        code == 0 and (aroot / "gates" / "rel.json").is_file()
                        and not stray.is_file(),
                        f"exit={code} " + out.strip()[-150:])
                os.chdir(lobby)

                # 22 — --project beside --root is a contradiction, not a preference.
                code, out = run_script("gate_receipt.py", "run", "--task", "SCC-00",
                                       "--gate", "both", "--root", str(aroot),
                                       "--project", str(lobby), "--cwd", str(lobby),
                                       "--", sys.executable, "-c", "print('ok')")
                c.check("22 SCC-154 --project and --root together are refused",
                        code == 2 and "mutually exclusive" in out,
                        f"exit={code} " + out.strip()[-150:])
            finally:
                os.chdir(prev_cwd)

    # ── SCC-178 (Part J): the writer stops measuring its OWN output as tree dirt ─────────
    # `dirty_paths` came from `git status --porcelain -z` over the WHOLE tree, and the
    # receipt lands INSIDE that tree at `<root>/gates/<gate>.json`. So the SECOND stamp of
    # a lane reads DIRTY because the FIRST one's receipt is untracked — the writer dirtying
    # the tree it is measuring. Every lane then paid a second full suite run to clear a
    # smudge it had made itself (SCC-163 self-audit: six suite runs, ~9.5 min, two of them
    # this). The exemption is the writer's OWN output DIRECTORY and nothing else: not
    # `_artifacts/`, not `gates/` anywhere, not a sibling of it. Cases J3a-J3d are the
    # controls that say so, and 9c-9e above are the reason the field has to stay honest —
    # `task_preflight` reads `dirty_paths` to decide whether a gate SKIP is authorized.
    if c.block("SCC-178: gate_receipt stops counting its own gates/ output as dirt"):
        prev_cwd = os.getcwd()
        with TempDir() as tmp3:
            try:
                lob = tmp3 / "lane"
                lob.mkdir()
                git(lob, "init", "-q")
                git(lob, "config", "user.email", "t@t.t")
                git(lob, "config", "user.name", "t")
                root = lob / "_artifacts" / "_main" / "2026-08-15_j"
                root.mkdir(parents=True)
                (lob / "code.py").write_text("x = 1\n", encoding="utf-8")
                # The plan is COMMITTED, as it is in a real lane. Without that, git collapses
                # the whole untracked `_artifacts/` into one entry and the receipt dir is
                # never named — the fixture would pass with the fix reverted.
                (root / "implementation_plan.md").write_text("# plan\n", encoding="utf-8")
                git(lob, "add", "-A")
                git(lob, "commit", "-qm", "seed")
                os.chdir(lob)
                relroot = "_artifacts/_main/2026-08-15_j"

                def stamp(gate: str) -> dict:
                    run_script("gate_receipt.py", "run", "--task", "SCC-178",
                               "--gate", gate, "--root", str(root), "--cwd", str(lob),
                               "--", sys.executable, "-c", "print('ok')")
                    return json.loads((root / "gates" / f"{gate}.json")
                                      .read_text(encoding="utf-8"))

                first = stamp("suite")
                c.check("J0 the first stamp on a clean tree is clean (baseline, not the bug)",
                        first["dirty_tree"] is False, f"paths={first['dirty_paths']!r}")

                # J1 — THE DEFECT. The only dirt in this tree is `suite.json`, which the
                # previous line wrote. Today: dirty_tree True.
                second = stamp("lint")
                c.check("J1 a tree whose ONLY dirt is a prior receipt is NOT dirty",
                        second["dirty_tree"] is False, f"paths={second['dirty_paths']!r}")
                c.check("J2 dirty_paths never names a path under the receipt's own gates/",
                        not [p for p in second["dirty_paths"]
                             if p.startswith(f"{relroot}/gates")],
                        f"paths={second['dirty_paths']!r}")

                # ── J3 · the controls. Each one dies if the exemption is widened. ──
                (root / "notes.md").write_text("a sibling of gates/, not gates/\n",
                                               encoding="utf-8")
                sib = stamp("sibling")
                c.check("J3a a sibling file under <root>/ that is not gates/ is still DIRTY",
                        sib["dirty_tree"] is True
                        and f"{relroot}/notes.md" in sib["dirty_paths"],
                        f"paths={sib['dirty_paths']!r}")
                (root / "notes.md").unlink()

                (lob / "code.py").write_text("x = 2\n", encoding="utf-8")
                cod = stamp("code")
                c.check("J3b a modified code file is still DIRTY",
                        cod["dirty_tree"] is True and "code.py" in cod["dirty_paths"],
                        f"paths={cod['dirty_paths']!r}")
                git(lob, "checkout", "--", "code.py")

                # J3c — the `_artifacts/`-wide mutant killer: real dirt INSIDE the artifacts
                # tree, beside receipts that are exempt. A widened exemption swallows both
                # and this reads clean.
                other = lob / "_artifacts" / "_main" / "2026-08-15_other"
                other.mkdir(parents=True)
                (other / "stray.md").write_text("another lane's dirt\n", encoding="utf-8")
                art = stamp("artifacts")
                c.check("J3c dirt elsewhere under _artifacts/ is still DIRTY "
                        "(the exemption is the gates dir, not the folder)",
                        art["dirty_tree"] is True
                        and any(p.startswith("_artifacts/_main/2026-08-15_other")
                                for p in art["dirty_paths"]),
                        f"paths={art['dirty_paths']!r}")
                import shutil
                shutil.rmtree(other)

                # J3d — the prefix is anchored on the directory boundary. A sibling whose
                # NAME merely starts with `gates` is not the writer's output.
                (root / "gates_old").mkdir()
                (root / "gates_old" / "keep.json").write_text("{}\n", encoding="utf-8")
                (root / "gatesnotes.md").write_text("not the gates dir\n", encoding="utf-8")
                near = stamp("near")
                c.check("J3d a sibling merely NAMED like gates/ is still DIRTY "
                        "(prefix anchored on the dir boundary, not startswith('gates'))",
                        near["dirty_tree"] is True
                        and any(p.startswith(f"{relroot}/gates_old") for p in near["dirty_paths"])
                        and f"{relroot}/gatesnotes.md" in near["dirty_paths"],
                        f"paths={near['dirty_paths']!r}")
                shutil.rmtree(root / "gates_old")
                (root / "gatesnotes.md").unlink()

                # J3e — story lane: same fix, and the exemption is THIS story's receipt dir.
                # Another story's receipts are somebody else's output and stay dirt.
                board = lob / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
                board.parent.mkdir(parents=True)
                board.write_text("development_status:\n  21-8b-x: review\n", encoding="utf-8")
                git(lob, "add", "-A")
                git(lob, "commit", "-qm", "board")

                def story_stamp(gate: str, story: str = "21.8b") -> dict:
                    run_script("gate_receipt.py", "run", "--story", story, "--gate", gate,
                               "--project", str(lob),
                               "--", sys.executable, "-c", "print('ok')")
                    sid = story.replace(".", "-")
                    return json.loads((lob / "_bmad-output" / "gates" / sid / f"{gate}.json")
                                      .read_text(encoding="utf-8"))

                story_stamp("one")
                s2 = story_stamp("two")
                c.check("J3f the story lane gets the same exemption "
                        "(_bmad-output/gates/<story>/)",
                        s2["dirty_tree"] is False, f"paths={s2['dirty_paths']!r}")
                s3 = story_stamp("first", story="99.9z")
                c.check("J3g ...but ANOTHER story's receipts are not this writer's output",
                        s3["dirty_tree"] is True
                        and any("gates/21-8b/" in p for p in s3["dirty_paths"]),
                        f"paths={s3['dirty_paths']!r}")
            finally:
                os.chdir(prev_cwd)

    if c.block("SCC-309/317: -q totals are quoted, and a worktree lane's receipts live IN the lane"):
        with TempDir() as tmp:
            repo = build(tmp)

            def gr(*args: str) -> tuple[int, str]:
                return run_script("gate_receipt.py", *args)

            def receipt_at(base: Path, gate: str) -> dict:
                return json.loads((base / "_bmad-output" / "gates" / "21-8b" / f"{gate}.json")
                                  .read_text(encoding="utf-8"))

            # SCC-309: pytest under -q prints the summary BARE (no === banner). The banner
            # pattern misses it and totals fell through to null while result recorded pass -
            # the one field downstream certification derives from, silently absent.
            code, _ = gr("run", "--story", "21.8b", "--gate", "quiet", "--project", str(repo),
                         "--", sys.executable, "-c",
                         "print('3043 passed, 35 skipped, 547 warnings in 9.14s')")
            r = receipt_at(repo, "quiet")
            c.check("Q1 a -q bare summary is quoted into totals, not dropped",
                    code == 0 and r["totals"] == "3043 passed, 35 skipped, 547 warnings in 9.14s",
                    f"exit={code} totals={r['totals']!r}")

            code, _ = gr("run", "--story", "21.8b", "--gate", "quietfail", "--project", str(repo),
                         "--", sys.executable, "-c",
                         "import sys; print('3 failed, 275 passed in 12.0s'); sys.exit(1)")
            r = receipt_at(repo, "quietfail")
            c.check("Q2 the failed-first -q form is quoted too",
                    r["totals"] == "3 failed, 275 passed in 12.0s", f"totals={r['totals']!r}")

            # Absence must STAY possible - a fabricated count is worse than an absent one.
            code, _ = gr("run", "--story", "21.8b", "--gate", "nosummary", "--project", str(repo),
                         "--", sys.executable, "-c", "print('did some stuff, no summary line')")
            r = receipt_at(repo, "nosummary")
            c.check("Q3 output with no recognisable summary still records null",
                    r["totals"] is None, f"totals={r['totals']!r}")

            # SCC-317: --project resolves the MAIN checkout, so a worktree lane's receipt was
            # written into the shared tree - it never rode the lane's branch, left the shared
            # checkout dirty, and `check` reported NO RECEIPT for a receipt that exists.
            wt = tmp / "lane"
            git(repo, "worktree", "add", "-q", str(wt), "-b", "lane")
            code, out = gr("run", "--story", "21.8b", "--gate", "suite",
                           "--project", str(repo), "--cwd", str(wt),
                           "--", sys.executable, "-c", "print('ok')")
            in_lane = (wt / "_bmad-output" / "gates" / "21-8b" / "suite.json").is_file()
            in_main = (repo / "_bmad-output" / "gates" / "21-8b" / "suite.json").is_file()
            c.check("W1 run --project + --cwd <worktree> writes the receipt INSIDE the worktree",
                    code == 0 and in_lane and not in_main,
                    f"exit={code} in_lane={in_lane} in_main={in_main}")

            code, out = gr("check", "--story", "21.8b", "--require", "suite",
                           "--project", str(repo), "--cwd", str(wt))
            c.check("W2 check with the same flags FINDS the lane's receipt (exit 0)",
                    code == 0, f"exit={code}\n{out[-300:]}")

            # A --cwd inside the MAIN checkout keeps today's behaviour byte-identical.
            sub = repo / "subdir"
            sub.mkdir()
            code, _ = gr("run", "--story", "21.8b", "--gate", "athome",
                         "--project", str(repo), "--cwd", str(repo),
                         "--", sys.executable, "-c", "print('ok')")
            c.check("W3 a --cwd at the project root still lands receipts in the project",
                    code == 0 and (repo / "_bmad-output" / "gates" / "21-8b" / "athome.json").is_file(),
                    f"exit={code}")

            # A --cwd in a DIFFERENT repo is ambiguity: refuse and NAME both trees -
            # silently picking one is the measured defect, just mirrored.
            other = tmp / "other"
            other.mkdir()
            git(other, "init", "-q")
            git(other, "config", "user.email", "t@t.t")
            git(other, "config", "user.name", "t")
            (other / "f.txt").write_text("x\n", encoding="utf-8")
            git(other, "add", "f.txt")
            git(other, "commit", "-qm", "seed")
            code, out = gr("run", "--story", "21.8b", "--gate", "foreign",
                           "--project", str(repo), "--cwd", str(other),
                           "--", sys.executable, "-c", "print('ok')")
            c.check("W4 a --cwd in a DIFFERENT repo refuses and names both trees",
                    code != 0 and str(repo.name) in out and str(other.name) in out,
                    f"exit={code}\n{out[-300:]}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
