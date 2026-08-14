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
        finally:
            os.chdir(prev_cwd)
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
