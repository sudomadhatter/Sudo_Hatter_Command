"""`link-worktree-assets.py` must resolve the repo it is standing over — including a SUBMODULE.

SCC-255, measured 2026-08-21 while opening an AGY lane from the lobby. The script resolved the
repo as `Path(--git-common-dir).parent` and reported `(nothing to link)` on a checkout that
plainly has a `backend/.venv`. In a submodule the common dir is `<super>/.git/modules/<name>`,
so `.parent` is `<super>/.git/modules` — a gitdir, never a working tree — and the scan finds
nothing because there is nothing there to find.

⛔ The three shapes below are ONE code path, and that is the point of testing all three:
`git -C <git-common-dir> rev-parse --show-toplevel` answers correctly for a plain repo (git
resolves a `.git` dir to its parent) AND for a submodule (it reads `core.worktree`), and FAILS
for anything with no working tree at all. The failure is not an edge case to swallow — it is
exactly the refusal B2 asks for, and it arrives for free.

⭐ WHY "ZERO ASSETS" IS NOT THE REFUSAL. SCC-255's ACCEPTANCE said a resolved repo with zero
assets should exit non-zero. Measured across the nine local checkouts, SIX have zero linkable
assets, and ten command bodies call this script at worktree-open time — so that refusal makes
every lane in those six repos un-openable, and a freshly cloned repo refuses until `npm install`
runs. The defect was never the count; it was that a FAILED RESOLUTION and an HONESTLY EMPTY REPO
printed the same sentence. So resolution is verified and named, the empty case says so out loud,
and `--require-assets` is there for the caller that knows better.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from _harness import Cases, TempDir, run_script

IS_WINDOWS = os.name == "nt"


def linked_dir(p: Path) -> bool:
    """A directory asset was placed as a LINK: symlink on POSIX, JUNCTION on Windows (SCC-321).

    ⛔ `p.is_symlink()` is FALSE for a junction, so asserting it made every directory case red on
    Windows against a script doing exactly the right thing — the script's docstring has said
    "Mac: symlink   PC: junction" since it was written, and a junction is used precisely because
    it needs no admin rights. The assertion, not the behaviour, was the one-machine artefact.
    """
    if p.is_symlink():
        return True
    if not IS_WINDOWS:
        return False
    if hasattr(os.path, "isjunction"):       # 3.12+
        return os.path.isjunction(p)
    try:                                     # 3.11 and earlier: read the reparse tag
        return bool(getattr(os.lstat(p), "st_reparse_tag", 0))
    except OSError:
        return False


def placed_file(p: Path) -> bool:
    """A FILE asset was placed the way this platform places it: symlink on POSIX, COPY on Windows.

    ⛔ The copy is deliberate and is NOT a degraded symlink. A Windows file-symlink needs admin or
    Developer Mode, and — the larger reason — the script's own docstring rules that "anything a
    lane MUTATES should be copied, not linked". A copied `.env` is the SAFER state: it is not
    shared across lanes. So the two machines differ in what is CORRECT here, and the test has to
    ask each one its own question rather than assert the Mac's answer twice.
    """
    return (p.is_file() and not p.is_symlink()) if IS_WINDOWS else p.is_symlink()


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def seed(repo: Path) -> Path:
    """A one-commit repo. `worktree add` needs a commit to branch from."""
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    (repo / "f.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "f.txt")
    git(repo, "commit", "-qm", "seed")
    return repo


def link(*args: str) -> tuple[int, str]:
    return run_script("link-worktree-assets.py", *args)


def main() -> int:
    c = Cases("link_worktree_assets")

    if c.block("B1 · submodule-resolves: a gitdir-file checkout links its own assets"):
        with TempDir() as tmp:
            src = seed(tmp / "subsrc")
            super_ = seed(tmp / "super")
            # `protocol.file.allow` is required since CVE-2022-39253 for a local-path submodule.
            r = git(super_, "-c", "protocol.file.allow=always", "submodule", "add", "-q",
                    str(src), "sub")
            sub = super_ / "sub"
            c.check("fixture: submodule added", r.returncode == 0 and sub.is_dir(),
                    (r.stderr or r.stdout).strip()[:200])
            c.check("fixture: sub/.git is a gitdir FILE (the shape under test)",
                    (sub / ".git").is_file(),
                    f"is_file={(sub / '.git').is_file()}")

            # The assets a real submodule carries: AGY's shape, one level down and at the root.
            # `backend/` itself must be TRACKED — the script skips an asset whose parent dir is
            # absent from the worktree, so an untracked `backend/` would make the depth-1 half of
            # this case vacuous rather than failing it.
            # ⛔ `seed()` set an identity on `src`; `submodule add` CLONED it, and local config
            # does not travel with a clone. On a machine with no ambient user.email the commit
            # below fails silently — `git()` neither checks nor raises — and the failure surfaces
            # four assertions later pointing at the script instead of at this fixture. Two
            # machines, and only one of them has an ambient identity.
            git(sub, "config", "user.email", "t@t.t")
            git(sub, "config", "user.name", "t")
            (sub / "backend").mkdir()
            (sub / "backend" / "keep.txt").write_text("tracked\n", encoding="utf-8")
            git(sub, "add", "backend/keep.txt")
            r = git(sub, "commit", "-qm", "backend")
            c.check("fixture: the submodule commit landed (identity is NOT inherited by a clone)",
                    r.returncode == 0, (r.stderr or r.stdout).strip()[:200])
            (sub / ".env").write_text("KEY=1\n", encoding="utf-8")
            (sub / "backend" / ".venv").mkdir()

            lane = tmp / "lane"
            git(sub, "worktree", "add", "-q", str(lane), "-b", "lane")
            c.check("fixture: lane worktree exists", (lane / "f.txt").is_file())

            code, out = link(str(lane))
            c.check("B1 exits 0", code == 0, f"exit={code}\n{out}")
            c.check("B1 names the submodule WORKING TREE as the repo",
                    f"repo:     {sub.resolve()}" in out, out.splitlines()[0] if out else "(no output)")
            c.check("B1 places the root .env", placed_file(lane / ".env"),
                    f"exists={(lane / '.env').exists()} symlink={(lane / '.env').is_symlink()}")
            c.check("B1 links backend/.venv one level down", linked_dir(lane / "backend" / ".venv"),
                    f"exists={(lane / 'backend' / '.venv').exists()}")
            c.check("B1 does NOT report 'nothing to link'", "nothing to link" not in out,
                    out)

    if c.block("B2a · unverified-resolution-refuses: no working tree behind the gitdir"):
        with TempDir() as tmp:
            plain = seed(tmp / "plain")
            home = tmp / "barehome"
            home.mkdir()
            bare = home / "bare.git"
            subprocess.run(["git", "clone", "-q", "--bare", str(plain), str(bare)],
                           capture_output=True, text=True)
            lane = tmp / "barelane"
            git(bare, "worktree", "add", "-q", str(lane), "-b", "bl")
            c.check("fixture: bare-backed lane exists", (lane / "f.txt").is_file())

            code, out = link(str(lane))
            c.check("B2a exits non-zero", code != 0, f"exit={code}\n{out}")
            c.check("B2a names the path it could not resolve", str(bare.resolve()) in out, out)
            c.check("B2a does NOT silently fall back to the gitdir's parent",
                    f"repo:     {home.resolve()}" not in out, out)
            # ⛔ WHICH refusal fired, not just THAT one did (found by the SCC-244 sweep).
            # `repo_root` raises in two places, and this fixture reaches both: the probe
            # fails, and then `realpath("")` — the empty toplevel — compares unequal to the
            # candidate, so the different-repo guard raises too. With only an "exit non-zero"
            # assertion, deleting the FIRST refusal outright still passed this block. The
            # reason line is the only thing that tells them apart, and it is also what the
            # operator reads: "is inside a DIFFERENT repo" sends them hunting a repo that
            # does not exist, when the truth is there is no checkout here at all.
            c.check("B2a gives the RIGHT reason: no working tree, not 'a different repo'",
                    "DIFFERENT repo" not in out, out)

    if c.block("B2b · verified-empty-repo-exits-zero: an honest zero is not a failure"):
        with TempDir() as tmp:
            plain = seed(tmp / "plain")          # deliberately carries NO linkable assets
            lane = tmp / "lane"
            git(plain, "worktree", "add", "-q", str(lane), "-b", "lane")

            code, out = link(str(lane))
            c.check("B2b exits 0 — six of nine local repos are this shape", code == 0,
                    f"exit={code}\n{out}")
            c.check("B2b says the resolution was VERIFIED, naming the repo",
                    f"resolution verified: {plain.resolve()}" in out, out)

            code, out = link(str(lane), "--require-assets")
            # ⛔ The exit code alone is a VACUOUS pass here: argparse exits 2 on an unknown flag,
            # so an unimplemented `--require-assets` would look like a working refusal. The
            # second check is what makes the first mean something.
            c.check("B2b --require-assets turns the same state into a refusal", code != 0,
                    f"exit={code}\n{out}")
            c.check("B2b --require-assets refuses on the ASSETS, not as an unknown flag",
                    "unrecognized arguments" not in out
                    and "--require-assets was given" in out
                    and str(plain.resolve()) in out, out)

    if c.block("B2c · different-repo-refuses: the candidate is inside SOMEONE ELSE's tree"):
        # ⛔ B2a only asserts this message is ABSENT. Nothing pinned it ever APPEARING, so
        # replacing the guard with `if False:` kept every check green — the symmetric hole to the
        # one B2a itself was written to close. It is reachable: a submodule gitdir whose
        # `core.worktree` names a plain subdirectory of the superproject.
        with TempDir() as tmp:
            src = seed(tmp / "subsrc")
            super_ = seed(tmp / "super")
            git(super_, "-c", "protocol.file.allow=always", "submodule", "add", "-q",
                str(src), "sub")
            sub_ = super_ / "sub"
            lane = tmp / "lane"
            git(sub_, "worktree", "add", "-q", str(lane), "-b", "lane")
            c.check("fixture: lane worktree exists", (lane / "f.txt").is_file())

            stray = super_ / "stray"
            stray.mkdir()
            gitdir = super_ / ".git" / "modules" / "sub"
            c.check("fixture: the submodule gitdir is where git puts it", gitdir.is_dir(),
                    str(gitdir))
            git(gitdir, "config", "core.worktree", str(stray))

            code, out = link(str(lane))
            c.check("B2c refuses", code != 0, f"exit={code}\n{out}")
            c.check("B2c gives the DIFFERENT-repo reason, and names the root it found",
                    "DIFFERENT repo" in out and str(super_.resolve()) in out, out)
            c.check("B2c does not link anything from a repo the lane does not belong to",
                    "linked" not in out, out)

    if c.block("B2d · a zero that was never verified may not claim it was"):
        # `--repo` skips repo_root() — that is what the escape hatch is FOR — and the report
        # printed "resolution verified" over it anyway, re-opening the exact ambiguity the
        # report exists to close. `--repo <an empty dir that is not a repo>` exited 0 and said
        # the repo genuinely has none.
        with TempDir() as tmp:
            lane = tmp / "lane"
            lane.mkdir()
            notrepo = tmp / "notrepo"
            notrepo.mkdir()

            code, out = link(str(lane), "--repo", str(notrepo))
            c.check("still exits 0 — --repo is an escape hatch, not a second gate", code == 0,
                    f"exit={code}\n{out}")
            c.check("...but does NOT claim the resolution was verified",
                    "resolution verified" not in out, out)
            c.check("...and says plainly that nothing was checked", "NOT verified" in out, out)
            c.check("...and warns that the given path is not a working tree at all",
                    "not a git working tree" in out, out)

    if c.block("B2e · assets FOUND but unplaceable is not 'this repo has none'"):
        # The third state nobody counted: the loop `continue`s past an asset whose parent dir is
        # missing from the worktree without incrementing linked OR skipped, so a repo that
        # visibly carries `backend/.venv` reported that it genuinely has none.
        with TempDir() as tmp:
            repo = seed(tmp / "repo")
            (repo / "backend").mkdir()
            (repo / "backend" / ".venv").mkdir()
            lane = tmp / "lane"                      # no `backend/` in it — nowhere to put it
            lane.mkdir()

            code, out = link(str(lane), "--repo", str(repo))
            c.check("the unplaceable asset is reported on its own line",
                    "! backend/.venv" in out, out)
            c.check("...and the report does NOT say the repo genuinely has none",
                    "genuinely has none" not in out, out)
            c.check("...it says how MANY assets were found and could not be placed",
                    "1 asset(s) FOUND in this repo" in out,
                    out + "\n      the COUNT is the assertion: a report that says `0 asset(s) "
                          "FOUND` is the same silent zero this block exists to catch")

            code, out = link(str(lane), "--repo", str(repo), "--require-assets")
            c.check("--require-assets refuses on this state too", code != 0, f"exit={code}\n{out}")
            c.check("...naming the unplaceable count, not 'it has no linkable assets'",
                    "1 asset(s) found but unplaceable" in out
                    and "has no linkable assets" not in out, out)

    if c.block("B2f · an unresolvable start REFUSES, it does not traceback"):
        # `check=True` on the first rev-parse raised CalledProcessError, which main() does not
        # catch — so the operator got a traceback instead of the refusal the SOP advertises.
        with TempDir() as tmp:
            loose = tmp / "loose"
            loose.mkdir()
            code, out = link(str(loose))
            c.check("exits 1, the refusal code", code == 1, f"exit={code}\n{out}")
            c.check("prints the refusal, not a stack trace",
                    "cannot resolve the repo behind" in out and "Traceback" not in out, out)
            c.check("...and still tells the operator the way out", "--repo" in out, out)

    if c.block("B3 · plain-repo-unchanged: the ten callers' everyday path still links"):
        # Characterization, and honestly green from the start: this is what the fix must not
        # break. Ten command bodies call this script at worktree-open time.
        with TempDir() as tmp:
            plain = seed(tmp / "plain")
            (plain / ".env").write_text("KEY=1\n", encoding="utf-8")
            (plain / "node_modules").mkdir()
            lane = tmp / "lane"
            git(plain, "worktree", "add", "-q", str(lane), "-b", "lane")

            code, out = link(str(lane))
            c.check("B3 exits 0", code == 0, f"exit={code}\n{out}")
            c.check("B3 resolves the plain repo", f"repo:     {plain.resolve()}" in out, out)
            c.check("B3 places .env", placed_file(lane / ".env"))
            c.check("B3 links node_modules", linked_dir(lane / "node_modules"))
            # ⛔ THE WARNING IS ABOUT SHARED STATE, AND ON WINDOWS THERE IS NONE (SCC-321).
            # `.env` is COPIED there, so editing it in this lane cannot reach any other — the
            # warning would be false, and a tool that cries shared-state at a private copy trains
            # the operator to ignore it. Each machine asserts its own truth, and the Windows arm
            # is the stronger claim of the two: the warning must be ABSENT.
            if IS_WINDOWS:
                c.check("B3 does NOT claim shared state for a COPIED .env",
                        "SHARED STATE" not in out, out)
            else:
                c.check("B3 still warns that .env is shared state", "SHARED STATE" in out, out)

            code, out = link("--unlink", str(lane))
            # ⛔ `--unlink` removes LINKS, never files — `find_links` enumerates reparse points,
            # deliberately ("ENUMERATE, never assume"). So a copied `.env` survives it on Windows,
            # which is correct: it is this lane's own file, not a door into a shared target.
            c.check("B3 --unlink removes the link(s)", code == 0
                    and not (lane / "node_modules").exists()
                    and (IS_WINDOWS or not (lane / ".env").exists()),
                    f"exit={code}\n{out}")
            if IS_WINDOWS:
                c.check("B3 --unlink leaves the lane's own COPY of .env in place",
                        (lane / ".env").is_file(),
                        "a copy is not a link; removing it is not this command's job")
            c.check("B3 --unlink leaves the TARGETS alone",
                    (plain / ".env").is_file() and (plain / "node_modules").is_dir())

    if c.block("B4 · claude-local-assets-link: settings.local.json and scratchpad-root travel into worktree"):
        with TempDir() as tmp:
            plain = seed(tmp / "plain")
            (plain / ".claude").mkdir()
            (plain / ".claude" / "tracked.txt").write_text("tracked\n", encoding="utf-8")
            git(plain, "add", ".claude/tracked.txt")
            git(plain, "commit", "-qm", "claude dir")
            (plain / ".claude" / "settings.local.json").write_text('{"permissions": {}}\n', encoding="utf-8")
            (plain / ".claude" / "scratchpad-root").write_text("/tmp/scratchpad\n", encoding="utf-8")
            lane = tmp / "lane"
            git(plain, "worktree", "add", "-q", str(lane), "-b", "lane")

            code, out = link(str(lane))
            c.check("B4 exits 0", code == 0, f"exit={code}\n{out}")
            c.check("B4 places .claude/settings.local.json",
                    placed_file(lane / ".claude" / "settings.local.json"))
            c.check("B4 places .claude/scratchpad-root",
                    placed_file(lane / ".claude" / "scratchpad-root"))

            code, out = link("--unlink", str(lane))
            # Both are FILES, so both are copies on Windows and survive --unlink — see B3.
            c.check("B4 --unlink removes both links", code == 0
                    and (IS_WINDOWS or (
                        not (lane / ".claude" / "settings.local.json").exists()
                        and not (lane / ".claude" / "scratchpad-root").exists())),
                    f"exit={code}\n{out}")
            c.check("B4 --unlink leaves the TARGETS alone",
                    (plain / ".claude" / "settings.local.json").is_file()
                    and (plain / ".claude" / "scratchpad-root").is_file())

    if c.block("SCC-310 · linked lanes stamp CLEAN: exclude entries hide the links, real dirt stays"):
        # A trailing-slash gitignore pattern (`auth_keys/`, `.venv/`) matches a DIRECTORY only,
        # never the symlink this script creates - so every linked lane read `?? auth_keys` etc.
        # and stamped its gate receipts dirty_tree: true. Measured (2026-08-24): a per-worktree
        # info/exclude is IGNORED by git (`--git-path info/exclude` resolves to the COMMON one),
        # so the fix is a managed block in `<common>/.git/info/exclude`.
        with TempDir() as tmp:
            plain = seed(tmp / "plain")
            (plain / ".gitignore").write_text(".env\nauth_keys/\n.venv/\n", encoding="utf-8")
            git(plain, "add", ".gitignore")
            git(plain, "commit", "-qm", "ignore")
            (plain / ".env").write_text("KEY=1\n", encoding="utf-8")
            (plain / "auth_keys").mkdir()
            (plain / ".venv").mkdir()
            excl = plain / ".git" / "info" / "exclude"

            lane = tmp / "lane"
            git(plain, "worktree", "add", "-q", str(lane), "-b", "lane")
            code, out = link(str(lane))
            st = git(lane, "status", "--short").stdout
            c.check("X1 a freshly linked worktree reports a CLEAN git status",
                    code == 0 and st.strip() == "", f"exit={code} status:\n{st}")

            (lane / "stray.md").write_text("real work\n", encoding="utf-8")
            st = git(lane, "status", "--short").stdout
            c.check("X2 real uncommitted work STILL reads dirty (no blanket silence)",
                    "stray.md" in st, f"status:\n{st}")
            (lane / "stray.md").unlink()

            # A SECOND lane shares the one exclude file - unlinking lane 1 must not dirty lane 2.
            lane2 = tmp / "lane2"
            git(plain, "worktree", "add", "-q", str(lane2), "-b", "lane2")
            link(str(lane2))
            code, out = link("--unlink", str(lane))
            text = excl.read_text(encoding="utf-8") if excl.is_file() else ""
            st2 = git(lane2, "status", "--short").stdout
            c.check("X3 unlinking ONE lane keeps the entries the sibling lane still needs",
                    code == 0 and "link-worktree-assets" in text and st2.strip() == "",
                    f"exit={code} exclude:\n{text}\nlane2 status:\n{st2}")

            # Unlinking the LAST lane removes the managed block - no stale entries left behind.
            git(plain, "worktree", "remove", "--force", str(lane))
            code, out = link("--unlink", str(lane2))
            text = excl.read_text(encoding="utf-8") if excl.is_file() else ""
            c.check("X4 unlinking the LAST lane leaves no managed exclude entries behind",
                    code == 0 and "link-worktree-assets" not in text,
                    f"exit={code} exclude:\n{text}")

    if c.block("SCC-310 X5 · a TRUNCATED managed block (END sentinel lost) never eats user patterns"):
        # Review finding (VERIFIED): with BEGIN present and END missing, the first cut treated
        # everything to end-of-file as managed - the user's own exclude patterns below the
        # block were rewritten away, and last-lane unlink deleted them outright.
        with TempDir() as tmp:
            plain = seed(tmp / "plain")
            (plain / ".gitignore").write_text(".env\n", encoding="utf-8")
            git(plain, "add", ".gitignore")
            git(plain, "commit", "-qm", "ignore")
            (plain / ".env").write_text("KEY=1\n", encoding="utf-8")
            excl = plain / ".git" / "info" / "exclude"
            excl.parent.mkdir(parents=True, exist_ok=True)
            excl.write_text("user-above.txt\n"
                            "# BEGIN link-worktree-assets (auto-managed - do not edit this block)\n"
                            "/stale-managed-entry\n"
                            "user-below.txt\n", encoding="utf-8")

            lane = tmp / "lane"
            git(plain, "worktree", "add", "-q", str(lane), "-b", "lane")
            code, out = link(str(lane))
            text = excl.read_text(encoding="utf-8")
            c.check("X5a linking over a truncated block keeps BOTH user patterns",
                    code == 0 and "user-above.txt" in text and "user-below.txt" in text,
                    f"exit={code} exclude:\n{text}")

            code, out = link("--unlink", str(lane))
            text = excl.read_text(encoding="utf-8") if excl.is_file() else ""
            c.check("X5b last-lane unlink removes only the managed block - user patterns survive",
                    code == 0 and "user-above.txt" in text and "user-below.txt" in text
                    and "link-worktree-assets" not in text,
                    f"exit={code} exclude:\n{text}")

    return c.finish()



if __name__ == "__main__":
    raise SystemExit(main())
