"""task_preflight.py — the CONTRACT half: what it reads, and what it emits. (SCC-214)

Split out of `test_task_preflight.py` because that file set the whole enforcement suite's wall
clock. `run_all.py` runs files concurrently, so the suite's wall IS its slowest file: measured
at **81.8 s** against a 94.0 s suite whose runner-up was 45.1 s — the other 41 files finished
and waited on this one. Halving it moves the floor to `test_jira_feed.py`, which is a different
ticket's problem.

⛔ THE SEAM IS MEASURED, NOT AESTHETIC. Every block was timed in one process — 73.9 s over 25
blocks — and the cut is the balance point: 38.8 s stays, 35.1 s moves here. It also falls on a
real boundary. The file it left keeps the REFUSALS (does the preflight stop what it must stop:
deployable code, the wrong lane, a bad branch shape, an unpushed tree, open subtasks). This one
takes the CONTRACT — the manifest it reads, the secondary repos that manifest declares, the plan
it prints, the receipts it leaves, and the end-to-end pass.

⛔ NOT ONE CASE CHANGED. This is the SCC-156 move that already produced `_pf_fixtures.py` and
`test_task_preflight_receipts.py`, done once more: same assertions, same fixtures, redistributed.
The two halves must still add to the 186 cases the single file had, and that arithmetic is the
guard — a split that loses a case is the only way this can go wrong, and it is countable.

Stdlib only, no pytest, matching every other file here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


from _harness import Cases, TempDir, run_script
from _pf_fixtures import (ADIR, MANIFEST, branch, commit, git, make_repo, preflight,
                          stamp_and_verdict, with_secondary, write)


def main() -> int:
    c = Cases("task_preflight — the manifest + receipt contract")

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
            # ⛔ THE NAME MUST APPEAR ON THE *UNCOMMITTED* LINE, not anywhere in the output.
            # A MUTANT SURVIVED on the looser form: `check_worktree` already warns
            # "lane-tree is checked out on chore/… - remove it with /cicd-prune-worktree",
            # so `"lane-tree" in out` was satisfied by an unrelated pre-existing warning
            # while the sync check had gone back to measuring only the checkout. The
            # assertion has to name the finding it is about.
            c.check("SCC-211 ...and the message names the LANE's tree, not the checkout",
                    any("lane-tree" in ln and "uncommitted" in ln
                        for ln in out.splitlines()), out.strip()[-400:])

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


    # ── SCC-283 · a live sibling lane's working copy is NOT unswept dirt ──────────────
    #
    # The classifier splits dirt three ways: this script's own receipt (by exact path), memory
    # files (named separately so a close-out cannot sweep another session's store), and
    # everything else - a hard error. "Everything else" had no way to recognise ANOTHER LIVE
    # LANE'S WORKING COPY. During SCC-244's close-out the shared checkout carried
    # `M .claude/settings.json` and `?? .claude/hooks/allow-scratchpad.py`, both belonging to
    # the live chore/SCC-263 lane, which had ALREADY COMMITTED them on its branch - its live
    # config, not unswept dirt (`.claude/settings.json` can ONLY be edited in the shared
    # checkout, because that is where the running Claude reads it). The preflight errored and
    # an agent adjudicated by hand - and the two answers have OPPOSITE correct actions: unswept
    # dirt is committed or parked, another lane's live copy is left alone. Backwards either
    # wedges a close-out or destroys someone else's work, and the second has happened once
    # already (SCC-180: a `reset --hard` remedy that ate three sessions' uncommitted work).
    # SCC-246 answered the same shape for `_artifacts/_memory/` by AUTHORSHIP; this is the
    # fourth bucket for the rest of the tree, and it is earned by BYTES: the dirty working
    # copy must equal the sibling lane's COMMITTED copy, or it is still dirt.
    if c.block("SCC-283 · a live sibling lane's working copy is not unswept dirt"):
        def sibling(t, repo, rel, text):
            """A live sibling worktree on chore/SCC-12-other that COMMITS `rel`."""
            git(repo, "branch", "-q", "chore/SCC-12-other", "main")
            wt = t / "sibling-tree"
            git(repo, "worktree", "add", "-q", str(wt), "chore/SCC-12-other")
            (wt / rel).parent.mkdir(parents=True, exist_ok=True)
            (wt / rel).write_text(text, encoding="utf-8")
            git(wt, "add", rel)
            git(wt, "commit", "--no-verify", "-q", "-m", "SCC-12 chore: the sibling's live config")
            return wt

        with TempDir() as t:
            # B1 · THE case: the shared checkout carries the sibling's file, byte-identical to
            # the copy that lane committed. Not this lane's dirt - say whose it is, do not error.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sibling(t, repo, ".claude/x.json", '{"hooks": "the sibling lane\'s live config"}\n')
            (repo / ".claude").mkdir(exist_ok=True)
            (repo / ".claude" / "x.json").write_text(
                '{"hooks": "the sibling lane\'s live config"}\n', encoding="utf-8")
            code, out = preflight(repo)
            c.check("SCC-283 a dirty path byte-identical to a live sibling lane's committed "
                    "copy does NOT error", code != 2, f"exit {code}: " + out.strip()[-500:])
            c.check("SCC-283 ...and it is reported as THAT lane's working copy, naming the branch",
                    any("chore/SCC-12-other" in ln and "working copy" in ln
                        for ln in out.splitlines()), out.strip()[-500:])

        with TempDir() as t:
            # B2 · POSITIVE CONTROL: a dirty path NO live lane committed still errors exactly
            # as before - the bucket did not simply go quiet.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sibling(t, repo, ".claude/x.json", "theirs\n")
            (repo / "docs" / "stray.md").write_text("nobody committed this anywhere\n",
                                                    encoding="utf-8")
            code, out = preflight(repo)
            c.check("SCC-283 CONTROL a dirty path matching NO live lane still errors",
                    code == 2 and "uncommitted change(s)" in out,
                    f"exit {code}: " + out.strip()[-400:])

        with TempDir() as t:
            # B3 · same path as the sibling's, DIFFERENT bytes: uncommitted work is uncommitted
            # work, whoever owns it. Matching by path alone would wave real edits through.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sibling(t, repo, ".claude/x.json", "theirs, committed\n")
            (repo / ".claude").mkdir(exist_ok=True)
            (repo / ".claude" / "x.json").write_text("theirs, but EDITED since\n",
                                                     encoding="utf-8")
            code, out = preflight(repo)
            c.check("SCC-283 a sibling's path whose CONTENT differs from its committed copy "
                    "still errors", code == 2 and "uncommitted change(s)" in out,
                    f"exit {code}: " + out.strip()[-400:])

        with TempDir() as t:
            # B4 · THE BASE BRANCH IS NEVER A SIBLING LANE (self-audit finding). A file this
            # lane changed and committed, then reverted by hand in the working copy to main's
            # bytes, is dirty AND byte-identical to `main:<path>` - and a checkout on `main`
            # is a worktree like any other. Treating it as "main's working copy" would wave an
            # uncommitted revert through: permissive in exactly the SCC-180 direction.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing",
                   {".agents/scripts/tests/run_all.py": "# changed on the lane\n"})
            git(repo, "worktree", "add", "-q", str(t / "main-tree"), "main")
            (repo / ".agents/scripts/tests/run_all.py").write_text("# fixture\n",
                                                                   encoding="utf-8")
            code, out = preflight(repo)
            c.check("SCC-283 a revert-to-main in the working copy still errors - `main` is "
                    "never a sibling lane", code == 2 and "uncommitted change(s)" in out,
                    f"exit {code}: " + out.strip()[-400:])

        with TempDir() as t:
            # B5 · THE TICKET'S OWN SHAPE: a TRACKED file, MODIFIED (` M`), as the FIRST status
            # line - `M .claude/settings.json` is exactly how SCC-244's close-out met it. Found
            # by this lane's mutant M7 surviving: B4 above "passed" for the wrong reason. The
            # classifier `.strip()`ped the whole porcelain output before splitting, which eats
            # the leading space of the FIRST line only, so ` M .claude/x.json` arrived as
            # `M .claude/x.json` and `ln[3:]` read `claude/x.json` - a path that does not
            # exist, so the sibling match could never fire on the one shape the ticket named.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {".claude/x.json": "{}\n"})
            git(repo, "checkout", "-q", "main")
            git(repo, "merge", "-q", "--no-verify", "chore/SCC-11-thing")   # main has the file too
            git(repo, "checkout", "-q", "chore/SCC-11-thing")
            sibling(t, repo, ".claude/x.json", '{"hooks": "edited on the sibling lane"}\n')
            (repo / ".claude" / "x.json").write_text('{"hooks": "edited on the sibling lane"}\n',
                                                     encoding="utf-8")
            st = git(repo, "status", "--porcelain").stdout
            c.check("B5 fixture: the sibling's file is a TRACKED-MODIFIED first line (` M`)",
                    st.startswith(" M .claude/x.json"), repr(st))
            code, out = preflight(repo)
            c.check("SCC-283 a TRACKED-MODIFIED sibling copy on the FIRST status line is owned "
                    "(the ticket's `M .claude/settings.json` shape)",
                    code != 2 and any("chore/SCC-12-other" in ln and "working copy" in ln
                                      for ln in out.splitlines()),
                    f"exit {code}: " + out.strip()[-500:])

        with TempDir() as t:
            # B6 · the SAME parse bug hit the memory ruling: a tracked-modified memory file as the
            # only dirty line read as `M _artifacts/_memory/...` -> `ln[3:]` = `artifacts/...`,
            # which does not start with `_artifacts/_memory/`, so SCC-64's park-don't-sweep
            # instruction was replaced by the generic "commit before merging" - the one
            # instruction that ruling forbids when another session wrote the file.
            repo = make_repo(t)
            branch(repo, "chore/SCC-11-thing", {"_artifacts/_memory/lesson.md": "v1\n"})
            (repo / "_artifacts/_memory/lesson.md").write_text("v2, another session\n",
                                                               encoding="utf-8")
            code, out = preflight(repo)
            c.check("SCC-283 a TRACKED-MODIFIED memory file on the FIRST status line still gets "
                    "the memory ruling, not the generic count",
                    code == 2 and "memory file(s) dirty" in out
                    and "uncommitted change(s)" not in out,
                    f"exit {code}: " + out.strip()[-500:])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
