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

import subprocess
from pathlib import Path

from _harness import Cases, TempDir, run_script


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
            (sub / "backend").mkdir()
            (sub / "backend" / "keep.txt").write_text("tracked\n", encoding="utf-8")
            git(sub, "add", "backend/keep.txt")
            git(sub, "commit", "-qm", "backend")
            (sub / ".env").write_text("KEY=1\n", encoding="utf-8")
            (sub / "backend" / ".venv").mkdir()

            lane = tmp / "lane"
            git(sub, "worktree", "add", "-q", str(lane), "-b", "lane")
            c.check("fixture: lane worktree exists", (lane / "f.txt").is_file())

            code, out = link(str(lane))
            c.check("B1 exits 0", code == 0, f"exit={code}\n{out}")
            c.check("B1 names the submodule WORKING TREE as the repo",
                    f"repo:     {sub.resolve()}" in out, out.splitlines()[0] if out else "(no output)")
            c.check("B1 links the root .env", (lane / ".env").is_symlink(),
                    f"exists={(lane / '.env').exists()} symlink={(lane / '.env').is_symlink()}")
            c.check("B1 links backend/.venv one level down", (lane / "backend" / ".venv").is_symlink(),
                    f"symlink={(lane / 'backend' / '.venv').is_symlink()}")
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
            c.check("B3 links .env", (lane / ".env").is_symlink())
            c.check("B3 links node_modules", (lane / "node_modules").is_symlink())
            c.check("B3 still warns that .env is shared state", "SHARED STATE" in out, out)

            code, out = link("--unlink", str(lane))
            c.check("B3 --unlink removes both links", code == 0
                    and not (lane / ".env").exists() and not (lane / "node_modules").exists(),
                    f"exit={code}\n{out}")
            c.check("B3 --unlink leaves the TARGETS alone",
                    (plain / ".env").is_file() and (plain / "node_modules").is_dir())

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
