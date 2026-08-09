"""task_preflight.py must never let deployable code reach `main` through the task lane.

`/close-task-merge-tree` merges to `main`. Everything else that does (`/sudo-push-e2e`) runs
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


def make_repo(root: Path, *, deployable: bool = False, remote: bool = True,
              walkthrough: bool = True) -> Path:
    """A repo standing on `main`, optionally with a bare origin it is in sync with."""
    repo = root / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "config", "commit.gpgsign", "false")
    write(repo, ".agents/jira.conf", JIRA_CONF)
    write(repo, ".agents/scripts/tests/run_all.py", "# fixture\n")
    write(repo, "README.md", "# fixture\n")
    if deployable:
        write(repo, "backend/app.py", "x = 1\n")
        write(repo, "frontend/page.tsx", "export default () => null\n")
    if walkthrough:
        write(repo, "_artifacts/_main/2026-08-08_scc-11-thing/walkthrough.md", WALKTHROUGH)
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


def preflight(repo: Path, *extra: str) -> tuple[int, str]:
    return run_script("task_preflight.py", "--repo", str(repo), *extra)


def main() -> int:
    c = Cases("task_preflight")

    # ── THE load-bearing negative: deployable code cannot ride the task lane ──
    with TempDir() as t:
        repo = make_repo(t, deployable=True)
        branch(repo, "chore/SCC-11-thing", {"backend/app.py": "x = 2\n"})
        code, out = preflight(repo)
        c.check("deployable diff -> HANDOFF", "LANE: HANDOFF" in out, out.strip()[-200:])
        c.check("deployable diff -> exit 2", code == 2, f"exit {code}")
        c.check("handoff names /sudo-push-e2e", "/sudo-push-e2e" in out)
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
    for name, expect in (("epic/SCC-11-thing", "/sudo-push-e2e"),
                         ("claude/SCC-11-thing", "/sudo-update-sprint-memory"),
                         ("incident/SCC-11-thing", "/sudo-mobile-error-team")):
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
        repo = make_repo(t, walkthrough=False)
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

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
