#!/usr/bin/env python3
"""Arm core.hooksPath in a way Claude Code's worktree setup cannot rewrite.

THE DEFECT this works around (Claude Code, function `w4l`): when it creates a git worktree it
parses the main repo's .git/config, reads core.hooksPath, resolves a RELATIVE value to an
ABSOLUTE one, and writes it back with `git config core.hooksPath <abs>` run inside the new
worktree. `git config` in a linked worktree writes the SHARED config, so that one-worktree
setting overwrites the value for the main checkout and every other lane. An absolute value
makes every worktree run the MAIN checkout's hooks instead of its own.

THE WORKAROUND: keep the value local and relative, but move it out of .git/config into an
included file. git follows include.path; a plain ini reader pointed at .git/config does not,
so the rewrite never fires.

Idempotent. Run it as many times as you like.

    python arm_hooks_include.py <repo> [<repo> ...]      # Windows
    python3 arm_hooks_include.py <repo> [<repo> ...]     # macOS / Linux
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CONF_NAME = "hooks.conf"
CONF_BODY = """\
# Loaded by .git/config via include.path.
#
# core.hooksPath MUST stay RELATIVE so the main checkout and every worktree each read their
# OWN .githooks/. It lives HERE, not in .git/config, because Claude Code's worktree setup
# parses .git/config directly, resolves a relative hooksPath to an ABSOLUTE one, and writes
# it back to the SHARED config -- silently repointing every worktree at the main checkout's
# hooks. It only does that when it can SEE the key. Here, it cannot.
[core]
\thooksPath = .githooks
"""


def git(repo: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, errors="replace")
    return r.returncode, r.stdout.strip()


def git_common_dir(repo: Path) -> Path | None:
    """The REAL .git directory. A submodule's .git is a FILE; a worktree's is too."""
    rc, out = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if rc != 0 or not out:
        return None
    return Path(out)


def arm(repo: Path) -> str:
    if not (repo / ".git").exists():
        return f"SKIP  {repo}  (not a git repo)"
    if not (repo / ".githooks").is_dir():
        return f"SKIP  {repo}  (no .githooks/ to point at)"

    gitdir = git_common_dir(repo)
    if gitdir is None:
        return f"ERROR {repo}  (could not resolve the git dir)"

    config = gitdir / "config"
    conf = gitdir / CONF_NAME

    # 1. the value goes in the included file
    current = conf.read_text(encoding="utf-8") if conf.exists() else None
    if current != CONF_BODY:
        conf.write_text(CONF_BODY, encoding="utf-8")

    # 2. remove any hooksPath key living directly in .git/config -- that key IS the trigger
    git(repo, "config", "--local", "--unset-all", "core.hooksPath")

    # 3. wire the include exactly once
    text = config.read_text(encoding="utf-8")
    if CONF_NAME not in text:
        config.write_text(text.rstrip("\n") + f"\n[include]\n\tpath = {CONF_NAME}\n",
                          encoding="utf-8")

    # 4. verify by asking GIT, not by trusting the write
    rc, effective = git(repo, "config", "--get", "core.hooksPath")
    visible = "hooksPath" in config.read_text(encoding="utf-8")
    ok = effective == ".githooks" and not visible
    return (f"{'OK   ' if ok else 'FAIL '} {repo}  effective={effective or '(unset)'}  "
            f"visible-in-.git/config={visible}")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    results = [arm(Path(a).resolve()) for a in argv]
    for line in results:
        print(line)
    return 0 if all(r.startswith(("OK", "SKIP")) for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
