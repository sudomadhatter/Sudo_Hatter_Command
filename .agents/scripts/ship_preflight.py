"""ship_preflight.py — the mechanical precheck for `/cicd-push-e2e`, the PRODUCTION door.

`/cicd-push-e2e` is the only command in this system that writes production `main`. Until
SCC-211 it was also the only door that ran no mechanical precheck: its two siblings each call
one first (`closeout_preflight.py` at `/cicd-close-story-merge-tree` Step 0.6,
`task_preflight.py` at `/smh-close-task-merge-tree` Step 1), while this one resolved a branch
from `git branch -a`, asked the operator to "confirm it with the operator by name", and began
merging.

THE FAILURE, AS A SEQUENCE. Uncommitted changes sit in the epic-branch checkout. Step 3 runs
the full gate on that dirty tree and it comes back GREEN. Step 4 checks out `main` and merges
the BRANCH, which does not contain those edits. What shipped to production was never what was
gated, and nothing in the door's 151 lines would have said so.

Four questions, each with an exact answer the door used to take on trust:

  1. SHAPE   — is this even a branch this door ships? (`epic/*` and, conditionally, `chore/*`)
  2. INTENT  — does it carry the key the operator PINNED, before any tool answered anything?
  3. SYNC    — is the checkout clean, and is the branch 0/0 with its remote?
  4. LANE    — a `chore/*` lane belongs here only when its diff reaches deployable code.

It READS and PRINTS. It never merges, checks out, fetches anything but refs, or writes a file.
The merge, the mint and the push stay in the command, where a human is watching the output.

    ship_preflight.py --repo PATH --branch B --expect-key KEY [--no-fetch] [--json]

⛔ ALL THREE ARE REQUIRED, and none of them is derived. `/cicd-push-e2e` binds `PROJECT_ROOT`
at its Step 0 and resolves the branch at its Step 1, so it holds every one of them; letting
this script guess any would re-open `worktree-per-story.md` § "cwd is not intent" — the trap
that had a close-out resolve a SIBLING lane's branch on 2026-08-09 and return a perfectly
honest verdict about the wrong work. `--expect-key` in particular is the one thing no derived
input can express: which ticket the operator MEANT.

Exit: 0 clean · 1 warnings only · 2 blocking. Same contract as both siblings, so the door can
say "exit 2 → STOP" and mean it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_preflight as tp
import wf_common as wf

# `epic/` ships an epic; `chore/` is admitted only when the LANE check below says so. The key
# sits IMMEDIATELY after the prefix (`epic/AVCH-23-thin-toolkit`, never `epic/thin-AVCH-23`)
# because Atlassian's GitHub app joins on the key as a literal string and reads the branch
# name too — the same shape `task_preflight.BRANCH_RE` pins for the chore lane.
BRANCH_RE = re.compile(r"^(epic|chore)/([A-Z][A-Z0-9]*)-(\d+)-(.+)$")

# Branches this door is deliberately NOT for, and where each one actually goes. Scanned in
# order, and the ORDER IS LOAD-BEARING: the specific incident prefix must precede the generic
# story one, or the generic entry makes the specific one dead code (SCC-148, measured in
# `task_preflight.WRONG_LANE` — a real `claude/incident-*` branch was confidently routed to
# the story close-out). One table, one lesson, two scripts.
WRONG_LANE = {
    "claude/incident-": ("/cicd-mobile-error-team",
                         "an incident branch has its own lane and its own pipeline"),
    "claude/": ("/cicd-close-story-merge-tree",
                "a story branch lands on its EPIC branch at close-out, never on main"),
}


# A remote-tracking spelling of a lane branch: `origin/epic/…` or `remotes/origin/epic/…`.
# ⛔ THIS IS THE DOOR'S OWN OUTPUT, NOT A TYPO. `/cicd-push-e2e` Step 1 discovers branches with
# `git branch -a --list '*epic/*'`, which prints remote refs as `remotes/origin/epic/KEY-slug`
# — so the operator pasting exactly what the door just showed them is the ordinary path, and
# it is the ONLY path for an epic pushed from the other machine. Left unnormalised those
# strings miss `BRANCH_RE` and earn the keyless-epic refusal, whose remedy is *"rename it to
# carry the epic's REAL key"* — advice to rename a branch that already carries its key.
# `closeout_preflight.REMOTE_PREFIX_RE` solved the same problem for the story door; the
# lookahead is what keeps it from eating a legitimate first segment.
REMOTE_PREFIX_RE = re.compile(r"^(?:remotes/)?[^/]+/(?=(?:epic|chore|claude)/)")


def check_shape(branch: str, rep: wf.Report) -> tuple[str | None, str | None]:
    """-> (prefix, key). Either may be None; a None key means every later check declines."""
    if branch in ("main", "HEAD", "origin/main"):
        rep.err("branch", f"HEAD/target is '{branch}' - this door merges a finished branch "
                          f"INTO main; it never ships main itself")
        return None, None
    for prefix, (cmd, why) in WRONG_LANE.items():
        if branch.startswith(prefix):
            rep.err("branch", f"{branch} is not a branch this door ships - {why}. "
                              f"Use {cmd}.")
            return None, None
    m = BRANCH_RE.match(branch)
    if not m:
        # ⛔ A KEYLESS `epic/<slug>` LANDS HERE, AND THAT IS THE POINT. The door's own branch
        # model calls those "pre-Jira" and said to ship them as-is — written before the
        # commit-msg gate was ARMED (2026-08-07), after which no new keyless branch can
        # accumulate commits at all. Shipping one now means production carries a merge no
        # ticket can be joined to, and `--expect-key` can never match a branch with no key
        # segment. The remedy is a rename, and it keeps the door's real rule intact:
        # rename it to the epic's REAL key — never invent one.
        rep.err("branch", f"{branch} is not `epic/<JIRA-KEY>-<slug>` (or an admitted "
                          f"`chore/<JIRA-KEY>-<slug>`) - the key must sit immediately after "
                          f"the prefix or Jira never links the merge. If this is a pre-Jira "
                          f"branch, rename it to carry the epic's REAL key first; never "
                          f"invent a key to get past this line")
        return None, None
    prefix, key = m.group(1), f"{m.group(2)}-{m.group(3)}"
    rep.info("branch", f"{branch} -> {key} ({prefix} lane)")
    return prefix, key


def check_intent(repo: Path, branch: str, key: str | None, expect: str,
                 rep: wf.Report) -> None:
    """cwd is not intent, and neither is `git branch -a`.

    Two different questions, and both have been answered wrong in production:
    does this branch carry the key the operator NAMED, and is that key one this repo even
    answers to?
    """
    if key is None:
        return  # check_shape already errored; a second message would bury the first
    if key != expect:
        rep.err("intent", f"--expect-key {expect} but {branch} carries {key} - this "
                          f"preflight is aimed at ANOTHER lane's branch. Re-run against the "
                          f"branch you actually mean; never ship a branch you did not name")
    else:
        rep.info("intent", f"{expect} matches the branch key")

    project = key.split("-")[0]
    allowed = tp.repo_keys(repo)
    if not allowed:
        rep.warn("intent", f"{key}: no .agents/jira.conf in this repo - the key cannot be "
                           f"checked against the repo's project")
    elif project not in allowed:
        # The same rule the armed commit-msg hook enforces, so reaching here means it did
        # not run: bypassed with --no-verify, or never armed on this machine
        # (`core.hooksPath` is per-machine and a fresh clone has it unset — SCC-110).
        rep.err("intent", f"{project} is not one of this repo's projects "
                          f"({', '.join(allowed)}) - these commits did not pass the "
                          f"commit-msg gate: it was either bypassed, or never armed here")
    else:
        rep.info("intent", f"project {project} matches this repo")


def _fetch(repo: Path) -> bool:
    """`git fetch`, with GITHUB_TOKEN removed from the CHILD environment.

    The door's own Rule 2 names a stale session token as a known push/pull failure and tells
    the operator to clear it (`env -u GITHUB_TOKEN`). This is that rule, applied to the one
    fetch the preflight makes: inherited, a stale token fails the fetch, the comparison
    silently degrades to "vs the LAST fetch", and the door proceeds on a stale answer that
    looks exactly like a fresh one. `wf.git` takes no env, so this is the one call built by
    hand.
    """
    env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
    try:
        r = subprocess.run(["git", "fetch", "--quiet"], cwd=str(repo), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=180,
                           env=env)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def check_sync(repo: Path, branch: str, fetch: bool, rep: wf.Report,
               shaped: bool = True) -> bool:
    """-> whether the remote comparison is FRESH (asked for AND succeeded).

    ⭐ THE OUTCOME, NEVER THE FLAG. `task_preflight` carries the same distinction for the same
    reason: a dying uplink fails `git fetch` too, so keying severity on "did the caller ask
    for a fetch" hard-blocks an offline operator on a comparison the code had just warned was
    stale. Intent is not evidence.
    """
    fresh = False
    if fetch:
        if _fetch(repo):
            fresh = True
        else:
            rep.warn("sync", "fetch failed - ahead/behind is vs the LAST fetch, not the "
                             "remote")
    else:
        rep.warn("sync", "--no-fetch: ahead/behind is vs the LAST fetch, not the remote")

    # ⛔ THE CHECK THIS WHOLE SCRIPT EXISTS FOR. The gate runs on the TREE; the merge ships
    # the BRANCH. Uncommitted work makes those two different content, and the door's Step 3
    # would gate the first while its Step 4 ships the second.
    #
    # `-c core.quotepath=false`: git octal-quotes any path holding a non-ASCII byte, and a
    # quoted path compares equal to nothing (`main_write_gate` and `task_preflight` both pass
    # the same flag — one repo, one spelling of a path).
    dirty = wf.git(["-c", "core.quotepath=false", "status", "--porcelain"],
                   repo).stdout.strip()
    if dirty:
        n = len(dirty.splitlines())
        rep.err("sync", f"{n} uncommitted change(s) in the checkout - the gate would run on "
                        f"THIS tree while the merge would not carry them, so what ships was "
                        f"never gated. Commit (explicit paths) and push, or stash, first")
    else:
        rep.info("sync", "working tree clean")

    standing = wf.git(["rev-parse", "--abbrev-ref", "HEAD"], repo).stdout.strip()
    if standing and standing != branch:
        # Not an error: the door checks the branch out at its Step 2, AFTER this runs. It is
        # said out loud because the dirt above belongs to whatever tree is standing here.
        rep.info("sync", f"the checkout is standing on '{standing}'; this preflight is "
                         f"about '{branch}'")

    # ⛔ THREE REF STATES, NOT TWO — and collapsing them inverts the message on a real shape.
    # The first cut asked only "did `rev-list origin/B...B` succeed?" and called every failure
    # "never pushed: the branch exists on this disk only". For a branch that exists ONLY on
    # `origin` that sentence is the exact opposite of the truth, and that shape is ordinary:
    # `/cicd-push-e2e` Step 1 resolves branches with `git branch -a`, which lists
    # remote-tracking refs, so a fresh clone or an epic pushed from the OTHER machine (this
    # system is two machines by design) arrives here with no local ref — and the door's own
    # Step 2 checkout is what creates it. A false BLOCKED on the shipping path is the failure
    # this repo treats as worst, because a gate that false-reds gets routed around.
    def _has(ref: str) -> bool:
        return wf.git(["rev-parse", "--verify", "--quiet", ref], repo).returncode == 0

    # ⛔ DECLINE WHEN THE SHAPE CHECK ALREADY RULED. `check_intent` declines the same way and
    # for the same reason: a second message under the first buries it, and here it was worse
    # than noise — it was FALSE. A live run on a real project repo answered `--branch
    # origin/main` with `origin/main: no such branch, local or remote`, because the probe had
    # gone looking for `refs/heads/origin/main`. The ref plainly exists; the question was
    # simply meaningless once the branch had been ruled to be the merge TARGET. *"A gate that
    # states something plainly untrue teaches the reader to stop believing its output"*
    # (`task_preflight.check_scope`, paid for once already).
    if not shaped:
        rep.info("sync", "ref state not checked - the branch was already ruled out above")
        return fresh

    local, remote = _has(f"refs/heads/{branch}"), _has(f"refs/remotes/origin/{branch}")
    if local and remote:
        counts = wf.git(["rev-list", "--left-right", "--count",
                         f"origin/{branch}...{branch}"], repo)
        behind, ahead = (counts.stdout.split() + ["?", "?"])[:2]
        if ahead != "0" or behind != "0":
            rep.err("sync", f"{branch}: {ahead} ahead / {behind} behind origin - merging an "
                            f"unpushed branch puts commits on production that exist on one "
                            f"disk")
        else:
            rep.info("sync", f"{branch}: 0/0 with origin")
    elif remote:
        rep.info("sync", f"{branch}: on origin, not checked out here - Step 2's checkout "
                         f"creates the local ref from origin, so there is nothing unpushed")
    elif local:
        rep.err("sync", f"{branch}: never pushed - the branch exists on this disk only, so "
                        f"nothing but this machine has ever seen what would ship")
    else:
        rep.err("sync", f"{branch}: no such branch, local or remote - nothing to ship. "
                        f"Check the name against `git branch -a --list '*epic/*'`")
    return fresh


def check_lane(repo: Path, branch: str, prefix: str | None, rep: wf.Report) -> str:
    """-> the lane: `full` · `light` · `handoff` · `unknown`.

    ⭐ WHAT A `chore/*` BRANCH IS ACTUALLY ALLOWED TO DO HERE (SCC-211 finding 3). The door
    admits one at Step 1 ("their direct ask IS that approval") and then names only `epic/*`
    in every operative line after it, so the shape it accepts has no written procedure —
    including the mint's `--branch`, which is what the token records as WHAT is being landed.
    `git-policy.md` routes only the deployable-touching chore diff here; everything else is
    the Task lane's, and landing it through this door skips that whole ceremony (the
    manifest, the `## Your Actions` contract, the Dev Record, the ticket move, the prune).

    So the admission is DERIVED from the diff, exactly as `task_preflight.check_scope`
    derives the mirror-image question, and the two agree by construction: they read the same
    `PRODUCT_DIRS` out of the same module rather than each re-typing the list.
    """
    if prefix is None:
        return "unknown"
    if prefix == "epic":
        rep.info("lane", "epic branch -> the full gate (backend suite + frontend build + "
                         "/cicd-e2e GREEN)")
        return "full"

    surface = tp.deploy_surface(repo)
    if not surface:
        rep.err("lane", "this repo has no deployable surface (no "
                        + ", ".join(d.rstrip("/") for d in tp.PRODUCT_DIRS)
                        + ") - there is no deploy for a chore lane to justify shipping "
                          "here. STOP and close it out with /smh-close-task-merge-tree")
        return "handoff"

    base = tp.base_ref(repo)
    # ⛔ NAME A REF THAT RESOLVES, AND READ THE EXIT CODE. Both halves were missing, and
    # together they printed a fact about a diff that never ran: `0 file(s) changed, none of
    # them deployable` — then routed the lane to `/smh-close-task-merge-tree` on it, a door
    # that refuses deployable diffs and hands the work straight back, each naming the other.
    # The trigger is ordinary: on a branch with no local ref (fetched from the other machine,
    # or a fresh clone) `base...<branch>` cannot resolve, so the ref is chosen the same way
    # `check_sync` chooses it.
    ref = branch
    if wf.git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], repo).returncode:
        ref = f"origin/{branch}"
    diff = wf.git(["diff", "--name-only", f"{base}...{ref}"], repo)
    if diff.returncode != 0:
        rep.err("lane", f"cannot read the diff for {ref} against {base} - the lane question "
                        f"is unanswerable, so this is not a refusal about your work: "
                        f"{(diff.stderr or '').strip()[:160]}")
        return "unknown"
    changed = [ln.strip() for ln in diff.stdout.splitlines() if ln.strip()]
    touched = sorted({d for d in surface for p in changed if p.startswith(d)})
    if touched:
        rep.info("lane", f"chore branch touching {', '.join(touched)} -> the light gate "
                         f"(backend suite + frontend build); a change that reaches "
                         f"deployable code is a product change whatever its ticket says")
        return "light"
    rep.err("lane", f"chore branch, {len(changed)} file(s) changed, none of them deployable "
                    f"({', '.join(surface)}) - this is Task work and the Task ceremony never "
                    f"runs for a lane that lands here. STOP and close it out with "
                    f"/smh-close-task-merge-tree")
    return "handoff"


VERDICTS = {
    0: "clear to gate and ship",
    1: "clear to gate and ship, with warnings",
    2: "BLOCKED - nothing may be gated, merged or pushed until these are fixed",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True,
                    help="the project root (PROJECT_ROOT, from the door's Step 0)")
    ap.add_argument("--branch", required=True,
                    help="the branch being shipped, from the door's Step 1")
    ap.add_argument("--expect-key", required=True,
                    help="the ticket you MEAN, pinned before any tool answered anything")
    ap.add_argument("--no-fetch", action="store_true",
                    help="offline opt-out; the VERDICT then says the comparison is stale")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    # ⛔ `required=True` IS SATISFIED BY THE EMPTY STRING, and an empty operand is exactly
    # what an unset shell variable becomes — the door pins `EXPECTED_KEY` in one fenced block
    # and consumes it in another, two steps later. Unchecked, an empty pin produced the worst
    # available message: `--expect-key  but epic/X carries SCC-11 … aimed at ANOTHER lane's
    # branch`, blaming a branch that was correct. Name the operand that never arrived instead.
    # (`_harness._case_filter` carries the same lesson for `--case`: a missing value and a
    # wrong value are different errors and must read differently.)
    for flag, value in (("--repo", args.repo), ("--branch", args.branch),
                        ("--expect-key", args.expect_key)):
        if not value.strip():
            ap.error(f"{flag} is empty - the operand never arrived (an unset shell variable "
                     f"becomes an empty string). This is not a verdict about your branch; "
                     f"re-run with {flag} set.")

    repo = tp.git_root(args.repo)
    branch = args.branch.strip()
    # Normalised ONCE, here, so every later check — the shape scan, `refs/heads/<branch>`,
    # `origin/<branch>`, the diff ref — sees one spelling. Announced rather than silent: the
    # operator pasted what the door printed, and they should see what it was read as.
    local_name = REMOTE_PREFIX_RE.sub("", branch)
    expect = args.expect_key.strip().upper()
    rep = wf.Report()
    # The door says "read the header before the verdict" because a verdict about another lane
    # reads exactly like a verdict about yours. That is just as true of the REPO — `--repo`
    # exists because cwd is not intent — and it used to appear only under `--json`.
    rep.info("repo", str(repo))
    if local_name != branch:
        rep.info("branch", f"read '{branch}' as the local lane name '{local_name}' - "
                           f"`git branch -a` prints remote refs that way")
        branch = local_name

    prefix, key = check_shape(branch, rep)
    check_intent(repo, branch, key, expect, rep)
    fresh = check_sync(repo, branch, not args.no_fetch, rep, shaped=prefix is not None)
    lane = check_lane(repo, branch, prefix, rep)

    code = rep.exit_code()
    verdict = VERDICTS[code]
    # ⭐ THE STALENESS RIDES THE VERDICT LINE ITSELF (SCC-193's finding, one door over). A
    # note saying the comparison was stale sat under a VERDICT reading "clear to close out
    # and merge", and the verdict line is the only line an agent acts on. Same evidence, same
    # place.
    if not fresh and code < 2:
        verdict += " (stale - no fresh fetch; the ahead/behind is vs the LAST fetch)"

    if args.json:
        print(json.dumps({"repo": str(repo), "branch": branch, "key": key, "lane": lane,
                          "expect_key": expect, "fresh": fresh, "verdict": verdict,
                          "exit": code,
                          "items": rep.items}, indent=1))
        return code

    # ⛔ ONE header, printed by `print_human` — it emits `== <title> ==` itself
    # (`wf_common.Report.print_human`). An explicit print here as well doubled the line, and
    # the door's Step 1.5 tells the reader "read the header before the verdict": two headers
    # on a door whose whole job is telling you which branch it resolved is the one place
    # noise is least affordable. Found by running the script against a real project repo —
    # the fixture assertion pinned that the header was PRESENT, which two of them satisfy.
    rep.print_human(f"ship preflight - {branch}")
    print(f"VERDICT: {verdict}")
    return code


if __name__ == "__main__":
    sys.exit(main())
