"""test_install_git_hooks.py — tests for the git hooks installer (SCC-115).

Verifies that install_git_hooks.py:
1. Discovers root repo and valid git submodules under Projects/.
2. Sets core.hooksPath to .githooks and arms gates across repositories.
3. Respects --verify-only by inspecting without writing config.
4. Correctly produces JSON output and clean console summaries.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

REPO = Path(__file__).resolve().parents[3]
INSTALLER_PATH = REPO / "docs" / "migrations" / "scripts" / "install_git_hooks.py"

# Add migration scripts path to sys.path
sys.path.insert(0, str(INSTALLER_PATH.parent))
import install_git_hooks  # noqa: E402


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        errors="replace",
    ).stdout.strip()


def seed_fixture_repo(d: Path, *, has_hooks: bool = True) -> None:
    """Create a minimal git repo fixture."""
    d.mkdir(parents=True, exist_ok=True)
    git("init", "-q", cwd=d)
    if has_hooks:
        hd = d / ".githooks"
        hd.mkdir(parents=True, exist_ok=True)
        for h in ("commit-msg", "pre-commit", "post-commit", "pre-push"):
            p = hd / h
            p.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        gh = d / ".agents" / "scripts" / "git-hooks"
        gh.mkdir(parents=True, exist_ok=True)
        for s in ("commit-msg-jira.sh", "sop-currency.sh", "pre-push-main-approval.sh",
                  "pre-commit-encoding.sh", "merge-target-guard.sh"):
            (gh / s).write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        for f in ("JIRA-ENFORCE", "SOP-ENFORCE", "MAIN-PUSH-ENFORCE", "MERGE-TARGET-ENFORCE"):
            (gh / f).write_text("armed\n", encoding="utf-8")
    git("add", "-A", cwd=d)


def main() -> int:
    c = Cases("install_git_hooks (SCC-115)")

    # ── 1 · discovery tests ──────────────────────────────────────────────────────────
    with TempDir() as d:
        seed_fixture_repo(d)
        proj_dir = d / "Projects"
        proj_dir.mkdir(parents=True, exist_ok=True)

        p1 = proj_dir / "Project_A"
        seed_fixture_repo(p1)

        p2 = proj_dir / "Project_B"
        seed_fixture_repo(p2)

        p_nogit = proj_dir / "Not_A_Git_Repo"
        p_nogit.mkdir(parents=True, exist_ok=True)

        repos = install_git_hooks.discover_repos(d)
        c.check("discovers root repo", d in repos)
        c.check("discovers subprojects with .git", p1 in repos and p2 in repos)
        c.check("skips non-git subdirectories", p_nogit not in repos)
        c.check("total discovered count is 3", len(repos) == 3)

    # ── 2 · single repo arming ───────────────────────────────────────────────────────
    with TempDir() as d:
        seed_fixture_repo(d, has_hooks=True)
        c.check("initially core.hooksPath is unset", git("config", "--get", "core.hooksPath", cwd=d) == "")

        res_arm = install_git_hooks.arm_single_repo(d, verify_only=False)
        c.check("arm_single_repo sets hooksPath", res_arm["hooksPath"] == ".githooks")
        c.check("arm_single_repo reports armed = True", res_arm["armed"] is True)
        c.check("arm_single_repo has zero errors", len(res_arm["errors"]) == 0)
        c.check("git config reflects .githooks", git("config", "--get", "core.hooksPath", cwd=d) == ".githooks")

    # ── 3 · verify-only flag preserves config ────────────────────────────────────────
    with TempDir() as d:
        seed_fixture_repo(d, has_hooks=True)
        res_verify = install_git_hooks.arm_single_repo(d, verify_only=True)
        c.check("verify_only does not set hooksPath", res_verify["hooksPath"] == "")
        c.check("verify_only reports unarmed", res_verify["armed"] is False)
        c.check("git config remains unset", git("config", "--get", "core.hooksPath", cwd=d) == "")

    # ── 4 · full CLI execution with JSON output ─────────────────────────────────────
    with TempDir() as d:
        seed_fixture_repo(d, has_hooks=True)
        p = d / "Projects" / "SubProj"
        seed_fixture_repo(p, has_hooks=True)

        proc = subprocess.run(
            [sys.executable, str(INSTALLER_PATH), "--root", str(d), "--json"],
            capture_output=True,
            text=True,
            errors="replace",
        )
        c.check("CLI returns exit 0", proc.returncode == 0, f"rc={proc.returncode}")
        try:
            data = json.loads(proc.stdout)
            c.check("JSON output parsed successfully", True)
            c.check("JSON reports 0 total_errors", data.get("total_errors") == 0)
            c.check("JSON contains 2 results", len(data.get("results", [])) == 2)
        except Exception as e:
            c.check("JSON output parsed successfully", False, str(e))

    # ── 5 · live repo verification ──────────────────────────────────────────────────
    live_res = install_git_hooks.arm_single_repo(REPO, verify_only=True)
    c.check("live repository has core.hooksPath set", live_res["hooksPath"] == ".githooks")
    c.check("live repository reports ARMED", live_res["armed"] is True)
    c.check("live repository has 0 errors", len(live_res["errors"]) == 0, str(live_res["errors"]))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
