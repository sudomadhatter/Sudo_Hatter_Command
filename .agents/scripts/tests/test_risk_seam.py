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
from _harness import Cases, TempDir, fake_exe  # noqa: E402

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
    body = json.dumps(payload) if not isinstance(payload, str) else payload
    # ⛔ The interpreter is named ABSOLUTELY, not via `/usr/bin/env python3`. Case I empties `PATH`
    # to prove the pipx fallback, and `env` resolves through `PATH` — so an env shebang makes the
    # fixture unlaunchable in exactly the case it exists to test, and the failure looks identical
    # to "the fallback does not work". Found by case I failing against correct code.
    #
    # ⛔ AND ON WINDOWS A SHEBANG IS NOT AN EXECUTABLE AT ALL (SCC-321). `_cli()` probes with
    # `shutil.which("code-review-graph")`, which resolves through `PATHEXT` — an extensionless
    # file is not on it, so this fixture was INVISIBLE and every case here measured the
    # no-tool-installed path while reading normally. `fake_exe` puts a `.cmd` launcher on
    # `PATHEXT` and keeps the shebang script on POSIX; `__file__` lands in `bindir` either way,
    # so the `argv.json` case C reads is written where it has always been.
    fake_exe(bindir, "code-review-graph",
             "import json, sys, pathlib\n"
             "pathlib.Path(__file__).with_name('argv.json').write_text(json.dumps(sys.argv[1:]))\n"
             f"sys.stdout.write({json.dumps(body)})\n"
             f"raise SystemExit({rc})\n")


def graph_at(root: Path, sha: str, tested_by: list[str] | None = None) -> None:
    """A real graph db carrying a real `git_head_sha` — the same stamp check 9 reads.

    `tested_by` seeds the TESTED_BY edge layer with the given SUBJECT qualified-names, so a case
    can pin the difference between "the graph has real test links" and "the graph has 24 edges
    that all point at builtins". Omit it entirely to model a graph built before that layer
    existed — the table is then ABSENT, not empty, which is a different failure to survive.
    """
    d = root / ".code-review-graph"
    d.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(d / "graph.db")
    con.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("INSERT INTO metadata VALUES ('git_head_sha', ?)", (sha,))
    if tested_by is not None:
        con.execute("CREATE TABLE edges (kind TEXT, source_qualified TEXT, target_qualified TEXT)")
        for subject in tested_by:
            con.execute("INSERT INTO edges VALUES ('TESTED_BY', ?, 'someTest')", (subject,))
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


def unclassified_shape(got: dict, root: "Path | None" = None) -> bool:
    """The degraded shape, WHOLE — status + tiers + (since SCC-289) the `root` echo.

    ⛔ Still a whole-shape check, not a loosened one: any key outside {status, tiers, root} fails,
    `tiers` must be empty, and when a repo is named the echo must be THAT repo. The six degradation
    cases used to compare against a two-key literal; the echo is the only field allowed to join it,
    and it is required whenever a root resolved — a degraded answer that cannot say which tree it
    was about is the ambiguity SCC-289 exists to remove.
    """
    if set(got) - {"status", "tiers", "root"}:
        return False
    if got.get("status") != "unclassified" or got.get("tiers") != {}:
        return False
    if root is None:
        return True
    echoed = got.get("root")
    return echoed is not None and Path(echoed).resolve() == Path(root).resolve()


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


def call_cli(cwd: Path, argv: list[str], env: dict[str, str]) -> tuple[int, dict, str]:
    """Run risk_seam.py as the DOORS run it — a real argv, a real cwd, a real process.

    ⛔ `classify(paths, root=…)` has taken a root since SCC-278; the defect SCC-289 fixes is that
    the CLI had no way to pass one, so every door invoking it from the command centre classified
    the CENTRE's cwd. Calling the function with `root=` cannot see that bug — only argv can.
    """
    r = subprocess.run([sys.executable, str(REPO / ".agents" / "scripts" / "risk_seam.py"), *argv],
                       capture_output=True, text=True, env=env, cwd=str(cwd))
    try:
        return r.returncode, json.loads(r.stdout), r.stderr
    except ValueError:
        return r.returncode, {}, (r.stderr or r.stdout)[-400:]


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
            c.check("E unclassified on a stale graph, and it says WHICH tree",
                    unclassified_shape(got, tmp), str(got)[:300])

    if c.block("F · ⛔ no graph at all is unclassified"):
        with TempDir() as tmp:
            git_repo(tmp)
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("F unclassified with no graph db, and it says WHICH tree",
                    unclassified_shape(got, tmp), str(got)[:300])

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
                        unclassified_shape(got, tmp), str(got)[:300])

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
                    unclassified_shape(got, tmp), str(got)[:300])
            fake_cli(tmp / "bin2", "not json at all")
            got2 = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin2"))
            c.check("H unclassified on unparseable stdout",
                    unclassified_shape(got2, tmp), str(got2)[:300])

    # ── J · a corrupt graph db must not raise out of the seam ─────────────────────────────────
    if c.block("J · ⛔ a corrupt graph db degrades, it does not raise"):
        with TempDir() as tmp:
            git_repo(tmp)
            (tmp / ".code-review-graph").mkdir()
            (tmp / ".code-review-graph" / "graph.db").write_text("not a database", encoding="utf-8")
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("J unclassified, no traceback",
                    unclassified_shape(got, tmp), str(got)[:300])

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

    # ── M · `untested` is only signal when the graph HAS a test-link layer ────────────────────
    # ⛔ THE REASON THIS CASE EXISTS. Measured in the command centre 2026-08-22, during SCC-270's
    # own review: the live graph held 24 TESTED_BY edges and NOT ONE named a subject under test.
    # 21 pointed at bare builtins (`str`, `Path`, `mkdir`, `isinstance`) and 3 at a test class's
    # own `assertEqual`/`assertIn`. Meanwhile CALLS was 22135/22135 path-resolved — the call graph
    # works, the test-link layer does not. Consequence: `untested` listed EVERY changed function
    # in the repo, and read exactly like a finding. A reviewer trusting it would open twelve files
    # that are all thoroughly tested. So `classify` must publish HOW MANY REAL TEST LINKS EXIST,
    # and a raw `count(*)` would have said 24 and hidden the whole problem.
    if c.block("M · classify publishes the test-link count, and does not count junk"):
        with TempDir() as tmp:
            head = git_repo(tmp)
            junk = ["str", "Path", "mkdir", "isinstance",                       # bare builtins
                    str(tmp / "t/tests/test_x.py") + "::TestX.assertEqual"]     # a test's own method
            graph_at(tmp, head, tested_by=junk)
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("M the shape carries test_links", "test_links" in got, str(got)[:200])
            c.check("M ⛔ 5 junk edges count as ZERO real test links",
                    got.get("test_links") == 0, str(got.get("test_links")))

        with TempDir() as tmp:
            head = git_repo(tmp)
            real = [str(tmp / "src/a.py") + "::alpha", str(tmp / "src/b.py") + "::beta"]
            graph_at(tmp, head, tested_by=real + ["len"])
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("M a REAL subject link is counted (and the builtin beside it is not)",
                    got.get("test_links") == 2, str(got.get("test_links")))

        with TempDir() as tmp:                       # graph predating the edges table entirely
            head = git_repo(tmp)
            graph_at(tmp, head)                      # no `tested_by` -> no edges TABLE
            fake_cli(tmp / "bin", CANNED)
            got = call_classify(tmp, ["src/a.py"], with_path(tmp / "bin"))
            c.check("M ⛔ a graph with no edges table degrades to 0, it does not raise",
                    got.get("status") == "classified" and got.get("test_links") == 0, str(got)[:200])

    # ── L · the canned shape vs the REAL tool, on a machine that has both ─────────────────────
    # ⛔ NOT a skip that hides a failure: it reports which arm ran. A canned fixture that has
    # drifted from the tool's actual output is invisible to every case above, and this is the
    # only thing that can see it. On a machine that cannot answer there is nothing to compare,
    # and the live arm states that rather than passing quietly.
    #
    # ⛔ A STALE GRAPH IS A PRECONDITION, NOT A FAILURE — and getting that wrong is what this
    # comment is here to stop happening twice. `classify` returns `unclassified` when the graph's
    # recorded sha is not HEAD, which is CORRECT and is what cases E/F pin. HEAD moves on every
    # merge, so a live arm that only skips on "no CLI / no db" turns every `git merge origin/main`
    # into a red suite that says nothing true about the code (measured 2026-08-22, SCC-270: the
    # merge that absorbed SCC-269/271/279 failed exactly this way while `code-review-graph update`
    # made it green untouched). The precondition for comparing against the real tool is that the
    # real tool can ANSWER: CLI present, db present, AND db at HEAD.
    if c.block("L · the real installed tool, when this machine has one"):
        import shutil
        exe = shutil.which("code-review-graph") or str(Path.home() / ".local/bin/code-review-graph")
        db = REPO / ".code-review-graph" / "graph.db"
        fresh = rs._graph_is_fresh(REPO) if (Path(exe).exists() and db.exists()) else False
        if Path(exe).exists() and db.exists() and fresh:
            got = rs.classify([".agents/hooks/rule-trigger.py"], root=str(REPO))
            live = got.get("status") == "classified" and got.get("tiers")
            c.check("L LIVE: the real tool classifies a file this lane changed", bool(live),
                    str(got)[:300])
            if live:
                t = next(iter(got["tiers"].values()))
                c.check("L LIVE: a tier carries risk/flows/untested",
                        set(t) == {"risk", "flows", "untested"}, str(t)[:200])
        elif Path(exe).exists() and db.exists():
            c.check("L SKIPPED — the graph is STALE (not at HEAD), so the real tool has nothing "
                    "to compare against. Run `code-review-graph update` and re-run this file to "
                    "verify the canned shape. This is the normal state right after a merge.",
                    True, f"db={db} fresh={fresh}")
        else:
            c.check("L SKIPPED — no code-review-graph and/or no graph db on this machine "
                    "(the canned shape in this file is therefore UNVERIFIED here)", True,
                    f"exe={exe} exists={Path(exe).exists()} db={db.exists()}")

    # ── N · SCC-289 · the CLI takes --repo, and the answer is about THAT repo ─────────────────
    # THE BUG THIS PINS: `_repo_root(None)` falls back to `git rev-parse --show-toplevel` of CWD.
    # The four review/audit doors run from the command centre while reviewing a PROJECT worktree,
    # so every project review resolved the CENTRE as the repo — which carries no graph, so the
    # answer was ALWAYS `unclassified`, and looked exactly like "this machine has no graph".
    if c.block("N · SCC-289 · classify --repo reads the named repo, not cwd"):
        with TempDir() as fixture, TempDir() as elsewhere:
            head = git_repo(fixture)
            graph_at(fixture, head)
            fake_cli(fixture / "bin", CANNED)
            git_repo(elsewhere)                     # a REAL, DIFFERENT git repo — with no graph
            env = with_path(fixture / "bin")

            rc, got, err = call_cli(elsewhere, ["classify", "--repo", str(fixture), "src/a.py"], env)
            c.check("N exit 0", rc == 0, f"rc={rc} err={err[:200]}")
            c.check("N the JSON ECHOES the root it classified against",
                    got.get("root") == str(fixture), f"root={got.get('root')!r} want={fixture}")
            c.check("N status is classified — the FIXTURE's graph was read, not cwd's absent one",
                    got.get("status") == "classified", str(got)[:300])
            c.check("N the tier belongs to the FIXTURE's path",
                    got.get("tiers", {}).get("src/a.py", {}).get("risk") == 0.7,
                    str(got.get("tiers"))[:300])

            # The other half, and it is what makes the first half mean something: WITHOUT the flag
            # the same command from the same cwd is unclassified. If this passed too, `--repo`
            # would be decoration.
            rc2, got2, err2 = call_cli(elsewhere, ["classify", "src/a.py"], env)
            c.check("N control · no --repo from that cwd is unclassified",
                    rc2 == 0 and got2.get("status") == "unclassified",
                    f"rc={rc2} got={str(got2)[:200]} err={err2[:150]}")
            # Compared RESOLVED: this root came from `git rev-parse`, which reports the physical
            # path, and on this Mac `/tmp` is a symlink to `/private/tmp`. The `--repo` half above
            # is compared EXACTLY on purpose — an argument is used as given (Port Check 1).
            root2 = got2.get("root")
            c.check("N control · and it echoes the CWD repo as its root, not the fixture",
                    root2 is not None and Path(root2).resolve() == elsewhere.resolve()
                    and Path(root2).resolve() != fixture.resolve(),
                    f"root={root2!r} want={elsewhere.resolve()}")

    if c.block("O · SCC-289 · --repo is discoverable and argument errors are exit 2"):
        rc, _got, err = call_cli(REPO, ["classify"], dict(os.environ))
        c.check("O no paths is exit 2 and the usage names --repo",
                rc == 2 and "--repo" in err, f"rc={rc} err={err[:200]}")
        # ⛔ `classify --repo` ALONE CANNOT TEST THIS, and the mutation sweep is what proved it
        # (M2 survived). Skip the flag and there are no paths left either, so the no-paths error
        # produces the same exit 2 — the case passed against code that had silently dropped the
        # value check. The path must come FIRST, so a fall-through would be a perfectly valid
        # command classified against CWD.
        rc3, got3, err3 = call_cli(REPO, ["classify", ".agents", "--repo"], dict(os.environ))
        c.check("O a trailing --repo with no value is exit 2, never a silent cwd fallback",
                rc3 == 2 and "--repo needs a value" in err3,
                f"rc={rc3} got={str(got3)[:120]} err={err3[:200]}")
        # ⛔ AN UNKNOWN FLAG IS THE SAME DEFECT THROUGH THE BACK DOOR (Blind Hunter, SCC-288).
        # The loop used to `paths.append` anything it did not recognise, so a one-character typo
        # left `root` unset and `classify` answered about CWD -- the command centre -- while the
        # new `root` echo stated that wrong tree with confidence. The guarded spellings above are
        # worth nothing if every other spelling reopens the hole.
        rc5, _g5, err5 = call_cli(REPO, ["classify", "--rep", "/x", ".agents"], dict(os.environ))
        c.check("O a MISSPELLED flag is exit 2, not a path (no silent cwd fallback)",
                rc5 == 2 and "--rep" in err5, f"rc={rc5} err={err5[:200]}")
        rc4, _g4, err4 = call_cli(REPO, ["classify", ".agents", "--repo="], dict(os.environ))
        c.check("O an EMPTY --repo= is exit 2 too (an unset shell variable expands to this)",
                rc4 == 2, f"rc={rc4} err={err4[:200]}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
