"""hooks_armed.py — are this repo's git gates actually RUNNING? (SCC-110)

git NEVER carries `core.hooksPath`. It is local config, per repo, per machine, and a fresh clone
has it UNSET. Unset does not fail: git reads `.git/hooks`, which is empty, so every gate this
system owns — the Jira key check, the encoding check, the SOP-currency check, the main-push
approval gate — is silently OFF, and every flow reports green.

SCC-77 proved the cost. Five Claude hooks were wired to `powershell` + `python`, neither of which
exists on the Mac, and all five exited 127 silently for weeks; six merges reached `main` on one
sign-off. It then built this check for exactly ONE gate, inside `test_main_push_gate.py`. This
generalises it and — more importantly — moves it to where the operator actually reads a verdict.

TWO LAYERS ARM A GATE, and either one can be off on its own:

    1. core.hooksPath   UNTRACKED, per machine. The master switch. Unset -> nothing runs.
    2. <NAME>-ENFORCE   TRACKED, per gate. Absent -> the gate WARNS instead of REJECTING, and
                        VS Code renders hook output nowhere the operator looks, so a warn-only
                        gate reads as clean success. See JIRA-ENFORCE's own header.

It REPORTS. It never arms. Silently rewriting a machine's git config out from under the operator
is worse than telling them; the remedy is one line and it is printed.

    hooks_armed.py [--repo PATH] [--json]

Exit: 0 clean · 1 warnings · 2 blocking.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HOOK_DIR = ".githooks"
SCRIPT_DIR = ".agents/scripts/git-hooks"
REMEDY = "git config --global core.hooksPath .githooks"

# ⛔ DECLARED, not derived — and that is deliberate. `core.hooksPath` tells you which hook FILES
# git runs. Nothing on disk tells you which inner script a `*-ENFORCE` flag arms, because the
# mapping is not one-to-one: `.githooks/commit-msg` dispatches BOTH `commit-msg-jira.sh`
# (JIRA-ENFORCE) and `sop-currency.sh` (SOP-ENFORCE) — two flags, two scripts, ONE hook file —
# and SOP-ENFORCE corresponds to no `.githooks/sop` at all. A filename-derivation cannot answer
# it. So the pairing is written down, and a flag that appears here without a row is REPORTED
# rather than swallowed, which is what keeps this table from going stale silently.
ARM_FLAGS = {
    "JIRA-ENFORCE":      ("commit-msg-jira.sh", "commit-msg"),
    "SOP-ENFORCE":       ("sop-currency.sh", "commit-msg"),
    "MAIN-PUSH-ENFORCE": ("pre-push-main-approval.sh", "pre-push"),
}


def _git_config(repo: Path, key: str) -> str:
    """`git config --get` exits 1 when the key is unset — that is data, not an error."""
    r = subprocess.run(["git", "-C", str(repo), "config", "--get", key],
                       capture_output=True, text=True, errors="replace")
    return r.stdout.strip() if r.returncode == 0 else ""


def _executable(p: Path) -> bool:
    return p.is_file() and p.stat().st_mode & 0o111 != 0


def scan(repo: Path) -> dict:
    """Read the arm state of every gate in `repo`. Pure inspection — writes nothing."""
    repo = Path(repo)
    findings: list[dict] = []
    hooks: list[dict] = []
    flags: list[dict] = []

    def err(msg: str, code: str = "unarmed") -> None:
        findings.append({"sev": "ERROR", "code": code, "msg": msg})

    def warn(msg: str, code: str = "unknown_flag") -> None:
        findings.append({"sev": "WARN", "code": code, "msg": msg})

    # ── the expected set comes from DISK, never from a literal ───────────────────────────
    # A hardcoded list rots the day a fifth hook lands — which is exactly how the three
    # unasserted hooks this script exists for came to be unasserted.
    tracked_dir = repo / HOOK_DIR
    expected = sorted(p.name for p in tracked_dir.iterdir() if p.is_file()) \
        if tracked_dir.is_dir() else []

    # ⭐ Nothing to check must NEVER read as clean. An empty derived set reporting "armed" is
    # this script's own failure class, one level up.
    #
    # But it is a DIFFERENT condition from a repo whose gates exist and are switched off, and
    # the two must not be conflated: a repo with no `.githooks/` never had gates, so there is
    # no `core.hooksPath` for it to be missing and nothing has drifted. It carries its own
    # `code` so `check()` can weigh it separately — see there for why that matters.
    if not expected:
        err(f"no hooks tracked in {HOOK_DIR}/ — this repo ships no commit gates, so nothing "
            f"mechanical is checking its commits. Never 'nothing to check, therefore fine'.",
            code="no_hook_dir")
        return {"repo": str(repo), "hooks_path": _git_config(repo, "core.hooksPath") or None,
                "resolved": None, "armed": False, "hooks": [], "flags": [],
                "findings": findings}

    configured = _git_config(repo, "core.hooksPath")
    if not configured:
        err(f"core.hooksPath is UNSET — git is reading .git/hooks, which is empty, so every "
            f"gate in this repo is OFF and says nothing. Remedy: {REMEDY}")
        resolved = None
    else:
        resolved = Path(configured) if Path(configured).is_absolute() else repo / configured
        if not resolved.is_dir():
            err(f"core.hooksPath = {configured!r} but that resolves to no directory "
                f"({resolved}) — every gate is OFF. Remedy: {REMEDY}")

    for name in expected:
        present = bool(resolved) and (resolved / name).is_file()
        ok_exec = bool(resolved) and _executable(resolved / name)
        hooks.append({"name": name, "present": present, "executable": ok_exec})
        if not present:
            err(f"hook {name!r} is tracked in {HOOK_DIR}/ but absent from the directory git "
                f"actually reads ({resolved}) — it will never run. Remedy: {REMEDY}")
        elif not ok_exec:
            err(f"hook {name!r} is present but NOT EXECUTABLE — git ignores it in silence. "
                f"Remedy: chmod +x {resolved / name}")

    # ── layer 2: the tracked arm flags, and the inner scripts they arm ───────────────────
    script_dir = repo / SCRIPT_DIR
    found = sorted(p.name for p in script_dir.glob("*-ENFORCE")) if script_dir.is_dir() else []

    for flag, (script, hook) in ARM_FLAGS.items():
        script_path = script_dir / script
        # Only judge a gate this repo actually ships. A repo without the script never had
        # the gate, and demanding its arm flag would be a finding about nothing.
        if not script_path.exists():
            continue
        present = flag in found
        ok_exec = _executable(script_path)
        flags.append({"name": flag, "present": present, "arms": script,
                      "via": hook, "script_executable": ok_exec})
        if not present:
            err(f"{flag} is missing — {script} still runs but only WARNS, and hook output is "
                f"rendered nowhere the operator looks. A warning nobody reads is not a gate. "
                f"Remedy: touch {script_path.parent / flag}")
        if not ok_exec:
            # ⭐ SCC-110 audit #2, finding C. `.githooks/commit-msg` ends with
            # `[ -x "$SOP" ] || exit 0` — non-executable and the hook exits 0 with NO OUTPUT,
            # while the JIRA branch directly above it announces the same condition loudly.
            err(f"{script} is NOT EXECUTABLE — {hook} skips it and exits 0 SILENTLY, with no "
                f"warning at all. Remedy: chmod +x {script_path}")

    for extra in found:
        if extra not in ARM_FLAGS:
            warn(f"{extra} is an arm flag this script's declared table does not know. The "
                 f"flag-to-script pairing cannot be derived from disk (see ARM_FLAGS) — add "
                 f"a row for it, or the gate it arms goes unchecked.")

    return {
        "repo": str(repo),
        "hooks_path": configured or None,
        "resolved": str(resolved) if resolved else None,
        "armed": not any(f["sev"] == "ERROR" for f in findings),
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

    ⭐ ONE finding is deliberately downgraded: `no_hook_dir`. A repo with gates that are
    switched off is drift and must block — that is the whole point. A repo that ships no
    `.githooks/` at all never had gates, and blocking it would mean a close-out could never
    complete there. Different condition, different weight. It still gets said out loud, so
    "this repo has nothing checking it" can never pass in silence.
    """
    res = scan(repo)
    for f in res["findings"]:
        blocking = f["sev"] == "ERROR" and f.get("code") != "no_hook_dir"
        (rep.err if blocking else rep.warn)("hooks", f["msg"])
    if res["armed"]:
        rep.info("hooks", f"ARMED - {len(res['hooks'])} hook(s) via core.hooksPath="
                          f"{res['hooks_path']}, {len(res['flags'])} arm flag(s) present")
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Are this repo's git gates actually running? (SCC-110)")
    ap.add_argument("--repo", default=".", help="repo root; default: cwd")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    res = scan(Path(args.repo).resolve())
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
