"""task_preflight.py — is this TASK branch safe to merge to main, and by WHICH gate? (SCC-49)

`/smh-close-task-merge-tree` closes **Task** work — workflow / IDE / rules / skills changes that
never got an epic and a story, and so can never reach `/cicd-close-story-merge-tree`. It merges
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
import walkthrough_roster as roster
import wf_common as wf

# ⭐ Re-exported from `wf_common`, which is where they live now (SCC-190 F6): the
# main-write gate needs `VERDICT_RE`/`strip_fenced`/`manifest_field` and was
# importing this whole module - and its six transitive dependencies - to get them.
# Same single definition, read off the leaf. Every existing importer still works.
VERDICT_RE = wf.VERDICT_RE
manifest_field = wf.manifest_field
strip_fenced = wf.strip_fenced
import hooks_armed
# SCC-146: the close-out reads the review's receipts. Imported the way closeout_preflight
# imports it, and for the same reason — two tools reading one receipt format must share one
# loader, or they drift apart about what a receipt even is.
import gate_receipt as gr
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
#
# ⛔ ORDER IS LOAD-BEARING (SCC-148). The scan below is first-match `startswith` over
# insertion order, so a specific prefix MUST precede any generic prefix of it —
# `claude/incident-` before `claude/` — or the generic entry swallows it and the specific
# one is dead code. That was the live bug: `/cicd-mobile-error-team` writes ONLY
# `claude/incident-<short-id-lower>` (no command anywhere creates a bare `incident/`), and
# a real incident branch was confidently routed to the STORY close-out — under production
# pressure, the worst moment for a wrong answer. test_task_preflight.py pins both
# properties: the exact key set (a reintroduced dead entry, or a dropped live one, forces
# a conscious edit there — the creator linkage itself was verified by hand at authoring)
# and no-shadowing (no entry unreachable behind an earlier prefix).
WRONG_LANE = {
    "epic/": ("/cicd-push-e2e", "an epic branch ships through the full gate, not this one"),
    "claude/incident-": ("/cicd-mobile-error-team", "incident branches have their own lane"),
    "claude/": ("/cicd-close-story-merge-tree",
                "a story branch lands on its EPIC branch at close-out, never on main"),
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
                   "`ticket: KEY-00` rows (the inline [{...}] form is not read) | riders: "
                   "[KEY-00, ...] subtasks whose work lands IN this lane, transitioned to "
                   "Done by the close ceremony (one-line flow style - a block list here is "
                   "not read)")




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


# One line, flow style, and NOTHING else - `\[` on the same physical line as the key. The
# hand parser's `\s*` idioms eat newlines, so a lazier pattern would half-read the block-list
# form and whichever half it kept would be wrong silently. An unread declaration fails CLOSED:
# check_children still blocks and its error prints the exact flow line to write.
RIDERS_RE = re.compile(r"^\s*riders\s*:[ \t]*\[([^\]\n]*)\]", re.MULTILINE)


def manifest_riders(repo: Path, expect: str, branch: str) -> frozenset[str]:
    """Subtask keys THIS lane declared it is carrying (SCC-156): their work lands in this
    lane's diff, so they are still open at preflight time BY DESIGN, and the close ceremony
    transitions them to Done first, the parent last - agent writes inside the operator-invoked
    close, never an operator edit. Settled sibling manifests are excluded for the same reason
    check_manifest() reads them as history: a landed lane's riders were flipped at ITS close,
    and inheriting the declaration would spare a child no one is actually carrying."""
    ref = base_ref(repo)
    keys: set[str] = set()
    for p, text in task_manifests(repo, expect):
        declared = manifest_field(text, "branch")
        if declared and declared != branch and manifest_settled(repo, p, ref):
            continue
        m = RIDERS_RE.search(text)
        if m:
            keys |= {k.strip().strip("\"'").upper()
                     for k in m.group(1).split(",") if k.strip()}
    return frozenset(keys)


# SCC-170: the ONLY value that means anything. Anything else - a typo, `full`, a mode a
# future ticket invents - is UNKNOWN and fails CLOSED, exactly like the block-form riders
# case: an unread declaration must never read as the permissive one.
LANDING_PARTIAL = "partial"

# ⛔ COLUMN-0 ANCHORED, and the key is `landing_mode`, not `landing`. `task.yaml` ALREADY has a
# `landing:` key - nested inside each `secondary_repos:` entry, values `independent-task` /
# `retain-on-epic` - and manifest_field's `^\s*` idiom happily matches an indented line, so the
# first cut of this read every cross-repo manifest's nested key as a landing MODE and blocked
# five green SCC-94 cases. Same family as the RIDERS_RE lesson: a permissive hand-parser pattern
# reads a neighbouring key and is confidently wrong. A distinct name plus `^` (no `\s*`) makes
# the collision unrepresentable rather than merely unlikely.
LANDING_MODE_RE = re.compile(r"^landing_mode\s*:[ \t]*([^\n#]*)", re.MULTILINE)


def manifest_landing(repo: Path, expect: str, branch: str) -> str | None:
    """The lane's declared landing mode, or None (SCC-170).

    A consolidated lane carries N subtasks on one branch. If it must ship before every part
    is built, the riders that DID land flip, the parent STAYS OPEN, and the rest becomes the
    next lane. Before this, check_children could not express that state: an open child that
    is not a declared rider blocks, full stop - so the only way to land early was to declare
    riders whose work is NOT in the diff, which is the exact lie the rider guard sentence
    forbids. The gate was pushing the lane into the failure it exists to prevent.

    Read from the SAME manifests as manifest_riders, on identical settled-lane rules: a landed
    sibling's `landing_mode: partial` is history and must not relax THIS close."""
    ref = base_ref(repo)
    value: str | None = None
    for p, text in task_manifests(repo, expect):
        declared = manifest_field(text, "branch")
        if declared and declared != branch and manifest_settled(repo, p, ref):
            continue
        m = LANDING_MODE_RE.search(text)
        if m and m.group(1).strip():
            value = m.group(1).strip().strip("\"'").lower()
    return value


KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")


def subject_keys(subject: str) -> frozenset[str]:
    """Every Jira key NAMED in one commit subject - not just the one that leads it.

    ⛔ SCC-282. This used to be `re.match` on the leading key only, and that collided with the
    house convention rather than with the gate: every command body leads a subject with the
    LANE's key (git-policy.md "lead the subject with the repo's Jira key"), so a consolidated
    lane's commits all lead with the PARENT key and no rider was ever found. Live proof on main:
    d9d9a9d reads "SCC-244 rider SCC-253: scripts/INDEX.md names a lever that is worth two
    seconds" - it IS that rider's whole implementation, and the leading-key reader did not see
    SCC-253 in it. The check fires at CLOSE-OUT, when every commit is immutable, so the only
    exits were rewriting history or abandoning the partial declaration. A rider's evidence is
    its key named ANYWHERE in a subject on the lane; `SCC-244 rider SCC-253: ...` and
    `SCC-253 fix: ...` both count."""
    return frozenset(k.upper() for k in KEY_RE.findall(subject))


def lane_commit_keys(repo: Path, branch: str) -> frozenset[str]:
    """Every Jira key NAMED in a commit subject on THIS lane, ahead of the mainline.

    The evidence half of `landing_mode: partial`. Declaring a rider says "this child's work is in
    this diff", and the ceremony flips it to Done on that word alone - so on a partial landing
    the word is checked against the commits. Range is explicit (`<merge-base>..HEAD` on this
    repo, via -C) rather than a bare `git log`: grep reads the branch you are parked on, and
    the preflight is routinely run from another tree."""
    ref = base_ref(repo)
    mb = wf.git(["merge-base", ref, branch], repo)
    if mb.returncode != 0 or not mb.stdout.strip():
        return frozenset()
    log = wf.git(["log", f"{mb.stdout.strip()}..{branch}", "--format=%s"], repo)
    if log.returncode != 0:
        return frozenset()
    keys: set[str] = set()
    for line in log.stdout.splitlines():
        keys |= subject_keys(line)
    return frozenset(keys)


def check_manifest(repo: Path, branch: str, expect: str,
                   rep: wf.Report) -> Path | None:
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
        return None
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
        return None

    # ⭐ SCC-192: this function already decides which manifest is THIS lane's contract, so it
    # is the one place that may say where the receipt goes. Deriving that a second time in the
    # writer is how two readers of one artifact drift apart about what the artifact even is.
    agreed: list[Path] = []
    for p, declared in live:
        if declared and declared != branch:
            rep.err("manifest", f"{rel_or_abs(p, repo)} declares branch `{declared}` but "
                                f"this preflight resolved `{branch}` - one of them is "
                                f"wrong; fix the manifest or aim at the declared branch")
        else:
            rep.info("manifest", f"{rel_or_abs(p, repo)} agrees: {expect} on "
                                 f"{declared or branch}")
            agreed.append(p)
    # Exactly one, or none. Two manifests agreeing on one branch is an ambiguity the receipt
    # must not resolve by picking - the PR gate reads the receipt BESIDE a manifest, so a
    # coin-flip here writes the evidence next to the wrong walkthrough.
    #
    # ⛔ AND IT HAS TO SAY SO. Returning None SILENTLY was the fourth loop, executed by two
    # review lenses independently: both manifests reported as INFO, the VERDICT still read
    # "clear to close out and merge", no receipt was written - and `main_write_gate --mode pr`
    # then DEMANDS a receipt beside EACH of them and prints a remedy (`re-run the preflight`)
    # that will again write nothing. A preflight that certifies a merge it has already made
    # unmergeable is worse than one that refuses: the operator is sent to a dead end by the
    # tool whose whole job is to keep them out of one.
    if len(agreed) > 1:
        rep.err("manifest",
                f"{len(agreed)} live task.yaml files declare {expect} on `{branch}`: "
                + ", ".join(rel_or_abs(q, repo) for q in agreed)
                + f" - {RECEIPT_NAME} is written BESIDE the lane's manifest and the PR gate "
                  f"reads it there, so two candidates means the evidence has no home. Keep "
                  f"the one that is THIS lane's contract; settle or remove the other.")
        return None
    return agreed[0] if agreed else None


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


def check_children(key: str | None, rep: wf.Report,
                   riders: frozenset[str] = frozenset(), timeout: int = 20,
                   landing: str | None = None,
                   lane_keys: frozenset[str] | None = None) -> None:
    """A parent Task does not close while its subtasks are still open (SCC-119).

    `riders` (SCC-156) are the subtask keys this lane's task.yaml declared it is carrying:
    work the operator ordered into THIS lane, so "still open at preflight" is the designed
    state, not an unfinished job. A declared rider WARNS with the ceremony's own transition
    command instead of blocking - and the warn names it an agent step, because no flow may
    ever leave the operator a manual board edit (operator ruling, 2026-08-14). The declared
    set only ever SHRINKS the error, never the check: an undeclared open child blocks
    exactly as before, and the error now teaches the declaration as the third exit beside
    finish-it and `Deferred`.

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

    # SCC-170. `partial` is the one value that relaxes anything, and it earns the relaxation
    # below by paying for it here: on a partial landing every declared rider must have real
    # work on the lane. Without that price, `landing_mode: partial` is a way to declare thirteen
    # riders, land two and flip all thirteen at the ceremony - the guard sentence's exact
    # failure, wearing a new key. Scoped to `partial` deliberately: a full landing's riders
    # are already covered by "the parent closes when the whole job is done", and widening it
    # would put a new blocking condition on every lane that has ever declared a rider.
    partial = False
    if landing is not None:
        if landing == LANDING_PARTIAL:
            partial = True
        else:
            rep.err("children", f"{key}: task.yaml says `landing_mode: {landing}` and nothing "
                                f"reads that value - the only landing mode is "
                                f"`landing_mode: {LANDING_PARTIAL}`. An unread declaration fails "
                                f"CLOSED: this close is gated exactly as if it said nothing.")
    if partial and riders and lane_keys is not None:
        absent = sorted(r for r in riders if r not in lane_keys)
        if absent:
            rep.err("children", f"{key}: a partial landing flips ONLY riders whose work is on "
                                f"this lane, and {', '.join(absent)} is/are named in no commit "
                                f"subject here - "
                                f"trim riders: to the subset that actually landed before you "
                                f"close, and carry the rest into the next lane's task.yaml. "
                                f"Never declare a ticket whose work is not real.")

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
    open_children: list[str] = []
    open_keys: list[str] = []
    riding = 0
    for item in items:
        fields = item.get("fields") or {}
        status = ((fields.get("status") or {}).get("name") or "").strip()
        if status.lower() in CHILD_CLOSED:
            continue
        ckey = (item.get("key") or "?").strip().upper()
        if ckey in riders:
            # Exact-key membership, never substring (the SCC-146 lesson: SCC-14 must not
            # match inside SCC-146) - both sides normalized upper by their builders.
            # The command stays on ONE physical line: the yes-guard in test_jira_feed.py
            # scans the command SPAN per line, and a wrap after `--status` reads as a
            # transition without `--yes`.
            cmd = f'acli jira workitem transition --key {ckey} --status "Done" --yes'
            riding += 1
            rep.warn("children", f"{key} subtask {ckey} ({status or '?'}) is a declared "
                                 f"RIDER - its work lands with this lane, and the close "
                                 f"ceremony transitions it to Done FIRST, parent last: "
                                 f"{cmd}  (an agent step inside the operator-invoked "
                                 f"close - never an operator edit)")
        else:
            open_children.append(f"{ckey} ({status or '?'})")
            open_keys.append(ckey)

    if open_children and partial:
        # The declared state, so it warns and proceeds - but it must NAME what is being left
        # behind and say the parent stays open, or the next lane inherits nothing and the
        # index quietly reads as finished.
        rep.warn("children", f"{key}: PARTIAL landing - {len(open_children)} subtask(s) do "
                             f"NOT land here and stay open: {', '.join(open_children)}. The "
                             f"declared riders flip at this close and the PARENT STAYS OPEN; "
                             f"carry the rest into the next lane as its task.yaml riders and "
                             f"name them in this walkthrough's `## Your Actions`.")
    elif open_children:
        example = ", ".join(sorted(set(riders) | set(open_keys)))
        rep.err("children", f"{key} has {len(open_children)} open subtask(s) - the parent "
                            f"closes LAST, when the whole job is done: "
                            f"{', '.join(open_children)}. Finish them, or descope one to "
                            f"`Deferred` if it is genuinely out of scope. If one's work "
                            f"genuinely lands IN THIS LANE, declare it in this lane's "
                            f"task.yaml - riders: [{example}] - and the close ceremony "
                            f"transitions it to Done first (an agent write inside the "
                            f"operator-invoked close). Never declare a ticket whose work "
                            f"is not real.")
    elif riding:
        # Not "all Done or Deferred" - a rider is still OPEN, by design. Saying otherwise
        # here would teach the reader the board is ahead of where it actually is.
        rep.info("children", f"{key}: {riding} rider(s) above are the ceremony's to close; "
                             f"every other subtask is Done or Deferred")
    elif items:
        rep.info("children", f"{key}: all {len(items)} subtask(s) are Done or Deferred - "
                             f"this parent is the last thing to close")
    else:
        rep.info("children", f"{key}: no subtasks")


def check_stalled_landing(repo: Path, fetch: bool, accept: bool, rep: wf.Report) -> None:
    """Is the DESTINATION itself unpushed? (SCC-159)

    Every other check in this file asks about the lane. None asked about `main` — and a local
    `main` ahead of `origin/main` is a landing that stalled: an earlier lane merged and never
    reached the remote. Every lane behind it then queues invisibly, which happened live on
    2026-08-14 for about an hour.

    Nothing downstream catches it either. Both close-out commands run `git pull --ff-only
    origin main` before merging, and that SUCCEEDS silently when local is merely ahead — it
    only errors on true divergence — so the next lane merges cleanly onto the stuck main and
    reports success. The `0 0` check they do run happens AFTER the push.

    Severity is deliberately split, and `fetch` here is the fetch's OUTCOME, not the flag —
    `check_sync` returns whether it actually succeeded. With a fresh fetch the answer is
    trustworthy and this is an ERROR. Without one — no `--fetch`, or a fetch that failed —
    the comparison is against whatever the last fetch saw, which on a plane is nothing, so it
    can only WARN. (The first cut took `args.fetch` and this paragraph was aspirational: a
    dead uplink hard-blocked the close-out on a stale comparison, found by three lenses.)
    And because
    reads succeed while pushes die on that same uplink, `--accept-unpushed-main` is the
    auditable way through: it downgrades this one check and says so in the output, so the
    walkthrough records that the operator chose it.
    """
    counts = wf.git(["rev-list", "--left-right", "--count", "origin/main...main"], repo)
    if counts.returncode != 0 or not counts.stdout.strip():
        rep.info("landing", "no local main and origin/main to compare")
        return
    # ⛔ NEVER FALL THROUGH ON AN UNREADABLE COUNT. This was `(split() + ["?", "?"])[:2]`,
    # and `"?"` is not the string `"0"` — so any answer this could not parse walked straight
    # into the ahead-branch and told the operator they were "? commit(s) ahead of origin/main",
    # an ERROR under `--fetch`. A local-only repo got its close-out refused on a diagnosis
    # that was literally a question mark (SCC-156 review, Test-Adequacy lens).
    parts = counts.stdout.split()
    if len(parts) < 2 or not (parts[0].isdigit() and parts[1].isdigit()):
        rep.info("landing", f"could not read origin/main...main ({counts.stdout.strip()!r}) "
                            f"- declined to judge the landing")
        return
    behind, ahead = int(parts[0]), int(parts[1])

    if ahead == 0:
        # `behind` was computed and never read. "level with origin/main" printed while
        # rev-list said `1  0` — an INFO line asserting the opposite of the truth, in the
        # commonest real state there is (a sibling landed, you have not pulled).
        if behind:
            rep.info("landing", f"main is {behind} commit(s) BEHIND origin/main - nothing is "
                                f"stalled ahead of you; absorb it before you merge")
        else:
            rep.info("landing", "main is level with origin/main (nothing stalled ahead of you)")
        return

    if behind:
        # ⛔ DIVERGED IS NOT STALLED, and the difference decides the remedy. `git push origin
        # main` is REJECTED non-fast-forward here, so prescribing it sends the operator into
        # an error; and the stalled-landing rationale ("`pull --ff-only` will NOT catch this")
        # is FALSE for this shape — divergence is the one case it does catch. Diagnosing both
        # states with one message meant the check was misdiagnosing and duplicating a net that
        # already works (SCC-156 review, Blind Hunter).
        what = (f"main has DIVERGED from origin/main - {ahead} ahead, {behind} behind. NOT a "
                f"stalled landing: a plain `git push origin main` is rejected "
                f"non-fast-forward, and `pull --ff-only` DOES catch this one. Reconcile main "
                f"first, then re-run")
    else:
        what = (f"main is {ahead} commit(s) ahead of origin/main - a STALLED LANDING: an "
                f"earlier lane merged and never reached the remote, and every lane behind it "
                f"queues behind that. Land it (`git push origin main`) or inspect it before "
                f"merging; `pull --ff-only` will NOT catch this, it succeeds when local is "
                f"merely ahead. In a multi-lane run this is usually the lane you JUST "
                f"merged and have not pushed yet - push main, then continue")
    if accept:
        rep.warn("landing", f"{what} - accepted by --accept-unpushed-main")
    elif fetch:
        rep.err("landing", f"{what} [--accept-unpushed-main to proceed anyway]")
    else:
        rep.warn("landing", f"{what} - the landing check ran vs the LAST fetch, so re-run "
                            f"with --fetch to be sure [--accept-unpushed-main to proceed "
                            f"anyway]")


def check_sync(repo: Path, branch: str, fetch: bool, rep: wf.Report,
               manifest: Path | None = None) -> bool:
    """`commit-and-push-are-one-action`: clean + 0/0, or the work is not finished. Merging
    an unpushed branch to main puts commits on production that exist on one disk.

    ⭐ RETURNS WHETHER THE REMOTE COMPARISON IS FRESH — a fetch was asked for AND succeeded.
    Three review lenses independently found `check_stalled_landing` keying on `args.fetch`,
    the FLAG, when its own docstring keys the severity on the OUTCOME ("no --fetch, or a
    fetch that failed ... can only WARN"). A dying uplink fails `git fetch` too, not only
    `git push`, so the offline operator was hard-blocked at exit 2 on a comparison this
    function had just warned was stale. Intent is not evidence; only the outcome is."""
    fresh = False
    if fetch:
        f = wf.git(["fetch", "--quiet"], repo, timeout=180)
        if f.returncode != 0:
            rep.warn("sync", "fetch failed - ahead/behind is vs the LAST fetch")
        else:
            fresh = True
    else:
        # ⭐ SCC-193 A · SEVERITY PARITY, and it is a fix, not a tidy-up. This was `info`
        # while a FAILED fetch was `warn` - so NEVER TRYING outranked TRYING AND FAILING, on
        # identical evidence (both compare against whatever the last fetch saw). It is also
        # the exact line SCC-164's close-out was told, underneath a VERDICT that still read
        # "clear to close out and merge": the agent grepped the report to ERROR|VERDICT and
        # the one fact that mattered was in neither. Same evidence, same severity, and the
        # verdict line below now carries it too.
        rep.warn("sync", "--no-fetch: ahead/behind is vs the LAST fetch, not the remote")

    # `-c core.quotepath=false`: git octal-quotes any path holding a non-ASCII byte, `"` or
    # `\`, and `own` below is built unquoted - so on a lane whose artifact folder carries one
    # (`…_SCC-3-café/`) the comparison never matched and the preflight counted its OWN
    # receipt as dirt, exit 2 on every re-run. `main_write_gate` met this first and passes
    # the same flag; one repo, one spelling of a path.
    # ⭐ SCC-211 · EVERY TREE THAT COULD BE GATED, not just the path `--repo` happened to name.
    # For `/smh-close-task-merge-tree` those are the same thing — its door stands in the lane —
    # but `/smh-merge-multiple-workingtrees` sets `REPO` to the tree you are STANDING in and
    # then preflights each lane's branch in turn. Orchestrating a set landing from the main
    # checkout is the natural way to run it, and there `--repo` is `main` (spotless) while
    # every lane's dirt sits in its own worktree, unseen — on the one path that is N
    # production merges at once. `wf.trees_to_measure` derives the tree from
    # `git worktree list`, and the same body backs `/cicd-push-e2e` and
    # `/cicd-close-story-merge-tree`, so the three doors cannot disagree about what they
    # measured.
    for tree_label, tree in wf.trees_to_measure(repo, branch):
        _check_tree_dirt(tree, tree_label, manifest, rep)

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
    return fresh


def _check_tree_dirt(repo: Path, label: str, manifest: Path | None, rep: wf.Report) -> None:
    """The dirty-tree classification for ONE tree. Body unchanged since SCC-192; it moved out
    of `check_sync` only so it can be applied to every tree that could be gated (SCC-211)."""
    dirty = wf.git(["-c", "core.quotepath=false", "status", "--porcelain"], repo).stdout.strip()
    if dirty:
        lines = dirty.splitlines()
        mem = [ln for ln in lines if ln[3:].startswith("_artifacts/_memory/")]
        # ⭐ SCC-192/SCC-178 · THE WRITER IS NOT ITS OWN DIRT. This script now writes a receipt
        # under `_artifacts/`, and on the very next run that file would read as an uncommitted
        # change and block the close-out it exists to evidence. `gate_receipt.py` met this
        # first and answered it the same way: the ONE file the writer owns is excluded from
        # the measurement, and nothing else is - a sibling artifact, another lane's file or any
        # code path still counts (the R4 control pins exactly that).
        # ⛔ THIS LANE'S receipt, by PATH - not "any file with that name". The first cut
        # matched the basename anywhere under `_artifacts/`, so a SIBLING lane's uncommitted
        # receipt was waved through too: another session's work dropped from the very count
        # that exists to notice it, and permissive in the direction that lets a close-out
        # look clean over someone else's unfinished writes. `check_manifest` has already
        # resolved which manifest is this lane's contract, so the owned path is known here.
        own = ""
        if manifest is not None:
            try:
                own = (manifest.parent / RECEIPT_NAME).resolve().relative_to(
                    repo.resolve()).as_posix()
            except (ValueError, OSError):
                own = ""
        mine = [ln for ln in lines
                if own and ln[3:].split(" -> ")[-1].strip() == own]
        rest = [ln for ln in lines if ln not in mem and ln not in mine]
        if rest:
            rep.err("sync", f"{label}: {len(rest)} uncommitted change(s) - commit "
                            f"(explicit paths) and push before merging")
        if mem:
            # Memory files are session output, and the session that wrote them may not be
            # this one - two lanes share one store. Naming them separately is what stops a
            # close-out from sweeping (or deleting) another session's memory to get green.
            rep.err("sync", f"{label}: {len(mem)} memory file(s) dirty under "
                            f"_artifacts/_memory/ - "
                            f"if ANOTHER session wrote them, park or leave them (never "
                            f"sweep, delete, or commit them under this task); if THIS "
                            f"session wrote them, commit them with explicit paths under "
                            f"this task's key first")
        if mine and not rest and not mem:
            rep.info("sync", f"{label} is clean ({len(mine)} uncommitted "
                             f"{RECEIPT_NAME} - this script's own receipt, not the lane's "
                             f"dirt; the close-out commits it with the flight event)")
    else:
        rep.info("sync", f"{label} is clean")


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
        # ⚠ This line USED to render DEPLOY_DIRS, which appends `.github/` - so in the command
        # centre it printed "no ... .github" while `.github/workflows/main-write-gate.yml` sat
        # right there. The VERDICT was correct (a CI dir cannot deploy a repo that ships
        # nothing - see the TWO LISTS note above); only the sentence was false, and a gate that
        # states something plainly untrue teaches the reader to stop believing its output.
        # It renders PRODUCT_DIRS now, which is the list actually consulted here.
        rep.info("scope", "this repo has no deployable surface (no "
                          + ", ".join(d.rstrip('/') for d in PRODUCT_DIRS)
                          + ") - there is no E2E suite here to skip"
                          + (f"; `{CI_DIR}` exists but ships nothing on its own here"
                             if (repo / CI_DIR).is_dir() else ""))
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

def check_artifacts(repo: Path, key: str | None, rep: wf.Report) -> list[Path]:
    """A walkthrough is what the Dev Record points AT, so its absence means the close-out
    would post a record citing nothing. `artifacts-always-first` exempts the plan on this
    lane; it never exempts the walkthrough.

    Returns the hit paths: `check_gate` reads the review verdict out of the SAME resolution
    (SCC-146) — a second walkthrough-finder would be a second chance to disagree."""
    if not key:
        return []
    root = repo / "_artifacts"
    lower = key.lower()
    # A missing `_artifacts/` tree is NOT "nothing to check" - it is the strongest possible
    # evidence the walkthrough was never written. Reporting it as a warning is how a check
    # goes quiet on precisely the repo that needed it.
    # ⛔ Match the path RELATIVE to `_artifacts/`, never the absolute path: a worktree named
    # after its key (`.claude/worktrees/scc-38-lane/`) puts the key into EVERY walkthrough's
    # absolute path, and every historic walkthrough without `## Your Actions` then blocks an
    # unrelated lane (found live, SCC-38 review). Same class as check_maps' cwd-basename trap.
    hits = [p for p in root.glob("**/walkthrough.md")
            if lower in str(p.parent.relative_to(root)).lower() or lower in wf.read_text(p).lower()
            ] if root.is_dir() else []
    if not hits:
        where = "no _artifacts/ tree in this repo" if not root.is_dir() \
            else f"no walkthrough.md mentions {key}"
        rep.err("artifacts", f"{where} - write the walkthrough before closing out; "
                             f"the Dev Record links it")
        return []
    for p in hits:
        rep.info("artifacts", rel_or_abs(p, repo))
        # `jira_feed.py finish` REFUSES to close a ticket whose walkthrough has no
        # `## Your Actions` - an absent section is not evidence that nothing is owed. Both
        # close-outs run it at Step 4, which is AFTER the merge, so the refusal used to land
        # at the one moment it could no longer be acted on cheaply. This is that same
        # refusal, one gate earlier; nothing that passes the close-out today starts failing
        # (SCC-155 review #22).
        if "## your actions" not in wf.read_text(p).lower():
            rep.err("artifacts", f"{rel_or_abs(p, repo)} has no `## Your Actions` section - "
                                 f"`jira_feed.py finish` refuses to close a ticket without "
                                 f"one, so this blocks at the merge either way. Add the "
                                 f"section (even empty) so the answer is recorded rather "
                                 f"than assumed")
    return hits


# ── 4.5. What did the REVIEW say, and can its evidence spare the gate? (SCC-146) ──────


# A line that LOOKS like a verdict stamp but fails the canonical regex — bolded, lowercased,
# or heading-prefixed (the three real-world shapes the SCC-146 review named). Requiring a
# status word AND an `@` is what keeps prose out. ⛔ The marker class is DELIBERATELY narrow
# (SCC-154 review): `\s`, backtick and `>` were in it and made INDENTED code-block quotes,
# inline-code citations and blockquoted stamps — house-standard EVIDENCE shapes that carry
# the `@` by construction — a hard exit-2 false red on the shipping path. Now only heading /
# bold / italic markers match. Known safe misses, on purpose: a dash-bulleted, blockquoted,
# indented or backtick-quoted stamp is ignored, which can never grant a SKIP and, under
# governing-latest, can never demote a canonical stamp either. (`* `-bulleted stamps still
# err — `*` must stay for `**Verdict…**` — the asymmetry is documented here, not papered
# over.)
NEAR_MISS_LINE = re.compile(r"^[#*_]{0,4} ?verdict\b[^\n]*?\b(?:pass|concerns|fail|waived)"
                            r"\b[^\n]*@", re.IGNORECASE)




def nonartifact_moved(repo: Path, sha: str) -> list[str] | None:
    """Paths changed between `sha` and HEAD that are NOT under `_artifacts/`.

    This is /smh-code-review Step 3's freshness rule made mechanical: artifact-only commits
    after the run do not invalidate it; code, test or doc changes do (the rule once said
    "doc-only" too, which overstated the mechanism — only `_artifacts/` is exempt, and a
    `docs/` commit invalidates; SCC-146 review finding 12, proven live when a docs commit
    staled a receipt mid-review). The verdict and the receipts always predate the artifacts
    commit that carries them (the stamp cannot cite the commit it rides in), so strict sha
    equality would mean no real lane could ever SKIP — observed live on SCC-149 (review
    finding C4). None = unknown sha here, which the callers treat as stale (fail toward
    running)."""
    r = wf.git(["diff", "--name-only", f"{sha}..HEAD"], repo)
    if r.returncode != 0:
        return None
    return [p.strip() for p in r.stdout.splitlines()
            if p.strip() and not p.strip().startswith("_artifacts/")]


def check_gate(repo: Path, hits: list[Path], lane: str, expect: str, branch: str,
               rep: wf.Report) -> str | None:
    """Read the review's `Verdict: ... @ <sha>` and decide the close-out gate's fate:

      any governing latest-stamp FAIL               -> rep.err: the merge is REFUSED
      governing PASS/CONCERNS + code-fresh
        + receipts valid                            -> return the `SKIP` line
      anything else (no governing verdict, WAIVED,
      ambiguous, moved, upstream errors,
      missing/invalid receipts)                     -> return None: the plan prints as today

    ⭐ GOVERNING means the walkthrough sits in this task's OWN session dir — beside a
    `task.yaml` declaring `task_key: <expect>`. check_artifacts matches by SUBSTRING
    (SCC-14 ⊂ SCC-146) and by content mention, so its pool can hold FOREIGN walkthroughs —
    proven live when this system's own close-out saw a sibling lane's PASS stamp in its
    pool (SCC-146 review findings 1/2/3). Foreign evidence neither grants a SKIP nor
    blocks: this lane's gate runs in full instead, which never trusts and never wedges.

    ⭐ And a LANDED lane's dir is history, not this run's contract — the same
    `manifest_settled` rule check_manifest applies: a settled manifest declaring another
    branch neither governs nor counts as ambiguity, or every follow-on lane of a
    multi-lane ticket would be wedged forever by its landed sibling (SCC-154 review).

    ⛔ THE FAIL SCAN RUNS BEFORE THE AMBIGUITY RETURN, and the order is load-bearing: with
    the guard first, a lane whose OWN latest stamp said FAIL slid past on an info line
    whenever a second stamped dir existed — a typo'd FAIL blocked harder than a canonical
    one (three review lenses converged on it). Ambiguity may withhold a SKIP; it must
    never withhold the block.

    Within one walkthrough the LATEST stamp governs — a re-review APPENDS its stamp, so
    FAIL-then-PASS clears and PASS-then-FAIL blocks. The old any(FAIL)-over-all-hits rule
    made the FAIL error's own remedy (re-run the review) unable to ever clear it.

    Fail toward running, never toward trusting (/cicd-code-review Step 3, ported). ONLY
    this function may produce a SKIP — the close-out command never decides one by reading.
    """
    if lane != "LOCAL" or not hits:
        return None
    ref = base_ref(repo)
    stamped: list[tuple[Path, list[tuple[str, str]]]] = []
    foreign_stamped = 0
    for p in hits:
        man = p.parent / "task.yaml"
        man_text = wf.read_text(man) if man.is_file() else ""
        text = strip_fenced(wf.read_text(p))
        found = [(m.group(1).upper(), m.group(2)) for m in VERDICT_RE.finditer(text)]
        if not (man_text and manifest_field(man_text, "task_key") == expect):
            foreign_stamped += 1 if found else 0
            continue
        declared = manifest_field(man_text, "branch")
        if declared and declared != branch and manifest_settled(repo, man, ref):
            rep.info("gate", f"{rel_or_abs(p, repo)}: a landed lane's dir (settled on "
                             f"{ref}) - history, neither governing nor ambiguous")
            continue
        # Near-miss stamps are an ERROR, and only in GOVERNING walkthroughs: a typo'd FAIL
        # must never demote to "no verdict, clean full run" (SCC-146 finding 6), while a
        # foreign lane's odd prose must never block a lane it does not govern.
        for ln in text.splitlines():
            if NEAR_MISS_LINE.match(ln) and not VERDICT_RE.match(ln):
                rep.err("gate", f"{rel_or_abs(p, repo)}: a verdict-looking line does not "
                                f"parse as the canonical stamp (`{ln.strip()[:70]}`) - fix "
                                f"the stamp; an unreadable verdict cannot gate a merge")
        if found:
            stamped.append((p, found))
            # ⛔ SCC-173/SCC-177 — the same parser closeout_preflight calls, handed the verdict
            # THIS file's own (stricter) regex just read. A stamp says what the review decided;
            # the roster is what shows it happened, and 130 of 142 walkthroughs had neither.
            #
            # ⛔ `found[-1]`, NEVER `found[0]` — THE LATEST STAMP GOVERNS, and this call site got
            # it wrong on the first cut. A re-review APPENDS its stamp, so a walkthrough reading
            # FAIL-then-PASS is a lane that was fixed; judging the roster against `found[0]`
            # hands this parser the superseded FAIL, which returns "Verdict FAIL" and blocks a
            # lane the rest of this function (`v[-1][0]`, `verdicts[-1]`) has already cleared.
            # That is the exact any(FAIL)-over-all-hits defect the docstring above records as
            # fixed: the remedy for a FAIL — re-run the review — could never clear it.
            ok_roster, why = roster.judge(text, p, found[-1][0])
            for line in why:
                (rep.info if ok_roster else rep.err)("gate", f"{rel_or_abs(p, repo)}: {line}")
    if not stamped:
        if foreign_stamped:
            rep.info("gate", f"verdict stamp(s) exist only in {foreign_stamped} "
                             f"walkthrough(s) whose task.yaml does not declare {expect} - "
                             f"foreign evidence never gates this lane; the full gate runs")
        else:
            rep.info("gate", "no review Verdict line in this task's own walkthrough - "
                             "the full gate runs")
        return None
    if any(v[-1][0] == "FAIL" for _, v in stamped):
        rep.err("gate", "the review verdict is FAIL - fix on the branch and re-run the "
                        "review; a FAIL lane does not merge")
        return None
    if len(stamped) > 1:
        rep.info("gate", f"{len(stamped)} walkthroughs under {expect} carry verdict "
                         f"stamps - which one governs is ambiguous; the full gate runs")
        return None
    wt, verdicts = stamped[0]
    status, sha = verdicts[-1]          # the LATEST stamp governs; a re-review APPENDS
    if status == "WAIVED":
        rep.info("gate", "verdict WAIVED (no suite exists to receipt) - treated as "
                         "CONCERNS; the printed gate plan stands")
        return None
    errs, _ = rep.counts()
    if errs:
        # Something upstream already blocks (dirty tree, unabsorbed main, open children...).
        # A SKIP printed beside a red finding would be a contradiction wearing a verdict.
        return None
    moved = nonartifact_moved(repo, sha)
    if moved is None:
        rep.warn("gate", f"verdict sha {sha[:8]} is not a commit here - cannot verify "
                         f"freshness; the full gate runs")
        return None
    if moved:
        rep.info("gate", f"code moved since the verdict ({len(moved)} non-artifact "
                         f"file(s), e.g. {moved[0]}) - the full gate runs")
        return None
    gates_dir = wt.parent / "gates"
    receipts = sorted(gates_dir.glob("*.json")) if gates_dir.is_dir() else []
    if not receipts:
        rep.info("gate", f"no receipts beside {rel_or_abs(wt, repo)} - the full gate runs "
                         f"(fail toward running, never toward trusting)")
        return None
    names: list[str] = []
    for rpath in receipts:
        data = gr.load_receipt(wt.parent, "unused", rpath.stem, wf.Report(), flat=True)
        # The RESULT half of validity is the shared loader's (one receipt format, one
        # reader — SCC-146's own rationale, finished by SCC-154 finding 10). Dirt POLICY
        # stays here: the recorder records strictly, and THIS consumer exempts dirt that
        # cannot affect the gate — `_artifacts/` is exactly what the freshness checks
        # already exempt (C6). No recorded paths (an older receipt) = no exemption.
        got = gr.receipt_defect(data)
        if got is None and data.get("dirty_tree"):
            paths = data.get("dirty_paths")
            if not (paths and all(str(p).replace("\\", "/").startswith("_artifacts/")
                                  for p in paths)):
                got = (f"result={data.get('result')} DIRTY"
                       + (" (non-artifacts dirt)" if paths else ""))
        if got:
            rep.info("gate", f"receipt {rpath.stem}: {got} - the full gate runs")
            return None
        rsha = str(data.get("sha") or "")
        rmoved = nonartifact_moved(repo, rsha) if rsha else None
        if rmoved is None or rmoved:
            rep.info("gate", f"receipt {rpath.stem}: stamped at {rsha[:8] or '?'} and code "
                             f"moved since - the full gate runs")
            return None
        names.append(rpath.stem)
    if "suite" not in names:
        rep.info("gate", "no `suite` receipt (the enforcement-suite run is the one that "
                         "matters) - the full gate runs")
        return None
    return f"SKIP - verdict {status} @ {sha[:8]}, receipts valid ({', '.join(names)})"


# ── 5. Anything still holding the branch? ──────────────────────────────────────

def check_worktree(repo: Path, branch: str, rep: wf.Report) -> None:
    """A worktree checked out on this branch blocks `git branch -d` after the merge, and
    deleting through one destroys the shared assets it junctions to
    (`/cicd-prune-worktree` Step 3a)."""
    out = wf.git(["worktree", "list", "--porcelain"], repo).stdout
    # [0] is the MAIN checkout, which is standing on this branch by definition when the
    # command runs from it - reporting that as "a worktree holds your branch" is a warning
    # that fires on every single clean run, and a warning that always fires gets ignored.
    for block in out.split("\n\n")[1:]:
        wt = re.search(r"^worktree (.+)$", block, re.MULTILINE)
        br = re.search(r"^branch refs/heads/(.+)$", block, re.MULTILINE)
        if wt and br and br.group(1).strip() == branch:
            rep.warn("worktree", f"{Path(wt.group(1)).name} is checked out on {branch} - "
                                 f"remove it with /cicd-prune-worktree before deleting "
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
    if (repo / ".agents/scripts/check_maps.py").is_file():
        # SCC-138. Without this the gate could not fail on the map/INDEX linter, because it
        # never ran it - and twice in one day the two disagreed with only the linter right
        # (SCC-124 landed a session folder with no INDEX row; SCC-119 nearly did) while
        # run_all reported 21/21 PASS. A clean verdict printed over a red linter is worse
        # than no verdict: it turns a detectable problem into a trusted one.
        #
        # ⛔ `--depth3-only --strict`, never bare check_maps. The close-out runs from a
        # WORKTREE, and bare check_maps there exits 1 on two GUARANTEED false positives
        # ("AUTO block is STALE" and "on disk but not in map: <lane-name>/") whose printed
        # remedy would ship the lane name into the map bound for main. `--depth3-only` is
        # the subset free of both. `--strict` is what makes it a gate at all: the bare form
        # exits 0 even on drift, because SessionStart runs it as a nag.
        plan.append("python3 .agents/scripts/check_maps.py --depth3-only --strict")
    if not plan:
        plan.append("(no enforcement suite in this repo - say so; do not report a gate "
                    "that did not run)")
    return plan


# ── SCC-192 · THE PREFLIGHT RECEIPT ────────────────────────────────────────────────────
#
# THE DEFECT IT CLOSES. An agent can perform this ceremony's steps BY HAND instead of invoking
# `/smh-close-task-merge-tree`, and until now nothing in the system could tell: the steps it
# does run all pass, so the omission is silent. Measured live on SCC-164's own landing (PR #13,
# 2026-08-16) - Step 2.5 skipped entirely, this preflight run without a fetch, both invisible
# until the operator asked what the workflow was. The PR was green the whole time.
#
# Rules and memory are not the fix: the agent had READ the rule when it broke it. What detects
# the ABSENCE of a ceremony is an artifact the ceremony leaves behind, so this writes one and
# `main_write_gate.py --mode pr` REQUIRES it. Both measured deviations produce a red check.
#
# ⛔ KEYED ON THE VERDICT SHA, NEVER ON HEAD - the constraint that makes it usable at all.
# Committing the receipt MOVES HEAD, so a receipt that must equal HEAD can never pass and the
# tree is dirty forever. The flight recorder solved this first (its docstring, § KEYING) and
# this reuses that answer: the walkthrough's governing `Verdict: ... @ <sha>`, read with the
# same two helpers, latest stamp governing. A lane with no stamp yet records `null` and says so.
RECEIPT_NAME = "preflight-receipt.json"
RECEIPT_SCHEMA_V = 1


def verdict_stamp(art_dir: Path, repo: Path) -> tuple[str | None, str | None]:
    """The governing verdict sha beside a manifest, and that commit's own date.

    `strip_fenced` + `VERDICT_RE` + `[-1]` - the same reader `check_gate` and the flight
    recorder use. Three readers of one stamp would be two too many."""
    wt = art_dir / "walkthrough.md"
    if not wt.is_file():
        return None, None
    found = VERDICT_RE.findall(strip_fenced(wf.read_text(wt)))
    if not found:
        return None, None
    sha7 = found[-1][1]
    r = wf.git(["rev-parse", "--verify", "-q", sha7 + "^{commit}"], repo)
    if r.returncode != 0 or not r.stdout.strip():
        return None, None
    sha = r.stdout.strip()
    when = wf.git(["show", "-s", "--format=%cI", sha], repo).stdout.strip() or None
    return sha, when


def write_receipt(manifest: Path | None, repo: Path, *, key: str, branch: str, lane: str,
                  fetch: bool, fresh: bool, accept: bool, verdict: str,
                  rep: wf.Report) -> Path | None:
    """One small JSON beside the lane's `task.yaml`. Returns the path, or None.

    No manifest = no receipt, deliberately: the PR gate finds receipts BY the manifest in the
    diff, so a receipt written anywhere else is evidence nothing will ever read, and inventing
    a location is worse than the absence the gate can at least report.

    ⭐ IDEMPOTENT ON CONTENT (A7). Every field is derived from the lane's state, never from the
    clock or from HEAD, so a re-run on an unchanged lane rewrites the same bytes - and the
    write is skipped entirely when they match, so a resumed close-out produces no churn commit.
    """
    if manifest is None:
        return None
    art = manifest.parent
    sha, when = verdict_stamp(art, repo)
    e, w = rep.counts()
    payload = {
        "schema_v": RECEIPT_SCHEMA_V,
        "task_key": key,
        "branch": branch,
        "verdict_sha": sha,
        "when": when,
        "fetch": bool(fetch),
        "fresh": bool(fresh),
        "accept_unpushed_main": bool(accept),
        "lane": lane,
        "verdict": verdict,
        "errors": e,
        "warnings": w,
        "exit": rep.exit_code(),
    }
    body = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path = art / RECEIPT_NAME
    try:
        # ⛔ `read_text` raises UnicodeDecodeError - a ValueError, which `except OSError`
        # never caught - on a receipt whose bytes are not UTF-8. That is exactly what an
        # INTERRUPTED close-out leaves behind, so the crash landed on the run that would
        # have replaced the corruption. Unreadable bytes are not evidence: rewrite them.
        try:
            same = path.is_file() and path.read_text(encoding="utf-8") == body
        except (UnicodeError, ValueError):
            same = False
        if not same:
            path.write_text(body, encoding="utf-8")
    except OSError as exc:
        # A receipt that cannot be written is worth saying out loud and is never fatal here:
        # the PR gate is the thing that refuses, and it refuses on the ABSENCE. Failing the
        # preflight on a read-only checkout would block a close-out over a filesystem.
        rep.warn("receipt", f"could not write {rel_or_abs(path, repo)}: {exc}")
        return None
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Task close-out preflight (SCC-49)")
    ap.add_argument("--expect-key", required=True,
                    help="the Jira key you INTEND to close (e.g. SCC-64) - the resolved "
                         "branch must carry it; cwd is not intent (SCC-64)")
    ap.add_argument("--repo", help="repo root; default: walk up from cwd")
    ap.add_argument("--branch", help="branch to close; default: current HEAD")
    # ⭐ SCC-193 A · DEFAULT-ON. `--fetch` was opt-in, so the close-out's freshness rested on
    # an agent remembering a flag - and on 2026-08-16 one typed the invocation from memory of
    # the signature rather than from the door's line, and measured ahead/behind against a
    # fetch from the day before. `--fetch` still parses (every existing caller keeps working);
    # `--no-fetch` is the explicit offline opt-out, and a FAILED fetch only warns, so
    # default-on is safe on a plane.
    ap.add_argument("--fetch", action=argparse.BooleanOptionalAction, default=True,
                    help="fetch before comparing (default: on). --no-fetch is the offline "
                         "opt-out and makes the VERDICT say the comparison is stale")
    ap.add_argument("--no-receipt", action="store_true",
                    help="do not write the preflight receipt. For probes and harnesses that "
                         "want the verdict without touching the tree; the close-out never "
                         "passes it, and the PR gate refuses a lane that has no receipt")
    ap.add_argument("--accept-unpushed-main", action="store_true",
                    help="proceed with a local main ahead of origin/main (SCC-159). "
                         "The auditable offline exit: reads succeed while pushes die "
                         "on a satellite uplink, so a hard refusal would brick every "
                         "close-out made from a plane. Prints itself back into the "
                         "output; typed per invocation, never sticky")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = git_root(args.repo)
    branch = args.branch or wf.git(["rev-parse", "--abbrev-ref", "HEAD"], repo).stdout.strip()
    expect = args.expect_key.strip().upper()

    rep = wf.Report()
    key = check_branch(repo, branch, rep)
    check_intent(branch, key, expect, rep)
    check_children(key, rep, riders=manifest_riders(repo, expect, branch),
                   landing=manifest_landing(repo, expect, branch),
                   lane_keys=lane_commit_keys(repo, branch))
    manifest = check_manifest(repo, branch, expect, rep)
    check_secondary(repo, expect, rep)
    # ⭐ `fresh`, not `args.fetch`. check_sync ran the fetch and knows whether it WORKED;
    # passing the flag instead made a dead uplink produce a hard exit 2 on a stale answer.
    fresh = check_sync(repo, branch, args.fetch, rep, manifest)
    check_stalled_landing(repo, fresh, args.accept_unpushed_main, rep)
    check_base(repo, branch, rep)
    lane, touched = check_scope(repo, branch, rep)
    art_hits = check_artifacts(repo, key, rep)
    check_worktree(repo, branch, rep)
    # Every check above this line reads a repo whose commits it ASSUMES were gated. That
    # assumption is only true while `core.hooksPath` is set - it is per-machine, git never
    # carries it, and a fresh clone has it unset with no error. Ask, do not assume (SCC-110).
    armed = hooks_armed.check(repo, rep)
    # SCC-146: the review verdict + its receipts can spare the lane a fourth identical
    # suite run — or refuse the merge outright on a FAIL. Runs after every other check so
    # its no-upstream-errors guard sees the complete picture.
    skip = check_gate(repo, art_hits, lane, expect, branch, rep)
    plan = gate_plan(repo, lane)
    if skip:
        # ⛔ A SKIP spares the SUITE ONLY (SCC-154, review compound C4). Every SKIPping lane
        # structurally carries at least one post-verdict `_artifacts/` commit the suite
        # receipt never inspected — the stamp cannot cite the commit it rides in — and
        # map/INDEX drift is exactly `_artifacts/`-borne. The cheap artifact-scoped checks
        # therefore still print; only the run the receipts actually prove is replaced.
        plan = [skip if "run_all.py" in cmd else cmd for cmd in plan]

    # ⭐ THE VERDICT IS COMPUTED ONCE, ABOVE BOTH OUTPUT PATHS, AND THE RECEIPT RECORDS IT.
    # It used to be built inline in the human branch, so `--json` callers and the receipt could
    # only ever re-derive it - two spellings of one answer is how they drift.
    e, _w = rep.counts()
    if e:
        verdict = "BLOCKED - resolve the errors above"
    elif not fresh:
        # ⭐ SCC-193 A · THE FRESHNESS GOES ON THE VERDICT LINE. It was an INFO three lines
        # above a verdict that read "clear to close out and merge", and the verdict line is the
        # only line an agent acts on. Exit is already non-zero here (check_sync warns), so this
        # is a stop, not a footnote: re-run without --no-fetch, or say why offline was chosen.
        # The two ways `fresh` goes false need DIFFERENT remedies, and printing the
        # --no-fetch one at an operator who never passed it (R3: the uplink was dead) is a
        # no-op instruction under a verdict they are supposed to act on. The receipt already
        # distinguishes them (`fetch: true, fresh: false`); the verdict line now does too.
        verdict = ("clear - but vs the LAST fetch (STALE), not the remote; "
                   + ("the fetch was asked for and FAILED - fix the uplink and re-run"
                      if args.fetch else
                      "re-run WITHOUT --no-fetch")
                   + " before you merge")
    else:
        verdict = "clear to close out and merge"

    if not args.no_receipt:
        got = write_receipt(manifest, repo, key=expect, branch=branch, lane=lane,
                            fetch=args.fetch, fresh=fresh,
                            accept=args.accept_unpushed_main, verdict=verdict, rep=rep)
        if got is not None:
            rep.info("receipt", f"{rel_or_abs(got, repo)} - the PR gate requires it; commit "
                                f"it with the flight event (close-out Step 2.5)")
        elif manifest is not None:
            # ⛔ THE VERDICT CANNOT SAY "clear" WHEN THE EVIDENCE WAS NOT WRITTEN. `write_receipt`
            # warns and returns None on an OSError (an unwritable tree), and
            # `main_write_gate --mode pr` refuses on the receipt's ABSENCE - so the run would
            # certify a merge it has already made impossible. That is the exact shape this lane
            # upgraded the two-manifest case to an error for, and the same answer applies: a
            # preflight that sends the operator to a dead end is worse than one that refuses.
            # (`manifest is None` is a different thing entirely - no lane owes a receipt then,
            # and R5 pins that.)
            verdict = ("BLOCKED - the receipt could not be written, and the PR gate refuses a "
                       "close-out PR without one")

    if args.json:
        print(json.dumps({"repo": str(repo), "branch": branch, "key": key,
                          "expect_key": expect, "lane": lane,
                          "deployable_touched": touched, "gate": plan,
                          "verdict": verdict, "fetch": args.fetch, "fresh": fresh,
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
        # A repo that CLAIMS gates and is not running them must never see the word "clear":
        # every check above it inferred something from commits that nothing actually checked.
        # A repo that never claimed gates is a different animal - it gets the normal line, with
        # the warning still standing above it (SCC-110 review, M4).
        #
        # ⛔ That rule is enforced ENTIRELY by `hooks_armed.check()`, which is why there is no
        # third branch here. A `NOT CLEAR` verdict used to sit between these two and was
        # UNREACHABLE (SCC-140): reaching it needed `armed=False` AND `claims_gates=True`, but
        # check() makes every finding a hard `rep.err` in exactly that case, so `e` is non-zero
        # and BLOCKED always wins. It was also self-contradictory - the text refused the merge
        # while `rep.exit_code()` returned 1, which callers read as "warnings only". Deleted
        # rather than pinned with a test: a test over unreachable code buys nothing and makes
        # the dead branch look load-bearing to the next reader.
        print("VERDICT: " + verdict)
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
