"""task_preflight.py — is this TASK branch safe to merge to main, and by WHICH gate? (SCC-49)

`/smh-close-task-merge-tree` closes **Task** work — workflow / IDE / rules / skills changes that
never got an epic and a story, and so can never reach `/cicd-update-sprint-memory`. It merges
to `main`, which makes it the second command in the system allowed anywhere near production,
and that is exactly why its preconditions are a script rather than a checklist.

The load-bearing question is the LANE, and it is the one an agent is worst at answering
honestly about its own work: *does this change reach anything that deploys?*

    LOCAL    - nothing deployable changed. The repo's own enforcement suite IS the whole gate.
    HANDOFF  - a deployable path changed. STOP; this is `/cicd-push-e2e`'s job, not a task.

It is derived from the repo, never asserted:

  * a repo with no deployable surface at all (the command centre - no `frontend/`, no
    `backend/`, and `git-policy.md` says it "has no E2E suite and never will") can only ever
    be LOCAL, so the E2E question does not arise there;
  * a repo that DOES deploy is LOCAL only while the diff stays clear of its deployable dirs.

    task_preflight.py --expect-key SCC-00 [--repo PATH] [--branch B] [--fetch] [--json]

`--expect-key` is REQUIRED (SCC-64). On 2026-08-09 a close-out ran this preflight while cwd
had silently drifted into a sibling lane's checkout: every check ran honestly against that
lane's branch and the verdict was a clean lie. The script cannot detect a wrong target from
derived inputs alone - repo and branch are both guesses when defaulted - so the caller must
state WHICH ticket they mean, and the branch's key must match it or the run blocks. A wrong
cwd now fails the key match instead of merging someone else's work.

Exit: 0 clean · 1 warnings · 2 blocking. It reads and reports; it never merges, never
transitions a ticket, and never deletes a branch. The command does those, after this passes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wf_common as wf
import hooks_armed
# ONE acli resolution path in this repo, not two. `jira_feed` already owns
# --acli / $ACLI_BIN / PATH and the "a hung uplink is not a verdict" wrapper; duplicating
# that here is exactly how the python3/python probe orders drifted apart before SCC-49.
# Import-safe: the module is guarded by `if __name__ == "__main__"` and pulls only stdlib.
import jira_feed

# The chore lane's branch shape, from `git-policy.md`: the key sits IMMEDIATELY after the
# prefix (`chore/SCC-11-acli-wrapper`, never `chore/fix-SCC-11`) because Atlassian's GitHub
# app joins on the key as a literal string and reads the branch name too.
BRANCH_RE = re.compile(r"^chore/([A-Z][A-Z0-9]*)-(\d+)-(.+)$")

# Branches this command is deliberately NOT for, and where each one actually goes. A refusal
# that names the right command costs nothing; a bare "wrong branch" sends someone hunting.
WRONG_LANE = {
    "epic/": ("/cicd-push-e2e", "an epic branch ships through the full gate, not this one"),
    "claude/": ("/cicd-update-sprint-memory",
                "a story branch lands on its EPIC branch at close-out, never on main"),
    "incident/": ("/cicd-mobile-error-team", "incident branches have their own lane"),
}

# Directories whose contents deploy. Presence answers "does this repo deploy at all?";
# a diff touching one answers "did THIS change reach it?".
#
# ⭐ TWO LISTS, NOT ONE, AND THE SPLIT IS LOAD-BEARING (SCC-118, 2026-08-12).
#
# `.github/` differs in kind from the other five. They hold a PRODUCT — code that ships to
# somewhere a user can reach. `.github/` holds machinery ABOUT the repo: CI, issue templates,
# the gates. In a repo that ships something, a workflow edit can change WHAT ships, so it is
# rightly deployable there. In a repo that ships nothing, it cannot deploy anything, because
# there is nothing to deploy.
#
# Collapsing both into one list was invisible for as long as the command centre had no
# `.github/` at all — and SCC-118 gave it one, the very first, holding the server-side half of
# the `main` write gate. The next close-out in this repo was refused as "NOT task-lane work"
# and sent to `/cicd-push-e2e`: a `cicd-*` command that binds exactly ONE PROJECT and never the
# lobby, running an E2E suite this repo does not have and never will. A verdict nobody could
# comply with — the same shape as SCC-113's "the gate could not express one ticket, two lanes."
#
# ⛔ The guard is NOT weakened where it means anything. A repo with a product surface still
# hands off the moment a diff touches `.github/` — that is the case this check exists for, and
# `test_task_preflight.py` asserts it as a control alongside the narrowing.
PRODUCT_DIRS = ("backend/", "frontend/", "firebase/", "functions/", "mobile/")
CI_DIR = ".github/"
DEPLOY_DIRS = PRODUCT_DIRS + (CI_DIR,)


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
        # The same rule the armed commit-msg hook enforces - so reaching here means it did not
        # run. TWO causes, and the message must name both: the hook was bypassed (--no-verify),
        # or it was never ARMED on this machine. `core.hooksPath` is per-machine and a fresh
        # clone has it unset, which makes the second cause the likelier one (SCC-110).
        rep.err("branch", f"{key} is not one of this repo's projects ({', '.join(allowed)}) "
                          f"- these commits did not pass the commit-msg gate: it was either "
                          f"bypassed, or never armed here (see the `hooks` findings)")
        return None
    else:
        rep.info("branch", f"{branch} -> {key} (project {m.group(1)} matches this repo)")
    return key


# ── 1b. Is this the branch the OPERATOR meant? ─────────────────────────────────

def check_intent(branch: str, key: str | None, expect: str, rep: wf.Report) -> None:
    """cwd is not intent. The one thing no derived input can express is which ticket the
    operator MEANT - so it arrives as --expect-key and the branch has to agree with it."""
    if key is None:
        return  # check_branch already errored; a second message would bury the first
    if key != expect:
        rep.err("intent", f"--expect-key {expect} but {branch} carries {key} - this "
                          f"preflight is aimed at ANOTHER lane's branch. cwd is not "
                          f"intent: re-run against the repo/branch you actually mean")
    else:
        rep.info("intent", f"{expect} matches the branch key")


# ── 1c. The task manifest, when one exists ─────────────────────────────────────

MANIFEST_SCHEMA = ("task_key: SCC-00 | primary_repo: <name> | branch: chore/SCC-00-<slug> | "
                   "close_command: smh-close-task-merge-tree | secondary_repos: [] or a BLOCK "
                   "list of `- repo: <path>` / `landing: independent-task|retain-on-epic` / "
                   "`ticket: KEY-00` rows (the inline [{...}] form is not read)")


def manifest_field(text: str, field: str) -> str | None:
    m = re.search(rf"^\s*{field}\s*:\s*[\"']?([^\"'\n#]+)", text, re.MULTILINE)
    return m.group(1).strip() if m else None


def task_manifests(repo: Path, expect: str) -> list[tuple[Path, str]]:
    """Every `task.yaml` under `_artifacts/` that declares THIS task key."""
    root = repo / "_artifacts"
    manifests = list(root.glob("**/task.yaml")) if root.is_dir() else []
    return [(p, t) for p in manifests
            if (t := wf.read_text(p)) and manifest_field(t, "task_key") == expect]


def manifest_settled(repo: Path, p: Path, ref: str) -> bool:
    """True only on POSITIVE evidence: this exact receipt, blob for blob, is already
    recorded on the mainline - the lane that wrote it has landed, so its claims are
    history, not this run's contract. Every way the probe can fail (no mainline, path
    never merged, file edited since landing) answers False and keeps the strict path:
    absence of evidence never relaxes a gate. (H-1 - the reverted fe46b4a asked "does
    the declared branch still exist?", which blessed the pruned-branch state a finished
    close-out is SUPPOSED to end in.)"""
    try:
        rel = p.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:  # symlinked checkout / macOS /tmp - same hazard rel_or_abs guards
        return False
    landed = wf.git(["rev-parse", "--verify", "--quiet", f"{ref}:{rel}"], repo)
    if landed.returncode != 0 or not landed.stdout.strip():
        return False
    ours = wf.git(["hash-object", str(p)], repo)
    return ours.returncode == 0 and ours.stdout.strip() == landed.stdout.strip()


def check_manifest(repo: Path, branch: str, expect: str, rep: wf.Report) -> None:
    """`task.yaml` is intent written down at task START - authored on the lane's own
    branch, it reaches the mainline only WHEN that lane lands. So multi-lane tickets
    leave one receipt PER landed lane in the tree, and re-litigating those would block
    every follow-on: a receipt settled on the mainline is read as history, and only the
    unlanded ones can bind this run. Those still must agree with what the preflight
    resolved - a manifest nobody checks against is decorative."""
    mine = task_manifests(repo, expect)
    if not mine:
        rep.warn("manifest", f"no task.yaml declares task_key: {expect} - intent rests on "
                             f"--expect-key alone. Author one in the task's _artifacts "
                             f"folder ({MANIFEST_SCHEMA})")
        return
    ref = base_ref(repo)
    live: list[tuple[Path, str | None]] = []
    for p, text in mine:
        declared = manifest_field(text, "branch")
        if declared and declared != branch and manifest_settled(repo, p, ref):
            rep.info("manifest", f"{rel_or_abs(p, repo)} declares `{declared}` and is "
                                 f"already recorded on {ref} - a landed lane's receipt, "
                                 f"not this lane's contract")
        else:
            live.append((p, declared))
    if not live:
        rep.warn("manifest", f"every task.yaml for {expect} is a landed lane's receipt - "
                             f"THIS lane has no manifest, so intent rests on --expect-key "
                             f"alone. Author one in the task's _artifacts folder "
                             f"({MANIFEST_SCHEMA})")
        return
    for p, declared in live:
        if declared and declared != branch:
            rep.err("manifest", f"{rel_or_abs(p, repo)} declares branch `{declared}` but "
                                f"this preflight resolved `{branch}` - one of them is "
                                f"wrong; fix the manifest or aim at the declared branch")
        else:
            rep.info("manifest", f"{rel_or_abs(p, repo)} agrees: {expect} on "
                                 f"{declared or branch}")


# ── 1d. The cross-repo half this repo's `git status` CANNOT see ────────────────
#
# `secondary_repos` was in MANIFEST_SCHEMA, in smh-quick-dev.md and in the close-out command, and
# was read by nothing: check_manifest() validated task_key and branch only. So a task could
# declare "this also lands in Projects/X under KEY-00" and close out green while that key was one
# X's commit-msg hook rejects, its branch was never pushed, or X was not even checked out.
#
# WHY THIS IS BLOCKING HERE AND ONLY A [SIGNAL] IN run_all. Project-store defects cannot fail the
# lobby's memory gate: a project is a separate repo whose hook rejects this repo's keys, so a
# blocking gate there would red every unrelated lane over a defect nobody in the lobby may fix.
# That objection does not survive at close-out. A lane that DECLARES a secondary repo has asserted
# it is cross-repo work - it can commit there, and it is about to merge. Blocking it is fair, and
# a single-repo lane never reaches any of this.

def _scalar(v: str) -> str:
    """A YAML scalar's value. `#` only opens a comment after whitespace - `Projects/C#App` is a
    path, not a truncated one."""
    return re.split(r"\s#", v, maxsplit=1)[0].strip().strip("\"'")


def secondary_rows(text: str) -> tuple[list[dict[str, str]], str | None]:
    """`(rows, unparsed)`. No PyYAML on these machines - the rest of this file parses the manifest
    by regex for the same reason.

    ⛔ `unparsed` is the FLOOR, and it is what makes this readable-or-loud rather than
    readable-or-silent. Every way of not understanding the value returns it: the inline `[{...}]`
    form, a duplicated key, and - the one that mattered - **the key present but yielding no rows**.
    Without that last case there is no difference between "no secondary repos" and "I could not
    read the secondary repos", so four valid YAML spellings verified nothing and reported nothing.
    The worst was self-inflicted: this command's own template shipped `secondary_repos: []` with a
    commented block underneath, and uncommenting it - the edit the comment invites - left the `[]`
    above to win the search. A cross-repo lane declaring a key its target repo REJECTS closed out
    green and silent. Never return an empty list from a branch that found the key."""
    # `[^\S\n]*`, NOT `\s*`: under re.MULTILINE `$` matches before a newline, but `\s` matches the
    # newline itself, so `\s*(.*)` runs past the line end and captures the NEXT line. Horizontal
    # whitespace only. `\s*:` before it, because `secondary_repos :` is valid YAML and
    # `manifest_field` already accepts that spelling.
    keys = list(re.finditer(r"^secondary_repos[^\S\n]*:[^\S\n]*(.*)$", text, re.MULTILINE))
    if not keys:
        return [], None
    if len(keys) > 1:
        return [], f"{len(keys)} `secondary_repos:` keys - which one is authoritative is undefined"
    m = keys[0]
    inline = _scalar(m.group(1))
    if inline:
        return ([], None) if inline in ("[]", "[ ]") else ([], inline)

    rows: list[dict[str, str]] = []
    stray = False
    for line in text[m.end():].splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue          # blank or comment at ANY indent - neither ends a block in YAML
        item = s.startswith("- ") or s == "-"
        if not line.startswith((" ", "\t")) and not item:
            break             # a real dedent to the next top-level key
        if item:
            rows.append({})
            s = s[2:].strip() if s != "-" else ""     # `-` alone is a valid non-compact item
        if not s:
            continue
        if ":" not in s:
            stray = True
            continue
        k, _, v = s.partition(":")
        if not rows:          # a mapping key before any `- ` item: not a list this reader knows
            stray = True
            continue
        rows[-1][k.strip()] = _scalar(v)

    if not rows or stray or any(not r for r in rows):
        return [], (m.group(0).strip() or "secondary_repos:") + " (block form unreadable here)"
    return rows, None


def store_problems(store: Path) -> tuple[list[str], str | None]:
    """`(problems, unavailable_reason)` for a memory store, reusing the gate's own contract.

    Imported from the gate rather than reimplemented: a second copy of "what makes a store valid"
    would drift from the one `run_all` enforces, and then two checks would disagree about the same
    store. In this repo `.agents/scripts/tests/` IS the enforcement layer (`run_all.py` is the
    gate), so depending on it from here is not a test/production inversion.

    Failures are REPORTED, never swallowed and never raised - a check that quietly becomes a no-op
    when its dependency moves is worse than no check, because the green still looks earned; and one
    that escapes as an exception is worse again. ⛔ The CALL is guarded as well as the import. It
    was not, and `check_store` reads the index with plain `read_text(encoding="utf-8")`: a single
    cp1252 byte in a project's MEMORY.md - the em-dash hazard this system has hit before - raised
    UnicodeDecodeError out of here and killed the whole preflight at exit 1, which this script's
    own contract grades as *warnings*. No VERDICT printed, and because this runs first, the
    deployable-lane question the script exists to answer never got asked at all."""
    try:
        tests = Path(__file__).resolve().parent / "tests"
        if str(tests) not in sys.path:
            sys.path.insert(0, str(tests))
        from test_memory_store import check_store          # noqa: PLC0415 (deliberately lazy)
    except Exception as e:                                 # noqa: BLE001 - any failure must speak
        return [], f"could not load the memory-store contract ({type(e).__name__}: {e})"
    try:
        return check_store(store), None
    except Exception as e:                                 # noqa: BLE001 - same reasoning
        return [], f"the store could not be read ({type(e).__name__}: {e})"


def worktree_main_root(repo: Path) -> Path | None:
    """The MAIN checkout when `repo` is a linked worktree, else None.

    Submodules do not populate in a `git worktree`: `Projects/<name>/` is an empty stub in every
    lane, and lanes are where close-outs run. Resolving there is not a workaround - the submodule
    content lives in the main checkout and is SHARED, so there is exactly one checkout of that
    repo and exactly one branch state to verify. Looking only under the lane made this check
    block every cross-repo close-out in the one place they all happen."""
    r = wf.git(["rev-parse", "--git-common-dir"], repo)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    common = Path(r.stdout.strip())
    if not common.is_absolute():
        common = (repo / common).resolve()
    root = common.parent
    return root if root.resolve() != repo.resolve() else None


def check_secondary(repo: Path, expect: str, rep: wf.Report) -> None:
    """Every declared cross-repo half: reachable, right key, clean, pushed, store intact."""
    for path, text in task_manifests(repo, expect):
        rows, unparsed = secondary_rows(text)
        if unparsed:
            # ERROR, not a warning. "I could not read your cross-repo declaration" and "there is
            # no cross-repo half" must never share an exit code: the whole point of this check is
            # that an unverified secondary repo does not reach a merge.
            rep.err("secondary", f"{rel_or_abs(path, repo)}: secondary_repos is present but not "
                                 f"readable (`{unparsed}`) - so it was NOT verified. Use the block "
                                 f"form, one `- repo:` per row ({MANIFEST_SCHEMA})")
        for row in rows:
            name = row.get("repo")
            ticket = row.get("ticket", "")
            landing = row.get("landing", "")
            if not name:
                rep.err("secondary", f"{rel_or_abs(path, repo)}: a secondary_repos row has no "
                                     f"`repo:` - there is nothing to verify")
                continue
            if landing and landing not in ("independent-task", "retain-on-epic"):
                rep.err("secondary", f"{name}: landing `{landing}` is not one of "
                                     f"independent-task / retain-on-epic - retain-on-epic is the "
                                     f"exception that must never be presented as merged to "
                                     f"production, so an unrecognised value cannot be assumed safe")

            # Two spellings are in the wild: `Projects/<name>` and a bare `<name>` (see the SCC-62
            # manifest). Accept both rather than hand the next author a hard block whose printed
            # remedy - a submodule path - cannot succeed for a bare name.
            candidates = [repo / name, repo / "Projects" / name]
            main_root = worktree_main_root(repo)
            if main_root:
                candidates += [main_root / name, main_root / "Projects" / name]
            sec = next((c.resolve() for c in candidates if (c / ".git").exists()), None)
            if sec is None:
                rep.err("secondary", f"{name}: declared as a secondary repo but not a git "
                                     f"checkout, here or in the main worktree - its half of "
                                     f"this task cannot be confirmed landed "
                                     f"(git submodule update --init -- {name})")
                continue
            if not (repo / name / ".git").exists():
                rep.info("secondary", f"{name}: not a checkout in this lane (submodules do not "
                                      f"populate in a worktree) - verified in the shared checkout "
                                      f"at {sec}")

            # The key, against that repo's OWN jira.conf. Widening a project's keys is ruled out
            # in writing, so a mismatch is not a preference - the hook there will reject the
            # commit, and finding that out at the commit is finding out too late.
            keys = repo_keys(sec)
            if not ticket:
                rep.err("secondary", f"{name}: no `ticket:` - cross-repo work is a ticket PER "
                                     f"REPO, and this half has none")
            elif "-" not in ticket or not ticket.split("-", 1)[1].strip():
                rep.err("secondary", f"{name}: `{ticket}` is a project key, not a ticket - a "
                                     f"cross-repo half is a specific work item (KEY-00)")
            elif not keys:
                # `check_branch` already handles this shape for the primary; matching it here
                # matters more, because the alternative was printing `matches its jira.conf ()` -
                # a claimed verification whose own empty parens are the proof it never happened.
                rep.warn("secondary", f"{name}: no .agents/jira.conf - {ticket} cannot be checked "
                                      f"against the keys that repo actually answers to")
            elif ticket.split("-")[0].upper() not in [k.upper() for k in keys]:
                rep.err("secondary", f"{name}: declared ticket {ticket} but that repo answers "
                                     f"only to {'/'.join(keys)} - its commit-msg hook will "
                                     f"reject a {ticket.split('-')[0].upper()}-keyed commit")
            else:
                rep.info("secondary", f"{name}: {ticket} matches its jira.conf ({'/'.join(keys)})")

            dirty = wf.git(["status", "--porcelain"], sec).stdout.strip()
            if dirty:
                rep.err("secondary", f"{name}: {len(dirty.splitlines())} uncommitted change(s) - "
                                     f"this repo's own `git status` cannot see them (submodules "
                                     f"are `ignore = all`), so nothing else will catch this")
            head = wf.git(["rev-parse", "--abbrev-ref", "HEAD"], sec).stdout.strip()
            if head == "HEAD":
                # Detached is not a mistake here - it is what `git submodule update --init`
                # produces, so every submodule on a fresh clone lands in this state. Asking
                # `origin/HEAD...HEAD` invents a branch and reports "never pushed" or a bogus
                # ahead/behind, with a remedy that does not apply.
                sha = wf.git(["rev-parse", "HEAD"], sec).stdout.strip()
                reachable = wf.git(["branch", "-r", "--contains", sha], sec).stdout.strip()
                if reachable:
                    rep.info("secondary", f"{name}: detached at {sha[:8]}, and that commit is on "
                                          f"{reachable.split()[0]} - pushed")
                else:
                    rep.err("secondary", f"{name}: detached at {sha[:8]} and that commit is on no "
                                         f"remote branch - its half of this task exists on one disk")
            else:
                counts = wf.git(["rev-list", "--left-right", "--count",
                                 f"origin/{head}...{head}"], sec)
                if counts.returncode != 0 or not counts.stdout.strip():
                    rep.err("secondary", f"{name}: branch `{head}` was never pushed - its half of "
                                         f"this task exists on one disk")
                else:
                    behind, ahead = (counts.stdout.split() + ["?", "?"])[:2]
                    if ahead != "0" or behind != "0":
                        rep.err("secondary", f"{name}: `{head}` is {ahead} ahead / {behind} behind "
                                             f"origin - commit and push are ONE action")

            # Has the other half actually LANDED? `independent-task` says it lands through its own
            # lane, so closing this one while that lane is unmerged ships half the work - and when
            # this half is a deletion whose destination is the other, it destroys what it moved.
            # A warning, not an error: the landing order between two open lanes is a real judgment
            # call. But it fires mechanically at the merge, which prose in a walkthrough does not.
            if landing != "retain-on-epic":
                sha = wf.git(["rev-parse", "HEAD"], sec).stdout.strip()
                base = base_ref(sec)
                landed = wf.git(["merge-base", "--is-ancestor", sha, base], sec).returncode == 0
                if not landed:
                    rep.warn("secondary", f"{name}: HEAD {sha[:8]} is NOT yet on {base} - this "
                                          f"half has not landed. Merge {ticket or 'it'} FIRST if "
                                          f"this task depends on it being there (a task that "
                                          f"deletes what the other half receives always does)")

            store = sec / "_artifacts" / "_memory"
            if not (store / "MEMORY.md").is_file():
                continue                     # no store yet is a beginning, not rot
            problems, unavailable = store_problems(store)
            if unavailable:
                rep.warn("secondary", f"{name}: memory store NOT checked - {unavailable}")
            for p in problems:
                rep.err("secondary", f"{name} memory store: {p}")


# ── 2. Is the branch clean, pushed, and current with main? ─────────────────────

# A child that is `Done` is finished; a child that is `Deferred` was descoped on purpose
# (jira.md: `Deferred` is a To Do-CATEGORY status precisely so descoped work does not read as
# shipped, and it pairs with the `descoped` label). Everything else is still open.
#
# ⭐ `Deferred` IS the escape hatch, and it is deliberately not a `--force` flag. A gate with
# no legitimate exit gets `--no-verify`d into oblivion; the legitimate exit here is to fix the
# BOARD - descope the child properly - which leaves an auditable trail. A bypass flag would
# leave none.
CHILD_CLOSED = ("done", "deferred")


def check_children(key: str | None, rep: wf.Report, timeout: int = 20) -> None:
    """A parent Task does not close while its subtasks are still open (SCC-119).

    ⛔ THREE ways this check could have passed without checking anything, all measured
    against the live board 2026-08-12 - this is the one gate in this file that talks to the
    network, so its failure modes are not the usual ones:

      1. **Row count is not the signal, the EXIT CODE is.** `parent = <KEY>` returns zero rows
         for a childless parent (exit 0) AND zero rows for a bad key (exit 1). Reading rows
         alone makes a wrong key look like a clean pass. `acli_json` returns None on any
         non-zero exit, so `None` here means UNKNOWN and never "no children".
      2. **`parent` is not a legal `--fields` value on `search`** - the real acli exits 1 with
         "field 'parent' is not allowed". Asking for it is the natural mistake when checking
         parentage, and it would have turned every run into a silent pass via (1). We ask for
         `key,summary,status` and get parentage from the JQL instead.
      3. **`acli_bin()` DIES when acli is absent.** Calling it here would have taken a local,
         offline-capable preflight and made it exit 2 on any machine without the CLI. Resolved
         gently instead.

    ⚠ Deliberate divergence from this ticket's own plan (§4a.3), recorded rather than
    silently taken: an unreachable board WARNS and does **not** flip the headline VERDICT.
    Making a local preflight's verdict depend on network reachability is a capability
    regression - sandboxed agent shells cannot reach the OS credential store at all
    (jira.md §top), so "NOT CLEAR" would become the normal output and stop meaning anything.
    The second layer is `/smh-close-task-merge-tree`, which re-asserts this immediately before
    it transitions the ticket to `Done` - a step that already holds the board. Neither layer
    is load-bearing alone, which is the same shape as the two `start` seams (SCC-113).
    """
    if key is None:
        return  # check_branch already errored; a second message would bury the first
    binary = os.environ.get("ACLI_BIN") or shutil.which("acli")
    if not binary:
        rep.warn("children", f"{key}: acli is not on this machine, so its subtasks were NOT "
                             f"checked - if this ticket is a parent, open children would not "
                             f"stop the close. Verify by hand: acli jira workitem search "
                             f'--jql "parent = {key}"')
        return
    data = jira_feed.acli_json(
        binary, ["jira", "workitem", "search", "--json", "--limit", "200",
                 # NOT `parent` - see (2) above. The JQL carries the parentage.
                 "--fields", "key,summary,status",
                 "--jql", f"parent = {key} ORDER BY key"], timeout=timeout)
    if data is None:
        rep.warn("children", f"{key}: the board could not be read, so its subtasks were NOT "
                             f"checked - this is transport, not a verdict on the ticket. "
                             f"Re-run when you have a connection, or check by hand.")
        return

    items = jira_feed.as_items(data, "issues")
    open_children = []
    for item in items:
        fields = item.get("fields") or {}
        status = ((fields.get("status") or {}).get("name") or "").strip()
        if status.lower() not in CHILD_CLOSED:
            open_children.append(f"{item.get('key') or '?'} ({status or '?'})")

    if open_children:
        rep.err("children", f"{key} has {len(open_children)} open subtask(s) - the parent "
                            f"closes LAST, when the whole job is done: "
                            f"{', '.join(open_children)}. Finish them, or descope one to "
                            f"`Deferred` if it is genuinely out of scope.")
    elif items:
        rep.info("children", f"{key}: all {len(items)} subtask(s) are Done or Deferred - "
                             f"this parent is the last thing to close")
    else:
        rep.info("children", f"{key}: no subtasks")


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
        lines = dirty.splitlines()
        mem = [ln for ln in lines if ln[3:].startswith("_artifacts/_memory/")]
        rest = [ln for ln in lines if ln not in mem]
        if rest:
            rep.err("sync", f"{len(rest)} uncommitted change(s) - commit "
                            f"(explicit paths) and push before merging")
        if mem:
            # Memory files are session output, and the session that wrote them may not be
            # this one - two lanes share one store. Naming them separately is what stops a
            # close-out from sweeping (or deleting) another session's memory to get green.
            rep.err("sync", f"{len(mem)} memory file(s) dirty under _artifacts/_memory/ - "
                            f"if ANOTHER session wrote them, park or leave them (never "
                            f"sweep, delete, or commit them under this task); if THIS "
                            f"session wrote them, commit them with explicit paths under "
                            f"this task's key first")
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

    Same reason `/cicd-push-e2e` merges `origin/main` into the epic branch before it gates:
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
        wf.report_overlap(repo, branch, base, rep)
    else:
        rep.info("base", f"{base} is fully absorbed into {branch}")


# ── 3. THE LANE — the one question this script exists to answer ────────────────

def deploy_surface(repo: Path) -> list[str]:
    """Which deployable dirs this repo actually HAS.

    Empty means the repo cannot deploy, so there is no E2E suite for a gate to skip - the
    command centre's case, and the reason `git-policy.md` says its whole gate is
    `run_all.py`. This is derived from the tree so no repo needs a config file saying so.

    ⭐ `.github/` only counts once something SHIPS here (SCC-118 - see PRODUCT_DIRS). A repo
    holding CI and nothing else deploys nothing, so calling its workflow directory a deploy
    surface routes an unshippable repo to `/cicd-push-e2e` - a command that binds a project,
    refuses the lobby, and gates on an E2E suite that does not exist here. Where a product
    DOES exist, `.github/` is returned exactly as before and a diff touching it still hands
    off."""
    tracked = wf.git(["ls-files"], repo).stdout.splitlines()
    product = [d for d in PRODUCT_DIRS if any(p.startswith(d) for p in tracked)]
    if not product:
        return []
    return product + ([CI_DIR] if any(p.startswith(CI_DIR) for p in tracked) else [])


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
                         f"task-lane work. STOP and ship it with /cicd-push-e2e.")
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
    (`/cicd-close-workingtree` Step 3a)."""
    out = wf.git(["worktree", "list", "--porcelain"], repo).stdout
    # [0] is the MAIN checkout, which is standing on this branch by definition when the
    # command runs from it - reporting that as "a worktree holds your branch" is a warning
    # that fires on every single clean run, and a warning that always fires gets ignored.
    for block in out.split("\n\n")[1:]:
        wt = re.search(r"^worktree (.+)$", block, re.MULTILINE)
        br = re.search(r"^branch refs/heads/(.+)$", block, re.MULTILINE)
        if wt and br and br.group(1).strip() == branch:
            rep.warn("worktree", f"{Path(wt.group(1)).name} is checked out on {branch} - "
                                 f"remove it with /cicd-close-workingtree before deleting "
                                 f"the branch (never delete through its junctions)")


# ── 6. Which gate, exactly ─────────────────────────────────────────────────────

def gate_plan(repo: Path, lane: str) -> list[str]:
    """The commands the caller must actually run. Printed rather than executed: this script
    reports, and a gate that a preflight ran quietly is a gate nobody read the output of."""
    if lane != "LOCAL":
        return ["/cicd-push-e2e   (the full gate: suite + build + /cicd-e2e GREEN)"]
    plan: list[str] = []
    if (repo / ".agents/scripts/tests/run_all.py").is_file():
        plan.append("python3 .agents/scripts/tests/run_all.py")
    if (repo / ".agents/scripts/workflow_lint.py").is_file():
        # In the command centre (no deployable surface), lint the TOOLKIT only - a root
        # task close-out must not go red or green on whichever product project happens to
        # be named in .agents/active-project.txt (SCC-64).
        flag = " --toolkit-only" if not deploy_surface(repo) else ""
        plan.append(f"python3 .agents/scripts/workflow_lint.py{flag}")
    if not plan:
        plan.append("(no enforcement suite in this repo - say so; do not report a gate "
                    "that did not run)")
    return plan


def main() -> int:
    ap = argparse.ArgumentParser(description="Task close-out preflight (SCC-49)")
    ap.add_argument("--expect-key", required=True,
                    help="the Jira key you INTEND to close (e.g. SCC-64) - the resolved "
                         "branch must carry it; cwd is not intent (SCC-64)")
    ap.add_argument("--repo", help="repo root; default: walk up from cwd")
    ap.add_argument("--branch", help="branch to close; default: current HEAD")
    ap.add_argument("--fetch", action="store_true", help="fetch first (network)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = git_root(args.repo)
    branch = args.branch or wf.git(["rev-parse", "--abbrev-ref", "HEAD"], repo).stdout.strip()
    expect = args.expect_key.strip().upper()

    rep = wf.Report()
    key = check_branch(repo, branch, rep)
    check_intent(branch, key, expect, rep)
    check_children(key, rep)
    check_manifest(repo, branch, expect, rep)
    check_secondary(repo, expect, rep)
    check_sync(repo, branch, args.fetch, rep)
    check_base(repo, branch, rep)
    lane, touched = check_scope(repo, branch, rep)
    check_artifacts(repo, key, rep)
    check_worktree(repo, branch, rep)
    # Every check above this line reads a repo whose commits it ASSUMES were gated. That
    # assumption is only true while `core.hooksPath` is set - it is per-machine, git never
    # carries it, and a fresh clone has it unset with no error. Ask, do not assume (SCC-110).
    armed = hooks_armed.check(repo, rep)
    plan = gate_plan(repo, lane)

    if args.json:
        print(json.dumps({"repo": str(repo), "branch": branch, "key": key,
                          "expect_key": expect, "lane": lane,
                          "deployable_touched": touched, "gate": plan,
                          "hooks_armed": armed["armed"], "hooks": armed,
                          "findings": rep.items, "exit": rep.exit_code()}, indent=2))
    else:
        rep.print_human(f"task preflight - {branch}")
        print(f"LANE: {lane}")
        # Hoisted, not inlined: a replacement field spanning two physical lines is PEP 701 and
        # needs Python 3.12+. This file must parse on the PC too, and it is the one script the
        # close-out cannot run without (SCC-110 review, H1).
        gates = ("ARMED" if armed["armed"] else
                 "NOT ARMED - the checks above assume hooks that are not running")
        print(f"GATES: {gates}")
        for cmd in plan:
            print(f"  gate: {cmd}")
        e, _ = rep.counts()
        # A repo that CLAIMS gates and is not running them must never see the word "clear":
        # every check above it inferred something from commits that nothing actually checked.
        # A repo that never claimed gates is a different animal - it gets the normal line, with
        # the warning still standing above it (SCC-110 review, M4).
        if e:
            verdict = "BLOCKED - resolve the errors above"
        elif not armed["armed"] and armed["claims_gates"]:
            verdict = ("NOT CLEAR - no blocking error, but this repo's commit gates are not "
                       "running, so nothing mechanical checked any of the commits above")
        else:
            verdict = "clear to close out and merge"
        print("VERDICT: " + verdict)
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
