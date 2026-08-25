#!/usr/bin/env python3
"""arm_hooks_path.py - immunise core.hooksPath against the worktree rewrite (SCC-323).

Claude Code's worktree setup parses the main repo's .git/config with a plain ini reader,
resolves a RELATIVE core.hooksPath to an ABSOLUTE one, and runs `git config core.hooksPath
<abs>` with cwd set to the new worktree. `git config` in a linked worktree writes the SHARED
config, so every worktree - and the main checkout - ends up running the MAIN checkout's hooks
instead of its own. A lane's gates are then not the gates being enforced on it.

The remedy keeps the value LOCAL and RELATIVE, but moves it out of .git/config into an
included file:

    .git/config      gains  [include] path = hooks.conf   (no hooksPath key remains here)
    .git/hooks.conf  holds  [core] hooksPath = .githooks

git follows include.path; the plain ini reader in the worktree setup does not, so it reads no
key and never fires.

Idempotent: running it twice changes nothing the second time. Repos with no .githooks/ are
skipped. A submodule's or worktree's real git dir is resolved via `rev-parse --git-common-dir`,
never by assuming `.git` is a directory.

Usage:
    python docs/migrations/scripts/arm_hooks_path.py
    python docs/migrations/scripts/arm_hooks_path.py --verify-only
    python docs/migrations/scripts/arm_hooks_path.py --repo Projects/AGY_AVIATIONCHAT
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# docs/migrations/scripts/ -> 3 levels up
DEFAULT_ROOT = Path(__file__).resolve().parents[3]

HOOKS_DIRNAME = ".githooks"
CONF_NAME = "hooks.conf"
CONF_BODY = "[core]\n\thooksPath = .githooks\n"

# The config KEY, not the substring: a section header such as
# [branch "chore/SCC-323-hookspath-immunisation"] contains the word and is not the key.
_KEY_RE = re.compile(r"\s*hooksPath\s*=", re.IGNORECASE)


def run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Execute git and return (returncode, stdout, stderr), both stripped."""
    try:
        res = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            errors="replace",
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except OSError as e:
        return 127, "", str(e)


def git_common_dir(repo: Path) -> Path | None:
    """Resolve the repo's REAL git dir - the shared one for a worktree, the module dir for a
    submodule. Never assumes `.git` is a directory."""
    rc, out, _ = run_git(["rev-parse", "--git-common-dir"], repo)
    if rc != 0 or not out:
        return None
    p = Path(out)
    return p if p.is_absolute() else (repo / p).resolve()


def discover_repos(root: Path) -> list[Path]:
    """The lobby plus every immediate child of Projects/ that is a git repo."""
    found = [root]
    projects = root / "Projects"
    if projects.is_dir():
        for child in sorted(projects.iterdir()):
            if child.is_dir() and (child / ".git").exists():
                found.append(child)
    return found


def local_hookspath_lines(config: Path) -> int:
    """How many hooksPath keys sit in the config FILE itself (not in anything it includes)."""
    if not config.is_file():
        return 0
    text = config.read_text(encoding="utf-8", errors="replace")
    return sum(1 for line in text.splitlines() if _KEY_RE.match(line))


def has_include(repo: Path) -> bool:
    """True if .git/config already includes hooks.conf. Reads the LOCAL scope only."""
    rc, out, _ = run_git(["config", "--local", "--get-all", "include.path"], repo)
    if rc != 0:
        return False
    return any(line.strip() == CONF_NAME for line in out.splitlines())


def arm(repo: Path, verify_only: bool) -> tuple[str, str]:
    """Return (status, detail). status is one of: skipped, armed, changed, FAILED."""
    if not (repo / HOOKS_DIRNAME).is_dir():
        return "skipped", f"no {HOOKS_DIRNAME}/"

    gitdir = git_common_dir(repo)
    if gitdir is None:
        return "FAILED", "could not resolve --git-common-dir"

    config = gitdir / "config"
    conf = gitdir / CONF_NAME

    if verify_only:
        return verify(repo, config)

    changed = False

    # 1. The included file carries the value. Write it first so no window exists where the
    #    hooks are unarmed.
    if not conf.is_file() or conf.read_text(encoding="utf-8", errors="replace") != CONF_BODY:
        # newline="" pins LF on Windows too. Without it write_text emits CRLF, the PowerShell
        # twin reads that as a mismatch, and the two rewrite each other's file forever.
        with open(conf, "w", encoding="utf-8", newline="") as fh:
            fh.write(CONF_BODY)
        changed = True

    # 2. .git/config includes it.
    if not has_include(repo):
        rc, _, err = run_git(["config", "--local", "--add", "include.path", CONF_NAME], repo)
        if rc != 0:
            return "FAILED", f"could not add include.path: {err}"
        changed = True

    # 3. Only now does the direct key leave .git/config. --local touches that file alone; the
    #    included file is untouched, so the value never disappears.
    if local_hookspath_lines(config) > 0:
        rc, _, err = run_git(["config", "--local", "--unset-all", "core.hooksPath"], repo)
        # 5 = key not present, which is the state we want anyway.
        if rc not in (0, 5):
            return "FAILED", f"could not unset core.hooksPath: {err}"
        changed = True

    status, detail = verify(repo, config)
    if status == "FAILED":
        return status, detail
    return ("changed" if changed else "armed"), detail


def verify(repo: Path, config: Path) -> tuple[str, str]:
    """Ask GIT what it resolves, and read the config FILE for the key that must be gone."""
    rc, value, _ = run_git(["config", "--get", "core.hooksPath"], repo)
    residue = local_hookspath_lines(config)

    if rc != 0 or value != HOOKS_DIRNAME:
        return "FAILED", f"git resolves core.hooksPath to {value!r} (want {HOOKS_DIRNAME!r})"
    if residue != 0:
        return "FAILED", f"{residue} hooksPath line(s) still in {config}"
    return "armed", f"core.hooksPath={value} - 0 lines in .git/config"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="workspace root")
    ap.add_argument("--repo", action="append", default=[], help="repo path (repeatable); default: discover")
    ap.add_argument("--verify-only", action="store_true", help="check, change nothing")
    args = ap.parse_args()

    root = args.root.resolve()
    if args.repo:
        repos = [(root / r).resolve() if not Path(r).is_absolute() else Path(r) for r in args.repo]
    else:
        repos = discover_repos(root)

    print(f"== arm_hooks_path @ {root} ==")
    print(f"   mode: {'VERIFY-ONLY' if args.verify_only else 'ARM'} - {len(repos)} repo(s)\n")

    failures = 0
    for repo in repos:
        status, detail = arm(repo, args.verify_only)
        if status == "FAILED":
            failures += 1
        label = repo.name if repo != root else f"{repo.name} (lobby)"
        print(f"[{status.upper():<7}] {label}: {detail}")

    print()
    if failures:
        print(f"-- {failures} repo(s) FAILED --")
        return 1
    print("-- all repos armed --")
    return 0


if __name__ == "__main__":
    sys.exit(main())
