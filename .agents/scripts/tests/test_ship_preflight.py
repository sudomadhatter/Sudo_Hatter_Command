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
            c.check("SP-B ...and it says the merge would not carry them",
                    "the merge" in out.lower() and "not carry" in out.lower(),
                    "the reason is the whole finding: the gate runs on this tree, the merge "
                    "ships the branch, and they are not the same content")
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
