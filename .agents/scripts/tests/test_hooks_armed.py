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

import json
import os
import stat
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
         scripts=("commit-msg-jira.sh", "sop-currency.sh", "pre-push-main-approval.sh",
                  "pre-commit-encoding.sh"),
         arm=True) -> None:
    """A minimal repo shaped like this one: hook dispatchers, inner scripts, arm flags.

    Everything is `git add`ed, because the checker reads the INDEX, not the filesystem — see
    the module docstring in hooks_armed.py for why that distinction is the whole correctness
    of it. `pre-commit-encoding.sh` is included deliberately: it is armed unconditionally and
    has NO flag, so it is the case that falls out of any flag-keyed executable check.
    """
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
    git("add", "-A", cwd=d)          # fixture only; the real lane is explicit-paths
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

    # ── M · ⛔ THE REVIEW'S H2 — a DELETED gate script must not read as ARMED ─────────────
    # The first cut used iterdir()/glob and skipped any script absent from disk, reasoning "a
    # repo without the script never had the gate". Applied unconditionally, that meant: delete
    # all three gate scripts and this tool reported ARMED with ZERO findings, while every
    # dispatcher's `[ -x ... ] || exit 0` silently allowed the operation. The index tells
    # deleted from never-had; the filesystem cannot.
    with TempDir() as d:
        seed(d)
        for s in ("commit-msg-jira.sh", "sop-currency.sh", "pre-push-main-approval.sh"):
            (d / ".agents/scripts/git-hooks" / s).unlink()
        r = hooks_armed.scan(d)
        c.check("M · deleting the gate scripts is NOT armed", r["armed"] is False,
                "iterdir() reported ARMED with 0 findings here - the tool's own failure class")
        c.check("M · each deleted script is named", len(errs(r)) >= 3, str(errs(r)))
        c.check("M · the message says the hook allows the operation unchecked",
                any("UNCHECKED" in m for m in errs(r)), str(errs(r)))

    # ── N · ⛔ THE REVIEW'S M5 — a gate with NO arm flag is still executable-checked ───────
    # `.githooks/pre-commit` is literally `[ -x "$HOOK" ] || exit 0`. The encoding gate is armed
    # unconditionally and has no *-ENFORCE flag, so a flag-keyed check exempts the one hook the
    # silent-exit-0 finding applies to most.
    with TempDir() as d:
        seed(d)
        (d / ".agents/scripts/git-hooks/pre-commit-encoding.sh").chmod(0o644)
        r = hooks_armed.scan(d)
        c.check("N · a flagless gate script is executable-checked too", bool(errs(r)),
                "ARM_FLAGS governs the FLAG question only, never executability")
        c.check("N · it names the encoding gate",
                any("pre-commit-encoding.sh" in m for m in errs(r)), str(errs(r)))

    # ── O · ⛔ THE REVIEW'S M6 — an UNTRACKED arm flag arms one clone and travels nowhere ──
    # The old remedy was a bare `touch`, which produces exactly this: green here, off on the
    # other machine. In a documented two-machine system that is the tool printing its own bypass.
    with TempDir() as d:
        seed(d)
        (d / ".agents/scripts/git-hooks/LOCAL-ENFORCE").write_text("armed\n", encoding="utf-8")
        r = hooks_armed.scan(d)
        c.check("O · an untracked arm flag is reported",
                any("UNTRACKED" in f["msg"] for f in r["findings"]), str(r["findings"]))
        c.check("O · the remedy says git add, not just touch",
                any("git add" in f["msg"] for f in r["findings"]), "a bare touch does not travel")

    # ── P · ⛔ THE REVIEW'S M4 — the downgrade is gated on whether the repo CLAIMS gates ───
    # A repo that never had gates warns (blocking would strand close-out in several Projects/*).
    # A repo that DECLARES a Jira project and yet tracks no hooks is drift, and drift blocks.
    # A worktree cut before .githooks/ existed is exactly that case, and it is fully ungated.
    with TempDir() as d:
        git("init", "-q", cwd=d)
        rep = wf.Report()
        hooks_armed.check(d, rep)
        c.check("P · a repo that never claimed gates warns", rep.exit_code() == 1,
                f"exit_code={rep.exit_code()}")
    with TempDir() as d:
        git("init", "-q", cwd=d)
        (d / ".agents").mkdir(parents=True)
        (d / ".agents/jira.conf").write_text('JIRA_KEYS="SCC"\n', encoding="utf-8")
        rep = wf.Report()
        res = hooks_armed.check(d, rep)
        c.check("P · a repo that CLAIMS gates but tracks none BLOCKS",
                res["claims_gates"] and rep.exit_code() == 2,
                f"claims={res['claims_gates']} exit_code={rep.exit_code()} - this is the "
                f"ungated-worktree case the review found printing 'clear to close out'")

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
                any("nothing mechanical is checking" in i["msg"] for i in rep.items),
                "silence here would be the vacuous green this ticket exists to close")

    # ── Q · the seam is really wired, and carries the REAL answer ─────────────────────────
    # The branch is read from git, never hardcoded — a literal lane name evaporates at prune and
    # takes this assertion with it. And the value is compared against a live scan, so a stub
    # that always answered `true` would fail here.
    branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=REPO)
    # ⛔ Pin acli to a childless stub before invoking the preflight (SCC-119). This test is
    # about the ARM STATE, not the board - but `task_preflight.check_children()` is the first
    # network call that script has ever made, and it resolves `acli` off PATH. Without this,
    # the suite quietly queried the LIVE Jira board on every run: ~2s, dependent on
    # credentials, and different on a machine where acli is absent or sandboxed (an agent
    # shell cannot reach the OS credential store at all). Measured before the pin: the run
    # printed "SCC-119: no subtasks", a fact it could only have learned from the real board.
    with TempDir() as board:
        stub = board / "acli_stub.py"
        stub.write_text("import sys\nprint('[]')\n", encoding="utf-8")
        launcher = board / ("acli.bat" if os.name == "nt" else "acli")
        if os.name == "nt":
            launcher.write_text(f'@echo off\r\n"{sys.executable}" "{stub}" %*\r\n',
                                encoding="utf-8")
        else:
            launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{stub}" "$@"\n',
                                encoding="utf-8")
            launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)
        os.environ["ACLI_BIN"] = str(launcher)
        rc, out = run_script("task_preflight.py", "--expect-key", "SCC-110",
                             "--repo", str(REPO), "--branch", branch, "--json")
        os.environ.pop("ACLI_BIN", None)
    c.check("Q · preflight's JSON carries the arm state", '"hooks_armed"' in out,
            "the check must run where the operator reads the verdict, not only in the suite")
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        payload = {}
    c.check("Q · and it carries the REAL answer, not a constant",
            payload.get("hooks_armed") == hooks_armed.scan(REPO)["armed"],
            f"preflight said {payload.get('hooks_armed')!r}; a live scan disagrees")

    # ═══ SCC-140 · the vacuous-ARMED family ═══════════════════════════════════════════════
    # Five ways this tool reported ARMED while gates were off. Its ONE job is not to do that,
    # so each is a fixture here and each must read NOT ARMED with a named finding.

    # ── R · ⛔ the INDEX/DISK split — the disarm procedure this repo DOCUMENTS ─────────────
    # scan() reads the arm flags from the git INDEX. Every consumer reads them from DISK:
    # commit-msg-jira.sh:85 `[ -f ... ]`, pre-push-main-approval.sh:38 `[ -f ... ] || exit 0`,
    # and SOP-ENFORCE at sop_currency.py:165 `(repo / ENFORCE_MARKER).exists()` — one layer
    # deeper than the shell, which is why grepping the hook scripts alone makes it look unread.
    # sop-currency.sh:12 tells you to disarm by DELETING the flag. Follow your own documented
    # instruction and the index still has it, so the tool says ARMED while the gate only warns.
    for flag in ("JIRA-ENFORCE", "SOP-ENFORCE", "MAIN-PUSH-ENFORCE"):
        with TempDir() as d:
            seed(d)
            (d / ".agents/scripts/git-hooks" / flag).unlink()   # tracked, gone from disk
            r = hooks_armed.scan(d)
            c.check(f"R · {flag} deleted from DISK is NOT armed", r["armed"] is False,
                    f"the hooks read this file from disk; errors={errs(r)}")
            c.check(f"R · ...and the finding names {flag}",
                    any(flag in m for m in errs(r)), str(errs(r)))

    # ── S · a gate script dropped from the INDEX while its flag stays tracked ─────────────
    # `git rm --cached` leaves the file on disk, so nothing looks wrong; the script vanishes
    # from `_tracked`, layer 2 never sees it, and layer 3's `continue` skipped its flag.
    with TempDir() as d:
        seed(d)
        git("rm", "--cached", "-q", ".agents/scripts/git-hooks/commit-msg-jira.sh", cwd=d)
        r = hooks_armed.scan(d)
        c.check("S · a gate script removed from the INDEX is NOT armed", r["armed"] is False,
                f"errors={errs(r)} - the dispatcher's `[ -x ] || exit 0` allows it unchecked")
        c.check("S · ...and the finding names the orphaned flag",
                any("JIRA-ENFORCE" in m for m in errs(r)), str(errs(r)))

    # ── T · a TRACKED flag whose paired script was never tracked ─────────────────────────
    # Acceptance item 2 of the original ticket is "reports every flag". The `continue`
    # silently skipped exactly the flags whose gate is missing — the ones worth reporting.
    with TempDir() as d:
        seed(d, scripts=("sop-currency.sh", "pre-push-main-approval.sh", "pre-commit-encoding.sh"))
        r = hooks_armed.scan(d)
        c.check("T · a tracked flag with no tracked script is REPORTED, not skipped",
                any("JIRA-ENFORCE" in m for m in errs(r)),
                f"errors={errs(r)} - a flag arming nothing is the loudest case, not the quietest")

    # ── U · ⭐ jira.conf + dispatchers + ZERO gate scripts certified ARMED ────────────────
    # The repo CLAIMS gates (it declares a Jira project) and ships hooks that dispatch to
    # scripts that do not exist. Every dispatcher exits 0. This is the shape a project
    # scaffolded by /smh-new-project is in before its gate scripts land.
    with TempDir() as d:
        seed(d, scripts=(), flags=())
        (d / ".agents").mkdir(parents=True, exist_ok=True)
        (d / ".agents/jira.conf").write_text('JIRA_KEYS="SCC"\n', encoding="utf-8")
        git("add", "-A", cwd=d)
        r = hooks_armed.scan(d)
        c.check("U · claiming gates while tracking ZERO gate scripts is NOT armed",
                r["armed"] is False,
                f"claims={r['claims_gates']} errors={errs(r)} - it reported ARMED with no findings")

    # ── V · ARM_FLAGS declares a `via` hook per flag and never checked it was tracked ─────
    with TempDir() as d:
        seed(d, hooks=("pre-commit", "post-commit", "pre-push"))   # no commit-msg dispatcher
        r = hooks_armed.scan(d)
        c.check("V · a flag whose declared `via` hook is untracked is NOT armed",
                r["armed"] is False, f"errors={errs(r)}")
        c.check("V · ...and the finding names the missing dispatcher",
                any("commit-msg" in m for m in errs(r)), str(errs(r)))

    # ── W · ⛔ the pathspec crosses slashes — a FALSE RED that hard-blocks close-out ──────
    # `git ls-files -- '.githooks/*'` matches across `/`, and `Path(p).name` then turns a
    # README and any nested file into "required executable hooks". Adding a README to that
    # directory blocked the close-out with "hook 'README.md' is present but NOT EXECUTABLE".
    with TempDir() as d:
        seed(d)
        (d / ".githooks/README.md").write_text("# what these are\n", encoding="utf-8")
        (d / ".githooks/lib").mkdir(parents=True, exist_ok=True)
        (d / ".githooks/lib/helper.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        git("add", "-A", cwd=d)
        r = hooks_armed.scan(d)
        names = {h["name"] for h in r["hooks"]}
        c.check("W · a tracked non-hook in .githooks/ is not a required hook",
                "README.md" not in names, f"hooks={sorted(names)}")
        c.check("W · a NESTED tracked file is not a required hook either",
                "helper.sh" not in names, f"hooks={sorted(names)}")
        c.check("W · ...and the four real dispatchers are still required",
                {"commit-msg", "pre-commit", "post-commit", "pre-push"} <= names,
                f"hooks={sorted(names)}")
        c.check("W · so a repo with a README in .githooks/ still reads ARMED",
                r["armed"] is True, f"errors={errs(r)}")

    # ── X · a tilde in core.hooksPath — git expands it, pathlib does not ─────────────────
    # A correctly armed machine reads NOT ARMED and is falsely blocked.
    c.check("X · `~` in core.hooksPath is expanded, not treated as a relative dir",
            hooks_armed.resolve_hooks_dir(Path("/repo"), "~/hooks")
            == Path("~/hooks").expanduser(),
            f"got {hooks_armed.resolve_hooks_dir(Path('/repo'), '~/hooks')}")
    c.check("X · ...while a genuinely relative path still resolves inside the repo",
            hooks_armed.resolve_hooks_dir(Path("/repo"), ".githooks") == Path("/repo/.githooks"))
    c.check("X · ...and an absolute path is left alone",
            hooks_armed.resolve_hooks_dir(Path("/repo"), "/etc/hooks") == Path("/etc/hooks"))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
