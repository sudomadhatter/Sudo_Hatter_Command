"""Build a fixture repo ONCE per shape, then hand every scenario a clean CLONE of it. (SCC-214)

`test_task_preflight.py` and `test_git_hooks.py` each build a real throwaway git repo per
scenario — `git init`, config, commits, hooks — and between them they set the wall clock of the
whole enforcement suite. This module replaces the construction with a reset from a template,
under the ticket's non-negotiable constraint:

    RESET-FROM-TEMPLATE, NEVER A SHARED MUTABLE REPO. `test_git_hooks.py` guards the merge gate;
    scenario N seeing state left by scenario N-1 trades a real safety property for seconds.

So a scenario never touches the template: it gets its own byte-identical copy, in its own
`TempDir`, and `test_repo_template.py` fails if anything crosses between two of them.

⭐ WHY EXECUTABLES ARE HARD-LINKED AND THE TEMPLATE'S COPIES ARE FROZEN. Measured on this Mac
(2026-08-21, `_artifacts/_main/2026-08-21_scc-214-template-clone-tests/measure/`): the OS assesses
every NEWLY CREATED executable once, on its first launch — 0.19-0.28 s idle, 1.6-2.8 s under the
suite's own parallel load, because the assessor serialises. It is keyed by INODE: a hard link to
an already-launched file costs 0.006 s, while a byte copy, an APFS clone and a byte-identical new
file each pay in full. Both suites create fresh executables per scenario (a fresh `acli` launcher
per preflight block, two to five hook scripts per git_hooks repo) — 88 + 72 first launches, about
58 s of the two files' 191 s. Linking pays it once per shape.

A shared inode is only safe because the template's executables are frozen `0o555`: an in-place
write raises `PermissionError` instead of reaching every other scenario. Git never writes a file
in place (it writes a temp file and renames), so checkouts, merges and branch switches over a
linked hook are isolated by construction — the rename replaces the directory entry and leaves the
template's inode untouched.

⛔ `HARD_LINKS` IS FALSE ON WINDOWS, DELIBERATELY. `_harness.TempDir.__exit__` cleans up with an
`rmtree` handler that chmods read-only files (`0o700`) so Windows can delete them — and a chmod
through a hard link would unfreeze the TEMPLATE, so the freeze would last exactly one scenario
there. The PC copies executables instead: identical semantics, and it has no assessor to save time
with. Any `os.link` failure (cross-device, a filesystem that refuses) falls back to `copy2` the
same way — correctness never depends on the link, only speed does.

Stdlib only, no pytest, matching everything else here. Single-threaded by contract: `run_all.py`
gives each test file its own process, and cases inside a file are sequential, so the cache needs
no lock.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Hashable

TEMPLATE_PREFIX = "wfscripts-tpl-"
"""Marks every template directory. `test_repo_template.py` greps a clone for it: a clone carrying
an absolute path back into a template is a leak, however clean its `git status` reads."""

_ROOT: Path | None = None
_CACHE: dict[Hashable, Path] = {}


def _force(func, path, _info):  # read-only files (and .git objects) on Windows
    Path(path).chmod(0o700)
    func(path)


def _links_work() -> bool:
    if os.name == "nt":                      # see the module docstring: the rmtree handler
        return False
    probe = Path(tempfile.mkdtemp(prefix=TEMPLATE_PREFIX + "probe-"))
    try:
        a = probe / "a"
        a.write_text("x", encoding="utf-8")
        a.chmod(0o555)
        b = probe / "b"
        os.link(a, b)
        return a.stat().st_ino == b.stat().st_ino
    except OSError:
        return False
    finally:
        shutil.rmtree(probe, onerror=_force)


HARD_LINKS = _links_work()


def shared_root() -> Path:
    """The one directory this process keeps its templates in, removed at exit.

    Lazily created, so importing this module costs nothing. A SIGKILL leaks one small directory
    under TMPDIR; `run_all.stop_running` sends SIGINT first, which unwinds normally.
    """
    global _ROOT
    if _ROOT is None:
        _ROOT = Path(tempfile.mkdtemp(prefix=TEMPLATE_PREFIX))
        import atexit
        atexit.register(_cleanup)
    return _ROOT


def _cleanup() -> None:
    global _ROOT
    if _ROOT is not None and _ROOT.exists():
        shutil.rmtree(_ROOT, onerror=_force)
    _ROOT = None


def _seal(root: Path) -> None:
    """Make a finished template safe to share: no path back to itself, no writable executable."""
    for fetch_head in root.rglob("FETCH_HEAD"):
        # Written by `git fetch`, and it records the ABSOLUTE URL it fetched from - the one file
        # in these fixtures that would carry the template's path into every clone.
        fetch_head.unlink()
    for p in root.rglob("*"):
        if p.is_file() and not p.is_symlink() and (p.stat().st_mode & 0o111):
            p.chmod(0o555)


def _template(key: Hashable, build: Callable[[Path], object]) -> Path:
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    root = Path(tempfile.mkdtemp(prefix=TEMPLATE_PREFIX, dir=shared_root()))
    try:
        build(root)
    except BaseException:
        # ⛔ A HALF-BUILT TEMPLATE IS NEVER CACHED. Cached, it would be handed to every later
        # scenario of this shape, and the failure would present as N mystery cases rather than
        # the one builder that raised.
        shutil.rmtree(root, onerror=_force)
        raise
    _seal(root)
    _CACHE[key] = root
    return root


def _copy_entry(src: Path, dst: Path) -> None:
    if src.is_symlink():
        os.symlink(os.readlink(src), dst)
    elif src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        for child in sorted(src.iterdir()):
            _copy_entry(child, dst / child.name)
    elif HARD_LINKS and (src.stat().st_mode & 0o111):
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    else:
        shutil.copy2(src, dst)


def clone(key: Hashable, build: Callable[[Path], object], dest: Path) -> Path:
    """Return `dest`, holding a fresh copy of the template `build` makes for `key`.

    `build(root)` writes whatever the fixture is into `root`; it runs at most once per key per
    process. `dest` may be missing or an EMPTY directory — `test_task_preflight_receipts.py`
    creates its scenario root before calling the builder, so "the directory exists" cannot be the
    refusal. What IS refused is a `dest` already holding one of the template's own entries: that
    is a second fixture landing on top of a live one, which the builders' `mkdir()` refused before
    this module existed.
    """
    tpl = _template(key, build)
    dest = Path(dest)
    if dest.exists():
        clash = [e.name for e in sorted(tpl.iterdir()) if (dest / e.name).exists()]
        if clash:
            raise FileExistsError(f"{dest} already holds {', '.join(clash)} - "
                                  f"a second fixture is landing on a live one")
    dest.mkdir(parents=True, exist_ok=True)
    for entry in sorted(tpl.iterdir()):
        _copy_entry(entry, dest / entry.name)
    return dest
