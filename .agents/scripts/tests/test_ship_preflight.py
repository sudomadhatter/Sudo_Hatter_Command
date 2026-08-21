"""ship_preflight.py — the door to PRODUCTION must answer mechanically, before it writes.

`/cicd-push-e2e` is the only command in this system that writes production `main`, and until
SCC-211 it was the only door that ran no mechanical precheck at all. Its two siblings both
call one — `closeout_preflight.py` for a story, `task_preflight.py` for a task — and this one
resolved a branch from `git branch -a`, asked the operator to confirm it by name, and started
merging.

THE FAILURE THAT NAMES THIS FILE. Uncommitted changes sit in the epic-branch checkout. Step 3
runs the full gate on that dirty tree and it comes back green. Step 4 checks out `main` and
merges the BRANCH, which does not contain those edits — so what shipped to production was
never what was gated, and nothing in the door's 151 lines would have said so. The same shape
as the 2026-08-09 close-out that resolved a sibling's branch and returned a clean verdict
about it: a door that reads the repo instead of asserting against it can be honestly, fluently
wrong.

Real git repositories in temp dirs with a real bare `origin` — every question here is a git
question (ancestry, ahead/behind, porcelain, a diff), and a mocked git would only prove the
mock agrees with itself. Commits use the fixture's own `--no-verify` path so these repos never
inherit this machine's hooks.

⛔ EVERY case pins a PHRASE, never an exit code alone. A missing or unparseable script exits 2
from the interpreter, and an exit-code-only assertion for a REFUSAL would pass on it — the red
would be indistinguishable from the green it is meant to precede
([[red-test-can-die-before-its-assertion]]). SP-A is the positive control that a refusal-only
file cannot satisfy.

Stdlib only, no pytest.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script
from _pf_fixtures import branch, commit, git, make_repo, write

SCRIPT = "ship_preflight.py"


def ship(repo: Path, br: str, *extra: str, expect: str = "SCC-11") -> tuple[int, str]:
    """The production door's preflight, invoked the way the door invokes it.

    ⛔ `--repo`, `--branch` and `--expect-key` are all passed, always, because the script
    REQUIRES all three. `/cicd-push-e2e` binds `PROJECT_ROOT` at its Step 0 and resolves the
    branch at its Step 1, so it has every one of them in hand; letting the script guess any
    of them would re-open `worktree-per-story.md` § "cwd is not intent" — the trap that made
    a close-out resolve a sibling lane's branch and report a clean verdict about it.
    """
    return run_script(SCRIPT, "--repo", str(repo), "--branch", br,
                      "--expect-key", expect, *extra)


def main() -> int:
    c = Cases("ship preflight (SCC-211 — the production door's mechanical precheck)")

    # A legible red if the script goes missing: without it every case below reports the same
    # "can't open file" and the reason is buried in each one.
    #
    # ⛔ GUARDED, like every other check here, and it did not start that way. Written bare, it
    # ran under EVERY `--case` filter and counted toward every filtered tally — so a mutant it
    # killed would be attributed to whichever case the sweep happened to name, which is
    # exactly the corruption `mutation_sweep.py` refuses to score. `test_suite_runner.py`'s
    # ORPHAN walker caught it in this lane's own first full run.
    if c.block("SP-0 · the script the door depends on exists"):
        c.check(f"SP-0 .agents/scripts/{SCRIPT} exists", (SCRIPTS / SCRIPT).is_file(),
                "/cicd-push-e2e Step 1.5 calls it; without it the door has no precheck at "
                "all, which is the SCC-211 defect restored")

    # ── SP-A · THE POSITIVE CONTROL ───────────────────────────────────────────────────────
    # A preflight that reports a problem on correct work is a preflight nobody runs twice,
    # and a file of refusals-only would pass every case below on a script that always
    # exits 2. This is the case that cannot be satisfied that way.
    if c.block("SP-A · the positive control: a clean, pushed epic branch is CLEAR"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-A clean epic -> exit 0", code == 0, out.strip()[-300:])
            # ⛔ COUNTED, not just present — and the count is the assertion that matters.
            # `in out` was true while the line printed TWICE (an explicit print plus the one
            # `Report.print_human` emits), and a review smoke-run against a real project
            # repo is what surfaced it. The door's Step 1.5 says "read the header before the
            # verdict"; a doubled header is noise in the one line that catches a wrong lane.
            c.check("SP-A the header echoes the branch it RESOLVED, EXACTLY once",
                    out.count("== ship preflight - epic/SCC-11-thing ==") == 1,
                    f"seen {out.count('== ship preflight - epic/SCC-11-thing ==')}x - the "
                    "header is the only thing that can catch a wrong branch: a verdict "
                    "about another lane reads exactly like a verdict about yours")
            c.check("SP-A the verdict says clear", "VERDICT: clear" in out,
                    out.strip()[-200:])
            c.check("SP-A an epic branch takes the FULL gate", "full gate" in out,
                    out.strip()[-300:])

    # ── SP-B · THE LOAD-BEARING NEGATIVE: a dirty checkout is gated, then not shipped ──────
    if c.block("SP-B · a dirty epic checkout REFUSES before the gate runs"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            write(repo, "backend/app.py", "x = 3   # never committed, never merged\n")
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-B dirty tree -> exit 2", code == 2, out.strip()[-300:])
            c.check("SP-B ...and it says UNCOMMITTED", "uncommitted" in out.lower(),
                    out.strip()[-300:])
            c.check("SP-B ...and it says WHY: what ships was never gated",
                    "what ships was never gated" in out.lower(),
                    "the reason is the whole finding: the gate runs on this tree, the merge "
                    "carries only the branch, and they are not the same content. Pinned on "
                    "that clause because it is the sentence that survives rewording — an "
                    "earlier pin on 'not carry' broke when the worktree fix improved the "
                    "message, which is a guard keying on prose rather than on meaning")
            c.check("SP-B the VERDICT is BLOCKED, not a warning under a clear line",
                    "VERDICT: BLOCKED" in out, out.strip()[-200:])

        # An UNTRACKED file is dirt too. `git status --porcelain` reports it `??`, and a
        # check written against ` M` alone would wave through a whole new module sitting in
        # the epic checkout — the shape that is hardest to notice, because nothing it
        # replaces looks different.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            write(repo, "backend/new_module.py", "def ship(): ...\n")
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-B an UNTRACKED file is dirt too -> exit 2",
                    code == 2 and "uncommitted" in out.lower(), out.strip()[-300:])

    # ── SP-C · the branch exists on ONE disk ──────────────────────────────────────────────
    if c.block("SP-C · unsynced: a commit on one disk cannot be what production runs"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            write(repo, "backend/app.py", "x = 4\n")
            commit(repo, "SCC-11 chore: local only")
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-C ahead of origin -> exit 2", code == 2, out.strip()[-300:])
            c.check("SP-C ...and it names ahead/behind", "ahead" in out.lower(),
                    out.strip()[-300:])

        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"}, push=False)
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-C never pushed -> exit 2", code == 2, out.strip()[-300:])
            c.check("SP-C ...and it says so in those words",
                    "never pushed" in out.lower(), out.strip()[-300:])

        # ⛔ THE MIRROR CASE, AND THE FIRST CUT GOT IT EXACTLY BACKWARDS. A branch that
        # exists ONLY on `origin` — no local ref — was reported as "never pushed: the branch
        # exists on this disk only", which is the precise opposite of the truth. It is not a
        # rare shape: `/cicd-push-e2e` Step 1 resolves branches with `git branch -a`, which
        # lists remote-tracking refs, so a fresh clone or an epic pushed from the OTHER
        # machine (this system is two machines by design) lands here — and the door's own
        # Step 2 then does `git checkout epic/...`, which creates the local ref from origin.
        # A false BLOCKED on the shipping path is the failure mode this repo treats as worst:
        # a gate that false-reds is a gate that gets routed around.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})   # pushed
            git(repo, "checkout", "-q", "main")
            git(repo, "branch", "-D", "epic/SCC-11-thing")                     # local ref gone
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-C remote-only (pushed, not checked out here) is CLEAR -> exit 0",
                    code == 0, out.strip()[-400:])
            c.check("SP-C ...and it never claims the branch is unpushed",
                    "never pushed" not in out.lower(), out.strip()[-400:])
            c.check("SP-C ...and it says the checkout will create it from origin",
                    "origin" in out.lower() and "not checked out" in out.lower(),
                    out.strip()[-400:])

        # And the shape where neither ref exists is its own answer, not either of the above.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            code, out = ship(repo, "epic/SCC-11-nonexistent", expect="SCC-11")
            c.check("SP-C a branch that exists NOWHERE -> exit 2", code == 2,
                    out.strip()[-300:])
            c.check("SP-C ...named as absent, not as unpushed",
                    "no such branch" in out.lower(), out.strip()[-300:])

    # ── SP-D · the branch the OPERATOR meant ──────────────────────────────────────────────
    if c.block("SP-D · intent: the resolved branch must carry the key that was PINNED"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing", expect="SCC-99")
            c.check("SP-D wrong --expect-key -> exit 2", code == 2, out.strip()[-300:])
            c.check("SP-D ...and it names BOTH keys",
                    "SCC-99" in out and "SCC-11" in out, out.strip()[-300:])

        # The key must also be one THIS repo answers to. `.agents/jira.conf` says SCC; an
        # AVCH-keyed branch here means the armed commit-msg hook never ran — bypassed, or
        # never armed on this machine (`core.hooksPath` is per-machine, so a fresh clone has
        # no gates at all).
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/AVCH-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/AVCH-11-thing", expect="AVCH-11")
            c.check("SP-D a key this repo does not answer to -> exit 2", code == 2,
                    out.strip()[-300:])
            # ⛔ NOT `"SCC" in out`. The temp repo's own PATH carries the string on this
            # machine (the lane is `SCC-211-push-e2e-precheck`), so that assertion passed
            # against a script that does not exist yet - a phrase pin matching the
            # scaffolding instead of the answer. Pin the SENTENCE.
            c.check("SP-D ...and it names the repo's own project(s)",
                    "not one of this repo's projects" in out.lower(), out.strip()[-300:])

    # ── SP-E · the shapes this door is NOT for ────────────────────────────────────────────
    if c.block("SP-E · shape: every refusal names the command that IS right"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "claude/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "claude/SCC-11-thing")
            c.check("SP-E a story branch -> exit 2 naming the story close-out",
                    code == 2 and "/cicd-close-story-merge-tree" in out,
                    out.strip()[-300:])

        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/legacy-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/legacy-thing")
            c.check("SP-E a keyless epic -> exit 2", code == 2, out.strip()[-300:])
            c.check("SP-E ...and it forbids inventing a key",
                    "never invent" in out.lower(), out.strip()[-300:])

        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            code, out = ship(repo, "main")
            c.check("SP-E standing on main -> exit 2", code == 2, out.strip()[-300:])
            c.check("SP-E ...and it says this door merges INTO main",
                    "into" in out.lower() and "main" in out.lower(), out.strip()[-300:])

    # ── SP-F · THE LANE: what a chore branch is actually allowed to do here ────────────────
    # `/cicd-push-e2e` admits a `chore/<KEY>-<slug>` branch and then names only `epic/*` in
    # every operative line after it, so the shape it accepts has no written procedure.
    # `git-policy.md` routes only the deployable-touching chore diff here; the rest belongs
    # to `/smh-close-task-merge-tree`, whose Task ceremony (manifest, `## Your Actions`, Dev
    # Record, ticket move, prune) never runs for a lane that lands through this door.
    if c.block("SP-F · the lane: a chore branch is admitted only when its diff DEPLOYS"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "chore/SCC-11-thing")
            c.check("SP-F a deployable chore diff is ADMITTED -> exit 0", code == 0,
                    out.strip()[-300:])
            c.check("SP-F ...under the LIGHT gate, named", "light gate" in out.lower(),
                    out.strip()[-300:])
            c.check("SP-F ...naming the deployable path it found",
                    "backend/" in out, out.strip()[-300:])

        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-thing", {"docs/notes.md": "# notes\n"})
            code, out = ship(repo, "chore/SCC-11-thing")
            c.check("SP-F a docs-only chore diff is REFUSED -> exit 2", code == 2,
                    out.strip()[-300:])
            c.check("SP-F ...and handed to the Task door",
                    "/smh-close-task-merge-tree" in out, out.strip()[-300:])

        # A repo with no deployable surface at all cannot produce a deployable diff, so the
        # chore lane can never be legitimate here. This is the command centre's own shape,
        # and the refusal must not depend on what the diff happens to contain.
        with TempDir() as t:
            repo = make_repo(t, deployable=False)
            branch(repo, "chore/SCC-11-thing", {"docs/notes.md": "# notes\n"})
            code, out = ship(repo, "chore/SCC-11-thing")
            c.check("SP-F a repo that deploys NOTHING refuses the chore lane -> exit 2",
                    code == 2 and "/smh-close-task-merge-tree" in out, out.strip()[-300:])
            # ⛔ AND IT MUST SAY *WHY*, which is a different sentence from the one the
            # missed-the-diff arm prints. A SURVIVING MUTANT FOUND THIS: deleting the
            # `not surface` arm entirely left this case green, because the diff arm below
            # also refuses and also names the Task door. Same verdict, different fact — and
            # the fact is the whole value of the arm: "your diff happened to miss" is
            # actionable, "this repo can never qualify" ends the question.
            c.check("SP-F ...naming the REASON: the repo has no deployable surface at all",
                    "no deployable surface" in out.lower(), out.strip()[-300:])

        # ⛔ AND THE CONTROL THAT KEEPS THE LANE HONEST IN THE OTHER DIRECTION: an epic
        # branch is never subjected to the deployable-diff question. An epic ships whatever
        # it ships; the question exists only to decide whether a CHORE lane belongs here.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"docs/notes.md": "# notes\n"})
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-F CONTROL: a docs-only EPIC is still clear (the lane question is "
                    "the chore lane's alone)", code == 0, out.strip()[-300:])

    # ── SP-I · the operands this script REFUSES to guess at ───────────────────────────────
    # `argparse`'s `required=True` is satisfied by the empty string, and an empty operand is
    # exactly what an unset shell variable becomes. The door pins `EXPECTED_KEY` in one fenced
    # block and consumes it in another two steps later, so the empty case is not exotic — and
    # left unchecked it produced the WORST possible message: `--expect-key  but epic/X carries
    # SCC-11 … aimed at ANOTHER lane's branch`, blaming a branch that was right all along.
    # `_harness._case_filter` carries this same lesson for `--case`.
    if c.block("SP-I · an empty operand is named as missing, never blamed on the branch"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing", expect="")
            c.check("SP-I an empty --expect-key -> exit 2", code == 2, out.strip()[-300:])
            c.check("SP-I ...named as the PIN that never arrived",
                    "expect-key" in out.lower()
                    and ("empty" in out.lower() or "never arrived" in out.lower()),
                    out.strip()[-300:])
            c.check("SP-I ...and it does NOT accuse the branch of being another lane's",
                    "another lane" not in out.lower(), out.strip()[-300:])

            code, out = run_script(SCRIPT, "--repo", "", "--branch", "epic/SCC-11-thing",
                                   "--expect-key", "SCC-11")
            c.check("SP-I an empty --repo -> exit 2, never a silent fall back to cwd",
                    code == 2 and "repo" in out.lower(), out.strip()[-300:])

    # ── SP-J · the human run names the REPO it resolved, not only the branch ───────────────
    # The door tells the reader "read the header before the verdict" because a verdict about
    # another lane reads exactly like a verdict about yours. That argument is just as true of
    # the repo — `--repo` exists precisely because cwd is not intent — and until this case the
    # resolved repo appeared only in `--json`. A run aimed at the wrong project printed a
    # verdict a reader could not tell from the right one.
    if c.block("SP-J · the resolved repo is echoed on the human path too"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing")
            # ⛔ THE FULL PATH, not `repo.name`. The fixture directory is literally called
            # `repo`, so `repo.name in out` matched the word "repo" already present in the
            # output and the case passed against a script that echoed nothing — a vacuous
            # green caught by running this very block red.
            c.check("SP-J the human output names the resolved repo PATH",
                    str(repo.resolve()) in out, out.strip()[:300])

    # ── SP-K · the LANE question needs a diff it actually GOT ─────────────────────────────
    # `check_lane` read `diff.stdout` without reading `diff.returncode`, so a diff that never
    # ran produced `0 file(s) changed, none of them deployable` — a stated FACT about a diff
    # the script did not obtain — and routed the lane to the Task door on it. The reachable
    # trigger is the same remote-only shape SP-C covers: no local ref, so `base...branch`
    # cannot resolve. A deployable chore lane would be sent to `/smh-close-task-merge-tree`,
    # which refuses deployable diffs and hands it straight back — each door naming the other.
    if c.block("SP-K · a chore lane on a remote-only branch still reads its real diff"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            git(repo, "checkout", "-q", "main")
            git(repo, "branch", "-D", "chore/SCC-11-thing")     # pushed, local ref gone
            code, out = ship(repo, "chore/SCC-11-thing")
            c.check("SP-K the deployable diff is still SEEN -> exit 0", code == 0,
                    out.strip()[-400:])
            c.check("SP-K ...and the light gate is named", "light gate" in out.lower(),
                    out.strip()[-400:])
            c.check("SP-K ...never '0 file(s) changed' about a diff it did not get",
                    "0 file(s) changed" not in out, out.strip()[-400:])

        # ⛔ AND THE CASE THAT ACTUALLY FAILS THE DIFF — added because a MUTANT SURVIVED.
        # Disabling the `diff.returncode` check left the block above green: the ref fallback
        # fixed alongside it means the diff now succeeds here, so the returncode arm had no
        # covering case at all and read as defensive code nobody had exercised. The arm is
        # right (a repo with neither `main` nor `origin/main` cannot resolve a base), so the
        # answer is a case, not a deletion: with no base to diff against, the script must say
        # the lane question is UNANSWERABLE rather than assert an empty diff as a fact.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-thing", {"backend/app.py": "x = 2\n"}, push=False)
            git(repo, "remote", "remove", "origin")     # no origin/main
            git(repo, "branch", "-D", "main")           # and no local main either
            code, out = ship(repo, "chore/SCC-11-thing")
            c.check("SP-K a diff that CANNOT run is named unanswerable, not empty",
                    "unanswerable" in out.lower(), out.strip()[-400:])
            c.check("SP-K ...and it never states a file count it did not measure",
                    "file(s) changed, none of them deployable" not in out,
                    out.strip()[-400:])

    # ── SP-N · THE DEFECT, SURVIVING IN THIS SYSTEM'S DEFAULT SHAPE ───────────────────────
    # `worktree-per-story` makes a linked worktree the NORM here, not an exotic case — "the
    # standing environment: parallel teams are the NORM". In that shape `PROJECT_ROOT` stands
    # on `main` and is spotless while the tree actually holding the epic branch is dirty, so
    # a `status --porcelain` in `PROJECT_ROOT` alone answered `working tree clean` and the
    # verdict read `clear to gate and ship`.
    #
    # That is not a near-miss of the SCC-211 defect — it IS the SCC-211 defect: the gate runs
    # where the work is (`wf_common.tree_guard` actively sends the operator there: "Run it in
    # the lane: cd <worktree>"), the merge ships the branch, and the uncommitted delta between
    # them is exactly what never gets gated. Reproduced before it was fixed.
    if c.block("SP-N · dirt in the worktree that HOLDS the branch is not invisible"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            git(repo, "checkout", "-q", "main")
            wt = t / "epic-tree"
            git(repo, "worktree", "add", "-q", str(wt), "epic/SCC-11-thing")
            (wt / "backend" / "app.py").write_text("x = 999   # uncommitted, in the worktree\n",
                                                   encoding="utf-8")
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-N a dirty linked worktree BLOCKS the ship", code == 2,
                    out.strip()[-500:])
            c.check("SP-N ...naming the tree that is actually dirty",
                    "epic-tree" in out, out.strip()[-500:])
            c.check("SP-N ...and never reports the lane as clean",
                    "working tree clean" not in out or "epic-tree" in out,
                    out.strip()[-500:])

        # The positive control: the same shape, CLEAN. A check that refuses every worktree
        # would be as broken as one that sees none — and worktrees are the normal shape here,
        # so a false red would fire on almost every ship.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            git(repo, "checkout", "-q", "main")
            git(repo, "worktree", "add", "-q", str(t / "epic-tree"), "epic/SCC-11-thing")
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-N CONTROL: a CLEAN linked worktree still ships", code == 0,
                    out.strip()[-400:])

    # ── SP-L · the TABLE and the REGEX, read directly — the fast tier ─────────────────────
    # Everything else here costs a subprocess, a temp repo and a real git round trip, which is
    # why the branch-shape gaps clustered: each extra shape cost a repo. These are the two
    # pure structures, imported and asserted, the way `test_task_preflight.py` pins the same
    # table for the sibling. Structural pins cannot see behaviour, so the behavioural cases
    # below still exist — this block makes them cheap, it does not replace them.
    if c.block("SP-L · WRONG_LANE and BRANCH_RE, pinned structurally"):
        sys.path.insert(0, str(SCRIPTS))
        import ship_preflight as _sp

        keys = list(_sp.WRONG_LANE)
        c.check("SP-L WRONG_LANE holds exactly the prefixes real commands create",
                set(keys) == {"claude/incident-", "claude/"}, f"got {sorted(keys)}")
        # ⛔ ORDER, and it is load-bearing: the scan is first-match `startswith` over insertion
        # order, so a generic prefix listed before a specific one makes the specific entry
        # UNREACHABLE. That is the literal SCC-148 defect — `claude/` before
        # `claude/incident-` routed a live incident branch to the story close-out, confidently,
        # on the one path that runs under production pressure. A set pin is order-blind, and
        # order is exactly what a future alphabetical tidy would break.
        shadowed = [(a, b) for i, a in enumerate(keys) for b in keys[i + 1:]
                    if b.startswith(a)]
        c.check("SP-L no WRONG_LANE entry is shadowed by an earlier prefix",
                not shadowed, f"unreachable: {shadowed}")
        c.check("SP-L every WRONG_LANE row names the command that IS right",
                all(v[0].startswith("/") for v in _sp.WRONG_LANE.values()),
                str(_sp.WRONG_LANE))

        # BRANCH_RE: the key sits IMMEDIATELY after the prefix, because Atlassian's GitHub app
        # joins on the key as a literal string in the branch NAME. `epic/thin-AVCH-23-x` is
        # git-legal and would link nothing.
        for good in ("epic/SCC-11-thing", "chore/SCC-11-thing", "epic/AVCH-9-x-y/z"):
            c.check(f"SP-L BRANCH_RE accepts {good}", bool(_sp.BRANCH_RE.match(good)))
        for bad in ("epic/thin-SCC-11-toolkit", "epic/scc-11-thing", "epic/SCC11-thing",
                    "epic/legacy-thing", "release/SCC-11-thing", "epic/SCC-11"):
            c.check(f"SP-L BRANCH_RE refuses {bad}", not _sp.BRANCH_RE.match(bad))

        # The remote-ref spellings `git branch -a` actually prints.
        for raw, want in (("remotes/origin/epic/SCC-11-x", "epic/SCC-11-x"),
                          ("origin/epic/SCC-11-x", "epic/SCC-11-x"),
                          ("upstream/chore/SCC-11-x", "chore/SCC-11-x"),
                          ("epic/SCC-11-x", "epic/SCC-11-x"),
                          ("origin/main", "origin/main")):
            got = _sp.REMOTE_PREFIX_RE.sub("", raw)
            c.check(f"SP-L remote prefix: {raw} -> {want}", got == want, f"got {got}")

    # ── SP-M · the shapes and states the fixtures could not reach ─────────────────────────
    # Every case here was added because a mutant SURVIVED the suite: an independent lens ran
    # its own 15-mutant sweep against this file and every one lived. They are grouped rather
    # than scattered so the reason stays legible.
    if c.block("SP-M · gaps a surviving mutant proved were uncovered"):
        # (1) the door's own Step 1 output, pasted verbatim
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            git(repo, "checkout", "-q", "main")
            git(repo, "branch", "-D", "epic/SCC-11-thing")
            code, out = ship(repo, "remotes/origin/epic/SCC-11-thing")
            c.check("SP-M `git branch -a`'s own spelling is understood, not refused",
                    code == 0, out.strip()[-400:])
            c.check("SP-M ...and it SAYS what it read the name as",
                    "read 'remotes/origin/epic/SCC-11-thing' as" in out, out.strip()[-400:])
            c.check("SP-M ...never advising a rename of a branch that carries its key",
                    "never invent" not in out.lower(), out.strip()[-400:])

        # (2) the incident lane — the sibling's SCC-148 guard, ported
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "claude/incident-abc123", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "claude/incident-abc123")
            c.check("SP-M claude/incident-* is refused", code == 2, f"exit {code}")
            c.check("SP-M ...naming the incident lane, never the story close-out",
                    "/cicd-mobile-error-team" in out
                    and "/cicd-close-story-merge-tree" not in out, out.strip()[-300:])

        # (1b) `origin/main` is a THIRD spelling of the target branch, and the remote-prefix
        # normaliser deliberately does not touch it (its lookahead only fires before a lane
        # prefix). So the standing-on-main guard has to name it itself — and it did, with no
        # case saying so: dropping that one member left the whole suite green while
        # `--branch origin/main` fell through to the keyless-epic refusal, which advises a
        # RENAME of production's own branch.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            code, out = ship(repo, "origin/main")
            c.check("SP-M origin/main is refused as the TARGET, not as a keyless epic",
                    code == 2 and "into" in out.lower() and "never invent" not in out.lower(),
                    out.strip()[-300:])
            # ⛔ AND IT IS REFUSED ONCE. A live run against a real project repo printed a
            # SECOND error underneath — `origin/main: no such branch, local or remote` —
            # about a ref that plainly exists, because the ref probe had gone looking for
            # `refs/heads/origin/main`. The verdict was right and the sentence was false, and
            # this repo has already paid for that distinction once: *"a gate that states
            # something plainly untrue teaches the reader to stop believing its output"*
            # (`task_preflight.check_scope`). Once the shape check has ruled, the ref-state
            # question is meaningless and must decline rather than pile on.
            c.check("SP-M ...and it does not then claim the ref does not exist",
                    "no such branch" not in out.lower(), out.strip()[-300:])

        # (2b) the scan must be ANCHORED at position 0, not a substring search. `BRANCH_RE`'s
        # slug group is `.+`, which matches slashes, so a chore branch embedding a lane word
        # mid-name is both git-legal and shape-legal — and a `prefix in branch` scan would
        # wrong-lane it to a command that has no business with it. The sibling carries this
        # exact guard for the same table.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-notes-on-claude/incident-triage",
                   {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "chore/SCC-11-notes-on-claude/incident-triage")
            c.check("SP-M a lane word INSIDE a slug is not a lane match (anchored scan)",
                    "/cicd-mobile-error-team" not in out
                    and "/cicd-close-story-merge-tree" not in out, out.strip()[-300:])

        # (3) a fetch that is ASKED FOR and FAILS — the outcome, not the flag
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            git(repo, "remote", "set-url", "origin", str(t / "no-such-remote.git"))
            code, out = ship(repo, "epic/SCC-11-thing")          # no --no-fetch
            verdict = [ln for ln in out.splitlines() if ln.startswith("VERDICT:")]
            c.check("SP-M a FAILED fetch is not a fresh comparison",
                    "fetch failed" in out.lower(), out.strip()[-400:])
            c.check("SP-M ...and the staleness rides the VERDICT line",
                    bool(verdict) and "stale" in verdict[0].lower(),
                    (verdict[0] if verdict else out.strip()[-200:]))
            c.check("SP-M ...and the exit is non-zero", code != 0, f"exit {code}")

        # (4) BEHIND, and the counts pinned VERBATIM. `"ahead" in out` was satisfied by the
        # message template itself, so swapping the --left-right columns survived.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            write(repo, "backend/app.py", "x = 4\n")
            commit(repo, "SCC-11 chore: pushed, then rewound locally")
            git(repo, "push", "-q", "origin", "epic/SCC-11-thing")
            git(repo, "reset", "-q", "--hard", "HEAD~1")            # local now 1 BEHIND
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-M a branch BEHIND origin -> exit 2", code == 2, out.strip()[-300:])
            c.check("SP-M ...with the counts the right way round: `0 ahead / 1 behind`",
                    "0 ahead / 1 behind" in out, out.strip()[-300:])

        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            write(repo, "backend/app.py", "x = 4\n")
            commit(repo, "SCC-11 chore: local only")
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-M ...and AHEAD reads `1 ahead / 0 behind`, verbatim",
                    "1 ahead / 0 behind" in out, out.strip()[-300:])

        # (5) a repo declaring no Jira project at all — the WARN arm
        with TempDir() as t:
            repo = make_repo(t, deployable=True, jira_conf=False)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-M no .agents/jira.conf WARNS, never blocks",
                    code == 1 and "no .agents/jira.conf" in out, out.strip()[-300:])

        # (5b) ...and the OTHER state that reaches the same arm. `repo_keys` returns [] both
        # when the file is missing and when it is present but declares nothing, and saying
        # "no .agents/jira.conf" in the second case sends the reader hunting for a file that
        # is sitting right there. The remedies differ, so the sentences must.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            write(repo, ".agents/jira.conf", "# JIRA_KEYS was commented out\n")
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-M a PRESENT but empty jira.conf is not called absent",
                    "no .agents/jira.conf" not in out and "declares no JIRA_KEYS" in out,
                    out.strip()[-300:])
            c.check("SP-M ...and it says what the gap COSTS",
                    "would NOT be caught" in out, out.strip()[-300:])

        # (5c) a keyed branch with a prefix this door does not ship. `WRONG_LANE` names the
        # three it knows; anything else must still be refused by shape rather than waved
        # through, and nothing asserted that.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "feature/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "feature/SCC-11-thing")
            c.check("SP-M a keyed branch with a FOREIGN prefix is refused",
                    code == 2 and "immediately after" in out.lower(), out.strip()[-300:])

        # (6) the key is normalised, so the operator's lowercase is not an accusation
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing", expect="scc-11")
            c.check("SP-M a lowercase --expect-key still matches", code == 0,
                    out.strip()[-300:])

        # (7) the branch shape the key-linking rule forbids
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/thin-SCC-11-toolkit", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/thin-SCC-11-toolkit")
            c.check("SP-M a key NOT immediately after the prefix is refused", code == 2,
                    out.strip()[-300:])
            c.check("SP-M ...naming the rule Atlassian actually joins on",
                    "immediately after" in out.lower(), out.strip()[-300:])

        # (8) the notice describing the state the door really calls this in
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            git(repo, "checkout", "-q", "main")
            code, out = ship(repo, "epic/SCC-11-thing")
            c.check("SP-M it says which branch the checkout is STANDING on",
                    "standing on 'main'" in out, out.strip()[-400:])

        # (9) --json on a REFUSAL: the values, not just the keys
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            write(repo, "backend/app.py", "x = 3\n")
            code, out = ship(repo, "epic/SCC-11-thing", "--json")
            try:
                doc = json.loads(out)
            except ValueError:
                doc = {}
            c.check("SP-M --json carries the REAL exit, lane and verdict on a refusal",
                    doc.get("exit") == 2 and doc.get("lane") == "full"
                    and "BLOCKED" in str(doc.get("verdict")), json.dumps(doc)[:220])

    # ── SP-O · the fetch runs WITHOUT the session's GITHUB_TOKEN ──────────────────────────
    # The door's own Rule 2 names a stale session token as a known pull/push failure and tells
    # the operator to clear it. `_fetch` therefore builds its child env by hand — and nothing
    # asserted it, so deleting `env=env` would have failed no test at all. A stale token there
    # fails the fetch, the comparison silently degrades to "vs the LAST fetch", and the door
    # proceeds on a stale answer that reads exactly like a fresh one.
    #
    # Observed rather than reasoned about: a `git` shim first on PATH records the environment
    # it was actually handed. That is the only way to see a child's env from outside it.
    if c.block("SP-O · the fetch child never inherits GITHUB_TOKEN"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            shim, seen = t / "bin", t / "fetch-env.txt"
            shim.mkdir()
            real = shutil.which("git") or "/usr/bin/git"
            (shim / "git").write_text(
                "#!/bin/sh\n"
                'for a in "$@"; do [ "$a" = "fetch" ] && '
                f'printf "%s" "${{GITHUB_TOKEN-<unset>}}" > "{seen}"; done\n'
                f'exec "{real}" "$@"\n', encoding="utf-8")
            (shim / "git").chmod(0o755)
            env = dict(os.environ, PATH=f"{shim}{os.pathsep}{os.environ['PATH']}",
                       GITHUB_TOKEN="stale-token-that-must-not-travel")
            subprocess.run([sys.executable, str(SCRIPTS / SCRIPT), "--repo", str(repo),
                            "--branch", "epic/SCC-11-thing", "--expect-key", "SCC-11"],
                           capture_output=True, text=True, env=env)
            c.check("SP-O the shim saw the fetch at all (the case is not vacuous)",
                    seen.is_file(), f"{seen} never written - PATH shim did not run")
            if seen.is_file():
                c.check("SP-O ...and GITHUB_TOKEN was NOT in the fetch's environment",
                        seen.read_text(encoding="utf-8") == "<unset>",
                        f"child saw GITHUB_TOKEN={seen.read_text(encoding='utf-8')!r}")

    # ── SP-G · an unfetched comparison is not a fresh one ──────────────────────────────────
    # SCC-193's finding, one door over: a note saying the comparison was stale sat under a
    # VERDICT reading "clear to close out and merge", and the verdict line is the only line
    # an agent acts on. So the staleness rides the VERDICT, not a line above it.
    if c.block("SP-G · --no-fetch: the VERDICT itself carries the staleness"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing", "--no-fetch")
            verdict = [ln for ln in out.splitlines() if ln.startswith("VERDICT:")]
            c.check("SP-G the verdict line exists", bool(verdict), out.strip()[-200:])
            c.check("SP-G ...and the word stale is ON it",
                    bool(verdict) and "stale" in verdict[0].lower(),
                    (verdict[0] if verdict else "") or out.strip()[-200:])
            c.check("SP-G ...and the exit is non-zero", code != 0, f"exit {code}")

    # ── SP-H · the machine-readable half ──────────────────────────────────────────────────
    if c.block("SP-H · --json carries what a harness needs"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "epic/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = ship(repo, "epic/SCC-11-thing", "--json")
            try:
                doc = json.loads(out)
            except ValueError:
                doc = None
            c.check("SP-H --json emits parseable JSON on stdout alone", doc is not None,
                    out.strip()[-200:])
            if doc is not None:
                for field in ("branch", "key", "lane", "verdict", "exit"):
                    c.check(f"SP-H ...carrying `{field}`", field in doc,
                            ", ".join(sorted(doc)))
                c.check("SP-H ...and it agrees with the human run",
                        doc.get("branch") == "epic/SCC-11-thing"
                        and doc.get("key") == "SCC-11",
                        json.dumps(doc)[:200])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
