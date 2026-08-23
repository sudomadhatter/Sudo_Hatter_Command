"""mutation_sweep.py — the sweep's own end-state check, made mechanical (SCC-179).

The doctrine was prose in two files (`smh-quick-dev.md`, `tests-must-gate-for-real.md`) and
every clause of it was self-reported. It failed live twice: SCC-144's timeout-killed sweep
left residue, and 8681d83 shipped a LIVE MUTANT into the gate because the scoped `--case`
re-runs never exercised the mutated pattern. Both are things a script can check and a
paragraph cannot.

The fixture is a throwaway git repo with a two-line "source" file and a stand-in test script
whose exit code and `FAILED:` line the case controls directly. That is deliberate: the sweep's
contract is with the HARNESS PROTOCOL (0 = survived, non-zero = killed, 3 = the filter selected
nothing, and the `FAILED:` line is what attributes the kill), not with any particular test
file, and a fixture that imports `_harness` would prove the harness agrees with itself.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from _harness import Cases, TempDir

SRC = "src.py"
PATTERN = 'if flag == "on":'


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def build(root: Path) -> Path:
    """A repo holding one source file and one stand-in test, both committed."""
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    (repo / SRC).write_text(f'def gate(flag):\n    {PATTERN}\n        return 1\n    return 0\n',
                            encoding="utf-8")
    # The stand-in test: it READS the source and decides its own verdict, so a mutant really
    # does change the outcome. `--case` selects which label it reports under.
    (repo / "t.py").write_text(
        "import sys, pathlib\n"
        "argv = sys.argv[1:]\n"
        "case = argv[argv.index('--case') + 1] if '--case' in argv else None\n"
        "src = pathlib.Path(__file__).parent.joinpath('src.py').read_text()\n"
        "labels = ['CASE-A pattern intact', 'CASE-B unrelated']\n"
        "sel = [l for l in labels if case is None or case.lower() in l.lower()]\n"
        "if case is not None and not sel:\n"
        "    print('NO CASES RAN: no block matched'); sys.exit(3)\n"
        "bad = [l for l in sel if l.startswith('CASE-A') and " + repr(PATTERN) + " not in src]\n"
        "for l in sel:\n"
        "    print(('[FAIL] ' if l in bad else '[PASS] ') + l)\n"
        "print(f'-- {len(sel) - len(bad)}/{len(sel)} passed --')\n"
        "if bad:\n"
        "    print('FAILED: ' + ', '.join(bad))\n"
        "sys.exit(1 if bad else 0)\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "seed")
    return repo


def table(repo: Path, mutants: list[dict], name: str = "sweep.json") -> Path:
    path = repo / name
    path.write_text(json.dumps(
        {"test": [sys.executable, "t.py"], "mutants": mutants}, indent=2), encoding="utf-8")
    return path


def killer(mid: str = "M1 break the pattern") -> dict:
    """A mutant that really does break CASE-A."""
    return {"id": mid, "file": SRC, "original": PATTERN,
            "mutated": 'if flag != "on":', "case": "CASE-A"}


def _run(repo: Path, args) -> tuple[int, str]:
    script = Path(__file__).resolve().parents[1] / "mutation_sweep.py"
    p = subprocess.run([sys.executable, str(script), *args], cwd=str(repo),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    c = Cases("mutation_sweep (SCC-179)")

    # ── K5 / K1 · the negative control: a clean sweep exits 0 and attributes every kill ──
    if c.block("K5 · a clean sweep exits 0 and names the case that killed each mutant"):
        with TempDir() as t:
            repo = build(t)
            tab = table(repo, [killer()])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K5a a clean sweep exits 0", code == 0, f"exit={code} " + out[-400:])
            c.check("K5b the output attributes the kill to the DECLARED case",
                    "M1 break the pattern" in out and "CASE-A" in out and "KILLED" in out,
                    out[-400:])
            c.check("K5c the source file is byte-identical afterwards",
                    "KILLED" in out          # ...of a sweep that actually ran
                    and PATTERN in (repo / SRC).read_text(encoding="utf-8")
                    and git(repo, "diff", "--quiet").returncode == 0,
                    (repo / SRC).read_text(encoding="utf-8"))

    # ── K2 · a mutant that SURVIVES, and residue that survives the restore ──
    if c.block("K2 · a surviving mutant and surviving residue both FAIL the sweep"):
        with TempDir() as t:
            repo = build(t)
            # A mutant no case notices: the test's verdict does not change, so exit 0.
            tab = table(repo, [{"id": "M9 cosmetic", "file": SRC,
                                "original": "    return 0\n", "mutated": "    return 0  # x\n",
                                "case": "CASE-A"}])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K2b a mutant that survives fails the sweep, named",
                    code != 0 and "SURVIVED" in out and "M9 cosmetic" in out,
                    f"exit={code} " + out[-400:])
            c.check("K2b2 ...and the tree is still restored despite the failure",
                    "SURVIVED" in out        # ...of a sweep that actually ran
                    and git(repo, "diff", "--quiet").returncode == 0,
                    git(repo, "status", "--short").stdout)

        with TempDir() as t:
            repo = build(t)
            # A mutant killed by a case OTHER than the declared one. SCC-156 #1: a kill that
            # cannot be attributed to the named case is not evidence about that case.
            # `block: CASE` selects BOTH labels, so CASE-A really fails and the run really
            # is non-zero. The declared case is CASE-B, which is NOT on the FAILED line.
            tab = table(repo, [dict(killer(), case="CASE-B unrelated", block="CASE")])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K2c a kill attributed to the WRONG case is not a kill",
                    code != 0 and "not `CASE-B unrelated`" in out and "CASE-A" in out,
                    f"exit={code} " + out[-500:])

        with TempDir() as t:
            repo = build(t)
            # A `kills` label no block matches -> the harness's exit 3. Reading that as a kill
            # is how a typo'd label launders a surviving mutant (the reason NO_MATCH exists).
            tab = table(repo, [dict(killer(), case="CASE-Z typo")])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K2d exit 3 (filter matched nothing) is a SWEEP ERROR, never a kill",
                    code != 0 and "exit 3" in out and "selected NO cases" in out,
                    f"exit={code} " + out[-500:])

        with TempDir() as t:
            repo = build(t)
            # A mutant that reaches HISTORY. The working tree restores byte-perfect, so the
            # snapshot check and `git status` both read clean — and the mutant is in the
            # branch. 8681d83 exactly. Only pinned-sha-vs-HEAD sees it.
            commits = repo / "commits.py"
            commits.write_text(
                "import subprocess, sys\n"
                "subprocess.run(['git', 'commit', '-qam', 'oops'], check=False)\n"
                "print('FAILED: CASE-A pattern intact'); sys.exit(1)\n", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "committer")
            tab = repo / "c.json"
            tab.write_text(json.dumps({"test": [sys.executable, "commits.py"],
                                       "mutants": [killer()]}, indent=2), encoding="utf-8")
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K2e a mutant that reaches HISTORY fails the sweep, even though the "
                    "working tree restored clean",
                    code != 0 and "COMMITTED" in out and SRC in out,
                    f"exit={code} " + out[-500:])
            c.check("K2e2 ...and the working tree really did look innocent",
                    (repo / SRC).read_text(encoding="utf-8").count(PATTERN) == 1,
                    (repo / SRC).read_text(encoding="utf-8"))

        with TempDir() as t:
            repo = build(t)
            # A runner that fails SILENTLY - non-zero, no `FAILED:` line. Nothing can be
            # attributed, so it is an error in the sweep and never a kill. Without this case
            # the whole attribution requirement could be deleted and no test noticed.
            (repo / "silent.py").write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "silent")
            tab = repo / "s.json"
            tab.write_text(json.dumps({"test": [sys.executable, "silent.py"],
                                       "mutants": [killer()]}, indent=2), encoding="utf-8")
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K2f a runner that fails with no `FAILED:` line cannot attribute a kill",
                    code != 0 and "no `FAILED:` line" in out,
                    f"exit={code} " + out[-400:])

    # ── K3 · refuse to start dirty · restore on interrupt · an empty table is a refusal ──
    if c.block("K3 · dirty start, interrupt, empty table, bad anchor"):
        with TempDir() as t:
            repo = build(t)
            (repo / SRC).write_text("def gate(flag):\n    return 0\n", encoding="utf-8")
            tab = table(repo, [killer()])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K3a a table file dirty at START is refused, exit 2, named",
                    code == 2 and SRC in out, f"exit={code} " + out[-400:])
            c.check("K3a2 the refusal says WHY (residue is indistinguishable from your edits)",
                    "indistinguish" in out.lower() or "residue" in out.lower(), out[-400:])

        with TempDir() as t:
            repo = build(t)
            code, out = _run(repo, ["--table", str(table(repo, []))])
            c.check("K3d an EMPTY mutant table is a REFUSAL, not a clean sweep",
                    code == 2 and ("empty" in out.lower() or "no mutants" in out.lower()),
                    f"exit={code} " + out[-300:])

        with TempDir() as t:
            repo = build(t)
            tab = table(repo, [dict(killer(), original="text that is not in the file")])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K3e an anchor that is not in the file is a sweep error, exit 2",
                    code == 2 and "M1" in out, f"exit={code} " + out[-400:])
            tab = table(repo, [dict(killer(), original="return")])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K3e2 a NON-UNIQUE anchor is a sweep error too (it mutates the wrong line)",
                    code == 2 and "unique" in out.lower(),
                    f"exit={code} " + out[-400:])

        with TempDir() as t:
            repo = build(t)
            # SIGTERM mid-mutant: the restore must be in a trap/finally, not after the run.
            slow = repo / "slow.py"
            slow.write_text("import time, sys\ntime.sleep(30)\n", encoding="utf-8")
            tab = table(repo, [killer()], name="slow.json")
            tab.write_text(json.dumps({"test": [sys.executable, "slow.py"],
                                       "mutants": [killer()]}, indent=2), encoding="utf-8")
            script = Path(__file__).resolve().parents[1] / "mutation_sweep.py"
            proc = subprocess.Popen([sys.executable, str(script), "--table", str(tab)],
                                    cwd=str(repo), stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True)
            deadline = time.time() + 15
            mutated = False
            while time.time() < deadline:
                if PATTERN not in (repo / SRC).read_text(encoding="utf-8"):
                    mutated = True
                    break
                time.sleep(0.1)
            proc.send_signal(signal.SIGTERM)
            try:
                proc.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
            c.check("K3b the fixture really did reach the mutated state",
                    mutated, "the sweep never wrote the mutant - the case proves nothing")
            c.check("K3b2 SIGTERM mid-sweep still RESTORES the file (trap/finally)",
                    PATTERN in (repo / SRC).read_text(encoding="utf-8"),
                    (repo / SRC).read_text(encoding="utf-8"))

        with TempDir() as t:
            repo = build(t)
            # SIGKILL cannot be trapped - that is the SCC-144 shape. The mechanical check is
            # the NEXT sweep refusing to start on the residue it left.
            slow = repo / "slow.py"
            slow.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
            tab = repo / "slow.json"
            tab.write_text(json.dumps({"test": [sys.executable, "slow.py"],
                                       "mutants": [killer()]}, indent=2), encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "fixtures")
            script = Path(__file__).resolve().parents[1] / "mutation_sweep.py"
            proc = subprocess.Popen([sys.executable, str(script), "--table", str(tab)],
                                    cwd=str(repo), stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            deadline = time.time() + 15
            while time.time() < deadline:
                if PATTERN not in (repo / SRC).read_text(encoding="utf-8"):
                    break
                time.sleep(0.1)
            proc.kill()
            proc.wait()
            residue = PATTERN not in (repo / SRC).read_text(encoding="utf-8")
            code, out = _run(repo, ["--table", str(table(repo, [killer()]))])
            c.check("K3c SIGKILL leaves residue (untrappable - this is the SCC-144 shape)",
                    residue, "no residue: the case below would prove nothing")
            c.check("K3c2 ...and the NEXT sweep refuses to start on it, naming the file",
                    code == 2 and SRC in out, f"exit={code} " + out[-400:])

        with TempDir() as t:
            repo = build(t)
            # Two mutants over the SAME line. Without a restore between them, mutant 2's
            # anchor no longer exists, `.replace()` silently does nothing, and a mutant that
            # would have been killed is reported as a survivor - a coverage hole invented by
            # the sweep itself. One-mutant tables cannot see this.
            tab = table(repo, [killer("M1 invert the test"),
                               dict(killer("M2 delete the test"),
                                    mutated='if True:')])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K3f each mutant starts from a RESTORED file, not the previous mutant's",
                    code == 0 and out.count("KILLED") >= 2 and "SURVIVED" not in out,
                    f"exit={code} " + out[-500:])

    # ── K4 · the FULL file runs once, unfiltered, after the sweep ──
    if c.block("K4 · the full test file runs once after the sweep, not the scoped subset"):
        with TempDir() as t:
            repo = build(t)
            tab = table(repo, [killer()])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K4a the sweep runs the FULL file unfiltered at the end",
                    code == 0 and "full" in out.lower()
                    and "2/2 passed" in out,   # both labels ran: no --case was passed
                    out[-600:])

        with TempDir() as t:
            repo = build(t)
            # 8681d83's exact shape: every scoped case is green, and the full file is red.
            # A sweep that stops at the scoped runs reports success over a broken tree.
            (repo / "t.py").write_text(
                (repo / "t.py").read_text(encoding="utf-8").replace(
                    "if bad:\n",
                    "if case is None:\n"
                    "    print('[FAIL] CASE-C only visible unfiltered')\n"
                    "    print('FAILED: CASE-C only visible unfiltered'); sys.exit(1)\n"
                    "if bad:\n"), encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "t")
            tab = table(repo, [killer()])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K4b a full-file failure fails the sweep, even with every mutant killed",
                    code != 0 and "CASE-C" in out, f"exit={code} " + out[-600:])

    # ── U · a test file that declares NO blocks (SCC-244) ────────────────────────────────
    # `test_label_tasks.py` has 118 cases and not one `c.block()`. There is no label to
    # select, so ANY `--case` matches nothing and the harness exits 3 - which this script
    # correctly refuses to score. Without an explicit "run the whole file", the largest code
    # change in a lane can have no sweep coverage at all, and the shape that hides that is a
    # transcript full of SWEEP ERROR lines that reads like a tooling niggle rather than a
    # coverage hole.
    if c.block("U · a file with no blocks is swept whole, and only when asked"):
        with TempDir() as t_:
            repo = build(t_)
            # A stand-in with no selectable blocks: any filter selects nothing.
            (repo / "tnb.py").write_text(
                "import sys, pathlib\n"
                "argv = sys.argv[1:]\n"
                "if '--case' in argv:\n"
                "    print('NO CASES RAN: no block matched'); sys.exit(3)\n"
                "src = pathlib.Path(__file__).parent.joinpath('src.py').read_text()\n"
                "bad = " + repr(PATTERN) + " not in src\n"
                "print(('[FAIL] ' if bad else '[PASS] ') + 'CASE-A pattern intact')\n"
                "print('-- %d/1 passed --' % (0 if bad else 1))\n"
                "if bad:\n"
                "    print('FAILED: CASE-A pattern intact')\n"
                "sys.exit(1 if bad else 0)\n", encoding="utf-8")
            git(repo, "add", "-A"); git(repo, "commit", "-qm", "no-block runner")
            base = {"id": "M1 break the pattern", "file": SRC, "original": PATTERN,
                    "mutated": 'if flag != "on":', "case": "CASE-A pattern intact",
                    "test": [sys.executable, "tnb.py"]}

            code, out = _run(repo, ["--table", str(table(repo, [dict(base)], "u1.json"))])
            # ⛔ `"KILLED" not in out` is WRONG here and passed vacuously the first time:
            # the refusal line itself reads `⛔ NOT KILLED`, which contains the substring.
            # Match the verdict line, not the word.
            killed_lines = [ln for ln in out.splitlines() if ln.startswith("KILLED")]
            c.check("U1 filtered, it is a SWEEP ERROR on exit 3 - never a kill and never a pass",
                    code != 0 and "SWEEP ERROR - exit 3" in out and not killed_lines,
                    f"exit={code} killed={killed_lines} " + out[-300:])

            code, out = _run(repo, ["--table", str(table(
                repo, [dict(base, unfiltered=True)], "u2.json"))])
            c.check("U2 `unfiltered` runs the whole file and the mutant is KILLED, attributed",
                    code == 0 and "KILLED" in out and "CASE-A pattern intact" in out,
                    f"exit={code} " + out[-300:])
            c.check("U2 ...and no `--case` reached the runner (no filter line at all)",
                    "-- filter " not in out, out[-300:])

            code, out = _run(repo, ["--table", str(table(
                repo, [dict(base, unfiltered=True, block="CASE-A")], "u3.json"))])
            c.check("U3 declaring BOTH `unfiltered` and `block` is refused at load, named",
                    code != 0 and "unfiltered" in out and "block" in out and "KILLED" not in out,
                    f"exit={code} " + out[-300:])

            c.check("U4 the tree is still restored after all three",
                    git(repo, "diff", "--quiet").returncode == 0,
                    git(repo, "status", "--short").stdout)


    # ── K6 · SCC-284: a DELETION mutant is legal; an ABSENT field is not ──────────────────
    # "Remove this line entirely and see if anything notices" is declared as `"mutated": ""`.
    # The loader tested the five required fields with `if not m.get(k)` - a FALSY test, not a
    # presence test - so the empty string read as *missing* and the whole table was refused
    # with "is missing mutated", sending the reader to look for a typo in a field that was
    # sitting right there. SCC-244 worked around it three times by substituting an inert line
    # (M16/M23/M26), which made the sweep record say "replaced" about a mutant that tested
    # "removed" - wrong in the one file whose whole job is being right about what was proven.
    if c.block("K6 · SCC-284: a DELETION mutant is legal; an ABSENT field is not"):
        with TempDir() as t:
            repo = build(t)
            tab = table(repo, [dict(killer("M1 delete the guard line"), mutated="")])
            code, out = _run(repo, ["--table", str(tab)])
            c.check("K6a `\"mutated\": \"\"` LOADS - the table is not refused as missing a field",
                    "is missing" not in out and "missing mutated" not in out,
                    f"exit={code} " + out[-400:])
            c.check("K6b ...and it APPLIES as a deletion and is scored like any other (KILLED, exit 0)",
                    code == 0 and "KILLED" in out and "M1 delete the guard line" in out,
                    f"exit={code} " + out[-400:])
            c.check("K6c ...and the deleted line is back afterwards (restore proven)",
                    PATTERN in (repo / SRC).read_text(encoding="utf-8")
                    and git(repo, "diff", "--quiet").returncode == 0,
                    (repo / SRC).read_text(encoding="utf-8"))

        with TempDir() as t:
            repo = build(t)
            absent = killer("M2 no mutated key at all")
            del absent["mutated"]
            code, out = _run(repo, ["--table", str(table(repo, [absent]))])
            c.check("K6d a mutant whose `mutated` key is genuinely ABSENT still refuses, exit 2",
                    code == 2 and "mutated" in out, f"exit={code} " + out[-400:])
            c.check("K6e ...and the message says ABSENT, so the reader does not hunt for a typo "
                    "in a field that is there",
                    "absent" in out.lower() and "empty" in out.lower(),
                    out[-400:])

        with TempDir() as t:
            repo = build(t)
            tab = table(repo, [dict(killer("M3 insert from nowhere"), original="")])
            code, out = _run(repo, ["--table", str(tab)])
            # ⛔ Pin the LOADER's refusal, not just "a refusal": the unique-anchor check
            # downstream also dies on "" (it occurs len+1 times), so `code == 2 and "original"
            # in out` was satisfied with the loader's guard deleted - mutant M5 of this lane's
            # own sweep survived on exactly that. The loader's message is the one that tells
            # the reader WHY ("only `mutated` may be empty"); the anchor-count message would
            # send them counting occurrences of an empty string.
            c.check("K6f `\"original\": \"\"` still refuses - a mutant that inserts from nowhere "
                    "has no unique anchor, and the LOADER says so (EMPTY, not 'occurs N times')",
                    code == 2 and "EMPTY" in out and "original" in out and "occurs" not in out,
                    f"exit={code} " + out[-400:])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
