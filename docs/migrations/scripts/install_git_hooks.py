#!/usr/bin/env python3
"""install_git_hooks.py — arm and verify git gates across all repos (SCC-115).

`core.hooksPath` is local git configuration that git NEVER transfers across clones or machines.
On a fresh clone or new machine, `core.hooksPath` is unset by default, leaving every gate
(Jira key check, SOP currency, push approval, merge target guard, encoding checks) silently OFF.

This script arms git hooks across the Home Base repo and all maintained project repositories:
1. Configures `git config core.hooksPath .githooks` for each repository.
2. Ensures executable permissions (0o755) on all hook and gate scripts on POSIX (macOS/Linux).
3. Executes `hooks_armed.py` inspection across every configured repository to verify 100% armed status.

Usage:
    python docs/migrations/scripts/install_git_hooks.py
    python docs/migrations/scripts/install_git_hooks.py --verify-only
    python docs/migrations/scripts/install_git_hooks.py --repo Projects/AGY_AVIATIONCHAT
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

# Resolve repo root relative to this script: docs/migrations/scripts/ -> 3 levels up
DEFAULT_ROOT = Path(__file__).resolve().parents[3]

# Add .agents/scripts to sys.path to access hooks_armed and wf_common
AGENTS_SCRIPTS = DEFAULT_ROOT / ".agents" / "scripts"
if str(AGENTS_SCRIPTS) not in sys.path and AGENTS_SCRIPTS.exists():
    sys.path.insert(0, str(AGENTS_SCRIPTS))

try:
    import hooks_armed
except ImportError:
    hooks_armed = None


def run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Execute git command and return (returncode, stdout, stderr)."""
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


def is_git_repo(path: Path) -> bool:
    """Return True if path is a git repository (contains .git dir or git file)."""
    git_entry = path / ".git"
    return git_entry.exists()


def discover_repos(root: Path, explicit_repo: Path | None = None) -> list[Path]:
    """Discover all git repositories to arm: root + project submodules."""
    if explicit_repo:
        target = explicit_repo if explicit_repo.is_absolute() else (root / explicit_repo).resolve()
        return [target] if is_git_repo(target) else []

    repos: list[Path] = []
    if is_git_repo(root):
        repos.append(root)

    projects_dir = root / "Projects"
    if projects_dir.is_dir():
        for item in sorted(projects_dir.iterdir()):
            if item.is_dir() and is_git_repo(item):
                repos.append(item)

    return repos


def make_executable(path: Path) -> None:
    """Set 0o755 executable permissions on POSIX systems."""
    if os.name != "nt" and path.is_file():
        try:
            current = path.stat().st_mode
            path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            pass


def fix_permissions_for_repo(repo: Path) -> None:
    """Ensure all hook scripts in .githooks and .agents have executable bits on POSIX."""
    if os.name == "nt":
        return

    githooks_dir = repo / ".githooks"
    if githooks_dir.is_dir():
        for item in githooks_dir.iterdir():
            if item.is_file() and not item.name.startswith(".") and not item.suffix:
                make_executable(item)

    scripts_dir = repo / ".agents" / "scripts" / "git-hooks"
    if scripts_dir.is_dir():
        for item in scripts_dir.iterdir():
            if item.is_file() and item.suffix == ".sh":
                make_executable(item)

    hooks_dir = repo / ".agents" / "hooks"
    if hooks_dir.is_dir():
        for item in hooks_dir.iterdir():
            if item.is_file() and item.suffix in (".sh", ".py"):
                make_executable(item)


def arm_single_repo(repo: Path, verify_only: bool = False) -> dict:
    """Arm a single repo by configuring core.hooksPath and verifying status."""
    result = {
        "repo": str(repo),
        "name": repo.name,
        "action": "verified" if verify_only else "armed",
        "hooksPath": "",
        "armed": False,
        "claims_gates": False,
        "errors": [],
        "warnings": [],
    }

    if not verify_only:
        rc, _, err = run_git(["config", "core.hooksPath", ".githooks"], cwd=repo)
        if rc != 0:
            result["errors"].append(f"Failed to set core.hooksPath: {err}")
        fix_permissions_for_repo(repo)

    # Read back current configuration
    _, current_hooks_path, _ = run_git(["config", "--get", "core.hooksPath"], cwd=repo)
    result["hooksPath"] = current_hooks_path

    # Run scan via hooks_armed if available
    if hooks_armed:
        scan_res = hooks_armed.scan(repo)
        result["claims_gates"] = scan_res.get("claims_gates", False)
        result["armed"] = scan_res.get("armed", False)

        for f in scan_res.get("findings", []):
            if f["sev"] == "ERROR":
                if hooks_armed.is_soft(f, scan_res):
                    result["warnings"].append(f["msg"])
                else:
                    result["errors"].append(f["msg"])
            elif f["sev"] == "WARN":
                result["warnings"].append(f["msg"])
    else:
        # Fallback inspection if hooks_armed module is unavailable
        result["armed"] = (current_hooks_path == ".githooks")
        if not result["armed"]:
            result["errors"].append(f"core.hooksPath is '{current_hooks_path}', expected '.githooks'")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Arm and verify Git hooks and gates across all repositories (SCC-115)."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"Root directory of the workspace (default: {DEFAULT_ROOT})",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Target a specific repository instead of scanning all discovered repos",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Check and verify hook status without modifying git config",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON summary",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )

    args = parser.parse_args()
    root = args.root.resolve()
    repos = discover_repos(root, args.repo)

    if not repos:
        if not args.quiet:
            print(f"[ERROR] No git repositories found under {root}", file=sys.stderr)
        return 1

    results: list[dict] = []
    hard_errors = 0

    for repo in repos:
        res = arm_single_repo(repo, verify_only=args.verify_only)
        results.append(res)
        hard_errors += len(res["errors"])

    if args.json:
        print(json.dumps({"results": results, "total_errors": hard_errors}, indent=2))
        return 0 if hard_errors == 0 else 1

    if not args.quiet:
        mode_str = "Verification" if args.verify_only else "Installation & Arming"
        print(f"=== Git Hooks {mode_str} (SCC-115) ===")
        print(f"Root: {root}\n")

        for r in results:
            if r["armed"]:
                status_tag = "[ARMED]"
            elif not r["claims_gates"]:
                status_tag = "[NO GATES CLAIMED]"
            else:
                status_tag = "[UNARMED]"

            print(f"{status_tag} {r['name']} ({r['repo']})")
            print(f"  core.hooksPath: {r['hooksPath'] or '(unset)'}")
            for w in r["warnings"]:
                print(f"  [WARN]  {w}")
            for e in r["errors"]:
                print(f"  [ERROR] {e}")
            print()

        if hard_errors == 0:
            action_done = "verified" if args.verify_only else "armed"
            print(f"Done. All maintained repositories {action_done} and active.")
        else:
            print(f"Failed. {hard_errors} error(s) detected across {len(results)} repository(ies).", file=sys.stderr)

    return 0 if hard_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
