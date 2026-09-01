import os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
def t(p): t0 = time.perf_counter(); subprocess.run([str(p)], capture_output=True); return time.perf_counter() - t0
def stub(p): p.write_text("#!/bin/sh\nexit 0\n"); p.chmod(0o755); return p
base = Path(tempfile.mkdtemp(prefix="probe-"))
a = stub(base / "a.sh"); print(f"fresh a: first {t(a):.3f}  second {t(a):.3f}")
b = stub(base / "b.sh"); print(f"fresh b SAME dir: first {t(b):.3f}")
c = base / "c.sh"; shutil.copy2(a, c); print(f"copy2 of assessed a -> c: first {t(c):.3f}")
d = base / "d.sh"; os.link(a, d); print(f"hard link of a -> d: first {t(d):.3f}")
e = base / "e.sh"; subprocess.run(["cp", "-c", str(a), str(e)]); print(f"cp -c (APFS clone) of a -> e: first {t(e):.3f}")
f = base / "f.sh"; shutil.copy2(a, f); os.utime(f, (0, 0)); print(f"copy2 + mtime 0 -> f: first {t(f):.3f}")
tree = Path(sys.argv[1]) / ".probe-tmp"; tree.mkdir(exist_ok=True)
g = stub(tree / "g.sh"); print(f"fresh g under WORKTREE: first {t(g):.3f}")
h = stub(base / "h.sh"); print(f"fresh h (different bytes: add comment)"); h.write_text("#!/bin/sh\n# x\nexit 0\n"); print(f"  first {t(h):.3f}")
# same bytes as a but a NEW file -> content-keyed or inode-keyed?
i = base / "i.sh"; i.write_text(a.read_text()); i.chmod(0o755); print(f"new file, byte-identical to a: first {t(i):.3f}")
# a python script executed via the interpreter (not exec'd): any stall?
j = base / "j.py"; j.write_text("print(1)\n"); t0 = time.perf_counter(); subprocess.run([sys.executable, str(j)], capture_output=True); print(f"python3 j.py (not exec'd): {time.perf_counter()-t0:.3f}")
# the same a.sh invoked via `sh a.sh` (interpreter + arg, not exec of the file)
k = stub(base / "k.sh"); t0 = time.perf_counter(); subprocess.run(["/bin/sh", str(k)], capture_output=True); print(f"sh k.sh (fresh, via interpreter): {time.perf_counter()-t0:.3f}")
shutil.rmtree(tree); shutil.rmtree(base)
