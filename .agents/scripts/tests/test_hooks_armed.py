"""test_hooks_armed.py — the arm-check reports every gate that is silently OFF (SCC-110).

Every gate this system owns is switched on by `core.hooksPath`, which git NEVER carries: it is
local config, per repo, per machine, and a fresh clone has it UNSET. Unset does not fail — git
reads `.git/hooks`, which is empty, and every flow runs green with every gate off.

SCC-77 built this check for ONE hook (`pre-push` + `MAIN-PUSH-ENFORCE`) inside
`test_main_push_gate.py`. This generalises it: 3 of the 4 tracked hooks and 2 of the 3 arm flags
had no assertion at all, and the check ran only in the test suite — never where the operator
reads the verdict.

Stdlib only, no pytest, matching every other script here: these must run on a fresh machine
before anything is installed, which is exactly when the arm state is wrong.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir, run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hooks_armed  # noqa: E402 — _harness puts .agents/scripts on sys.path
import wf_common as wf  # noqa: E402

REPO = Path(__file__).resolve().parents[3]


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, errors="replace").stdout.strip()


def seed(d: Path, *, hooks=("commit-msg", "pre-commit", "post-commit", "pre-push"),
         flags=("JIRA-ENFORCE", "SOP-ENFORCE", "MAIN-PUSH-ENFORCE"),
         scripts=("commit-msg-jira.sh", "sop-currency.sh", "pre-push-main-approval.sh"),
         arm=True) -> None:
    """A minimal repo shaped like this one: hook dispatchers, inner scripts, arm flags."""
    git("init", "-q", cwd=d)
    hd = d / ".githooks"
    hd.mkdir(parents=True, exist_ok=True)
    for h in hooks:
        p = hd / h
        p.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        p.chmod(0o755)
    gh = d / ".agents/scripts/git-hooks"
    gh.mkdir(parents=True, exist_ok=True)
    for s in scripts:
        p = gh / s
        p.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        p.chmod(0o755)
    for f in flags:
        (gh / f).write_text("armed\n", encoding="utf-8")
    if arm:
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=str(d),
                       capture_output=True)


def errs(res: dict) -> list[str]:
    return [f["msg"] for f in res["findings"] if f["sev"] == "ERROR"]


def main() -> int:
    c = Cases("hooks arm-check (SCC-110)")

    # ── A · the live repo, which IS armed, must read clean ────────────────────────────────
    # Negative control. A check that fires on a correctly-armed repo is noise, and noise gets
    # disabled — which is how the gates went off in the first place.
    live = hooks_armed.scan(REPO)
    c.check("A · live repo reports ARMED", live["armed"] is True,
            f"errors: {errs(live)}")
    c.check("A · live repo has no ERROR findings", not errs(live), str(errs(live)))

    # ── B · core.hooksPath unset — the fresh-clone case ───────────────────────────────────
    with TempDir() as d:
        seed(d, arm=False)
        r = hooks_armed.scan(d)
        c.check("B · unset hooksPath is NOT armed", r["armed"] is False)
        c.check("B · unset hooksPath is an ERROR", bool(errs(r)))
        c.check("B · the remedy command is printed",
                any("core.hooksPath" in m for m in errs(r)),
                "an operator who cannot see the fix will not apply it")

    # ── C · armed, but pointing somewhere that holds nothing ──────────────────────────────
    with TempDir() as d:
        seed(d)
        (d / "empty").mkdir()
        subprocess.run(["git", "config", "core.hooksPath", "empty"], cwd=str(d),
                       capture_output=True)
        r = hooks_armed.scan(d)
        c.check("C · hooksPath resolving to an empty dir is NOT armed", r["armed"] is False)

    # ── D · present but not executable — git ignores it, silently ─────────────────────────
    with TempDir() as d:
        seed(d)
        (d / ".githooks/commit-msg").chmod(0o644)
        r = hooks_armed.scan(d)
        c.check("D · a non-executable hook is an ERROR", bool(errs(r)))
        c.check("D · the message names chmod",
                any("chmod" in m for m in errs(r)), str(errs(r)))

    # ── E · the second arming layer: a tracked *-ENFORCE flag is gone ─────────────────────
    with TempDir() as d:
        seed(d, flags=("SOP-ENFORCE", "MAIN-PUSH-ENFORCE"))
        r = hooks_armed.scan(d)
        c.check("E · a missing arm flag is an ERROR", bool(errs(r)))
        c.check("E · the message names the flag",
                any("JIRA-ENFORCE" in m for m in errs(r)), str(errs(r)))

    # ── F · ⭐ audit #2 finding C — the inner script, and the SILENT exit 0 ────────────────
    # `.githooks/commit-msg` ends with `[ -x "$SOP" ] || exit 0`. Missing OR merely
    # non-executable and the hook exits 0 with NO output — while the JIRA branch directly
    # above it announces the same condition loudly. This is the ticket's own failure class
    # living inside the hook the ticket is about.
    with TempDir() as d:
        seed(d)
        (d / ".agents/scripts/git-hooks/sop-currency.sh").chmod(0o644)
        r = hooks_armed.scan(d)
        c.check("F · a non-executable INNER script is an ERROR", bool(errs(r)))
        c.check("F · the message names the script",
                any("sop-currency.sh" in m for m in errs(r)), str(errs(r)))

    # ── G · derivation — a 5th hook is reported with NO edit to hooks_armed.py ────────────
    with TempDir() as d:
        seed(d, hooks=("commit-msg", "pre-commit", "post-commit", "pre-push", "pre-rebase"))
        r = hooks_armed.scan(d)
        c.check("G · a hook nobody hardcoded is still reported",
                any(h["name"] == "pre-rebase" for h in r["hooks"]),
                "the expected set must come from disk, or it rots the day a 5th hook lands")

    # ── H · ⭐ audit #1 finding — the vacuous green ───────────────────────────────────────
    # Nothing to check must NEVER read as clean. That is this ticket's own failure class
    # re-introduced one level up, by the fix for it.
    with TempDir() as d:
        git("init", "-q", cwd=d)
        r = hooks_armed.scan(d)
        c.check("H · a repo with NO .githooks/ is NOT armed", r["armed"] is False)
        c.check("H · an empty derived set is an ERROR, not a pass", bool(errs(r)),
                "nothing-to-check reporting clean is the exact bug this ticket closes")

    # ── I · an arm flag the declared table does not know is surfaced, not swallowed ───────
    with TempDir() as d:
        seed(d)
        (d / ".agents/scripts/git-hooks/FUTURE-ENFORCE").write_text("armed\n", encoding="utf-8")
        r = hooks_armed.scan(d)
        c.check("I · an unknown *-ENFORCE flag is reported",
                any("FUTURE-ENFORCE" in f["msg"] for f in r["findings"]),
                "silently ignoring it is how the declared table goes stale")

    # ── J · it REPORTS. It never arms. ────────────────────────────────────────────────────
    with TempDir() as d:
        seed(d, arm=False)
        before = git("config", "--get", "core.hooksPath", cwd=d)
        hooks_armed.scan(d)
        run_script("hooks_armed.py", "--repo", str(d))
        after = git("config", "--get", "core.hooksPath", cwd=d)
        c.check("J · a scan does not change the repo's git config", before == after,
                "changing a machine's config out from under the operator is worse than telling them")

    # ── K · the seam into preflight ───────────────────────────────────────────────────────
    # task_preflight's VERDICT prints "clear to close out and merge" only when the error count
    # is zero, so an ERROR provably removes it. Assert the propagation here, and assert the
    # wiring by running preflight for real — a source grep would prove neither.
    with TempDir() as d:
        seed(d, arm=False)
        rep = wf.Report()
        hooks_armed.check(d, rep)
        c.check("K · check() pushes a blocking ERROR into a Report", rep.exit_code() == 2,
                f"exit_code={rep.exit_code()} - anything less and the VERDICT still reads clear")

    # ── L · the two OFF states are NOT the same, and preflight must weigh them apart ──────
    # Found by test_task_preflight regressing: its fixtures are throwaway repos with no gate
    # infrastructure at all, and hard-blocking those would mean a close-out could never
    # complete in such a repo. Gates present-but-switched-off (case K) is drift and blocks;
    # gates that never existed warns. Conflating them is what broke the sibling suite.
    with TempDir() as d:
        git("init", "-q", cwd=d)
        rep = wf.Report()
        hooks_armed.check(d, rep)
        c.check("L · a repo shipping NO gates warns, it does not block", rep.exit_code() == 1,
                f"exit_code={rep.exit_code()} - blocking strands close-out in such a repo")
        c.check("L · but 'nothing is checking this repo' is still said out loud",
                any("no commit gates" in i["msg"] for i in rep.items),
                "silence here would be the vacuous green this ticket exists to close")

    rc, out = run_script("task_preflight.py", "--expect-key", "SCC-110",
                         "--repo", str(REPO), "--branch", "chore/SCC-110-hooks-armed", "--json")
    c.check("K · preflight's JSON carries the arm state", '"hooks_armed"' in out,
            "the check must run where the operator reads the verdict, not only in the suite")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
