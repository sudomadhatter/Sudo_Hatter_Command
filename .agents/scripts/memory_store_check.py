"""memory_store_check.py — make silent memory-store damage LOUD (SCC-319).

`_artifacts/_memory/` is the LIVE store every session reads, reached through a symlink at
`~/.claude/projects/<slug>/memory`. There is no second copy, so any git operation that moves
the working tree (`reset --keep`/`--hard`, `checkout`, `merge`, `rebase`) is a live mutation
of the store — and a store missing three files is indistinguishable from a store that never
had them. Measured 2026-08-24: the lobby store WAS damaged by `git reset --keep HEAD~1` and
restored by hand. Detection is the fix — not a "use --soft" rule (operator ruling).

Two halves:
  * INTEGRITY — promoted from test_memory_store.py (one implementation, two callers): the
    MEMORY.md contract. Exit non-zero when a row resolves to no file.
  * DELTA (`--delta`) — the incident's shape. The damage reverts MEMORY.md along with the
    files, so integrity stays green; only a baseline sees the drop. The checker keeps the
    store's file names per WORKING TREE (`<git-dir>/memory-store-state.json` — the
    per-worktree git dir, so a lane checked out to an older branch never shouts about the
    main store) and SHOUTS every name present last run and gone now.

Called standalone (`--store <path>`), and by the advisory `.githooks/post-checkout`,
`post-merge` and `post-rewrite` hooks — which always exit 0, because a post-* hook cannot
veto an operation that already happened; the value is that a human SEES the shout within
one command. Hooks are inert until `git config core.hooksPath .githooks` (per machine).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

INDEX_CAP = 25 * 1024
EXEMPT = {"MEMORY.md", "README.md"}

STATE_NAME = "memory-store-state.json"


def index_text(store: Path) -> str:
    idx = store / "MEMORY.md"
    return idx.read_text(encoding="utf-8") if idx.is_file() else ""


def check_store(store: Path) -> list[str]:
    """Every problem as one human sentence; empty list = the contract holds."""
    problems: list[str] = []
    idx = store / "MEMORY.md"
    if not idx.is_file():
        return [f"no MEMORY.md index in {store} - the store is unreadable by contract"]
    text = idx.read_text(encoding="utf-8")
    size = len(text.encode("utf-8"))
    if size > INDEX_CAP:
        problems.append(
            f"MEMORY.md is {size} bytes (cap {INDEX_CAP}) - every session on every "
            f"platform pays this; run /memory-audit to retire and compress (the 90% "
            f"trigger fired before this and was not acted on)")
    links = {m.split("/")[-1] for m in re.findall(r"\]\(([^)#]+\.md)\)", text)}
    files = {p.name for p in store.glob("*.md")} - EXEMPT
    for dead in sorted(links - files):
        problems.append(f"MEMORY.md links `{dead}` but no such file is in the store - "
                        f"recall of nothing; fix or delete the line")
    for orphan in sorted(files - links):
        problems.append(f"`{orphan}` has no MEMORY.md line - an unindexed memory is "
                        f"invisible to every session; add a one-line pointer")
    for p in sorted(store.glob("*.md")):
        if p.name in EXEMPT:
            continue
        head = p.read_text(encoding="utf-8", errors="replace")[:800]
        if not head.startswith("---") or "description:" not in head:
            problems.append(f"`{p.name}`: no frontmatter description - recall relevance "
                            f"is judged from it; add the ---/description header")
    return problems


def _git_dir(store: Path) -> Path | None:
    """The PER-WORKTREE git dir of the repo holding the store (baselines must not be shared
    across worktrees: each tree legitimately holds a different branch's store)."""
    rp = subprocess.run(
        ["git", "-C", str(store), "rev-parse", "--path-format=absolute", "--absolute-git-dir"],
        capture_output=True, text=True,
    )
    if rp.returncode != 0 or not rp.stdout.strip():
        return None
    return Path(rp.stdout.strip())


def check_delta(store: Path) -> list[str]:
    """Files present at the last check and gone now, by name. Updates the baseline.

    First run writes the baseline and reports nothing — there is nothing to compare.
    A GROWN store is never a problem; only a drop is the incident's signature."""
    gd = _git_dir(store)
    if gd is None:
        return []          # not in a git repo - no working-tree moves to guard against
    state_path = gd / STATE_NAME
    current = sorted(p.name for p in store.glob("*.md"))
    previous: list[str] = []
    if state_path.is_file():
        try:
            previous = json.loads(state_path.read_text(encoding="utf-8")).get("files", [])
        except (json.JSONDecodeError, OSError):
            previous = []
    try:
        state_path.write_text(json.dumps({"files": current}, indent=1) + "\n", encoding="utf-8")
    except OSError:
        pass               # a read-only git dir must not turn the checker into a crash
    return [n for n in previous if n not in current]


def main() -> int:
    ap = argparse.ArgumentParser(description="Memory store integrity + regression check")
    ap.add_argument("--store", help="path to the store (default: <repo>/_artifacts/_memory "
                                    "resolved from the current directory)")
    ap.add_argument("--delta", action="store_true",
                    help="also compare against the last check's baseline and SHOUT files "
                         "that vanished (the git-move damage integrity cannot see)")
    ap.add_argument("--from-hook", metavar="HOOK",
                    help="label the output with the hook that fired (advisory context only)")
    args = ap.parse_args()

    if args.store:
        store = Path(args.store).resolve()
    else:
        rp = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--show-toplevel"],
                            capture_output=True, text=True)
        if rp.returncode != 0 or not rp.stdout.strip():
            print("memory-store-check: not inside a git repo and no --store given", file=sys.stderr)
            return 2
        store = Path(rp.stdout.strip()) / "_artifacts" / "_memory"

    if not store.is_dir():
        # A repo with no store is whole by definition (three of the four covered repos have
        # one; a fresh project may not yet) - a hook firing there must stay silent.
        return 0

    tag = f" ({args.from_hook})" if args.from_hook else ""
    code = 0

    if args.delta:
        gone = check_delta(store)
        if gone:
            print(f"⛔ MEMORY STORE REGRESSION{tag}: {len(gone)} file(s) present at the last "
                  f"check are MISSING from {store}:")
            for n in gone:
                print(f"     MISSING  {n}")
            print("   A git working-tree move (reset/checkout/merge) removes store files "
                  "silently - recover with `git checkout <ref> -- <paths>` and verify by sha.")
            code = 2

    problems = check_store(store)
    for p in problems:
        print(f"memory-store-check{tag}: {p}")
    if problems:
        code = max(code, 1)
    return code


if __name__ == "__main__":
    sys.exit(main())
