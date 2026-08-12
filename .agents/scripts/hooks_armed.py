"""hooks_armed.py — are this repo's git gates actually RUNNING? (SCC-110)

git NEVER carries `core.hooksPath`. It is local config, per repo, per machine, and a fresh clone
has it UNSET. Unset does not fail: git reads `.git/hooks`, which is empty, so every gate this
system owns — the Jira key check, the encoding check, the SOP-currency check, the main-push
approval gate — is silently OFF, and every flow reports green.

SCC-77 proved the cost. Five Claude hooks were wired to `powershell` + `python`, neither of which
exists on the Mac, and all five exited 127 silently for weeks; six merges reached `main` on one
sign-off. It then built this check for exactly ONE gate, inside `test_main_push_gate.py`. This
generalises it and — more importantly — moves it to where the operator actually reads a verdict.

THREE WAYS A GATE IS OFF, and each is silent on its own:

    1. core.hooksPath   UNTRACKED, per machine. The master switch. Unset -> nothing runs.
    2. the inner script  Every dispatcher in `.githooks/` ends with the same two-liner —
                         `[ -x "$SCRIPT" ] || exit 0`. Delete the script, or merely drop its
                         executable bit, and the hook exits 0 with NO OUTPUT AT ALL.
    3. <NAME>-ENFORCE    TRACKED, per gate. Absent -> the gate WARNS instead of REJECTING, and
                         hook output is rendered nowhere the operator looks. See JIRA-ENFORCE.

⭐ THE EXPECTED SET COMES FROM `git ls-files`, NOT FROM `iterdir()`. The difference is the whole
correctness of this script. A directory listing cannot tell "this gate was deleted" from "this
repo never had that gate", so an earlier cut of this file reported ARMED with zero findings on a
repo whose three gate scripts had all been removed — the exact vacuous green it exists to prevent.
Asking the index answers both, and it also ignores untracked junk (a stray `.DS_Store` in
`.githooks/` is not a broken hook).

It REPORTS. It never arms. Silently rewriting a machine's git config out from under the operator
is worse than telling them; the remedy is one line and it is printed.

    hooks_armed.py [--repo PATH] [--json]

Exit: 0 clean · 1 warnings · 2 blocking.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK_DIR = ".githooks"
SCRIPT_DIR = ".agents/scripts/git-hooks"
# NOT `--global`. A relative path set globally arms `.githooks/` in EVERY repo on the machine,
# including third-party clones that happen to ship that directory. Per-repo is what the rest of
# this system actually does — see `.githooks/post-commit` and `new-project.ps1`.
REMEDY = "git config core.hooksPath .githooks"

# ⛔ DECLARED, not derived — and that is deliberate. `core.hooksPath` tells you which hook FILES
# git runs. Nothing on disk tells you which inner script a `*-ENFORCE` flag arms, because the
# mapping is not one-to-one: `.githooks/commit-msg` dispatches BOTH `commit-msg-jira.sh`
# (JIRA-ENFORCE) and `sop-currency.sh` (SOP-ENFORCE) — two flags, two scripts, ONE hook file —
# and SOP-ENFORCE corresponds to no `.githooks/sop` at all. A filename-derivation cannot answer
# it. So the pairing is written down, and a flag that appears without a row is REPORTED rather
# than swallowed, which is what keeps this table from going stale silently.
#
# This table governs the FLAG question ONLY. Script executability is checked for every tracked
# `*.sh` in `git-hooks/`, flag or no flag — `pre-commit-encoding.sh` is armed unconditionally and
# has no flag, and leaving it out of the executable check would exempt the encoding gate from the
# very failure mode this script was written for.
ARM_FLAGS = {
    "JIRA-ENFORCE":      ("commit-msg-jira.sh", "commit-msg"),
    "SOP-ENFORCE":       ("sop-currency.sh", "commit-msg"),
    "MAIN-PUSH-ENFORCE": ("pre-push-main-approval.sh", "pre-push"),
}


def git_root(start: str | Path) -> Path:
    """Walk up for the repo root. Running from a subdirectory must not read as 'no hooks'."""
    r = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, errors="replace")
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else Path(start)


def _git_config(repo: Path, key: str) -> str:
    """`git config --get` exits 1 when the key is unset — that is data, not an error."""
    r = subprocess.run(["git", "-C", str(repo), "config", "--get", key],
                       capture_output=True, text=True, errors="replace")
    return r.stdout.strip() if r.returncode == 0 else ""


def _tracked(repo: Path, pathspec: str) -> list[str]:
    """Repo-relative paths git actually tracks. The index, not the filesystem — see module doc."""
    r = subprocess.run(["git", "-C", str(repo), "ls-files", "-z", "--", pathspec],
                       capture_output=True, text=True, errors="replace")
    return sorted(p for p in r.stdout.split("\0") if p) if r.returncode == 0 else []


def is_executable(p: Path) -> bool:
    """⚠ Windows has no POSIX executable bit.

    CPython synthesises `st_mode` there from file attributes and sets the exec bits only for
    `.exe/.bat/.cmd/.com`, so every extensionless hook and every `.sh` would read as dead — and
    git-for-windows does not consult that bit for hooks anyway. Reporting a running gate as dead
    is worse than not checking: it would block close-out on the PC and print `chmod +x` as the
    remedy on a machine that has no `chmod`. Existence is the honest answer there.
    """
    if not p.is_file():
        return False
    if os.name == "nt":
        return True
    return p.stat().st_mode & 0o111 != 0


def scan(repo: Path) -> dict:
    """Read the arm state of every gate in `repo`. Pure inspection — writes nothing."""
    repo = Path(repo)
    findings: list[dict] = []
    hooks: list[dict] = []
    flags: list[dict] = []

    def err(msg: str, code: str = "unarmed") -> None:
        findings.append({"sev": "ERROR", "code": code, "msg": msg})

    def warn(msg: str, code: str = "advisory") -> None:
        findings.append({"sev": "WARN", "code": code, "msg": msg})

    expected = [Path(p).name for p in _tracked(repo, f"{HOOK_DIR}/*")]
    gate_scripts = _tracked(repo, f"{SCRIPT_DIR}/*.sh")
    tracked_flags = [Path(p).name for p in _tracked(repo, f"{SCRIPT_DIR}/*-ENFORCE")]

    # Does this repo CLAIM to have gates? Used only to weigh the "no hooks at all" finding —
    # see `check()`. A repo declaring a Jira project, or shipping gate scripts, is asserting
    # that its commits are checked; a repo doing neither never made that claim.
    claims_gates = bool(gate_scripts) or (repo / ".agents/jira.conf").is_file()

    # ⭐ Nothing to check must NEVER read as clean. But "no gates at all" is a different
    # condition from "gates that exist and are switched off", and `check()` weighs them apart.
    if not expected:
        err(f"no hooks tracked in {HOOK_DIR}/ — nothing mechanical is checking this repo's "
            f"commits. Never 'nothing to check, therefore fine'.", code="no_hook_dir")
        return {"repo": str(repo), "hooks_path": _git_config(repo, "core.hooksPath") or None,
                "resolved": None, "armed": False, "claims_gates": claims_gates,
                "hooks": [], "flags": [], "findings": findings}

    configured = _git_config(repo, "core.hooksPath")
    if not configured:
        err(f"core.hooksPath is UNSET — git is reading .git/hooks, which is empty, so every "
            f"gate in this repo is OFF and says nothing. Remedy: {REMEDY}")
        resolved = None
    else:
        resolved = Path(configured) if Path(configured).is_absolute() else repo / configured
        if not resolved.is_dir():
            err(f"core.hooksPath = {configured!r} resolves to no directory ({resolved}) — "
                f"every gate is OFF. Remedy: {REMEDY}")

    for name in expected:
        present = bool(resolved) and (resolved / name).is_file()
        ok_exec = bool(resolved) and is_executable(resolved / name)
        hooks.append({"name": name, "present": present, "executable": ok_exec})
        if not present:
            err(f"hook {name!r} is tracked in {HOOK_DIR}/ but absent from the directory git "
                f"actually reads ({resolved}) — it will never run. Remedy: {REMEDY}")
        elif not ok_exec:
            err(f"hook {name!r} is present but NOT EXECUTABLE — git ignores it in silence. "
                f"Remedy: chmod +x {resolved / name}")

    # ── layer 2: the inner scripts every dispatcher guards with `[ -x ... ] || exit 0` ───────
    for rel in gate_scripts:
        disk = repo / rel
        name = Path(rel).name
        if not disk.is_file():
            err(f"{name} is TRACKED but missing from disk — its dispatcher guards the call with "
                f"`[ -x ... ] || exit 0`, so the hook exits 0 and allows the operation UNCHECKED.")
        elif not is_executable(disk):
            err(f"{name} is NOT EXECUTABLE — its dispatcher skips it and exits 0 SILENTLY, with "
                f"no warning at all. Remedy: chmod +x {disk}")

    # ── layer 3: the arm flags ───────────────────────────────────────────────────────────────
    script_names = {Path(p).name for p in gate_scripts}
    for flag, (script, hook) in ARM_FLAGS.items():
        if script not in script_names:
            continue  # this repo does not ship that gate; its flag is not owed
        present = flag in tracked_flags
        flags.append({"name": flag, "present": present, "arms": script, "via": hook})
        if not present:
            err(f"{flag} is not tracked — {script} still runs but only WARNS, and hook output is "
                f"rendered nowhere the operator looks. A warning nobody reads is not a gate. "
                f"Remedy: touch {SCRIPT_DIR}/{flag} && git add {SCRIPT_DIR}/{flag}")

    for extra in tracked_flags:
        if extra not in ARM_FLAGS:
            warn(f"{extra} is an arm flag this script's declared table does not know. The "
                 f"flag-to-script pairing cannot be derived from disk (see ARM_FLAGS) — add a "
                 f"row for it, or the gate it arms goes unchecked.")

    # An arm flag on disk but not in the index arms this machine and travels to no other. That
    # is the two-machine trap, and it is exactly what a bare `touch` remedy would produce.
    sdir = repo / SCRIPT_DIR
    if sdir.is_dir():
        for p in sorted(sdir.glob("*-ENFORCE")):
            if p.name not in tracked_flags:
                warn(f"{p.name} exists but is UNTRACKED — it arms this clone only and reaches no "
                     f"other machine. Remedy: git add {SCRIPT_DIR}/{p.name}")

    return {
        "repo": str(repo),
        "hooks_path": configured or None,
        "resolved": str(resolved) if resolved else None,
        "armed": not any(f["sev"] == "ERROR" for f in findings),
        "claims_gates": claims_gates,
        "hooks": hooks,
        "flags": flags,
        "findings": findings,
    }


def check(repo: Path, rep) -> dict:
    """Fold a scan into a `wf_common.Report`. Used by task_preflight.

    Findings land as ERRORs on purpose. A warn-only arm-check would be the very thing this
    script exists to catch: preflight's VERDICT reads "clear to close out and merge" whenever
    the error count is zero, so a warning would leave the clean line intact on a repo whose
    gates never ran.

    ⭐ ONE finding is conditionally downgraded: `no_hook_dir`, and ONLY for a repo that never
    claimed to have gates. Several `Projects/*` ship no `.githooks/` at all and never did;
    hard-blocking those would strand close-out in each of them forever. But a repo that DOES
    claim gates — it declares a Jira project, or ships the gate scripts — and yet tracks no
    hooks is drift, and drift blocks. A worktree cut before `.githooks/` existed is exactly
    that case, and it is completely ungated.
    """
    res = scan(repo)
    for f in res["findings"]:
        soft = f.get("code") == "no_hook_dir" and not res["claims_gates"]
        (rep.err if f["sev"] == "ERROR" and not soft else rep.warn)("hooks", f["msg"])
    if res["armed"]:
        rep.info("hooks", f"ARMED - {len(res['hooks'])} hook(s) via core.hooksPath="
                          f"{res['hooks_path']}, {len(res['flags'])} arm flag(s) tracked")
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Are this repo's git gates actually running? (SCC-110)")
    ap.add_argument("--repo", default=".", help="anywhere inside the repo; default: cwd")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    res = scan(git_root(args.repo))
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"== hooks arm-check - {res['repo']} ==")
        for f in res["findings"]:
            print(f"[{f['sev']:5}] {f['msg']}")
        print(f"\n{'ARMED' if res['armed'] else 'NOT ARMED'} - "
              f"core.hooksPath={res['hooks_path'] or '(unset)'}")
    errors = sum(1 for f in res["findings"] if f["sev"] == "ERROR")
    warns = sum(1 for f in res["findings"] if f["sev"] == "WARN")
    return 2 if errors else (1 if warns else 0)


if __name__ == "__main__":
    sys.exit(main())
