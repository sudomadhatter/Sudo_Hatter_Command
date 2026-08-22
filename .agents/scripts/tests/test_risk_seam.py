"""risk_seam.py — the risk-classification seam the self-audit calls. (SCC-228 · SCC-278)

SCC-228 built the seam and left the body a placeholder; SCC-278 fills it from the code graph.
What these cases pin is unchanged and load-bearing: **the classifier INFORMS the Parity+Blast
lens, it never gates the audit** — so a real classifier replacing a placeholder cannot silently
change the audit's meaning.

⛔ THE SEAM MUST DEGRADE, NOT DEPEND. The graph is per-machine, absent from a fresh clone, and
stale the moment you commit. The pure-Python path stays the normal one (operator ruling
2026-08-19), so every unusable state — no CLI, no graph, stale graph, a CLI that errors or
returns nonsense — returns the same defined `unclassified` shape that has always been returned.
An audit that cannot run because a machine-local index is missing is a worse defect than an audit
with less context.

How the graph-backed cases are driven, and why it is not a mock of the code under test: a REAL
executable is placed on `PATH` and a REAL sqlite graph is written to a temp repo. `classify` probes
`PATH`, checks the db, spawns the process, and parses its stdout exactly as it does in production.
The only thing standing in is the third-party tool itself. Case L then runs the whole path against
the actual installed CLI when this machine has one, so the canned shape can never drift from the
real one unnoticed.

Written RED first. Stdlib only, no pytest.
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases, TempDir  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import risk_seam as rs  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
TRUNK_NAMES = set(rs.TRUNKS)

# One changed function per file, one test gap, in the real tool's shape — see
# `code-review-graph detect-changes --help`: the FULL JSON is the default output, and `--brief`
# replaces it. There is no `--json` flag.
CANNED = {
    "summary": "Analyzed 2 changed file(s)",
    "risk_score": 0.4,
    "changed_functions": [
        {"name": "alpha", "qualified_name": "src/a.py::alpha", "file_path": "src/a.py",
         "line_start": 1, "line_end": 4, "is_test": False, "risk_score": 0.7},
        {"name": "beta", "qualified_name": "src/a.py::beta", "file_path": "src/a.py",
         "line_start": 8, "line_end": 9, "is_test": False, "risk_score": 0.2},
        {"name": "gamma", "qualified_name": "src/b.py::gamma", "file_path": "src/b.py",
         "line_start": 1, "line_end": 3, "is_test": False, "risk_score": 0.5},
    ],
    "affected_flows": [{"name": "checkout", "file_path": "src/a.py"}],
    "test_gaps": [{"name": "beta", "qualified_name": "src/a.py::beta", "file": "src/a.py",
                   "line_start": 8, "line_end": 9}],
    "review_priorities": [],
    "functions_truncated": False,
}


def fake_cli(bindir: Path, payload: object, rc: int = 0) -> None:
    """A real executable named `code-review-graph`, found by the same PATH probe production uses.

    It also writes its own argv to `argv.json` beside itself, which is the ONLY way to see what
    `--base` the seam chose — and `--base` is where the expensive mistake lives (see case C).
    """
    bindir.mkdir(parents=True, exist_ok=True)
    script = bindir / "code-review-graph"
    body = json.dumps(payload) if not isinstance(payload, str) else payload
    # ⛔ The interpreter is named ABSOLUTELY, not via `/usr/bin/env python3`. Case I empties `PATH`
    # to prove the pipx fallback, and `env` resolves through `PATH` — so an env shebang makes the
    # fixture unlaunchable in exactly the case it exists to test, and the failure looks identical
    # to "the fallback does not work". Found by case I failing against correct code.
    script.write_text(
        f"#!{sys.executable}\n"
        "import json, sys, pathlib\n"
        "pathlib.Path(__file__).with_name('argv.json').write_text(json.dumps(sys.argv[1:]))\n"
        f"sys.stdout.write({json.dumps(body)})\n"
        f"raise SystemExit({rc})\n",
        encoding="utf-8")
    script.chmod(0o755)


def graph_at(root: Path, sha: str) -> None:
    """A real graph db carrying a real `git_head_sha` — the same stamp check 9 reads."""
    d = root / ".code-review-graph"
    d.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(d / "graph.db")
    con.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("INSERT INTO metadata VALUES ('git_head_sha', ?)", (sha,))
    con.commit()
    con.close()


def git_repo(root: Path) -> str:
    """A one-commit git repo. Returns its HEAD sha."""
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    run = lambda *a: subprocess.run(["git", *a], cwd=root, env=env,  # noqa: E731
                                    capture_output=True, text=True)
    run("init", "-q", "-b", "main")
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    run("add", "seed.txt")
    run("commit", "-qm", "seed")
    return run("rev-parse", "HEAD").stdout.strip()


def with_path(bindir: Path) -> dict[str, str]:
    return dict(os.environ, PATH=f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}")


def git_only_path() -> str | None:
    """A `PATH` holding git but NOT `code-review-graph`, or None if this machine cannot provide one.

    ⛔ AN EMPTY `PATH` PROVES NOTHING HERE, and the first cut of cases G and I used one. `git`
    disappears along with everything else, so `_graph_is_fresh` fails at `git rev-parse` and the
    seam returns `unclassified` for a reason that has nothing to do with the tool being absent —
    a pass that would survive deleting the CLI probe entirely. Found by case I failing against
    correct code, which then exposed G as vacuous in the same way.
    """
    import shutil
    git = shutil.which("git")
    if not git:
        return None
    d = str(Path(git).parent)
    return None if shutil.which("code-review-graph", path=d) else d


def call_classify(root: Path, paths: list[str], env: dict[str, str]) -> dict:
    """Out of process, because PATH is read at call time and this suite runs concurrently."""
    code = ("import json,sys;sys.path.insert(0,%r);import risk_seam as rs;"
            "print(json.dumps(rs.classify(json.loads(sys.argv[1]), root=sys.argv[2])))"
            % str(REPO / ".agents" / "scripts"))
    r = subprocess.run([sys.executable, "-c", code, json.dumps(paths), str(root)],
                       capture_output=True, text=True, env=env, cwd=str(root))
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {"status": f"UNPARSEABLE rc={r.returncode}", "stderr": r.stderr[-400:]}


def main() -> int:
    c = Cases("risk_seam")

    # ── the shape contract, unchanged since SCC-228 ───────────────────────────────────────────
    if c.block("A · the fixed shape, and empty input"):
        r = rs.classify([".agents/commands/smh-self-audit.md", ".agents/scripts/x.py"])
        c.check("a return always carries status + tiers",
                set(r) >= {"status", "tiers"} and isinstance(r["tiers"], dict), str(r)[:200])
        c.check("empty input is the same defined shape, not an error",
                rs.classify([]) == {"status": "unclassified", "tiers": {}},
                str(rs.classify([])))

    # ── the seam's ONE semantic promise ───────────────────────────────────────────────────────
    # gates_audit IS the seam's semantics: False for every possible return, placeholder or real.
    # A classifier that wants to gate must change this function — and this test.
    if c.block("B · ⛔ nothing a classifier returns can gate the audit"):
        placeholder = {"status": "unclassified", "tiers": {}}
        populated = {"status": "classified",
                     "tiers": {"src/a.py": {"risk": 0.7, "flows": 1, "untested": ["beta"]}}}
        c.check("an unclassified return never gates the audit",
                rs.gates_audit(placeholder) is False, str(rs.gates_audit(placeholder)))
        c.check("a POPULATED classifier return never gates the audit either",
                rs.gates_audit(populated) is False, str(rs.gates_audit(populated)))
        c.check("even a malformed return cannot gate the audit",
                rs.gates_audit({"status": "P0-EVERYTHING-ON-FIRE"}) is False,
                str(rs.gates_audit({"status": "P0-EVERYTHING-ON-FIRE"})))

    # ── C · the happy path: fresh graph + a working CLI → real tiers ──────────────────────────
    if c.block("C · a FRESH graph classifies the paths it was asked about"):
        with TempDir() as tmp:
            head = git_repo(tmp)
            graph_at(tmp, head)
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py", "src/b.py"], with_path(tmp / "bin"))
            c.check("C status is classified", got.get("status") == "classified", str(got)[:300])
            tiers = got.get("tiers", {})
            c.check("C both requested paths carry a tier", set(tiers) == {"src/a.py", "src/b.py"},
                    str(sorted(tiers)))
            c.check("C risk is the HIGHEST of a file's changed functions, not the last or the mean",
                    tiers.get("src/a.py", {}).get("risk") == 0.7, str(tiers.get("src/a.py")))
            c.check("C untested names the function in test_gaps",
                    tiers.get("src/a.py", {}).get("untested") == ["beta"],
                    str(tiers.get("src/a.py")))
            c.check("C flows counts only the flows touching THAT file",
                    (tiers.get("src/a.py", {}).get("flows"),
                     tiers.get("src/b.py", {}).get("flows")) == (1, 0), str(tiers))
            # ⛔ THE EXPENSIVE ONE. `--base main` is a TWO-DOT diff: it includes everything that
            # landed on the trunk since the lane started (measured: 104 files reported for a
            # 12-file lane). Only a merge-base sha describes the lane's own work — and the wrong
            # answer looks completely normal, which is why it is asserted rather than trusted.
            argv = json.loads((tmp / "bin" / "argv.json").read_text(encoding="utf-8"))
            base = argv[argv.index("--base") + 1] if "--base" in argv else ""
            c.check("C ⛔ --base is a merge-base SHA, never a branch name",
                    len(base) == 40 and base not in TRUNK_NAMES and base == head,
                    f"argv={argv}")

    # ── D · a path nobody changed gets no tier, and does not fake one ─────────────────────────
    if c.block("D · a path outside the diff is absent from tiers, never a zero"):
        with TempDir() as tmp:
            head = git_repo(tmp)
            graph_at(tmp, head)
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py", "src/untouched.py"], with_path(tmp / "bin"))
            c.check("D still classified", got.get("status") == "classified", str(got)[:200])
            c.check("D the unchanged path carries NO tier (silence, not a 0.0 risk)",
                    "src/untouched.py" not in got.get("tiers", {}), str(got.get("tiers")))

    # ── E–H · every unusable state returns the SAME defined shape ─────────────────────────────
    if c.block("E · ⛔ a STALE graph is unclassified, never stale answers"):
        with TempDir() as tmp:
            git_repo(tmp)
            graph_at(tmp, "0" * 40)          # a sha that is not HEAD
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("E unclassified on a stale graph",
                    got == {"status": "unclassified", "tiers": {}}, str(got)[:300])

    if c.block("F · ⛔ no graph at all is unclassified"):
        with TempDir() as tmp:
            git_repo(tmp)
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("F unclassified with no graph db",
                    got == {"status": "unclassified", "tiers": {}}, str(got)[:300])

    if c.block("G · ⛔ no CLI on this machine is unclassified"):
        with TempDir() as tmp:
            head = git_repo(tmp)
            graph_at(tmp, head)
            bare = git_only_path()
            if bare is None:
                c.check("G SKIPPED — this machine has no git-without-the-tool PATH to build",
                        True, "")
            else:
                env = dict(os.environ, PATH=bare,
                           HOME=str(tmp / "home"), USERPROFILE=str(tmp / "home"))
                got = call_classify(tmp, ["src/a.py"], env)
                c.check("G unclassified with the tool absent (git still present)",
                        got == {"status": "unclassified", "tiers": {}}, str(got)[:300])

    # ── I · the pipx fallback. G alone does NOT pin the probe ─────────────────────────────────
    # G shows only that the seam degrades when the tool is missing — it says nothing about HOW the
    # tool is found when it is present but off `PATH`, which is the situation on this Mac every
    # time: `pipx` installs to `~/.local/bin` and that directory is not on `PATH` in every shell
    # this runs from. Delete the fallback and G still passes; only this case notices.
    # `Path.home()` reads `$HOME` / `%USERPROFILE%`, so a temp home drives the real code path with
    # no back door and without writing to the real home directory.
    if c.block("I · ⛔ the tool is FOUND at pipx's dir even when PATH does not have it"):
        with TempDir() as tmp:
            head = git_repo(tmp)
            graph_at(tmp, head)
            home = tmp / "home"
            fake_cli(home / ".local" / "bin", CANNED)
            bare = git_only_path()
            if bare is None:
                c.check("I SKIPPED — this machine has no git-without-the-tool PATH to build",
                        True, "")
            else:
                env = dict(os.environ, PATH=bare, HOME=str(home), USERPROFILE=str(home))
                got = call_classify(tmp, ["src/a.py"], env)
                c.check("I classified via the ~/.local/bin fallback, tool NOT on PATH",
                        got.get("status") == "classified" and "src/a.py" in got.get("tiers", {}),
                        str(got)[:300])

    if c.block("H · ⛔ a CLI that fails, or answers nonsense, is unclassified"):
        with TempDir() as tmp:
            head = git_repo(tmp)
            graph_at(tmp, head)
            fake_cli(tmp / "bin", CANNED, rc=1)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("H unclassified on a non-zero exit",
                    got == {"status": "unclassified", "tiers": {}}, str(got)[:300])
            fake_cli(tmp / "bin2", "not json at all")
            got2 = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin2"))
            c.check("H unclassified on unparseable stdout",
                    got2 == {"status": "unclassified", "tiers": {}}, str(got2)[:300])

    # ── J · a corrupt graph db must not raise out of the seam ─────────────────────────────────
    if c.block("J · ⛔ a corrupt graph db degrades, it does not raise"):
        with TempDir() as tmp:
            git_repo(tmp)
            (tmp / ".code-review-graph").mkdir()
            (tmp / ".code-review-graph" / "graph.db").write_text("not a database", encoding="utf-8")
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("J unclassified, no traceback",
                    got == {"status": "unclassified", "tiers": {}}, str(got)[:300])

    # ── K · the CLI door prints the tiers the review command reads ────────────────────────────
    if c.block("K · the CLI prints the same JSON the commands quote"):
        with TempDir() as tmp:
            head = git_repo(tmp)
            graph_at(tmp, head)
            fake_cli(tmp / "bin", CANNED)
            r = subprocess.run([sys.executable, str(REPO / ".agents" / "scripts" / "risk_seam.py"),
                                "classify", "src/a.py"],
                               capture_output=True, text=True, cwd=str(tmp),
                               env=with_path(tmp / "bin"))
            c.check("K exits 0", r.returncode == 0, r.stderr[-300:])
            try:
                out = json.loads(r.stdout)
            except ValueError:
                out = {}
            c.check("K prints classified tiers", out.get("status") == "classified",
                    r.stdout[:300])

    # ── L · the canned shape vs the REAL tool, on a machine that has both ─────────────────────
    # ⛔ NOT a skip that hides a failure: it reports which arm ran. A canned fixture that has
    # drifted from the tool's actual output is invisible to every case above, and this is the
    # only thing that can see it. On a machine with no CLI or no graph there is nothing to
    # compare, and the live arm states that rather than passing quietly.
    if c.block("L · the real installed tool, when this machine has one"):
        import shutil
        exe = shutil.which("code-review-graph") or str(Path.home() / ".local/bin/code-review-graph")
        db = REPO / ".code-review-graph" / "graph.db"
        if Path(exe).exists() and db.exists():
            got = rs.classify([".agents/hooks/rule-trigger.py"], root=str(REPO))
            live = got.get("status") == "classified" and got.get("tiers")
            c.check("L LIVE: the real tool classifies a file this lane changed", bool(live),
                    str(got)[:300])
            if live:
                t = next(iter(got["tiers"].values()))
                c.check("L LIVE: a tier carries risk/flows/untested",
                        set(t) == {"risk", "flows", "untested"}, str(t)[:200])
        else:
            c.check("L SKIPPED — no code-review-graph and/or no graph db on this machine "
                    "(the canned shape in this file is therefore UNVERIFIED here)", True,
                    f"exe={exe} exists={Path(exe).exists()} db={db.exists()}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
