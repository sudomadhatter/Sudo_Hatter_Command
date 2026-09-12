"""repro_receipt.py — a reproduction is a receipt, and a receipt implies execution. (SCC-447 Part 3)

⛔ WHY THIS EXISTS. A lens proves a defect exists in ITS OWN worktree copy, which it may have edited
(SCC-295 measured three of five lenses writing to the builder's tree, one reporting a RED no version
of the real code could produce). Only the door's run on the REAL tree proves it exists in shipping
code. This script is that run: it executes the finding's `reproduce:` command and writes the receipt
from the true exit code. There is no `--result` flag - you cannot hand it a verdict.

Same shape as `gate_receipt.py`, kept separate because a gate receipt is one per gate NAME and a
reproduction is one per FINDING. Real git repos in temp dirs; stdlib only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir, run_script

SCRIPTS = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> str:
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    out = subprocess.run(("git", *args), cwd=repo, env=env, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout.strip()


def _repo(tmp: Path) -> Path:
    repo = tmp / "lane"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-qm", "seed")
    return repo


def main() -> int:
    c = Cases("repro_receipt (SCC-447)")
    PY = sys.executable

    with TempDir() as tmp:
        repo = _repo(tmp)
        head = _git(repo, "rev-parse", "HEAD")
        root = repo / "_artifacts" / "_main" / "2026-09-13_lane"
        root.mkdir(parents=True)

        def run(*args: str) -> tuple[int, str]:
            return run_script("repro_receipt.py", "run", "--root", str(root), "--cwd", str(repo), *args)

        def receipt(fid: str) -> dict:
            # `{}` for an absent receipt, so a missing write is a FAILED: line, not a traceback.
            p = root / "gates" / "repro" / f"{fid}.json"
            return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}

        if c.block("1 · the receipt carries the TRUE exit code and the output tail"):
            code, out = run("--id", "f1", "--", PY, "-c", "import sys; print('boom'); sys.exit(3)")
            r = receipt("f1")
            c.check("1a a command that FAILS is `reproduced`, and the script exits 0",
                    code == 0 and r.get("result") == "reproduced", f"exit={code} result={r.get('result')!r}")
            c.check("1b the receipt records the real exit code, not a claim",
                    r.get("exit_code") == 3, f"exit_code={r.get('exit_code')!r}")
            c.check("1c the output tail is in the receipt", "boom" in (r.get("output_tail") or ""),
                    f"tail={r.get('output_tail')!r}")
            c.check("1d the receipt names the id, the command, the cwd and the sha",
                    r.get("id") == "f1" and r.get("command", [])[-1].endswith("sys.exit(3)")
                    and r.get("cwd") == str(repo) and r.get("sha") == head,
                    f"{ {k: r.get(k) for k in ('id', 'cwd', 'sha')} }")
            c.check("1e a clean tree records dirty_tree=false", r.get("dirty_tree") is False, "")
            c.check("1f the printed line names the id and says REPRODUCED",
                    "f1" in out and "REPRODUCED" in out.upper() and "NOT REPRODUCED" not in out.upper(),
                    out[-200:])

        if c.block("2 · a command that PASSES is not a reproduction"):
            code, out = run("--id", "f2", "--", PY, "-c", "print('fine')")
            r = receipt("f2")
            c.check("2a the receipt says `not-reproduced` with exit 0 recorded",
                    r.get("result") == "not-reproduced" and r.get("exit_code") == 0,
                    f"result={r.get('result')!r} exit_code={r.get('exit_code')!r}")
            c.check("2b the script exits 1 - the finding is DROPPED, and a caller can branch on it",
                    code == 1, f"exit={code}")
            c.check("2c the printed line says NOT REPRODUCED", "NOT REPRODUCED" in out.upper(), out[-200:])

        if c.block("3 · a command that never RAN is `unrunnable`, never a reproduction"):
            # ⛔ THE HOLE THIS CLOSES: a typo'd executable exits 127 - non-zero - and a naive
            # "non-zero means reproduced" would stamp every finding whose command is broken.
            code, out = run("--id", "f3", "--", "no-such-tool-xyz", "--flag")
            r = receipt("f3")
            c.check("3a a missing executable is `unrunnable`, exit 2",
                    code == 2 and r.get("result") == "unrunnable", f"exit={code} result={r.get('result')!r}")
            code, out = run("--id", "f3b", "--", PY, "-c", "import no_such_module_xyz")
            r = receipt("f3b")
            c.check("3b a ModuleNotFoundError in the tail is `unrunnable` too (the SCC-441 shape)",
                    code == 2 and r.get("result") == "unrunnable", f"exit={code} result={r.get('result')!r}")
            # ⛔ Found by SCC-447's own tip review (both Edge Hunters, receipt e2): a house test whose
            # `--case` label matches no block exits 3 and prints `NO CASES RAN ... a filter error, not
            # a result` - non-zero, none of the unrunnable signatures - and it read as `reproduced`.
            # A command that ran zero checks is the very thing "never RAN" means.
            code, out = run("--id", "f3c", "--", PY, "-c",
                            "print('-- 0/0 passed --'); print('NO CASES RAN: no block matched - this is "
                            "a filter error, not a result.'); import sys; sys.exit(3)")
            r = receipt("f3c")
            c.check("3c the harness's NO_MATCH (exit 3, `NO CASES RAN`) is `unrunnable`, never a reproduction",
                    code == 2 and r.get("result") == "unrunnable", f"exit={code} result={r.get('result')!r}")

        if c.block("4 · an existing id refuses without --replace"):
            f1 = root / "gates" / "repro" / "f1.json"
            before = f1.read_text(encoding="utf-8") if f1.is_file() else ""
            code, out = run("--id", "f1", "--", PY, "-c", "print('overwrite')")
            after = f1.read_text(encoding="utf-8") if f1.is_file() else ""
            c.check("4a a second run on the same id is exit 2 and names --replace",
                    code == 2 and "--replace" in out, f"exit={code} {out[-200:]}")
            c.check("4b ...and the first receipt is byte-unchanged", before == after,
                    "a refused write must not touch the file")
            code, out = run("--id", "f1", "--replace", "--", PY, "-c", "print('overwrite')")
            c.check("4c with --replace it is rewritten from the new run",
                    code == 1 and receipt("f1").get("result") == "not-reproduced",
                    f"exit={code} result={receipt('f1').get('result')!r}")

        if c.block("5 · a dirty tree is recorded, and the writer's own output is not dirt"):
            # The receipts written above sit under `_artifacts/.../gates/repro/` INSIDE the repo
            # and are untracked. They are this writer's own output, so they are not dirt (the
            # SCC-178 rule gate_receipt already holds) - block 1e proved a clean read with none,
            # this proves the read stays clean with them present.
            code, _ = run("--id", "f5", "--", PY, "-c", "import sys; sys.exit(1)")
            c.check("5a earlier receipts under gates/repro/ do not make the tree dirty",
                    receipt("f5").get("dirty_tree") is False, str(receipt("f5").get("dirty_tree")))
            (repo / "stray.txt").write_text("uncommitted\n", encoding="utf-8")
            code, _ = run("--id", "f5b", "--", PY, "-c", "import sys; sys.exit(1)")
            c.check("5b a real untracked file IS recorded as dirty",
                    receipt("f5b").get("dirty_tree") is True, str(receipt("f5b").get("dirty_tree")))
            (repo / "stray.txt").unlink()

        if c.block("6 · there is no way to hand it a verdict"):
            code, out = run("--id", "f6", "--result", "reproduced", "--", PY, "-c", "pass")
            c.check("6a `--result` is rejected by the parser",
                    code == 2 and "unrecognized" in out.lower() and not (root / "gates/repro/f6.json").exists(),
                    f"exit={code} {out[-200:]}")
            code, out = run("--id", "f6b")
            c.check("6b no command after `--` is exit 2, and no receipt is written",
                    code == 2 and not (root / "gates/repro/f6b.json").exists(), f"exit={code} {out[-200:]}")
            code, out = run_script("repro_receipt.py", "run", "--root", str(root), "--id", "f6c",
                                   "--", PY, "-c", "pass")
            c.check("6c `--cwd` is REQUIRED - without it the command would run wherever the caller "
                    "stood and record a result about nothing (SCC-154)",
                    code == 2 and "--cwd" in out and not (root / "gates/repro/f6c.json").exists(),
                    f"exit={code} {out[-200:]}")
            # ⛔ Found by the SCC-447 tip review (Test-Adequacy lens, receipt t3): the guard existed
            # and nothing pinned it. Without it the receipt lands with `sha: null` and the run dies
            # exit 1 - which a door reads as NOT reproduced while a `reproduced` receipt sits on
            # disk. Two evidence surfaces disagreeing is worse than either alone.
            nogit = tmp / "not-a-repo"
            nogit.mkdir()
            code, out = run_script("repro_receipt.py", "run", "--root", str(root), "--id", "f6d",
                                   "--cwd", str(nogit), "--", PY, "-c", "import sys; sys.exit(3)")
            c.check("6d a `--cwd` outside any git tree is refused, exit 2, and no receipt is written",
                    code == 2 and "git" in out.lower() and not (root / "gates/repro/f6d.json").exists(),
                    f"exit={code} {out[-200:]}")

        # ── 7. the id is a FILENAME segment, never a path ───────────────────────────────
        # The id is copied off a walkthrough row (`repro <id>`) and joined verbatim onto
        # `<root>/gates/repro/`, so it is the only thing keeping the receipt where the roster
        # gate looks. Found by the SCC-447 tip review (receipt t2): the guard existed, unpinned.
        if c.block("7 · a finding id is a filename segment, never a path"):
            for bad in ("../../escape", "f 1", "a/b"):
                code, out = run("--id", bad, "--", PY, "-c", "import sys; sys.exit(3)")
                c.check(f"7 `--id {bad!r}` is refused, exit 2, nothing written",
                        code == 2 and "finding id" in out
                        and not (root / "escape.json").exists()
                        and not (root / "gates/repro/escape.json").exists()
                        and not (root / "gates/repro/f 1.json").exists()
                        and not (root / "gates/repro/a/b.json").exists(),
                        f"exit={code} {out[-200:]}")
            code, out = run("--id", "ok-id_7.a", "--", PY, "-c", "import sys; sys.exit(3)")
            c.check("7 (control) a legal id with `.`, `-` and `_` still runs and reproduces",
                    code == 0 and receipt("ok-id_7.a").get("result") == "reproduced",
                    f"exit={code} {out[-200:]}")

        # ── 8. an operator-bearing command runs through a shell, and the WHOLE line's exit counts ──
        # ⛔ Found by the SCC-447 tip review (Edge Hunter, receipt x3): the door's shell parses
        # `-- python3 -c "..." | grep -q X` BEFORE this script starts, so only the left-hand stage
        # reached the writer and the receipt attested to a command the lens never wrote. A lens
        # command with an operator is passed as ONE argument and run through `bash -c`.
        if c.block("8 · a single argument carrying a shell operator runs through a shell, whole"):
            code, out = run("--id", "f8", "--", "python3 -c 'print(\"ERROR\")' | grep -q NOPE")
            r = receipt("f8")
            c.check("8a `... | grep -q NOPE` is one command, the pipeline's exit (1) is the result, reproduced",
                    code == 0 and r.get("result") == "reproduced" and r.get("exit_code") == 1,
                    f"exit={code} result={r.get('result')!r} exit_code={r.get('exit_code')!r}")
            code, out = run("--id", "f8b", "--", "python3 -c 'print(\"ERROR\")' | grep -q ERROR")
            r = receipt("f8b")
            c.check("8b (control) the same pipeline whose right-hand stage passes is not-reproduced",
                    code == 1 and r.get("result") == "not-reproduced", f"exit={code} result={r.get('result')!r}")
            c.check("8c the receipt records the WHOLE line as the command",
                    r.get("command") == ["bash", "-c", "python3 -c 'print(\"ERROR\")' | grep -q ERROR"],
                    f"command={r.get('command')!r}")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
