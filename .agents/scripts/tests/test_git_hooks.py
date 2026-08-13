"""test_git_hooks.py — does a merge land where you think it does? (SCC-144)

Every gate in this system checks the branch you merge FROM: `--expect-key`, the preflight's header,
`main_write_gate.py`, the push token. NOTHING checked the branch you merge INTO. On 2026-08-11 a
`cd` in one tool call and a bare `git merge` in a later one — by which time the shell's working
directory had silently reverted — put a production merge commit on a SIBLING LANE's branch and
printed success (SCC-97, commit 0b380d4, two parents). It was caught by suspicion, not by machinery.

⛔ EVERY CASE HERE DRIVES REAL GIT. Not one of them greps a script for a string. A source-grep guard
cannot see whether git ever invoked the hook, and this repo has already shipped guards that pinned a
file's PROSE while the wiring underneath said the opposite (SCC-125). So each fixture is a real repo
with a real `core.hooksPath`, and the assertion is on what `git merge` / `git push` actually did.

⭐ THE ALLOW HALF OUTNUMBERS THE REFUSE HALF, ON PURPOSE. A gate that refuses everything is as broken
as one that refuses nothing, and the expensive failure here is the false red: a guard that blocks a
correct merge is one an operator learns to route around, and this repo has shipped four of those
(`hooks_armed`'s README, its dotfiles, its `~` expansion, `check_maps` in a worktree). Cases A, C, D,
H, I, M, N and O are negative controls and they are load-bearing.

Stdlib only, no pytest, matching every other file here.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hooks_armed  # noqa: E402 — _harness puts .agents/scripts on sys.path

REPO = Path(__file__).resolve().parents[3]
HOOKDIR = REPO / ".agents/scripts/git-hooks"

GUARD = HOOKDIR / "merge-target-guard.sh"
BACKSTOP = HOOKDIR / "pre-push-merge-backstop.sh"
FLAG = HOOKDIR / "MERGE-TARGET-ENFORCE"
MERGE_DISPATCH = REPO / ".githooks/commit-msg"
PUSH_DISPATCH = REPO / ".githooks/pre-push"

ZERO = "0" * 40


def sh(*args: str, cwd: Path, stdin: str = "") -> tuple[int, str]:
    r = subprocess.run(list(args), cwd=str(cwd), input=stdin,
                       capture_output=True, text=True, errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def head(d: Path) -> str:
    return sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()


def make_repo(tmp: Path, *, name: str = "work",
              scripts=(GUARD,), hooks=(MERGE_DISPATCH,), arm: bool = True) -> Path:
    """A real repo carrying the REAL hook files, armed the way this system arms them.

    ⛔ Missing files are COPIED IF PRESENT, never demanded. A `shutil.copy2` on a script that does
    not exist yet raises in SETUP, and a test that dies in setup looks identical to one that failed
    its assertion — only one of those is a real red. Before the guard is built these fixtures come
    up gate-less and the cases fail where they assert, which is what makes the RED honest.
    """
    d = tmp / name
    d.mkdir()
    sh("git", "init", "-q", "-b", "main", cwd=d)
    sh("git", "config", "user.email", "t@t.t", cwd=d)
    sh("git", "config", "user.name", "t", cwd=d)
    (d / ".agents/scripts/git-hooks").mkdir(parents=True)
    (d / ".githooks").mkdir()
    for f in scripts:
        if f.is_file():
            shutil.copy2(f, d / ".agents/scripts/git-hooks" / f.name)
            (d / ".agents/scripts/git-hooks" / f.name).chmod(0o755)
    for f in hooks:
        if f.is_file():
            shutil.copy2(f, d / ".githooks" / f.name)
            (d / ".githooks" / f.name).chmod(0o755)
    if arm:
        (d / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").write_text("armed\n", encoding="utf-8")
    (d / "README").write_text("x\n", encoding="utf-8")
    sh("git", "add", "README", ".agents", ".githooks", cwd=d)
    sh("git", "commit", "-qm", "SCC-144 base", cwd=d)
    sh("git", "config", "core.hooksPath", ".githooks", cwd=d)
    return d


def make_pushable(tmp: Path, *, push_main: bool = True,
                  scripts=(GUARD, BACKSTOP), extra_flags=()) -> tuple[Path, Path]:
    """A repo with a REAL bare remote, so the push cases drive `git push` and not a stub.

    Everything the push gates need can be faked at the script level; whether git actually invokes
    the dispatcher, and whether the dispatcher actually feeds both gates, cannot. That is the
    whole point of these fixtures — `test_main_push_gate.py` learned the same lesson ("if this
    passes, git is not running the hook — the whole gate is decorative").
    """
    d = make_repo(tmp, scripts=scripts, hooks=(MERGE_DISPATCH, PUSH_DISPATCH))
    for f in extra_flags:
        (d / ".agents/scripts/git-hooks" / f).write_text("armed\n", encoding="utf-8")
    bare = tmp / "remote.git"
    sh("git", "init", "-q", "--bare", str(bare), cwd=tmp)
    sh("git", "remote", "add", "origin", str(bare), cwd=d)
    if push_main:
        sh("git", "push", "-q", "--no-verify", "origin", "main", cwd=d)
        sh("git", "fetch", "-q", "origin", cwd=d)
    return d, bare


def make_carveout_repo(tmp: Path, *, flag: str, script: str) -> Path:
    """A repo carrying ONE of the two merge-exempting gates, armed, plus what it needs to run.

    Deliberately one gate at a time: with both armed, a message satisfying the Jira gate would
    mask whether the SOP gate ran at all, and the failure being measured is a shared carve-out
    that either of them can be blind to independently.
    """
    d = tmp / "carveout"
    d.mkdir()
    sh("git", "init", "-q", "-b", "main", cwd=d)
    sh("git", "config", "user.email", "t@t.t", cwd=d)
    sh("git", "config", "user.name", "t", cwd=d)
    (d / ".agents/scripts/git-hooks").mkdir(parents=True)
    (d / ".agents/commands").mkdir(parents=True)
    (d / "docs/_scc_sops_prds").mkdir(parents=True)
    (d / ".githooks").mkdir()
    shutil.copy2(HOOKDIR / script, d / ".agents/scripts/git-hooks" / script)
    (d / ".agents/scripts/git-hooks" / script).chmod(0o755)
    shutil.copy2(REPO / ".githooks/commit-msg", d / ".githooks/commit-msg")
    (d / ".githooks/commit-msg").chmod(0o755)
    shutil.copy2(REPO / ".agents/scripts/sop_currency.py", d / ".agents/scripts/sop_currency.py")
    (d / ".agents/scripts/git-hooks" / flag).write_text("armed\n", encoding="utf-8")
    (d / ".agents/jira.conf").write_text('JIRA_KEYS="SCC"\n', encoding="utf-8")
    (d / "docs/_scc_sops_prds/workflows_testing_SOP.md").write_text("# sop\n", encoding="utf-8")
    (d / "README").write_text("x\n", encoding="utf-8")
    sh("git", "add", "-A", cwd=d)      # fixture only; the real lane is explicit-paths
    sh("git", "commit", "-qm", "SCC-144 base [sop-ok]", cwd=d)
    sh("git", "config", "core.hooksPath", ".githooks", cwd=d)
    return d


def seed_and_merge(tree: Path, branch: str) -> tuple[int, str]:
    """Make a branch that edits a USAGE SURFACE, then merge it with a message that satisfies
    NEITHER gate's fallback — no Jira key, no SOP doc staged, and a subject that does not start
    with the capital-M `Merge ` the carve-out's second test matches. Exactly the shape of this
    repo's own absorb-main merges (`SCC-127 merge: absorb main`), minus the key.
    """
    here = sh("git", "rev-parse", "--abbrev-ref", "HEAD", cwd=tree)[1].strip()
    sh("git", "checkout", "-q", "-b", branch, cwd=tree)
    (tree / ".agents/commands" / f"{branch.replace('/', '_')}.md").write_text("# cmd\n",
                                                                             encoding="utf-8")
    sh("git", "add", ".agents/commands", cwd=tree)
    sh("git", "commit", "-qm", "SCC-144 a usage surface changed [sop-ok]", cwd=tree)
    sh("git", "checkout", "-q", here, cwd=tree)
    return sh("git", "merge", "--no-ff", "-m", "merge: absorbing the lane", branch, cwd=tree)


def lane(d: Path, branch: str, from_ref: str = "main", *, work: bool = True) -> None:
    """Cut `branch` from `from_ref` and (by default) put one commit on it."""
    sh("git", "checkout", "-q", "-b", branch, from_ref, cwd=d)
    if work:
        (d / f"{branch.replace('/', '_')}.txt").write_text("x\n", encoding="utf-8")
        sh("git", "add", f"{branch.replace('/', '_')}.txt", cwd=d)
        sh("git", "commit", "-qm", f"SCC-144 work on {branch}", cwd=d)


def merge(d: Path, target: str, source: str, *, no_verify: bool = False,
          ff_only: bool = False) -> tuple[int, str, bool]:
    """Merge `source` INTO `target` for real. Returns (rc, output, head_moved)."""
    sh("git", "checkout", "-q", target, cwd=d)
    before = head(d)
    args = ["git", "merge"]
    if ff_only:
        args.append("--ff-only")
    else:
        args += ["--no-ff", "-m", f"SCC-144 merge: {source} -> {target}"]
    if no_verify:
        args.append("--no-verify")
    rc, out = sh(*args, source, cwd=d)
    return rc, out, head(d) != before


def main() -> int:
    c = Cases("merge-target guard (SCC-144)")

    # ── the files exist at all ────────────────────────────────────────────────────────────
    c.check("the guard script exists", GUARD.is_file(), f"{GUARD} — nothing to arm")
    c.check("the commit-msg dispatcher carries the merge-target gate",
            "merge-target-guard.sh" in MERGE_DISPATCH.read_text(encoding="utf-8"),
            f"{MERGE_DISPATCH} — git has nothing to invoke")
    c.check("the guard is executable", hooks_armed.is_executable(GUARD),
            "a non-executable gate is skipped by its dispatcher in SILENCE")
    c.check("the arm flag is tracked in the live repo", FLAG.is_file(),
            f"{FLAG} — without it the gate warns instead of refusing")

    # ── A · chore -> main · ALLOW ─────────────────────────────────────────────────────────
    # NEGATIVE CONTROL. This is the shipping path `/smh-close-task-merge-tree` drives on every
    # Task close-out. A guard that breaks it is worse than no guard.
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "chore/SCC-144-a")
        rc, out, moved = merge(d, "main", "chore/SCC-144-a")
        c.check("A · chore -> main is ALLOWED", rc == 0 and moved, out.strip()[-300:])

    # ── B · ⛔ chore -> chore · REFUSE — THE SCC-97 SIGNATURE ──────────────────────────────
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "chore/SCC-144-a")
        lane(d, "chore/SCC-144-b", "main")
        before_b = head(d)
        rc, out, moved = merge(d, "chore/SCC-144-b", "chore/SCC-144-a")
        c.check("B · chore -> chore is REFUSED", rc != 0, out.strip()[-300:])
        c.check("B · ...and NO merge commit was created", not moved,
                "the refusal has to happen BEFORE the commit is sealed, or it is a post-mortem")
        c.check("B · the refusal names the TARGET", "chore/SCC-144-b" in out, out.strip()[-300:])
        c.check("B · the refusal names the SOURCE", "chore/SCC-144-a" in out, out.strip()[-300:])
        c.check("B · the refusal names the RULE", "git-policy.md" in out, out.strip()[-300:])
        # ⭐ A DIAGNOSIS WITH NO REMEDY IS HALF A GATE. `test_hooks_armed` case B pins the same
        # property on the arm-check: an operator who cannot see the fix will not apply it.
        c.check("B · the refusal names the REMEDY", "git merge --abort" in out, out.strip()[-300:])
        c.check("B · the refusal names the OVERRIDE", "--no-verify" in out, out.strip()[-300:])

        # ── B2 · ⛔ git's OWN suggested next step must not walk you through the gate ────────
        # A refused merge leaves the merge in progress, and git ends by printing "Not committing
        # merge; use 'git commit' to complete the merge." Follow that instruction and the topology
        # is unchanged — so the gate has to refuse again. If it did not, the refusal would be a
        # speed bump with the bypass printed underneath it by git itself.
        rc2, out2 = sh("git", "commit", "-m", "SCC-144 completing it anyway", cwd=d)
        c.check("B2 · git's own 'use git commit to complete the merge' is ALSO refused",
                rc2 != 0 and "MERGE REFUSED" in out2, out2.strip()[-300:])
        c.check("B2 · ...and still no merge commit exists", head(d) == before_b,
                "the second door has to hold, or the first one is decorative")

    # ── C · epic -> main · ALLOW ──────────────────────────────────────────────────────────
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "epic/SCC-144-e")
        rc, out, moved = merge(d, "main", "epic/SCC-144-e")
        c.check("C · epic -> main is ALLOWED", rc == 0 and moved, out.strip()[-300:])

    # ── D · story -> epic · ALLOW ─────────────────────────────────────────────────────────
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "epic/SCC-144-e")
        lane(d, "claude/SCC-144-s", "epic/SCC-144-e")
        rc, out, moved = merge(d, "epic/SCC-144-e", "claude/SCC-144-s")
        c.check("D · story -> epic is ALLOWED", rc == 0 and moved, out.strip()[-300:])

    # ── D2 · main -> chore · ALLOW — absorbing main into a lane ───────────────────────────
    # `/smh-close-task-merge-tree` and `/smh-merge-multiple-workingtrees` Step 4b both do this
    # on every landing. Refusing it would refuse this system's own reconciliation step.
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "chore/SCC-144-a")
        sh("git", "checkout", "-q", "main", cwd=d)
        (d / "onmain.txt").write_text("x\n", encoding="utf-8")
        sh("git", "add", "onmain.txt", cwd=d)
        sh("git", "commit", "-qm", "SCC-144 on main", cwd=d)
        rc, out, moved = merge(d, "chore/SCC-144-a", "main")
        c.check("D2 · main -> chore (absorb) is ALLOWED", rc == 0 and moved, out.strip()[-300:])

    # ── E · ⛔ THE FAST-FORWARD BLIND SPOT, PINNED AS A FACT ABOUT GIT ─────────────────────
    # A ff merge creates NO COMMIT, so `pre-merge-commit` never runs — measured: only `post-merge`
    # fires, and post-merge is after the fact and cannot refuse. This case therefore runs a
    # FORBIDDEN topology (chore -> chore) as a fast-forward, fully ARMED, and asserts it SUCCEEDS.
    #
    # It pins a gap rather than a fix, and that is deliberate: it is the standing justification for
    # the pre-push backstop, and if some future git ever closes it this case goes red and tells
    # whoever is here that the backstop's reason for existing has changed. Asserting the ABSENCE of
    # a hook call via a tracer file would instead assert something about the fixture.
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "chore/SCC-144-a")
        sh("git", "checkout", "-q", "-b", "chore/SCC-144-b", "main", cwd=d)   # behind a, no work
        rc, out, moved = merge(d, "chore/SCC-144-b", "chore/SCC-144-a", ff_only=True)
        c.check("E · a FAST-FORWARD of a forbidden topology is NOT caught by the merge hook",
                rc == 0 and moved,
                "if this ever goes red, git now fires a hook on a ff merge and the pre-push "
                "backstop's justification has changed — read it before 'fixing' this")

    # ── F · --no-verify · the auditable override ──────────────────────────────────────────
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "chore/SCC-144-a")
        lane(d, "chore/SCC-144-b", "main")
        rc, out, moved = merge(d, "chore/SCC-144-b", "chore/SCC-144-a", no_verify=True)
        c.check("F · --no-verify bypasses the guard", rc == 0 and moved, out.strip()[-300:])
    c.check("F · ...and the guard's own header says so",
            "--no-verify" in (GUARD.read_text(encoding="utf-8") if GUARD.is_file() else ""),
            "an undocumented override gets 'fixed' by the next person who finds it")

    # ── J · not armed -> WARN, do not refuse ──────────────────────────────────────────────
    with TempDir() as tmp:
        d = make_repo(tmp, arm=False)
        lane(d, "chore/SCC-144-a")
        lane(d, "chore/SCC-144-b", "main")
        rc, out, moved = merge(d, "chore/SCC-144-b", "chore/SCC-144-a")
        c.check("J · without MERGE-TARGET-ENFORCE the merge is ALLOWED", rc == 0 and moved,
                out.strip()[-300:])
        c.check("J · ...but it still says something", "merge-target" in out.lower(),
                "a disarmed gate that is also silent is indistinguishable from a deleted one")

    # ── K · the DISABLE kill switch every gate here honors ────────────────────────────────
    with TempDir() as tmp:
        d = make_repo(tmp)
        (d / ".agents/scripts/git-hooks/DISABLE").write_text("off\n", encoding="utf-8")
        lane(d, "chore/SCC-144-a")
        lane(d, "chore/SCC-144-b", "main")
        rc, out, moved = merge(d, "chore/SCC-144-b", "chore/SCC-144-a")
        c.check("K · DISABLE allows the merge", rc == 0 and moved, out.strip()[-300:])

    # ── M · ambiguity — one sha, two names, one of them legal ─────────────────────────────
    # Several branches can point at one commit, and this is not a contrived case: a lane cut from
    # `main` with NO commits of its own IS `main`. Merging it into another lane is an absorb-main
    # by any other name, and `chore/SCC-144-a` and `main` are both true names for that sha.
    #
    # The rule is ANY ALLOW WINS, biased toward the false negative on purpose: a guard that blocks
    # a correct merge costs more than one that misses an ambiguous case, and the ambiguous case is
    # still caught at push time by the backstop.
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "chore/SCC-144-b")                      # cut from main, has its own work
        sh("git", "checkout", "-q", "main", cwd=d)      # main then moves on without it
        (d / "onmain.txt").write_text("x\n", encoding="utf-8")
        sh("git", "add", "onmain.txt", cwd=d)
        sh("git", "commit", "-qm", "SCC-144 on main", cwd=d)
        sh("git", "branch", "chore/SCC-144-a", "main", cwd=d)   # empty lane — its sha IS main's
        rc, out, moved = merge(d, "chore/SCC-144-b", "chore/SCC-144-a")
        c.check("M · a sha carrying both a legal and an illegal name is ALLOWED",
                rc == 0 and moved, out.strip()[-300:])

    # ── N · an unclassified branch — allowed, and SAID OUT LOUD ───────────────────────────
    # `incident-*` is explicitly outside the branch model (git-policy.md). A gate that fires on a
    # branch class it was never given a rule for is a gate that gets disarmed. But an unpinned
    # hole widens silently, so the decision has to be visible in the output.
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "incident-42")
        rc, out, moved = merge(d, "main", "incident-42")
        c.check("N · an unclassified SOURCE is allowed", rc == 0 and moved, out.strip()[-300:])
        c.check("N · ...and the guard says it declined to judge",
                "declined" in out.lower(), out.strip()[-300:])

    # ── N2 · a source NO branch name points at — the other half of the hole ───────────────
    # Merging a commit that is not any branch's tip: `git branch --points-at` returns nothing and
    # git's own message reads "Merge commit '<sha>'", which the `Merge branch 'x'` fallback does
    # not match either. The guard therefore knows the target and cannot name the source at all.
    # Found by a mutation sweep — this path had no case, so its output could have gone silent
    # without a single assertion noticing.
    with TempDir() as tmp:
        d = make_repo(tmp)
        lane(d, "chore/SCC-144-a")
        (d / "second.txt").write_text("x\n", encoding="utf-8")
        sh("git", "add", "second.txt", cwd=d)
        sh("git", "commit", "-qm", "SCC-144 a second commit on a", cwd=d)
        mid = sh("git", "rev-parse", "chore/SCC-144-a~1", cwd=d)[1].strip()
        sh("git", "checkout", "-q", "-b", "chore/SCC-144-b", "main", cwd=d)
        before = head(d)
        rc, out = sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: a mid-branch commit",
                     mid, cwd=d)
        c.check("N2 · an UNNAMEABLE source is allowed", rc == 0 and head(d) != before,
                out.strip()[-300:])
        c.check("N2 · ...and the guard says so rather than passing in silence",
                "declined to judge" in out, out.strip()[-300:])

    # ═══ THE FAST-FORWARD BACKSTOP ════════════════════════════════════════════════════════
    # Case E measured the gap: a ff merge creates no commit, so NO commit-time hook can see it.
    # What it leaves behind is evidence — another lane's unlanded commits are now contained in
    # yours — and push time is the last moment anything can refuse.

    # ── G · a lane carrying another UNLANDED lane's commits is REFUSED at push ────────────
    with TempDir() as tmp:
        d, bare = make_pushable(tmp)
        lane(d, "chore/SCC-144-a")                             # never landed
        sh("git", "checkout", "-q", "-b", "chore/SCC-144-b", "main", cwd=d)
        sh("git", "merge", "--ff-only", "chore/SCC-144-a", cwd=d)   # the gap from case E
        rc, out = sh("git", "push", "origin", "chore/SCC-144-b", cwd=d)
        c.check("G · pushing a lane contaminated by a FF merge is REFUSED", rc != 0,
                out.strip()[-400:])
        c.check("G · ...and the refusal names the foreign lane", "chore/SCC-144-a" in out,
                out.strip()[-400:])
        c.check("G · ...and names the remedy", "reset" in out, out.strip()[-400:])
        rc, out = sh("git", "ls-remote", "--heads", str(bare), "chore/SCC-144-b", cwd=d)
        c.check("G · ...and nothing reached the remote", "chore/SCC-144-b" not in out, out)

    # ── H · ⭐ THE FALSE-RED CONTROL — absorbing main after a sibling LANDED is fine ───────
    # This is the everyday move: a sibling lane lands on main, you absorb main, you push. Those
    # commits are now contained in your lane too. If the check keyed on containment alone it would
    # refuse this — the single most common thing a lane does — which is why it asks whether the
    # foreign lane is reachable from origin/main.
    with TempDir() as tmp:
        d, bare = make_pushable(tmp)
        lane(d, "chore/SCC-144-a")
        sh("git", "checkout", "-q", "main", cwd=d)
        sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: land a", "chore/SCC-144-a", cwd=d)
        sh("git", "push", "-q", "origin", "main", cwd=d)       # the sibling LANDS
        sh("git", "fetch", "-q", "origin", cwd=d)
        sh("git", "checkout", "-q", "-b", "chore/SCC-144-b", "origin/main", cwd=d)
        (d / "b.txt").write_text("x\n", encoding="utf-8")
        sh("git", "add", "b.txt", cwd=d)
        sh("git", "commit", "-qm", "SCC-144 work on b", cwd=d)
        rc, out = sh("git", "push", "origin", "chore/SCC-144-b", cwd=d)
        c.check("H · a lane holding a LANDED sibling's commits pushes fine", rc == 0,
                out.strip()[-400:])

    # ── I · ⭐ THE SHIPPING-PATH CONTROL — main carrying the lane it is landing ────────────
    # `/smh-close-task-merge-tree` merges chore/X into main and pushes main. chore/X is contained
    # and unlanded BY DEFINITION at that moment — that is what landing IS. A backstop that did not
    # exempt main and epic/* would refuse this system's primary shipping path on every close-out.
    with TempDir() as tmp:
        d, bare = make_pushable(tmp)
        lane(d, "chore/SCC-144-a")
        sh("git", "checkout", "-q", "main", cwd=d)
        sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: a -> main", "chore/SCC-144-a", cwd=d)
        rc, out = sh("git", "push", "origin", "main", cwd=d)
        c.check("I · landing a lane on main is ALLOWED", rc == 0, out.strip()[-400:])

    # ── I2 · the same control for a story lane landing on its epic ────────────────────────
    with TempDir() as tmp:
        d, bare = make_pushable(tmp)
        lane(d, "epic/SCC-144-e")
        sh("git", "push", "-q", "origin", "epic/SCC-144-e", cwd=d)
        lane(d, "claude/SCC-144-s", "epic/SCC-144-e")
        sh("git", "checkout", "-q", "epic/SCC-144-e", cwd=d)
        sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: s -> e", "claude/SCC-144-s", cwd=d)
        rc, out = sh("git", "push", "origin", "epic/SCC-144-e", cwd=d)
        c.check("I2 · landing a story on its epic is ALLOWED", rc == 0, out.strip()[-400:])

    # ── O · no origin/main — there is no reference point, so it declines and SAYS so ───────
    # Refusing on the absence of a reference point is the vacuous red, the mirror of the vacuous
    # green. Pinned so the hole cannot widen quietly.
    with TempDir() as tmp:
        d, bare = make_pushable(tmp, push_main=False)
        lane(d, "chore/SCC-144-a")
        sh("git", "checkout", "-q", "-b", "chore/SCC-144-b", "main", cwd=d)
        sh("git", "merge", "--ff-only", "chore/SCC-144-a", cwd=d)
        rc, out = sh("git", "push", "origin", "chore/SCC-144-b", cwd=d)
        c.check("O · with no origin/main the push is ALLOWED", rc == 0, out.strip()[-400:])
        c.check("O · ...and it says it could not judge", "origin/main" in out, out.strip()[-400:])

    # ── P · ⛔⛔ THE STDIN TEE — pre-push gets ONE stdin and there are now TWO gates ────────
    # A pre-push hook receives one line per ref ON STDIN, and stdin can be consumed exactly once.
    # If the dispatcher hands the raw stream to the first gate, the second reads EOF, its `while
    # read` loop never runs, and it exits 0 — SILENTLY ALLOWING EVERYTHING. That is this ticket's
    # own failure class inside this ticket's own fix, so it gets a case that can only pass if the
    # SECOND gate really saw its input: a push to main with no approval token must still be
    # refused by the token gate, which is the gate that runs last.
    with TempDir() as tmp:
        d, bare = make_pushable(tmp, push_main=False,
                               scripts=(GUARD, BACKSTOP, HOOKDIR / "pre-push-main-approval.sh"),
                               extra_flags=("MAIN-PUSH-ENFORCE",))
        rc, out = sh("git", "push", "origin", "main", cwd=d)
        c.check("P · the token gate STILL refuses an unapproved push to main", rc != 0,
                "the backstop consumed stdin and the token gate read EOF - every push now passes")
        c.check("P · ...with its own message, not the backstop's", "PUSH TO main REFUSED" in out,
                out.strip()[-400:])

    # ═══ THE MERGE CARVE-OUT WAS BLIND INSIDE A WORKTREE (SCC-144 F-D) ════════════════════
    # `commit-msg-jira.sh` and `sop-currency.sh` both exempt merges — git writes those messages, so
    # blocking them blocks the tool rather than the author. Both probed for it with
    # `[ -f .git/MERGE_HEAD ]`.
    #
    # ⛔ IN A WORKTREE `.git` IS A FILE, NOT A DIRECTORY. The real path is
    # `.git/worktrees/<name>/MERGE_HEAD`, so that probe is ALWAYS FALSE there — and every lane in
    # this system is a worktree. The subject fallback does not cover it either: it matches
    # `'Merge '*`, case-sensitively, while this repo's own merge subjects read
    # `merge: chore/... -> main` and `SCC-127 merge: absorb main`.
    #
    # So the absorb-main merge that /smh-merge-multiple-workingtrees Step 4b performs INSIDE the
    # lane was gated, while the identical merge in the shared checkout was exempt. Found while
    # answering this ticket's own open question about `[sop-ok]`.
    for gate_name, flag, script in (("jira", "JIRA-ENFORCE", "commit-msg-jira.sh"),
                                    ("sop", "SOP-ENFORCE", "sop-currency.sh")):
        with TempDir() as tmp:
            d = make_carveout_repo(tmp, flag=flag, script=script)

            # The CONTROL, and it is the whole point: the SAME merge in the SHARED CHECKOUT.
            # If this ever fails, the carve-out is broken outright and the worktree case below
            # is measuring the wrong thing.
            rc, out = seed_and_merge(d, "chore/SCC-144-shared")
            c.check(f"F-D · {gate_name}: a merge in the SHARED CHECKOUT is exempt",
                    rc == 0, out.strip()[-300:])

            wt = tmp / "lane"
            sh("git", "worktree", "add", "-q", str(wt), "-b", "chore/SCC-144-wt", "main", cwd=d)
            c.check(f"F-D · {gate_name}: .git in that worktree really is a FILE",
                    (wt / ".git").is_file(),
                    "if this is a directory the fixture is not reproducing the condition")
            rc, out = seed_and_merge(wt, "chore/SCC-144-inwt")
            c.check(f"F-D · {gate_name}: the SAME merge inside a WORKTREE is exempt too",
                    rc == 0, out.strip()[-300:])

            # ...and the gate must still be a gate. An ordinary commit in that same worktree,
            # touching the same surface, is still refused — otherwise the fix disarmed it.
            (wt / ".agents/commands/plain.md").write_text("# plain\n", encoding="utf-8")
            sh("git", "add", ".agents/commands/plain.md", cwd=wt)
            rc, out = sh("git", "commit", "-m", "no key here and no sop doc", cwd=wt)
            c.check(f"F-D · {gate_name}: an ORDINARY commit in the worktree is still REFUSED",
                    rc != 0, out.strip()[-300:])

    # ── L · the arm accounting — a fresh clone must report this gate OFF, not green ────────
    # `core.hooksPath` is local config git NEVER carries, so a fresh clone has every gate silently
    # off and every flow reporting green. That is the whole reason `hooks_armed.py` exists, and a
    # new gate that is not in its accounting is a gate that reports clean while dead.
    c.check("L · ARM_FLAGS carries a row for the merge-target gate",
            "MERGE-TARGET-ENFORCE" in hooks_armed.ARM_FLAGS,
            "a gate outside the accounting certifies ARMED while switched off")
    if "MERGE-TARGET-ENFORCE" in hooks_armed.ARM_FLAGS:
        script, via = hooks_armed.ARM_FLAGS["MERGE-TARGET-ENFORCE"]
        c.check("L · ...naming the script it actually arms", script == GUARD.name, script)
        # ⛔ Not a cosmetic field. test_hooks_armed case V asserts that a flag whose declared `via`
        # hook is untracked reads NOT ARMED — so naming a dispatcher that does not carry this gate
        # would either mis-report or hard-block, depending on which way it was wrong.
        c.check("L · ...and the dispatcher that really carries it", via == "commit-msg", via)
        c.check("L · ...which really does call it",
                "merge-target-guard.sh" in (REPO / ".githooks" / via).read_text(encoding="utf-8"),
                f".githooks/{via} does not mention the script ARM_FLAGS says it dispatches")

    # The live repo, scanned for real — the same shape `task_preflight` prints at close-out.
    live = hooks_armed.scan(REPO)
    c.check("L · the live repo reports the new flag as tracked",
            any(f["name"] == "MERGE-TARGET-ENFORCE" for f in live["flags"]),
            f"flags={[f['name'] for f in live['flags']]}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
