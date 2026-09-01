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

    link-worktree-assets <worktree-path> [--repo <path>] [--copy-env] [--require-assets]
    link-worktree-assets --unlink <worktree-path>

⛔ --unlink MUST run before the worktree is removed. A recursive delete THROUGH a junction walks into
the real directory and destroys the shared target, not just the link. `git worktree remove` does a
recursive delete. This is why /smh-close-task-merge-tree Step 5 and /cicd-prune-worktree Step 3 unlink
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
    ("settings.local.json", "file"),
    ("scratchpad-root", "file"),
]


class ResolutionError(RuntimeError):
    """The repo behind this worktree does not resolve to a working tree (SCC-255)."""


# SCC-310: a trailing-slash gitignore pattern (`auth_keys/`, `.venv/`) matches a DIRECTORY
# only - never the symlink this script creates - so every linked lane read `?? auth_keys`
# and stamped its gate receipts dirty_tree: true. Measured 2026-08-24: git reads ONLY the
# COMMON `info/exclude` (a per-worktree one is silently ignored), so the entries below are
# shared by every lane of the repo. They are root-anchored with NO trailing slash, matching
# the symlink in a lane and the real dir in the main checkout alike; removal is gated on
# being the last linked worktree, so pruning one lane never dirties its siblings.
EXCLUDE_BEGIN = "# BEGIN link-worktree-assets (auto-managed - do not edit this block)"
EXCLUDE_END = "# END link-worktree-assets"


def common_exclude_path(worktree: Path) -> Path | None:
    rp = subprocess.run(
        ["git", "-C", str(worktree), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True, encoding="utf-8", text=True,
    )
    if rp.returncode != 0 or not rp.stdout.strip():
        return None
    return Path(rp.stdout.strip()) / "info" / "exclude"


def _split_managed_block(text: str) -> tuple[str, list[str]]:
    """(text without the managed block, the entries the block held)."""
    lines = text.splitlines()
    if EXCLUDE_BEGIN not in lines:
        return text, []
    start = lines.index(EXCLUDE_BEGIN)
    try:
        end = lines.index(EXCLUDE_END, start)
    except ValueError:
        # END sentinel lost (truncated edit): claiming everything below BEGIN would absorb
        # the USER'S own exclude patterns into the managed block and delete them on
        # last-lane unlink (review finding, verified). Claim only the sentinel line itself;
        # any stale entries below it are kept as user content - residue, never data loss.
        rest = lines[:start] + lines[start + 1:]
        return "\n".join(rest).rstrip("\n") + ("\n" if rest else ""), []
    entries = [ln for ln in lines[start + 1:end] if ln.strip()]
    rest = lines[:start] + lines[end + 1:]
    return "\n".join(rest).rstrip("\n") + ("\n" if rest else ""), entries


def write_exclude_entries(worktree: Path, rels: list[str]) -> None:
    """Union the placed assets into the managed block (idempotent per lane)."""
    excl = common_exclude_path(worktree)
    if excl is None or not rels:
        return
    excl.parent.mkdir(parents=True, exist_ok=True)
    text = excl.read_text(encoding="utf-8") if excl.is_file() else ""
    rest, existing = _split_managed_block(text)
    entries = sorted(set(existing) | {"/" + r for r in rels})
    block = "\n".join([EXCLUDE_BEGIN, *entries, EXCLUDE_END])
    excl.write_text(rest + ("\n" if rest and not rest.endswith("\n") else "") + block + "\n",
                    encoding="utf-8")
    print(f"  exclude:  {len(entries)} entry(ies) in the shared info/exclude "
          f"(links must not read as dirt)")


def other_linked_worktrees(worktree: Path) -> list[str]:
    """Linked worktrees of this repo OTHER than `worktree` (the main checkout not counted)."""
    rp = subprocess.run(
        ["git", "-C", str(worktree), "worktree", "list", "--porcelain"],
        capture_output=True, encoding="utf-8", text=True,
    )
    if rp.returncode != 0:
        return []
    trees = [ln[len("worktree "):] for ln in rp.stdout.splitlines() if ln.startswith("worktree ")]
    me = os.path.realpath(str(worktree))
    return [t for t in trees[1:] if os.path.realpath(t) != me]   # trees[0] is the main checkout


def remove_exclude_entries(worktree: Path) -> None:
    """Drop the managed block - but only when no OTHER linked worktree still needs it."""
    excl = common_exclude_path(worktree)
    if excl is None or not excl.is_file():
        return
    text = excl.read_text(encoding="utf-8")
    if EXCLUDE_BEGIN not in text:
        return
    others = other_linked_worktrees(worktree)
    if others:
        print(f"  exclude:  kept - {len(others)} other linked worktree(s) still use the entries")
        return
    rest, _ = _split_managed_block(text)
    excl.write_text(rest, encoding="utf-8")
    print("  exclude:  managed block removed (this was the last linked worktree)")


def repo_root(start: Path) -> Path:
    """The main WORKING TREE — from a linked worktree, and from inside a SUBMODULE.

    ⛔ NOT `Path(--git-common-dir).parent` on its own. That is right only when the git dir is
    literally `<worktree>/.git`. In a submodule the common dir is `<super>/.git/modules/<name>`,
    so the parent is `<super>/.git/modules` — a gitdir, never a checkout. The asset scan then
    finds nothing and prints "nothing to link", which is indistinguishable from an honestly
    empty repo. That was the measured defect (SCC-255): an AGY lane reported nothing to link
    over a checkout that plainly carries `backend/.venv`.

    Git has exactly TWO rules for finding the checkout behind a git dir, and both are needed:

      `core.worktree` set  -> that, resolved RELATIVE TO THE GIT DIR. This is what a submodule
                              sets (`../../../sub`), and it is the whole fix.
      unset                -> the git dir's parent. The ordinary `<repo>/.git` case.

    ⛔ And do NOT try to collapse them into one `git -C <common-dir> rev-parse --show-toplevel`.
    It looks like it works — it is correct for the submodule — but inside a plain `<repo>/.git`
    git answers `fatal: this operation must be run in a work tree`, so that shortcut refuses
    every ordinary repo in the house. Ten command bodies call this script at worktree-open time;
    the regression block in the test file is what caught it.

    The candidate is then VERIFIED to be a working-tree root, because a wrong path that links
    real files somewhere unexpected is worse than a refusal. Anything with no checkout behind it
    — a bare repo, a submodule whose directory was deleted — raises instead of returning a
    plausible-looking answer.
    """
    # ⛔ NO `check=True` here. It raises CalledProcessError, which is not what main() catches,
    # so the operator gets a raw traceback instead of the refusal this script promises — and the
    # promise is the whole point of the resolution work below. A lane whose `.git` file points at
    # a gitdir `git worktree prune` has already removed reaches exactly this line.
    rp = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True, encoding="utf-8", text=True,
    )
    if rp.returncode != 0 or not rp.stdout.strip():
        why = (rp.stderr or "").strip().splitlines()
        raise ResolutionError(
            f"{start} — git cannot name a git dir here: "
            f"{why[0] if why else 'rev-parse --git-common-dir printed nothing'}")
    common = Path(rp.stdout.strip())

    cw = subprocess.run(
        ["git", "-C", str(common), "config", "--get", "core.worktree"],
        capture_output=True, encoding="utf-8", text=True,
    )
    declared = cw.stdout.strip() if cw.returncode == 0 else ""
    candidate = Path(os.path.realpath(common / declared)) if declared else common.parent

    probe = subprocess.run(
        ["git", "-C", str(candidate), "rev-parse", "--path-format=absolute", "--show-toplevel"],
        capture_output=True, encoding="utf-8", text=True,
    )
    top = probe.stdout.strip()
    if probe.returncode != 0 or not top:
        why = (probe.stderr or "").strip().splitlines()
        raise ResolutionError(
            f"{candidate} (from git dir {common}) — {why[0] if why else 'it has no working tree'}")
    if Path(os.path.realpath(top)) != Path(os.path.realpath(candidate)):
        raise ResolutionError(
            f"{candidate} (from git dir {common}) — is inside a DIFFERENT repo, whose root is "
            f"{top}; refusing to link assets from a repo this worktree does not belong to")
    return candidate


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


def do_link(worktree: Path, repo: Path, copy_env: bool, require_assets: bool = False,
            verified: bool = True) -> int:
    """`verified` is False when the caller GAVE the repo with --repo instead of resolving it.

    ⛔ It is not decoration. The zero-assets report below claims the resolution was checked, and
    that claim is the entire point of the report — so it may only be made about a repo this
    script actually resolved. `--repo` skips `repo_root()`, which is exactly what the escape
    hatch is for, and printing "resolution verified" over it re-opens the ambiguity the report
    was written to close."""
    print(f"repo:     {repo}")
    print(f"worktree: {worktree}\n")

    assets = find_assets(repo)
    linked = skipped = unplaceable = 0
    env_symlinked = shared_node_modules = False
    placed_rels: list[str] = []
    for src, kind in assets:
        rel = src.relative_to(repo)
        dst = worktree / rel
        # ⛔ `as_posix()` in every PRINTED path, matching `placed_rels` below (SCC-321). `str(rel)`
        # renders `backend\.venv` on Windows and `backend/.venv` on the Mac, so this tool's output
        # said something different on each machine about the same asset — and anything reading it
        # (a doc, a receipt, an operator following a runbook) has to know which one it is looking
        # at. git prints POSIX separators on Windows for the same reason.
        shown = rel.as_posix()
        if not dst.parent.is_dir():
            print(f"  ! {shown} — its parent dir is not in the worktree, skipped")
            unplaceable += 1
            continue
        if dst.exists() or dst.is_symlink():
            print(f"  = {shown:<24} already present — left alone")
            skipped += 1
        else:
            how = link_dir(src, dst) if kind == "dir" else link_file(src, dst, copy_env)
            print(f"  + {shown:<24} {how}")
            linked += 1
        placed_rels.append(shown)
        env_symlinked = env_symlinked or (kind == "file" and dst.is_symlink())
        shared_node_modules = shared_node_modules or (rel.name == "node_modules" and dst.exists())

    if not linked and not skipped:
        # ⭐ SAY WHICH KIND OF ZERO THIS IS (SCC-255). Six of the nine local checkouts genuinely
        # have no linkable assets, and so does any repo before its first `npm install` — refusing
        # on the COUNT would make ten command bodies unable to open a lane in them. The defect was
        # never the zero; it was that every different reason for a zero printed one sentence.
        # There are THREE, and only the first may claim the repo genuinely has none:
        #   assets == []    the repo really is empty of them — and we resolved it ourselves
        #   unplaceable     assets ARE there, this worktree just has nowhere to put them
        #   not verified    --repo was given, so repo_root() never ran and nothing was checked
        print("  (nothing to link — no gitignored runtime assets at the repo root or one level down)"
              if not assets else
              f"  ({unplaceable} asset(s) FOUND in this repo, none placeable in this worktree — "
              f"see the `!` line(s) above)")
        if not assets and verified:
            print(f"  resolution verified: {repo} — this repo genuinely has none.")
        elif not assets:
            print(f"  ⚠ NOT verified: {repo} was given with --repo, so it was never checked to be "
                  f"the working tree behind this worktree. Drop --repo to have it resolved.")
        if require_assets:
            print(f"error: --require-assets was given, but nothing was linked from {repo}"
                  + (f" ({unplaceable} asset(s) found but unplaceable)" if unplaceable
                     else " (it has no linkable assets at its root or one level down)"),
                  file=sys.stderr)
            return 1
        return 0

    write_exclude_entries(worktree, placed_rels)   # SCC-310: links must not read as dirt
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
    the hard way (see /cicd-prune-worktree Step 3): lanes link more than this script knows about,
    and TOOLS plant their own — Next.js/Turbopack creates junctions under frontend/.next/ just by
    running the dev server. A missed reparse point is not a cosmetic leak: the recursive delete that
    follows walks through it and destroys the shared target.
    """
    print(f"worktree: {worktree}\n")

    links = find_links(worktree)
    if not links:
        print("  (no reparse points found)")
        remove_exclude_entries(worktree)
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

    remove_exclude_entries(worktree)
    print(f"\n{len(links)} unlinked, 0 remaining. Safe to `git worktree remove` now.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Link gitignored runtime assets into a git worktree.")
    ap.add_argument("worktree", help="path to the worktree")
    ap.add_argument("--repo", help="source repo (default: this repo's main working tree)")
    ap.add_argument("--unlink", action="store_true", help="remove the links (run BEFORE worktree remove)")
    ap.add_argument("--copy-env", action="store_true", help="copy .env instead of linking it")
    ap.add_argument("--require-assets", action="store_true",
                    help="fail if the resolved repo has no linkable assets (for a caller that "
                         "KNOWS it should — most callers must not use this: six of nine local "
                         "repos legitimately have none)")
    args = ap.parse_args()

    worktree = Path(args.worktree).resolve()
    if not worktree.is_dir():
        print(f"error: not a directory: {worktree}", file=sys.stderr)
        return 2

    if args.unlink:
        return do_unlink(worktree)

    verified = not args.repo
    if args.repo:
        repo = Path(args.repo).resolve()
        # Not a refusal — --repo IS the escape hatch, and refusing here would close it. But a
        # path that is not a working-tree root is almost always a typo, and saying so beats
        # linking nothing and reporting a clean run.
        probe = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--path-format=absolute", "--show-toplevel"],
            capture_output=True, encoding="utf-8", text=True)
        top = probe.stdout.strip()
        if probe.returncode != 0 or not top:
            print(f"⚠ --repo {repo} is not a git working tree; linking from it anyway "
                  f"because you asked.", file=sys.stderr)
        elif Path(os.path.realpath(top)) != Path(os.path.realpath(repo)):
            print(f"⚠ --repo {repo} is not a repo ROOT; its root is {top}. Assets are only "
                  f"looked for at the root and one level down.", file=sys.stderr)
    else:
        try:
            repo = repo_root(worktree)
        except ResolutionError as exc:
            print(f"error: cannot resolve the repo behind {worktree}\n"
                  f"       {exc}\n"
                  f"       pass --repo <path> if you know which working tree these assets "
                  f"belong to", file=sys.stderr)
            return 1
    if repo == worktree:
        print("error: source repo and worktree are the same path", file=sys.stderr)
        return 2
    return do_link(worktree, repo, args.copy_env, args.require_assets, verified)


if __name__ == "__main__":
    raise SystemExit(main())
