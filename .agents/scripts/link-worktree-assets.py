#!/usr/bin/env python3
"""Link a repo's gitignored runtime assets into a git worktree (SCC-62).

A worktree does not inherit `.env`, `auth_keys/` or `node_modules` — they are not in git, so
`git worktree add` has nothing to copy. Reading them by absolute path does not help either: pytest,
uvicorn, `next dev` and the Firebase emulators resolve them RELATIVE TO CWD, so it is the process,
not the agent, that breaks.

We link rather than copy, so opening a tree costs seconds instead of gigabytes:

    node_modules/   Mac: symlink   PC: junction   (directory; a junction needs no admin)
    auth_keys/      Mac: symlink   PC: junction   (directory, read-only in practice)
    .env            Mac: symlink   PC: COPY       (Windows file-symlinks need admin/Developer Mode)

Assets are discovered at the repo ROOT and ONE directory down — `backend/.env`, `backend/.venv`,
`frontend/node_modules` is AGY's real layout, and a root-only scan finds none of them (SCC-62
follow-on). Depth-1 is deliberate, not lazy: an unbounded walk would descend into the very
node_modules trees being linked.

Two things worth holding, both reported at runtime:
  - A symlinked `.env` is SHARED STATE. Edit it in one lane and every lane sees it. That is usually
    what you want (key rotation propagates), but it is one collision surface re-introduced. Anything
    a lane MUTATES should be copied, not linked — which is why `.env` is copied on Windows and why
    --copy-env exists everywhere.
  - Shared `node_modules` is fine for dev, NOT for E2E: two lanes on different installs will fight.
    The E2E tier keeps its own `npm ci`.

    link-worktree-assets <worktree-path> [--repo <path>] [--copy-env]
    link-worktree-assets --unlink <worktree-path>

⛔ --unlink MUST run before the worktree is removed. A recursive delete THROUGH a junction walks into
the real directory and destroys the shared target, not just the link. `git worktree remove` does a
recursive delete. This is why /smh-close-task-merge-tree Step 5 and /cicd-close-workingtree Step 3 unlink
first, every time.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

IS_WINDOWS = os.name == "nt"

# (name, kind) — kind decides how it travels. Order is stable for predictable output.
ASSETS: list[tuple[str, str]] = [
    ("node_modules", "dir"),
    ("auth_keys", "dir"),
    (".venv", "dir"),
    (".env", "file"),
    (".env.local", "file"),
]


def repo_root(start: Path) -> Path:
    """The main working tree, even when called from inside a worktree."""
    out = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    # --git-common-dir points at the MAIN repo's .git even from a linked worktree.
    return Path(out).parent


def link_dir(src: Path, dst: Path) -> str:
    if IS_WINDOWS:
        # Junction: no admin rights required, unlike a directory symlink.
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
            check=True,
            capture_output=True,
        )
        return "junction"
    dst.symlink_to(src, target_is_directory=True)
    return "symlink"


def link_file(src: Path, dst: Path, force_copy: bool) -> str:
    # Windows file-symlinks need admin or Developer Mode, so we copy there by default.
    if IS_WINDOWS or force_copy:
        shutil.copy2(src, dst)
        return "copy"
    dst.symlink_to(src)
    return "symlink"


def find_assets(repo: Path) -> list[tuple[Path, str]]:
    """Assets at the repo root AND one directory down (backend/.env, frontend/node_modules).

    Depth-1 is deliberate, not lazy: AGY keeps every runtime asset in a top-level package dir,
    and an unbounded walk would descend into the very node_modules trees being linked.
    """
    asset_names = {name for name, _ in ASSETS}
    parents = [repo]
    for child in sorted(p for p in repo.iterdir() if p.is_dir()):
        # Never treat an asset (or a link) as a parent to scan inside.
        if child.name in asset_names or child.name == ".git" or child.is_symlink():
            continue
        parents.append(child)
    found: list[tuple[Path, str]] = []
    for name, kind in ASSETS:
        for parent in parents:
            if (parent / name).exists():
                found.append((parent / name, kind))
    return found


def do_link(worktree: Path, repo: Path, copy_env: bool) -> int:
    print(f"repo:     {repo}")
    print(f"worktree: {worktree}\n")

    linked, skipped = 0, 0
    env_symlinked = shared_node_modules = False
    for src, kind in find_assets(repo):
        rel = src.relative_to(repo)
        dst = worktree / rel
        if not dst.parent.is_dir():
            print(f"  ! {rel} — its parent dir is not in the worktree, skipped")
            continue
        if dst.exists() or dst.is_symlink():
            print(f"  = {str(rel):<24} already present — left alone")
            skipped += 1
        else:
            how = link_dir(src, dst) if kind == "dir" else link_file(src, dst, copy_env)
            print(f"  + {str(rel):<24} {how}")
            linked += 1
        env_symlinked = env_symlinked or (kind == "file" and dst.is_symlink())
        shared_node_modules = shared_node_modules or (rel.name == "node_modules" and dst.exists())

    if not linked and not skipped:
        print("  (nothing to link — no gitignored runtime assets at the repo root or one level down)")
        return 0

    print(f"\n{linked} linked, {skipped} already present.")
    if env_symlinked:
        print(
            "\n⚠ .env is SHARED STATE via symlink — editing it here edits every lane.\n"
            "  Re-run with --copy-env if this lane will change it."
        )
    if shared_node_modules:
        print(
            "⚠ node_modules is shared — fine for dev, NOT for E2E.\n"
            "  The E2E tier must run its own `npm ci` in this tree."
        )
    print("\n⛔ Run `--unlink` BEFORE `git worktree remove`, or the delete eats the shared targets.")
    return 0


def is_link(p: Path) -> bool:
    """True for a POSIX symlink OR a Windows junction.

    os.path.islink() returns False for junctions, so Windows needs the reparse tag.
    """
    if p.is_symlink():
        return True
    if not IS_WINDOWS:
        return False
    if hasattr(os.path, "isjunction"):  # Python 3.12+
        return os.path.isjunction(p)
    try:
        return bool(getattr(os.lstat(p), "st_reparse_tag", 0))
    except OSError:
        return False


def find_links(root: Path) -> list[Path]:
    """Every reparse point under root, WITHOUT descending through any of them."""
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        here = Path(dirpath)
        keep = []
        for d in dirnames:
            p = here / d
            if is_link(p):
                found.append(p)  # record it, and do NOT walk into it
            else:
                keep.append(d)
        dirnames[:] = keep
        found.extend(here / f for f in filenames if is_link(here / f))
    return found


def unlink_one(p: Path) -> None:
    """Remove the LINK only — never the target."""
    if p.is_symlink() or not p.is_dir():
        p.unlink()
    else:
        # Windows junction: rmdir removes the link, not the target.
        subprocess.run(["cmd", "/c", "rmdir", str(p)], check=True, capture_output=True)


def do_unlink(worktree: Path) -> int:
    """⛔ ENUMERATE, never assume.

    Working from a list of "the assets I linked" is wrong for two independent reasons, both learned
    the hard way (see /cicd-close-workingtree Step 3): lanes link more than this script knows about,
    and TOOLS plant their own — Next.js/Turbopack creates junctions under frontend/.next/ just by
    running the dev server. A missed reparse point is not a cosmetic leak: the recursive delete that
    follows walks through it and destroys the shared target.
    """
    print(f"worktree: {worktree}\n")

    links = find_links(worktree)
    if not links:
        print("  (no reparse points found)")
        print("\nSafe to `git worktree remove` now.")
        return 0

    for p in links:
        target = ""
        try:
            target = f"  ->  {os.readlink(p)}"
        except OSError:
            pass
        unlink_one(p)
        print(f"  - {p.relative_to(worktree)}{target}")

    # Prove none remain BEFORE anything recursive touches this path.
    left = find_links(worktree)
    if left:
        print("\nABORT — reparse points still present, do NOT remove the worktree:", file=sys.stderr)
        for p in left:
            print(f"  ! {p}", file=sys.stderr)
        return 1

    print(f"\n{len(links)} unlinked, 0 remaining. Safe to `git worktree remove` now.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Link gitignored runtime assets into a git worktree.")
    ap.add_argument("worktree", help="path to the worktree")
    ap.add_argument("--repo", help="source repo (default: this repo's main working tree)")
    ap.add_argument("--unlink", action="store_true", help="remove the links (run BEFORE worktree remove)")
    ap.add_argument("--copy-env", action="store_true", help="copy .env instead of linking it")
    args = ap.parse_args()

    worktree = Path(args.worktree).resolve()
    if not worktree.is_dir():
        print(f"error: not a directory: {worktree}", file=sys.stderr)
        return 2

    if args.unlink:
        return do_unlink(worktree)

    repo = Path(args.repo).resolve() if args.repo else repo_root(worktree)
    if repo == worktree:
        print("error: source repo and worktree are the same path", file=sys.stderr)
        return 2
    return do_link(worktree, repo, args.copy_env)


if __name__ == "__main__":
    raise SystemExit(main())
