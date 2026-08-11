"""check_maps.py must not confuse a MEMORY named in prose with a session folder on disk.

The depth-3 reconciler extracts every backticked token from every INDEX table row and asks
"is this a session folder that no longer exists?". The classifier it asks with,
SESSION_FOLDER_RE, was written to sort DIRECTORY NAMES; pointing it at arbitrary prose makes
any memory whose slug starts with `story-`, `tea-`, `epic-`, `autopilot-`, `wave-` or
`close-out-` look like a folder that has gone missing.

That is not a theoretical collision. On 2026-08-11 the combined gate on `main` reported
`stale row \x60tea-retrofit-active-initiative/\x60 (folder not on disk)` for a row whose prose
cites the memory `tea-retrofit-active-initiative` — 9 memories in the lobby store carry a
matching prefix. Ledger rows exist to explain WHY a decision was made, and naming the memory a
decision rests on is exactly what they are for, so the gate was punishing the behaviour the
convention asks for.

Both halves are asserted here. A gate that stops crying wolf by going blind is not a fix:
case D proves a genuinely stale session row is STILL reported.

Stdlib only, no pytest — same constraint as the script under test.
"""
from __future__ import annotations

import sys
from pathlib import Path

from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_maps import _check_depth3_tree  # noqa: E402

MEMORY_PREFIXED = [
    "tea-retrofit-active-initiative",
    "story-status-flip-contract",
    "autopilot-glm-hybrid-lane",
    "close-out-command-is-daniels-signoff",
]


def _bucket(root: Path, sessions: list[str], index_body: str) -> Path:
    """A depth-3 bucket: <root>/_artifacts/_main/ with >=2 session folders and an INDEX."""
    bucket = root / "_artifacts" / "_main"
    for s in sessions:
        (bucket / s).mkdir(parents=True, exist_ok=True)
    (bucket / "INDEX.md").write_text(index_body, encoding="utf-8")
    return bucket


def _problems(root: Path) -> list[str]:
    return _check_depth3_tree(root, root / "_artifacts")


def main() -> int:
    c = Cases("check_maps")
    sessions = ["2026-08-11_scc-88-memory-relocation-sweep", "2026-08-11_scc-90-sop-restructure"]
    rows = (
        "# _main — INDEX\n\n| Session folder | What | Artifacts |\n|---|---|---|\n"
        f"| `{sessions[0]}/` | did a thing | walkthrough |\n"
        f"| `{sessions[1]}/` | did another | walkthrough |\n"
    )

    # ── A: the live regression — a memory cited in prose is not a missing folder ──────────
    for slug in MEMORY_PREFIXED:
        with TempDir() as root:
            body = rows.replace(
                "| did a thing |",
                f"| the ruling rests on `{slug}`, which stays in the lobby |",
            )
            _bucket(root, sessions, body)
            probs = _problems(root)
            stale = [p for p in probs if "stale row" in p]
            c.check(
                f"A a memory named in prose (`{slug}`) is not reported stale",
                not stale,
                f"got {stale[0]}" if stale else "",
            )

    # ── B: it must not swing the other way and start MISSING real folders ────────────────
    with TempDir() as root:
        body = rows.replace("| did a thing |", "| see `tea-retrofit-active-initiative` |")
        _bucket(root, sessions, body)
        probs = _problems(root)
        missing = [p for p in probs if "missing row" in p]
        c.check("B both real session folders still count as mentioned", not missing,
                f"got {missing}" if missing else "")

    # ── C: a memory slug in a NON-table line was never the problem, and still is not ─────
    with TempDir() as root:
        _bucket(root, sessions, rows + "\nSee also `story-artifacts-two-doc-close` for the why.\n")
        c.check("C a backticked slug outside any table row is ignored",
                not [p for p in _problems(root) if "stale row" in p])

    # ── D: THE MIRROR — a genuinely stale session row is STILL reported ──────────────────
    #     Without this, the fix could be "stop reporting stale rows" and case A would pass.
    with TempDir() as root:
        ghost = "2026-08-04_a-session-folder-that-was-deleted"
        _bucket(root, sessions, rows + f"| `{ghost}/` | landed and its folder was removed | walkthrough |\n")
        probs = [p for p in _problems(root) if "stale row" in p]
        c.check("D a real stale session row IS still reported (the gate kept its teeth)",
                any(ghost in p for p in probs),
                f"probs={probs}")

    # ── E: and a genuinely missing row is still reported ─────────────────────────────────
    with TempDir() as root:
        body = (
            "# _main — INDEX\n\n| Session folder | What | Artifacts |\n|---|---|---|\n"
            f"| `{sessions[0]}/` | only one row for two folders | walkthrough |\n"
        )
        _bucket(root, sessions, body)
        probs = [p for p in _problems(root) if "missing row" in p]
        c.check("E a session folder with no row IS still reported",
                any(sessions[1] in p for p in probs), f"probs={probs}")

    # ── F: the live tree — main itself must be clean of phantom stales ───────────────────
    repo = Path(__file__).resolve().parents[3]
    live = [p for p in _check_depth3_tree(repo, repo / "_artifacts") if "stale row" in p]
    c.check("F the live _artifacts tree reports no stale rows", not live, f"got {live}")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
