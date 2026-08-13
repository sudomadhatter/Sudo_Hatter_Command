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
import os
import stat
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir, run_script

JIRA_CONF = '# test fixture\nJIRA_KEYS="SCC"\n'

WALKTHROUGH = """---
type: walkthrough
story: SCC-11
---

# SCC-11 — a task

## Task Checklist
- [x] did the thing
"""


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit(repo: Path, message: str) -> None:
    git(repo, "add", "-A")            # fixture only; the real lane is explicit-paths
    git(repo, "commit", "--no-verify", "-q", "-m", message)


MANIFEST = ("task_key: SCC-11\nprimary_repo: repo\nbranch: chore/SCC-11-thing\n"
            "close_command: smh-close-task-merge-tree\nsecondary_repos: []\n")


def make_repo(root: Path, *, deployable: bool = False, remote: bool = True,
              walkthrough: bool = True, manifest: bool = True, hooks: bool = True,
              ci: bool = False) -> Path:
    """A repo standing on `main`, optionally with a bare origin it is in sync with."""
    repo = root / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "config", "commit.gpgsign", "false")
    write(repo, ".agents/jira.conf", JIRA_CONF)
    write(repo, ".agents/scripts/tests/run_all.py", "# fixture\n")
    # SCC-110: a repo carrying `.agents/jira.conf` is CLAIMING a commit gate, so the fixture
    # has to carry the hook that enforces it and the per-machine switch that runs it. Without
    # these the fixture modelled a repo in a state none of the real ones are in — declared
    # gates, nothing running them — and the arm-check rightly objected.
    if hooks:
        write(repo, ".githooks/commit-msg", "#!/bin/sh\nexit 0\n")
        (repo / ".githooks/commit-msg").chmod(0o755)
        git(repo, "config", "core.hooksPath", ".githooks")
    write(repo, "README.md", "# fixture\n")
    if deployable:
        write(repo, "backend/app.py", "x = 1\n")
        write(repo, "frontend/page.tsx", "export default () => null\n")
    if ci:
        # A repo carrying CI. Independent of `deployable` on purpose: the whole point of
        # SCC-118's split is that these two are different questions, and the fixture has to
        # be able to ask them separately.
        write(repo, ".github/workflows/gate.yml", "name: gate\non: [push]\n")
    if walkthrough:
        write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/walkthrough.md", WALKTHROUGH)
    if manifest:
        write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml", MANIFEST)
    commit(repo, "SCC-11 chore: base")
    if remote:
        bare = root / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], capture_output=True)
        git(repo, "remote", "add", "origin", str(bare))
        git(repo, "push", "-q", "-u", "origin", "main")
    return repo


def branch(repo: Path, name: str, files: dict[str, str], *, push: bool = True) -> None:
    git(repo, "checkout", "-q", "-b", name)
    for rel, text in files.items():
        write(repo, rel, text)
    commit(repo, "SCC-11 chore: the work")
    if push:
        git(repo, "push", "-q", "-u", "origin", name)


# ── The board stub (SCC-119) ───────────────────────────────────────────────────
# `check_children` is the first thing in this script that talks to the network, and these
# fixtures use REAL Jira keys (SCC-11 exists). Without a stub the suite would query the live
# board once per preflight - slow, machine-dependent, and green or red by accident. The stub
# is a real executable for the same reason jira_feed's is: the production path (subprocess,
# --json, exit code) then runs unchanged.
BOARD_STUB = r'''
import json, os, sys
state = json.load(open(os.environ["PF_BOARD_STATE"], encoding="utf-8"))
args = sys.argv[1:]
if args[:3] != ["jira", "workitem", "search"]:
    print("stub: unhandled " + " ".join(args), file=sys.stderr)
    sys.exit(9)
fields = ""
if "--fields" in args:
    fields = args[args.index("--fields") + 1]
# The real acli REJECTS `parent` as a --fields value on search (exit 1). Enforced here so a
# caller that asks for it fails in the suite exactly as it would in production - otherwise
# the natural mistake reads as "no children" and the gate passes vacuously.
if "parent" in [f.strip() for f in fields.split(",")]:
    print("Error: field 'parent' is not allowed", file=sys.stderr)
    sys.exit(1)
if state.get("fail"):
    print("Error: the search failed", file=sys.stderr)
    sys.exit(1)
print(json.dumps([{"key": k, "fields": {"status": {"name": s}, "summary": "child"}}
                  for k, s in state.get("children", [])]))
'''


def board(root: Path, children: object = (), fail: bool = False) -> None:
    """Point ACLI_BIN at a stub board holding `children` = [(key, status), ...]."""
    stub_py = root / "board_stub.py"
    stub_py.write_text(BOARD_STUB, encoding="utf-8")
    if os.name == "nt":
        launcher = root / "acli.bat"
        launcher.write_text(f'@echo off\r\n"{sys.executable}" "{stub_py}" %*\r\n',
                            encoding="utf-8")
    else:
        launcher = root / "acli"
        launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{stub_py}" "$@"\n',
                            encoding="utf-8")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    state = root / "board_state.json"
    state.write_text(json.dumps({"children": list(children), "fail": fail}),
                     encoding="utf-8")
    os.environ["ACLI_BIN"] = str(launcher)
    os.environ["PF_BOARD_STATE"] = str(state)


def preflight(repo: Path, *extra: str, expect: str = "SCC-11") -> tuple[int, str]:
    # --expect-key is REQUIRED since SCC-64; the fixtures' branches carry SCC-11.
    # A childless board by default, unless this repo's test set one up - so every pre-SCC-119
    # case keeps its exact verdict and none of them reach the real network.
    #
    # ⚠ Test the FILE, not the env var. Each block runs in its own TempDir, so the state file
    # is deleted at the end of the block while `os.environ` survives the whole process - an
    # env-var-only guard left every later block pointing at a path that no longer exists, the
    # stub crashed, and eleven previously-clean cases went red for a reason that had nothing
    # to do with what they test.
    state = os.environ.get("PF_BOARD_STATE")
    if not state or not Path(state).exists():
        board(repo.parent)
    return run_script("task_preflight.py", "--repo", str(repo),
                      "--expect-key", expect, *extra)


def main() -> int:
    c = Cases("task_preflight")

    # ── THE load-bearing negative: deployable code cannot ride the task lane ──
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
    with TempDir() as t:
        repo = make_repo(t, deployable=True)
        branch(repo, "chore/SCC-11-thing", {".agents/rules/x.md": "rule\n"})
        code, out = preflight(repo)
        c.check("docs-only diff in a deploying repo -> LOCAL", "LANE: LOCAL" in out)
        c.check("docs-only diff -> exit 0", code == 0, out.strip()[-300:])
        c.check("says the deploy gate cannot be affected",
                "touches none of them" in out, out.strip()[-300:])

    # ── SCC-118: `.github/` is a deploy surface only where something SHIPS ────────────
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
    for name, expect in (("epic/SCC-11-thing", "/cicd-push-e2e"),
                         ("claude/SCC-11-thing", "/cicd-update-sprint-memory"),
                         ("incident/SCC-11-thing", "/cicd-mobile-error-team")):
        with TempDir() as t:
            repo = make_repo(t)
            branch(repo, name, {"docs/x.md": "x\n"})
            code, out = preflight(repo)
            c.check(f"{name.split('/')[0]}/ branch refused", code == 2, f"exit {code}")
            c.check(f"{name.split('/')[0]}/ refusal names {expect}", expect in out)

    with TempDir() as t:
        repo = make_repo(t)
        code, out = preflight(repo, "--branch", "main")
        c.check("standing on main is refused", code == 2 and "never runs standing on main" in out,
                out.strip()[-200:])

    # ── Branch shape: the key must sit immediately after the prefix ──
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

    # ── Regression: the MAIN checkout is not "a worktree holding your branch" ──
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

    # ── SCC-110 · the whole point, end to end ────────────────────────────────────────────
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
    with TempDir() as t:
        repo = make_repo(t, manifest=False)
        branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
        code, out = preflight(repo)
        c.check("SCC-64 a missing manifest warns with the schema, never blocks",
                code == 1 and "no task.yaml declares task_key: SCC-11" in out,
                out.strip()[-400:])

    # ── SCC-113 H-1: a receipt already ON the mainline is a landed lane's, not drift ──
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
    with TempDir() as t:
        repo = make_repo(t)
        write(repo, ".agents/scripts/workflow_lint.py", "# fixture\n")
        commit(repo, "SCC-11 chore: lint fixture")
        git(repo, "push", "-q", "origin", "main")
        branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
        code, out = preflight(repo)
        c.check("SCC-64 no-deploy repo prints workflow_lint --toolkit-only",
                "workflow_lint.py --toolkit-only" in out, out.strip()[-300:])

    # ── SCC-94: secondary_repos was documented in three places and read by NOTHING ──
    # A cross-repo task could declare "this also lands in <repo> under <KEY>" and close out green
    # while that key was one the repo's hook rejects, the branch was never pushed, or the half was
    # not even checked out. The positive control matters as much as the refusals: a correctly
    # declared secondary repo must still exit 0, or this becomes "always stop" and gets designed
    # around inside a week - the same argument the deployable-lane cases above are built on.

    def secondary(t: Path, *, keys: str = "AVCH", clean: bool = True, pushed: bool = True,
                  store: str | None = "ok", checked_out: bool = True) -> Path:
        """A sibling repo under `Projects/`, like a real submodule checkout.

        `Projects/` is gitignored in the primary so the sibling reads as untracked-but-clean -
        which is what `ignore = all` produces for real, and is exactly why the primary's own
        `git status` cannot see a dirty project half."""
        proj = t / "repo" / "Projects" / "SECONDARY"
        proj.mkdir(parents=True)
        if not checked_out:
            return proj                                   # an empty stub: submodule not init'd
        git(proj, "init", "-q", "-b", "main")
        git(proj, "config", "user.email", "t@example.com")
        git(proj, "config", "user.name", "T")
        git(proj, "config", "commit.gpgsign", "false")
        write(proj, ".agents/jira.conf", f'JIRA_KEYS="{keys}"\n')
        write(proj, "README.md", "# secondary\n")
        if store:
            mem = "_artifacts/_memory"
            write(proj, f"{mem}/a-fact.md",
                  "---\nname: a-fact\ndescription: one fact\n---\n\nThe fact.\n")
            # "broken" seeds an ORPHAN: a memory file with no index line, invisible to every
            # session. Same defect check_store() catches in the lobby - the point of this case
            # is that here it must BLOCK, not merely be reported.
            index = "# Index\n- [A fact](a-fact.md) - hook\n" if store == "ok" else "# Index\n"
            write(proj, f"{mem}/MEMORY.md", index)
        commit(proj, "AVCH-1 chore: base")
        bare = t / "secondary-origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], capture_output=True)
        git(proj, "remote", "add", "origin", str(bare))
        if pushed:
            git(proj, "push", "-q", "-u", "origin", "main")
        if not clean:
            write(proj, "uncommitted.md", "in flight\n")
        return proj

    def with_secondary(t: Path, ticket: str = "AVCH-53", **kw) -> Path:
        repo = make_repo(t)
        write(repo, ".gitignore", "Projects/\n")
        write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/task.yaml",
              "task_key: SCC-11\nprimary_repo: repo\nbranch: chore/SCC-11-thing\n"
              "close_command: smh-close-task-merge-tree\nsecondary_repos:\n"
              f"  - repo: Projects/SECONDARY\n    landing: independent-task\n"
              f"    ticket: {ticket}\n")
        commit(repo, "SCC-11 chore: declare the secondary repo")
        git(repo, "push", "-q", "origin", "main")
        branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
        secondary(t, **kw)
        return repo

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

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
