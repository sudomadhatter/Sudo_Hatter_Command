"""check_maps.py must not confuse a MEMORY named in prose with a session folder on disk.

The depth-3 reconciler extracts every backticked token from every INDEX table row and asks
"is this a session folder that no longer exists?". The classifier it asks with,
SESSION_FOLDER_RE, was written to sort DIRECTORY NAMES; pointing it at arbitrary prose makes
any memory whose slug starts with `story-`, `tea-`, `epic-`, `autopilot-`, `wave-` or
`close-out-` look like a folder that has gone missing.

That is not a theoretical collision. On 2026-08-11 the combined gate on `main` reported
`stale row \x60tea-retrofit-active-initiative/\x60 (folder not on disk)` for a row whose prose
cites the memory `tea-retrofit-active-initiative` — 9 memories in the lobby store carry a
matching prefix. Ledger rows exist to explain WHY a decision was made, and naming the memory a
decision rests on is exactly what they are for, so the gate was punishing the behaviour the
convention asks for.

Both halves are asserted here. A gate that stops crying wolf by going blind is not a fix:
case D proves a genuinely stale session row is STILL reported.

Stdlib only, no pytest — same constraint as the script under test.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir, run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_maps import _check_depth3_tree, check_level2_indexes, find_indexes  # noqa: E402

MEMORY_PREFIXED = [
    "tea-retrofit-active-initiative",
    "story-status-flip-contract",
    "autopilot-glm-hybrid-lane",
    "close-out-command-is-daniels-signoff",
]


def _bucket(root: Path, sessions: list[str], index_body: str) -> Path:
    """A depth-3 bucket: <root>/_artifacts/_main/ with >=2 session folders and an INDEX."""
    bucket = root / "_artifacts" / "_main"
    for s in sessions:
        (bucket / s).mkdir(parents=True, exist_ok=True)
    (bucket / "INDEX.md").write_text(index_body, encoding="utf-8")
    return bucket


def _problems(root: Path) -> list[str]:
    return _check_depth3_tree(root, root / "_artifacts")


def main() -> int:
    c = Cases("check_maps")
    sessions = ["2026-08-11_scc-88-memory-relocation-sweep", "2026-08-11_scc-90-sop-restructure"]
    rows = (
        "# _main — INDEX\n\n| Session folder | What | Artifacts |\n|---|---|---|\n"
        f"| `{sessions[0]}/` | did a thing | walkthrough |\n"
        f"| `{sessions[1]}/` | did another | walkthrough |\n"
    )

    # ── A: the live regression — a memory cited in prose is not a missing folder ──────────
    for slug in MEMORY_PREFIXED:
        with TempDir() as root:
            body = rows.replace(
                "| did a thing |",
                f"| the ruling rests on `{slug}`, which stays in the lobby |",
            )
            _bucket(root, sessions, body)
            probs = _problems(root)
            stale = [p for p in probs if "stale row" in p]
            c.check(
                f"A a memory named in prose (`{slug}`) is not reported stale",
                not stale,
                f"got {stale[0]}" if stale else "",
            )

    # ── B: it must not swing the other way and start MISSING real folders ────────────────
    with TempDir() as root:
        body = rows.replace("| did a thing |", "| see `tea-retrofit-active-initiative` |")
        _bucket(root, sessions, body)
        probs = _problems(root)
        missing = [p for p in probs if "missing row" in p]
        c.check("B both real session folders still count as mentioned", not missing,
                f"got {missing}" if missing else "")

    # ── C: a memory slug in a NON-table line was never the problem, and still is not ─────
    with TempDir() as root:
        _bucket(root, sessions, rows + "\nSee also `story-artifacts-two-doc-close` for the why.\n")
        c.check("C a backticked slug outside any table row is ignored",
                not [p for p in _problems(root) if "stale row" in p])

    # ── D: THE MIRROR — a genuinely stale session row is STILL reported ──────────────────
    #     Without this, the fix could be "stop reporting stale rows" and case A would pass.
    with TempDir() as root:
        ghost = "2026-08-04_a-session-folder-that-was-deleted"
        _bucket(root, sessions, rows + f"| `{ghost}/` | landed and its folder was removed | walkthrough |\n")
        probs = [p for p in _problems(root) if "stale row" in p]
        c.check("D a real stale session row IS still reported (the gate kept its teeth)",
                any(ghost in p for p in probs),
                f"probs={probs}")

    # ── E: and a genuinely missing row is still reported ─────────────────────────────────
    with TempDir() as root:
        body = (
            "# _main — INDEX\n\n| Session folder | What | Artifacts |\n|---|---|---|\n"
            f"| `{sessions[0]}/` | only one row for two folders | walkthrough |\n"
        )
        _bucket(root, sessions, body)
        probs = [p for p in _problems(root) if "missing row" in p]
        c.check("E a session folder with no row IS still reported",
                any(sessions[1] in p for p in probs), f"probs={probs}")

    # ── F: the live tree — main itself must be clean of phantom stales ───────────────────
    repo = Path(__file__).resolve().parents[3]
    live = [p for p in _check_depth3_tree(repo, repo / "_artifacts") if "stale row" in p]
    c.check("F the live _artifacts tree reports no stale rows", not live, f"got {live}")

    # ── F2 · ⭐ SCC-139 — the OTHER half of the same contract, which nothing asserted ──────
    # Case F pinned "no STALE rows" and stopped there. Nothing asserted "no MISSING rows",
    # so a session folder with no INDEX row passed the whole suite - which is exactly how
    # SCC-124 landed one and how SCC-119 nearly did, both at 21/21 PASS. Half a contract
    # under test reads identically to a whole one right up until the day it doesn't.
    live_missing = [p for p in _check_depth3_tree(repo, repo / "_artifacts") if "missing row" in p]
    c.check("F2 the live _artifacts tree reports no MISSING rows", not live_missing,
            f"got {live_missing} - add the INDEX row before closing out")

    # ...and the teeth, ON THE LIVE TREE. A fixture-only assertion is precisely what left
    # this hole open, so the folder is seeded into the real _artifacts and removed again.
    # ⛔ THE TEARDOWN IS GUARDED ON "WE CREATED IT" (SCC-140 review). The first cut ran
    # `probe.rmdir()` in a bare `finally`, so if the directory ALREADY existed the `mkdir`
    # raised FileExistsError and the finally then DELETED SOMEBODY ELSE'S DIRECTORY on the way
    # out. Measured, not theorised. A test that mutates the live tree has to be able to say
    # exactly what it owns.
    probe = repo / "_artifacts" / "_main" / "2026-08-13_scc-139-liveness-probe"
    created = False
    try:
        try:
            probe.mkdir(parents=True, exist_ok=False)
            created = True
        except FileExistsError:
            pass
        c.check("F2 the live probe directory is ours to create", created,
                f"{probe} already existed - a previous run was killed before its teardown. "
                f"Remove it by hand; this case will not delete a directory it did not make.")
        if created:
            seeded = [p for p in _check_depth3_tree(repo, repo / "_artifacts")
                      if "missing row" in p]
            c.check("F2 ...and a rowless folder seeded into the LIVE tree IS reported",
                    any(probe.name in p for p in seeded),
                    f"got {seeded} - without this, F2 above passes by having nothing to find")
    finally:
        if created:
            probe.rmdir()

    # ── L · ⭐ SCC-139 — SCAN_IGNORES, which had ZERO coverage ────────────────────────────
    # It rode in on SCC-135 as a carried operator change with no acceptance item and no test.
    #
    # ⛔ Driven through its REAL consumers - `check_level2_indexes` and `find_indexes` - and
    # NOT through the close-out gate. `_check_depth3_tree` never reads SCAN_IGNORES (it filters
    # on `_archived` and dotfiles only), so an assertion routed through `--depth3-only` would
    # pass no matter what the set contained: a vacuous green inside the ticket that exists to
    # kill vacuous greens. Characterization, so it is green-first by design; the mutation below
    # is what proves it is load-bearing.
    with TempDir() as root:
        # `Projects` IS in SCAN_IGNORES - separate repos, own maps, own linter.
        (root / "Projects" / "SomeProject").mkdir(parents=True)
        # `workspace` is NOT - an ordinary level-2 folder, which owes an INDEX.md.
        (root / "workspace" / "a-real-folder").mkdir(parents=True)
        probs = check_level2_indexes(root)
        c.check("L an ignored dir (Projects/) is NOT required to carry an INDEX",
                not any("Projects/" in p for p in probs), f"got {probs}")
        c.check("L ...while a non-ignored level-2 folder still IS (the mirror)",
                any("workspace/a-real-folder" in p for p in probs), f"got {probs}")

    with TempDir() as root:
        (root / "node_modules" / "pkg").mkdir(parents=True)
        (root / "node_modules" / "pkg" / "INDEX.md").write_text("# vendor\n", encoding="utf-8")
        (root / "real").mkdir()
        (root / "real" / "INDEX.md").write_text("# ours\n", encoding="utf-8")
        found = [p.as_posix() for p in find_indexes(root)]
        c.check("L find_indexes skips an INDEX.md inside an ignored dir",
                not any("node_modules" in p for p in found), f"got {found}")
        c.check("L ...and still collects the real one", any("/real/INDEX.md" in p for p in found),
                f"got {found}")

    # ── G–J · ⭐ SCC-138 — the lane gate can FAIL on a drifted index ──────────────────────
    # `gate_plan()` built the Task lane's gate from run_all + workflow_lint only, so the
    # close-out printed "clear to close out and merge" over a repo whose own linter was RED.
    # It happened twice in one day: SCC-124 landed a session folder with no INDEX row and
    # SCC-119 nearly did, both while run_all reported 21/21 PASS.
    #
    # ⛔ Why the gate runs `--depth3-only --strict` and NOT bare `check_maps`: the close-out
    # runs from a WORKTREE, and there bare check_maps exits 1 on two GUARANTEED false
    # positives — "AUTO block is STALE" and "on disk but not in map: <lane-name>/" — whose
    # printed remedy would ship the lane name into the map bound for main. Those live in the
    # repo-map comparison; `--depth3-only` runs the depth-3 INDEX reconciliation ALONE, which
    # reads only `root/` and never the CWD. Case K proves both halves against a real worktree.
    drifted = ["2026-08-11_scc-88-memory-relocation-sweep", "2026-08-11_scc-90-sop-restructure"]
    one_row = (
        "# _main — INDEX\n\n| Session folder | What | Artifacts |\n|---|---|---|\n"
        f"| `{drifted[0]}/` | only one row for two folders | walkthrough |\n"
    )

    with TempDir() as root:
        _bucket(root, drifted, one_row)
        rc, out = run_script("check_maps.py", "--root", str(root), "--depth3-only", "--strict")
        c.check("G --depth3-only --strict EXITS 1 on a missing INDEX row", rc == 1,
                f"rc={rc} - a gate that cannot fail is worse than no gate; out={out[:200]}")
        c.check("G and it names the folder that has no row", drifted[1] in out, out[:200])

    with TempDir() as root:
        _bucket(root, drifted, one_row)
        rc, _ = run_script("check_maps.py", "--root", str(root), "--depth3-only")
        c.check("H bare --depth3-only STILL exits 0 on the same drift", rc == 0,
                f"rc={rc} - SessionStart runs this as a nag; making it block would gate boot")

    with TempDir() as root:
        _bucket(root, drifted, one_row.replace("only one row for two folders", "a")
                + f"| `{drifted[1]}/` | b | walkthrough |\n")
        rc, _ = run_script("check_maps.py", "--root", str(root), "--depth3-only", "--strict")
        c.check("I --strict exits 0 on a CLEAN tree", rc == 0,
                f"rc={rc} - a gate that fires on a clean repo is noise, and noise gets disabled")

    with TempDir() as root:
        # F7 — empty input must not be a silent pass by accident. A workspace with no
        # _artifacts/ has nothing that CAN drift, so 0 is right; assert it deliberately
        # rather than leave it reading as the vacuous-gate tripwire.
        rc, _ = run_script("check_maps.py", "--root", str(root), "--depth3-only", "--strict")
        c.check("J --strict on a workspace with no _artifacts/ exits 0 (nothing can drift)",
                rc == 0, f"rc={rc}")

    # ── J2 · `--strict` ALONE is refused, not silently reinterpreted (SCC-140 review) ─────
    # It is read only inside the --depth3-only branch, so on its own it used to be accepted
    # and run the FULL linter instead — which from a worktree exits 1 on the two documented
    # false positives whose printed remedy ships the lane name into the map. A flag that
    # quietly does something ELSE is worse than one that refuses. Caught by mutation: the
    # refusal shipped with no assertion behind it, and the mutant survived until this case.
    with TempDir() as root:
        _bucket(root, drifted, one_row)
        rc, out = run_script("check_maps.py", "--root", str(root), "--strict")
        c.check("J2 --strict without --depth3-only is REFUSED", rc == 2, f"rc={rc}")
        c.check("J2 ...and the refusal names the combination that works",
                "--depth3-only --strict" in out, out[-200:])

    # ── K · ⛔ THE WORKTREE PROOF — why the gate is a SUBSET and not the whole linter ──────
    # SCC-138 acceptance: "Proven from inside a worktree - the false-positive rows do not
    # block, and the real ones do." This cannot be shown on a synthetic fixture: the two
    # false positives come from the repo-map comparison, which needs the real map. So it runs
    # against a REAL detached worktree of this repo - the same thing a close-out stands in.
    #
    # Both halves are asserted, and the first is what makes the second mean anything: if bare
    # check_maps ever stops exiting 1 here, the subset is no longer buying anything and this
    # case says so instead of quietly passing.
    #
    # ⚠ POSIX only. `is_executable` aside, the teardown is the problem: on Windows a pruned
    # worktree leaves a directory shell that blocks a later `worktree add`, and only PowerShell
    # removes it. Skipped rather than shipped red on the machine that cannot clean up after it.
    if os.name != "nt" and (repo / ".git").exists():
        with TempDir() as tmp:
            wt = tmp / "lane-probe"
            add = subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach",
                                  str(wt), "HEAD"], capture_output=True, text=True)
            if add.returncode != 0:
                c.check("K worktree fixture could be created", False, add.stderr.strip()[:200])
            else:
                try:
                    # ⛔ Point the WORKING COPY of the script at the worktree, rather than
                    # running the worktree's own copy. `git worktree add` checks out HEAD, so
                    # the worktree carries the COMMITTED script - a test written this way goes
                    # green only after the commit that introduces the flag, which makes it
                    # useless during the change it exists to prove. `root` is resolved from
                    # --root here and from the script's own location otherwise, so a worktree
                    # path as --root reproduces exactly the condition under test: a workspace
                    # whose basename is the lane name.
                    bare_rc, bare_out = run_script("check_maps.py", "--root", str(wt))
                    strict_rc, strict_out = run_script("check_maps.py", "--root", str(wt),
                                                       "--depth3-only", "--strict")
                    c.check("K bare check_maps on a worktree FALSE-BLOCKS (this is why --depth3-only)",
                            bare_rc == 1,
                            f"rc={bare_rc} - if this ever passes, the subset buys nothing "
                            f"and the gate should just run the whole linter")
                    c.check("K ...and the false positive names the LANE, whose remedy would "
                            "ship that name to main",
                            "not in map" in bare_out or "AUTO block" in bare_out,
                            bare_out[-300:])
                    # The property is "the false-positive rows do not block", NOT "exit 0" -
                    # HEAD may carry genuine depth-3 drift, and that SHOULD block. Asserting
                    # the exit code would couple this case to whatever the tree happens to
                    # hold; asserting the rows proves the actual contract either way.
                    c.check("K --depth3-only --strict reports NEITHER worktree false positive",
                            "AUTO block" not in strict_out and "not in map" not in strict_out,
                            f"the close-out gate must not fire on an artefact of standing in "
                            f"a worktree; out={strict_out[-300:]}")

                    # ...and the mirror, or "reports nothing" would pass by going blind.
                    ghost = wt / "_artifacts" / "_main" / "2026-08-13_no-row-for-this-one"
                    ghost.mkdir(parents=True, exist_ok=True)
                    real_rc, real_out = run_script("check_maps.py", "--root", str(wt),
                                                   "--depth3-only", "--strict")
                    c.check("K ...and a REAL missing row still blocks from inside the worktree",
                            real_rc == 1 and "2026-08-13_no-row-for-this-one" in real_out,
                            f"rc={real_rc} out={real_out[-300:]}")
                finally:
                    # ⛔ `remove --force` ONLY — never a bare `worktree prune` (SCC-140 review).
                    # `prune` is REPO-WIDE: it deregisters every worktree whose directory is
                    # currently missing, which in this system is a real state (an external
                    # volume, or the known "pruned worktree leaves a blocking shell" case). A
                    # sibling lane losing its registration as a side effect of someone running
                    # the test suite is a far worse outcome than a stale entry here, and
                    # `remove --force` already deregisters the one we created.
                    subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force",
                                    str(wt)], capture_output=True)

    # ── CM10 · SCC-290 · check 10, doc-graph freshness — and the PROJECT SKIP ────────────────
    # ⛔ THE SKIP IS THE FINDING (audit F1). `check_maps --all` fans out over every conformant
    # project and NO project carries a doc graph. Armed unconditionally, check 10 prints FAIL for
    # every project on the operator's next ceremony — and the natural "fix" is to generate a 200 KB
    # graph inside a repo where nothing reads it. Check 9 already takes this shape.
    # CM10 · SCC-290 · doc-graph freshness fails on drift, and is SILENT where absent
    import check_maps as cm
    import refresh_maps as rm

    with TempDir() as root:
        # a root with no docs/doc-graph.md at all — every project on the fan-out
        (root / "docs").mkdir(parents=True)
        c.check("CM10 A ⛔ a workspace with no doc graph reports NOTHING (the project skip)",
                cm.check_doc_graph_fresh(root) == [], str(cm.check_doc_graph_fresh(root)))

    with TempDir() as root:
        # a root that HAS one, and it disagrees with the tree
        (root / "docs").mkdir(parents=True)
        (root / ".agents" / "rules").mkdir(parents=True)
        (root / ".agents" / "rules" / "a.md").write_text("# a\n", encoding="utf-8")
        (root / "docs" / "doc-graph.md").write_text("stale, and not even the right shape\n",
                                                    encoding="utf-8")
        probs = cm.check_doc_graph_fresh(root)
        c.check("CM10 B a workspace WITH a doc graph is checked, and drift is reported",
                any("doc-graph.md" in p and "STALE" in p for p in probs), str(probs))
        c.check("CM10 C the report names the regeneration command",
                any("refresh_maps.py --staged" in p for p in probs), str(probs))

        # and it goes quiet once the tree agrees
        for rel, text in rm.regenerate(root, {"doc-graph"}).items():
            (root / rel).write_text(text, encoding="utf-8")
        c.check("CM10 D once regenerated, check 10 is clean",
                cm.check_doc_graph_fresh(root) == [], str(cm.check_doc_graph_fresh(root)))

    c.check("CM10 E check 10 is WIRED into the FATAL drift dict, not the hint section",
            "drift[\"doc-graph freshness\"]" in
            (Path(cm.__file__).read_text(encoding="utf-8")),
            "a check that cannot fail the lint is not a gate")
    # ── CM-LABEL · SCC-290 · the worktree false positive check 1 has always had ──────────────
    # `build_auto_body` labelled the tree with `Path(root).name` — the WORKTREE directory basename
    # — so check 1 reported "AUTO block is STALE / in map but not on disk: <repo>/" from every
    # lane, and its printed remedy would have shipped the lane name into the map bound for main.
    # SCC-290 had to retire it: `refresh_maps --verify` runs at PUSH and every push here is from a
    # worktree, so a per-tree label would have refused every push in the system.
    # CM-LABEL · SCC-290 · the repo-map's root label is stable across worktrees
    import generate_repo_map as grm
    with TempDir() as root:
        main_co = root / "Repo_Name"
        main_co.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(main_co),
                       capture_output=True)
        (main_co / "seed.txt").write_text("x\n", encoding="utf-8")
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        subprocess.run(["git", "add", "seed.txt"], cwd=str(main_co), capture_output=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=str(main_co), env=env,
                       capture_output=True)
        wt = root / "lane-slug-that-is-not-the-repo"
        r = subprocess.run(["git", "worktree", "add", "-q", str(wt), "-b", "chore/x"],
                           cwd=str(main_co), env=env, capture_output=True, text=True)
        if r.returncode != 0:
            c.check("CM-LABEL SKIPPED - git worktree add failed here", True, r.stderr[-200:])
        else:
            c.check("CM-LABEL from the main checkout the label is the repo name",
                    grm.repo_label(main_co) == "Repo_Name", grm.repo_label(main_co))
            c.check("CM-LABEL ⛔ from a WORKTREE it is the SAME string, not the lane slug",
                    grm.repo_label(wt) == "Repo_Name",
                    f"{grm.repo_label(wt)!r} (dir basename is {wt.name!r})")
            c.check("CM-LABEL so the AUTO block's first line matches from both trees",
                    grm.build_auto_body(str(main_co), 8, "auto", set()).splitlines()[5]
                    == grm.build_auto_body(str(wt), 8, "auto", set()).splitlines()[5],
                    "the map changes identity depending on who regenerated it")
    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
