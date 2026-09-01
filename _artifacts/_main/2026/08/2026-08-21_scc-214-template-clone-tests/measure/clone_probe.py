import os, shutil, subprocess, sys, time
from pathlib import Path
TESTS = Path(sys.argv[1]); sys.path.insert(0, str(TESTS))
import _pf_fixtures as pf, test_git_hooks as gh
from _harness import TempDir
def g(*a, cwd): return subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True).stdout.strip()
def link_exec(src, dst):
    if os.access(src, os.X_OK) and Path(src).is_file(): os.link(src, dst)
    else: shutil.copy2(src, dst)
with TempDir() as tpl, TempDir() as t:
    r = pf.make_repo(tpl); base = g("rev-parse", "HEAD", cwd=r)
    shutil.copytree(tpl, t, dirs_exist_ok=True, copy_function=link_exec)
    c = t / "repo"; g("remote", "set-url", "origin", str(t / "origin.git"), cwd=c)
    print("pf clone: status=", repr(g("status", "--porcelain", cwd=c)), "| HEAD==base:", g("rev-parse", "HEAD", cwd=c) == base,
          "| ls-remote origin main ok:", base in g("ls-remote", "origin", "main", cwd=c), "| hooksPath:", g("config", "core.hooksPath", cwd=c))
    hook = c / ".githooks/commit-msg"; print("  hook linked (same inode):", hook.stat().st_ino == (tpl / "repo/.githooks/commit-msg").stat().st_ino)
    # a scenario-style push from the clone must land on the CLONE's bare, not the template's
    (c / "x.md").write_text("x\n"); pf.commit(c, "SCC-11 x"); g("push", "-q", "origin", "main", cwd=c)
    print("  template bare untouched:", base in g("ls-remote", str(tpl / "origin.git"), "main", cwd=tpl), "| clone bare moved:", base not in g("ls-remote", str(t / "origin.git"), "main", cwd=c))
with TempDir() as tpl, TempDir() as t:
    d, bare = gh.make_pushable(tpl); base = gh.head(d)
    for p in (tpl / "work").rglob("*"):
        if p.is_file() and os.access(p, os.X_OK): p.chmod(0o555)
    (tpl / "work/.git/FETCH_HEAD").unlink(missing_ok=True)
    shutil.copytree(tpl, t, dirs_exist_ok=True, copy_function=link_exec)
    c = t / "work"; g("remote", "set-url", "origin", str(t / "remote.git"), cwd=c)
    print("gh clone: status=", repr(g("status", "--porcelain", cwd=c)), "| HEAD==base:", gh.head(c) == base, "| origin/main present:", bool(g("rev-parse", "--verify", "origin/main", cwd=c)))
    gh.lane(c, "chore/SCC-144-a"); rc, out, moved = gh.merge(c, "main", "chore/SCC-144-a")
    print("  merge through linked, read-only hooks: rc=", rc, "moved=", moved, "| hook still 0o555:", oct((c / '.githooks/commit-msg').stat().st_mode & 0o777))
    try: (c / ".githooks/commit-msg").write_text("x"); print("  in-place write: SUCCEEDED (freeze failed)")
    except PermissionError: print("  in-place write through the link: PermissionError (freeze holds)")
    print("  template hook bytes intact:", (tpl / "work/.githooks/commit-msg").read_bytes() == gh.MERGE_DISPATCH.read_bytes())
    print("  paths into template in clone .git:", sum(str(tpl) in p.read_text(errors='replace') for p in (c / '.git').rglob('*') if p.is_file() and p.stat().st_size < 100000))
