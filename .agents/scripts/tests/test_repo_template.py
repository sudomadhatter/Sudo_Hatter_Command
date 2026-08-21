"""_repo_template.py — every scenario repo is a CLONE, and a clone is not shared state. (SCC-214)

`test_task_preflight.py` and `test_git_hooks.py` build a real throwaway git repo per scenario.
SCC-214 replaces the construction with a reset from a template clone, and the ticket's constraint
is the whole reason this file exists:

    RESET-FROM-TEMPLATE, NEVER A SHARED MUTABLE REPO. `test_git_hooks.py` guards the merge gate;
    introducing cross-test coupling there — scenario N seeing state left by scenario N-1 — trades
    a real safety property for seconds.

⛔ SO THE ISOLATION IS PROVEN BY A TEST THAT FAILS WHEN IT LEAKS, never by inspection (ticket
acceptance 2). Every case below drives the REAL builders or the real helper: a commit, a config
key, an untracked file, an in-place edit and a pushed ref made in one clone must be invisible in
the next, and in one cut afterwards.

⭐ THE SPEED PROPERTY IS A CASE TOO, and it is the one measurement found. This Mac assesses every
newly created executable ONCE, on its first launch — 0.2 s idle, 1.6–2.8 s under the suite's own
parallel load — and the assessment is per INODE: a hard link to an assessed file is instant, a
byte-copy pays again. Both suites create fresh executables per scenario (a fresh `acli` launcher
per preflight block, two to five hook scripts per git_hooks repo). So the clone HARD-LINKS
executables to the template's inode and FREEZES the template's copies read-only: the link is what
carries the assessment, and the freeze is what stops a shared inode from being shared state — an
in-place write raises instead of leaking. Git never writes a file in place (temp + rename), so
every git operation on a scenario's hook is isolated by construction. `HARD_LINKS` is False on
Windows on purpose: `_harness.TempDir.__exit__`'s rmtree handler chmods read-only files, which
through a link would unfreeze the template (and the PC has no assessor to save time with anyway).

Stdlib only, no pytest, matching every other file here.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ⛔ A MISSING MODULE IS A FAILING ROW, NEVER A SETUP DEATH. Before `_repo_template.py` exists this
# file must come up and fail where it ASSERTS — a test that dies on import looks identical to one
# that failed its assertion, and only one of those is a real red (`smh-quick-dev` Step 2).
try:
    import _repo_template as rt
    RT_ERR = ""
except Exception as exc:                       # noqa: BLE001 — any import failure, reported not raised
    rt = None
    RT_ERR = repr(exc)

import _pf_fixtures as pf                       # noqa: E402 — after the guarded import, deliberately
import test_git_hooks as gh                     # noqa: E402

# ⭐ THE BUILDER BLOCKS BELOW RUN WITH OR WITHOUT THE MODULE, and that is the point: T2 and T3
# assert what the REAL builders must do, so before `_repo_template.py` exists they run against
# today's builders and the rows that must change go red where they assert. Only the rows that
# call `rt.clone` directly (T1, T4 — the helper's own contract) can be skipped by its absence.
TEMPLATE_PREFIX = getattr(rt, "TEMPLATE_PREFIX", "wfscripts-tpl-")
HARD_LINKS = getattr(rt, "HARD_LINKS", os.name != "nt")


def sh(*args: str, cwd: Path) -> str:
    r = subprocess.run(list(args), cwd=str(cwd), capture_output=True, text=True, errors="replace")
    return (r.stdout or "") + (r.stderr or "")


def build_repo(root: Path) -> None:
    """A minimal real repo + a real executable, standing in for the suites' builders."""
    d = root / "repo"
    d.mkdir(parents=True)
    sh("git", "init", "-q", "-b", "main", cwd=d)
    sh("git", "config", "user.email", "t@t.t", cwd=d)
    sh("git", "config", "user.name", "t", cwd=d)
    (d / "README").write_text("base\n", encoding="utf-8")
    hook = d / "hook.sh"
    hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hook.chmod(0o755)
    sh("git", "add", "README", "hook.sh", cwd=d)
    sh("git", "commit", "-qm", "SCC-214 base", cwd=d)


def leaks(clone: Path) -> list[str]:
    """Every file under `clone` carrying an absolute path into a template root."""
    hits = []
    for p in clone.rglob("*"):
        if p.is_file() and p.stat().st_size < 200_000:
            try:
                if TEMPLATE_PREFIX in p.read_text(errors="replace"):
                    hits.append(str(p.relative_to(clone)))
            except OSError:
                pass
    return hits


def main() -> int:
    c = Cases("repo template clones (SCC-214)")

    if c.block("T1 · the helper contract — build once, clone clean, freeze what is shared"):
        c.check("the module imports", rt is not None, RT_ERR)

        if rt is not None:
            with TempDir() as t:
                builds = []
                key = ("t1", "build-once")
                for i in range(3):
                    rt.clone(key, lambda tpl: (builds.append(1), build_repo(tpl))[1], t / f"s{i}")
                c.check("clone builds the template ONCE per key", len(builds) == 1,
                        f"built {len(builds)} times for 3 clones")

            with TempDir() as t:
                key = ("t1", "leak")
                a = rt.clone(key, build_repo, t / "a") / "repo"
                (a / "new.md").write_text("x\n", encoding="utf-8")
                sh("git", "add", "new.md", cwd=a)
                sh("git", "commit", "-qm", "SCC-214 scenario A", cwd=a)
                sh("git", "config", "scc214.left", "behind", cwd=a)
                (a / "untracked.txt").write_text("dropped\n", encoding="utf-8")
                b = rt.clone(key, build_repo, t / "b") / "repo"
                log = sh("git", "log", "--format=%s", cwd=b)
                c.check("a clone does not see its predecessor's commit",
                        "scenario A" not in log, log.strip()[:200])
                c.check("a clone does not see its predecessor's config",
                        not sh("git", "config", "scc214.left", cwd=b).strip(), "config leaked")
                c.check("a clone does not see its predecessor's untracked file",
                        not (b / "untracked.txt").exists(), "untracked file leaked")
                c.check("a fresh clone reads git-clean",
                        not sh("git", "status", "--porcelain", cwd=b).strip(),
                        sh("git", "status", "--porcelain", cwd=b).strip()[:200])

            with TempDir() as t:
                key = ("t1", "regular-vs-exec")
                a = rt.clone(key, build_repo, t / "a") / "repo"
                b = rt.clone(key, build_repo, t / "b") / "repo"
                (a / "README").write_text("A rewrote this\n", encoding="utf-8")
                c.check("editing a regular file in one clone leaves the other untouched",
                        (b / "README").read_text(encoding="utf-8") == "base\n",
                        (b / "README").read_text(encoding="utf-8")[:80])
                try:
                    with open(a / "hook.sh", "w", encoding="utf-8") as fh:
                        fh.write("mutated\n")
                    wrote = True
                except PermissionError:
                    wrote = False
                c.check("an in-place write through a shared executable raises",
                        not wrote, "the write SUCCEEDED — the freeze is not holding")
                c.check("the executable is still the template's bytes in the other clone",
                        (b / "hook.sh").read_text(encoding="utf-8") == "#!/bin/sh\nexit 0\n",
                        (b / "hook.sh").read_text(encoding="utf-8")[:80])

            with TempDir() as t:
                key = ("t1", "occupied")
                dest = t / "d"
                rt.clone(key, build_repo, dest)
                # ⛔ CATCH EVERYTHING, THEN ASSERT THE TYPE. A bare `except FileExistsError`
                # lets any other error escape and abort the whole file — and a file that dies
                # in a traceback prints no `FAILED:` line, which `mutation_sweep.judge()`
                # refuses to score, so the mutant aimed here would read as a survivor.
                err: BaseException | None = None
                try:
                    rt.clone(key, build_repo, dest)
                except BaseException as exc:                      # noqa: BLE001 — see above
                    err = exc
                c.check("a second clone into an occupied root refuses",
                        isinstance(err, FileExistsError),
                        f"raised {err!r} — a clone landed on top of an existing scenario")
                empty = t / "empty"
                empty.mkdir()
                ok = rt.clone(key, build_repo, empty)
                c.check("an EMPTY destination directory is accepted",
                        (ok / "repo/README").is_file(), "the receipts fixture shape was refused")

    if c.block("T2 · the preflight builders — isolation, the shared launcher, the key"):
        if True:
            with TempDir() as t:
                r1 = pf.make_repo(t / "s1")
                pf.write(r1, "docs/leak.md", "x\n")
                pf.commit(r1, "SCC-11 scenario one")
                pf.git(r1, "push", "-q", "origin", "main")
                r2 = pf.make_repo(t / "s2")
                log = pf.git(r2, "log", "--format=%s").stdout
                c.check("a preflight scenario does not see its predecessor's commit",
                        "scenario one" not in log, log.strip()[:200])
                # ⛔ FETCH FIRST. `refs/remotes/origin/main` was copied from the template and
                # sits at base whatever the remote holds, so reading it without fetching passes
                # even when `origin` still points at the TEMPLATE's bare — the exact leak this
                # row exists to catch. Found by aiming a mutant at it (SCC-214 sweep, M5).
                pf.git(r2, "fetch", "-q", "origin")
                remote = pf.git(r2, "log", "--format=%s", "origin/main").stdout
                c.check("a push from one scenario is invisible to the next scenario's origin",
                        "scenario one" not in remote, remote.strip()[:200])
                c.check("no clone carries a path into the template root (preflight)",
                        leaks(t / "s2") == [], str(leaks(t / "s2"))[:200])

            with TempDir() as t:
                plain = pf.make_repo(t / "plain")
                withci = pf.make_repo(t / "ci", ci=True)
                c.check("make_repo(ci=True) after make_repo() carries the workflow file",
                        (withci / ".github/workflows/gate.yml").is_file()
                        and not (plain / ".github/workflows/gate.yml").exists(),
                        "the template key is not distinguishing ci=True")

            with TempDir() as t:
                # ⛔ (inode, mtime), never inode alone. The launcher lives at a FIXED path, so a
                # `board()` that rewrote it every call would truncate-and-rewrite the SAME inode
                # and an inode-only assertion would read that as one launcher — while the OS
                # re-assessed the changed file all 88 times, which is the entire cost this
                # memo exists to remove. The pair pins both halves: written once, and written
                # somewhere that outlives the scenario's TempDir.
                stamps = set()
                for i in range(3):
                    d = t / f"b{i}"
                    d.mkdir()
                    pf.board(d)
                    st = Path(os.environ["ACLI_BIN"]).stat()
                    stamps.add((st.st_ino, st.st_mtime_ns))
                c.check("one launcher per process", len(stamps) == 1,
                        f"{len(stamps)} distinct (inode, mtime) launchers for 3 board() calls")
                c.check("each board() still points PF_BOARD_STATE at its own state file",
                        Path(os.environ["PF_BOARD_STATE"]).parent == t / "b2",
                        os.environ["PF_BOARD_STATE"])

    if c.block("T3 · the git_hooks builders — the inode share, the key, the real merge"):
        if True:
            with TempDir() as t:
                (t / "s1").mkdir()
                (t / "s2").mkdir()
                d1, _ = gh.make_pushable(t / "s1")
                gh.lane(d1, "chore/SCC-144-a")
                d2, _ = gh.make_pushable(t / "s2")
                branches = gh.sh("git", "branch", "--list", cwd=d2)[1]
                c.check("a git_hooks scenario does not see its predecessor's branch",
                        "SCC-144-a" not in branches, branches.strip()[:200])
                c.check("no clone carries a path into the template root (git_hooks)",
                        leaks(t / "s2") == [], str(leaks(t / "s2"))[:200])
                if HARD_LINKS:
                    c.check("a hook shares the template inode",
                            (d1 / ".githooks/commit-msg").stat().st_ino
                            == (d2 / ".githooks/commit-msg").stat().st_ino,
                            "the hook was copied, not linked — the assessment is paid twice")
                else:
                    c.check("a hook shares the template inode", True,
                            "SKIPPED: HARD_LINKS is False on this platform (by design on Windows)")

            with TempDir() as t:
                (t / "armed").mkdir()
                (t / "bare").mkdir()
                armed = gh.make_repo(t / "armed")
                bare = gh.make_repo(t / "bare", arm=False)
                c.check("make_repo(arm=False) after make_repo() carries no flag",
                        (armed / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").is_file()
                        and not (bare / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").exists(),
                        "the template key is not distinguishing arm=False")

            with TempDir() as t:
                (t / "merge").mkdir()
                d = gh.make_repo(t / "merge")
                gh.lane(d, "chore/SCC-144-x")
                rc, out, moved = gh.merge(d, "main", "chore/SCC-144-x")
                c.check("a real merge still runs through the linked, frozen hooks",
                        rc == 0 and moved, f"rc={rc} moved={moved} {out.strip()[-200:]}")

    if c.block("T4 · a build that raises caches NOTHING"):
        if rt is not None:
            with TempDir() as t:
                key = ("t4", "boom")
                calls = []

                def boom(tpl: Path) -> None:
                    calls.append(1)
                    build_repo(tpl)
                    raise RuntimeError("SCC-214 build failed on purpose")

                for i in range(2):
                    try:
                        rt.clone(key, boom, t / f"s{i}")
                    except BaseException:                          # noqa: BLE001, S110 — a cached
                        pass                                       # dead template raises here too
                c.check("a failed build caches nothing", len(calls) == 2,
                        f"the build ran {len(calls)} times — a failed template was cached")
                try:
                    good = rt.clone(key, build_repo, t / "after")
                    later, why = (good / "repo/README").is_file(), "the failed key stayed poisoned"
                except BaseException as exc:                       # noqa: BLE001
                    later, why = False, f"raised {exc!r}"
                c.check("a key whose build failed can still be built later", later, why)

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
