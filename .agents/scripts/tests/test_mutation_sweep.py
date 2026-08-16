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

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
