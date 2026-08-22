"""The post-commit recorder that moves a keyed branch's ticket to `In Progress` (SCC-113).

Four seams wrote `Done`; exactly one wrote `In Progress`, and it was the BMAD story lane. On
a board where every non-epic ticket is a Task, that meant nothing was ever visible as in
flight - work sat in `To Do` while it was built and teleported to `Done` at merge.

The trigger deliberately does NOT hang on a command. `/smh-quick-dev` is not always run, and a
fix that depends on remembering to run it re-creates the defect it closes. Work provably starts
when the first commit lands on a keyed branch - whatever path got there, including a bare
`git commit` with no workflow at all.

Why `post-commit` and not the armed `commit-msg` gate: that hook's own header forbids growing
it - "a live 'does AVCH-57 exist?' call would put a network round-trip on every commit and
would fail closed on a plane." `post-commit` carries the opposite contract, equally explicit:
it fires after the commit is sealed, so it can never block one, and every error is swallowed.

This runs the REAL hook against a REAL git repo with a stubbed `acli`. The things that can
only be proved by executing it, and that prose could not hold:

  * it costs exactly ONE TRANSITION per branch - a marker short-circuits every later commit,
    or a round-trip rides every commit forever. (One transition, not one CALL: the exchange is
    view -> transition -> read-back. Round-trip cost is the whole argument for post-commit over
    commit-msg, so the number is stated precisely rather than flatteringly.)
  * a FAILED call writes no marker, so an offline commit retries on the next one;
  * it can never block or fail a commit, whatever the hook does;
  * `main` and unkeyed branches are silent.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir
from test_jira_feed import STUB          # ONE acli stub in the suite, not a second copy

LOBBY = SCRIPTS.parent.parent


def git(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    e = {**os.environ, **(env or {})}
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=e)


def build(root: Path) -> tuple[Path, Path, Path]:
    """A real repo carrying the real hooks. Returns (repo, acli-launcher, state-file)."""
    repo = root / "repo"
    (repo / ".agents/scripts/git-hooks").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)

    # The production files, copied - not re-implemented. A fixture that re-states the hook
    # proves the fixture works.
    for rel in (".agents/scripts/jira_feed.py", ".agents/scripts/wf_common.py",
                ".agents/scripts/git-hooks/post-commit-jira-start.sh",
                ".githooks/post-commit"):
        src = LOBBY / rel
        if src.exists():
            shutil.copy2(src, repo / rel)
            if src.suffix == ".sh" or "hooks" in rel:
                (repo / rel).chmod((repo / rel).stat().st_mode | stat.S_IXUSR)

    (repo / ".agents/jira.conf").write_text('JIRA_KEYS="TEST"\n', encoding="utf-8")

    stub_py = root / "acli_stub.py"
    stub_py.write_text(STUB, encoding="utf-8")
    if os.name == "nt":
        launcher = root / "acli.bat"
        launcher.write_text(f'@echo off\r\n"{sys.executable}" "{stub_py}" %*\r\n',
                            encoding="utf-8")
    else:
        launcher = root / "acli"
        launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{stub_py}" "$@"\n',
                            encoding="utf-8")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)

    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "core.hooksPath", ".githooks")

    # COMMIT the toolkit, don't just drop it in the working tree. `git worktree add` checks
    # out a commit, so an uncommitted .agents/ leaves the worktree case with no jira_feed.py
    # to call and no jira.conf to read - which reads exactly like the hook failing, and cost
    # a wrong diagnosis once already.
    git(repo, "add", ".agents", ".githooks")
    git(repo, "commit", "-q", "-m", "TEST-0 chore: the toolkit under test")
    return repo, launcher, root / "state.json"


def set_state(path: Path, **kw) -> None:
    state = {"description": "", "comments": [], "search": []}
    state.update(kw)
    path.write_text(json.dumps(state), encoding="utf-8")


def get_state(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def commit(repo: Path, acli: Path, state: Path, name: str, body: str = "x"):
    """A real commit, with the hook armed. --no-verify would defeat the whole fixture."""
    (repo / name).write_text(body, encoding="utf-8")
    git(repo, "add", name)
    return git(repo, "commit", "-q", "-m", "TEST-1 chore: a keyed commit",
               env={"ACLI_BIN": str(acli), "STUB_STATE": str(state)})


def marker_dir(repo: Path) -> Path:
    r = git(repo, "rev-parse", "--absolute-git-dir")
    return Path(r.stdout.strip())


def main() -> int:
    c = Cases("jira_start_hook")

    hook = LOBBY / ".agents/scripts/git-hooks/post-commit-jira-start.sh"
    c.check("hook: the recorder script exists", hook.exists(),
            "post-commit delegates to it, as commit-msg already delegates to two scripts")
    if not hook.exists():
        return c.finish()

    text = hook.read_text(encoding="utf-8")
    stripped = "\n".join(ln for ln in text.splitlines()
                         if not ln.lstrip().startswith("#"))
    c.check("hook: probes python3, python AND py",
            "for c in python3 python py" in stripped,
            "the Mac has no bare `python`; the PC has no `python3`")
    c.check("hook: covers chore/, claude/ AND epic/",
            all(p in stripped for p in ("chore", "claude", "epic")))
    # Value-aware, not presence-aware: `"--timeout" in text` passes for `--timeout 900`,
    # which is the whole defect it would be guarding against. The runtime half of this
    # (silence on a failure path) is the TEST-9 case below - a presence check for
    # `>/dev/null 2>&1` was VACUOUS here, satisfied by the interpreter probe's own
    # `command -v "$c" >/dev/null 2>&1` line, and passed against the unfixed hook.
    c.check("hook: passes a SHORT --timeout, not the 90s default",
            re.search(r"--timeout\s+(\d+)", stripped)
            and int(re.search(r"--timeout\s+(\d+)", stripped).group(1)) <= 15,
            "it runs inline on every commit until it succeeds; 90s stalls each commit "
            "for a minute and a half on a dead uplink")

    with TempDir() as tmp:
        repo, acli, state = build(tmp)

        # ── a keyed branch fires, exactly once ─────────────────────────────────
        set_state(state, types={"TEST-1": "Task"}, statuses={"TEST-1": "To Do"})
        git(repo, "checkout", "-q", "-b", "chore/TEST-1-a-task")
        r = commit(repo, acli, state, "one.txt")
        c.check("hook: the commit itself always succeeds", r.returncode == 0,
                (r.stderr or r.stdout).strip()[:200])
        c.check("hook: first commit on chore/TEST-1-* moves it to In Progress",
                get_state(state)["statuses"]["TEST-1"] == "In Progress",
                "this is the whole point of the lane")
        c.check("hook: it wrote the marker",
                (marker_dir(repo) / "jira-started-chore-TEST-1-a-task").exists())
        # Exactly one TRANSITION - which is not the same as one acli call, and the first
        # cut's assertion name claimed the latter while measuring the former. The exchange
        # is three round-trips (view -> transition -> read-back). Round-trip cost is the
        # whole argument for post-commit over commit-msg, so the number has to be honest.
        after_first = len(get_state(state).get("transitions", []))
        c.check("hook: exactly ONE transition per branch", after_first == 1,
                f"made {after_first}")

        # ── every later commit is free ─────────────────────────────────────────
        commit(repo, acli, state, "two.txt")
        commit(repo, acli, state, "three.txt")
        c.check("hook: later commits cost NO further transition",
                len(get_state(state).get("transitions", [])) == after_first,
                "without the marker this is a network round-trip on every commit forever")

        # ── main and unkeyed branches are silent ───────────────────────────────
        set_state(state, types={"TEST-1": "Task"}, statuses={"TEST-1": "To Do"})
        git(repo, "checkout", "-q", "main")
        commit(repo, acli, state, "four.txt")
        c.check("hook: a commit on main transitions nothing",
                not get_state(state).get("transitions"))

        git(repo, "checkout", "-q", "-b", "spike-no-ticket")
        commit(repo, acli, state, "five.txt")
        c.check("hook: an unkeyed branch transitions nothing",
                not get_state(state).get("transitions"))

        # ── the other two prefixes ─────────────────────────────────────────────
        for prefix in ("claude", "epic"):
            set_state(state, types={"TEST-1": "Task"}, statuses={"TEST-1": "To Do"})
            git(repo, "checkout", "-q", "-b", f"{prefix}/TEST-1-lane")
            commit(repo, acli, state, f"{prefix}.txt")
            c.check(f"hook: {prefix}/ is in scope too",
                    get_state(state)["statuses"]["TEST-1"] == "In Progress")
            git(repo, "checkout", "-q", "main")

        # ── the DISABLE kill switch, at RUNTIME ────────────────────────────────
        # This was a source-grep (`"DISABLE" in text`), which any string containing those
        # letters satisfies and which cannot see whether the check runs BEFORE the call it
        # guards - the repo's own source-grep-guards-cannot-see-order lesson.
        set_state(state, types={"TEST-3": "Task"}, statuses={"TEST-3": "To Do"})
        git(repo, "checkout", "-q", "-b", "chore/TEST-3-killswitch")
        (repo / ".agents/scripts/git-hooks/DISABLE").write_text("", encoding="utf-8")
        commit(repo, acli, state, "killed.txt")
        c.check("hook: DISABLE actually stops it - no call, no marker",
                not get_state(state).get("transitions")
                and not (marker_dir(repo) / "jira-started-chore-TEST-3-killswitch").exists(),
                "a kill switch checked AFTER the call is not a kill switch")
        (repo / ".agents/scripts/git-hooks/DISABLE").unlink()
        commit(repo, acli, state, "revived.txt")
        c.check("hook: removing DISABLE revives it",
                get_state(state)["statuses"]["TEST-3"] == "In Progress")
        git(repo, "checkout", "-q", "main")

        # ── jira.conf is READ, not merely mentioned ────────────────────────────
        # A repo with no board binding has nothing to move. Same reason: the old assertion
        # ("jira.conf" in text) could not tell reading from mentioning.
        set_state(state, types={"TEST-4": "Task"}, statuses={"TEST-4": "To Do"})
        conf = repo / ".agents/jira.conf"
        conf.rename(repo / ".agents/jira.conf.off")
        git(repo, "checkout", "-q", "-b", "chore/TEST-4-noconf")
        commit(repo, acli, state, "noconf.txt")
        c.check("hook: no jira.conf means no board binding, so nothing moves",
                not get_state(state).get("transitions"),
                "graceful degradation, the same as the armed commit-msg gate")
        (repo / ".agents/jira.conf.off").rename(conf)
        git(repo, "checkout", "-q", "main")

        # ── a status that is NOT startable must not write the marker ───────────
        # The bug the clean-room review found: `Blocking` exited 0, the marker was written,
        # and when the blocker cleared the ticket sat in `To Do` for the whole build - the
        # exact defect this lane exists to close, reintroduced by the lane itself.
        set_state(state, types={"TEST-6": "Task"}, statuses={"TEST-6": "Blocking"})
        git(repo, "checkout", "-q", "-b", "chore/TEST-6-blocked")
        commit(repo, acli, state, "blocked.txt")
        c.check("hook: a Blocking ticket writes NO marker",
                not (marker_dir(repo) / "jira-started-chore-TEST-6-blocked").exists(),
                "'left alone' is not 'settled'")
        set_state(state, types={"TEST-6": "Task"}, statuses={"TEST-6": "To Do"})
        commit(repo, acli, state, "unblocked.txt")
        c.check("hook: once the blocker clears, the NEXT commit starts it",
                get_state(state)["statuses"]["TEST-6"] == "In Progress",
                "this is what marking on exit 0 destroyed")
        git(repo, "checkout", "-q", "main")

        # ── a real WORKTREE, which is where this toolkit actually runs ─────────
        # Promised by the plan's audit finding F-3 and not delivered in the first cut: every
        # case above uses `git checkout -b` in one ordinary checkout, and --absolute-git-dir
        # resolves DIFFERENTLY in a worktree (.git/worktrees/<name>). If it resolved to the
        # shared .git, the marker PATH would differ from where the hook looks. (It is named
        # for the BRANCH and git forbids two worktrees on one branch, so the git dir is not
        # what prevents a cross-lane collision - the branch name is. What this case actually
        # earns is proof the hook RUNS from inside a worktree at all, and it paid for itself
        # immediately: build() never COMMITTED .agents/, so a fresh worktree had no
        # jira_feed.py to call, which reads exactly like the hook failing.)
        set_state(state, types={"TEST-5": "Task"}, statuses={"TEST-5": "To Do"})
        wt = tmp / "wt-lane"
        git(repo, "worktree", "add", "-q", str(wt), "-b", "chore/TEST-5-in-a-worktree")
        (wt / "w.txt").write_text("x", encoding="utf-8")
        git(wt, "add", "w.txt")
        r = git(wt, "commit", "-q", "-m", "TEST-5 chore: from inside a worktree",
                env={"ACLI_BIN": str(acli), "STUB_STATE": str(state)})
        c.check("hook: fires from inside a real worktree", r.returncode == 0
                and get_state(state)["statuses"]["TEST-5"] == "In Progress",
                (r.stderr or r.stdout).strip()[:200])
        c.check("hook: the marker lands in the WORKTREE's git dir, not the shared one",
                (marker_dir(wt) / "jira-started-chore-TEST-5-in-a-worktree").exists()
                and "worktrees" in str(marker_dir(wt)),
                "a shared marker would let one lane silence another")

        # ── SILENCE on a say()-to-stdout failure, at RUNTIME ───────────────────
        # ⭐ The load-bearing one, and the previous cut had NO effective coverage of it: the
        # assertion was `">/dev/null 2>&1" in text`, which the interpreter probe's own
        # `command -v "$c" >/dev/null 2>&1` satisfies — so it passed against the UNFIXED
        # hook. A `Done` key is the right probe because jira_feed refuses it through say(),
        # which prints to STDOUT; the old `2>/dev/null` swallowed only stderr, so this
        # five-line refusal hit the terminal on EVERY commit of the branch.
        set_state(state, types={"TEST-9": "Task"}, statuses={"TEST-9": "Done"})
        git(repo, "checkout", "-q", "-b", "chore/TEST-9-done-key")
        (repo / "nine9.txt").write_text("x", encoding="utf-8")
        git(repo, "add", "nine9.txt")
        r = git(repo, "commit", "-q", "-m", "TEST-9 chore: a key that is already Done",
                env={"ACLI_BIN": str(acli), "STUB_STATE": str(state)})
        noise = (r.stdout or "") + (r.stderr or "")
        c.check("hook: a refusal is SILENT - nothing reaches the terminal",
                r.returncode == 0 and "not your key" not in noise and not noise.strip(),
                f"leaked: {noise.strip()[:160]!r}")
        c.check("hook: a refused key writes NO marker, and did not move the ticket",
                not (marker_dir(repo) / "jira-started-chore-TEST-9-done-key").exists()
                and get_state(state)["statuses"]["TEST-9"] == "Done")
        git(repo, "checkout", "-q", "main")

        # ── a re-opened ticket, cut as a fresh lane, fires again ───────────────
        # The marker is named for the BRANCH, not the key. A key-named marker made this go
        # silent: `flag` moves a broken ticket Done -> To Do and the fix is cut as a new
        # lane, which would then never leave `To Do`. Found by the claude//epic/ cases above
        # failing for this reason and not the one they were written for.
        set_state(state, types={"TEST-1": "Task"}, statuses={"TEST-1": "To Do"})
        git(repo, "checkout", "-q", "-b", "chore/TEST-1-the-refix")
        commit(repo, acli, state, "refix.txt")
        c.check("hook: a SECOND branch on the same key still fires (re-opened ticket)",
                get_state(state)["statuses"]["TEST-1"] == "In Progress",
                "a key-named marker would leave the rebuild sitting in To Do")
        git(repo, "checkout", "-q", "main")

        # ── a move that SILENTLY NO-OPS: no marker, so the NEXT commit retries ──
        # `stuck_status` makes the stub exit 0 and print "Work item transitioned" while
        # changing nothing - acli's real swallow, which is why every write verb here reads
        # the ticket back. This is NOT the offline case; that one is below. Naming it
        # "unreachable" was wrong and hid the fact that the genuine transport failure was
        # never driven from this file.
        set_state(state, types={"TEST-2": "Task"}, statuses={"TEST-2": "To Do"},
                  stuck_status=True)
        git(repo, "checkout", "-q", "-b", "chore/TEST-2-silent-noop")
        r = commit(repo, acli, state, "six.txt")
        c.check("hook: a commit still succeeds when the move silently no-ops",
                r.returncode == 0, (r.stderr or r.stdout).strip()[:200])
        c.check("hook: a move that did not land writes NO marker",
                not (marker_dir(repo) / "jira-started-chore-TEST-2-silent-noop").exists(),
                "the read-back is what turns a swallowed write into a retry")

        set_state(state, types={"TEST-2": "Task"}, statuses={"TEST-2": "To Do"})
        commit(repo, acli, state, "seven.txt")
        c.check("hook: the next commit retries and lands it",
                get_state(state)["statuses"]["TEST-2"] == "In Progress",
                "self-healing, by construction")
        git(repo, "checkout", "-q", "main")

        # ── genuinely unreachable: acli itself fails ───────────────────────────
        # The transport failure, driven for real by pointing ACLI_BIN at a binary that is
        # not there - the plane case. Distinct code path (acli_json -> None -> wf.die) from
        # the silent no-op above, and it was never exercised until the review said so.
        set_state(state, types={"TEST-8": "Task"}, statuses={"TEST-8": "To Do"})
        git(repo, "checkout", "-q", "-b", "chore/TEST-8-no-board")
        (repo / "eight.txt").write_text("x", encoding="utf-8")
        git(repo, "add", "eight.txt")
        r = git(repo, "commit", "-q", "-m", "TEST-8 chore: committed with no board",
                env={"ACLI_BIN": str(tmp / "does-not-exist"), "STUB_STATE": str(state)})
        c.check("hook: a commit succeeds with NO board reachable at all",
                r.returncode == 0, (r.stderr or r.stdout).strip()[:200])
        c.check("hook: an unreachable board is SILENT - nothing on stdout or stderr",
                not (r.stdout or "").strip() and not (r.stderr or "").strip(),
                "jira_feed prints through say() -> STDOUT; redirecting stderr alone printed "
                "a five-line refusal on EVERY commit")
        c.check("hook: unreachable writes no marker, so it retries when you land",
                not (marker_dir(repo) / "jira-started-chore-TEST-8-no-board").exists())
        commit(repo, acli, state, "nine.txt")
        c.check("hook: back online, the next commit starts it",
                get_state(state)["statuses"]["TEST-8"] == "In Progress")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
