"""check_maps.py check 9 must read the code graph's OWN record of the commit it was built at.

The freshness hint exists because the graph index is machine-local and gitignored: a `git pull`
moves HEAD past it, and every impact / test-selection answer it gives afterwards is quietly about
the wrong tree. The check therefore has exactly one job — compare what the graph says it was built
at against HEAD — and one hard constraint: it must work with **no CLI on `PATH`**. A lint that
shells out to the tool it is checking cannot report "the tool is missing", and the SessionStart
hook runs it in a stripped-PATH environment where that is the normal case, not the edge case.

`code-review-graph` stores that stamp in its own SQLite database, `.code-review-graph/graph.db`,
in a `metadata` table keyed `git_head_sha`. Reading it takes stdlib `sqlite3` and nothing else.

Four cases, and case D is the one that matters most: a check that stops crying wolf by going blind
is not a fix. Stdlib only, no pytest — same constraint as the script under test.
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_maps import check_graph_fresh  # noqa: E402


def _repo(root: Path) -> str:
    """A real git repo with one commit; returns its HEAD sha."""
    run = lambda *a: subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True)
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    (root / "f.txt").write_text("x", encoding="utf-8")
    run("add", "f.txt")
    run("commit", "-qm", "one")
    return run("rev-parse", "HEAD").stdout.strip()


def _graph(root: Path, sha: str | None) -> None:
    """Write a minimal graph.db carrying (or deliberately missing) the built-at stamp."""
    d = root / ".code-review-graph"
    d.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(d / "graph.db")
    con.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
    if sha is not None:
        con.execute("INSERT INTO metadata VALUES ('git_head_sha', ?)", (sha,))
    con.commit()
    con.close()


def main() -> int:
    c = Cases("check_maps_graph_fresh")

    # A — no graph at all is the normal state of a fresh clone, and it is NOT a problem to report.
    with TempDir() as root:
        _repo(root)
        c.check("A no graph in the workspace -> silent",
                check_graph_fresh(root) == [], str(check_graph_fresh(root)))

    # B — graph built at HEAD: the whole point of the check passing.
    with TempDir() as root:
        head = _repo(root)
        _graph(root, head)
        c.check("B graph built at HEAD -> silent",
                check_graph_fresh(root) == [], str(check_graph_fresh(root)))

    # C — a graph with no stamp cannot be judged; silence beats a false alarm.
    with TempDir() as root:
        _repo(root)
        _graph(root, None)
        c.check("C graph with no git_head_sha -> silent",
                check_graph_fresh(root) == [], str(check_graph_fresh(root)))

    # D — ⭐ THE CASE THE CHECK EXISTS FOR. A commit lands after the build; the graph is now lying.
    #     If this ever goes quiet the check is worthless, so it asserts the sha is NAMED, not just
    #     that something was returned.
    with TempDir() as root:
        old = _repo(root)
        _graph(root, old)
        subprocess.run(["git", "-C", str(root), "commit", "-q", "--allow-empty", "-m", "two"],
                       capture_output=True)
        new = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        out = check_graph_fresh(root)
        c.check("D graph behind HEAD -> STALE, naming both shas and the fix",
                len(out) == 1 and old[:7] in out[0] and new[:7] in out[0]
                and "code-review-graph update" in out[0],
                str(out))

    # E — an unreadable/corrupt database must not raise out of a SessionStart hook.
    with TempDir() as root:
        _repo(root)
        d = root / ".code-review-graph"
        d.mkdir(parents=True, exist_ok=True)
        (d / "graph.db").write_text("this is not a database", encoding="utf-8")
        try:
            out = check_graph_fresh(root)
            ok = isinstance(out, list)
        except Exception as exc:  # noqa: BLE001 - the failure mode under test
            ok, out = False, f"raised {exc!r}"
        c.check("E corrupt graph.db -> returns a list, never raises", ok, str(out))

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
