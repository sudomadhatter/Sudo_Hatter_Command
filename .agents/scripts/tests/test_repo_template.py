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

import inspect
import os
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ⛔ A MISSING MODULE IS A FAILING ROW, NEVER A SETUP DEATH. Before `_repo_template.py` exists this
# file must come up and fail where it ASSERTS — a test that dies on import looks identical to one
# that failed its assertion, and only one of those is a real red (`smh-quick-dev` Step 2).
# ⛔ ALL THREE IMPORTS IN ONE GUARD, and that is the whole point. Guarding only
# `_repo_template` was theatre: `_pf_fixtures` and `test_git_hooks` BOTH import it at module
# scope, so the guarded failure re-raised, unguarded, on the very next line — no title, no
# rows, no `-- n/m passed --`, no `FAILED:` line. `mutation_sweep.judge()` refuses to score
# that shape, so a mutant that breaks this module's import scored as a SWEEP ERROR against
# the very guard meant to catch it. Found by three independent review lenses.
try:
    import _repo_template as rt
    import _pf_fixtures as pf
    import test_git_hooks as gh
    RT_ERR = ""
except Exception as exc:                       # noqa: BLE001 — any import failure, reported not raised
    rt = pf = gh = None
    RT_ERR = repr(exc)

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
    """Every path under `clone` carrying an absolute path into a template root.

    ⛔ SYMLINKS ARE CHECKED BY TARGET, NOT BY CONTENT. `is_file()` and `read_text()` both FOLLOW
    links, so a symlink pointing at an absolute template path was read as its target's bytes and
    never matched — while `_copy_entry` carries an explicit symlink branch, so the copier
    anticipated them and the detector did not.
    """
    hits = []
    for p in clone.rglob("*"):
        if p.is_symlink():
            if TEMPLATE_PREFIX in os.readlink(p):
                hits.append(f"{p.relative_to(clone)} -> {os.readlink(p)}")
            continue
        if p.is_file() and p.stat().st_size < 200_000:
            try:
                if TEMPLATE_PREFIX in p.read_text(errors="replace"):
                    hits.append(str(p.relative_to(clone)))
            except OSError:
                pass
    return hits


def main() -> int:
    """Run every block, and make sure an ESCAPED exception is still a reported row.

    ⛔ A file that dies mid-run prints no `-- n/m passed --` and no `FAILED:` line, and
    `mutation_sweep.judge()` refuses to score that shape — so a mutant that CRASHES this file
    is recorded as `SWEEP ERROR`, indistinguishable from a survivor. Three mutants in this
    lane's own table landed there. Catching here turns any escape into a named row that a
    sweep can attribute, and `finish()` always runs.
    """
    c = Cases("repo template clones (SCC-214)")
    try:
        _run(c)
    except Exception as exc:                       # noqa: BLE001 — a crash must be a ROW
        # ⛔ THE ROW GOES UNDER A BLOCK, and the block is named for the filter that was
        # running. `test_suite_runner.py`'s ORPHAN guard requires every `c.check` to sit
        # inside an `if c.block(...)` body, so `--case` governs it — and it is right: a row
        # outside every block runs under every filter and cannot be attributed. Leading the
        # label with the active filter makes the substring match certain, so a crash under
        # `--case T1` is reported and scoreable rather than vanishing into a traceback.
        if c.block(f"{c.filter or 'T0'} · a block escaped with an unexpected error"):
            c.check("no unexpected error escaped a block", False,
                    f"{exc!r} — a defect has to become a red ROW; a file that dies prints no "
                    f"FAILED: line, and a sweep cannot tell that from a survivor")
    return c.finish()


def _run(c: Cases) -> None:

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

            # ⛔ THE CHMOD ESCAPE — the hole the freeze alone does NOT close, and the reason
            # `_verify_sealed` exists. `0o555` stops a write; a scenario that chmods first
            # writes straight through the shared inode into every other clone. Both halves.
            with TempDir() as t:
                key = ("t1", "chmod-escape")
                a = rt.clone(key, build_repo, t / "a") / "repo"
                c.check("a clean template passes the seal check (the ALLOW half)",
                        (rt.clone(key, build_repo, t / "b") / "repo/hook.sh").is_file(),
                        "a clean template was refused")
                # ⛔ THE ESCAPE ROUTE ITSELF IS PLATFORM-SHAPED (SCC-321). On POSIX the clone's
                # hook IS the template's inode (`HARD_LINKS`), so chmod-ing the clone corrupts
                # the template and the next clone must refuse. On Windows `HARD_LINKS` is False
                # BY DESIGN — the module's docstring says so, because the rmtree cleanup handler
                # chmods read-only files and would unfreeze the template through a link — so each
                # clone is a copy and chmod-ing one CANNOT reach the template. Asserting the POSIX
                # refusal there would demand a corruption the design has already made impossible.
                #
                # So each machine drives the guard through the door it actually has, and BOTH
                # end at `_verify_sealed` refusing a corrupt template — the Windows arm reaches
                # it by corrupting the template directly, which is the only route that exists
                # there, and it also pins the isolation that closes the clone route.
                victim = (a / "hook.sh") if rt.HARD_LINKS else (
                    rt._CACHE[key] / "repo" / "hook.sh")
                if not rt.HARD_LINKS:
                    (a / "hook.sh").chmod(0o755)
                    c.check("chmod in a CLONE cannot reach the template (no shared inode here)",
                            rt._is_frozen(rt._CACHE[key] / "repo" / "hook.sh"),
                            "a copy-based clone leaked a mode change into the template")
                victim.chmod(0o755)                   # the corruption, performed for real
                err = None
                try:
                    rt.clone(key, build_repo, t / "c")
                except Exception as exc:              # noqa: BLE001
                    err = exc
                c.check("a template whose executable was chmod'd is REFUSED (the REFUSE half)",
                        isinstance(err, rt.TemplateCorrupted),
                        f"raised {err!r} — a scenario mutated a SHARED template and the next "
                        f"clone accepted it, which is the shared-mutable-repo the ticket bans")
                victim.chmod(0o555)                   # leave the cache usable for later blocks
                if not rt.HARD_LINKS:
                    (a / "hook.sh").chmod(0o555)

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
                # ⛔ CATCH BROADLY, THEN ASSERT THE TYPE. A bare `except FileExistsError`
                # lets any other error escape and abort the whole file — and a file that dies
                # in a traceback prints no `FAILED:` line, which `mutation_sweep.judge()`
                # refuses to score, so the mutant aimed here would read as a survivor.
                # `Exception`, not `BaseException`: every error that concern names is an
                # Exception subclass, and catching KeyboardInterrupt here would swallow the
                # SIGINT unwind `run_all.stop_running` depends on.
                err: BaseException | None = None
                try:
                    rt.clone(key, build_repo, dest)
                except Exception as exc:                          # noqa: BLE001 — see above
                    err = exc
                c.check("a second clone into an occupied root refuses",
                        isinstance(err, FileExistsError),
                        f"raised {err!r} — a clone landed on top of an existing scenario")
                empty = t / "empty"
                empty.mkdir()
                ok = rt.clone(key, build_repo, empty)
                c.check("an EMPTY destination directory is accepted",
                        (ok / "repo/README").is_file(), "the receipts fixture shape was refused")

            # WIDTH, not just existence: the refusal above is proven on a template with ONE
            # top-level entry, so a clash scan narrowed to `sorted(tpl.iterdir())[:1]` passes it.
            # A two-entry template with only the SECOND entry pre-created is what separates
            # "checks every entry" from "checks any one entry".
            with TempDir() as t:
                def two_entries(root: Path) -> None:
                    build_repo(root)
                    (root / "origin.git").mkdir()
                    (root / "origin.git/HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
                key = ("t1", "occupied-width")
                rt.clone(key, two_entries, t / "first")
                dest = t / "second"
                # ⛔ THE SECOND ENTRY BY SORT ORDER — `sorted()` puts `origin.git` before
                # `repo`, so clashing on `origin.git` is still caught by a first-entry-only
                # scan and proves nothing. Clashing on `repo` is what separates the two.
                (dest / "repo").mkdir(parents=True)
                err = None
                try:
                    rt.clone(key, two_entries, dest)
                except Exception as exc:                       # noqa: BLE001
                    err = exc
                c.check("the occupied check scans EVERY template entry, not just the first",
                        isinstance(err, FileExistsError),
                        f"raised {err!r} — a clash on a later entry was not seen")

    if c.block("T2 · the preflight builders — isolation, the shared launcher, the key"):
        if pf is not None and rt is not None:
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
                url = pf.git(r2, "config", "remote.origin.url").stdout.strip()
                c.check("the clone's origin is re-pointed at ITS OWN bare",
                        url == str(t / "s2" / "origin.git"),
                        f"origin is {url!r} — not this scenario's bare. Asserting only that "
                        f"the predecessor's commit is invisible passes when origin is merely "
                        f"BROKEN, which is how a dropped set-url survived the first sweep")
                pf.git(r2, "fetch", "-q", "origin")
                remote = pf.git(r2, "log", "--format=%s", "origin/main").stdout
                c.check("a push from one scenario is invisible to the next scenario's origin",
                        "scenario one" not in remote, remote.strip()[:200])
                c.check("the sealed TEMPLATE itself carries no path into its own root",
                        leaks(rt.shared_root()) == [],
                        f"the template still leaks: {leaks(rt.shared_root())[:3]} — every "
                        f"clone inherits this, and only the caller's re-point hides it")
                found = leaks(t / "s2")     # bound ONCE: `detail` is eager, so the inline
                c.check("no clone carries a path into the template root (preflight)",
                        found == [], str(found)[:200])

            with TempDir() as t:
                plain = pf.make_repo(t / "plain")
                withci = pf.make_repo(t / "ci", ci=True)
                c.check("make_repo(ci=True) after make_repo() carries the workflow file",
                        (withci / ".github/workflows/gate.yml").is_file()
                        and not (plain / ".github/workflows/gate.yml").exists(),
                        "the template key is not distinguishing ci=True")

            with TempDir() as t:
                err = None
                try:
                    pf.make_repo(t / "typo", deployble=True)    # the typo IS the case
                except Exception as exc:                        # noqa: BLE001
                    err = exc
                # ⛔ `make_repo()`, not `_build_repo()`. Python raises its own TypeError from
                # `_build_repo(**opts)` and that message also carries the bad keyword — so a
                # case checking only the keyword passes with the explicit guard REMOVED. What
                # the guard actually buys is an error naming the function the caller typed.
                c.check("a typo'd keyword raises TypeError naming make_repo(), not the builder",
                        isinstance(err, TypeError) and "deployble" in str(err)
                        and "make_repo()" in str(err),
                        f"raised {err!r} — the caller is told about a private function they "
                        f"never called, or the wrapper swallowed a bad keyword entirely")
                good = pf.make_repo(t / "control", deployable=True)
                c.check("...and the REAL keyword is still accepted (the allow half)",
                        (good / "backend/app.py").is_file(), "a valid keyword was refused")

            # `_REPO_DEFAULTS` must mirror `_build_repo`'s keywords or that shape becomes
            # UNREACHABLE. Asserted in a ⛔ comment and, until now, nowhere in code.
            sig = {n for n, prm in inspect.signature(pf._build_repo).parameters.items()
                   if prm.kind is inspect.Parameter.KEYWORD_ONLY}
            c.check("_REPO_DEFAULTS mirrors _build_repo's keyword-only parameters exactly",
                    sig == set(pf._REPO_DEFAULTS),
                    f"only in _build_repo: {sorted(sig - set(pf._REPO_DEFAULTS))} · "
                    f"only in _REPO_DEFAULTS: {sorted(set(pf._REPO_DEFAULTS) - sig)}")

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
                c.check("the shared acli launcher is FROZEN, like every shared executable",
                        (Path(os.environ["ACLI_BIN"]).stat().st_mode & 0o222) == 0,
                        f"mode {oct(Path(os.environ['ACLI_BIN']).stat().st_mode & 0o777)} is "
                        f"writable — one write poisons every later block in the process")
                c.check("each board() still points PF_BOARD_STATE at its own state file",
                        Path(os.environ["PF_BOARD_STATE"]).parent == t / "b2",
                        os.environ["PF_BOARD_STATE"])

    if c.block("T3 · the git_hooks builders — the inode share, the key, the real merge"):
        if gh is not None and rt is not None:
            with TempDir() as t:
                (t / "s1").mkdir()
                (t / "s2").mkdir()
                d1, _ = gh.make_pushable(t / "s1")
                gh.lane(d1, "chore/SCC-144-a")
                d2, _ = gh.make_pushable(t / "s2")
                branches = gh.sh("git", "branch", "--list", cwd=d2)[1]
                c.check("a git_hooks scenario does not see its predecessor's branch",
                        "SCC-144-a" not in branches, branches.strip()[:200])
                found = leaks(t / "s2")     # form re-walked a whole cloned git repo twice,
                c.check("no clone carries a path into the template root (git_hooks)",
                        found == [], str(found)[:200])
                # ⛔ POSITIVE CONTROL — without it the row above passes by having nothing to
                # find. Measured: rename the two `mkdtemp(prefix=...)` sites while leaving
                # TEMPLATE_PREFIX defined and `leaks()` returns [] with a real FETCH_HEAD leak
                # sitting in the clone. Planting the REAL shared_root path proves the needle
                # still matches the haystack this module actually builds.
                (d2 / "planted.txt").write_text(str(rt.shared_root()), encoding="utf-8")
                c.check("...and the leak detector can actually SEE a planted template path",
                        leaks(t / "s2") != [],
                        f"leaks() is blind: TEMPLATE_PREFIX {rt.TEMPLATE_PREFIX!r} does not "
                        f"occur in the real template root {rt.shared_root()}")
                (d2 / "planted.txt").unlink()
                # ⛔ THE EXPECTATION IS COMPUTED HERE, NOT READ FROM THE MODULE UNDER TEST.
                # Reading `rt.HARD_LINKS` to decide whether to assert let the module switch its
                # own check off: mutating `_links_work`'s platform gate disabled hard-linking
                # entirely — the whole mechanism this ticket exists to build — and the row
                # printed "SKIPPED" while the suite stayed 24/24 green. So probe linkability
                # INDEPENDENTLY and require the module to agree with the probe.
                probe_links = os.name != "nt"
                if probe_links:
                    try:
                        a = t / "_probe_a"
                        a.write_text("x", encoding="utf-8")
                        os.link(a, t / "_probe_b")
                        probe_links = a.stat().st_ino == (t / "_probe_b").stat().st_ino
                    except OSError:
                        probe_links = False
                c.check("HARD_LINKS agrees with an independent probe of this platform",
                        rt.HARD_LINKS == probe_links,
                        f"module says {rt.HARD_LINKS}, probe says {probe_links} — the module "
                        f"cannot be allowed to declare its own speed property off")
                same_inode = ((d1 / ".githooks/commit-msg").stat().st_ino
                              == (d2 / ".githooks/commit-msg").stat().st_ino)
                c.check("a hook shares the template inode exactly when linking is possible",
                        same_inode == probe_links,
                        f"inode shared={same_inode}, linking possible={probe_links} — a copy "
                        f"where a link was possible pays the OS assessment on every scenario")
                # The fallback half: linked or copied, the bytes must be identical either way,
                # because the module docstring claims correctness never depends on the link.
                c.check("linked or copied, the hook is byte-identical in both scenarios",
                        (d1 / ".githooks/commit-msg").read_bytes()
                        == (d2 / ".githooks/commit-msg").read_bytes(),
                        "the two scenarios disagree on the hook's contents")

            # `_key()` is a NEW function whose stated invariant nothing exercised: `return ()`
            # survives the whole suite, because no existing caller varies `scripts=`. A check
            # that passes only because its condition cannot yet occur is not a check.
            with TempDir() as t:
                (t / "full").mkdir()
                (t / "none").mkdir()
                full = gh.make_repo(t / "full")
                nogd = gh.make_repo(t / "none", scripts=())
                c.check("_key() distinguishes a DIFFERENT scripts= tuple",
                        (full / ".agents/scripts/git-hooks/merge-target-guard.sh").is_file()
                        and not (nogd / ".agents/scripts/git-hooks"
                                 "/merge-target-guard.sh").exists(),
                        "two different scripts= shapes were served ONE template")

            # `make_carveout_repo` is the third converted git_hooks builder and had no case at
            # all — acceptance row 2 says EVERY scenario in both files starts from a fresh clone.
            with TempDir() as t:
                (t / "c1").mkdir()
                (t / "c2").mkdir()
                kw = {"flag": "SOP-ENFORCE", "script": "sop-currency.sh"}
                c1 = gh.make_carveout_repo(t / "c1", **kw)
                (c1 / "scenario-one.txt").write_text("left behind\n", encoding="utf-8")
                gh.sh("git", "config", "scc214.left", "behind", cwd=c1)
                c2 = gh.make_carveout_repo(t / "c2", **kw)
                c.check("a carveout scenario does not see its predecessor's leftovers",
                        not (c2 / "scenario-one.txt").exists()
                        and not gh.sh("git", "config", "scc214.left", cwd=c2)[1].strip(),
                        "carveout clones are not isolated")
                found = leaks(t / "c2")
                c.check("...and no carveout clone carries a path into the template root",
                        found == [], str(found)[:200])

            with TempDir() as t:
                (t / "armed").mkdir()
                (t / "bare").mkdir()
                armed = gh.make_repo(t / "armed")
                bare = gh.make_repo(t / "bare", arm=False)
                c.check("make_repo(arm=False) after make_repo() carries no flag",
                        (armed / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").is_file()
                        and not (bare / ".agents/scripts/git-hooks/MERGE-TARGET-ENFORCE").exists(),
                        "the template key is not distinguishing arm=False")

            # ⛔ BOTH HALVES, because one half is not a gate. Asserting only that a legal merge
            # SUCCEEDS is satisfied by a repo running no hook at all — measured: delete
            # `core.hooksPath` from the fixture and the old single-sided row still passed,
            # 24/24. The linked, frozen hook must also still REFUSE what it exists to refuse,
            # which is the only evidence that git is invoking it through the hard link.
            with TempDir() as t:
                (t / "merge").mkdir()
                d = gh.make_repo(t / "merge")
                gh.lane(d, "chore/SCC-144-x")
                gh.lane(d, "chore/SCC-144-y", "main")
                # ⛔ REFUSE FIRST, while both lanes are still siblings off `main`. Cutting `y`
                # AFTER `x` has landed makes the merge a no-op ("Already up to date", rc 0,
                # HEAD unmoved) and git never invokes the hook at all — which is a green row
                # proving nothing, the very shape this half exists to prevent.
                rc2, out2, moved2 = gh.merge(d, "chore/SCC-144-y", "chore/SCC-144-x")
                c.check("REFUSE half · the linked, frozen hook still REFUSES chore -> chore",
                        rc2 != 0 and not moved2,
                        f"rc={rc2} moved={moved2} — the hook did not run through the hard "
                        f"link, so this row proves nothing: {out2.strip()[-300:]}")
                # The refusal leaves the merge IN PROGRESS - staged changes and MERGE_HEAD -
                # so the next checkout dies on "local changes would be overwritten". That is
                # not incidental: it is the remedy the guard itself prints, and skipping it is
                # how the ALLOW half below reads as a failure of the gate rather than of setup.
                gh.sh("git", "merge", "--abort", cwd=d)
                rc, out, moved = gh.merge(d, "main", "chore/SCC-144-x")
                c.check("ALLOW half · a legal merge still succeeds through the linked hooks",
                        rc == 0 and moved, f"rc={rc} moved={moved} {out.strip()[-200:]}")

    if c.block("T5 · the helper's quieter decisions — fallback, symlinks, memo, cleanup"):
        if rt is not None:
            # The module docstring claims "correctness never depends on the link, only speed
            # does". Nothing tested it: replacing the `except OSError: copy2` fallback with
            # `raise` survives the whole suite. Drive the fallback for real.
            with TempDir() as t:
                real_link = rt.os.link
                rt.os.link = lambda *a, **k: (_ for _ in ()).throw(OSError("no links here"))
                a = b = None      # bound FIRST: a raising clone must fail this row, not
                try:                  # NameError its way out of the block
                    a = rt.clone(("t5", "fallback"), build_repo, t / "a") / "repo"
                    b = rt.clone(("t5", "fallback"), build_repo, t / "b") / "repo"
                    ok, why = True, ""
                except Exception as exc:                       # noqa: BLE001
                    ok, why = False, f"raised {exc!r}"
                finally:
                    rt.os.link = real_link
                c.check("a clone is correct when os.link FAILS (the copy2 fallback)",
                        ok and a is not None and (a / "hook.sh").read_text(encoding="utf-8")
                        == "#!/bin/sh\nexit 0\n", why or "the fallback clone is wrong")
                c.check("...and with linking unavailable the executables are NOT shared",
                        a is not None and b is not None
                        and (a / "hook.sh").stat().st_ino != (b / "hook.sh").stat().st_ino,
                        why or "an inode was shared despite os.link raising")

            # `_copy_entry`'s symlink branch and `_seal`'s `not p.is_symlink()` guard: no
            # fixture contains a symlink, so both survived being neutered to `pass`.
            with TempDir() as t:
                def with_link(root: Path) -> None:
                    build_repo(root)
                    (root / "repo/link-to-hook").symlink_to("hook.sh")
                    (root / "repo/abs-link").symlink_to(root / "repo/README")
                key = ("t5", "symlink")
                a = rt.clone(key, with_link, t / "a") / "repo"
                c.check("a symlink survives the clone AS a symlink, target intact",
                        (a / "link-to-hook").is_symlink()
                        and os.readlink(a / "link-to-hook") == "hook.sh",
                        f"is_symlink={(a / 'link-to-hook').is_symlink()}")
                c.check("...and leaks() SEES a symlink whose target points into the template",
                        any("abs-link" in h for h in leaks(t / "a")),
                        f"leaks() followed the link instead of reading it: {leaks(t / 'a')}")

            # `shared_root()`'s memo: forcing a rebuild each call survives, and every template
            # root but the last then leaks into TMPDIR with only one cleaned at exit.
            c.check("shared_root() is memoised — one root per process",
                    rt.shared_root() is rt.shared_root(),
                    "a second call built a second root; atexit cleans only the last")

            # The ⛔ "half-built template" comment has TWO halves. T4 pins the cache half; the
            # rmtree half survived removal, leaving the failed build's directory on disk.
            with TempDir() as t:
                before = {q.name for q in rt.shared_root().iterdir()}
                def boom2(root: Path) -> None:
                    build_repo(root)
                    raise RuntimeError("SCC-214 build failed on purpose")
                try:
                    rt.clone(("t5", "cleanup"), boom2, t / "s")
                except Exception:                              # noqa: BLE001, S110 — the raise
                    pass                                       # IS the case; the assertion is
                                                               # about what it left on disk
                after = {q.name for q in rt.shared_root().iterdir()}
                c.check("a failed build leaves NO template directory behind",
                        after == before, f"leaked: {sorted(after - before)}")

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
                    except Exception:                              # noqa: BLE001, S110 — a cached
                        pass                                       # dead template raises here too
                c.check("a failed build caches nothing", len(calls) == 2,
                        f"the build ran {len(calls)} times — a failed template was cached")
                try:
                    good = rt.clone(key, build_repo, t / "after")
                    later, why = (good / "repo/README").is_file(), "the failed key stayed poisoned"
                except Exception as exc:                           # noqa: BLE001
                    later, why = False, f"raised {exc!r}"
                c.check("a key whose build failed can still be built later", later, why)


if __name__ == "__main__":
    sys.exit(main())
