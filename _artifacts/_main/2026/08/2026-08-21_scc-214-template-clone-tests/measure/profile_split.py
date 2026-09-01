"""Where does each file's wall clock go? Construction vs scenario work, and the FIRST exec of a
fresh executable vs later execs. Wraps in place before the test module binds names; runs main()."""
import sys, time, io, contextlib, os
from pathlib import Path
TESTS = Path(sys.argv[1]); which = sys.argv[2]; sys.path.insert(0, str(TESTS))
sys.argv = [sys.argv[0]]
acc, calls, depth = {}, [], [0]
def timed(name, fn, builder=False):
    def w(*a, **k):
        t0 = time.perf_counter()
        if builder: depth[0] += 1
        try: return fn(*a, **k)
        finally:
            if builder: depth[0] -= 1
            n, s = acc.get(name, (0, 0.0)); acc[name] = (n + 1, s + time.perf_counter() - t0)
    return w
if which == "pf":
    import _harness
    def rs(name, *args):
        t0 = time.perf_counter(); r = _harness._orig_run_script(name, *args)
        calls.append(("run_script", os.environ.get("PF_BOARD_STATE"), time.perf_counter() - t0, depth[0])); return r
    _harness._orig_run_script = _harness.run_script; _harness.run_script = rs
    import _pf_fixtures as pf
    pf.make_repo = timed("pf.make_repo", pf.make_repo, True)
    pf.secondary = timed("pf.secondary", pf.secondary, True)
    pf.branch = timed("pf.branch", pf.branch, True)
    pf.board = timed("pf.board (fresh acli launcher)", pf.board, True)
    pf.stamp_and_verdict = timed("pf.stamp_and_verdict", pf.stamp_and_verdict, True)
    import test_task_preflight as mod
else:
    import test_git_hooks as mod
    _sh = mod.sh
    def sh(*args, cwd, stdin=""):
        t0 = time.perf_counter(); r = _sh(*args, cwd=cwd, stdin=stdin)
        calls.append((" ".join(args[:2]), str(cwd), time.perf_counter() - t0, depth[0])); return r
    mod.sh = sh
    mod.make_repo = timed("gh.make_repo", mod.make_repo, True)
    mod.make_pushable = timed("gh.make_pushable (incl make_repo)", mod.make_pushable, True)
    mod.make_carveout_repo = timed("gh.make_carveout_repo", mod.make_carveout_repo, True)
buf = io.StringIO(); t0 = time.perf_counter()
with contextlib.redirect_stdout(buf): rc = mod.main()
total = time.perf_counter() - t0; out = buf.getvalue()
tail = [l for l in out.splitlines() if "passed --" in l or l.startswith("FAILED")]
print(f"{which}: rc={rc} total={total:.1f}s  {' '.join(tail)}")
for name, (n, s) in sorted(acc.items(), key=lambda kv: -kv[1][1]):
    print(f"  {name:36s} n={n:3d}  {s:6.1f}s  ({100*s/total:4.1f}% of wall)")
if which == "pf":
    seen, first, later = set(), [], []
    for _, st, dt, _d in calls:
        (later if st in seen else first).append(dt); seen.add(st)
    print(f"  run_script: n={len(calls)} total={sum(d for *_, d, _ in calls):.1f}s | FIRST call per fresh launcher n={len(first)} avg={sum(first)/max(1,len(first)):.2f}s total={sum(first):.1f}s | later n={len(later)} avg={sum(later)/max(1,len(later)):.2f}s")
else:
    by = {}
    for cmd, cwd, dt, d in calls:
        k = (cmd, "in-builder" if d else "scenario"); n, s = by.get(k, (0, 0.0)); by[k] = (n + 1, s + dt)
    print(f"  sh calls: n={len(calls)} total={sum(c[2] for c in calls):.1f}s")
    for (cmd, where), (n, s) in sorted(by.items(), key=lambda kv: -kv[1][1])[:12]:
        print(f"    {cmd:22s} {where:10s} n={n:3d} {s:6.1f}s")
    # the assessment signature: first hook-running git op per repo vs later ones
    seen, first, later = set(), [], []
    for cmd, cwd, dt, d in calls:
        if cmd.split()[-1] in ("merge", "push", "commit") and not d:
            (later if cwd in seen else first).append(dt); seen.add(cwd)
    print(f"  first hook-running op per repo: n={len(first)} avg={sum(first)/max(1,len(first)):.2f}s total={sum(first):.1f}s | later: n={len(later)} avg={sum(later)/max(1,len(later)):.2f}s total={sum(later):.1f}s")
