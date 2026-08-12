"""main_write_gate.py — the SERVER-SIDE half of the `main` write gate (SCC-118, 2026-08-12).

  ── WHY THIS EXISTS AT ALL ─────────────────────────────────────────────────────────────────
SCC-77 built a gate for `main`. It is a git hook, so it lives on a machine, and it runs at
`git push`. A merge performed on GitHub's servers — the web *Merge pull request* button, or the
REST API — never touches a machine. The hook is not bypassed there; it is ABSENT. There is
nothing to bypass.

Demonstrated 2026-08-12: PR #2 merged to `main` as `dabb3c3` from a Claude Code web session.
Authorised, nothing bad landed, but no gate was structurally capable of looking at it.

  ── THE FINDING THAT SHAPED THIS FILE ──────────────────────────────────────────────────────
The obvious fix — "restrict who may merge to main" — cannot work here. The merge on PR #2 reads:

    merged_by: sudomadhatter (User)      committer: web-flow

The agent merged AS THE OPERATOR. Not a bot account, not a separate app: the same GitHub
identity. So there is no *who* to restrict — any rule that lets the operator through lets an
autonomous agent through with it. The only server-side discriminator left is a REQUIRED STATUS
CHECK: GitHub refusing a commit until a named check has gone green on that exact commit.

  ── WHAT THIS IS NOT ───────────────────────────────────────────────────────────────────────
⛔ This is NOT a port of the local hook, and must never be described as one.

The local hook (`git-hooks/pre-push-main-approval.sh`) enforces AUTHORISATION — one operator
sign-off buys exactly one merge — using a single-use token under `.git/`. That half CANNOT cross
to a server: the token by design never leaves the machine, and identity cannot stand in for it
(see above). Anything claiming to have moved it has built something that merely looks like it.

What crosses is the ENFORCEMENT half: the real suite ran, and the thing being merged came from
an authorised kind of branch. The two halves guard different ground and neither covers the
other's. That asymmetry is stated in `.agents/rules/git-policy.md` § "The write gate" and it is
the honest description — see `.agents/rules/tests-must-gate-for-real.md`, which exists precisely
because a gate that reads like protection and is not is worse than no gate.

  ── THE TWO MODES, AND WHY THEY DIFFER ─────────────────────────────────────────────────────
`pr`    A pull request targeting `main`. GitHub builds the merge commit itself, AFTER the check
        passes, so there are no parents to inspect yet. All we can check is the source branch's
        NAME. Weaker — deliberately, and it is the weaker case that this ticket was about.

`gate`  The local shipping doors merge on the machine and push the finished merge commit. A
        required status check refuses a commit carrying no green check, and a commit made
        locally has never been to GitHub — so the doors first push that exact commit to a
        throwaway `gate/**` ref, let this run on it, then push it to `main`. Checks attach to
        the COMMIT, not the branch, so the green travels with it (GitHub's own documented
        route for direct pushes under required checks).

        Here the merge commit exists, so we check its SHAPE — and that shape is the same
        invariant the local hook enforces: `main` advances by exactly one merge commit sitting
        directly on the remote's current tip, and what it merges is the tip of a real, pushed
        `epic/*` or `chore/*` branch. Batching several merges into one push breaks it. So does
        rewinding `main` and force-pushing.

  ── SOP CURRENCY IS CHECKED HERE TOO, AND THAT IS THE POINT ────────────────────────────────
`sop_currency.py` normally runs as a commit-msg hook. A commit authored where `core.hooksPath`
was never set — a fresh clone, or a web session with no local git at all — was never seen by it.
That is the same population of commits this whole file exists for, so the landing set is
re-checked here rather than trusted. It calls the REAL `sop_currency` module, not a re-implementation.

Stdlib only, no pytest, no install step — matching every other script in this directory.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sop_currency  # noqa: E402 — same directory; see module docstring

# The two roads to `main` in the branch model (`.agents/rules/git-policy.md` § "Branch model").
# `claude/*` is a STORY lane: it lands on its epic branch, never on main. PR #2 came from
# `claude/fit-repo-workflow-integration-xzvg6q`, which is exactly what this must refuse.
AUTHORISED_PREFIXES = ("epic", "chore")


def read_jira_keys(repo: Path) -> list[str]:
    """The keys THIS repo answers to, from the same tracked file the commit-msg hook reads.

    Not hardcoded to `SCC`: `.agents/jira.conf` is the single source (repo-local enforcement
    never centralises — a project's key binding stays in the project). A repo with no
    `jira.conf` has no key gate at all, which is the same graceful degradation the commit-msg
    hook chose, and is why this returns a list rather than raising.
    """
    conf = repo / ".agents/jira.conf"
    if not conf.is_file():
        return []
    for line in conf.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("JIRA_KEYS="):
            continue
        return line.split("=", 1)[1].strip().strip('"').strip("'").split()
    return []


def branch_pattern(keys: list[str]) -> re.Pattern[str]:
    """`(epic|chore)/<KEY>-<number>-<slug>` — the slug is required, not optional.

    `chore/SCC-118` alone is not a branch this system produces, and accepting it would let a
    hand-typed near-miss through the one check that names the road.
    """
    keyalt = "|".join(re.escape(k) for k in keys) if keys else r"[A-Z][A-Z0-9]+"
    return re.compile(rf"^({'|'.join(AUTHORISED_PREFIXES)})/({keyalt})-\d+-.+")


def authorised_branch(name: str, keys: list[str]) -> tuple[bool, str]:
    """Pure — the whole point, so the tests can drive it without a git repo."""
    name = name.strip()
    if not name:
        return False, "no source branch was supplied"
    if branch_pattern(keys).match(name):
        return True, f"'{name}' is an authorised source branch"
    return False, (
        f"'{name}' is not an authorised source of a merge into main.\n"
        f"        Expected epic/<KEY>-<n>-<slug> or chore/<KEY>-<n>-<slug>"
        + (f" with KEY in {', '.join(keys)}." if keys else ".")
        + "\n        A story lane (claude/*) lands on its epic branch, never on main."
    )


def git(repo: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                       text=True, errors="replace")
    return r.returncode, (r.stdout or "").strip()


def check_merge_shape(repo: Path, head: str, keys: list[str]) -> list[str]:
    """gate mode: the pushed commit must advance `main` by exactly ONE merge of a real branch.

    Returns a list of failure reasons; empty means pass. Mirrors the local hook's `^1`/`^2`
    checks, which is deliberate — that hook's comment explains why the sha check alone was not
    sufficient, and the same reasoning applies verbatim on this side.
    """
    fails: list[str] = []

    rc, parents = git(repo, "rev-list", "--parents", "-n", "1", head)
    if rc != 0 or not parents:
        return [f"cannot resolve {head} in this checkout"]
    shas = parents.split()[1:]
    if len(shas) != 2:
        return [f"{head[:12]} is not a merge commit — it has {len(shas)} parent(s). "
                "main advances by exactly one merge commit."]
    p1, p2 = shas

    rc, remote_main = git(repo, "rev-parse", "origin/main")
    if rc != 0:
        fails.append("cannot resolve origin/main — a shallow checkout cannot see it "
                     "(the workflow needs fetch-depth: 0)")
    elif p1 != remote_main:
        fails.append(
            f"this does not advance main by exactly one merge.\n"
            f"        origin/main is at {remote_main}\n"
            f"        the merge's first parent is {p1}\n"
            "        Batching several merges into one push, or rewinding main, both land here.")

    # ⭐ The second parent must be the TIP of a pushed epic/chore branch — not merely a commit
    # that happens to be reachable from one. `--points-at` is the difference: "contains" would
    # accept any ancestor, so an old commit from the middle of a branch would pass.
    rc, refs = git(repo, "for-each-ref", "--points-at", p2,
                   "--format=%(refname:short)", "refs/remotes/origin")
    candidates = [r.split("/", 1)[1] for r in refs.splitlines() if r.startswith("origin/")]
    if not candidates:
        fails.append(
            f"the merged commit {p2[:12]} is not the tip of any branch on origin.\n"
            "        Push the source branch before pre-flighting the merge.")
    elif not any(authorised_branch(c, keys)[0] for c in candidates):
        ok, why = authorised_branch(candidates[0], keys)
        fails.append(f"{why}\n        (branches at that commit: {', '.join(candidates)})")

    return fails


def check_sop_currency(repo: Path, base: str, head: str) -> list[str]:
    """Re-check every non-merge commit in the landing set against the REAL sop_currency gate.

    Merge commits are skipped for the same reason the commit-msg hook exempts them: their
    message is generated by git and their `--name-only` diff is empty by default, so a merge
    can neither carry a key nor name a changed surface.
    """
    rc, out = git(repo, "rev-list", "--no-merges", f"{base}..{head}")
    if rc != 0:
        return [f"cannot list commits in {base}..{head}"]
    fails: list[str] = []
    for sha in [s for s in out.splitlines() if s.strip()]:
        _, msg = git(repo, "log", "-1", "--format=%B", sha)
        _, names = git(repo, "show", "--name-only", "--format=", sha)
        paths = [p for p in names.splitlines() if p.strip()]
        if not paths:
            continue
        code = sop_currency.main(["--repo", str(repo), "--message", msg, "--paths", *paths])
        if code != 0:
            _, subject = git(repo, "log", "-1", "--format=%h %s", sha)
            fails.append(f"sop_currency rejects {subject}")
    return fails


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Server-side half of the main write gate (SCC-118).")
    ap.add_argument("--mode", choices=("pr", "gate"), required=True)
    ap.add_argument("--repo", default=".", help="repo root (default: cwd)")
    ap.add_argument("--branch", default="", help="pr mode: the PR's source branch")
    ap.add_argument("--base", default="origin/main", help="the commit main is at now")
    ap.add_argument("--head", default="HEAD", help="the commit that wants to land")
    a = ap.parse_args(argv)

    repo = Path(a.repo).resolve()
    keys = read_jira_keys(repo)
    fails: list[str] = []

    print(f"== main-write-gate ({a.mode}) ==")

    if a.mode == "pr":
        ok, why = authorised_branch(a.branch, keys)
        print(f"[{'PASS' if ok else 'FAIL'}] authorised source branch: {why}")
        if not ok:
            fails.append(why)
    else:
        shape = check_merge_shape(repo, a.head, keys)
        print(f"[{'PASS' if not shape else 'FAIL'}] merge shape"
              + ("" if not shape else ": " + "\n        ".join(shape)))
        fails += shape

    sop = check_sop_currency(repo, a.base, a.head)
    print(f"[{'PASS' if not sop else 'FAIL'}] SOP currency across the landing commits"
          + ("" if not sop else ": " + "; ".join(sop)))
    fails += sop

    if fails:
        print("")
        print("  ⛔ MAIN WRITE GATE REFUSED")
        print("     This is the enforcement half only. It does NOT prove the operator")
        print("     approved this merge — that stays local (git-policy.md § The write gate).")
        return 1

    print("-- main-write-gate: pass --")
    return 0


if __name__ == "__main__":
    sys.exit(main())
