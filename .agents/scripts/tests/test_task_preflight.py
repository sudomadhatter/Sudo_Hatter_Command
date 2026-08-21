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

import json
import sys
from pathlib import Path


from _harness import Cases, TempDir, run_script
from _pf_fixtures import (ADIR, MANIFEST, WALKTHROUGH, WALKTHROUGH_NO_ACTIONS,
                          board, branch, commit, git, make_repo, preflight,
                          stamp_and_verdict, with_secondary, write)


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

    # ── SCC-110 · the whole point, end to end ────────────────────────────────────────────
    if c.block("SCC-110 · the whole point, end to end"):
        # A repo that CLAIMS gates (it declares a Jira project) while tracking no hooks is
        # completely ungated: every check above the verdict inferred something from commits that
        # nothing actually checked. Before SCC-110 this printed "clear to close out and merge".
        # Asserted here rather than in test_hooks_armed because only the real script proves it -
        # a unit assertion on wf.Report proves the plumbing, not the printed verdict.
        with TempDir() as t:
            repo = make_repo(t, hooks=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-110 an UNARMED repo that claims gates is BLOCKED", code == 2,
                    out.strip()[-400:])
            c.check("SCC-110 and the words 'clear to close out and merge' never appear",
                    "clear to close out and merge" not in out, out.strip()[-400:])
            c.check("SCC-110 the operator is told which layer is off", "GATES: NOT ARMED" in out,
                    out.strip()[-400:])

        # A real extra worktree DOES trigger it - or the check above passes by being dead.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "checkout", "-q", "main")
            git(repo, "worktree", "add", "-q", str(t / "wt"), "chore/SCC-11-thing")
            code, out = preflight(repo, "--branch", "chore/SCC-11-thing")
            c.check("a real extra worktree IS reported",
                    "is checked out on" in out, out.strip()[-300:])

    # ── --json carries the lane a caller can branch on ──
    if c.block("--json carries the lane a caller can branch on"):
        with TempDir() as t:
            repo = make_repo(t, deployable=True)
            branch(repo, "chore/SCC-11-thing", {"frontend/page.tsx": "export default 1\n"})
            code, out = preflight(repo, "--json")
            import json as _json
            data = _json.loads(out)
            c.check("--json lane is HANDOFF", data["lane"] == "HANDOFF", str(data.get("lane")))
            c.check("--json key is parsed", data["key"] == "SCC-11", str(data.get("key")))
            c.check("--json lists the deployable path touched",
                    data["deployable_touched"] == ["frontend/"], str(data.get("deployable_touched")))

    # ── SCC-64: intent — the preflight refuses to run without a stated target ──
    if c.block("SCC-64: intent — the preflight refuses to run without a stated t"):
        # The 2026-08-09 failure: cwd drifted into a sibling lane and every check ran honestly
        # against the wrong branch. No derived input can catch that; a required one can.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = run_script("task_preflight.py", "--repo", str(repo))
            c.check("SCC-64 bare run (no --expect-key) is refused",
                    code == 2 and "--expect-key" in out, out.strip()[-200:])

        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo, expect="SCC-99")
            c.check("SCC-64 a branch carrying ANOTHER lane's key blocks", code == 2, f"exit {code}")
            c.check("SCC-64 the mismatch names both keys",
                    "SCC-99" in out and "SCC-11" in out and "ANOTHER lane" in out,
                    out.strip()[-300:])

        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo, expect="scc-11")
            c.check("SCC-64 expect-key is case-normalized and a match is stated",
                    code == 0 and "SCC-11 matches the branch key" in out, out.strip()[-300:])

    # ── SCC-64: the manifest cross-check ──
    if c.block("SCC-64: the manifest cross-check"):
        with TempDir() as t:
            repo = make_repo(t, manifest=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-64 a missing manifest warns with the schema, never blocks",
                    code == 1 and "no task.yaml declares task_key: SCC-11" in out,
                    out.strip()[-400:])

    # ── SCC-113 H-1: a receipt already ON the mainline is a landed lane's, not drift ──
    if c.block("SCC-113 H-1: a receipt already ON the mainline is a landed lane'"):
        # Multi-lane tickets leave one task.yaml per landed lane in the tree (SCC-113 carries
        # three), so "a manifest naming a different branch" is the DESIGNED end-state of every
        # closed sibling - re-litigating those blocks every follow-on lane. The reverted
        # fe46b4a asked "does the declared branch still exist?", which blessed exactly the
        # pruned-branch state a close-out ends in. The sound question needs POSITIVE evidence:
        # is this exact receipt, blob for blob, already recorded on the mainline? Landed ->
        # settled, skipped. Unlanded, edited since landing, or no mainline to ask -> the same
        # hard block as before; absence of evidence never relaxes the gate.

        with TempDir() as t:
            repo = make_repo(t)  # its manifest (chore/SCC-11-thing) is committed AND pushed to main
            branch(repo, "chore/SCC-11-other", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("H-1 a landed receipt for another branch is settled, never an error",
                    "already recorded on origin/main" in out and "declares branch" not in out,
                    out.strip()[-400:])
            c.check("H-1 all receipts settled -> THIS lane has no manifest, and that warns",
                    code == 1 and "intent rests on --expect-key alone" in out,
                    out.strip()[-400:])

        with TempDir() as t:  # the real H-1 shape: two landed lanes + the live one, same ticket
            repo = make_repo(t)
            for lane in ("a", "b"):
                write(repo, f"_artifacts/_main/2026-08-08_scc-11-{lane}/task.yaml",
                      MANIFEST.replace("chore/SCC-11-thing", f"chore/SCC-11-{lane}"))
            commit(repo, "SCC-11 chore: two landed lanes")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("H-1 two settled siblings + this lane's own receipt -> clean exit 0",
                    code == 0 and out.count("already recorded on origin/main") == 2
                    and "agrees: SCC-11 on chore/SCC-11-thing" in out,
                    out.strip()[-500:])

        with TempDir() as t:  # drift is still drift: an UNLANDED receipt naming another branch
            repo = make_repo(t, manifest=False)
            branch(repo, "chore/SCC-11-other",
                   {"docs/x.md": "x\n",
                    "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml": MANIFEST})
            code, out = preflight(repo)
            c.check("SCC-64/H-1 an unlanded receipt naming a DIFFERENT branch still blocks",
                    code == 2 and "declares branch `chore/SCC-11-thing`" in out,
                    out.strip()[-400:])

        with TempDir() as t:  # edited since landing = the receipt on disk is NOT the one that merged
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-other",
                   {"docs/x.md": "x\n",
                    "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml": MANIFEST + "# amended\n"})
            code, out = preflight(repo)
            c.check("H-1 a landed receipt EDITED after landing loses settled status and blocks",
                    code == 2 and "declares branch `chore/SCC-11-thing`" in out
                    and "already recorded" not in out,
                    out.strip()[-400:])

        with TempDir() as t:  # no mainline to ask -> the probe fails -> strict, never lenient
            repo = make_repo(t, remote=False, manifest=False)
            branch(repo, "chore/SCC-11-other",
                   {"docs/x.md": "x\n",
                    "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml": MANIFEST},
                   push=False)
            code, out = preflight(repo)
            c.check("H-1 absent evidence keeps the hard block (no remote, receipt unlanded)",
                    code == 2 and "declares branch `chore/SCC-11-thing`" in out,
                    out.strip()[-400:])

    # ── SCC-64: dirty memory files are named, with the park-don't-sweep instruction ──
    if c.block("SCC-64: dirty memory files are named, with the park-don't-sweep "):
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            write(repo, "_artifacts/_memory/some-lesson.md", "a memory\n")
            code, out = preflight(repo)
            c.check("SCC-64 a dirty memory file still blocks", code == 2, f"exit {code}")
            c.check("SCC-64 memory files get their own instruction, not the generic count",
                    "memory file(s) dirty under _artifacts/_memory/" in out
                    and "sweep" in out and "park" in out, out.strip()[-400:])

    # ── SCC-64: in a no-deploy repo the printed gate is scoped to the toolkit ──
    if c.block("SCC-64: in a no-deploy repo the printed gate is scoped to the to"):
        with TempDir() as t:
            repo = make_repo(t)
            write(repo, ".agents/scripts/workflow_lint.py", "# fixture\n")
            commit(repo, "SCC-11 chore: lint fixture")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-64 no-deploy repo prints workflow_lint --toolkit-only",
                    "workflow_lint.py --toolkit-only" in out, out.strip()[-300:])

    # ── SCC-138 · the lane gate must RUN the map linter, not just the test suite ──────────
    if c.block("SCC-138 · the lane gate must RUN the map linter, not just the te"):
        # `gate_plan()` built the LOCAL gate from run_all + workflow_lint ONLY, so the close-out
        # could not fail on a linter it never ran. Twice in one day the two disagreed and only the
        # linter was right: SCC-124 landed a session folder with no INDEX row and SCC-119 nearly
        # did, both while run_all reported 21/21 PASS. A gate that prints a clean verdict over a
        # red linter is worse than no gate - it converts a detectable problem into a trusted one.
        with TempDir() as t:
            repo = make_repo(t)
            write(repo, ".agents/scripts/check_maps.py", "# fixture\n")
            commit(repo, "SCC-11 chore: check_maps fixture")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-138 the printed gate includes check_maps",
                    "check_maps.py" in out, out.strip()[-400:])
            # ⛔ The `--strict` token is the whole gate. `--depth3-only` ALONE exits 0 even on
            # drift (it is SessionStart's nag), so the entry without it is a gate that cannot
            # fail - the exact vacuous green this ticket closes. Pin the token, not the prose.
            c.check("SCC-138 ...with --strict, or the entry is a gate that cannot fail",
                    "check_maps.py --depth3-only --strict" in out, out.strip()[-400:])

        # A repo that does not ship the linter must not be told to run it - never report a gate
        # that did not run (the same rule the empty-plan branch already states).
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-138 a repo without check_maps is not told to run it",
                    "check_maps.py" not in out, out.strip()[-400:])

    # ── SCC-94: secondary_repos was documented in three places and read by NOTHING ──
    if c.block("SCC-94: secondary_repos was documented in three places and read "):
        # A cross-repo task could declare "this also lands in <repo> under <KEY>" and close out green
        # while that key was one the repo's hook rejects, the branch was never pushed, or the half was
        # not even checked out. The positive control matters as much as the refusals: a correctly
        # declared secondary repo must still exit 0, or this becomes "always stop" and gets designed
        # around inside a week - the same argument the deployable-lane cases above are built on.


        with TempDir() as t:                                   # POSITIVE CONTROL, first
            repo = with_secondary(t)
            code, out = preflight(repo)
            c.check("SCC-94 a correctly declared secondary repo still exits 0",
                    code == 0, out.strip()[-500:])
            c.check("SCC-94 ...and says which repo/ticket pair it verified",
                    "SECONDARY" in out and "AVCH-53" in out, out.strip()[-500:])

        with TempDir() as t:
            repo = with_secondary(t, ticket="SCC-99")           # a key that repo's hook rejects
            code, out = preflight(repo)
            c.check("SCC-94 a ticket key the secondary repo does not answer to BLOCKS",
                    code == 2 and "SCC-99" in out and "AVCH" in out, out.strip()[-500:])

        with TempDir() as t:
            repo = with_secondary(t, clean=False)
            code, out = preflight(repo)
            c.check("SCC-94 a dirty secondary repo blocks - the lobby's own status cannot see it",
                    code == 2 and "SECONDARY" in out, out.strip()[-500:])

        with TempDir() as t:
            repo = with_secondary(t, pushed=False)
            code, out = preflight(repo)
            c.check("SCC-94 an unpushed secondary repo blocks (commit-and-push are ONE action)",
                    code == 2 and "SECONDARY" in out, out.strip()[-500:])

        with TempDir() as t:
            repo = with_secondary(t, checked_out=False)
            code, out = preflight(repo)
            c.check("SCC-94 a declared-but-uncheckedout secondary repo blocks, never passes quietly",
                    code == 2 and "SECONDARY" in out, out.strip()[-500:])

        with TempDir() as t:
            repo = with_secondary(t, store="broken")
            code, out = preflight(repo)
            c.check("SCC-94 a broken secondary memory store BLOCKS here, unlike run_all's SIGNAL",
                    code == 2 and "a-fact" in out, out.strip()[-500:])

        with TempDir() as t:                                   # no store at all is a beginning
            repo = with_secondary(t, store=None)
            code, out = preflight(repo)
            c.check("SCC-94 a secondary repo with no memory store yet is NOT a failure",
                    code == 0, out.strip()[-500:])

        with TempDir() as t:                                   # regression: the common case is empty
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-94 `secondary_repos: []` is untouched - single-repo tasks see nothing new",
                    code == 0 and "secondary" not in out.lower(), out.strip()[-400:])

    # ── SCC-94 review: the parser could not tell "none declared" from "I could not read it" ──
    if c.block("SCC-94 review: the parser could not tell 'none declared' from 'I"):
        # Every row below returned ([], None) from the first implementation: verified nothing, said
        # nothing, exit 0. The adversarial review found four valid YAML spellings that did it, and the
        # worst was self-inflicted - this command's own template shipped `secondary_repos: []` above a
        # COMMENTED block, so uncommenting it (the edit the comment invites) left the `[]` to win the
        # search. These are unit-level on purpose: the failure is in the reader, and a fixture repo
        # per spelling would hide which spelling broke.
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "tp", Path(__file__).resolve().parents[1] / "task_preflight.py")
        tp = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(tp)

        ROW = "  - repo: Projects/SECONDARY\n    landing: independent-task\n    ticket: SCC-99\n"
        for label, text in (
            ("the shipped template with its block UNCOMMENTED (two keys)",
             f"task_key: SCC-11\nsecondary_repos: []\nsecondary_repos:\n{ROW}"),
            ("a zero-indent block, which is what yaml.dump emits",
             "secondary_repos:\n- repo: Projects/SECONDARY\n  ticket: SCC-99\n"),
            ("a space before the colon, which manifest_field already accepts",
             f"secondary_repos :\n{ROW}"),
            ("`-` alone on its line (valid non-compact sequence)",
             "secondary_repos:\n  -\n    repo: Projects/SECONDARY\n    ticket: SCC-99\n"),
            ("a mapping key before any `- ` item",
             "secondary_repos:\n    repo: Projects/SECONDARY\n    ticket: SCC-99\n"),
        ):
            rows, unparsed = tp.secondary_rows(text)
            c.check(f"SCC-94 review: {label} is READ or reported, never silently empty",
                    bool(rows) or bool(unparsed), f"rows={rows} unparsed={unparsed}")

        rows, unparsed = tp.secondary_rows(
            "secondary_repos:\n  - repo: A\n    ticket: AVCH-1\n# a comment at column 0\n"
            "  - repo: B\n    ticket: SCC-99\n")
        c.check("SCC-94 review: a column-0 comment does not truncate the list (YAML allows it anywhere)",
                len(rows) == 2 or bool(unparsed), f"rows={rows} unparsed={unparsed}")

        c.check("SCC-94 review: `#` inside a value is a path, not a comment",
                tp.secondary_rows("secondary_repos:\n  - repo: Projects/C#App\n    ticket: AVCH-1\n"
                                  )[0][0]["repo"] == "Projects/C#App",
                str(tp.secondary_rows("secondary_repos:\n  - repo: Projects/C#App\n    ticket: AVCH-1\n")))

        # The negative controls: the two forms that legitimately mean "nothing to verify" must stay
        # silent, or every single-repo task in the system starts failing.
        for label, text in (("an absent key", "task_key: SCC-11\n"),
                            ("the inline empty list", "secondary_repos: []\n"),
                            ("the inline empty list with a trailing comment",
                             "secondary_repos: []   # single-repo task\n")):
            rows, unparsed = tp.secondary_rows(text)
            c.check(f"SCC-94 review: {label} stays silent - no rows AND no complaint",
                    rows == [] and unparsed is None, f"rows={rows} unparsed={unparsed}")

        # A5's two refusals, which the review found implemented and completely untested.
        with TempDir() as t:
            repo = with_secondary(t, ticket="")
            code, out = preflight(repo)
            c.check("SCC-94 review: a row with no `ticket:` blocks (a ticket PER REPO)",
                    code == 2 and "no `ticket:`" in out, out.strip()[-400:])

        with TempDir() as t:
            repo = make_repo(t)
            write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml",
                  "task_key: SCC-11\nprimary_repo: repo\nbranch: chore/SCC-11-thing\n"
                  "secondary_repos: [{repo: Projects/X, ticket: SCC-99}]\n")
            commit(repo, "SCC-11 chore: inline form")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("SCC-94 review: the unreadable inline form BLOCKS - it verified nothing",
                    code == 2 and "not " in out and "readable" in out, out.strip()[-400:])

        # Detached HEAD is not a mistake: `git submodule update --init` produces it, so every
        # submodule on a fresh clone is detached. The first version asked `origin/HEAD...HEAD`,
        # inventing a branch, and blocked with a remedy that does not apply.
        with TempDir() as t:
            repo = with_secondary(t)
            proj = repo / "Projects" / "SECONDARY"
            git(proj, "checkout", "-q", "--detach", "HEAD")
            code, out = preflight(repo)
            c.check("SCC-94 review: a DETACHED secondary that is pushed does not block",
                    code == 0 and "detached" in out, out.strip()[-500:])
        with TempDir() as t:
            repo = with_secondary(t, pushed=False)
            proj = repo / "Projects" / "SECONDARY"
            git(proj, "checkout", "-q", "--detach", "HEAD")
            code, out = preflight(repo)
            c.check("SCC-94 review: ...but a detached secondary on NO remote branch still blocks",
                    code == 2 and "on one disk" in out, out.strip()[-500:])

        # A repo with no jira.conf used to print `matches its jira.conf ()` - a claimed verification
        # whose own empty parens prove it never happened. `check_branch` warns for the primary; this
        # now matches it.
        with TempDir() as t:
            repo = with_secondary(t)
            (repo / "Projects" / "SECONDARY" / ".agents" / "jira.conf").unlink()
            code, out = preflight(repo)
            c.check("SCC-94 review: no jira.conf WARNS, never claims a match it did not make",
                    "cannot be checked against" in out and "matches its jira.conf ()" not in out,
                    out.strip()[-500:])

        # A cp1252 byte in a project's MEMORY.md raised UnicodeDecodeError straight out of the check,
        # killing the run at exit 1 - which this script's own contract grades as *warnings* - with no
        # VERDICT line and the deployable-lane question never asked.
        with TempDir() as t:
            repo = with_secondary(t)
            proj = repo / "Projects" / "SECONDARY"
            (proj / "_artifacts" / "_memory" / "MEMORY.md").write_bytes(
                b"# Index\n- [A fact](a-fact.md) \x97 an em-dash in cp1252\n")
            # Committed and pushed, so the ONLY thing wrong is that the store cannot be decoded -
            # otherwise the dirty-tree error fires and the assertion passes for the wrong reason.
            commit(proj, "AVCH-1 chore: cp1252 byte")
            git(proj, "push", "-q", "origin", "main")
            code, out = preflight(repo)
            c.check("SCC-94 review: an unreadable secondary store is reported, never raised",
                    code != 2 and "VERDICT" in out and "could not be read" in out, out.strip()[-500:])

        # ⭐ The case the fixtures above CANNOT see, and the one that matters: close-outs run from a
        # worktree, and submodules do not populate there - `Projects/<name>/` is an empty stub in
        # every lane. Resolving only under the lane made this check block every cross-repo close-out
        # in the one place they all happen. Found by running it against a real lane, not by a fixture,
        # which is why this test exists: a real linked worktree, secondary present only in the main
        # checkout, preflight aimed at the LANE.
        with TempDir() as t:
            repo = with_secondary(t)
            lane = t / "lane"
            # The primary goes back to `main` first: git refuses to check a branch out twice, and a
            # main checkout sitting on main while the work happens in a lane is the real arrangement.
            git(repo, "checkout", "-q", "main")
            git(repo, "worktree", "add", "-q", str(lane), "chore/SCC-11-thing")
            (lane / "Projects" / "SECONDARY").mkdir(parents=True, exist_ok=True)   # the empty stub
            code, out = run_script("task_preflight.py", "--repo", str(lane),
                                   "--branch", "chore/SCC-11-thing", "--expect-key", "SCC-11")
            # Not `code == 0`: a live lane always warns that the worktree is still checked out, which
            # is exit 1. The property under test is that the secondary check does not BLOCK - exit 2.
            c.check("SCC-94 a lane resolves the secondary in the SHARED checkout, not the stub",
                    code != 2 and "VERDICT: clear" in out, out.strip()[-600:])
            c.check("SCC-94 ...and says so, so the operator knows which checkout was verified",
                    "shared checkout" in out, out.strip()[-600:])


    # ── SCC-192 + SCC-193 · THE RECEIPT, AND FETCH AS THE DEFAULT ───────────────────────
    #
    # ⛔ THE TWO MEASURED SLIPS THIS BLOCK EXISTS FOR (SCC-164's own landing, 2026-08-16):
    #   * the preflight was run WITHOUT --fetch, so ahead/behind was measured against a stale
    #     fetch — and the note saying so was an INFO under a VERDICT line that still read
    #     "clear to close out and merge". The verdict line is the only line an agent acts on,
    #     so the fact has to be ON it, and the exit has to be non-zero.
    #   * the ceremony was hand-run and NOTHING could tell: the preflight wrote no trace at
    #     all. It now leaves one receipt, which the PR gate (main_write_gate --mode pr)
    #     REQUIRES — so a close-out that skipped this call produces a red check, server-side.
    #
    # ⛔ THE RECEIPT IS KEYED ON THE VERDICT SHA, NEVER HEAD. Committing the receipt MOVES
    # HEAD, so a receipt carrying HEAD can never be byte-stable and the tree is dirty forever
    # (SCC-192's own loop-1 constraint). The flight recorder solved this first; one rule, two
    # writers.
    if c.block("SCC-192/193 · the preflight leaves a RECEIPT, and fetch is the DEFAULT"):
        RECEIPT = f"{ADIR}/preflight-receipt.json"

        def receipt(repo) -> dict:
            p = repo / RECEIPT
            return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}

        # ⛔ Never `read_bytes()` straight: while this block is RED the file does not exist,
        # and a test that dies in setup is indistinguishable from one that fails its
        # assertion (`red-test-can-die-before-its-assertion`). Absent reads as b"".
        def raw(repo) -> bytes:
            p = repo / RECEIPT
            return p.read_bytes() if p.is_file() else b""

        with TempDir() as t:
            # R1 · the ordinary lane: no flag at all, and the fetch happens anyway.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = stamp_and_verdict(repo, "PASS")
            code, out = preflight(repo)
            r = receipt(repo)
            c.check("R1 a preflight with NO flag fetches, and says the comparison is fresh",
                    code == 0 and "clear to close out and merge" in out
                    and "no --fetch" not in out, f"exit {code}: " + out.strip()[-400:])
            c.check("R1 ...and leaves a receipt beside the lane's task.yaml",
                    (repo / RECEIPT).is_file(), RECEIPT)
            c.check("R1 the receipt records the key, the branch and the FLAGS IT RAN WITH",
                    r.get("task_key") == "SCC-11"
                    and r.get("branch") == "chore/SCC-11-thing"
                    and r.get("fetch") is True and r.get("fresh") is True
                    and r.get("accept_unpushed_main") is False,
                    json.dumps(r))
            c.check("R1 the receipt carries the VERDICT the agent acted on, and its exit",
                    str(r.get("verdict", "")).startswith("clear") and r.get("exit") == 0,
                    json.dumps(r))
            c.check("R1 ⛔ keyed on the VERDICT sha, never on HEAD",
                    r.get("verdict_sha") == sha
                    and not any(k in r for k in ("head", "tip", "head_sha")),
                    json.dumps(r))

            # R4 · idempotent on CONTENT, and the writer's own file is not its own dirt.
            before = raw(repo)
            code2, out2 = preflight(repo)
            c.check("R4 a re-run rewrites byte-identical content (no churn commit)",
                    bool(before) and raw(repo) == before,
                    "the receipt moved on a no-op run, or was never written")
            c.check("R4 ...and the uncommitted receipt does not make its own tree DIRTY",
                    code2 == 0 and "uncommitted change" not in out2,
                    f"exit {code2}: " + out2.strip()[-400:])
            # ⭐ R6 · THE CASE A SURVIVING MUTANT PROVED WAS MISSING. R4 above re-runs with
            # NOTHING else changed, so a receipt that embedded HEAD would still be byte-stable
            # across those two runs and R4 passes - the mutant "rewrite unconditionally, padded
            # by HEAD's length" survived exactly there. The real sequence is the one the door
            # performs: the receipt is COMMITTED (which MOVES HEAD, the whole reason the
            # SCC-192 design forbids keying on it) and a resumed close-out re-runs the
            # preflight. If any field tracked HEAD, the bytes would move here and every
            # resumed close-out would owe a churn commit.
            git(repo, "add", RECEIPT)
            commit(repo, "SCC-11 chore(recorder): flight event + receipt [sop-ok]")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            after_commit = raw(repo)
            code4, out4 = preflight(repo)
            c.check("R6 the receipt is byte-stable ACROSS the commit that lands it",
                    bool(after_commit) and raw(repo) == after_commit,
                    "committing the receipt moves HEAD - a receipt that tracked HEAD would "
                    "move with it, and no close-out could ever converge")
            c.check("R6 ...and the tree is clean afterwards, so the lane can merge",
                    code4 == 0 and "uncommitted change" not in out4,
                    f"exit {code4}: " + out4.strip()[-300:])

            # ...but the exemption is ONE file, not a licence for the folder.
            write(repo, f"{ADIR}/scratch.txt", "a sibling artifact nobody committed\n")
            code3, out3 = preflight(repo)
            c.check("R4 CONTROL: a SIBLING dirty artifact still blocks (the exemption is one file)",
                    code3 == 2 and "uncommitted change" in out3,
                    f"exit {code3}: " + out3.strip()[-400:])

        with TempDir() as t:
            # R2 · the opt-out. `--no-fetch` is honest about what it cost.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS")
            code, out = preflight(repo, "--no-fetch")
            r = receipt(repo)
            c.check("R2 --no-fetch never prints the clear verdict",
                    "clear to close out and merge" not in out, out.strip()[-400:])
            c.check("R2 ...the VERDICT line itself names the staleness, and the exit is non-zero",
                    code != 0 and "VERDICT:" in out
                    and "stale" in out.split("VERDICT:")[-1].lower(),
                    f"exit {code}: " + out.strip()[-400:])
            c.check("R2 ...and the remedy fits the branch that produced it (--no-fetch)",
                    "re-run WITHOUT --no-fetch" in out.split("VERDICT:")[-1],
                    out.strip()[-400:])
            c.check("R2 ...an omitted fetch is a WARN, not an info footnote",
                    "[WARN ] sync" in out or "[WARN] sync" in out, out.strip()[-500:])
            c.check("R2 ...and the receipt records that it ran without one",
                    r.get("fetch") is False and r.get("fresh") is False
                    and r.get("exit") == code, json.dumps(r))

        with TempDir() as t:
            # R3 · ⭐ SEVERITY PARITY. A fetch that FAILED and a fetch never ATTEMPTED are the
            # same evidence — a comparison against the last fetch — so they are the same
            # severity. Today the omitted one is `info` (:876) and the failed one is `warn`
            # (:874): never trying outranks trying, which is backwards, and it is exactly how
            # SCC-164's run was told it was clear.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS")
            git(repo, "remote", "set-url", "origin", str(t / "no-such-remote.git"))
            code, out = preflight(repo)          # asks for the fetch; the uplink is dead
            r = receipt(repo)
            c.check("R3 a FAILED fetch reaches the same verdict as an omitted one",
                    code != 0 and "clear to close out and merge" not in out
                    and "stale" in out.split("VERDICT:")[-1].lower(),
                    f"exit {code}: " + out.strip()[-400:])
            # ⛔ AND THE REMEDY MUST FIT. This operator never passed --no-fetch: the uplink is
            # dead. Printing "re-run WITHOUT --no-fetch" at them is a no-op instruction under a
            # verdict they are supposed to act on, and the receipt distinguished the two cases
            # long before the verdict line did.
            c.check("R3 ...and the VERDICT's remedy names the FAILED fetch, not --no-fetch",
                    "asked for and FAILED" in out.split("VERDICT:")[-1]
                    and "WITHOUT --no-fetch" not in out.split("VERDICT:")[-1],
                    out.strip()[-400:])
            c.check("R3 ...and the receipt says the fetch was ASKED FOR but is not fresh",
                    r.get("fetch") is True and r.get("fresh") is False, json.dumps(r))
            c.check("R3 ...a failed fetch is still only a WARN — offline is not a defect",
                    "[ERROR] sync" not in out and "fetch failed" in out,
                    out.strip()[-500:])

        with TempDir() as t:
            # R5 · a lane with NO live manifest has nowhere to put a receipt, and inventing a
            # location is worse than not writing one: the PR gate keys on the manifest.
            repo = make_repo(t, manifest=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check("R5 no manifest -> no receipt, and the run still reports normally",
                    not (repo / RECEIPT).is_file() and "VERDICT:" in out,
                    out.strip()[-300:])

        with TempDir() as t:
            # ⭐ R7 · THE AMBIGUITY LOOP THE EDGE-CASE LENS EXECUTED. `check_manifest` returns
            # the ONE manifest that is this lane's contract, and deliberately returns None when
            # two agree rather than coin-flipping a location. But it reported both as INFO, so
            # the VERDICT still read "clear", no receipt was written — and `main_write_gate
            # --mode pr` then DEMANDS a receipt beside each of those manifests. A green
            # preflight handing the PR an unmeetable demand is the worst of the four loops:
            # the operator is told to merge by the tool that guaranteed the merge is blocked.
            # Ambiguity about WHERE the evidence goes is an error about the evidence.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            write(repo, "_artifacts/_main/2026-08-08_scc-11-second/task.yaml", MANIFEST)
            commit(repo, "SCC-11 chore: a second manifest for the same lane")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            stamp_and_verdict(repo, "PASS")
            code, out = preflight(repo)
            c.check("R7 two manifests agreeing on ONE lane is an ERROR, not two infos",
                    code == 2 and "VERDICT: BLOCKED" in out,
                    f"exit {code}: " + out.strip()[-500:])
            c.check("R7 ...and it names both, and says the receipt has nowhere to go",
                    "2026-08-08_scc-11-second" in out and "scc-11-thing" in out
                    and RECEIPT.rsplit("/", 1)[-1] in out,
                    out.strip()[-600:])
            c.check("R7 ...and no receipt is invented beside either of them",
                    not (repo / RECEIPT).is_file(),
                    "a coin-flip here puts the evidence next to the wrong walkthrough")

        with TempDir() as t:
            # R8 · a receipt that is not readable TEXT must not kill the preflight. The writer
            # compares bytes to decide whether to rewrite, and `read_text` raises
            # UnicodeDecodeError — a ValueError, which `except OSError` never caught. A truncated
            # or half-written receipt (an interrupted close-out) is exactly how that file ends up
            # non-UTF-8, and the crash lands on the run that would have REPLACED it.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS")
            (repo / RECEIPT).write_bytes(b"\xff\xfe not utf-8 at all")
            code, out = preflight(repo)
            c.check("R8 a corrupt receipt is REPLACED, not a traceback",
                    "Traceback" not in out and raw(repo).startswith(b"{"),
                    f"exit {code}: " + out.strip()[-500:])

        with TempDir() as t:
            # ⭐ R9 · THE EXEMPTION IS THIS LANE'S RECEIPT, and the comment above it already
            # said so ("the ONE file the writer owns"). The test measured the NAME and the
            # `_artifacts/` prefix, so ANY folder's `preflight-receipt.json` was waved through —
            # including a sibling lane's uncommitted one, which is another session's work being
            # silently dropped from the dirty-tree count that exists to catch exactly that.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS")
            # ⛔ THE SIBLING FOLDER MUST ALREADY BE TRACKED. git reports a wholly-untracked
            # directory as ONE `?? <dir>/` row, and `Path("<dir>/").name` is the folder name
            # under the fix AND under the mutant - so the first cut of this control passed
            # either way and S-M9 survived it. With the folder tracked, the receipt appears as
            # its own row and the path comparison is the only thing that can answer.
            write(repo, "_artifacts/_main/2026-08-08_scc-99-other/notes.md", "another lane\n")
            commit(repo, "SCC-11 chore: a sibling lane's folder (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            write(repo, "_artifacts/_main/2026-08-08_scc-99-other/preflight-receipt.json",
                  '{"task_key": "SCC-99"}\n')
            code, out = preflight(repo)
            c.check("R9 CONTROL: ANOTHER lane's uncommitted receipt is still dirt",
                    code == 2 and "uncommitted change" in out,
                    f"exit {code}: " + out.strip()[-400:])

    # ══ SCC-211 · THE TREE MEASURED MUST BE THE TREE THAT HOLDS THE BRANCH ════════════════
    #
    # `check_sync` asked `git status --porcelain` in whatever `--repo` named. For
    # `/smh-close-task-merge-tree` that is the lane's own worktree, so the question was right
    # by construction — and **`/smh-merge-multiple-workingtrees` is the shape where it is
    # not.** That command sets `REPO=$(git rev-parse --show-toplevel)` — the tree you are
    # STANDING in — and then preflights each lane's branch in turn (its Step, line 119).
    # Orchestrating a multi-lane landing from the main checkout is the natural way to run it,
    # and in that shape `--repo` is `main` (spotless) while every lane's dirt sits in its own
    # worktree, unseen. A set-landing is the worst place to be blind: it is N production
    # merges, and the combined gate at the end is the only run that sees the set together.
    #
    # The answer is the one all three doors now share — `wf_common.trees_to_measure` derives
    # the tree from `git worktree list` rather than trusting the path the caller happened to
    # pass. Same body, so the doors cannot drift about what they are measuring.
    if c.block("SCC-211 · a dirty LANE worktree is seen from the main checkout"):
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "checkout", "-q", "main")
            wt = t / "lane-tree"
            git(repo, "worktree", "add", "-q", str(wt), "chore/SCC-11-thing")
            (wt / "docs" / "x.md").write_text("uncommitted, in the lane\n", encoding="utf-8")
            code, out = preflight(repo, "--branch", "chore/SCC-11-thing")
            c.check("SCC-211 the lane's dirt is found from the main checkout", code == 2,
                    out.strip()[-400:])
            c.check("SCC-211 ...and the message names the LANE's tree, not the checkout",
                    "lane-tree" in out, out.strip()[-400:])

        # ⛔ THE POSITIVE CONTROL. Worktrees are the norm here, so a check that refused every
        # lane holding one would false-red every close-out — the way a gate stops being used.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "checkout", "-q", "main")
            git(repo, "worktree", "add", "-q", str(t / "lane-tree"), "chore/SCC-11-thing")
            code, out = preflight(repo, "--branch", "chore/SCC-11-thing")
            c.check("SCC-211 CONTROL: a CLEAN lane worktree raises no uncommitted error",
                    "uncommitted change(s)" not in out, out.strip()[-400:])

        # ⛔ AND THE MEMORY RULING SURVIVES THE SECOND TREE. Two lanes share one memory store,
        # so `_artifacts/_memory/` dirt is named as its own class wherever it is found — never
        # folded into "commit before merging", which is the one instruction the ruling forbids
        # when another session wrote those files.
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            git(repo, "checkout", "-q", "main")
            wt = t / "lane-tree"
            git(repo, "worktree", "add", "-q", str(wt), "chore/SCC-11-thing")
            (wt / "_artifacts" / "_memory").mkdir(parents=True, exist_ok=True)
            (wt / "_artifacts" / "_memory" / "note.md").write_text("m\n", encoding="utf-8")
            code, out = preflight(repo, "--branch", "chore/SCC-11-thing")
            c.check("SCC-211 memory dirt in the LANE tree keeps its own ruling",
                    "memory file(s) dirty" in out, out.strip()[-400:])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
