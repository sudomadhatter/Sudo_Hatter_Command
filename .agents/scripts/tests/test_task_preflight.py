"""task_preflight.py must never let deployable code reach `main` through the task lane.

`/smh-close-task-merge-tree` merges to `main`. Everything else that does (`/cicd-push-e2e`) runs
the end-to-end suite first, and the ONLY thing that justifies this command skipping it is the
claim "nothing that deploys changed". That claim is exactly the kind an agent makes about its
own work with unearned confidence, so it is derived here from the repo and the diff, and the
negatives below are what stop it from being derived permissively:

  * a repo that DOES deploy, with `backend/` in the diff -> HANDOFF and a hard exit 2, so a
    product change cannot be re-labelled a task;
  * the same repo with the same command and a docs-only diff -> LOCAL, so the gate is not
    just "always stop", which would get routed around within a week;
  * a repo with no deployable surface at all (the command centre) -> LOCAL, because there is
    no E2E suite there to skip - `git-policy.md` says so and this proves the script agrees.

Plus the positive control: a genuinely clean task branch must exit 0. A preflight that
reports a problem on correct work is a preflight nobody runs twice.

Real git repositories in temp dirs, with a real bare `origin` - the checks are ancestry,
ahead/behind and diff questions, and a mocked git would only prove the mock agrees with
itself. Commits use --no-verify: these fixtures must not inherit the machine's hooks.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir
from _pf_fixtures import (MANIFEST, WALKTHROUGH, WALKTHROUGH_NO_ACTIONS, board, branch,
                          commit, git, make_repo, preflight, write)


def main() -> int:
    c = Cases("task_preflight")

    # ── THE load-bearing negative: deployable code cannot ride the task lane ──
    if c.block("THE load-bearing negative: deployable code cannot ride the task "):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-thing", {"backend/app.py": "x = 2\n"})
            code, out = preflight(repo)
            c.check("deployable diff -> HANDOFF", "LANE: HANDOFF" in out, out.strip()[-200:])
            c.check("deployable diff -> exit 2", code == 2, f"exit {code}")
            c.check("handoff names /cicd-push-e2e", "/cicd-push-e2e" in out)
            c.check("handoff names the offending dir", "backend/" in out)

        # A deploy dir touched only on ANOTHER path must still not be reachable by prefix luck:
        # `backendless/` starts with neither `backend/` nor any other deploy dir.
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-thing", {"backendless/notes.md": "hi\n"})
            code, out = preflight(repo)
            c.check("`backendless/` is not `backend/`", "LANE: LOCAL" in out, out.strip()[-200:])

    # ── Same repo, same command, docs-only diff: the gate must NOT be "always stop" ──
    if c.block("Same repo, same command, docs-only diff: the gate must NOT be 'a"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-thing", {".agents/rules/x.md": "rule\n"})
            code, out = preflight(repo)
            c.check("docs-only diff in a deploying repo -> LOCAL", "LANE: LOCAL" in out)
            c.check("docs-only diff -> exit 0", code == 0, out.strip()[-300:])
            c.check("says the deploy gate cannot be affected",
                    "touches none of them" in out, out.strip()[-300:])

    # ── SCC-118: `.github/` is a deploy surface only where something SHIPS ────────────
    if c.block("SCC-118: `.github/` is a deploy surface only where something SHI"):
        # The regression, first. Before this split the command centre had no `.github/` at all,
        # so one list served both questions and nothing could tell. SCC-118 gave it one — the
        # server-side half of the main write gate — and the next close-out here was refused as
        # "NOT task-lane work" and routed to /cicd-push-e2e: a command that binds a PROJECT,
        # refuses the lobby, and gates on an E2E suite this repo does not have. Unfollowable.
        with TempDir() as t:
            repo = make_repo(t, deployable=False, ci=True)
            branch(repo, "chore/SCC-11-thing", {".github/workflows/gate.yml": "name: gate2\n"})
            code, out = preflight(repo)
            c.check("CI-only repo touching .github/ -> LOCAL", "LANE: LOCAL" in out,
                    out.strip()[-300:])
            c.check("CI-only repo touching .github/ -> exit 0", code == 0, out.strip()[-300:])
            c.check("and it says WHY: nothing here deploys",
                    "no deployable surface" in out, out.strip()[-300:])
            c.check("it does NOT route to a command that refuses this repo",
                    "/cicd-push-e2e" not in out, out.strip()[-300:])

        # ⛔ THE CONTROL THAT MAKES THE NARROWING DEFENSIBLE. Assert only the case above and you
        # have proved the softening and not the strictness. Where a product exists, `.github/`
        # is deployable exactly as before — a workflow edit there can change WHAT ships.
        with TempDir() as t:
            repo = make_repo(t, deployable=True, ci=True)
            branch(repo, "chore/SCC-11-thing", {".github/workflows/gate.yml": "name: gate2\n"})
            code, out = preflight(repo)
            c.check("CONTROL a product repo touching .github/ still HANDOFFs",
                    "LANE: HANDOFF" in out, out.strip()[-300:])
            c.check("CONTROL that handoff is still a hard exit 2", code == 2, f"exit {code}")
            c.check("CONTROL it still names .github/ as the offender",
                    ".github/" in out, out.strip()[-300:])

        # And the other half of the product case is untouched: a product repo whose diff stays
        # clear of every deploy dir is still LOCAL, with `.github/` present.
        with TempDir() as t:
            repo = make_repo(t, deployable=True, ci=True)
            branch(repo, "chore/SCC-11-thing", {".agents/rules/x.md": "rule\n"})
            code, out = preflight(repo)
            c.check("CONTROL product repo + CI, docs-only diff -> LOCAL", "LANE: LOCAL" in out,
                    out.strip()[-300:])

    # ── The command centre: no deployable surface at all ──
    if c.block("The command centre: no deployable surface at all"):
        with TempDir() as t:
            repo = make_repo(t, deployable=False)
            branch(repo, "chore/SCC-11-thing", {".agents/commands/x.md": "cmd\n"})
            code, out = preflight(repo)
            c.check("no deployable surface -> LOCAL", "LANE: LOCAL" in out)
            c.check("no deployable surface -> exit 0 (positive control)", code == 0,
                    out.strip()[-300:])
            c.check("says why there is no E2E to skip",
                    "no deployable surface" in out, out.strip()[-300:])
            c.check("gate plan names the enforcement suite",
                    "run_all.py" in out, out.strip()[-300:])

    # ── Wrong lane: each refusal must name the command that IS right ──
    if c.block("Wrong lane: each refusal must name the command that IS right"):
        for name, expect in (("epic/SCC-11-thing", "/cicd-push-e2e"),
                             ("claude/SCC-11-thing", "/cicd-close-story-merge-tree")):
            with TempDir() as t:
                repo = make_repo(t)
                branch(repo, name, {"docs/x.md": "x\n"})
                code, out = preflight(repo)
                c.check(f"{name.split('/')[0]}/ branch refused", code == 2, f"exit {code}")
                c.check(f"{name.split('/')[0]}/ refusal names {expect}", expect in out)

        # ── SCC-148: the REAL incident branch. `/cicd-mobile-error-team` writes ONLY
        # `claude/incident-<short-id-lower>` — no command anywhere creates a bare `incident/`
        # branch. The old table scanned `claude/` first, so a live incident branch was refused
        # with instructions to run the STORY close-out — the wrong command, told confidently,
        # on the one path that runs under production pressure, often from a phone. The refusal
        # must name the incident lane and must NOT name the story close-out anywhere.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "claude/incident-abc123", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-148 claude/incident-* (the real shape) is refused", code == 2,
                    f"exit {code}")
            c.check("SCC-148 ...naming /cicd-mobile-error-team, never the story close-out",
                    "/cicd-mobile-error-team" in out
                    and "/cicd-close-story-merge-tree" not in out,
                    out.strip()[-300:])

        # ── SCC-148: WRONG_LANE table integrity. An entry can die two ways, and each gets its
        # own guard because each is blind to the other:
        #   * dead-by-nonexistence — a prefix no command creates (the old bare `incident/`).
        #     The key-set pin catches it; an order check cannot.
        #   * dead-by-shadowing — the scan is first-match `startswith` over insertion order, so
        #     a generic prefix listed before a specific one makes the specific entry unreachable
        #     (the actual SCC-148 bug: `claude/` before `claude/incident-`). The shadow check
        #     catches ANY entry hidden behind an earlier generic prefix — a set pin is
        #     order-blind, and order is exactly what a future alphabetical "tidy" would break.
        import task_preflight as _tp
        lane_keys = list(_tp.WRONG_LANE)
        c.check("SCC-148 WRONG_LANE holds exactly the prefixes real commands create",
                set(lane_keys) == {"epic/", "claude/incident-", "claude/"},
                f"got {sorted(lane_keys)}")
        shadowed = [(a, b) for i, a in enumerate(lane_keys) for b in lane_keys[i + 1:]
                    if b.startswith(a)]
        c.check("SCC-148 no WRONG_LANE entry is shadowed by an earlier prefix (first-match scan)",
                not shadowed, f"unreachable: {shadowed}")

        # ── SCC-148 sweep survivor: the scan must be ANCHORED at position 0, not a substring
        # search. `BRANCH_RE`'s slug group is `.+`, which matches slashes, so a chore branch
        # embedding a lane word mid-name is git-legal AND shape-legal — and a `prefix in branch`
        # scan (mutant M4, which survived the first sweep with zero failing cases) would
        # wrong-lane it to /cicd-push-e2e. It is a chore branch and must never be refused as
        # someone else's lane.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-docs-for-epic/pages", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            # Both halves on purpose (review): the negatives alone would score green over a
            # crashed run, whose traceback contains neither pinned string — so the case also
            # pins the POSITIVE marker check_branch prints only after the branch survives the
            # lane scan and matches BRANCH_RE. This fixture is the only slash-in-slug shape,
            # so no other case would catch a scan crash here.
            c.check("SCC-148 a chore slug embedding a lane word is not wrong-laned (anchored scan)",
                    "is not a task branch" not in out and "/cicd-push-e2e" not in out
                    and "-> SCC-11" in out and code in (0, 1),
                    f"exit {code}: " + out.strip()[-300:])

        # ── Review: the bare `incident/` shape lost its WRONG_LANE entry (dead code — nothing
        # creates it), so its behavior is now the generic shape refusal. Pinned so the close-out
        # command's check-table claim about this fall-through has a machine behind it, and so
        # any future drift in what an unclassifiable branch gets told is visible.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "incident/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-148 bare incident/ (no creator) falls to the generic shape refusal",
                    code == 2 and "the key must sit" in out
                    and "/cicd-mobile-error-team" not in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:
            repo = make_repo(t)
            code, out = preflight(repo, "--branch", "main")
            c.check("standing on main is refused", code == 2 and "never runs standing on main" in out,
                    out.strip()[-200:])

    # ── Branch shape: the key must sit immediately after the prefix ──
    if c.block("Branch shape: the key must sit immediately after the prefix"):
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/fix-SCC-11", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("`chore/fix-SCC-11` refused (key not after the prefix)",
                    code == 2 and "immediately after the prefix" in out, out.strip()[-200:])

        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/AVCH-3-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("wrong-project key refused", code == 2 and "not one of this repo's projects" in out,
                    out.strip()[-200:])

    # ── Clean + pushed + current ──
    if c.block("Clean + pushed + current"):
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            write(repo, "docs/uncommitted.md", "dirty\n")
            code, out = preflight(repo)
            c.check("dirty tree blocks", code == 2 and "uncommitted change" in out,
                    out.strip()[-200:])

        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"}, push=False)
            code, out = preflight(repo)
            c.check("never-pushed branch warns", "never pushed" in out, out.strip()[-200:])

        # ── SCC-159 · THE STALLED LANDING ────────────────────────────────────────────────
        # Every check in this script asks about the LANE. None asked whether the DESTINATION
        # was itself unpushed — and local `main` ahead of `origin/main` is exactly that: an
        # earlier lane merged and never landed. Every lane behind it then queues invisibly
        # (it happened live 2026-08-14, for about an hour), and the close-out's own
        # `pull --ff-only` cannot catch it: that succeeds silently when local is merely
        # AHEAD, so the next lane merges cleanly onto the stuck main and reports success.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "checkout", "-q", "main")
            write(repo, "docs/stalled.md", "an earlier lane that never landed\n")
            commit(repo, "SCC-11 merge: an earlier lane (never pushed)")
            git(repo, "checkout", "-q", "chore/SCC-11-thing")
            git(repo, "merge", "-q", "--no-ff", "-m", "SCC-11 chore: absorb main", "main")
            # Push the LANE, so the only thing wrong with this fixture is the stalled main.
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo, "--fetch")
            c.check("SCC-159 local main ahead of origin/main BLOCKS the close-out",
                    code == 2 and "main is 1 commit(s) ahead of origin/main" in out,
                    out.strip()[-400:])
            c.check("SCC-159 ...and names it a stalled landing, with the remedy",
                    "STALLED LANDING" in out and "git push origin main" in out,
                    out.strip()[-400:])
            c.check("SCC-159 ...and names the flag that overrides it",
                    "--accept-unpushed-main" in out, out.strip()[-400:])

            # The offline exit. Reads pass and pushes die on the operator's satellite uplink,
            # so a hard refusal with no auditable way through would brick every close-out
            # made from a plane. The flag is typed per invocation and prints itself back.
            code, out = preflight(repo, "--fetch", "--accept-unpushed-main")
            c.check("SCC-159 --accept-unpushed-main downgrades it to a warning",
                    code != 2 and "main is 1 commit(s) ahead of origin/main" in out,
                    out.strip()[-400:])
            c.check("SCC-159 ...and the override is stated in the output, not silent",
                    "accepted by --accept-unpushed-main" in out, out.strip()[-400:])

            # ⭐ THE SEVERITY SPLIT, and it had NO case until a width mutant survived: without
            # a fresh fetch the comparison is only as good as the last one, which on a plane is
            # nothing — so it may WARN and must not hard-refuse. Hardening this to an error
            # would brick every offline close-out for a question that was never asked freshly.
            #
            # ⛔ SCC-193: THE FLAG MOVED, THE PROPERTY DID NOT. This said `preflight(repo)` and
            # meant "no fetch happened" — true while --fetch was opt-in, and the exact opposite
            # now that it is the default. Left as it was, the case would assert that a lane
            # measured against a FRESH fetch only warns about a stalled main, which is the one
            # reading SCC-159 rules out (fresh evidence is an ERROR). `--no-fetch` is how the
            # not-fresh half is spelled now; the assertions below are untouched.
            code, out = preflight(repo, "--no-fetch")
            c.check("SCC-159 with --no-fetch the stalled landing only WARNS",
                    code != 2 and "main is 1 commit(s) ahead of origin/main" in out,
                    out.strip()[-400:])
            c.check("SCC-159 ...and says the comparison is against the last fetch",
                    "vs the LAST fetch" in out, out.strip()[-400:])

        with TempDir() as t:
            # ⭐ THE FALSE-RED CONTROL. main level with origin ⇒ silence: a check that fires on
            # the normal case is one every close-out learns to read past.
            #
            # ⛔ THE ASSERTION IS `.lower()` ON PURPOSE (SCC-156 review, Blind Hunter). It read
            # `"stalled landing" not in out` while the message says "a STALLED LANDING:" in
            # caps — so the string half was a TAUTOLOGY, absent whether or not the check fired,
            # and only `code == 0` carried any evidence. A mutant that emits the message at
            # rep.info severity (exit stays 0) passed this control unchanged. The sibling file
            # `test_git_hooks.py` already did this correctly with `not in out.lower()`; this is
            # the same lane committing the vacuous-guard error its own rule file bans, one
            # block away from where it fixed it.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo, "--fetch")
            c.check("SCC-159 control: main level with origin/main is CLEAR and silent",
                    code == 0 and "stalled landing" not in out.lower(), out.strip()[-300:])

    # ── SCC-156 review · THE STALLED LANDING'S FOUR UNCOVERED STATES ─────────────────────
    # Its own block, for two reasons. The review found `--case "SCC-159"` matched 0/20 blocks
    # (the fixtures lived inside "Clean + pushed + current", so citing them by name was
    # impossible — exactly what the assertion-evidence row now demands). And every case here
    # exists because a lens proved the shipped code wrong on a state no fixture reached.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            # main moves on AFTER the branch was cut: the branch is now stale.
            git(repo, "checkout", "-q", "main")
            write(repo, "docs/hotfix.md", "later\n")
            commit(repo, "SCC-11 chore: hotfix on main")
            git(repo, "push", "-q", "origin", "main")
            git(repo, "checkout", "-q", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("un-absorbed main blocks", code == 2 and "NOT on" in out, out.strip()[-300:])
            c.check("un-absorbed main says merge it here first",
                    "conflicts surface here, not on main" in out, out.strip()[-300:])
            # SCC-41: being behind is routine; being behind ON A FILE YOU EDITED is the part that
            # costs a session. main moved on docs/hotfix.md, the branch owns docs/x.md - disjoint.
            c.check("SCC-41 no overlap is stated, not left silent",
                    "no file overlap" in out and "should be clean" in out, out.strip()[-400:])
            c.check("SCC-41 a clean-absorb case does not cry conflict",
                    "changed on BOTH sides" not in out, out.strip()[-400:])

        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/shared.md": "mine\n"})
            # Same file edited on both sides - the ONE case worth naming out loud.
            git(repo, "checkout", "-q", "main")
            write(repo, "docs/shared.md", "theirs\n")
            commit(repo, "SCC-11 chore: another lane edits the same file")
            git(repo, "push", "-q", "origin", "main")
            git(repo, "checkout", "-q", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-41 an overlapping file is NAMED",
                    "changed on BOTH sides" in out and "docs/shared.md" in out, out.strip()[-400:])
            c.check("SCC-41 the overlap tells you how to resolve it",
                    "keeping both sides' facts" in out, out.strip()[-400:])

        with TempDir() as t:
            repo = make_repo(t)
            git(repo, "checkout", "-q", "-b", "chore/SCC-11-thing")
            git(repo, "push", "-q", "-u", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("zero commits ahead blocks", code == 2 and "nothing to merge" in out,
                    out.strip()[-300:])

    # ── The walkthrough the Dev Record will point at ──
    if c.block("SCC-159 · the STALLED LANDING — divergence, behind, no-origin, dead fetch"):
        with TempDir() as t:
            # ⛔ DIVERGED, not stalled. `behind, ahead = ...` computed both and read only
            # `ahead`, so behind=N/ahead=M printed "an earlier lane merged and never reached
            # the remote" and prescribed `git push origin main` — which git REJECTS
            # non-fast-forward. The docstring's own justification ("`pull --ff-only` will NOT
            # catch this") is false here: divergence is the one case it DOES catch.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            # origin/main moves (a merge landed on the server, e.g. via main_write_gate)...
            git(repo, "checkout", "-q", "main")
            write(repo, "docs/theirs.md", "landed on the server\n")
            commit(repo, "SCC-11 chore: a commit that reached origin")
            git(repo, "push", "-q", "origin", "main")
            git(repo, "reset", "-q", "--hard", "HEAD~1")
            # ...while local main grows its own unpushed commit. Now: 1 behind, 1 ahead.
            write(repo, "docs/mine.md", "never pushed\n")
            commit(repo, "SCC-11 merge: a local landing that never went out")
            git(repo, "checkout", "-q", "chore/SCC-11-thing")
            git(repo, "merge", "-q", "--no-ff", "-m", "SCC-11 chore: absorb main", "main")
            git(repo, "push", "-q", "-f", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo, "--fetch")
            c.check("SCC-159 R1 a DIVERGED main is named as diverged, not as a stalled landing",
                    "DIVERGED" in out and "never reached the remote" not in out,
                    out.strip()[-500:])
            # The property, not the literal. `git push origin main` legitimately APPEARS in
            # the diverged message — saying "that push is rejected non-fast-forward" is the
            # point. What must not appear is the stalled-landing PRESCRIPTION, `Land it (...)`,
            # which is the sentence that sends the operator into the error.
            c.check("SCC-159 R1 ...and does NOT prescribe a push git would reject",
                    "Land it (`git push origin main`)" not in out
                    and "rejected non-fast-forward" in out, out.strip()[-500:])

        with TempDir() as t:
            # BEHIND ONLY — the commonest real state (a sibling landed, you have not pulled).
            # `if ahead == "0"` fired the all-clear, so this printed "main is level with
            # origin/main" while rev-list said `1  0`. An INFO line asserting the opposite of
            # the truth is the false-read this check exists to prevent.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "checkout", "-q", "main")
            write(repo, "docs/theirs.md", "a sibling landed\n")
            commit(repo, "SCC-11 chore: sibling landing")
            git(repo, "push", "-q", "origin", "main")
            git(repo, "reset", "-q", "--hard", "HEAD~1")
            git(repo, "checkout", "-q", "chore/SCC-11-thing")
            code, out = preflight(repo, "--fetch")
            c.check("SCC-159 R2 main merely BEHIND is not reported as level with origin/main",
                    "level with origin/main" not in out, out.strip()[-500:])

        with TempDir() as t:
            # NO origin/main at all. `rev-list origin/main...main` fails, but the `["?", "?"]`
            # padding is never the string "0", so the ahead-check fell through and a local-only
            # repo was told it was "? commit(s) ahead of origin/main" — an err under --fetch,
            # i.e. a close-out refused on a nonsense diagnosis.
            repo = make_repo(t, remote=False)
            code, out = preflight(repo, "--fetch")
            c.check("SCC-159 R3 a repo with no origin/main is not accused of a stalled landing",
                    "STALLED LANDING" not in out and "? commit" not in out, out.strip()[-500:])

        with TempDir() as t:
            # ⭐ THE FETCH THAT FAILED. Three lenses found this independently. The docstring
            # says the severity split is about EVIDENCE QUALITY — "no `--fetch`, OR A FETCH
            # THAT FAILED ... can only WARN" — but the code was handed `args.fetch`, the FLAG,
            # so a dead uplink produced a hard ERROR on a comparison the previous check had
            # just warned was stale. That is the offline operator hard-blocked on a phantom:
            # the precise case the split exists to protect, broken by keying on intent
            # instead of outcome.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "checkout", "-q", "main")
            write(repo, "docs/stalled.md", "never landed\n")
            commit(repo, "SCC-11 merge: an earlier lane (never pushed)")
            git(repo, "checkout", "-q", "chore/SCC-11-thing")
            git(repo, "merge", "-q", "--no-ff", "-m", "SCC-11 chore: absorb main", "main")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            # Kill the uplink the way a plane does: the remote URL still resolves as a path,
            # and there is nothing there.
            git(repo, "remote", "set-url", "origin", str(t / "no-such-remote.git"))
            code, out = preflight(repo, "--fetch")
            c.check("SCC-159 R4 a FAILED --fetch warns, never hard-errors, on the landing check",
                    "fetch failed" in out and "[ERROR] landing" not in out, out.strip()[-600:])
            c.check("SCC-159 R4 ...and says the comparison is only as good as the last fetch",
                    "vs the LAST fetch" in out, out.strip()[-600:])

    if c.block("The walkthrough the Dev Record will point at"):
        # Two ways it can be absent, and BOTH are errors. "No `_artifacts/` tree at all" is the
        # strongest evidence the walkthrough was never written - reporting that as a warning is
        # how the check would go quiet on exactly the repo that needed it.
        with TempDir() as t:
            # manifest=False too: the case IS "no _artifacts/ tree at all", and the default
            # task.yaml fixture would create the tree this check looks for.
            repo = make_repo(t, walkthrough=False, manifest=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("no _artifacts/ tree blocks (not a warning)",
                    code == 2 and "no _artifacts/ tree" in out, out.strip()[-300:])

        with TempDir() as t:
            repo = make_repo(t, walkthrough=False)
            write(repo, "_artifacts/_main/2026-08-08_other/walkthrough.md",
                  "# SCC-99 — something else\n")
            commit(repo, "SCC-11 chore: other walkthrough")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("a walkthrough for a DIFFERENT key does not count",
                    code == 2 and "no walkthrough.md mentions SCC-11" in out, out.strip()[-300:])

        # ── ⛔ SCC-155 review #22: the section `finish` REQUIRES, checked BEFORE the merge ──
        # `jira_feed.py finish` refuses (exit 2) on a walkthrough with no `## Your Actions`,
        # and the close-out runs it at Step 4 - AFTER the merge has landed. Preflight already
        # demands the walkthrough; demanding its section costs one read and moves an existing
        # hard failure to the one point where it is still cheap to fix. It ships ARMED because
        # it is not a new gate: it is the same refusal, earlier, so nothing that passes the
        # close-out today starts failing here.
        with TempDir() as t:
            repo = make_repo(t, walkthrough=False)
            write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/walkthrough.md",
                  WALKTHROUGH_NO_ACTIONS)
            commit(repo, "SCC-11 chore: walkthrough with no Your Actions")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("#22 a walkthrough with no `## Your Actions` blocks at PREFLIGHT",
                    code == 2 and "Your Actions" in out, out.strip()[-300:])
            c.check("#22 and it names finish as the reason, not a style preference",
                    "finish" in out, out.strip()[-300:])

        # Found by CONTENT, not just by folder name - a walkthrough filed under a date-slug
        # folder that does not carry the key is the normal shape in this repo.
        with TempDir() as t:
            repo = make_repo(t, walkthrough=False)
            write(repo, "_artifacts/_main/2026-08-08_some-slug/walkthrough.md", WALKTHROUGH)
            commit(repo, "SCC-11 chore: walkthrough")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("walkthrough found by content, not folder name", code == 0, out.strip()[-300:])

        # ── SCC-38 review: the key is matched against the walkthrough's path RELATIVE to
        # `_artifacts/`, never the absolute path. A worktree named after its key
        # (`.claude/worktrees/scc-11-lane/`) put the key into EVERY walkthrough's absolute
        # path, so every walkthrough in the repo became a "hit" and 35 historic ones without
        # `## Your Actions` blocked an unrelated lane's merge. Found live, on the first lane
        # whose worktree carried its key.
        with TempDir() as t:
            repo = make_repo(t / "scc-11-lane", walkthrough=False)      # the KEY is in the path
            write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/walkthrough.md", WALKTHROUGH)
            write(repo, "_artifacts/_main/2026-08-01_scc-99-other/walkthrough.md",
                  "# SCC-99 - something else, no actions section\n")
            commit(repo, "SCC-11 chore: two walkthroughs")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("a worktree/dir NAMED with the key does not make every walkthrough a hit",
                    code == 0 and "scc-99-other" not in out, out.strip()[-300:])

    # ── Regression: the MAIN checkout is not "a worktree holding your branch" ──
    if c.block("Regression: the MAIN checkout is not 'a worktree holding your br"):
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("main checkout does not trigger the worktree warning",
                    "is checked out on" not in out, out.strip()[-300:])
            c.check("clean task branch -> exit 0 (positive control)", code == 0, out.strip()[-300:])
            c.check("SCC-110 an ARMED repo still says GATES: ARMED", "GATES: ARMED" in out,
                    out.strip()[-300:])

    # ── SCC-119 · a parent does not close while its subtasks are open ────────────────────
    if c.block("SCC-119 · a parent does not close while its subtasks are open"):
        # The whole job closes together at the end (operator ruling): each subtask lands its own
        # branch as it finishes, and the PARENT is what closes last. Nothing mechanical enforced
        # that before - a parent could go Done over five open children and the board would read
        # as finished work.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})

            board(t, children=[("SCC-20", "Done"), ("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("open subtask BLOCKS the parent close",
                    code == 2 and "SCC-21" in out and "open subtask" in out, out.strip()[-400:])
            c.check("the block names the finished child too, so the state is readable",
                    "SCC-20" not in out.split("open subtask")[1][:200], out.strip()[-400:])

            # ⭐ THE escape hatch, and the reason it is not a --force flag: a gate with no
            # legitimate exit gets --no-verify'd. Descoping through `Deferred` leaves a trail.
            board(t, children=[("SCC-20", "Done"), ("SCC-21", "Deferred")])
            code, out = preflight(repo)
            c.check("a Deferred child does NOT block - descoping is the auditable escape",
                    code == 0 and "clear to close out and merge" in out, out.strip()[-400:])

            board(t, children=[("SCC-20", "Done"), ("SCC-21", "Done")])
            code, out = preflight(repo)
            c.check("all children Done -> the parent is clear to close last",
                    code == 0 and "last thing to close" in out, out.strip()[-400:])

            board(t, children=[])
            code, out = preflight(repo)
            c.check("a childless ticket passes for the RIGHT reason, not by accident",
                    code == 0 and "no subtasks" in out, out.strip()[-400:])

            # ⛔ THE load-bearing negative. A failed query and a childless parent BOTH return zero
            # rows - measured on the live board 2026-08-12: `parent = <bad key>` exits 1 with no
            # rows, exactly like a real childless parent exits 0 with no rows. A gate that counted
            # rows would read "the key was wrong" as "nothing is open" and wave the close through.
            board(t, children=[("SCC-21", "In Progress")], fail=True)
            code, out = preflight(repo)
            c.check("a FAILED query is never read as 'no children' (exit code, not row count)",
                    "NOT checked" in out, out.strip()[-400:])
            c.check("...and it says transport, not a verdict - the operator must not mint or "
                    "assume anything from it",
                    "transport, not a verdict" in out, out.strip()[-400:])

            # The deliberate divergence from the plan, pinned so it cannot drift back silently:
            # an unreachable board WARNS and does not flip the headline. Sandboxed agent shells
            # cannot reach the credential store at all, so blocking here would make "NOT CLEAR"
            # the normal output and stop it meaning anything. /smh-close-task-merge-tree
            # re-asserts this with the board in hand, immediately before it writes `Done`.
            c.check("an unreachable board warns (exit 1) rather than blocking (exit 2)",
                    code == 1, f"exit {code}: " + out.strip()[-300:])

    # ── SCC-156 · riders: a subtask worked in THIS lane rides its close ──────────────────
    if c.block("SCC-156 · riders: a subtask worked in THIS lane rides its close"):
        # The hole, measured on this ticket's own close-out: SCC-159's work landed in
        # SCC-156's lane by the operator's explicit one-lane ruling, so at close-out the
        # child was still `In Progress` - and check_children read the DESIGNED state as "the
        # job is not done", BLOCKED, and the agent handed the operator a manual Jira edit.
        # `riders:` is the manifest declaring that state up front; the close ceremony
        # transitions riders to Done FIRST, parent LAST - agent writes, every one. A flow
        # that leaves the operator a board edit is broken by definition (operator ruling,
        # 2026-08-14).
        def declare(repo, riders_line):
            # On the BRANCH: task_manifests() reads the working tree, and the preflight
            # demands a clean, pushed one - so declare, commit, push.
            write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml",
                  MANIFEST + riders_line)
            commit(repo, "SCC-11 chore: declare riders")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")

        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            declare(repo, "riders: [SCC-21]\n")
            board(t, children=[("SCC-20", "Done"), ("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("a DECLARED rider does not block its own lane's close (warn, not error)",
                    code == 1 and "clear to close out and merge" in out,
                    f"exit {code}: " + out.strip()[-500:])
            c.check("...and the warn IS the ceremony's instruction, command included",
                    'acli jira workitem transition --key SCC-21 --status "Done" --yes' in out,
                    out.strip()[-500:])
            c.check("...named as an agent step - never an operator edit",
                    "never an operator edit" in out, out.strip()[-500:])
            c.check("...and the info line does not claim the board is further along than "
                    "it is", "are Done or Deferred -" not in out
                    and "rider(s) above are the ceremony's to close" in out,
                    out.strip()[-500:])

        with TempDir() as t:
            # An UNDECLARED open child still blocks - and the error now teaches the third
            # exit: the exact riders: line to write when the work genuinely rode this lane.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            board(t, children=[("SCC-20", "Done"), ("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("an undeclared open child still BLOCKS - riders never weaken the default",
                    code == 2 and "open subtask" in out, f"exit {code}: " + out.strip()[-400:])
            c.check("...and the error hands over the exact declaration line",
                    "riders: [SCC-21]" in out, out.strip()[-500:])
            c.check("...with the guard sentence that polices it",
                    "work is not real" in out, out.strip()[-500:])

        with TempDir() as t:
            # A declared rider next to an undeclared open sibling: the block stands, the
            # error's open-list names ONLY the undeclared child, and the suggested line is
            # the COMPLETE corrected declaration - a copy-paste must never clobber riders
            # already declared.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            declare(repo, "riders: [SCC-21]\n")
            board(t, children=[("SCC-21", "In Progress"), ("SCC-23", "In Progress")])
            code, out = preflight(repo)
            segment = out.split("whole job is done:")[1].split(".")[0] if \
                "whole job is done:" in out else "(no error fired)"
            c.check("a rider does not spare its undeclared SIBLING", code == 2,
                    f"exit {code}: " + out.strip()[-400:])
            c.check("...the open-list names the undeclared child only",
                    "SCC-23" in segment and "SCC-21" not in segment, segment)
            c.check("...and the suggested line is the COMPLETE declaration, rider kept",
                    "riders: [SCC-21, SCC-23]" in out, out.strip()[-500:])

        with TempDir() as t:
            # A rider that is already Done needs no instruction - the ceremony re-run after
            # the flip must read quiet, or the warn becomes noise that never clears.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            declare(repo, "riders: [SCC-21]\n")
            board(t, children=[("SCC-21", "Done")])
            code, out = preflight(repo)
            # "transition --key", not the full command phrase: the yes-guard sweeps every
            # .agents/ line mentioning the transition verb for `--yes`, and an absence
            # assertion must not read as an un-flagged call site.
            c.check("a rider already Done raises no instruction (control: fires only while "
                    "open)", code == 0 and "transition --key" not in out
                    and "declared RIDER" not in out,
                    f"exit {code}: " + out.strip()[-400:])
            c.check("...and the normal all-closed info stands", "last thing to close" in out,
                    out.strip()[-300:])

        with TempDir() as t:
            # Exact-key matching, the SCC-146 lesson re-applied: SCC-2 declared must not
            # spare SCC-21 by prefix. The complete-line suggestion carries BOTH - the
            # machine cannot know a declared key is a typo, so it keeps it and lets the
            # guard sentence police the edit.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            declare(repo, "riders: [SCC-2]\n")
            board(t, children=[("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("rider matching is EXACT - SCC-2 does not spare SCC-21", code == 2,
                    f"exit {code}: " + out.strip()[-400:])
            c.check("...and the suggestion keeps the declared key beside the missing one",
                    "riders: [SCC-2, SCC-21]" in out, out.strip()[-500:])

        with TempDir() as t:
            # ⛔ The YAML-habituated trap: block-form riders. The hand parser reads the
            # same-line [flow] form ONLY, so a block list is an UNREAD declaration - and an
            # unread declaration must fail CLOSED (still blocks) with the flow form in hand,
            # never silently pass. If block parsing is ever implemented, this case goes red
            # and the rewrite is a decision, not drift.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            declare(repo, "riders:\n  - SCC-21\n")
            board(t, children=[("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("block-form riders is UNREAD and fails CLOSED - the gate still blocks",
                    code == 2, f"exit {code}: " + out.strip()[-400:])
            c.check("...with the flow-form line to write instead",
                    "riders: [SCC-21]" in out, out.strip()[-500:])

        with TempDir() as t:
            # A COMMENT quoting the syntax is not a declaration (the comment-literals class:
            # prose about a gate must never satisfy it). RIDERS_RE's `^\s*` anchor is what
            # makes this true - this case is that anchor's killer.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            declare(repo, "# declare like this: riders: [SCC-21]\n")
            board(t, children=[("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("a COMMENT quoting riders syntax declares nothing - the gate still "
                    "blocks", code == 2, f"exit {code}: " + out.strip()[-400:])

        with TempDir() as t:
            # Key normalization: a lowercase declaration still spares - both sides of the
            # membership test are upper-cased by their builders.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            declare(repo, "riders: [scc-21]\n")
            board(t, children=[("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("a lowercase rider declaration still spares its child",
                    code == 1 and "clear to close out and merge" in out,
                    f"exit {code}: " + out.strip()[-400:])

        with TempDir() as t:
            # A landed sibling lane's manifest is HISTORY (manifest_settled): its riders were
            # flipped at ITS close, so inheriting the declaration would spare a child no one
            # is carrying. Settled = recorded on the mainline blob-for-blob AND declaring
            # another branch - built here exactly like check_manifest's own settled path.
            repo = make_repo(t)
            write(repo, "_artifacts/_main/2026-08-01_scc-11-other/task.yaml",
                  "task_key: SCC-11\nprimary_repo: repo\nbranch: chore/SCC-11-OTHER\n"
                  "close_command: smh-close-task-merge-tree\nriders: [SCC-21]\n")
            commit(repo, "SCC-11 chore: a landed sibling lane's receipt")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            board(t, children=[("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("a landed sibling's riders are HISTORY - they spare nothing here",
                    code == 2, f"exit {code}: " + out.strip()[-400:])

    # ── SCC-170 · partial landing: a consolidated lane may ship before every part ────────
    if c.block("SCC-170 partial landing: a consolidated lane ships before every "):
        # SCC-164's lane carries thirteen subtasks on one branch (the operator's consolidation
        # ruling, 2026-08-15). If it must land before every part is built, the riders that DID
        # land flip, the parent STAYS OPEN, and the rest becomes the next lane - but
        # check_children could not express that: an open child that is not a declared rider
        # blocks, full stop, so the only way to land early was to declare children whose work
        # is NOT in the diff. That is precisely what the rider guard sentence forbids ("never
        # declare a ticket whose work is not real"), so the gate was pushing the lane into the
        # lie it exists to prevent.
        #
        # `landing_mode: partial` is the manifest saying so out loud. It only ever downgrades the
        # UNDECLARED-child error to a warn; it never touches what a rider means, and it earns
        # that downgrade by paying for it below - every declared rider must have real work on
        # the lane, checked against the commits.
        def declare_manifest(repo, extra, *, msg="SCC-11 chore: declare"):
            write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml", MANIFEST + extra)
            commit(repo, msg)
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")

        with TempDir() as t:
            # THE case. Declared rider SCC-21 rode this lane; SCC-23 did not and stays open.
            # `landing_mode: partial` -> warn + proceed, and the warn must name the child that is
            # being left behind, because the walkthrough has to carry it to the next lane.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "commit", "--no-verify", "-q", "--allow-empty",
                "-m", "SCC-21 fix(thing): the rider's own work")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            declare_manifest(repo, "riders: [SCC-21]\nlanding_mode: partial\n")
            board(t, children=[("SCC-21", "In Progress"), ("SCC-23", "To Do")])
            code, out = preflight(repo)
            c.check("`landing_mode: partial` lets a consolidated lane land with an undeclared "
                    "child still open (warn, not error)",
                    code == 1 and "clear to close out and merge" in out,
                    f"exit {code}: " + out.strip()[-600:])
            c.check("...and it NAMES the child being left behind, so the walkthrough can "
                    "hand it to the next lane", "SCC-23" in out, out.strip()[-600:])
            c.check("...and it says the parent stays OPEN - a partial landing never closes "
                    "the index", "parent stays open" in out.lower(), out.strip()[-600:])
            c.check("...the rider still gets its ceremony transition line",
                    'transition --key SCC-21 --status "Done" --yes' in out,
                    out.strip()[-600:])

        with TempDir() as t:
            # ⛔ THE CONTROL that makes the downgrade defensible: without the declaration the
            # SAME fixture still BLOCKS. Partial landing is a thing you say, never a default.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "commit", "--no-verify", "-q", "--allow-empty",
                "-m", "SCC-21 fix(thing): the rider's own work")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            declare_manifest(repo, "riders: [SCC-21]\n")
            board(t, children=[("SCC-21", "In Progress"), ("SCC-23", "To Do")])
            code, out = preflight(repo)
            c.check("CONTROL no `landing_mode:` line -> the undeclared child still BLOCKS",
                    code == 2 and "open subtask" in out, f"exit {code}: " + out.strip()[-400:])

        with TempDir() as t:
            # The price of the downgrade, and the reason it cannot be abused: a declared rider
            # with NO commit on the lane is a declaration error - exit 2 naming it. Without
            # this, `landing_mode: partial` would be a way to declare thirteen riders, land two, and
            # flip all thirteen to Done at the ceremony. Checked against the COMMITS on the
            # lane, not against belief.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            declare_manifest(repo, "riders: [SCC-21, SCC-22]\nlanding_mode: partial\n")
            board(t, children=[("SCC-21", "In Progress"), ("SCC-22", "To Do")])
            code, out = preflight(repo)
            c.check("a declared rider with NO commit on the lane is a declaration error",
                    code == 2, f"exit {code}: " + out.strip()[-600:])
            c.check("...and it names the rider that declared work it never did",
                    "SCC-21" in out and "SCC-22" in out, out.strip()[-600:])
            c.check("...quoting the guard sentence the riders error already teaches",
                    "work is not real" in out, out.strip()[-600:])

        with TempDir() as t:
            # CONTROL for the check above: riders that DID commit on the lane pass it, so the
            # trimmed-riders check is not simply "partial always fails".
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            for k in ("SCC-21", "SCC-22"):
                git(repo, "commit", "--no-verify", "-q", "--allow-empty",
                    "-m", f"{k} fix(thing): real work")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            declare_manifest(repo, "riders: [SCC-21, SCC-22]\nlanding_mode: partial\n")
            board(t, children=[("SCC-21", "In Progress"), ("SCC-22", "To Do")])
            code, out = preflight(repo)
            c.check("CONTROL riders that really committed on the lane pass the trim check",
                    code == 1 and "clear to close out and merge" in out,
                    f"exit {code}: " + out.strip()[-600:])

        with TempDir() as t:
            # ⛔ SCC-282 · THE CONVENTION THE READER COULD NOT SEE. Every command body in this
            # repo leads a commit subject with the LANE's key (git-policy.md: "lead the subject
            # with the repo's Jira key"), and SCC-244 landed eight riders exactly that way -
            # `SCC-244 rider SCC-253: ...`. lane_commit_keys() read only the LEADING key, so on
            # a consolidated lane no rider was ever found and `landing_mode: partial` could not
            # be earned by any commit the convention allowed. The check fires at CLOSE-OUT, when
            # every commit is immutable - the only exits were rewriting history or abandoning
            # the declaration. A rider's evidence is its key NAMED in a subject, anywhere.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            for k in ("SCC-21", "SCC-22"):
                git(repo, "commit", "--no-verify", "-q", "--allow-empty",
                    "-m", f"SCC-11 rider {k}: the rider's work, parent key leading")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            declare_manifest(repo, "riders: [SCC-21, SCC-22]\nlanding_mode: partial\n")
            board(t, children=[("SCC-21", "In Progress"), ("SCC-22", "To Do")])
            code, out = preflight(repo)
            c.check("SCC-282 a rider NAMED in a subject the lane key leads earns its evidence "
                    "(the house convention is not a declaration error)",
                    code == 1 and "clear to close out and merge" in out,
                    f"exit {code}: " + out.strip()[-600:])

            # The pure function, on the LIVE proof: commit d9d9a9d on main reads
            # "SCC-244 rider SCC-253: scripts/INDEX.md names a lever that is worth two seconds
            # [sop-ok]" - it IS that rider's whole implementation, and the leading-key reader
            # did not see SCC-253 in it. The verbatim subject is the fixture; when the sha is
            # reachable from the repo under test, the live subject must still equal it.
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            import task_preflight as tp
            fixture = ("SCC-244 rider SCC-253: scripts/INDEX.md names a lever that is worth "
                       "two seconds [sop-ok]")
            found = set(tp.subject_keys(fixture)) if hasattr(tp, "subject_keys") else set()
            c.check("SCC-282 subject_keys() finds EVERY key in d9d9a9d's verbatim subject, "
                    "not just the leading one",
                    found == {"SCC-244", "SCC-253"}, f"found {sorted(found)}")
            here = Path(__file__).resolve().parent
            live = subprocess.run(["git", "log", "-1", "--format=%s", "d9d9a9d"], cwd=str(here),
                                  capture_output=True, text=True)
            if live.returncode == 0 and live.stdout.strip():
                c.check("SCC-282 ...and the fixture IS the live subject of d9d9a9d",
                        live.stdout.strip() == fixture, live.stdout.strip())
            else:
                print("   (d9d9a9d not reachable here - shallow clone; live read skipped, "
                      "fixture still asserted)")

        with TempDir() as t:
            # `landing_mode: partial` with NOTHING left open is just a normal close - it must not
            # invent a warning, or the ceremony's output stops meaning anything.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "commit", "--no-verify", "-q", "--allow-empty",
                "-m", "SCC-21 fix(thing): real work")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            declare_manifest(repo, "riders: [SCC-21]\nlanding_mode: partial\n")
            board(t, children=[("SCC-21", "In Progress"), ("SCC-23", "Done")])
            code, out = preflight(repo)
            c.check("CONTROL `landing_mode: partial` with nothing left open raises no "
                    "left-behind warning", code == 1 and "SCC-23" not in out,
                    f"exit {code}: " + out.strip()[-500:])

        with TempDir() as t:
            # An unknown `landing_mode:` value must fail CLOSED. `landing: full`, a typo, or a
            # future mode nothing implements cannot silently read as "partial" - the whole
            # RIDERS_RE lesson (an unread declaration blocks) applied to the new key.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "commit", "--no-verify", "-q", "--allow-empty",
                "-m", "SCC-21 fix(thing): real work")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            declare_manifest(repo, "riders: [SCC-21]\nlanding_mode: prtial\n")
            board(t, children=[("SCC-21", "In Progress"), ("SCC-23", "To Do")])
            code, out = preflight(repo)
            c.check("an unknown `landing_mode:` value fails CLOSED - the child still blocks",
                    code == 2, f"exit {code}: " + out.strip()[-500:])
            c.check("...and it names the value it did not understand",
                    "prtial" in out, out.strip()[-500:])

        with TempDir() as t:
            # ⛔ THE COLLISION CONTROL, and it is drawn from a real regression this change
            # caused: `task.yaml` already carries a `landing:` key - NESTED under each
            # `secondary_repos:` entry, values `independent-task` / `retain-on-epic`. The first
            # cut of this feature read the mode with manifest_field's `^\s*landing\s*:` idiom,
            # which matches an INDENTED line, so every cross-repo manifest suddenly declared an
            # unknown landing mode and five green SCC-94 cases went red. The key is now
            # `landing_mode` and its pattern is anchored at column 0; this case is what keeps
            # both true.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml",
                  MANIFEST + "secondary_repos:\n  - repo: Projects/OTHER\n"
                             "    landing: independent-task\n    ticket: AVCH-53\n")
            commit(repo, "SCC-11 chore: a cross-repo manifest")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            board(t, children=[("SCC-21", "In Progress")])
            code, out = preflight(repo)
            c.check("a NESTED `landing:` under secondary_repos is NOT a landing mode",
                    "landing_mode" not in out, out.strip()[-500:])
            c.check("...so the cross-repo lane is gated exactly as it always was (the open "
                    "child blocks, and nothing else does)",
                    code == 2 and "open subtask" in out, f"exit {code}: " + out.strip()[-400:])


    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
