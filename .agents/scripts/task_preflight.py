"""task_preflight.py — is this TASK branch safe to merge to main, and by WHICH gate? (SCC-49)

`/close-task-merge-tree` closes **Task** work — workflow / IDE / rules / skills changes that
never got an epic and a story, and so can never reach `/sudo-update-sprint-memory`. It merges
to `main`, which makes it the second command in the system allowed anywhere near production,
and that is exactly why its preconditions are a script rather than a checklist.

The load-bearing question is the LANE, and it is the one an agent is worst at answering
honestly about its own work: *does this change reach anything that deploys?*

    LOCAL    - nothing deployable changed. The repo's own enforcement suite IS the whole gate.
    HANDOFF  - a deployable path changed. STOP; this is `/sudo-push-e2e`'s job, not a task.

It is derived from the repo, never asserted:

  * a repo with no deployable surface at all (the command centre - no `frontend/`, no
    `backend/`, and `git-policy.md` says it "has no E2E suite and never will") can only ever
    be LOCAL, so the E2E question does not arise there;
  * a repo that DOES deploy is LOCAL only while the diff stays clear of its deployable dirs.

    task_preflight.py [--repo PATH] [--branch B] [--fetch] [--json]

Exit: 0 clean · 1 warnings · 2 blocking. It reads and reports; it never merges, never
transitions a ticket, and never deletes a branch. The command does those, after this passes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf

# The chore lane's branch shape, from `git-policy.md`: the key sits IMMEDIATELY after the
# prefix (`chore/SCC-11-acli-wrapper`, never `chore/fix-SCC-11`) because Atlassian's GitHub
# app joins on the key as a literal string and reads the branch name too.
BRANCH_RE = re.compile(r"^chore/([A-Z][A-Z0-9]*)-(\d+)-(.+)$")

# Branches this command is deliberately NOT for, and where each one actually goes. A refusal
# that names the right command costs nothing; a bare "wrong branch" sends someone hunting.
WRONG_LANE = {
    "epic/": ("/sudo-push-e2e", "an epic branch ships through the full gate, not this one"),
    "claude/": ("/sudo-update-sprint-memory",
                "a story branch lands on its EPIC branch at close-out, never on main"),
    "incident/": ("/sudo-mobile-error-team", "incident branches have their own lane"),
}

# Directories whose contents deploy. Presence answers "does this repo deploy at all?";
# a diff touching one answers "did THIS change reach it?". Both questions, one list.
DEPLOY_DIRS = ("backend/", "frontend/", "firebase/", "functions/", "mobile/", ".github/")


def git_root(arg: str | None) -> Path:
    """The repo, WITHOUT requiring a sprint board.

    `wf.resolve_project_root` insists on `sprint-status.yaml`, and the command centre
    deliberately has none - which would make the one repo this command runs in most the one
    repo it could not resolve. Same trap `jira_feed.py` hit; same fix.
    """
    start = Path(arg).resolve() if arg else Path.cwd()
    if not start.exists():
        wf.die(f"--repo path does not exist: {start}")
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    wf.die(f"not inside a git repository: {start}")
    raise AssertionError  # unreachable


def repo_keys(repo: Path) -> list[str]:
    """The Jira project keys this repo answers to, from its own `.agents/jira.conf`.

    Sourced as shell by the commit-msg hook, so it is plain `KEY="value"` lines; parsing the
    one line we need is safer than executing the file."""
    conf = repo / ".agents" / "jira.conf"
    if not conf.is_file():
        return []
    m = re.search(r'^\s*JIRA_KEYS\s*=\s*"?([^"\n#]+)"?', wf.read_text(conf), re.MULTILINE)
    return m.group(1).split() if m else []


def rel_or_abs(path: Path, root: Path) -> str:
    """`relative_to` RAISES when the two paths resolve differently - a symlinked checkout,
    or macOS's `/tmp` -> `/private/tmp`. In `jira_feed.py` that traceback killed a whole
    section of a ticket comment. A path is display text here; it is never worth a crash."""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def base_ref(repo: Path) -> str:
    """`origin/main` when there is a remote, else `main`. A repo with no remote is the
    test/offline case, not an error - the ancestry questions below are still answerable."""
    r = wf.git(["rev-parse", "--verify", "--quiet", "origin/main"], repo)
    return "origin/main" if r.returncode == 0 and r.stdout.strip() else "main"


# ── 1. Is this the right branch, in the right shape? ───────────────────────────

def check_branch(repo: Path, branch: str, rep: wf.Report) -> str | None:
    """Returns the Jira key, or None. The key is what every later step is FOR."""
    if branch in ("main", "HEAD"):
        rep.err("branch", f"HEAD is '{branch}' - this command closes a chore branch and "
                          f"merges it INTO main; it never runs standing on main")
        return None
    for prefix, (cmd, why) in WRONG_LANE.items():
        if branch.startswith(prefix):
            rep.err("branch", f"{branch} is not a task branch - {why}. Use {cmd}.")
            return None
    m = BRANCH_RE.match(branch)
    if not m:
        rep.err("branch", f"{branch} is not `chore/<JIRA-KEY>-<slug>` - the key must sit "
                          f"immediately after the prefix or Jira never links the commits")
        return None
    key = f"{m.group(1)}-{m.group(2)}"
    allowed = repo_keys(repo)
    if not allowed:
        rep.warn("branch", f"{key}: no .agents/jira.conf in this repo - the key cannot be "
                           f"checked against the repo's project")
    elif m.group(1) not in allowed:
        # The same rule the armed commit-msg hook enforces. If it were wrong the commits on
        # this branch could not exist, so reaching here means the hook was bypassed.
        rep.err("branch", f"{key} is not one of this repo's projects ({', '.join(allowed)}) "
                          f"- a wrong-project key means these commits skipped the hook")
        return None
    else:
        rep.info("branch", f"{branch} -> {key} (project {m.group(1)} matches this repo)")
    return key


# ── 2. Is the branch clean, pushed, and current with main? ─────────────────────

def check_sync(repo: Path, branch: str, fetch: bool, rep: wf.Report) -> None:
    """`commit-and-push-are-one-action`: clean + 0/0, or the work is not finished. Merging
    an unpushed branch to main puts commits on production that exist on one disk."""
    if fetch:
        f = wf.git(["fetch", "--quiet"], repo, timeout=180)
        if f.returncode != 0:
            rep.warn("sync", "fetch failed - ahead/behind is vs the LAST fetch")
    else:
        rep.info("sync", "no --fetch, ahead/behind is vs the LAST fetch")

    dirty = wf.git(["status", "--porcelain"], repo).stdout.strip()
    if dirty:
        rep.err("sync", f"{len(dirty.splitlines())} uncommitted change(s) - commit "
                        f"(explicit paths) and push before merging")
    else:
        rep.info("sync", "working tree clean")

    counts = wf.git(["rev-list", "--left-right", "--count",
                     f"origin/{branch}...{branch}"], repo)
    if counts.returncode == 0 and counts.stdout.strip():
        behind, ahead = (counts.stdout.split() + ["?", "?"])[:2]
        if ahead != "0" or behind != "0":
            rep.err("sync", f"{branch}: {ahead} ahead / {behind} behind origin")
        else:
            rep.info("sync", f"{branch}: 0/0 with origin")
    else:
        rep.warn("sync", f"{branch}: never pushed - the branch exists on this disk only")


def check_base(repo: Path, branch: str, rep: wf.Report) -> None:
    """Absorb main HERE, so a conflict surfaces on the chore branch and never on main.

    Same reason `/sudo-push-e2e` merges `origin/main` into the epic branch before it gates:
    whatever the gate runs on has to be what the merge will actually produce."""
    base = base_ref(repo)
    ahead = wf.git(["rev-list", "--count", f"{base}..{branch}"], repo)
    n = ahead.stdout.strip() if ahead.returncode == 0 else "?"
    if n == "0":
        rep.err("base", f"{branch} has 0 commits not on {base} - nothing to merge")
    else:
        rep.info("base", f"{branch} is {n} commit(s) ahead of {base}")

    merged = wf.git(["merge-base", "--is-ancestor", base, branch], repo)
    if merged.returncode != 0:
        behind = wf.git(["rev-list", "--count", f"{branch}..{base}"], repo).stdout.strip() or "?"
        rep.err("base", f"{base} has {behind} commit(s) NOT on {branch} - merge {base} into "
                        f"this branch first so conflicts surface here, not on main")
    else:
        rep.info("base", f"{base} is fully absorbed into {branch}")


# ── 3. THE LANE — the one question this script exists to answer ────────────────

def deploy_surface(repo: Path) -> list[str]:
    """Which deployable dirs this repo actually HAS.

    Empty means the repo cannot deploy, so there is no E2E suite for a gate to skip - the
    command centre's case, and the reason `git-policy.md` says its whole gate is
    `run_all.py`. This is derived from the tree so no repo needs a config file saying so."""
    tracked = wf.git(["ls-files"], repo).stdout.splitlines()
    return [d for d in DEPLOY_DIRS if any(p.startswith(d) for p in tracked)]


def check_scope(repo: Path, branch: str, rep: wf.Report) -> tuple[str, list[str]]:
    """Returns (lane, touched). LOCAL merges here; HANDOFF stops and names the command."""
    base = base_ref(repo)
    surface = deploy_surface(repo)
    diff = wf.git(["diff", "--name-only", f"{base}...{branch}"], repo)
    changed = [ln.strip() for ln in diff.stdout.splitlines() if ln.strip()]
    rep.info("scope", f"{len(changed)} file(s) changed vs {base}")

    if not surface:
        rep.info("scope", "this repo has no deployable surface (no "
                          + ", ".join(d.rstrip('/') for d in DEPLOY_DIRS)
                          + ") - there is no E2E suite here to skip")
        return "LOCAL", []

    touched = sorted({d for d in surface for p in changed if p.startswith(d)})
    if touched:
        # NOT a judgment call, and deliberately not overridable by a flag. A task that
        # reaches deployable code is not a task; it is a change to the product, and the
        # product has one road to main.
        rep.err("scope", f"deployable path(s) changed: {', '.join(touched)} - this is NOT "
                         f"task-lane work. STOP and ship it with /sudo-push-e2e.")
        return "HANDOFF", touched
    rep.info("scope", f"repo deploys ({', '.join(surface)}) but this diff touches none of "
                      f"them - the deploy gate cannot be affected by it")
    return "LOCAL", []


# ── 4. Is there a record of what was done? ─────────────────────────────────────

def check_artifacts(repo: Path, key: str | None, rep: wf.Report) -> None:
    """A walkthrough is what the Dev Record points AT, so its absence means the close-out
    would post a record citing nothing. `artifacts-always-first` exempts the plan on this
    lane; it never exempts the walkthrough."""
    if not key:
        return
    root = repo / "_artifacts"
    lower = key.lower()
    # A missing `_artifacts/` tree is NOT "nothing to check" - it is the strongest possible
    # evidence the walkthrough was never written. Reporting it as a warning is how a check
    # goes quiet on precisely the repo that needed it.
    hits = [p for p in root.glob("**/walkthrough.md")
            if lower in str(p.parent).lower() or lower in wf.read_text(p).lower()
            ] if root.is_dir() else []
    if not hits:
        where = "no _artifacts/ tree in this repo" if not root.is_dir() \
            else f"no walkthrough.md mentions {key}"
        rep.err("artifacts", f"{where} - write the walkthrough before closing out; "
                             f"the Dev Record links it")
        return
    for p in hits:
        rep.info("artifacts", rel_or_abs(p, repo))


# ── 5. Anything still holding the branch? ──────────────────────────────────────

def check_worktree(repo: Path, branch: str, rep: wf.Report) -> None:
    """A worktree checked out on this branch blocks `git branch -d` after the merge, and
    deleting through one destroys the shared assets it junctions to
    (`/sudo-close-workingtree` Step 3a)."""
    out = wf.git(["worktree", "list", "--porcelain"], repo).stdout
    # [0] is the MAIN checkout, which is standing on this branch by definition when the
    # command runs from it - reporting that as "a worktree holds your branch" is a warning
    # that fires on every single clean run, and a warning that always fires gets ignored.
    for block in out.split("\n\n")[1:]:
        wt = re.search(r"^worktree (.+)$", block, re.MULTILINE)
        br = re.search(r"^branch refs/heads/(.+)$", block, re.MULTILINE)
        if wt and br and br.group(1).strip() == branch:
            rep.warn("worktree", f"{Path(wt.group(1)).name} is checked out on {branch} - "
                                 f"remove it with /sudo-close-workingtree before deleting "
                                 f"the branch (never delete through its junctions)")


# ── 6. Which gate, exactly ─────────────────────────────────────────────────────

def gate_plan(repo: Path, lane: str) -> list[str]:
    """The commands the caller must actually run. Printed rather than executed: this script
    reports, and a gate that a preflight ran quietly is a gate nobody read the output of."""
    if lane != "LOCAL":
        return ["/sudo-push-e2e   (the full gate: suite + build + /sudo-e2e GREEN)"]
    plan: list[str] = []
    if (repo / ".agents/scripts/tests/run_all.py").is_file():
        plan.append("python3 .agents/scripts/tests/run_all.py")
    if (repo / ".agents/scripts/workflow_lint.py").is_file():
        plan.append("python3 .agents/scripts/workflow_lint.py")
    if not plan:
        plan.append("(no enforcement suite in this repo - say so; do not report a gate "
                    "that did not run)")
    return plan


def main() -> int:
    ap = argparse.ArgumentParser(description="Task close-out preflight (SCC-49)")
    ap.add_argument("--repo", help="repo root; default: walk up from cwd")
    ap.add_argument("--branch", help="branch to close; default: current HEAD")
    ap.add_argument("--fetch", action="store_true", help="fetch first (network)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = git_root(args.repo)
    branch = args.branch or wf.git(["rev-parse", "--abbrev-ref", "HEAD"], repo).stdout.strip()

    rep = wf.Report()
    key = check_branch(repo, branch, rep)
    check_sync(repo, branch, args.fetch, rep)
    check_base(repo, branch, rep)
    lane, touched = check_scope(repo, branch, rep)
    check_artifacts(repo, key, rep)
    check_worktree(repo, branch, rep)
    plan = gate_plan(repo, lane)

    if args.json:
        print(json.dumps({"repo": str(repo), "branch": branch, "key": key, "lane": lane,
                          "deployable_touched": touched, "gate": plan,
                          "findings": rep.items, "exit": rep.exit_code()}, indent=2))
    else:
        rep.print_human(f"task preflight - {branch}")
        print(f"LANE: {lane}")
        for cmd in plan:
            print(f"  gate: {cmd}")
        e, _ = rep.counts()
        print("VERDICT: " + ("BLOCKED - resolve the errors above" if e
                             else "clear to close out and merge"))
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
