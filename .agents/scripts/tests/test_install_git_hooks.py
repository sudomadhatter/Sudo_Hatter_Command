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
import shutil
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir, unset_hooks_path

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
    if c.block("SCC-115 · 1 · discovery finds every git repo and skips the rest"):
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
    if c.block("SCC-115 · 2 · arming a single repo sets core.hooksPath"):
        # ⛔ `unset_hooks_path()` or the "initially unset" assertion measures the OPERATOR'S GLOBAL
        # CONFIG, not the installer (SCC-321). A temp repo INHERITS `core.hooksPath`, and this
        # system tells the operator to set exactly that globally — so on such a machine the
        # fixture is born armed and the case is red for a reason the installer cannot control.
        with TempDir() as d, unset_hooks_path():
            seed_fixture_repo(d, has_hooks=True)
            c.check("initially core.hooksPath is unset", git("config", "--get", "core.hooksPath", cwd=d) == "")

            res_arm = install_git_hooks.arm_single_repo(d, verify_only=False)
            c.check("arm_single_repo sets hooksPath", res_arm["hooksPath"] == ".githooks")
            c.check("arm_single_repo reports armed = True", res_arm["armed"] is True)
            c.check("arm_single_repo has zero errors", len(res_arm["errors"]) == 0)
            c.check("git config reflects .githooks", git("config", "--get", "core.hooksPath", cwd=d) == ".githooks")

            # ⛔⛔ THE EFFECTIVE VALUE ALONE PASSES ON THE BROKEN ARRANGEMENT (SCC-323). Claude
            # Code's worktree setup parses .git/config, resolves a relative core.hooksPath to an
            # ABSOLUTE one and writes it back to the SHARED config — after which every worktree
            # runs the MAIN checkout's hooks instead of its own. It can only do that when the key
            # is IN .git/config. So "armed" has two halves: git resolves .githooks, AND the key is
            # not sitting in the file that gets rewritten. Assert both, or the installer is free to
            # regress to a bare `git config` and every case above stays green.
            cfg = (d / ".git" / "config").read_text(encoding="utf-8")
            c.check("the key is NOT written into .git/config - that key IS the rewrite trigger",
                    "hooksPath" not in cfg, cfg)
            c.check("it is reached through an include git follows", "hooks.conf" in cfg, cfg)
            c.check("and the included file carries the RELATIVE value",
                    "hooksPath = .githooks" in (d / ".git" / "hooks.conf").read_text(encoding="utf-8"))

            # idempotent: arming twice must not stack includes or change the answer
            install_git_hooks.arm_single_repo(d, verify_only=False)
            cfg2 = (d / ".git" / "config").read_text(encoding="utf-8")
            c.check("arming twice is a no-op", cfg2 == cfg and cfg2.count("hooks.conf") == 1, cfg2)

    # ── 3 · verify-only flag preserves config ────────────────────────────────────────
    if c.block("SCC-115 · 3 · --verify-only inspects without writing config"):
        with TempDir() as d, unset_hooks_path():   # see block 2 — the fixture must ENFORCE unset
            seed_fixture_repo(d, has_hooks=True)
            res_verify = install_git_hooks.arm_single_repo(d, verify_only=True)
            c.check("verify_only does not set hooksPath", res_verify["hooksPath"] == "")
            c.check("verify_only reports unarmed", res_verify["armed"] is False)
            c.check("git config remains unset", git("config", "--get", "core.hooksPath", cwd=d) == "")

    # ── 4 · full CLI execution with JSON output ─────────────────────────────────────
    if c.block("SCC-115 · 4 · the CLI end to end, with JSON output"):
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
    if c.block("SCC-115 · 5 · THIS repository is armed"):
        live_res = install_git_hooks.arm_single_repo(REPO, verify_only=True)
        c.check("live repository has core.hooksPath set", live_res["hooksPath"] == ".githooks")
        c.check("live repository reports ARMED", live_res["armed"] is True)
        c.check("live repository has 0 errors", len(live_res["errors"]) == 0, str(live_res["errors"]))

    #
    # ⛔ THE AUDIT FINDING, run for real. `.githooks/pre-commit` is a tracked dispatcher that now
    # chains TWO delegates (the maps refresh, then the encoding gate), and it necessarily contains
    # the string `pre-commit-encoding`. The installer's ownership test was `-match $MARKER`, so it
    # called that file its own and overwrote it with its three-line body — silently deleting the
    # maps delegate on any PC that ran the new-machine guide. `git status` would show a modified
    # `.githooks/pre-commit`, which reads as "the installer touched its own file".
    #
    # Ownership is now byte equality. Three outcomes, all asserted: foreign -> refuse,
    # ours-but-extended -> refuse, ours-and-identical -> allowed (rewriting is a no-op).
    #
    # ⛔ F2 AND F3 ARE SIBLING TOP-LEVEL BLOCKS, never one nested in the other. `_harness`'s
    # `--case` filter selects blocks, the mutation sweep aims its kills through that filter, and a
    # block declared inside another block's body is only ever REACHED when the outer label matches
    # — so a mutant aimed at it returns exit 3 (NO_MATCH), which the sweep records as an error in
    # the sweep rather than a result about the code. Their shared fixtures are hoisted above both.
    ps = shutil.which("pwsh") or shutil.which("powershell")
    installer = REPO / ".agents" / "scripts" / "git-hooks" / "install-encoding-hook.ps1"
    own_body = (
        "#!/bin/sh\n"
        "# pre-commit-encoding (installed by "
        ".agents/scripts/git-hooks/install-encoding-hook.ps1)\n"
        'exec "$(git rev-parse --show-toplevel)'
        '/.agents/scripts/git-hooks/pre-commit-encoding.sh" "$@"\n'
    )
    EXTENDED = ("#!/bin/sh\n# two delegates\n"
                'MAPS="$ROOT/.agents/scripts/git-hooks/pre-commit-maps.sh"\n'
                '[ -x "$MAPS" ] && { "$MAPS" "$@" || exit $?; }\n'
                'exec "$ROOT/.agents/scripts/git-hooks/pre-commit-encoding.sh" "$@"\n')
    FOREIGN = "#!/bin/sh\nsomeone-elses-hook\n"

    def run_installer(body: str, *extra: str):
        """One scenario: plant `body` as the repo's pre-commit hook, run the installer, report."""
        with TempDir() as tmp:
            d = tmp / "wk"
            seed_fixture_repo(d)
            subprocess.run(["git", "config", "core.hooksPath", ".githooks"],
                           cwd=str(d), capture_output=True)
            hook = d / ".githooks" / "pre-commit"
            hook.write_text(body, encoding="utf-8")
            r = subprocess.run([ps, "-NoProfile", "-File", str(installer), "-Repo", str(d),
                                *extra], capture_output=True, text=True)
            said = ("REFUSED" if "REFUSED" in r.stdout else
                    "removed" if "removed" in r.stdout else
                    "installed" if "installed" in r.stdout else
                    "SKIP" if "SKIP" in r.stdout else f"?? {r.stdout[-160:]}")
            after = hook.read_text(encoding="utf-8") if hook.exists() else None
            return said, after, r

    if c.block("F2 · SCC-290 · -Install refuses to clobber an EXTENDED dispatcher"):
        if not ps:
            c.check("F2 SKIPPED - no PowerShell on this machine (the PC path is unverified here)",
                    True, "install pwsh to run this case")
        else:
            for label, want, body in (
                ("extended (ours + the maps delegate)", "REFUSED", EXTENDED),
                ("foreign (no marker at all)", "REFUSED", FOREIGN),
                ("ours, byte-identical", "installed", own_body),
            ):
                said, after, r = run_installer(body)
                c.check(f"F2 {label} -> {want}", said == want,
                        f"said {said!r}; rc={r.returncode}; stderr={r.stderr[-200:]}")
                if want == "REFUSED":
                    c.check(f"F2 {label}: and the file on disk is UNTOUCHED", after == body,
                            "the installer rewrote a hook it had just refused")

    # ── F3 · SCC-288 · -Uninstall must use the SAME ownership test as -Install ───────────────
    # ⛔ REVIEW FINDING R2. F2 replaced the marker-only ownership test on the INSTALL path and left
    # `-Uninstall` on the old one, where the consequence is worse: install overwrites a tracked
    # file (visible in `git status`, recoverable with `git checkout`), uninstall DELETES it.
    # `.githooks/pre-commit` is tracked, it necessarily contains the marker, and SCC-290 made it
    # chain the maps refresh as well — so removing "the encoding hook" silently disarmed two gates
    # and left the operator with no hook file at all.
    #
    # Same three outcomes as F2, and the middle one is the finding: ours-but-EXTENDED is refused,
    # not deleted. Only a byte-identical hook of ours is removed, because that is the only file
    # this installer can prove it wrote.
    if c.block("F3 · SCC-288 · -Uninstall must not delete a hook it did not write"):
        if not ps:
            c.check("F3 SKIPPED - no PowerShell on this machine (the PC path is unverified here)",
                    True, "install pwsh to run this case")
        else:
            for label, want, body in (
                ("extended (ours + the maps delegate)", "REFUSED", EXTENDED),
                ("foreign (no marker at all)", "SKIP", FOREIGN),
                ("ours, byte-identical", "removed", own_body),
            ):
                said, after, r = run_installer(body, "-Uninstall")
                c.check(f"F3 -Uninstall {label} -> {want}", said == want,
                        f"said {said!r}; rc={r.returncode}; stderr={r.stderr[-200:]}")
                if want == "removed":
                    c.check("F3 ours, byte-identical: the file is GONE", after is None,
                            "the installer refused to remove the hook it wrote itself")
                else:
                    c.check(f"F3 {label}: the file SURVIVES with its bytes intact", after == body,
                            "-Uninstall deleted a hook this installer did not write")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
