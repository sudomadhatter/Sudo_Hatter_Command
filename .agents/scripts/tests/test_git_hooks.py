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

import re
import shutil
import subprocess
import sys
from pathlib import Path

import _repo_template
from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hooks_armed  # noqa: E402 — _harness puts .agents/scripts on sys.path

REPO = Path(__file__).resolve().parents[3]
HOOKDIR = REPO / ".agents/scripts/git-hooks"

GUARD = HOOKDIR / "merge-target-guard.sh"
BACKSTOP = HOOKDIR / "pre-push-merge-backstop.sh"
# ⛔ PRESENT IN EVERY PUSH FIXTURE, AND DISARMED THERE. This file's subject is the BACKSTOP, so
# the token gate must not interfere — but it must still EXIST, because `.githooks/pre-push`
# refuses a push to `main` when it is missing (SCC-172 D3: "no gate ran" must not be quieter than
# "the gate said no"). Omitting it modelled a stale worktree, which is not what any case here is
# about, and three ALLOW controls (I, G6d, EP5) started reading D3's refusal as the backstop's.
# It is installed WITHOUT `MAIN-PUSH-ENFORCE`, so it exits 0 immediately and changes nothing.
APPROVAL = HOOKDIR / "pre-push-main-approval.sh"
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


def _key(paths) -> tuple:
    """The cache half of a builder's file arguments — the FULL path of each.

    ⛔ FULL PATHS, not basenames. Both halves of a template's identity must be in its key or two
    different fixtures share one template, and basenames throw half of it away: two entries of
    `scripts` or `hooks` sharing a name in different directories would collapse to one key and
    be served one template, silently. Today's five constants have distinct basenames so nothing
    is currently mis-keyed — which is exactly why the narrowing would have shipped unnoticed.
    `_CACHE` never leaves this process (`run_all.py` gives each test file its own), so an
    absolute path is a correct key; readability belongs in the failure message, not the key.
    """
    return tuple(str(p) for p in paths)


def make_repo(tmp: Path, *, name: str = "work",
              scripts=(GUARD,), hooks=(MERGE_DISPATCH,), arm: bool = True) -> Path:
    """A real repo carrying the REAL hook files, armed the way this system arms them.

    Built once per shape and CLONED per scenario (SCC-214): same signature, same return, same
    isolation — a scenario's repo is its own copy, and the hook scripts are hard links to a
    read-only template inode so the OS assesses each executable once instead of 72 times.
    """
    _repo_template.clone(
        ("gh.make_repo", name, _key(scripts), _key(hooks), arm),
        lambda tpl: _build_repo(tpl, name=name, scripts=scripts, hooks=hooks, arm=arm),
        tmp)
    return tmp / name


def _build_repo(tmp: Path, *, name: str = "work",
                scripts=(GUARD,), hooks=(MERGE_DISPATCH,), arm: bool = True) -> Path:
    """The template build — the body `make_repo` had before SCC-214, unchanged.

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
                  scripts=(GUARD, BACKSTOP, APPROVAL), extra_flags=()) -> tuple[Path, Path]:
    """A repo with a REAL bare remote, so the push cases drive `git push` and not a stub.

    Built once per shape and CLONED per scenario (SCC-214). The clone carries the template's
    absolute remote URL, so `origin` is re-pointed at THIS scenario's own bare — otherwise a push
    here would land on the template's bare and the next scenario would fetch it.
    """
    _repo_template.clone(
        # ⛔ `extra_flags` is already a tuple of NAMES ("MAIN-PUSH-ENFORCE"), not Paths — it goes
        # into the key as-is. `_key` is for the Path tuples (`scripts`, `hooks`) only.
        ("gh.make_pushable", push_main, _key(scripts), tuple(extra_flags)),
        lambda tpl: _build_pushable(tpl, push_main=push_main, scripts=scripts,
                                    extra_flags=extra_flags),
        tmp)
    d, bare = tmp / "work", tmp / "remote.git"
    sh("git", "remote", "set-url", "origin", str(bare), cwd=d)
    return d, bare


def _build_pushable(tmp: Path, *, push_main: bool = True,
                    scripts=(GUARD, BACKSTOP, APPROVAL), extra_flags=()) -> tuple[Path, Path]:
    """The template build — the body `make_pushable` had before SCC-214, unchanged.

    Everything the push gates need can be faked at the script level; whether git actually invokes
    the dispatcher, and whether the dispatcher actually feeds both gates, cannot. That is the
    whole point of these fixtures — `test_main_push_gate.py` learned the same lesson ("if this
    passes, git is not running the hook — the whole gate is decorative").
    """
    d = _build_repo(tmp, scripts=scripts, hooks=(MERGE_DISPATCH, PUSH_DISPATCH))
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

    Built once per (flag, script) and CLONED per scenario (SCC-214).
    """
    _repo_template.clone(("gh.make_carveout_repo", flag, script),
                         lambda tpl: _build_carveout_repo(tpl, flag=flag, script=script), tmp)
    return tmp / "carveout"


def _build_carveout_repo(tmp: Path, *, flag: str, script: str) -> Path:
    """The template build — the body `make_carveout_repo` had before SCC-214, unchanged.

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
    if c.block("the files exist at all"):
        c.check("the guard script exists", GUARD.is_file(), f"{GUARD} — nothing to arm")
        c.check("the commit-msg dispatcher carries the merge-target gate",
                "merge-target-guard.sh" in MERGE_DISPATCH.read_text(encoding="utf-8"),
                f"{MERGE_DISPATCH} — git has nothing to invoke")
        c.check("the guard is executable", hooks_armed.is_executable(GUARD),
                "a non-executable gate is skipped by its dispatcher in SILENCE")
        # ⛔ TRACKED, not merely present. `Path.is_file()` cannot tell the two apart, and the
        # difference IS the failure mode: a flag on disk but not in the index arms this clone and
        # reaches no other machine — which is the state this lane was actually in for a while, and
        # `hooks_armed.py` said so in exactly those words. An assertion whose NAME says "tracked" and
        # whose predicate says "exists" is the prose-pinning shape (SCC-125) in an assertion.
        tracked = sh("git", "ls-files", "--error-unmatch",
                     ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE", cwd=REPO)[0] == 0
        c.check("the arm flag is TRACKED in the live repo (not merely on disk)", tracked,
                f"{FLAG} — untracked, it arms this clone only and reaches no other machine")

    # ── A · chore -> main · ALLOW ─────────────────────────────────────────────────────────
    if c.block("A · chore -> main · ALLOW"):
        # NEGATIVE CONTROL. This is the shipping path `/smh-close-task-merge-tree` drives on every
        # Task close-out. A guard that breaks it is worse than no guard.
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "chore/SCC-144-a")
            rc, out, moved = merge(d, "main", "chore/SCC-144-a")
            c.check("A · chore -> main is ALLOWED", rc == 0 and moved, out.strip()[-300:])

    # ── B · ⛔ chore -> chore · REFUSE — THE SCC-97 SIGNATURE ──────────────────────────────
    if c.block("B · ⛔ chore -> chore · REFUSE — THE SCC-97 SIGNATURE"):
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

    # ── B3 · the refusal carries the DESTINATION and the SIGNATURE, not just the diagnosis ─
    if c.block("B3 · the refusal carries the DESTINATION and the SIGNATURE, not "):
        # A mutation sweep found `destination()` and the SCC-97 signature block could both be gutted
        # with the suite green: case B matched `git merge --abort`, which is a STATIC line, so the
        # generated half of the message was unasserted.
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "chore/SCC-144-a")
            lane(d, "chore/SCC-144-b", "main")
            rc, out, _ = merge(d, "chore/SCC-144-b", "chore/SCC-144-a")
            c.check("B3 · the refusal names where a chore lane SHOULD land",
                    "/smh-close-task-merge-tree" in out, out.strip()[-300:])
            c.check("B3 · ...and names the SCC-97 signature", "SCC-97 signature" in out,
                    out.strip()[-300:])

    # ── ⭐ THE REFUSE HALF OF THE VERDICT TABLE ────────────────────────────────────────────
    if c.block("⭐ THE REFUSE HALF OF THE VERDICT TABLE"):
        # A review mutation sweep flipped SEVEN refusal cells to `allow` with this suite fully green:
        # only chore:chore was defended. Every refusing cell now has a case, so a flipped verdict is
        # a failed case rather than a silent hole.
        for label, target, source, cut_from in (
            ("story -> main", "main", "claude/SCC-144-s", "main"),
            ("chore -> epic", "epic/SCC-144-e", "chore/SCC-144-c", "main"),
            ("epic  -> epic", "epic/SCC-144-e", "epic/SCC-144-f", "main"),
            ("story -> chore", "chore/SCC-144-c", "claude/SCC-144-s", "main"),
            ("story -> story", "claude/SCC-144-t", "claude/SCC-144-s", "main"),
            ("chore -> story", "claude/SCC-144-t", "chore/SCC-144-c", "main"),
        ):
            with TempDir() as tmp:
                d = make_repo(tmp)
                lane(d, source, cut_from)
                lane(d, target, "main")
                rc, out, moved = merge(d, target, source)
                # `moved` is measured inside merge(), AFTER it checks out the target — capturing a
                # `before` out here reads the SOURCE branch's tip and compares two unrelated shas.
                c.check(f"TBL · {label} is REFUSED", rc != 0, out.strip()[-200:])
                c.check(f"TBL · {label} — no merge commit", not moved, "HEAD moved")

    # ── ⭐ THE ALLOW HALF, for the cells the shipping paths actually use ───────────────────
    if c.block("⭐ THE ALLOW HALF, for the cells the shipping paths actually use"):
        for label, target, source in (
            ("main  -> epic (absorb before /cicd-push-e2e)", "epic/SCC-144-e", "main"),
            ("epic  -> story (a story lane absorbs its epic)", "claude/SCC-144-s", "epic/SCC-144-e"),
            ("main  -> story", "claude/SCC-144-s", "main"),
        ):
            with TempDir() as tmp:
                d = make_repo(tmp)
                lane(d, "epic/SCC-144-e")
                lane(d, "claude/SCC-144-s", "epic/SCC-144-e")
                # The epic and main must BOTH move after the story lane was cut, or the "absorb"
                # merges are `Already up to date` and prove nothing about the verdict table.
                sh("git", "checkout", "-q", "epic/SCC-144-e", cwd=d)
                (d / "onepic.txt").write_text("x\n", encoding="utf-8")
                sh("git", "add", "onepic.txt", cwd=d)
                sh("git", "commit", "-qm", "SCC-144 on the epic", cwd=d)
                sh("git", "checkout", "-q", "main", cwd=d)
                (d / "onmain.txt").write_text("x\n", encoding="utf-8")
                sh("git", "add", "onmain.txt", cwd=d)
                sh("git", "commit", "-qm", "SCC-144 on main", cwd=d)
                rc, out, moved = merge(d, target, source)
                c.check(f"TBL · {label} is ALLOWED", rc == 0 and moved, out.strip()[-200:])
                # ⛔ ALLOWED, not merely not-refused. A `claude/*` misclassified as `unknown` also
                # exits 0 — while printing "declined to judge" — so rc alone cannot tell a correct
                # classification from a lost one. A mutant that made `claude/*` unknown survived
                # until this assertion existed.
                c.check(f"TBL · {label} — classified, not declined", "declined" not in out,
                        out.strip()[-200:])

    # ── ⭐ THE GUARD, INSIDE A REAL WORKTREE — where every lane in this system lives ───────
    if c.block("⭐ THE GUARD, INSIDE A REAL WORKTREE — where every lane in this s"):
        # Mutants that reverted `git rev-parse MERGE_HEAD` and `--git-path MERGE_MSG` to the literal
        # `.git/...` probes SURVIVED the suite: the guard could be reverted to the exact worktree-blind
        # shape this same lane removes from two sibling gates, and nothing would have noticed.
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "chore/SCC-144-a")
            sh("git", "checkout", "-q", "main", cwd=d)
            wt = tmp / "lane"
            sh("git", "worktree", "add", "-q", str(wt), "-b", "chore/SCC-144-b", "main", cwd=d)
            c.check("WT · .git in the worktree really is a FILE", (wt / ".git").is_file(),
                    "if this is a directory the fixture is not reproducing the condition")
            before = head(wt)
            rc, out = sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: a -> b",
                         "chore/SCC-144-a", cwd=wt)
            c.check("WT · chore -> chore is REFUSED inside a worktree too",
                    rc != 0 and head(wt) == before, out.strip()[-300:])
            c.check("WT · ...and the refusal is the real one", "MERGE REFUSED" in out,
                    out.strip()[-300:])

    # ── OCT · an octopus merge is judged on EVERY parent, not just the first ──────────────
    if c.block("OCT · an octopus merge is judged on EVERY parent, not just the f"):
        # `git rev-parse --verify --quiet MERGE_HEAD` prints the FIRST sha and exits 0 on an octopus
        # merge — it does not fail. So `git merge main <sibling-lane>` was judged on `main` alone and
        # ALLOWED, sealing a commit whose third parent was a sibling lane. Position-dependent, too:
        # reversing the argument order refused. Found by two review lenses, both measured.
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "chore/SCC-144-a")
            lane(d, "chore/SCC-144-b", "main")
            sh("git", "checkout", "-q", "main", cwd=d)
            (d / "onmain.txt").write_text("x\n", encoding="utf-8")
            sh("git", "add", "onmain.txt", cwd=d)
            sh("git", "commit", "-qm", "SCC-144 on main", cwd=d)
            sh("git", "checkout", "-q", "chore/SCC-144-b", cwd=d)
            before = head(d)
            rc, out = sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: octopus",
                         "main", "chore/SCC-144-a", cwd=d)
            c.check("OCT · a legal FIRST parent does not launder an illegal later one",
                    rc != 0 and head(d) == before, out.strip()[-300:])
            c.check("OCT · ...and the refusal names the illegal parent",
                    "chore/SCC-144-a" in out, out.strip()[-300:])

    # ── SQ · `git merge --squash` — the second blind spot, now closed ─────────────────────
    if c.block("SQ · `git merge --squash` — the second blind spot, now closed"):
        # `--squash` records SQUASH_MSG and NO MERGE_HEAD, and it rewrites history, so the source is
        # not an ancestor of the result either: neither this guard nor the pre-push backstop could
        # see it. It was a silent hole while the backstop's header claimed exactly one.
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "chore/SCC-144-a")
            lane(d, "chore/SCC-144-b", "main")
            before = head(d)
            sh("git", "merge", "--squash", "chore/SCC-144-a", cwd=d)
            rc, out = sh("git", "commit", "-m", "SCC-144 squashed the sibling in", cwd=d)
            c.check("SQ · a squash-merge of a sibling lane is REFUSED",
                    rc != 0 and head(d) == before, out.strip()[-300:])
            c.check("SQ · ...and it names the sibling it recovered from SQUASH_MSG",
                    "chore/SCC-144-a" in out, out.strip()[-300:])

    # ── SELF · `git merge origin/<self>` — the two-machine sync move, never a violation ────
    if c.block("SELF · `git merge origin/<self>` — the two-machine sync move, ne"):
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "chore/SCC-144-a")
            sh("git", "push", "-q", "--no-verify", "origin", "chore/SCC-144-a", cwd=d)
            (d / "more.txt").write_text("x\n", encoding="utf-8")
            sh("git", "add", "more.txt", cwd=d)
            sh("git", "commit", "-qm", "SCC-144 more work", cwd=d)
            rc, out = sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: absorb my own remote",
                         "origin/chore/SCC-144-a", cwd=d)
            c.check("SELF · merging origin/<this same branch> is ALLOWED", rc == 0,
                    out.strip()[-300:])

    # ── ORD · an ordinary commit passes in SILENCE ───────────────────────────────────────
    if c.block("ORD · an ordinary commit passes in SILENCE"):
        # This guard now runs on every commit in the repo as gate 1 of commit-msg. A mutant that
        # dropped the not-a-merge early exit made it comment on every ordinary commit, and the suite
        # stayed green.
        with TempDir() as tmp:
            d = make_repo(tmp)
            sh("git", "checkout", "-q", "-b", "chore/SCC-144-a", cwd=d)
            (d / "plain.txt").write_text("x\n", encoding="utf-8")
            sh("git", "add", "plain.txt", cwd=d)
            rc, out = sh("git", "commit", "-m", "SCC-144 an ordinary commit", cwd=d)
            c.check("ORD · an ordinary commit succeeds", rc == 0, out.strip()[-200:])
            c.check("ORD · ...and the guard says nothing at all",
                    "merge-target" not in out.lower(), out.strip()[-200:])

    # ── C · epic -> main · ALLOW ──────────────────────────────────────────────────────────
    if c.block("C · epic -> main · ALLOW"):
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "epic/SCC-144-e")
            rc, out, moved = merge(d, "main", "epic/SCC-144-e")
            c.check("C · epic -> main is ALLOWED", rc == 0 and moved, out.strip()[-300:])

    # ── D · story -> epic · ALLOW ─────────────────────────────────────────────────────────
    if c.block("D · story -> epic · ALLOW"):
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "epic/SCC-144-e")
            lane(d, "claude/SCC-144-s", "epic/SCC-144-e")
            rc, out, moved = merge(d, "epic/SCC-144-e", "claude/SCC-144-s")
            c.check("D · story -> epic is ALLOWED", rc == 0 and moved, out.strip()[-300:])

    # ── D2 · main -> chore · ALLOW — absorbing main into a lane ───────────────────────────
    if c.block("D2 · main -> chore · ALLOW — absorbing main into a lane"):
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
    if c.block("E · ⛔ THE FAST-FORWARD BLIND SPOT, PINNED AS A FACT ABOUT GIT"):
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
    if c.block("F · --no-verify · the auditable override"):
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
    if c.block("J · not armed -> WARN, do not refuse"):
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
    if c.block("K · the DISABLE kill switch every gate here honors"):
        with TempDir() as tmp:
            d = make_repo(tmp)
            (d / ".agents/scripts/git-hooks/DISABLE").write_text("off\n", encoding="utf-8")
            lane(d, "chore/SCC-144-a")
            lane(d, "chore/SCC-144-b", "main")
            rc, out, moved = merge(d, "chore/SCC-144-b", "chore/SCC-144-a")
            c.check("K · DISABLE allows the merge", rc == 0 and moved, out.strip()[-300:])

    # ── M · ambiguity — one sha, two names, one of them legal ─────────────────────────────
    if c.block("M · ambiguity — one sha, two names, one of them legal"):
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
    if c.block("N · an unclassified branch — allowed, and SAID OUT LOUD"):
        # A gate that fires on a branch class it was never given a rule for is a gate that gets
        # disarmed. But an unpinned hole widens silently, so the decision has to be visible in the
        # output. The bare `incident-42` fixture is a genuinely unclassified name — NO command
        # creates that shape (this comment once called it "the" incident prefix; the real one is
        # `claude/incident-*`, which has its own carve-out and its own case block, INC — SCC-149).
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "incident-42")
            rc, out, moved = merge(d, "main", "incident-42")
            c.check("N · an unclassified SOURCE is allowed", rc == 0 and moved, out.strip()[-300:])
            c.check("N · ...and the guard says it declined to judge",
                    "declined" in out.lower(), out.strip()[-300:])
            # SCC-154 width pin: a bare name must never read as the incident pipeline's lane —
            # kills the mutant that widens classify's incident arm from `claude/incident-*` to
            # `*incident*` (the allow verdict would not change here; only this line sees it).
            c.check("N · ...and never claims the incident pipeline owns a bare name",
                    "/cicd-mobile-error-team" not in out, out.strip()[-300:])

    # ── N2 · a source NO branch name points at — the other half of the hole ───────────────
    if c.block("N2 · a source NO branch name points at — the other half of the h"):
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

    # ── INC · the REAL incident shape — `claude/incident-*` — carved out BEFORE the story arm ─
    if c.block("INC · the REAL incident shape — `claude/incident-*` — carved out"):
        # SCC-149. The only incident branch any command creates is `claude/incident-<short-id-lower>`
        # (cicd-mobile-error-team.md writes nothing else), and it MATCHES the `claude/*` glob:
        # without a carve-out the guard classified it STORY and refused an emergency local hotfix
        # merge to main with story-lane instructions — during an incident. Case N above keeps its
        # bare-name fixture (`incident-42`): that shape genuinely is unclassified and no command
        # creates it; THIS is the shape the incident pipeline actually pushes.
        # ⛔ BOTH ARMS IN ONE BLOCK, deliberately: the last case proves the carve-out did not swallow
        # the story arm — a gate that allows everything is as broken as one that refuses everything.
        # The TBL loop also holds the story->main cell; the local pair keeps this block self-contained
        # and gives mutant M4 (arm pattern widened to `claude/*`) a kill that lives NEXT TO the allow.
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "claude/incident-abc123")
            rc, out, moved = merge(d, "main", "claude/incident-abc123")
            c.check("INC · a claude/incident-* hotfix merge into main is ALLOWED",
                    rc == 0 and moved, out.strip()[-300:])
            c.check("INC · ...and it is never the story-lane refusal",
                    "MERGE REFUSED" not in out and "story lane merges into ITS epic" not in out,
                    out.strip()[-300:])
            # Positive, not just absence-of-strings: a crashed or silent run passes the two negatives
            # above on empty output (the SCC-148 review's own finding class, pre-applied here).
            c.check("INC · ...and the note names the pipeline that owns the lane",
                    "/cicd-mobile-error-team" in out, out.strip()[-300:])
            # SCC-154 (finding 3): the note REPLACES the generic line — "positively classified"
            # printed one line under "outside the branch model" was the guard contradicting itself,
            # and the line is runtime-assembled, so no source grep can ever see the pairing.
            c.check("INC · the incident note REPLACES 'outside the branch model'",
                    "outside the branch model" not in out, out.strip()[-300:])
            # The paired arm: an ordinary story lane is still refused AFTER the carve-out exists.
            lane(d, "claude/SCC-149-s", "main")
            rc, out, moved = merge(d, "main", "claude/SCC-149-s")
            c.check("INC · the ordinary story arm still refuses (the carve-out swallowed nothing)",
                    rc != 0 and not moved and "MERGE REFUSED" in out, out.strip()[-300:])
            # SCC-154 positive pin: the refusal PRESCRIBES the story destination — the wording the
            # INC allow-case above asserts the ABSENCE of, which was otherwise never asserted
            # anywhere in the positive direction (the dev-wave finding).
            c.check("INC · ...and the refusal prescribes the story destination",
                    "story lane merges into ITS epic" in out, out.strip()[-300:])

    # ── INC2 · SCC-154 pins landed BEFORE the judge-arm narrowing (C3's sequencing) ────────
    if c.block("INC2 · SCC-154 pins landed BEFORE the judge-arm narrowing (C3's "):
        # Characterization-green by design: each pins a behavior that is already correct TODAY and
        # that the narrowing (INC3's arms) could silently break — the safety net goes up first.
        with TempDir() as tmp:
            d = make_repo(tmp)
            # Target-side: the incident lane absorbing main — the everyday mid-incident move. The
            # SCC-149 review shipped the source-side allow only; this is the unpinned half.
            lane(d, "claude/incident-abc123")
            sh("git", "checkout", "-q", "main", cwd=d)
            (d / "onmain.txt").write_text("x\n", encoding="utf-8")
            sh("git", "add", "onmain.txt", cwd=d)
            sh("git", "commit", "-qm", "SCC-154 on main", cwd=d)
            rc, out, moved = merge(d, "claude/incident-abc123", "main")
            c.check("INC2 · main -> incident (absorb) is ALLOWED", rc == 0 and moved,
                    out.strip()[-300:])
            # Amended by the SCC-154 review: the absorb is now sanctioned OUTRIGHT (`allow`, not
            # unjudged-with-note) — `allow` is what lets any-legal-name-wins protect the absorb
            # when a sibling lane's tip coincides with main's (case INC4). The original pin
            # asserted the pipeline note here, and that note-shape was itself the defect: an
            # unjudged incident target had no allow arm, so a coincident story name forced a
            # refusal on the emergency path.
            c.check("INC2 · ...never a refusal, never the generic decline",
                    "MERGE REFUSED" not in out and "outside the branch model" not in out,
                    out.strip()[-300:])
        with TempDir() as tmp:
            d = make_repo(tmp)
            # Boundary: the EMPTY suffix still matches the glob — `claude/incident-` is incident.
            lane(d, "claude/incident-")
            rc, out, moved = merge(d, "main", "claude/incident-")
            c.check("INC2 · claude/incident- (empty suffix) classifies as incident",
                    rc == 0 and moved and "/cicd-mobile-error-team" in out, out.strip()[-300:])
        with TempDir() as tmp:
            d = make_repo(tmp)
            # Boundary: the glob is CASE-SENSITIVE — claude/INCIDENT-x is an ordinary story lane.
            lane(d, "claude/INCIDENT-x")
            rc, out, moved = merge(d, "main", "claude/INCIDENT-x")
            c.check("INC2 · claude/INCIDENT-x (case) classifies as story and is REFUSED",
                    rc != 0 and not moved and "MERGE REFUSED" in out, out.strip()[-300:])
        with TempDir() as tmp:
            d = make_repo(tmp)
            # Multi-name: one sha carrying an incident name AND a story name vs main. `unknown`
            # is not `allow`, so any-legal-name-wins does NOT extend to incident — the story
            # name's refuse verdict stands (SCC-149 finding 13, semantics now pinned).
            lane(d, "claude/incident-abc")
            sh("git", "branch", "claude/SCC-154-s", "claude/incident-abc", cwd=d)
            rc, out, moved = merge(d, "main", "claude/incident-abc")
            c.check("INC2 · a sha carrying incident + story names vs main is REFUSED "
                    "(unknown never launders a refusable name)",
                    rc != 0 and not moved and "claude/SCC-154-s" in out, out.strip()[-300:])

    # ── INC4 · SCC-154 review fix: the absorb survives a COINCIDENT sibling tip ────────────
    if c.block("INC4 · SCC-154 review fix: the absorb survives a COINCIDENT sibl"):
        # The review's measured false red: a freshly-cut story/chore lane sitting at main's tip
        # (the normal state between cut and first commit) adds its name to main's sha; with no
        # allow arm for incident targets, judge(incident:story)=refuse won the aggregate and the
        # EMERGENCY absorb ate a story-lane refusal mid-incident. incident:main|incident:epic are
        # now `allow`, and any-legal-name-wins does the rest.
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "claude/incident-abc123")
            sh("git", "checkout", "-q", "main", cwd=d)
            (d / "onmain.txt").write_text("x\n", encoding="utf-8")
            sh("git", "add", "onmain.txt", cwd=d)
            sh("git", "commit", "-qm", "SCC-154 on main", cwd=d)
            sh("git", "branch", "claude/SCC-154-fresh", "main", cwd=d)   # tip == main's tip
            rc, out, moved = merge(d, "claude/incident-abc123", "main")
            c.check("INC4 · the absorb is ALLOWED with a fresh sibling lane at main's tip",
                    rc == 0 and moved and "MERGE REFUSED" not in out, out.strip()[-300:])
        with TempDir() as tmp:
            d = make_repo(tmp)
            # ...and the epic direction of the sanctioned absorb (the header's own words):
            # `allow`, so no note prints — the width pin that kills a dropped incident:epic arm.
            lane(d, "epic/SCC-154-e")
            lane(d, "claude/incident-abc123", "main")
            sh("git", "checkout", "-q", "epic/SCC-154-e", cwd=d)
            (d / "onepic.txt").write_text("x\n", encoding="utf-8")
            sh("git", "add", "onepic.txt", cwd=d)
            sh("git", "commit", "-qm", "SCC-154 on the epic", cwd=d)
            rc, out, moved = merge(d, "claude/incident-abc123", "epic/SCC-154-e")
            c.check("INC4 · epic -> incident (absorb) is ALLOWED outright, no decline note",
                    rc == 0 and moved and "MERGE REFUSED" not in out
                    and "/cicd-mobile-error-team" not in out, out.strip()[-300:])

    # ── INC3 · SCC-154: the four story/chore <-> incident pairs are POSITIVELY refused ─────
    if c.block("INC3 · SCC-154: the four story/chore <-> incident pairs are POSI"):
        # Before this, all four fell through to the `*)` unknown default — allowed with a note —
        # so narrowing the incident arm alone would NOT have re-refused them (the SCC-149 review's
        # own measurement). An incident lane exchanges work with main and only main.
        for label, target, source in (
            ("incident -> story", "claude/SCC-154-t", "claude/incident-abc123"),
            ("incident -> chore", "chore/SCC-154-c", "claude/incident-abc123"),
            ("story -> incident", "claude/incident-abc123", "claude/SCC-154-s"),
            ("chore -> incident", "claude/incident-abc123", "chore/SCC-154-c"),
        ):
            with TempDir() as tmp:
                d = make_repo(tmp)
                lane(d, source)
                lane(d, target, "main")
                rc, out, moved = merge(d, target, source)
                c.check(f"INC3 · {label} is REFUSED", rc != 0 and not moved, out.strip()[-300:])
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "claude/incident-abc123")
            lane(d, "claude/SCC-154-t", "main")
            rc, out, _ = merge(d, "claude/SCC-154-t", "claude/incident-abc123")
            c.check("INC3 · ...and the refusal names the incident destination",
                    "incident pipeline" in out, out.strip()[-300:])

    # ── INC5 · SCC-159: incident <-> incident is REFUSED, both directions ──────────────────
    if c.block("INC5 · SCC-159: incident <-> incident is REFUSED, both direction"):
        # Two concurrent incidents + a `cd` slip cross-lands one incident's work on the other,
        # and BOTH gates waved it through with a friendly note: judge() sent the pair to the
        # `incident:*|*:incident` unknown arm, which is positively-classified-then-unjudged.
        # "Unjudged" was right for incident<->main; for a sibling incident lane it is the SCC-97
        # wrong-target shape wearing a second incident name, and the pair has no legitimate use.
        #
        # BOTH DIRECTIONS are pinned even though the classes are identical, because the arm is
        # matched on the "$target:$source" pair — a mutant narrowing it to one side would be
        # invisible to a single-direction case.
        for label, target, source in (
            ("A <- B", "claude/incident-aaa111", "claude/incident-bbb222"),
            ("B <- A", "claude/incident-bbb222", "claude/incident-aaa111"),
        ):
            with TempDir() as tmp:
                d = make_repo(tmp)
                lane(d, source)
                lane(d, target, "main")
                rc, out, moved = merge(d, target, source)
                c.check(f"INC5 · incident {label} incident is REFUSED",
                        rc != 0 and not moved, out.strip()[-300:])
                # ⛔ "incident pipeline" alone was satisfied by the STALE destination sentence
                # ("never with a story or chore lane") — a refusal of an incident<->incident
                # merge that read as a misfire mid-incident, and a pin that could not fail its
                # subject (SCC-156 review #12). The sentence now names the sibling case, and
                # this pins THAT.
                c.check(f"INC5 · ...and the {label} refusal names the SIBLING incident case",
                        "sibling incident lane" in out, out.strip()[-300:])

        # ⭐ THE FALSE-RED CONTROLS — the arms this narrowing must NOT eat. An incident lane
        # absorbing main (or an epic) is the everyday mid-incident move and stays ALLOWED
        # outright; SCC-154 landed that allow arm precisely because a refusal there costs more
        # than a miss, and INC5 sits between it and the unknown wildcard.
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "claude/incident-aaa111")
            # main must MOVE first, or the absorb is "Already up to date" and this control
            # passes on a merge that never happened.
            sh("git", "checkout", "-q", "main", cwd=d)
            (d / "on_main.txt").write_text("x\n", encoding="utf-8")
            sh("git", "add", "on_main.txt", cwd=d)
            sh("git", "commit", "-qm", "SCC-159 work on main", "--no-verify", cwd=d)
            rc, out, moved = merge(d, "claude/incident-aaa111", "main")
            c.check("INC5 · control: incident <- main absorb is still ALLOWED",
                    rc == 0 and moved, out.strip()[-300:])
        with TempDir() as tmp:
            d = make_repo(tmp)
            lane(d, "epic/SCC-159-e")
            lane(d, "claude/incident-aaa111", "main")
            rc, out, moved = merge(d, "claude/incident-aaa111", "epic/SCC-159-e")
            c.check("INC5 · control: incident <- epic absorb is still ALLOWED",
                    rc == 0 and moved, out.strip()[-300:])

        # ═══ THE FAST-FORWARD BACKSTOP ════════════════════════════════════════════════════════
        # Case E measured the gap: a ff merge creates no commit, so NO commit-time hook can see it.
        # What it leaves behind is evidence — another lane's unlanded commits are now contained in
        # yours — and push time is the last moment anything can refuse.

    # ── G · a lane carrying another UNLANDED lane's commits is REFUSED at push ────────────
    if c.block("G · a lane carrying another UNLANDED lane's commits is REFUSED a"):
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
    if c.block("H · ⭐ THE FALSE-RED CONTROL — absorbing main after a sibling LAN"):
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
    if c.block("I · ⭐ THE SHIPPING-PATH CONTROL — main carrying the lane it is l"):
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
    if c.block("I2 · the same control for a story lane landing on its epic"):
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "epic/SCC-144-e")
            sh("git", "push", "-q", "origin", "epic/SCC-144-e", cwd=d)
            lane(d, "claude/SCC-144-s", "epic/SCC-144-e")
            sh("git", "checkout", "-q", "epic/SCC-144-e", cwd=d)
            sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: s -> e", "claude/SCC-144-s", cwd=d)
            rc, out = sh("git", "push", "origin", "epic/SCC-144-e", cwd=d)
            c.check("I2 · landing a story on its epic is ALLOWED", rc == 0, out.strip()[-400:])

    # ── ⛔⛔ PARK · THE CRITICAL CONTROL — a story lane pushes after absorbing its epic ─────
    if c.block("⛔⛔ PARK · THE CRITICAL CONTROL — a story lane pushes after absor"):
        # This is `/cicd-park` verbatim: absorb `origin/epic/<KEY>` inside the worktree, then push the
        # `claude/*` branch. `git-policy.md` marks that push FREE — no approval. The first cut of the
        # backstop measured "already landed" against `origin/main` ONLY, so the moment one story landed
        # on the epic and a sibling absorbed it, this push was REFUSED — with a remedy naming a ref that
        # does not exist yet, on the one command whose job is stopping work being stranded on a machine.
        #
        # Three review lenses found it independently and two reproduced it end to end. It is the exact
        # failure this file's own header calls the expensive one, committed by the file that names it.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "epic/SCC-144-e")
            sh("git", "push", "-q", "origin", "epic/SCC-144-e", cwd=d)
            lane(d, "claude/SCC-144-s1", "epic/SCC-144-e")           # story 1
            sh("git", "checkout", "-q", "epic/SCC-144-e", cwd=d)     # ...lands on the EPIC, not main
            sh("git", "merge", "--no-ff", "-m", "SCC-144 merge: s1 -> e", "claude/SCC-144-s1", cwd=d)
            sh("git", "push", "-q", "origin", "epic/SCC-144-e", cwd=d)
            sh("git", "fetch", "-q", "origin", cwd=d)
            lane(d, "claude/SCC-144-s2", "epic/SCC-144-e")           # story 2 absorbs it
            rc, out = sh("git", "push", "origin", "claude/SCC-144-s2", cwd=d)
            c.check("PARK · a story lane carrying a sibling that landed on the EPIC pushes fine",
                    rc == 0,
                    "the epic does not reach main until /cicd-push-e2e ships it, so measuring "
                    "'landed' against origin/main alone refuses every parked story lane: "
                    + out.strip()[-300:])
            rc, out = sh("git", "ls-remote", "--heads", str(bare), "claude/SCC-144-s2", cwd=d)
            c.check("PARK · ...and it reached the remote", "claude/SCC-144-s2" in out, out)

    # ── G2 · the backstop still REFUSES a story lane carrying a genuinely unlanded sibling ─
    if c.block("G2 · the backstop still REFUSES a story lane carrying a genuinel"):
        # The other half of the PARK fix: widening the reference set must not disarm the check for
        # story lanes, or the fix traded a false red for a silent hole.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "epic/SCC-144-e")
            sh("git", "push", "-q", "origin", "epic/SCC-144-e", cwd=d)
            sh("git", "fetch", "-q", "origin", cwd=d)
            lane(d, "claude/SCC-144-s1", "epic/SCC-144-e")           # never landed anywhere
            sh("git", "checkout", "-q", "-b", "claude/SCC-144-s2", "epic/SCC-144-e", cwd=d)
            sh("git", "merge", "--ff-only", "claude/SCC-144-s1", cwd=d)
            rc, out = sh("git", "push", "origin", "claude/SCC-144-s2", cwd=d)
            c.check("G2 · a story lane carrying an UNLANDED sibling is still REFUSED", rc != 0,
                    out.strip()[-300:])
            c.check("G2 · ...and the remedy names the EPIC, not main",
                    "its epic/* branch" in out,
                    "'land it on main first' is the one thing merge-target-guard REFUSES for a "
                    "story lane: " + out.strip()[-300:])

    # ── G3 · the backstop's DISARMED path — warn, never refuse ────────────────────────────
    if c.block("G3 · the backstop's DISARMED path — warn, never refuse"):
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            (d / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").unlink()
            lane(d, "chore/SCC-144-a")
            sh("git", "checkout", "-q", "-b", "chore/SCC-144-b", "main", cwd=d)
            sh("git", "merge", "--ff-only", "chore/SCC-144-a", cwd=d)
            rc, out = sh("git", "push", "origin", "chore/SCC-144-b", cwd=d)
            c.check("G3 · disarmed, a contaminated push is ALLOWED", rc == 0, out.strip()[-300:])
            c.check("G3 · ...but it still says so", "disarmed" in out, out.strip()[-300:])

    # ── G4 · the backstop's DISABLE kill switch ───────────────────────────────────────────
    if c.block("G4 · the backstop's DISABLE kill switch"):
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            (d / ".agents/scripts/git-hooks/DISABLE").write_text("off\n", encoding="utf-8")
            lane(d, "chore/SCC-144-a")
            sh("git", "checkout", "-q", "-b", "chore/SCC-144-b", "main", cwd=d)
            sh("git", "merge", "--ff-only", "chore/SCC-144-a", cwd=d)
            rc, out = sh("git", "push", "origin", "chore/SCC-144-b", cwd=d)
            c.check("G4 · DISABLE allows the contaminated push", rc == 0, out.strip()[-300:])

    # ── G5 · a renamed refspec must not flag the lane against ITSELF ──────────────────────
    if c.block("G5 · a renamed refspec must not flag the lane against ITSELF"):
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "chore/SCC-144-a")
            rc, out = sh("git", "push", "origin",
                         "chore/SCC-144-a:refs/heads/chore/SCC-144-renamed", cwd=d)
            c.check("G5 · pushing a lane under a different remote name is ALLOWED", rc == 0,
                    "the self-skip compared the REMOTE name against LOCAL branch names: "
                    + out.strip()[-300:])

    # ── G6 · SCC-154: an incident ref through the backstop — the pipeline's business ───────
    if c.block("G6 · SCC-154: an incident ref through the backstop — the pipelin"):
        # The backstop matched incident refs through the `refs/heads/claude/*` glob and judged them
        # as story lanes: refusal + the SCC-148 misroute remedy ("its epic/* branch"), printed to a
        # phone mid-incident (SCC-149 C1). An incident lane's merges are the incident pipeline's
        # business, same posture as the guard: note, never a refusal.
        # ⭐ SCC-159 NARROWED THIS (finding 28). The skip was keyed on the pushed ref alone, so
        # an incident ref was waved through carrying ANYTHING — while the commit-time guard
        # refuses exactly that content as story:incident / chore:incident. A fast-forward makes
        # no commit, so the ff variant of a refused merge escaped both gates: the divergence was
        # widest precisely during an incident, when mistakes are most likely.
        #
        # What stays allowed is the lane ITSELF — that is what "the pipeline owns it" means.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "claude/incident-abc123")                           # its own work only
            rc, out = sh("git", "push", "origin", "claude/incident-abc123", cwd=d)
            c.check("G6 · pushing an incident lane carrying ONLY its own work is ALLOWED",
                    rc == 0, out.strip()[-400:])
            c.check("G6 · ...and says so, naming the pipeline", "/cicd-mobile-error-team" in out,
                    out.strip()[-400:])
            c.check("G6 · ...never the story-lane misroute", "its epic/* branch" not in out,
                    out.strip()[-400:])

        # ── G6b · SCC-159: the ff-variant hole — an incident ref carrying a FOREIGN lane ────
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "chore/SCC-159-x")                                  # unlanded foreign work
            sh("git", "checkout", "-q", "-b", "claude/incident-abc123", "main", cwd=d)
            sh("git", "merge", "--ff-only", "chore/SCC-159-x", cwd=d)   # the contaminated topology
            rc, out = sh("git", "push", "origin", "claude/incident-abc123", cwd=d)
            c.check("G6b · an incident ref carrying an UNLANDED chore lane is REFUSED",
                    rc != 0, out.strip()[-400:])
            c.check("G6b · ...and the refusal names the contaminating lane",
                    "chore/SCC-159-x" in out, out.strip()[-400:])
            c.check("G6b · ...and still routes incidents to the pipeline, never the epic misroute",
                    "/cicd-mobile-error-team" in out and "its epic/* branch" not in out,
                    out.strip()[-400:])

        # ── G6c · SCC-159: incident carrying a sibling INCIDENT — the push half of INC5 ─────
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "claude/incident-bbb222")
            sh("git", "checkout", "-q", "-b", "claude/incident-aaa111", "main", cwd=d)
            sh("git", "merge", "--ff-only", "claude/incident-bbb222", cwd=d)
            rc, out = sh("git", "push", "origin", "claude/incident-aaa111", cwd=d)
            c.check("G6c · an incident ref carrying a SIBLING incident lane is REFUSED",
                    rc != 0, out.strip()[-400:])
            c.check("G6c · ...and names the sibling",
                    "claude/incident-bbb222" in out, out.strip()[-400:])

        # ── G6d · the false-red control: incident content already on main is NOT foreign ────
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "chore/SCC-159-y")
            sh("git", "checkout", "-q", "main", cwd=d)
            sh("git", "merge", "--no-ff", "-m", "SCC-159 merge: landed", "chore/SCC-159-y",
               "--no-verify", cwd=d)
            sh("git", "push", "-q", "origin", "main", cwd=d)            # it LANDED
            sh("git", "checkout", "-q", "-b", "claude/incident-abc123", "main", cwd=d)
            (d / "fix.txt").write_text("hotfix\n", encoding="utf-8")
            sh("git", "add", "fix.txt", cwd=d)
            sh("git", "commit", "-qm", "SCC-159 hotfix", "--no-verify", cwd=d)
            rc, out = sh("git", "push", "origin", "claude/incident-abc123", cwd=d)
            c.check("G6d · an incident lane cut from a main that already carries the lane is ALLOWED",
                    rc == 0, out.strip()[-400:])

        # ── G6e · ⛔ THE EPIC-WIDENING HOLE. Two review lenses reproduced this independently.
        # Removing the `continue` sent incident refs into the containment loop — but `lane` is
        # then `claude/incident-*`, which MATCHES the `claude/*` glob in the BASES switch. So
        # every `origin/epic/*` tip was added as a landing point, and any story lane that had
        # landed on ANY epic scored `landed=1` and rode through.
        #
        # The asymmetry is the tell: `integration_of()` was given an ordered `claude/incident-*`
        # arm above `claude/*` in SCC-154 for this exact first-match reason. The BASES switch is
        # its sibling and never got the arm. An incident lane integrates on MAIN — the epic
        # widening exists to spare `/cicd-park` on STORY lanes and has no business here, which
        # is why the previous G6 cases could not see it: none of their fixtures creates an
        # `origin/epic/*` ref at all.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            # A story lane that landed on its epic — the ordinary state of a story lane — and
            # is NOT on main.
            lane(d, "claude/SCC-201-story")
            sh("git", "checkout", "-q", "-b", "epic/SCC-200-thing", "main", cwd=d)
            sh("git", "merge", "--no-ff", "-m", "SCC-200 merge: story onto epic",
               "claude/SCC-201-story", "--no-verify", cwd=d)
            sh("git", "push", "-q", "origin", "epic/SCC-200-thing", cwd=d)
            # The incident lane fast-forwards that unlanded story in.
            sh("git", "checkout", "-q", "-b", "claude/incident-abc123", "main", cwd=d)
            sh("git", "merge", "--ff-only", "claude/SCC-201-story", cwd=d)
            rc, out = sh("git", "push", "origin", "claude/incident-abc123", cwd=d)
            c.check("G6e · an incident ref carrying epic-only work is REFUSED even when an "
                    "origin/epic exists", rc != 0, out.strip()[-500:])
            c.check("G6e · ...and the remedy names MAIN via the pipeline, never 'the epic'",
                    "origin/main or the epic" not in out, out.strip()[-500:])

        # ── G6f · the control that keeps G6e honest: the SAME epic topology on a STORY lane
        # must still be ALLOWED. This is the `/cicd-park` path `git-policy.md` marks free, and
        # refusing it strands work on one machine — the false red this file prices above a miss.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "claude/SCC-201-story")
            sh("git", "checkout", "-q", "-b", "epic/SCC-200-thing", "main", cwd=d)
            sh("git", "merge", "--no-ff", "-m", "SCC-200 merge: story onto epic",
               "claude/SCC-201-story", "--no-verify", cwd=d)
            sh("git", "push", "-q", "origin", "epic/SCC-200-thing", cwd=d)
            sh("git", "checkout", "-q", "-b", "claude/SCC-202-sibling", "main", cwd=d)
            sh("git", "merge", "--ff-only", "claude/SCC-201-story", cwd=d)
            rc, out = sh("git", "push", "origin", "claude/SCC-202-sibling", cwd=d)
            c.check("G6f · CONTROL a STORY lane carrying epic-landed work is still ALLOWED",
                    rc == 0, out.strip()[-500:])

    # ── EP · SCC-163: the containment loop was blind to `epic/*` ──────────────────────────
    if c.block("EP · SCC-163: the containment loop was blind to epic/*"):
        # ⛔ THE DEFECT. The loop enumerated `refs/heads/chore` and `refs/heads/claude` only, so a
        # `chore/*` lane that fast-forwarded an epic carried that epic's unlanded commits to the
        # remote with NOTHING looking. `merge-target-guard.sh` already rules the pairing
        # `chore:epic -> refuse` (its judge table, `target:source`) — this made the backstop
        # enforce law the guard had been stating alone since SCC-144. A ff writes no commit, so
        # the commit-time guard never fired: exactly the blind spot this file exists to cover.
        #
        # ⛔⛔ AND IT CANNOT BE A BLANKET WIDENING, WHICH IS THE WHOLE DIFFICULTY. Three arms of
        # that same table say an epic inside a lane is LEGITIMATE:
        #     story:epic     allow   (a story lane absorbing its own epic — /cicd-park, every day)
        #     incident:epic  allow   ("absorbing main (or an epic) is the everyday mid-incident move")
        #     epic:story     allow   (pushed ref is epic/* — declined at the ref filter above)
        # Adding `refs/heads/epic` unconditionally false-reds every one of them. So the arm is
        # keyed on the lane class, mirroring the BASES switch it sits beside: `chore/*` ONLY.
        # EP2/EP2b/EP3 are the controls that hold that line, and they are why the fix is four
        # words in a `case` rather than one word in a `for`.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "epic/SCC-163-thing")                              # unlanded epic work
            sh("git", "checkout", "-q", "-b", "chore/SCC-163-lane", "main", cwd=d)
            sh("git", "merge", "--ff-only", "epic/SCC-163-thing", cwd=d)   # writes NO commit
            rc, out = sh("git", "push", "origin", "chore/SCC-163-lane", cwd=d)
            c.check("EP1 · a chore lane carrying an UNLANDED epic is REFUSED", rc != 0,
                    "chore:epic is `refuse` in the judge table; the ff variant escaped both "
                    "gates: " + out.strip()[-500:])
            c.check("EP1 · ...and the refusal names the epic",
                    "epic/SCC-163-thing" in out, out.strip()[-500:])
            c.check("EP1 · ...and prints the standard banner",
                    "carrying another lane's unlanded work" in out, out.strip()[-500:])
            rc, out = sh("git", "ls-remote", "--heads", str(bare), "chore/SCC-163-lane", cwd=d)
            c.check("EP1 · ...and nothing reached the remote",
                    "chore/SCC-163-lane" not in out, out)

        # ── EP2 · CONTROL story:epic — the epic is LOCAL, so BASES cannot rescue it ──────────
        # Deliberately an UNPUSHED epic. With the epic on `origin`, a blanket widening would
        # still score `landed=1` through the `claude/*` arm of the BASES switch and this control
        # would pass against the very mutant it exists to kill (A-M2). Unpushed, BASES is
        # `origin/main` alone — so only the lane-class arm can keep this green.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "epic/SCC-163-e")                                  # never pushed
            lane(d, "claude/SCC-163-s", "epic/SCC-163-e")              # cut from it => contains it
            rc, out = sh("git", "push", "origin", "claude/SCC-163-s", cwd=d)
            c.check("EP2 · CONTROL a STORY lane carrying its own (local) epic is ALLOWED",
                    rc == 0,
                    "story:epic is `allow`; a blanket widening false-reds every story lane: "
                    + out.strip()[-500:])

        # ── EP2b · the same control in the /cicd-park shape: the epic IS on origin ───────────
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "epic/SCC-163-e")
            sh("git", "push", "-q", "origin", "epic/SCC-163-e", cwd=d)
            sh("git", "fetch", "-q", "origin", cwd=d)
            lane(d, "claude/SCC-163-s", "epic/SCC-163-e")
            rc, out = sh("git", "push", "origin", "claude/SCC-163-s", cwd=d)
            c.check("EP2b · CONTROL the same story lane with the epic pushed is ALLOWED",
                    rc == 0, out.strip()[-500:])

        # ── EP3 · CONTROL incident:epic — `allow` at the judge table, so never enumerated ────
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "epic/SCC-163-e")                                  # local, unlanded
            sh("git", "checkout", "-q", "-b", "claude/incident-abc123", "main", cwd=d)
            sh("git", "merge", "--ff-only", "epic/SCC-163-e", cwd=d)
            rc, out = sh("git", "push", "origin", "claude/incident-abc123", cwd=d)
            c.check("EP3 · CONTROL an INCIDENT lane absorbing an epic is ALLOWED", rc == 0,
                    "incident:epic is `allow` — the everyday mid-incident move: "
                    + out.strip()[-500:])

        # ── EP4 · CONTROL epic:story — a pushed epic/* is declined at the ref filter ─────────
        # This is the arm SCC-163 deliberately did NOT widen (operator ruling: "A3. no we dont
        # need it."). The case pins the CONSEQUENCE of that ruling — an epic push is not judged —
        # so if anyone widens the filter later without building the third enumeration set, this
        # goes red and says why.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "claude/SCC-163-s")
            sh("git", "checkout", "-q", "-b", "epic/SCC-163-e", "main", cwd=d)
            sh("git", "merge", "--ff-only", "claude/SCC-163-s", cwd=d)
            rc, out = sh("git", "push", "origin", "epic/SCC-163-e", cwd=d)
            c.check("EP4 · CONTROL a pushed epic/* carrying a story is ALLOWED", rc == 0,
                    "epic:story is `allow`, and the ref filter declines epic pushes outright: "
                    + out.strip()[-500:])

        # ── EP5 · CONTROL main:epic — landing an epic on main is the shipping path ───────────
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "epic/SCC-163-e")
            sh("git", "checkout", "-q", "main", cwd=d)
            sh("git", "merge", "--ff-only", "epic/SCC-163-e", cwd=d)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("EP5 · CONTROL landing an epic on main is ALLOWED", rc == 0,
                    "main:epic is `allow` — /cicd-push-e2e's whole job: " + out.strip()[-500:])

        # ── EP6 · the ruled omission is WIRING, not a promise in prose ───────────────────────
        # SCC-125: a guard pinned to a DESCRIPTION is vacuous — the opposite-meaning file scores
        # full marks. So this reads the two things that are actually load-bearing: the epic
        # enumeration is inside a chore-only arm, and the pushed-ref filter still does NOT accept
        # `refs/heads/epic/*`. The prose rationale is required too, but it is checked LAST and
        # only after the wiring, so a comment can never satisfy this case on its own.
        src = BACKSTOP.read_text(encoding="utf-8")
        # ⛔ Read CODE, not the file. An earlier cut of this case compared `src.index(...)`
        # offsets, which the fix's own explanatory comment then broke by mentioning
        # `refs/heads/epic` above the arm — a guard a COMMENT can invert, which is the exact
        # shape memory:comment-literals-invert-source-grep-tests names. Comments are stripped
        # first, so the only lines left are ones git actually executes.
        code = [ln for ln in src.splitlines() if not ln.lstrip().startswith("#")]
        epic_lines = [ln for ln in code if "refs/heads/epic" in ln]
        c.check("EP6 · the epic enumeration is keyed to chore/* only",
                len(epic_lines) == 1 and "chore/*)" in epic_lines[0],
                "the enumeration must sit inside a lane-class arm, not in the bare for-loop; "
                f"executable lines naming refs/heads/epic: {epic_lines}")
        c.check("EP6 · the pushed-ref filter still declines epic/* (the ruled omission)",
                "refs/heads/chore/*|refs/heads/claude/*)" in src
                and "refs/heads/epic/*)" not in src,
                "A3 was ruled `document, do not widen` — widening needs its own enumeration set")
        c.check("EP6 · ...and the omission is documented with its reason",
                "epic:chore" in src and "epic:epic" in src,
                "a residual gap recorded nowhere is indistinguishable from one nobody noticed")

    # ── G7 · SCC-154: incident-as-FOREIGN — still refused, remedy re-routed ────────────────
    if c.block("G7 · SCC-154: incident-as-FOREIGN — still refused, remedy re-rou"):
        # A chore lane genuinely carrying an unlanded incident branch IS contaminated — the refusal
        # stands. What must change is the prescription: `integration_of` sent the operator to "its
        # epic/* branch" for a branch class that lands on MAIN via the incident pipeline.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp)
            lane(d, "claude/incident-abc123")                           # unlanded incident work
            sh("git", "checkout", "-q", "-b", "chore/SCC-154-b", "main", cwd=d)
            sh("git", "merge", "--ff-only", "claude/incident-abc123", cwd=d)
            rc, out = sh("git", "push", "origin", "chore/SCC-154-b", cwd=d)
            c.check("G7 · a chore lane carrying an UNLANDED incident branch is still REFUSED",
                    rc != 0, out.strip()[-400:])
            c.check("G7 · ...and the remedy routes to the incident pipeline, never the epic misroute",
                    "/cicd-mobile-error-team" in out and "its epic/* branch" not in out,
                    out.strip()[-400:])

    # ── O · no origin/main — there is no reference point, so it declines and SAYS so ───────
    if c.block("O · no origin/main — there is no reference point, so it declines"):
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
    if c.block("P · ⛔⛔ THE STDIN TEE — pre-push gets ONE stdin and there are now"):
        # A pre-push hook receives one line per ref ON STDIN, and stdin can be consumed exactly once.
        # If the dispatcher hands the raw stream to the first gate, the second reads EOF, its `while
        # read` loop never runs, and it exits 0 — SILENTLY ALLOWING EVERYTHING. That is this ticket's
        # own failure class inside this ticket's own fix, so it gets a case that can only pass if the
        # SECOND gate really saw its input: a push to main with no approval token must still be
        # refused by the token gate, which is the gate that runs last.
        with TempDir() as tmp:
            d, bare = make_pushable(tmp, push_main=False,
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
    if c.block("L · the arm accounting — a fresh clone must report this gate OFF"):
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

    # ── RH (SCC-180) · `git reset --hard` is never printed as a remedy ────────────────────
    #
    # ⛔ THIS IS NOT A STYLE RULE. On 2026-08-15 this hook's own refusal banner printed
    #
    #     git reset --hard origin/$1     # ONLY if this lane was already pushed
    #
    # an agent read it as the instruction it looks like, ran it in the lobby's MAIN CHECKOUT,
    # and destroyed three other sessions' uncommitted work. The main checkout hosts
    # `_artifacts/_memory/`, which every session on this machine writes, so it is NEVER a clean
    # tree — `--hard` there is not a reset, it is a delete of other people's work. There is no
    # git hook for `reset`: nothing can refuse it after the fact. The only available fix is to
    # stop printing it, everywhere, and to keep it stopped.
    if c.block("RH · SCC-180: no instruction prints `git reset --hard` as a step"):

        def payload(line: str) -> str:
            """The line reduced to what a reader would TYPE, if anything.

            ⭐ THE WHOLE CHECK IS THIS FUNCTION, and it exists because a flat grep is wrong in
            BOTH directions here. The banner's occurrence is inside an `echo "…"` in a shell
            script — a *printed* command line, which is the most dangerous form, because it
            arrives looking like output from the tool itself. And the SOP's occurrence is prose
            explaining why `reset --hard` is the WRONG move: flagging that would push someone to
            delete the very sentence that teaches the lesson. Comment-literal blindness inverts
            naive source greps (SCC-125), and this is the case where it inverts them twice.
            """
            s = line.strip()
            for lead in ('echo "', "echo '", 'printf "', "printf '"):
                if s.startswith(lead):
                    s = s[len(lead):]
                    break
            s = s.lstrip("> \t")                       # markdown blockquote
            s = re.sub(r"^([-*+]|\d+\.)\s+", "", s)    # list bullet
            s = s.lstrip("$ \t")                       # shell prompt
            # ⛔ A LEADING BACKTICK IS DELIBERATELY NOT STRIPPED, and that is the rule, not an
            # omission. In markdown a backtick IS the signal "this is a name, not a step" — and
            # the first cut stripped it, which flagged `git-policy.md`'s own SCC-180 paragraph:
            # a line that names the command *in order to forbid it* was read as an instruction to
            # run it. The guard would have demanded the deletion of the sentence that carries the
            # lesson. Cost: a genuine instruction written as inline code (`` `git reset --hard x`
            # — run this ``) is not caught. That trade is taken knowingly; the dangerous form is
            # the bare, copy-pasteable one, and RH4 pins the mention side so it cannot drift back.
            return s.strip()

        NEEDLE = "reset --hard"
        imperatives: list[str] = []
        prose_hits = 0
        scanned = 0
        for rel in subprocess.run(
                ["git", "ls-files", ".agents", "docs"], cwd=str(REPO),
                capture_output=True, text=True).stdout.splitlines():
            p = REPO / rel
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            scanned += 1
            for n, line in enumerate(text.splitlines(), 1):
                if NEEDLE not in line:
                    continue
                if payload(line).startswith("git " + NEEDLE):
                    imperatives.append(f"{rel}:{n}")
                else:
                    prose_hits += 1

        # ⛔ The floor. A wrong CWD, a renamed directory or a `git ls-files` that matched nothing
        # makes every assertion below vacuously true — the SCC-165 lesson, applied here.
        c.check("RH0 · the sweep actually read the toolkit", scanned >= 100,
                f"only {scanned} tracked files scanned under .agents/ + docs/ — an empty glob "
                f"scores this whole block green while checking nothing")
        c.check("RH1 · nothing under .agents/ or docs/ prints `git reset --hard` as a step",
                not imperatives,
                f"found {imperatives} — the main checkout is never a clean tree; printing this "
                f"as a remedy is how three sessions' uncommitted work was destroyed (SCC-180)")

        # ⛔ RH1's ANTI-VACUITY TWIN, and the mutation sweep is what demanded it. RH1 asserts
        # "no imperatives found" — which is exactly what a BLIND detector reports too. Break one
        # line of `payload` (stop stripping `echo "`) and the guard stops seeing printed command
        # lines altogether, RH1 goes green on an empty list, RH2/RH3/RH4 all still pass, and the
        # whole block certifies a check that can no longer fail. RH0 is the floor for the SCAN
        # (did we read any files?); this is the floor for the DETECTOR (can it still tell the two
        # forms apart?). Both fixtures are synthetic on purpose: a control that reads the live
        # tree would go vacuous again the moment the tree is clean, which is the state we want.
        POSITIVE = '        echo "              git reset --hard origin/$1     # was the remedy"'
        NEGATIVE = "> Never `git reset --hard` in a shared checkout — it eats other lanes' work."
        c.check("RH1b · (control) the detector still SEES a printed `--hard` remedy",
                payload(POSITIVE).startswith("git " + NEEDLE),
                f"the shape the backstop shipped on 2026-08-15 is no longer recognised, so RH1 "
                f"passes by blindness rather than by cleanliness. payload -> {payload(POSITIVE)!r}")
        c.check("RH1c · (control) ...and still does NOT see the prose that forbids it",
                NEEDLE in NEGATIVE and not payload(NEGATIVE).startswith("git " + NEEDLE),
                f"a detector that flags the sentence teaching the lesson gets the lesson deleted. "
                f"payload -> {payload(NEGATIVE)!r}")

        # The two fixtures that keep RH1 honest, pinned by CONTENT rather than line number.
        banner = BACKSTOP.read_text(encoding="utf-8")
        # ⭐ ASSERTED THROUGH `payload`, NOT AS A FLAT SUBSTRING — and the first cut of this line
        # was `"reset --hard" not in banner`, which went RED against the CORRECT fix. The file now
        # explains why `--hard` was removed, and that explanation contains the string. A guard that
        # forbids the string forbids the lesson: the next person deletes the comment to get green,
        # and the reason is gone. Exactly the inversion SCC-125 records, reproduced inside the
        # check written to prevent it.
        banner_imperatives = [n for n, ln in enumerate(banner.splitlines(), 1)
                              if NEEDLE in ln and payload(ln).startswith("git " + NEEDLE)]
        c.check("RH2 · (fixture) the backstop's remedy is `--keep`, and says why",
                "reset --keep" in banner and not banner_imperatives,
                f"the banner is the FAIL fixture: if it ever prints `--hard` as a step again, RH1 "
                f"must fire. Imperative lines here: {banner_imperatives}")
        c.check("RH2b · ...and it names `--soft` for undoing a local commit",
                "reset --soft" in banner,
                "`--keep` refuses when the tree is dirty; the reader still needs the move that "
                "undoes a commit without touching the tree, or they reach for `--hard` anyway")
        sop = (REPO / "docs/_scc_sops_prds/workflows_testing_SOP.md").read_text(encoding="utf-8")
        c.check("RH3 · (fixture) PROSE naming `reset --hard` as the wrong move still PASSES",
                NEEDLE in sop and prose_hits >= 1,
                "the SOP explains why `reset --hard` would be expensive. A check that cannot "
                "tell that from an instruction would demand deleting the lesson")

        # RH4 · the second mention fixture, and the one that caught the detector being wrong.
        # `git-policy.md`'s SCC-180 paragraph names the command at the START of a line, inside
        # backticks, in order to FORBID it. Stripping that backtick made it read as a step.
        policy = (REPO / ".agents/rules/git-policy.md").read_text(encoding="utf-8")
        c.check("RH4 · (fixture) the RULE that forbids `--hard` may name it, and still PASSES",
                "reset --keep" in policy and "reset --soft" in policy
                and not [n for n, ln in enumerate(policy.splitlines(), 1)
                         if NEEDLE in ln and payload(ln).startswith("git " + NEEDLE)],
                "the law names --keep and --soft as the replacements, and naming --hard to ban "
                "it must not trip the ban — otherwise the only way to green is to delete the law")

    # ── RH-B · and the remedy we now print does what the banner claims ────────────────────
    # Prose in a banner is a promise. `--keep` is only the right advice if it genuinely refuses
    # rather than discarding — asserted against real git, not assumed from the man page.
    if c.block("RH-B · `git reset --keep` refuses on a dirty tree instead of discarding"):
        with TempDir() as tmp:
            r = tmp / "keep"
            r.mkdir()
            run = lambda *a: subprocess.run(["git", *a], cwd=str(r), capture_output=True,  # noqa: E731
                                            text=True)
            run("init", "-q", "-b", "main")
            run("config", "user.email", "t@t.t")
            run("config", "user.name", "t")
            (r / "landed.txt").write_text("v1\n")
            run("add", "-A"), run("commit", "-qm", "base")
            base = run("rev-parse", "HEAD").stdout.strip()
            (r / "landed.txt").write_text("v2\n")
            run("add", "-A"), run("commit", "-qm", "second")
            second = run("rev-parse", "HEAD").stdout.strip()

            # CLEAN tree: the drill still works, or the new advice is useless.
            got = run("reset", "--keep", base)
            c.check("RH-B1 · on a CLEAN tree `--keep` rewinds exactly as `--hard` would",
                    got.returncode == 0
                    and run("rev-parse", "HEAD").stdout.strip() == base
                    and (r / "landed.txt").read_text() == "v1\n",
                    (got.stdout + got.stderr).strip()[:200])

            # ⭐ DIRTY tree: THE POINT. This is the state the lobby's main checkout is always in.
            # ⛔ Re-advance to `second` FIRST. RH-B1 has already rewound HEAD to `base`, so
            # resetting to `base` again is a NO-OP that exits 0 — the assertion below went red on
            # its own setup, not on git's behaviour, and a "refuses" check that can pass because
            # nothing was asked of it is worthless in the other direction too.
            run("reset", "-q", "--hard", second)
            (r / "other-session.txt").write_text("another session's unsaved memory edit\n")
            (r / "landed.txt").write_text("v1-edited-by-someone-else\n")
            got = run("reset", "--keep", base)
            c.check("RH-B2 · on a DIRTY tree `--keep` REFUSES and the other work survives",
                    got.returncode != 0
                    and (r / "other-session.txt").is_file()
                    and (r / "landed.txt").read_text() == "v1-edited-by-someone-else\n",
                    "this is the whole reason the banner changed — `--hard` here would have "
                    "eaten both files without a word:\n" + (got.stdout + got.stderr).strip()[:200])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
