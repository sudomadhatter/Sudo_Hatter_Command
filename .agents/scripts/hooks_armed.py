"""hooks_armed.py — are this repo's git gates actually RUNNING? (SCC-110)

git NEVER carries `core.hooksPath`. It is local config, per repo, per machine, and a fresh clone
has it UNSET. Unset does not fail: git reads `.git/hooks`, which is empty, so every gate this
system owns — the Jira key check, the encoding check, the SOP-currency check, the main-push
approval gate — is silently OFF, and every flow reports green.

SCC-77 proved the cost. Five Claude hooks were wired to `powershell` + `python`, neither of which
exists on the Mac, and all five exited 127 silently for weeks; six merges reached `main` on one
sign-off. It then built this check for exactly ONE gate, inside `test_main_push_gate.py`. This
generalises it and — more importantly — moves it to where the operator actually reads a verdict.

FIVE WAYS A GATE IS OFF, and each is silent on its own. This said THREE until SCC-140, which
found the tool reporting ARMED with ZERO findings in every one of cases 3b, 4 and 5:

    1. core.hooksPath   UNTRACKED, per machine. The master switch. Unset -> nothing runs.
    2. the inner script  Every dispatcher in `.githooks/` ends with the same two-liner —
                         `[ -x "$SCRIPT" ] || exit 0`. Delete the script, or merely drop its
                         executable bit, and the hook exits 0 with NO OUTPUT AT ALL.
    3. <NAME>-ENFORCE    Absent -> the gate WARNS instead of REJECTING, and hook output is
                         rendered nowhere the operator looks. Checked (a) in the INDEX and
                         (b) ON DISK, because every consumer reads the flag from the
                         filesystem — `commit-msg-jira.sh`, `pre-push-main-approval.sh`, and
                         `sop_currency.py` via `.exists()` — while `sop-currency.sh` documents
                         "delete the flag" as the disarm. An index-only check therefore said
                         ARMED to an operator following this system's own instructions.
    4. an ORPHANED flag  A tracked flag whose gate script is NOT tracked: the marker claims the
                         gate is armed and the gate does not exist, so its dispatcher exits 0.
                         Includes the whole-repo case — claims gates, tracks zero gate scripts.
    5. the DISPATCHER    A flag arming a script reached through a hook that is not tracked in
                         `.githooks/`. Nothing dispatches it, so it never runs.

⚠ KNOWN GAP, stated rather than papered over (SCC-140 review). Cases 4 and 5 are FLAG-KEYED:
they walk `ARM_FLAGS`, so a gate with NO flag is invisible to them. Drop `.githooks/pre-commit`
from the index while `pre-commit-encoding.sh` stays tracked and executable and this reports
ARMED with zero findings — and the encoding gate is precisely the flagless one. It is not
derivable either: `mint-push-token.sh` is a tracked `git-hooks/*.sh` that NO dispatcher
references, so "every gate script needs a referencing dispatcher" would fire on a correct repo.
That is the same wall `ARM_FLAGS` documents — the flag-to-script mapping is declared because it
cannot be derived. Closing this needs a declared dispatcher table for flagless gates; until
then, layer 2's executability check is the only thing standing behind them.

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


def _run(args: list[str]):
    """Run git. `None` means the BINARY is not there at all.

    Every call in this file used to let `FileNotFoundError` escape, so on a machine without
    git — or with a PATH the agent shell does not share — the arm-check ended in a raw
    traceback. A traceback is not a verdict: it tells the operator nothing about whether
    their gates run, and it takes the close-out down with it.
    """
    try:
        return subprocess.run(args, capture_output=True, text=True, errors="replace")
    except OSError:
        return None


def git_root(start: str | Path) -> Path:
    """Walk up for the repo root. Running from a subdirectory must not read as 'no hooks'."""
    r = _run(["git", "-C", str(start), "rev-parse", "--show-toplevel"])
    return Path(r.stdout.strip()) if r and r.returncode == 0 and r.stdout.strip() else Path(start)


def _git_config(repo: Path, key: str) -> str:
    """`git config --get` exits 1 when the key is unset — that is data, not an error."""
    r = _run(["git", "-C", str(repo), "config", "--get", key])
    return r.stdout.strip() if r and r.returncode == 0 else ""


def _tracked(repo: Path, pathspec: str) -> list[str] | None:
    """Repo-relative paths git actually tracks. The index, not the filesystem — see module doc.

    `None` is NOT `[]`. Empty means "git answered: nothing matches"; None means "git could not
    be asked at all", and collapsing the two would turn a missing binary into the confident
    claim that this repo tracks no hooks — the exact vacuous answer this file exists to refuse.
    """
    r = _run(["git", "-C", str(repo), "ls-files", "-z", "--", pathspec])
    if r is None:
        return None
    return sorted(p for p in r.stdout.split("\0") if p) if r.returncode == 0 else []


def resolve_hooks_dir(repo: Path, configured: str) -> Path:
    """Where git will ACTUALLY look for hooks, given `core.hooksPath = configured`.

    ⚠ `~` is the whole reason this is a function. GIT expands it; `pathlib` does not, and
    `Path("~/hooks").is_absolute()` is False — so a tilde path was joined onto the repo root,
    resolved to nothing, and a correctly armed machine read NOT ARMED and was falsely blocked
    from closing out. A gate you cannot satisfy is one you learn to route around.
    """
    p = Path(configured).expanduser()
    return p if p.is_absolute() else repo / p


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

    # ⚠ A git pathspec `*` CROSSES SLASHES — `.githooks/*` returns `.githooks/README.md` AND
    # `.githooks/lib/helper.sh`, and taking `.name` of those made a README a "required
    # executable hook". Close-out then hard-blocked with `hook 'README.md' is present but NOT
    # EXECUTABLE` — a false red produced by documenting your own hooks directory.
    #
    # TWO filters, because both failure shapes are real: direct children only (no nested
    # helpers), and no suffix. A git hook is named exactly after the git event — `commit-msg`,
    # `pre-push` — and never carries an extension, so `.md` is documentation and `.sh` is a
    # library. Neither is a dispatcher git will ever run.
    hook_files = _tracked(repo, f"{HOOK_DIR}/")
    if hook_files is None:
        err("git is not runnable from here, so NOTHING about this repo's gates could be "
            "checked. This is not a clean result - it is the absence of one. Put git on "
            "PATH and re-run.", code="no_git")
        return {"repo": str(repo), "hooks_path": None, "resolved": None, "armed": False,
                "claims_gates": True, "hooks": [], "flags": [], "findings": findings}

    # ⛔ THE DOTFILE FILTER IS NOT REDUNDANT WITH THE SUFFIX ONE. `Path(".gitignore").suffix`
    # is `''` — pathlib reads a leading dot as the start of a NAME, not a suffix — so a
    # `.gitignore`, `.gitattributes` or `.keep` tracked in `.githooks/` sailed straight through
    # the suffix test, entered `expected` as a required hook, and hard-blocked close-out with
    # `chmod +x .githooks/.gitignore`. Found by the SCC-140 review: the same false-red this
    # filter exists to close, left half-closed by checking only one of the two shapes.
    expected = [Path(p).name for p in hook_files
                if Path(p).parent.as_posix() == HOOK_DIR
                and not Path(p).suffix
                and not Path(p).name.startswith(".")]
    gate_scripts = _tracked(repo, f"{SCRIPT_DIR}/*.sh") or []
    tracked_flags = [Path(p).name for p in (_tracked(repo, f"{SCRIPT_DIR}/*-ENFORCE") or [])]

    # Does this repo CLAIM to have gates? Used only to weigh the "no hooks at all" finding —
    # see `check()`. A repo declaring a Jira project, or shipping gate scripts, is asserting
    # that its commits are checked; a repo doing neither never made that claim.
    # ⓘ `jira.conf` is read from DISK, not the index, and that is DELIBERATE (SCC-140,
    # decision A). It looks inconsistent beside this file's ask-the-index doctrine, so it
    # gets a line rather than being re-found by every review: this is not the deleted-vs-
    # never-had question the doctrine exists for. It asks only "is this repo asserting that
    # its commits are checked", and a declaration present in the working tree is that
    # assertion whether or not it has been committed yet. Over-claiming is also the SAFE
    # direction here - it makes drift BLOCK rather than warn.
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
        resolved = resolve_hooks_dir(repo, configured)
        if not resolved.is_dir():
            err(f"core.hooksPath = {configured!r} resolves to no directory ({resolved}) — "
                f"every gate is OFF. Remedy: {REMEDY}")

    # ⛔ ONE CAUSE, ONE ERROR. When hooksPath is unset or points nowhere, `resolved` is None
    # and this loop used to add a finding PER TRACKED HOOK — five errors on a fresh clone,
    # four of them printing "absent from the directory git actually reads (None)". A fresh
    # clone is the first time anyone reads this output, and it opened with four lines of
    # noise wrapped around the one line that mattered. The cause is already reported above;
    # the hooks are still listed so the --json shape does not change.
    gates_off = resolved is None or not resolved.is_dir()
    for name in expected:
        present = (not gates_off) and (resolved / name).is_file()
        ok_exec = (not gates_off) and is_executable(resolved / name)
        hooks.append({"name": name, "present": present, "executable": ok_exec})
        if gates_off:
            continue
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

    # ⭐ A repo that CLAIMS gates and tracks not one gate script is the vacuous green in its
    # purest form: `jira.conf` + the four dispatchers + zero scripts reported ARMED with no
    # findings at all, while every dispatcher's `[ -x ... ] || exit 0` allowed the operation.
    # That is the state a project scaffolded from the skeleton sits in before its gate scripts
    # land, and the shipped `make_repo` test fixture was in it too.
    if claims_gates and not gate_scripts:
        err(f"this repo CLAIMS gates (it declares a Jira project or ships hook dispatchers) but "
            f"tracks NO gate scripts in {SCRIPT_DIR}/ — every dispatcher ends `[ -x ... ] || "
            f"exit 0`, so all of them exit 0 and allow the operation UNCHECKED.")

    # ── layer 3: the arm flags ───────────────────────────────────────────────────────────────
    script_names = {Path(p).name for p in gate_scripts}
    hook_names = set(expected)
    for flag, (script, hook) in ARM_FLAGS.items():
        tracked = flag in tracked_flags
        # ⛔ NOT `if script not in script_names: continue`. That single line was FOUR defects.
        # It read as "this repo does not ship that gate, so its flag is not owed" — true only
        # when the flag is absent too. A TRACKED flag whose script is gone is the loudest case
        # there is: the gate was deleted (or dropped from the index with `git rm --cached`,
        # which leaves the file on disk so nothing looks wrong) while the marker that claims it
        # is armed stayed behind. Skipping it is how a deleted gate certified ARMED.
        shipped = script in script_names
        if not shipped and not tracked:
            continue  # genuinely never had this gate — nothing is owed and nothing is claimed
        flags.append({"name": flag, "present": tracked, "arms": script, "via": hook})

        if not shipped:
            err(f"{flag} is tracked but {script} is NOT — the flag says this gate is armed and "
                f"the gate it names does not exist in the index. Its dispatcher exits 0 and "
                f"allows the operation UNCHECKED. Remedy: restore {SCRIPT_DIR}/{script}, or "
                f"git rm {SCRIPT_DIR}/{flag} if the gate was retired on purpose.")
        elif not tracked:
            err(f"{flag} is not tracked — {script} still runs but only WARNS, and hook output is "
                f"rendered nowhere the operator looks. A warning nobody reads is not a gate. "
                f"Remedy: touch {SCRIPT_DIR}/{flag} && git add {SCRIPT_DIR}/{flag}")
        elif not (repo / SCRIPT_DIR / flag).is_file():
            # ⛔ THE INDEX/DISK SPLIT. Everything else here asks the index on purpose — it is
            # the only thing that can tell "deleted" from "never had". The flags are the ONE
            # exception, because every consumer reads them from DISK at runtime:
            # commit-msg-jira.sh:85 and pre-push-main-approval.sh:38 both `[ -f ... ]`, and
            # SOP-ENFORCE is read by sop_currency.py:165 as `(repo / ENFORCE_MARKER).exists()`.
            # sop-currency.sh:12 documents "disarm to warn-only: delete SOP-ENFORCE" — so
            # following this repo's OWN written instruction left the tool reporting ARMED.
            err(f"{flag} is tracked but MISSING FROM DISK — the hooks read this file from the "
                f"filesystem, not the index, so {script} has been silently downgraded to "
                f"warn-only on this machine. Remedy: git checkout {SCRIPT_DIR}/{flag}")
        elif hook not in hook_names:
            # ARM_FLAGS declares which dispatcher carries each gate and nothing ever checked
            # that dispatcher was tracked. A flag arming a script reached through a hook that
            # does not exist is armed in name only.
            err(f"{flag} arms {script} via the {hook!r} hook, which is NOT tracked in "
                f"{HOOK_DIR}/ — nothing dispatches this gate, so it never runs.")

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


def is_soft(finding: dict, res: dict) -> bool:
    """Is this finding downgraded to a warning?

    ONE definition, called by BOTH `check()` (preflight's path) and `main()` (the CLI), because
    a repo that never claimed gates must get the same answer whichever door you came through.
    It lived in two places for exactly one review cycle — SCC-140 aligned the CLI's exit code
    to `check()` and left the predicate written out twice, under a comment claiming it was not.
    """
    return finding.get("code") == "no_hook_dir" and not res["claims_gates"]


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
        soft = is_soft(f, res)
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
    # ⭐ ONE STATE, ONE VERDICT. `check()` downgrades `no_hook_dir` for a repo that never
    # claimed gates; this exit code did not, so the same repo was a warning through preflight
    # and a hard 2 from the CLI. Nothing in the system gates on this CLI — `task_preflight`
    # via `check()` is the only programmatic caller and the SOP documents this as something a
    # human types — so the CLI was the half that was wrong. Both now call `is_soft()`; the
    # predicate is defined once, beside `check()`.
    errors = sum(1 for f in res["findings"] if f["sev"] == "ERROR" and not is_soft(f, res))
    warns = sum(1 for f in res["findings"] if f["sev"] == "WARN" or is_soft(f, res))
    return 2 if errors else (1 if warns else 0)


if __name__ == "__main__":
    sys.exit(main())
